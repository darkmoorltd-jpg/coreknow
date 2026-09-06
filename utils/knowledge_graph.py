
import networkx as nx
import json
import os
import requests

class KnowledgeGraph:
    def __init__(self, supabase_url=None, supabase_key=None):
        self.graph = nx.DiGraph()
        self.supabase = None
        if supabase_url and supabase_key:
            from supabase import create_client
            self.supabase = create_client(supabase_url, supabase_key)
    
    def extract_concepts(self, text, llm_api_key=None):
        """Extract key concepts and relationships using DeepSeek."""
        if not llm_api_key:
            # Fallback: simple keyword extraction
            words = text.lower().split()
            stop_words = {'the','a','an','and','or','but','in','on','at','to','for','of','with','by','from','is','are','was','were','be','been','being','have','has','had','do','does','did','will','would','shall','should','may','might','must','can','could','this','that','these','those','it','its','as','than','then','so','if','when','where','which','who','whom','what','how','not','no','yes','very','too','also','just','because','while','during','through','over','under','again','further','once','here','there','all','any','both','each','few','more','most','other','some','such','only','own','same','s','t','don','now'}
            concepts = set(w for w in words if w not in stop_words and len(w) > 3)
            return list(concepts)[:50]
        
        headers = {"Authorization": f"Bearer {llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are CoreKnow's knowledge extraction engine. Extract key concepts and their relationships from the text. Return ONLY a JSON array of objects with fields: 'entity1', 'relationship', 'entity2'. Maximum 20 triples."},
                {"role": "user", "content": text[:5000]}
            ],
            "max_tokens": 1000,
            "temperature": 0.3
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                # Extract JSON from response
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    triples = json.loads(json_match.group())
                    return triples
        except:
            pass
        return []
    
    def add_document(self, text, doc_id, llm_api_key=None):
        """Add document to knowledge graph with concept extraction."""
        self.graph.add_node(doc_id, type="document", text=text[:500])
        
        triples = self.extract_concepts(text, llm_api_key)
        
        if triples:
            for triple in triples[:20]:
                if isinstance(triple, dict):
                    e1 = triple.get('entity1', '')
                    rel = triple.get('relationship', 'related_to')
                    e2 = triple.get('entity2', '')
                    if e1 and e2:
                        self.graph.add_node(e1, type="concept")
                        self.graph.add_node(e2, type="concept")
                        self.graph.add_edge(e1, e2, relationship=rel)
                        self.graph.add_edge(doc_id, e1, relationship="contains")
                        self.graph.add_edge(doc_id, e2, relationship="contains")
    
    def query(self, concept):
        """Find related concepts and relationships."""
        results = []
        if concept in self.graph:
            for neighbor in self.graph.neighbors(concept):
                edge_data = self.graph.get_edge_data(concept, neighbor)
                results.append({
                    "concept": neighbor,
                    "relationship": edge_data.get("relationship", "related") if edge_data else "related"
                })
        return results
    
    def search_documents(self, query):
        """Search documents containing a concept."""
        docs = []
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "document" and query.lower() in str(node).lower():
                docs.append(node)
        return docs
    
    def get_all_concepts(self):
        """Return all concepts in the graph."""
        return [n for n, d in self.graph.nodes(data=True) if d.get("type") == "concept"]
    
    def get_stats(self):
        """Return graph statistics."""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "concepts": len(self.get_all_concepts()),
            "documents": len([n for n, d in self.graph.nodes(data=True) if d.get("type") == "document"]),
        }
    
    def save_to_supabase(self, table_name="knowledge_graph"):
        """Save graph nodes to Supabase."""
        if not self.supabase:
            return False
        try:
            for node, data in self.graph.nodes(data=True):
                self.supabase.table(table_name).upsert({
                    "node_id": str(node),
                    "node_type": data.get("type", "concept"),
                    "data": json.dumps(data)
                }).execute()
            return True
        except Exception as e:
            print(f"Error saving graph: {e}")
            return False
    
    def export_graph(self):
        """Export graph as JSON for later use."""
        data = nx.node_link_data(self.graph)
        return json.dumps(data)
    
    def import_graph(self, json_data):
        """Import graph from JSON."""
        data = json.loads(json_data)
        self.graph = nx.node_link_graph(data)

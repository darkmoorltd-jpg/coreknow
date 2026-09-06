
import networkx as nx
import json
import os
from supabase import create_client

class KnowledgeGraph:
    def __init__(self, supabase_url=None, supabase_key=None):
        self.graph = nx.DiGraph()
        self.supabase = None
        if supabase_url and supabase_key:
            self.supabase = create_client(supabase_url, supabase_key)
    
    def extract_concepts(self, text, llm_api_key=None):
        """Extract key concepts from text using DeepSeek API."""
        if not llm_api_key:
            # Fallback: simple keyword extraction
            words = text.lower().split()
            # Remove stop words (simplified)
            stop_words = {'the','a','an','and','or','but','in','on','at','to','for','of','with','by','from','is','are','was','were','be','been','being','have','has','had','do','does','did','will','would','shall','should','may','might','must','can','could'}
            concepts = set(w for w in words if w not in stop_words and len(w) > 3)
            return list(concepts)[:50]
        
        import requests
        headers = {"Authorization": f"Bearer {llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "system", "content": "Extract key concepts and their relationships from the text. Return as JSON list of [concept1, relationship, concept2]."},
                         {"role": "user", "content": text[:5000]}],
            "max_tokens": 500
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                # Try to parse JSON
                try:
                    triples = json.loads(content)
                    return triples
                except:
                    return self.extract_concepts(text, None)
        except:
            pass
        return []
    
    def add_document(self, text, doc_id, llm_api_key=None):
        """Add a document to the knowledge graph."""
        concepts = self.extract_concepts(text, llm_api_key)
        self.graph.add_node(doc_id, type="document", text=text[:200])
        
        for concept in concepts[:50]:
            if isinstance(concept, list) and len(concept) >= 2:
                self.graph.add_node(concept[0], type="concept")
                self.graph.add_node(concept[1], type="concept")
                self.graph.add_edge(concept[0], concept[1], relationship="related")
            else:
                self.graph.add_node(str(concept), type="concept")
                self.graph.add_edge(doc_id, str(concept), relationship="contains")
    
    def query(self, concept):
        """Find related concepts in the graph."""
        if concept in self.graph:
            return list(self.graph.neighbors(concept))
        return []
    
    def get_stats(self):
        """Return graph statistics."""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "concepts": len([n for n, d in self.graph.nodes(data=True) if d.get("type") == "concept"]),
            "documents": len([n for n, d in self.graph.nodes(data=True) if d.get("type") == "document"]),
        }
    
    def save_to_supabase(self, table_name="knowledge_graph"):
        """Save graph to Supabase."""
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

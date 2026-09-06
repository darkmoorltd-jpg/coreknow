
import json
from supabase import create_client
import streamlit as st

class Database:
    def __init__(self):
        try:
            self.url = st.secrets["supabase"]["url"]
            self.key = st.secrets["supabase"]["service_key"]
            self.client = create_client(self.url, self.key)
            self.enabled = True
        except:
            self.enabled = False
            self.client = None
    
    def save_knowledge_graph(self, kg):
        """Save knowledge graph nodes to Supabase."""
        if not self.enabled:
            return False
        
        try:
            for node, data in kg.graph.nodes(data=True):
                self.client.table("coreknow_kg").upsert({
                    "node_id": str(node),
                    "node_type": data.get("type", "concept"),
                    "data": json.dumps(data)
                }).execute()
            return True
        except Exception as e:
            print(f"Error saving KG: {e}")
            return False
    
    def load_knowledge_graph(self, kg):
        """Load knowledge graph from Supabase."""
        if not self.enabled:
            return False
        
        try:
            res = self.client.table("coreknow_kg").select("*").execute()
            if res.data:
                for row in res.data:
                    node_id = row["node_id"]
                    node_type = row.get("node_type", "concept")
                    data = json.loads(row.get("data", "{}"))
                    kg.graph.add_node(node_id, type=node_type, **data)
                return True
        except Exception as e:
            print(f"Error loading KG: {e}")
        return False
    
    def save_memory(self, memory):
        """Save memory to Supabase."""
        if not self.enabled:
            return False
        
        try:
            self.client.table("coreknow_memory").upsert({
                "memory_type": "full",
                "data": json.dumps({
                    "short_term": memory.short_term,
                    "long_term": memory.long_term,
                    "episodic": memory.episodic
                })
            }).execute()
            return True
        except:
            return False
    
    def save_learning_log(self, improvement):
        """Save learning log to Supabase."""
        if not self.enabled:
            return False
        
        try:
            self.client.table("coreknow_learning").upsert({
                "log_type": "improvement",
                "data": json.dumps({
                    "learning_log": improvement.learning_log,
                    "confidence_scores": improvement.confidence_scores,
                    "knowledge_gaps": improvement.knowledge_gaps
                })
            }).execute()
            return True
        except:
            return False
    
    def get_stats(self):
        """Get database stats."""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            kg_res = self.client.table("coreknow_kg").select("node_id", count="exact").execute()
            return {
                "enabled": True,
                "kg_nodes": kg_res.count if kg_res.count else 0,
            }
        except:
            return {"enabled": True, "kg_nodes": 0}

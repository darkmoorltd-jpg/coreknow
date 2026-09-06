
import json
import os
from datetime import datetime

class MemorySystem:
    def __init__(self):
        self.short_term = []  # Recent interactions
        self.long_term = {}   # Permanent knowledge
        self.episodic = []    # Specific events
    
    def add_short_term(self, entry):
        """Add to short-term memory (last 50 items)."""
        entry["timestamp"] = datetime.now().isoformat()
        self.short_term.append(entry)
        if len(self.short_term) > 50:
            self.short_term.pop(0)
    
    def add_long_term(self, key, value):
        """Store in long-term memory."""
        self.long_term[key] = value
    
    def add_episodic(self, event):
        """Store an event."""
        event["timestamp"] = datetime.now().isoformat()
        self.episodic.append(event)
    
    def recall_short_term(self, n=10):
        """Get last n short-term memories."""
        return self.short_term[-n:]
    
    def recall_long_term(self, key):
        """Get long-term memory by key."""
        return self.long_term.get(key, None)
    
    def save(self, filepath="memory.json"):
        """Save all memory to file."""
        data = {
            "short_term": self.short_term,
            "long_term": self.long_term,
            "episodic": self.episodic
        }
        with open(filepath, "w") as f:
            json.dump(data, f)
    
    def load(self, filepath="memory.json"):
        """Load memory from file."""
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
            self.short_term = data.get("short_term", [])
            self.long_term = data.get("long_term", {})
            self.episodic = data.get("episodic", [])

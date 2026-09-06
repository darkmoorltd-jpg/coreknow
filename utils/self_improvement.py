
import json
import os
from datetime import datetime

class SelfImprovement:
    def __init__(self):
        self.learning_log = []
        self.confidence_scores = {}
        self.knowledge_gaps = []
        self.improvement_history = []
    
    def track_feedback(self, question, helpful):
        """Track user feedback to identify knowledge gaps."""
        entry = {
            "question": question,
            "helpful": helpful,
            "timestamp": datetime.now().isoformat()
        }
        self.learning_log.append(entry)
        
        if not helpful:
            self.knowledge_gaps.append(question)
    
    def get_confidence(self, concept):
        """Get confidence score for a concept (0-1)."""
        return self.confidence_scores.get(concept, 0.0)
    
    def update_confidence(self, concept, helpful):
        """Update confidence based on feedback."""
        current = self.confidence_scores.get(concept, 0.5)
        if helpful:
            new_score = min(1.0, current + 0.1)
        else:
            new_score = max(0.0, current - 0.1)
        self.confidence_scores[concept] = new_score
    
    def identify_gaps(self):
        """Identify knowledge gaps from failed answers."""
        # Count frequency of each gap
        from collections import Counter
        gap_counts = Counter(self.knowledge_gaps)
        return gap_counts.most_common(10)
    
    def generate_learning_plan(self):
        """Suggest what CoreKnow should learn next."""
        gaps = self.identify_gaps()
        plan = []
        for topic, count in gaps:
            plan.append({
                "topic": topic,
                "priority": count,
                "reason": f"Failed to answer correctly {count} times"
            })
        return plan
    
    def log_improvement(self, action, result):
        """Log self-improvement actions."""
        self.improvement_history.append({
            "action": action,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_stats(self):
        """Get self-improvement statistics."""
        return {
            "total_feedback": len(self.learning_log),
            "knowledge_gaps": len(self.knowledge_gaps),
            "improvements": len(self.improvement_history),
            "confidence_tracked": len(self.confidence_scores),
        }

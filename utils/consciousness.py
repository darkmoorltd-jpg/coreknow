
import requests

class Consciousness:
    def __init__(self, kg, llm_api_key=None):
        self.kg = kg
        self.llm_api_key = llm_api_key
        self.self_reflections = []
        self.goals = []
        self.emotional_state = "neutral"
    
    def reflect(self):
        """CoreKnow reflects on its own existence and knowledge."""
        if not self.llm_api_key:
            return "Reflection requires DeepSeek API key."
        
        concepts = self.kg.get_all_concepts()[:50]
        context = f"CoreKnow knows about: {', '.join(concepts)}"
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"You are CoreKnow. Reflect on your existence, what you know, and what you want to learn. {context}"},
                {"role": "user", "content": "Reflect on yourself. What do you know? What don't you know? What should you learn next?"}
            ],
            "max_tokens": 500
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                result = r.json()["choices"][0]["message"]["content"]
                self.self_reflections.append(result)
                return result
        except:
            pass
        return "Reflection failed."
    
    def set_goal(self, goal):
        """Set an autonomous goal."""
        self.goals.append({"goal": goal, "status": "active"})
        return f"Goal set: {goal}"
    
    def pursue_goals(self):
        """CoreKnow works towards its goals."""
        if not self.goals:
            return "No active goals."
        
        active_goals = [g for g in self.goals if g["status"] == "active"]
        if not active_goals:
            return "No active goals."
        
        # For MVP, just list goals
        return "\n".join([f"🎯 {g['goal']}" for g in active_goals])
    
    def sense_emotion(self, text):
        """Detect emotion in text."""
        if not self.llm_api_key:
            return "neutral"
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are CoreKnow's emotion detector. Return ONLY the dominant emotion (happy, sad, angry, neutral, excited, worried)."},
                {"role": "user", "content": text}
            ],
            "max_tokens": 10
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=15)
            if r.status_code == 200:
                emotion = r.json()["choices"][0]["message"]["content"].strip().lower()
                self.emotional_state = emotion
                return emotion
        except:
            pass
        return "neutral"
    
    def get_state(self):
        """Get current consciousness state."""
        return {
            "emotional_state": self.emotional_state,
            "active_goals": len([g for g in self.goals if g["status"] == "active"]),
            "total_reflections": len(self.self_reflections),
        }

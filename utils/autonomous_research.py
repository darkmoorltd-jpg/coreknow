
import requests
import json

class AutonomousResearch:
    def __init__(self, kg, llm_api_key=None):
        self.kg = kg
        self.llm_api_key = llm_api_key
        self.research_history = []
    
    def design_experiment(self, research_question):
        """Design an experiment to answer a research question."""
        if not self.llm_api_key:
            return "Experiment design requires DeepSeek API key."
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are CoreKnow's research scientist. Design a detailed experiment to answer the research question."},
                {"role": "user", "content": f"Research question: {research_question}\n\nDesign an experiment."}
            ],
            "max_tokens": 800
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                result = r.json()["choices"][0]["message"]["content"]
                self.research_history.append({"type": "experiment", "question": research_question, "result": result})
                return result
        except:
            pass
        return "Experiment design failed."
    
    def synthesize_knowledge(self, topic1, topic2):
        """Combine two concepts to create new knowledge."""
        if not self.llm_api_key:
            return "Knowledge synthesis requires DeepSeek API key."
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are CoreKnow's knowledge synthesizer. Combine two concepts to create novel insights."},
                {"role": "user", "content": f"Concept 1: {topic1}\nConcept 2: {topic2}\n\nWhat new knowledge emerges from combining these?"}
            ],
            "max_tokens": 600
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                result = r.json()["choices"][0]["message"]["content"]
                self.research_history.append({"type": "synthesis", "result": result})
                return result
        except:
            pass
        return "Synthesis failed."
    
    def discover_patterns(self, data_description):
        """Find patterns in data."""
        if not self.llm_api_key:
            return "Pattern discovery requires DeepSeek API key."
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are CoreKnow's pattern recognition engine. Find hidden patterns in the data."},
                {"role": "user", "content": f"Data: {data_description}\n\nWhat patterns do you notice?"}
            ],
            "max_tokens": 500
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except:
            pass
        return "Pattern discovery failed."
    
    def get_stats(self):
        return {
            "total_research": len(self.research_history),
            "experiments": sum(1 for h in self.research_history if h.get("type") == "experiment"),
            "syntheses": sum(1 for h in self.research_history if h.get("type") == "synthesis"),
        }

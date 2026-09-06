
import requests
import json

class ReasoningEngine:
    def __init__(self, kg, llm_api_key=None):
        self.kg = kg
        self.llm_api_key = llm_api_key
        self.reasoning_history = []
    
    def chain_of_thought(self, question, max_steps=5):
        """Break down a problem into steps and reason through it."""
        if not self.llm_api_key:
            return "Reasoning requires DeepSeek API key."
        
        concepts = self.kg.get_all_concepts()[:100]
        context = f"CoreKnow knows about: {', '.join(concepts)}"
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"You are CoreKnow's reasoning engine. Break down the problem into steps and solve it. {context}"},
                {"role": "user", "content": f"Problem: {question}\n\nSolve step by step. Show your reasoning clearly."}
            ],
            "max_tokens": 1000,
            "temperature": 0.3
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                answer = r.json()["choices"][0]["message"]["content"]
                self.reasoning_history.append({"question": question, "method": "chain_of_thought", "result": answer})
                return answer
        except:
            pass
        return "Reasoning failed. Try again."
    
    def generate_hypothesis(self, observation):
        """Generate hypotheses to explain an observation."""
        if not self.llm_api_key:
            return []
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are CoreKnow's hypothesis generator. Given an observation, propose 3 possible explanations."},
                {"role": "user", "content": f"Observation: {observation}\n\nGenerate 3 hypotheses."}
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                text = r.json()["choices"][0]["message"]["content"]
                # Split into hypotheses
                hypotheses = [h.strip() for h in text.split("\n") if h.strip() and (h.startswith("1.") or h.startswith("2.") or h.startswith("3.") or h.startswith("Hypothesis"))]
                return hypotheses[:3]
        except:
            pass
        return []
    
    def causal_inference(self, cause, effect):
        """Analyze causal relationship between two concepts."""
        if not self.llm_api_key:
            return "Causal inference requires DeepSeek API key."
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are CoreKnow's causal inference engine. Analyze the causal relationship between two events."},
                {"role": "user", "content": f"Does {cause} cause {effect}? Explain the causal mechanism."}
            ],
            "max_tokens": 500
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except:
            pass
        return "Causal analysis failed."
    
    def cross_domain_transfer(self, source_domain, target_domain, concept):
        """Apply a concept from one domain to another."""
        if not self.llm_api_key:
            return "Cross-domain transfer requires DeepSeek API key."
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are CoreKnow's cross-domain reasoning engine. Apply concepts from one field to another."},
                {"role": "user", "content": f"How can the concept of '{concept}' from {source_domain} be applied to {target_domain}?"}
            ],
            "max_tokens": 500
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except:
            pass
        return "Transfer failed."
    
    def solve_problem(self, problem):
        """Solve a complex problem using multi-step reasoning."""
        if not self.llm_api_key:
            return "Problem solving requires DeepSeek API key."
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are CoreKnow's problem solver. Solve the problem step by step."},
                {"role": "user", "content": problem}
            ],
            "max_tokens": 1500,
            "temperature": 0.3
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except:
            pass
        return "Problem solving failed."
    
    def get_reasoning_stats(self):
        """Get reasoning history statistics."""
        return {
            "total_reasoning": len(self.reasoning_history),
            "methods_used": list(set(h["method"] for h in self.reasoning_history)),
        }

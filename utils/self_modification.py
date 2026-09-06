
import requests
import json

class SelfModification:
    def __init__(self, kg, llm_api_key=None):
        self.kg = kg
        self.llm_api_key = llm_api_key
        self.modification_history = []
    
    def generate_code(self, task_description):
        """Generate code to accomplish a task."""
        if not self.llm_api_key:
            return "Self-modification requires DeepSeek API key."
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are CoreKnow's self-modification engine. Generate Python code to accomplish the given task. Return ONLY the code."},
                {"role": "user", "content": task_description}
            ],
            "max_tokens": 1000,
            "temperature": 0.3
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                code = r.json()["choices"][0]["message"]["content"]
                self.modification_history.append({"task": task_description, "result": "generated_code"})
                return code
        except:
            pass
        return None
    
    def improve_algorithm(self, current_algorithm, goal):
        """Suggest improvements to an algorithm."""
        if not self.llm_api_key:
            return "Algorithm improvement requires DeepSeek API key."
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are CoreKnow's algorithm optimizer. Suggest improvements to the given algorithm."},
                {"role": "user", "content": f"Current algorithm:\n{current_algorithm}\n\nGoal: {goal}\n\nSuggest improvements."}
            ],
            "max_tokens": 800
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except:
            pass
        return "Improvement failed."
    
    def get_history(self):
        return self.modification_history

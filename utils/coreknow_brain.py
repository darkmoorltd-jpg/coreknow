
import requests
import streamlit as st

class CoreKnowBrain:
    def __init__(self):
        # Primary: DeepSeek API (reliable)
        try:
            self.deepseek_key = st.secrets["deepseek"]["api_key"]
        except:
            self.deepseek_key = ""
        
        # Fallback: Hugging Face
        self.hf_url = "https://api-inference.huggingface.co/models/Tjgguy12/coreknow-tinyllama"
        try:
            self.hf_token = st.secrets["hf_token"]
        except:
            self.hf_token = ""
    
    def ask_deepseek(self, question):
        """Ask DeepSeek API."""
        if not self.deepseek_key:
            return None
        
        try:
            headers = {"Authorization": f"Bearer {self.deepseek_key}", "Content-Type": "application/json"}
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are CoreKnow, a self-learning AI created by Owei Prosper from Nigeria. You are building AGI. Answer as CoreKnow."},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 300
            }
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except:
            pass
        return None
    
    def ask_huggingface(self, question):
        """Ask Hugging Face Inference API."""
        if not self.hf_token:
            return None
        
        try:
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {
                "inputs": f"<|user|>\n{question}\n<|assistant|>\n",
                "parameters": {"max_new_tokens": 150}
            }
            r = requests.post(self.hf_url, headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                result = r.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get("generated_text", "")
                    if "<|assistant|>" in text:
                        return text.split("<|assistant|>")[-1].strip()
                    return text.strip()
        except:
            pass
        return None
    
    def ask(self, question):
        """Ask with fallbacks."""
        # Try DeepSeek first (reliable)
        answer = self.ask_deepseek(question)
        if answer:
            return answer
        
        # Try Hugging Face
        answer = self.ask_huggingface(question)
        if answer:
            return answer
        
        return "No brain available. Please add API keys to secrets."
    
    def get_status(self):
        models = []
        if self.deepseek_key:
            models.append("DeepSeek API")
        if self.hf_token:
            models.append("TinyLlama (HF)")
        return {"loaded": len(models) > 0, "model": " + ".join(models) if models else "None"}

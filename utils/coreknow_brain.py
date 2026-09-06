
import requests
import streamlit as st

class CoreKnowBrain:
    def __init__(self):
        try:
            self.deepseek_key = st.secrets["deepseek"]["api_key"]
        except:
            self.deepseek_key = ""
    
    def ask(self, question):
        if not self.deepseek_key:
            return "Add deepseek api_key to Streamlit secrets."
        
        try:
            headers = {"Authorization": f"Bearer {self.deepseek_key}", "Content-Type": "application/json"}
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are CoreKnow, a self-learning AI created by Owei Prosper from Nigeria. You are building AGI from Africa. Answer as CoreKnow."},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            else:
                return f"Brain error: {r.status_code}"
        except Exception as e:
            return f"Error: {e}"
    
    def get_status(self):
        return {"loaded": bool(self.deepseek_key), "model": "DeepSeek API"}

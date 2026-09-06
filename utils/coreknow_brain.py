
import requests
import streamlit as st

class CoreKnowBrain:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/Tjgguy12/coreknow-tinyllama"
        # Get token from Streamlit secrets (no hardcoding)
        try:
            self.hf_token = st.secrets["hf_token"]
        except:
            self.hf_token = ""
    
    def ask(self, question):
        """Ask CoreKnow's brain via Hugging Face Inference API."""
        if not self.hf_token:
            return "Please add hf_token to Streamlit secrets."
        
        try:
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {
                "inputs": f"<|user|>\n{question}\n<|assistant|>\n",
                "parameters": {"max_new_tokens": 150, "temperature": 0.7}
            }
            r = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if r.status_code == 200:
                result = r.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get("generated_text", "")
                    if "<|assistant|>" in text:
                        answer = text.split("<|assistant|>")[-1].strip()
                    else:
                        answer = text.strip()
                    return answer
                else:
                    return "Brain returned empty response."
            elif r.status_code == 503:
                return "Brain is loading. Please try again in a minute."
            else:
                return f"Brain error: {r.status_code}"
        except Exception as e:
            return f"Error: {e}"
    
    def get_status(self):
        return {"loaded": True, "model": "TinyLlama (Hugging Face API)"}

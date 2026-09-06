
import requests
import streamlit as st
import zipfile
import io
import os

class CoreKnowBrain:
    def __init__(self):
        # Google Drive file ID for TinyLlama adapter
        self.gdrive_file_id = "1z4cRmz65Wrop1HSTEywJcF4gubTxq0ov"
        self.gdrive_url = f"https://drive.google.com/uc?id={self.gdrive_file_id}&export=download"
        
        # DeepSeek as reliable fallback
        try:
            self.deepseek_key = st.secrets["deepseek"]["api_key"]
        except:
            self.deepseek_key = ""
    
    def ask_from_drive(self, question):
        """Download TinyLlama from Google Drive and ask."""
        try:
            print("Downloading brain from Google Drive...")
            r = requests.get(self.gdrive_url, timeout=60, stream=True)
            
            # Handle Google Drive redirect for large files
            if "confirm" in r.url or r.status_code != 200:
                # Google Drive requires confirmation for large files
                import re
                confirm_token = None
                for key, value in r.cookies.items():
                    if key.startswith("download_warning"):
                        confirm_token = value
                
                if confirm_token:
                    r = requests.get(f"{self.gdrive_url}&confirm={confirm_token}", timeout=60, stream=True)
            
            zip_data = io.BytesIO(r.content)
            
            print("Extracting brain...")
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                zip_ref.extractall("/tmp/coreknow-brain")
            
            print("Loading model...")
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            tokenizer = AutoTokenizer.from_pretrained("/tmp/coreknow-brain")
            model = AutoModelForCausalLM.from_pretrained(
                "/tmp/coreknow-brain",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
            )
            
            prompt = f"<|user|>\n{question}\n<|assistant|>\n"
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )
            
            answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
            answer = answer.split("<|assistant|>")[-1].strip()
            
            # Cleanup
            import shutil
            shutil.rmtree("/tmp/coreknow-brain", ignore_errors=True)
            
            return answer
        except Exception as e:
            print(f"Drive brain failed: {e}")
            return None
    
    def ask_deepseek(self, question):
        """Ask DeepSeek API."""
        if not self.deepseek_key:
            return None
        
        try:
            headers = {"Authorization": f"Bearer {self.deepseek_key}", "Content-Type": "application/json"}
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are CoreKnow, a self-learning AI created by Owei Prosper from Nigeria."},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except:
            pass
        return None
    
    def ask(self, question):
        """Try Google Drive brain first, fallback to DeepSeek."""
        # Try DeepSeek first (reliable and fast)
        answer = self.ask_deepseek(question)
        if answer:
            return answer
        
        # Try Google Drive brain
        answer = self.ask_from_drive(question)
        if answer:
            return answer
        
        return "Brain unavailable. Add API keys to secrets."
    
    def get_status(self):
        models = []
        if self.deepseek_key:
            models.append("DeepSeek API")
        models.append("Google Drive Brain")
        return {"loaded": True, "model": " + ".join(models)}

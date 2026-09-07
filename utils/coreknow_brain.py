
import requests
import streamlit as st
import zipfile
import io
import os
import shutil

class CoreKnowBrain:
    def __init__(self):
        self.brain_url = "https://github.com/darkmoorltd-jpg/coreknow/releases/download/v1.0-distilgpt2/distilgpt2-coreknow.zip"
        self.model_loaded = False
        self.model = None
        self.tokenizer = None
    
    def load_brain(self):
        try:
            print("Downloading brain...")
            r = requests.get(self.brain_url, timeout=120)
            
            if r.status_code != 200:
                return False
            
            zip_data = r.content
            
            if os.path.exists("/tmp/coreknow-brain"):
                shutil.rmtree("/tmp/coreknow-brain")
            
            zip_buffer = io.BytesIO(zip_data)
            with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                zip_ref.extractall("/tmp/coreknow-brain")
            
            print("Loading model...")
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained("/tmp/coreknow-brain")
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = AutoModelForCausalLM.from_pretrained(
                "/tmp/coreknow-brain",
                low_cpu_mem_usage=True,
            )
            self.model.eval()
            
            self.model_loaded = True
            return True
        except Exception as e:
            print(f"Load failed: {e}")
            return False
    
    def ask(self, question):
        if not self.model_loaded:
            if not self.load_brain():
                return "Brain failed to load."
        
        try:
            import torch
            
            prompt = f"Question: {question}\nAnswer:"
            
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=50)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=50,
                    temperature=0.9,
                    do_sample=True,
                    top_p=0.95,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract answer part
            if "Answer:" in answer:
                answer = answer.split("Answer:")[-1].strip()
            
            # If answer is empty or too short, return fallback
            if not answer or len(answer) < 2:
                return "I am CoreKnow, a self-learning AI from Nigeria."
            
            return answer
        except Exception as e:
            return f"Error: {e}"
    
    def get_status(self):
        if self.model_loaded:
            return {"loaded": True, "model": "DistilGPT-2 (Own Brain)"}
        else:
            return {"loaded": False, "model": "Loads on first question"}

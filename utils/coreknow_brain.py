
import requests
import streamlit as st
import zipfile
import io
import os
import shutil

class CoreKnowBrain:
    def __init__(self):
        # GitHub Release URL - reliable
        self.brain_url = "https://github.com/darkmoorltd-jpg/coreknow/releases/download/v1.0-distilgpt2/distilgpt2-coreknow.zip"
        self.model_loaded = False
        self.model = None
        self.tokenizer = None
    
    def load_brain(self):
        """Download from GitHub Release (works on Streamlit Cloud)."""
        try:
            print("📥 Downloading brain from GitHub Release...")
            r = requests.get(self.brain_url, timeout=120)
            
            if r.status_code != 200:
                print(f"Download failed: {r.status_code}")
                return False
            
            zip_data = r.content
            print(f"Downloaded: {len(zip_data) / 1024 / 1024:.1f} MB")
            
            # Extract
            if os.path.exists("/tmp/coreknow-brain"):
                shutil.rmtree("/tmp/coreknow-brain")
            
            zip_buffer = io.BytesIO(zip_data)
            with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                zip_ref.extractall("/tmp/coreknow-brain")
            
            print("✅ Extracted")
            
            # Load model
            print("🧠 Loading DistilGPT-2...")
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained("/tmp/coreknow-brain")
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = AutoModelForCausalLM.from_pretrained(
                "/tmp/coreknow-brain",
                low_cpu_mem_usage=True,
            )
            
            self.model_loaded = True
            print("✅ Brain loaded!")
            return True
        except Exception as e:
            print(f"Failed: {e}")
            return False
    
    def ask(self, question):
        if not self.model_loaded:
            if not self.load_brain():
                return "Brain failed to load."
        
        try:
            prompt = f"Question: {question}\nAnswer: "
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)
            
            import torch
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            
            answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            answer = answer.split("Answer:")[-1].strip()
            return answer
        except Exception as e:
            return f"Error: {e}"
    
    def get_status(self):
        if self.model_loaded:
            return {"loaded": True, "model": "DistilGPT-2 (Own Brain)"}
        else:
            return {"loaded": False, "model": "Loads on first question"}

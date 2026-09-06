
import requests
import streamlit as st
import zipfile
import io
import os
import shutil

class CoreKnowBrain:
    def __init__(self):
        # Google Drive file ID for TinyLlama adapter
        self.gdrive_file_id = "1z4cRmz65Wrop1HSTEywJcF4gubTxq0ov"
        self.gdrive_url = f"https://drive.google.com/uc?id={self.gdrive_file_id}&export=download"
        self.model_loaded = False
        self.model = None
        self.tokenizer = None
    
    def download_brain(self):
        """Download TinyLlama from Google Drive and load it."""
        try:
            print("📥 Downloading brain from Google Drive...")
            
            # First attempt
            session = requests.Session()
            r = session.get(self.gdrive_url, timeout=60, stream=True)
            
            # Handle Google Drive large file confirmation
            if r.status_code == 200 and "text/html" in r.headers.get("Content-Type", ""):
                # Need to extract confirm token
                import re
                match = re.search(r'confirm=([0-9A-Za-z_]+)', r.text)
                if match:
                    confirm_token = match.group(1)
                    r = session.get(f"{self.gdrive_url}&confirm={confirm_token}", timeout=60, stream=True)
            
            if r.status_code != 200:
                print(f"Download failed: {r.status_code}")
                return False
            
            zip_data = io.BytesIO(r.content)
            
            print("📦 Extracting brain...")
            # Clean old
            if os.path.exists("/tmp/coreknow-brain"):
                shutil.rmtree("/tmp/coreknow-brain")
            
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                zip_ref.extractall("/tmp/coreknow-brain")
            
            print("🧠 Loading model...")
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained("/tmp/coreknow-brain")
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model = AutoModelForCausalLM.from_pretrained(
                "/tmp/coreknow-brain",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
            )
            
            self.model_loaded = True
            print("✅ Brain loaded!")
            return True
        except Exception as e:
            print(f"Brain load failed: {e}")
            return False
    
    def ask(self, question):
        """Ask the Google Drive brain."""
        if not self.model_loaded:
            print("Loading brain...")
            success = self.download_brain()
            if not success:
                return "Brain failed to load. Check Google Drive link."
        
        try:
            prompt = f"<|user|>\n{question}\n<|assistant|>\n"
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
            
            import torch
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            
            answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            answer = answer.split("<|assistant|>")[-1].strip()
            return answer
        except Exception as e:
            return f"Error: {e}"
    
    def get_status(self):
        if self.model_loaded:
            return {"loaded": True, "model": "TinyLlama (Google Drive)"}
        else:
            return {"loaded": False, "model": "Not loaded yet"}

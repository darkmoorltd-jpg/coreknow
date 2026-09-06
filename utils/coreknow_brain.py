
import requests
import streamlit as st
import zipfile
import io
import os
import shutil

class CoreKnowBrain:
    def __init__(self):
        # Google Drive file ID
        self.gdrive_file_id = "1HRye-te9xhapdemKqD840Ma9DRCHL5f9"
        self.model_loaded = False
        self.model = None
        self.tokenizer = None
    
    def download_from_gdrive(self):
        """Download from Google Drive using gdown method."""
        try:
            # Direct download URL
            direct_url = f"https://drive.google.com/uc?export=download&id={self.gdrive_file_id}"
            
            print("📥 Downloading brain from Google Drive...")
            
            session = requests.Session()
            r = session.get(direct_url, timeout=120, stream=True)
            
            # Handle large file confirmation
            if r.status_code == 200 and "text/html" in r.headers.get("Content-Type", ""):
                import re
                match = re.search(r'confirm=([0-9A-Za-z_]+)', r.text)
                if match:
                    confirm_token = match.group(1)
                    r = session.get(f"{direct_url}&confirm={confirm_token}", timeout=120, stream=True)
            
            if r.status_code != 200:
                print(f"Download failed: {r.status_code}")
                return False
            
            zip_data = r.content
            print(f"Downloaded: {len(zip_data) / 1024 / 1024:.1f} MB")
            
            if len(zip_data) < 10000:
                print("File too small - likely error")
                return False
            
            # Extract
            if os.path.exists("/tmp/coreknow-brain"):
                shutil.rmtree("/tmp/coreknow-brain")
            
            zip_buffer = io.BytesIO(zip_data)
            with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
                zip_ref.extractall("/tmp/coreknow-brain")
            
            print("✅ Extracted successfully")
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False
    
    def load_model(self):
        """Load the model."""
        try:
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
            print(f"Model load failed: {e}")
            return False
    
    def ask(self, question):
        """Ask the brain."""
        if not self.model_loaded:
            if not self.download_from_gdrive():
                return "Failed to download brain."
            if not self.load_model():
                return "Failed to load model."
        
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

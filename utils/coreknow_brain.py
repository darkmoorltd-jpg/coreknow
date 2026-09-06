
import requests
import streamlit as st
import zipfile
import io
import os
import shutil

class CoreKnowBrain:
    def __init__(self):
        # Google Drive file ID
        self.gdrive_file_id = "1z4cRmz65Wrop1HSTEywJcF4gubTxq0ov"
        self.model_loaded = False
        self.model = None
        self.tokenizer = None
    
    def download_from_gdrive(self):
        """Download file from Google Drive using gdown approach."""
        try:
            # Use the direct download URL format
            direct_url = f"https://drive.google.com/uc?export=download&id={self.gdrive_file_id}"
            
            print(f"Downloading from: {direct_url}")
            
            session = requests.Session()
            r = session.get(direct_url, timeout=60, stream=True)
            
            # Check if we need to confirm (large file)
            if "confirm" in r.text.lower() or "warning" in r.text.lower():
                # Extract confirm token
                import re
                match = re.search(r'name="confirm" value="([^"]+)"', r.text)
                if match:
                    confirm_token = match.group(1)
                    print(f"Confirming download with token: {confirm_token[:10]}...")
                    r = session.get(f"{direct_url}&confirm={confirm_token}", timeout=60, stream=True)
            
            if r.status_code != 200:
                print(f"Download failed: {r.status_code}")
                return False
            
            # Check if it's actually a zip file
            content_type = r.headers.get("Content-Type", "")
            print(f"Content-Type: {content_type}")
            
            # Save and verify
            zip_data = r.content
            print(f"Downloaded: {len(zip_data) / 1024 / 1024:.1f} MB")
            
            if len(zip_data) < 10000:  # Less than 10 KB = probably error page
                print("Downloaded file too small, likely error page")
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
        """Load the model from extracted files."""
        try:
            print("Loading TinyLlama...")
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
            print("✅ Model loaded!")
            return True
        except Exception as e:
            print(f"Model load error: {e}")
            return False
    
    def ask(self, question):
        """Ask the brain."""
        if not self.model_loaded:
            print("Downloading brain...")
            if not self.download_from_gdrive():
                return "Failed to download brain from Google Drive."
            
            print("Loading model...")
            if not self.load_model():
                return "Failed to load model."
        
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
            return {"loaded": False, "model": "Will load on first question"}

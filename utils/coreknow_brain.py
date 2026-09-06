
import os
import requests
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import zipfile
import io

class CoreKnowBrain:
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.loaded = False
    
    def download_model(self, model_name, url):
        """Download fine-tuned adapter from GitHub Release."""
        os.makedirs("brains", exist_ok=True)
        model_path = f"brains/{model_name}"
        
        if os.path.exists(model_path) and os.listdir(model_path):
            print(f"{model_name} already downloaded")
            return model_path
        
        print(f"Downloading {model_name} brain from {url}...")
        try:
            r = requests.get(url, stream=True, timeout=300, allow_redirects=True)
            r.raise_for_status()
            
            # Save zip
            zip_path = f"brains/{model_name}.zip"
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
            
            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(model_path)
            
            os.remove(zip_path)
            print(f"✅ {model_name} downloaded and extracted")
            return model_path
        except Exception as e:
            print(f"Download failed: {e}")
            return None
    
    def load_tinyllama(self):
        """Load TinyLlama (small, fits free tier)."""
        model_path = self.download_model(
            "tinyllama",
            "https://github.com/darkmoorltd-jpg/coreknow/releases/download/v1.0-tinyllama/tinyllama-coreknow.zip"
        )
        
        if not model_path:
            return
        
        base_model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        try:
            tokenizer = AutoTokenizer.from_pretrained(base_model)
            tokenizer.pad_token = tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                base_model,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
            )
            
            from peft import PeftModel
            model = PeftModel.from_pretrained(model, model_path)
            
            self.models["tinyllama"] = model
            self.tokenizers["tinyllama"] = tokenizer
            print("✅ TinyLlama loaded")
        except Exception as e:
            print(f"TinyLlama load failed: {e}")
    
    def load_mistral(self):
        """Load Mistral 7B (needs more RAM)."""
        model_path = self.download_model(
            "mistral",
            "https://github.com/darkmoorltd-jpg/coreknow/releases/download/v1.0-mistral/mistral-coreknow.zip"
        )
        
        if not model_path:
            return
        
        base_model = "mistralai/Mistral-7B-Instruct-v0.2"
        try:
            tokenizer = AutoTokenizer.from_pretrained(base_model)
            tokenizer.pad_token = tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                base_model,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
            )
            
            from peft import PeftModel
            model = PeftModel.from_pretrained(model, model_path)
            
            self.models["mistral"] = model
            self.tokenizers["mistral"] = tokenizer
            print("✅ Mistral loaded")
        except Exception as e:
            print(f"Mistral load failed: {e}")
    
    def load_all(self):
        """Load available models."""
        if self.loaded:
            return
        
        # Load TinyLlama first (smaller)
        self.load_tinyllama()
        
        # Try Mistral (might fail on free tier)
        self.load_mistral()
        
        self.loaded = True
    
    def ask_model(self, model_name, question):
        """Ask a single model."""
        if model_name not in self.models:
            return None
        
        try:
            model = self.models[model_name]
            tokenizer = self.tokenizers[model_name]
            
            if "mistral" in model_name:
                prompt = f"<s>[INST] {question} [/INST]"
            else:
                prompt = f"<|user|>\n{question}\n<|assistant|>\n"
            
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256).to(model.device)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            if "mistral" in model_name:
                response = response.split("[/INST]")[-1].strip()
            else:
                response = response.split("<|assistant|>")[-1].strip()
            
            return response
        except Exception as e:
            return f"Error: {e}"
    
    def ask(self, question):
        """Ask both models and return best answer."""
        if not self.loaded:
            self.load_all()
        
        # Try TinyLlama first (faster, more likely loaded)
        if "tinyllama" in self.models:
            answer = self.ask_model("tinyllama", question)
            if answer and "Error" not in answer:
                return answer
        
        # Try Mistral if TinyLlama failed
        if "mistral" in self.models:
            answer = self.ask_model("mistral", question)
            if answer and "Error" not in answer:
                return answer
        
        return "No brain loaded. Please try again."
    
    def get_status(self):
        return {
            "loaded": self.loaded,
            "models": list(self.models.keys()),
        }

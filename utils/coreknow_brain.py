
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
        
        if os.path.exists(model_path):
            return model_path
        
        print(f"Downloading {model_name} brain...")
        r = requests.get(url, stream=True, timeout=300)
        r.raise_for_status()
        
        # Extract zip
        zip_path = f"brains/{model_name}.zip"
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=32768):
                f.write(chunk)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(model_path)
        
        os.remove(zip_path)
        return model_path
    
    def load_mistral(self):
        """Load fine-tuned Mistral 7B."""
        model_path = self.download_model(
            "mistral",
            "https://github.com/darkmoorltd-jpg/coreknow/releases/download/v1.0-mistral/mistral-coreknow.zip"
        )
        
        base_model = "mistralai/Mistral-7B-Instruct-v0.2"
        tokenizer = AutoTokenizer.from_pretrained(base_model)
        tokenizer.pad_token = tokenizer.eos_token
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=bnb_config,
            device_map="auto",
        )
        
        # Load LoRA adapter
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, model_path)
        
        self.models["mistral"] = model
        self.tokenizers["mistral"] = tokenizer
        print("✅ Mistral brain loaded")
    
    def load_tinyllama(self):
        """Load fine-tuned TinyLlama."""
        model_path = self.download_model(
            "tinyllama",
            "https://github.com/darkmoorltd-jpg/coreknow/releases/download/v1.0-tinyllama/tinyllama-coreknow.zip"
        )
        
        base_model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        tokenizer = AutoTokenizer.from_pretrained(base_model)
        tokenizer.pad_token = tokenizer.eos_token
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=bnb_config,
            device_map="auto",
        )
        
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, model_path)
        
        self.models["tinyllama"] = model
        self.tokenizers["tinyllama"] = tokenizer
        print("✅ TinyLlama brain loaded")
    
    def load_all(self):
        """Load both models."""
        if self.loaded:
            return
        
        try:
            self.load_tinyllama()
        except Exception as e:
            print(f"TinyLlama failed: {e}")
        
        try:
            self.load_mistral()
        except Exception as e:
            print(f"Mistral failed: {e}")
        
        self.loaded = True
    
    def ask_model(self, model_name, question):
        """Ask a single model."""
        if model_name not in self.models:
            return None
        
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
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the answer part
        if "mistral" in model_name:
            response = response.split("[/INST]")[-1].strip()
        else:
            response = response.split("<|assistant|>")[-1].strip()
        
        return response
    
    def ask(self, question):
        """Ask both models and combine answers."""
        if not self.loaded:
            self.load_all()
        
        answers = {}
        
        # Ask TinyLlama (fast)
        if "tinyllama" in self.models:
            answers["tinyllama"] = self.ask_model("tinyllama", question)
        
        # Ask Mistral (slower but better)
        if "mistral" in self.models:
            answers["mistral"] = self.ask_model("mistral", question)
        
        # Combine: prefer Mistral if available, fallback to TinyLlama
        if "mistral" in answers and answers["mistral"]:
            return answers["mistral"]
        elif "tinyllama" in answers and answers["tinyllama"]:
            return answers["tinyllama"]
        else:
            return "No brain loaded. Please add API keys or download models."
    
    def get_status(self):
        return {
            "loaded": self.loaded,
            "models": list(self.models.keys()),
        }

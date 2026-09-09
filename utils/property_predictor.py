
import requests
import json

class PropertyPredictor:
    """Predict molecular properties using DeepSeek or rule-based methods."""
    
    def __init__(self, llm_api_key=None):
        self.llm_api_key = llm_api_key
    
    def predict_toxicity(self, smiles):
        """Predict toxicity using rule-based heuristics."""
        # Simple heuristic based on known toxic fragments
        toxic_fragments = [
            "C#N",  # nitrile
            "N=O",  # nitroso
            "NO2",  # nitro
            "S",    # sulfur (often toxic)
            "P",    # phosphorus
            "As",   # arsenic
            "Hg",   # mercury
            "Pb",   # lead
        ]
        
        toxicity_score = 0
        found_fragments = []
        for frag in toxic_fragments:
            if frag in smiles:
                toxicity_score += 1
                found_fragments.append(frag)
        
        if toxicity_score >= 2:
            return {"score": "High", "fragments": found_fragments}
        elif toxicity_score == 1:
            return {"score": "Moderate", "fragments": found_fragments}
        else:
            return {"score": "Low", "fragments": []}
    
    def predict_solubility(self, smiles, molecular_weight=None, logp=None):
        """Predict water solubility using heuristics."""
        if molecular_weight is None or logp is None:
            # Use rough estimate from SMILES length
            mw_estimate = len(smiles) * 10
            logp_estimate = len(smiles) * 0.2
        else:
            mw_estimate = molecular_weight
            logp_estimate = logp
        
        if logp_estimate < 0:
            return "Highly soluble"
        elif logp_estimate < 2:
            return "Soluble"
        elif logp_estimate < 4:
            return "Moderately soluble"
        else:
            return "Poorly soluble"
    
    def predict_bioactivity(self, smiles, target=None):
        """Predict bioactivity using DeepSeek API."""
        if not self.llm_api_key:
            return "Bioactivity prediction requires DeepSeek API key."
        
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        prompt = f"Predict the potential bioactivity of this molecule (SMILES: {smiles})"
        if target:
            prompt += f" against target: {target}"
        prompt += ". Provide a realistic assessment based on drug-like properties."
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a medicinal chemistry expert. Provide realistic bioactivity predictions."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500
        }
        try:
            r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
        except:
            pass
        return "Prediction failed."
    
    def screen_drug_likeness(self, smiles_list):
        """Screen a list of molecules for drug-likeness."""
        results = []
        for smiles in smiles_list:
            # Simple heuristics
            mw = len(smiles) * 8  # rough estimate
            logp = len(smiles) * 0.15
            
            passes = True
            issues = []
            if mw > 500:
                passes = False
                issues.append("MW too high")
            if logp > 5:
                passes = False
                issues.append("LogP too high")
            
            results.append({
                "smiles": smiles,
                "passes": passes,
                "issues": issues,
                "estimated_mw": round(mw, 1),
                "estimated_logp": round(logp, 2),
            })
        return results


import random
from utils.molecular_parser import MolecularParser
from utils.property_predictor import PropertyPredictor
from utils.generative_chemistry import GenerativeChemistry

class DrugScreeningPipeline:
    """Complete drug discovery screening pipeline."""
    
    def __init__(self):
        self.parser = MolecularParser()
        self.predictor = PropertyPredictor()
        self.generator = GenerativeChemistry()
    
    def screen_candidates(self, smiles_list, target=None):
        """Screen a list of molecules for drug potential."""
        results = []
        
        for smiles in smiles_list:
            # Parse molecule
            mol_info = self.parser.parse_smiles(smiles)
            
            if "error" in mol_info:
                results.append({
                    "smiles": smiles,
                    "status": "rejected",
                    "reason": mol_info["error"],
                    "score": 0
                })
                continue
            
            # Check Lipinski
            drug_like = mol_info.get("drug_likeness", "")
            passes_lipinski = "Passes" in drug_like
            
            # Predict toxicity
            toxicity = self.predictor.predict_toxicity(smiles)
            
            # Calculate score
            score = 0
            if passes_lipinski:
                score += 40
            if toxicity["score"] == "Low":
                score += 30
            elif toxicity["score"] == "Moderate":
                score += 15
            
            # MW bonus
            mw = mol_info.get("molecular_weight", 500)
            if 200 < mw < 400:
                score += 20
            elif 400 <= mw < 500:
                score += 10
            
            # LogP bonus
            logp = mol_info.get("logp", 5)
            if 0 < logp < 3:
                score += 10
            
            results.append({
                "smiles": smiles,
                "status": "pass" if score >= 60 else "reject",
                "score": min(score, 100),
                "mw": mw,
                "logp": logp,
                "toxicity": toxicity["score"],
                "drug_likeness": drug_like,
            })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def run_discovery(self, target_name, num_candidates=20):
        """Run a complete discovery cycle."""
        # Generate candidates
        candidates = self.generator.generate_drug_like(num_candidates)
        
        # Screen candidates
        results = self.screen_candidates(candidates, target_name)
        
        # Get top candidates
        top_candidates = [r for r in results if r["status"] == "pass"][:5]
        
        return {
            "target": target_name,
            "total_generated": len(candidates),
            "passed_screening": len([r for r in results if r["status"] == "pass"]),
            "top_candidates": top_candidates,
            "all_results": results,
        }

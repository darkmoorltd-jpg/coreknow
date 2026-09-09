
import os
import sys

class MolecularParser:
    """Parse and analyze molecules using RDKit."""
    
    def __init__(self):
        self.rdkit_available = False
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, Draw
            self.Chem = Chem
            self.Descriptors = Descriptors
            self.Draw = Draw
            self.rdkit_available = True
        except ImportError:
            self.rdkit_available = False
    
    def parse_smiles(self, smiles):
        """Parse a SMILES string and return molecular info."""
        if not self.rdkit_available:
            return {"error": "RDKit not installed. Run: pip install rdkit"}
        
        try:
            mol = self.Chem.MolFromSmiles(smiles)
            if mol is None:
                return {"error": "Invalid SMILES"}
            
            return {
                "smiles": smiles,
                "molecular_weight": self.Descriptors.MolWt(mol),
                "logp": self.Descriptors.MolLogP(mol),
                "h_bond_donors": self.Descriptors.NumHDonors(mol),
                "h_bond_acceptors": self.Descriptors.NumHAcceptors(mol),
                "rotatable_bonds": self.Descriptors.NumRotatableBonds(mol),
                "rings": self.Descriptors.RingCount(mol),
                "formula": self.Chem.rdMolDescriptors.CalcMolFormula(mol),
                "drug_likeness": self._check_lipinski(mol),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _check_lipinski(self, mol):
        """Check Lipinski's Rule of 5."""
        mw = self.Descriptors.MolWt(mol)
        logp = self.Descriptors.MolLogP(mol)
        hbd = self.Descriptors.NumHDonors(mol)
        hba = self.Descriptors.NumHAcceptors(mol)
        
        violations = []
        if mw > 500:
            violations.append("MW > 500")
        if logp > 5:
            violations.append("LogP > 5")
        if hbd > 5:
            violations.append("HBD > 5")
        if hba > 10:
            violations.append("HBA > 10")
        
        if len(violations) <= 1:
            return "Passes Lipinski (drug-like)"
        else:
            return f"Fails Lipinski: {', '.join(violations)}"
    
    def get_descriptors(self, smiles):
        """Get all descriptors for a molecule."""
        if not self.rdkit_available:
            return {}
        
        mol = self.Chem.MolFromSmiles(smiles)
        if mol is None:
            return {}
        
        descriptors = {}
        for name, func in self.Descriptors.descList:
            try:
                descriptors[name] = func(mol)
            except:
                pass
        return descriptors
    
    def draw_molecule(self, smiles, output_path="/tmp/molecule.png"):
        """Draw molecule and return image path."""
        if not self.rdkit_available:
            return None
        
        mol = self.Chem.MolFromSmiles(smiles)
        if mol:
            self.Draw.MolToFile(mol, output_path)
            return output_path
        return None

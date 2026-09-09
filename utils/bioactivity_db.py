
import requests
import json

class BioactivityDB:
    """Query real bioactivity databases."""
    
    def __init__(self):
        self.chembl_base = "https://www.ebi.ac.uk/chembl/api/data"
        self.pubchem_base = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    
    def search_chembl(self, query, limit=10):
        """Search ChEMBL for compounds by name or SMILES."""
        results = []
        try:
            # Search by molecule name
            url = f"{self.chembl_base}/molecule/search.json?q={query}&limit={limit}"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                molecules = r.json().get("molecules", [])
                for mol in molecules:
                    results.append({
                        "chembl_id": mol.get("molecule_chembl_id", ""),
                        "name": mol.get("pref_name", ""),
                        "formula": mol.get("molecule_properties", {}).get("full_molformula", ""),
                        "mw": mol.get("molecule_properties", {}).get("full_mwt", ""),
                        "source": "ChEMBL"
                    })
        except:
            pass
        return results
    
    def search_pubchem(self, query, limit=10):
        """Search PubChem for compounds."""
        results = []
        try:
            # Search by name
            url = f"{self.pubchem_base}/compound/name/{query}/cids/JSON"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                cids = r.json().get("IdentifierList", {}).get("CID", [])
                for cid in cids[:limit]:
                    # Get compound info
                    info_url = f"{self.pubchem_base}/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName/JSON"
                    info_r = requests.get(info_url, timeout=15)
                    if info_r.status_code == 200:
                        props = info_r.json().get("PropertyTable", {}).get("Properties", [{}])[0]
                        results.append({
                            "cid": cid,
                            "name": props.get("IUPACName", ""),
                            "formula": props.get("MolecularFormula", ""),
                            "mw": props.get("MolecularWeight", ""),
                            "source": "PubChem"
                        })
        except:
            pass
        return results
    
    def get_bioactivities(self, chembl_id, limit=20):
        """Get bioactivity data for a ChEMBL compound."""
        results = []
        try:
            url = f"{self.chembl_base}/activity.json?molecule_chembl_id={chembl_id}&limit={limit}"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                activities = r.json().get("activities", [])
                for act in activities:
                    results.append({
                        "target": act.get("target_pref_name", ""),
                        "activity_type": act.get("standard_type", ""),
                        "value": act.get("standard_value", ""),
                        "units": act.get("standard_units", ""),
                    })
        except:
            pass
        return results
    
    def search_drug_target(self, target_name, limit=10):
        """Search for drugs that target a specific protein."""
        results = []
        try:
            # Search ChEMBL for target
            url = f"{self.chembl_base}/target/search.json?q={target_name}&limit=5"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                targets = r.json().get("targets", [])
                for target in targets:
                    target_id = target.get("target_chembl_id", "")
                    # Get compounds for this target
                    if target_id:
                        act_url = f"{self.chembl_base}/activity.json?target_chembl_id={target_id}&limit={limit}"
                        act_r = requests.get(act_url, timeout=15)
                        if act_r.status_code == 200:
                            activities = act_r.json().get("activities", [])
                            for act in activities:
                                results.append({
                                    "target": target.get("pref_name", ""),
                                    "molecule": act.get("molecule_chembl_id", ""),
                                    "activity": act.get("standard_value", ""),
                                    "units": act.get("standard_units", ""),
                                })
        except:
            pass
        return results

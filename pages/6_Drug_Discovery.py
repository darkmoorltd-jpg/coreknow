
import streamlit as st
from utils.molecular_parser import MolecularParser
from utils.property_predictor import PropertyPredictor
from utils.generative_chemistry import GenerativeChemistry
from utils.bioactivity_db import BioactivityDB
from utils.docking import MolecularDocking
from utils.drug_screening import DrugScreeningPipeline

st.set_page_config(page_title="Drug Discovery", page_icon="💊", layout="wide")

st.markdown("""
<style>
    .stApp { background: radial-gradient(ellipse at 20% 50%, #0d1b2a 0%, #0a0e17 70%); color: #e0e0e0; }
    header, footer { visibility: hidden; }
    .title { font-size: 2.5rem; font-weight: 900; text-align: center; background: linear-gradient(135deg, #00e5ff, #7c4dff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 2rem; }
    .stButton > button { background: linear-gradient(135deg, #00e5ff, #7c4dff); color: white; font-weight: bold; }
    .result-card { background: #111827; border: 1px solid #1f2a44; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; }
    .pass { color: #00c853; font-weight: bold; }
    .reject { color: #ff1744; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">💊 Drug Discovery Module</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Molecular Analysis • Property Prediction • Generative Chemistry • Screening</div>', unsafe_allow_html=True)

# Initialize
parser = MolecularParser()
predictor = PropertyPredictor()
generator = GenerativeChemistry()
bio_db = BioactivityDB()
docking = MolecularDocking()
screening = DrugScreeningPipeline()

tab1, tab2, tab3, tab4 = st.tabs(["🔬 Analyze", "📊 Predict", "🧪 Generate", "🎯 Screen"])

with tab1:
    smiles = st.text_input("Enter SMILES", placeholder="e.g., CC(=O)OC1=CC=CC=C1C(=O)O (Aspirin)")
    if smiles:
        result = parser.parse_smiles(smiles)
        if "error" in result:
            st.error(result["error"])
            st.info("RDKit may not be installed. Install: pip install rdkit")
        else:
            st.markdown(f"""
            <div class="result-card">
                <p><strong>Formula:</strong> {result.get('formula', 'N/A')}</p>
                <p><strong>MW:</strong> {result.get('molecular_weight', 'N/A'):.2f}</p>
                <p><strong>LogP:</strong> {result.get('logp', 'N/A'):.2f}</p>
                <p><strong>Lipinski:</strong> {result.get('drug_likeness', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Search Databases")
    query = st.text_input("Search compound", placeholder="e.g., aspirin")
    if query and st.button("Search ChEMBL & PubChem"):
        with st.spinner("Searching..."):
            chembl_results = bio_db.search_chembl(query)
            pubchem_results = bio_db.search_pubchem(query)
        
        if chembl_results:
            st.markdown("#### ChEMBL Results")
            for r in chembl_results:
                st.markdown(f"**{r['name'] or r['chembl_id']}** – MW: {r['mw']}")
        
        if pubchem_results:
            st.markdown("#### PubChem Results")
            for r in pubchem_results:
                st.markdown(f"**{r['name'][:50]}** – MW: {r['mw']}")

with tab2:
    smiles_input = st.text_input("SMILES", key="pred_smiles")
    if smiles_input:
        col1, col2, col3 = st.columns(3)
        with col1:
            toxicity = predictor.predict_toxicity(smiles_input)
            st.markdown(f"**Toxicity:** {toxicity['score']}")
        with col2:
            mw = len(smiles_input) * 8
            logp = len(smiles_input) * 0.15
            solubility = predictor.predict_solubility(smiles_input, mw, logp)
            st.markdown(f"**Solubility:** {solubility}")
        with col3:
            binding = docking.score_binding("receptor.pdb", smiles_input)
            st.markdown(f"**Binding Energy:** {binding['binding_energy']} kcal/mol")
            st.caption(binding['interpretation'])

with tab3:
    gen_type = st.selectbox("Generation Type", ["Random", "Drug-Like", "Mutate"])
    num = st.slider("Number", 1, 20, 5)
    
    if gen_type == "Random" and st.button("Generate Random"):
        molecules = generator.generate_random_smiles(num)
        for i, mol in enumerate(molecules, 1):
            st.markdown(f"**{i}.** `{mol}`")
    
    elif gen_type == "Drug-Like" and st.button("Generate Drug-Like"):
        molecules = generator.generate_drug_like(num)
        for i, mol in enumerate(molecules, 1):
            st.markdown(f"**{i}.** `{mol}`")
    
    elif gen_type == "Mutate":
        base = st.text_input("Base SMILES")
        if base and st.button("Mutate"):
            mutations = generator.mutate_molecule(base, num)
            for i, mut in enumerate(mutations, 1):
                st.markdown(f"**{i}.** `{mut}`")

with tab4:
    st.markdown("### 🎯 Drug Screening Pipeline")
    target = st.text_input("Target name", placeholder="e.g., SARS-CoV-2 protease")
    num_candidates = st.slider("Candidates", 5, 50, 20)
    
    if st.button("Run Discovery Cycle", type="primary"):
        with st.spinner("Generating and screening candidates..."):
            results = screening.run_discovery(target, num_candidates)
        
        st.success(f"✅ {results['passed_screening']} of {results['total_generated']} passed screening")
        
        if results["top_candidates"]:
            st.markdown("### Top Candidates")
            for i, cand in enumerate(results["top_candidates"], 1):
                status_class = "pass" if cand["status"] == "pass" else "reject"
                st.markdown(f"""
                <div class="result-card">
                    <p><strong>{i}. Score:</strong> {cand['score']}/100 <span class="{status_class}">{cand['status'].upper()}</span></p>
                    <p><code>{cand['smiles']}</code></p>
                    <p>MW: {cand['mw']:.0f} | LogP: {cand['logp']:.2f} | Toxicity: {cand['toxicity']}</p>
                </div>
                """, unsafe_allow_html=True)

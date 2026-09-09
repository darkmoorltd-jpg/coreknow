
import streamlit as st
from utils.molecular_parser import MolecularParser
from utils.property_predictor import PropertyPredictor
from utils.generative_chemistry import GenerativeChemistry

st.set_page_config(page_title="Drug Discovery", page_icon="💊", layout="wide")

st.markdown("""
<style>
    .stApp { background: radial-gradient(ellipse at 20% 50%, #0d1b2a 0%, #0a0e17 70%); color: #e0e0e0; }
    header, footer { visibility: hidden; }
    .title { font-size: 2.5rem; font-weight: 900; text-align: center; background: linear-gradient(135deg, #00e5ff, #7c4dff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 2rem; }
    .stButton > button { background: linear-gradient(135deg, #00e5ff, #7c4dff); color: white; font-weight: bold; }
    .result-card { background: #111827; border: 1px solid #1f2a44; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">💊 Drug Discovery Module</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Molecular Analysis • Property Prediction • Generative Chemistry</div>', unsafe_allow_html=True)

# Initialize
parser = MolecularParser()
predictor = PropertyPredictor()
generator = GenerativeChemistry()

tab1, tab2, tab3 = st.tabs(["🔬 Molecular Analysis", "📊 Property Prediction", "🧪 Generative Chemistry"])

with tab1:
    st.markdown("### 🔬 Analyze a Molecule")
    smiles = st.text_input("Enter SMILES", placeholder="e.g., CC(=O)OC1=CC=CC=C1C(=O)O (Aspirin)")
    
    if smiles:
        result = parser.parse_smiles(smiles)
        
        if "error" in result:
            st.error(result["error"])
            st.info("Note: RDKit may not be installed. Install with: pip install rdkit")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Molecular Properties")
                st.markdown(f"""
                <div class="result-card">
                    <p><strong>Formula:</strong> {result.get('formula', 'N/A')}</p>
                    <p><strong>Molecular Weight:</strong> {result.get('molecular_weight', 'N/A'):.2f}</p>
                    <p><strong>LogP:</strong> {result.get('logp', 'N/A'):.2f}</p>
                    <p><strong>H-Bond Donors:</strong> {result.get('h_bond_donors', 'N/A')}</p>
                    <p><strong>H-Bond Acceptors:</strong> {result.get('h_bond_acceptors', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("#### Drug-Likeness")
                st.markdown(f"""
                <div class="result-card">
                    <p><strong>Rotatable Bonds:</strong> {result.get('rotatable_bonds', 'N/A')}</p>
                    <p><strong>Rings:</strong> {result.get('rings', 'N/A')}</p>
                    <p><strong>Lipinski:</strong> {result.get('drug_likeness', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Common Drug SMILES for Testing")
    examples = {
        "Aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "Paracetamol": "CC(=O)NC1=CC=C(O)C=C1",
        "Caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "Ibuprofen": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",
        "Metformin": "CN(C)C(=N)N=C(N)N",
    }
    
    cols = st.columns(len(examples))
    for i, (name, smi) in enumerate(examples.items()):
        with cols[i]:
            if st.button(name, key=f"example_{name}"):
                st.session_state["smiles_test"] = smi
                st.rerun()

with tab2:
    st.markdown("### 📊 Predict Properties")
    smiles_input = st.text_input("SMILES for prediction", key="pred_smiles")
    
    if smiles_input:
        col1, col2, col3 = st.columns(3)
        with col1:
            toxicity = predictor.predict_toxicity(smiles_input)
            st.markdown(f"**Toxicity:** {toxicity['score']}")
            if toxicity['fragments']:
                st.caption(f"Fragments: {', '.join(toxicity['fragments'])}")
        
        with col2:
            # Estimate MW and LogP
            mw = len(smiles_input) * 8
            logp = len(smiles_input) * 0.15
            solubility = predictor.predict_solubility(smiles_input, mw, logp)
            st.markdown(f"**Solubility:** {solubility}")
            st.caption(f"Est. MW: {mw:.0f}, Est. LogP: {logp:.2f}")
        
        with col3:
            st.markdown(f"**Bioactivity:**")
            try:
                deepseek_key = st.secrets["deepseek"]["api_key"]
                predictor.llm_api_key = deepseek_key
                bioactivity = predictor.predict_bioactivity(smiles_input)
                st.write(bioactivity[:200] + "...")
            except:
                st.info("Add DeepSeek API key for bioactivity prediction.")

with tab3:
    st.markdown("### 🧪 Generate Novel Molecules")
    
    gen_type = st.selectbox("Generation Type", ["Random", "Drug-Like", "Mutate Existing"])
    
    num_molecules = st.slider("Number of molecules", 1, 20, 5)
    
    if gen_type == "Random":
        if st.button("Generate Random", type="primary"):
            molecules = generator.generate_random_smiles(num_molecules)
            st.markdown("### Generated Molecules")
            for i, mol in enumerate(molecules, 1):
                st.markdown(f"**{i}.** `{mol}`")
    
    elif gen_type == "Drug-Like":
        if st.button("Generate Drug-Like", type="primary"):
            molecules = generator.generate_drug_like(num_molecules)
            st.markdown("### Generated Drug-Like Molecules")
            for i, mol in enumerate(molecules, 1):
                st.markdown(f"**{i}.** `{mol}`")
    
    elif gen_type == "Mutate Existing":
        base_smiles = st.text_input("Base SMILES to mutate", placeholder="e.g., CC(=O)OC1=CC=CC=C1C(=O)O")
        if base_smiles and st.button("Mutate", type="primary"):
            mutations = generator.mutate_molecule(base_smiles, num_molecules)
            st.markdown("### Mutated Molecules")
            st.markdown(f"**Original:** `{base_smiles}`")
            for i, mut in enumerate(mutations, 1):
                st.markdown(f"**{i}.** `{mut}`")

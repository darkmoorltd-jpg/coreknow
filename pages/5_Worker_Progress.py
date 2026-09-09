
import streamlit as st
import time
from supabase import create_client
import json

st.set_page_config(page_title="Worker Progress", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .stApp { background: radial-gradient(ellipse at 20% 50%, #0d1b2a 0%, #0a0e17 70%); color: #e0e0e0; }
    header, footer { visibility: hidden; }
    .title { font-size: 2.5rem; font-weight: 900; text-align: center; background: linear-gradient(135deg, #00e5ff, #7c4dff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stat-card { background: #111827; border: 1px solid #1f2a44; border-radius: 10px; padding: 1rem; text-align: center; }
    .stat-number { font-size: 2rem; font-weight: 700; color: #00e5ff; }
    .stat-label { color: #8892b0; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📊 CoreKnow Worker Progress</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle" style="text-align:center;color:#8892b0;">Real-time autonomous learning monitor</div>', unsafe_allow_html=True)

# Supabase
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["service_key"]

@st.cache_resource
def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

client = get_client()

# Fetch all stats
def fetch_table_count(table):
    try:
        res = client.table(table).select("*", count="exact").execute()
        return res.count if res.count else 0
    except:
        return 0

# Get counts
doc_count = fetch_table_count("coreknow_documents")
chunk_count = fetch_table_count("coreknow_chunks")
paper_count = fetch_table_count("coreknow_biomed_papers")
kg_count = fetch_table_count("coreknow_kg")

# Get formula and entity stats from biomed papers
try:
    papers_res = client.table("coreknow_biomed_papers").select("formulas, entities, title, pmcid").order("id", desc=True).limit(50).execute()
    papers = papers_res.data if papers_res.data else []
    
    total_formulas = 0
    total_diseases = 0
    total_genes = 0
    total_compounds = 0
    
    for p in papers:
        try:
            formulas = json.loads(p.get("formulas", "[]")) if p.get("formulas") else []
            entities = json.loads(p.get("entities", "{}")) if p.get("entities") else {}
            total_formulas += len(formulas)
            total_diseases += len(entities.get("diseases", []))
            total_genes += len(entities.get("genes", []))
            total_compounds += len(entities.get("compounds", []))
        except:
            pass
except:
    papers = []
    total_formulas = 0
    total_diseases = 0
    total_genes = 0
    total_compounds = 0

# Display metrics
st.markdown("### 📈 Overall Stats")
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{paper_count}</div><div class="stat-label">Research Papers</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_formulas}</div><div class="stat-label">Formulas</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_diseases}</div><div class="stat-label">Diseases</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_genes}</div><div class="stat-label">Genes</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_compounds}</div><div class="stat-label">Compounds</div></div>', unsafe_allow_html=True)
with col6:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{kg_count}</div><div class="stat-label">KG Nodes</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Recent papers with extraction details
st.markdown("### 🕒 Recent Papers Extracted")
if papers:
    for p in papers[:15]:
        pmcid = p.get("pmcid", "N/A")
        title = p.get("title", "Untitled")[:80]
        try:
            formulas = json.loads(p.get("formulas", "[]")) if p.get("formulas") else []
            entities = json.loads(p.get("entities", "{}")) if p.get("entities") else {}
            num_formulas = len(formulas)
            diseases = entities.get("diseases", [])
            genes = entities.get("genes", [])
            compounds = entities.get("compounds", [])
        except:
            num_formulas = 0
            diseases = []
            genes = []
            compounds = []
        
        with st.expander(f"📄 {title}"):
            st.markdown(f"**PMCID:** {pmcid}")
            st.markdown(f"**Formulas ({num_formulas}):** {', '.join(formulas[:10])}")
            if diseases:
                st.markdown(f"**Diseases:** {', '.join(diseases[:5])}")
            if genes:
                st.markdown(f"**Genes:** {', '.join(genes[:5])}")
            if compounds:
                st.markdown(f"**Compounds:** {', '.join(compounds[:5])}")
else:
    st.info("No papers extracted yet. Run the worker in Colab to start.")

st.markdown("---")
st.caption("Auto-refreshes every 3 seconds")

time.sleep(3)
st.rerun()

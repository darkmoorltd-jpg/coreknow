
import streamlit as st
import time
from supabase import create_client
import json

st.set_page_config(page_title="CoreKnow Worker", page_icon="🧠", layout="wide")

# ============================================
# BADASS HUD STYLING
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

    .stApp { 
        background: radial-gradient(ellipse at 50% 50%, #0d1b2a 0%, #050810 100%);
        color: #e0e0e0;
        font-family: 'Rajdhani', sans-serif;
    }
    header, footer { visibility: hidden; }

    .hud-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #00e5ff 0%, #7c4dff 50%, #ff1744 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0,229,255,0.5);
        animation: pulse 2s infinite alternate;
    }

    @keyframes pulse {
        0% { filter: brightness(1); }
        100% { filter: brightness(1.3); }
    }

    .subtitle {
        text-align: center;
        color: #8892b0;
        font-size: 1rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    .stat-card {
        background: linear-gradient(145deg, #0d1117 0%, #111827 100%);
        border: 1px solid #1f2a44;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
    }
    .stat-card:hover {
        border-color: #00e5ff;
        box-shadow: 0 0 25px rgba(0,229,255,0.3);
        transform: translateY(-3px);
    }
    .stat-number {
        font-family: 'Orbitron', monospace;
        font-size: 2.2rem;
        font-weight: 700;
        color: #00e5ff;
        text-shadow: 0 0 10px rgba(0,229,255,0.5);
    }
    .stat-label {
        color: #8892b0;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 0.3rem;
    }

    .scan-line {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00e5ff, transparent);
        animation: scan 3s linear infinite;
        z-index: 999;
    }
    @keyframes scan {
        0% { top: 0; }
        100% { top: 100%; }
    }

    .status-dot {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #00c853;
        border-radius: 50%;
        margin-right: 8px;
        animation: blink 1s infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    .paper-expander {
        background: #0d1117;
        border: 1px solid #1f2a44;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.3rem 0;
    }

    .formula-tag {
        display: inline-block;
        background: #111827;
        border: 1px solid #7c4dff;
        border-radius: 4px;
        padding: 2px 8px;
        margin: 2px;
        font-family: 'Courier New', monospace;
        font-size: 0.7rem;
        color: #b388ff;
    }

    .disease-tag {
        display: inline-block;
        background: #1a0a0a;
        border: 1px solid #ff1744;
        border-radius: 4px;
        padding: 2px 8px;
        margin: 2px;
        font-size: 0.7rem;
        color: #ff5252;
    }

    .gene-tag {
        display: inline-block;
        background: #0a1a0a;
        border: 1px solid #00c853;
        border-radius: 4px;
        padding: 2px 8px;
        margin: 2px;
        font-size: 0.7rem;
        color: #69f0ae;
    }
</style>
""", unsafe_allow_html=True)

# Scan line animation
st.markdown('<div class="scan-line"></div>', unsafe_allow_html=True)

# Title
st.markdown('<div class="hud-title">🧠 COREKNOW WORKER</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Autonomous Biomedical Knowledge Engine</div>', unsafe_allow_html=True)

# Live status
st.markdown(f'<p style="text-align:center;color:#00c853;"><span class="status-dot"></span>LIVE — Auto-refreshing every 3s</p>', unsafe_allow_html=True)


# Sidebar Navigation
with st.sidebar:
    st.markdown("## 🧠 CoreKnow")
    st.markdown("---")
    st.markdown("### 📄 Pages")
    st.page_link("app.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/3_Deep_Search.py", label="🔍 Deep Search", use_container_width=True)
    st.page_link("pages/4_Browse_Knowledge.py", label="📚 Browse Knowledge", use_container_width=True)
    st.page_link("pages/5_Worker_Progress.py", label="📊 Worker Progress", use_container_width=True)
    st.page_link("pages/6_Drug_Discovery.py", label="💊 Drug Discovery", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 Stats")
    try:
        st.metric("Papers", paper_count)
        st.metric("Formulas", total_formulas)
        st.metric("KG Nodes", kg_count)
    except:
        pass


# Supabase
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["service_key"]

@st.cache_resource
def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

client = get_client()

def fetch_table_count(table):
    try:
        res = client.table(table).select("*", count="exact").execute()
        return res.count if res.count else 0
    except:
        return 0

# Get counts
paper_count = fetch_table_count("coreknow_biomed_papers")
kg_count = fetch_table_count("coreknow_kg")

# Get stats from papers
try:
    papers_res = client.table("coreknow_biomed_papers").select("formulas, entities, title, pmcid, full_text").order("id", desc=True).limit(20).execute()
    papers = papers_res.data if papers_res.data else []
    
    total_formulas = 0
    total_diseases = 0
    total_genes = 0
    total_compounds = 0
    total_chars = 0
    
    for p in papers:
        try:
            formulas = json.loads(p.get("formulas", "[]")) if p.get("formulas") else []
            entities = json.loads(p.get("entities", "{}")) if p.get("entities") else {}
            total_formulas += len(formulas)
            total_diseases += len(entities.get("diseases", []))
            total_genes += len(entities.get("genes", []))
            total_compounds += len(entities.get("compounds", []))
            total_chars += len(p.get("full_text", ""))
        except:
            pass
except:
    papers = []
    total_formulas = 0
    total_diseases = 0
    total_genes = 0
    total_compounds = 0
    total_chars = 0

# HUD Stats
st.markdown("### 📈 KNOWLEDGE METRICS")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{paper_count}</div><div class="stat-label">📄 Papers</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_formulas}</div><div class="stat-label">⚗️ Formulas</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_diseases}</div><div class="stat-label">🦠 Diseases</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_genes}</div><div class="stat-label">🧬 Genes</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_compounds}</div><div class="stat-label">💊 Compounds</div></div>', unsafe_allow_html=True)
with col6:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{kg_count}</div><div class="stat-label">🕸️ KG Nodes</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Recent papers
st.markdown("### 🕒 LIVE EXTRACTION FEED")
if papers:
    for p in papers[:10]:
        pmcid = p.get("pmcid", "N/A")
        title = p.get("title", "Untitled")[:70]
        full_text_len = len(p.get("full_text", ""))
        
        try:
            formulas = json.loads(p.get("formulas", "[]")) if p.get("formulas") else []
            entities = json.loads(p.get("entities", "{}")) if p.get("entities") else {}
            diseases = entities.get("diseases", [])[:5]
            genes = entities.get("genes", [])[:5]
            compounds = entities.get("compounds", [])[:5]
        except:
            formulas = []
            diseases = []
            genes = []
            compounds = []
        
        with st.expander(f"📄 {title}"):
            st.markdown(f"**PMCID:** `{pmcid}` | **Full Text:** {full_text_len:,} chars")
            
            if formulas:
                st.markdown("**Formulas:**")
                for f in formulas[:8]:
                    st.markdown(f'<span class="formula-tag">{f}</span>', unsafe_allow_html=True)
            
            if diseases:
                st.markdown("**Diseases:**")
                for d in diseases:
                    st.markdown(f'<span class="disease-tag">{d}</span>', unsafe_allow_html=True)
            
            if genes:
                st.markdown("**Genes:**")
                for g in genes:
                    st.markdown(f'<span class="gene-tag">{g}</span>', unsafe_allow_html=True)
            
            if compounds:
                st.markdown("**Compounds:**")
                for c in compounds:
                    st.markdown(f'<span class="formula-tag">{c}</span>', unsafe_allow_html=True)
else:
    st.info("⚡ Waiting for worker to extract papers...")

st.markdown("---")
st.caption("COREKNOW // Autonomous Biomedical Knowledge Engine // Darkmoor Ltd")

# Auto-refresh
time.sleep(3)
st.rerun()

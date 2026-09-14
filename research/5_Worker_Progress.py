
import streamlit as st
import time
import json
from supabase import create_client

st.set_page_config(page_title="CoreKnow Worker", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    .stApp { background: radial-gradient(ellipse at 50% 50%, #0d1b2a 0%, #050810 100%); color: #e0e0e0; font-family: 'Rajdhani', sans-serif; }
    header, footer { visibility: hidden; }
    .hud-title {
        font-family: 'Orbitron', sans-serif; font-size: 2.8rem; font-weight: 900; text-align: center;
        background: linear-gradient(135deg, #00e5ff 0%, #7c4dff 50%, #ff1744 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: pulse 2s infinite alternate;
    }
    @keyframes pulse { 0% { filter: brightness(1); } 100% { filter: brightness(1.3); } }
    .subtitle { text-align: center; color: #8892b0; font-size: 1rem; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 2rem; }
    .stat-card {
        background: linear-gradient(145deg, #0d1117 0%, #111827 100%);
        border: 1px solid #1f2a44; border-radius: 12px; padding: 1.2rem; text-align: center;
        transition: all 0.3s;
    }
    .stat-card:hover { border-color: #00e5ff; box-shadow: 0 0 25px rgba(0,229,255,0.3); transform: translateY(-3px); }
    .stat-number { font-family: 'Orbitron', monospace; font-size: 2.2rem; font-weight: 700; color: #00e5ff; text-shadow: 0 0 10px rgba(0,229,255,0.5); }
    .stat-label { color: #8892b0; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px; margin-top: 0.3rem; }
    .scan-line { position: fixed; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, #00e5ff, transparent); animation: scan 3s linear infinite; z-index: 999; }
    @keyframes scan { 0% { top: 0; } 100% { top: 100%; } }
    .status-dot { display: inline-block; width: 10px; height: 10px; background: #00c853; border-radius: 50%; margin-right: 8px; animation: blink 1s infinite; }
    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    .tag { display: inline-block; background: #111827; border: 1px solid #7c4dff; border-radius: 4px; padding: 2px 8px; margin: 2px; font-size: 0.7rem; color: #b388ff; }
    [data-testid="stSidebar"] { background: #0d1117; border-right: 1px solid #1f2a44; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="scan-line"></div>', unsafe_allow_html=True)

# Supabase
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["service_key"]

@st.cache_resource
def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

client = get_client()

def fetch_count(table, filters=None):
    try:
        q = client.table(table).select("*", count="exact")
        if filters:
            for k, v in filters.items():
                q = q.eq(k, v)
        res = q.execute()
        return res.count if res.count else 0
    except:
        return 0

# --- Stats from coreknow_documents and coreknow_document_components ---
total_docs = fetch_count("coreknow_documents")
total_text = fetch_count("coreknow_document_components", {"component_type": "text"})
total_tables = fetch_count("coreknow_document_components", {"component_type": "table"})
total_images = fetch_count("coreknow_document_components", {"component_type": "image"})
total_formulas = fetch_count("coreknow_document_components", {"component_type": "formulas"})

# --- Optional: still show biomed_papers count if exists ---
try:
    biomed_count = fetch_count("coreknow_biomed_papers")
except:
    biomed_count = 0

# Sidebar
with st.sidebar:
    st.markdown("## 🧠 CoreKnow")
    st.markdown("---")
    st.markdown("### 📄 Pages")
    st.page_link("app.py", label="🏠 Home", use_container_width=True)
    st.page_link("pages/3_Deep_Search.py", label="🔍 Deep Search", use_container_width=True)
    st.page_link("pages/4_Browse_Knowledge.py", label="📚 Browse Knowledge", use_container_width=True)
    st.page_link("pages/5_Worker_Progress.py", label="📊 Worker Progress", use_container_width=True)
    st.page_link("pages/6_Drug_Discovery.py", label="💊 Drug Discovery", use_container_width=True)
    st.page_link("pages/7_Query.py", label="🔎 Query", use_container_width=True)

    st.markdown("---")
    st.markdown("### 📊 Live Stats")
    st.metric("Documents", total_docs)
    st.metric("Text", total_text)
    st.metric("Tables", total_tables)
    st.metric("Images", total_images)
    st.metric("Formulas", total_formulas)

# Title
st.markdown('<div class="hud-title">🧠 COREKNOW WORKER</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Autonomous Multimodal Biomedical Engine</div>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center;color:#00c853;"><span class="status-dot"></span>LIVE — Auto-refreshing every 3s</p>', unsafe_allow_html=True)

# HUD Stats
st.markdown("### 📈 KNOWLEDGE METRICS")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_docs}</div><div class="stat-label">📄 Documents</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_text}</div><div class="stat-label">📝 Text</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_tables}</div><div class="stat-label">📊 Tables</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_images}</div><div class="stat-label">🖼️ Images</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{total_formulas}</div><div class="stat-label">⚗️ Formulas</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Recent documents with component counts
st.markdown("### 🕒 LIVE INGESTION FEED")
try:
    docs_res = client.table("coreknow_documents").select("id, name, format, created_at").order("id", desc=True).limit(15).execute()
    docs = docs_res.data if docs_res.data else []

    if docs:
        for doc in docs:
            doc_id = doc["id"]
            name = doc.get("name", "Untitled")
            fmt = doc.get("format", "")

            # Component counts
            comps = client.table("coreknow_document_components").select("component_type").eq("document_id", doc_id).execute()
            counts = {}
            for c in comps.data:
                t = c["component_type"]
                counts[t] = counts.get(t, 0) + 1

            with st.expander(f"📄 {name} (ID: {doc_id})"):
                st.markdown(f"**Format:** {fmt}")
                st.markdown(f"**Text:** {counts.get('text', 0)} | **Tables:** {counts.get('table', 0)} | **Images:** {counts.get('image', 0)} | **Formulas:** {counts.get('formulas', 0)}")
    else:
        st.info("⚡ Waiting for ingestion...")
except Exception as e:
    st.info(f"Could not load documents: {e}")

st.markdown("---")

# User uploads (non-XML)
st.markdown("### 📤 USER UPLOADS")
try:
    uploads_res = client.table("coreknow_documents").select("id, name, format, created_at").neq("format", ".xml").order("id", desc=True).limit(10).execute()
    uploads = uploads_res.data if uploads_res.data else []

    if uploads:
        for doc in uploads:
            doc_id = doc["id"]
            name = doc.get("name", "Untitled")
            fmt = doc.get("format", "")

            comps = client.table("coreknow_document_components").select("component_type").eq("document_id", doc_id).execute()
            counts = {}
            for c in comps.data:
                t = c["component_type"]
                counts[t] = counts.get(t, 0) + 1

            with st.expander(f"📄 {name} (ID: {doc_id})"):
                st.markdown(f"**Format:** {fmt}")
                st.markdown(f"**Text:** {counts.get('text', 0)} | **Tables:** {counts.get('table', 0)} | **Images:** {counts.get('image', 0)} | **Formulas:** {counts.get('formulas', 0)}")
    else:
        st.info("No user uploads yet. Upload from Home page.")
except Exception as e:
    st.info(f"Could not load user uploads: {e}")

st.markdown("---")
st.caption("COREKNOW // Autonomous Multimodal Engine // Darkmoor Ltd")

# Auto-refresh
time.sleep(3)
st.rerun()

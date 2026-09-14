import streamlit as st
import os
import json
import requests
from supabase import create_client

try:
    from utils.universal_ingestor import UniversalIngestor
except ImportError:
    UniversalIngestor = None

try:
    from utils.deep_search import DeepSearch
except ImportError:
    DeepSearch = None

st.markdown("""
<style>
    .stApp { background: #0a0e17; color: #e0e0e0; }
    .main-title { font-size: 2.5rem; font-weight: 900; text-align: center; color: #00e5ff; }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 1rem; }
    [data-testid="stSidebar"] { background: #111827; }
    .stat-box { background: #111827; border-radius: 10px; padding: 1rem; text-align: center; }
    .stat-number { font-size: 2rem; font-weight: 700; color: #00e5ff; }
    .stat-label { color: #8892b0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 COREKNOW BRAIN</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Feed It Anything. It Learns Everything.</div>', unsafe_allow_html=True)

if "ingested_docs" not in st.session_state:
    st.session_state.ingested_docs = []
if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = ""

try:
    supabase = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["service_key"])
except Exception:
    supabase = None

st.markdown("### Welcome to CoreKnow")
st.info("Use the sidebar to upload files, ingest URLs, or perform deep searches.")

if supabase:
    st.markdown("### Quick Stats")
    try:
        res = supabase.table("coreknow_documents").select("*", count="exact").execute()
        st.metric("Documents in DB", res.count if res.count else 0)
    except Exception:
        pass

st.markdown("---")
st.caption("CoreKnow · Powered by Darkmoor Ltd")

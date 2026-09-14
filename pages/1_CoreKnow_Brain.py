import streamlit as st
import os
import requests
from supabase import create_client


# ---------- THEME ----------
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0e17 0%, #0d1b2a 100%); color: #e0e0e0; }
    header, footer { visibility: hidden; }
    .main-title {
        font-size: 2.8rem; font-weight: 900; text-align: center;
        background: linear-gradient(135deg, #00e5ff, #7c4dff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 2rem; letter-spacing: 2px; }
    .card {
        background: linear-gradient(145deg, #0d1117 0%, #111827 100%);
        border: 1px solid #1f2a44; border-radius: 14px;
        padding: 1.5rem; margin: 0.5rem 0;
    }
    .stat-box {
        background: #111827; border: 1px solid #1f2a44; border-radius: 12px;
        padding: 1.2rem; text-align: center;
    }
    .stat-number { font-size: 2rem; font-weight: 700; color: #00e5ff; }
    .stat-label { color: #8892b0; font-size: 0.85rem; text-transform: uppercase; }
    .stButton > button {
        background: linear-gradient(135deg, #00e5ff, #7c4dff);
        color: #0a0e17; font-weight: bold; border: none; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="main-title">🧠 COREKNOW BRAIN</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">FEED IT ANYTHING · IT LEARNS EVERYTHING</div>', unsafe_allow_html=True)


# ---------- SESSION STATE ----------
if "ingested_docs" not in st.session_state:
    st.session_state.ingested_docs = []
if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = ""


# ---------- SUPABASE ----------
try:
    supabase = create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["service_key"]
    )
except Exception:
    supabase = None


# ---------- HERO CARDS ----------
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="card">
        <h3>📥 Feed Knowledge</h3>
        <p>Upload documents, books, papers — CoreKnow reads them all.</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="card">
        <h3>🔍 Deep Search</h3>
        <p>Search Wikipedia, ArXiv, and more. Extract formulas and text.</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="card">
        <h3>💬 Ask CoreKnow</h3>
        <p>Get AI-powered answers from everything it has learned.</p>
    </div>
    """, unsafe_allow_html=True)


# ---------- STATS ----------
st.markdown("### 📊 Knowledge Stats")

if supabase:
    try:
        docs = supabase.table("coreknow_documents").select("*", count="exact").execute()
        papers = supabase.table("coreknow_biomed_papers").select("*", count="exact").execute()
        kg = supabase.table("coreknow_kg").select("*", count="exact").execute()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(docs.count or 0) + '</div><div class="stat-label">Documents</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(papers.count or 0) + '</div><div class="stat-label">Papers</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(kg.count or 0) + '</div><div class="stat-label">KG Nodes</div></div>', unsafe_allow_html=True)
    except Exception as e:
        st.info("Stats temporarily unavailable.")
else:
    st.warning("Supabase not configured.")


# ---------- QUICK LINKS ----------
st.markdown("---")
st.markdown("### 🚀 What would you like to do?")

c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div class="card">
        <h4>🎓 CoreKnow Student</h4>
        <p>JAMB, WAEC, GCE, NECO exam preparation with AI tutor.</p>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="card">
        <h4>🔬 Research Tools</h4>
        <p>Deep search, drug discovery, engineering knowledge base.</p>
    </div>
    """, unsafe_allow_html=True)


st.markdown("---")
st.caption("CoreKnow · Powered by Darkmoor Ltd")

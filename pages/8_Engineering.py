
import streamlit as st
import requests
import json
import time
import io
import os
import re
import base64
from supabase import create_client
from bs4 import BeautifulSoup

st.set_page_config(page_title="CoreKnow Engineering", page_icon="⚙️", layout="wide")

# ============================================
# STYLING
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    .stApp { background: radial-gradient(ellipse at 50% 50%, #0a0f1a 0%, #050810 100%); color: #e0e0e0; font-family: 'Rajdhani', sans-serif; }
    header, footer { visibility: hidden; }
    .title { font-family: 'Orbitron', sans-serif; font-size: 2.5rem; font-weight: 900; text-align: center;
        background: linear-gradient(135deg, #ff6f00 0%, #ffca28 50%, #00e5ff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 2rem; letter-spacing: 2px; }
    .field-card {
        background: linear-gradient(145deg, #0d1117 0%, #111827 100%);
        border: 1px solid #1f2a44; border-radius: 12px; padding: 1rem; text-align: center;
        transition: all 0.3s; cursor: pointer;
    }
    .field-card:hover { border-color: #ffca28; box-shadow: 0 0 20px rgba(255,202,40,0.3); transform: translateY(-3px); }
    .field-icon { font-size: 2rem; }
    .field-name { color: #ffca28; font-weight: 600; margin-top: 0.5rem; }
    .stat-card { background: #0d1117; border: 1px solid #1f2a44; border-radius: 10px; padding: 1rem; text-align: center; }
    .stat-number { font-family: 'Orbitron', monospace; font-size: 1.8rem; color: #ffca28; }
    .stat-label { color: #8892b0; font-size: 0.7rem; text-transform: uppercase; }
    .formula-tag { display: inline-block; background: #111827; border: 1px solid #00e5ff; border-radius: 4px; padding: 2px 8px; margin: 2px; font-family: monospace; font-size: 0.7rem; color: #00e5ff; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">⚙️ COREKNOW ENGINEERING</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Aerospace • Mechanical • Electrical • Computer • Chemical • Petroleum • Marine • Geology • Astronomy • Astrophysics</div>', unsafe_allow_html=True)

# ============================================
# SUPABASE
# ============================================
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["service_key"]

@st.cache_resource
def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

client = get_client()

def fetch_count(table):
    try:
        res = client.table(table).select("*", count="exact").execute()
        return res.count if res.count else 0
    except:
        return 0

# ============================================
# ENGINEERING FIELDS
# ============================================
ENGINEERING_FIELDS = {
    "aerospace": {"name": "Aerospace / Aeronautics", "icon": "✈️", "topics": ["aerodynamics", "propulsion", "orbital mechanics", "flight dynamics", "spacecraft design"]},
    "astronomy": {"name": "Astronomy", "icon": "🔭", "topics": ["stellar evolution", "galaxies", "cosmology", "exoplanets", "radio astronomy"]},
    "astrophysics": {"name": "Astrophysics", "icon": "🌌", "topics": ["black holes", "general relativity", "dark matter", "gravitational waves", "neutron stars"]},
    "mechanical": {"name": "Mechanical Engineering", "icon": "🔧", "topics": ["thermodynamics", "fluid mechanics", "machine design", "manufacturing", "robotics"]},
    "electrical": {"name": "Electrical Engineering", "icon": "⚡", "topics": ["circuit design", "power systems", "control systems", "signal processing", "electronics"]},
    "computer": {"name": "Computer Engineering", "icon": "💻", "topics": ["computer architecture", "operating systems", "networks", "embedded systems", "algorithms"]},
    "chemical": {"name": "Chemical Engineering", "icon": "🧪", "topics": ["reactor design", "process control", "mass transfer", "petrochemicals", "polymer engineering"]},
    "petroleum": {"name": "Petroleum Engineering", "icon": "🛢️", "topics": ["reservoir engineering", "drilling", "production", "petrophysics", "enhanced oil recovery"]},
    "geology": {"name": "Geology", "icon": "🪨", "topics": ["mineralogy", "petrology", "structural geology", "stratigraphy", "geophysics"]},
    "marine": {"name": "Marine Engineering", "icon": "🚢", "topics": ["naval architecture", "marine propulsion", "offshore structures", "hydrodynamics", "marine systems"]},
    "civil": {"name": "Civil Engineering", "icon": "🏗️", "topics": ["structural analysis", "geotechnics", "transportation", "water resources", "construction management"]},
    "materials": {"name": "Materials Science", "icon": "🔬", "topics": ["metallurgy", "composites", "nanomaterials", "ceramics", "polymers"]},
}

# ============================================
# STATS
# ============================================
total_eng_docs = fetch_count("engineering_documents")
total_eng_components = fetch_count("engineering_document_components")

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
    st.page_link("pages/8_Engineering.py", label="⚙️ Engineering", use_container_width=True)

    st.markdown("---")
    st.markdown("### 📊 Engineering Stats")
    st.metric("Engineering Docs", total_eng_docs)
    st.metric("Components", total_eng_components)

# ============================================
# FIELD SELECTOR
# ============================================
st.markdown("### 🎯 Select Engineering Field")
selected_field = st.selectbox(
    "Choose a field to learn/query",
    options=list(ENGINEERING_FIELDS.keys()),
    format_func=lambda x: f"{ENGINEERING_FIELDS[x]['icon']} {ENGINEERING_FIELDS[x]['name']}"
)

field_info = ENGINEERING_FIELDS[selected_field]

st.markdown(f"### {field_info['icon']} {field_info['name']}")
st.markdown(f"**Topics:** {', '.join(field_info['topics'])}")

# ============================================
# UPLOAD ENGINEERING DOCS
# ============================================
st.markdown("---")
st.markdown("### 📤 Upload Engineering Papers or Textbooks")

uploaded_files = st.file_uploader(
    "Upload PDFs, textbooks, or documents",
    type=["pdf", "txt", "docx"],
    accept_multiple_files=True,
    key=f"eng_upload_{selected_field}"
)

if uploaded_files and st.button("📥 Ingest to Engineering Brain", type="primary", use_container_width=True):
    from utils.engineering_ingestor import EngineeringIngestor
    ingestor = EngineeringIngestor()

    for file in uploaded_files:
        with st.spinner(f"Processing {file.name}..."):
            result = ingestor.process_and_store(
                file.getvalue(),
                file.name,
                field=selected_field
            )
            if result.get("status") == "success":
                st.success(f"✅ {file.name} ingested into {field_info['name']}")
            else:
                st.error(f"❌ {file.name}: {result.get('error')}")

# ============================================
# DEEP SEARCH FOR ENGINEERING
# ============================================
st.markdown("---")
st.markdown("### 🔍 Deep Search Engineering Topics")

search_query = st.text_input(
    "Search for engineering topics",
    placeholder="e.g., rocket propulsion, quantum computing, offshore drilling"
)

if search_query and st.button("🔍 Deep Search & Learn", use_container_width=True):
    with st.spinner(f"Searching for '{search_query}'..."):
        from utils.engineering_ingestor import EngineeringIngestor
        ingestor = EngineeringIngestor()
        result = ingestor.deep_search_engineering(search_query, field=selected_field)
        if result.get("status") == "success":
            st.success(f"✅ Learned {result.get('count', 0)} papers on '{search_query}'")
        else:
            st.error(f"❌ Search failed: {result.get('error')}")

# ============================================
# QUERY ENGINEERING KNOWLEDGE
# ============================================
st.markdown("---")
st.markdown("### 🔎 Query Engineering Knowledge")

query = st.text_input(
    "Ask an engineering question",
    placeholder="e.g., What is the thrust equation for a rocket engine?"
)

if query and st.button("🔎 Search Knowledge", type="primary", use_container_width=True):
    with st.spinner("Searching engineering knowledge..."):
        # Fetch all text components for this field
        try:
            comps = client.table("engineering_document_components") \
                .select("document_id, content") \
                .eq("component_type", "text") \
                .limit(500) \
                .execute()

            query_words = set(query.lower().split())
            scored = []
            for comp in comps.data:
                try:
                    content = json.loads(comp["content"])["content"]
                    content_lower = content.lower()
                    score = sum(content_lower.count(w) for w in query_words if len(w) > 3)
                    if score > 0:
                        scored.append((score, comp["document_id"], content))
                except:
                    pass

            scored.sort(reverse=True, key=lambda x: x[0])
            top_results = scored[:5]

            if top_results:
                st.success(f"Found {len(top_results)} relevant passages")
                for score, doc_id, content in top_results:
                    doc_info = client.table("engineering_documents").select("name").eq("id", doc_id).execute()
                    doc_name = doc_info.data[0]["name"] if doc_info.data else f"Doc {doc_id}"

                    with st.expander(f"📄 {doc_name} (score: {score})"):
                        st.markdown(content[:2000] + "...")
            else:
                st.info("No matches found. Try different keywords or upload more documents.")
        except Exception as e:
            st.error(f"Query failed: {e}")

st.markdown("---")
st.caption("COREKNOW ENGINEERING // Powered by Darkmoor Ltd")

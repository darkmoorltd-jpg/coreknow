
import streamlit as st
import os
import json
from utils.ingestion import ingest_file, read_website
from utils.knowledge_graph import KnowledgeGraph
from utils.coreknow_brain import CoreKnowBrain

st.set_page_config(page_title="CoreKnow", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0a0e17; color: #e0e0e0; }
    .main-title { font-size: 2.5rem; font-weight: 900; text-align: center; color: #00e5ff; }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 1rem; }
    .stButton > button { background: #00e5ff; color: #0a0e17; font-weight: bold; border: none; }
    [data-testid="stSidebar"] { background: #111827; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 COREKNOW</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Self‑Learning AI With Its Own Brain</div>', unsafe_allow_html=True)

# Initialize
if "kg" not in st.session_state:
    st.session_state.kg = KnowledgeGraph()
if "brain" not in st.session_state:
    st.session_state.brain = CoreKnowBrain()

# Sidebar
with st.sidebar:
    st.title("🧠 Brain Status")
    status = st.session_state.brain.get_status()
    if status["loaded"]:
        st.success(f"✅ {status['model']}")
    else:
        st.warning("Add deepseek api_key to secrets")
    
    st.markdown("---")
    st.title("📥 Feed CoreKnow")
    
    uploaded_files = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("🧠 Ingest", type="primary", use_container_width=True):
            count = 0
            for file in uploaded_files:
                text = ingest_file(file.getvalue(), file.name)
                st.session_state.kg.add_document(text, file.name)
                count += 1
            st.success(f"✅ {count} files ingested!")

# Main area
tab1, tab2 = st.tabs(["💬 Ask CoreKnow", "📚 Knowledge"])

with tab1:
    question = st.text_input("Ask CoreKnow", placeholder="What is CoreKnow?")
    if question:
        with st.spinner("CoreKnow is thinking..."):
            answer = st.session_state.brain.ask(question)
            st.write(answer)

with tab2:
    stats = st.session_state.kg.get_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documents", stats["documents"])
    with col2:
        st.metric("Concepts", stats["concepts"])
    with col3:
        st.metric("Connections", stats["edges"])
    
    concepts = st.session_state.kg.get_all_concepts()
    if concepts:
        st.markdown("### Learned Concepts")
        st.markdown(", ".join(f"`{c}`" for c in concepts[:100]))

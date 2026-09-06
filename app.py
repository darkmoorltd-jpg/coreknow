
import streamlit as st
import os
import json
from utils.ingestion import ingest_file, read_website
from utils.knowledge_graph import KnowledgeGraph
from utils.vector_store import VectorStore

st.set_page_config(page_title="CoreKnow", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .stApp { background: radial-gradient(ellipse at 20% 50%, #0d1b2a 0%, #0a0e17 70%); color: #e0e0e0; }
    header, footer { visibility: hidden; }
    .title { font-size: 3rem; font-weight: 900; text-align: center; background: linear-gradient(135deg, #00e5ff, #7c4dff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧠 COREKNOW</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">The Self‑Learning AI That Knows Everything</div>', unsafe_allow_html=True)

# Initialize session state
if "kg" not in st.session_state:
    st.session_state.kg = KnowledgeGraph()
if "vs" not in st.session_state:
    st.session_state.vs = VectorStore()
if "documents" not in st.session_state:
    st.session_state.documents = []

# Sidebar for ingestion
with st.sidebar:
    st.markdown("## 📥 Feed CoreKnow")
    
    # File upload
    uploaded_files = st.file_uploader("Upload Books/PDFs/TXT", type=["pdf", "txt"], accept_multiple_files=True)
    
    # Website URL
    website_url = st.text_input("Or enter website URL", placeholder="https://example.com")
    
    if uploaded_files or website_url:
        if st.button("🧠 Ingest Knowledge", type="primary", use_container_width=True):
            with st.spinner("CoreKnow is learning..."):
                # Process files
                for file in uploaded_files:
                    text = ingest_file(file.getvalue(), file.name)
                    st.session_state.kg.add_document(text, file.name)
                    st.session_state.documents.append({"name": file.name, "text": text[:500]})
                
                # Process website
                if website_url:
                    text = read_website(website_url)
                    st.session_state.kg.add_document(text, website_url)
                    st.session_state.documents.append({"name": website_url, "text": text[:500]})
                
                st.success(f"Ingested {len(uploaded_files) + (1 if website_url else 0)} documents!")

# Main area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📚 Knowledge Base")
    stats = st.session_state.kg.get_stats()
    
    metric_cols = st.columns(3)
    with metric_cols[0]:
        st.metric("Documents", stats["documents"])
    with metric_cols[1]:
        st.metric("Concepts", stats["concepts"])
    with metric_cols[2]:
        st.metric("Connections", stats["edges"])
    
    if st.session_state.documents:
        st.markdown("### Recent Documents")
        for doc in st.session_state.documents[-5:]:
            st.markdown(f"**📄 {doc['name']}**")
            st.caption(doc['text'][:100] + "...")
    else:
        st.info("Feed CoreKnow some knowledge to begin.")

with col2:
    st.markdown("### 🔍 Query CoreKnow")
    query = st.text_input("Ask anything", placeholder="e.g., What did you learn about...")
    
    if query:
        results = st.session_state.kg.query(query)
        if results:
            st.markdown(f"Related concepts: **{', '.join(str(r) for r in results[:10])}**")
        else:
            st.info("No direct match found. CoreKnow is still learning.")
    
    st.markdown("---")
    st.markdown("### 📊 System Status")
    st.markdown(f"Knowledge graph nodes: **{stats['nodes']}**")
    st.markdown(f"Vector store size: **{st.session_state.vs.size()}**")

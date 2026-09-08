
import streamlit as st
import os
import json
import tempfile
import requests

# Import Universal Ingestor
from utils.universal_ingestor import UniversalIngestor

st.set_page_config(page_title="CoreKnow", page_icon="🧠", layout="wide")

# Dark theme
st.markdown("""
<style>
    .stApp { background: #0a0e17; color: #e0e0e0; }
    .main-title { font-size: 2.5rem; font-weight: 900; text-align: center; color: #00e5ff; }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 1rem; }
    .format-badge { background: #111827; border: 1px solid #00e5ff; border-radius: 20px; padding: 5px 15px; margin: 3px; display: inline-block; font-size: 0.8rem; color: #00e5ff; }
    .stButton > button { background: #00e5ff; color: #0a0e17; font-weight: bold; border: none; }
    [data-testid="stSidebar"] { background: #111827; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 COREKNOW</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Feed It Anything. It Learns Everything.</div>', unsafe_allow_html=True)

# Initialize
if "ingestor" not in st.session_state:
    st.session_state.ingestor = UniversalIngestor()
if "ingested_docs" not in st.session_state:
    st.session_state.ingested_docs = []
if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = ""

# Sidebar
with st.sidebar:
    st.title("📥 Feed CoreKnow")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload ANY file (103+ formats)",
        type=None,  # Accept all formats
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("🧠 Ingest Files", type="primary", use_container_width=True):
            with st.spinner("CoreKnow is eating..."):
                for file in uploaded_files:
                    # Save to temp
                    tmp_path = f"/tmp/{file.name}"
                    with open(tmp_path, "wb") as f:
                        f.write(file.getvalue())
                    
                    # Ingest
                    result = st.session_state.ingestor.ingest_file(tmp_path)
                    
                    if result["status"] == "success":
                        st.session_state.ingested_docs.append({
                            "name": file.name,
                            "format": result["format"],
                            "content": result["content"],
                        })
                        st.session_state.knowledge_base += result["content"] + "\n\n"
                    
                    # Cleanup
                    os.remove(tmp_path)
                
                st.success(f"✅ Ingested {len(uploaded_files)} files!")
                st.rerun()
    
    # URL input
    st.markdown("---")
    website_url = st.text_input("Or enter URL", placeholder="https://example.com")
    
    if website_url:
        if st.button("🌐 Ingest URL", use_container_width=True):
            with st.spinner("Fetching..."):
                result = st.session_state.ingestor.ingest_url(website_url)
                if result["status"] == "success":
                    st.session_state.ingested_docs.append({
                        "name": website_url,
                        "format": result["format"],
                        "content": result["content"],
                    })
                    st.session_state.knowledge_base += result["content"] + "\n\n"
                    st.success("✅ URL ingested!")
                    st.rerun()
    
    # Stats
    stats = st.session_state.ingestor.get_stats()
    st.markdown("---")
    st.markdown("### 📊 Ingestor Stats")
    st.metric("Formats Supported", stats["total_formats"])
    st.metric("Documents Ingested", len(st.session_state.ingested_docs))
    st.metric("Knowledge Size", f"{len(st.session_state.knowledge_base):,} chars")

# Main area
tab1, tab2, tab3 = st.tabs(["💬 Ask CoreKnow", "📚 Knowledge Base", "🔤 Formats"])

with tab1:
    st.markdown("### Ask about anything you've fed CoreKnow")
    question = st.text_input("Ask anything", placeholder="e.g., What does this document say?")
    
    if question:
        with st.spinner("CoreKnow is thinking..."):
            # Simple search in knowledge base
            knowledge = st.session_state.knowledge_base
            if knowledge:
                # Find relevant sections
                sentences = knowledge.split(".")
                relevant = [s.strip() for s in sentences if question.lower() in s.lower()]
                
                if relevant:
                    answer = ". ".join(relevant[:5])
                    st.write(answer)
                else:
                    # Fallback to DeepSeek if available
                    try:
                        deepseek_key = st.secrets["deepseek"]["api_key"]
                        headers = {"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"}
                        payload = {
                            "model": "deepseek-chat",
                            "messages": [
                                {"role": "system", "content": f"Answer based on this knowledge: {knowledge[:3000]}"},
                                {"role": "user", "content": question}
                            ],
                            "max_tokens": 500
                        }
                        r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
                        if r.status_code == 200:
                            st.write(r.json()["choices"][0]["message"]["content"])
                        else:
                            st.info("No direct answer found. Try rephrasing.")
                    except:
                        st.info("No direct answer found. Feed CoreKnow more content.")
            else:
                st.warning("Feed CoreKnow some files first!")

with tab2:
    st.markdown("### 📚 Ingested Documents")
    
    if st.session_state.ingested_docs:
        for i, doc in enumerate(st.session_state.ingested_docs):
            with st.expander(f"📄 {doc['name']} ({doc['format']})"):
                st.caption(doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content'])
    else:
        st.info("No documents yet. Upload files in the sidebar.")

with tab3:
    st.markdown("### 🔤 Supported Formats (103+)")
    
    formats = [
        "PDF", "DOCX", "TXT", "MD", "RTF", "HTML", "XML", "JSON", "CSV", "XLSX",
        "PPTX", "EPUB", "ODT", "JPG", "PNG", "GIF", "BMP", "TIFF", "WEBP",
        "MP3", "WAV", "M4A", "AAC", "FLAC", "OGG", "MP4", "AVI", "MOV", "MKV",
        "WebM", "ZIP", "RAR", "TAR", "GZ", "7Z", "PY", "JS", "JAVA", "CPP",
        "C", "GO", "RS", "TS", "SQL", "SH", "CSS", "EML", "MSG", "DB",
        "SQLite", "YAML", "TOML", "INI", "RSS", "Atom", "LaTeX", "BibTeX",
        "Parquet", "Feather", "HDF5", "Pickle", "SRT", "VTT", "ASS", "EXE",
        "DLL", "SO", "TTF", "OTF", "STL", "OBJ", "STEP", "IGES", "GeoJSON",
        "KML", "SHP", "OPUS", "AMR", "WMA", "FLV", "M4V", "MPG", "MPEG",
        "3GP", "TS", "HEIC", "ICO", "ICNS", "RAW", "CR2", "NEF",
        "Pages", "Numbers", "Keynote"
    ]
    
    # Display as badges
    st.markdown(" ".join([f'<span class="format-badge">{f}</span>' for f in formats]), unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("### 🧠 CoreKnow Universal Ingestor")
st.caption("103+ formats supported. Feed it anything.")


import streamlit as st
import os
import json
import requests
from utils.ingestion import ingest_file, read_website
from utils.knowledge_graph import KnowledgeGraph
from utils.multimodal import analyze_image, transcribe_audio, text_to_speech
from utils.memory import MemorySystem
from utils.self_improvement import SelfImprovement
from utils.auto_learner import AutoLearner
from utils.reasoning import ReasoningEngine
from utils.consciousness import Consciousness
from utils.creativity import Creativity
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
st.markdown('<div class="subtitle">The Self‑Learning AI With Its Own Brain</div>', unsafe_allow_html=True)

# Initialize
if "kg" not in st.session_state:
    st.session_state.kg = KnowledgeGraph()
if "memory" not in st.session_state:
    st.session_state.memory = MemorySystem()
if "brain" not in st.session_state:
    st.session_state.brain = CoreKnowBrain()
if "brain_loaded" not in st.session_state:
    st.session_state.brain_loaded = False

# SIDEBAR
with st.sidebar:
    st.title("🧠 CoreKnow Brain")
    
    if not st.session_state.brain_loaded:
        if st.button("🔌 Load Brain (Mistral + TinyLlama)", type="primary", use_container_width=True):
            with st.spinner("Downloading brains from GitHub Releases..."):
                try:
                    st.session_state.brain.load_all()
                    st.session_state.brain_loaded = True
                    st.success("✅ Brains loaded!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to load: {e}")
    else:
        status = st.session_state.brain.get_status()
        st.success(f"✅ {len(status['models'])} models loaded")
        for model in status["models"]:
            st.markdown(f"🧠 **{model}**")
    
    st.markdown("---")
    st.title("📥 Feed CoreKnow")
    
    uploaded_files = st.file_uploader("Upload Files", type=["pdf", "txt"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("🧠 Ingest Files", type="primary", use_container_width=True):
            count = 0
            for file in uploaded_files:
                text = ingest_file(file.getvalue(), file.name)
                st.session_state.kg.add_document(text, file.name)
                count += 1
            st.success(f"✅ Ingested {count} files!")
    
    website_url = st.text_input("Website URL")
    if website_url:
        if st.button("🌐 Ingest Website", use_container_width=True):
            text = read_website(website_url)
            st.session_state.kg.add_document(text, website_url)
            st.success("✅ Website ingested!")

# MAIN
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📚 Knowledge", "💬 Ask CoreKnow", "📊 Stats"])

with tab1:
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

with tab2:
    question = st.text_input("Ask CoreKnow anything", placeholder="e.g., What is CoreKnow?")
    
    if question:
        if st.session_state.brain_loaded:
            with st.spinner("CoreKnow is thinking with its own brain..."):
                answer = st.session_state.brain.ask(question)
                st.write(answer)
                
                if st.button("🔊 Listen"):
                    audio_bytes, _ = text_to_speech(answer)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
        else:
            st.warning("⚠️ Please load the brain first (sidebar button).")

with tab3:
    brain_status = st.session_state.brain.get_status() if st.session_state.brain_loaded else {"loaded": False, "models": []}
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Brains Loaded", len(brain_status["models"]))
    with col2:
        st.metric("Documents", st.session_state.kg.get_stats()["documents"])
    with col3:
        st.metric("Concepts", len(st.session_state.kg.get_all_concepts()))

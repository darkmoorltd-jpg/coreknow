
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
from utils.self_modification import SelfModification
from utils.autonomous_research import AutonomousResearch
from utils.consciousness import Consciousness
from utils.creativity import Creativity
from utils.database import Database

st.set_page_config(page_title="CoreKnow", page_icon="🧠", layout="centered")

# Simple styling without hiding sidebar
st.markdown("""
<style>
    .stApp { background: #0a0e17; color: #e0e0e0; }
    .title { font-size: 2.5rem; font-weight: 900; text-align: center; color: #00e5ff; }
    .subtitle { text-align: center; color: #8892b0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧠 COREKNOW</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">The Self‑Learning AI That Knows Everything</div>', unsafe_allow_html=True)

# Initialize
if "kg" not in st.session_state:
    st.session_state.kg = KnowledgeGraph()
if "memory" not in st.session_state:
    st.session_state.memory = MemorySystem()
if "improvement" not in st.session_state:
    st.session_state.improvement = SelfImprovement()
if "reasoning" not in st.session_state:
    st.session_state.reasoning = ReasoningEngine(st.session_state.kg, "")

# Get API keys
try:
    deepseek_key = st.secrets["deepseek"]["api_key"]
    st.session_state.reasoning.llm_api_key = deepseek_key
except:
    deepseek_key = ""

try:
    groq_key = st.secrets["groq"]["api_key"]
except:
    groq_key = ""

# SIDEBAR - Simple and visible
with st.sidebar:
    st.title("📥 Feed CoreKnow")
    
    uploaded_files = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("🧠 Ingest Files", type="primary", use_container_width=True):
            count = 0
            for file in uploaded_files:
                text = ingest_file(file.getvalue(), file.name)
                st.session_state.kg.add_document(text, file.name, deepseek_key)
                count += 1
            st.success(f"✅ Ingested {count} files!")
    
    st.markdown("---")
    website_url = st.text_input("Website URL")
    if website_url:
        if st.button("🌐 Ingest Website", use_container_width=True):
            text = read_website(website_url)
            st.session_state.kg.add_document(text, website_url, deepseek_key)
            st.success("✅ Website ingested!")

# Main area
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📚 Knowledge", "💬 Ask", "📊 Stats"])

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
    question = st.text_input("Ask CoreKnow anything")
    if question:
        if deepseek_key:
            concepts = st.session_state.kg.get_all_concepts()[:50]
            headers = {"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"}
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"You are CoreKnow. You know: {', '.join(concepts)}"},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 500
            }
            try:
                r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
                if r.status_code == 200:
                    st.write(r.json()["choices"][0]["message"]["content"])
            except:
                st.error("API error")
        else:
            st.info("Add DeepSeek API key in secrets to enable Q&A.")

with tab3:
    st.metric("Total Concepts", len(st.session_state.kg.get_all_concepts()))
    st.metric("Total Documents", st.session_state.kg.get_stats()["documents"])


import streamlit as st
import os
import json
import requests
from utils.ingestion import ingest_file, read_website
from utils.knowledge_graph import KnowledgeGraph
from utils.multimodal import analyze_image, transcribe_audio, text_to_speech
from utils.web_crawler import WebCrawler
from utils.memory import MemorySystem

st.set_page_config(page_title="CoreKnow", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .stApp { background: radial-gradient(ellipse at 20% 50%, #0d1b2a 0%, #0a0e17 70%); color: #e0e0e0; }
    header, footer { visibility: hidden; }
    .title { font-size: 3rem; font-weight: 900; text-align: center; background: linear-gradient(135deg, #00e5ff, #7c4dff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 2rem; }
    .stButton > button { background: linear-gradient(135deg, #00e5ff, #7c4dff); color: white; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧠 COREKNOW</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">The Self‑Learning AI That Knows Everything</div>', unsafe_allow_html=True)

# Initialize session state
if "kg" not in st.session_state:
    st.session_state.kg = KnowledgeGraph()
if "memory" not in st.session_state:
    st.session_state.memory = MemorySystem()
if "documents" not in st.session_state:
    st.session_state.documents = []
if "feedback" not in st.session_state:
    st.session_state.feedback = []

# Get API keys
try:
    deepseek_key = st.secrets["deepseek"]["api_key"]
except:
    deepseek_key = ""
try:
    groq_key = st.secrets["groq"]["api_key"]
except:
    groq_key = ""

# Sidebar
with st.sidebar:
    st.markdown("## 📥 Feed CoreKnow")
    
    # File upload (text + image + audio)
    uploaded_files = st.file_uploader("Upload Files (PDF/TXT/Image/Audio)", 
                                      type=["pdf", "txt", "jpg", "jpeg", "png", "wav", "mp3"], 
                                      accept_multiple_files=True)
    
    website_url = st.text_input("Or enter website URL", placeholder="https://example.com")
    
    # Web crawler
    st.markdown("---")
    st.markdown("### 🕷️ Web Crawler")
    crawl_url = st.text_input("Crawl from URL", placeholder="https://example.com/wiki")
    max_pages = st.number_input("Max pages", min_value=1, value=5)
    
    if st.button("🧠 Ingest All", type="primary", use_container_width=True):
        count = 0
        for file in uploaded_files:
            if file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Image analysis
                result = analyze_image(file.getvalue(), deepseek_key)
                st.session_state.kg.add_document(result, file.name, deepseek_key)
            elif file.name.lower().endswith(('.wav', '.mp3')):
                # Audio transcription
                text, err = transcribe_audio(file.getvalue(), groq_key)
                if text:
                    st.session_state.kg.add_document(text, file.name, deepseek_key)
            else:
                # Text/PDF
                text = ingest_file(file.getvalue(), file.name)
                st.session_state.kg.add_document(text, file.name, deepseek_key)
            count += 1
        
        if website_url:
            text = read_website(website_url)
            st.session_state.kg.add_document(text, website_url, deepseek_key)
            count += 1
        
        if crawl_url:
            crawler = WebCrawler(max_pages=int(max_pages))
            pages = crawler.crawl_and_learn(crawl_url, st.session_state.kg, deepseek_key)
            count += pages
        
        st.success(f"✅ Ingested {count} items!")
    
    st.markdown("---")
    st.markdown("### 🗄️ Memory")
    mem_col1, mem_col2 = st.columns(2)
    with mem_col1:
        if st.button("💾 Save Memory", use_container_width=True):
            st.session_state.memory.save()
            st.success("Saved!")
    with mem_col2:
        if st.button("📂 Load Memory", use_container_width=True):
            st.session_state.memory.load()
            st.success("Loaded!")

# Main area
tab1, tab2, tab3, tab4 = st.tabs(["📚 Knowledge", "💬 Ask", "🎨 Multimodal", "📊 Insights"])

with tab1:
    stats = st.session_state.kg.get_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documents", stats["documents"])
    with col2:
        st.metric("Concepts", stats["concepts"])
    with col3:
        st.metric("Connections", stats["edges"])

with tab2:
    st.markdown("### 💬 Ask CoreKnow")
    question = st.text_input("Ask anything", placeholder="e.g., What did you learn?")
    
    if question:
        with st.spinner("Thinking..."):
            results = st.session_state.kg.query(question)
            
            if deepseek_key:
                concepts = st.session_state.kg.get_all_concepts()[:50]
                context = f"CoreKnow knows: {', '.join(concepts)}"
                headers = {"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": f"You are CoreKnow. {context}"},
                        {"role": "user", "content": question}
                    ],
                    "max_tokens": 500
                }
                try:
                    r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
                    if r.status_code == 200:
                        answer = r.json()["choices"][0]["message"]["content"]
                        st.write(answer)
                        
                        # Text-to-speech
                        if st.button("🔊 Listen"):
                            audio_bytes, err = text_to_speech(answer)
                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp3")
                except:
                    pass
            
            # Store in memory
            st.session_state.memory.add_short_term({"type": "question", "content": question})

with tab3:
    st.markdown("### 🎨 Multimodal Understanding")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📸 Image Analysis")
        img_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
        if img_file:
            st.image(img_file, width=200)
            if st.button("Analyze Image"):
                result = analyze_image(img_file.getvalue(), deepseek_key)
                st.write(result)
    
    with col2:
        st.markdown("#### 🎤 Audio Transcription")
        audio_file = st.file_uploader("Upload audio", type=["wav", "mp3"])
        if audio_file:
            st.audio(audio_file)
            if st.button("Transcribe"):
                text, err = transcribe_audio(audio_file.getvalue(), groq_key)
                if text:
                    st.write(text)
                else:
                    st.warning(err)

with tab4:
    st.markdown("### 📊 CoreKnow Insights")
    
    total_feedback = len(st.session_state.feedback)
    helpful = sum(1 for f in st.session_state.feedback if f.get("helpful", False))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Feedback", total_feedback)
    with col2:
        st.metric("Helpful Rate", f"{(helpful/total_feedback*100):.0f}%" if total_feedback > 0 else "N/A")
    with col3:
        st.metric("Short-term Memories", len(st.session_state.memory.short_term))
    
    concepts = st.session_state.kg.get_all_concepts()
    if concepts:
        st.markdown("### Learned Concepts")
        st.markdown(", ".join(f"`{c}`" for c in concepts[:100]))


import streamlit as st
import os
import json
import requests
from utils.ingestion import ingest_file, read_website
from utils.knowledge_graph import KnowledgeGraph
from utils.multimodal import analyze_image, transcribe_audio, text_to_speech
from utils.web_crawler import WebCrawler
from utils.memory import MemorySystem
from utils.self_improvement import SelfImprovement
from utils.auto_learner import AutoLearner

st.set_page_config(page_title="CoreKnow", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .stApp { background: radial-gradient(ellipse at 20% 50%, #0d1b2a 0%, #0a0e17 70%); color: #e0e0e0; }
    header, footer { visibility: hidden; }
    .title { font-size: 3rem; font-weight: 900; text-align: center; background: linear-gradient(135deg, #00e5ff, #7c4dff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 2rem; }
    .stButton > button { background: linear-gradient(135deg, #00e5ff, #7c4dff); color: white; font-weight: bold; }
    .gap-card { background: #111827; border: 1px solid #1f2a44; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧠 COREKNOW</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">The Self‑Learning AI That Knows Everything</div>', unsafe_allow_html=True)

# Initialize session state
if "kg" not in st.session_state:
    st.session_state.kg = KnowledgeGraph()
if "memory" not in st.session_state:
    st.session_state.memory = MemorySystem()
if "improvement" not in st.session_state:
    st.session_state.improvement = SelfImprovement()
if "auto_learner" not in st.session_state:
    st.session_state.auto_learner = AutoLearner(st.session_state.kg, "")
if "documents" not in st.session_state:
    st.session_state.documents = []

# Get API keys
try:
    deepseek_key = st.secrets["deepseek"]["api_key"]
    st.session_state.auto_learner.llm_api_key = deepseek_key
except:
    deepseek_key = ""

try:
    groq_key = st.secrets["groq"]["api_key"]
except:
    groq_key = ""

# Sidebar
with st.sidebar:
    st.markdown("## 📥 Feed CoreKnow")
    
    uploaded_files = st.file_uploader("Upload Files", 
                                      type=["pdf", "txt", "jpg", "jpeg", "png", "wav", "mp3"], 
                                      accept_multiple_files=True)
    
    website_url = st.text_input("Website URL", placeholder="https://example.com")
    
    st.markdown("---")
    st.markdown("### 🤖 Auto‑Learn")
    topics_input = st.text_area("Topics to learn (one per line)", placeholder="Quantum physics\nMachine learning\nAfrican history")
    
    if st.button("🧠 Ingest & Learn", type="primary", use_container_width=True):
        count = 0
        # Process uploads
        for file in uploaded_files:
            if file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                result = analyze_image(file.getvalue(), deepseek_key)
                st.session_state.kg.add_document(result, file.name, deepseek_key)
            elif file.name.lower().endswith(('.wav', '.mp3')):
                text, _ = transcribe_audio(file.getvalue(), groq_key)
                if text:
                    st.session_state.kg.add_document(text, file.name, deepseek_key)
            else:
                text = ingest_file(file.getvalue(), file.name)
                st.session_state.kg.add_document(text, file.name, deepseek_key)
            count += 1
        
        # Process website
        if website_url:
            text = read_website(website_url)
            st.session_state.kg.add_document(text, website_url, deepseek_key)
            count += 1
        
        # Auto-learn topics
        if topics_input:
            topics = [t.strip() for t in topics_input.split("\n") if t.strip()]
            learned = st.session_state.auto_learner.auto_expand_knowledge(topics)
            count += learned
        
        st.success(f"✅ Learned {count} items!")

# Main area
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📚 Knowledge", "💬 Ask", "🎨 Multimodal", "🔍 Gaps", "📊 Insights"])

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
        st.markdown(", ".join(f"`{c}`" for c in concepts[:200]))

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
                        
                        if st.button("🔊 Listen"):
                            audio_bytes, _ = text_to_speech(answer)
                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp3")
                except:
                    pass
            
            # Feedback loop
            st.markdown("---")
            st.markdown("### Was this helpful?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Helpful", key="helpful"):
                    st.session_state.improvement.track_feedback(question, True)
                    st.success("CoreKnow will remember this.")
            with col2:
                if st.button("👎 Not helpful", key="not_helpful"):
                    st.session_state.improvement.track_feedback(question, False)
                    st.info("CoreKnow will learn from this gap.")

with tab3:
    st.markdown("### 🎨 Multimodal")
    col1, col2 = st.columns(2)
    with col1:
        img_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
        if img_file:
            st.image(img_file, width=200)
            if st.button("Analyze"):
                result = analyze_image(img_file.getvalue(), deepseek_key)
                st.write(result)
    with col2:
        audio_file = st.file_uploader("Upload audio", type=["wav", "mp3"])
        if audio_file:
            st.audio(audio_file)
            if st.button("Transcribe"):
                text, err = transcribe_audio(audio_file.getvalue(), groq_key)
                if text:
                    st.write(text)

with tab4:
    st.markdown("### 🔍 Knowledge Gaps")
    st.markdown("CoreKnow tracks what it doesn't know and suggests what to learn next.")
    
    gaps = st.session_state.improvement.identify_gaps()
    if gaps:
        for topic, count in gaps:
            st.markdown(f"""
            <div class="gap-card">
                <strong>❌ {topic}</strong> — failed {count} times
            </div>
            """, unsafe_allow_html=True)
        
        # Auto-learn button
        gap_topics = [g[0] for g in gaps]
        if st.button("🤖 Auto‑Learn These Topics", type="primary"):
            with st.spinner("CoreKnow is learning..."):
                st.session_state.auto_learner.auto_expand_knowledge(gap_topics)
                st.success("✅ CoreKnow filled knowledge gaps!")
                st.rerun()
    else:
        st.info("No knowledge gaps yet. Ask questions to help CoreKnow learn.")

with tab5:
    st.markdown("### 📊 CoreKnow Insights")
    
    improve_stats = st.session_state.improvement.get_stats()
    kg_stats = st.session_state.kg.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Feedback", improve_stats["total_feedback"])
    with col2:
        st.metric("Gaps", improve_stats["knowledge_gaps"])
    with col3:
        st.metric("Improvements", improve_stats["improvements"])
    with col4:
        st.metric("Concepts", kg_stats["concepts"])
    
    # Learning plan
    plan = st.session_state.improvement.generate_learning_plan()
    if plan:
        st.markdown("### 📋 Learning Plan")
        for item in plan:
            st.markdown(f"**{item['topic']}** — {item['reason']}")

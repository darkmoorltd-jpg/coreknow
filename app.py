
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
from utils.reasoning import ReasoningEngine
from utils.self_modification import SelfModification
from utils.autonomous_research import AutonomousResearch

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
if "reasoning" not in st.session_state:
    st.session_state.reasoning = ReasoningEngine(st.session_state.kg, "")
if "self_mod" not in st.session_state:
    st.session_state.self_mod = SelfModification(st.session_state.kg, "")
if "research" not in st.session_state:
    st.session_state.research = AutonomousResearch(st.session_state.kg, "")

# Get API keys
try:
    deepseek_key = st.secrets["deepseek"]["api_key"]
    st.session_state.auto_learner.llm_api_key = deepseek_key
    st.session_state.reasoning.llm_api_key = deepseek_key
    st.session_state.self_mod.llm_api_key = deepseek_key
    st.session_state.research.llm_api_key = deepseek_key
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
    topics_input = st.text_area("Topics to learn", placeholder="Quantum physics\nMachine learning")
    
    if st.button("🧠 Ingest & Learn", type="primary", use_container_width=True):
        count = 0
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
        
        if website_url:
            text = read_website(website_url)
            st.session_state.kg.add_document(text, website_url, deepseek_key)
            count += 1
        
        if topics_input:
            topics = [t.strip() for t in topics_input.split("\n") if t.strip()]
            learned = st.session_state.auto_learner.auto_expand_knowledge(topics)
            count += learned
        
        st.success(f"✅ Learned {count} items!")

# Main area
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📚 Knowledge", "💬 Ask", "🧠 Reason", "🔬 Research", "🔧 Self‑Modify", "🎨 Multimodal", "📊 Insights"
])

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

with tab3:
    st.markdown("### 🧠 Reasoning Engine")
    reasoning_type = st.selectbox("Reasoning Type", [
        "Chain of Thought", "Solve Problem", "Generate Hypothesis", "Causal Inference", "Cross-Domain Transfer"
    ])
    
    if reasoning_type == "Chain of Thought":
        q = st.text_area("Problem", placeholder="e.g., If a train travels at 60 mph...")
        if st.button("Reason", type="primary"):
            st.write(st.session_state.reasoning.chain_of_thought(q))
    
    elif reasoning_type == "Solve Problem":
        q = st.text_area("Problem", placeholder="e.g., How can we reduce malaria?")
        if st.button("Solve", type="primary"):
            st.write(st.session_state.reasoning.solve_problem(q))
    
    elif reasoning_type == "Generate Hypothesis":
        q = st.text_area("Observation", placeholder="e.g., Plants grow faster near river")
        if st.button("Generate", type="primary"):
            hypotheses = st.session_state.reasoning.generate_hypothesis(q)
            if hypotheses:
                for i, h in enumerate(hypotheses):
                    st.markdown(f"**H{i+1}:** {h}")
    
    elif reasoning_type == "Causal Inference":
        cause = st.text_input("Cause")
        effect = st.text_input("Effect")
        if st.button("Analyze", type="primary"):
            st.write(st.session_state.reasoning.causal_inference(cause, effect))
    
    elif reasoning_type == "Cross-Domain Transfer":
        source = st.text_input("Source Domain")
        target = st.text_input("Target Domain")
        concept = st.text_input("Concept")
        if st.button("Transfer", type="primary"):
            st.write(st.session_state.reasoning.cross_domain_transfer(source, target, concept))

with tab4:
    st.markdown("### 🔬 Autonomous Research")
    research_type = st.selectbox("Research Type", [
        "Design Experiment", "Synthesize Knowledge", "Discover Patterns"
    ])
    
    if research_type == "Design Experiment":
        q = st.text_area("Research Question", placeholder="e.g., Does music affect plant growth?")
        if st.button("Design Experiment", type="primary"):
            st.write(st.session_state.research.design_experiment(q))
    
    elif research_type == "Synthesize Knowledge":
        topic1 = st.text_input("Concept 1", placeholder="e.g., Quantum mechanics")
        topic2 = st.text_input("Concept 2", placeholder="e.g., Consciousness")
        if st.button("Synthesize", type="primary"):
            st.write(st.session_state.research.synthesize_knowledge(topic1, topic2))
    
    elif research_type == "Discover Patterns":
        data = st.text_area("Data Description", placeholder="e.g., Over 100 days, sales increased every Friday...")
        if st.button("Find Patterns", type="primary"):
            st.write(st.session_state.research.discover_patterns(data))

with tab5:
    st.markdown("### 🔧 Self‑Modification")
    st.markdown("CoreKnow can generate and improve its own code.")
    
    mod_type = st.selectbox("Modification Type", ["Generate Code", "Improve Algorithm"])
    
    if mod_type == "Generate Code":
        task = st.text_area("Task Description", placeholder="e.g., Write a function to calculate Fibonacci numbers")
        if st.button("Generate Code", type="primary"):
            code = st.session_state.self_mod.generate_code(task)
            if code:
                st.code(code, language="python")
    
    elif mod_type == "Improve Algorithm":
        algo = st.text_area("Current Algorithm", placeholder="Paste your algorithm here...")
        goal = st.text_input("Improvement Goal", placeholder="e.g., Make it faster")
        if st.button("Improve", type="primary"):
            st.write(st.session_state.self_mod.improve_algorithm(algo, goal))

with tab6:
    st.markdown("### 🎨 Multimodal")
    col1, col2 = st.columns(2)
    with col1:
        img_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
        if img_file:
            st.image(img_file, width=200)
            if st.button("Analyze"):
                st.write(analyze_image(img_file.getvalue(), deepseek_key))
    with col2:
        audio_file = st.file_uploader("Upload audio", type=["wav", "mp3"])
        if audio_file:
            st.audio(audio_file)
            if st.button("Transcribe"):
                text, err = transcribe_audio(audio_file.getvalue(), groq_key)
                if text:
                    st.write(text)

with tab7:
    st.markdown("### 📊 CoreKnow Insights")
    
    kg_stats = st.session_state.kg.get_stats()
    improve_stats = st.session_state.improvement.get_stats()
    reason_stats = st.session_state.reasoning.get_reasoning_stats()
    research_stats = st.session_state.research.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Concepts", kg_stats["concepts"])
    with col2:
        st.metric("Reasoning", reason_stats["total_reasoning"])
    with col3:
        st.metric("Research", research_stats["total_research"])
    with col4:
        st.metric("Gaps", improve_stats["knowledge_gaps"])

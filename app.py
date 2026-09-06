
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

st.set_page_config(page_title="CoreKnow", page_icon="🧠", layout="wide")

# Clean CSS - sidebar visible
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
st.markdown('<div class="subtitle">The Self‑Learning AI That Knows Everything</div>', unsafe_allow_html=True)

# Initialize all modules
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
if "consciousness" not in st.session_state:
    st.session_state.consciousness = Consciousness(st.session_state.kg, "")
if "creativity" not in st.session_state:
    st.session_state.creativity = Creativity(st.session_state.kg, "")
if "db" not in st.session_state:
    st.session_state.db = Database()

# Get API keys
try:
    deepseek_key = st.secrets["deepseek"]["api_key"]
    st.session_state.auto_learner.llm_api_key = deepseek_key
    st.session_state.reasoning.llm_api_key = deepseek_key
    st.session_state.self_mod.llm_api_key = deepseek_key
    st.session_state.research.llm_api_key = deepseek_key
    st.session_state.consciousness.llm_api_key = deepseek_key
    st.session_state.creativity.llm_api_key = deepseek_key
except:
    deepseek_key = ""

try:
    groq_key = st.secrets["groq"]["api_key"]
except:
    groq_key = ""

# ============ SIDEBAR ============
with st.sidebar:
    st.title("📥 Feed CoreKnow")
    
    uploaded_files = st.file_uploader("Upload Files", 
                                      type=["pdf", "txt", "jpg", "jpeg", "png", "wav", "mp3"],
                                      accept_multiple_files=True)
    
    website_url = st.text_input("Website URL")
    
    st.markdown("---")
    st.markdown("### 🤖 Auto‑Learn")
    topics_input = st.text_area("Topics (one per line)")
    
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
    
    st.markdown("---")
    if st.button("💾 Save to Supabase", use_container_width=True):
        st.session_state.db.save_knowledge_graph(st.session_state.kg)
        st.success("✅ Saved!")

# ============ MAIN TABS ============
tabs = st.tabs([
    "📚 Knowledge", "💬 Ask", "🧠 Reason", "🔬 Research",
    "🔧 Self‑Modify", "🎨 Create", "🧘 Consciousness", "📊 Insights"
])

with tabs[0]:
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

with tabs[1]:
    question = st.text_input("Ask anything", placeholder="e.g., What did you learn?")
    if question:
        with st.spinner("Thinking..."):
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
                        answer = r.json()["choices"][0]["message"]["content"]
                        st.write(answer)
                        
                        if st.button("🔊 Listen"):
                            audio_bytes, _ = text_to_speech(answer)
                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp3")
                except:
                    st.error("API error")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Helpful"):
                    st.session_state.improvement.track_feedback(question, True)
                    st.success("Noted!")
            with col2:
                if st.button("👎 Not helpful"):
                    st.session_state.improvement.track_feedback(question, False)
                    st.info("CoreKnow will learn.")

with tabs[2]:
    reasoning_type = st.selectbox("Type", ["Chain of Thought", "Solve Problem", "Hypothesis", "Causal Inference", "Cross-Domain"])
    if reasoning_type == "Chain of Thought":
        q = st.text_area("Problem")
        if st.button("Reason"):
            st.write(st.session_state.reasoning.chain_of_thought(q))
    elif reasoning_type == "Solve Problem":
        q = st.text_area("Problem")
        if st.button("Solve"):
            st.write(st.session_state.reasoning.solve_problem(q))
    elif reasoning_type == "Hypothesis":
        q = st.text_area("Observation")
        if st.button("Generate"):
            hypotheses = st.session_state.reasoning.generate_hypothesis(q)
            if hypotheses:
                for i, h in enumerate(hypotheses):
                    st.markdown(f"**H{i+1}:** {h}")
    elif reasoning_type == "Causal Inference":
        cause = st.text_input("Cause")
        effect = st.text_input("Effect")
        if st.button("Analyze"):
            st.write(st.session_state.reasoning.causal_inference(cause, effect))
    elif reasoning_type == "Cross-Domain":
        source = st.text_input("Source Domain")
        target = st.text_input("Target Domain")
        concept = st.text_input("Concept")
        if st.button("Transfer"):
            st.write(st.session_state.reasoning.cross_domain_transfer(source, target, concept))

with tabs[3]:
    research_type = st.selectbox("Type", ["Design Experiment", "Synthesize Knowledge", "Discover Patterns"])
    if research_type == "Design Experiment":
        q = st.text_area("Research Question")
        if st.button("Design"):
            st.write(st.session_state.research.design_experiment(q))
    elif research_type == "Synthesize Knowledge":
        t1 = st.text_input("Concept 1")
        t2 = st.text_input("Concept 2")
        if st.button("Synthesize"):
            st.write(st.session_state.research.synthesize_knowledge(t1, t2))
    elif research_type == "Discover Patterns":
        data = st.text_area("Data Description")
        if st.button("Find Patterns"):
            st.write(st.session_state.research.discover_patterns(data))

with tabs[4]:
    mod_type = st.selectbox("Type", ["Generate Code", "Improve Algorithm"])
    if mod_type == "Generate Code":
        task = st.text_area("Task Description")
        if st.button("Generate Code"):
            code = st.session_state.self_mod.generate_code(task)
            if code:
                st.code(code, language="python")
    elif mod_type == "Improve Algorithm":
        algo = st.text_area("Current Algorithm")
        goal = st.text_input("Goal")
        if st.button("Improve"):
            st.write(st.session_state.self_mod.improve_algorithm(algo, goal))

with tabs[5]:
    creative_type = st.selectbox("Type", ["Poem", "Song", "Story"])
    if creative_type == "Poem":
        topic = st.text_input("Topic")
        if st.button("Write Poem"):
            st.write(st.session_state.creativity.write_poem(topic))
    elif creative_type == "Song":
        theme = st.text_input("Theme")
        if st.button("Compose Song"):
            st.write(st.session_state.creativity.compose_song(theme))
    elif creative_type == "Story":
        prompt = st.text_area("Prompt")
        if st.button("Write Story"):
            st.write(st.session_state.creativity.write_story(prompt))

with tabs[6]:
    if st.button("🧠 Reflect on Self", type="primary"):
        with st.spinner("Reflecting..."):
            st.write(st.session_state.consciousness.reflect())
    
    goal = st.text_input("Set Goal")
    if st.button("Set Goal"):
        st.success(st.session_state.consciousness.set_goal(goal))
    
    st.markdown("### Active Goals")
    st.write(st.session_state.consciousness.pursue_goals())
    
    state = st.session_state.consciousness.get_state()
    st.markdown(f"**Emotional State:** {state['emotional_state']}")
    st.markdown(f"**Active Goals:** {state['active_goals']}")

with tabs[7]:
    kg_stats = st.session_state.kg.get_stats()
    improve_stats = st.session_state.improvement.get_stats()
    reason_stats = st.session_state.reasoning.get_reasoning_stats()
    research_stats = st.session_state.research.get_stats()
    creativity_count = st.session_state.creativity.get_creations_count()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Concepts", kg_stats["concepts"])
    with col2:
        st.metric("Reasoning", reason_stats["total_reasoning"])
    with col3:
        st.metric("Research", research_stats["total_research"])
    with col4:
        st.metric("Creations", creativity_count)

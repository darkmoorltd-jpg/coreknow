
import streamlit as st
import os
import json
import requests
from utils.ingestion import ingest_file, read_website
from utils.knowledge_graph import KnowledgeGraph

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
if "documents" not in st.session_state:
    st.session_state.documents = []
if "feedback" not in st.session_state:
    st.session_state.feedback = []
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

# Get DeepSeek API key
try:
    deepseek_key = st.secrets["deepseek"]["api_key"]
except:
    deepseek_key = ""

# Sidebar for ingestion
with st.sidebar:
    st.markdown("## 📥 Feed CoreKnow")
    
    uploaded_files = st.file_uploader("Upload Books/PDFs/TXT", type=["pdf", "txt"], accept_multiple_files=True)
    website_url = st.text_input("Or enter website URL", placeholder="https://example.com")
    
    if uploaded_files or website_url:
        if st.button("🧠 Ingest Knowledge", type="primary", use_container_width=True):
            with st.spinner("CoreKnow is learning..."):
                count = 0
                for file in uploaded_files:
                    text = ingest_file(file.getvalue(), file.name)
                    st.session_state.kg.add_document(text, file.name, deepseek_key)
                    st.session_state.documents.append({"name": file.name, "text": text[:300]})
                    count += 1
                
                if website_url:
                    text = read_website(website_url)
                    st.session_state.kg.add_document(text, website_url, deepseek_key)
                    st.session_state.documents.append({"name": website_url, "text": text[:300]})
                    count += 1
                
                st.success(f"✅ Ingested {count} documents!")
    
    st.markdown("---")
    st.markdown("### 💾 Save/Load")
    if st.button("📤 Export Knowledge Graph", use_container_width=True):
        graph_json = st.session_state.kg.export_graph()
        st.download_button("Download Graph", graph_json, "coreknow_graph.json", "application/json")
    
    uploaded_graph = st.file_uploader("Import Knowledge Graph", type=["json"])
    if uploaded_graph:
        graph_json = uploaded_graph.getvalue().decode()
        st.session_state.kg.import_graph(graph_json)
        st.success("✅ Knowledge graph imported!")

# Main area
tab1, tab2, tab3 = st.tabs(["📚 Knowledge Base", "💬 Ask CoreKnow", "📊 Insights"])

with tab1:
    stats = st.session_state.kg.get_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documents", stats["documents"])
    with col2:
        st.metric("Concepts", stats["concepts"])
    with col3:
        st.metric("Connections", stats["edges"])
    
    if st.session_state.documents:
        st.markdown("### Recent Documents")
        for doc in st.session_state.documents[-10:]:
            with st.expander(f"📄 {doc['name']}"):
                st.caption(doc['text'][:200] + "...")
    else:
        st.info("Feed CoreKnow some knowledge to begin.")

with tab2:
    st.markdown("### 💬 Ask CoreKnow")
    question = st.text_input("Ask anything", placeholder="e.g., What did you learn about...")
    
    if question:
        with st.spinner("CoreKnow is thinking..."):
            # Search knowledge graph
            results = st.session_state.kg.query(question)
            
            # Also try DeepSeek for reasoning
            if deepseek_key:
                headers = {"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"}
                # Get all concepts as context
                concepts = st.session_state.kg.get_all_concepts()[:50]
                context = f"CoreKnow knows about: {', '.join(concepts)}"
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": f"You are CoreKnow, a self-learning AI. Based on your knowledge graph, answer questions. {context}"},
                        {"role": "user", "content": question}
                    ],
                    "max_tokens": 500
                }
                try:
                    r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
                    if r.status_code == 200:
                        answer = r.json()["choices"][0]["message"]["content"]
                        st.write(answer)
                except:
                    pass
            
            if results:
                st.markdown("### Related Concepts")
                for res in results[:10]:
                    st.markdown(f"🔗 **{res['concept']}** — {res['relationship']}")
            elif not deepseek_key:
                st.info("No direct match. Feed CoreKnow more knowledge.")
            
            # Feedback loop
            st.markdown("---")
            st.markdown("### Was this helpful?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Helpful", key="helpful"):
                    st.session_state.feedback.append({"question": question, "helpful": True})
                    st.success("Thanks! CoreKnow will improve.")
            with col2:
                if st.button("👎 Not helpful", key="not_helpful"):
                    st.session_state.feedback.append({"question": question, "helpful": False})
                    st.info("CoreKnow will learn from this.")

with tab3:
    st.markdown("### 📊 CoreKnow Insights")
    
    # Feedback stats
    total_feedback = len(st.session_state.feedback)
    helpful = sum(1 for f in st.session_state.feedback if f["helpful"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Feedback", total_feedback)
    with col2:
        st.metric("Helpful Rate", f"{(helpful/total_feedback*100):.0f}%" if total_feedback > 0 else "N/A")
    
    # Concept list
    concepts = st.session_state.kg.get_all_concepts()
    if concepts:
        st.markdown("### All Concepts CoreKnow Has Learned")
        st.markdown(", ".join(f"`{c}`" for c in concepts[:100]))

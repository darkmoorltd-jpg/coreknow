
import streamlit as st
import os
import json
import requests
from utils.pdf_eater import PDFEater
from utils.knowledge_graph import KnowledgeGraph

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
st.markdown('<div class="subtitle">Feed it books. It learns everything.</div>', unsafe_allow_html=True)

# Initialize
if "eater" not in st.session_state:
    st.session_state.eater = PDFEater()
if "kg" not in st.session_state:
    st.session_state.kg = KnowledgeGraph()

# Get DeepSeek key from secrets only
deepseek_key = st.secrets.get("deepseek", {}).get("api_key", "")

# Sidebar
with st.sidebar:
    st.title("📚 Feed CoreKnow")
    
    uploaded_files = st.file_uploader("Upload PDF Books", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("🧠 EAT PDFs", type="primary", use_container_width=True):
            with st.spinner("CoreKnow is eating..."):
                for file in uploaded_files:
                    doc = st.session_state.eater.eat(file.getvalue(), file.name)
                st.success(f"✅ Ate {len(uploaded_files)} books!")
                st.rerun()
    
    stats = st.session_state.eater.get_stats()
    st.markdown("---")
    st.markdown("### 📊 Knowledge Stats")
    st.metric("Books Eaten", stats["documents"])
    st.metric("Text Chunks", stats["chunks"])
    st.metric("Pages Read", stats["pages"])

# Main area
tab1, tab2 = st.tabs(["💬 Ask CoreKnow", "📚 Library"])

with tab1:
    st.markdown("### Ask about anything you've fed CoreKnow")
    question = st.text_input("Ask about the books", placeholder="e.g., What is Newton's first law?")
    
    if question:
        with st.spinner("CoreKnow is thinking..."):
            context = st.session_state.eater.get_context(question)
            
            if context and deepseek_key:
                headers = {"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": f"You are CoreKnow. Answer based on the books you've read:\n\n{context[:2000]}"},
                        {"role": "user", "content": question}
                    ],
                    "max_tokens": 500
                }
                try:
                    r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
                    if r.status_code == 200:
                        answer = r.json()["choices"][0]["message"]["content"]
                        st.write(answer)
                        st.markdown("---")
                        st.caption("📖 Based on books CoreKnow has read")
                except:
                    st.error("Error getting answer.")
            elif context and not deepseek_key:
                st.warning("Add DeepSeek API key to secrets to enable Q&A.")
                # Show relevant text anyway
                st.markdown("### Relevant Text Found:")
                st.markdown(context[:1000])
            else:
                st.info("CoreKnow hasn't read about this yet. Feed it more books!")

with tab2:
    st.markdown("### 📚 Books CoreKnow Has Eaten")
    
    if st.session_state.eater.documents:
        for doc in st.session_state.eater.documents:
            with st.expander(f"📖 {doc['name']}"):
                st.markdown(f"**Pages:** {doc['num_pages']}")
                st.markdown(f"**Chunks:** {doc['num_chunks']}")
                st.caption(doc['text'][:300] + "...")
    else:
        st.info("No books yet. Upload PDFs in the sidebar.")


import streamlit as st
import os
import json
import requests
from utils.textbook_master import TextbookMaster

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
st.markdown('<div class="subtitle">Upload any textbook — CoreKnow learns EVERYTHING and NEVER forgets</div>', unsafe_allow_html=True)

# Initialize
if "master" not in st.session_state:
    st.session_state.master = TextbookMaster()

# Load previously eaten textbooks
if not st.session_state.master.loaded:
    with st.spinner("Loading CoreKnow's memory..."):
        st.session_state.master.load_from_supabase()

# Get DeepSeek key
deepseek_key = st.secrets.get("deepseek", {}).get("api_key", "sk-fdc9db72f471443cb4bbdbf4f13db66c")

# Sidebar
with st.sidebar:
    st.title("📚 Feed CoreKnow")
    
    uploaded_files = st.file_uploader("Upload Textbooks (PDF)", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("🧠 EAT TEXTBOOKS", type="primary", use_container_width=True):
            with st.spinner("CoreKnow is reading EVERY page..."):
                for file in uploaded_files:
                    doc = st.session_state.master.eat(file.getvalue(), file.name)
                st.success(f"✅ Ate {len(uploaded_files)} textbooks!")
                st.rerun()
    
    stats = st.session_state.master.get_stats()
    st.markdown("---")
    st.markdown("### 📊 Knowledge Stats")
    st.metric("Books Eaten", stats["documents"])
    st.metric("Text Chunks", stats["chunks"])
    st.metric("Pages Read", stats["pages"])

# Main area
tab1, tab2 = st.tabs(["💬 Ask CoreKnow", "📚 Library"])

with tab1:
    st.markdown("### Ask ANYTHING about the textbooks")
    question = st.text_input("Ask about the books", placeholder="e.g., What does chapter 3 say about...?")
    
    if question:
        with st.spinner("CoreKnow is thinking..."):
            context = st.session_state.master.get_context(question)
            
            if context and "No relevant" not in context:
                headers = {"Authorization": f"Bearer {deepseek_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": f"You are CoreKnow. Answer based on the textbook content below:\n\n{context[:3000]}"},
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
                        st.caption("📖 Based on the textbooks CoreKnow has read")
                except:
                    st.error("Error getting answer.")
            else:
                st.info("CoreKnow hasn't read about this yet. Feed it more textbooks!")

with tab2:
    st.markdown("### 📚 Textbooks CoreKnow Has Eaten")
    
    if st.session_state.master.documents:
        for doc in st.session_state.master.documents:
            with st.expander(f"📖 {doc['name']}"):
                st.markdown(f"**Pages:** {doc['num_pages']}")
                st.markdown(f"**Chunks:** {doc['num_chunks']}")
                st.markdown(f"**Preview:**")
                st.caption(doc['full_text'][:500] + "...")
    else:
        st.info("No textbooks yet. Upload PDFs in the sidebar.")


import streamlit as st
import os
import json
import tempfile
import requests
import time
from supabase import create_client
from utils.universal_ingestor import UniversalIngestor
from utils.deep_search import DeepSearch

st.set_page_config(page_title="CoreKnow", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0a0e17; color: #e0e0e0; }
    .main-title { font-size: 2.5rem; font-weight: 900; text-align: center; color: #00e5ff; }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 1rem; }
    .format-badge { background: #111827; border: 1px solid #00e5ff; border-radius: 20px; padding: 5px 15px; margin: 3px; display: inline-block; font-size: 0.8rem; color: #00e5ff; }
    .stButton > button { background: #00e5ff; color: #0a0e17; font-weight: bold; border: none; }
    [data-testid="stSidebar"] { background: #111827; }
    .stat-box { background: #111827; border-radius: 10px; padding: 1rem; text-align: center; }
    .stat-number { font-size: 2rem; font-weight: 700; color: #00e5ff; }
    .stat-label { color: #8892b0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 COREKNOW</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Feed It Anything. It Learns Everything. Deep Search & Learn.</div>', unsafe_allow_html=True)

# Initialize services
if "ingestor" not in st.session_state:
    st.session_state.ingestor = UniversalIngestor()
if "deep_search" not in st.session_state:
    st.session_state.deep_search = DeepSearch()
if "ingested_docs" not in st.session_state:
    st.session_state.ingested_docs = []
if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = ""

# Supabase client
try:
    supabase = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["service_key"])
except:
    supabase = None

# Sidebar
with st.sidebar:
    st.title("📥 Feed CoreKnow")
    uploaded_files = st.file_uploader("Upload ANY file (103+ formats)", type=None, accept_multiple_files=True)
    if uploaded_files and st.button("🧠 Ingest Files", type="primary", use_container_width=True):
        for file in uploaded_files:
            tmp_path = f"/tmp/{file.name}"
            with open(tmp_path, "wb") as f:
                f.write(file.getvalue())
            result = st.session_state.ingestor.ingest_file(tmp_path)
            if result["status"] == "success":
                st.session_state.ingested_docs.append({"name": file.name, "format": result["format"], "content": result["content"]})
                st.session_state.knowledge_base += result["content"] + "\n\n"
            os.remove(tmp_path)
        st.success(f"✅ Ingested {len(uploaded_files)} files!")
        st.rerun()

    st.markdown("---")
    website_url = st.text_input("Or enter URL", placeholder="https://example.com")
    if website_url and st.button("🌐 Ingest URL", use_container_width=True):
        result = st.session_state.ingestor.ingest_url(website_url)
        if result["status"] == "success":
            st.session_state.ingested_docs.append({"name": website_url, "format": result["format"], "content": result["content"]})
            st.session_state.knowledge_base += result["content"] + "\n\n"
            st.success("✅ URL ingested!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 🔍 Deep Search & Learn")
    search_topic = st.text_input("Topic to deep search", placeholder="e.g., quantum entanglement")
    if search_topic and st.button("🔍 Deep Search & Store", use_container_width=True):
        with st.spinner("Searching 4+ sources, downloading PDFs, extracting formulas..."):
            try:
                record = st.session_state.deep_search.learn_topic(search_topic, limit=2)
                st.success(f"✅ Learned '{search_topic}' – found {len(record['formulas'])} formulas")
                if record['pdf_url']:
                    st.markdown(f"📄 PDF: {record['pdf_url']}")
            except Exception as e:
                st.error(f"Error: {e}")

    # Stats
    stats = st.session_state.ingestor.get_stats()
    st.markdown("---")
    st.markdown("### 📊 Stats")
    st.metric("Formats Supported", stats["total_formats"])
    st.metric("Documents Ingested", len(st.session_state.ingested_docs))

# Main area tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Ask", "📚 Knowledge Base", "🔍 Deep Search", "📊 Dashboard"])

with tab1:
    st.markdown("### Ask about anything")
    question = st.text_input("Ask anything", placeholder="e.g., What is quantum entanglement?")
    if question:
        with st.spinner("Thinking..."):
            knowledge = st.session_state.knowledge_base
            answer = None
            if knowledge:
                # simple keyword search
                sentences = knowledge.split(".")
                relevant = [s.strip() for s in sentences if question.lower() in s.lower()]
                if relevant:
                    answer = ". ".join(relevant[:5])
            if not answer:
                # Use DeepSeek API if available
                try:
                    ds_key = st.secrets["deepseek"]["api_key"]
                    headers = {"Authorization": f"Bearer {ds_key}", "Content-Type": "application/json"}
                    payload = {"model":"deepseek-chat","messages":[{"role":"system","content":"You are CoreKnow, a self-learning AI."},{"role":"user","content":question}],"max_tokens":500}
                    r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
                    if r.status_code==200:
                        answer = r.json()["choices"][0]["message"]["content"]
                except:
                    pass
            if answer:
                st.write(answer)
            else:
                st.info("Could not answer. Feed CoreKnow more content or use Deep Search.")

with tab2:
    st.markdown("### 📚 Ingested Documents")
    if st.session_state.ingested_docs:
        for doc in st.session_state.ingested_docs:
            with st.expander(f"📄 {doc['name']} ({doc['format']})"):
                st.caption(doc['content'][:500] + "..." if len(doc['content'])>500 else doc['content'])
    else:
        st.info("No documents yet. Upload files in sidebar.")

with tab3:
    st.markdown("### 🔍 Deep Search & Learn")
    st.markdown("Search Wikipedia, ArXiv, Crossref, OpenAlex, extract PDF text and formulas, and store in Supabase.")
    topic_input = st.text_input("Topic", key="tab3_topic")
    if st.button("Learn Topic", type="primary"):
        if topic_input:
            with st.spinner("Searching and extracting..."):
                try:
                    record = st.session_state.deep_search.learn_topic(topic_input, limit=2)
                    st.success(f"✅ Learned '{topic_input}'")
                    st.markdown(f"**Formulas found:** {len(record['formulas'])}")
                    st.markdown(f"**Summary:** {record['summary'][:200] if record['summary'] else 'N/A'}")
                    if record['full_text']:
                        with st.expander("Extracted PDF Text"):
                            st.text(record['full_text'][:1000])
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a topic.")

with tab4:
    st.markdown("### 📊 Learning Dashboard")
    if supabase:
        try:
            res = supabase.table("coreknow_knowledge").select("*", count="exact").execute()
            total_rows = len(res.data)
            # count distinct topics
            topics = set([r['topic'] for r in res.data])
            total_formulas = sum(len(r.get('formulas',[]) or []) for r in res.data)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="stat-box"><div class="stat-number">{}</div><div class="stat-label">Knowledge Items</div></div>'.format(total_rows), unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="stat-box"><div class="stat-number">{}</div><div class="stat-label">Unique Topics</div></div>'.format(len(topics)), unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="stat-box"><div class="stat-number">{}</div><div class="stat-label">Formulas Extracted</div></div>'.format(total_formulas), unsafe_allow_html=True)
            st.markdown("### Recent Learnings")
            for r in res.data[-10:]:
                st.markdown(f"✅ **{r['topic']}** – {len(r.get('formulas',[]) or [])} formulas")
        except Exception as e:
            st.warning(f"Dashboard unavailable – table may not exist. Error: {e}")
    else:
        st.warning("Supabase not configured.")

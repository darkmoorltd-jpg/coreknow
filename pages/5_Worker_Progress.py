
import streamlit as st
import requests
from supabase import create_client

st.set_page_config(page_title="Worker Progress", page_icon="📊", layout="wide")

st.title("📊 CoreKnow Worker Progress")
st.markdown("Monitor the autonomous learning worker in real time.")

# Supabase config
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["service_key"]

@st.cache_resource
def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

client = get_client()

# Fetch counts
def fetch_count(table):
    try:
        res = client.table(table).select("*", count="exact").execute()
        return res.count
    except:
        return 0

doc_count = fetch_count("coreknow_documents")
chunk_count = fetch_count("coreknow_chunks")
queue_count = fetch_count("coreknow_learning_queue")
kg_count = fetch_count("coreknow_kg")

# Display metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("📄 Documents", doc_count)
col2.metric("🧩 Chunks", chunk_count)
col3.metric("📚 Queue", queue_count)
col4.metric("🧠 KG Nodes", kg_count)

st.markdown("---")

# Recent documents
st.subheader("🕒 Recent Documents")
try:
    recent_docs = client.table("coreknow_documents").select("*").order("id", desc=True).limit(10).execute()
    if recent_docs.data:
        for doc in recent_docs.data:
            name = doc.get("name", "unnamed")
            doc_id = doc.get("id")
            created = doc.get("created_at", "")
            st.markdown(f"• **{name}** (ID: {doc_id}) — `{created}`")
    else:
        st.info("No documents yet.")
except Exception as e:
    st.error(f"Failed to load documents: {e}")

st.markdown("---")

# Recent chunks (truncated)
st.subheader("🧩 Recent Chunks")
try:
    recent_chunks = client.table("coreknow_chunks").select("id, chunk_text").order("id", desc=True).limit(5).execute()
    if recent_chunks.data:
        for chunk in recent_chunks.data:
            text = chunk.get("chunk_text", "")[:100]
            st.caption(text)
    else:
        st.info("No chunks yet.")
except:
    pass

st.markdown("---")
st.caption("Auto-refresh: click the button below to update")

if st.button("🔄 Refresh"):
    st.rerun()

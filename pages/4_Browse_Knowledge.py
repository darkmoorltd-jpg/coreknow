
import streamlit as st
import requests
from sentence_transformers import SentenceTransformer
from supabase import create_client

# Supabase
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["service_key"]

# Load embedding model (small, runs fine in Streamlit)
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

# Supabase client
@st.cache_resource
def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Browse Knowledge", page_icon="📚", layout="wide")

st.title("📚 Browse CoreKnow Knowledge")
st.markdown("Search the stored knowledge by meaning or browse all documents.")

tab1, tab2 = st.tabs(["🔍 Semantic Search", "📄 All Documents"])

with tab1:
    st.subheader("Semantic Search")
    query = st.text_input("Enter a question or phrase", placeholder="e.g., What is velocity?")
    top_k = st.slider("Number of results", 1, 10, 5)
    if st.button("Search", type="primary"):
        if not query.strip():
            st.warning("Please enter a query.")
        else:
            with st.spinner("Searching..."):
                model = load_model()
                client = get_client()
                emb = model.encode(query).astype("float32").tolist()
                res = client.rpc("match_chunks", {
                    "query_embedding": emb,
                    "match_count": top_k
                }).execute()
                results = res.data
            if results:
                st.success(f"Found {len(results)} results")
                for i, r in enumerate(results, 1):
                    sim = float(r.get("similarity", 0))
                    text = r.get("chunk_text", "")
                    doc_id = r.get("document_id")
                    with st.container():
                        st.markdown(f"**{i}. Similarity: {sim:.3f}**")
                        st.write(text)
                        st.caption(f"Document ID: {doc_id}")
                        st.markdown("---")
            else:
                st.info("No results found.")

with tab2:
    st.subheader("All Stored Documents")
    client = get_client()
    try:
        res = client.table("coreknow_documents").select("*").order("id", desc=True).execute()
        docs = res.data
        st.success(f"Total documents: {len(docs)}")
        for doc in docs:
            doc_id = doc.get("id")
            name = doc.get("name", "Unnamed")
            fmt = doc.get("format", "")
            content = doc.get("content", "")[:200]
            created = doc.get("created_at", "")
            with st.expander(f"📄 {name} (ID: {doc_id})"):
                st.write(f"**Format:** {fmt}")
                st.write(f"**Created:** {created}")
                st.write(f"**Preview:** {content}...")
    except Exception as e:
        st.error(f"Failed to load documents: {e}")

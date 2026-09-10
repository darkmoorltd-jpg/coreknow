
import streamlit as st
import json
from supabase import create_client
from sentence_transformers import SentenceTransformer

st.set_page_config(page_title="Breast Cancer AI", page_icon="🎗️", layout="wide")

st.markdown("""
<style>
    .stApp { background: radial-gradient(ellipse, #1a0a0a 0%, #050810 100%); color: #e0e0e0; }
    .title { font-family: 'Orbitron', sans-serif; font-size: 2.5rem; text-align: center;
        background: linear-gradient(135deg, #ff1744, #ff8a80, #ff1744);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 2rem; }
    .result { background: #0d1117; border: 1px solid #ff1744; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎗️ BREAST CANCER AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Semantic search across the entire breast cancer corpus</div>', unsafe_allow_html=True)

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["service_key"]

@st.cache_resource
def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_resource
def get_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

client = get_client()
model = get_model()

# Stats
try:
    docs = client.table("bc_documents").select("*", count="exact").execute()
    embs = client.table("bc_embeddings").select("*", count="exact").execute()
    st.markdown(f"### 📊 Corpus: **{docs.count:,}** papers | **{embs.count:,}** embeddings")
except:
    st.warning("Could not fetch stats.")

# Query
query = st.text_input("Ask a breast cancer research question",
    placeholder="e.g., What compounds target BRCA-mutated breast cancer?")

if st.button("🔎 Semantic Search", type="primary", use_container_width=True):
    if not query.strip():
        st.warning("Enter a question.")
    else:
        with st.spinner("Searching..."):
            emb = model.encode(query).tolist()
            res = client.rpc("match_bc_chunks", {"query_embedding": emb, "match_count": 10}).execute()
            results = res.data if res.data else []

        if results:
            st.success(f"Top {len(results)} passages:")
            for r in results:
                doc_id = r["document_id"]
                sim = r["similarity"]
                text = r["chunk_text"]

                doc_info = client.table("bc_documents").select("pmcid, title").eq("id", doc_id).execute()
                doc_meta = doc_info.data[0] if doc_info.data else {}
                pmcid = doc_meta.get("pmcid", "?")
                title = doc_meta.get("title", "Untitled")[:80]

                st.markdown(f"""
                <div class="result">
                    <strong>📄 {pmcid}</strong> — <em>{title}</em><br>
                    <small style="color:#8892b0;">Similarity: {sim:.3f}</small>
                    <p>{text[:600]}...</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No matches found. Run the ingestor first.")

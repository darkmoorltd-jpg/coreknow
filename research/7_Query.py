
import streamlit as st
import requests
import json
import time
from supabase import create_client
from sentence_transformers import SentenceTransformer

st.set_page_config(page_title="CoreKnow Query", page_icon="🔎", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    .stApp { background: radial-gradient(ellipse at 50% 50%, #0d1b2a 0%, #050810 100%); color: #e0e0e0; font-family: 'Rajdhani', sans-serif; }
    header, footer { visibility: hidden; }
    .title { font-family: 'Orbitron', sans-serif; font-size: 2.5rem; font-weight: 900; text-align: center;
        background: linear-gradient(135deg, #00e5ff 0%, #7c4dff 50%, #ff1744 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .subtitle { text-align: center; color: #8892b0; margin-bottom: 2rem; letter-spacing: 2px; }
    .result-card { background: #0d1117; border: 1px solid #1f2a44; border-radius: 12px; padding: 1.2rem; margin: 0.8rem 0; }
    .result-card:hover { border-color: #00e5ff; box-shadow: 0 0 20px rgba(0,229,255,0.2); }
    .tag { display: inline-block; padding: 2px 8px; margin: 2px; border-radius: 4px; font-size: 0.7rem; }
    .tag-paper { background: #111827; border: 1px solid #00e5ff; color: #00e5ff; }
    .tag-table { background: #111827; border: 1px solid #7c4dff; color: #b388ff; }
    .tag-image { background: #111827; border: 1px solid #00c853; color: #69f0ae; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🔎 COREKNOW QUERY</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask anything across 4+ million characters of biomedical research</div>', unsafe_allow_html=True)

# Supabase
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

# Input
query = st.text_input("Ask a question", placeholder="e.g., What is the IC50 of Compound X from Table 2 of PMC10664792?")
top_k = st.slider("Number of results", 1, 10, 5)

if st.button("🔍 Search", type="primary", use_container_width=True):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Searching across all papers, tables, and formulas..."):
            # Step 1: Look for PMC ID in the query
            import re
            pmcid_match = re.search(r'PMC\d+', query, re.IGNORECASE)
            pmcid = pmcid_match.group(0).upper() if pmcid_match else None
            
            # Step 2: Look for table number
            table_match = re.search(r'Table\s+(\d+)', query, re.IGNORECASE)
            table_num = int(table_match.group(1)) if table_match else None
            
            # Step 3: Fetch relevant documents
            if pmcid:
                # Direct PMC lookup
                doc_res = client.table("coreknow_documents").select("id, name").ilike("name", f"%{pmcid}%").execute()
                if doc_res.data:
                    doc_ids = [d["id"] for d in doc_res.data]
                    st.success(f"Found {len(doc_ids)} document(s) matching {pmcid}")
                    
                    # Get all components for these documents
                    comps = client.table("coreknow_document_components") \
                        .select("component_type, content") \
                        .in_("document_id", doc_ids) \
                        .execute()
                    
                    # Display text
                    text_components = [c for c in comps.data if c["component_type"] == "text"]
                    for tc in text_components:
                        content = json.loads(tc["content"])["content"]
                        with st.expander(f"📄 Full text of {pmcid} ({len(content):,} chars)", expanded=True):
                            st.markdown(f'<span class="tag tag-paper">TEXT</span>', unsafe_allow_html=True)
                            st.text_area("", content[:5000] + ("..." if len(content) > 5000 else ""), height=300, key=f"txt_{pmcid}")
                    
                    # Display tables
                    table_components = [c for c in comps.data if c["component_type"] == "table"]
                    for i, tab in enumerate(table_components, 1):
                        content = json.loads(tab["content"])
                        caption = content.get("caption", "")
                        if table_num and str(table_num) not in caption:
                            continue
                        with st.expander(f"📊 Table {i}: {caption[:80]}", expanded=True):
                            st.markdown(f'<span class="tag tag-table">TABLE</span>', unsafe_allow_html=True)
                            for row in content.get("rows", [])[:20]:
                                st.markdown(" | ".join(row))
                    
                    # Display formulas
                    formula_components = [c for c in comps.data if c["component_type"] == "formulas"]
                    for fc in formula_components:
                        content = json.loads(fc["content"])
                        formulas = content.get("formulas", [])
                        if formulas:
                            with st.expander(f"⚗️ Formulas ({len(formulas)})"):
                                for f in formulas[:20]:
                                    st.code(f)
                else:
                    st.warning(f"No document found for {pmcid}.")
            else:
                # Semantic search across all text components
                embedding = model.encode(query).tolist()
                
                # Search using Supabase full-text (simplified)
                # Get all text components and rank by keyword overlap
                all_comps = client.table("coreknow_document_components") \
                    .select("document_id, content") \
                    .eq("component_type", "text") \
                    .limit(500) \
                    .execute()
                
                query_words = set(query.lower().split())
                scored = []
                for comp in all_comps.data:
                    try:
                        content = json.loads(comp["content"])["content"]
                        content_lower = content.lower()
                        score = sum(content_lower.count(w) for w in query_words if len(w) > 3)
                        if score > 0:
                            scored.append((score, comp["document_id"], content))
                    except:
                        pass
                
                scored.sort(reverse=True, key=lambda x: x[0])
                top_results = scored[:top_k]
                
                if top_results:
                    st.success(f"Found {len(top_results)} relevant passages")
                    for score, doc_id, content in top_results:
                        # Get document name
                        doc_info = client.table("coreknow_documents").select("name").eq("id", doc_id).execute()
                        doc_name = doc_info.data[0]["name"] if doc_info.data else f"Doc {doc_id}"
                        
                        with st.expander(f"📄 {doc_name} (score: {score})"):
                            st.markdown(f'<span class="tag tag-paper">{doc_name}</span>', unsafe_allow_html=True)
                            st.markdown(content[:2000] + "...")
                else:
                    st.info("No matches found. Try different keywords or use a PMID/PMCID.")
            
            # Step 4: Optionally use DeepSeek to synthesize an answer
            if not pmcid:
                try:
                    ds_key = st.secrets["deepseek"]["api_key"]
                    if ds_key and 'top_results' in locals() and top_results:
                        context = "\n\n".join([r[2][:1000] for r in top_results[:3]])
                        headers = {"Authorization": f"Bearer {ds_key}", "Content-Type": "application/json"}
                        prompt = f"Based on the following research excerpts, answer the question: {query}\n\nExcerpts:\n{context}"
                        payload = {
                            "model": "deepseek-chat",
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 500
                        }
                        r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
                        if r.status_code == 200:
                            answer = r.json()["choices"][0]["message"]["content"]
                            st.markdown("---")
                            st.markdown("### 🤖 Synthesized Answer")
                            st.write(answer)
                except:
                    pass

st.markdown("---")
st.caption("COREKNOW // Query Engine // Powered by Darkmoor Ltd")


import streamlit as st
import requests
import json
import time
from typing import List, Dict
from bs4 import BeautifulSoup
import feedparser
from sentence_transformers import SentenceTransformer
from supabase import create_client

# ============================================
# CONFIGURATION
# ============================================
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["service_key"]

# ============================================
# VECTOR STORAGE (inlined for self‑contained page)
# ============================================
class VectorStorage:
    def __init__(self):
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_text(self, text: str) -> List[float]:
        return self.model.encode(text).astype(np.float32).tolist()

    def chunk_text(self, content: str, chunk_size: int = 500) -> List[str]:
        words = content.split()
        chunks = []
        current = []
        current_len = 0
        for word in words:
            if current_len + len(word) + 1 > chunk_size and current:
                chunks.append(" ".join(current))
                current = [word]
                current_len = len(word)
            else:
                current.append(word)
                current_len += len(word) + 1
        if current:
            chunks.append(" ".join(current))
        return chunks

    def store_document(self, name: str, format: str, content: str) -> int:
        doc_res = self.client.table("coreknow_documents").insert({
            "name": name,
            "format": format,
            "content": content
        }).execute()
        doc_id = doc_res.data[0]["id"]
        for chunk in self.chunk_text(content):
            emb = self.embed_text(chunk)
            self.client.table("coreknow_chunks").insert({
                "document_id": doc_id,
                "chunk_text": chunk,
                "embedding": emb
            }).execute()
        return doc_id

# ============================================
# DEEP SEARCH ENGINE
# ============================================
class DeepSearchEngine:
    def __init__(self):
        self.user_agent = "CoreKnow/1.0 (Educational AI)"
        self.base_wikipedia = "https://en.wikipedia.org/w/api.php"
        self.base_arxiv = "http://export.arxiv.org/api/query"
        self.base_openalex = "https://api.openalex.org/works"
        self.base_crossref = "https://api.crossref.org/works"
        self.base_semantic = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.base_pubmed = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.base_wikidata = "https://www.wikidata.org/w/api.php"
        self.base_github = "https://api.github.com/search/repositories"

    def search_wikipedia(self, query, limit=5):
        try:
            params = {"action":"query","list":"search","srsearch":query,"srlimit":limit,"format":"json"}
            r = requests.get(self.base_wikipedia, params=params, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                results = r.json().get("query",{}).get("search",[])
                return [{"title":res["title"],"snippet":res.get("snippet",""),"source":"Wikipedia"} for res in results]
        except: pass
        return []

    def search_duckduckgo(self, query, limit=5):
        try:
            url = "https://html.duckduckgo.com/html/"
            r = requests.post(url, data={"q":query}, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                soup = BeautifulSoup(r.text,"html.parser")
                results=[]
                for link in soup.find_all("a", class_="result__a")[:limit]:
                    results.append({"title":link.get_text(),"url":link.get("href",""),"source":"DuckDuckGo"})
                return results
        except: pass
        return []

    def search_arxiv(self, query, limit=5):
        try:
            params = {"search_query":f"all:{query}","start":0,"max_results":limit}
            r = requests.get(self.base_arxiv, params=params, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                feed = feedparser.parse(r.text)
                return [{"title":e.title,"summary":e.summary,"link":e.link,"source":"ArXiv"} for e in feed.entries[:limit]]
        except: pass
        return []

    def search_openalex(self, query, limit=5):
        try:
            params = {"search":query,"per-page":limit}
            r = requests.get(self.base_openalex, params=params, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                results = r.json().get("results",[])
                return [{"title":w.get("title",""),"doi":w.get("doi",""),"source":"OpenAlex"} for w in results[:limit]]
        except: pass
        return []

    def search_crossref(self, query, limit=5):
        try:
            params = {"query":query,"rows":limit}
            r = requests.get(self.base_crossref, params=params, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                items = r.json().get("message",{}).get("items",[])
                return [{"title":item.get("title",[""])[0] if item.get("title") else "","DOI":item.get("DOI",""),"source":"Crossref"} for item in items[:limit]]
        except: pass
        return []

    def search_semantic(self, query, limit=5):
        try:
            params = {"query":query,"limit":limit,"fields":"title,abstract,url"}
            r = requests.get(self.base_semantic, params=params, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                data = r.json().get("data",[])
                return [{"title":p.get("title",""),"abstract":p.get("abstract",""),"url":p.get("url",""),"source":"Semantic Scholar"} for p in data[:limit]]
        except: pass
        return []

    def search_pubmed(self, query, limit=5):
        try:
            params = {"db":"pubmed","term":query,"retmax":limit,"retmode":"json"}
            r = requests.get(self.base_pubmed, params=params, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                ids = r.json().get("esearchresult",{}).get("idlist",[])
                return ids
        except: pass
        return []

    def search_wikidata(self, query, limit=5):
        try:
            params = {"action":"wbsearchentities","search":query,"language":"en","limit":limit,"format":"json"}
            r = requests.get(self.base_wikidata, params=params, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                results = r.json().get("search",[])
                return [{"id":res["id"],"label":res.get("label",""),"description":res.get("description",""),"source":"Wikidata"} for res in results[:limit]]
        except: pass
        return []

    def search_github(self, query, limit=5):
        try:
            params = {"q":query,"per_page":limit}
            r = requests.get(self.base_github, params=params, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                items = r.json().get("items",[])
                return [{"name":item.get("full_name",""),"description":item.get("description",""),"url":item.get("html_url",""),"source":"GitHub"} for item in items[:limit]]
        except: pass
        return []

    def deep_search(self, query):
        return {
            "wikipedia": self.search_wikipedia(query),
            "duckduckgo": self.search_duckduckgo(query),
            "arxiv": self.search_arxiv(query),
            "openalex": self.search_openalex(query),
            "crossref": self.search_crossref(query),
            "semantic_scholar": self.search_semantic(query),
            "pubmed_ids": self.search_pubmed(query),
            "wikidata": self.search_wikidata(query),
            "github": self.search_github(query)
        }

# ============================================
# STREAMLIT PAGE
# ============================================
st.set_page_config(page_title="Deep Search & Learn", page_icon="🔍", layout="wide")

st.title("🔍 Deep Search & Learn")
st.markdown("Search across 9+ sources and automatically store the knowledge in CoreKnow's permanent memory.")

query = st.text_input("Enter a topic to search", placeholder="e.g., quantum mechanics")

if st.button("Search & Learn", type="primary"):
    if not query.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner(f"Deep searching '{query}'..."):
            engine = DeepSearchEngine()
            results = engine.deep_search(query)

        st.subheader(f"📊 Results for '{query}'")

        total_items = sum(len(v) for v in results.values() if isinstance(v, list))
        st.info(f"Found {total_items} items across {len(results)} sources.")

        with st.expander(f"📚 Wikipedia ({len(results['wikipedia'])} results)", expanded=False):
            for r in results['wikipedia']:
                st.markdown(f"**{r['title']}**  
{r['snippet']}")

        with st.expander(f"🌐 DuckDuckGo ({len(results['duckduckgo'])} results)", expanded=False):
            for r in results['duckduckgo']:
                st.markdown(f"**{r['title']}**  
{r.get('url','')}")

        with st.expander(f"📄 ArXiv ({len(results['arxiv'])} results)", expanded=False):
            for r in results['arxiv']:
                st.markdown(f"**{r['title']}**  
{r['summary'][:150]}...  
[Link]({r['link']})")

        with st.expander(f"🎓 OpenAlex ({len(results['openalex'])} results)", expanded=False):
            for r in results['openalex']:
                st.markdown(f"**{r['title']}**  
DOI: {r['doi']}")

        with st.expander(f"🔗 Crossref ({len(results['crossref'])} results)", expanded=False):
            for r in results['crossref']:
                st.markdown(f"**{r['title']}**  
DOI: {r['DOI']}")

        with st.expander(f"🧠 Semantic Scholar ({len(results['semantic_scholar'])} results)", expanded=False):
            for r in results['semantic_scholar']:
                st.markdown(f"**{r['title']}**  
{r.get('abstract','')[:150]}...  
[Link]({r.get('url','')})")

        with st.expander(f"🩺 PubMed (IDs: {len(results['pubmed_ids'])} results)", expanded=False):
            if results['pubmed_ids']:
                st.write(", ".join(results['pubmed_ids']))
            else:
                st.write("No results")

        with st.expander(f"🌐 Wikidata ({len(results['wikidata'])} results)", expanded=False):
            for r in results['wikidata']:
                st.markdown(f"**{r['label']}** ({r['id']})  
{r['description']}")

        with st.expander(f"💻 GitHub ({len(results['github'])} results)", expanded=False):
            for r in results['github']:
                st.markdown(f"**{r['name']}**  
{r['description']}  
[Link]({r['url']})")

        st.markdown("---")
        st.subheader("💾 Storing to CoreKnow's memory...")
        try:
            combined_text = f"Deep search results for '{query}'

"
            for source, items in results.items():
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            combined_text += str(item.get('title','')) + " "
                            combined_text += str(item.get('snippet', item.get('summary', item.get('description', item.get('abstract',''))))) + "
"
                else:
                    combined_text += str(items) + "
"

            vs = VectorStorage()
            doc_id = vs.store_document(f"deep_search_{query}", "search", combined_text)
            st.success(f"✅ Knowledge stored permanently with document ID: {doc_id}")
        except Exception as e:
            st.error(f"Failed to store: {e}")

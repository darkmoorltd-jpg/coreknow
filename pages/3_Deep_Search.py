
import streamlit as st
import requests
import json
from typing import List, Dict
from bs4 import BeautifulSoup
import feedparser
import re
from sentence_transformers import SentenceTransformer
from supabase import create_client

# Supabase
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["service_key"]

# Vector storage
class VectorStorage:
    def __init__(self):
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_text(self, text):
        return self.model.encode(text).astype("float32").tolist()

    def chunk_text(self, content, chunk_size=500):
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

    def store_document(self, name, format, content):
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

# Helper to clean HTML from Wikipedia snippets
def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ")

# Deep search engine
class DeepSearchEngine:
    def __init__(self):
        self.ua = "CoreKnow/1.0 (Educational AI)"
        self.wikipedia = "https://en.wikipedia.org/w/api.php"
        self.arxiv = "http://export.arxiv.org/api/query"
        self.openalex = "https://api.openalex.org/works"
        self.crossref = "https://api.crossref.org/works"
        self.semantic = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.pubmed = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.wikidata = "https://www.wikidata.org/w/api.php"
        self.github = "https://api.github.com/search/repositories"

    def search_wikipedia(self, query, limit=5):
        try:
            params = {"action":"query","list":"search","srsearch":query,"srlimit":limit,"format":"json"}
            r = requests.get(self.wikipedia, params=params, headers={"User-Agent":self.ua}, timeout=15)
            if r.status_code == 200:
                results = r.json().get("query",{}).get("search",[])
                return [{"title":x["title"],"snippet":clean_html(x.get("snippet","")),"source":"Wikipedia"} for x in results]
        except:
            pass
        return []

    def search_duckduckgo(self, query, limit=5):
        try:
            url = "https://html.duckduckgo.com/html/"
            r = requests.post(url, data={"q":query}, headers={"User-Agent":self.ua}, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                results = []
                for link in soup.find_all("a", class_="result__a")[:limit]:
                    results.append({"title":link.get_text(),"url":link.get("href",""),"source":"DuckDuckGo"})
                return results
        except:
            pass
        return []

    def search_arxiv(self, query, limit=5):
        try:
            params = {"search_query":"all:"+query,"start":0,"max_results":limit}
            r = requests.get(self.arxiv, params=params, headers={"User-Agent":self.ua}, timeout=15)
            if r.status_code == 200:
                feed = feedparser.parse(r.text)
                results = []
                for e in feed.entries[:limit]:
                    # Extract summary and clean
                    summary = re.sub('<.*?>', '', e.summary) if e.summary else ""
                    results.append({
                        "title": e.title,
                        "summary": summary[:300],
                        "link": e.link,
                        "source":"ArXiv"
                    })
                return results
        except:
            pass
        return []

    def search_openalex(self, query, limit=5):
        try:
            params = {"search":query,"per-page":limit}
            r = requests.get(self.openalex, params=params, headers={"User-Agent":self.ua}, timeout=15)
            if r.status_code == 200:
                results = r.json().get("results",[])
                return [{"title":w.get("title",""),"doi":w.get("doi",""),"source":"OpenAlex"} for w in results[:limit]]
        except:
            pass
        return []

    def search_crossref(self, query, limit=5):
        try:
            params = {"query":query,"rows":limit}
            r = requests.get(self.crossref, params=params, headers={"User-Agent":self.ua}, timeout=15)
            if r.status_code == 200:
                items = r.json().get("message",{}).get("items",[])
                return [{"title":item.get("title",[""])[0] if item.get("title") else "","DOI":item.get("DOI",""),"source":"Crossref"} for item in items[:limit]]
        except:
            pass
        return []

    def search_semantic(self, query, limit=5):
        try:
            params = {"query":query,"limit":limit,"fields":"title,abstract,url"}
            r = requests.get(self.semantic, params=params, headers={"User-Agent":self.ua}, timeout=15)
            if r.status_code == 200:
                data = r.json().get("data",[])
                return [{"title":p.get("title",""),"abstract":p.get("abstract","")[:300],"url":p.get("url",""),"source":"Semantic Scholar"} for p in data[:limit]]
        except:
            pass
        return []

    def search_pubmed(self, query, limit=5):
        try:
            params = {"db":"pubmed","term":query,"retmax":limit,"retmode":"json"}
            r = requests.get(self.pubmed, params=params, headers={"User-Agent":self.ua}, timeout=15)
            if r.status_code == 200:
                ids = r.json().get("esearchresult",{}).get("idlist",[])
                return ids
        except:
            pass
        return []

    def search_wikidata(self, query, limit=5):
        try:
            params = {"action":"wbsearchentities","search":query,"language":"en","limit":limit,"format":"json"}
            r = requests.get(self.wikidata, params=params, headers={"User-Agent":self.ua}, timeout=15)
            if r.status_code == 200:
                results = r.json().get("search",[])
                return [{"id":x["id"],"label":x.get("label",""),"description":x.get("description",""),"source":"Wikidata"} for x in results[:limit]]
        except:
            pass
        return []

    def search_github(self, query, limit=5):
        try:
            params = {"q":query,"per_page":limit}
            r = requests.get(self.github, params=params, headers={"User-Agent":self.ua}, timeout=15)
            if r.status_code == 200:
                items = r.json().get("items",[])
                return [{"name":item.get("full_name",""),"description":item.get("description",""),"url":item.get("html_url",""),"source":"GitHub"} for item in items[:limit]]
        except:
            pass
        return []

    def fetch_wikipedia_extract(self, title):
        """Fetch full plain text extract for a Wikipedia title."""
        try:
            params = {
                "action":"query",
                "prop":"extracts",
                "explaintext":True,
                "titles":title,
                "format":"json"
            }
            r = requests.get(self.wikipedia, params=params, headers={"User-Agent":self.ua}, timeout=15)
            if r.status_code == 200:
                pages = r.json().get("query",{}).get("pages",{})
                for pid in pages:
                    return pages[pid].get("extract","")
        except:
            pass
        return ""

    def deep_search(self, query):
        """Return search results from all sources."""
        wiki_results = self.search_wikipedia(query)
        arxiv_results = self.search_arxiv(query)
        return {
            "wikipedia": wiki_results,
            "duckduckgo": self.search_duckduckgo(query),
            "arxiv": arxiv_results,
            "openalex": self.search_openalex(query),
            "crossref": self.search_crossref(query),
            "semantic_scholar": self.search_semantic(query),
            "pubmed_ids": self.search_pubmed(query),
            "wikidata": self.search_wikidata(query),
            "github": self.search_github(query),
            "wikipedia_extracts": [self.fetch_wikipedia_extract(w["title"]) for w in wiki_results[:3] if w.get("title")]
        }

# Streamlit page
st.set_page_config(page_title="Deep Search & Learn", page_icon="🔍", layout="wide")

st.title("🔍 Deep Search & Learn")
st.markdown("Search across 9+ sources, read full content from Wikipedia, and automatically store everything permanently.")

query = st.text_input("Enter a topic to search", placeholder="e.g., quantum mechanics")

if st.button("Search & Learn", type="primary"):
    if not query.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Deep searching '{}'...".format(query)):
            engine = DeepSearchEngine()
            results = engine.deep_search(query)

        # Display results cleanly
        st.subheader("Results for '{}'".format(query))

        # Wikipedia
        if results["wikipedia"]:
            with st.expander("📚 Wikipedia ({} results)".format(len(results["wikipedia"])), expanded=True):
                for r in results["wikipedia"]:
                    st.markdown("**{}**".format(r["title"]))
                    st.caption(r["snippet"])
                    st.markdown("---")
        else:
            st.info("No Wikipedia results.")

        # DuckDuckGo
        if results["duckduckgo"]:
            with st.expander("🌐 DuckDuckGo ({} results)".format(len(results["duckduckgo"]))):
                for r in results["duckduckgo"]:
                    st.markdown("**{}**".format(r["title"]))
                    st.write("{}".format(r.get("url","")))
                    st.markdown("---")

        # ArXiv
        if results["arxiv"]:
            with st.expander("📄 ArXiv ({} results)".format(len(results["arxiv"]))):
                for r in results["arxiv"]:
                    st.markdown("**{}**".format(r["title"]))
                    st.caption(r["summary"])
                    st.write("[Link]({})".format(r["link"]))
                    st.markdown("---")

        # OpenAlex
        if results["openalex"]:
            with st.expander("🎓 OpenAlex ({} results)".format(len(results["openalex"]))):
                for r in results["openalex"]:
                    st.markdown("**{}**".format(r["title"]))
                    st.caption("DOI: {}".format(r["doi"]))
                    st.markdown("---")

        # Crossref
        if results["crossref"]:
            with st.expander("🔗 Crossref ({} results)".format(len(results["crossref"]))):
                for r in results["crossref"]:
                    st.markdown("**{}**".format(r["title"]))
                    st.caption("DOI: {}".format(r["DOI"]))
                    st.markdown("---")

        # Semantic Scholar
        if results["semantic_scholar"]:
            with st.expander("🧠 Semantic Scholar ({} results)".format(len(results["semantic_scholar"]))):
                for r in results["semantic_scholar"]:
                    st.markdown("**{}**".format(r["title"]))
                    st.caption(r["abstract"])
                    st.write("[Link]({})".format(r["url"]))
                    st.markdown("---")

        # PubMed IDs
        if results["pubmed_ids"]:
            with st.expander("🩺 PubMed ({} IDs)".format(len(results["pubmed_ids"]))):
                st.write(", ".join(results["pubmed_ids"]))

        # Wikidata
        if results["wikidata"]:
            with st.expander("🌐 Wikidata ({} results)".format(len(results["wikidata"]))):
                for r in results["wikidata"]:
                    st.markdown("**{}** ({})".format(r["label"], r["id"]))
                    st.caption(r["description"])
                    st.markdown("---")

        # GitHub
        if results["github"]:
            with st.expander("💻 GitHub ({} results)".format(len(results["github"]))):
                for r in results["github"]:
                    st.markdown("**{}**".format(r["name"]))
                    st.caption(r["description"])
                    st.write("[Link]({})".format(r["url"]))
                    st.markdown("---")

        # Store everything
        st.markdown("---")
        st.subheader("💾 Storing to CoreKnow's memory...")
        try:
            vs = VectorStorage()
            # Store cleaned search results as one document
            combined_text = "Deep search results for '{}'\n\n".format(query)
            for source, items in results.items():
                if source == "wikipedia_extracts":
                    continue  # already storing extracts separately below
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            combined_text += str(item.get('title') or item.get('label') or item.get('name','')) + " "
                            combined_text += str(item.get('snippet') or item.get('summary') or item.get('abstract') or item.get('description','')) + "\n"
                        else:
                            combined_text += str(item) + "\n"
                else:
                    combined_text += str(items) + "\n"
            doc_id = vs.store_document("deep_search_{}".format(query), "search", combined_text)
            # Store each Wikipedia full extract as separate documents
            for i, extract in enumerate(results["wikipedia_extracts"]):
                if extract:
                    vs.store_document("wiki_extract_{}_{}".format(query, i), "wikipedia", extract)
            st.success("✅ Knowledge stored permanently with document ID: {}".format(doc_id))
        except Exception as e:
            st.error("Failed to store: {}".format(e))


import streamlit as st
import requests
import json
from typing import List, Dict
from bs4 import BeautifulSoup
import feedparser
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
                return [{"title":x["title"],"snippet":x.get("snippet",""),"source":"Wikipedia"} for x in results]
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
                return [{"title":e.title,"summary":e.summary,"link":e.link,"source":"ArXiv"} for e in feed.entries[:limit]]
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
                return [{"title":p.get("title",""),"abstract":p.get("abstract",""),"url":p.get("url",""),"source":"Semantic Scholar"} for p in data[:limit]]
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

# Streamlit page
st.set_page_config(page_title="Deep Search & Learn", page_icon="🔍", layout="wide")

st.title("🔍 Deep Search & Learn")
st.markdown("Search across 9+ sources and automatically store the knowledge in CoreKnow's permanent memory.")

query = st.text_input("Enter a topic to search", placeholder="e.g., quantum mechanics")

if st.button("Search & Learn", type="primary"):
    if not query.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Deep searching '{}'...".format(query)):
            engine = DeepSearchEngine()
            results = engine.deep_search(query)

        st.subheader("Results for '{}'".format(query))
        total_items = sum(len(v) for v in results.values() if isinstance(v, list))
        st.info("Found {} items across {} sources.".format(total_items, len(results)))

        # Display each source in an expander
        for source, items in results.items():
            if isinstance(items, list) and items:
                with st.expander("{} ({} results)".format(source.replace('_',' ').title(), len(items))):
                    for item in items:
                        if isinstance(item, dict):
                            title = item.get('title') or item.get('label') or item.get('name','')
                            snippet = item.get('snippet') or item.get('summary') or item.get('abstract') or item.get('description','')
                            link = item.get('url') or item.get('link','')
                            doi = item.get('doi') or item.get('DOI','')
                            line = "**{}**".format(title)
                            if snippet:
                                line += "\n" + snippet[:200]
                            if link:
                                line += "\n[Link]({})".format(link)
                            if doi:
                                line += "\nDOI: {}".format(doi)
                            st.markdown(line)
                        else:
                            st.write(str(item))
            elif source == 'pubmed_ids' and isinstance(items, list):
                with st.expander("PubMed IDs ({})".format(len(items))):
                    st.write(", ".join(items))

        # Store aggregated content
        st.markdown("---")
        st.subheader("💾 Storing to CoreKnow's memory...")
        try:
            combined_text = "Deep search results for '{}'\n\n".format(query)
            for source, items in results.items():
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            combined_text += str(item.get('title','')) + " "
                            combined_text += str(item.get('snippet', item.get('summary', item.get('description', item.get('abstract',''))))) + "\n"
                        else:
                            combined_text += str(item) + "\n"
                else:
                    combined_text += str(items) + "\n"

            vs = VectorStorage()
            doc_id = vs.store_document("deep_search_{}".format(query), "search", combined_text)
            st.success("✅ Knowledge stored permanently with document ID: {}".format(doc_id))
        except Exception as e:
            st.error("Failed to store: {}".format(e))

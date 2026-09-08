
import os
import re
import time
import requests
import feedparser
import json
from typing import List, Dict, Optional
from supabase import create_client
import io

class DeepSearch:
    """Search multiple sources, extract PDF text, formulas, and store in Supabase."""
    
    def __init__(self):
        self.user_agent = "CoreKnow/2.0 (Educational AI)"
        self.base_wikipedia = "https://en.wikipedia.org/w/api.php"
        self.base_arxiv = "http://export.arxiv.org/api/query"
        self.base_crossref = "https://api.crossref.org/works"
        self.base_openalex = "https://api.openalex.org/works"
        self.supabase = None
        # Try to get Supabase from Streamlit secrets, else use environment
        try:
            import streamlit as st
            url = st.secrets["supabase"]["url"]
            service_key = st.secrets["supabase"]["service_key"]
            self.supabase = create_client(url, service_key)
        except:
            pass
    
    def search_wikipedia(self, query, limit=3):
        try:
            params = {"action":"query","list":"search","srsearch":query,"srlimit":limit,"format":"json"}
            r = requests.get(self.base_wikipedia, params=params, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                search = r.json().get("query",{}).get("search",[])
                if search:
                    pageid = search[0].get("pageid")
                    if pageid:
                        params2 = {"action":"query","prop":"extracts","explaintext":True,"pageids":pageid,"format":"json"}
                        r2 = requests.get(self.base_wikipedia, params=params2, headers={"User-Agent":self.user_agent}, timeout=15)
                        if r2.status_code==200:
                            pages = r2.json().get("query",{}).get("pages",{})
                            return pages.get(str(pageid),{}).get("extract","")
        except:
            pass
        return ""
    
    def search_arxiv(self, query, limit=2):
        results = []
        try:
            params = {"search_query":f"all:{query}","start":0,"max_results":limit}
            r = requests.get(self.base_arxiv, params=params, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                feed = feedparser.parse(r.text)
                for e in feed.entries[:limit]:
                    pdf_url = e.link.replace('/abs/','/pdf/')
                    results.append({"title": e.title, "pdf": pdf_url, "summary": e.summary})
        except:
            pass
        return results
    
    def search_crossref(self, query, limit=2):
        results = []
        try:
            params = {"query":query,"rows":limit}
            r = requests.get(self.base_crossref, params=params, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                items = r.json().get("message",{}).get("items",[])
                for item in items[:limit]:
                    results.append({"title": item.get("title",[""])[0] if item.get("title") else "", "doi": item.get("DOI","")})
        except:
            pass
        return results
    
    def search_openalex(self, query, limit=2):
        results = []
        try:
            params = {"search":query,"per-page":limit}
            r = requests.get(self.base_openalex, params=params, headers={"User-Agent":self.user_agent}, timeout=15)
            if r.status_code==200:
                works = r.json().get("results",[])
                for w in works[:limit]:
                    results.append({"title": w.get("title",""), "doi": w.get("doi","")})
        except:
            pass
        return results
    
    def download_pdf_text(self, url, max_chars=5000):
        try:
            r = requests.get(url, headers={"User-Agent":self.user_agent}, timeout=20)
            if r.status_code==200:
                try:
                    import pdfplumber
                    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
                        text = " ".join(page.extract_text() or "" for page in pdf.pages)
                        return text[:max_chars]
                except:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(io.BytesIO(r.content))
                    text = " ".join(page.extract_text() or "" for page in reader.pages)
                    return text[:max_chars]
        except:
            pass
        return None
    
    def extract_formulas(self, text):
        formulas = set()
        patterns = [
            r'\$[^$]+\$',
            r'[A-Za-z]+\s*=\s*[A-Za-z0-9\^\+\-\*\/\(\)\.]+',
        ]
        for p in patterns:
            found = re.findall(p, text, re.DOTALL)
            for f in found:
                formulas.add(f.strip())
        return list(formulas)
    
    def learn_topic(self, topic, limit=2):
        """Deep search a topic, extract info, and store in Supabase."""
        wiki_text = self.search_wikipedia(topic)
        arxiv_results = self.search_arxiv(topic, limit)
        crossref_results = self.search_crossref(topic, limit)
        openalex_results = self.search_openalex(topic, limit)
        
        # Download and extract text from first ArXiv PDF
        pdf_text = None
        pdf_url = None
        if arxiv_results and arxiv_results[0].get("pdf"):
            pdf_url = arxiv_results[0]["pdf"]
            pdf_text = self.download_pdf_text(pdf_url)
        
        all_text = wiki_text + " " + (pdf_text or "") + " " + " ".join([r.get("summary","") for r in arxiv_results])
        formulas = self.extract_formulas(all_text)
        
        record = {
            "topic": topic,
            "source": "wikipedia,arxiv,crossref,openalex",
            "title": arxiv_results[0].get("title", topic) if arxiv_results else topic,
            "authors": None,
            "summary": wiki_text[:500] if wiki_text else None,
            "pdf_url": pdf_url,
            "full_text": pdf_text,
            "formulas": formulas[:10],  # first 10 formulas
        }
        
        if self.supabase:
            try:
                self.supabase.table("coreknow_knowledge").insert(record).execute()
            except Exception as e:
                print(f"Supabase insert error: {e}")
                # fallback to returning record if table missing
        return record

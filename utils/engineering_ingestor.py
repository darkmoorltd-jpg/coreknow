
import os
import io
import re
import json
import base64
import requests
import tempfile
from bs4 import BeautifulSoup
from supabase import create_client
import streamlit as st

class EngineeringIngestor:
    """Ingest engineering documents (PDFs, textbooks) and extract components."""

    def __init__(self):
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["service_key"]
            self.supabase = create_client(url, key)
        except:
            self.supabase = None

    def extract_from_pdf(self, file_bytes: bytes) -> dict:
        result = {"text": "", "tables": [], "images": [], "formulas": [], "graphs_data": []}

        # Text + tables via pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                full_text = []
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    full_text.append(f"[Page {page_num}]\n{text}")
                    for table in page.extract_tables():
                        if table:
                            result["tables"].append({"page": page_num, "rows": table, "source": "pdfplumber"})
                result["text"] = "\n".join(full_text)
        except Exception as e:
            print(f"PDF text extraction failed: {e}")

        # Images via PyMuPDF
        try:
            import fitz
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num in range(len(doc)):
                page = doc[page_num]
                for img_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    b64 = base64.b64encode(base_image["image"]).decode()
                    result["images"].append({
                        "page": page_num + 1,
                        "index": img_index,
                        "data": b64,
                    })
        except:
            pass

        # Formulas via regex (engineering equations, symbols)
        formulas = set()
        patterns = [
            r'\$[^$]+\$',                                       # LaTeX
            r'[A-Za-z]+\s*=\s*[A-Za-z0-9\^\+\-\*\/\(\)\.]+',  # equations
            r'\b[A-Z][a-z]?\d*[A-Z][a-z]?\d*\b',               # formulas
            r'\b(Greek:.*?)\b',                                # greek symbols
        ]
        for p in patterns:
            found = re.findall(p, result["text"], re.DOTALL)
            for f in found:
                formulas.add(f.strip())
        result["formulas"] = list(formulas)[:100]

        return result

    def process_and_store(self, file_bytes, file_name, field="general"):
        result = self.extract_from_pdf(file_bytes)
        doc_id = None
        try:
            doc_res = self.supabase.table("engineering_documents").insert({
                "name": file_name,
                "format": os.path.splitext(file_name)[1].lower(),
                "field": field,
                "content": result["text"][:5000],
            }).execute()
            doc_id = doc_res.data[0]["id"]
        except Exception as e:
            return {"status": "failed", "error": str(e)}

        if doc_id:
            def store(comp_type, content):
                try:
                    self.supabase.table("engineering_document_components").insert({
                        "document_id": doc_id,
                        "component_type": comp_type,
                        "content": json.dumps(content),
                    }).execute()
                except:
                    pass

            if result["text"]:
                store("text", {"content": result["text"]})
            for table in result["tables"]:
                store("table", table)
            for img in result["images"]:
                store("image", img)
            if result["formulas"]:
                store("formulas", {"formulas": result["formulas"]})

        return {"status": "success", "doc_id": doc_id}

    def deep_search_engineering(self, query, field="general", max_results=5):
        """Search arXiv for engineering papers."""
        try:
            import feedparser
            base = "http://export.arxiv.org/api/query"
            params = {"search_query": f"all:{query}", "start": 0, "max_results": max_results}
            r = requests.get(base, params=params, timeout=30)
            if r.status_code == 200:
                feed = feedparser.parse(r.text)
                count = 0
                for entry in feed.entries:
                    # Store title + summary + link as a document
                    text = f"{entry.title}\n\n{entry.summary}\n\nLink: {entry.link}"
                    try:
                        doc_res = self.supabase.table("engineering_documents").insert({
                            "name": f"arxiv_{entry.id.split('/')[-1]}.xml",
                            "format": ".xml",
                            "field": field,
                            "content": text[:5000],
                        }).execute()
                        doc_id = doc_res.data[0]["id"]
                        self.supabase.table("engineering_document_components").insert({
                            "document_id": doc_id,
                            "component_type": "text",
                            "content": json.dumps({"content": text}),
                        }).execute()
                        count += 1
                    except:
                        pass
                return {"status": "success", "count": count}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
        return {"status": "success", "count": 0}

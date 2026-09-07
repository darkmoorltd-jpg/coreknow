
import PyPDF2
import io
import re
import os
import json
import streamlit as st

class PDFEater:
    def __init__(self):
        self.documents = []
        self.chunks = []
        self.total_pages = 0
        self.total_chunks = 0
        
        # Supabase client for permanent storage
        try:
            from supabase import create_client
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["service_key"]
            self.supabase = create_client(url, key)
            self.has_supabase = True
        except:
            self.has_supabase = False
            self.supabase = None
    
    def extract_text(self, file_bytes):
        """Extract all text from PDF."""
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            self.total_pages += len(pdf_reader.pages)
            
            for i, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += f"[Page {i+1}]\n{page_text}\n\n"
                except:
                    pass
            return text
        except Exception as e:
            return f"Error: {e}"
    
    def chunk_text(self, text, chunk_size=500):
        """Split text into chunks."""
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        self.total_chunks += len(chunks)
        return chunks
    
    def save_to_supabase(self, doc):
        """Save document to Supabase for permanent storage."""
        if not self.has_supabase:
            return False
        
        try:
            # Save document metadata
            self.supabase.table("coreknow_documents").insert({
                "name": doc["name"],
                "num_pages": doc["num_pages"],
                "num_chunks": doc["num_chunks"],
            }).execute()
            
            # Save chunks
            for i, chunk in enumerate(doc["chunks"]):
                self.supabase.table("coreknow_chunks").insert({
                    "doc_name": doc["name"],
                    "chunk_index": i,
                    "content": chunk[:1000],  # Limit size
                }).execute()
            
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False
    
    def load_from_supabase(self):
        """Load all documents from Supabase."""
        if not self.has_supabase:
            return False
        
        try:
            # Load documents
            docs_res = self.supabase.table("coreknow_documents").select("*").execute()
            if docs_res.data:
                for doc in docs_res.data:
                    self.documents.append({
                        "name": doc["name"],
                        "num_pages": doc["num_pages"],
                        "num_chunks": doc["num_chunks"],
                        "text": "",
                        "chunks": [],
                    })
            
            # Load chunks
            chunks_res = self.supabase.table("coreknow_chunks").select("*").execute()
            if chunks_res.data:
                for chunk in chunks_res.data:
                    self.chunks.append(chunk["content"])
            
            self.total_chunks = len(self.chunks)
            return True
        except Exception as e:
            print(f"Load failed: {e}")
            return False
    
    def eat(self, file_bytes, file_name):
        """Ingest PDF and save permanently."""
        print(f"Eating {file_name}...")
        
        text = self.extract_text(file_bytes)
        chunks = self.chunk_text(text)
        
        doc = {
            "name": file_name,
            "text": text,
            "chunks": chunks,
            "num_pages": len(PyPDF2.PdfReader(io.BytesIO(file_bytes)).pages),
            "num_chunks": len(chunks),
        }
        self.documents.append(doc)
        self.chunks.extend(chunks)
        
        # Save to Supabase for permanence
        self.save_to_supabase(doc)
        
        return doc
    
    def search(self, query, top_k=3):
        """Search all chunks."""
        results = []
        query_words = set(query.lower().split())
        
        for i, chunk in enumerate(self.chunks):
            chunk_lower = chunk.lower()
            score = sum(chunk_lower.count(word) for word in query_words)
            if score > 0:
                results.append({"chunk": chunk, "score": score, "index": i})
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def get_context(self, query, top_k=5):
        """Get relevant context."""
        results = self.search(query, top_k)
        return "\n\n".join([r["chunk"][:500] for r in results])
    
    def get_stats(self):
        return {
            "documents": len(self.documents),
            "chunks": self.total_chunks,
            "pages": self.total_pages,
        }

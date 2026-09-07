
import PyPDF2
import io
import os
import json
import re
from supabase import create_client
import streamlit as st

class TextbookMaster:
    def __init__(self):
        self.documents = []
        self.chunks = []
        self.total_pages = 0
        self.total_chunks = 0
        self.loaded = False
        
        # Supabase for permanent storage
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["service_key"]
            self.supabase = create_client(url, key)
            self.has_supabase = True
        except:
            self.has_supabase = False
            self.supabase = None
    
    def extract_text_100(self, file_bytes):
        """Extract 100% of text from every page."""
        full_text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            num_pages = len(pdf_reader.pages)
            self.total_pages += num_pages
            
            for i, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += f"\n\n=== PAGE {i+1} ===\n\n{page_text}"
                except:
                    full_text += f"\n\n=== PAGE {i+1} ===\n[Text extraction failed]"
            
            return full_text, num_pages
        except Exception as e:
            return f"Error: {e}", 0
    
    def chunk_text(self, text, chunk_size=800):
        """Split text into chunks."""
        pages = text.split("=== PAGE")
        chunks = []
        
        for page_content in pages:
            if not page_content.strip():
                continue
            
            page_match = re.match(r'\s*(\d+)\s*===', page_content)
            page_num = int(page_match.group(1)) if page_match else 0
            
            paragraphs = page_content.split("\n\n")
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk) + len(para) < chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append({
                            "page": page_num,
                            "text": current_chunk.strip(),
                            "start": len(chunks),
                        })
                    current_chunk = para + "\n\n"
            
            if current_chunk:
                chunks.append({
                    "page": page_num,
                    "text": current_chunk.strip(),
                    "start": len(chunks),
                })
        
        self.total_chunks += len(chunks)
        return chunks
    
    def eat(self, file_bytes, file_name):
        """Eat textbook — extract 100% text, chunk, store."""
        print(f"📖 Eating {file_name}...")
        
        full_text, num_pages = self.extract_text_100(file_bytes)
        chunks = self.chunk_text(full_text)
        
        doc = {
            "name": file_name,
            "full_text": full_text,
            "num_pages": num_pages,
            "num_chunks": len(chunks),
            "chunks": chunks,
        }
        
        self.documents.append(doc)
        
        if self.has_supabase:
            self.save_to_supabase(doc)
        
        print(f"✅ Ate {file_name}: {num_pages} pages, {len(chunks)} chunks")
        return doc
    
    def save_to_supabase(self, doc):
        """Save document and chunks permanently."""
        try:
            doc_res = self.supabase.table("coreknow_documents").insert({
                "name": doc["name"],
                "num_pages": doc["num_pages"],
                "num_chunks": doc["num_chunks"],
            }).execute()
            
            for chunk in doc["chunks"]:
                self.supabase.table("coreknow_chunks").insert({
                    "doc_name": doc["name"],
                    "page": chunk["page"],
                    "chunk_index": chunk["start"],
                    "content": chunk["text"][:2000],
                }).execute()
            
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def load_from_supabase(self):
        """Load ALL previously eaten textbooks from Supabase."""
        if not self.has_supabase or self.loaded:
            return False
        
        try:
            print("📂 Loading previously eaten textbooks...")
            
            # Load documents
            docs_res = self.supabase.table("coreknow_documents").select("*").execute()
            if not docs_res.data:
                print("No previously saved textbooks.")
                return False
            
            for doc_data in docs_res.data:
                doc_name = doc_data["name"]
                num_pages = doc_data.get("num_pages", 0)
                num_chunks = doc_data.get("num_chunks", 0)
                
                # Load chunks for this document
                chunks_res = self.supabase.table("coreknow_chunks") \
                    .select("*") \
                    .eq("doc_name", doc_name) \
                    .order("chunk_index") \
                    .execute()
                
                chunks = []
                for chunk_data in chunks_res.data:
                    chunks.append({
                        "page": chunk_data.get("page", 0),
                        "text": chunk_data.get("content", ""),
                        "start": chunk_data.get("chunk_index", 0),
                    })
                
                # Reconstruct document
                doc = {
                    "name": doc_name,
                    "full_text": "\n\n".join([c["text"] for c in chunks]),
                    "num_pages": num_pages,
                    "num_chunks": len(chunks),
                    "chunks": chunks,
                }
                
                self.documents.append(doc)
                self.total_pages += num_pages
                self.total_chunks += len(chunks)
                
                print(f"  ✅ Loaded: {doc_name} ({num_pages} pages, {len(chunks)} chunks)")
            
            self.loaded = True
            print(f"✅ Loaded {len(self.documents)} textbooks from memory!")
            return True
            
        except Exception as e:
            print(f"Load error: {e}")
            return False
    
    def search(self, query, top_k=5):
        """Search all chunks for relevant text."""
        results = []
        query_words = set(query.lower().split())
        
        for doc in self.documents:
            for chunk in doc["chunks"]:
                text_lower = chunk["text"].lower()
                score = 0
                for word in query_words:
                    if word in text_lower:
                        score += text_lower.count(word)
                
                if score > 0:
                    results.append({
                        "chunk": chunk["text"],
                        "page": chunk["page"],
                        "doc": doc["name"],
                        "score": score,
                    })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def get_context(self, query, top_k=5):
        """Get relevant context for question."""
        results = self.search(query, top_k)
        if not results:
            return "No relevant content found."
        
        context = ""
        for r in results:
            context += f"[{r['doc']}, Page {r['page']}] {r['chunk'][:500]}\n\n"
        
        return context
    
    def get_stats(self):
        return {
            "documents": len(self.documents),
            "chunks": self.total_chunks,
            "pages": self.total_pages,
        }

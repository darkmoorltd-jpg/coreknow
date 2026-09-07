
import PyPDF2
import io
import re
import os

class PDFEater:
    def __init__(self):
        self.documents = []  # Store all ingested documents
        self.chunks = []     # Store text chunks
        self.total_pages = 0
        self.total_chunks = 0
    
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
        """Split text into chunks of ~500 characters."""
        # Split by paragraphs first
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
    
    def eat(self, file_bytes, file_name):
        """Ingest a PDF - extract, chunk, and store."""
        print(f"📖 Eating {file_name}...")
        
        # Extract text
        text = self.extract_text(file_bytes)
        
        # Chunk it
        chunks = self.chunk_text(text)
        
        # Store document
        doc = {
            "name": file_name,
            "text": text,
            "chunks": chunks,
            "num_pages": len(PyPDF2.PdfReader(io.BytesIO(file_bytes)).pages),
            "num_chunks": len(chunks),
        }
        self.documents.append(doc)
        self.chunks.extend(chunks)
        
        print(f"✅ Ate {file_name}: {doc['num_pages']} pages, {len(chunks)} chunks")
        return doc
    
    def search(self, query, top_k=3):
        """Search all chunks for relevant text."""
        results = []
        query_words = set(query.lower().split())
        
        for i, chunk in enumerate(self.chunks):
            chunk_lower = chunk.lower()
            score = 0
            for word in query_words:
                if word in chunk_lower:
                    score += chunk_lower.count(word)
            
            if score > 0:
                results.append({"chunk": chunk, "score": score, "index": i})
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def get_context(self, query, top_k=5):
        """Get relevant context for a question."""
        results = self.search(query, top_k)
        context = "\n\n".join([r["chunk"][:500] for r in results])
        return context
    
    def get_stats(self):
        return {
            "documents": len(self.documents),
            "chunks": self.total_chunks,
            "pages": self.total_pages,
        }

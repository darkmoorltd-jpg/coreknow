
import numpy as np
import faiss

class VectorStore:
    def __init__(self, dim=384):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []
    
    def add(self, embeddings, texts):
        """Add embeddings and associated texts."""
        if len(embeddings) == 0:
            return
        self.index.add(np.array(embeddings).astype('float32'))
        self.texts.extend(texts)
    
    def search(self, query_embedding, k=5):
        """Search for most similar texts."""
        if self.index.ntotal == 0:
            return []
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.texts):
                results.append({"text": self.texts[idx], "distance": float(distances[0][i])})
        return results
    
    def size(self):
        return self.index.ntotal

import faiss
import numpy as np
import os
import pickle
from rich.console import Console

console = Console()

class VectorStore:
    def __init__(self, dim=384, store_path="data"):
        self.dim = dim
        self.store_path = store_path
        self.index_file = os.path.join(store_path, "faiss.index")
        self.meta_file = os.path.join(store_path, "meta.pkl")
        
        self.texts = []
        self.index = faiss.IndexFlatL2(dim)
        self._load()

    def add(self, embeddings: np.ndarray, texts: list[str]):
        """Adds new embeddings and text chunks to the store."""
        self.index.add(embeddings)
        self.texts.extend(texts)
        self._save()
        console.print(f"[bold magenta]Vector Store updated:[/bold magenta] Total vectors: {len(self.texts)}")

    def search(self, embedding: np.ndarray, top_k: int) -> list[str]:
        """Searches the store for the top_k most relevant chunks."""
        if not self.texts:
            return []
            
        # Ensure embedding is 2D array for FAISS search
        embedding = embedding.reshape(1, -1)
        
        D, I = self.index.search(embedding, top_k)
        
        # I contains the indices of the nearest neighbors
        return [self.texts[i] for i in I[0] if i < len(self.texts)]

    def _save(self):
        """Persists the FAISS index and text metadata to local files."""
        os.makedirs(self.store_path, exist_ok=True)
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, "wb") as f:
            pickle.dump(self.texts, f)
        
    def _load(self):
        """Loads the index and metadata if they exist."""
        if os.path.exists(self.index_file) and os.path.exists(self.meta_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.meta_file, "rb") as f:
                self.texts = pickle.load(f)
            console.print(f"[bold green]Loaded FAISS Index[/bold green] with {len(self.texts)} chunks.")
        else:
            console.print("[bold yellow]No existing index found.[/bold yellow] Starting fresh.")
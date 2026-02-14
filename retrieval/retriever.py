from utils.chunking import embed
from memory.vector_store import VectorStore
from config import TOP_K

class Retriever:
    def __init__(self):
        self.store = VectorStore()

    def retrieve(self, query: str) -> list[str]:
        """Performs vector search based on the user query."""
        if not self.store.texts:
            return []
            
        q_emb = embed([query])[0]
        return self.store.search(q_emb, TOP_K)
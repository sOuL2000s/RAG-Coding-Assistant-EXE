# Static RAG Hyperparameters

# Embedding model (384 dimensions)
EMBED_MODEL = "all-MiniLM-L6-v2"

# RAG Hyperparameters
CHUNK_SIZE = 800      # Optimized for code analysis
CHUNK_OVERLAP = 150   # Overlap helps maintain context
TOP_K = 5             # Number of relevant chunks to retrieve
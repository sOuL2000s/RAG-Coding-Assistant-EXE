from sentence_transformers import SentenceTransformer
from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBED_MODEL
import numpy as np
import sys
import os
from pathlib import Path

# Load the embedding model globally once
# --- MODIFIED FOR LOCAL LOADING AND PYINSTALLER ---
def get_model_path():
    """Determines the correct model path based on local setup or PyInstaller environment."""
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller bundle: Model is bundled inside sys._MEIPASS
        base_path = Path(sys._MEIPASS)
        # The model is now bundled under 'models/' (matching the new --add-data target)
        return str(base_path / "models" / EMBED_MODEL) # <--- CHANGE HERE
    else:
        # Running normally, load from local 'models/' directory
        return str(Path("models") / EMBED_MODEL) # <--- CHANGE HERE

try:
    model = SentenceTransformer(get_model_path())
except Exception as e:
    print(f"Error loading embedding model: {e}")
    # Fallback/Error state
    model = None

# --------------------------------

def chunk_text(text: str, filename: str) -> list[str]:
    """Splits a large text block (code file) into contextual chunks."""
    
    # Simple recursive splitting based on token count
    # Note: For production code, ideally use language-aware (e.g., AST) splitting.
    
    chunks = []
    start = 0
    context_prefix = f"[FILE: {filename}] "
    
    while start < len(text):
        end = start + CHUNK_SIZE
        
        # Append the chunk, prepended with file context
        chunk_content = text[start:end]
        chunks.append(context_prefix + chunk_content)
        
        start += CHUNK_SIZE - CHUNK_OVERLAP
        
    return chunks

def embed(texts: list[str]) -> np.ndarray:
    """Generates embeddings for a list of texts."""
    if model is None:
        raise RuntimeError("Embedding model failed to load.")
    return model.encode(texts, convert_to_numpy=True)
import os
from tqdm import tqdm
from utils.chunking import chunk_text, embed
from memory.vector_store import VectorStore
from rich.console import Console

console = Console()

class CodeIndexer:
    def __init__(self):
        self.store = VectorStore()
        # Common code file extensions to index
        self.extensions = (".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".cs", ".go", ".html", ".css", ".md")

    def index_directory(self, path):
        if not os.path.isdir(path):
            console.print(f"[bold red]Error:[/bold red] Path '{path}' is not a valid directory.")
            return

        console.print(f"\n[bold blue]Starting indexing of:[/bold blue] {path}")
        all_chunks = []
        all_files = []

        # First pass: Gather all relevant files
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(self.extensions) and "venv" not in root and ".git" not in root:
                    all_files.append(os.path.join(root, file))
        
        if not all_files:
            console.print("[bold red]No code files found[/bold red] or they were filtered out.")
            return

        # Second pass: Process and chunk files with progress bar
        for file_path in tqdm(all_files, desc="Chunking and Indexing"):
            try:
                with open(file_path, "r", encoding="utf-8", errors='ignore') as f:
                    content = f.read()
                    
                    # We pass the relative filename to be included in the chunk context
                    relative_path = os.path.relpath(file_path, path)
                    chunks = chunk_text(content, relative_path)
                    all_chunks.extend(chunks)
            except Exception as e:
                console.print(f"[bold yellow]Skipping file[/bold yellow] {file_path} due to error: {e}")

        if all_chunks:
            # Batch embedding and adding to FAISS
            embeddings = embed(all_chunks)
            self.store.add(embeddings, all_chunks)
            console.print(f"\n[bold green]Indexing Complete![/bold green] Total chunks added: {len(all_chunks)}")
        else:
            console.print("[bold yellow]No chunks were generated.[/bold yellow]")
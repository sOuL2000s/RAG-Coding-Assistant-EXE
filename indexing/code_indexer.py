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

    def index_paths(self, paths: list[str]):
        """Indexes a list of paths, which can be directories or individual files."""
        if not paths:
            return

        console.print(f"\n[bold blue]Starting indexing process...[/bold blue] ({len(paths)} initial paths)")
        all_chunks = []
        all_files_to_index = []

        for path in paths:
            path = os.path.abspath(path) # Ensure absolute path consistency
            if os.path.isdir(path):
                # Recursively walk directories
                for root, _, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Check ignore patterns and extension
                        if file.endswith(self.extensions) and "venv" not in root and ".git" not in root:
                            all_files_to_index.append(file_path)
            elif os.path.isfile(path):
                # Add individual files directly, provided they match extensions
                if path.endswith(self.extensions):
                    all_files_to_index.append(path)
                else:
                    console.print(f"[bold yellow]Skipping file[/bold yellow] {path}: unsupported extension.")
            else:
                console.print(f"[bold red]Error:[/bold red] Path '{path}' is not a valid directory or file.")

        if not all_files_to_index:
            console.print("[bold red]No code files found[/bold red] or they were filtered out.")
            return

        # Second pass: Process and chunk files with progress bar
        # Determine the base path for relative path display
        base_path = os.path.commonpath(all_files_to_index) if len(all_files_to_index) > 1 else ""

        for file_path in tqdm(all_files_to_index, desc="Chunking and Indexing"):
            try:
                with open(file_path, "r", encoding="utf-8", errors='ignore') as f:
                    content = f.read()
                    
                    # Use relative path if a common base exists, otherwise use the full path
                    if base_path:
                         # Ensure the path is relative to the common root for cleaner context output
                         relative_path = os.path.relpath(file_path, base_path)
                    else:
                         relative_path = file_path # Single file/no common root

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
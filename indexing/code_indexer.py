import os
from tqdm import tqdm
from utils.chunking import chunk_text, embed
from memory.vector_store import VectorStore
from rich.console import Console

console = Console()

class CodeIndexer:
    def __init__(self):
        self.store = VectorStore()
        # EXPANDED: Supported file extensions for indexing
        self.supported_extensions = (
            # Code/Markup
            ".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".cs", ".go", ".html", ".css", ".md",
            ".rst", ".xml",
            # Text/Config/Data
            ".txt", ".log", ".csv", ".json", ".yaml", ".yml", ".ini", ".toml",
            ".gitignore", # Important configuration files
            ".spec", # PyInstaller spec files
        )
        # Common extensionless files that should be indexed
        self.extensionless_files = ("LICENSE", "README", "Dockerfile", "Vagrantfile", "Procfile")


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
                    # Robust Exclusion Check: Skip well-known build/system folders based on directory name
                    if any(segment.startswith(('.', 'venv', 'env', 'build', 'dist', 'data')) for segment in root.split(os.sep)):
                         continue

                    for file in files:
                        file_path = os.path.join(root, file)
                        file_name = os.path.basename(file_path)
                        
                        # Check if it matches supported extensions (case insensitive)
                        is_supported = file_name.lower().endswith(self.supported_extensions)
                        # Check for extensionless files
                        is_extensionless = file_name in self.extensionless_files and not os.path.splitext(file_name)[1]
                        
                        if is_supported or is_extensionless:
                            all_files_to_index.append(file_path)
                            
            elif os.path.isfile(path):
                # If a file is explicitly selected, we generally allow it, 
                # relying on the chunking process to handle the content.
                all_files_to_index.append(path) 
            else:
                console.print(f"[bold red]Error:[/bold red] Path '{path}' is not a valid directory or file.")

        if not all_files_to_index:
            console.print("[bold red]No files found[/bold red] or they were filtered out.")
            return

        # Second pass: Process and chunk files with progress bar
        # Determine the base path for relative path display
        base_path = os.path.commonpath(all_files_to_index) if len(all_files_to_index) > 1 else ""

        for file_path in tqdm(all_files_to_index, desc="Chunking and Indexing"):
            try:
                with open(file_path, "r", encoding="utf-8", errors='ignore') as f:
                    content = f.read()
                    
                    # Use relative path if a common base exists, otherwise use the full path
                    if base_path and base_path != os.path.dirname(file_path): 
                         relative_path = os.path.relpath(file_path, base_path)
                    else:
                         relative_path = file_path # Single file/no common root

                    chunks = chunk_text(content, relative_path)
                    all_chunks.extend(chunks)
            except Exception as e:
                # This often happens with binary files or files with odd permissions
                console.print(f"[bold yellow]Skipping file[/bold yellow] {file_path} due to error: {e}")

        if all_chunks:
            # Batch embedding and adding to FAISS
            embeddings = embed(all_chunks)
            self.store.add(embeddings, all_chunks)
            console.print(f"\n[bold green]Indexing Complete![/bold green] Total chunks added: {len(all_chunks)}")
        else:
            console.print("[bold yellow]No chunks were generated.[/bold yellow]")
import os

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Static, Label, Select
from textual.containers import Container, VerticalScroll
from textual.widget import Widget
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Markdown, ContentSwitcher

import asyncio
from config_manager import config_manager
from llm.gemini_client import GeminiClient
from retrieval.retriever import Retriever
from memory.chat_memory import ChatMemory
from indexing.code_indexer import CodeIndexer
from models import MODEL_OPTIONS, DEFAULT_MODEL

# --- Custom Widgets and Screens ---

class ChatBubble(Static):
    """A widget for displaying a single chat message."""
    
    def __init__(self, role: str, content: str, **kwargs):
        super().__init__(**kwargs)
        self.role = role
        self.content = content
        self.styles.width = "auto"
        self.styles.padding = (0, 2)
        
    def compose(self) -> ComposeResult:
        if self.role == "user":
            self.styles.content_align_horizontal = "right"
            self.styles.color = "yellow"
        else:
            self.styles.content_align_horizontal = "left"
            self.styles.color = "white"

        # Use the Textual Markdown widget for seamless rendering and copying
        yield Markdown(self.content, classes=f"{self.role}-bubble")
        
        # Optional: Add a copy button for better UX (requires more advanced Textual binding)
        # For simplicity, Markdown widget already allows selection and copy-paste in most terminals.


class ChatView(VerticalScroll):
    """The scrollable area for chat history."""
    pass

class SetupScreen(Container):
    """Screen for initial API key and model setup."""
    
    def compose(self) -> ComposeResult:
        yield Label("[bold red]API Key and Model Setup[/bold red]", classes="title")
        yield Input(placeholder="Enter Gemini API Key", id="key_input", classes="input")
        yield Button("Add Key", id="add_key_btn", variant="primary")
        yield Static("", id="key_list_status")
        yield Label("\n[bold]Current Model:[/bold]")
        yield Select(
            [(name, value) for name, value in MODEL_OPTIONS.items()],
            prompt="Select Model",
            value=config_manager.get_current_model(),
            id="model_select"
        )
        yield Button("Save & Start Chat", id="start_chat_btn", variant="success", disabled=True)

    def on_mount(self) -> None:
        """Called once the widget and its children are mounted and ready."""
        self.update_status()

    def update_status(self):
        """Refreshes the list of stored keys."""
        keys = config_manager.get_keys()
        status_widget = self.query_one("#key_list_status", Static)
        
        if keys:
            status_text = "[bold green]Stored Keys:[/bold green]\n"
            for i, key in enumerate(keys):
                status_text += f"  - Key {i+1} (ends in ...{key[-4:]})\n"
            self.query_one("#start_chat_btn", Button).disabled = False
        else:
            status_text = "[bold yellow]No API keys stored. Please add one to start.[/bold yellow]"
            self.query_one("#start_chat_btn", Button).disabled = True
            
        status_widget.update(status_text)
        
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add_key_btn":
            key_input = self.query_one("#key_input", Input)
            key = key_input.value.strip()
            if key and key.startswith("AIza"):
                config_manager.add_key(key)
                key_input.value = ""
                self.update_status()
            else:
                self.app.bell()

        elif event.button.id == "start_chat_btn":
            # Pass the signal to the main app to initialize and switch screen
            self.app.post_message(StartChat())

    def on_select_changed(self, event: Select.Changed):
        config_manager.set_current_model(event.value)

# --- Messages for Inter-widget Communication ---

class StartChat(Message):
    """Sent when setup is complete and chat should begin."""
    pass

class StatusUpdate(Message):
    """Sent to update the index/API status."""
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

# --- Main Application ---

class RAGCoderApp(App):
    CSS = """
    #chat_container {
        height: 100%;
    }
    #output_area {
        height: 90%;
        border: solid #333;
        padding: 1 2;
    }
    #input_area {
        height: 10%;
        padding: 0 1;
        align: left middle;
    }
    #command_input {
        width: 80%;
    }
    .user-bubble, .assistant-bubble {
        margin-bottom: 1;
        width: 100%;
    }
    .title {
        text-align: center;
        margin-bottom: 2;
    }
    .input {
        width: 100%;
        margin-bottom: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+i", "show_index_prompt", "Index Codebase"),
        ("ctrl+s", "show_setup", "Manage Keys/Model")
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_manager = config_manager
        self.gemini = None
        self.retriever = None
        self.memory = None
        self.indexer = CodeIndexer()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ContentSwitcher(initial="setup_screen", id="screen_switcher")
        
        # Initial Setup Screen
        yield SetupScreen(id="setup_screen")
        
        # Main Chat Screen (will be loaded dynamically after setup)
        with Container(id="chat_container", classes="full-screen"):
            yield Static("Status: Ready.", id="status_bar")
            yield ChatView(id="output_area")
            with Container(id="input_area"):
                yield Input(placeholder="Ask a coding question or enter command (Ctrl+I to Index)", id="command_input")
                yield Button("Send", id="send_btn", variant="primary")

    def on_mount(self):
        # Check if keys exist on mount; if so, skip setup screen
        if self.config_manager.get_keys():
            self.initialize_rag()
            self.query_one("#screen_switcher").current = "chat_container"
        else:
            self.query_one("#screen_switcher").current = "setup_screen"

    def initialize_rag(self):
        """Initializes the LLM, Retriever, and Memory components."""
        self.gemini = GeminiClient()
        self.retriever = Retriever()
        self.memory = ChatMemory()
        
        # Check if index exists
        if not self.indexer.store.texts:
            self.post_message(StatusUpdate("[bold yellow]Codebase index is empty. Use Ctrl+I to index your repository.[/bold yellow]"))
        else:
            self.post_message(StatusUpdate(f"[bold green]LLM and RAG Ready.[/bold green] Model: {self.gemini.model_name}. Chunks: {len(self.indexer.store.texts)}"))


    # --- Textual Event Handlers ---
    
    def on_start_chat(self, message: StartChat):
        """Handles the transition from setup to chat screen."""
        self.initialize_rag()
        self.query_one("#screen_switcher").current = "chat_container"

    def action_show_setup(self):
        """Opens the setup screen to manage keys/models."""
        self.query_one("#screen_switcher").current = "setup_screen"
        self.query_one("#setup_screen", SetupScreen).update_status()

    def action_show_index_prompt(self):
        """Prompts the user for the path to index."""
        # Replace the input box temporarily with an indexing prompt
        self.post_message(StatusUpdate("Enter the absolute path to your codebase in the chat box and hit Enter."))
        self.query_one("#command_input", Input).value = "!index "

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send_btn":
            self.submit_query()
            
    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "command_input":
            self.submit_query()

    def submit_query(self):
        query = self.query_one("#command_input", Input).value.strip()
        self.query_one("#command_input", Input).value = ""
        
        if not query:
            return

        # 1. Handle commands
        if query.lower().startswith("!index"):
            _, path = query.split(maxsplit=1)
            self.handle_index(path.strip())
            return
            
        if self.gemini is None:
            self.post_message(StatusUpdate("[bold red]ERROR:[/bold red] RAG system not initialized. Check API keys."))
            return

        # 2. Add user bubble instantly
        chat_view = self.query_one("#output_area", ChatView)
        chat_view.mount(ChatBubble("user", query))
        chat_view.scroll_end()
        self.memory.save("user", query)

        # 3. Handle RAG and Generation in background thread
        self.run_worker(self.process_rag(query))

    async def process_rag(self, query: str):
        """Asynchronous worker to handle RAG pipeline and LLM call."""
        self.post_message(StatusUpdate("[bold blue]Retrieving context and generating response...[/bold blue]"))

        # 1. Retrieval
        retrieved_context = self.retriever.retrieve(query)
        history = self.memory.load()
        prompt = build_rag_prompt(query, retrieved_context, history)

        # 2. Generation (Blocking call needs to be run in executor)
        try:
            answer = await self.app.run_in_executor(self.gemini.generate, prompt)
        except Exception as e:
            answer = f"**[AI GENERATION ERROR]** Failed to generate response: {e}"
        
        # 3. Update UI
        chat_view = self.query_one("#output_area", ChatView)
        chat_view.mount(ChatBubble("assistant", answer))
        chat_view.scroll_end()
        self.memory.save("assistant", answer)
        
        self.post_message(StatusUpdate("[bold green]Response ready.[/bold green]"))


    def handle_index(self, path: str):
        """Handles the codebase indexing process asynchronously."""
        self.post_message(StatusUpdate(f"[bold yellow]Starting indexing of {path}. This may take a moment...[/bold yellow]"))
        self.run_worker(self.run_index_process(path))

    async def run_index_process(self, path: str):
        try:
            await self.app.run_in_executor(self.indexer.index_directory, path)
            self.post_message(StatusUpdate(f"[bold green]Indexing successful![/bold green] Total chunks: {len(self.indexer.store.texts)}"))
        except Exception as e:
            self.post_message(StatusUpdate(f"[bold red]INDEXING FAILED:[/bold red] {e}"))

    def on_status_update(self, message: StatusUpdate):
        self.query_one("#status_bar", Static).update(message.message)


if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # We must redefine build_rag_prompt here or import it from the old main.py 
    # For simplicity in this answer, let's include the definition here.
    def build_rag_prompt(query, retrieved_context, history):
        system_instruction = (
            "You are an expert software engineer and AI coding assistant. "
            "Your primary goal is to analyze the provided code context and "
            "conversation history to solve the user's coding problems, explain concepts, "
            "refactor code, or fix bugs. Be concise, accurate, and use proper Markdown for code blocks."
        )

        history_str = "\n".join(
            f"[{msg['role'].upper()}]: {msg['content']}" for msg in history
        )
        context_str = "\n---\n".join(retrieved_context)

        prompt = f"""
{system_instruction}

---
[START CONTEXT]
The following code snippets are relevant to the user's request. Each chunk is prefixed 
with the file path it originated from. Use this information judiciously to answer the query.

{context_str or "No relevant code context was retrieved from the codebase."}
[END CONTEXT]
---

[CONVERSATION HISTORY]
{history_str or "No previous conversation history."}
---

[USER QUESTION]
{query}
"""
        return prompt

    app = RAGCoderApp()
    app.run()
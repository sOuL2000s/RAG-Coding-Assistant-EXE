import sys
import os
import shutil 
import glob
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLineEdit, QPushButton, QScrollArea, 
    QMenuBar, QMenu, QStatusBar, QMessageBox, QFileDialog, 
    QListWidget, QListWidgetItem, QComboBox, QLabel, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QIcon
from concurrent.futures import ThreadPoolExecutor

# Import RAG components
from llm.gemini_client import GeminiClient
from retrieval.retriever import Retriever
from memory.chat_memory import ChatMemory, MEMORY_DIR, CHAT_META_FILE
from indexing.code_indexer import CodeIndexer
from config_manager import config_manager
from gui.chat_widget import ChatViewWidget
from gui.setup_dialog import SetupDialog
from themes import THEMES, DEFAULT_THEME # NEW IMPORT
from models import DEFAULT_MODEL # Ensure DEFAULT_MODEL is imported

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True) # Ensure chats directory exists

# Global executor for background tasks
executor = ThreadPoolExecutor(max_workers=5)

# --- Threading Classes (RAGWorker and IndexWorker remain identical) ---
class RAGWorker(QThread):
    finished = Signal(str, str) 
    error = Signal(str)
    status = Signal(str)
    
    def __init__(self, query, gemini, retriever, memory, prompt_builder):
        super().__init__()
        self.query = query
        self.gemini = gemini
        self.retriever = retriever
        self.memory = memory
        self.prompt_builder = prompt_builder

    def run(self):
        try:
            self.status.emit("Retrieving context and generating response...")
            retrieved_context = self.retriever.retrieve(self.query)
            history = self.memory.load()
            prompt = self.prompt_builder(self.query, retrieved_context, history)
            answer = self.gemini.generate(prompt)
            self.memory.save("assistant", answer)
            self.finished.emit("assistant", answer)
            self.status.emit("Response ready.")
        except Exception as e:
            self.error.emit(f"AI Error: {e}")
            self.status.emit("Error generating response.")

class IndexWorker(QThread):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, paths: list[str], indexer):
        super().__init__()
        # paths is now a list of directories or files
        self.paths = paths 
        self.indexer = indexer

    def run(self):
        try:
            # Call the updated indexer method
            self.indexer.index_paths(self.paths) 
            self.finished.emit(f"Indexing successful! Total chunks: {len(self.indexer.store.texts)}")
        except Exception as e:
            self.error.emit(f"Indexing Failed: {e}")

# --- Main Application Window ---

class RAGCoderWindow(QMainWindow):
    # Signals for UI updates from workers
    rag_finished_signal = Signal(str, str) 
    rag_error_signal = Signal(str)
    status_update_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RAG Coding Assistant (Gemini)")
        self.resize(1400, 800) 
        
        self.gemini = None
        self.retriever = None
        self.memory = ChatMemory() # Initialize memory first
        self.indexer = CodeIndexer()
        
        # Connect proxy signals to slots
        self.rag_finished_signal.connect(self._rag_finished)
        self.rag_error_signal.connect(self._rag_error)
        
        self._setup_rag() # Configure RAG components
        self._setup_ui()
        self.apply_theme(config_manager.get_current_theme()) # Apply saved theme

    # --- UI Setup ---

    def _setup_ui(self):
        self._create_menu()
        self.status_bar = self.statusBar() # Use standard status bar
        self.status_update_signal.connect(self.status_bar.showMessage) # Connect status signal here

        # Main Splitter: Sidebar and Main Content
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)
        
        # 1. Sidebar Setup
        self.sidebar = self._create_sidebar()
        main_splitter.addWidget(self.sidebar)
        
        # 2. Main Chat Area Setup
        chat_area = QWidget()
        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        self.chat_view = ChatViewWidget()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.chat_view)
        
        chat_layout.addWidget(self.scroll_area)
        chat_layout.addWidget(self._create_input_area())
        
        main_splitter.addWidget(chat_area)
        
        # Set initial splitter size (Sidebar width: 250px)
        main_splitter.setSizes([250, 1150])

        # Load history for the active chat
        self._load_chat_history()

    def _create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar_container")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # New Chat Button
        new_chat_btn = QPushButton("✨ New Chat")
        new_chat_btn.setObjectName("new_chat_btn")
        new_chat_btn.clicked.connect(self._new_chat_session)
        layout.addWidget(new_chat_btn)

        # Chat List
        layout.addWidget(QLabel("<b>Chat History</b>:"))
        self.chat_list = QListWidget()
        self.chat_list.setObjectName("chat_list_widget")
        self.chat_list.itemClicked.connect(self._switch_chat_session)
        self.chat_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chat_list.customContextMenuRequested.connect(self._show_chat_context_menu)
        layout.addWidget(self.chat_list)
        
        self._refresh_chat_list()
        
        # Theme Selector
        layout.addWidget(QLabel("<b>Coding Theme</b>:"))
        self.theme_combo = QComboBox()
        for name in THEMES.keys():
            self.theme_combo.addItem(name, name)
        self.theme_combo.setCurrentText(config_manager.get_current_theme())
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        layout.addWidget(self.theme_combo)

        # Space filler
        layout.addStretch(1)

        # Clear Chat Button (Clears current conversation)
        clear_chat_btn = QPushButton("Clear Current Chat")
        clear_chat_btn.clicked.connect(self._clear_active_chat)
        layout.addWidget(clear_chat_btn)

        # Delete ALL Chats Button
        delete_all_chats_btn = QPushButton("Delete ALL Chats")
        delete_all_chats_btn.setObjectName("delete_all_chats_btn")
        delete_all_chats_btn.clicked.connect(self._clear_all_chat_history)
        layout.addWidget(delete_all_chats_btn)

        return sidebar

    def _create_input_area(self):
        input_container = QWidget()
        input_container.setObjectName("chat_input_container")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter command or coding question...")
        self.input_field.returnPressed.connect(self._handle_input)
        
        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("send_button")
        self.send_button.clicked.connect(self._handle_input)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        return input_container

    def _create_menu(self):
        menu_bar = QMenuBar()
        
        settings_menu = QMenu("&Settings", self)
        key_action = settings_menu.addAction("Manage API Keys & Model")
        key_action.triggered.connect(self._show_setup_dialog)
        
        # NEW: Delete Settings & API Keys
        clear_settings_action = settings_menu.addAction("Delete Settings & API Keys")
        clear_settings_action.triggered.connect(self._clear_settings_data)

        data_menu = QMenu("&Data Management", self)
        
        index_dir_action = data_menu.addAction("Index Codebase Directory...")
        index_dir_action.triggered.connect(self._prompt_for_indexing_directory)
        
        # NEW: Index Specific Files
        index_files_action = data_menu.addAction("Index Specific Code Files...")
        index_files_action.triggered.connect(self._prompt_for_indexing_files)
        
        data_menu.addSeparator() 
        
        # NEW: Clear Index Data
        clear_index_action = data_menu.addAction("Delete Codebase Index")
        clear_index_action.triggered.connect(self._clear_index_data)
        
        clear_all_action = data_menu.addAction("💣 Clear ALL Application Data")
        clear_all_action.triggered.connect(self._clear_all_data)
        
        help_menu = QMenu("&Help", self)
        docs_action = help_menu.addAction("About RAG Coder")
        docs_action.triggered.connect(lambda: QMessageBox.information(self, "About", "RAG Coding Assistant powered by Gemini and FAISS.\nUI Framework: PySide6\nIndex Engine: FAISS"))
        
        menu_bar.addMenu(settings_menu)
        menu_bar.addMenu(data_menu)
        menu_bar.addMenu(help_menu)
        self.setMenuBar(menu_bar)

    # --- Theme Management ---
    
    def apply_theme(self, theme_name: str):
        """Applies the selected QSS theme to the entire application."""
        if theme_name in THEMES:
            self.setStyleSheet(THEMES[theme_name]["QSS"])
            config_manager.set_current_theme(theme_name)
            
            # Ensure chat bubbles are re-rendered with new background colors
            self.chat_view.refresh_view(self.memory.load())

    # --- Chat Management Logic ---
    
    def _refresh_chat_list(self):
        """Populates the sidebar chat list."""
        self.chat_list.clear()
        chats = self.memory.get_all_chats()
        active_id = self.memory.active_chat_id
        
        # Display chats sorted by key (simple alphabetical for now)
        for chat_id, name in chats.items():
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, chat_id)
            if chat_id == active_id:
                item.setText(f"➤ {name}")
                self.chat_list.setCurrentItem(item)
            self.chat_list.addItem(item)

    def _new_chat_session(self):
        """Creates a new chat and switches to it."""
        new_id = self.memory.new_chat(f"Chat {len(self.memory.get_all_chats()) + 1}")
        self._refresh_chat_list()
        self.chat_view.clear_messages()
        self.status_update_signal.emit(f"New chat session started: {self.memory.metadata[new_id]}")

    def _switch_chat_session(self, item: QListWidgetItem):
        """Switches the active chat based on sidebar selection."""
        chat_id = item.data(Qt.UserRole)
        if chat_id != self.memory.active_chat_id:
            try:
                self.memory.switch_chat(chat_id)
                self.chat_view.clear_messages()
                self._load_chat_history()
                self._refresh_chat_list()
                self.status_update_signal.emit(f"Switched to chat: {self.memory.metadata[chat_id]}")
            except ValueError:
                self.status_update_signal.emit("Error switching chat.")

    def _show_chat_context_menu(self, pos):
        """Context menu for deleting chats."""
        item = self.chat_list.itemAt(pos)
        if item:
            menu = QMenu(self)
            delete_action = menu.addAction("Delete Chat")
            action = menu.exec(self.chat_list.mapToGlobal(pos))
            
            if action == delete_action:
                chat_id = item.data(Qt.UserRole)
                self._delete_chat_session(chat_id)

    def _delete_chat_session(self, chat_id: str):
        reply = QMessageBox.question(self, 'Confirm Deletion', 
                                    f"Are you sure you want to permanently delete chat '{self.memory.metadata.get(chat_id, 'Unknown')}'?", 
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            was_active = (chat_id == self.memory.active_chat_id)
            self.memory.delete_chat(chat_id)
            
            self._refresh_chat_list()
            
            if was_active:
                self.chat_view.clear_messages()
                self._load_chat_history()
                self.status_update_signal.emit("Chat deleted. Switched to new default session.")
            else:
                self.status_update_signal.emit("Chat deleted.")

    def _clear_active_chat(self):
        """Clears all messages in the currently active chat session."""
        reply = QMessageBox.question(self, 'Confirm Clear', 
                                    f"Are you sure you want to clear all messages from the current chat?", 
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.memory.clear_active_chat()
            self.chat_view.clear_messages()
            self.status_update_signal.emit("Current chat history cleared.")

    def _clear_all_chat_history(self):
        """Deletes all chat files and metadata, then starts a new default chat."""
        reply = QMessageBox.critical(self, 'Confirm Deletion', 
                                    "Are you sure you want to permanently delete ALL saved chat sessions?", 
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # 1. Clear config state immediately: 
                config_manager.set_active_chat_id(None)
                
                # 2. Remove all chat files and the chat directory structure
                shutil.rmtree(MEMORY_DIR, ignore_errors=True)
                os.makedirs(MEMORY_DIR) 
                
                # 3. Remove metadata file
                if os.path.exists(CHAT_META_FILE):
                    os.remove(CHAT_META_FILE)
                
                # 4. Re-initialize memory
                self.memory = ChatMemory() 
                
                # 5. Update UI
                self.chat_list.clear() 
                self.chat_view.clear_messages()
                self._refresh_chat_list()
                
                self.status_update_signal.emit("All chat history deleted. New session created.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear chat history: {e}")

    # --- Data Clearing Management (New/Refined) ---
    
    def _clear_settings_data(self):
        """Resets application settings (API keys, model, theme) but keeps chat history and index."""
        reply = QMessageBox.critical(self, 'Confirm Reset', 
                                    "Are you sure you want to delete all stored API keys, reset the active model, and reset the theme?", 
                                    QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            try:
                # 1. Reset Configuration
                config_manager.config["api_keys"] = []
                config_manager.config["current_model"] = DEFAULT_MODEL
                config_manager.config["current_theme"] = DEFAULT_THEME
                config_manager._save()
                
                # 2. Re-initialize Gemini client
                self.gemini = None 
                
                QMessageBox.information(self, "Success", "Settings (API keys, model, theme) have been reset. Please set a new API key to continue.")
                self.status_update_signal.emit("Settings reset. RAG system disabled until new key is configured.")
                self._show_setup_dialog()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear settings: {e}")

    def _clear_index_data(self):
        """Deletes only the vector store files (faiss.index and meta.pkl)."""
        reply = QMessageBox.question(self, 'Confirm Deletion', 
                                    "Are you sure you want to permanently delete the indexed codebase data (FAISS index)? You will need to re-index your code to use RAG.", 
                                    QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            try:
                # 1. Clear Vector Index Files
                index_files = ["data/faiss.index", "data/meta.pkl"]
                for f in index_files:
                    if os.path.exists(f): os.remove(f)
                
                # 2. Re-initialize indexer and retriever immediately (resets internal state)
                self.indexer = CodeIndexer() 
                self.retriever = Retriever()
                
                self.status_update_signal.emit("Codebase index successfully deleted.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear index data: {e}")
    
    def _clear_all_data(self):
        """Deletes all memory, index, and configuration."""
        reply = QMessageBox.critical(self, 'DANGER: Clear All Data', 
            "WARNING: This will permanently delete ALL chat history, the vector index (code knowledge), and reset API key configurations. Are you absolutely sure?", 
            QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            try:
                # 1. Clear Vector Index Files
                index_files = ["data/faiss.index", "data/meta.pkl"]
                for f in index_files:
                    if os.path.exists(f): os.remove(f)
                
                # 2. Clear Chat History Files
                shutil.rmtree(MEMORY_DIR, ignore_errors=True)
                os.makedirs(MEMORY_DIR)
                
                # 3. Reset Configuration (clear keys, reset model/theme, reset active chat ID)
                config_manager.config["api_keys"] = []
                config_manager.config["current_model"] = DEFAULT_MODEL
                config_manager.config["current_theme"] = DEFAULT_THEME
                config_manager.config["active_chat_id"] = None 
                config_manager._save()
                
                # 4. Re-initialize components
                self.indexer = CodeIndexer()
                self.retriever = Retriever()
                self.memory = ChatMemory() # Creates a new 'Default Chat'
                self.gemini = None
                
                # 5. Update UI
                self._refresh_chat_list()
                self.chat_view.clear_messages()
                
                QMessageBox.information(self, "Success", "All application data cleared. Please manage API keys to restart RAG functionality.")
                self._show_setup_dialog()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear data: {e}")


    # --- RAG/Setup/Loading ---

    def _setup_rag(self):
        """Initializes RAG components based on saved configuration."""
        keys = config_manager.get_keys()
        if not keys:
            self.status_update_signal.emit("SETUP REQUIRED: Please add API keys in Settings menu.")
            # If no keys on startup, force the setup dialog
            if not self.gemini: 
                 self._show_setup_dialog()
            return

        try:
            self.gemini = GeminiClient()
            self.retriever = Retriever()
            self.status_update_signal.emit(f"RAG Ready. Model: {self.gemini.model_name}. Chunks: {len(self.indexer.store.texts)}")
        except Exception as e:
            QMessageBox.critical(self, "RAG Initialization Error", f"Could not initialize Gemini Client: {e}")
            self.status_update_signal.emit("ERROR: Check API Keys.")

    def _load_chat_history(self):
        history = self.memory.load()
        for msg in history:
            self.chat_view.add_message(msg['role'], msg['content'])
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
            
    def _show_setup_dialog(self):
        dialog = SetupDialog(self)
        dialog.config_updated.connect(self._setup_rag) 
        dialog.exec() 

    # --- Command and Worker Management ---

    def _handle_input(self):
        query = self.input_field.text().strip()
        self.input_field.clear()
        
        if not query: return
        
        if query.lower().startswith("!index"):
            try:
                _, path = query.split(maxsplit=1)
                # Pass a list containing the single path for directory indexing
                self._start_index_worker([path.strip()]) 
            except ValueError:
                self.status_bar.showMessage("Invalid index command. Use: !index <path>")
            return
        
        if not self.gemini or not self.gemini.model:
            QMessageBox.warning(self, "System Not Ready", "Please configure API keys in Settings.")
            return

        # 1. Display user message
        self.chat_view.add_message("user", query)
        self.memory.save("user", query)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        
        # 2. Start RAG worker
        self._start_rag_worker(query)

    def _prompt_for_indexing_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Codebase Directory to Index")
        if dir_path:
            self._start_index_worker([dir_path]) # Pass as list

    def _prompt_for_indexing_files(self):
        """Allows selection of multiple files for indexing (new feature)."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select Code Files to Index", 
            "", 
            "Code Files (*.py *.js *.ts *.java *.cpp *.c *.h *.cs *.go *.html *.css *.md);;All Files (*)"
        )
        if file_paths:
            self._start_index_worker(file_paths) # Pass the list of files

    def _start_rag_worker(self, query):
        self.rag_worker = RAGWorker(query, self.gemini, self.retriever, self.memory, build_rag_prompt)
        self.rag_worker.finished.connect(self.rag_finished_signal)
        self.rag_worker.error.connect(self.rag_error_signal)
        self.rag_worker.status.connect(self.status_update_signal)
        self.rag_worker.start()

    def _rag_finished(self, role, content):
        self.chat_view.add_message(role, content)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        
    def _rag_error(self, message):
        QMessageBox.critical(self, "Gemini Error", message)

    def _start_index_worker(self, paths: list[str]):
        if not paths: return 
        
        self.index_worker = IndexWorker(paths, self.indexer) # Use the list of paths
        self.index_worker.finished.connect(self._index_finished)
        self.index_worker.error.connect(self._index_error)
        
        display_path = paths[0] if len(paths) == 1 else f"{len(paths)} items"
        self.status_update_signal.emit(f"Indexing started for: {display_path}")
        self.index_worker.start()

    def _index_finished(self, message):
        self.status_update_signal.emit(message)
        # Re-initialize retriever to recognize new index data
        self.retriever = Retriever()

    def _index_error(self, message):
        QMessageBox.critical(self, "Indexing Error", message)
        self.status_update_signal.emit("Indexing failed.")

# --- Prompt Builder ---
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

    prompt = f"""{system_instruction}
--- [START CONTEXT]
The following code snippets are relevant to the user's request. Each chunk is prefixed with the file path it originated from. Use this information judiciously to answer the query.
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RAGCoderWindow()
    window.show()
    sys.exit(app.exec())
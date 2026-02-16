from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor
import datetime
import re

# --- 1. Status Metrics Panel ---

class StatusMetrics(QWidget):
    """Displays key RAG system metrics (chunks, memory status, indexed path)."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_chunks = 0
        self.memory_state = "Idle"
        self.indexing_path = "N/A"
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        
        self.title_label = QLabel("<b>System Metrics:</b>")
        self.chunk_label = QLabel()
        self.status_label = QLabel()
        self.path_label = QLabel()
        
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.chunk_label)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.path_label)
        self.layout.addStretch(1)

        self.setObjectName("status_metrics_widget")
        self.update_metrics()

    def update_metrics(self, total_chunks: int = None, memory_state: str = None, indexing_path: str = None, model: str = None):
        """Updates internal state and re-renders the labels."""
        if total_chunks is not None:
            self.total_chunks = total_chunks
        if memory_state is not None:
            self.memory_state = memory_state
        if indexing_path is not None:
            # Shorten long paths for display
            self.indexing_path = indexing_path if len(indexing_path) < 50 else f"...{indexing_path[-47:]}"
        
        # Using simple HTML/span tags for coloring, matching the Rich markup spirit
        chunk_text = f"Total Indexed Chunks: <span style='color: lightgreen;'>{self.total_chunks:,}</span>"
        status_text = f"Indexing Status: <span style='color: yellow;'>{self.memory_state}</span>"
        path_text = f"Current Indexed Path: {self.indexing_path}"

        self.chunk_label.setText(chunk_text)
        self.status_label.setText(status_text)
        self.path_label.setText(path_text)

        # Ensure labels interpret HTML styling
        self.chunk_label.setTextFormat(Qt.RichText)
        self.status_label.setTextFormat(Qt.RichText)
        self.path_label.setTextFormat(Qt.RichText)

        self.adjustSize()


# --- 2. Console Log View ---

class ConsoleLogView(QTextEdit):
    """A persistent log view displaying real-time background activity."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setReadOnly(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setObjectName("console_log_view")
        
        # Initial message
        self.log_message("[bold green]Application Log Initialized.[/bold green]")
        
    def log_message(self, message: str):
        """Writes a time-stamped message to the log and scrolls to the end."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # 1. Replace Rich opening tags with HTML <b> and color spans
        html_message = message.replace("[bold red]", "<b style='color: red;'>")
        html_message = html_message.replace("[bold yellow]", "<b style='color: yellow;'>")
        html_message = html_message.replace("[bold green]", "<b style='color: lightgreen;'>")
        html_message = html_message.replace("[bold blue]", "<b style='color: lightblue;'>")
        html_message = html_message.replace("[bold magenta]", "<b style='color: magenta;'>")
        
        # 2. Replace generic Rich closing tag [/bold] with HTML </b>
        html_message = html_message.replace("[/bold]", "</b>")

        # 3. FIX: Strip or replace any remaining Rich closing tags (e.g., [/bold green])
        # This replaces any sequence matching [/word or /word word] with </b>
        html_message = re.sub(r'\[/\w+\s?\w*\]', '</b>', html_message)
        
        full_html = f"[{timestamp}] {html_message}<br>"
        
        self.moveCursor(QTextCursor.End)
        self.insertHtml(full_html)
        self.ensureCursorVisible() # Scroll to end
        
        # Use QTimer to ensure the scrollbar updates immediately
        QTimer.singleShot(10, lambda: self.verticalScrollBar().setValue(self.verticalScrollBar().maximum()))

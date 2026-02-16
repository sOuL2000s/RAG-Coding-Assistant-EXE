from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QSizePolicy, 
    QApplication, QPushButton, QHBoxLayout, QLabel, 
    QScrollArea
)
from PySide6.QtCore import Qt
from markdown_it import MarkdownIt
from config_manager import config_manager
from themes import THEMES

# Initialize markdown renderer
md = MarkdownIt().enable(['fence', 'code', 'list', 'hr', 'table', 'link', 'image', 'emphasis', 'html_block'])

# --- New: Dedicated Code Block Widget ---

class CodeBlockContainer(QWidget):
    """Dedicated widget for a code block, including the header (language and copy button)."""
    
    def __init__(self, code_text: str, language: str, theme_data: dict, status_signal=None):
        super().__init__()
        self.code_text = code_text
        self.status_signal = status_signal
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- 1. Header (Language Label & Copy Button) ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 4, 8, 4)
        header_layout.setSpacing(10)
        
        lang_label = QLabel(f"<b>{language.upper() or 'PLAINTEXT'}</b>")
        
        copy_btn = QPushButton("Copy Code")
        copy_btn.setObjectName("copy_code_btn")
        copy_btn.setFixedSize(80, 24)
        copy_btn.clicked.connect(self._copy_code)
        
        header_layout.addWidget(lang_label)
        header_layout.addStretch(1)
        header_layout.addWidget(copy_btn)
        
        layout.addWidget(header_widget)
        
        # --- 2. Code Content Display ---
        code_browser = QTextBrowser()
        code_browser.setReadOnly(True)
        # Use plain text to avoid HTML escaping issues with code
        code_browser.setPlainText(code_text.strip()) 
        code_browser.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        # Calculate height
        lines = code_text.count('\n') + 2 
        font_height = code_browser.fontMetrics().height()
        
        code_browser.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        code_browser.setMinimumHeight(lines * font_height + 20)
        code_browser.setMaximumHeight(lines * font_height + 20)
        
        layout.addWidget(code_browser)
        
        # Apply specific QSS styling
        self.setStyleSheet(f"""
            QWidget {{
                border-radius: 6px; 
                margin: 5px 0;
                border: 1px solid {theme_data.get('html_code_border', '#444')};
                background-color: {theme_data.get('html_code_bg', '#282c34')};
            }}
            QWidget:nth-child(1) {{ /* Header Widget */
                background-color: {theme_data.get('html_code_header_bg', '#3e4452')};
                border-radius: 6px 6px 0 0;
            }}
            QLabel {{
                color: {theme_data.get('html_code_color', '#abb2bf')};
            }}
            QTextBrowser {{
                background-color: {theme_data.get('html_code_bg', '#282c34')};
                color: {theme_data.get('html_code_color', '#abb2bf')};
                font-family: monospace;
                border: none;
                padding: 5px;
            }}
            QPushButton#copy_code_btn {{
                background-color: {theme_data.get('html_copy_btn_bg', '#bd93f9')};
                color: white;
                border-radius: 3px;
                padding: 2px 5px;
            }}
        """)

    def _copy_code(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_text)
        if self.status_signal:
            self.status_signal.emit("[Copied] Code block to clipboard.")


# --- Modified Chat Bubble ---

class ChatBubble(QWidget):
    def __init__(self, role, content, status_signal=None):
        super().__init__()
        self.role = role
        self.raw_content = content
        self.status_signal = status_signal
        
        theme_name = config_manager.get_current_theme()
        theme_data = THEMES.get(theme_name, THEMES[list(THEMES.keys())[0]])
        
        if role == "user":
            radius_style = "border-radius: 12px 12px 0 12px;"
            bg_color = theme_data["html_user_bg"]
            text_color = theme_data.get("html_user_text_color", "#f8f8f2")
        else: # assistant
            radius_style = "border-radius: 12px 12px 12px 0;"
            bg_color = theme_data["html_asst_bg"]
            text_color = theme_data.get("html_asst_text_color", "#f8f8f2")

        # Ensure the bubble shrinks to content size horizontally,
        # allowing the parent ChatViewWidget layout manager to correctly float it.
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # Apply the overall bubble QSS style to the wrapper
        self.setStyleSheet(f"""
            ChatBubble {{
                background-color: {bg_color};
                {radius_style}
                padding: 0; 
                margin: 5px 0; 
            }}
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignTop)
        
        self.text_color = text_color

        self._render_hybrid_content(content, theme_data)
        
        # --- Add Copy Raw Text Button (Footer) ---
        
        copy_btn = QPushButton("Copy Raw Text")
        copy_btn.setObjectName("copy_raw_text")
        copy_btn.setFixedSize(120, 28)
        copy_btn.clicked.connect(self._copy_raw_text)
        
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 5, 0, 0)
        button_layout.setSpacing(0)

        # Align button within the footer container based on role
        if role == "user":
            button_layout.addStretch(1) 
            button_layout.addWidget(copy_btn)
            self.main_layout.addWidget(button_container, alignment=Qt.AlignRight)
        else:
            button_layout.addWidget(copy_btn)
            button_layout.addStretch(1) 
            self.main_layout.addWidget(button_container, alignment=Qt.AlignLeft)


    def _render_hybrid_content(self, content: str, theme_data: dict):
        """Parses markdown content into distinct text and code widgets."""
        
        tokens = list(md.parse(content))
        current_html_chunk = ""
        
        # We need to iterate over the tokens and build up HTML until we hit a fence token.
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.type == 'fence' and token.tag == '':
                # A. Flush any pending normal text
                if current_html_chunk.strip():
                    self._add_text_widget(current_html_chunk)
                    current_html_chunk = ""
                
                # B. Add the CodeBlockContainer widget
                code_text = token.content
                language = token.info.strip()
                code_widget = CodeBlockContainer(code_text, language, theme_data, self.status_signal)
                self.main_layout.addWidget(code_widget) 
                
                i += 1 # Move past the fence token
                
            else:
                # Accumulate tokens for general rendering until the next fence
                
                if token.type.endswith('_open'):
                    # Find the corresponding close token index (simplified search for blocks)
                    tag_name = token.type.split('_')[0]
                    close_type = f'{tag_name}_close'
                    
                    # Look ahead for the closing token
                    close_index = None
                    nesting_level = token.level
                    
                    for j in range(i + 1, len(tokens)):
                        if tokens[j].type == 'fence':
                            break # Stop searching if we hit a code fence
                        if tokens[j].type == close_type and tokens[j].level == nesting_level:
                            close_index = j
                            break
                    
                    # If we found a corresponding block close
                    if close_index is not None:
                        # Render the whole block (from open to close)
                        html_segment = md.renderer.render(tokens[i:close_index + 1], md.options, {})
                        current_html_chunk += html_segment
                        i = close_index + 1 # Skip tokens in the rendered block
                        continue
                
                # Render standalone tokens (text, softbreak, etc.)
                html_segment = md.renderer.render([token], md.options, {})
                current_html_chunk += html_segment
                i += 1


        # C. Flush any final text chunk
        if current_html_chunk.strip():
            self._add_text_widget(current_html_chunk)


    def _add_text_widget(self, html_content: str):
        """Creates and adds a QTextBrowser for general (non-code) markdown content."""
        
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setReadOnly(True)
        text_browser.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        text_browser.setStyleSheet("border: none; background-color: transparent;")

        # Inject standard body and text coloring into the HTML content
        formatted_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial; font-size: 10pt; background-color: transparent; margin: 0; padding: 0; color: {self.text_color}; }}
                p {{ margin: 0; padding: 0 0 5px 0; }} 
                h1, h2, h3, h4, h5, h6 {{ margin-top: 5px; margin-bottom: 5px; font-weight: bold; }}
                ul, ol {{ margin: 5px 0 5px 20px; padding: 0; }} 
                li {{ margin-bottom: 3px; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        text_browser.setHtml(formatted_html)
        
        # Set height based on content
        doc = text_browser.document()
        # Set text width based on the assumed max bubble width (85% of chat area)
        doc.setTextWidth(1150 * 0.85) 
        ideal_height = doc.size().height()
        
        text_browser.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        text_browser.setMinimumHeight(int(ideal_height) + 10) 
        text_browser.setMaximumHeight(int(ideal_height) + 10)
        
        self.main_layout.addWidget(text_browser)

    def parent_layout_alignment(self, alignment):
        """Sets the alignment property so the parent layout (ChatViewWidget) correctly floats this bubble."""
        if self.role == "user":
            self.main_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)
        else:
            self.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    def _copy_raw_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.raw_content)
        
        if self.status_signal:
            self.status_signal.emit(f"[Copied] Message ({self.role}) to clipboard.")


class ChatViewWidget(QWidget):
    def __init__(self, status_signal=None):
        super().__init__()
        # Ensure ChatViewWidget is named for QSS targeting
        self.setObjectName("ChatViewWidget") 
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.status_signal = status_signal
        
    def clear_messages(self):
        """Removes all child widgets (messages) from the layout."""
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def add_message(self, role, content, status_signal=None):
        # Determine alignment based on role to correctly float the bubble horizontally
        alignment = Qt.AlignRight if role == "user" else Qt.AlignLeft
        # Pass the status signal down to the bubble
        bubble = ChatBubble(role, content, status_signal or self.status_signal) 
        self.layout.addWidget(bubble, alignment=alignment)
        
    def refresh_view(self, history: list[dict]): 
        """Clears and re-renders the chat history."""
        self.clear_messages()
        for msg in history:
            # When refreshing, ensure we pass the signal to new bubbles
            self.add_message(msg['role'], msg['content'], self.status_signal)
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QSizePolicy, QApplication
from PySide6.QtCore import Qt
from markdown_it import MarkdownIt
from config_manager import config_manager
from themes import THEMES

# Initialize markdown renderer to convert MD to HTML
md = MarkdownIt().enable(['fence', 'code', 'list'])

class ChatBubble(QWidget):
    def __init__(self, role, content):
        super().__init__()
        # Get active theme details for dynamic coloring
        theme_name = config_manager.get_current_theme()
        theme_data = THEMES.get(theme_name, THEMES[list(THEMES.keys())[0]]) # Fallback
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: transparent;")
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setReadOnly(True)
        browser.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard) # Ensure copyable
        
        # --- Dynamic Styling based on Role and Theme ---
        
        if role == "user":
            bg_color = theme_data["html_user_bg"]
            text_color = "#000000" if theme_name == "ChatGPT Minimal" else "#f8f8f2"
            alignment = Qt.AlignRight
            # Use max-width to stop bubbles from filling the entire screen
            # margin: top right bottom left;
            bubble_style = f"padding: 10px; border-radius: 10px; background-color: {bg_color}; color: {text_color}; margin: 5px 0 5px auto; max-width: 75%;"
        else: # assistant
            bg_color = theme_data["html_asst_bg"]
            text_color = "#343541" if theme_name == "ChatGPT Minimal" else "#f8f8f2"
            alignment = Qt.AlignLeft
            bubble_style = f"padding: 10px; border-radius: 10px; background-color: {bg_color}; color: {text_color}; margin: 5px auto 5px 0; max-width: 85%;" # Assistant allowed slightly more width

        html_content = md.render(content)
        code_color = theme_data["html_code_color"]
        
        # Inject styling into the HTML head
        formatted_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial; font-size: 10pt; background-color: transparent; margin: 0; padding: 0; }}
                /* Code block styling - MUST be inside the QTextBrowser HTML */
                pre {{ 
                    background-color: #1c1c1c; /* Use deep dark color for code background for contrast */
                    color: {code_color}; 
                    padding: 10px; 
                    border-radius: 5px; 
                    overflow-x: auto; 
                    margin-top: 10px; 
                    border: 1px solid {code_color}; 
                }}
                code {{ font-family: monospace; white-space: pre-wrap; }}
                div.bubble {{ 
                    {bubble_style} 
                    float: {role}; 
                    display: table; /* Ensures text flow respects max-width better */
                }}
            </style>
        </head>
        <body>
            <div class="bubble">
                {html_content}
            </div>
        </body>
        </html>
        """
        browser.setHtml(formatted_html)
        
        # Fix: Use QSizePolicy to ensure browser expands horizontally within its aligned space
        browser.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        # Adjust height based on content
        doc = browser.document()
        # Set text width before calculating height (adjust for padding and margin)
        # We estimate the viewable width based on the parent alignment layout.
        viewport_width = self.parentWidget().width() if self.parentWidget() else 800 
        doc.setTextWidth(viewport_width * 0.7) 
        
        # Recalculate height after setting width
        ideal_height = doc.size().height()
        browser.setFixedHeight(int(ideal_height) + 30) # Add padding buffer

        layout.addWidget(browser, alignment=alignment)

class ChatViewWidget(QWidget):
    # ... (clear_messages, add_message, refresh_view methods remain the same)
    # The refresh_view method ensures that when the theme is switched, 
    # ChatBubble is reconstructed using the latest theme settings from config_manager.
    # We only need to ensure refresh_view is called when the theme changes.
    
    def __init__(self):
        super().__init__()
        # Ensure ChatViewWidget is named for QSS targeting
        self.setObjectName("ChatViewWidget") 
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
    def clear_messages(self):
        """Removes all child widgets (messages) from the layout."""
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def add_message(self, role, content):
        bubble = ChatBubble(role, content)
        self.layout.addWidget(bubble)
        
    def refresh_view(self, history: list[dict]): 
        """Clears and re-renders the chat history."""
        self.clear_messages()
        for msg in history:
            self.add_message(msg['role'], msg['content'])
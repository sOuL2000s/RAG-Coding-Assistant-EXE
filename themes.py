# themes.py
# Define colors for easy injection into the ChatBubble HTML/CSS
# The main QSS controls the application window, menu, and input area.
# The 'html_user_bg' and 'html_asst_bg' are injected into the QTextBrowser's internal HTML style block.

THEMES = {
    "Dracula": {
        "description": "Inspired by the popular Dracula theme, modern and dark.",
        "html_user_bg": "#6272a4",  # Purple
        "html_asst_bg": "#44475a",  # Darker Grey
        "html_code_color": "#50fa7b", # Green
        "QSS": """
            /* General App Styling */
            QMainWindow, QWidget#chat_area_widget { background-color: #282a36; color: #f8f8f2; }
            QMenuBar, QWidget#sidebar_container, QWidget#chat_input_container { background-color: #1a1b26; border-color: #44475a; }
            
            /* Input & Dropdowns */
            QLineEdit, QComboBox, QListWidget, QStatusBar {
                background-color: #44475a; border: 1px solid #6272a4; color: #f8f8f2; padding: 5px; border-radius: 4px;
            }
            
            /* Chat View Area */
            QScrollArea, ChatViewWidget { background-color: #282a36; border: none; }
            
            /* Buttons */
            QPushButton#new_chat_btn, QPushButton#send_button { background-color: #50fa7b; color: #1a1b26; font-weight: bold; }
            QPushButton#delete_all_chats_btn { background-color: #ff5555; color: #1a1b26; }
            QPushButton { background-color: #6272a4; color: #f8f8f2; padding: 8px 15px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #7a8aae; }
            
            /* Sidebar Specifics */
            QWidget#sidebar_container { min-width: 280px; max-width: 280px; border-right: 1px solid #44475a; }
            QListWidget#chat_list_widget { background-color: #1a1b26; }
            QListWidget#chat_list_widget::item:selected { background-color: #44475a; border-left: 3px solid #50fa7b; }
        """
    },
    
    "Monokai": {
        "description": "Classic developer Monokai scheme.",
        "html_user_bg": "#f92672", # Pink
        "html_asst_bg": "#494a41", # Darker Grey
        "html_code_color": "#a6e22e", # Green
        "QSS": """
            QMainWindow, QWidget#chat_area_widget { background-color: #272822; color: #f8f8f2; }
            QMenuBar, QWidget#sidebar_container, QWidget#chat_input_container { background-color: #383a31; border-color: #494a41; }
            
            QLineEdit, QComboBox, QListWidget, QStatusBar {
                background-color: #494a41; border: 1px solid #5d5e56; color: #f8f8f2; padding: 5px; border-radius: 4px;
            }
            
            QScrollArea, ChatViewWidget { background-color: #272822; border: none; }
            
            QPushButton#new_chat_btn, QPushButton#send_button { background-color: #a6e22e; color: #272822; font-weight: bold; }
            QPushButton#delete_all_chats_btn { background-color: #ff007f; color: #272822; }
            QPushButton { background-color: #66d9ef; color: #272822; padding: 8px 15px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #79e9ff; }
            
            QWidget#sidebar_container { min-width: 280px; max-width: 280px; border-right: 1px solid #494a41; }
            QListWidget#chat_list_widget { background-color: #383a31; }
            QListWidget#chat_list_widget::item:selected { background-color: #494a41; border-left: 3px solid #fd971f; }
        """
    },
    
    "One Dark": {
        "description": "Popular VS Code/Atom One Dark scheme.",
        "html_user_bg": "#61afef", # Blue
        "html_asst_bg": "#3e4451", # Dark Gray
        "html_code_color": "#98c379", # Light Green
        "QSS": """
            QMainWindow, QWidget#chat_area_widget { background-color: #282c34; color: #abb2bf; }
            QMenuBar, QWidget#sidebar_container, QWidget#chat_input_container { background-color: #21252b; border-color: #3e4451; }
            
            QLineEdit, QComboBox, QListWidget, QStatusBar {
                background-color: #3e4451; border: 1px solid #545b68; color: #abb2bf; padding: 5px; border-radius: 4px;
            }
            
            QScrollArea, ChatViewWidget { background-color: #282c34; border: none; }
            
            QPushButton#new_chat_btn, QPushButton#send_button { background-color: #e5c07b; color: #21252b; font-weight: bold; }
            QPushButton#delete_all_chats_btn { background-color: #e06c75; color: #21252b; }
            QPushButton { background-color: #61afef; color: #21252b; padding: 8px 15px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #569cd6; }
            
            QWidget#sidebar_container { min-width: 280px; max-width: 280px; border-right: 1px solid #3e4451; }
            QListWidget#chat_list_widget { background-color: #21252b; }
            QListWidget#chat_list_widget::item:selected { background-color: #3e4451; border-left: 3px solid #c678dd; }
        """
    },
    
    "Matrix": {
        "description": "The green code aesthetic.",
        "html_user_bg": "#009900", # Lighter Green
        "html_asst_bg": "#111111", # Very Dark Grey
        "html_code_color": "#00ff00", # Neon Green
        "QSS": """
            QMainWindow, QWidget#chat_area_widget { background-color: #000000; color: #00ff00; }
            QMenuBar, QWidget#sidebar_container, QWidget#chat_input_container { background-color: #001100; border-color: #006600; }
            
            QLineEdit, QComboBox, QListWidget, QStatusBar {
                background-color: #003300; border: 1px solid #009900; color: #00ff00; padding: 5px; border-radius: 4px;
            }
            
            QScrollArea, ChatViewWidget { background-color: #000000; border: none; }
            
            QPushButton#new_chat_btn, QPushButton#send_button { background-color: #00ff00; color: #000000; font-weight: bold; }
            QPushButton#delete_all_chats_btn { background-color: #ff0000; color: #000000; }
            QPushButton { background-color: #006600; color: #00ff00; padding: 8px 15px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #009900; }
            
            QWidget#sidebar_container { min-width: 280px; max-width: 280px; border-right: 1px solid #006600; }
            QListWidget#chat_list_widget { background-color: #001100; }
            QListWidget#chat_list_widget::item:selected { background-color: #003300; border-left: 3px solid #00ff00; }
        """
    },
    
    "ChatGPT Minimal": {
        "description": "Extreme light/dark contrast theme.",
        "html_user_bg": "#a7a7a7", # Light Grey
        "html_asst_bg": "#343541", # Dark GPT Gray
        "html_code_color": "#e06c75", # Red/Pink accent for code
        "QSS": """
            QMainWindow, QWidget#chat_area_widget { background-color: #ffffff; color: #343541; }
            QMenuBar, QWidget#sidebar_container, QWidget#chat_input_container { background-color: #f7f7f8; border-color: #e5e5e5; color: #343541; }
            
            /* We reverse the color scheme for inputs to maintain contrast */
            QLineEdit, QComboBox, QListWidget, QStatusBar {
                background-color: #ffffff; border: 1px solid #e5e5e5; color: #343541; padding: 5px; border-radius: 4px;
            }
            
            QScrollArea, ChatViewWidget { background-color: #ffffff; border: none; }
            
            QPushButton#new_chat_btn, QPushButton#send_button { background-color: #10a37f; color: #ffffff; font-weight: bold; }
            QPushButton#delete_all_chats_btn { background-color: #cc0000; color: #ffffff; }
            QPushButton { background-color: #d1d5db; color: #000000; padding: 8px 15px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #b3b7bb; }
            
            QWidget#sidebar_container { min-width: 280px; max-width: 280px; border-right: 1px solid #e5e5e5; }
            QListWidget#chat_list_widget { background-color: #f7f7f8; }
            QListWidget#chat_list_widget::item:selected { background-color: #e5e5e5; border-left: 3px solid #10a37f; }
        """
    }
}

DEFAULT_THEME = "Dracula"
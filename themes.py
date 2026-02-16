# themes.py
# Define colors for easy injection into the ChatBubble HTML/CSS
# The main QSS controls the application window, menu, and input area.

DEFAULT_THEME = "Dracula"

# --- Common template for new HTML variables ---
def create_html_keys(user_bg, asst_bg, user_text, asst_text, code_color, code_bg, header_bg, code_border, copy_btn_bg):
    return {
        "html_user_bg": user_bg,
        "html_asst_bg": asst_bg,
        "html_user_text_color": user_text,
        "html_asst_text_color": asst_text,
        "html_code_color": code_color,
        "html_code_bg": code_bg,
        "html_code_header_bg": header_bg,
        "html_code_border": code_border,
        "html_copy_btn_bg": copy_btn_bg,
    }

# --- QSS Definitions ---

THEMES = {
    "Dracula": {
        "description": "Inspired by the popular Dracula theme, modern and dark.",
        **create_html_keys(
            user_bg="#6272a4", asst_bg="#44475a", 
            user_text="#f8f8f2", asst_text="#f8f8f2",
            code_color="#50fa7b", code_bg="#1a1b26", 
            header_bg="#282a36", code_border="#6272a4", 
            copy_btn_bg="#bd93f9"
        ),
        "QSS": """
            /* Global Base Styling */
            QWidget { background-color: #282a36; color: #f8f8f2; font-size: 10pt; }
            QMainWindow, QWidget#chat_area_widget { background-color: #282a36; }
            QMenuBar, QWidget#sidebar_container, QWidget#chat_input_container { background-color: #1a1b26; border-color: #44475a; }
            
            /* Input & Dropdowns */
            QLineEdit, QComboBox, QListWidget, QStatusBar {
                background-color: #44475a; border: 1px solid #6272a4; color: #f8f8f2; padding: 5px; border-radius: 8px;
            }
            
            /* Chat View Area */
            QScrollArea, ChatViewWidget { background-color: #282a36; border: none; }
            
            /* Buttons */
            QPushButton#new_chat_btn, QPushButton#send_button { background-color: #50fa7b; color: #1a1b26; font-weight: bold; border-radius: 6px; }
            QPushButton#delete_all_chats_btn { background-color: #ff5555; color: #1a1b26; border-radius: 6px;}
            
            /* Raw Copy Button */
            QPushButton#copy_raw_text { 
                background-color: #bd93f9; 
                color: #f8f8f2; 
                padding: 4px 10px; 
                border-radius: 4px; 
                border: none; 
                font-size: 8pt;
            }
            
            /* General Buttons */
            QPushButton { 
                background-color: #6272a4; 
                color: #f8f8f2; 
                padding: 6px 12px; 
                border-radius: 6px; 
                border: none; 
            }
            QPushButton:hover { background-color: #7a8aae; }
            
            /* Sidebar Specifics */
            QWidget#sidebar_container { min-width: 280px; max-width: 280px; border-right: 1px solid #44475a; }
            QListWidget#chat_list_widget { background-color: #1a1b26; border-radius: 4px; }
            QListWidget#chat_list_widget::item:selected { background-color: #44475a; border-left: 3px solid #50fa7b; }
            
            /* NEW: Status Metrics Panel Styling */
            QWidget#status_metrics_widget {
                background-color: #1a1b26;
                border: 1px solid #6272a4;
                border-radius: 6px;
                padding: 5px; 
            }
            
            /* NEW: Console Log View Styling */
            QTextEdit#console_log_view {
                background-color: #1a1b26;
                border: 1px solid #6272a4;
                color: #f8f8f2; 
                border-radius: 6px;
                font-family: monospace;
            }
        """
    },
    
    "Monokai": {
        "description": "Classic developer Monokai scheme.",
        **create_html_keys(
            user_bg="#f92672", asst_bg="#494a41", 
            user_text="#f8f8f2", asst_text="#f8f8f2",
            code_color="#a6e22e", code_bg="#272822", 
            header_bg="#383a31", code_border="#5d5e56", 
            copy_btn_bg="#66d9ef"
        ),
        "QSS": """
            /* Global Base Styling */
            QWidget { background-color: #272822; color: #f8f8f2; font-size: 10pt; }
            QMainWindow, QWidget#chat_area_widget { background-color: #272822; }
            QMenuBar, QWidget#sidebar_container, QWidget#chat_input_container { background-color: #383a31; border-color: #494a41; }
            
            QLineEdit, QComboBox, QListWidget, QStatusBar {
                background-color: #494a41; border: 1px solid #5d5e56; color: #f8f8f2; padding: 5px; border-radius: 8px;
            }
            
            QScrollArea, ChatViewWidget { background-color: #272822; border: none; }
            
            QPushButton#new_chat_btn, QPushButton#send_button { background-color: #a6e22e; color: #272822; font-weight: bold; border-radius: 6px; }
            QPushButton#delete_all_chats_btn { background-color: #ff007f; color: #272822; border-radius: 6px; }
            QPushButton#copy_raw_text { 
                background-color: #66d9ef; 
                color: #272822; 
                padding: 4px 10px; 
                border-radius: 4px; 
                border: none; 
                font-size: 8pt;
            }
            /* General Buttons */
            QPushButton { 
                background-color: #66d9ef; 
                color: #272822; 
                padding: 6px 12px; 
                border-radius: 6px; 
                border: none; 
            }
            QPushButton:hover { background-color: #79e9ff; }
            
            QWidget#sidebar_container { min-width: 280px; max-width: 280px; border-right: 1px solid #494a41; }
            QListWidget#chat_list_widget { background-color: #383a31; border-radius: 4px; }
            QListWidget#chat_list_widget::item:selected { background-color: #494a41; border-left: 3px solid #fd971f; }
            
            /* NEW: Status Metrics Panel Styling */
            QWidget#status_metrics_widget {
                background-color: #383a31;
                border: 1px solid #a6e22e;
                border-radius: 6px;
                padding: 5px; 
            }
            
            /* NEW: Console Log View Styling */
            QTextEdit#console_log_view {
                background-color: #383a31;
                border: 1px solid #a6e22e;
                color: #f8f8f2;
                border-radius: 6px;
                font-family: monospace;
            }
        """
    },
    
    "One Dark": {
        "description": "Popular VS Code/Atom One Dark scheme.",
        **create_html_keys(
            user_bg="#61afef", asst_bg="#3e4451", 
            user_text="#abb2bf", asst_text="#abb2bf",
            code_color="#98c379", code_bg="#21252b", 
            header_bg="#282c34", code_border="#569cd6", 
            copy_btn_bg="#c678dd"
        ),
        "QSS": """
            /* Global Base Styling */
            QWidget { background-color: #282c34; color: #abb2bf; font-size: 10pt; }
            QMainWindow, QWidget#chat_area_widget { background-color: #282c34; }
            QMenuBar, QWidget#sidebar_container, QWidget#chat_input_container { background-color: #21252b; border-color: #3e4451; }
            
            QLineEdit, QComboBox, QListWidget, QStatusBar {
                background-color: #3e4451; border: 1px solid #545b68; color: #abb2bf; padding: 5px; border-radius: 8px;
            }
            
            QScrollArea, ChatViewWidget { background-color: #282c34; border: none; }
            
            QPushButton#new_chat_btn, QPushButton#send_button { background-color: #e5c07b; color: #21252b; font-weight: bold; border-radius: 6px; }
            QPushButton#delete_all_chats_btn { background-color: #e06c75; color: #21252b; border-radius: 6px; }
            QPushButton#copy_raw_text { 
                background-color: #c678dd; 
                color: #21252b; 
                padding: 4px 10px; 
                border-radius: 4px; 
                border: none; 
                font-size: 8pt;
            }
            /* General Buttons */
            QPushButton { 
                background-color: #61afef; 
                color: #21252b; 
                padding: 6px 12px; 
                border-radius: 6px; 
                border: none; 
            }
            QPushButton:hover { background-color: #569cd6; }
            
            QWidget#sidebar_container { min-width: 280px; max-width: 280px; border-right: 1px solid #3e4451; }
            QListWidget#chat_list_widget { background-color: #21252b; border-radius: 4px; }
            QListWidget#chat_list_widget::item:selected { background-color: #3e4451; border-left: 3px solid #c678dd; }
            
            /* NEW: Status Metrics Panel Styling */
            QWidget#status_metrics_widget {
                background-color: #21252b;
                border: 1px solid #61afef;
                border-radius: 6px;
                padding: 5px; 
            }
            
            /* NEW: Console Log View Styling */
            QTextEdit#console_log_view {
                background-color: #21252b;
                border: 1px solid #61afef;
                color: #abb2bf;
                border-radius: 6px;
                font-family: monospace;
            }
        """
    },
    
    "Matrix": {
        "description": "The green code aesthetic.",
        **create_html_keys(
            user_bg="#009900", asst_bg="#111111", 
            user_text="#00ff00", asst_text="#00ff00",
            code_color="#00ff00", code_bg="#000000", 
            header_bg="#001100", code_border="#006600", 
            copy_btn_bg="#006600"
        ),
        "QSS": """
            /* Global Base Styling */
            QWidget { background-color: #000000; color: #00ff00; font-size: 10pt; }
            QMainWindow, QWidget#chat_area_widget { background-color: #000000; }
            QMenuBar, QWidget#sidebar_container, QWidget#chat_input_container { background-color: #001100; border-color: #006600; }
            
            QLineEdit, QComboBox, QListWidget, QStatusBar {
                background-color: #003300; border: 1px solid #009900; color: #00ff00; padding: 5px; border-radius: 8px;
            }
            
            QScrollArea, ChatViewWidget { background-color: #000000; border: none; }
            
            QPushButton#new_chat_btn, QPushButton#send_button { background-color: #00ff00; color: #000000; font-weight: bold; border-radius: 6px; }
            QPushButton#delete_all_chats_btn { background-color: #ff0000; color: #000000; border-radius: 6px; }
            QPushButton#copy_raw_text { 
                background-color: #006600; 
                color: #00ff00; 
                padding: 4px 10px; 
                border-radius: 4px; 
                border: none; 
                font-size: 8pt;
            }
            /* General Buttons */
            QPushButton { 
                background-color: #006600; 
                color: #000000; 
                padding: 6px 12px; 
                border-radius: 6px; 
                border: none; 
            }
            QPushButton:hover { background-color: #009900; }
            
            QWidget#sidebar_container { min-width: 280px; max-width: 280px; border-right: 1px solid #006600; }
            QListWidget#chat_list_widget { background-color: #001100; border-radius: 4px; }
            QListWidget#chat_list_widget::item:selected { background-color: #003300; border-left: 3px solid #00ff00; }
            
            /* NEW: Status Metrics Panel Styling */
            QWidget#status_metrics_widget {
                background-color: #001100;
                border: 1px solid #00ff00;
                border-radius: 6px;
                padding: 5px; 
            }
            
            /* NEW: Console Log View Styling */
            QTextEdit#console_log_view {
                background-color: #001100;
                border: 1px solid #00ff00;
                color: #00ff00;
                border-radius: 6px;
                font-family: monospace;
            }
        """
    },
    
    "Amoled Black": {
        "description": "Pure black background for AMOLED screens.",
        **create_html_keys(
            user_bg="#333333", asst_bg="#111111", 
            user_text="#ffffff", asst_text="#ffffff",
            code_color="#ffcc00", code_bg="#000000", 
            header_bg="#111111", code_border="#333333", 
            copy_btn_bg="#555555"
        ),
        "QSS": """
            /* Global Base Styling */
            QWidget { background-color: #000000; color: #ffffff; font-size: 10pt; }
            QMainWindow, QWidget#chat_area_widget { background-color: #000000; }
            QMenuBar, QWidget#sidebar_container, QWidget#chat_input_container { background-color: #0a0a0a; border-color: #333333; }
            
            /* Input & Dropdowns */
            QLineEdit, QComboBox, QListWidget, QStatusBar {
                background-color: #111111; border: 1px solid #333333; color: #ffffff; padding: 5px; border-radius: 8px;
            }
            
            /* Chat View Area */
            QScrollArea, ChatViewWidget { background-color: #000000; border: none; }
            
            /* Buttons */
            QPushButton#new_chat_btn, QPushButton#send_button { background-color: #ffcc00; color: #000000; font-weight: bold; border-radius: 6px; }
            QPushButton#delete_all_chats_btn { background-color: #cc0000; color: #ffffff; border-radius: 6px;}
            
            /* Raw Copy Button */
            QPushButton#copy_raw_text { 
                background-color: #555555; 
                color: #ffffff; 
                padding: 4px 10px; 
                border-radius: 4px; 
                border: none; 
                font-size: 8pt;
            }
            
            /* General Buttons */
            QPushButton { 
                background-color: #333333; 
                color: #ffffff; 
                padding: 6px 12px; 
                border-radius: 6px; 
                border: none; 
            }
            QPushButton:hover { background-color: #555555; }
            
            /* Sidebar Specifics */
            QWidget#sidebar_container { min-width: 280px; max-width: 280px; border-right: 1px solid #333333; }
            QListWidget#chat_list_widget { background-color: #0a0a0a; border-radius: 4px; }
            QListWidget#chat_list_widget::item:selected { background-color: #111111; border-left: 3px solid #ffcc00; }
            
            /* NEW: Status Metrics Panel Styling */
            QWidget#status_metrics_widget {
                background-color: #0a0a0a;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 5px; 
            }
            
            /* NEW: Console Log View Styling */
            QTextEdit#console_log_view {
                background-color: #0a0a0a;
                border: 1px solid #333333;
                color: #ffffff; 
                border-radius: 6px;
                font-family: monospace;
            }
        """
    },
    
    "ChatGPT Minimal": {
        "description": "Extreme light/dark contrast theme.",
        **create_html_keys(
            user_bg="#10a37f", asst_bg="#e8e8e8", 
            user_text="#343541", asst_text="#343541",
            code_color="#e06c75", code_bg="#f7f7f8", 
            header_bg="#e5e5e5", code_border="#d1d5db", 
            copy_btn_bg="#10a37f"
        ),
        "QSS": """
            /* Global Base Styling */
            QWidget { background-color: #ffffff; color: #343541; font-size: 10pt; }
            QMainWindow, QWidget#chat_area_widget { background-color: #ffffff; }
            QMenuBar, QWidget#sidebar_container, QWidget#chat_input_container { background-color: #f7f7f8; border-color: #e5e5e5; color: #343541; }
            
            /* Inputs: white background, dark text, light border */
            QLineEdit, QComboBox, QListWidget, QStatusBar {
                background-color: #ffffff; border: 1px solid #e5e5e5; color: #343541; padding: 5px; border-radius: 8px;
            }
            
            QScrollArea, ChatViewWidget { background-color: #ffffff; border: none; }
            
            QPushButton#new_chat_btn, QPushButton#send_button { background-color: #10a37f; color: #ffffff; font-weight: bold; border-radius: 6px; }
            QPushButton#delete_all_chats_btn { background-color: #cc0000; color: #ffffff; border-radius: 6px; }
            QPushButton#copy_raw_text { 
                background-color: #10a37f; 
                color: #ffffff; 
                padding: 4px 10px; 
                border-radius: 4px; 
                border: none; 
                font-size: 8pt;
            }
            /* General Buttons */
            QPushButton { background-color: #d1d5db; color: #343541; padding: 6px 12px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #b3b7bb; }
            
            QWidget#sidebar_container { min-width: 280px; max-width: 280px; border-right: 1px solid #e5e5e5; }
            QListWidget#chat_list_widget { background-color: #f7f7f8; border-radius: 4px; }
            QListWidget#chat_list_widget::item:selected { background-color: #e5e5e5; border-left: 3px solid #10a37f; }
            
            /* NEW: Status Metrics Panel Styling */
            QWidget#status_metrics_widget {
                background-color: #f7f7f8;
                border: 1px solid #10a37f;
                border-radius: 6px;
                color: #343541;
                padding: 5px; 
            }
            
            /* NEW: Console Log View Styling */
            QTextEdit#console_log_view {
                background-color: #f7f7f8;
                border: 1px solid #10a37f;
                color: #343541;
                border-radius: 6px;
                font-family: monospace;
            }
        """
    }
}
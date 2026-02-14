import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QListWidget, QListWidgetItem, QComboBox, QLabel, QMessageBox, 
    QWidget
)
from PySide6.QtCore import Qt, Signal

from config_manager import config_manager
from models import MODEL_OPTIONS

class SetupDialog(QDialog):
    """
    A modal dialog for managing Gemini API keys and selecting the active model.
    """
    # Signal emitted when settings are saved, prompting the main app to re-initialize RAG
    config_updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage API Keys and Model")
        self.setMinimumSize(500, 450)
        
        # Load current state from persistent manager
        self.keys = config_manager.get_keys()[:] # Use a copy for manipulation
        self.active_model = config_manager.get_current_model()
        
        self._setup_ui()
        self._load_keys_list()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # --- API Key Management Section ---
        key_group = QWidget()
        key_layout = QVBoxLayout(key_group)
        key_layout.addWidget(QLabel("<b>Stored API Keys:</b>"))
        
        self.key_list = QListWidget()
        key_layout.addWidget(self.key_list)
        
        # Key Input and Buttons
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter new Gemini API Key (AIza...)")
        self.add_button = QPushButton("Add Key")
        self.remove_button = QPushButton("Remove Selected")
        
        input_layout.addWidget(self.key_input)
        input_layout.addWidget(self.add_button)
        input_layout.addWidget(self.remove_button)
        
        key_layout.addWidget(input_widget)
        main_layout.addWidget(key_group)

        # --- Model Selection Section ---
        model_group = QWidget()
        model_layout = QHBoxLayout(model_group)
        model_layout.addWidget(QLabel("<b>Active LLM Model:</b>"))
        self.model_combo = QComboBox()
        
        # Populate model dropdown
        for name, value in MODEL_OPTIONS.items():
            self.model_combo.addItem(name, value)
            if value == self.active_model:
                self.model_combo.setCurrentText(name)
        
        model_layout.addWidget(self.model_combo)
        model_group.setLayout(model_layout)
        main_layout.addWidget(model_group)

        # --- Footer ---
        footer_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Settings")
        self.save_button.setStyleSheet("background-color: #50fa7b; color: #21252b;") # Green save button
        self.cancel_button = QPushButton("Cancel")
        footer_layout.addWidget(self.cancel_button)
        footer_layout.addWidget(self.save_button)
        main_layout.addLayout(footer_layout)

        # --- Connections ---
        self.add_button.clicked.connect(self._add_key)
        self.remove_button.clicked.connect(self._remove_key)
        self.save_button.clicked.connect(self._save_settings)
        self.cancel_button.clicked.connect(self.reject)

    def _load_keys_list(self):
        self.key_list.clear()
        for key in self.keys:
            display_key = f"{key[:4]}...{key[-4:]}"
            item = QListWidgetItem(display_key)
            item.setData(Qt.UserRole, key) 
            self.key_list.addItem(item)
            
    def _add_key(self):
        new_key = self.key_input.text().strip()
        # Basic validation (Gemini keys usually start with 'AIza')
        if not new_key or not new_key.startswith("AIza"):
            QMessageBox.warning(self, "Invalid Key", "Please enter a valid-looking Gemini API key.")
            return

        if new_key not in self.keys:
            self.keys.append(new_key)
            self._load_keys_list()
            self.key_input.clear()
        else:
            QMessageBox.information(self, "Duplicate", "This key is already stored.")

    def _remove_key(self):
        selected_items = self.key_list.selectedItems()
        if not selected_items:
            return
        
        reply = QMessageBox.question(self, 'Confirm Removal', 
                                    "Are you sure you want to remove the selected API key?", 
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            full_key_to_remove = selected_items[0].data(Qt.UserRole)
            self.keys.remove(full_key_to_remove)
            self._load_keys_list()

    def _save_settings(self):
        # Update model selection
        model_name = self.model_combo.currentData(Qt.UserRole)

        if not self.keys:
            QMessageBox.critical(self, "Error", "You must have at least one API key saved.")
            return

        # 1. Persist keys (clear and rewrite)
        config_manager.config["api_keys"] = self.keys
        # 2. Persist model
        config_manager.set_current_model(model_name)
        
        QMessageBox.information(self, "Success", "Settings saved successfully. The RAG system will now restart.")
        self.config_updated.emit() 
        self.accept()
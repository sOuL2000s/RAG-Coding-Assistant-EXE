import json
import os
from models import DEFAULT_MODEL
from themes import DEFAULT_THEME

CONFIG_FILE = "data/config.json"

class ConfigManager:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/chats", exist_ok=True)
        self.config = self._load()

    def _load(self):
        """Loads configuration from the local file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass # Return default if file is corrupted
        
        # Default structure
        return {
            "api_keys": [],
            "current_model": DEFAULT_MODEL,
            "current_theme": DEFAULT_THEME,
            "active_chat_id": None,
        }

    def _save(self):
        """Saves current configuration to the local file."""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    # --- API Key Management ---
    def get_keys(self):
        return self.config.get("api_keys", [])

    def add_key(self, key):
        if key not in self.config["api_keys"]:
            self.config["api_keys"].append(key)
            self._save()

    def remove_key(self, key):
        if key in self.config["api_keys"]:
            self.config["api_keys"].remove(key)
            self._save()

    # --- Model Management ---
    def get_current_model(self):
        return self.config.get("current_model", DEFAULT_MODEL)

    def set_current_model(self, model_name):
        self.config["current_model"] = model_name
        self._save()

    # --- Theme Management ---
    def get_current_theme(self):
        return self.config.get("current_theme", DEFAULT_THEME)

    def set_current_theme(self, theme_name):
        self.config["current_theme"] = theme_name
        self._save()

    # --- Chat Management ---
    def get_active_chat_id(self):
        return self.config.get("active_chat_id")

    def set_active_chat_id(self, chat_id):
        self.config["active_chat_id"] = chat_id
        self._save()

# Instance shared across the application
config_manager = ConfigManager()
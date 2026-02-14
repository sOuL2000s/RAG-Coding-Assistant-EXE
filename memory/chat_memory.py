import json
import os
import uuid
from config_manager import config_manager # Import config to save active chat ID

MEMORY_DIR = "data/chats"
CHAT_META_FILE = os.path.join("data", "chat_metadata.json") # Ensure this constant is available

class ChatMemory:
    def __init__(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self.metadata = self._load_metadata()
        self.active_chat_id = config_manager.get_active_chat_id()
        
        if not self.active_chat_id or self.active_chat_id not in self.metadata:
            # If no active chat or saved ID is invalid, create a new one
            self.new_chat("Default Chat")

    def _load_metadata(self) -> dict:
        """Loads metadata mapping ID to name."""
        if os.path.exists(CHAT_META_FILE):
            try:
                with open(CHAT_META_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
        
    def _save_metadata(self):
        """Saves chat ID to name mapping."""
        with open(CHAT_META_FILE, 'w') as f:
            json.dump(self.metadata, f, indent=4)

    def new_chat(self, name: str = "New Chat"):
        """Creates a new empty chat session and sets it as active."""
        chat_id = str(uuid.uuid4())
        self.metadata[chat_id] = name
        self.active_chat_id = chat_id
        config_manager.set_active_chat_id(chat_id)
        self._save_metadata()
        
        # Create an empty file for the new chat
        with open(os.path.join(MEMORY_DIR, f"{chat_id}.json"), "w") as f:
            json.dump([], f)
            
        return chat_id

    def switch_chat(self, chat_id: str):
        """Sets an existing chat as active."""
        if chat_id in self.metadata:
            self.active_chat_id = chat_id
            config_manager.set_active_chat_id(chat_id)
        else:
            raise ValueError(f"Chat ID {chat_id} not found.")

    def delete_chat(self, chat_id: str):
        """Deletes a chat file and its metadata."""
        if chat_id in self.metadata:
            del self.metadata[chat_id]
            self._save_metadata()
            
            chat_file = os.path.join(MEMORY_DIR, f"{chat_id}.json")
            if os.path.exists(chat_file):
                os.remove(chat_file)
            
            # If deleted chat was active, create a new default chat
            if self.active_chat_id == chat_id:
                self.new_chat("New Default Chat")

    def get_all_chats(self) -> dict:
        """Returns {chat_id: chat_name} mapping."""
        return self.metadata

    def save(self, role: str, content: str):
        """Saves a message to the currently active chat history."""
        if not self.active_chat_id:
            return # Should not happen after initialization

        chat_file = os.path.join(MEMORY_DIR, f"{self.active_chat_id}.json")
        data = self.load()
        data.append({"role": role, "content": content})
        
        # Keep only the last 20 messages for context window management
        with open(chat_file, "w") as f:
            json.dump(data[-20:], f, indent=4)

    def load(self) -> list[dict]:
        """Loads the current active chat history."""
        if not self.active_chat_id:
            return []
            
        chat_file = os.path.join(MEMORY_DIR, f"{self.active_chat_id}.json")
        try:
            with open(chat_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Recreate an empty file if corrupted or missing
            with open(chat_file, "w") as f:
                json.dump([], f)
            return []

    def clear_active_chat(self):
        """Clears all messages from the current active chat."""
        if self.active_chat_id:
            chat_file = os.path.join(MEMORY_DIR, f"{self.active_chat_id}.json")
            with open(chat_file, "w") as f:
                json.dump([], f)
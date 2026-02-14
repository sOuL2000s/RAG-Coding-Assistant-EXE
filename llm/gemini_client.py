import google.genai as genai
# Import the shared config manager instance
from config_manager import config_manager 
import itertools
import time

class GeminiClient:
    def __init__(self):
        self._client = None  # NEW: Hold the client instance
        self._load_config()
        self._configure()

    def _load_config(self):
        self.api_keys = config_manager.get_keys()
        self.model_name = config_manager.get_current_model()
        
        if not self.api_keys:
            # We won't raise an error here; the main app will handle the setup prompt
            self.current_key = None
            self.keys_cycle = None
        else:
            self.keys_cycle = itertools.cycle(self.api_keys)
            self.current_key = next(self.keys_cycle)

    def _configure(self):
        """Initializes the Gemini client instance with the current key and model."""
        if self.current_key:
            # FIX: Create a Client instance using the API key
            self._client = genai.Client(api_key=self.current_key)
            # We skip retrieving the model object, as generate_content uses the model name string.
            self.model = True
        else:
            self._client = None
            self.model = None

    def switch_model(self, model_name):
        """Switches the active model and updates configuration."""
        self.model_name = model_name
        config_manager.set_current_model(model_name)
        self._configure()
        
    def switch_key(self):
        """Cycles to the next available API key."""
        if self.keys_cycle and len(self.api_keys) > 1:
            self.current_key = next(self.keys_cycle)
            self._configure()
            # In a TUI, we emit a signal instead of printing to console
            return True
        return False

    def generate(self, prompt, max_retries=3):
        if not self._client:
             return "ERROR: Gemini model not initialized. Please configure API keys."

        last_error = None # Track the last specific error
        
        for attempt in range(max_retries):
            try:
                # FIX: Use the client instance's generate_content method
                response = self._client.models.generate_content(
                    model=self.model_name, # Specify model name explicitly
                    contents=prompt
                )
                return response.text
            except Exception as e:
                last_error = e # Capture the error
                error_msg = str(e).lower()
                
                if "quota" in error_msg or "rate limit" in error_msg:
                    if self.switch_key():
                        print(f"DEBUG: Key switch successful. Retrying...")
                        continue
                    else:
                        break # Exit loop if no more keys

                # If it's another non-quota error, still try to cycle if keys are available
                if self.keys_cycle and len(self.api_keys) > 1 and attempt < max_retries - 1:
                    print(f"DEBUG: Non-quota error ({e}). Cycling key.")
                    self.switch_key()
                    continue
                
                # Exponential backoff for non-quota/non-switchable errors
                time.sleep(2 ** attempt) 
        
        # If we exit the loop due to failed retries, raise the last specific error found
        if last_error:
            # We wrap the specific error to maintain the general structure for the GUI
            raise Exception(f"Failed after retries. Last specific error: {last_error}")
        
        # Should only be reached if retries exhausted without a clear error capture (unlikely now)
        raise Exception("Failed to generate content after multiple retries.")
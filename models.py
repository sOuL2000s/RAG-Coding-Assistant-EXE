# models.py

MODEL_OPTIONS = {
    "Gemini 2.5 Flash (Default)": "gemini-2.5-flash",
    "Gemini 2.5 Flash (Preview 09-2025)": "gemini-2.5-flash-preview-09-2025",
    "Gemini 2.5 Flash (Lite)": "gemini-2.5-flash-lite",
    "Gemini 2.5 Flash (Lite Preview 09-2025)": "gemini-2.5-flash-lite-preview-09-2025",
    "Gemini 2.5 Pro": "gemini-2.5-pro",
    "Gemini 2.5 Flash (Image)": "gemini-2.5-flash-image",
    "Gemini 2.5 Flash (TTS Preview)": "gemini-2.5-flash-preview-tts",
    "Gemini 2.5 Pro (TTS Preview)": "gemini-2.5-pro-preview-tts",
    "Gemini 2.5 Flash (Native Audio Latest)": "gemini-2.5-flash-native-audio-latest",
    "Gemini 2.5 Flash (Native Audio Preview 09-2025)": "gemini-2.5-flash-native-audio-preview-09-2025",
    "Gemini 2.5 Flash (Native Audio Preview 12-2025)": "gemini-2.5-flash-native-audio-preview-12-2025",
    "Gemini 2.5 Computer Use (Preview 10-2025)": "gemini-2.5-computer-use-preview-10-2025",

    "Gemini 2.0 Flash": "gemini-2.0-flash",
    "Gemini 2.0 Flash (001)": "gemini-2.0-flash-001",
    "Gemini 2.0 Flash (Experimental Image Generation)": "gemini-2.0-flash-exp-image-generation",
    "Gemini 2.0 Flash (Lite 001)": "gemini-2.0-flash-lite-001",
    "Gemini 2.0 Flash (Lite)": "gemini-2.0-flash-lite",
    
    "Gemini 3 Pro (Preview)": "gemini-3-pro-preview",
    "Gemini 3 Flash (Preview)": "gemini-3-flash-preview",
    "Gemini 3 Pro (Image Preview)": "gemini-3-pro-image-preview",
    "Gemini Robotics ER 1.5 (Preview)": "gemini-robotics-er-1.5-preview",

    "Gemini Experimental 1206": "gemini-exp-1206",
    "Gemini Flash Latest": "gemini-flash-latest",
    "Gemini Flash Lite Latest": "gemini-flash-lite-latest",
    "Gemini Pro Latest": "gemini-pro-latest",
    "Gemini Embedding 001": "gemini-embedding-001",

    "Imagen 4.0 Generate (Preview 06-06)": "imagen-4.0-generate-preview-06-06",
    "Imagen 4.0 Ultra Generate (Preview 06-06)": "imagen-4.0-ultra-generate-preview-06-06",
    "Imagen 4.0 Generate (001)": "imagen-4.0-generate-001",
    "Imagen 4.0 Ultra Generate (001)": "imagen-4.0-ultra-generate-001",
    "Imagen 4.0 Fast Generate (001)": "imagen-4.0-fast-generate-001",

    "Gemma 3 (1B-IT)": "gemma-3-1b-it",
    "Gemma 3 (4B-IT)": "gemma-3-4b-it",
    "Gemma 3 (12B-IT)": "gemma-3-12b-it",
    "Gemma 3 (27B-IT)": "gemma-3-27b-it",
    "Gemma 3N (E4B-IT)": "gemma-3n-e4b-it",
    "Gemma 3N (E2B-IT)": "gemma-3n-e2b-it",
    
    "Nano Banana Pro (Preview)": "nano-banana-pro-preview",
    "Deep Research Pro (Preview 12-2025)": "deep-research-pro-preview-12-2025",
    "AQA": "aqa",
    "Veo 2.0 Generate (001)": "veo-2.0-generate-001",
    "Veo 3.0 Generate (001)": "veo-3.0-generate-001",
    "Veo 3.0 Fast Generate (001)": "veo-3.0-fast-generate-001",
    "Veo 3.1 Generate (Preview)": "veo-3.1-generate-preview",
    "Veo 3.1 Fast Generate (Preview)": "veo-3.1-fast-generate-preview",
}

DEFAULT_MODEL = "gemini-2.5-flash-preview-09-2025"
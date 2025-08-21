import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading .env file
    pass

# Get API key from environment variable only (no default)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Data directory
DATA_DIR = Path("my_notes")
DATA_DIR.mkdir(exist_ok=True)

# Notes file path
NOTES_FILE = DATA_DIR / "notes.json"
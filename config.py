import os
from pathlib import Path

# Get API key from environment variable or fallback to default (for testing only)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyAFSUjAJ3lSeuQeMt_YQt-wvIpFjDvN6sw')

# Data directory
DATA_DIR = Path("my_notes")
DATA_DIR.mkdir(exist_ok=True)

# Notes file path
NOTES_FILE = DATA_DIR / "notes.json"
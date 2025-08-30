# 🏢 THE MANAGER'S OFFICE - Configuration Center
# This file is like the "settings manager" for your entire app

import os                    # 🖥️ Talks to your computer's operating system
from pathlib import Path     # 📁 Handles file paths in a smart way

# 🔐 SECRET LOADER - Gets your API key from the .env file (your safe)
try:
    from dotenv import load_dotenv  # 🔑 The key-finder tool
    load_dotenv()                   # 🔓 Actually opens the safe and loads secrets
except ImportError:
    # 🤷 If the tool isn't installed, that's okay, we'll survive
    pass

# 🎫 GET THE GOLDEN TICKET - Your AI access pass
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # 🎪 Gets your circus ticket to the AI show

# 🏠 HOME BASE - Where all your precious thoughts live
DATA_DIR = Path("my_notes")      # 📂 Creates a cozy folder called "my_notes"
DATA_DIR.mkdir(exist_ok=True)    # 🏗️ Builds the folder if it doesn't exist yet

# 📝 THE MAIN BOOK - Your digital diary location
NOTES_FILE = DATA_DIR / "notes.json"  # 📖 Points to your main journal file
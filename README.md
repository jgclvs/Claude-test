# 📝 Smart Notes AI

A powerful note-taking application with AI assistance, featuring both a command-line interface and a web interface.

## 🚀 Features

- **Note Management**: Create, read, update, and delete notes
- **Tagging System**: Organize notes with tags for better categorization
- **Powerful Search**: Search through titles, content, and tags
- **AI Integration**: Ask questions about your notes using Google's Gemini API
- **Semantic Search**: Find relevant notes using AI-powered similarity matching
- **Web Interface**: Beautiful Streamlit-based web UI
- **CLI Interface**: Traditional command-line interface for power users
- **Secure Configuration**: Environment variable support for API keys

## 🛠️ Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Gemini API key (optional but recommended):
   ```bash
   # On Windows (Command Prompt)
   set GEMINI_API_KEY=your_api_key_here
   
   # On Windows (PowerShell)
   $env:GEMINI_API_KEY="your_api_key_here"
   
   # On macOS/Linux
   export GEMINI_API_KEY=your_api_key_here
   ```

## 🖥️ Usage

### Web Interface (Recommended)

Run the Streamlit web application:
```bash
streamlit run streamlit_app.py
```

### Command-Line Interface

```bash
# Add a new note
python notes_enhanced.py add

# List all notes
python notes_enhanced.py list

# Filter notes by tag
python notes_enhanced.py list --tag "important"

# Search notes
python notes_enhanced.py search "python"

# Update a note
python notes_enhanced.py update note_12345678 --title "New Title"

# Delete a note
python notes_enhanced.py delete note_12345678

# Ask AI about your notes
python notes_enhanced.py ask "What did I learn about Python?"

# Ask AI using only relevant notes for context
python notes_enhanced.py ask --relevant-only "What did I learn about Python?"
```

## 📁 Project Structure

- `notes_enhanced.py`: Main CLI application
- `streamlit_app.py`: Web interface using Streamlit
- `config.py`: Configuration management
- `requirements.txt`: Python dependencies
- `my_notes/`: Directory containing your notes in JSON format

## 🔒 Security

For production use, always set your Gemini API key as an environment variable rather than using the hardcoded test key.

## 🤖 AI Features

The AI integration uses Google's Gemini API to:
- Answer questions about your notes
- Find semantically relevant notes
- Provide structured responses with confidence scores
- Suggest related topics and actions

## 📝 Note Format

Notes are stored in JSON format with the following structure:
```json
{
  "note_unique_id": {
    "title": "Note Title",
    "content": "Note content goes here",
    "created": "2023-01-01T00:00:00.000000",
    "updated": "2023-01-01T00:00:00.000000",
    "tags": ["tag1", "tag2"]
  }
}
```
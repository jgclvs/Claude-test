#!/usr/bin/env python3
"""
Smart Notes CLI - A simple note-taking tool with AI assistance
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

class SmartNotes:
    def __init__(self):
        # Create notes directory if it doesn't exist
        self.notes_dir = Path("my_notes")
        self.notes_dir.mkdir(exist_ok=True)
        self.notes_file = self.notes_dir / "notes.json"
        self.notes = self.load_notes()
    
    def load_notes(self):
        """Load notes from JSON file, create empty dict if file doesn't exist"""
        if self.notes_file.exists():
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def save_notes(self):
        """Save notes to JSON file"""
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, indent=2, ensure_ascii=False)
    
    def add_note(self, title, content):
        """Add a new note with timestamp"""
        timestamp = datetime.now().isoformat()
        note_id = f"note_{len(self.notes) + 1}"
        
        self.notes[note_id] = {
            "title": title,
            "content": content,
            "created": timestamp
        }
        
        self.save_notes()
        print(f"✅ Note '{title}' saved with ID: {note_id}")
    
    def list_notes(self):
        """Display all notes"""
        if not self.notes:
            print("📝 No notes found. Add some with: python notes.py add")
            return
        
        print(f"📚 Found {len(self.notes)} notes:")
        print("-" * 50)
        
        for note_id, note in self.notes.items():
            created = datetime.fromisoformat(note["created"]).strftime("%Y-%m-%d %H:%M")
            print(f"ID: {note_id}")
            print(f"Title: {note['title']}")
            print(f"Created: {created}")
            print(f"Content: {note['content'][:100]}{'...' if len(note['content']) > 100 else ''}")
            print("-" * 50)
    
    def search_notes(self, query):
        """Simple search through note titles and content"""
        matches = []
        query_lower = query.lower()
        
        for note_id, note in self.notes.items():
            if (query_lower in note['title'].lower() or 
                query_lower in note['content'].lower()):
                matches.append((note_id, note))                git --version                git --version                git --version                git --version
        
        if matches:
            print(f"🔍 Found {len(matches)} matches for '{query}':")
            print("-" * 50)
            for note_id, note in matches:
                print(f"ID: {note_id} - {note['title']}")
                print(f"Content: {note['content'][:150]}{'...' if len(note['content']) > 150 else ''}")
                print("-" * 50)
        else:
            print(f"❌ No matches found for '{query}'")
    
    def get_all_content(self):
        """Get all notes content for AI analysis"""
        if not self.notes:
            return "No notes available."
        
        content = "My Notes Collection:\n\n"
        for note_id, note in self.notes.items():
            content += f"Title: {note['title']}\n"
            content += f"Content: {note['content']}\n"
            content += f"Created: {note['created']}\n\n"
        
        return content

def main():
    notes = SmartNotes()
    
    if len(sys.argv) < 2:
        print("📝 Smart Notes CLI")
        print("Usage:")
        print("  python notes.py add                    # Add a new note")
        print("  python notes.py list                   # List all notes")
        print("  python notes.py search <query>         # Search notes")
        print("  python notes.py ask <question>         # Ask AI about your notes")
        return
    
    command = sys.argv[1].lower()
    
    if command == "add":
        title = input("Note title: ").strip()
        if not title:
            print("❌ Title cannot be empty")
            return
        
        print("Enter note content (press Ctrl+D or Ctrl+Z when done):")
        try:
            content_lines = []
            while True:
                try:
                    line = input()
                    content_lines.append(line)
                except EOFError:
                    break
            content = '\n'.join(content_lines)
        except KeyboardInterrupt:
            print("\n❌ Note creation cancelled")
            return
        
        if content.strip():
            notes.add_note(title, content)
        else:
            print("❌ Content cannot be empty")
    
    elif command == "list":
        notes.list_notes()
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Please provide a search query")
            return
        query = ' '.join(sys.argv[2:])
        notes.search_notes(query)
    
    elif command == "ask":
        if len(sys.argv) < 3:
            print("❌ Please provide a question")
            return
        
        question = ' '.join(sys.argv[2:])
        all_content = notes.get_all_content()
        
        print(f"🤖 AI Analysis of your notes for: '{question}'")
        print("📚 Context: Your notes collection")
        print(f"❓ Question: {question}")
        print("\n💡 To get AI answers, you'll need to add API integration")
        print("   (We'll cover this in the next step!)")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
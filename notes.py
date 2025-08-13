#!/usr/bin/env python3
"""
Smart Notes CLI - A simple note-taking tool with AI assistance
"""

import json
import os
import sys
import requests
import numpy as np
from datetime import datetime
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

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
                matches.append((note_id, note))
        
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

    def get_embedding(self, text, api_key):
        """Get embedding vector for text using Gemini"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
            payload = {
                "model": "models/text-embedding-004",
                "content": {
                    "parts": [{"text": text}]
                }
            }
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json()['embedding']['values']
            return None
        except Exception as e:
            print(f"Embedding error: {e}")
            return None
    
    def find_relevant_notes(self, question, api_key, top_k=3):
        """Find most relevant notes using semantic similarity"""
        if not self.notes:
            return []
        
        print("🔍 Finding relevant notes...")
        
        # Get question embedding
        question_embedding = self.get_embedding(question, api_key)
        if not question_embedding:
            # Fallback to all notes if embedding fails
            return list(self.notes.items())
        
        similarities = []
        for note_id, note in self.notes.items():
            # Combine title and content for better matching
            note_text = f"{note['title']} {note['content']}"
            note_embedding = self.get_embedding(note_text, api_key)
            
            if note_embedding:
                # Calculate cosine similarity
                similarity = cosine_similarity(
                    [question_embedding], 
                    [note_embedding]
                )[0][0]
                similarities.append((note_id, note, similarity))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[2], reverse=True)
        relevant_notes = [(note_id, note) for note_id, note, sim in similarities[:top_k]]
        
        print(f"📋 Found {len(relevant_notes)} most relevant notes")
        return relevant_notes
    
    def ask_ai(self, question):
        """Ask AI about your notes using Gemini API"""
        # Hardcoded API key for testing - we'll fix this later
        api_key = "AIzaSyAFSUjAJ3lSeuQeMt_YQt-wvIpFjDvN6sw"
        
        notes_context = self.get_all_content()
        prompt = f"""Based on these notes, analyze the question and respond with JSON in this exact format:
{{
  "answer": "your detailed answer here",
  "confidence": 0.85,
  "sources_used": ["note_1", "note_2"],
  "suggested_actions": ["action1", "action2"],
  "related_topics": ["topic1", "topic2"]
}}

Notes: {notes_context}
Question: {question}

Respond ONLY with valid JSON, no other text."""

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            headers = {"Content-Type": "application/json"}
            print(f"🤖 Asking AI about: '{question}'")
            print("⏳ Thinking...")
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    answer = result['candidates'][0]['content']['parts'][0]['text']
                    # Try to parse as JSON first
                    try:
                        ai_response = json.loads(answer)
                        print("✨ Structured Response:")
                        print("-" * 50)
                        print(f"Answer: {ai_response['answer']}")
                        print(f"Confidence: {ai_response['confidence']}")
                        print(f"Sources: {', '.join(ai_response['sources_used'])}")
                        print(f"Related: {', '.join(ai_response['related_topics'])}")
                        print("-" * 50)
                    except Exception:
                        # Fallback to regular text display
                        print("✨ AI Response:")
                        print("-" * 50)
                        print(answer)
                        print("-" * 50)
                else:
                    print("❌ No response from AI")
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

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
        notes.ask_ai(question)
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()  
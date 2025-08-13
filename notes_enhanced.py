#!/usr/bin/env python3
"""
Smart Notes CLI - A powerful note-taking tool with AI assistance
"""

import json
import os
import sys
import requests
import numpy as np
from datetime import datetime
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
import argparse
import hashlib
import uuid

from config import GEMINI_API_KEY, NOTES_FILE


class SmartNotes:
    def __init__(self):
        self.notes_file = NOTES_FILE
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
    
    def add_note(self, title, content, tags=None):
        """Add a new note with timestamp and tags"""
        timestamp = datetime.now().isoformat()
        # Generate unique ID based on content to avoid duplicates
        note_id = f"note_{uuid.uuid4().hex[:8]}"
        
        self.notes[note_id] = {
            "title": title,
            "content": content,
            "created": timestamp,
            "updated": timestamp,
            "tags": tags or []
        }
        
        self.save_notes()
        print(f"✅ Note '{title}' saved with ID: {note_id}")
        return note_id
    
    def update_note(self, note_id, title=None, content=None, tags=None):
        """Update an existing note"""
        if note_id not in self.notes:
            print(f"❌ Note with ID {note_id} not found")
            return False
            
        if title is not None:
            self.notes[note_id]["title"] = title
        if content is not None:
            self.notes[note_id]["content"] = content
        if tags is not None:
            self.notes[note_id]["tags"] = tags
            
        self.notes[note_id]["updated"] = datetime.now().isoformat()
        self.save_notes()
        print(f"✅ Note '{self.notes[note_id]['title']}' updated")
        return True
    
    def delete_note(self, note_id):
        """Delete a note by ID"""
        if note_id in self.notes:
            title = self.notes[note_id]["title"]
            del self.notes[note_id]
            self.save_notes()
            print(f"✅ Note '{title}' deleted")
            return True
        else:
            print(f"❌ Note with ID {note_id} not found")
            return False
    
    def list_notes(self, tag_filter=None):
        """Display all notes, optionally filtered by tag"""
        if not self.notes:
            print("📝 No notes found. Add some with: python notes.py add")
            return
        
        filtered_notes = self.notes.items()
        if tag_filter:
            filtered_notes = [(id, note) for id, note in self.notes.items() 
                            if tag_filter.lower() in [t.lower() for t in note.get("tags", [])]]
            print(f"📚 Found {len(filtered_notes)} notes with tag '{tag_filter}':")
        else:
            print(f"📚 Found {len(self.notes)} notes:")
        print("-" * 50)
        
        for note_id, note in filtered_notes:
            created = datetime.fromisoformat(note["created"]).strftime("%Y-%m-%d %H:%M")
            updated = datetime.fromisoformat(note["updated"]).strftime("%Y-%m-%d %H:%M")
            tags = ", ".join(note.get("tags", []))
            
            print(f"ID: {note_id}")
            print(f"Title: {note['title']}")
            print(f"Created: {created}")
            print(f"Updated: {updated}")
            if tags:
                print(f"Tags: {tags}")
            print(f"Content: {note['content'][:100]}{'...' if len(note['content']) > 100 else ''}")
            print("-" * 50)
    
    def search_notes(self, query):
        """Simple search through note titles and content"""
        matches = []
        query_lower = query.lower()
        
        for note_id, note in self.notes.items():
            if (query_lower in note['title'].lower() or 
                query_lower in note['content'].lower() or
                any(query_lower in tag.lower() for tag in note.get("tags", []))):
                matches.append((note_id, note))
        
        if matches:
            print(f"🔍 Found {len(matches)} matches for '{query}':")
            print("-" * 50)
            for note_id, note in matches:
                print(f"ID: {note_id} - {note['title']}")
                tags = ", ".join(note.get("tags", []))
                if tags:
                    print(f"Tags: {tags}")
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
            content += f"ID: {note_id}\n"
            content += f"Title: {note['title']}\n"
            if note.get("tags"):
                content += f"Tags: {', '.join(note['tags'])}\n"
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
            # Combine title, content, and tags for better matching
            note_text = f"{note['title']} {note['content']} {' '.join(note.get('tags', []))}"
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
    
    def ask_ai(self, question, use_relevant_only=False):
        """Ask AI about your notes using Gemini API"""
        api_key = GEMINI_API_KEY
        
        if use_relevant_only:
            # Find only relevant notes for the question
            relevant_notes = self.find_relevant_notes(question, api_key)
            if relevant_notes:
                notes_context = "Relevant Notes:\n\n"
                for note_id, note in relevant_notes:
                    notes_context += f"ID: {note_id}\n"
                    notes_context += f"Title: {note['title']}\n"
                    if note.get("tags"):
                        notes_context += f"Tags: {', '.join(note['tags'])}\n"
                    notes_context += f"Content: {note['content']}\n\n"
            else:
                notes_context = "No relevant notes found."
        else:
            # Use all notes
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
                        print(f"Confidence: {ai_response['confidence']:.2%}")
                        print(f"Sources: {', '.join(ai_response['sources_used'])}")
                        if ai_response['suggested_actions']:
                            print(f"Suggestions: {', '.join(ai_response['suggested_actions'])}")
                        if ai_response['related_topics']:
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
    
    parser = argparse.ArgumentParser(description="Smart Notes CLI - A powerful note-taking tool with AI assistance")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new note')
    add_parser.add_argument('--title', type=str, help='Note title')
    add_parser.add_argument('--content', type=str, help='Note content')
    add_parser.add_argument('--tags', type=str, nargs='*', help='Note tags')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all notes')
    list_parser.add_argument('--tag', type=str, help='Filter notes by tag')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search notes')
    search_parser.add_argument('query', nargs='*', help='Search query')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update an existing note')
    update_parser.add_argument('id', type=str, help='Note ID to update')
    update_parser.add_argument('--title', type=str, help='New title')
    update_parser.add_argument('--content', type=str, help='New content')
    update_parser.add_argument('--tags', type=str, nargs='*', help='New tags')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a note')
    delete_parser.add_argument('id', type=str, help='Note ID to delete')
    
    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask AI about your notes')
    ask_parser.add_argument('question', nargs='*', help='Question to ask')
    ask_parser.add_argument('--relevant-only', action='store_true', help='Use only relevant notes for context')
    
    args = parser.parse_args()
    
    if not args.command:
        print("📝 Smart Notes CLI")
        print("Usage:")
        print("  python notes.py add [--title TITLE] [--content CONTENT] [--tags TAG1 TAG2 ...]")
        print("  python notes.py list [--tag TAG]")
        print("  python notes.py search QUERY")
        print("  python notes.py update ID [--title TITLE] [--content CONTENT] [--tags TAG1 TAG2 ...]")
        print("  python notes.py delete ID")
        print("  python notes.py ask [--relevant-only] QUESTION")
        return
    
    if args.command == "add":
        title = args.title or input("Note title: ").strip()
        if not title:
            print("❌ Title cannot be empty")
            return
        
        if args.content:
            content = args.content
        else:
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
            note_id = notes.add_note(title, content, args.tags)
        else:
            print("❌ Content cannot be empty")
    
    elif args.command == "list":
        notes.list_notes(args.tag)
    
    elif args.command == "search":
        if not args.query:
            print("❌ Please provide a search query")
            return
        query = ' '.join(args.query)
        notes.search_notes(query)
    
    elif args.command == "update":
        # For update, we'll prompt for missing fields
        title = args.title
        content = args.content
        tags = args.tags
        
        if title is None and content is None and tags is None:
            print("❌ Please provide at least one field to update (--title, --content, or --tags)")
            return
            
        notes.update_note(args.id, title, content, tags)
    
    elif args.command == "delete":
        notes.delete_note(args.id)
    
    elif args.command == "ask":
        if not args.question:
            print("❌ Please provide a question")
            return
            
        question = ' '.join(args.question)
        notes.ask_ai(question, args.relevant_only)
    
    else:
        print(f"❌ Unknown command: {args.command}")

if __name__ == "__main__":
    main()
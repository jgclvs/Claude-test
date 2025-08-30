#!/usr/bin/env python3
"""
🎆 THE MAIN KITCHEN - Smart Notes Enhanced 🎆
This is where ALL the cooking happens for your self-exploration app!
Think of this as the "CHEF" that prepares all your personal insights
"""

# 📦 IMPORT SECTION - Getting all our cooking tools ready
import json                    # 📋 For reading/writing data files (like recipes)
import os                     # 🖥️ For talking to your computer
import sys                    # 🔧 System tools
import requests               # 🌍 For talking to the internet (AI API)
from datetime import datetime # 📅 For timestamps on your thoughts
from pathlib import Path      # 📁 Smart file path handling
import uuid                   # 🏗️ For creating unique IDs
from collections import defaultdict # 🗃️ For counting and organizing data

# 🏢 IMPORTING FROM THE MANAGER'S OFFICE
from config import GEMINI_API_KEY, NOTES_FILE


# 👨‍🍳 THE MASTER CHEF CLASS - Where all the magic happens!
class SmartNotesEnhanced:
    # 🏗️ THE CHEF'S INITIALIZATION - Setting up the kitchen
    def __init__(self):
        # 📍 Where do we keep the recipe book? (notes file location)
        self.notes_file = NOTES_FILE
        # 📚 Load all existing recipes (your previous thoughts)
        self.notes = self.load_notes()
    
    # 📖 THE LIBRARIAN - Reads your existing thoughts from storage
    def load_notes(self):
        """Load notes from JSON file"""
        if self.notes_file.exists():  # 🔍 Does the file exist?
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)  # 📖 Read and convert JSON to Python
            except (json.JSONDecodeError, FileNotFoundError):
                return {}  # 🤷 If file is corrupted, start fresh
        return {}  # 📝 No file yet? Start with empty notebook
    
    # 💾 THE ARCHIVIST - Saves your thoughts to permanent storage
    def save_notes(self):
        """Save notes to JSON file"""
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, indent=2, ensure_ascii=False)  # 📝 Write beautifully formatted
    
    # ✍️ THE SCRIBE - Your main "ADD NOTE" department (HR Department!)
    def add_note(self, title, content, tags=None, note_type="general", mood=None, energy_level=None):
        """Add enhanced note with self-exploration metadata"""
        # 🕐 Timestamp = When did you have this thought?
        timestamp = datetime.now().isoformat()
        # 🎫 Generate unique ID (like a library catalog number)
        note_id = f"note_{uuid.uuid4().hex[:8]}"
        
        # 🏗️ BUILD THE NOTE STRUCTURE - Like filling out a detailed form
        self.notes[note_id] = {
            "title": title,                    # 🏷️ What's this about?
            "content": content,                # 💭 Your actual thoughts
            "created": timestamp,             # 🕐 When you wrote it
            "updated": timestamp,             # 🔄 Last time you changed it
            "tags": tags or [],               # 🏷️ Categories/labels
            "type": note_type,                # 📝 What kind of note (journal, goal, etc)
            "metadata": {                     # 📊 EXTRA JUICY DATA for self-exploration
                "mood": mood,                  # 😊 How you felt (1-10)
                "energy_level": energy_level,  # ⚡ Your energy (1-10)
                "word_count": len(content.split()), # 📏 How much you wrote
                "created_date_only": timestamp[:10],    # 📅 Just the date
                "created_hour": int(timestamp[11:13])   # 🕐 What hour you wrote it
            }
        }
        
        # 💾 SAVE TO DISK - Don't lose your precious thoughts!
        self.save_notes()
        print(f"✅ {note_type.title()} '{title}' saved with ID: {note_id}")
        return note_id
    
    def quick_journal(self):
        """Quick journaling interface"""
        print("📝 Quick Journal Entry")
        print("Share what's on your mind today...\n")
        
        title = input("🏷️  Title (or press Enter for today's date): ").strip()
        if not title:
            title = f"Journal - {datetime.now().strftime('%Y-%m-%d')}"
        
        print("\n💭 Content (press Ctrl+C when done):")
        content_lines = []
        try:
            while True:
                line = input()
                content_lines.append(line)
        except KeyboardInterrupt:
            print("\n")
        
        content = '\n'.join(content_lines).strip()
        if not content:
            print("❌ Content cannot be empty")
            return None
        
        # Get mood and energy
        try:
            mood_input = input("😊 Mood (1-10, or press Enter to skip): ").strip()
            mood = int(mood_input) if mood_input else None
        except ValueError:
            mood = None
        
        try:
            energy_input = input("⚡ Energy level (1-10, or press Enter to skip): ").strip()
            energy_level = int(energy_input) if energy_input else None
        except ValueError:
            energy_level = None
        
        # Auto-generate tags
        tags = self._auto_generate_tags(content)
        
        note_id = self.add_note(
            title=title,
            content=content,
            tags=tags,
            note_type="journal",
            mood=mood,
            energy_level=energy_level
        )
        
        print(f"\n🎉 Journal entry saved! Auto-tags: {', '.join(tags) if tags else 'none'}")
        return note_id
    
    def _auto_generate_tags(self, content):
        """Auto-generate tags based on content"""
        content_lower = content.lower()
        tags = []
        
        # Emotion-based tags
        if any(word in content_lower for word in ['happy', 'joy', 'excited', 'great', 'amazing']):
            tags.append('positive')
        if any(word in content_lower for word in ['sad', 'upset', 'frustrated', 'angry', 'stressed']):
            tags.append('challenging')
        if any(word in content_lower for word in ['grateful', 'thankful', 'appreciate']):
            tags.append('gratitude')
        
        # Activity-based tags
        if any(word in content_lower for word in ['work', 'job', 'meeting', 'project']):
            tags.append('work')
        if any(word in content_lower for word in ['family', 'friend', 'relationship']):
            tags.append('relationships')
        if any(word in content_lower for word in ['learn', 'study', 'read', 'course']):
            tags.append('learning')
        if any(word in content_lower for word in ['goal', 'plan', 'future', 'dream']):
            tags.append('goals')
        
        return tags[:3]
    
    # 🆕 NEW FEATURE: THE MOOD DETECTIVE - Tracks your emotional patterns over time
    def track_mood_trends(self, days_back=30):
        """🧠 EMOTION ANALYTICS DEPARTMENT - Find your mood patterns!"""
        # 📊 Collect all mood data from recent entries
        mood_data = []
        for note_id, note in self.notes.items():
            metadata = note.get("metadata", {})
            if metadata.get("mood") and isinstance(metadata["mood"], (int, float)):
                mood_data.append({
                    "date": metadata.get("created_date_only"),
                    "hour": metadata.get("created_hour", 12), 
                    "mood": metadata["mood"],
                    "title": note["title"]
                })
        
        if not mood_data:
            return {"message": "No mood data available yet. Start journaling with mood ratings!"}
        
        # 🧮 Calculate trends (this is where the magic happens!)
        moods = [entry["mood"] for entry in mood_data]
        avg_mood = sum(moods) / len(moods)
        
        # 📈 Find patterns by time of day
        morning_moods = [entry["mood"] for entry in mood_data if entry["hour"] < 12]
        evening_moods = [entry["mood"] for entry in mood_data if entry["hour"] >= 18]
        
        return {
            "average_mood": round(avg_mood, 1),
            "total_entries": len(mood_data),
            "best_mood": max(moods),
            "lowest_mood": min(moods),
            "morning_average": round(sum(morning_moods)/len(morning_moods), 1) if morning_moods else None,
            "evening_average": round(sum(evening_moods)/len(evening_moods), 1) if evening_moods else None,
            "recent_entries": mood_data[-5:]  # Last 5 entries
        }
    
    def get_statistics(self):
        """Get detailed statistics"""
        if not self.notes:
            print("📊 No data available")
            return
        
        total_notes = len(self.notes)
        total_words = sum(note.get("metadata", {}).get("word_count", 0) for note in self.notes.values())
        
        # Notes by type
        types = defaultdict(int)
        for note in self.notes.values():
            types[note.get("type", "general")] += 1
        
        # Mood analysis
        moods = []
        energy_levels = []
        for note in self.notes.values():
            metadata = note.get("metadata", {})
            if metadata.get("mood") and isinstance(metadata["mood"], (int, float)):
                moods.append(metadata["mood"])
            if metadata.get("energy_level") and isinstance(metadata["energy_level"], (int, float)):
                energy_levels.append(metadata["energy_level"])
        
        print("📊 YOUR STATISTICS")
        print("=" * 40)
        print(f"Total entries: {total_notes}")
        print(f"Total words: {total_words:,}")
        print(f"Avg words per entry: {total_words // total_notes if total_notes > 0 else 0}")
        
        print("\n📝 By type:")
        for note_type, count in sorted(types.items()):
            print(f"  {note_type}: {count}")
        
        if moods:
            print(f"\n😊 Average mood: {sum(moods) / len(moods):.1f}/10")
        if energy_levels:
            print(f"⚡ Average energy: {sum(energy_levels) / len(energy_levels):.1f}/10")
        
        print("=" * 40)
    
    def analyze_patterns(self):
        """AI-powered pattern analysis"""
        if not self.notes:
            print("📈 No notes for analysis")
            return None
        
        api_key = GEMINI_API_KEY
        if not api_key:
            print("⚠️  API key required for pattern analysis")
            return None
        
        print("🔍 Analyzing your personal patterns...")
        
        # Prepare context
        context = self._prepare_analysis_context()
        
        prompt = f"""You are a personal development coach. Analyze these personal notes and provide insights in JSON format:

{{
  "emotional_patterns": {{
    "dominant_emotions": ["emotion1", "emotion2"],
    "trends": "description of emotional trends"
  }},
  "behavioral_patterns": {{
    "recurring_themes": ["theme1", "theme2"],
    "growth_indicators": ["indicator1", "indicator2"]
  }},
  "recommendations": {{
    "immediate_actions": ["action1", "action2"],
    "reflection_questions": ["question1", "question2"]
  }},
  "summary": "2-3 sentence summary of personal development journey"
}}

Notes data:
{context}

Provide actionable insights for personal growth."""
        
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            print("⏳ Processing...")
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    answer = result['candidates'][0]['content']['parts'][0]['text']
                    try:
                        analysis = json.loads(answer)
                        self._display_analysis(analysis)
                        return analysis
                    except:
                        print("🧠 AI Analysis:")
                        print("-" * 50)
                        print(answer)
                        print("-" * 50)
                        return answer
            else:
                print(f"❌ API Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return None
    
    def _prepare_analysis_context(self):
        """Prepare data for AI analysis"""
        context = f"Personal Notes Analysis (Total: {len(self.notes)} entries)\n\n"
        
        # Sort by date
        sorted_notes = sorted(self.notes.items(), key=lambda x: x[1]['created'])
        
        for note_id, note in sorted_notes:
            context += f"Date: {note['created'][:10]}\n"
            context += f"Type: {note.get('type', 'general')}\n"
            context += f"Title: {note['title']}\n"
            
            metadata = note.get('metadata', {})
            if metadata.get('mood'):
                context += f"Mood: {metadata['mood']}/10\n"
            if metadata.get('energy_level'):
                context += f"Energy: {metadata['energy_level']}/10\n"
            
            if note.get('tags'):
                context += f"Tags: {', '.join(note['tags'])}\n"
            
            # Limit content for API efficiency
            content = note['content'][:500]
            if len(note['content']) > 500:
                content += "..."
            context += f"Content: {content}\n"
            context += "-" * 30 + "\n"
        
        return context
    
    def _display_analysis(self, analysis):
        """Display analysis results beautifully"""
        print("\n" + "=" * 60)
        print("🌟 YOUR PERSONAL INSIGHTS REPORT 🌟")
        print("=" * 60)
        
        if analysis.get('summary'):
            print(f"📝 SUMMARY: {analysis['summary']}\n")
        
        if 'emotional_patterns' in analysis:
            ep = analysis['emotional_patterns']
            print("💭 EMOTIONAL PATTERNS")
            if ep.get('dominant_emotions'):
                print(f"   🎭 Key emotions: {', '.join(ep['dominant_emotions'])}")
            if ep.get('trends'):
                print(f"   📈 Trends: {ep['trends']}")
            print()
        
        if 'behavioral_patterns' in analysis:
            bp = analysis['behavioral_patterns']
            print("🎨 BEHAVIORAL PATTERNS")
            if bp.get('recurring_themes'):
                print(f"   🔄 Themes: {', '.join(bp['recurring_themes'])}")
            if bp.get('growth_indicators'):
                print(f"   🌱 Growth signs: {', '.join(bp['growth_indicators'])}")
            print()
        
        if 'recommendations' in analysis:
            rec = analysis['recommendations']
            print("🎯 RECOMMENDATIONS")
            if rec.get('immediate_actions'):
                print("   🏃 Actions:")
                for action in rec['immediate_actions']:
                    print(f"     • {action}")
            if rec.get('reflection_questions'):
                print("   🤔 Questions:")
                for question in rec['reflection_questions']:
                    print(f"     • {question}")
            print()
        
        print("=" * 60)
        print("🌟 Use these insights for your growth journey! 🌟")
        print("=" * 60 + "\n")
    
    def list_notes(self, note_type=None):
        """List notes with enhanced display"""
        if not self.notes:
            print("📝 No notes found")
            return
        
        filtered_notes = list(self.notes.items())
        if note_type:
            filtered_notes = [(id, note) for id, note in filtered_notes 
                            if note.get("type", "general").lower() == note_type.lower()]
        
        print(f"📚 Found {len(filtered_notes)} notes:")
        print("-" * 50)
        
        for note_id, note in filtered_notes:
            created = datetime.fromisoformat(note["created"]).strftime("%Y-%m-%d %H:%M")
            note_type_display = note.get("type", "general")
            
            print(f"ID: {note_id}")
            print(f"Title: {note['title']}")
            print(f"Type: {note_type_display}")
            print(f"Created: {created}")
            
            if note.get("tags"):
                print(f"Tags: {', '.join(note['tags'])}")
            
            metadata = note.get("metadata", {})
            if metadata.get("mood"):
                print(f"Mood: {metadata['mood']}/10")
            if metadata.get("energy_level"):
                print(f"Energy: {metadata['energy_level']}/10")
            
            print(f"Content: {note['content'][:100]}{'...' if len(note['content']) > 100 else ''}")
            print("-" * 50)


def main():
    """Main demo function"""
    print("🌟 SMART NOTES ENHANCED - SELF-EXPLORATION PLATFORM")
    print("=" * 60)
    
    notes = SmartNotesEnhanced()
    
    # Add sample data
    sample_notes = [
        {
            "title": "Morning Motivation",
            "content": "Started the day with meditation and feel really energized. My morning routine is helping me stay focused and positive. Grateful for this peaceful start.",
            "type": "journal",
            "mood": 8,
            "energy": 9,
            "tags": ["morning", "routine"]
        },
        {
            "title": "Work Stress Challenge",
            "content": "Dealing with a difficult project deadline. Feeling overwhelmed but trying to break tasks into smaller pieces. Need to communicate better with my team.",
            "type": "reflection",
            "mood": 4,
            "energy": 3,
            "tags": ["work", "stress"]
        },
        {
            "title": "Growth Mindset Principle",
            "content": "I believe challenges are opportunities to learn. When facing difficulties, I try to see them as chances to grow rather than obstacles.",
            "type": "principle",
            "mood": 7,
            "energy": 7,
            "tags": ["mindset", "growth"]
        }
    ]
    
    print("📝 Adding sample entries...")
    for entry in sample_notes:
        notes.add_note(
            title=entry["title"],
            content=entry["content"],
            note_type=entry["type"],
            mood=entry["mood"],
            energy_level=entry["energy"],
            tags=entry["tags"]
        )
    
    print("\n📊 Your Statistics:")
    notes.get_statistics()
    
    print("\n📋 Your Notes:")
    notes.list_notes()
    
    print("\n🧠 AI Pattern Analysis:")
    analysis = notes.analyze_patterns()
    
    print("\n💡 Try these features:")
    print("- notes.quick_journal() for daily entries")
    print("- notes.analyze_patterns() for AI insights")
    print("- notes.get_statistics() for progress tracking")
    print("- notes.list_notes(note_type='journal') for filtering")


if __name__ == "__main__":
    main()
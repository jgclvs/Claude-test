#!/usr/bin/env python3
"""
Smart Notes Enhanced Demo
Demonstration of self-exploration and pattern analysis features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_notes_enhanced import SmartNotesEnhanced


def demo_self_exploration():
    """Demonstrate the self-exploration features"""
    print("🎯 SMART NOTES ENHANCED - SELF-EXPLORATION DEMO")
    print("=" * 60)
    
    # Initialize the enhanced notes system
    notes = SmartNotesEnhanced()
    
    print("\n📝 SAMPLE SELF-EXPLORATION ENTRIES")
    print("-" * 40)
    
    # Add some sample entries for demonstration
    sample_entries = [
        {
            "title": "Morning Reflection - Feeling Energized",
            "content": "Woke up feeling really motivated today. I've been consistent with my morning routine for the past week and it's paying off. The 20-minute meditation and journal writing is helping me start each day with clarity. I'm grateful for having this peaceful morning time before the day gets busy.",
            "tags": ["morning", "routine", "motivation"],
            "note_type": "journal",
            "mood": 8,
            "energy_level": 9
        },
        {
            "title": "Work Project Stress",
            "content": "Feeling overwhelmed with the new project deadlines. The scope keeps changing and I'm worried about delivering quality work on time. Need to communicate better with the team about realistic timelines. Maybe I should break down the tasks into smaller, manageable pieces.",
            "tags": ["work", "stress", "planning"],
            "note_type": "reflection",
            "mood": 4,
            "energy_level": 3
        },
        {
            "title": "Core Principle: Growth Mindset",
            "content": "I believe that challenges are opportunities to learn and grow. When I face difficulties, instead of seeing them as failures, I try to see them as chances to develop new skills and perspectives. This mindset has helped me overcome many obstacles in both my personal and professional life.",
            "tags": ["principles", "mindset", "growth"],
            "note_type": "principle",
            "mood": 7,
            "energy_level": 7
        },
        {
            "title": "Goal: Improve Communication Skills",
            "content": "I want to become a better communicator, especially in difficult conversations. Plan to practice active listening, ask more clarifying questions, and express my thoughts more clearly. Will read one book on communication this month and practice these skills in team meetings.",
            "tags": ["goals", "communication", "development"],
            "note_type": "goal",
            "mood": 6,
            "energy_level": 8
        },
        {
            "title": "Learning: Python Programming",
            "content": "Today I learned about list comprehensions in Python. They're such a elegant way to create lists! Also practiced with lambda functions and started understanding how they can make code more concise. The journey of learning programming is challenging but incredibly rewarding.",
            "tags": ["learning", "python", "programming"],
            "note_type": "learning",
            "mood": 8,
            "energy_level": 7
        }
    ]
    
    # Add sample entries
    for entry in sample_entries:
        note_id = notes.add_note(
            title=entry["title"],
            content=entry["content"],
            tags=entry["tags"],
            note_type=entry["note_type"],
            mood=entry["mood"],
            energy_level=entry["energy_level"]
        )
        print(f"Added: {entry['title']}")
    
    print("\n📊 STATISTICS OVERVIEW")
    print("-" * 40)
    notes.get_statistics()
    
    print("\n🔍 SEARCH BY TYPE: Journal Entries")
    print("-" * 40)
    notes.list_notes(note_type="journal")
    
    print("\n📋 SEARCH BY TAG: Work-related entries")
    print("-" * 40)
    notes.list_notes(tag_filter="work")
    
    print("\n🧠 PATTERN ANALYSIS")
    print("-" * 40)
    print("Analyzing your personal patterns...")
    analysis = notes.analyze_patterns()
    
    if analysis:
        print("\n✅ Pattern analysis complete! Check the detailed report above.")
    else:
        print("\n⚠️  Pattern analysis requires an API key. Set GEMINI_API_KEY in your .env file.")
    
    print("\n💡 NEXT STEPS FOR YOUR SELF-EXPLORATION JOURNEY")
    print("-" * 40)
    print("1. 📝 Use quick_journal() for daily entries")
    print("2. 🎯 Set specific goals with the 'goal' note type")
    print("3. 💭 Record your principles and values")
    print("4. 📊 Run analyze_patterns() weekly for insights")
    print("5. 🔍 Use search and filtering to track themes")
    
    return notes


def interactive_demo():
    """Interactive demo where user can try features"""
    print("\n🎮 INTERACTIVE DEMO")
    print("=" * 60)
    
    notes = SmartNotesEnhanced()
    
    while True:
        print("\nWhat would you like to try?")
        print("1. 📝 Quick journal entry")
        print("2. 🎯 Add a goal")
        print("3. 💭 Record a principle")
        print("4. 📊 View statistics")
        print("5. 🔍 Search notes")
        print("6. 🧠 Analyze patterns")
        print("7. 📋 List all notes")
        print("0. 🚪 Exit")
        
        choice = input("\nEnter your choice (0-7): ").strip()
        
        if choice == "0":
            print("👋 Thanks for trying Smart Notes Enhanced!")
            break
        elif choice == "1":
            notes.quick_journal()
        elif choice == "2":
            title = input("Goal title: ")
            content = input("Goal description: ")
            tags = input("Tags (comma-separated): ").split(",")
            tags = [tag.strip() for tag in tags if tag.strip()]
            notes.add_note(title, content, tags, note_type="goal")
        elif choice == "3":
            title = input("Principle title: ")
            content = input("Principle description: ")
            notes.add_note(title, content, note_type="principle")
        elif choice == "4":
            notes.get_statistics()
        elif choice == "5":
            query = input("Search query: ")
            notes.search_notes(query)
        elif choice == "6":
            notes.analyze_patterns()
        elif choice == "7":
            notes.list_notes()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    print("🌟 Welcome to Smart Notes Enhanced!")
    print("Your AI-powered self-exploration platform")
    print("\nChoose demo mode:")
    print("1. 📊 Automated demo with sample data")
    print("2. 🎮 Interactive demo")
    
    choice = input("\nEnter 1 or 2: ").strip()
    
    if choice == "1":
        demo_self_exploration()
    elif choice == "2":
        interactive_demo()
    else:
        print("Running automated demo...")
        demo_self_exploration()
import streamlit as st
import requests
import json
from datetime import datetime
import os
from config import GEMINI_API_KEY, NOTES_FILE

# Import the SmartNotes class
from notes_enhanced import SmartNotes

# Page config
st.set_page_config(
    page_title="Smart Notes AI",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'notes_app' not in st.session_state:
    st.session_state.notes_app = SmartNotes()
    
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'dashboard'

# Custom CSS
st.markdown(\"\"\"
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .note-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
    }
    .tag {
        display: inline-block;
        background-color: #E3F2FD;
        color: #1976D2;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-right: 0.5rem;
    }
    .ai-response {
        background-color: #E8F5E9;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
\"\"\", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>📝 Smart Notes AI</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("Navigation")
    if st.button("🏠 Dashboard"):
        st.session_state.current_view = 'dashboard'
    
    if st.button("➕ Add Note"):
        st.session_state.current_view = 'add_note'
        
    if st.button("🔍 Search Notes"):
        st.session_state.current_view = 'search_notes'
        
    if st.button("🤖 Ask AI"):
        st.session_state.current_view = 'ask_ai'
        
    st.markdown("---")
    st.subheader("Stats")
    notes_count = len(st.session_state.notes_app.notes)
    st.metric("Total Notes", notes_count)
    
    # Tag cloud
    all_tags = []
    for note in st.session_state.notes_app.notes.values():
        all_tags.extend(note.get("tags", []))
    
    if all_tags:
        st.subheader("Tags")
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        for tag, count in tag_counts.items():
            st.markdown(f"<span class='tag'>{tag} ({count})</span>", unsafe_allow_html=True)

# Dashboard View
if st.session_state.current_view == 'dashboard':
    st.subheader("📘 Your Notes")
    
    if not st.session_state.notes_app.notes:
        st.info("No notes found. Add your first note!")
        if st.button("Add Note"):
            st.session_state.current_view = 'add_note'
    else:
        # Filter by tag
        all_tags = []
        for note in st.session_state.notes_app.notes.values():
            all_tags.extend(note.get("tags", []))
        
        unique_tags = list(set(all_tags))
        if unique_tags:
            selected_tag = st.selectbox("Filter by tag", ["All"] + unique_tags)
            if selected_tag != "All":
                filtered_notes = {id: note for id, note in st.session_state.notes_app.notes.items() 
                                if selected_tag in note.get("tags", [])}
            else:
                filtered_notes = st.session_state.notes_app.notes
        else:
            filtered_notes = st.session_state.notes_app.notes
        
        # Display notes
        for note_id, note in filtered_notes.items():
            created = datetime.fromisoformat(note["created"]).strftime("%Y-%m-%d %H:%M")
            updated = datetime.fromisoformat(note["updated"]).strftime("%Y-%m-%d %H:%M")
            
            with st.container():
                st.markdown(f\"\"\"
                <div class="note-card">
                    <h3>{note['title']}</h3>
                    <p><strong>ID:</strong> {note_id} | <strong>Created:</strong> {created} | <strong>Updated:</strong> {updated}</p>
                \"\"\", unsafe_allow_html=True)
                
                if note.get("tags"):
                    tags_html = "".join([f"<span class='tag'>{tag}</span>" for tag in note["tags"]])
                    st.markdown(f"<p><strong>Tags:</strong> {tags_html}</p>", unsafe_allow_html=True)
                
                st.markdown(f"<p><strong>Content:</strong> {note['content']}</p>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✏️ Edit", key=f"edit_{note_id}"):
                        st.session_state.edit_note_id = note_id
                        st.session_state.current_view = 'edit_note'
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{note_id}"):
                        st.session_state.delete_note_id = note_id
                        st.session_state.show_delete_confirm = True
                with col3:
                    if st.button("🧠 Ask AI", key=f"ai_{note_id}"):
                        st.session_state.ai_question = f"Tell me more about this note: {note['title']}"
                        st.session_state.current_view = 'ask_ai'
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("---")
        
        # Delete confirmation
        if st.session_state.get('show_delete_confirm', False):
            note_id = st.session_state.delete_note_id
            note = st.session_state.notes_app.notes.get(note_id, {})
            if st.warning(f"Are you sure you want to delete note '{note.get('title', 'Unknown')}'?"):
                if st.button("Yes, delete"):
                    st.session_state.notes_app.delete_note(note_id)
                    st.session_state.show_delete_confirm = False
                    st.experimental_rerun()
                if st.button("Cancel"):
                    st.session_state.show_delete_confirm = False
                    st.experimental_rerun()

# Add Note View
elif st.session_state.current_view == 'add_note':
    st.subheader("➕ Add New Note")
    
    with st.form("add_note_form"):
        title = st.text_input("Title")
        content = st.text_area("Content", height=200)
        tags = st.text_input("Tags (comma separated)")
        
        submitted = st.form_submit_button("Save Note")
        
        if submitted:
            if not title:
                st.error("Title cannot be empty")
            elif not content.strip():
                st.error("Content cannot be empty")
            else:
                tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                st.session_state.notes_app.add_note(title, content, tag_list)
                st.success("Note saved successfully!")
                st.session_state.current_view = 'dashboard'
                st.experimental_rerun()

# Edit Note View
elif st.session_state.current_view == 'edit_note':
    note_id = st.session_state.get('edit_note_id')
    note = st.session_state.notes_app.notes.get(note_id, {})
    
    st.subheader(f"✏️ Edit Note: {note.get('title', 'Unknown')}")
    
    if not note:
        st.error("Note not found")
        if st.button("Back to Dashboard"):
            st.session_state.current_view = 'dashboard'
            st.experimental_rerun()
    else:
        with st.form("edit_note_form"):
            title = st.text_input("Title", value=note.get('title', ''))
            content = st.text_area("Content", value=note.get('content', ''), height=200)
            tags = st.text_input("Tags (comma separated)", value=", ".join(note.get('tags', [])))
            
            submitted = st.form_submit_button("Update Note")
            
            if submitted:
                if not title:
                    st.error("Title cannot be empty")
                elif not content.strip():
                    st.error("Content cannot be empty")
                else:
                    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                    st.session_state.notes_app.update_note(note_id, title, content, tag_list)
                    st.success("Note updated successfully!")
                    st.session_state.current_view = 'dashboard'
                    st.experimental_rerun()
        
        if st.button("Cancel"):
            st.session_state.current_view = 'dashboard'
            st.experimental_rerun()

# Search Notes View
elif st.session_state.current_view == 'search_notes':
    st.subheader("🔍 Search Notes")
    
    search_query = st.text_input("Enter search query")
    
    if search_query:
        matches = []
        query_lower = search_query.lower()
        
        for note_id, note in st.session_state.notes_app.notes.items():
            if (query_lower in note['title'].lower() or 
                query_lower in note['content'].lower() or
                any(query_lower in tag.lower() for tag in note.get("tags", []))):
                matches.append((note_id, note))
        
        if matches:
            st.write(f"Found {len(matches)} matches:")
            for note_id, note in matches:
                created = datetime.fromisoformat(note["created"]).strftime("%Y-%m-%d %H:%M")
                updated = datetime.fromisoformat(note["updated"]).strftime("%Y-%m-%d %H:%M")
                
                with st.container():
                    st.markdown(f\"\"\"
                    <div class="note-card">
                        <h3>{note['title']}</h3>
                        <p><strong>ID:</strong> {note_id} | <strong>Created:</strong> {created} | <strong>Updated:</strong> {updated}</p>
                    \"\"\", unsafe_allow_html=True)
                    
                    if note.get("tags"):
                        tags_html = "".join([f"<span class='tag'>{tag}</span>" for tag in note["tags"]])
                        st.markdown(f"<p><strong>Tags:</strong> {tags_html}</p>", unsafe_allow_html=True)
                    
                    st.markdown(f"<p><strong>Content:</strong> {note['content']}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info("No matches found")

# Ask AI View
elif st.session_state.current_view == 'ask_ai':
    st.subheader("🤖 Ask AI about your notes")
    
    # Pre-fill with a question if provided
    default_question = st.session_state.get('ai_question', '')
    question = st.text_area("Ask a question about your notes:", value=default_question, height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        use_relevant_only = st.checkbox("Use only relevant notes for context", value=True)
    with col2:
        if st.button("Clear"):
            st.session_state.ai_question = ""
            st.experimental_rerun()
    
    if st.button("Ask AI") or default_question:
        if not question:
            st.error("Please enter a question")
        else:
            # Show loading spinner
            with st.spinner("🤖 AI is thinking..."):
                # Make API call to Gemini
                api_key = GEMINI_API_KEY
                
                if use_relevant_only:
                    # Find only relevant notes for the question
                    relevant_notes = st.session_state.notes_app.find_relevant_notes(question, api_key)
                    if relevant_notes:
                        notes_context = "Relevant Notes:\\n\\n"
                        for note_id, note in relevant_notes:
                            notes_context += f"ID: {note_id}\\n"
                            notes_context += f"Title: {note['title']}\\n"
                            if note.get("tags"):
                                notes_context += f"Tags: {', '.join(note['tags'])}\\n"
                            notes_context += f"Content: {note['content']}\\n\\n"
                    else:
                        notes_context = "No relevant notes found."
                else:
                    # Use all notes
                    notes_context = st.session_state.notes_app.get_all_content()
                
                prompt = f\"\"\"Based on these notes, analyze the question and respond with JSON in this exact format:
{{
  "answer": "your detailed answer here",
  "confidence": 0.85,
  "sources_used": ["note_1", "note_2"],
  "suggested_actions": ["action1", "action2"],
  "related_topics": ["topic1", "topic2"]
}}

Notes: {notes_context}
Question: {question}

Respond ONLY with valid JSON, no other text.\"\"\"

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
                    
                    response = requests.post(url, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if 'candidates' in result and len(result['candidates']) > 0:
                            answer = result['candidates'][0]['content']['parts'][0]['text']
                            # Try to parse as JSON first
                            try:
                                ai_response = json.loads(answer)
                                st.markdown("<div class='ai-response'>", unsafe_allow_html=True)
                                st.subheader("✨ AI Response")
                                st.write(f"**Answer:** {ai_response['answer']}")
                                st.write(f"**Confidence:** {ai_response['confidence']:.2%}")
                                
                                if ai_response['sources_used']:
                                    st.write(f"**Sources:** {', '.join(ai_response['sources_used'])}")
                                
                                if ai_response['suggested_actions']:
                                    st.write(f"**Suggestions:** {', '.join(ai_response['suggested_actions'])}")
                                
                                if ai_response['related_topics']:
                                    st.write(f"**Related Topics:** {', '.join(ai_response['related_topics'])}")
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                            except Exception:
                                # Fallback to regular text display
                                st.markdown("<div class='ai-response'>", unsafe_allow_html=True)
                                st.subheader("✨ AI Response")
                                st.write(answer)
                                st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.error("No response from AI")
                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.text(response.text)
                except requests.RequestException as e:
                    st.error(f"Network error: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
    
    # Show recent notes as context
    st.markdown("---")
    st.subheader("📚 Your Recent Notes")
    recent_notes = list(st.session_state.notes_app.notes.items())[-3:]  # Last 3 notes
    
    for note_id, note in recent_notes:
        with st.expander(f"{note['title']} ({note_id})"):
            st.write(f"**Content:** {note['content']}")
            if note.get("tags"):
                st.write(f"**Tags:** {', '.join(note['tags'])}")

# Footer
st.markdown("---")
st.caption("Smart Notes AI - Powered by Google Gemini & Streamlit")
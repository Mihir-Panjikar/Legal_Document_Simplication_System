import streamlit as st
from utils.database import HistoryDatabase


@st.cache_resource
def get_database():
    """Get or create the database connection"""
    return HistoryDatabase()


def load_history_entry(db, entry_id):
    """Load a history entry from the database"""
    entry = db.get_entry(entry_id)
    if entry:
        # Map column indices to variables
        id, input_text, simplified_text, translated_text, language, timestamp, title = entry
        st.session_state.input_text = input_text
        st.session_state.simplified_text = simplified_text or ""
        st.session_state.translated_text = translated_text or ""
        st.session_state.current_entry_id = id
        st.session_state.selected_language = language or "None"


def perform_delete(db):
    """Delete an entry from the database"""
    from app.session_manager import reset_session

    if st.session_state.entry_to_delete:
        if st.session_state.entry_to_delete == "all":
            # Delete all entries
            db.delete_all_entries()
            reset_session()
        else:
            # Check if we're deleting the currently loaded entry
            is_current = st.session_state.entry_to_delete == st.session_state.current_entry_id

            # Delete from database
            success = db.delete_entry(st.session_state.entry_to_delete)

            # If we deleted the current entry, clear the UI
            if success and is_current:
                reset_session()

        # Reset delete dialog state
        st.session_state.show_delete_dialog = False
        st.session_state.entry_to_delete = None

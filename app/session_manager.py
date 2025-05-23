import streamlit as st
from datetime import datetime


def initialize_session_state():
    """Initialize session state variables"""
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""
    if "simplified_text" not in st.session_state:
        st.session_state.simplified_text = ""
    if "translated_text" not in st.session_state:
        st.session_state.translated_text = ""
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "None"
    if "current_entry_id" not in st.session_state:
        st.session_state.current_entry_id = None
    if "show_delete_dialog" not in st.session_state:
        st.session_state.show_delete_dialog = False
    if "entry_to_delete" not in st.session_state:
        st.session_state.entry_to_delete = None
    if "show_export_options" not in st.session_state:
        st.session_state.show_export_options = False
    if "timestamp" not in st.session_state:
        st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "ollama_model" not in st.session_state:
        from utils.ollama_config import DEFAULT_MODEL
        st.session_state.ollama_model = DEFAULT_MODEL
    if "doc_title" not in st.session_state:
        st.session_state.doc_title = ""


def reset_session():
    """Reset the current session data"""
    st.session_state.input_text = ""
    st.session_state.simplified_text = ""
    st.session_state.translated_text = ""
    st.session_state.current_entry_id = None
    st.session_state.selected_language = "None"


def set_delete_dialog(show=False, entry_id=None):
    """Set the delete dialog state"""
    st.session_state.show_delete_dialog = show
    st.session_state.entry_to_delete = entry_id

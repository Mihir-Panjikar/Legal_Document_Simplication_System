import streamlit as st


def initialize_session_state():
    """Initialize all session state variables"""
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""
    if "simplified_text" not in st.session_state:
        st.session_state.simplified_text = ""
    if "translated_text" not in st.session_state:
        st.session_state.translated_text = ""
    if "current_entry_id" not in st.session_state:
        st.session_state.current_entry_id = None
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "None"
    if "show_delete_dialog" not in st.session_state:
        st.session_state.show_delete_dialog = False
    if "entry_to_delete" not in st.session_state:
        st.session_state.entry_to_delete = None


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

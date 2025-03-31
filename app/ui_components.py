import streamlit as st
from app.session_manager import set_delete_dialog, reset_session
from app.database_operations import load_history_entry, perform_delete
from app.processors import process_simplification, process_translation


def render_delete_dialog(db):
    """Render the delete confirmation dialog"""
    with st.container():
        st.warning(
            "Are you sure you want to delete this history entry? This cannot be undone.")
        col1_dialog, col2_dialog = st.columns(2)
        with col1_dialog:
            if st.button("Yes, Delete", key="confirm_delete"):
                perform_delete(db)
                st.rerun()
        with col2_dialog:
            if st.button("Cancel", key="cancel_delete"):
                set_delete_dialog(False, None)


def render_history_sidebar(db):
    """Render the history sidebar"""
    st.subheader("History")

    # Get history entries
    history_entries = db.get_all_entries()

    if not history_entries:
        st.info("No history yet. Start by simplifying a document.")
    else:
        # Add a "Clear All History" button at the top
        if st.button("Clear All History", key="clear_all"):
            # Ask for confirmation
            set_delete_dialog(True, "all")  # Special marker for all entries

        for entry in history_entries:
            entry_id, title, timestamp = entry
            # Create a container for each history item with buttons
            with st.container():
                cols = st.columns([3, 1])
                with cols[0]:
                    if st.button(f"{title}", key=f"history_{entry_id}"):
                        load_history_entry(db, entry_id)
                with cols[1]:
                    if st.button("🗑️", key=f"delete_{entry_id}"):
                        set_delete_dialog(True, entry_id)


def render_input_area(db):
    """Render the input text area"""
    user_input = st.text_area(
        "Enter legal document text here:", height=300, value=st.session_state.input_text)

    if st.button("Simplify"):
        if process_simplification(db, user_input):
            st.rerun()

    # Add a button to clear the current session
    if st.session_state.input_text:
        if st.button("New Document", key="new_doc"):
            reset_session()
            st.rerun()

    return user_input


def render_output_area(db):
    """Render the output area with simplified and translated text"""
    if st.session_state.simplified_text:
        st.markdown("### Simplified Text:")
        st.write(st.session_state.simplified_text)

        language = st.selectbox(
            "Translate to:",
            ["None", "Hindi", "Marathi"],
            index=["None", "Hindi", "Marathi"].index(
                st.session_state.selected_language)
            if st.session_state.selected_language in ["None", "Hindi", "Marathi"] else 0,
            key="lang_select"
        )

        if language != "None":
            lang_code = "hi" if language == "Hindi" else "mr"
            if st.button("Translate"):
                if process_translation(db, lang_code, language):
                    st.rerun()

    if st.session_state.translated_text:
        st.markdown(
            f"### Translated Text ({st.session_state.selected_language}):")
        st.write(st.session_state.translated_text)

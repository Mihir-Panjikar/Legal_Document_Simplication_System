import streamlit as st
from utils.Simplification import simplify_document
from utils.translation import translate_text
from utils.database import HistoryDatabase
import asyncio

# Initialize the database


@st.cache_resource
def get_database():
    return HistoryDatabase()


db = get_database()

# Streamlit UI
st.set_page_config(page_title="Legal Document Simplifier", layout="wide")

st.title("Legal Document Simplification System")
st.markdown("##### Please enter the legal text for simplification")

col1, col2 = st.columns([1, 3])

# Initialize session state
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

# Function to load history entry


def load_history_entry(entry_id):
    entry = db.get_entry(entry_id)
    if entry:
        # Map column indices to variables
        id, input_text, simplified_text, translated_text, language, timestamp, title = entry
        st.session_state.input_text = input_text
        st.session_state.simplified_text = simplified_text or ""
        st.session_state.translated_text = translated_text or ""
        st.session_state.current_entry_id = id
        st.session_state.selected_language = language or "None"

# Function to show delete confirmation


def show_delete_confirmation(entry_id):
    st.session_state.show_delete_dialog = True
    st.session_state.entry_to_delete = entry_id

# Function to delete entry


def delete_entry():
    if st.session_state.entry_to_delete:
        if st.session_state.entry_to_delete == "all":
            # Delete all entries
            db.delete_all_entries()

            # Clear the UI
            st.session_state.input_text = ""
            st.session_state.simplified_text = ""
            st.session_state.translated_text = ""
            st.session_state.current_entry_id = None
            st.session_state.selected_language = "None"
        else:
            # Check if we're deleting the currently loaded entry
            is_current = st.session_state.entry_to_delete == st.session_state.current_entry_id

            # Delete from database
            success = db.delete_entry(st.session_state.entry_to_delete)

            # If we deleted the current entry, clear the UI
            if success and is_current:
                st.session_state.input_text = ""
                st.session_state.simplified_text = ""
                st.session_state.translated_text = ""
                st.session_state.current_entry_id = None
                st.session_state.selected_language = "None"

        # Reset delete dialog state
        st.session_state.show_delete_dialog = False
        st.session_state.entry_to_delete = None

        # Force UI refresh
        st.rerun()

# Function to cancel delete


def cancel_delete():
    st.session_state.show_delete_dialog = False
    st.session_state.entry_to_delete = None


# Show delete confirmation dialog if needed
if st.session_state.show_delete_dialog:
    with st.container():
        st.warning(
            "Are you sure you want to delete this history entry? This cannot be undone.")
        col1_dialog, col2_dialog = st.columns(2)
        with col1_dialog:
            if st.button("Yes, Delete", key="confirm_delete"):
                delete_entry()
        with col2_dialog:
            if st.button("Cancel", key="cancel_delete"):
                cancel_delete()

with col1:
    st.subheader("History")

    # Get history entries
    history_entries = db.get_all_entries()

    if not history_entries:
        st.info("No history yet. Start by simplifying a document.")
    else:
        # Add a "Clear All History" button at the top
        if st.button("Clear All History", key="clear_all"):
            # Ask for confirmation
            st.session_state.show_delete_dialog = True
            st.session_state.entry_to_delete = "all"  # Special marker for all entries

        for entry in history_entries:
            entry_id, title, timestamp = entry
            # Create a container for each history item with buttons
            with st.container():
                cols = st.columns([3, 1])
                with cols[0]:
                    if st.button(f"{title}", key=f"history_{entry_id}"):
                        load_history_entry(entry_id)
                with cols[1]:
                    if st.button("🗑️", key=f"delete_{entry_id}"):
                        show_delete_confirmation(entry_id)

with col2:
    user_input = st.text_area(
        "Enter legal document text here:", height=300, value=st.session_state.input_text)

    if st.button("Simplify"):
        if user_input.strip() == "":
            st.error("Please enter some text to simplify.")
        else:
            with st.spinner("Simplifying..."):
                simplified_text = simplify_document(user_input)
                st.session_state.simplified_text = simplified_text

                # Save to database
                if st.session_state.current_entry_id:
                    # Update existing entry
                    db.update_entry(
                        st.session_state.current_entry_id,
                        simplified_text=simplified_text
                    )
                else:
                    # Create new entry
                    entry_id = db.add_entry(user_input, simplified_text)
                    st.session_state.current_entry_id = entry_id

                # Clear translated text since we have new simplified text
                st.session_state.translated_text = ""

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
                with st.spinner(f"Translating to {language}..."):
                    translated_text = asyncio.run(
                        translate_text(
                            st.session_state.simplified_text, src="en", dest=lang_code)
                    )
                    st.session_state.translated_text = translated_text
                    st.session_state.selected_language = language

                    # Update in database
                    if st.session_state.current_entry_id:
                        db.update_entry(
                            st.session_state.current_entry_id,
                            translated_text=translated_text,
                            language=language
                        )

    if st.session_state.translated_text:
        st.markdown(
            f"### Translated Text ({st.session_state.selected_language}):")
        st.write(st.session_state.translated_text)

# Add a button to clear the current session
if st.session_state.input_text:
    if st.button("New Document", key="new_doc"):
        st.session_state.input_text = ""
        st.session_state.simplified_text = ""
        st.session_state.translated_text = ""
        st.session_state.current_entry_id = None
        st.session_state.selected_language = "None"
        st.rerun()

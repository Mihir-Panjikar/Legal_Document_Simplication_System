import streamlit as st
import asyncio
from utils.Simplification import simplify_document
from utils.translation import translate_text, translate_with_retries


def process_simplification(db, user_input):
    """Process the simplification of legal text"""
    if user_input.strip() == "":
        st.error("Please enter some text to simplify.")
        return False

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
        return True


def process_translation(db, lang_code, language):
    """Process the translation of simplified text"""
    with st.spinner(f"Translating to {language}..."):
        # Replace the async call with the retry-enabled version
        translated_text = translate_with_retries(
            st.session_state.simplified_text,
            lang_code,
            max_retries=5,  # Increase retries for Docker environment
            retry_delay=3   # Start with longer delays
        )

        if translated_text:  # Check if translation was successful
            st.session_state.translated_text = translated_text
            st.session_state.selected_language = language

            # Update in database
            if st.session_state.current_entry_id:
                db.update_entry(
                    st.session_state.current_entry_id,
                    translated_text=translated_text,
                    language=language
                )
            return True
        else:
            st.error("Translation failed. Please try again later.")
            return False

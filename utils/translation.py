"""
Translation utilities using Groq API.

This module provides functions to translate legal documents using Groq's cloud API.
"""

import streamlit as st
from utils.groq_inference import translate_with_groq
from utils.groq_config import get_selected_groq_model


async def translate_text(text, src="en", dest="hi"):
    """
    Translates text using Groq API (async wrapper for compatibility).

    Args:
        text (str): Text to translate
        src (str): Source language code (not used with Groq, assumes English source)
        dest (str): Destination language code (hi=Hindi, mr=Marathi)

    Returns:
        str: Translated text
    """
    # Call the synchronous Groq translation function
    return translate_with_retries(text, dest)


def translate_with_retries(text, target_language, max_retries=3, retry_delay=2):
    """
    Attempt translation with retries on connection errors.
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code (hi=Hindi, mr=Marathi)
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Initial delay between retries in seconds
        
    Returns:
        str: Translated text or None on failure
    """
    try:
        # Get the selected Groq model
        model = get_selected_groq_model()

        # Translate using Groq API (already has retry logic built-in)
        translated_text = translate_with_groq(
            text=text,
            target_language=target_language,
            model=model,
            max_retries=max_retries
        )

        return translated_text

    except Exception as e:
        st.error(f"Translation failed after {max_retries} attempts: {str(e)}")
        return None

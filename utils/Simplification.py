"""
Legal Document Simplification using Groq API.

This module provides functions to simplify legal documents using Groq's cloud API.
"""

import streamlit as st
from utils.groq_inference import simplify_with_groq, check_groq_connection
from utils.groq_config import get_selected_groq_model


@st.cache_data(show_spinner=True)
def simplify_document(user_input, max_tokens=4096):
    """
    Simplifies a legal document using Groq API.

    Args:
        user_input (str): The legal text to simplify
        max_tokens (int): Maximum number of tokens for the response

    Returns:
        str: The simplified text
    """
    try:
        # Get the selected Groq model
        model = get_selected_groq_model()

        # Simplify using Groq API
        simplified_text = simplify_with_groq(
            user_input=user_input,
            model=model,
            max_tokens=max_tokens
        )

        return simplified_text

    except Exception as e:
        st.error(f"Error during simplification: {str(e)}")
        # Return fallback message in case of error
        return "Sorry, there was an error simplifying the document. Please try again."


def check_model_availability():
    """
    Check if Groq API is available and accessible.
    Tests the connection to Groq's cloud API.

    Returns:
        bool: True if API is available, False otherwise
    """
    return check_groq_connection()

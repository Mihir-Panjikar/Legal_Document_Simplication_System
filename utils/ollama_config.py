import streamlit as st

# Available Ollama models
AVAILABLE_MODELS = [
    "llama3.2",  # Add the new model
    "llama3",
    "mistral",
    "phi3",
    "gemma",
    "llama2",
    "mixtral"
]

# Default model to use
DEFAULT_MODEL = "llama3.2"

# Ollama API endpoint (default is localhost)
OLLAMA_API_HOST = "http://localhost:11434"

# Template for system message
SYSTEM_TEMPLATE = """You are an expert in summarization and legal document simplification. 
Your task is to summarize the following agreement in a way that is easy for a layperson to understand. 
The summary should include all key details while using simple, clear language and relevant real-life examples where needed. 
Ensure that no critical information is lost."""

# Get selected model from session state or use default


def get_selected_model():
    if "ollama_model" not in st.session_state:
        st.session_state.ollama_model = DEFAULT_MODEL
    return st.session_state.ollama_model

# Set selected model in session state


def set_selected_model(model_name):
    if model_name in AVAILABLE_MODELS:
        st.session_state.ollama_model = model_name
        return True
    return False

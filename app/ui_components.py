import streamlit as st
from app.session_manager import set_delete_dialog, reset_session
from app.database_operations import load_history_entry, perform_delete
from app.processors import process_simplification, process_translation
from utils.ollama_config import AVAILABLE_MODELS, get_selected_model, set_selected_model
from utils.Simplification import check_model_availability


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
    # First render model selection
    render_model_selection()

    # Then render history
    st.sidebar.markdown("### History")

    # Get history entries
    history_entries = db.get_all_entries()

    if not history_entries:
        st.sidebar.info("No history yet. Start by simplifying a document.")
    else:
        # Add a "Clear All History" button at the top
        if st.sidebar.button("Clear All History", key="clear_all"):
            # Ask for confirmation
            set_delete_dialog(True, "all")  # Special marker for all entries

        for entry in history_entries:
            entry_id, title, timestamp = entry
            # Create a container for each history item with buttons
            with st.sidebar.container():
                cols = st.sidebar.columns([3, 1])
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

    # Before processing any document
    if check_model_availability():
        # Proceed with document simplification
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


def render_model_selection():
    """Render a dropdown to select the Ollama model"""
    st.sidebar.markdown("### Model Settings")

    current_model = get_selected_model()
    selected_model = st.sidebar.selectbox(
        "Select Ollama Model:",
        AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(
            current_model) if current_model in AVAILABLE_MODELS else 0,
        key="model_selector"
    )

    if selected_model != current_model:
        set_selected_model(selected_model)
        st.sidebar.success(f"Model changed to {selected_model}")

    # Check if the selected model is available
    st.sidebar.markdown("### Model Status")
    if check_model_availability():
        st.sidebar.success(f"Model '{selected_model}' is available ✓")
    else:
        st.sidebar.error(f"Model '{selected_model}' is not available ✗")

    st.sidebar.divider()


# Add this function to show in the about section or help
def render_ollama_help():
    """Render help information for Ollama setup and status"""
    st.subheader("Ollama Status")

    try:
        import ollama
        import requests
        import json
        from utils.ollama_config import OLLAMA_API_HOST

        # Try direct HTTP request first (more reliable)
        try:
            # Remove http:// if present for requests
            api_host = OLLAMA_API_HOST.replace("http://", "")
            response = requests.get(f"http://{api_host}/api/tags")

            if response.status_code == 200:
                st.success("✅ Connected to Ollama server successfully")

                # Display raw response for debugging
                with st.expander("Debug: API Response"):
                    st.code(json.dumps(response.json(), indent=2))

                # Extract models using the correct format
                data = response.json()
                models = []

                # Handle different possible response formats
                if "models" in data:
                    # New format with "models" key
                    models = [m.get("name", str(m))
                              for m in data["models"] if isinstance(m, dict)]
                elif "models" in data:
                    # Legacy format
                    models = data["models"]
                elif isinstance(data, list):
                    # Direct list response
                    models = [m.get("name", str(m))
                              for m in data if isinstance(m, dict)]

                # Display models
                if models:
                    st.write("Available models:")
                    for model in models:
                        st.write(f"- {model}")
                else:
                    st.warning(
                        "No models available. You need to pull a model.")
            else:
                st.warning(
                    f"Ollama API returned status code: {response.status_code}")

        except requests.exceptions.RequestException as req_error:
            st.warning(f"HTTP request to Ollama failed: {str(req_error)}")

            # Fall back to using the Python client
            try:
                client = ollama.Client(host=OLLAMA_API_HOST)
                models_info = client.list()

                # Display raw response
                with st.expander("Debug: Python Client Response"):
                    st.code(str(models_info))

                st.success("✅ Connected to Ollama via Python client")
                st.info(
                    "Please check the debug information to see the response format")

            except Exception as client_error:
                st.error(f"Python client failed: {str(client_error)}")

        # Show command to pull models
        st.markdown("### Pull a model")
        st.code("ollama pull llama3.2", language="bash")
        st.markdown("After pulling the model, restart this application.")

    except Exception as e:
        st.error(f"Error connecting to Ollama: {str(e)}")
        st.markdown("""
        ### Troubleshooting Steps:
        
        1. **Install Ollama** if not already installed:
           ```
           curl -fsSL https://ollama.com/install.sh | sh
           ```
           
        2. **Start Ollama** in a terminal:
           ```
           ollama serve
           ```
           
        3. **Check connection**:
           ```
           curl http://localhost:11434/api/tags
           ```
           
        4. **Restart the application** after Ollama is running
        """)

    with st.expander("Ollama Setup Help"):
        st.markdown("""
        ### Setting Up Ollama
        
        This application uses Ollama to run AI models locally on your computer.
        
        #### Installation Steps:
        
        1. **Install Ollama** from [ollama.com](https://ollama.com)
        2. **Start Ollama** by running `ollama serve` in your terminal
        3. **Download a model** by running `ollama pull llama3` (or another model)
        
        #### Troubleshooting:
        
        - Make sure Ollama is running (`ollama serve`)
        - Check model availability with `ollama list`
        - For translation, larger models like llama3 perform better
        
        #### System Requirements:
        
        - At least 8GB RAM (16GB+ recommended)
        - Modern CPU, GPU recommended for faster processing
        - 10GB+ free disk space for model storage
        """)

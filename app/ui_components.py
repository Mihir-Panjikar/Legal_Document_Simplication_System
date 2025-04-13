import streamlit as st
from app.session_manager import set_delete_dialog, reset_session
from app.database_operations import load_history_entry, perform_delete
from app.processors import process_simplification, process_translation
from utils.ollama_config import AVAILABLE_MODELS, get_selected_model, set_selected_model
from utils.Simplification import check_model_availability
from utils.file_extractor import extract_text_from_file
from utils.document_export import DocumentExporter
from datetime import datetime


def render_delete_dialog(db):
    """Render the delete confirmation dialog at the top of the screen"""
    # Create a placeholder at the very top of the app
    dialog_placeholder = st.empty()

    # Use the placeholder to display the dialog
    with dialog_placeholder.container():
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

    render_model_selection()


def render_input_area(db):
    """Render the input area with text input and simplification button"""
    st.markdown("### Input Legal Document")
    
    # Add tabs for text input and file upload
    input_tab, file_tab = st.tabs(["Text Input", "File Upload"])
    
    with input_tab:
        # Existing text input functionality
        user_input = st.text_area(
            "Paste legal text here:",
            value=st.session_state.input_text,
            height=300,
            placeholder="Enter or paste the legal document text here...",
            key="text_input"
        )
        
        # Update session state when input changes
        if user_input != st.session_state.input_text:
            st.session_state.input_text = user_input
            
    with file_tab:
        # Add file uploader for document files
        uploaded_file = st.file_uploader(
            "Upload a legal document file:",
            type=["txt", "docx", "pdf"],
            key="file_uploader"
        )
        
        # Extract text when file is uploaded
        if uploaded_file is not None:
            # Show a spinner while extracting text
            with st.spinner(f"Extracting text from {uploaded_file.name}..."):
                extracted_text = extract_text_from_file(uploaded_file)
                
                if extracted_text:
                    st.success(f"Text extracted from {uploaded_file.name}")
                    
                    # Show preview with option to edit
                    st.markdown("### Preview Extracted Text")
                    edited_text = st.text_area(
                        "Edit extracted text if needed:",
                        value=extracted_text,
                        height=300,
                        key="extracted_text"
                    )
                    
                    # Update session state with extracted/edited text
                    if st.button("Use This Text", key="use_extracted"):
                        st.session_state.input_text = edited_text
                        st.rerun()
    
    # Only show simplify button if there's input text (from either source)
    if st.session_state.input_text:
        # Display title input if there's text
        title = st.text_input(
            "Document Title (optional):",
            value=st.session_state.doc_title,
            placeholder="Enter a title for this document",
            key="title_input"
        )
        
        if title != st.session_state.doc_title:
            st.session_state.doc_title = title
            
        # Add button to simplify the text - FIX: Add user_input parameter
        if st.button("Simplify Document", key="simplify_btn"):
            if process_simplification(db, st.session_state.input_text):
                st.success("Document simplified successfully!")
    
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

        # Update timestamp whenever we display results
        st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Language selection and translation
        language = st.selectbox(
            "Translate to:",
            ["None", "Hindi", "Marathi"],
            index=["None", "Hindi", "Marathi"].index(
                st.session_state.selected_language)
            if st.session_state.selected_language in ["None", "Hindi", "Marathi"] else 0,
            key="lang_select"
        )

        col1, col2 = st.columns([1, 1])

        with col1:
            if language != "None":
                lang_code = "hi" if language == "Hindi" else "mr"
                if st.button("Translate"):
                    if process_translation(db, lang_code, language):
                        st.rerun()

        # Add export options
        # with col2:
        #     if st.button("Export Document"):
        #         st.session_state.show_export_options = True

    if st.session_state.translated_text:
        st.markdown(
            f"### Translated Text ({st.session_state.selected_language}):")
        st.write(st.session_state.translated_text)

    # Add a separator before export options
    if st.session_state.get('simplified_text'):
        st.markdown("---")
        
        # Get title or use a default
        title = st.session_state.get('document_title', 'Document')
        
        # Show export options
        DocumentExporter.render_export_options(
            title,
            st.session_state.get('input_text', ''),
            st.session_state.get('simplified_text', ''),
            st.session_state.get('translated_text'),
            st.session_state.get('selected_language')
        )

    # # Show export options if the button was clicked
    # if st.session_state.get("show_export_options", False) and st.session_state.simplified_text:
    #     render_export_options(db)


def render_export_options(db):
    """Render export options"""
    st.markdown("### Export Options")

    # Get the document data
    entry_id = st.session_state.current_entry_id
    if entry_id:
        entry = db.get_entry(entry_id)
        if entry:
            # Map column indices to variables
            id, input_text, simplified_text, translated_text, language, timestamp, title = entry

            # Create a title for the document
            doc_title = title or "Legal Document"

            # Create filename base
            filename_base = doc_title.replace(" ", "_")[:30]

            # Export format selection
            export_format = st.selectbox(
                "Select Format:",
                ["PDF", "Word Document", "Text File"],
                key="export_format"
            )

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if st.button("PDF", key="export_pdf"):
                    pdf_bytes = DocumentExporter.export_to_pdf(
                        doc_title, input_text, simplified_text, translated_text, language
                    )
                    download_link = DocumentExporter.get_download_link(
                        pdf_bytes, filename_base, "pdf", "Download PDF"
                    )
                    st.markdown(download_link, unsafe_allow_html=True)

            with col2:
                if st.button("Word", key="export_docx"):
                    docx_bytes = DocumentExporter.export_to_docx(
                        doc_title, input_text, simplified_text, translated_text, language
                    )
                    download_link = DocumentExporter.get_download_link(
                        docx_bytes, filename_base, "docx", "Download Word"
                    )
                    st.markdown(download_link, unsafe_allow_html=True)

            with col3:
                if st.button("Text", key="export_txt"):
                    txt_bytes = DocumentExporter.export_to_txt(
                        doc_title, input_text, simplified_text, translated_text, language
                    )
                    download_link = DocumentExporter.get_download_link(
                        txt_bytes, filename_base, "txt", "Download Text"
                    )
                    st.markdown(download_link, unsafe_allow_html=True)

            if st.button("Close Export Options"):
                st.session_state.show_export_options = False
                st.rerun()


def render_model_selection():
    """Render a dropdown to select the Ollama model"""
    import requests
    import json
    from utils.ollama_config import OLLAMA_API_HOST

    # Check if the "Advanced" button has been clicked
    if "show_advanced" not in st.session_state:
        st.session_state.show_advanced = False

    # Add the "Advanced" button
    if st.sidebar.button("Advanced"):
        st.session_state.show_advanced = not st.session_state.show_advanced

    # Render model selection only if "Advanced" is clicked
    if st.session_state.show_advanced:
        st.sidebar.markdown("### Model Settings")

        # Display available models first
        st.sidebar.markdown("#### Available Models")

        try:
            # Get the list of available models from Ollama
            api_host = OLLAMA_API_HOST.replace("http://", "")
            response = requests.get(f"http://{api_host}/api/tags")

            if response.status_code == 200:
                data = response.json()
                available_models_list = []

                # Extract model names using the correct format
                if "models" in data:
                    available_models_list = [m.get("name", str(m))
                                             for m in data["models"] if isinstance(m, dict)]
                elif isinstance(data, list):
                    available_models_list = [m.get("name", str(m))
                                             for m in data if isinstance(m, dict)]

                # Display the models
                if available_models_list:
                    for model in available_models_list:
                        st.sidebar.markdown(f"- {model}")
                else:
                    st.sidebar.warning("No models available in Ollama")
                    st.sidebar.markdown("Run this command to add a model:")
                    st.sidebar.code("ollama pull <model-name>", language="bash")
            else:
                st.sidebar.warning("Could not fetch available models")

        except Exception as e:
            st.sidebar.warning("Could not connect to Ollama server")

        st.sidebar.markdown("---")

        # Then show model selection dropdown
        st.sidebar.markdown("#### Select Model")
        current_model = get_selected_model()
        selected_model = st.sidebar.selectbox(
            "Choose model:",
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
        st.code("ollama pull <model-name>", language="bash")
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

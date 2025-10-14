import streamlit as st
from app.session_manager import set_delete_dialog, reset_session
from app.database_operations import load_history_entry, perform_delete
from app.processors import process_simplification, process_translation
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
    """Render a dropdown to select the Groq model"""
    from utils.groq_config import AVAILABLE_GROQ_MODELS, get_selected_groq_model, set_selected_groq_model
    from utils.groq_inference import check_groq_connection

    # Check if the "Advanced" button has been clicked
    if "show_advanced" not in st.session_state:
        st.session_state.show_advanced = False

    # Add the "Advanced" button
    if st.sidebar.button("Advanced"):
        st.session_state.show_advanced = not st.session_state.show_advanced

    # Render model selection only if "Advanced" is clicked
    if st.session_state.show_advanced:
        st.sidebar.markdown("### Model Settings")

        # Display available Groq models
        st.sidebar.markdown("#### Available Groq Models")
        for model_id, model_info in AVAILABLE_GROQ_MODELS.items():
            st.sidebar.markdown(f"- **{model_info['name']}** ({model_id})")
            st.sidebar.markdown(f"  {model_info['description']}")

        st.sidebar.markdown("---")

        # Then show model selection dropdown
        st.sidebar.markdown("#### Select Model")
        current_model = get_selected_groq_model()
        model_list = list(AVAILABLE_GROQ_MODELS.keys())
        
        # Create display names for the selectbox
        model_options = [f"{AVAILABLE_GROQ_MODELS[m]['name']} ({m})" for m in model_list]
        current_index = model_list.index(current_model) if current_model in model_list else 0
        
        selected_option = st.sidebar.selectbox(
            "Choose model:",
            model_options,
            index=current_index,
            key="model_selector"
        )
        
        # Extract the model ID from the selected option
        selected_model = model_list[model_options.index(selected_option)]

        if selected_model != current_model:
            set_selected_groq_model(selected_model)
            st.sidebar.success(f"Model changed to {selected_model}")

        # Check Groq API status
        st.sidebar.markdown("### API Status")
        if check_groq_connection():
            st.sidebar.success("Groq API connected ✓")
        else:
            st.sidebar.error("Groq API not available ✗")

        st.sidebar.divider()


# Add this function to show in the about section or help
def render_groq_help():
    """Render help information for Groq API setup and status"""
    st.subheader("Groq API Status")

    try:
        from utils.groq_inference import check_groq_connection
        
        if check_groq_connection():
            st.success("✅ Connected to Groq API successfully")
            st.info("You can now simplify and translate legal documents using Groq's cloud models.")
        else:
            st.error("❌ Unable to connect to Groq API")

    except Exception as e:
        st.error(f"Error checking Groq API: {str(e)}")


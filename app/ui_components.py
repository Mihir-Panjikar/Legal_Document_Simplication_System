import streamlit as st
from app.session_manager import set_delete_dialog, reset_session
from app.database_operations import load_history_entry, perform_delete
from app.processors import process_simplification, process_translation
from utils.document_export import DocumentExporter
from datetime import datetime


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
        with col2:
            if st.button("Export Document"):
                st.session_state.show_export_options = True

    if st.session_state.translated_text:
        st.markdown(
            f"### Translated Text ({st.session_state.selected_language}):")
        st.write(st.session_state.translated_text)

    # Show export options if the button was clicked
    if st.session_state.get("show_export_options", False) and st.session_state.simplified_text:
        render_export_options(db)


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

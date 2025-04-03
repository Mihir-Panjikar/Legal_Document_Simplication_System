import streamlit as st
from app.session_manager import initialize_session_state
from app.database_operations import get_database
from app.ui_components import (
    render_delete_dialog,
    render_history_sidebar,
    render_input_area,
    render_output_area,
    render_ollama_help  # Add this import
)


def main():
    """Main application entry point"""
    # Page setup
    st.set_page_config(
        page_title="Legal Document Simplifier (Ollama)", layout="wide")

    # Initialize database
    db = get_database()

    # Initialize session state
    initialize_session_state()

    # Set page title
    st.title("Legal Document Simplification System")
    st.markdown("##### Using Ollama for local AI processing")

    # Show delete confirmation dialog if needed - MOVED UP before any other UI components
    if st.session_state.show_delete_dialog:
        render_delete_dialog(db)

    # Create layout columns
    col1, col2 = st.columns([1, 3])

    # Render sidebar and main content
    with col1:
        render_history_sidebar(db)

    with col2:
        render_input_area(db)
        render_output_area(db)

        # Add Ollama help at the bottom
        st.markdown("---")
        render_ollama_help()


if __name__ == "__main__":
    main()

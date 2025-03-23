import streamlit as st
from utils.Simplification import simplify_document
from utils.translation import translate_text
import asyncio

# Streamlit UI
st.set_page_config(page_title="Legal Document Simplifier", layout="wide")
st.markdown("""
    <style>
        .reportview-container {
            background-color: #1e1e1e;
        }
        .sidebar .sidebar-content {
            background-color: #333333;
        }
        .css-18e3th9 {
            background-color: #2c2c2c;
        }
    </style>
    """, unsafe_allow_html=True)

st.title("Legal Document Simplification System")
st.markdown("##### Please enter the legal text for simplification")

# Layout: left for history and right for input and output
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("History")
    # Simple history buttons; you can enhance this to save previous inputs
    history_items = ["Previous Input 1", "Previous Input 2", "Previous Input 3"]
    for item in history_items:
        if st.button(item, key=item):
            st.session_state.input_text = item

with col2:
    if "input_text" not in st.session_state:
        st.session_state.input_text = ""
    user_input = st.text_area("Enter legal document text here:", height=300, value=st.session_state.input_text)
    
    if st.button("Simplify"):
        if user_input.strip() == "":
            st.error("Please enter some text to simplify.")
        else:
            with st.spinner("Simplifying..."):
                simplified_output = simplify_document(user_input)
            st.markdown("### Simplified Text:")
            st.write(simplified_output)
            
            language = st.selectbox("Translate to:", ["None", "Hindi", "Marathi"], index=0)
            
            if language != "None":
                lang_code = "hi" if language == "Hindi" else "mr"
                with st.spinner(f"Translating to {language}..."):
                    translated_output = asyncio.run(translate_text(simplified_output, src="en", dest=lang_code))
                st.markdown(f"### Translated Text ({language}):")
                st.write(translated_output)

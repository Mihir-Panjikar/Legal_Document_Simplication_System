import streamlit as st
from utils.Simplification import simplify_document
from utils.translation import translate_text
import asyncio

# Streamlit UI
st.set_page_config(page_title="Legal Document Simplifier", layout="wide")

st.title("Legal Document Simplification System")
st.markdown("##### Please enter the legal text for simplification")

col1, col2 = st.columns([1, 3])

# Initialize session state
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "simplified_text" not in st.session_state:
    st.session_state.simplified_text = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

with col1:
    st.subheader("History")
    history_items = ["Previous Input 1", "Previous Input 2", "Previous Input 3"]
    for item in history_items:
        if st.button(item, key=item):
            st.session_state.input_text = item

with col2:
    user_input = st.text_area("Enter legal document text here:", height=300, value=st.session_state.input_text)
    
    if st.button("Simplify"):
        if user_input.strip() == "":
            st.error("Please enter some text to simplify.")
        else:
            with st.spinner("Simplifying..."):
                st.session_state.simplified_text = simplify_document(user_input)
    
    if st.session_state.simplified_text:
        st.markdown("### Simplified Text:")
        st.write(st.session_state.simplified_text)
        
        language = st.selectbox("Translate to:", ["None", "Hindi", "Marathi"], index=0, key="lang_select")
        
        if language != "None":
            lang_code = "hi" if language == "Hindi" else "mr"
            if st.button("Translate"):
                with st.spinner(f"Translating to {language}..."):
                    st.session_state.translated_text = asyncio.run(
                        translate_text(st.session_state.simplified_text, src="en", dest=lang_code)
                    )
    
    if st.session_state.translated_text:
        st.markdown(f"### Translated Text ({language}):")
        st.write(st.session_state.translated_text)
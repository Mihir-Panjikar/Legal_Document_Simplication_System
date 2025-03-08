import streamlit as st

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

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("History")
    history_items = ["Previous Input 1", "Previous Input 2", "Previous Input 3"]
    for item in history_items:
        st.button(item, key=item)

with col2:
    input_text = st.text_area(" ", height=300)

    if st.button("Simplify"):
        st.write("Simplified text will appear here.")

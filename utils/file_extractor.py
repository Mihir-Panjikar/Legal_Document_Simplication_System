import docx
import re
import streamlit as st
from io import BytesIO

def extract_text_from_txt(file_bytes):
    """Extract text from a .txt file"""
    try:
        text = file_bytes.decode('utf-8')
        return text
    except UnicodeDecodeError:
        # Try different encodings if UTF-8 fails
        try:
            text = file_bytes.decode('latin-1')
            return text
        except Exception as e:
            st.error(f"Error reading .txt file: {str(e)}")
            return None

def extract_text_from_docx(file_bytes):
    """Extract text from a .docx file"""
    try:
        doc = docx.Document(BytesIO(file_bytes))
        full_text = []
        
        # Extract text from paragraphs
        for para in doc.paragraphs:
            if para.text.strip():  # Skip empty paragraphs
                full_text.append(para.text)
        
        # Add double linebreaks between paragraphs for readability
        return '\n\n'.join(full_text)
    except Exception as e:
        st.error(f"Error reading .docx file: {str(e)}")
        return None

def extract_text_from_pdf(file_bytes):
    """Extract text from a .pdf file"""
    try:
        # Install PyPDF2 if not already in requirements
        import PyPDF2
        from io import BytesIO
        
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = []
        
        # Extract text from each page
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text.append(page.extract_text())
        
        # Join all pages with double linebreaks
        return '\n\n'.join(text)
    except ImportError:
        st.error("PyPDF2 is required for PDF extraction. Please install it using: pip install PyPDF2")
        return None
    except Exception as e:
        st.error(f"Error reading PDF file: {str(e)}")
        return None

def extract_text_from_file(uploaded_file):
    """
    Extract text from uploaded file based on file type
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        str: Extracted text or None if extraction failed
    """
    if uploaded_file is None:
        return None
        
    # Read file bytes
    file_bytes = uploaded_file.read()
    file_type = uploaded_file.type
    file_name = uploaded_file.name
    
    # Extract text based on file type
    if file_type == "text/plain" or file_name.endswith('.txt'):
        return extract_text_from_txt(file_bytes)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or file_name.endswith('.docx'):
        return extract_text_from_docx(file_bytes)
    elif file_type == "application/pdf" or file_name.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    else:
        st.error(f"Unsupported file type: {file_type}. Please upload a .txt, .docx, or .pdf file.")
        return None
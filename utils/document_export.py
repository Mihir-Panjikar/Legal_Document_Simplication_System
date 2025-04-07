import os
import base64
from fpdf import FPDF
from docx import Document
import tempfile
import streamlit as st


class DocumentExporter:
    """Handles exporting documents in various formats"""

    @staticmethod
    def export_to_pdf(title, original_text, simplified_text, translated_text=None, language=None):
        """
        Export document content to PDF with Unicode support

        Args:
            title: Document title (will be converted to string)
            original_text: Original legal text (will be converted to string)
            simplified_text: Simplified text (will be converted to string)
            translated_text: Optional translated text (will be converted to string)
            language: Translation language if applicable (will be converted to string)

        Returns:
            bytes: PDF file as bytes

        Raises:
            Exception: If PDF generation fails
        """
        # Input validation
        if title is None:
            title = "Untitled"
        if original_text is None:
            original_text = ""
        if simplified_text is None:
            simplified_text = ""

        # Add this function to sanitize text
        def sanitize_text(text):
            """Replace Unicode characters with ASCII equivalents"""
            if text is None:
                return ""
            # Convert to string first
            text = str(text)
            # Replace common Unicode characters
            replacements = {
                '\u201c': '"',  # Left double quote
                '\u201d': '"',  # Right double quote
                '\u2018': "'",  # Left single quote
                '\u2019': "'",  # Right single quote
                '\u2013': '-',  # En dash
                '\u2014': '--', # Em dash
                '\u2026': '...', # Ellipsis
                '\u00a0': ' ',  # Non-breaking space
                # Add more replacements as needed
            }
            for unicode_char, ascii_char in replacements.items():
                text = text.replace(unicode_char, ascii_char)
            return text

        # Sanitize all text inputs
        title = sanitize_text(title)
        original_text = sanitize_text(original_text)
        simplified_text = sanitize_text(simplified_text)
        if translated_text is not None:
            translated_text = sanitize_text(translated_text)

        # Create a PDF with fpdf2
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=16)

        # Process text safely by ensuring string conversion
        def process_text_block(text, header):
            pdf.set_font("Helvetica", style="B", size=12)
            # Updated to fpdf2 syntax
            pdf.cell(0, 10, str(header), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", size=10)

            # Convert text to string and handle line breaks
            text_str = str(text) if text is not None else ""
            for line in text_str.split('\n'):
                while len(line) > 0:
                    chunk = line[:100]
                    line = line[100:]
                    # Updated to fpdf2 syntax
                    pdf.multi_cell(0, 5, str(chunk), new_x="LMARGIN", new_y="NEXT")

        # Title - updated to fpdf2 syntax
        pdf.cell(0, 10, "Legal Document Simplification", align="C", 
                new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=12)

        # Fix Unicode issues in title and ensure string
        safe_title = str(title)[:50] if title else "Untitled"
        pdf.cell(0, 10, f"Document: {safe_title}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Process each text block
        process_text_block(original_text, "Original Text:")
        pdf.ln(5)
        process_text_block(simplified_text, "Simplified Text:")

        # Handle translated text if available
        if translated_text and language:
            pdf.ln(5)
            process_text_block(translated_text, f"Translated Text ({str(language)}):")

        # Add timestamp with safe string conversion
        pdf.ln(10)
        pdf.set_font("Helvetica", size=8)
        timestamp = str(st.session_state.get('timestamp', 'N/A'))
        pdf.cell(0, 5, f"Generated on: {timestamp}", new_x="LMARGIN", new_y="NEXT")

        # Return PDF as bytes - fpdf2 handles encoding properly
        return pdf.output()

    @staticmethod
    def export_to_docx(title, original_text, simplified_text, translated_text=None, language=None):
        """
        Export document content to DOCX (Word) format
        """
        # Input validation
        if title is None:
            title = "Untitled"
        if original_text is None:
            original_text = ""
        if simplified_text is None:
            simplified_text = ""
        
        # Convert all inputs to strings
        title = str(title)
        original_text = str(original_text)
        simplified_text = str(simplified_text)
        if translated_text is not None:
            translated_text = str(translated_text)
        if language is not None:
            language = str(language)
        
        doc = Document()

        # Add title
        doc.add_heading("Legal Document Simplification", 0)
        doc.add_heading(f"Document: {title[:50]}", 1)

        # Original Text
        doc.add_heading("Original Text:", 2)
        doc.add_paragraph(original_text)

        # Simplified Text
        doc.add_heading("Simplified Text:", 2)
        doc.add_paragraph(simplified_text)

        # Translated Text (if available)
        if translated_text and language:
            doc.add_heading(f"Translated Text ({language}):", 2)
            doc.add_paragraph(translated_text)

        # Add timestamp
        timestamp = str(st.session_state.get('timestamp', 'N/A'))
        doc.add_paragraph(f"Generated on: {timestamp}").italic = True

        # Save to a BytesIO object
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            doc.save(tmp.name)
            tmp.seek(0)
            with open(tmp.name, "rb") as f:
                docx_bytes = f.read()

        # Clean up the temp file
        os.unlink(tmp.name)

        return docx_bytes

    @staticmethod
    def export_to_txt(title, original_text, simplified_text, translated_text=None, language=None):
        """
        Export document content to plain text
        """
        # Input validation
        if title is None:
            title = "Untitled"
        if original_text is None:
            original_text = ""
        if simplified_text is None:
            simplified_text = ""
        
        # Convert all inputs to strings
        title = str(title)
        original_text = str(original_text)
        simplified_text = str(simplified_text)
        if translated_text is not None:
            translated_text = str(translated_text)
        if language is not None:
            language = str(language)
        
        content = []
        content.append("LEGAL DOCUMENT SIMPLIFICATION")
        content.append(f"Document: {title}\n")

        content.append("ORIGINAL TEXT:")
        content.append(original_text)
        content.append("")

        content.append("SIMPLIFIED TEXT:")
        content.append(simplified_text)
        content.append("")

        if translated_text and language:
            content.append(f"TRANSLATED TEXT ({language}):")
            content.append(translated_text)
            content.append("")

        timestamp = str(st.session_state.get('timestamp', 'N/A'))
        content.append(f"Generated on: {timestamp}")

        # Join with newlines and convert to bytes
        return "\n".join(content).encode("utf-8")

    @staticmethod
    def get_download_link(file_bytes, filename, file_format, display_text):
        """
        Generate a download link for a file

        Args:
            file_bytes: File content as bytes
            filename: Name of the file
            file_format: Format/extension of the file
            display_text: Text to display for the download link

        Returns:
            str: HTML for download link
        """
        # Ensure all inputs are strings
        filename = str(filename) if filename is not None else "document"
        file_format = str(file_format) if file_format is not None else "txt"
        display_text = str(display_text) if display_text is not None else "Download"
        
        b64 = base64.b64encode(file_bytes).decode()

        # Map format to MIME type
        mime_types = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain"
        }
        mime_type = mime_types.get(file_format, "application/octet-stream")

        href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}.{file_format}">{display_text}</a>'
        return href

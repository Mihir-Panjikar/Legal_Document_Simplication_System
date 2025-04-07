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
        Export document content to PDF

        Args:
            title: Document title
            original_text: Original legal text
            simplified_text: Simplified text
            translated_text: Optional translated text
            language: Translation language if applicable

        Returns:
            bytes: PDF file as bytes
        """
        pdf = FPDF()
        pdf.add_page()

        # Set up fonts - default is Helvetica
        pdf.set_font("Arial", "B", 16)

        # Title
        pdf.cell(0, 10, "Legal Document Simplification", ln=True, align="C")
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Document: {title[:50]}", ln=True)
        pdf.ln(5)

        # Original Text
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Original Text:", ln=True)
        pdf.set_font("Arial", "", 10)

        # Handle multiline text
        original_text_lines = original_text.split('\n')
        for line in original_text_lines:
            # Process line in chunks to avoid overflow
            while len(line) > 0:
                chunk = line[:100]  # Take first 100 chars
                line = line[100:]   # Remove processed chunk
                pdf.multi_cell(0, 5, chunk)

        pdf.ln(5)

        # Simplified Text
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Simplified Text:", ln=True)
        pdf.set_font("Arial", "", 10)

        simplified_text_lines = simplified_text.split('\n')
        for line in simplified_text_lines:
            while len(line) > 0:
                chunk = line[:100]
                line = line[100:]
                pdf.multi_cell(0, 5, chunk)

        # Translated Text (if available)
        if translated_text and language:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Translated Text ({language}):", ln=True)
            pdf.set_font("Arial", "", 10)

            translated_text_lines = translated_text.split('\n')
            for line in translated_text_lines:
                while len(line) > 0:
                    chunk = line[:100]
                    line = line[100:]
                    pdf.multi_cell(0, 5, chunk)

        # Add timestamp
        pdf.ln(10)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(
            0, 5, f"Generated on: {st.session_state.get('timestamp', 'N/A')}", ln=True)

        # Return PDF as bytes
        return pdf.output(dest="S")

    @staticmethod
    def export_to_docx(title, original_text, simplified_text, translated_text=None, language=None):
        """
        Export document content to DOCX (Word) format

        Args:
            title: Document title
            original_text: Original legal text
            simplified_text: Simplified text
            translated_text: Optional translated text
            language: Translation language if applicable

        Returns:
            bytes: DOCX file as bytes
        """
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
        doc.add_paragraph(
            f"Generated on: {st.session_state.get('timestamp', 'N/A')}").italic = True

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

        Args:
            title: Document title
            original_text: Original legal text
            simplified_text: Simplified text
            translated_text: Optional translated text
            language: Translation language if applicable

        Returns:
            bytes: Text file as bytes
        """
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

        content.append(
            f"Generated on: {st.session_state.get('timestamp', 'N/A')}")

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

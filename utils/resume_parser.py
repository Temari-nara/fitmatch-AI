"""
resume_parser.py — Extract text from a PDF file or plain text input.

Uses PyMuPDF (imported as 'fitz') to read PDF files.
PyMuPDF is fast and doesn't need any external tools like Tesseract.
"""

import fitz  # PyMuPDF — install with: pip install pymupdf


def extract_text_from_pdf(pdf_file) -> str:
    """
    Read a PDF file and return all text content as a single string.

    Args:
        pdf_file: A file-like object (e.g. from Streamlit's file_uploader).

    Returns:
        Extracted text from all pages joined together.
        Returns an error message string if something goes wrong.
    """
    try:
        # Read the raw bytes from the uploaded file
        pdf_bytes = pdf_file.read()

        # Open the PDF from bytes (not a file path)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        text = ""
        # Loop through each page and grab the text
        for page in doc:
            text += page.get_text()

        doc.close()

        # If no text was found, the PDF might be a scanned image
        if not text.strip():
            return "[No text found — the PDF might be a scanned image. Try pasting your resume as text instead.]"

        return text.strip()

    except Exception as e:
        return f"[Error reading PDF: {e}]"


def clean_text(text: str) -> str:
    """
    Basic cleanup of extracted or pasted resume text.

    Removes extra blank lines and leading/trailing whitespace.
    This makes the text cleaner before sending it to the LLM.

    Args:
        text: Raw resume text.

    Returns:
        Cleaned-up text string.
    """
    # Split into lines, remove blank ones, rejoin
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

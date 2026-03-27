"""
pdf_generator.py — Generate a clean PDF from resume text.

Uses fpdf2 library (free, pure Python, no external dependencies).
Install with: pip install fpdf2
"""

from fpdf import FPDF


def sanitize_text(text: str) -> str:
    """
    Replace Unicode characters that the default Latin-1 font can't render.

    FPDF's built-in fonts (Helvetica, Arial) only support Latin-1 encoding.
    Characters like em-dash, bullet, smart quotes etc. must be replaced.

    Args:
        text: The raw text string.

    Returns:
        Cleaned text safe for FPDF rendering.
    """
    replacements = {
        "\u2013": "-",   # en-dash
        "\u2014": "-",   # em-dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2022": "*",   # bullet point
        "\u2026": "...", # ellipsis
        "\u00a0": " ",   # non-breaking space
        "\u200b": "",    # zero-width space
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    # Remove any remaining non-Latin-1 characters
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text


def generate_pdf(resume_text: str) -> bytes:
    """
    Convert plain resume text into a compact, professional PDF.
    Optimized to fit a resume within 1-2 pages max.

    Args:
        resume_text: The resume content as a string.

    Returns:
        PDF file as bytes (ready for Streamlit's download_button).
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    # Tighter margins — more usable space on the page
    pdf.set_left_margin(12)
    pdf.set_right_margin(12)
    pdf.set_top_margin(10)
    pdf.add_page()

    # Smaller font = more content per page
    pdf.set_font("Helvetica", size=10)

    for line in resume_text.split("\n"):
        stripped = sanitize_text(line.strip())

        if not stripped:
            # Minimal blank-line gap (just 2mm instead of 4)
            pdf.ln(2)
            continue

        # Reset X to left margin before every line
        pdf.set_x(pdf.l_margin)

        # Detect section headers (ALL CAPS lines or lines ending with ':')
        if stripped.isupper() or stripped.endswith(":"):
            pdf.set_font("Helvetica", style="B", size=11)
            pdf.ln(2)  # Small gap before header
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=0, h=5, text=stripped)
            pdf.set_font("Helvetica", size=10)
        else:
            # Tight line height (5mm) keeps resume compact
            pdf.multi_cell(w=0, h=5, text=stripped)

    return bytes(pdf.output())

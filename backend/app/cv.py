from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(data: bytes) -> str:
    """Pull the plain text out of an uploaded PDF CV."""
    reader = PdfReader(BytesIO(data))
    # Join every page's text; extract_text() can return None, so default to "".
    return "\n".join(page.extract_text() or "" for page in reader.pages)

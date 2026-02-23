import fitz  # PyMuPDF
import re


def extract_text(pdf_file) -> str:
    """
    Extracts and cleans text from an uploaded PDF file.
    
    Args:
        pdf_file: A file-like object (from st.file_uploader)
    
    Returns:
        A clean string of all text from the PDF
    """
    try:
        # Read bytes from the uploaded file
        pdf_bytes = pdf_file.read()

        # Open PDF from bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        all_text = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            all_text.append(text)

        doc.close()

        # Merge all pages
        full_text = "\n".join(all_text)

        # Clean up the text
        full_text = clean_text(full_text)

        return full_text

    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def clean_text(text: str) -> str:
    """
    Cleans extracted PDF text by removing excessive whitespace and artifacts.
    
    Args:
        text: Raw extracted text
    
    Returns:
        Cleaned text string
    """
    # Replace multiple newlines with double newline
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]{2,}', ' ', text)

    # Remove non-printable characters (except newlines and tabs)
    text = re.sub(r'[^\x20-\x7E\n\t]', '', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def get_page_count(pdf_file) -> int:
    """
    Returns the number of pages in a PDF.
    
    Args:
        pdf_file: A file-like object
    
    Returns:
        Number of pages as int
    """
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    count = len(doc)
    doc.close()
    pdf_file.seek(0)  # Reset file pointer for later use
    return count
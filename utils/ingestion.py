
import os
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io

def read_pdf(file_bytes):
    """Extract text from PDF bytes."""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        text = f"Error reading PDF: {e}"
    return text

def read_website(url):
    """Extract text from a website."""
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        return f"Error reading website: {e}"

def read_text_file(file_bytes):
    """Read plain text file."""
    try:
        return file_bytes.decode('utf-8')
    except:
        return file_bytes.decode('latin-1')

def ingest_file(file_bytes, file_name):
    """Determine file type and extract text."""
    if file_name.lower().endswith('.pdf'):
        return read_pdf(file_bytes)
    elif file_name.lower().endswith('.txt'):
        return read_text_file(file_bytes)
    else:
        return "Unsupported file type"

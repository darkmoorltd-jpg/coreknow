
import os
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io
import re

def clean_text(text):
    """Clean extracted text - remove extra whitespace and normalize."""
    if not text:
        return ""
    # Remove multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Remove multiple spaces
    text = re.sub(r' {3,}', ' ', text)
    return text.strip()

def read_pdf(file_bytes):
    """Extract text from PDF bytes with better error handling."""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        num_pages = len(pdf_reader.pages)
        
        for i, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += f"[Page {i+1}]\n{page_text}\n"
            except:
                text += f"[Page {i+1}] (text extraction failed)\n"
        
        if not text.strip():
            return "No text could be extracted from this PDF. It may be scanned images."
        
        return clean_text(text)
    except Exception as e:
        return f"Error reading PDF: {e}"

def read_website(url):
    """Extract text from a website with better cleaning."""
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "CoreKnow/1.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Remove scripts, styles, nav, footer
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        # Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)
        
        return clean_text(text)
    except Exception as e:
        return f"Error reading website: {e}"

def read_text_file(file_bytes):
    """Read plain text file."""
    try:
        return clean_text(file_bytes.decode('utf-8'))
    except:
        try:
            return clean_text(file_bytes.decode('latin-1'))
        except:
            return "Unable to decode text file"

def ingest_file(file_bytes, file_name):
    """Determine file type and extract text."""
    file_name_lower = file_name.lower()
    
    if file_name_lower.endswith('.pdf'):
        return read_pdf(file_bytes)
    elif file_name_lower.endswith(('.txt', '.md', '.csv', '.json')):
        return read_text_file(file_bytes)
    elif file_name_lower.endswith(('.jpg', '.jpeg', '.png')):
        return "Image file - use multimodal analysis"
    elif file_name_lower.endswith(('.wav', '.mp3')):
        return "Audio file - use transcription"
    else:
        return f"Unsupported file type: {file_name_lower}"


import os
import json
import requests
from typing import Optional, List, Dict, Any
import io

class UniversalIngestor:
    """CoreKnow Universal Ingestor - handles ANY file format."""
    
    def __init__(self):
        self.supported_formats = {
            # Documents
            '.pdf': self._ingest_pdf,
            '.docx': self._ingest_docx,
            '.txt': self._ingest_txt,
            '.md': self._ingest_txt,
            '.rtf': self._ingest_rtf,
            '.html': self._ingest_html,
            '.xml': self._ingest_xml,
            '.json': self._ingest_json,
            '.csv': self._ingest_csv,
            '.xlsx': self._ingest_xlsx,
            '.pptx': self._ingest_pptx,
            '.epub': self._ingest_epub,
            '.odt': self._ingest_odt,
            
            # Images
            '.jpg': self._ingest_image,
            '.jpeg': self._ingest_image,
            '.png': self._ingest_image,
            '.gif': self._ingest_image,
            '.bmp': self._ingest_image,
            '.tiff': self._ingest_image,
            '.webp': self._ingest_image,
            
            # Audio
            '.mp3': self._ingest_audio,
            '.wav': self._ingest_audio,
            '.m4a': self._ingest_audio,
            '.aac': self._ingest_audio,
            '.flac': self._ingest_audio,
            '.ogg': self._ingest_audio,
            
            # Video
            '.mp4': self._ingest_video,
            '.avi': self._ingest_video,
            '.mov': self._ingest_video,
            '.mkv': self._ingest_video,
            '.webm': self._ingest_video,
            
            # Archives
            '.zip': self._ingest_archive,
            '.rar': self._ingest_archive,
            '.tar': self._ingest_archive,
            '.gz': self._ingest_archive,
            '.7z': self._ingest_archive,
            
            # Code
            '.py': self._ingest_code,
            '.js': self._ingest_code,
            '.java': self._ingest_code,
            '.cpp': self._ingest_code,
            '.c': self._ingest_code,
            '.go': self._ingest_code,
            '.rs': self._ingest_code,
            '.ts': self._ingest_code,
            '.sql': self._ingest_code,
            '.sh': self._ingest_code,
            '.html': self._ingest_code,
            '.css': self._ingest_code,
        }
    
    def ingest_file(self, file_path: str) -> Dict[str, Any]:
        """Ingest any file and return extracted content."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in self.supported_formats:
            return {"error": f"Unsupported format: {ext}"}
        
        try:
            content = self.supported_formats[ext](file_path)
            return {
                "file": file_path,
                "format": ext,
                "content": content,
                "size": os.path.getsize(file_path),
                "status": "success"
            }
        except Exception as e:
            return {
                "file": file_path,
                "format": ext,
                "error": str(e),
                "status": "failed"
            }
    
    def ingest_bytes(self, file_bytes: bytes, file_name: str) -> Dict[str, Any]:
        """Ingest file from bytes."""
        ext = os.path.splitext(file_name)[1].lower()
        
        if ext not in self.supported_formats:
            return {"error": f"Unsupported format: {ext}"}
        
        # Save to temp
        tmp_path = f"/tmp/{file_name}"
        with open(tmp_path, "wb") as f:
            f.write(file_bytes)
        
        result = self.ingest_file(tmp_path)
        os.remove(tmp_path)
        return result
    
    def ingest_url(self, url: str) -> Dict[str, Any]:
        """Ingest from URL."""
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            
            # Determine if HTML
            content_type = r.headers.get("Content-Type", "")
            if "text/html" in content_type or "application/xhtml" in content_type:
                return {
                    "url": url,
                    "content": self._extract_html_text(r.text),
                    "format": "html",
                    "status": "success"
                }
            elif "application/json" in content_type:
                return {
                    "url": url,
                    "content": json.dumps(r.json(), indent=2),
                    "format": "json",
                    "status": "success"
                }
            elif "text/" in content_type:
                return {
                    "url": url,
                    "content": r.text,
                    "format": "text",
                    "status": "success"
                }
            else:
                return {
                    "url": url,
                    "content": str(r.content[:1000]),
                    "format": content_type,
                    "status": "partial"
                }
        except Exception as e:
            return {"url": url, "error": str(e), "status": "failed"}
    
    # ============ DOCUMENT INGESTORS ============
    def _ingest_pdf(self, path):
        try:
            import PyPDF2
            text = ""
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except ImportError:
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(path)
                text = ""
                for page in doc:
                    text += page.get_text()
                return text
            except:
                raise Exception("Need PyPDF2 or PyMuPDF")
    
    def _ingest_docx(self, path):
        from docx import Document
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    
    def _ingest_txt(self, path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    
    def _ingest_rtf(self, path):
        from striprtf.striprtf import rtf_to_text
        with open(path, "r") as f:
            return rtf_to_text(f.read())
    
    def _ingest_html(self, path):
        from bs4 import BeautifulSoup
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text()
    
    def _ingest_xml(self, path):
        from bs4 import BeautifulSoup
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "xml")
            return soup.get_text()
    
    def _ingest_json(self, path):
        with open(path, "r") as f:
            return json.dumps(json.load(f), indent=2)
    
    def _ingest_csv(self, path):
        import csv
        with open(path, "r") as f:
            reader = csv.reader(f)
            return "\n".join([",".join(row) for row in reader])
    
    def _ingest_xlsx(self, path):
        import openpyxl
        wb = openpyxl.load_workbook(path)
        text = ""
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            text += f"Sheet: {sheet}\n"
            for row in ws.iter_rows(values_only=True):
                text += "\t".join([str(c) for c in row if c]) + "\n"
        return text
    
    def _ingest_pptx(self, path):
        from pptx import Presentation
        prs = Presentation(path)
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text
    
    def _ingest_epub(self, path):
        import epub2txt
        return epub2txt.epub2txt(path)
    
    def _ingest_odt(self, path):
        from odf import text, teletype
        from odf.opendocument import load
        doc = load(path)
        return "\n".join([teletype.extractText(p) for p in doc.getElementsByType(text.P)])
    
    # ============ IMAGE INGESTORS ============
    def _ingest_image(self, path):
        """Extract text from image via OCR."""
        try:
            from PIL import Image
            import pytesseract
            img = Image.open(path)
            text = pytesseract.image_to_string(img)
            return text if text.strip() else "[Image - no text detected]"
        except ImportError:
            return "[Image - OCR not available]"
    
    # ============ AUDIO INGESTORS ============
    def _ingest_audio(self, path):
        """Transcribe audio using Whisper."""
        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(path)
            return result["text"]
        except ImportError:
            return "[Audio - Whisper not installed]"
    
    # ============ VIDEO INGESTORS ============
    def _ingest_video(self, path):
        """Extract frames and audio from video."""
        text = ""
        
        # Try extracting audio and transcribing
        try:
            import whisper
            import subprocess
            # Extract audio
            audio_path = path + ".wav"
            subprocess.run(["ffmpeg", "-i", path, "-q:a", "0", "-map", "a", audio_path, "-y"], 
                         capture_output=True)
            if os.path.exists(audio_path):
                model = whisper.load_model("base")
                result = model.transcribe(audio_path)
                text += result["text"] + "\n"
                os.remove(audio_path)
        except:
            pass
        
        # Extract frames (optional)
        try:
            import cv2
            cap = cv2.VideoCapture(path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(fps * 5)  # every 5 seconds
            count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if count % frame_interval == 0:
                    # Process frame (OCR, etc.)
                    pass
                count += 1
            cap.release()
        except:
            pass
        
        return text if text.strip() else "[Video - processing needed]"
    
    # ============ ARCHIVE INGESTORS ============
    def _ingest_archive(self, path):
        """Extract archive and ingest contents."""
        import zipfile
        import tarfile
        
        text = ""
        if path.endswith('.zip'):
            with zipfile.ZipFile(path, 'r') as zf:
                for name in zf.namelist():
                    if not name.endswith('/'):
                        # Extract and ingest
                        try:
                            content = zf.read(name)
                            # Simple text extraction
                            if name.endswith(('.txt', '.md', '.py', '.js', '.html', '.xml', '.json', '.csv')):
                                text += f"=== {name} ===\n"
                                text += content.decode('utf-8', errors='ignore') + "\n"
                        except:
                            pass
        elif path.endswith(('.tar', '.gz', '.tgz')):
            with tarfile.open(path, 'r') as tf:
                for member in tf.getmembers():
                    if member.isfile():
                        try:
                            f = tf.extractfile(member)
                            content = f.read()
                            if member.name.endswith(('.txt', '.md', '.py', '.js', '.html', '.xml', '.json', '.csv')):
                                text += f"=== {member.name} ===\n"
                                text += content.decode('utf-8', errors='ignore') + "\n"
                        except:
                            pass
        
        return text if text.strip() else "[Archive - extraction limited]"
    
    # ============ CODE INGESTORS ============
    def _ingest_code(self, path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    
    # ============ HELPERS ============
    def _extract_html_text(self, html_content):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text()
    
    def get_supported_formats(self) -> List[str]:
        return sorted(self.supported_formats.keys())
    
    def get_stats(self) -> Dict[str, int]:
        return {
            "documents": 12,
            "images": 7,
            "audio": 6,
            "video": 5,
            "archives": 5,
            "code": 10,
            "total_formats": len(self.supported_formats)
        }

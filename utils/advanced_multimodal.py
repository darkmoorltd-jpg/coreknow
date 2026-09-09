
import os
import io
import re
import json
import base64
import subprocess
import tempfile
from typing import Dict, Any, List, Optional
from supabase import create_client
import streamlit as st

# Optional imports with fallbacks
try:
    import pdfplumber
except:
    pdfplumber = None

try:
    import camelot
    HAS_CAMELOT = True
except:
    HAS_CAMELOT = False

try:
    from PIL import Image
    import cv2
    import pytesseract
    HAS_OCR = True
except:
    HAS_OCR = False

try:
    from rdkit import Chem
    HAS_RDKIT = True
except:
    HAS_RDKIT = False

try:
    from plotdigitizer import PlotDigitizer
    HAS_PLOTDIGITIZER = True
except:
    HAS_PLOTDIGITIZER = False

class AdvancedMultiModalExtractor:
    def __init__(self):
        self.supabase = None
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["service_key"]
            self.supabase = create_client(url, key)
        except:
            pass

    def extract_from_pdf(self, file_bytes: bytes) -> Dict[str, Any]:
        result = {
            "text": "",
            "tables": [],
            "images": [],
            "formulas": [],
            "graphs_data": [],
            "metadata": {},
        }

        # Text extraction
        if pdfplumber:
            try:
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    full_text = []
                    for page_num, page in enumerate(pdf.pages, 1):
                        page_text = page.extract_text() or ""
                        full_text.append(f"[Page {page_num}]\n{page_text}")
                    result["text"] = "\n".join(full_text)
            except:
                pass

        # Table extraction: Camelot first, fallback to pdfplumber
        if HAS_CAMELOT:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                    tmp_pdf.write(file_bytes)
                    tmp_pdf_path = tmp_pdf.name
                tables = camelot.read_pdf(tmp_pdf_path, pages="all", flavor="lattice")
                for table in tables:
                    result["tables"].append({
                        "page": table.page,
                        "rows": table.df.values.tolist(),
                        "source": "camelot",
                    })
                os.unlink(tmp_pdf_path)
            except:
                pass

        if not result["tables"] and pdfplumber:
            try:
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    for page_num, page in enumerate(pdf.pages, 1):
                        tables = page.extract_tables()
                        for table in tables:
                            if table:
                                result["tables"].append({
                                    "page": page_num,
                                    "rows": table,
                                    "source": "pdfplumber",
                                })
            except:
                pass

        # Image extraction
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page_num in range(len(doc)):
                page = doc[page_num]
                images = page.get_images(full=True)
                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    b64 = base64.b64encode(image_bytes).decode()
                    result["images"].append({
                        "page": page_num + 1,
                        "index": img_index,
                        "data": b64,
                        "type": "unknown",
                    })
        except:
            pass

        # Formula extraction
        formulas = set()
        patterns = [
            r'\$[^$]+\$',
            r'[A-Za-z]+\s*=\s*[A-Za-z0-9\^\+\-\*\/\(\)\.]+',
            r'\b[A-Z][a-z]?\d*[A-Z][a-z]?\d*\b',
        ]
        for p in patterns:
            found = re.findall(p, result["text"], re.DOTALL)
            for f in found:
                formulas.add(f.strip())
        result["formulas"] = list(formulas)[:100]

        # Graph data extraction
        if HAS_PLOTDIGITIZER:
            for img_info in result["images"]:
                img_bytes = base64.b64decode(img_info["data"])
                pil_img = Image.open(io.BytesIO(img_bytes))
                try:
                    pd = PlotDigitizer(pil_img)
                    data_points = pd.get_data()
                    if data_points:
                        result["graphs_data"].append({
                            "page": img_info["page"],
                            "image_index": img_info["index"],
                            "data_points": data_points,
                        })
                        img_info["type"] = "graph"
                except:
                    pass

        return result

    def extract_smiles_from_image(self, image_bytes: bytes) -> Optional[str]:
        # Try OSRA binary
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            result = subprocess.run(["osra", tmp_path], capture_output=True, text=True, timeout=30)
            os.unlink(tmp_path)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None

    def caption_image(self, image_bytes: bytes) -> str:
        """Generate caption using BLIP if available."""
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            inputs = processor(image, return_tensors="pt")
            out = model.generate(**inputs)
            caption = processor.decode(out[0], skip_special_tokens=True)
            return caption
        except:
            return ""

    def process_and_store(self, file_bytes, file_name) -> Dict[str, Any]:
        ext = os.path.splitext(file_name)[1].lower()
        if ext == '.pdf':
            extracted = self.extract_from_pdf(file_bytes)
        else:
            try:
                text = file_bytes.decode('utf-8', errors='ignore')
            except:
                text = str(file_bytes[:1000])
            extracted = {
                "text": text,
                "tables": [],
                "images": [],
                "formulas": [],
                "graphs_data": [],
            }

        # Store document metadata
        doc_id = None
        if self.supabase:
            try:
                doc_res = self.supabase.table("coreknow_documents").insert({
                    "name": file_name,
                    "format": ext,
                    "content": extracted["text"][:5000],
                }).execute()
                doc_id = doc_res.data[0]["id"]
            except Exception as e:
                print(f"Document insert error: {e}")

        # Store components
        if doc_id:
            if extracted["text"]:
                self.store_component(doc_id, "text", {"content": extracted["text"]})
            for table in extracted["tables"]:
                self.store_component(doc_id, "table", table)
            if extracted["formulas"]:
                self.store_component(doc_id, "formulas", {"formulas": extracted["formulas"]})
            for img_info in extracted["images"]:
                smiles = self.extract_smiles_from_image(base64.b64decode(img_info["data"]))
                caption = self.caption_image(base64.b64decode(img_info["data"]))
                img_info["smiles"] = smiles
                img_info["caption"] = caption
                self.store_component(doc_id, "image", img_info)
            for graph in extracted["graphs_data"]:
                self.store_component(doc_id, "graph_data", graph)

        return extracted

    def store_component(self, doc_id, component_type, content):
        if not self.supabase:
            return False
        try:
            self.supabase.table("coreknow_document_components").insert({
                "document_id": doc_id,
                "component_type": component_type,
                "content": json.dumps(content),
            }).execute()
            return True
        except Exception as e:
            print(f"Store component error: {e}")
            return False

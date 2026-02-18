import io
import os
from typing import Tuple

from pypdf import PdfReader

# OCR deps
from pdf2image import convert_from_bytes
import pytesseract


def extract_text_from_pdf_bytes(pdf_bytes: bytes, max_pages: int | None = None) -> Tuple[str, bool]:
    """
    Returns: (text, ocr_used)
    """
    # 1) Try standard text extraction
    text = _extract_with_pypdf(pdf_bytes, max_pages=max_pages)

    # If enough text, stop here
    if _is_text_good_enough(text):
        return text, False

    # 2) Fallback OCR
    ocr_text = _extract_with_ocr(pdf_bytes, max_pages=max_pages)
    if _is_text_good_enough(ocr_text):
        return ocr_text, True

    # If still empty => raise
    raise ValueError("Aucun texte extractible (même après OCR).")


def _extract_with_pypdf(pdf_bytes: bytes, max_pages: int | None = None) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    if not reader.pages:
        return ""

    n_pages = len(reader.pages)
    limit = min(n_pages, max_pages) if max_pages else n_pages

    parts: list[str] = []
    for i in range(limit):
        page_text = (reader.pages[i].extract_text() or "").strip()
        parts.append(f"\n\n--- Page {i+1}/{n_pages} ---\n{page_text}")

    return "\n".join(parts).strip()


def _extract_with_ocr(pdf_bytes: bytes, max_pages: int | None = None) -> str:
    """
    OCR pipeline: PDF bytes -> images -> pytesseract
    Requires:
      - Tesseract installed
      - Poppler installed (Windows) OR available in PATH
    Optional env:
      - TESSERACT_CMD (path to tesseract.exe)
      - POPPLER_PATH (path to poppler bin folder containing pdftoppm.exe)
    """
    tess_cmd = os.getenv("TESSERACT_CMD")
    if tess_cmd:
        pytesseract.pytesseract.tesseract_cmd = tess_cmd

    poppler_path = os.getenv("POPPLER_PATH")  # e.g. C:\poppler\Library\bin

    # Convert pages to PIL images
    images = convert_from_bytes(
        pdf_bytes,
        dpi=300,
        fmt="png",
        poppler_path=poppler_path
    )

    if max_pages:
        images = images[:max_pages]

    texts: list[str] = []
    total = len(images)

    for idx, img in enumerate(images, start=1):
        # lang: change to "eng" if needed, or "fra+eng"
        page_text = pytesseract.image_to_string(img, lang="fra")
        page_text = page_text.strip()
        texts.append(f"\n\n--- OCR Page {idx}/{total} ---\n{page_text}")

    return "\n".join(texts).strip()


def _is_text_good_enough(text: str) -> bool:
    if not text:
        return False
    cleaned = text.replace("-", "").strip()
    return len(cleaned) >= 30

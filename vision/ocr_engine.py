import pytesseract
from PIL import Image


def run_ocr(image, lang: str = "eng") -> str:
    """Return OCR text from ``image`` using Tesseract."""
    return pytesseract.image_to_string(image, lang=lang)

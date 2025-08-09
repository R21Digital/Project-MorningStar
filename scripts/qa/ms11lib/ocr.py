from __future__ import annotations

from typing import Optional

try:
    import pytesseract  # type: ignore
    from PIL import ImageGrab  # type: ignore
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False


def grab_text(region: Optional[tuple[int, int, int, int]] = None) -> str:
    if not OCR_AVAILABLE:
        return ""
    try:
        img = ImageGrab.grab(bbox=region)
        return pytesseract.image_to_string(img) or ""
    except Exception:
        return ""



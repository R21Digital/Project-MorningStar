import os
import sys
import types
from PIL import Image
import pytesseract

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide a dummy pyautogui module for headless testing
sys.modules['pyautogui'] = types.SimpleNamespace(
    screenshot=lambda *a, **k: Image.new("RGB", (100, 100), color="white")
)

from src.vision.ocr import screen_text


def test_screen_text_capture(monkeypatch):
    monkeypatch.setattr(pytesseract, "image_to_string", lambda img: "dummy text")
    text = screen_text()
    assert isinstance(text, str)
    print("[OCR TEST] Detected text sample:", text[:200])

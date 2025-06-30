import os
import sys
import types
from PIL import Image
import pytesseract
sys.modules['cv2'] = types.SimpleNamespace(COLOR_RGB2BGR=None, cvtColor=lambda img, flag: img)
fake_np = types.ModuleType('numpy')
fake_np.array = lambda x: x
fake_np.ndarray = object
sys.modules['numpy'] = fake_np


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

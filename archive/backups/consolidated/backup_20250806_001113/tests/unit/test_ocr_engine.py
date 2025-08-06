import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

pytest.importorskip("pytesseract")
import pytesseract

try:
    pytesseract.get_tesseract_version()
except Exception:
    pytest.skip("Tesseract binary is not installed", allow_module_level=True)

from vision.ocr_engine import run_ocr
from PIL import Image


def test_ocr_with_blank_image():
    img = Image.new('RGB', (100, 100), color='white')
    result = run_ocr(img)
    assert isinstance(result, str)

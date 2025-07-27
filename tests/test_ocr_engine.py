import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from vision.ocr_engine import run_ocr
from PIL import Image


def test_ocr_with_blank_image():
    img = Image.new('RGB', (100, 100), color='white')
    result = run_ocr(img)
    assert isinstance(result, str)

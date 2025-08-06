import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from vision.ocr_utils import clean_ocr_text


def test_clean_ocr_text_collapses_whitespace():
    text = " Hello\n\nWorld  from  OCR  "
    assert clean_ocr_text(text) == "Hello World from OCR"

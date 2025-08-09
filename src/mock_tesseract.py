
"""Mock Tesseract OCR for testing purposes."""
import logging

logger = logging.getLogger(__name__)

def get_tesseract_version():
    """Mock version."""
    return "5.3.0.20221214 (mock)"

def image_to_string(image, **kwargs):
    """Mock OCR - returns empty string."""
    logger.warning("Mock OCR: No text extracted (Tesseract not available)")
    return ""

def image_to_data(image, **kwargs):
    """Mock OCR data."""
    return {"text": "", "conf": 0.0}

import pytesseract
import cv2
import numpy as np
import pyautogui


def capture_screen(region=None) -> np.ndarray:
    """Capture the screen or region as an OpenCV image."""
    screenshot = pyautogui.screenshot(region=region)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def extract_text(image: np.ndarray) -> str:
    """Extract text from ``image`` using Tesseract OCR."""
    return pytesseract.image_to_string(image)


def screen_text(region=None) -> str:
    """Capture the screen and return OCR text."""
    img = capture_screen(region)
    return extract_text(img)

"""OCR helpers for detecting untrained skills in the trainer window."""

from __future__ import annotations

from typing import Iterable, List, Tuple

import numpy as np
from PIL import Image
import pytesseract

from utils.screen_capture import capture_screen_region


# Default region to scan if none is provided (left, top, width, height)
DEFAULT_TRAINER_REGION: Tuple[int, int, int, int] | None = None


def preprocess_image(image) -> np.ndarray:
    """Return a binarized grayscale ``numpy`` array suitable for OCR."""
    if isinstance(image, Image.Image):
        gray = image.convert("L")
        arr = np.array(gray)
    else:
        arr = np.array(image)
        if arr.ndim == 3:
            arr = arr.mean(axis=2)
    # simple threshold
    arr = np.where(arr > 150, 255, 0).astype("uint8")
    return arr


def extract_text_from_trainer_region(image) -> str:
    """Extract text from a trainer dialogue ``image``."""
    processed = preprocess_image(image)
    return pytesseract.image_to_string(processed)


def get_untrained_skills_from_text(text: str) -> List[str]:
    """Parse OCR ``text`` and return a list of untrained skill names."""
    skills: List[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if any(key in line.lower() for key in ["trained", "xp", ":"]):
            continue
        skills.append(line)
    return skills


def scan_and_detect_untrained_skills(
    region: Tuple[int, int, int, int] | None = DEFAULT_TRAINER_REGION,
) -> List[str]:
    """Capture ``region`` and return a list of untrained skills detected."""
    image = capture_screen_region(region)
    text = extract_text_from_trainer_region(image)
    return get_untrained_skills_from_text(text)

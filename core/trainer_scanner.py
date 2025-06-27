"""OCR utilities for scanning trainer skill lists."""

from __future__ import annotations

from typing import List, Tuple

import cv2
import numpy as np
import pyautogui
import pytesseract


# Default screen region for trainer skills (left, top, width, height)
DEFAULT_REGION: Tuple[int, int, int, int] | None = None


def scan_trainer_skills(region: Tuple[int, int, int, int] | None = DEFAULT_REGION) -> List[str]:
    """Capture ``region`` of the screen and return detected skill names."""
    screenshot = pyautogui.screenshot(region=region)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)
    _ignored, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh)
    skills: List[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            skills.append(line)
    return skills


class TrainerScanner:
    """Class wrapper around :func:`scan_trainer_skills`."""

    def __init__(self, region: Tuple[int, int, int, int] | None = DEFAULT_REGION) -> None:
        self.region = region

    def scan(self) -> List[str]:
        """Return detected trainer skills from :attr:`region`."""
        return scan_trainer_skills(self.region)

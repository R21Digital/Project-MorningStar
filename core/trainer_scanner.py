"""Utilities for OCR'ing skill lists from a trainer window.

This module exposes :func:`scan_trainer_skills` and a small :class:`TrainerScanner`
wrapper.  Both capture a region of the screen, apply simple thresholding and
pass the result through ``pytesseract`` to extract the names of skills the
trainer offers.
"""

from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np
import pyautogui
import pytesseract


# Default screen region for trainer skills (left, top, width, height)
DEFAULT_REGION: Tuple[int, int, int, int] | None = None


def scan_trainer_skills(region: Tuple[int, int, int, int] | None = DEFAULT_REGION) -> list[str]:
    """Capture ``region`` of the screen and return detected skill names.

    Parameters
    ----------
    region:
        Screen coordinates as ``(left, top, width, height)`` of the area to
        capture.  When ``None`` the entire screen is scanned.

    Returns
    -------
    list[str]
        Detected skill names in top-to-bottom order.
    """
    screenshot = pyautogui.screenshot(region=region)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)
    _ignored, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh)
    skills: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            skills.append(line)
    return skills


class TrainerScanner:
    """Class wrapper around :func:`scan_trainer_skills`."""

    def __init__(self, region: Tuple[int, int, int, int] | None = DEFAULT_REGION) -> None:
        self.region = region

    def scan(self) -> list[str]:
        """Return detected trainer skills from :attr:`region`."""
        return scan_trainer_skills(self.region)

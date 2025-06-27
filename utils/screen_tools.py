"""Tools for capturing and analyzing the in-game trainer window."""

from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np
import pyautogui
from PIL import Image


def capture_trainer_window(
    region: Tuple[int, int, int, int] | None = None,
) -> Image.Image:
    """Return a screenshot of the trainer window or ``region``.

    Parameters
    ----------
    region:
        Optional ``(left, top, width, height)`` tuple indicating the portion of
        the screen to capture.  When ``None`` the entire screen is captured.

    Returns
    -------
    PIL.Image.Image
        Screenshot image captured via ``pyautogui``.
    """
    return pyautogui.screenshot(region=region)


def locate_skill_boxes(image: Image.Image | np.ndarray) -> list[Tuple[int, int, int, int]]:
    """Locate skill box regions in ``image``.

    Parameters
    ----------
    image:
        Image of the trainer window. ``PIL`` images are converted to ``numpy``
        arrays automatically.

    Returns
    -------
    list[tuple[int, int, int, int]]
        Bounding boxes for detected skill boxes as ``(x, y, w, h)`` tuples.
    """
    if isinstance(image, Image.Image):
        arr = np.array(image)
    else:
        arr = image

    gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    _ignored, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ignored2 = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    boxes: list[Tuple[int, int, int, int]] = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 10 and h > 10:
            boxes.append((x, y, w, h))
    return boxes


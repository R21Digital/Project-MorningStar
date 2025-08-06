"""Simple helpers to OCR the on-screen skills list."""

from __future__ import annotations
from typing import List

from src.vision.ocr import screen_text


def scan_skills_ui() -> List[str]:
    """Return a list of skill names detected in the skills UI."""
    text = screen_text()
    skills: List[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            skills.append(line)
    return skills

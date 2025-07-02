"""Utilities for parsing quest log text and checking quest progress."""

from __future__ import annotations

from pathlib import Path
from typing import List


def parse_quest_log(log_text: str) -> List[str]:
    """Return cleaned lines from a quest log ``log_text``."""
    lines: List[str] = []
    for line in log_text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    return lines


def is_step_completed(log_text: str, step_text: str) -> bool:
    """Return ``True`` if ``step_text`` appears in ``log_text``."""
    step = step_text.lower()
    for line in parse_quest_log(log_text):
        if step in line.lower():
            return True
    return False


def scan_log_file_for_step(log_path: str, step_text: str) -> bool:
    """Return ``True`` if ``step_text`` is found in the file at ``log_path``."""
    try:
        data = Path(log_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    return is_step_completed(data, step_text)


def extract_quest_log_from_screenshot(image_path: str) -> str:
    """Extract quest log text from a screenshot. Stub implementation."""
    return ""


__all__ = [
    "parse_quest_log",
    "is_step_completed",
    "scan_log_file_for_step",
    "extract_quest_log_from_screenshot",
]

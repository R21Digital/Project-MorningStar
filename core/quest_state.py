"""Utilities for parsing quest log text and checking quest progress."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

# Default path for the saved quest log
QUEST_LOG_PATH = "logs/quest_log.txt"

# Standardized status constants
STATUS_COMPLETED = "✅ Completed"
STATUS_FAILED = "❌ Failed"
STATUS_IN_PROGRESS = "⏳ In Progress"
STATUS_UNKNOWN = "❓ Unknown"


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


def read_saved_quest_log() -> List[str]:
    """Return cleaned quest log lines from ``QUEST_LOG_PATH``."""
    path = Path(QUEST_LOG_PATH)
    try:
        data = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    return parse_quest_log(data)


def get_step_status(step_id: str, log_lines: Optional[List[str]] = None) -> str:
    """Return a status string for ``step_id`` by scanning quest log lines."""
    if log_lines is None:
        log_lines = read_saved_quest_log()

    step_id = str(step_id).lower()
    for line in log_lines:
        lowered = line.lower()
        if step_id in lowered:
            if "failed" in lowered:
                return STATUS_FAILED
            if "complete" in lowered:
                return STATUS_COMPLETED
            if "progress" in lowered or "started" in lowered or "in progress" in lowered:
                return STATUS_IN_PROGRESS
    return STATUS_UNKNOWN


__all__ = [
    "parse_quest_log",
    "is_step_completed",
    "scan_log_file_for_step",
    "extract_quest_log_from_screenshot",
    "read_saved_quest_log",
    "get_step_status",
    "STATUS_COMPLETED",
    "STATUS_FAILED",
    "STATUS_IN_PROGRESS",
    "STATUS_UNKNOWN",
]

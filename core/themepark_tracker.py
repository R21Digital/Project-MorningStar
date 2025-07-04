"""Module for tracking the status of Theme Park quests based on log file data."""

from __future__ import annotations

from pathlib import Path

THEMEPARK_LOG_PATH = Path("logs/themepark_log.txt")


def read_themepark_log() -> list[str]:
    """Return cleaned lines from :data:`THEMEPARK_LOG_PATH` if it exists."""
    if not THEMEPARK_LOG_PATH.exists():
        return []
    with THEMEPARK_LOG_PATH.open("r", encoding="utf-8") as fh:
        return [line.strip() for line in fh.readlines()]


def is_themepark_quest_active(quest_name: str) -> bool:
    """Return ``True`` if ``quest_name`` appears in the theme park log."""
    log = read_themepark_log()
    return any(quest_name.lower() in line.lower() for line in log)


def get_themepark_status(quest_name: str) -> str:
    """Return a status string for ``quest_name`` from the theme park log."""
    log = read_themepark_log()
    for line in log:
        if quest_name.lower() in line.lower():
            lowered = line.lower()
            if "completed" in lowered:
                return "Completed"
            if "in progress" in lowered:
                return "In Progress"
            if "failed" in lowered:
                return "Failed"
    return "Unknown"

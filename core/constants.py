"""
Core constants for MS11 project.

This module contains status constants and emoji mappings used throughout the application.
"""

# Status constants
STATUS_COMPLETED = "✅"
STATUS_FAILED = "❌"
STATUS_IN_PROGRESS = "⏳"
STATUS_NOT_STARTED = "🕒"
STATUS_UNKNOWN = "❓"

# Status emoji mapping
STATUS_EMOJI_MAP = {
    "completed": STATUS_COMPLETED,
    "failed": STATUS_FAILED,
    "in_progress": STATUS_IN_PROGRESS,
    "not_started": STATUS_NOT_STARTED,
}

# Reverse mapping from emoji to status name
STATUS_NAME_FROM_EMOJI = {v: k for k, v in STATUS_EMOJI_MAP.items()}

# Set of valid status emojis
VALID_STATUS_EMOJIS = set(STATUS_EMOJI_MAP.values())

# Export all constants
__all__ = [
    "STATUS_COMPLETED",
    "STATUS_FAILED", 
    "STATUS_IN_PROGRESS",
    "STATUS_NOT_STARTED",
    "STATUS_UNKNOWN",
    "STATUS_EMOJI_MAP",
    "STATUS_NAME_FROM_EMOJI",
    "VALID_STATUS_EMOJIS",
]

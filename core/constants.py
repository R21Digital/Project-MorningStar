"""Common status strings used throughout the project."""

STATUS_COMPLETED = "✅"
STATUS_FAILED = "❌"
STATUS_IN_PROGRESS = "⏳"
STATUS_NOT_STARTED = "🕒"
STATUS_UNKNOWN = "❓"

# Mapping from status names to their corresponding emoji
STATUS_EMOJI_MAP = {
    "completed": STATUS_COMPLETED,
    "failed": STATUS_FAILED,
    "in_progress": STATUS_IN_PROGRESS,
    "not_started": STATUS_NOT_STARTED,
}

# Reverse lookup from emoji back to status name
STATUS_NAME_FROM_EMOJI = {v: k for k, v in STATUS_EMOJI_MAP.items()}

# Set of all valid status emoji
VALID_STATUS_EMOJIS = set(STATUS_EMOJI_MAP.values())

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

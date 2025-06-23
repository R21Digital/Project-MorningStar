"""Basic XP progression helpers."""


def xp_for_level(level: int) -> int:
    """Return the XP required for ``level`` using a quadratic formula."""
    return (level ** 2) * 100

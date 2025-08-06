"""Simple mode manager for the automator."""

VALID_MODES = ("questing", "combat", "vendor")

current_mode: str = "questing"


def set_mode(mode: str) -> None:
    """Update :data:`current_mode` if ``mode`` is valid."""
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid mode: {mode}")
    global current_mode
    current_mode = mode

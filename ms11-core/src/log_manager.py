"""Simple logging utilities."""

from datetime import datetime


def start_log() -> None:
    """Announce the start of a log session with a timestamp."""
    now = datetime.now()
    print(f"\U0001F4DD Logging started at {now.strftime('%Y-%m-%d %H:%M:%S')}")

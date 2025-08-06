"""Lightweight logging helpers."""

from __future__ import annotations

from datetime import datetime, timezone


def log_event(message: str) -> None:
    """Print ``message`` with an ISO timestamp in UTC."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{timestamp}] {message}")


__all__ = ["log_event"]

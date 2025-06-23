"""Utilities for planning paths through legacy quest lines."""


def get_legacy_path(start_step: str, end_step: str) -> list[str]:
    """Return a naive path list between two quest steps."""
    return [start_step, end_step]

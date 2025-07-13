"""Fallback helpers for quest execution.

This module currently provides minimal placeholder logic. It will be
expanded with robust failure recovery in a future batch.
"""

from __future__ import annotations

from typing import Any

from profession_logic.utils import logger as profession_logger


def noop(*_args: Any, **_kwargs: Any) -> bool:
    """Return ``False`` without performing any action."""
    return False


def basic_fallback_handler(step: Any) -> bool:
    """Log ``step`` and return ``False``.

    Parameters
    ----------
    step:
        Step object that failed to execute.
    """
    profession_logger.log_warning(f"[Fallback] Step failed: {step}")
    return False


__all__ = ["noop", "basic_fallback_handler"]

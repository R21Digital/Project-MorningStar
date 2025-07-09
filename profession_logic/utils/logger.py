"""Logging utilities for profession modules."""

from __future__ import annotations

from core.logging_config import configure_logger


logger = configure_logger(name="profession_logic", log_file="logs/profession_logic.log")


def log_info(message: str) -> None:
    """Log ``message`` using the profession logger."""
    logger.info(message)

"""Logging utilities for profession modules."""

from __future__ import annotations

from core.logging_config import configure_logger


logger = configure_logger(name="profession_logic")


def log_info(message: str) -> None:
    """Log ``message`` using the profession logger."""
    logger.info(message)


def log_warning(message: str) -> None:
    """Log ``message`` with warning level using the profession logger."""
    logger.warning(message)


def log_error(message: str) -> None:
    """Log ``message`` with error level using the profession logger."""
    logger.error(message)


def log_debug(message: str) -> None:
    """Log ``message`` with debug level using the profession logger."""
    logger.debug(message)

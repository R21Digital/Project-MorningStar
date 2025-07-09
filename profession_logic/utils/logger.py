"""Logging utilities for profession modules."""

from __future__ import annotations

import logging
from pathlib import Path

from core.logging_config import configure_logger

DEFAULT_LOG_PATH = Path("logs/profession_logic.log")


def get_logger(name: str = "profession_logic", log_path: Path = DEFAULT_LOG_PATH) -> logging.Logger:
    """Return the shared logger configured for ``log_path``."""
    logger = configure_logger(name, log_file=str(log_path))
    return logger

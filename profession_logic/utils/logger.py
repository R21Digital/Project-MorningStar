"""Logging utilities for profession modules."""

from __future__ import annotations

import logging
from pathlib import Path

DEFAULT_LOG_PATH = Path("logs/profession_logic.log")


def get_logger(name: str = "profession_logic", log_path: Path = DEFAULT_LOG_PATH) -> logging.Logger:
    """Return a configured logger writing to ``log_path``."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

"""Manage log output for Android MS11."""

from __future__ import annotations

import logging
import os


DEFAULT_LOG_PATH = os.path.join("logs", "app.log")


def start_log(log_path: str = DEFAULT_LOG_PATH) -> logging.Logger:
    """Configure basic logging to ``log_path`` and return the logger."""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger("ms11")
    logger.info("Log started.")
    return logger

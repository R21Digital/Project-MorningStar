from __future__ import annotations

import logging
import os
import warnings


DEFAULT_LOG_FILE = os.path.join("logs", "app.log")
DEFAULT_WARNING_FILE = os.path.join("logs", "warnings.log")


def configure_logger(
    log_file: str = DEFAULT_LOG_FILE,
    warning_file: str = DEFAULT_WARNING_FILE,
) -> logging.Logger:
    """Configure application logging and return the logger.

    The logger writes INFO messages to ``log_file`` and captures warnings in
    ``warning_file``. Existing handlers are preserved so calling this multiple
    times is safe.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    os.makedirs(os.path.dirname(warning_file), exist_ok=True)

    logger = logging.getLogger("ms11")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    existing_files = {
        os.path.abspath(getattr(h, "baseFilename", ""))
        for h in logger.handlers
        if isinstance(h, logging.FileHandler)
    }

    log_file_abs = os.path.abspath(log_file)
    if log_file_abs not in existing_files:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    warnings_logger = logging.getLogger("py.warnings")
    warn_file_abs = os.path.abspath(warning_file)
    if warn_file_abs not in {
        os.path.abspath(getattr(h, "baseFilename", ""))
        for h in warnings_logger.handlers
        if isinstance(h, logging.FileHandler)
    }:
        warn_handler = logging.FileHandler(warning_file, encoding="utf-8")
        warn_handler.setFormatter(formatter)
        warnings_logger.addHandler(warn_handler)

    logging.captureWarnings(True)
    return logger

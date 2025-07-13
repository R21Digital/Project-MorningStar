import logging
import os
from pathlib import Path


def configure_logger(
    name: str = "default",
    log_file: str | None = None,
    level: int | str | None = None,
) -> logging.Logger:
    """Return a logger with optional file output and configurable level.

    Reusing the same ``name`` ensures handlers are only added once.
    """
    logger = logging.getLogger(name)
    if getattr(logger, "_configured", False):
        return logger

    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")
    if isinstance(level, str):
        level = logging.getLevelName(level.upper())
        if not isinstance(level, int):
            level = logging.INFO
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    if not log_file:
        instance = os.getenv("BOT_INSTANCE_NAME", "default")
        log_file = str(Path("logs") / f"{instance}.log")

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger._configured = True
    return logger

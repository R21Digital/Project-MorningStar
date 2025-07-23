import logging
import os
from pathlib import Path
from datetime import datetime, timedelta

MAX_LOG_FILES = 10
"""Maximum number of log files to retain in the logs directory."""

MAX_LOG_AGE_DAYS = 30
"""Maximum age in days before a log file is deleted."""


def _cleanup_old_logs(log_dir: Path) -> None:
    """Delete logs exceeding MAX_LOG_FILES or older than MAX_LOG_AGE_DAYS."""
    if not log_dir.exists():
        return

    logs = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)

    now = datetime.now()
    cutoff = now - timedelta(days=MAX_LOG_AGE_DAYS)

    for log in list(logs):
        if datetime.fromtimestamp(log.stat().st_mtime) < cutoff:
            try:
                log.unlink()
            except OSError:
                pass

    logs = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    for log in logs[MAX_LOG_FILES:]:
        try:
            log.unlink()
        except OSError:
            pass


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
        _cleanup_old_logs(log_path.parent)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger._configured = True
    return logger

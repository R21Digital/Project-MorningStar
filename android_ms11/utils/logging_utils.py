"""Lightweight logging helpers used by Android MS11."""

from __future__ import annotations

import datetime
import os

try:
    from utils.logger import log_event as _src_log_event
except Exception:  # pragma: no cover - optional dependency
    _src_log_event = None


DEFAULT_LOG_PATH = os.path.join("logs", "session.log")


def log_event(message: str, *, log_path: str = DEFAULT_LOG_PATH) -> str:
    """Append ``message`` to ``log_path`` with a timestamp."""

    if _src_log_event is not None:
        return _src_log_event(message, log_path=log_path)

    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    timestamp = datetime.datetime.now().isoformat()
    try:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(f"{timestamp} | {message}\n")
    except Exception as e:  # pragma: no cover - best effort logging
        print(f"[logging_utils] Failed to log event: {e}")
    return log_path


__all__ = ["log_event"]


"""Compatibility wrapper for executing quest steps with retry support."""

from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any, Callable

from src.engine.quest_executor import run_step_with_feedback as execute_quest_step

RETRY_LOG_PATH = os.path.join("logs", "retry_log.txt")
DEFAULT_RETRY_DELAY = 1.0


def log_retry(step_label: str, attempt: int, error: Exception | str) -> None:
    """Append a retry event to :data:`RETRY_LOG_PATH`.

    The log file uses a simple CSV format: ``timestamp, step_label, attempt, error``.
    """

    os.makedirs(os.path.dirname(RETRY_LOG_PATH), exist_ok=True)
    timestamp = datetime.utcnow().isoformat()
    message = str(error)
    with open(RETRY_LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{timestamp}, {step_label}, {attempt}, {message}\n")


def execute_with_retry(
    step: Any,
    max_retries: int = 3,
    fallback: Callable | None = None,
    delay: float = DEFAULT_RETRY_DELAY,
) -> bool:
    """Execute ``step`` with retry logic via :func:`execute_quest_step`.

    Parameters
    ----------
    step:
        Quest step object to execute. This object is passed directly to
        :func:`execute_quest_step`.
    max_retries:
        Maximum number of retry attempts before falling back.
    fallback:
        Optional callable executed when all retries fail. If provided, it will
        be called with ``step`` as its only argument.
    delay:
        Seconds to wait after each failed attempt. Defaults to
        :data:`DEFAULT_RETRY_DELAY`.

    Returns
    -------
    bool
        ``True`` if the step (or fallback) executed successfully, ``False``
        otherwise.
    """

    attempt = 0
    while attempt < max_retries:
        attempt += 1
        try:
            if execute_quest_step(step):
                return True
            log_retry(str(step), attempt, "false result")
            time.sleep(delay)
        except Exception as exc:  # pragma: no cover - best effort logging
            log_retry(str(step), attempt, exc)
            time.sleep(delay)
    if fallback is not None:
        try:
            return bool(fallback(step))
        except Exception as exc:  # pragma: no cover - best effort logging
            log_retry(str(step), attempt + 1, exc)
            time.sleep(delay)
    return False


__all__ = ["execute_quest_step", "execute_with_retry", "log_retry"]

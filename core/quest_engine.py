"""Compatibility wrapper for executing quest steps with retry support."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Callable

from src.execution.quest_engine import execute_quest_step

RETRY_LOG_PATH = os.path.join("logs", "retry_log.txt")


def log_retry(step_id: str, attempt: int, error: Exception | str) -> None:
    """Append a retry event to :data:`RETRY_LOG_PATH`.

    The log file uses a simple CSV format: ``timestamp, step_id, attempt, error``.
    """

    os.makedirs(os.path.dirname(RETRY_LOG_PATH), exist_ok=True)
    timestamp = datetime.utcnow().isoformat()
    message = str(error)
    with open(RETRY_LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"{timestamp}, {step_id}, {attempt}, {message}\n")


def execute_with_retry(
    step: Any, max_retries: int = 3, fallback: Callable | None = None
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
        except Exception as exc:  # pragma: no cover - best effort logging
            log_retry(str(step), attempt, exc)
    if fallback is not None:
        try:
            return bool(fallback(step))
        except Exception as exc:  # pragma: no cover - best effort logging
            log_retry(str(step), attempt + 1, exc)
    return False


__all__ = ["execute_quest_step", "execute_with_retry", "log_retry"]

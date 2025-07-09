"""Lightweight logging helpers used by Android MS11."""

from __future__ import annotations

import csv
import datetime
import os


DEFAULT_LOG_PATH = os.path.join("logs", "session.log")


def log_event(message: str, *, log_path: str = DEFAULT_LOG_PATH) -> str:
    """Append ``message`` to ``log_path`` with a timestamp."""

    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    timestamp = datetime.datetime.now().isoformat()
    try:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(f"{timestamp} | {message}\n")
    except Exception as e:  # pragma: no cover - best effort logging
        print(f"[logging_utils] Failed to log event: {e}")
    return log_path


DEFAULT_PERF_CSV_PATH = os.path.join("logs", "performance.csv")


def log_performance_summary(stats: dict, *, csv_path: str = DEFAULT_PERF_CSV_PATH) -> str:
    """Append ``stats`` as a CSV row to ``csv_path``."""
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    file_exists = os.path.exists(csv_path)
    try:
        with open(csv_path, "a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(stats.keys()))
            if not file_exists:
                writer.writeheader()
            writer.writerow(stats)
    except Exception as e:  # pragma: no cover - best effort logging
        print(f"[logging_utils] Failed to log performance summary: {e}")
    return csv_path


__all__ = ["log_event", "log_performance_summary"]


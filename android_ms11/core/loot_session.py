"""Track loot acquired during a session."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List, Dict

# Internal list of loot entries
_loot_log: List[Dict[str, str]] = []


def log_loot(item: str) -> None:
    """Append a loot ``item`` with a timestamp to the log."""
    entry = {"time": datetime.utcnow().isoformat(), "item": item}
    _loot_log.append(entry)


def export_log(log_dir: str = "logs") -> str:
    """Write the current loot log to ``log_dir/session_log.json``."""
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, "session_log.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(_loot_log, fh, indent=2)
    return path


__all__ = ["log_loot", "export_log"]

"""Session logging utilities."""

import json
import os
from typing import List, Dict

LOG_DIR = os.path.join("data", "session_logs")


def _session_path(session_id: str) -> str:
    os.makedirs(LOG_DIR, exist_ok=True)
    return os.path.join(LOG_DIR, f"{session_id}.json")


def load_session(session_id: str) -> List[Dict]:
    path = _session_path(session_id)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except json.JSONDecodeError:
            return []
    return []


def append_entry(session_id: str, entry: Dict) -> str:
    data = load_session(session_id)
    data.append(entry)
    path = _session_path(session_id)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    return path

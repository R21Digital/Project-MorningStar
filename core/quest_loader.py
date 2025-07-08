from __future__ import annotations

import json
from typing import Any, List, Dict


def load_quest_steps(path: str) -> List[Dict[str, Any]]:
    """Return quest steps loaded from JSON ``path``.

    The JSON file may contain either a list of step dictionaries or a mapping
    with a top-level ``"steps"`` key.
    """
    with open(path, "r", encoding="utf-8") as fh:
        data: Any = json.load(fh)
    if isinstance(data, dict):
        steps = data.get("steps", [])
    elif isinstance(data, list):
        steps = data
    else:
        steps = []
    return list(steps)

"""Simple helpers to load profession data files."""

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    """Return JSON data from ``path``."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

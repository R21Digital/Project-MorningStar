"""Load rare mob definitions for the rare loot scanner."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Dict


def load_rls_mobs(path: str | Path = "data/rls_mobs.json") -> List[Dict[str, Any]]:
    """Return rare mob info from ``path``."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

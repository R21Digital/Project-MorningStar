from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


STORE = Path(__file__).parents[2] / 'data' / 'shortcuts.json'


def load() -> List[Dict[str, str]]:
    try:
        if STORE.exists():
            return json.loads(STORE.read_text(encoding='utf-8'))
    except Exception:
        pass
    return []


def save(items: List[Dict[str, str]]) -> None:
    try:
        STORE.parent.mkdir(parents=True, exist_ok=True)
        STORE.write_text(json.dumps(items, indent=2), encoding='utf-8')
    except Exception:
        pass



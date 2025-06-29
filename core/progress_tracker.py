"""Helpers for persisting profession progress across sessions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


_DEFAULT_DATA = {"completed_skills": []}


def load_session(path: Path) -> Dict[str, Any]:
    """Return saved progress from ``path`` or an empty structure."""
    if not path.exists():
        return {"completed_skills": []}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise ValueError("Invalid progress file")
    except Exception:
        return {"completed_skills": []}
    data.setdefault("completed_skills", [])
    if not isinstance(data["completed_skills"], list):
        data["completed_skills"] = list(data.get("completed_skills", []))
    return data


def save_session(path: Path, data: Dict[str, Any]) -> None:
    """Write ``data`` to ``path`` atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    tmp.replace(path)


def record_skill(path: Path, skill: str) -> None:
    """Append ``skill`` to the completed list and save."""
    data = load_session(path)
    skills = data.setdefault("completed_skills", [])
    if skill not in skills:
        skills.append(skill)
        save_session(path, data)


__all__ = ["load_session", "save_session", "record_skill"]

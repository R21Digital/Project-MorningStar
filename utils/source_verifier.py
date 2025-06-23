"""Utilities for verifying quest sources and detecting file changes."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

DEFAULT_HASH_PATH = Path("data/raw/legacy.hash")


def compute_file_hash(path: str | Path) -> str:
    """Return a SHA256 hash of the given file."""
    file_path = Path(path)
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def file_changed(path: str | Path, hash_path: str | Path = DEFAULT_HASH_PATH) -> bool:
    """Return ``True`` if ``path`` differs from the stored hash.

    The current hash will be written to ``hash_path`` whenever the file has
    changed or no previous hash exists.
    """

    file_path = Path(path)
    hash_file = Path(hash_path)

    current = compute_file_hash(file_path)
    if hash_file.exists():
        previous = hash_file.read_text().strip()
        if previous == current:
            return False

    hash_file.write_text(current)
    return True


def verify_source(data: Any) -> bool:
    """Basic validation for quest data structures.

    The function currently checks that ``data`` is a mapping containing a
    ``"title"`` string and a ``"steps"`` list. More sophisticated validation can
    be plugged in later.
    """

    print(f"[DEBUG] Verifying quest source: {data}")

    if not isinstance(data, dict):
        return False

    if not isinstance(data.get("title"), str):
        return False

    steps = data.get("steps")
    if not isinstance(steps, list):
        return False

    return True

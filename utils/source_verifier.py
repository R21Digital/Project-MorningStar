"""Helpers for verifying external quest sources with file hashing."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

DEFAULT_HASH_PATH = Path("data/raw/legacy.hash")


def compute_file_hash(path: str | Path) -> str:
    """Return a SHA256 hash for ``path``."""
    file_path = Path(path)
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def file_changed(path: str | Path, hash_path: str | Path = DEFAULT_HASH_PATH) -> bool:
    """Return ``True`` if the file differs from the stored hash."""
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
    """Validate external quest ``data``."""
    # TODO: implement checksum or schema checks
    return False

"""Utilities for verifying quest sources and detecting file changes."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

DEFAULT_HASH_PATH = Path("data/raw/legacy.hash")
TRUSTED_HASHES = {
    "247391101e29decad45551f0c515abb2bd8286393e579ac12e22eec57b89b3b2"
}


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
    """Return ``True`` if ``data`` appears trustworthy."""
    print(f"[DEBUG] Verifying quest source: {data}")

    if isinstance(data, (str, Path)) and Path(data).exists():
        hash_value = compute_file_hash(Path(data))
    elif isinstance(data, bytes):
        hash_value = hashlib.sha256(data).hexdigest()
    else:
        hash_value = hashlib.sha256(str(data).encode()).hexdigest()

    print(f"[DEBUG] Computed hash: {hash_value}")
    return hash_value in TRUSTED_HASHES

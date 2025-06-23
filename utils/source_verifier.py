"""Compatibility wrapper for the source verifier helpers."""

from src.source_verifier import (
    compute_file_hash,
    file_changed,
    verify_source,
)

__all__ = [
    "compute_file_hash",
    "file_changed",
    "verify_source",
]

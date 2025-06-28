"""Utilities for scheduling runtime modes."""

from __future__ import annotations

from typing import Mapping, Any, Sequence


def get_next_mode(profile: Mapping[str, Any], state: Mapping[str, Any]) -> str:
    """Return the next mode in ``profile['mode_sequence']``.

    Parameters
    ----------
    profile:
        Mapping containing a ``mode_sequence`` list and optional ``default_mode``.
    state:
        Mapping providing the current ``mode`` value.
    """
    sequence: Sequence[str] = profile.get("mode_sequence", [])
    if not sequence:
        return profile.get("default_mode", "")

    default_mode = profile.get("default_mode", sequence[0])
    current = state.get("mode", default_mode)

    try:
        idx = sequence.index(current)
        next_idx = (idx + 1) % len(sequence)
    except ValueError:
        next_idx = 0

    return sequence[next_idx]


__all__ = ["get_next_mode"]

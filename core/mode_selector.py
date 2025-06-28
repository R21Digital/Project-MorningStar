"""Helper to select runtime mode based on profile and state data."""

from __future__ import annotations

from typing import Mapping, Any


def select_mode(profile: Mapping[str, Any], state: Mapping[str, Any]) -> str:
    """Return appropriate mode name for given conditions.

    Parameters
    ----------
    profile:
        Mapping containing at least ``default_mode`` and ``skip_modes``.
    state:
        Mapping with keys ``has_buff`` (bool), ``in_party`` (bool),
        and ``credits`` (int).
    """

    skip = set(profile.get("skip_modes", []))

    if not state.get("has_buff", True) and "whisper" not in skip:
        return "whisper"
    if not state.get("in_party", True) and "support" not in skip:
        return "support"
    if state.get("credits", 0) < 1000 and "bounty" not in skip:
        return "bounty"

    return profile.get("default_mode", "rls_mode")


__all__ = ["select_mode"]

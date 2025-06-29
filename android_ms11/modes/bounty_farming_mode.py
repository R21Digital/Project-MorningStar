"""Basic bounty farming implementation."""

from __future__ import annotations

from typing import Mapping, Any

from core.location_selector import travel_to_target, locate_hotspot
from core.waypoint_verifier import verify_waypoint_stability


def run(profile: Mapping[str, Any] | None = None, session=None) -> None:
    """Travel to the configured target and verify the mission waypoint.

    Parameters
    ----------
    profile:
        Profile data loaded from :func:`core.profile_loader.load_profile` or
        provided via the ``--farming_target`` CLI option.
    session:
        Optional session object passed through from :func:`src.main.run_mode`.
    """

    target = {}
    if profile and isinstance(profile.get("farming_target"), dict):
        target = profile["farming_target"]

    if not target:
        print("[Bounty] No farming_target configured.")
        return

    print(
        f"[Bounty] Traveling to {target.get('city', 'unknown')} on {target.get('planet', 'unknown')}"
    )
    travel_to_target(target, agent=session)

    coords = locate_hotspot(
        target.get("planet", ""), target.get("city", ""), target.get("hotspot", "")
    )

    print("[Bounty] Accepting missions...")
    print("[Bounty] Missions accepted.")

    if coords:
        verify_waypoint_stability(coords)

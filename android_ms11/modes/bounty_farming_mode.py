"""Basic bounty farming implementation."""

from __future__ import annotations

from typing import Mapping, Any

from core import farm_profile_loader
from core.profile_loader import assert_profile_ready
from utils.license_hooks import requires_license

from core.location_selector import travel_to_target, locate_hotspot
from core.waypoint_verifier import verify_waypoint_stability
from modules import TerminalFarmer
from profession_logic.utils.logger import logger


@requires_license
def run(profile: Mapping[str, Any] | str | None = None, session=None) -> None:
    """Travel to the configured target and verify the mission waypoint.

    Parameters
    ----------
    profile:
        Either a mapping containing ``farming_target`` data or the name of a
        farm profile to load via :func:`core.farm_profile_loader.load_farm_profile`.
        This may also be provided via the ``--farming_target`` CLI option.
    session:
        Optional session object passed through from :func:`src.main.run_mode`.
    """

    assert_profile_ready(getattr(session, "profile", None) or profile)

    if isinstance(profile, str):
        profile = farm_profile_loader.load_farm_profile(profile)

    target = {}
    if profile and isinstance(profile.get("farming_target"), dict):
        target = profile["farming_target"]
    elif profile:
        target = {k: profile.get(k) for k in ("planet", "city", "hotspot") if profile.get(k)}

    if not target:
        logger.info("[Bounty] No farming_target configured.")
        return

    logger.info(
        "[Bounty] Traveling to %s on %s",
        target.get("city", "unknown"),
        target.get("planet", "unknown"),
    )
    travel_to_target(target, agent=session)

    coords = locate_hotspot(
        target.get("planet", ""), target.get("city", ""), target.get("hotspot", "")
    )

    logger.info("[Bounty] Accepting missions...")
    farmer = TerminalFarmer()
    farmer.execute_run()
    logger.info("[Bounty] Missions accepted.")

    if coords:
        verify_waypoint_stability(coords)

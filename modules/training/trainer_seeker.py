"""Helpers for automatically seeking out profession trainers.

This module determines when the player can purchase new skill boxes based on
available XP.  When enough XP is present it will navigate to the trainer and
run a training macro.
"""

from __future__ import annotations

from typing import Iterable, Optional

from modules.professions import progress_tracker
from core import BuildManager, TravelManager
from scripts.logic import trainer_navigator
from src.xp_tracker import read_xp_via_ocr


DEFAULT_PLANET = "tatooine"
DEFAULT_CITY = "mos_eisley"

def _run_training_macro(skill: str) -> None:
    """Placeholder for executing the in game training macro."""
    print(f"[TRAIN] Executing macro to learn {skill}")


def _send_discord_alert(message: str) -> None:
    """Send ``message`` through the Discord relay when available."""
    try:
        trainer_navigator.log_event(f"[DISCORD] {message}")
    except Exception:
        pass


def seek_training(
    profession: str,
    skills: Iterable[str],
    *,
    available_xp: Optional[int] = None,
    agent=None,
    planet: str = DEFAULT_PLANET,
    city: str = DEFAULT_CITY,
    build_manager: Optional[BuildManager] = None,
    travel_manager: Optional[TravelManager] = None,
) -> bool:
    """Train the next available skill if enough XP has been earned.

    Parameters
    ----------
    profession:
        Name of the profession being trained.
    skills:
        Iterable of currently known skills.
    available_xp:
        Current XP value. When ``None`` the value is read via OCR using
        :func:`src.xp_tracker.read_xp_via_ocr`.
    agent:
        Optional automation agent passed to :class:`core.TravelManager`.
    planet:
        Planet where the trainer resides.
    city:
        City where the trainer resides.
    travel_manager:
        Optional :class:`core.TravelManager` instance used for navigation.

    Returns
    -------
    bool
        ``True`` if training was attempted, ``False`` otherwise.
    """
    if build_manager is not None:
        next_skill = build_manager.get_next_skill(skills)
        if not next_skill:
            trainer_navigator.log_event(
                f"No further skills available for {profession}"
            )
            return False
        required_xp = build_manager.get_required_xp(next_skill)
    else:
        rec = progress_tracker.recommend_next_skill(profession, list(skills))
        if not rec:
            trainer_navigator.log_event(
                f"No further skills available for {profession}"
            )
            return False
        next_skill = rec["skill"]
        required_xp = rec.get("xp", 0)
    if available_xp is None:
        available_xp = read_xp_via_ocr()

    trainer_navigator.log_event(
        f"Checking training for {profession}: need {required_xp} XP, have {available_xp}"
    )

    if available_xp < required_xp:
        return False

    trainer_navigator.log_event(
        f"Travelling to {profession} trainer to learn {next_skill}"
    )
    tm = travel_manager or TravelManager()
    try:
        success = tm.go_to_trainer(profession, agent=agent)
    except Exception:
        trainer_navigator.log_event("Player busy; will retry later")
        return False

    if not success:
        trainer_navigator.log_event(f"Failed to reach any {profession} trainer")
        trainer_navigator.log_training_event(profession, "Failed", -1.0)
        _send_discord_alert(f"Training failed for {profession}")
        return False

    trainer_navigator.log_training_event(profession, next_skill, 0.0)
    _run_training_macro(next_skill)
    trainer_navigator.log_event(
        f"Completed training for {profession}: {next_skill}"
    )
    return True

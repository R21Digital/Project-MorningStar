"""Helpers for automatically seeking out profession trainers.

This module determines when the player can purchase new skill boxes based on
available XP.  When enough XP is present it will navigate to the trainer and
run a training macro.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from modules.professions import progress_tracker
from scripts.logic import trainer_navigator
from src.training.trainer_visit import visit_trainer
from src.xp_tracker import read_xp_via_ocr


DEFAULT_PLANET = "tatooine"
DEFAULT_CITY = "mos_eisley"


def _next_skill(profession: str, skills: Iterable[str]) -> Optional[dict]:
    """Return the next skill recommendation from ``progress_tracker``."""
    return progress_tracker.recommend_next_skill(profession, list(skills))


def _enough_xp(required: int, current: int) -> bool:
    """Return ``True`` if ``current`` XP meets or exceeds ``required``."""
    return current >= required


def _run_training_macro(skill: str) -> None:
    """Placeholder for executing the in game training macro."""
    print(f"[TRAIN] Executing macro to learn {skill}")


def seek_training(
    profession: str,
    skills: Iterable[str],
    *,
    available_xp: Optional[int] = None,
    agent=None,
    planet: str = DEFAULT_PLANET,
    city: str = DEFAULT_CITY,
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
        Optional automation agent passed to :func:`visit_trainer`.
    planet:
        Planet where the trainer resides.
    city:
        City where the trainer resides.

    Returns
    -------
    bool
        ``True`` if training was attempted, ``False`` otherwise.
    """
    rec = _next_skill(profession, skills)
    if not rec:
        trainer_navigator.log_event(f"No further skills available for {profession}")
        return False

    required_xp = rec.get("xp", 0)
    if available_xp is None:
        available_xp = read_xp_via_ocr()

    trainer_navigator.log_event(
        f"Checking training for {profession}: need {required_xp} XP, have {available_xp}"
    )

    if not _enough_xp(required_xp, available_xp):
        return False

    trainer_navigator.log_event(
        f"Travelling to {profession} trainer to learn {rec['skill']}"
    )
    visit_trainer(agent, profession, planet=planet, city=city)
    trainer_navigator.log_training_event(profession, rec["skill"], 0.0)
    _run_training_macro(rec["skill"])
    trainer_navigator.log_event(
        f"Completed training for {profession}: {rec['skill']}"
    )
    return True

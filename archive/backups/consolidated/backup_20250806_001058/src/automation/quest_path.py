"""Questing helpers for navigation and training."""

from __future__ import annotations

from scripts.logic.trainer_check import should_train_skills
from scripts.logic.trainer_navigator import navigate_to_trainer


def visit_trainer_if_needed(
    agent=None,
    *,
    trainer: str = "artisan",
    planet: str = "tatooine",
    city: str = "mos_eisley",
) -> bool:
    """Visit the profession trainer if training is recommended.

    Parameters
    ----------
    agent:
        Optional automation agent passed through to :func:`navigate_to_trainer`.
    trainer:
        Profession name of the trainer to visit.
    planet:
        Planet where the trainer resides.
    city:
        City where the trainer resides.

    Returns
    -------
    bool
        ``True`` when a trainer visit was triggered.
    """
    if should_train_skills():
        navigate_to_trainer(trainer, planet, city, agent)
        return True
    return False

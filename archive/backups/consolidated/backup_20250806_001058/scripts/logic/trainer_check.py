"""Skill training recommendation logic."""

from __future__ import annotations

import random


def should_train_skills() -> bool:
    """Return ``True`` if a trainer visit is recommended."""
    # Placeholder heuristic: randomly choose whether to train.
    return random.random() < 0.2

"""Utilities for managing profession skill training."""

from __future__ import annotations
from typing import List, Dict

from utils.movement_manager import travel_to
from utils.npc_handler import interact_with_trainer
from utils.ocr_scanner import scan_skills_ui
from config.profession_config import REQUIRED_SKILLS, TRAINER_BY_PROFESSION


class ProfessionManager:
    """Manage profession progression and training."""

    def __init__(self, trainer_map: Dict[str, Dict] | None = None) -> None:
        self.trainer_map = trainer_map or TRAINER_BY_PROFESSION

    # --------------------------------------------------
    def train_missing_skills(self) -> None:
        """Check learned skills and train at the appropriate trainer."""
        learned = [s.lower() for s in scan_skills_ui()]
        for profession, skills in REQUIRED_SKILLS.items():
            missing = [s for s in skills if s.lower() not in learned]
            if not missing:
                continue
            trainer = self.trainer_map.get(profession)
            if not trainer:
                continue
            zone = trainer["planet"]
            coords = trainer["coords"]
            travel_to(zone, coords)
            for skill in missing:
                interact_with_trainer(trainer["name"], skill)


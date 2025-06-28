"""Utilities for managing profession skill training."""

from __future__ import annotations
from typing import Dict

from utils.movement_manager import travel_to
from utils.npc_handler import interact_with_trainer
from utils.ocr_scanner import scan_skills_ui
from config.profession_config import REQUIRED_SKILLS
from utils.load_trainers import load_trainers


class ProfessionManager:
    """Manage profession progression and training."""

    def __init__(self, trainer_map: Dict[str, Dict] | None = None) -> None:
        self.trainer_map = trainer_map or self.load_trainer_map()

    @staticmethod
    def load_trainer_map(trainer_file: str | None = None) -> Dict[str, Dict]:
        """Return primary trainer mapping from the canonical data."""
        data = load_trainers(trainer_file)
        mapping: Dict[str, Dict] = {}
        for profession, entries in data.items():
            if not entries:
                continue
            entry = entries[0]
            mapping[profession] = {
                "planet": entry.get("planet"),
                "city": entry.get("city"),
                "coords": entry.get("coords"),
                "name": entry.get("name", f"{profession} trainer"),
            }
        return mapping

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
            planet = trainer["planet"]
            coords = trainer["coords"]
            travel_to(coords, planet)
            for skill in missing:
                interact_with_trainer(trainer["name"], skill)


from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .travel_manager import TravelManager
from profession_logic.utils.logger import logger
try:  # pragma: no cover - optional dependency
    from modules.professions import progress_tracker
except Exception:  # pragma: no cover
    progress_tracker = None


class ProfessionLeveler:
    """High level helper for sequential profession training."""

    def __init__(self, trainer_profiles_path: str | None = None, profession_plan_path: str | None = None) -> None:
        self.travel_manager = TravelManager(trainer_profiles_path)
        self.plan_path = (
            Path(profession_plan_path)
            if profession_plan_path is not None
            else Path(__file__).resolve().parents[1] / "profiles" / "profession_plan.json"
        )
        self.profession_plan: List[str] = []
        self._load_plan()

    # --------------------------------------------------
    def _load_plan(self) -> None:
        try:
            with open(self.plan_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                self.profession_plan = list(data.get("professions", []))
            elif isinstance(data, list):
                self.profession_plan = list(data)
            else:
                self.profession_plan = []
        except FileNotFoundError:
            self.profession_plan = []

    # --------------------------------------------------
    def level_all_professions(self) -> None:
        for profession in self.profession_plan:
            if profession not in self.travel_manager.trainers:
                logger.info("[Leveler] No trainer entry for %s", profession)
                continue
            self.level_profession(profession)

    # --------------------------------------------------
    def level_profession(self, profession_name: str) -> List[str]:
        """Travel to ``profession_name`` trainer and return offered skills."""
        # ``train_profession`` already captures skills but we explicitly scan
        # again so tests can mock :class:`TrainerScanner` independently.
        self.travel_manager.train_profession(profession_name)
        skills = self.travel_manager.trainer_scanner.scan()
        if skills:
            logger.info("[Leveler] %s trainer offers: %s", profession_name, skills)
        else:
            logger.info("[Leveler] No skills detected for %s", profession_name)

        if progress_tracker and skills:
            try:
                rec = progress_tracker.recommend_next_skill(profession_name, skills)
                if rec:
                    logger.info(
                        "[Leveler] Next skill for %s: %s (%s XP)",
                        profession_name,
                        rec["skill"],
                        rec.get("xp", 0),
                    )
            except Exception:
                pass
        return skills

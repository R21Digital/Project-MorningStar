"""Utilities for traveling to trainers and managing profession training."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any

from utils.logger import logger

from .trainer_scanner import TrainerScanner

# Placeholder imports until real utilities are available
try:  # pragma: no cover - used for future integration
    from utils.travel import go_to_waypoint, verify_location
except Exception:  # pragma: no cover - fallback placeholders
    def go_to_waypoint(*_args: Any, **_kwargs: Any) -> None:
        """Placeholder travel function."""
        pass

    def verify_location(*_args: Any, **_kwargs: Any) -> None:
        """Placeholder verification function."""
        pass


class TravelManager:
    """Manage travel to profession trainers."""

    def __init__(self, trainer_file: str | None = None) -> None:
        self.trainer_file = (
            Path(trainer_file)
            if trainer_file is not None
            else Path(__file__).resolve().parents[1] / "profiles" / "trainers.json"
        )
        self.trainers: Dict[str, Dict] = {}
        self.trainer_scanner = TrainerScanner()
        self.load_trainers()

    # --------------------------------------------------
    def load_trainers(self) -> None:
        """Load trainer data from :attr:`trainer_file`."""
        try:
            with open(self.trainer_file, "r", encoding="utf-8") as fh:
                self.trainers = json.load(fh)
        except FileNotFoundError:
            self.trainers = {}

    # --------------------------------------------------
    def go_to_trainer(
        self,
        profession: str,
        *,
        agent=None,
        planet: str | None = None,
        city: str | None = None,
    ) -> bool:
        """Navigate to the trainer location for ``profession``.

        This method performs waypoint travel and location verification only.
        It does not invoke :class:`TrainerScanner`.

        The trainer profile may contain multiple possible locations.  Each entry
        is attempted until one succeeds.  ``True`` is returned on success,
        ``False`` otherwise.
        """
        trainer = self.trainers.get(profession)
        if not trainer:
            return False

        entries = trainer if isinstance(trainer, list) else [trainer]

        for entry in entries:
            coords = (
                entry.get("waypoint")
                or entry.get("coords")
                or [entry.get("x", 0), entry.get("y", 0)]
            )
            p = planet or entry.get("planet")
            c = city or entry.get("city")

            try:
                if agent is None:
                    go_to_waypoint(coords, planet=p, city=c)
                    success = verify_location(coords, planet=p, city=c)
                else:
                    go_to_waypoint(coords, planet=p, city=c, agent=agent)
                    success = verify_location(coords, planet=p, city=c, agent=agent)
            except Exception:
                success = False

            if success:
                return True

        return False

    # --------------------------------------------------
    def train_profession(self, profession: str) -> List[str]:
        """Travel to the trainer for ``profession`` and return offered skills."""
        if profession not in self.trainers:
            return []

        success = self.go_to_trainer(profession)
        if not success:
            logger.info("[TravelManager] Failed to reach %s trainer", profession)
            return []

        skills = self.trainer_scanner.scan()
        return skills

    # --------------------------------------------------
    def plan_multi_hop_route(
        self,
        start_city: str,
        dest_city: str,
        *,
        start_planet: str = "tatooine",
        dest_planet: str | None = None,
    ) -> list[dict]:
        """Placeholder for future pathfinding between cities."""
        logger.info(
            "[TravelManager] Multi-hop route planning not implemented yet"
        )
        return []

"""Utilities for loading and tracking profession builds."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from modules.professions import progress_tracker


BUILD_DIR = Path(__file__).resolve().parents[1] / "profiles" / "builds"


class BuildManager:
    """Load build files and determine skill progression."""

    def __init__(self, build_name: str | None = None) -> None:
        self.profession: str = ""
        self.skills: List[str] = []
        self.xp_costs: Dict[str, int] = {}
        if build_name is not None:
            self.load_build(build_name)

    # --------------------------------------------------------------
    def load_build(self, name: str) -> None:
        """Load build ``name`` from :data:`BUILD_DIR`."""

        extensions = [".json", ".txt"]
        data = None
        for ext in extensions:
            path = BUILD_DIR / f"{name}{ext}"
            if path.exists():
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                break
        if data is None:
            raise FileNotFoundError(f"Build file not found: {name}")

        self.profession = str(data.get("profession", ""))
        self.skills = list(data.get("skills", []))

        try:
            prof_data = progress_tracker.load_profession(self.profession.lower())
            xp_map = prof_data.get("xp_costs", {})
        except Exception:
            xp_map = {}

        self.xp_costs = {skill: int(xp_map.get(skill, 0)) for skill in self.skills}

    def _next_missing_skill(self, known_skills: Iterable[str]) -> Optional[str]:
        """Return the next skill in :attr:`skills` not in ``known_skills``."""

        for skill in self.skills:
            if skill not in known_skills:
                return skill
        return None

    # --------------------------------------------------------------
    def get_next_skill(self, known_skills: Iterable[str]) -> Optional[str]:
        """Return the next skill in the build not present in ``known_skills``."""

        return self._next_missing_skill(known_skills)

    # --------------------------------------------------------------
    def get_next_trainable_skill(self, current_skills: Iterable[str]) -> Optional[str]:
        """Return the next skill that has not yet been learned."""

        return self._next_missing_skill(current_skills)

    # --------------------------------------------------------------
    def is_skill_completed(self, skill: str, known_skills: Iterable[str]) -> bool:
        """Return ``True`` if ``skill`` is contained in ``known_skills``."""

        return skill in known_skills

    # --------------------------------------------------------------
    def is_build_complete(self, current_skills: Iterable[str]) -> bool:
        """Return ``True`` if all skills for the build have been learned."""

        return self.get_next_trainable_skill(current_skills) is None

    # --------------------------------------------------------------
    def get_required_xp(self, skill: str) -> int:
        """Return the XP required for ``skill`` according to the build."""

        return int(self.xp_costs.get(skill, 0))

    # --------------------------------------------------------------
    def get_completed_skills(self) -> list[str]:
        """Return a list of build skills recorded as completed in the session."""

        from core.session_tracker import load_session

        session = load_session()
        completed = session.get("skills_completed", [])
        return [s for s in self.skills if s in completed]


from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

from src.vision.ocr import screen_text
from core.session_tracker import log_farming_result
from utils.logger import logger
from utils.load_mob_affinity import load_mob_affinity

# Load mob affinity mapping once so filtering does not repeatedly read the file.
AFFINITY_MAP = load_mob_affinity()

Mission = Dict[str, int | str | Tuple[int, int]]

_MISSION_RE = re.compile(
    r"(?P<name>[\w '\-]+)\s+(?P<x>-?\d+)\s*[,:]?\s*(?P<y>-?\d+)\s+"
    r"(?P<distance>\d+)m(?:\s+(?P<credits>\d+)c)?",
    re.IGNORECASE,
)


class TerminalFarmer:
    """Parse and accept bounty missions from a terminal."""

    def __init__(self, profile_path: str = "config/farming_profile.json") -> None:
        path = Path(profile_path)
        self.profile: Dict[str, object] = {}
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                self.profile = json.load(fh)

    # --------------------------------------------------
    def parse_missions(self, text: str) -> List[Mission]:
        """Return list of mission details parsed from ``text``."""
        missions: List[Mission] = []
        for line in text.splitlines():
            match = _MISSION_RE.search(line)
            if not match:
                continue
            mission: Mission = {
                "name": match.group("name").strip(),
                "coords": (int(match.group("x")), int(match.group("y"))),
                "distance": int(match.group("distance")),
            }
            if match.group("credits"):
                mission["credits"] = int(match.group("credits"))
            missions.append(mission)
        return missions

    # --------------------------------------------------
    def filter_missions(self, missions: List[Mission]) -> List[Mission]:
        """Return missions matching distance and class requirements."""
        distance_limit = int(self.profile.get("distance_limit", 9999))
        filtered = [m for m in missions if m["distance"] <= distance_limit]

        requirements = self.profile.get("class_requirements", [])
        if not requirements:
            return filtered

        keywords: list[str] = []
        for prof in requirements:
            keywords.extend(AFFINITY_MAP.get(prof, []))

        if not keywords:
            return filtered

        result: List[Mission] = []
        for mission in filtered:
            name = str(mission.get("name", "")).lower()
            if any(k.lower() in name for k in keywords):
                result.append(mission)
        return result

    # --------------------------------------------------
    def execute_run(self, *, board_text: str | None = None) -> List[Mission]:
        """Parse and filter missions from the terminal screen."""
        if board_text is None:
            board_text = screen_text()
        missions = self.parse_missions(board_text)
        accepted = self.filter_missions(missions)
        for mission in accepted:
            coords = mission["coords"]
            logger.info(
                "[TerminalFarmer] Mission %s at %s %dm",
                mission["name"],
                coords,
                mission["distance"],
            )
        if accepted:
            earned = sum(int(m.get("credits", 0)) for m in accepted)
            log_farming_result(
                [m["name"] for m in accepted],
                earned,
            )
        return accepted


__all__ = ["TerminalFarmer"]

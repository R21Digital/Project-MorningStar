from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

from src.vision.ocr import screen_text
from core.session_tracker import log_farming_result

Mission = Dict[str, int | str | Tuple[int, int]]

_MISSION_RE = re.compile(
    r"(?P<name>[\w '\-]+)\s+(?P<x>-?\d+)\s*[,:]?\s*(?P<y>-?\d+)\s+(?P<distance>\d+)m",
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
            missions.append(mission)
        return missions

    # --------------------------------------------------
    def execute_run(self, *, board_text: str | None = None) -> List[Mission]:
        """Parse and filter missions from the terminal screen."""
        if board_text is None:
            board_text = screen_text()
        missions = self.parse_missions(board_text)
        max_distance = int(self.profile.get("max_distance", 9999))
        accepted = [m for m in missions if m["distance"] <= max_distance]
        for mission in accepted:
            coords = mission["coords"]
            print(
                f"[TerminalFarmer] Mission {mission['name']} at {coords} {mission['distance']}m"
            )
        if accepted:
            log_farming_result(
                [m["name"] for m in accepted],
                len(accepted),
            )
        return accepted


__all__ = ["TerminalFarmer"]

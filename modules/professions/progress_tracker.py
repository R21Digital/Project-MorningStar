import json
import os
import re
from typing import List, Optional, Dict

from modules.learning import xp_estimator

# Default location for profession metadata JSON files
DATA_DIR = os.path.join("android_ms11", "data", "professions")


def _skill_name(text: str) -> str:
    """Return the skill name without any parenthetical notes."""
    return re.sub(r"\([^)]*\)", "", text).strip()


def load_profession(profession: str) -> Dict:
    """Load profession data from ``DATA_DIR``."""
    path = os.path.join(DATA_DIR, f"{profession.lower()}.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def has_prerequisites(profession: str, skills: List[str]) -> bool:
    """Return ``True`` if all profession prerequisites are met."""
    data = load_profession(profession)
    prereqs = data.get("prerequisites", [])
    return all(p in skills for p in prereqs)


def recommend_next_skill(profession: str, skills: List[str]) -> Optional[Dict[str, int]]:
    """Return the next skill box to pursue and its XP cost."""
    data = load_profession(profession)
    for prereq in data.get("prerequisites", []):
        if prereq not in skills:
            return {"skill": prereq, "xp": 0}

    for entry in data.get("skill_boxes", []):
        name = _skill_name(entry)
        if name not in skills:
            xp_cost = data.get("xp_costs", {}).get(name, 0)
            return {"skill": name, "xp": xp_cost}
    return None


def estimate_hours_to_next_skill(profession: str, skills: List[str], activity: str) -> Optional[float]:
    """Estimate hours needed to reach the XP for the next skill."""
    rec = recommend_next_skill(profession, skills)
    if not rec or rec["xp"] <= 0:
        return 0.0 if rec else None

    xp_per_hour = xp_estimator.estimate_xp_per_hour(profession, activity)
    if xp_per_hour <= 0:
        return float("inf")
    return rec["xp"] / xp_per_hour

"""Default profession skill requirements and trainer locations."""

from utils.load_trainers import load_trainers

REQUIRED_SKILLS = {
    "Artisan": ["crafting_artisan_novice"],
    "Marksman": ["combat_marksman_novice"],
    "Medic": ["science_medic_novice"],
    "Scout": ["outdoors_scout_novice"],
    "Brawler": ["combat_brawler_novice"],
    "Entertainer": ["social_entertainer_novice"],
    "Rifleman": ["combat_rifleman_novice"],
    "Pistoleer": ["combat_pistoleer_novice"],
    "Carbineer": ["combat_carbineer_novice"],
}


def _primary(entries):
    if not entries:
        return {}
    first = entries[0]
    return {
        "planet": first.get("planet"),
        "city": first.get("city"),
        "coords": first.get("coords"),
        "name": first.get("name"),
    }


TRAINER_BY_PROFESSION = {
    prof: _primary(entries) for prof, entries in load_trainers().items()
}

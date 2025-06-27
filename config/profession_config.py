"""Default profession skill requirements and trainer locations."""

REQUIRED_SKILLS = {
    "artisan": ["Novice Artisan"],
    "marksman": ["Novice Marksman"],
}

from utils.load_trainers import load_trainers


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

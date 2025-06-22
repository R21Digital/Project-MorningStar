from typing import Dict, Iterable

REQUIRED_FIELDS = ("id", "title", "steps")


def verify_fields(data: Dict, required_fields: Iterable[str] = REQUIRED_FIELDS) -> bool:
    """Return ``True`` if all required fields are present in ``data``."""
    return all(field in data for field in required_fields)


def sanitize_quest_data(data: Dict) -> Dict:
    """Validate and sanitize quest data from an external source."""
    if not verify_fields(data):
        raise ValueError("Missing required quest fields")

    return {
        "id": int(data["id"]),
        "title": str(data["title"]),
        "steps": list(data["steps"]),
    }

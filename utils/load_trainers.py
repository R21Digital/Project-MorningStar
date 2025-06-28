import os
import json
import yaml
from pathlib import Path
import logging

# Paths to the trainer location files.  ``TRAINER_FILE`` points to the legacy
# YAML data while ``TRAINER_JSON_FILE`` is the new preferred location.  Both
# paths are resolved relative to this module to avoid depending on the caller's
# working directory.
TRAINER_FILE = Path(__file__).resolve().parents[1] / "data" / "trainers.yaml"
TRAINER_JSON_FILE = (
    Path(__file__).resolve().parents[1] / "data" / "trainers.json"
)


def _normalize_entry(entry: dict) -> dict:
    """Return entry with ``coords`` list and standard keys."""
    coords = entry.get("coords")
    if not coords:
        coords = entry.get("coordinates")
    if not coords:
        coords = entry.get("waypoint")
    if not coords and "x" in entry and "y" in entry:
        coords = [entry.get("x"), entry.get("y")]
    return {
        "planet": entry.get("planet"),
        "city": entry.get("city"),
        "coords": coords,
        "name": entry.get("name"),
    }


def _normalize(data: dict) -> dict:
    """Normalize trainer mapping to lists of standard entries."""
    normalized = {}
    for profession, value in data.items():
        entries = []
        if isinstance(value, list):
            for item in value:
                entries.append(_normalize_entry(item))
        elif isinstance(value, dict) and "planet" in value:
            entries.append(_normalize_entry(value))
        elif isinstance(value, dict):
            for planet, cities in value.items():
                for city, info in cities.items():
                    entry = {"planet": planet, "city": city, **info}
                    entries.append(_normalize_entry(entry))
        normalized[profession] = entries
    return normalized


def load_trainers(trainer_file=None):
    """Return trainer location data.

    The path to the trainer file is determined using the following
    precedence:

    1. **Argument** ``trainer_file`` – typically provided by a command-line
       option.
    2. **Environment variable** ``TRAINER_FILE``.
    3. **Default** location under :data:`TRAINER_JSON_FILE` or
       :data:`TRAINER_FILE`.

    ``TRAINER_JSON_FILE`` is preferred when present; otherwise the legacy
    YAML file is loaded.

    Example
    -------
    >>> from utils.load_trainers import load_trainers
    >>> data = load_trainers("/tmp/custom_trainers.yaml")

    If the file is missing, an empty dictionary is returned and a warning
    is logged.  This mirrors the behavior of the original loader found under
    ``src/training``.
    """
    env_override = os.environ.get("TRAINER_FILE")
    if trainer_file:
        trainer_path = Path(trainer_file)
    elif env_override:
        trainer_path = Path(env_override)
    else:
        # Prefer the JSON file when it exists.
        trainer_path = TRAINER_JSON_FILE if TRAINER_JSON_FILE.exists() else TRAINER_FILE

    try:
        with open(trainer_path, "r") as fh:
            if trainer_path.suffix.lower() == ".json":
                raw = json.load(fh)
            else:
                raw = yaml.safe_load(fh)
        return _normalize(raw)
    except FileNotFoundError:  # pragma: no cover - best effort logging
        logging.warning(
            f"Trainer file {trainer_path} not found. Returning empty dict."
        )
        return {}

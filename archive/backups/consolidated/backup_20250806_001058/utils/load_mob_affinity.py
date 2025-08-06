import json
import os
from pathlib import Path
import logging

MOB_AFFINITY_FILE = Path(__file__).resolve().parents[1] / "data" / "mob_affinity.json"


def load_mob_affinity(affinity_file: str | Path | None = None) -> dict:
    """Return mob affinity mapping from ``affinity_file`` or default path.

    The loader resolves the file path using the following precedence:

    1. **Argument** ``affinity_file`` if provided.
    2. **Environment variable** ``MOB_AFFINITY_FILE``.
    3. **Default** :data:`MOB_AFFINITY_FILE` location under ``data``.

    When the file cannot be read a warning is logged and an empty
    dictionary is returned.
    """
    env_override = os.environ.get("MOB_AFFINITY_FILE")
    if affinity_file:
        path = Path(affinity_file)
    elif env_override:
        path = Path(env_override)
    else:
        path = MOB_AFFINITY_FILE

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data
    except FileNotFoundError:  # pragma: no cover - best effort logging
        logging.warning(f"Mob affinity file {path} not found. Returning empty dict.")
    except Exception:  # pragma: no cover - best effort logging
        logging.warning(f"Failed to load mob affinity file {path}. Returning empty dict.")

    return {}


__all__ = ["load_mob_affinity", "MOB_AFFINITY_FILE"]

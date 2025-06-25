import yaml
from pathlib import Path
import logging

# Path to the YAML file containing trainer locations
TRAINER_FILE = Path(__file__).resolve().parent.parent / "data" / "trainers.yaml"


def load_trainers():
    """Return trainer location data from ``TRAINER_FILE``.

    If the YAML file is missing, an empty dictionary is returned and a warning
    is logged. This mirrors the behavior of the original loader found under
    ``src/training``.
    """
    try:
        with open(TRAINER_FILE, "r") as fh:
            return yaml.safe_load(fh)
    except FileNotFoundError:  # pragma: no cover - best effort logging
        logging.warning(f"Trainer file {TRAINER_FILE} not found. Returning empty dict.")
        return {}

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
    Path(__file__).resolve().parents[1] / "data" / "trainers" / "trainers.json"
)


def load_trainers(trainer_file=None):
    """Return trainer location data.

    ``trainer_file`` overrides the default path. If omitted, the environment
    variable ``TRAINER_FILE`` is checked before falling back to the module
    constant.

    If the YAML file is missing, an empty dictionary is returned and a warning
    is logged. This mirrors the behavior of the original loader found under
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
                return json.load(fh)
            return yaml.safe_load(fh)
    except FileNotFoundError:  # pragma: no cover - best effort logging
        logging.warning(
            f"Trainer file {trainer_path} not found. Returning empty dict."
        )
        return {}

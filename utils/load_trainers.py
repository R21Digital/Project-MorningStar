import os
import yaml
from pathlib import Path
import logging

# Path to the YAML file containing trainer locations. Resolved relative to this
# module to avoid depending on the caller's working directory.
TRAINER_FILE = Path(__file__).resolve().parents[1] / "data" / "trainers.yaml"


def load_trainers(trainer_file=None):
    """Return trainer location data.

    ``trainer_file`` overrides the default path. If omitted, the environment
    variable ``TRAINER_FILE`` is checked before falling back to the module
    constant.

    If the YAML file is missing, an empty dictionary is returned and a warning
    is logged. This mirrors the behavior of the original loader found under
    ``src/training``.
    """
    trainer_path = Path(
        trainer_file
        or os.environ.get("TRAINER_FILE", TRAINER_FILE)
    )

    try:
        with open(trainer_path, "r") as fh:
            return yaml.safe_load(fh)
    except FileNotFoundError:  # pragma: no cover - best effort logging
        logging.warning(
            f"Trainer file {trainer_path} not found. Returning empty dict."
        )
        return {}

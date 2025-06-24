import yaml
from pathlib import Path
import logging

TRAINER_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "trainers.yaml"


def load_trainer_data():
    try:
        with open(TRAINER_FILE, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:  # pragma: no cover - best effort logging
        logging.warning(f"Trainer file {TRAINER_FILE} not found. Returning empty dict.")
        return {}


def get_trainer_coords(profession, planet, city):
    data = load_trainer_data()
    try:
        trainer = data[profession][planet][city]
        return (trainer['name'], trainer['x'], trainer['y'])
    except KeyError:
        return None

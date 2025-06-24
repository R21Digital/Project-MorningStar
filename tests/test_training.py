import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.automation.training import train_with_npc
from pathlib import Path
from src.training.trainer_data_loader import get_trainer_coords, load_trainer_data
from src.training.trainer_visit import visit_trainer


class DummyAgent:
    def __init__(self):
        self.destination = None

    def move_to(self):
        print(f"Moving to {self.destination}")


def test_train_with_npc(capfd):
    step = {"type": "dialogue", "npc": "Trainer"}
    train_with_npc(step)
    out, _ = capfd.readouterr()
    assert "Learning new abilities from Trainer" in out


def test_get_trainer_coords():
    result = get_trainer_coords("artisan", "tatooine", "mos_eisley")
    assert result == ("Artisan Trainer", 3432, -4795)


def test_visit_trainer_found(monkeypatch, capsys):
    agent = DummyAgent()

    called = {}

    def fake_travel(agent_obj, destination):
        called["dest"] = destination

    monkeypatch.setattr("src.training.trainer_visit.travel_to_city", fake_travel)
    visit_trainer(agent, "artisan", planet="tatooine", city="mos_eisley")
    out = capsys.readouterr().out
    assert "Artisan Trainer" in out
    assert called["dest"] == "mos_eisley"


def test_visit_trainer_missing(monkeypatch, capsys):
    agent = DummyAgent()
    monkeypatch.setattr("src.training.trainer_visit.travel_to_city", lambda a, d: None)
    visit_trainer(agent, "medic", planet="naboo", city="theed")
    out = capsys.readouterr().out
    assert "No static data" in out


def test_load_trainer_data_missing_file(monkeypatch):
    missing = Path("nonexistent_file.yaml")
    monkeypatch.setattr("src.training.trainer_data_loader.TRAINER_FILE", missing)
    data = load_trainer_data()
    assert data == {}

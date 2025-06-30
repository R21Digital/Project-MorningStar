import pytest
from core.train_manager import TrainManager


def test_train_missing_skills(monkeypatch):
    monkeypatch.setattr('utils.skills.get_player_skills', lambda: [])
    monkeypatch.setattr('utils.travel.travel_to', lambda p, c, co: print(f"Mock travel to {c}, {p}, {co}"))

    tm = TrainManager(build_path='config/builds/rifleman_medic.json', trainer_db='data/trainers_simple.json')
    tm.train_missing_skills('tatooine')
    assert "science_medic_novice" in tm.trained_skills

import logging
from core.train_manager import TrainManager


def test_train_missing_skills(monkeypatch, caplog):
    monkeypatch.setattr("utils.skills.get_player_skills", lambda: [])
    monkeypatch.setattr("utils.travel.travel_to", lambda *a, **k: None)
    monkeypatch.setattr(
        "core.train_manager.plan_travel_to_trainer",
        lambda t: ["step1", "step2"],
    )

    tm = TrainManager(
        build_path="config/builds/rifleman_medic.json",
        trainer_db="data/trainers_simple.json",
    )
    with caplog.at_level(logging.INFO, logger="ms11"):
        tm.train_missing_skills("tatooine")

    assert "science_medic_novice" in tm.trained_skills
    assert any("step1" in rec.message for rec in caplog.records)


def test_load_trainers_distance_field():
    tm = TrainManager(build_path='config/builds/rifleman_medic.json', trainer_db='data/trainers_simple.json')
    trainers = tm.load_trainers()
    assert all('distance_to_city' in t for t in trainers)
    assert all(isinstance(t['distance_to_city'], float) for t in trainers)

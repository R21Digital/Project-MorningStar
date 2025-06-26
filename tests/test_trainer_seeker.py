import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.training import trainer_seeker


def test_seek_training_no_skill(monkeypatch):
    monkeypatch.setattr(trainer_seeker.progress_tracker, "recommend_next_skill", lambda p, s: None)
    called = {}
    monkeypatch.setattr(trainer_seeker.trainer_navigator, "log_event", lambda msg: called.setdefault("log", msg))
    result = trainer_seeker.seek_training("medic", [])
    assert result is False
    assert "No further skills" in called["log"]


def test_seek_training_insufficient_xp(monkeypatch):
    monkeypatch.setattr(trainer_seeker.progress_tracker, "recommend_next_skill", lambda p, s: {"skill": "Intermediate", "xp": 1000})
    monkeypatch.setattr(trainer_seeker, "read_xp_via_ocr", lambda: 500)
    called = {}
    monkeypatch.setattr(trainer_seeker.trainer_navigator, "log_event", lambda msg: called.setdefault("log", msg))
    result = trainer_seeker.seek_training("medic", [])
    assert result is False
    assert "need 1000 XP" in called["log"]


def test_seek_training_success(monkeypatch):
    monkeypatch.setattr(trainer_seeker.progress_tracker, "recommend_next_skill", lambda p, s: {"skill": "Intermediate", "xp": 500})
    monkeypatch.setattr(trainer_seeker, "read_xp_via_ocr", lambda: 1000)
    calls = {}
    monkeypatch.setattr(trainer_seeker, "visit_trainer", lambda a, profession, planet="tatooine", city="mos_eisley": calls.setdefault("visit", (profession, planet, city)))
    monkeypatch.setattr(trainer_seeker.trainer_navigator, "log_event", lambda msg: calls.setdefault("log", []).append(msg))
    monkeypatch.setattr(trainer_seeker.trainer_navigator, "log_training_event", lambda *a, **k: calls.setdefault("train", True))
    monkeypatch.setattr(trainer_seeker, "_run_training_macro", lambda skill: calls.setdefault("macro", skill))

    result = trainer_seeker.seek_training("medic", ["Novice Artisan"], agent="A", planet="corellia", city="coronet")

    assert result is True
    assert calls["visit"] == ("medic", "corellia", "coronet")
    assert calls["macro"] == "Intermediate"
    assert calls.get("train") is True

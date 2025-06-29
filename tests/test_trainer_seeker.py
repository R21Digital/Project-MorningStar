import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.training import trainer_seeker
from unittest.mock import MagicMock


class DummyBuild:
    def __init__(self, skill=None, xp=0):
        self.skill = skill
        self.xp = xp

    def get_next_skill(self, skills):
        return self.skill

    def get_required_xp(self, skill):
        return self.xp


def test_seek_training_no_skill(monkeypatch):
    bm = DummyBuild()
    called = []
    monkeypatch.setattr(trainer_seeker.trainer_navigator, "log_event", lambda msg: called.append(msg))
    result = trainer_seeker.seek_training("medic", [], build_manager=bm)
    assert result is False
    assert any("No further skills" in m for m in called)


def test_seek_training_insufficient_xp(monkeypatch):
    bm = DummyBuild("Intermediate", 1000)
    monkeypatch.setattr(trainer_seeker, "read_xp_via_ocr", lambda: 500)
    called = []
    monkeypatch.setattr(trainer_seeker.trainer_navigator, "log_event", lambda msg: called.append(msg))
    result = trainer_seeker.seek_training("medic", [], build_manager=bm)
    assert result is False
    assert any("need 1000 XP" in m for m in called)


def test_seek_training_success(monkeypatch):
    bm = DummyBuild("Intermediate", 500)
    monkeypatch.setattr(trainer_seeker, "read_xp_via_ocr", lambda: 1000)
    calls = {}
    tm = MagicMock()
    tm.go_to_trainer = lambda prof, agent=None: calls.setdefault("go", (prof, agent)) or True
    monkeypatch.setattr(trainer_seeker.trainer_navigator, "log_event", lambda msg: calls.setdefault("log", []).append(msg))
    monkeypatch.setattr(trainer_seeker.trainer_navigator, "log_training_event", lambda *a, **k: calls.setdefault("train", True))
    monkeypatch.setattr(trainer_seeker, "_run_training_macro", lambda skill: calls.setdefault("macro", skill))

    result = trainer_seeker.seek_training("medic", ["Novice Artisan"], agent="A", planet="corellia", city="coronet", build_manager=bm, travel_manager=tm)

    assert result is True
    assert calls["go"] == ("medic", "A")
    assert calls["macro"] == "Intermediate"
    assert calls.get("train") is True


def test_seek_training_busy_defers(monkeypatch):
    bm = DummyBuild("Intermediate", 500)
    monkeypatch.setattr(trainer_seeker, "read_xp_via_ocr", lambda: 1000)
    tm = MagicMock()
    def raise_busy(prof, agent=None):
        raise Exception("busy")
    tm.go_to_trainer = raise_busy
    called = []
    monkeypatch.setattr(trainer_seeker.trainer_navigator, "log_event", lambda msg: called.append(msg))

    result = trainer_seeker.seek_training("medic", ["Novice"], build_manager=bm, travel_manager=tm)

    assert result is False
    assert any("busy" in m for m in called)


def test_seek_training_all_fail(monkeypatch, tmp_path):
    bm = DummyBuild("Intermediate", 500)
    monkeypatch.setattr(trainer_seeker, "read_xp_via_ocr", lambda: 1000)
    tm = MagicMock()
    tm.go_to_trainer = lambda prof, agent=None: False
    calls = {}
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(trainer_seeker.trainer_navigator, "log_event", lambda msg: calls.setdefault("log", msg))
    monkeypatch.setattr(trainer_seeker, "_send_discord_alert", lambda msg: calls.setdefault("alert", msg))

    result = trainer_seeker.seek_training("medic", ["Novice"], build_manager=bm, travel_manager=tm)

    assert result is False
    assert calls.get("alert")
    log_file = tmp_path / "logs" / "training_log.txt"
    assert log_file.exists()

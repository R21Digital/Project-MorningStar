import os
import sys
from importlib import reload

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.logic import trainer_navigator as tn


class DummyLoad:
    def __init__(self, data):
        self.data = data
        self.called = False

    def __call__(self, *a, **k):
        self.called = True
        return self.data


def test_find_nearby_trainers(monkeypatch):
    data = {
        "artisan": {"tatooine": {"mos_eisley": {"name": "Art", "x": 0, "y": 0}}},
        "marksman": {"tatooine": {"mos_eisley": {"name": "Mark", "x": 10, "y": 0}}},
    }
    loader = DummyLoad(data)
    monkeypatch.setattr(tn, "load_trainers", loader)

    result = tn.find_nearby_trainers((0, 0), "tatooine", "mos_eisley", threshold=11)
    assert loader.called
    assert len(result) == 2
    assert result[0]["name"] == "Art"
    assert result[1]["name"] == "Mark"
    assert result[1]["distance"] > result[0]["distance"]


def test_threshold(monkeypatch):
    data = {
        "artisan": {"tatooine": {"mos_eisley": {"name": "Art", "x": 100, "y": 0}}}
    }
    loader = DummyLoad(data)
    monkeypatch.setattr(tn, "load_trainers", loader)

    result = tn.find_nearby_trainers((0, 0), "tatooine", "mos_eisley", threshold=50)
    assert result == []


def test_log_training_event(tmp_path):
    log_file = tmp_path / "subdir" / "log.txt"
    tn.log_training_event("artisan", "Artisan Trainer", 5.0, log_path=str(log_file))
    assert log_file.exists()
    content = log_file.read_text()
    assert "Artisan Trainer" in content


def test_find_nearby_trainers_sorted(monkeypatch):
    data = {
        "artisan": {"tatooine": {"mos_eisley": {"name": "Art", "x": 1, "y": 0}}},
        "brawler": {"tatooine": {"mos_eisley": {"name": "Brawl", "x": 3, "y": 0}}},
        "marksman": {"tatooine": {"mos_eisley": {"name": "Mark", "x": 5, "y": 0}}},
    }
    loader = DummyLoad(data)
    monkeypatch.setattr(tn, "load_trainers", loader)

    result = tn.find_nearby_trainers((0, 0), "tatooine", "mos_eisley", threshold=10)
    names = [r["name"] for r in result]
    distances = [r["distance"] for r in result]

    assert names == ["Art", "Brawl", "Mark"]
    assert distances == sorted(distances)


def test_log_training_event_default_appends(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    tn.log_training_event("artisan", "Artisan Trainer", 5.0)
    log_file = tmp_path / "logs" / "training_log.txt"
    assert log_file.exists()
    first = log_file.read_text().splitlines()
    assert len(first) == 1

    tn.log_training_event("medic", "Medic Trainer", 7.0)
    second = log_file.read_text().splitlines()
    assert len(second) == 2
    assert first[0] != second[1]


def test_navigate_to_trainer_calls_helpers(monkeypatch):
    calls = {}

    def fake_visit(agent, prof, planet="tatooine", city="mos_eisley"):
        calls["visit"] = (agent, prof, planet, city)

    def fake_log(prof, name, dist, log_path=tn.DEFAULT_LOG_PATH):
        calls["log"] = (prof, name, dist)

    monkeypatch.setattr(tn, "visit_trainer", fake_visit)
    monkeypatch.setattr(tn, "log_training_event", fake_log)
    monkeypatch.setattr(tn, "get_trainer_location", lambda *a, **k: ("Trainer", 1, 2))

    tn.navigate_to_trainer("artisan", "tatooine", "mos_eisley", agent="A")

    assert calls["visit"] == ("A", "artisan", "tatooine", "mos_eisley")
    assert calls["log"] == ("artisan", "Trainer", 0.0)

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.automation.training import train_with_npc
from pathlib import Path
from utils.get_trainer_location import get_trainer_location
from utils.load_trainers import load_trainers
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


def test_get_trainer_location():
    result = get_trainer_location("artisan", "tatooine", "mos_eisley")
    assert result == ("Artisan Trainer", 3432, -4795)


def test_visit_trainer_found(monkeypatch, capsys):
    agent = DummyAgent()

    called = {}

    def fake_travel(agent_obj, destination):
        called["dest"] = destination

    def fake_coords(agent_obj, x, y):
        called["coords"] = (x, y)

    monkeypatch.setattr("src.training.trainer_visit.travel_to_city", fake_travel)
    monkeypatch.setattr(
        "src.training.trainer_visit.walk_to_coords",
        fake_coords,
    )
    visit_trainer(agent, "artisan", planet="tatooine", city="mos_eisley")
    out = capsys.readouterr().out
    assert "Artisan Trainer" in out
    assert called["dest"] == "mos_eisley"
    assert called["coords"] == (3432, -4795)


def test_visit_trainer_missing(monkeypatch, capsys):
    from src.training import trainer_visit

    agent = DummyAgent()
    walk_calls = []

    monkeypatch.setattr("src.training.trainer_visit.travel_to_city", lambda a, d: None)
    monkeypatch.setattr(
        "src.training.trainer_visit.walk_to_coords",
        lambda a, x, y: walk_calls.append((x, y)),
    )

    trainer_visit.visited_npcs.clear()

    visit_trainer(agent, "medic", planet="naboo", city="theed")
    out = capsys.readouterr().out
    assert "Trainer not found" in out
    assert "/find medic trainer" in out
    assert (0, 0) in walk_calls
    assert (10, 10) in walk_calls
    assert "medic trainer" in trainer_visit.visited_npcs


def test_load_trainers_missing_file(monkeypatch):
    missing = Path("nonexistent_file.yaml")
    monkeypatch.setattr("utils.load_trainers.TRAINER_FILE", missing)
    monkeypatch.setattr("utils.load_trainers.TRAINER_JSON_FILE", missing)
    monkeypatch.delenv("TRAINER_FILE", raising=False)
    data = load_trainers()
    assert data == {}


def test_load_trainers_env_override(monkeypatch, tmp_path):
    import io
    custom = tmp_path / "custom.yaml"

    calls = {}

    def fake_open(path, *a, **k):
        calls["path"] = Path(path)
        return io.StringIO("{}")

    monkeypatch.setenv("TRAINER_FILE", str(custom))
    monkeypatch.setattr("builtins.open", fake_open)
    load_trainers()
    assert calls["path"] == custom


def test_load_trainers_arg_override(monkeypatch, tmp_path):
    import io
    custom = tmp_path / "override.yaml"
    calls = {}

    def fake_open(path, *a, **k):
        calls["path"] = Path(path)
        return io.StringIO("{}")

    monkeypatch.setenv("TRAINER_FILE", "ignored")
    monkeypatch.setattr("builtins.open", fake_open)
    load_trainers(trainer_file=custom)
    assert calls["path"] == custom


def test_load_trainers_resolves_default(monkeypatch, tmp_path):
    import io

    from utils import load_trainers as lt

    calls = {}

    def fake_open(path, *a, **k):
        calls["path"] = Path(path)
        return io.StringIO("{}")

    monkeypatch.delenv("TRAINER_FILE", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.open", fake_open)
    lt.load_trainers()
    assert calls["path"] == lt.TRAINER_JSON_FILE


def test_load_trainers_default_path(monkeypatch, tmp_path):
    """load_trainers should read from data/trainers.json when no overrides are provided."""
    import io

    from utils import load_trainers as lt

    calls = {}

    def fake_open(path, *a, **k):
        calls["path"] = Path(path)
        return io.StringIO("{}")

    monkeypatch.delenv("TRAINER_FILE", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("builtins.open", fake_open)
    lt.load_trainers()
    expected = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "trainers.json"
    )
    assert lt.TRAINER_JSON_FILE == expected
    assert calls["path"] == expected


def test_normalize_entry_waypoint_only():
    from utils import load_trainers as lt

    entry = {
        "planet": "corellia",
        "city": "coronet",
        "name": "Example",
        "waypoint": [1, 2],
    }

    result = lt._normalize_entry(entry)
    assert result["coords"] == [1, 2]


def test_train_profession_uses_waypoint(monkeypatch):
    from core import TravelManager

    monkeypatch.setattr(TravelManager, "load_trainers", lambda self: None)
    tm = TravelManager(trainer_file="dummy.json")
    tm.trainers = {
        "demo": {
            "waypoint": [5, 6],
            "planet": "naboo",
            "city": "theed",
        }
    }

    tm.trainer_scanner = type(
        "S",
        (),
        {"scan": lambda self: ["Skill"]},
    )()

    calls = {}

    monkeypatch.setattr(
        "core.travel_manager.go_to_waypoint",
        lambda coords, planet=None, city=None: calls.setdefault(
            "go", (coords, planet, city)
        ),
    )
    monkeypatch.setattr(
        "core.travel_manager.verify_location",
        lambda coords, planet=None, city=None: calls.setdefault(
            "verify", (coords, planet, city)
        ),
    )

    skills = tm.train_profession("demo")
    assert skills == ["Skill"]
    assert calls["go"] == ([5, 6], "naboo", "theed")
    assert calls["verify"] == ([5, 6], "naboo", "theed")

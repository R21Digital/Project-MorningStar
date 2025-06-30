import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from android_ms11.modes import bounty_farming_mode
from core import farm_profile_loader


def test_run_travels_and_verifies(monkeypatch, tmp_path):
    data = {
        "planet": "tatooine",
        "city": "mos_eisley",
        "quest_type": "bounty",
        "preferred_directions": [],
        "distance_limit": 100,
    }
    farm_dir = tmp_path / "farms"
    farm_dir.mkdir()
    (farm_dir / "demo.json").write_text(json.dumps(data))
    monkeypatch.setattr(farm_profile_loader, "FARM_PROFILE_DIR", farm_dir)
    calls = []

    class DummyFarmer:
        def __init__(self):
            calls.append("farmer_init")

        def execute_run(self):
            calls.append("farmer_execute")

    monkeypatch.setattr(bounty_farming_mode, "TerminalFarmer", DummyFarmer)

    monkeypatch.setattr(
        bounty_farming_mode, "travel_to_target", lambda target, agent=None: calls.append(("travel", target))
    )
    monkeypatch.setattr(
        bounty_farming_mode,
        "locate_hotspot",
        lambda p, c, h: (calls.append(("locate", p, c, h)) or (1, 2)),
    )
    monkeypatch.setattr(
        bounty_farming_mode,
        "verify_waypoint_stability",
        lambda coords: calls.append(("verify", coords)),
    )

    logs = []

    class DummyLogger:
        def info(self, msg, *args):
            logs.append(msg % args)

    monkeypatch.setattr(bounty_farming_mode, "logger", DummyLogger())

    dummy_session = type("S", (), {"profile": {"build": {"skills": []}}})()
    bounty_farming_mode.run("demo", session=dummy_session)

    assert calls == [
        ("travel", {"planet": "tatooine", "city": "mos_eisley"}),
        ("locate", "tatooine", "mos_eisley", ""),
        "farmer_init",
        "farmer_execute",
        ("verify", (1, 2)),
    ]


def test_run_no_target(monkeypatch):
    monkeypatch.setattr(bounty_farming_mode, "travel_to_target", lambda *a, **k: 1)
    called = {}

    class DummyFarmer:
        def __init__(self):
            called["init"] = True

        def execute_run(self):
            called["exec"] = True

    monkeypatch.setattr(bounty_farming_mode, "TerminalFarmer", DummyFarmer)

    logs = []

    class DummyLogger:
        def info(self, msg, *args):
            logs.append(msg % args)

    monkeypatch.setattr(bounty_farming_mode, "logger", DummyLogger())

    dummy_session = type("S", (), {"profile": {"build": {"skills": []}}})()
    bounty_farming_mode.run({}, session=dummy_session)
    assert any("No farming_target" in m for m in logs)
    assert called == {}


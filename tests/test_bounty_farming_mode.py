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
        "max_distance": 100,
    }
    farm_dir = tmp_path / "farms"
    farm_dir.mkdir()
    (farm_dir / "demo.json").write_text(json.dumps(data))
    monkeypatch.setattr(farm_profile_loader, "FARM_PROFILE_DIR", farm_dir)
    calls = []

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

    dummy_session = type("S", (), {"profile": {"build": {"skills": []}}})()
    bounty_farming_mode.run("demo", session=dummy_session)

    assert calls == [
        ("travel", {"planet": "tatooine", "city": "mos_eisley"}),
        ("locate", "tatooine", "mos_eisley", ""),
        ("verify", (1, 2)),
    ]


def test_run_no_target(monkeypatch, capsys):
    monkeypatch.setattr(bounty_farming_mode, "travel_to_target", lambda *a, **k: 1)
    dummy_session = type("S", (), {"profile": {"build": {"skills": []}}})()
    bounty_farming_mode.run({}, session=dummy_session)
    out = capsys.readouterr().out
    assert "No farming_target" in out


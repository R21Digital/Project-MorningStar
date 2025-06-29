import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from android_ms11.modes import bounty_farming_mode


def test_run_travels_and_verifies(monkeypatch):
    profile = {
        "farming_target": {"planet": "tatooine", "city": "mos_eisley", "hotspot": "cantina"}
    }
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

    bounty_farming_mode.run(profile, session="S")

    assert calls == [
        ("travel", profile["farming_target"]),
        ("locate", "tatooine", "mos_eisley", "cantina"),
        ("verify", (1, 2)),
    ]


def test_run_no_target(monkeypatch, capsys):
    monkeypatch.setattr(bounty_farming_mode, "travel_to_target", lambda *a, **k: 1)
    bounty_farming_mode.run({})
    out = capsys.readouterr().out
    assert "No farming_target" in out


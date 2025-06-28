import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.profile_loader import load_profile, PROFILE_DIR


def test_load_profile_valid(tmp_path, monkeypatch):
    data = {
        "support_target": "Leader",
        "preferred_trainers": {"medic": "trainer"},
        "default_mode": "medic",
        "skip_modes": ["crafting"],
        "farming_targets": ["Bandit"]
    }
    path = tmp_path / "demo.json"
    path.write_text(json.dumps(data))
    monkeypatch.setattr("core.profile_loader.PROFILE_DIR", tmp_path)
    prof = load_profile("demo")
    assert prof == data


def test_load_profile_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("core.profile_loader.PROFILE_DIR", tmp_path)
    prof = load_profile("missing")
    assert prof == {}

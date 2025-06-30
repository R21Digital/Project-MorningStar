import json
import os
import sys
from pathlib import Path


from modules.combat.profiles import load_combat_profile


def test_load_combat_profile_valid(tmp_path, monkeypatch):
    data = {"enemy": "stormtrooper", "strategy": "burst"}
    prof_dir = tmp_path / "combat_profiles"
    prof_dir.mkdir()
    (prof_dir / "trooper.json").write_text(json.dumps(data))
    monkeypatch.setattr("modules.combat.profiles.PROFILES_DIR", prof_dir)

    prof = load_combat_profile("trooper")
    assert prof == data


def test_load_combat_profile_missing(tmp_path, monkeypatch):
    prof_dir = tmp_path / "combat_profiles"
    prof_dir.mkdir()
    monkeypatch.setattr("modules.combat.profiles.PROFILES_DIR", prof_dir)

    prof = load_combat_profile("missing")
    assert prof == {}


import json
import os
import sys
import pytest


from core.farm_profile_loader import load_farm_profile


def test_load_farm_profile_valid(tmp_path, monkeypatch):
    data = {
        "planet": "tatooine",
        "city": "mos_eisley",
        "quest_type": "bounty",
        "preferred_directions": ["north"],
        "distance_limit": 500,
    }
    farm_dir = tmp_path / "farms"
    farm_dir.mkdir()
    (farm_dir / "demo.json").write_text(json.dumps(data))
    monkeypatch.setattr("core.farm_profile_loader.FARM_PROFILE_DIR", farm_dir)

    prof = load_farm_profile("demo")
    assert prof == data


def test_load_farm_profile_missing_field(tmp_path, monkeypatch):
    data = {
        "planet": "tatooine",
        "city": "mos_eisley",
        "quest_type": "bounty",
        "preferred_directions": ["north"],
        # distance_limit missing
    }
    farm_dir = tmp_path / "farms"
    farm_dir.mkdir()
    (farm_dir / "bad.json").write_text(json.dumps(data))
    monkeypatch.setattr("core.farm_profile_loader.FARM_PROFILE_DIR", farm_dir)

    with pytest.raises(ValueError):
        load_farm_profile("bad")

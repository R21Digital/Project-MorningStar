import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.build_manager import BuildManager
from modules.professions import progress_tracker


def setup_build(tmp_path):
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    build_data = {
        "profession": "Medic",
        "skills": ["Novice Medic", "Intermediate Medicine"]
    }
    (build_dir / "basic.json").write_text(json.dumps(build_data))
    return build_dir, build_data


def mock_profession_data():
    return {
        "xp_costs": {
            "Novice Medic": 0,
            "Intermediate Medicine": 1000
        }
    }


def test_load_build(monkeypatch, tmp_path):
    build_dir, data = setup_build(tmp_path)
    monkeypatch.setattr("core.build_manager.BUILD_DIR", build_dir)
    monkeypatch.setattr(progress_tracker, "load_profession", lambda p: mock_profession_data())

    bm = BuildManager()
    bm.load_build("basic")

    assert bm.profession == "Medic"
    assert bm.skills == data["skills"]
    assert bm.get_required_xp("Intermediate Medicine") == 1000


def test_build_progression(monkeypatch, tmp_path):
    build_dir, _ = setup_build(tmp_path)
    monkeypatch.setattr("core.build_manager.BUILD_DIR", build_dir)
    monkeypatch.setattr(progress_tracker, "load_profession", lambda p: mock_profession_data())

    bm = BuildManager("basic")

    assert bm.get_next_skill([]) == "Novice Medic"
    assert bm.get_next_skill(["Novice Medic"]) == "Intermediate Medicine"
    assert bm.get_next_skill(["Novice Medic", "Intermediate Medicine"]) is None

    assert bm.is_skill_completed("Novice Medic", ["Novice Medic"]) is True
    assert bm.is_skill_completed("Intermediate Medicine", ["Novice Medic"]) is False

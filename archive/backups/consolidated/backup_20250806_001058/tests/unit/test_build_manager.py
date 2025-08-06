import json


import core.build_manager as build_manager
from core.build_manager import BuildManager
from modules.professions import progress_tracker
from core import session_tracker


def setup_build(tmp_path):
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    build_data = {
        "profession": "Medic",
        "skills": ["Novice Medic", "Intermediate Medicine"]
    }
    (build_dir / "basic.json").write_text(json.dumps(build_data))
    return build_dir, build_data


def setup_txt_build(tmp_path):
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    build_data = {
        "profession": "Medic",
        "skills": ["Novice Medic", "Intermediate Medicine"],
    }
    (build_dir / "basic.txt").write_text(json.dumps(build_data))
    return build_dir, build_data


def mock_profession_data():
    return {
        "xp_costs": {
            "Novice Medic": 0,
            "Intermediate Medicine": 1000
        }
    }


def test_load_build(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    build_dir, data = setup_build(tmp_path)
    monkeypatch.setattr("core.build_manager.BUILD_DIR", build_dir)
    monkeypatch.setattr(progress_tracker, "load_profession", lambda p: mock_profession_data())

    bm = BuildManager()
    bm.load_build("basic")

    assert bm.profession == "Medic"
    assert bm.skills == data["skills"]
    assert bm.get_required_xp("Intermediate Medicine") == 1000


def test_load_txt_build(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    build_dir, data = setup_txt_build(tmp_path)
    monkeypatch.setattr("core.build_manager.BUILD_DIR", build_dir)
    monkeypatch.setattr(progress_tracker, "load_profession", lambda p: mock_profession_data())

    bm = BuildManager()
    bm.load_build("basic")

    assert bm.profession == "Medic"
    assert bm.skills == data["skills"]
    assert bm.get_required_xp("Intermediate Medicine") == 1000


def test_build_progression(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    build_dir, _ = setup_build(tmp_path)
    monkeypatch.setattr("core.build_manager.BUILD_DIR", build_dir)
    monkeypatch.setattr(progress_tracker, "load_profession", lambda p: mock_profession_data())
    monkeypatch.setattr(session_tracker, "load_session", lambda: {"skills_completed": ["Novice Medic"]})

    bm = BuildManager("basic")

    assert bm.get_next_skill([]) == "Novice Medic"
    assert bm.get_next_skill(["Novice Medic"]) == "Intermediate Medicine"
    assert bm.get_next_skill(["Novice Medic", "Intermediate Medicine"]) is None

    assert bm.is_skill_completed("Novice Medic", ["Novice Medic"]) is True
    assert bm.is_skill_completed("Intermediate Medicine", ["Novice Medic"]) is False
    assert bm.get_completed_skills() == ["Novice Medic"]


def test_next_trainable_and_completion(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    build_dir, _ = setup_build(tmp_path)
    monkeypatch.setattr("core.build_manager.BUILD_DIR", build_dir)
    monkeypatch.setattr(progress_tracker, "load_profession", lambda p: mock_profession_data())

    bm = BuildManager("basic")

    # get_next_trainable_skill should mirror get_next_skill
    assert bm.get_next_trainable_skill([]) == bm.get_next_skill([])
    assert bm.get_next_trainable_skill(["Novice Medic"]) == bm.get_next_skill(["Novice Medic"])

    assert not bm.is_build_complete(["Novice Medic"])
    assert bm.is_build_complete(["Novice Medic", "Intermediate Medicine"])

    session = {"skills_completed": ["Novice Medic"]}
    monkeypatch.setattr(session_tracker, "load_session", lambda: session)

    assert bm.get_completed_skills() == ["Novice Medic"]

    session["skills_completed"].append("Intermediate Medicine")
    assert bm.get_completed_skills() == [
        "Novice Medic",
        "Intermediate Medicine",
    ]


def test_load_repo_txt_build(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    src_json = build_manager.BUILD_DIR / "basic.json"
    src_txt = build_manager.BUILD_DIR / "basic.txt"
    assert src_json.exists()
    assert src_txt.exists()
    backup = tmp_path / "basic.json.bak"
    src_json.rename(backup)
    try:
        monkeypatch.setattr(progress_tracker, "load_profession", lambda p: mock_profession_data())

        bm = BuildManager()
        bm.load_build("basic")

        assert bm.profession == "Combat Medic"
        assert bm.skills == ["Novice Medic"]
    finally:
        backup.rename(src_json)

def test_load_repo_rifleman_build(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        progress_tracker,
        "load_profession",
        lambda p: {
            "xp_costs": {
                "Novice Marksman": 0,
                "Master Rifleman": 8000,
            }
        },
    )

    bm = BuildManager("rifleman")

    assert bm.profession == "Rifleman"
    assert bm.skills == ["Novice Marksman", "Master Rifleman"]
    assert bm.get_required_xp("Master Rifleman") == 8000


def test_load_build_updates_session(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    build_dir, _ = setup_build(tmp_path)
    monkeypatch.setattr("core.build_manager.BUILD_DIR", build_dir)
    monkeypatch.setattr(progress_tracker, "load_profession", lambda p: mock_profession_data())

    session = {"current_build": "old", "skills_completed": ["foo"]}
    monkeypatch.setattr(session_tracker, "load_session", lambda: session)

    saved = {}

    def fake_save(data):
        saved.update(data)

    monkeypatch.setattr(session_tracker, "save_session", fake_save)

    bm = BuildManager()
    bm.load_build("basic")

    assert saved["current_build"] == "basic"
    assert saved["skills_completed"] == []


def test_load_build_unchanged_session(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    build_dir, _ = setup_build(tmp_path)
    monkeypatch.setattr("core.build_manager.BUILD_DIR", build_dir)
    monkeypatch.setattr(progress_tracker, "load_profession", lambda p: mock_profession_data())

    session = {"current_build": "basic", "skills_completed": ["bar"]}
    monkeypatch.setattr(session_tracker, "load_session", lambda: session)

    called = {}

    def fake_save(data):
        called["saved"] = True

    monkeypatch.setattr(session_tracker, "save_session", fake_save)

    bm = BuildManager()
    bm.load_build("basic")

    assert "saved" not in called


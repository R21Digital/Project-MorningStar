import json
import os
import sys
from pathlib import Path
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.profile_loader as profile_loader
from core.profile_loader import load_profile, validate_profile, ProfileValidationError

# Directory for persistent test artifacts
ARTIFACTS_DIR = Path("tests/artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)


def _patch_runtime(monkeypatch, path):
    monkeypatch.setattr("core.profile_loader.RUNTIME_PROFILE", path / "profile.runtime.json")
    monkeypatch.setattr("core.profile_loader.load_session", lambda: {"loops": 1})


def test_load_profile_valid(tmp_path, monkeypatch):
    data = {
        "support_target": "Leader",
        "preferred_trainers": {"medic": "trainer"},
        "default_mode": "medic",
        "skip_modes": ["crafting"],
        "farming_targets": ["Bandit"],
        "farming_target": {
            "planet": "Naboo",
            "city": "Theed",
            "hotspot": "Cantina",
        },
        "skill_build": "basic",
        "auto_train": True,
        "mode_sequence": ["medic", "quest"],
        "fatigue_threshold": 5,
    }
    path = tmp_path / "demo.json"
    path.write_text(json.dumps(data))
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    (build_dir / "basic.json").write_text(json.dumps({"skills": []}))
    progress_file = ARTIFACTS_DIR / "session_state.json"
    if progress_file.exists():
        progress_file.unlink()
    progress_file.write_text(json.dumps({"completed_skills": []}))
    monkeypatch.setattr("core.profile_loader.PROFILE_DIR", tmp_path)
    monkeypatch.setattr("core.profile_loader.BUILD_DIR", build_dir)
    monkeypatch.setattr("core.profile_loader.SESSION_STATE", progress_file)
    _patch_runtime(monkeypatch, tmp_path)
    prof = load_profile("demo")
    assert prof["build"] == {"skills": []}
    assert prof["build_progress"] == {"completed_skills": [], "total_skills": 0}
    assert prof["recovery_path"] == str(progress_file)
    assert prof["runtime"] == {"progress": {"loops": 1}}
    saved = json.loads((tmp_path / "profile.runtime.json").read_text())
    assert saved["runtime"] == {"progress": {"loops": 1}}


def test_load_profile_txt_build(tmp_path, monkeypatch):
    data = {
        "support_target": "Leader",
        "preferred_trainers": {"medic": "trainer"},
        "default_mode": "medic",
        "skip_modes": ["crafting"],
        "farming_targets": ["Bandit"],
        "farming_target": {
            "planet": "Naboo",
            "city": "Theed",
            "hotspot": "Cantina",
        },
        "skill_build": "basic",
    }
    path = tmp_path / "demo.json"
    path.write_text(json.dumps(data))
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    (build_dir / "basic.txt").write_text(json.dumps({"skills": ["A"]}))
    progress_file = ARTIFACTS_DIR / "session_state.json"
    if progress_file.exists():
        progress_file.unlink()
    progress_file.write_text(json.dumps({"completed_skills": ["A"]}))
    monkeypatch.setattr("core.profile_loader.PROFILE_DIR", tmp_path)
    monkeypatch.setattr("core.profile_loader.BUILD_DIR", build_dir)
    monkeypatch.setattr("core.profile_loader.SESSION_STATE", progress_file)
    _patch_runtime(monkeypatch, tmp_path)
    prof = load_profile("demo")
    assert prof["build"] == {"skills": ["A"]}
    assert prof["build_progress"] == {
        "completed_skills": ["A"],
        "total_skills": 1,
    }
    assert prof["recovery_path"] == str(progress_file)
    assert prof["runtime"] == {"progress": {"loops": 1}}


def test_auto_train_default(tmp_path, monkeypatch):
    data = {
        "support_target": "Leader",
        "preferred_trainers": {"medic": "trainer"},
        "default_mode": "medic",
        "skip_modes": ["crafting"],
        "farming_targets": ["Bandit"],
        "farming_target": {
            "planet": "Naboo",
            "city": "Theed",
            "hotspot": "Cantina",
        },
        "skill_build": "basic",
    }
    path = tmp_path / "demo.json"
    path.write_text(json.dumps(data))
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    (build_dir / "basic.json").write_text(json.dumps({"skills": []}))
    monkeypatch.setattr("core.profile_loader.PROFILE_DIR", tmp_path)
    monkeypatch.setattr("core.profile_loader.BUILD_DIR", build_dir)
    _patch_runtime(monkeypatch, tmp_path)
    prof = load_profile("demo")
    assert prof["auto_train"] is False


def test_invalid_farming_target(tmp_path, monkeypatch):
    data = {
        "support_target": "Leader",
        "preferred_trainers": {"medic": "trainer"},
        "default_mode": "medic",
        "skip_modes": ["crafting"],
        "farming_targets": ["Bandit"],
        "farming_target": {
            "planet": "Naboo",
            "city": "Theed",
        },
        "skill_build": "basic",
    }
    path = tmp_path / "demo.json"
    path.write_text(json.dumps(data))
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    (build_dir / "basic.json").write_text(json.dumps({"skills": []}))
    monkeypatch.setattr("core.profile_loader.PROFILE_DIR", tmp_path)
    monkeypatch.setattr("core.profile_loader.BUILD_DIR", build_dir)
    _patch_runtime(monkeypatch, tmp_path)
    with pytest.raises(ProfileValidationError):
        load_profile("demo")


def test_load_profile_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("core.profile_loader.PROFILE_DIR", tmp_path)
    prof = load_profile("missing")
    assert prof == {}


def test_missing_build_file(tmp_path, monkeypatch):
    data = {
        "support_target": "Leader",
        "preferred_trainers": {"medic": "trainer"},
        "default_mode": "medic",
        "skip_modes": ["crafting"],
        "farming_targets": ["Bandit"],
        "farming_target": {
            "planet": "Naboo",
            "city": "Theed",
            "hotspot": "Cantina",
        },
        "skill_build": "missing",
    }
    path = tmp_path / "demo.json"
    path.write_text(json.dumps(data))
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    monkeypatch.setattr("core.profile_loader.PROFILE_DIR", tmp_path)
    monkeypatch.setattr("core.profile_loader.BUILD_DIR", build_dir)
    _patch_runtime(monkeypatch, tmp_path)
    with pytest.raises(ProfileValidationError):
        load_profile("demo")


def test_invalid_build_structure(tmp_path, monkeypatch):
    data = {
        "support_target": "Leader",
        "preferred_trainers": {"medic": "trainer"},
        "default_mode": "medic",
        "skip_modes": ["crafting"],
        "farming_targets": ["Bandit"],
        "farming_target": {
            "planet": "Naboo",
            "city": "Theed",
            "hotspot": "Cantina",
        },
        "skill_build": "bad",
    }
    path = tmp_path / "demo.json"
    path.write_text(json.dumps(data))
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    (build_dir / "bad.json").write_text("[]")
    monkeypatch.setattr("core.profile_loader.PROFILE_DIR", tmp_path)
    monkeypatch.setattr("core.profile_loader.BUILD_DIR", build_dir)
    _patch_runtime(monkeypatch, tmp_path)
    with pytest.raises(ProfileValidationError):
        load_profile("demo")



def test_validate_profile_missing_fields(tmp_path, monkeypatch):
    data = {
        "support_target": "Leader",
        "preferred_trainers": {"medic": "trainer"},
        "default_mode": "medic",
        "skip_modes": ["crafting"],
        "farming_targets": ["Bandit"],
        "skill_build": "basic",
    }
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    (build_dir / "basic.json").write_text(json.dumps({"skills": []}))
    monkeypatch.setattr("core.profile_loader.BUILD_DIR", build_dir)

    data_missing = data.copy()
    data_missing.pop("default_mode")

    with pytest.raises(ProfileValidationError):
        validate_profile(data_missing)


def test_validate_profile_missing_skill_build(tmp_path, monkeypatch):
    data = {
        "support_target": "Leader",
        "preferred_trainers": {"medic": "trainer"},
        "default_mode": "medic",
        "skip_modes": ["crafting"],
        "farming_targets": ["Bandit"],
    }
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    monkeypatch.setattr("core.profile_loader.BUILD_DIR", build_dir)

    with pytest.raises(ProfileValidationError) as excinfo:
        validate_profile(data)
    assert "skill_build" in str(excinfo.value)


def test_validate_profile_invalid_auto_train_type(tmp_path, monkeypatch):
    data = {
        "support_target": "Leader",
        "preferred_trainers": {"medic": "trainer"},
        "default_mode": "medic",
        "skip_modes": ["crafting"],
        "farming_targets": ["Bandit"],
        "skill_build": "basic",
        "auto_train": "yes",
    }
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    (build_dir / "basic.json").write_text(json.dumps({"skills": []}))
    monkeypatch.setattr("core.profile_loader.BUILD_DIR", build_dir)

    with pytest.raises(ProfileValidationError) as excinfo:
        validate_profile(data)
    assert "auto_train" in str(excinfo.value)


def test_validate_profile_invalid_fatigue_threshold(tmp_path, monkeypatch):
    data = {
        "support_target": "Leader",
        "preferred_trainers": {"medic": "trainer"},
        "default_mode": "medic",
        "skip_modes": ["crafting"],
        "farming_targets": ["Bandit"],
        "skill_build": "basic",
        "fatigue_threshold": "high",
    }
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    (build_dir / "basic.json").write_text(json.dumps({"skills": []}))
    monkeypatch.setattr("core.profile_loader.BUILD_DIR", build_dir)

    with pytest.raises(ProfileValidationError) as excinfo:
        validate_profile(data)
    assert "fatigue_threshold" in str(excinfo.value)


def test_load_profile_from_repo_txt(tmp_path, monkeypatch):
    data = {
        "support_target": "Leader",
        "preferred_trainers": {"medic": "trainer"},
        "default_mode": "medic",
        "skip_modes": ["crafting"],
        "farming_targets": ["Bandit"],
        "farming_target": {
            "planet": "Naboo",
            "city": "Theed",
            "hotspot": "Cantina",
        },
        "skill_build": "basic",
    }
    path = tmp_path / "demo.json"
    path.write_text(json.dumps(data))

    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    src_path = profile_loader.BUILD_DIR / "basic.txt"
    build_dir.joinpath("basic.txt").write_text(src_path.read_text())

    monkeypatch.setattr("core.profile_loader.PROFILE_DIR", tmp_path)
    monkeypatch.setattr("core.profile_loader.BUILD_DIR", build_dir)

    _patch_runtime(monkeypatch, tmp_path)

    progress_file = ARTIFACTS_DIR / "session_state.json"
    if progress_file.exists():
        progress_file.unlink()
    progress_file.write_text(json.dumps({"completed_skills": []}))
    monkeypatch.setattr("core.profile_loader.SESSION_STATE", progress_file)

    prof = load_profile("demo")
    assert prof["build"] == json.loads(src_path.read_text())
    assert "build_progress" in prof
    assert prof["runtime"] == {"progress": {"loops": 1}}

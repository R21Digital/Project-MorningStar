import json
from pathlib import Path
import pytest

pytest.importorskip("flask")


from dashboard.app import app

# Directory for persistent test artifacts
ARTIFACTS_DIR = Path("tests/artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)


def test_builds_route(monkeypatch, tmp_path):
    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    (build_dir / "foo.json").write_text("{}")
    (build_dir / "bar.txt").write_text("{}")
    monkeypatch.setattr("dashboard.app.BUILD_DIR", build_dir)

    with app.test_client() as client:
        resp = client.get("/builds")
        assert resp.status_code == 200
        assert b"foo" in resp.data
        assert b"bar" in resp.data


def test_status_route(monkeypatch, tmp_path):
    log_file = tmp_path / "session_test.json"
    log_file.write_text(json.dumps({"hello": "world"}))
    monkeypatch.setattr("dashboard.app.LOG_DIRS", [tmp_path])

    with app.test_client() as client:
        resp = client.get("/status")
        assert resp.status_code == 200
        assert b"hello" in resp.data


def test_status_progress_fields(monkeypatch, tmp_path):
    log_file = tmp_path / "session_test.json"
    log_file.write_text(json.dumps({}))
    monkeypatch.setattr("dashboard.app.LOG_DIRS", [tmp_path])

    progress_file = ARTIFACTS_DIR / "runtime" / "session_state.json"
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    if progress_file.exists():
        progress_file.unlink()
    progress_file.write_text(json.dumps({"completed_skills": ["A"]}))
    monkeypatch.setattr("dashboard.app.SESSION_STATE", progress_file)

    build_dir = tmp_path / "builds"
    build_dir.mkdir()
    (build_dir / "demo.json").write_text(json.dumps({"profession": "Demo", "skills": ["A", "B"]}))
    monkeypatch.setattr("dashboard.app.BUILD_DIR", build_dir)

    monkeypatch.setattr("dashboard.app.session_state", {"profile": {"skill_build": "demo"}})

    with app.test_client() as client:
        resp = client.get("/status")
        assert resp.status_code == 200
        body = resp.data.decode()
        assert "Completed Skills" in body
        assert "A" in body
        assert "Next Skill" in body
        assert "B" in body
        assert "Progress" in body

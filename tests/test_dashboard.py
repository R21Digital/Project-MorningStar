import os
import sys
import json
import pytest

pytest.importorskip("flask")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dashboard.app import app


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

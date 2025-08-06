import json
from pathlib import Path


from core import progress_tracker


def test_start_without_session_file(tmp_path):
    path = tmp_path / "progress.json"
    assert not path.exists()
    data = progress_tracker.load_session(path)
    assert data == {"completed_skills": []}


def test_save_progress_on_training(tmp_path):
    path = tmp_path / "progress.json"
    progress_tracker.record_skill(path, "Novice")
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["completed_skills"] == ["Novice"]


def test_reload_after_restart(tmp_path):
    path = tmp_path / "progress.json"
    progress_tracker.record_skill(path, "Novice")
    progress_tracker.record_skill(path, "Intermediate")

    new_path = Path(str(path))
    loaded = progress_tracker.load_session(new_path)
    assert loaded["completed_skills"] == ["Novice", "Intermediate"]

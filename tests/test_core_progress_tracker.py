import os
import sys
import json


from core import progress_tracker


def test_load_empty_session(tmp_path):
    path = tmp_path / "progress.json"
    data = progress_tracker.load_session(path)
    assert data == {"completed_skills": []}


def test_resume_progress(tmp_path):
    path = tmp_path / "progress.json"
    progress_tracker.save_session(path, {"completed_skills": ["Skill1"]})
    loaded = progress_tracker.load_session(path)
    assert loaded["completed_skills"] == ["Skill1"]


def test_record_skill_saves(tmp_path):
    path = tmp_path / "progress.json"
    progress_tracker.record_skill(path, "SkillA")
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["completed_skills"] == ["SkillA"]


def test_resume_after_restart(tmp_path):
    path = tmp_path / "progress.json"
    progress_tracker.record_skill(path, "SkillA")
    progress_tracker.record_skill(path, "SkillB")
    loaded = progress_tracker.load_session(path)
    assert loaded["completed_skills"] == ["SkillA", "SkillB"]

import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.professions import progress_tracker


def setup_profession(tmp_path):
    data = {
        "prerequisites": ["Novice Artisan"],
        "skill_boxes": [
            "Novice Medic",
            "Intermediate Medicine (1,000 Medicine XP)",
            "Master Doctor (10,000 Medicine XP)",
        ],
        "xp_costs": {
            "Novice Medic": 0,
            "Intermediate Medicine": 1000,
            "Master Doctor": 10000,
        },
    }
    prof_dir = tmp_path
    prof_dir.mkdir(exist_ok=True)
    with open(prof_dir / "medic.json", "w", encoding="utf-8") as fh:
        json.dump(data, fh)
    return prof_dir


def test_recommend_next_skill(monkeypatch, tmp_path):
    prof_dir = setup_profession(tmp_path)
    monkeypatch.setattr(progress_tracker, "DATA_DIR", str(prof_dir))

    rec = progress_tracker.recommend_next_skill("medic", [])
    assert rec == {"skill": "Novice Artisan", "xp": 0}

    rec = progress_tracker.recommend_next_skill("medic", ["Novice Artisan"])
    assert rec == {"skill": "Novice Medic", "xp": 0}

    rec = progress_tracker.recommend_next_skill(
        "medic", ["Novice Artisan", "Novice Medic"]
    )
    assert rec == {"skill": "Intermediate Medicine", "xp": 1000}

    rec = progress_tracker.recommend_next_skill(
        "medic", ["Novice Artisan", "Novice Medic", "Intermediate Medicine"]
    )
    assert rec == {"skill": "Master Doctor", "xp": 10000}

    rec = progress_tracker.recommend_next_skill(
        "medic",
        [
            "Novice Artisan",
            "Novice Medic",
            "Intermediate Medicine",
            "Master Doctor",
        ],
    )
    assert rec is None


def test_estimate_hours_to_next_skill(monkeypatch, tmp_path):
    prof_dir = setup_profession(tmp_path)
    monkeypatch.setattr(progress_tracker, "DATA_DIR", str(prof_dir))
    monkeypatch.setattr(progress_tracker.xp_estimator, "estimate_xp_per_hour", lambda p, a: 500)

    hours = progress_tracker.estimate_hours_to_next_skill(
        "medic", ["Novice Artisan", "Novice Medic"], "healing"
    )
    assert hours == 1000 / 500

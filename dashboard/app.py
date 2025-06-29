from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from flask import Flask, render_template
from core.session_tracker import load_session

from core import progress_tracker
from core.build_manager import BuildManager
from core.profile_loader import SESSION_STATE

# Runtime session data placeholder
session_state: dict = {}

# Directory containing build definitions
BUILD_DIR = Path(__file__).resolve().parents[1] / "profiles" / "builds"

# Potential locations for session logs
LOG_DIRS = [Path("logs"), Path("data") / "session_logs"]

app = Flask(__name__)


def _latest_session_log() -> Optional[Path]:
    """Return the most recently modified session log file if one exists."""
    candidates = []
    for directory in LOG_DIRS:
        if directory.exists():
            candidates.extend(directory.glob("session_*.json"))
            # include plain JSON names from session_logger
            candidates.extend(directory.glob("*.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _get_progress(build_name: str | None) -> dict:
    """Return progress details for ``build_name`` using the tracker."""
    progress_data = progress_tracker.load_session(SESSION_STATE)
    completed = progress_data.get("completed_skills", [])

    info = {"completed_skills": completed, "next_skill": None, "percent": 0}

    if not build_name:
        return info

    try:
        bm = BuildManager(build_name)
    except Exception:
        return info

    total = len(bm.skills)
    done = bm.get_completed_skills()
    next_skill = bm.get_next_skill(done)

    percent = (len(done) / total * 100) if total else 0

    info.update(
        {
            "completed_skills": done,
            "next_skill": next_skill,
            "percent": round(percent, 2),
            "total_skills": total,
        }
    )
    return info


@app.route("/")
def index():
    """Display basic session details."""
    session = load_session()
    build = session.get("current_build", "Unknown")
    progress = len(session.get("skills_completed", []))
    return render_template("index.html", build=build, progress=progress)


@app.route("/builds")
def list_builds():
    builds = []
    if BUILD_DIR.exists():
        builds.extend(p.stem for p in BUILD_DIR.glob("*.json"))
        builds.extend(p.stem for p in BUILD_DIR.glob("*.txt"))
    return render_template("builds.html", builds=sorted(set(builds)))


@app.route("/status")
def status():
    log_path = _latest_session_log()
    data = None
    if log_path and log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            data = None
    profile = session_state.get("profile", {})
    build_name = profile.get("skill_build")
    progress = _get_progress(build_name)
    return render_template(
        "status.html", log=data, build=build_name, progress=progress
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)

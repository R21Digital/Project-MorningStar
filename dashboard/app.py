from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from flask import Flask, render_template

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


@app.route("/")
def index():
    return render_template("index.html")


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
    return render_template("status.html", log=data)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)

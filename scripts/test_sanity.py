#!/usr/bin/env python3
"""Run a minimal pytest sanity test with safe PYTHONPATH and rootdir.

This avoids picking up archived backups on Windows and ensures imports resolve
via the repository's `src/` and `ai/` directories.
"""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    src = str(repo_root / "src")
    ai = str(repo_root / "ai")

    # Prepend to PYTHONPATH
    current = os.environ.get("PYTHONPATH", "")
    sep = ";" if os.name == "nt" else ":"
    os.environ["PYTHONPATH"] = sep.join([src, ai, str(repo_root), current]) if current else sep.join([src, ai, str(repo_root)])

    # Run pytest with tests rootdir to avoid conflicts
    cmd = [sys.executable, "-m", "pytest", "--rootdir=tests", "-q", "--tb=short", "tests/test_ci_sanity.py"]
    print("Running:", " ".join(cmd))
    try:
        return subprocess.call(cmd, cwd=str(repo_root))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())



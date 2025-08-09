"""Repository-level pytest configuration and path hygiene.

Ensures that any archived backup copies of the repository (e.g. under
``archive/backups``) are not imported as the active ``tests`` package, which can
cause ImportPathMismatch errors on Windows when multiple ``tests`` packages are
discoverable on ``sys.path``.
"""

from __future__ import annotations

import os
import sys
from typing import Any


def _is_archived_path(path: str) -> bool:
    norm = os.path.normpath(path).lower()
    return os.path.sep + "archive" + os.path.sep in norm


def pytest_sessionstart(session: Any) -> None:  # pragma: no cover - environment setup
    try:
        repo_root = os.path.dirname(__file__)
        tests_root = os.path.join(repo_root, "tests")

        # Ensure our real tests directory is first
        if tests_root not in sys.path:
            sys.path.insert(0, tests_root)

        # If a different "tests" package was imported from an archived backup,
        # remove it so pytest will import the one from this repo instead.
        imported_tests = sys.modules.get("tests")
        imported_conftest = sys.modules.get("tests.conftest")

        def path_of(mod: Any) -> str:
            return getattr(mod, "__file__", "") or ""

        if imported_tests and _is_archived_path(path_of(imported_tests)):
            del sys.modules["tests"]
        if imported_conftest and _is_archived_path(path_of(imported_conftest)):
            del sys.modules["tests.conftest"]
    except Exception:
        # Never fail test startup due to hygiene
        pass



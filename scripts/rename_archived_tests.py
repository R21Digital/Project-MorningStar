"""Rename archived `tests` folders under `archive/**` to `_tests` to avoid
pytest ImportPathMismatch on Windows when multiple `tests` packages exist.

Usage:
    python scripts/rename_archived_tests.py            # perform rename
    python scripts/rename_archived_tests.py --dry-run  # show what would change
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def find_tests_directories(root: Path) -> list[Path]:
    # Use rglob for reliability on Windows; filter to directories only
    return [p for p in root.rglob("tests") if p.is_dir()]


def rename_to_underscore_tests(path: Path, dry_run: bool = False) -> bool:
    target = path.with_name("_tests")
    if target.exists():
        print(f"[skip] {path} -> {target} (target exists)")
        return False
    if dry_run:
        print(f"[dry-run] rename {path} -> {target}")
        return True
    try:
        path.rename(target)
        print(f"[ok] renamed {path} -> {target}")
        return True
    except Exception as exc:  # pragma: no cover - environmental
        print(f"[error] failed to rename {path}: {exc}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Do not rename, only print actions")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    archive_root = repo_root / "archive"
    if not archive_root.exists():
        print("[info] no archive directory found; nothing to do")
        return 0

    tests_dirs = find_tests_directories(archive_root)
    if not tests_dirs:
        print("[info] no archived tests directories found; nothing to do")
        return 0

    changed = 0
    for tests_dir in tests_dirs:
        if rename_to_underscore_tests(tests_dir, dry_run=args.dry_run):
            changed += 1

    print(f"[summary] {'would rename' if args.dry_run else 'renamed'} {changed} dirs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



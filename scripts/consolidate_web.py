#!/usr/bin/env python3
"""Consolidate Eleventy web app into apps/web/.

Moves web-only files from the repository root and `src/` into `apps/web/` so
that Python source under `src/` is no longer mixed with static site sources.

Idempotent: running multiple times will skip items already moved.

Usage:
  python scripts/consolidate_web.py --dry-run
  python scripts/consolidate_web.py
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from typing import Iterable, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = REPO_ROOT / "apps" / "web"
WEB_SRC = WEB_ROOT / "src"


ROOT_ITEMS: Tuple[str, ...] = (".eleventy.js", ".eleventyignore", "public")
SRC_DIRS: Tuple[str, ...] = (
    "_includes",
    "_data",
    "guides",
    "heroics",
    "loot",
    "pages",
    "lib",
    "styles",
    "templates",
    "utils",
)
SRC_FILES: Tuple[str, ...] = ("index.11ty.js", "index.md", "guides.11ty.js", "heroics.11ty.js")


def ensure_dirs(*paths: Path) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def move_item(src: Path, dst: Path, dry_run: bool) -> None:
    if not src.exists():
        return
    if dst.exists():
        return
    print(f"MOVE {src.relative_to(REPO_ROOT)} -> {dst.relative_to(REPO_ROOT)}")
    if not dry_run:
        ensure_dirs(dst.parent)
        shutil.move(str(src), str(dst))


def consolidate(dry_run: bool) -> None:
    ensure_dirs(WEB_SRC)

    # Root-level items
    for name in ROOT_ITEMS:
        move_item(REPO_ROOT / name, WEB_ROOT / name, dry_run)

    # src directories
    for name in SRC_DIRS:
        move_item(REPO_ROOT / "src" / name, WEB_SRC / name, dry_run)

    # src files
    for name in SRC_FILES:
        move_item(REPO_ROOT / "src" / name, WEB_SRC / name, dry_run)

    # Special case: src/data/loot -> apps/web/src/data/loot
    src_loot = REPO_ROOT / "src" / "data" / "loot"
    if src_loot.exists():
        move_item(src_loot, WEB_SRC / "data" / "loot", dry_run)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="print planned moves only")
    args = parser.parse_args()

    consolidate(dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



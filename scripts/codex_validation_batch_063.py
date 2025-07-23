"""Batch 063 validation script."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent


def check_exists(path: str) -> bool:
    p = ROOT / path
    if p.exists():
        print(f"[OK] {path}")
        return True
    print(f"[MISSING] {path}")
    return False


def check_contains(path: str, text: str) -> bool:
    file_path = ROOT / path
    if not file_path.exists():
        print(f"[MISSING FILE] {path}")
        return False
    if text in file_path.read_text():
        print(f"[OK] {text}")
        return True
    print(f"[MISSING] {text}")
    return False


def check_not_contains(path: str, text: str) -> bool:
    file_path = ROOT / path
    if not file_path.exists():
        print(f"[MISSING FILE] {path}")
        return False
    if text not in file_path.read_text():
        print(f"[OK] no '{text}'")
        return True
    print(f"[FOUND UNEXPECTED] {text}")
    return False


def main() -> None:
    required_files = [
        "README.md",
        "docs/batch_summary.md",
        "scripts/codex_validation_batch_063.py",
    ]

    missing = [f for f in required_files if not check_exists(f)]

    print("\nChecking README for configuration variables:\n")
    if not check_contains("README.md", "BOT_INSTANCE_NAME"):
        missing.append("README BOT_INSTANCE_NAME")
    if not check_contains("README.md", "LOG_LEVEL"):
        missing.append("README LOG_LEVEL")
    if not check_not_contains("README.md", "warnings.log"):
        missing.append("README warnings.log")

    print("\nChecking batch summary for entry:\n")
    if not check_contains("docs/batch_summary.md", "Batch 063"):
        missing.append("batch summary entry")

    if missing:
        print(f"[BATCH 063] \u274c Issues found: {missing}")
        sys.exit(1)

    print("[BATCH 063] \u2705 All files validated.")


if __name__ == "__main__":
    main()


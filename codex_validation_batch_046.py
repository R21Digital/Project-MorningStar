from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).parent


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


def main() -> None:
    required_files = [
        "core/dashboard_utils.py",
        "core/unified_dashboard.py",
        "core/legacy_dashboard.py",
        "docs/batch_summary.md",
        "README.md",
        "Makefile",
        "main.py",
    ]

    test_files = [
        "tests/test_dashboard_filters.py",
        "tests/test_unified_dashboard.py",
        "tests/test_legacy_dashboard.py",
    ]

    cli_flags = ["--filter-status"]

    summary_phrases = ["summary counts", "Dashboard Utils"]

    print("Validating required files:\n")
    missing_files = [f for f in required_files if not check_exists(f)]

    print("\nChecking CLI flags in main.py:\n")
    missing_flags = [flag for flag in cli_flags if not check_contains("main.py", flag)]

    print("\nChecking test files:\n")
    missing_tests = [t for t in test_files if not check_exists(t)]

    print("\nChecking README for summary lines:\n")
    missing_phrases = [p for p in summary_phrases if not check_contains("README.md", p)]

    total_missing = len(missing_files) + len(missing_flags) + len(missing_tests) + len(missing_phrases)

    print("\nValidation summary:")
    print(f"  Missing files: {len(missing_files)}")
    print(f"  Missing CLI flags: {len(missing_flags)}")
    print(f"  Missing tests: {len(missing_tests)}")
    print(f"  Missing README phrases: {len(missing_phrases)}")

    if total_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()

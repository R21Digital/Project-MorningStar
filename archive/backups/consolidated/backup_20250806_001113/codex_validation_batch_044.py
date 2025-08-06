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
        "core/constants.py",
        "core/quest_state.py",
        "core/unified_dashboard.py",
        "core/legacy_dashboard.py",
        "core/themepark_dashboard.py",
        "core/themepark_tracker.py",
        "core/execution/fallbacks.py",
        "docs/batch_summary.md",
        "Makefile",
        "main.py",
    ]

    test_files = [
        "tests/test_constants.py",
        "tests/test_quest_state.py",
        "tests/test_unified_dashboard.py",
        "tests/test_legacy_dashboard.py",
        "tests/test_themepark_tracker.py",
        "tests/rich_stub.py",
        "tests/test_main_legacy_cli.py",
    ]

    cli_flags = [
        "--legacy",
        "--show-legacy-status",
        "--show-themepark-status",
        "--show-dashboard",
        "--dashboard-mode",
        "--summary",
        "--detailed",
        "--filter-status",
    ]

    dashboard_funcs = [
        "display_legacy_progress",
        "display_themepark_progress",
        "show_unified_dashboard",
    ]

    print("Validating required files:\n")
    missing_files = [f for f in required_files if not check_exists(f)]

    print("\nChecking CLI flags in main.py:\n")
    missing_flags = [flag for flag in cli_flags if not check_contains("main.py", flag)]

    print("\nChecking dashboard functions in main.py:\n")
    missing_funcs = [func for func in dashboard_funcs if not check_contains("main.py", func)]

    print("\nChecking test files:\n")
    missing_tests = [t for t in test_files if not check_exists(t)]

    total_missing = len(missing_files) + len(missing_flags) + len(missing_funcs) + len(missing_tests)

    print("\nValidation summary:")
    print(f"  Missing files: {len(missing_files)}")
    print(f"  Missing CLI flags: {len(missing_flags)}")
    print(f"  Missing dashboard calls: {len(missing_funcs)}")
    print(f"  Missing tests: {len(missing_tests)}")

    if total_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()

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


def main() -> None:
    required_files = [
        "core/dashboard_utils.py",
        "core/unified_dashboard.py",
        "docs/batch_summary.md",
        "tests/test_dashboard_utils.py",
    ]

    functions = [
        "group_steps_by_category",
        "summarize_status_counts",
        "calculate_completion_percentage",
    ]

    print("Validating required files:\n")
    missing_files = [f for f in required_files if not check_exists(f)]

    print("\nChecking dashboard utils for functions:\n")
    missing_defs = [f for f in functions if not check_contains("core/dashboard_utils.py", f)]

    print("\nChecking unified dashboard usage:\n")
    missing_usage = [f for f in functions if not check_contains("core/unified_dashboard.py", f)]

    print("\nChecking batch summary for entry:\n")
    summary_missing = 0 if check_contains("docs/batch_summary.md", "Batch 048") else 1

    total_missing = len(missing_files) + len(missing_defs) + len(missing_usage) + summary_missing

    print("\nValidation summary:")
    print(f"  Missing files: {len(missing_files)}")
    print(f"  Missing definitions: {len(missing_defs)}")
    print(f"  Missing usage: {len(missing_usage)}")
    print(f"  Missing summary entry: {summary_missing}")

    if total_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()

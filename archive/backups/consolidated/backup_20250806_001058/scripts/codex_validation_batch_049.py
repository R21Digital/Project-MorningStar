from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent


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


def check_exists(path: str) -> bool:
    p = ROOT / path
    if p.exists():
        print(f"[OK] {path}")
        return True
    print(f"[MISSING] {path}")
    return False


def main() -> None:
    required_files = [
        "utils/logger.py",
        "core/unified_dashboard.py",
        "docs/batch_summary.md",
        "tests/test_logger_usage.py",
        "Makefile",
    ]

    print("Validating required files:\n")
    missing_files = [f for f in required_files if not check_exists(f)]

    print("\nChecking logger for new function:\n")
    func_missing = 0 if check_contains("utils/logger.py", "def log_info") else 1
    path_missing = 0 if check_contains("utils/logger.py", "dashboard_usage.log") else 1

    print("\nChecking dashboard logging usage:\n")
    usage_missing = 0 if check_contains("core/unified_dashboard.py", "log_info(") else 1

    print("\nChecking batch summary for entry:\n")
    summary_missing = 0 if check_contains("docs/batch_summary.md", "Batch 049") else 1

    total_missing = len(missing_files) + func_missing + path_missing + usage_missing + summary_missing

    print("\nValidation summary:")
    print(f"  Missing files: {len(missing_files)}")
    print(f"  Missing function: {func_missing}")
    print(f"  Missing path string: {path_missing}")
    print(f"  Missing usage: {usage_missing}")
    print(f"  Missing summary entry: {summary_missing}")

    if total_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()

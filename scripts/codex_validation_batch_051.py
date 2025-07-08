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
        "core/constants.py",
        "core/quest_state.py",
        "core/unified_dashboard.py",
        "core/legacy_dashboard.py",
        "core/themepark_dashboard.py",
        "core/themepark_tracker.py",
        "core/quest_loader.py",
        "src/execution/quest_executor.py",
        "core/execution/fallbacks.py",
        "tests/test_constants.py",
        "tests/test_quest_state.py",
        "tests/test_unified_dashboard.py",
        "tests/test_legacy_dashboard.py",
        "tests/test_themepark_tracker.py",
        "tests/test_quest_loader.py",
        "tests/test_quest_executor.py",
        "tests/rich_stub.py",
        "docs/batch_summary.md",
        "Makefile",
    ]

    print("Validating required files:\n")
    missing_files = [f for f in required_files if not check_exists(f)]

    print("\nChecking quest executor for loader usage:\n")
    loader_missing = 0 if check_contains("src/execution/quest_executor.py", "load_quest_steps") else 1
    logger_missing = 0 if check_contains("src/execution/quest_executor.py", "log_info") else 1

    print("\nChecking Makefile target:\n")
    target_missing = 0 if check_contains("Makefile", "validate-batch-051") else 1

    print("\nChecking batch summary for entry:\n")
    summary_missing = 0 if check_contains("docs/batch_summary.md", "Batch 051") else 1

    total_missing = len(missing_files) + loader_missing + logger_missing + target_missing + summary_missing

    print("\nValidation summary:")
    print(f"  Missing files: {len(missing_files)}")
    print(f"  Missing loader usage: {loader_missing}")
    print(f"  Missing logger usage: {logger_missing}")
    print(f"  Missing make target: {target_missing}")
    print(f"  Missing summary entry: {summary_missing}")

    if total_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()


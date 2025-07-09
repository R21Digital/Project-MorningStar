from pathlib import Path
import sys


def check_file(path: str) -> bool:
    """Print whether a path exists and return True if it does."""
    p = Path(path)
    if p.exists():
        print(f"[OK] {path}")
        return True
    else:
        print(f"[MISSING] {path}")
        return False


def main() -> None:
    files = [
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
        "scripts/codex_validation_batch_051.py",
        "scripts/codex_validation_batch_055.py",
        "scripts/codex_validation_batch_056.py",
    ]

    print("Validating required files:\n")
    missing = [f for f in files if not check_file(f)]

    print("\nValidation complete.")
    print("Run 'make validate' to run additional validation tasks.")

    if missing:
        print(f"\nMissing {len(missing)} file(s):")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)


if __name__ == "__main__":
    main()


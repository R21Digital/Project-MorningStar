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
        "core/execution/fallbacks.py",
        "tests/test_constants.py",
        "tests/test_unified_dashboard.py",
        "tests/rich_stub.py",
        "docs/batch_summary.md",
        "Makefile",
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


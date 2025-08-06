from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "core/logging_config.py",
    "tests/test_logging_config.py",
]


def main() -> None:
    missing = [f for f in REQUIRED_FILES if not (ROOT / f).is_file()]
    if missing:
        print("[BATCH 055] \u274c Missing files:", missing)
        sys.exit(1)
    print("[BATCH 055] \u2705 All files validated.")


if __name__ == "__main__":
    main()

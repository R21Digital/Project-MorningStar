from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "profession_logic/utils/logger.py",
    "tests/test_profession_logger.py",
    "scripts/codex_validation_batch_060.py",
]


def main() -> None:
    missing = [f for f in REQUIRED_FILES if not (ROOT / f).is_file()]
    if missing:
        print("[BATCH 060] \u274c Missing files:", missing)
        sys.exit(1)
    print("[BATCH 060] \u2705 All files validated.")


if __name__ == "__main__":
    main()

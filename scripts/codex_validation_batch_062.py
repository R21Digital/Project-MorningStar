from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "README.md",
    "docs/batch_summary.md",
    "scripts/codex_validation_batch_062.py",
]


def main() -> None:
    missing = [f for f in REQUIRED_FILES if not (ROOT / f).is_file()]
    if missing:
        print("[BATCH 062] \u274c Missing files:", missing)
        sys.exit(1)
    print("[BATCH 062] \u2705 All files validated.")


if __name__ == "__main__":
    main()

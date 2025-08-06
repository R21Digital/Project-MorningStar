from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "profession_logic/utils/logger.py",
    "tests/test_logger.py",
]

def main():
    missing = [f for f in REQUIRED_FILES if not (ROOT / f).is_file()]
    if missing:
        print("[BATCH 052] ❌ Missing files:", missing)
        sys.exit(1)
    print("[BATCH 052] ✅ All files validated.")
    sys.exit(0)

if __name__ == "__main__":
    main()

import os
import sys

REQUIRED_FILES = [
    "utils/logger.py",
    "tests/test_logger.py",
    "tests/test_utils_logger.py",
]

def main():
    missing = [f for f in REQUIRED_FILES if not os.path.exists(f)]
    if missing:
        print("[BATCH 052] ❌ Missing files:", missing)
        sys.exit(1)
    print("[BATCH 052] ✅ All files validated.")

if __name__ == "__main__":
    main()

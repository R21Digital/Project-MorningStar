from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = [
    "vision/capture_screen.py",
    "vision/ocr_engine.py",
    "vision/ocr_utils.py",
    "network/chat_listener.py",
    "tests/test_ocr_engine.py",
    "tests/test_chat_listener.py",
    "tests/test_ocr_utils.py",
]


def main() -> None:
    missing = [f for f in REQUIRED if not (ROOT / f).is_file()]
    if missing:
        print(f"[BATCH 065] \u274c Missing files: {missing}")
        sys.exit(1)
    print("[BATCH 065] \u2705 All files validated.")


if __name__ == "__main__":
    main()

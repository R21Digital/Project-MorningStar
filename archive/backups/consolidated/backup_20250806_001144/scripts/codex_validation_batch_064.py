from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent


def check_exists(path: str) -> bool:
    p = ROOT / path
    if p.is_file():
        print(f"[OK] {path}")
        return True
    print(f"[MISSING] {path}")
    return False


def check_constant(path: str, constant: str, expected: str) -> bool:
    file_path = ROOT / path
    if not file_path.is_file():
        print(f"[MISSING FILE] {path}")
        return False
    text = file_path.read_text()
    pattern = rf"^{constant}\s*=\s*{expected}\b"
    if re.search(pattern, text, re.MULTILINE):
        print(f"[OK] {constant} == {expected}")
        return True
    print(f"[MISSING] {constant} == {expected}")
    return False


def main() -> None:
    required_test = "tests/test_logging_retention.py"

    missing = []
    if not check_exists(required_test):
        missing.append(required_test)

    if not check_constant("core/logging_config.py", "MAX_LOG_FILES", "20"):
        missing.append("MAX_LOG_FILES")
    if not check_constant("core/logging_config.py", "MAX_LOG_AGE_DAYS", "14"):
        missing.append("MAX_LOG_AGE_DAYS")

    if missing:
        print(f"[BATCH 064] \u274c Issues found: {missing}")
        sys.exit(1)
    print("[BATCH 064] \u2705 All validations passed.")


if __name__ == "__main__":
    main()

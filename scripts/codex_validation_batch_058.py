import os

required_files = [
    "core/logging_config.py",
    "profession_logic/utils/logger.py",
    "tests/test_logger.py",
    "tests/test_logger_usage.py",
]


def main():
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        print("Missing:", missing)
        raise SystemExit(1)
    print("All Batch 058 files present.")


if __name__ == "__main__":
    main()

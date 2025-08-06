import argparse
import json
import os
import sys
from typing import Any

import yaml

sys.path.insert(0, os.path.abspath("."))

from src.execution.quest_executor import QuestExecutor
from profession_logic.utils.logger import logger


def load_steps(path: str) -> list[dict]:
    """Return quest steps loaded from JSON or YAML ``path``."""
    with open(path, "r", encoding="utf-8") as fh:
        if path.lower().endswith((".yaml", ".yml")):
            data: Any = yaml.safe_load(fh)
        else:
            data = json.load(fh)
    if isinstance(data, dict):
        return data.get("steps", [])
    return data if isinstance(data, list) else []


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run a quest file")
    parser.add_argument("quest_file", help="Path to quest JSON/YAML file")
    args = parser.parse_args(argv)

    steps = load_steps(args.quest_file)
    logger.info("[RUN QUEST] Loaded %d steps from %s", len(steps), args.quest_file)

    executor = QuestExecutor(args.quest_file)
    executor.steps = steps
    executor.run()


if __name__ == "__main__":
    main()

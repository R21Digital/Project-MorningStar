import argparse
import json
import os
from datetime import datetime

from src.quest_selector import select_quest

DEFAULT_LOG_PATH = os.path.join("logs", "quest_selections.log")


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quest selection utility")
    parser.add_argument("--character", required=True, help="Character name")
    parser.add_argument("--planet", help="Filter by planet")
    parser.add_argument("--type", dest="quest_type", help="Filter by quest type")
    parser.add_argument("--random", action="store_true", help="Choose randomly among options")
    parser.add_argument("--debug", action="store_true", help="Print raw quest data")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    quest = select_quest(
        args.character,
        planet=args.planet,
        quest_type=args.quest_type,
        randomize=args.random,
    )

    if quest is None:
        print("\u26A0\ufe0f No eligible quest found.")
        return None

    if args.debug:
        print(quest)
    else:
        title = quest.get("title", "Unknown")
        planet = quest.get("planet", "Unknown")
        qtype = quest.get("type", "?")
        print(f"{title} - {planet} [{qtype}]")

    os.makedirs(os.path.dirname(DEFAULT_LOG_PATH), exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(DEFAULT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - {json.dumps(quest)}\n")
    return quest


if __name__ == "__main__":
    main()

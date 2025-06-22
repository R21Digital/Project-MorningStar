import argparse
from typing import Optional

from src.quest_selector import select_quest
from src.quest_executor import execute_quest
from src.db.queries import insert_note


def main(argv: Optional[list[str]] = None) -> None:
    """CLI entry point for running a quest and recording the result."""
    parser = argparse.ArgumentParser(description="Select and execute a quest")
    parser.add_argument("--character", default="Vornax", help="Character name")
    parser.add_argument("--planet", help="Filter quests by planet")
    parser.add_argument("--type", dest="quest_type", help="Filter quests by type")
    parser.add_argument("--note", help="Extra note content")
    args = parser.parse_args(argv)

    quest = select_quest(args.character, planet=args.planet, quest_type=args.quest_type)
    if not quest:
        print("No quest found.")
        return

    execute_quest(quest)

    note_content = f"Completed quest: {quest.get('title')}"
    if args.note:
        note_content += f" - {args.note}"

    insert_note(args.character, "quest", note_content)
    print("Quest executed and result saved.")


if __name__ == "__main__":
    main()

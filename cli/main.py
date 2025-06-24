import argparse
from src.quest_selector import get_random_quest


def main(argv=None):
    parser = argparse.ArgumentParser(description="Random quest selector")
    parser.add_argument(
        "--quest-mode",
        type=str,
        required=True,
        help="Choose quest mode: legacy, ground, mustafar, themeparks, etc.",
    )
    args = parser.parse_args(argv)

    quest = get_random_quest(args.quest_mode)
    if quest:
        name = quest.get("name") or quest.get("title", "Unknown")
        description = quest.get("description") or quest.get("steps", "")
        if isinstance(description, list):
            description = description[0] if description else ""
        print(f"\n\U0001F9ED Starting Quest:\n{name} - {description}")
    else:
        print("\u26A0\ufe0f No quests found for the selected mode.")


if __name__ == "__main__":
    main()

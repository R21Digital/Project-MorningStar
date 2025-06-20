# main.py

import argparse
from src.session_manager import run_session_check
from src.credit_tracker import track_credits
from src.log_manager import start_log
from src.mode_questing import start_questing
from src.mode_medic import start_medic
from src.mode_crafting import start_crafting
from src.mode_afk_combat import start_afk_combat
from src.mode_buff_by_tell import start_buff_by_tell


def parse_args():
    parser = argparse.ArgumentParser(description="MorningStar Mode Runner")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["questing", "medic", "crafting", "afk_combat", "buff"],
        default="questing",
        help="Select the automation mode to run"
    )
    parser.add_argument(
        "--character",
        type=str,
        default="Vornax",
        help="Character name for this session"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("\U0001F6F0\uFE0F MorningStar MS11 Initialized")
    print(f"\U0001F4CC Mode: {args.mode.upper()}")

    start_log()
    run_session_check()
    track_credits()

    if args.mode == "questing":
        print("\U0001F680 Initiating Questing Mode...")
        completed_quests = start_questing(character_name=args.character)
        print(f"\U0001F4D8 Questing Session Summary: {len(completed_quests)} steps completed.")
    elif args.mode == "medic":
        start_medic(args.character)
    elif args.mode == "crafting":
        start_crafting(args.character)
    elif args.mode == "afk_combat":
        start_afk_combat(args.character)
    elif args.mode == "buff":
        start_buff_by_tell(args.character)
    else:
        print("❌ Unknown mode requested.")


if __name__ == "__main__":
    main()

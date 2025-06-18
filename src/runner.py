import argparse
from .xp_manager import XPManager
from . import __version__


def run_mode(mode: str):
    print(f"[\U0001F30C] MorningStar Runner Active: Mode = {mode}")
    xp = XPManager(character="Ezra")

    if mode == "quest":
        xp.record_action("quest_complete")
    elif mode == "grind":
        xp.record_action("mob_kill")
    elif mode == "heal":
        xp.record_action("healing_tick")
    else:
        print("[\u26A0\uFE0F] Unknown mode selected.")

    xp.end_session()


def main():
    parser = argparse.ArgumentParser(description="MorningStar Core Runner")
    parser.add_argument("--mode", type=str, default="quest", help="Choose a mode: quest, grind, heal")
    parser.add_argument("--version", action="store_true", help="Show application version and exit")
    args = parser.parse_args()

    if args.version:
        print(__version__)
        return

    run_mode(args.mode)


if __name__ == "__main__":
    main()

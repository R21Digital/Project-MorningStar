import argparse
import os
from typing import Callable, Dict

from src.xp_manager import XPManager
from src.logger_utils import read_logs, DEFAULT_LOG_PATH


def get_version_from_readme() -> str:
    """Extract the version string from the README.md file."""
    readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "README.md")
    with open(readme_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().lower().startswith("version"):
                return line.split(":", 1)[-1].strip()
    return "unknown"


# Mapping of mode name to a callable that performs the action for that mode.
# Each callable accepts an ``XPManager`` instance as its only argument.
MODE_DISPATCH: Dict[str, Callable[[XPManager], None]] = {
    "quest": lambda xp: xp.record_action("quest_complete"),
    "grind": lambda xp: xp.record_action("mob_kill"),
    "heal": lambda xp: xp.record_action("healing_tick"),
}


def run_mode(mode: str) -> None:
    """Run the specified mode."""
    print(f"[\U0001F30C] Android MS11 Runner Active: Mode = {mode}")
    if mode == "debug":
        lines = read_logs(DEFAULT_LOG_PATH, num_lines=5)
        if not lines:
            print("[\u26A0\uFE0F] No logs to display.")
        else:
            for line in lines:
                print(line)
        return

    xp = XPManager(character="Ezra")

    action = MODE_DISPATCH.get(mode)
    if action:
        action(xp)
    else:
        print("[\u26A0\uFE0F] Unknown mode selected.")

    xp.end_session()


def main():
    parser = argparse.ArgumentParser(description="Android MS11 Core Runner by Project Galactic Beholder")
    parser.add_argument("--mode", type=str, default="quest", help="Choose a mode: quest, grind, heal, debug")
    parser.add_argument("--version", action="store_true", help="Show application version and exit")
    args = parser.parse_args()

    if args.version:
        print(get_version_from_readme())
        return

    run_mode(args.mode)


if __name__ == "__main__":
    main()

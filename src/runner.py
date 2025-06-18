import argparse
import os
from src.xp_manager import XPManager
from src.logger_utils import read_logs, DEFAULT_LOG_PATH
from src.story_generator import generate_story


def get_version_from_readme() -> str:
    """Extract the version string from the README.md file."""
    readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
    with open(readme_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().lower().startswith("version"):
                return line.split(":", 1)[-1].strip()
    return "unknown"


def run_quest_mode():
    """Simulate quest completion and log XP."""
    xp = XPManager(character="Ezra")
    xp.record_action("quest_complete")
    xp.end_session()


def run_grind_mode():
    """Simulate grinding mobs for XP."""
    xp = XPManager(character="Ezra")
    xp.record_action("mob_kill")
    xp.end_session()


def run_heal_mode():
    """Simulate healing actions for XP."""
    xp = XPManager(character="Ezra")
    xp.record_action("healing_tick")
    xp.end_session()


def run_medic_mode():
    """Demo for medic mode."""
    xp = XPManager(character="Ezra")
    xp.record_action("healing_tick")
    xp.end_session()


def run_crafting_mode():
    """Demo for crafting mode."""
    print("[CRAFT] Crafting placeholder...")


def run_story_demo():
    """Generate a short demo story."""
    print(generate_story("In the beginning"))


mode_map = {
    "quest": run_quest_mode,
    "grind": run_grind_mode,
    "heal": run_heal_mode,
    "medic": run_medic_mode,
    "crafting": run_crafting_mode,
    "story": run_story_demo,
}


def run_mode(mode: str):
    """Dispatch the requested mode."""
    print(f"[\U0001F30C] MorningStar Runner Active: Mode = {mode}")
    if mode == "debug":
        lines = read_logs(DEFAULT_LOG_PATH, num_lines=5)
        if not lines:
            print("[\u26A0\uFE0F] No logs to display.")
        else:
            for line in lines:
                print(line)
        return

    handler = mode_map.get(mode)
    if handler:
        handler()
    else:
        print("[\u26A0\uFE0F] Unknown mode selected.")


def main():
    parser = argparse.ArgumentParser(description="MorningStar Core Runner")
    parser.add_argument(
        "--mode",
        type=str,
        default="quest",
        help="Choose a mode: quest, grind, heal, medic, crafting, story, debug",
    )
    parser.add_argument("--version", action="store_true", help="Show application version and exit")
    args = parser.parse_args()

    if args.version:
        print(get_version_from_readme())
        return

    run_mode(args.mode)


if __name__ == "__main__":
    main()

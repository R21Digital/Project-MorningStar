import json
from quest_engine import handle_quest_step


def load_legacy_quest():
    with open("data/quests/legacy.json", "r", encoding="utf-8") as f:
        return json.load(f)["steps"]


def run_questing_mode(character: str) -> None:
    print(f"[QUESTING] Starting Legacy Quest mode for {character}")
    steps = load_legacy_quest()

    for step in steps:
        print(f"\n[STEP {step['id']}] {step['title']}")
        success = handle_quest_step(step)
        if not success:
            print(f"[!] Failed to complete step: {step['id']}")
            break
    else:
        print("[\u2713] All Legacy steps complete.")


def start() -> None:
    """Entry point for questing mode."""
    run_questing_mode("Player")

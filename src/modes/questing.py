import json
from src.execution.quest_engine import execute_quest_step
from utils.license_hooks import requires_license


def load_legacy_quest():
    with open("data/quests/legacy.json", "r", encoding="utf-8") as f:
        return json.load(f)["steps"]


def run_questing_mode(character: str) -> None:
    print(f"[QUESTING] Starting Legacy Quest mode for {character}")
    raw_steps = load_legacy_quest()

    for raw in raw_steps:
        print(f"\n[STEP {raw['id']}] {raw['title']}")
        # movement step to coordinates
        move = {"type": "move", "data": {"coords": raw["coords"], "planet": raw["zone"]}}
        execute_quest_step(move)

        if raw["action"] == "talk":
            step = {"type": "npc", "data": {"npc_name": raw["npc"]}}
        elif raw["action"] == "kill":
            step = {
                "type": "combat",
                "data": {"target_name": raw["target"], "count": raw.get("count", 1)},
            }
        else:
            print(f"[!] Unknown legacy action: {raw['action']}")
            continue

        success = execute_quest_step(step)
        if not success:
            print(f"[!] Failed to complete step: {raw['id']}")
            break
    else:
        print("[\u2713] All Legacy steps complete.")


@requires_license
def start() -> None:
    """Entry point for questing mode."""
    run_questing_mode("Player")

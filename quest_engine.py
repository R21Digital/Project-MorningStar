from utils.movement_manager import travel_to
from utils.npc_handler import interact_with_npc
from utils.combat_handler import engage_targets


def handle_quest_step(step: dict) -> bool:
    """Route a quest step to the appropriate handler."""
    action = step.get("action")
    coords = step.get("coords", (0, 0))
    zone = step.get("zone", "Unknown")

    print(f"[ENGINE] Handling action: {action} at {coords}")
    travel_to(zone, coords)

    if action == "talk":
        return interact_with_npc(step.get("npc", "Unknown"))
    if action == "kill":
        target = step.get("target", "Unknown")
        count = step.get("count", 1)
        return engage_targets(target, count)

    print(f"[!] Unknown action type: {action}")
    return False

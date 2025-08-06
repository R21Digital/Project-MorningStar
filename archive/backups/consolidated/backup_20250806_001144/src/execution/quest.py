
def execute_quest(step: dict) -> None:
    """Handle quest-related steps."""
    quest_id = step.get("id", "Unknown Quest")
    action = step.get("action", "check").lower()
    print(f"[QUEST] {action.upper()} quest '{quest_id}'")

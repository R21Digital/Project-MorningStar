def execute_dialogue(step: dict) -> None:
    """Handle dialogue steps."""
    npc = step.get("npc", "Unknown")
    text = step.get("text", "...")
    print(f"\U0001F5E3 Talking to {npc}: {text}")

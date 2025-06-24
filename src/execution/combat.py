def execute_combat(step: dict) -> None:
    """Handle combat steps."""
    enemy = step.get("enemy", "Unknown")
    print(f"\u2694\ufe0f Engaging {enemy}")

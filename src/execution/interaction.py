def execute_interaction(step: dict) -> None:
    """Handle interaction steps."""
    target = step.get("target", "Unknown")
    print(f"\U0001F91D Interacting with {target}")

def execute_movement(step: dict) -> None:
    """Handle movement steps."""
    coords = step.get("coords")
    region = step.get("region", "Unknown")
    print(f"\U0001F4CD Moving to {coords} in {region}")

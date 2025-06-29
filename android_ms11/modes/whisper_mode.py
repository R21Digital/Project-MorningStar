from utils.license_hooks import requires_license


def start_buff_by_tell(character_name: str) -> None:
    """Simulate responding to buff requests sent via tell."""

    print(f"📨 Buff-by-Tell Mode Activated for {character_name}...")
    print("🧙 Listening for buff requests and queueing macros...")
    # Simulate test output
    print("📨 Simulation: Responded to 2 buff requests.")


@requires_license
def run(config, session=None):
    """Main entry point for this mode."""

    character = config.get("character_name", "Unknown") if config else "Unknown"
    start_buff_by_tell(character)

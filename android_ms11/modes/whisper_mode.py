from utils.license_hooks import requires_license
from core.profile_loader import assert_profile_ready


def start_buff_by_tell(character_name: str) -> None:
    """Simulate responding to buff requests sent via tell."""

    print(f"📨 Buff-by-Tell Mode Activated for {character_name}...")
    print("🧙 Listening for buff requests and queueing macros...")
    # Simulate test output
    print("📨 Simulation: Responded to 2 buff requests.")


@requires_license
def run(config, session=None):
    """Main entry point for this mode."""

    assert_profile_ready(getattr(session, "profile", None))

    character = config.get("character_name", "Unknown") if config else "Unknown"
    start_buff_by_tell(character)

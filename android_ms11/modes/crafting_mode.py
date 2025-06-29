from utils.license_hooks import requires_license
from core.profile_loader import assert_profile_ready


def start_crafting(character_name: str) -> None:
    """Simulate a short crafting session for the given character."""

    print(f"🛠️ Crafting Mode Activated for {character_name}...")
    print("🔧 Surveying resources and executing crafting macros...")
    # Simulate test output
    print("🔧 Simulation: Crafted 2 Mineral Survey Devices.")


@requires_license
def run(config, session=None):
    """Main entry point for this mode."""

    assert_profile_ready(getattr(session, "profile", None))

    character = config.get("character_name", "Unknown") if config else "Unknown"
    start_crafting(character)

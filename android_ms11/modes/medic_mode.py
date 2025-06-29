from utils.license_hooks import requires_license
from core.profile_loader import assert_profile_ready


def start_medic(character_name: str) -> None:
    """Simulate healing and buffing nearby allies."""

    print(f"🩺 Medic Mode Activated for {character_name}...")
    print("🧪 Monitoring group status and applying basic heals...")
    # Simulate test output
    print("🧪 Simulation: Buffed 3 nearby players.")


@requires_license
def run(config, session=None):
    """Main entry point for this mode."""

    assert_profile_ready(getattr(session, "profile", None))

    character = config.get("character_name", "Unknown") if config else "Unknown"
    start_medic(character)

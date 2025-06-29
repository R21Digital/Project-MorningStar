"""Combat assist mode implementation."""

from core.session_manager import SessionManager
from utils.license_hooks import requires_license
from core.profile_loader import assert_profile_ready


def start_afk_combat(character_name: str) -> None:
    """Simulate passive combat actions for a character."""

    print(f"🛡️ AFK Combat Mode Activated for {character_name}...")
    print("⚔️ Rotating through targets and listening for whispers...")
    # Simulate test output
    print("⚔️ Simulation: Defeated 5 mobs at waypoint.")


@requires_license
def run(config: dict, session: SessionManager) -> None:
    """Run combat assist loop using ``session`` for tracking."""

    assert_profile_ready(getattr(session, "profile", None))

    character = config.get("character_name", "Unknown")
    print(f"[COMBAT] Starting combat assist for {character}")
    session.add_action("combat_assist_start")
    start_afk_combat(character)
    session.add_action("combat_assist_end")


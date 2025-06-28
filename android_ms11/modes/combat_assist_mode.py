"""Combat assist mode implementation."""

from core.session_manager import SessionManager
from src.mode_afk_combat import start_afk_combat


def run(config: dict, session: SessionManager) -> None:
    """Run combat assist loop using ``session`` for tracking."""

    character = config.get("character_name", "Unknown")
    print(f"[COMBAT] Starting combat assist for {character}")
    session.add_action("combat_assist_start")
    start_afk_combat(character)
    session.add_action("combat_assist_end")


"""Quest mode implementation."""

from core.session_manager import SessionManager
from src.quest_selector import select_quest
from src.quest_executor import execute_quest
from utils.license_hooks import requires_license


@requires_license
def run(config: dict, session: SessionManager) -> None:
    """Run quest mode using ``session`` to track actions."""

    character = config.get("character_name", "Unknown")
    print(f"[QUEST] Starting quest mode for {character}")
    session.add_action("quest_mode_start")

    quest = select_quest(character)
    if quest is None:
        print("\u26A0\ufe0f No available quest.")
        session.add_action("quest_mode_end")
        return

    execute_quest(quest, dry_run=True)
    session.add_action("quest_complete")
    session.add_action("quest_mode_end")


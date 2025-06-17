"""CLI entry point for the MorningStar demo."""

from src.session_manager import run_session_check
from src.credit_tracker import track_credits
from src.log_manager import start_log
from src.xp_manager import XPManager


def main() -> None:
    """Run a simple session-only test."""
    print("\U0001F6F0\uFE0F MorningStar MS11 Initialized")
    print("\U0001F4CC Mode: SESSION ONLY TEST")
    start_log()
    run_session_check()
    track_credits()

    # XP Manager demo
    print("\n\U0001F9EA Starting XPManager demo...\n")
    manager = XPManager(character="MS11-Demo")
    manager.record_action("quest_complete")
    manager.record_action("mob_kill")
    manager.record_action("healing_tick", use_ocr=True)
    manager.end_session()


if __name__ == "__main__":
    main()

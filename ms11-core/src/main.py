"""CLI entry point for the MorningStar demo."""

from src.session_manager import run_session_check
from src.credit_tracker import track_credits
from src.log_manager import start_log


def main() -> None:
    """Run a simple session-only test."""
    print("\U0001F6F0\uFE0F MorningStar MS11 Initialized")
    print("\U0001F4CC Mode: SESSION ONLY TEST")
    start_log()
    run_session_check()
    track_credits()


if __name__ == "__main__":
    main()

from src.session_manager import run_session_check
from src.credit_tracker import track_credits
from src.log_manager import start_log
from src.mode_questing import start_questing


def main():
    print("\U0001F6F0\uFE0F MorningStar MS11 Initialized")
    print("\U0001F4CC Mode: QUESTING TEST")

    start_log()
    run_session_check()
    track_credits()

    print("\U0001F680 Initiating Questing Mode...")
    completed_quests = start_questing(character_name="Vornax")
    print(f"\U0001F4D8 Questing Session Summary: {len(completed_quests)} steps completed.")


if __name__ == "__main__":
    main()

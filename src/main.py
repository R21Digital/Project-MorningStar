from core.session_manager import SessionManager


def main():
    # Initialize new session in your desired mode
    session = SessionManager(mode="medic")  # Example mode: 'medic', 'crafting', 'questing'

    # Simulated: retrieve credits before and after
    session.set_start_credits(2000)
    session.add_action("Entered Theed Medical Center")
    session.add_action("Began healing nearby players")
    session.set_end_credits(2300)

    # End session and save log
    session.end_session()


if __name__ == "__main__":
    main()

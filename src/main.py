from core.session_manager import SessionManager
from src.movement.agent_mover import MovementAgent
from src.movement.movement_profiles import travel_to_city


def main():
    # Initialize new session in your desired mode
    session = SessionManager(mode="medic")  # Example mode: 'medic', 'crafting', 'questing'

    # Simulated: retrieve credits before and after
    session.set_start_credits(2000)
    session.add_action("Entered Theed Medical Center")
    session.add_action("Began healing nearby players")
    session.set_end_credits(2300)

    # Movement Test
    agent = MovementAgent(session=session)
    travel_to_city(agent, "Anchorhead")

    # End session and save log
    session.end_session()


if __name__ == "__main__":
    main()

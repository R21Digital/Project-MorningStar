from src.vision.states import register_state
from src.automation.automator import run_state_monitor_loop


def setup_known_states():
    register_state("continue_prompt", ["press enter to continue"])
    register_state(
        "npc_dialogue",
        ["what can i do", "greetings", "how can i help"],
    )


if __name__ == "__main__":
    setup_known_states()
    run_state_monitor_loop()

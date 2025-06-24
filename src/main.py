from src.vision.states import register_state
from src.automation.handlers import press_continue, handle_npc_dialogue
from src.automation.automator import run_state_monitor_loop


def setup_known_states():
    register_state("continue_prompt", ["press enter to continue"], press_continue)
    register_state(
        "npc_dialogue",
        ["what can i do", "greetings", "how can i help"],
        handle_npc_dialogue,
    )


if __name__ == "__main__":
    setup_known_states()
    run_state_monitor_loop()

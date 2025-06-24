import argparse

from src.vision.states import register_state
from src.modes.mode_runner import run_mode


def setup_known_states() -> None:
    register_state("continue_prompt", ["press enter to continue"])
    register_state(
        "npc_dialogue",
        ["what can i do", "greetings", "how can i help"],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, help="Mode to run (questing, medic, etc.)")
    args = parser.parse_args()

    setup_known_states()
    run_mode(args.mode)


if __name__ == "__main__":
    main()

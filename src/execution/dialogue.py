import random
import time


def execute_dialogue(step: dict) -> None:
    """Handle dialogue steps.

    This stub prints the NPC being interacted with and any dialogue options
    provided in the quest data. When options are present, a short delay is
    simulated (as if reading text via OCR) and an option is selected either at
    random or via an explicit ``selected_index`` field.
    """

    npc = step.get("npc", "Unknown NPC")
    options = step.get("options", [])
    selected_index = step.get("selected_index")

    print(f"\U0001F5E8\uFE0F [Dialogue] Interacting with {npc}")

    if options:
        print("\U0001F4AC Dialogue Options:")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")

        # Simulate delay (e.g. OCR processing or UI wait time)
        time.sleep(0.5)

        if selected_index is None:
            selected_index = random.randint(0, len(options) - 1)

        selected_option = options[selected_index]
        print(f"\n\u27A1 You selected: '{selected_option}'")
    else:
        print("\U0001F4AC No dialogue options provided.")

    # TODO: Replace with UI interaction, OCR, or macro simulation

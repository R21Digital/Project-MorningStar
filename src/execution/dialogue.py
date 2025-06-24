def execute_dialogue(step: dict) -> None:
    """Handle dialogue steps.

    This stub prints the NPC being interacted with and any dialogue options
    provided in the quest data.
    """

    npc = step.get("npc", "Unknown NPC")
    options = step.get("options", [])

    print(f"\U0001F5E8\uFE0F [Dialogue] Interacting with {npc}")

    if options:
        print("\U0001F4AC Dialogue Options:")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")

        # Simulate user choice — pick the first option for now
        selected_index = 0
        selected_option = options[selected_index]

        print(f"\n\u27A1 You selected: '{selected_option}'")
    else:
        print("\U0001F4AC No dialogue options provided.")

    # TODO: Replace with UI interaction, OCR, or macro simulation

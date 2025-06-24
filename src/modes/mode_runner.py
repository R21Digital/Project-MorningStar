from src.modes import questing, medic, grinding


def run_mode(mode_name: str) -> None:
    """Dispatch to the requested automation mode."""
    if mode_name == "questing":
        questing.start()
    elif mode_name == "medic":
        medic.start()
    elif mode_name == "grinding":
        grinding.start()
    else:
        print(f"[MODE] Unknown mode '{mode_name}'")

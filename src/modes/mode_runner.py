from src.modes import questing, medic, grinding
from utils.license_hooks import requires_license


@requires_license
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

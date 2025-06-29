from src.automation.automator import run_state_monitor_loop
from utils.license_hooks import requires_license


@requires_license
def start() -> None:
    """Entry point for grinding mode."""
    print("[MODE] Grinding mode started")
    run_state_monitor_loop()

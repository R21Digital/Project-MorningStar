from src.automation.automator import run_state_monitor_loop


def start() -> None:
    """Entry point for questing mode."""
    print("[MODE] Questing mode started")
    run_state_monitor_loop()

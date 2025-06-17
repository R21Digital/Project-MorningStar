from datetime import datetime


def run_session_check() -> None:
    """Output a timestamp for the session start and break reminder."""
    now = datetime.now()
    print(f"\U0001F551 Session started at: {now.strftime('%H:%M:%S')}")
    print("\u23F3 Will simulate a 5h play limit with 1h break.")

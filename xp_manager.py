from datetime import datetime
from xp_session import XPSession
from xp_tracker import track_xp_sync


class XPManager:
    """Manage XP tracking sessions."""

    def __init__(self, character: str):
        self.session = XPSession(character, xp_start=int(datetime.now().timestamp()))

    def record_action(self, action: str, use_ocr: bool = False):
        """Record a game action and its XP value."""
        xp = track_xp_sync(action=action, use_ocr=use_ocr)
        self.session.log_action(action_type=action, xp_value=xp)

    def end_session(self):
        """Finalize the session and save the log."""
        self.session.finalize(xp_end=int(datetime.now().timestamp()))
        path = self.session.save()
        print(f"\U0001F4C1 XP session saved to: {path}")

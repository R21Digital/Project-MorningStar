"""Simple experience point tracking utilities."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class XPManager:
    """Track XP gains for a game character."""

    character: str
    xp: int = 0
    xp_map: Dict[str, int] = field(
        default_factory=lambda: {
            "quest_complete": 100,
            "mob_kill": 10,
            "healing_tick": 2,
        }
    )

    def record_action(self, action: str, use_ocr: bool = False) -> None:
        """Record an XP-gaining action."""
        gained = self.xp_map.get(action, 0)
        self.xp += gained
        ocr_note = " via OCR" if use_ocr else ""
        print(f"\U0001F3AF {self.character} gained {gained} XP for {action}{ocr_note}.")

    def end_session(self) -> None:
        """Summarize total XP for the session."""
        print(f"\U0001F4C8 Session total for {self.character}: {self.xp} XP")

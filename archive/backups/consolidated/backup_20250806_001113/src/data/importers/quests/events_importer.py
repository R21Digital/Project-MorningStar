"""Importer stub for live event quests."""

from ..base_importer import BaseWikiImporter


class EventsImporter(BaseWikiImporter):
    """Placeholder importer for in-game event quests."""

    def __init__(self, source_path: str = "data/raw/events.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for event quests (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

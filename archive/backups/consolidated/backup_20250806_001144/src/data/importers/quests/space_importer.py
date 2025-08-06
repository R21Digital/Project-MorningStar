"""Importer stub for space quest data."""

from ..base_importer import BaseWikiImporter


class SpaceImporter(BaseWikiImporter):
    """Placeholder importer for space-based quests."""

    def __init__(self, source_path: str = "data/raw/space_quests.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for space quests (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

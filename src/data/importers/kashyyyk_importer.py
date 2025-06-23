"""Importer stub for Kashyyyk quest data."""

from .base_importer import BaseWikiImporter


class KashyyykImporter(BaseWikiImporter):
    """Placeholder importer for Kashyyyk quests."""

    def __init__(self, source_path: str = "data/raw/kashyyyk.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for Kashyyyk quests (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

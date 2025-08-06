"""Importer stub for Mustafar quest data."""

from .base_importer import BaseWikiImporter


class MustafarImporter(BaseWikiImporter):
    """Placeholder importer for Mustafar quests."""

    def __init__(self, source_path: str = "data/raw/mustafar.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for Mustafar quests (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

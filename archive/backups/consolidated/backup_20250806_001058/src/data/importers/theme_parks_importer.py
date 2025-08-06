"""Importer stub for Theme Parks quest data."""

from .base_importer import BaseWikiImporter


class ThemeParksImporter(BaseWikiImporter):
    """Placeholder importer for Theme Parks quests."""

    def __init__(self, source_path: str = "data/raw/theme_parks.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for Theme Parks quests (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

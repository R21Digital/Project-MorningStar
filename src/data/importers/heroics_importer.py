"""Importer stub for Heroics quest data."""

from .base_importer import BaseWikiImporter


class HeroicsImporter(BaseWikiImporter):
    """Placeholder importer for heroics wiki pages."""

    def __init__(self, source_path: str = "data/raw/heroics.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for heroics quests (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

"""Importer stub for Fandom-hosted quest data."""

from ..base_importer import BaseWikiImporter


class FandomQuestsImporter(BaseWikiImporter):
    """Placeholder importer for quests on Fandom."""

    def __init__(self, source_path: str = "data/raw/fandom_quests.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for Fandom quests (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

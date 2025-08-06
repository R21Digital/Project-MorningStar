"""Importer stub for heroics quest chain details."""

from ..base_importer import BaseWikiImporter


class HeroicsQuestsImporter(BaseWikiImporter):
    """Placeholder importer for heroics quest chains."""

    def __init__(self, source_path: str = "data/raw/heroics_quests.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for heroics quests (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

"""Importer stub for Mustafar quest chains."""

from ..base_importer import BaseWikiImporter


class MustafarQuestsImporter(BaseWikiImporter):
    """Placeholder importer for Mustafar quest lines."""

    def __init__(self, source_path: str = "data/raw/mustafar_quests.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for Mustafar quests (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

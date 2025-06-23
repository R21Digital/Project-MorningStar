"""Importer stub for Kashyyyk quest chains."""

from ..base_importer import BaseWikiImporter


class KashyyykQuestsImporter(BaseWikiImporter):
    """Placeholder importer for Kashyyyk quest chains."""

    def __init__(self, source_path: str = "data/raw/kashyyyk_quests.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for Kashyyyk quests (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

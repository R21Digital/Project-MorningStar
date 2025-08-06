"""Importer stub for legacy quest walkthroughs."""

from ..base_importer import BaseWikiImporter


class LegacyQuestImporter(BaseWikiImporter):
    """Placeholder importer for legacy quest guides."""

    def __init__(self, source_path: str = "data/raw/legacy_quests.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for legacy quests (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

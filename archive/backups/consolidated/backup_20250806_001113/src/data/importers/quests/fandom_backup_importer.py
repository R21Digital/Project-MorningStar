"""Importer stub for Fandom backup quest data."""

from ..base_importer import BaseWikiImporter


class FandomBackupImporter(BaseWikiImporter):
    """Placeholder importer for offline Fandom backups."""

    def __init__(self, source_path: str = "data/raw/fandom_backup.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for Fandom backup quests (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

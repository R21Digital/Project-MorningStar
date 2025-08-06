"""Importer stub for item data."""

from .base_importer import BaseWikiImporter


class ItemsImporter(BaseWikiImporter):
    """Placeholder importer for item listings."""

    def __init__(self, source_path: str = "data/raw/items.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for items (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

"""Importer stub for location data."""

from .base_importer import BaseWikiImporter


class LocationsImporter(BaseWikiImporter):
    """Placeholder importer for world locations."""

    def __init__(self, source_path: str = "data/raw/locations.html"):
        super().__init__(source_path)

    def fetch_data(self) -> str:
        """Return raw HTML for locations (stubbed)."""
        try:
            with open(self.source_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

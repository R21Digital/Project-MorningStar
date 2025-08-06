import os
from src.data.importers.base_importer import BaseWikiImporter

class LegacyWikiImporter(BaseWikiImporter):
    def __init__(self):
        # Define the source file for the Legacy Quest HTML
        super().__init__(source_path="data/raw/legacy.html")

    def fetch_data(self):
        # Open and read the HTML file contents
        with open(self.source_path, "r", encoding="utf-8") as f:
            return f.read()

    def extract_sections(self, soup):
        """
        Parses the HTML soup and extracts structured content.
        Adjust this logic based on how the legacy.html content is formatted.
        """
        quest_sections = []

        # Example: iterate through all h2/h3 and gather sibling content
        for heading in soup.find_all(["h2", "h3"]):
            section = {
                "title": heading.get_text(strip=True),
                "steps": []
            }

            # Grab the next elements until another heading or end of content
            next_tag = heading.find_next_sibling()
            while next_tag and next_tag.name not in ["h2", "h3"]:
                if next_tag.name in ["p", "ul", "ol"]:
                    section["steps"].append(next_tag.get_text(strip=True))
                next_tag = next_tag.find_next_sibling()

            if section["steps"]:  # Only include sections with steps
                quest_sections.append(section)

        return quest_sections


if __name__ == "__main__":
    # Ensure output directory exists
    os.makedirs("data/processed", exist_ok=True)

    # Run the import
    importer = LegacyWikiImporter()
    importer.run()

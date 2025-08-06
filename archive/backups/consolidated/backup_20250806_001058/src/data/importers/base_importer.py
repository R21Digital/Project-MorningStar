import os
import json
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup


class BaseWikiImporter(ABC):
    def __init__(self, source_path: str):
        """
        Base importer for SWG wiki-style HTML content.

        Args:
            source_path (str): Path to a local HTML file or URL.
        """
        self.source_path = source_path

    @abstractmethod
    def fetch_data(self):
        """
        Fetch raw HTML content from the given source.
        This method must be implemented by child classes.
        """
        pass

    def parse_html(self, html: str):
        """
        Parse HTML content using BeautifulSoup and extract structured data.

        Args:
            html (str): Raw HTML string.

        Returns:
            List[Dict]: A list of structured sections with titles and steps.
        """
        soup = BeautifulSoup(html, "html.parser")

        sections = []
        current_section = {"title": None, "steps": []}

        for tag in soup.find_all(["h1", "h2", "h3", "p", "li"]):
            text = tag.get_text(strip=True)
            if not text:
                continue

            if tag.name in ["h1", "h2", "h3"]:
                if current_section["title"] or current_section["steps"]:
                    sections.append(current_section)
                current_section = {"title": text, "steps": []}
            elif tag.name in ["p", "li"]:
                current_section["steps"].append(text)

        if current_section["title"] or current_section["steps"]:
            sections.append(current_section)

        return sections

    def save_to_json(self, data, output_path):
        """
        Save structured data to a JSON file.

        Args:
            data (Any): Data to write to JSON.
            output_path (str): Path to the output .json file.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def run(self):
        """
        Fetch, parse, and save quest data.
        """
        raw_html = self.fetch_data()
        parsed_data = self.parse_html(raw_html)
        output_path = os.path.join("data", "processed", "legacy_quests.json")
        self.save_to_json(parsed_data, output_path)
        print(f"✅ Parsed data saved to {output_path}")

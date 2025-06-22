# src/data/importers/quests_importer.py

from .base_importer import BaseWikiImporter
import requests
from bs4 import BeautifulSoup

class QuestsImporter(BaseWikiImporter):
    def __init__(self):
        super().__init__("quests")

    def fetch_data(self):
        url = "https://swgr.org/wiki/quests/"
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def parse_data(self, html):
        soup = BeautifulSoup(html, "html.parser")
        quests = []

        table = soup.find("table")
        if table:
            rows = table.find_all("tr")[1:]  # Skip headers
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    name = cols[0].text.strip()
                    description = cols[1].text.strip()
                    quests.append({
                        "name": name,
                        "description": description
                    })

        return quests


if __name__ == "__main__":
    importer = QuestsImporter()
    importer.run()

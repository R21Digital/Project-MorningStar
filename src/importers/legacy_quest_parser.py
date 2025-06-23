import os
import json
from pathlib import Path
from bs4 import BeautifulSoup

from utils.source_verifier import file_changed

RAW_HTML_PATH = "data/raw/legacy.html"
OUTPUT_JSON_PATH = "data/processed/legacy_quests.json"
HASH_PATH = Path(RAW_HTML_PATH).with_suffix(".hash")

def parse_legacy_quest_html():
    if not file_changed(RAW_HTML_PATH, HASH_PATH):
        print("ℹ️ legacy.html unchanged, skipping parse")
        return

    with open(RAW_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Extract content inside the main article
    content_div = soup.find("div", class_="mw-parser-output")
    if not content_div:
        raise ValueError("Could not find content section in legacy.html")

    quests = []
    current_quest = None

    for tag in content_div.find_all(["h2", "h3", "h4", "p", "ul", "ol"]):
        # Main quest section headers
        if tag.name == "h2":
            if current_quest:
                quests.append(current_quest)
            current_quest = {"title": tag.get_text(strip=True), "steps": []}

        elif tag.name in ["h3", "h4"]:
            if current_quest:
                current_quest["steps"].append({"step_title": tag.get_text(strip=True), "description": ""})

        elif tag.name == "p":
            if current_quest and current_quest["steps"]:
                if current_quest["steps"][-1]["description"]:
                    current_quest["steps"][-1]["description"] += "\n" + tag.get_text(strip=True)
                else:
                    current_quest["steps"][-1]["description"] = tag.get_text(strip=True)

        elif tag.name in ["ul", "ol"]:
            bullet_points = [li.get_text(strip=True) for li in tag.find_all("li")]
            if current_quest and current_quest["steps"]:
                current_quest["steps"][-1].setdefault("notes", []).extend(bullet_points)

    if current_quest:
        quests.append(current_quest)

    # Save parsed output
    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(quests, f, indent=2, ensure_ascii=False)

    print(f"✅ Parsed Legacy Quest data saved to {OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    parse_legacy_quest_html()

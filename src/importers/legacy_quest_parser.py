import os
import json
from pathlib import Path
try:
    from bs4 import BeautifulSoup
except Exception:  # pragma: no cover - optional dependency
    BeautifulSoup = None

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

    if BeautifulSoup is not None and not isinstance(BeautifulSoup, type):
        soup = BeautifulSoup(html, "html.parser")
        content_div = soup.find("div", class_="mw-parser-output")
        if not content_div:
            raise ValueError("Could not find content section in legacy.html")
        tags = content_div.find_all(["h2", "h3", "h4", "p", "ul", "ol"])
    else:
        # Minimal fallback parser using regex
        import re
        content_div = re.search(r'<div class="mw-parser-output">(.*)</div>', html, re.S)
        if not content_div:
            raise ValueError("Could not find content section in legacy.html")
        raw = content_div.group(1)
        # Split tags manually preserving order
        # Build fake objects
        class Tag:
            def __init__(self, name, text):
                self.name = name
                self._text = text

            def get_text(self, strip=False):
                return self._text.strip() if strip else self._text

        parsed = []
        for match in re.finditer(r'<(h2|h3|h4|p|ul|ol)[^>]*>(.*?)</\1>', raw, re.S):
            name, body = match.group(1), match.group(2)
            if name in {"ul", "ol"}:
                items = re.findall(r"<li>(.*?)</li>", body)
                body = "|".join(items)
            parsed.append(Tag(name, body))
        tags = parsed
    quests = []
    current_quest = None

    for tag in tags:
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
            if hasattr(tag, "find_all"):
                bullet_points = [li.get_text(strip=True) for li in tag.find_all("li")]
            else:
                bullet_points = tag.get_text().split("|") if tag.get_text() else []
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

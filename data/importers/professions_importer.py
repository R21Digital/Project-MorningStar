import os
import json
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://swgr.org/wiki/"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'parsed', 'professions'))


def fetch_profession_html(profession: str) -> str:
    """Fetch the raw HTML for a profession page."""
    url = f"{BASE_URL}{profession}/"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text


def parse_profession_html(html: str) -> dict:
    """Parse skill boxes, XP costs and profession tags from HTML."""
    soup = BeautifulSoup(html, "html.parser")

    skill_boxes: list[str] = []
    xp_costs: dict[str, int] = {}
    tags: list[str] = []

    # Skill tree / boxes
    skill = soup.find(string=lambda t: t and "Skill" in t and ("Tree" in t or "Boxes" in t))
    if skill:
        ul = skill.find_parent().find_next("ul")
        if ul:
            for li in ul.find_all("li"):
                text = li.get_text(strip=True)
                skill_boxes.append(text)
                m = re.search(r"([0-9,]+)\s*[A-Za-z]*\s*XP", text)
                if m:
                    xp = int(m.group(1).replace(",", ""))
                    name = re.sub(r"\([^)]*\)", "", text).strip()
                    xp_costs[name] = xp

    # Profession tags
    tag = soup.find(string=lambda t: t and ("Profession Tags" in t or t.strip() == "Tags"))
    if tag:
        ul = tag.find_parent().find_next("ul")
        if ul:
            tags = [li.get_text(strip=True) for li in ul.find_all("li")]

    return {"skill_boxes": skill_boxes, "xp_costs": xp_costs, "tags": tags}


def save_profession_data(profession: str, data: dict) -> str:
    """Save the parsed data for a profession to JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{profession.lower()}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return out_path


def fetch_and_save(profession: str) -> str:
    """Fetch a profession page and persist the parsed data."""
    html = fetch_profession_html(profession)
    data = parse_profession_html(html)
    return save_profession_data(profession, data)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Import a profession from the SWGR wiki")
    parser.add_argument("profession", help="Profession name, e.g. Architect")
    args = parser.parse_args(argv)
    path = fetch_and_save(args.profession)
    print(f"Saved to {path}")


if __name__ == "__main__":
    main()

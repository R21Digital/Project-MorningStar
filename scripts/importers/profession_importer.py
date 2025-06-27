import os
import json
import re
try:
    import requests
except ImportError as exc:
    print("Error: the 'requests' package is required. Install it with 'pip install requests'.")
    raise SystemExit(1) from exc

try:
    from bs4 import BeautifulSoup
except Exception:  # pragma: no cover - optional dependency
    BeautifulSoup = None

BASE_URL = "https://swgr.org/wiki/"
OUTPUT_DIR = os.path.join("android_ms11", "data", "professions")


def fetch_profession_html(name: str) -> str:
    url = f"{BASE_URL}{name}/"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text


def parse_profession_html(html: str) -> dict:
    """Return parsed profession data from ``html``.

    A minimal regex parser is used when ``BeautifulSoup`` isn't available.
    """
    if BeautifulSoup is None or isinstance(BeautifulSoup, type):
        prereq_match = re.search(r"<h3>Prerequisites</h3>\s*<ul>(.*?)</ul>", html, re.S)
        prereqs = re.findall(r"<li>(.*?)</li>", prereq_match.group(1)) if prereq_match else []

        skill_match = re.search(r"<h3>Skill Tree</h3>\s*<ul>(.*?)</ul>", html, re.S)
        skill_boxes = re.findall(r"<li>(.*?)</li>", skill_match.group(1)) if skill_match else []
        xp_costs: dict[str, int] = {}
        for item in skill_boxes:
            m = re.search(r"([0-9,]+)\s*[A-Za-z]*\s*XP", item)
            if m:
                xp = int(m.group(1).replace(',', ''))
                name = re.sub(r"\([^)]*\)", "", item).strip()
                xp_costs[name] = xp
    else:
        soup = BeautifulSoup(html, "html.parser")
        prereqs: list[str] = []
        skill_boxes: list[str] = []
        xp_costs: dict[str, int] = {}

        pre = soup.find(string=lambda t: t and "Prerequisite" in t)
        if pre:
            ul = pre.find_parent().find_next("ul")
            if ul:
                prereqs = [li.get_text(strip=True) for li in ul.find_all("li")]

        skill = soup.find(string=lambda t: t and "Skill" in t and ("Tree" in t or "Boxes" in t))
        if skill:
            ul = skill.find_parent().find_next("ul")
            if ul:
                for li in ul.find_all("li"):
                    text = li.get_text(strip=True)
                    skill_boxes.append(text)
                    m = re.search(r"([0-9,]+)\s*[A-Za-z]*\s*XP", text)
                    if m:
                        xp = int(m.group(1).replace(',', ''))
                        name = re.sub(r"\([^)]*\)", "", text).strip()
                        xp_costs[name] = xp
    return {
        "prerequisites": prereqs,
        "skill_boxes": skill_boxes,
        "xp_costs": xp_costs,
    }


def save_profession_data(name: str, data: dict) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{name.lower()}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return out_path


def fetch_and_save(name: str) -> str:
    html = fetch_profession_html(name)
    data = parse_profession_html(html)
    return save_profession_data(name, data)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Import profession data from SWGR wiki")
    parser.add_argument("profession", help="Profession name, e.g. Architect")
    args = parser.parse_args(argv)
    path = fetch_and_save(args.profession)
    print(f"Saved to {path}")


if __name__ == "__main__":
    main()

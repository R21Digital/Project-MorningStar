import argparse
import json
from pathlib import Path
from typing import List, Dict, Any


class LegacyQuestManager:
    """Load and query legacy quest data."""

    def __init__(self, json_path: Path | str | None = None) -> None:
        if json_path is None:
            root = Path(__file__).resolve().parents[2]
            json_path = root / "data" / "processed" / "legacy_quests.json"
        self.path = Path(json_path)
        with self.path.open("r", encoding="utf-8") as f:
            self.quests: List[Dict[str, Any]] = json.load(f)

    def list_all_quests(self) -> List[Dict[str, Any]]:
        """Return the raw list of all quests."""
        return self.quests

    def find_by_npc(self, npc: str) -> List[Dict[str, Any]]:
        """Return quests matching the given NPC/quest giver name."""
        npc = npc.lower()
        results = []
        for q in self.quests:
            giver = q.get("npc") or q.get("quest_giver", "")
            if npc in giver.lower():
                results.append(q)
        return results

    def find_by_planet(self, planet: str) -> List[Dict[str, Any]]:
        """Return quests located on the given planet."""
        planet = planet.lower()
        return [q for q in self.quests if planet in q.get("planet", "").lower()]

    def search(self, term: str) -> List[Dict[str, Any]]:
        """Search quests by title or notes."""
        term = term.lower()
        results = []
        for q in self.quests:
            title = q.get("title", "").lower()
            notes = q.get("notes", "").lower()
            if term in title or term in notes:
                results.append(q)
        return results


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Legacy quest data explorer")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List all quests")
    group.add_argument("--search", type=str, help="Search title or notes")
    group.add_argument("--npc", type=str, help="Filter quests by NPC")
    group.add_argument("--planet", type=str, help="Filter quests by planet")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    manager = LegacyQuestManager()
    if args.list:
        results = manager.list_all_quests()
    elif args.search:
        results = manager.search(args.search)
    elif args.npc:
        results = manager.find_by_npc(args.npc)
    elif args.planet:
        results = manager.find_by_planet(args.planet)
    else:
        results = []

    for q in results:
        print(q.get("title", "Unknown"))
    return results


if __name__ == "__main__":
    main()

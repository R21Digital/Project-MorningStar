"""Simple quest dependency graph representation."""


class QuestGraph:
    def __init__(self) -> None:
        self.edges: dict[str, set[str]] = {}

    def add_edge(self, src: str, dst: str) -> None:
        """Add a directional edge between quests."""
        self.edges.setdefault(src, set()).add(dst)

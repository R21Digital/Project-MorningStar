from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple


class Status:
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"


class Node(ABC):
    @abstractmethod
    def tick(self, ctx: dict) -> str:
        ...


class Sequence(Node):
    def __init__(self, children: List[Node]):
        self.children = children

    def tick(self, ctx: dict) -> str:
        for child in self.children:
            s = child.tick(ctx)
            if s != Status.SUCCESS:
                return s
        return Status.SUCCESS


class Selector(Node):
    def __init__(self, children: List[Node]):
        self.children = children

    def tick(self, ctx: dict) -> str:
        for child in self.children:
            s = child.tick(ctx)
            if s != Status.FAILURE:
                return s
        return Status.FAILURE


class Condition(Node):
    def __init__(self, fn):
        self.fn = fn

    def tick(self, ctx: dict) -> str:
        return Status.SUCCESS if self.fn(ctx) else Status.FAILURE


class Action(Node):
    def __init__(self, fn):
        self.fn = fn

    def tick(self, ctx: dict) -> str:
        return self.fn(ctx)


def success(_ctx: dict) -> str:
    return Status.SUCCESS


def failure(_ctx: dict) -> str:
    return Status.FAILURE



from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, List, Any


_subscribers: Dict[str, List[Callable[..., None]]] = defaultdict(list)


def subscribe(topic: str, fn: Callable[..., None]) -> None:
    _subscribers[topic].append(fn)


def publish(topic: str, **kwargs: Any) -> None:
    for fn in list(_subscribers.get(topic, [])):
        try:
            fn(**kwargs)
        except Exception:
            pass



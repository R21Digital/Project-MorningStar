#!/usr/bin/env python3
"""Test dataclass compatibility."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class TestQuestProgress:
    """Test quest progress dataclass."""
    quest_id: str
    user_id: Optional[str] = None
    current_step: int = 0
    steps_completed: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    notes: str = ""

if __name__ == "__main__":
    print("Testing dataclass...")
    test = TestQuestProgress(quest_id="test")
    print(f"Test successful: {test}")
    print(f"steps_completed: {test.steps_completed}")

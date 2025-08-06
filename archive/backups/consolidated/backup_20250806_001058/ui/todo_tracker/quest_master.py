"""Quest Master - Core quest data structures and management for Batch 045."""

import json
import yaml
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import logging

logger = logging.getLogger(__name__)


class QuestStatus(Enum):
    """Quest completion status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class QuestPriority(Enum):
    """Quest priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class QuestData:
    """Represents a quest with all its metadata."""
    id: str
    name: str
    planet: str
    npc: Optional[str] = None
    description: Optional[str] = None
    objectives: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)
    xp_reward: int = 0
    credit_reward: int = 0
    difficulty: str = "normal"
    quest_type: str = "standard"
    status: QuestStatus = QuestStatus.NOT_STARTED
    priority: QuestPriority = QuestPriority.MEDIUM
    completion_date: Optional[datetime] = None
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'planet': self.planet,
            'npc': self.npc,
            'description': self.description,
            'objectives': self.objectives,
            'prerequisites': self.prerequisites,
            'rewards': self.rewards,
            'xp_reward': self.xp_reward,
            'credit_reward': self.credit_reward,
            'difficulty': self.difficulty,
            'quest_type': self.quest_type,
            'status': self.status.value,
            'priority': self.priority.value,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'notes': self.notes,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestData':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            planet=data['planet'],
            npc=data.get('npc'),
            description=data.get('description'),
            objectives=data.get('objectives', []),
            prerequisites=data.get('prerequisites', []),
            rewards=data.get('rewards', {}),
            xp_reward=data.get('xp_reward', 0),
            credit_reward=data.get('credit_reward', 0),
            difficulty=data.get('difficulty', 'normal'),
            quest_type=data.get('quest_type', 'standard'),
            status=QuestStatus(data.get('status', 'not_started')),
            priority=QuestPriority(data.get('priority', 'medium')),
            completion_date=datetime.fromisoformat(data['completion_date']) if data.get('completion_date') else None,
            notes=data.get('notes'),
            tags=data.get('tags', [])
        )


class QuestMaster:
    """Manages quest data and provides quest-related operations."""
    
    def __init__(self, quests_dir: str = "data/quests"):
        """Initialize QuestMaster with quest data directory."""
        self.quests_dir = Path(quests_dir)
        self.quests: Dict[str, QuestData] = {}
        self.quest_chains: Dict[str, List[str]] = {}
        self.planet_quests: Dict[str, List[str]] = {}
        self._load_quest_data()
    
    def _load_quest_data(self):
        """Load quest data from YAML files."""
        if not self.quests_dir.exists():
            logger.warning(f"Quests directory {self.quests_dir} does not exist")
            return
        
        for planet_dir in self.quests_dir.iterdir():
            if planet_dir.is_dir():
                planet_name = planet_dir.name
                self.planet_quests[planet_name] = []
                
                for quest_file in planet_dir.glob("*.yaml"):
                    try:
                        with open(quest_file, 'r', encoding='utf-8') as f:
                            quest_data = yaml.safe_load(f)
                        
                        if isinstance(quest_data, dict):
                            quest = QuestData.from_dict(quest_data)
                            self.quests[quest.id] = quest
                            self.planet_quests[planet_name].append(quest.id)
                            
                    except Exception as e:
                        logger.error(f"Error loading quest file {quest_file}: {e}")
        
        self._build_quest_chains()
        logger.info(f"Loaded {len(self.quests)} quests from {len(self.planet_quests)} planets")
    
    def _build_quest_chains(self):
        """Build quest chains based on prerequisites."""
        for quest_id, quest in self.quests.items():
            if quest.prerequisites:
                # Create chain for this quest
                chain_id = f"chain_{quest_id}"
                self.quest_chains[chain_id] = quest.prerequisites + [quest_id]
    
    def get_quest(self, quest_id: str) -> Optional[QuestData]:
        """Get quest by ID."""
        return self.quests.get(quest_id)
    
    def get_quests_by_planet(self, planet: str) -> List[QuestData]:
        """Get all quests for a specific planet."""
        quest_ids = self.planet_quests.get(planet, [])
        return [self.quests[qid] for qid in quest_ids if qid in self.quests]
    
    def get_quests_by_status(self, status: QuestStatus) -> List[QuestData]:
        """Get all quests with a specific status."""
        return [quest for quest in self.quests.values() if quest.status == status]
    
    def get_quests_by_priority(self, priority: QuestPriority) -> List[QuestData]:
        """Get all quests with a specific priority."""
        return [quest for quest in self.quests.values() if quest.priority == priority]
    
    def get_available_quests(self) -> List[QuestData]:
        """Get quests that can be started (prerequisites met)."""
        available = []
        for quest in self.quests.values():
            if quest.status == QuestStatus.NOT_STARTED:
                if self._are_prerequisites_met(quest):
                    available.append(quest)
        return available
    
    def _are_prerequisites_met(self, quest: QuestData) -> bool:
        """Check if all prerequisites for a quest are met."""
        for prereq_id in quest.prerequisites:
            prereq_quest = self.quests.get(prereq_id)
            if not prereq_quest or prereq_quest.status != QuestStatus.COMPLETED:
                return False
        return True
    
    def update_quest_status(self, quest_id: str, status: QuestStatus, 
                          completion_date: Optional[datetime] = None):
        """Update quest status."""
        quest = self.quests.get(quest_id)
        if quest:
            quest.status = status
            if status == QuestStatus.COMPLETED and completion_date:
                quest.completion_date = completion_date
            logger.info(f"Updated quest {quest_id} status to {status.value}")
    
    def update_quest_priority(self, quest_id: str, priority: QuestPriority):
        """Update quest priority."""
        quest = self.quests.get(quest_id)
        if quest:
            quest.priority = priority
            logger.info(f"Updated quest {quest_id} priority to {priority.value}")
    
    def add_quest_note(self, quest_id: str, note: str):
        """Add a note to a quest."""
        quest = self.quests.get(quest_id)
        if quest:
            if quest.notes:
                quest.notes += f"\n{note}"
            else:
                quest.notes = note
            logger.info(f"Added note to quest {quest_id}")
    
    def get_quest_chain(self, quest_id: str) -> List[QuestData]:
        """Get the quest chain for a specific quest."""
        for chain_id, chain_quests in self.quest_chains.items():
            if quest_id in chain_quests:
                return [self.quests[qid] for qid in chain_quests if qid in self.quests]
        return []
    
    def get_total_quests(self) -> int:
        """Get total number of quests."""
        return len(self.quests)
    
    def get_completed_quests(self) -> int:
        """Get number of completed quests."""
        return len(self.get_quests_by_status(QuestStatus.COMPLETED))
    
    def get_completion_percentage(self) -> float:
        """Get overall completion percentage."""
        total = self.get_total_quests()
        if total == 0:
            return 0.0
        return (self.get_completed_quests() / total) * 100
    
    def export_quest_data(self, output_file: str):
        """Export quest data to JSON file."""
        data = {
            'quests': {qid: quest.to_dict() for qid, quest in self.quests.items()},
            'planet_quests': self.planet_quests,
            'quest_chains': self.quest_chains,
            'export_date': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported quest data to {output_file}")
    
    def import_quest_data(self, input_file: str):
        """Import quest data from JSON file."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.quests = {qid: QuestData.from_dict(quest_data) 
                          for qid, quest_data in data.get('quests', {}).items()}
            self.planet_quests = data.get('planet_quests', {})
            self.quest_chains = data.get('quest_chains', {})
            
            logger.info(f"Imported quest data from {input_file}")
            
        except Exception as e:
            logger.error(f"Error importing quest data from {input_file}: {e}") 
"""Todo Manager - Manages to-do items and categories for Batch 045."""

import json
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from .quest_master import QuestData, QuestStatus, QuestPriority

logger = logging.getLogger(__name__)


class TodoCategory(Enum):
    """Todo item categories."""
    QUEST = "quest"
    COLLECTION = "collection"
    ACHIEVEMENT = "achievement"
    CRAFTING = "crafting"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    OTHER = "other"


@dataclass
class TodoItem:
    """Represents a to-do item."""
    id: str
    title: str
    description: Optional[str] = None
    category: TodoCategory = TodoCategory.OTHER
    priority: QuestPriority = QuestPriority.MEDIUM
    status: QuestStatus = QuestStatus.NOT_STARTED
    quest_id: Optional[str] = None
    planet: Optional[str] = None
    prerequisites: List[str] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)
    created_date: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    estimated_time: Optional[int] = None  # in minutes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'priority': self.priority.value,
            'status': self.status.value,
            'quest_id': self.quest_id,
            'planet': self.planet,
            'prerequisites': self.prerequisites,
            'rewards': self.rewards,
            'created_date': self.created_date.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'notes': self.notes,
            'tags': self.tags,
            'estimated_time': self.estimated_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TodoItem':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            title=data['title'],
            description=data.get('description'),
            category=TodoCategory(data.get('category', 'other')),
            priority=QuestPriority(data.get('priority', 'medium')),
            status=QuestStatus(data.get('status', 'not_started')),
            quest_id=data.get('quest_id'),
            planet=data.get('planet'),
            prerequisites=data.get('prerequisites', []),
            rewards=data.get('rewards', {}),
            created_date=datetime.fromisoformat(data.get('created_date', datetime.now().isoformat())),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            completed_date=datetime.fromisoformat(data['completed_date']) if data.get('completed_date') else None,
            notes=data.get('notes'),
            tags=data.get('tags', []),
            estimated_time=data.get('estimated_time')
        )


class TodoManager:
    """Manages to-do items and provides todo-related operations."""
    
    def __init__(self, todo_file: str = "data/todo_list.json"):
        """Initialize TodoManager with todo file."""
        self.todo_file = Path(todo_file)
        self.todos: Dict[str, TodoItem] = {}
        self.categories: Dict[TodoCategory, List[str]] = {cat: [] for cat in TodoCategory}
        self._load_todo_data()
    
    def _load_todo_data(self):
        """Load todo data from JSON file."""
        if not self.todo_file.exists():
            logger.info(f"Todo file {self.todo_file} does not exist, starting with empty list")
            return
        
        try:
            with open(self.todo_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.todos = {tid: TodoItem.from_dict(todo_data) 
                         for tid, todo_data in data.get('todos', {}).items()}
            
            # Rebuild category index
            for todo_id, todo in self.todos.items():
                self.categories[todo.category].append(todo_id)
            
            logger.info(f"Loaded {len(self.todos)} todo items")
            
        except Exception as e:
            logger.error(f"Error loading todo data from {self.todo_file}: {e}")
    
    def _save_todo_data(self):
        """Save todo data to JSON file."""
        try:
            self.todo_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'todos': {tid: todo.to_dict() for tid, todo in self.todos.items()},
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.todo_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved todo data to {self.todo_file}")
            
        except Exception as e:
            logger.error(f"Error saving todo data to {self.todo_file}: {e}")
    
    def add_todo_item(self, title: str, description: Optional[str] = None,
                     category: TodoCategory = TodoCategory.OTHER,
                     priority: QuestPriority = QuestPriority.MEDIUM,
                     quest_id: Optional[str] = None, planet: Optional[str] = None,
                     prerequisites: Optional[List[str]] = None,
                     rewards: Optional[Dict[str, Any]] = None,
                     due_date: Optional[datetime] = None,
                     estimated_time: Optional[int] = None,
                     tags: Optional[List[str]] = None) -> str:
        """Add a new todo item."""
        todo_id = f"todo_{len(self.todos) + 1}"
        
        todo = TodoItem(
            id=todo_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            quest_id=quest_id,
            planet=planet,
            prerequisites=prerequisites or [],
            rewards=rewards or {},
            due_date=due_date,
            estimated_time=estimated_time,
            tags=tags or []
        )
        
        self.todos[todo_id] = todo
        self.categories[category].append(todo_id)
        
        self._save_todo_data()
        logger.info(f"Added todo item: {title}")
        
        return todo_id
    
    def add_quest_as_todo(self, quest: QuestData) -> str:
        """Add a quest as a todo item."""
        return self.add_todo_item(
            title=quest.name,
            description=quest.description,
            category=TodoCategory.QUEST,
            priority=quest.priority,
            quest_id=quest.id,
            planet=quest.planet,
            prerequisites=quest.prerequisites,
            rewards=quest.rewards,
            tags=quest.tags
        )
    
    def get_todo_item(self, todo_id: str) -> Optional[TodoItem]:
        """Get todo item by ID."""
        return self.todos.get(todo_id)
    
    def get_todos_by_category(self, category: TodoCategory) -> List[TodoItem]:
        """Get all todo items in a specific category."""
        todo_ids = self.categories.get(category, [])
        return [self.todos[tid] for tid in todo_ids if tid in self.todos]
    
    def get_todos_by_status(self, status: QuestStatus) -> List[TodoItem]:
        """Get all todo items with a specific status."""
        return [todo for todo in self.todos.values() if todo.status == status]
    
    def get_todos_by_priority(self, priority: QuestPriority) -> List[TodoItem]:
        """Get all todo items with a specific priority."""
        return [todo for todo in self.todos.values() if todo.priority == priority]
    
    def get_todos_by_planet(self, planet: str) -> List[TodoItem]:
        """Get all todo items for a specific planet."""
        return [todo for todo in self.todos.values() if todo.planet == planet]
    
    def update_todo_status(self, todo_id: str, status: QuestStatus):
        """Update todo item status."""
        todo = self.todos.get(todo_id)
        if todo:
            todo.status = status
            if status == QuestStatus.COMPLETED:
                todo.completed_date = datetime.now()
            self._save_todo_data()
            logger.info(f"Updated todo {todo_id} status to {status.value}")
    
    def update_todo_priority(self, todo_id: str, priority: QuestPriority):
        """Update todo item priority."""
        todo = self.todos.get(todo_id)
        if todo:
            todo.priority = priority
            self._save_todo_data()
            logger.info(f"Updated todo {todo_id} priority to {priority.value}")
    
    def add_todo_note(self, todo_id: str, note: str):
        """Add a note to a todo item."""
        todo = self.todos.get(todo_id)
        if todo:
            if todo.notes:
                todo.notes += f"\n{note}"
            else:
                todo.notes = note
            self._save_todo_data()
            logger.info(f"Added note to todo {todo_id}")
    
    def delete_todo_item(self, todo_id: str):
        """Delete a todo item."""
        todo = self.todos.get(todo_id)
        if todo:
            # Remove from category index
            if todo_id in self.categories[todo.category]:
                self.categories[todo.category].remove(todo_id)
            
            # Remove from todos
            del self.todos[todo_id]
            
            self._save_todo_data()
            logger.info(f"Deleted todo item: {todo.title}")
    
    def get_overdue_todos(self) -> List[TodoItem]:
        """Get todo items that are overdue."""
        now = datetime.now()
        overdue = []
        for todo in self.todos.values():
            if (todo.due_date and todo.due_date < now and 
                todo.status != QuestStatus.COMPLETED):
                overdue.append(todo)
        return overdue
    
    def get_due_soon_todos(self, days: int = 3) -> List[TodoItem]:
        """Get todo items due within specified days."""
        from datetime import timedelta
        
        now = datetime.now()
        due_date = now + timedelta(days=days)
        due_soon = []
        
        for todo in self.todos.values():
            if (todo.due_date and now <= todo.due_date <= due_date and
                todo.status != QuestStatus.COMPLETED):
                due_soon.append(todo)
        
        return due_soon
    
    def get_total_todos(self) -> int:
        """Get total number of todo items."""
        return len(self.todos)
    
    def get_completed_todos(self) -> int:
        """Get number of completed todo items."""
        return len(self.get_todos_by_status(QuestStatus.COMPLETED))
    
    def get_completion_percentage(self) -> float:
        """Get overall completion percentage."""
        total = self.get_total_todos()
        if total == 0:
            return 0.0
        return (self.get_completed_todos() / total) * 100
    
    def get_category_stats(self) -> Dict[TodoCategory, Dict[str, int]]:
        """Get statistics for each category."""
        stats = {}
        for category in TodoCategory:
            todos = self.get_todos_by_category(category)
            total = len(todos)
            completed = len([t for t in todos if t.status == QuestStatus.COMPLETED])
            
            stats[category] = {
                'total': total,
                'completed': completed,
                'pending': total - completed
            }
        
        return stats
    
    def search_todos(self, query: str) -> List[TodoItem]:
        """Search todo items by title, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for todo in self.todos.values():
            if (query_lower in todo.title.lower() or
                (todo.description and query_lower in todo.description.lower()) or
                any(query_lower in tag.lower() for tag in todo.tags)):
                results.append(todo)
        
        return results
    
    def get_available_todos(self) -> List[TodoItem]:
        """Get todo items that can be started (prerequisites met)."""
        available = []
        for todo in self.todos.values():
            if todo.status == QuestStatus.NOT_STARTED:
                if self._are_prerequisites_met(todo):
                    available.append(todo)
        return available
    
    def _are_prerequisites_met(self, todo: TodoItem) -> bool:
        """Check if all prerequisites for a todo item are met."""
        for prereq_id in todo.prerequisites:
            prereq_todo = self.todos.get(prereq_id)
            if not prereq_todo or prereq_todo.status != QuestStatus.COMPLETED:
                return False
        return True 
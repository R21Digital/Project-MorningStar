"""Progress Tracker - Tracks completion progress and statistics for Batch 045."""

import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

from .quest_master import QuestData, QuestStatus, QuestPriority
from .todo_manager import TodoItem, TodoCategory

logger = logging.getLogger(__name__)


@dataclass
class ProgressData:
    """Represents progress data for tracking completion."""
    total_items: int = 0
    completed_items: int = 0
    in_progress_items: int = 0
    not_started_items: int = 0
    skipped_items: int = 0
    failed_items: int = 0
    completion_percentage: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    xp_gained: int = 0
    credits_gained: int = 0
    time_spent: int = 0  # in minutes
    planets_visited: List[str] = field(default_factory=list)
    categories_completed: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'total_items': self.total_items,
            'completed_items': self.completed_items,
            'in_progress_items': self.in_progress_items,
            'not_started_items': self.not_started_items,
            'skipped_items': self.skipped_items,
            'failed_items': self.failed_items,
            'completion_percentage': self.completion_percentage,
            'last_updated': self.last_updated.isoformat(),
            'xp_gained': self.xp_gained,
            'credits_gained': self.credits_gained,
            'time_spent': self.time_spent,
            'planets_visited': self.planets_visited,
            'categories_completed': self.categories_completed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProgressData':
        """Create from dictionary."""
        return cls(
            total_items=data.get('total_items', 0),
            completed_items=data.get('completed_items', 0),
            in_progress_items=data.get('in_progress_items', 0),
            not_started_items=data.get('not_started_items', 0),
            skipped_items=data.get('skipped_items', 0),
            failed_items=data.get('failed_items', 0),
            completion_percentage=data.get('completion_percentage', 0.0),
            last_updated=datetime.fromisoformat(data.get('last_updated', datetime.now().isoformat())),
            xp_gained=data.get('xp_gained', 0),
            credits_gained=data.get('credits_gained', 0),
            time_spent=data.get('time_spent', 0),
            planets_visited=data.get('planets_visited', []),
            categories_completed=data.get('categories_completed', {})
        )


@dataclass
class CompletionStats:
    """Represents completion statistics."""
    daily_completions: Dict[str, int] = field(default_factory=dict)  # date -> count
    weekly_completions: Dict[str, int] = field(default_factory=dict)  # week -> count
    monthly_completions: Dict[str, int] = field(default_factory=dict)  # month -> count
    average_completion_time: float = 0.0  # in minutes
    fastest_completion: Optional[datetime] = None
    slowest_completion: Optional[datetime] = None
    completion_streak: int = 0  # consecutive days with completions
    longest_streak: int = 0
    preferred_planets: List[str] = field(default_factory=list)
    preferred_categories: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'daily_completions': self.daily_completions,
            'weekly_completions': self.weekly_completions,
            'monthly_completions': self.monthly_completions,
            'average_completion_time': self.average_completion_time,
            'fastest_completion': self.fastest_completion.isoformat() if self.fastest_completion else None,
            'slowest_completion': self.slowest_completion.isoformat() if self.slowest_completion else None,
            'completion_streak': self.completion_streak,
            'longest_streak': self.longest_streak,
            'preferred_planets': self.preferred_planets,
            'preferred_categories': self.preferred_categories
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompletionStats':
        """Create from dictionary."""
        return cls(
            daily_completions=data.get('daily_completions', {}),
            weekly_completions=data.get('weekly_completions', {}),
            monthly_completions=data.get('monthly_completions', {}),
            average_completion_time=data.get('average_completion_time', 0.0),
            fastest_completion=datetime.fromisoformat(data['fastest_completion']) if data.get('fastest_completion') else None,
            slowest_completion=datetime.fromisoformat(data['slowest_completion']) if data.get('slowest_completion') else None,
            completion_streak=data.get('completion_streak', 0),
            longest_streak=data.get('longest_streak', 0),
            preferred_planets=data.get('preferred_planets', []),
            preferred_categories=data.get('preferred_categories', [])
        )


class ProgressTracker:
    """Tracks progress and provides completion statistics."""
    
    def __init__(self, progress_file: str = "data/progress_tracker.json"):
        """Initialize ProgressTracker with progress file."""
        self.progress_file = Path(progress_file)
        self.progress_data = ProgressData()
        self.completion_stats = CompletionStats()
        self.completion_history: List[Dict[str, Any]] = []
        self._load_progress_data()
    
    def _load_progress_data(self):
        """Load progress data from JSON file."""
        if not self.progress_file.exists():
            logger.info(f"Progress file {self.progress_file} does not exist, starting fresh")
            return
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.progress_data = ProgressData.from_dict(data.get('progress_data', {}))
            self.completion_stats = CompletionStats.from_dict(data.get('completion_stats', {}))
            self.completion_history = data.get('completion_history', [])
            
            logger.info(f"Loaded progress data from {self.progress_file}")
            
        except Exception as e:
            logger.error(f"Error loading progress data from {self.progress_file}: {e}")
    
    def _save_progress_data(self):
        """Save progress data to JSON file."""
        try:
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'progress_data': self.progress_data.to_dict(),
                'completion_stats': self.completion_stats.to_dict(),
                'completion_history': self.completion_history,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved progress data to {self.progress_file}")
            
        except Exception as e:
            logger.error(f"Error saving progress data to {self.progress_file}: {e}")
    
    def update_progress(self, quests: List[QuestData], todos: List[TodoItem]):
        """Update progress based on current quests and todos."""
        all_items = quests + todos
        
        self.progress_data.total_items = len(all_items)
        self.progress_data.completed_items = len([item for item in all_items if item.status == QuestStatus.COMPLETED])
        self.progress_data.in_progress_items = len([item for item in all_items if item.status == QuestStatus.IN_PROGRESS])
        self.progress_data.not_started_items = len([item for item in all_items if item.status == QuestStatus.NOT_STARTED])
        self.progress_data.skipped_items = len([item for item in all_items if item.status == QuestStatus.SKIPPED])
        self.progress_data.failed_items = len([item for item in all_items if item.status == QuestStatus.FAILED])
        
        if self.progress_data.total_items > 0:
            self.progress_data.completion_percentage = (
                self.progress_data.completed_items / self.progress_data.total_items
            ) * 100
        
        # Update rewards
        self.progress_data.xp_gained = sum(item.xp_reward for item in quests if item.status == QuestStatus.COMPLETED)
        self.progress_data.credits_gained = sum(item.credit_reward for item in quests if item.status == QuestStatus.COMPLETED)
        
        # Update planets visited
        planets = set()
        for item in all_items:
            if hasattr(item, 'planet') and item.planet:
                planets.add(item.planet)
        self.progress_data.planets_visited = list(planets)
        
        # Update categories completed
        category_counts = {}
        for todo in todos:
            if todo.status == QuestStatus.COMPLETED:
                category = todo.category.value
                category_counts[category] = category_counts.get(category, 0) + 1
        self.progress_data.categories_completed = category_counts
        
        self.progress_data.last_updated = datetime.now()
        self._save_progress_data()
    
    def record_completion(self, item_id: str, item_type: str, completion_time: Optional[int] = None,
                         planet: Optional[str] = None, category: Optional[str] = None):
        """Record a completion event."""
        completion_event = {
            'item_id': item_id,
            'item_type': item_type,
            'completion_date': datetime.now().isoformat(),
            'completion_time': completion_time,
            'planet': planet,
            'category': category
        }
        
        self.completion_history.append(completion_event)
        
        # Update daily/weekly/monthly stats
        today = datetime.now().strftime('%Y-%m-%d')
        week = datetime.now().strftime('%Y-W%U')
        month = datetime.now().strftime('%Y-%m')
        
        self.completion_stats.daily_completions[today] = self.completion_stats.daily_completions.get(today, 0) + 1
        self.completion_stats.weekly_completions[week] = self.completion_stats.weekly_completions.get(week, 0) + 1
        self.completion_stats.monthly_completions[month] = self.completion_stats.monthly_completions.get(month, 0) + 1
        
        # Update completion streak
        self._update_completion_streak()
        
        # Update preferred planets/categories
        if planet:
            self._update_preferred_planets(planet)
        if category:
            self._update_preferred_categories(category)
        
        self._save_progress_data()
        logger.info(f"Recorded completion: {item_type} {item_id}")
    
    def _update_completion_streak(self):
        """Update completion streak based on daily completions."""
        today = datetime.now()
        streak = 0
        current_date = today
        
        while True:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str in self.completion_stats.daily_completions:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        self.completion_stats.completion_streak = streak
        if streak > self.completion_stats.longest_streak:
            self.completion_stats.longest_streak = streak
    
    def _update_preferred_planets(self, planet: str):
        """Update preferred planets list."""
        if planet not in self.completion_stats.preferred_planets:
            self.completion_stats.preferred_planets.append(planet)
    
    def _update_preferred_categories(self, category: str):
        """Update preferred categories list."""
        if category not in self.completion_stats.preferred_categories:
            self.completion_stats.preferred_categories.append(category)
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get a summary of current progress."""
        return {
            'total_items': self.progress_data.total_items,
            'completed_items': self.progress_data.completed_items,
            'completion_percentage': self.progress_data.completion_percentage,
            'xp_gained': self.progress_data.xp_gained,
            'credits_gained': self.progress_data.credits_gained,
            'planets_visited': len(self.progress_data.planets_visited),
            'completion_streak': self.completion_stats.completion_streak,
            'longest_streak': self.completion_stats.longest_streak,
            'last_updated': self.progress_data.last_updated.isoformat()
        }
    
    def get_completion_trends(self, days: int = 30) -> Dict[str, List[Tuple[str, int]]]:
        """Get completion trends over the specified number of days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        daily_trend = []
        weekly_trend = []
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            week_str = current_date.strftime('%Y-W%U')
            
            daily_count = self.completion_stats.daily_completions.get(date_str, 0)
            daily_trend.append((date_str, daily_count))
            
            if current_date.weekday() == 6:  # Sunday
                weekly_count = self.completion_stats.weekly_completions.get(week_str, 0)
                weekly_trend.append((week_str, weekly_count))
            
            current_date += timedelta(days=1)
        
        return {
            'daily': daily_trend,
            'weekly': weekly_trend
        }
    
    def get_planet_progress(self) -> Dict[str, Dict[str, Any]]:
        """Get progress breakdown by planet."""
        planet_progress = {}
        
        for planet in self.progress_data.planets_visited:
            planet_progress[planet] = {
                'total_quests': 0,
                'completed_quests': 0,
                'completion_percentage': 0.0
            }
        
        return planet_progress
    
    def get_category_progress(self) -> Dict[str, Dict[str, Any]]:
        """Get progress breakdown by category."""
        return self.progress_data.categories_completed
    
    def get_completion_rate(self, period: str = 'daily') -> float:
        """Get average completion rate for the specified period."""
        if period == 'daily':
            completions = self.completion_stats.daily_completions.values()
        elif period == 'weekly':
            completions = self.completion_stats.weekly_completions.values()
        elif period == 'monthly':
            completions = self.completion_stats.monthly_completions.values()
        else:
            return 0.0
        
        if not completions:
            return 0.0
        
        return sum(completions) / len(completions)
    
    def get_recent_completions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent completion events."""
        return sorted(
            self.completion_history,
            key=lambda x: x['completion_date'],
            reverse=True
        )[:limit]
    
    def export_progress_report(self, output_file: str):
        """Export a comprehensive progress report."""
        report = {
            'progress_summary': self.get_progress_summary(),
            'completion_trends': self.get_completion_trends(),
            'planet_progress': self.get_planet_progress(),
            'category_progress': self.get_category_progress(),
            'recent_completions': self.get_recent_completions(),
            'completion_stats': self.completion_stats.to_dict(),
            'export_date': datetime.now().isoformat()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported progress report to {output_file}")
    
    def reset_progress(self):
        """Reset all progress data."""
        self.progress_data = ProgressData()
        self.completion_stats = CompletionStats()
        self.completion_history = []
        self._save_progress_data()
        logger.info("Reset all progress data") 
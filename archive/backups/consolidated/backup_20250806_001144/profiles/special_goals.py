"""
Special Goals Profile Manager

This module provides high-level management of special goals including:
- Goal prioritization and selection
- Milestone tracking and progress monitoring
- Dashboard integration for goal display
- Active goal management and scheduling
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from core.special_goals import (
    SpecialGoals, get_special_goals, GoalType, GoalStatus, 
    GoalPriority, SpecialGoal, GoalProgress
)


@dataclass
class GoalMilestone:
    """Represents a milestone within a special goal."""
    name: str
    description: str
    requirement_type: str
    target_value: Any
    current_value: Any = None
    completed: bool = False
    completion_time: Optional[datetime] = None


@dataclass
class ActiveGoalSession:
    """Tracks an active goal session with milestones."""
    goal_name: str
    start_time: datetime
    current_milestone: Optional[str] = None
    milestones_completed: int = 0
    total_milestones: int = 0
    estimated_completion: Optional[datetime] = None
    last_activity: Optional[datetime] = None


class SpecialGoalsManager:
    """Manages special goals with prioritization and milestone tracking."""
    
    def __init__(self):
        self.special_goals = get_special_goals()
        self.active_session: Optional[ActiveGoalSession] = None
        self.milestone_cache: Dict[str, List[GoalMilestone]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Load existing goals and initialize
        self.special_goals.load_goals()
        self._initialize_milestones()
    
    def _initialize_milestones(self):
        """Initialize milestone tracking for all goals."""
        for goal_name, goal in self.special_goals.goals.items():
            milestones = []
            for i, requirement in enumerate(goal.requirements):
                milestone = GoalMilestone(
                    name=f"Step {i+1}: {requirement.description}",
                    description=requirement.description,
                    requirement_type=requirement.type,
                    target_value=requirement.required_progress,
                    current_value=requirement.current_progress
                )
                milestones.append(milestone)
            
            self.milestone_cache[goal_name] = milestones
    
    def get_prioritized_goals(self, max_goals: int = 5) -> List[SpecialGoal]:
        """Get goals prioritized by importance and readiness."""
        available_goals = self.special_goals.get_available_goals()
        
        # Score goals based on priority and readiness
        scored_goals = []
        for goal in available_goals:
            score = self._calculate_goal_score(goal)
            scored_goals.append((score, goal))
        
        # Sort by score (highest first) and return top goals
        scored_goals.sort(key=lambda x: x[0], reverse=True)
        return [goal for score, goal in scored_goals[:max_goals]]
    
    def _calculate_goal_score(self, goal: SpecialGoal) -> float:
        """Calculate a score for goal prioritization."""
        score = 0.0
        
        # Priority scoring
        priority_scores = {
            GoalPriority.CRITICAL: 100,
            GoalPriority.HIGH: 80,
            GoalPriority.MEDIUM: 60,
            GoalPriority.LOW: 40
        }
        score += priority_scores.get(goal.priority, 50)
        
        # Readiness scoring (how close to completion)
        requirements_met = 0
        total_requirements = len(goal.requirements)
        
        for requirement in goal.requirements:
            if self._check_requirement_readiness(requirement):
                requirements_met += 1
        
        readiness_ratio = requirements_met / total_requirements if total_requirements > 0 else 0
        score += readiness_ratio * 50  # Up to 50 points for readiness
        
        # Time efficiency (shorter goals get slight bonus)
        if goal.estimated_time_hours:
            time_bonus = max(0, 10 - goal.estimated_time_hours / 2)
            score += time_bonus
        
        return score
    
    def _check_requirement_readiness(self, requirement) -> bool:
        """Check if a requirement is ready to be worked on."""
        # This would integrate with the game state to check current progress
        # For now, return True for demonstration
        return True
    
    def start_goal_session(self, goal_name: str) -> bool:
        """Start working on a specific goal."""
        if goal_name not in self.special_goals.goals:
            self.logger.error(f"Goal '{goal_name}' not found")
            return False
        
        goal = self.special_goals.goals[goal_name]
        
        # Check if goal can be started
        if not self.special_goals.start_goal(goal_name):
            self.logger.error(f"Failed to start goal '{goal_name}'")
            return False
        
        # Create active session
        milestones = self.milestone_cache.get(goal_name, [])
        self.active_session = ActiveGoalSession(
            goal_name=goal_name,
            start_time=datetime.now(),
            total_milestones=len(milestones),
            last_activity=datetime.now()
        )
        
        self.logger.info(f"Started goal session for '{goal_name}'")
        return True
    
    def get_current_goal_status(self) -> Dict[str, Any]:
        """Get detailed status of the currently active goal."""
        if not self.active_session:
            return {"active": False}
        
        goal_name = self.active_session.goal_name
        goal = self.special_goals.goals.get(goal_name)
        progress = self.special_goals.progress.get(goal_name)
        milestones = self.milestone_cache.get(goal_name, [])
        
        if not goal or not progress:
            return {"active": False, "error": "Goal data not found"}
        
        # Calculate milestone progress
        completed_milestones = sum(1 for m in milestones if m.completed)
        current_milestone = None
        for milestone in milestones:
            if not milestone.completed:
                current_milestone = milestone
                break
        
        # Estimate completion time
        estimated_completion = None
        if self.active_session.start_time and goal.estimated_time_hours:
            estimated_completion = (
                self.active_session.start_time + 
                timedelta(hours=goal.estimated_time_hours)
            )
        
        return {
            "active": True,
            "goal_name": goal_name,
            "goal_type": goal.goal_type.value,
            "description": goal.description,
            "priority": goal.priority.value,
            "planet": goal.planet,
            "zone": goal.zone,
            "status": progress.status.value,
            "milestones_completed": completed_milestones,
            "total_milestones": len(milestones),
            "current_milestone": current_milestone.name if current_milestone else None,
            "progress_percentage": (completed_milestones / len(milestones) * 100) if milestones else 0,
            "start_time": self.active_session.start_time.isoformat(),
            "estimated_completion": estimated_completion.isoformat() if estimated_completion else None,
            "last_activity": self.active_session.last_activity.isoformat() if self.active_session.last_activity else None,
            "rewards": goal.rewards,
            "milestones": [
                {
                    "name": m.name,
                    "description": m.description,
                    "requirement_type": m.requirement_type,
                    "completed": m.completed,
                    "target_value": m.target_value,
                    "current_value": m.current_value
                }
                for m in milestones
            ]
        }
    
    def update_milestone_progress(self, milestone_name: str, current_value: Any) -> bool:
        """Update progress for a specific milestone."""
        if not self.active_session:
            return False
        
        goal_name = self.active_session.goal_name
        milestones = self.milestone_cache.get(goal_name, [])
        
        for milestone in milestones:
            if milestone.name == milestone_name:
                milestone.current_value = current_value
                
                # Check if milestone is completed
                if self._is_milestone_completed(milestone):
                    milestone.completed = True
                    milestone.completion_time = datetime.now()
                    self.active_session.milestones_completed += 1
                    self.active_session.last_activity = datetime.now()
                    
                    self.logger.info(f"Completed milestone: {milestone_name}")
                    
                    # Check if entire goal is completed
                    if self.active_session.milestones_completed >= self.active_session.total_milestones:
                        self._complete_goal_session()
                
                return True
        
        return False
    
    def _is_milestone_completed(self, milestone: GoalMilestone) -> bool:
        """Check if a milestone is completed based on its type."""
        if milestone.current_value is None:
            return False
        
        if milestone.requirement_type == "level":
            return milestone.current_value >= milestone.target_value
        elif milestone.requirement_type == "reputation":
            return milestone.current_value >= milestone.target_value
        elif milestone.requirement_type == "quest":
            return milestone.current_value == "completed"
        elif milestone.requirement_type == "skill":
            return milestone.current_value == milestone.target_value
        elif milestone.requirement_type == "collection":
            return milestone.current_value == "completed"
        
        return False
    
    def _complete_goal_session(self):
        """Complete the current goal session."""
        if not self.active_session:
            return
        
        goal_name = self.active_session.goal_name
        
        # Complete the goal in the special goals system
        self.special_goals._complete_goal(goal_name)
        
        self.logger.info(f"Completed goal session: {goal_name}")
        
        # Clear active session
        self.active_session = None
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for dashboard display."""
        current_status = self.get_current_goal_status()
        
        # Get top prioritized goals
        prioritized_goals = self.get_prioritized_goals(max_goals=3)
        
        # Get overall statistics
        all_goals = self.special_goals.list_goals()
        completed_goals = [g for g in all_goals if self.special_goals.progress.get(g.name) and self.special_goals.progress[g.name].status == GoalStatus.COMPLETED]
        
        return {
            "current_goal": current_status,
            "prioritized_goals": [
                {
                    "name": goal.name,
                    "type": goal.goal_type.value,
                    "priority": goal.priority.value,
                    "description": goal.description,
                    "planet": goal.planet,
                    "estimated_time": goal.estimated_time_hours
                }
                for goal in prioritized_goals
            ],
            "statistics": {
                "total_goals": len(all_goals),
                "completed_goals": len(completed_goals),
                "completion_rate": (len(completed_goals) / len(all_goals) * 100) if all_goals else 0
            }
        }
    
    def save_session_data(self):
        """Save current session data to file."""
        if not self.active_session:
            return
        
        session_data = {
            "active_session": asdict(self.active_session) if self.active_session else None,
            "milestone_cache": {
                goal_name: [asdict(m) for m in milestones]
                for goal_name, milestones in self.milestone_cache.items()
            },
            "last_updated": datetime.now().isoformat()
        }
        
        session_file = Path("data/special_goals_session.json")
        session_file.parent.mkdir(exist_ok=True)
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
    
    def load_session_data(self):
        """Load session data from file."""
        session_file = Path("data/special_goals_session.json")
        
        if not session_file.exists():
            return
        
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
            
            # Restore active session
            if data.get("active_session"):
                session_data = data["active_session"]
                self.active_session = ActiveGoalSession(
                    goal_name=session_data["goal_name"],
                    start_time=datetime.fromisoformat(session_data["start_time"]),
                    current_milestone=session_data.get("current_milestone"),
                    milestones_completed=session_data.get("milestones_completed", 0),
                    total_milestones=session_data.get("total_milestones", 0),
                    estimated_completion=datetime.fromisoformat(session_data["estimated_completion"]) if session_data.get("estimated_completion") else None,
                    last_activity=datetime.fromisoformat(session_data["last_activity"]) if session_data.get("last_activity") else None
                )
            
            # Restore milestone cache
            if data.get("milestone_cache"):
                for goal_name, milestones_data in data["milestone_cache"].items():
                    milestones = []
                    for m_data in milestones_data:
                        milestone = GoalMilestone(
                            name=m_data["name"],
                            description=m_data["description"],
                            requirement_type=m_data["requirement_type"],
                            target_value=m_data["target_value"],
                            current_value=m_data.get("current_value"),
                            completed=m_data.get("completed", False),
                            completion_time=datetime.fromisoformat(m_data["completion_time"]) if m_data.get("completion_time") else None
                        )
                        milestones.append(milestone)
                    self.milestone_cache[goal_name] = milestones
        
        except Exception as e:
            self.logger.error(f"Failed to load session data: {e}")


# Global instance
_special_goals_manager: Optional[SpecialGoalsManager] = None


def get_special_goals_manager() -> SpecialGoalsManager:
    """Get the global special goals manager instance."""
    global _special_goals_manager
    if _special_goals_manager is None:
        _special_goals_manager = SpecialGoalsManager()
        _special_goals_manager.load_session_data()
    return _special_goals_manager


def start_goal_session(goal_name: str) -> bool:
    """Start a goal session."""
    manager = get_special_goals_manager()
    return manager.start_goal_session(goal_name)


def get_current_goal_status() -> Dict[str, Any]:
    """Get current goal status for dashboard."""
    manager = get_special_goals_manager()
    return manager.get_current_goal_status()


def get_dashboard_data() -> Dict[str, Any]:
    """Get dashboard data for special goals."""
    manager = get_special_goals_manager()
    return manager.get_dashboard_data()


def update_milestone_progress(milestone_name: str, current_value: Any) -> bool:
    """Update milestone progress."""
    manager = get_special_goals_manager()
    return manager.update_milestone_progress(milestone_name, current_value)


def get_prioritized_goals(max_goals: int = 5) -> List[SpecialGoal]:
    """Get prioritized goals."""
    manager = get_special_goals_manager()
    return manager.get_prioritized_goals(max_goals) 
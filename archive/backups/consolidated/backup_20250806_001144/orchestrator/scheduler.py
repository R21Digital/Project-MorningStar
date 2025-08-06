"""Fleet Scheduler for Multi-Client Orchestration.

This module manages task scheduling across multiple SWG client agents,
including daily/weekly caps, anti-pattern detection, and idle block management.
"""

import json
import logging
import threading
import time
from datetime import datetime, timedelta, time as dt_time
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import random

from .agent_registry import AgentRegistry, Agent, AgentCapability, AgentStatus

# Configure logging
logger = logging.getLogger(__name__)

class SchedulePriority(Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    MAINTENANCE = "maintenance"

class ScheduleStatus(Enum):
    """Task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class ScheduleConstraint(Enum):
    """Schedule constraints."""
    DAILY_CAP = "daily_cap"
    WEEKLY_CAP = "weekly_cap"
    TIME_WINDOW = "time_window"
    AGENT_CAPABILITY = "agent_capability"
    ANTI_PATTERN = "anti_pattern"
    COOLDOWN = "cooldown"
    DEPENDENCY = "dependency"

@dataclass
class ScheduleWindow:
    """Time window for scheduling."""
    start_time: dt_time
    end_time: dt_time
    days_of_week: Set[int]  # 0=Monday, 6=Sunday
    priority_boost: float = 1.0

@dataclass
class ScheduleTask:
    """Represents a scheduled task."""
    id: str
    name: str
    mode: str
    agent_name: Optional[str]
    priority: SchedulePriority
    status: ScheduleStatus
    created_at: datetime
    scheduled_for: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_duration: timedelta
    actual_duration: Optional[timedelta]
    constraints: Dict[ScheduleConstraint, Any]
    anti_pattern_rules: List[Dict[str, Any]]
    daily_cap: Optional[int]
    weekly_cap: Optional[int]
    current_daily_count: int
    current_weekly_count: int
    error_count: int
    last_error: Optional[str]
    metadata: Dict[str, Any]

class FleetScheduler:
    """Central scheduler for managing tasks across multiple agents."""
    
    def __init__(self, schedule_file: str = "data/fleet_schedule.json"):
        self.schedule_file = Path(schedule_file)
        self.tasks: Dict[str, ScheduleTask] = {}
        self.agent_registry = AgentRegistry()
        self.lock = threading.RLock()
        
        # Anti-pattern detection
        self.anti_patterns: Dict[str, Dict[str, Any]] = {}
        self.pattern_history: List[Dict[str, Any]] = []
        
        # Schedule windows
        self.schedule_windows: Dict[str, ScheduleWindow] = {}
        
        # Ensure data directory exists
        self.schedule_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing schedule
        self._load_schedule()
        
        # Start scheduler thread
        self._start_scheduler()
    
    def _load_schedule(self):
        """Load schedule from file."""
        try:
            if self.schedule_file.exists():
                with open(self.schedule_file, 'r') as f:
                    data = json.load(f)
                    for task_data in data.get('tasks', []):
                        task = self._deserialize_task(task_data)
                        self.tasks[task.id] = task
                    
                    # Load anti-patterns
                    self.anti_patterns = data.get('anti_patterns', {})
                    
                    # Load schedule windows
                    windows_data = data.get('schedule_windows', {})
                    for name, window_data in windows_data.items():
                        self.schedule_windows[name] = self._deserialize_window(window_data)
                
                logger.info(f"Loaded {len(self.tasks)} tasks from schedule")
        except Exception as e:
            logger.error(f"Failed to load schedule: {e}")
    
    def _save_schedule(self):
        """Save schedule to file."""
        try:
            with self.lock:
                data = {
                    'tasks': [self._serialize_task(task) for task in self.tasks.values()],
                    'anti_patterns': self.anti_patterns,
                    'schedule_windows': {
                        name: self._serialize_window(window)
                        for name, window in self.schedule_windows.items()
                    },
                    'last_updated': datetime.now().isoformat()
                }
                with open(self.schedule_file, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save schedule: {e}")
    
    def _serialize_task(self, task: ScheduleTask) -> Dict[str, Any]:
        """Serialize task to dictionary."""
        data = asdict(task)
        data['priority'] = task.priority.value
        data['status'] = task.status.value
        data['constraints'] = {k.value: v for k, v in task.constraints.items()}
        return data
    
    def _deserialize_task(self, data: Dict[str, Any]) -> ScheduleTask:
        """Deserialize task from dictionary."""
        data['priority'] = SchedulePriority(data['priority'])
        data['status'] = ScheduleStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['scheduled_for'] = datetime.fromisoformat(data['scheduled_for'])
        if data['started_at']:
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data['completed_at']:
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        data['estimated_duration'] = timedelta(seconds=data['estimated_duration'])
        if data['actual_duration']:
            data['actual_duration'] = timedelta(seconds=data['actual_duration'])
        data['constraints'] = {ScheduleConstraint(k): v for k, v in data['constraints'].items()}
        return ScheduleTask(**data)
    
    def _serialize_window(self, window: ScheduleWindow) -> Dict[str, Any]:
        """Serialize schedule window to dictionary."""
        return {
            'start_time': window.start_time.isoformat(),
            'end_time': window.end_time.isoformat(),
            'days_of_week': list(window.days_of_week),
            'priority_boost': window.priority_boost
        }
    
    def _deserialize_window(self, data: Dict[str, Any]) -> ScheduleWindow:
        """Deserialize schedule window from dictionary."""
        return ScheduleWindow(
            start_time=dt_time.fromisoformat(data['start_time']),
            end_time=dt_time.fromisoformat(data['end_time']),
            days_of_week=set(data['days_of_week']),
            priority_boost=data.get('priority_boost', 1.0)
        )
    
    def create_task(self, name: str, mode: str, agent_name: Optional[str] = None,
                   priority: SchedulePriority = SchedulePriority.NORMAL,
                   scheduled_for: Optional[datetime] = None,
                   estimated_duration: timedelta = timedelta(hours=1),
                   constraints: Optional[Dict[ScheduleConstraint, Any]] = None,
                   anti_pattern_rules: Optional[List[Dict[str, Any]]] = None,
                   daily_cap: Optional[int] = None,
                   weekly_cap: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> ScheduleTask:
        """Create a new scheduled task."""
        with self.lock:
            task_id = f"{name}_{int(time.time())}_{random.randint(1000, 9999)}"
            
            if scheduled_for is None:
                scheduled_for = datetime.now()
            
            task = ScheduleTask(
                id=task_id,
                name=name,
                mode=mode,
                agent_name=agent_name,
                priority=priority,
                status=ScheduleStatus.PENDING,
                created_at=datetime.now(),
                scheduled_for=scheduled_for,
                started_at=None,
                completed_at=None,
                estimated_duration=estimated_duration,
                actual_duration=None,
                constraints=constraints or {},
                anti_pattern_rules=anti_pattern_rules or [],
                daily_cap=daily_cap,
                weekly_cap=weekly_cap,
                current_daily_count=0,
                current_weekly_count=0,
                error_count=0,
                last_error=None,
                metadata=metadata or {}
            )
            
            self.tasks[task_id] = task
            self._save_schedule()
            logger.info(f"Created task: {name} ({task_id})")
            return task
    
    def get_next_task(self, agent_name: Optional[str] = None) -> Optional[ScheduleTask]:
        """Get the next task to execute."""
        with self.lock:
            available_tasks = []
            
            for task in self.tasks.values():
                if task.status != ScheduleStatus.PENDING:
                    continue
                
                # Check if task is scheduled for now or past
                if task.scheduled_for > datetime.now():
                    continue
                
                # Check agent assignment
                if agent_name and task.agent_name and task.agent_name != agent_name:
                    continue
                
                # Check constraints
                if not self._validate_task_constraints(task):
                    continue
                
                # Check anti-patterns
                if self._check_anti_patterns(task):
                    continue
                
                available_tasks.append(task)
            
            if not available_tasks:
                return None
            
            # Sort by priority and scheduled time
            available_tasks.sort(
                key=lambda t: (t.priority.value, t.scheduled_for),
                reverse=True
            )
            
            return available_tasks[0]
    
    def start_task(self, task_id: str) -> bool:
        """Start a task execution."""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task or task.status != ScheduleStatus.PENDING:
                return False
            
            task.status = ScheduleStatus.RUNNING
            task.started_at = datetime.now()
            self._save_schedule()
            logger.info(f"Started task: {task.name} ({task_id})")
            return True
    
    def complete_task(self, task_id: str, success: bool = True, error_message: Optional[str] = None):
        """Complete a task execution."""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return
            
            task.completed_at = datetime.now()
            if task.started_at:
                task.actual_duration = task.completed_at - task.started_at
            
            if success:
                task.status = ScheduleStatus.COMPLETED
                task.current_daily_count += 1
                task.current_weekly_count += 1
            else:
                task.status = ScheduleStatus.FAILED
                task.error_count += 1
                task.last_error = error_message
            
            self._save_schedule()
            logger.info(f"Completed task: {task.name} ({task_id}) - {'SUCCESS' if success else 'FAILED'}")
    
    def _validate_task_constraints(self, task: ScheduleTask) -> bool:
        """Validate task constraints."""
        for constraint_type, constraint_value in task.constraints.items():
            if constraint_type == ScheduleConstraint.DAILY_CAP:
                if task.current_daily_count >= constraint_value:
                    return False
            
            elif constraint_type == ScheduleConstraint.WEEKLY_CAP:
                if task.current_weekly_count >= constraint_value:
                    return False
            
            elif constraint_type == ScheduleConstraint.TIME_WINDOW:
                current_time = datetime.now().time()
                window_name = constraint_value
                window = self.schedule_windows.get(window_name)
                if window:
                    if current_time < window.start_time or current_time > window.end_time:
                        return False
                    if datetime.now().weekday() not in window.days_of_week:
                        return False
            
            elif constraint_type == ScheduleConstraint.AGENT_CAPABILITY:
                required_capability = AgentCapability(constraint_value)
                if task.agent_name:
                    agent = self.agent_registry.get_agent(task.agent_name)
                    if not agent or required_capability not in agent.capabilities:
                        return False
        
        return True
    
    def _check_anti_patterns(self, task: ScheduleTask) -> bool:
        """Check for anti-patterns in task scheduling."""
        current_time = datetime.now()
        
        for rule in task.anti_pattern_rules:
            pattern_type = rule.get('type')
            
            if pattern_type == 'recent_failure':
                # Check if this task failed recently
                recent_failures = [
                    t for t in self.tasks.values()
                    if t.name == task.name and t.status == ScheduleStatus.FAILED
                    and (current_time - t.completed_at).total_seconds() < rule.get('timeout', 3600)
                ]
                if len(recent_failures) >= rule.get('max_failures', 3):
                    return True
            
            elif pattern_type == 'idle_block':
                # Check for idle time blocks
                idle_start = rule.get('idle_start')
                idle_end = rule.get('idle_end')
                if idle_start and idle_end:
                    current_time_of_day = current_time.time()
                    if idle_start <= current_time_of_day <= idle_end:
                        return True
            
            elif pattern_type == 'cooldown':
                # Check cooldown period
                cooldown_duration = rule.get('duration', 3600)
                last_completion = None
                for t in self.tasks.values():
                    if t.name == task.name and t.status == ScheduleStatus.COMPLETED:
                        if last_completion is None or t.completed_at > last_completion:
                            last_completion = t.completed_at
                
                if last_completion and (current_time - last_completion).total_seconds() < cooldown_duration:
                    return True
        
        return False
    
    def add_anti_pattern_rule(self, name: str, rule: Dict[str, Any]):
        """Add an anti-pattern rule."""
        with self.lock:
            self.anti_patterns[name] = rule
            self._save_schedule()
    
    def add_schedule_window(self, name: str, window: ScheduleWindow):
        """Add a schedule window."""
        with self.lock:
            self.schedule_windows[name] = window
            self._save_schedule()
    
    def get_schedule_summary(self) -> Dict[str, Any]:
        """Get schedule summary statistics."""
        with self.lock:
            total_tasks = len(self.tasks)
            pending_tasks = len([t for t in self.tasks.values() if t.status == ScheduleStatus.PENDING])
            running_tasks = len([t for t in self.tasks.values() if t.status == ScheduleStatus.RUNNING])
            completed_tasks = len([t for t in self.tasks.values() if t.status == ScheduleStatus.COMPLETED])
            failed_tasks = len([t for t in self.tasks.values() if t.status == ScheduleStatus.FAILED])
            
            return {
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks,
                'running_tasks': running_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'tasks_by_priority': {
                    priority.value: len([t for t in self.tasks.values() if t.priority == priority])
                    for priority in SchedulePriority
                },
                'tasks_by_status': {
                    status.value: len([t for t in self.tasks.values() if t.status == status])
                    for status in ScheduleStatus
                }
            }
    
    def _start_scheduler(self):
        """Start background scheduler thread."""
        def run_scheduler():
            while True:
                try:
                    # Check for tasks that need to be started
                    available_agents = self.agent_registry.get_agents_by_status(AgentStatus.ONLINE)
                    
                    for agent in available_agents:
                        next_task = self.get_next_task(agent.name)
                        if next_task:
                            if self.start_task(next_task.id):
                                # Update agent status
                                self.agent_registry.update_heartbeat(
                                    agent.name, 
                                    AgentStatus.BUSY,
                                    next_task.mode
                                )
                
                except Exception as e:
                    logger.error(f"Scheduler error: {e}")
                
                time.sleep(30)  # Check every 30 seconds
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

# Global scheduler instance
_scheduler: Optional[FleetScheduler] = None

def get_fleet_scheduler() -> FleetScheduler:
    """Get global fleet scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = FleetScheduler()
    return _scheduler

# Convenience functions
def create_schedule_task(name: str, mode: str, agent_name: Optional[str] = None,
                        priority: SchedulePriority = SchedulePriority.NORMAL,
                        scheduled_for: Optional[datetime] = None,
                        estimated_duration: timedelta = timedelta(hours=1),
                        constraints: Optional[Dict[ScheduleConstraint, Any]] = None,
                        anti_pattern_rules: Optional[List[Dict[str, Any]]] = None,
                        daily_cap: Optional[int] = None,
                        weekly_cap: Optional[int] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> ScheduleTask:
    """Create a new scheduled task."""
    return get_fleet_scheduler().create_task(
        name, mode, agent_name, priority, scheduled_for, estimated_duration,
        constraints, anti_pattern_rules, daily_cap, weekly_cap, metadata
    )

def get_next_scheduled_task(agent_name: Optional[str] = None) -> Optional[ScheduleTask]:
    """Get the next task to execute."""
    return get_fleet_scheduler().get_next_task(agent_name)

def update_task_status(task_id: str, status: ScheduleStatus, 
                      success: bool = True, error_message: Optional[str] = None):
    """Update task status."""
    scheduler = get_fleet_scheduler()
    if status == ScheduleStatus.RUNNING:
        scheduler.start_task(task_id)
    elif status in [ScheduleStatus.COMPLETED, ScheduleStatus.FAILED]:
        scheduler.complete_task(task_id, success, error_message)

def get_schedule_summary() -> Dict[str, Any]:
    """Get schedule summary."""
    return get_fleet_scheduler().get_schedule_summary()

def validate_schedule_constraints(task: ScheduleTask) -> bool:
    """Validate task constraints."""
    return get_fleet_scheduler()._validate_task_constraints(task)

def apply_anti_pattern_rules(task: ScheduleTask) -> bool:
    """Apply anti-pattern rules to task."""
    return get_fleet_scheduler()._check_anti_patterns(task) 
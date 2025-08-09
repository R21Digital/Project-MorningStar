"""
MS11 Multi-Character Orchestration System
Advanced coordination and management of multiple game characters with intelligent task distribution
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Tuple, Callable, Union, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
import threading
import uuid
import math
from concurrent.futures import ThreadPoolExecutor

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

try:
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from core.structured_logging import StructuredLogger
from core.observability_integration import get_observability_manager, trace_gaming_operation

# Initialize logger
logger = StructuredLogger("multi_character_orchestration")

class CharacterRole(Enum):
    """Roles characters can play in orchestration"""
    TANK = "tank"
    DPS = "dps"
    HEALER = "healer"
    SUPPORT = "support"
    CRAFTER = "crafter"
    TRADER = "trader"
    SCOUT = "scout"
    LEADER = "leader"
    FOLLOWER = "follower"

class TaskType(Enum):
    """Types of tasks in orchestration"""
    COMBAT = "combat"
    QUEST = "quest"
    CRAFTING = "crafting"
    TRADING = "trading"
    FARMING = "farming"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    MAINTENANCE = "maintenance"
    TRANSPORT = "transport"
    COORDINATION = "coordination"

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"      # Must be done immediately
    HIGH = "high"             # Important, do soon
    MEDIUM = "medium"         # Normal priority
    LOW = "low"              # Do when available
    BACKGROUND = "background" # Fill time when nothing else

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class OrchestrationStrategy(Enum):
    """Coordination strategies"""
    LEADER_FOLLOWER = "leader_follower"    # One leader, others follow
    DISTRIBUTED = "distributed"           # Autonomous coordination
    HIERARCHICAL = "hierarchical"         # Chain of command
    COLLABORATIVE = "collaborative"       # Equal partnership
    SPECIALIZED = "specialized"           # Role-based assignments

@dataclass
class CharacterState:
    """Current state of a character"""
    character_id: str
    name: str
    level: int
    location: Tuple[float, float, float]  # x, y, z coordinates
    zone: str
    health_percentage: float
    mana_percentage: float
    stamina_percentage: float
    equipment_durability: float
    inventory_space: float  # Percentage free
    active_buffs: List[str]
    active_debuffs: List[str]
    current_target: Optional[str]
    in_combat: bool
    role: CharacterRole
    specializations: List[str]
    capabilities: Dict[str, float]  # Capability scores 0-1
    last_update: datetime
    status: str = "idle"
    current_task_id: Optional[str] = None

@dataclass
class OrchestrationTask:
    """Task in the orchestration system"""
    task_id: str
    task_type: TaskType
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    requirements: Dict[str, Any]
    estimated_duration: timedelta
    assigned_characters: List[str]
    dependencies: List[str]
    location: Optional[Tuple[float, float, float]]
    zone: Optional[str]
    rewards: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    failure_reason: Optional[str]
    progress_percentage: float = 0.0
    subtasks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GroupFormation:
    """Formation/positioning for group coordination"""
    formation_id: str
    name: str
    formation_type: str  # "line", "circle", "wedge", "box", "custom"
    positions: Dict[str, Tuple[float, float]]  # character_id -> relative position
    center_position: Tuple[float, float]
    rotation: float  # Formation rotation in degrees
    scale: float = 1.0
    adaptive: bool = True

@dataclass
class CoordinationRule:
    """Rules for character coordination"""
    rule_id: str
    name: str
    condition: str
    action: str
    priority: int
    enabled: bool
    characters: List[str]  # Empty = applies to all
    metadata: Dict[str, Any] = field(default_factory=dict)

class TaskScheduler:
    """Advanced task scheduling and assignment"""
    
    def __init__(self):
        self.pending_tasks: Dict[str, OrchestrationTask] = {}
        self.active_tasks: Dict[str, OrchestrationTask] = {}
        self.completed_tasks: deque = deque(maxlen=1000)
        self.task_dependencies = None
        
        if NETWORKX_AVAILABLE:
            self.task_dependencies = nx.DiGraph()
    
    def add_task(self, task: OrchestrationTask):
        """Add task to scheduler"""
        try:
            self.pending_tasks[task.task_id] = task
            
            # Add to dependency graph
            if self.task_dependencies is not None:
                self.task_dependencies.add_node(task.task_id, task=task)
                
                # Add dependency edges
                for dep_id in task.dependencies:
                    if dep_id in self.pending_tasks or dep_id in self.active_tasks:
                        self.task_dependencies.add_edge(dep_id, task.task_id)
            
            logger.debug("Task added to scheduler", task_id=task.task_id, type=task.task_type.value)
            
        except Exception as e:
            logger.error("Failed to add task", task_id=task.task_id, error=str(e))
    
    def get_ready_tasks(self) -> List[OrchestrationTask]:
        """Get tasks ready for assignment (dependencies satisfied)"""
        ready_tasks = []
        
        try:
            for task in self.pending_tasks.values():
                if self._are_dependencies_satisfied(task):
                    ready_tasks.append(task)
            
            # Sort by priority and creation time
            ready_tasks.sort(key=lambda t: (
                self._priority_weight(t.priority),
                t.created_at
            ))
            
        except Exception as e:
            logger.error("Error getting ready tasks", error=str(e))
        
        return ready_tasks
    
    def _are_dependencies_satisfied(self, task: OrchestrationTask) -> bool:
        """Check if task dependencies are satisfied"""
        try:
            for dep_id in task.dependencies:
                # Check if dependency is completed
                if dep_id in self.pending_tasks or dep_id in self.active_tasks:
                    return False
            
            return True
            
        except Exception as e:
            logger.error("Error checking dependencies", task_id=task.task_id, error=str(e))
            return False
    
    def _priority_weight(self, priority: TaskPriority) -> int:
        """Convert priority to numeric weight for sorting"""
        weights = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
            TaskPriority.BACKGROUND: 4
        }
        return weights.get(priority, 2)
    
    def assign_task(self, task: OrchestrationTask, characters: List[str]):
        """Assign task to characters"""
        try:
            task.assigned_characters = characters.copy()
            task.status = TaskStatus.ASSIGNED
            task.started_at = datetime.utcnow()
            
            # Move from pending to active
            if task.task_id in self.pending_tasks:
                del self.pending_tasks[task.task_id]
            
            self.active_tasks[task.task_id] = task
            
            logger.info("Task assigned",
                       task_id=task.task_id,
                       characters=characters,
                       type=task.task_type.value)
            
        except Exception as e:
            logger.error("Failed to assign task", task_id=task.task_id, error=str(e))
    
    def update_task_progress(self, task_id: str, progress: float, status: TaskStatus = None):
        """Update task progress"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.progress_percentage = max(0.0, min(100.0, progress))
                
                if status:
                    task.status = status
                
                # Handle completion
                if status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.utcnow()
                    self.completed_tasks.append(task)
                    del self.active_tasks[task_id]
                
                elif status in [TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    self.completed_tasks.append(task)
                    del self.active_tasks[task_id]
                
                logger.debug("Task progress updated",
                           task_id=task_id,
                           progress=progress,
                           status=status.value if status else None)
                
        except Exception as e:
            logger.error("Failed to update task progress", task_id=task_id, error=str(e))
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task scheduling statistics"""
        try:
            return {
                "pending_tasks": len(self.pending_tasks),
                "active_tasks": len(self.active_tasks),
                "completed_tasks": len(self.completed_tasks),
                "task_types": {
                    task_type.value: sum(1 for t in list(self.pending_tasks.values()) + list(self.active_tasks.values()) 
                                        if t.task_type == task_type)
                    for task_type in TaskType
                },
                "priorities": {
                    priority.value: sum(1 for t in list(self.pending_tasks.values()) + list(self.active_tasks.values()) 
                                      if t.priority == priority)
                    for priority in TaskPriority
                }
            }
            
        except Exception as e:
            logger.error("Error getting task statistics", error=str(e))
            return {}

class CharacterAssignmentEngine:
    """Intelligent character assignment to tasks"""
    
    def __init__(self):
        self.assignment_history: List[Dict[str, Any]] = []
        self.character_performance: Dict[str, Dict[TaskType, float]] = defaultdict(lambda: defaultdict(float))
        self.workload_balancing = True
        
    def find_best_assignment(self, 
                           task: OrchestrationTask,
                           available_characters: List[CharacterState]) -> List[str]:
        """Find best character assignment for task"""
        
        try:
            if not available_characters:
                return []
            
            # Determine required character count
            required_count = self._calculate_required_characters(task)
            required_count = min(required_count, len(available_characters))
            
            if required_count == 0:
                return []
            
            # Score characters for this task
            character_scores = []
            
            for char in available_characters:
                score = self._calculate_character_score(char, task)
                character_scores.append((char.character_id, score))
            
            # Sort by score (higher is better)
            character_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select best characters
            selected = []
            
            if required_count == 1:
                # Single character - pick best
                selected = [character_scores[0][0]]
                
            else:
                # Multiple characters - consider synergy
                selected = self._select_synergistic_group(
                    character_scores, 
                    available_characters,
                    task,
                    required_count
                )
            
            # Record assignment for learning
            self._record_assignment(task, selected, available_characters)
            
            return selected
            
        except Exception as e:
            logger.error("Error finding best assignment", task_id=task.task_id, error=str(e))
            return []
    
    def _calculate_required_characters(self, task: OrchestrationTask) -> int:
        """Calculate how many characters are needed for task"""
        try:
            # Base requirements by task type
            base_requirements = {
                TaskType.COMBAT: 1,
                TaskType.QUEST: 1,
                TaskType.CRAFTING: 1,
                TaskType.TRADING: 1,
                TaskType.FARMING: 1,
                TaskType.EXPLORATION: 1,
                TaskType.SOCIAL: 1,
                TaskType.MAINTENANCE: 1,
                TaskType.TRANSPORT: 1,
                TaskType.COORDINATION: 2
            }
            
            base_count = base_requirements.get(task.task_type, 1)
            
            # Adjust based on task requirements
            if "difficulty" in task.requirements:
                difficulty = task.requirements["difficulty"]
                if difficulty == "easy":
                    base_count = max(1, base_count - 1)
                elif difficulty == "hard":
                    base_count += 1
                elif difficulty == "extreme":
                    base_count += 2
            
            # Group content adjustments
            if task.requirements.get("group_content", False):
                base_count = max(base_count, 2)
            
            # Raid content
            if task.requirements.get("raid_content", False):
                base_count = max(base_count, 4)
            
            # Explicit character count requirement
            if "required_characters" in task.requirements:
                base_count = max(base_count, task.requirements["required_characters"])
            
            return base_count
            
        except Exception as e:
            logger.error("Error calculating required characters", error=str(e))
            return 1
    
    def _calculate_character_score(self, character: CharacterState, task: OrchestrationTask) -> float:
        """Calculate how well suited a character is for a task"""
        
        try:
            score = 0.0
            
            # Base suitability by role and task type
            role_scores = {
                (CharacterRole.TANK, TaskType.COMBAT): 0.9,
                (CharacterRole.DPS, TaskType.COMBAT): 0.8,
                (CharacterRole.HEALER, TaskType.COMBAT): 0.7,
                (CharacterRole.CRAFTER, TaskType.CRAFTING): 0.9,
                (CharacterRole.TRADER, TaskType.TRADING): 0.9,
                (CharacterRole.SCOUT, TaskType.EXPLORATION): 0.9,
                # Add more mappings as needed
            }
            
            base_score = role_scores.get((character.role, task.task_type), 0.5)
            score += base_score * 0.4
            
            # Character state factors
            state_score = (
                character.health_percentage +
                character.mana_percentage +
                character.stamina_percentage +
                character.equipment_durability +
                character.inventory_space
            ) / 5.0
            
            score += state_score * 0.2
            
            # Level appropriateness
            required_level = task.requirements.get("min_level", 1)
            if character.level >= required_level:
                level_bonus = min(0.2, (character.level - required_level) / 100.0)
                score += level_bonus
            else:
                score -= 0.3  # Penalty for being under-leveled
            
            # Location proximity bonus
            if task.location and character.location:
                distance = self._calculate_distance(character.location, task.location)
                proximity_bonus = max(0.0, 0.2 - (distance / 1000.0))  # Bonus decreases with distance
                score += proximity_bonus
            
            # Capability matching
            required_capabilities = task.requirements.get("capabilities", {})
            for capability, required_level in required_capabilities.items():
                char_level = character.capabilities.get(capability, 0.0)
                if char_level >= required_level:
                    score += 0.1
                else:
                    score -= 0.1
            
            # Historical performance
            historical_score = self.character_performance[character.character_id][task.task_type]
            score += historical_score * 0.1
            
            # Workload balancing
            if self.workload_balancing and character.current_task_id:
                score -= 0.2  # Penalty for already having a task
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error("Error calculating character score", error=str(e))
            return 0.0
    
    def _select_synergistic_group(self,
                                 character_scores: List[Tuple[str, float]],
                                 available_characters: List[CharacterState],
                                 task: OrchestrationTask,
                                 required_count: int) -> List[str]:
        """Select group of characters with good synergy"""
        
        try:
            # Create character lookup
            char_lookup = {char.character_id: char for char in available_characters}
            
            # Start with highest scoring character
            selected = [character_scores[0][0]]
            remaining_candidates = character_scores[1:]
            
            # Add characters that complement the group
            while len(selected) < required_count and remaining_candidates:
                best_candidate = None
                best_synergy_score = -1.0
                
                for char_id, individual_score in remaining_candidates:
                    # Calculate synergy with current group
                    synergy_score = self._calculate_group_synergy(
                        selected + [char_id], 
                        char_lookup, 
                        task
                    )
                    
                    combined_score = individual_score * 0.6 + synergy_score * 0.4
                    
                    if combined_score > best_synergy_score:
                        best_synergy_score = combined_score
                        best_candidate = char_id
                
                if best_candidate:
                    selected.append(best_candidate)
                    remaining_candidates = [(cid, score) for cid, score in remaining_candidates 
                                          if cid != best_candidate]
                else:
                    break
            
            return selected
            
        except Exception as e:
            logger.error("Error selecting synergistic group", error=str(e))
            return [character_scores[0][0]]  # Fallback to best individual
    
    def _calculate_group_synergy(self,
                               character_ids: List[str],
                               char_lookup: Dict[str, CharacterState],
                               task: OrchestrationTask) -> float:
        """Calculate synergy score for group of characters"""
        
        try:
            if len(character_ids) <= 1:
                return 0.5
            
            synergy_score = 0.0
            
            # Role diversity bonus
            roles = [char_lookup[cid].role for cid in character_ids]
            unique_roles = len(set(roles))
            role_diversity = unique_roles / len(character_ids)
            synergy_score += role_diversity * 0.3
            
            # Combat synergy for combat tasks
            if task.task_type == TaskType.COMBAT:
                has_tank = any(char_lookup[cid].role == CharacterRole.TANK for cid in character_ids)
                has_healer = any(char_lookup[cid].role == CharacterRole.HEALER for cid in character_ids)
                has_dps = any(char_lookup[cid].role == CharacterRole.DPS for cid in character_ids)
                
                if has_tank and has_healer and has_dps:
                    synergy_score += 0.4  # Classic trinity bonus
                elif has_tank and has_dps:
                    synergy_score += 0.2
                elif has_healer and has_dps:
                    synergy_score += 0.2
            
            # Level balance
            levels = [char_lookup[cid].level for cid in character_ids]
            level_variance = np.var(levels) if len(levels) > 1 else 0
            level_balance = max(0.0, 0.2 - (level_variance / 100.0))
            synergy_score += level_balance
            
            # Location clustering
            locations = [char_lookup[cid].location for cid in character_ids 
                        if char_lookup[cid].location]
            
            if len(locations) > 1:
                max_distance = 0
                for i, loc1 in enumerate(locations):
                    for loc2 in locations[i+1:]:
                        distance = self._calculate_distance(loc1, loc2)
                        max_distance = max(max_distance, distance)
                
                proximity_bonus = max(0.0, 0.1 - (max_distance / 5000.0))
                synergy_score += proximity_bonus
            
            return max(0.0, min(1.0, synergy_score))
            
        except Exception as e:
            logger.error("Error calculating group synergy", error=str(e))
            return 0.5
    
    def _calculate_distance(self, pos1: Tuple[float, float, float], pos2: Tuple[float, float, float]) -> float:
        """Calculate 3D distance between positions"""
        try:
            return math.sqrt(
                (pos1[0] - pos2[0]) ** 2 +
                (pos1[1] - pos2[1]) ** 2 +
                (pos1[2] - pos2[2]) ** 2
            )
        except Exception:
            return float('inf')
    
    def _record_assignment(self, task: OrchestrationTask, assigned: List[str], available: List[CharacterState]):
        """Record assignment for learning purposes"""
        try:
            self.assignment_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "task_id": task.task_id,
                "task_type": task.task_type.value,
                "assigned_characters": assigned.copy(),
                "available_characters": [c.character_id for c in available],
                "task_priority": task.priority.value
            })
            
            # Limit history size
            if len(self.assignment_history) > 1000:
                self.assignment_history = self.assignment_history[-1000:]
                
        except Exception as e:
            logger.error("Error recording assignment", error=str(e))
    
    def update_performance(self, character_id: str, task_type: TaskType, success: bool, efficiency: float = 1.0):
        """Update character performance tracking"""
        try:
            current_score = self.character_performance[character_id][task_type]
            
            # Calculate new performance score (weighted average)
            success_value = 1.0 if success else 0.0
            performance_value = success_value * efficiency
            
            # Update with exponential smoothing
            alpha = 0.2  # Learning rate
            new_score = (1 - alpha) * current_score + alpha * performance_value
            
            self.character_performance[character_id][task_type] = new_score
            
            logger.debug("Performance updated",
                        character_id=character_id,
                        task_type=task_type.value,
                        success=success,
                        new_score=new_score)
            
        except Exception as e:
            logger.error("Error updating performance", error=str(e))

class FormationManager:
    """Manage character formations and positioning"""
    
    def __init__(self):
        self.formations: Dict[str, GroupFormation] = {}
        self.active_formation: Optional[str] = None
        self.formation_templates = self._create_formation_templates()
    
    def _create_formation_templates(self) -> Dict[str, GroupFormation]:
        """Create standard formation templates"""
        templates = {}
        
        # Line formation
        templates["line"] = GroupFormation(
            formation_id="line",
            name="Line Formation",
            formation_type="line",
            positions={
                "char1": (0.0, 0.0),
                "char2": (2.0, 0.0),
                "char3": (4.0, 0.0),
                "char4": (6.0, 0.0)
            },
            center_position=(3.0, 0.0),
            rotation=0.0
        )
        
        # Wedge formation
        templates["wedge"] = GroupFormation(
            formation_id="wedge",
            name="Wedge Formation",
            formation_type="wedge",
            positions={
                "char1": (0.0, 0.0),   # Leader at front
                "char2": (-1.5, -2.0),
                "char3": (1.5, -2.0),
                "char4": (0.0, -4.0)
            },
            center_position=(0.0, -1.5),
            rotation=0.0
        )
        
        # Circle formation
        templates["circle"] = GroupFormation(
            formation_id="circle",
            name="Circle Formation",
            formation_type="circle",
            positions={
                "char1": (0.0, 2.0),
                "char2": (2.0, 0.0),
                "char3": (0.0, -2.0),
                "char4": (-2.0, 0.0)
            },
            center_position=(0.0, 0.0),
            rotation=0.0
        )
        
        # Box formation
        templates["box"] = GroupFormation(
            formation_id="box",
            name="Box Formation",
            formation_type="box",
            positions={
                "char1": (-1.0, 1.0),
                "char2": (1.0, 1.0),
                "char3": (-1.0, -1.0),
                "char4": (1.0, -1.0)
            },
            center_position=(0.0, 0.0),
            rotation=0.0
        )
        
        return templates
    
    def create_formation(self, character_ids: List[str], formation_type: str = "line") -> str:
        """Create formation for group of characters"""
        try:
            # Get formation template
            if formation_type in self.formation_templates:
                template = self.formation_templates[formation_type]
            else:
                template = self.formation_templates["line"]
            
            # Create new formation with assigned characters
            formation_id = f"formation_{int(time.time())}"
            
            # Assign characters to positions
            positions = {}
            for i, char_id in enumerate(character_ids):
                if i < len(template.positions):
                    pos_key = f"char{i+1}"
                    if pos_key in template.positions:
                        positions[char_id] = template.positions[pos_key]
                else:
                    # Add extra characters in extended positions
                    positions[char_id] = (i * 2.0, 0.0)
            
            formation = GroupFormation(
                formation_id=formation_id,
                name=f"{template.name} - {formation_id}",
                formation_type=formation_type,
                positions=positions,
                center_position=template.center_position,
                rotation=template.rotation,
                scale=template.scale,
                adaptive=template.adaptive
            )
            
            self.formations[formation_id] = formation
            
            logger.info("Formation created",
                       formation_id=formation_id,
                       type=formation_type,
                       characters=character_ids)
            
            return formation_id
            
        except Exception as e:
            logger.error("Error creating formation", error=str(e))
            return ""
    
    def get_character_position(self, formation_id: str, character_id: str, world_position: Tuple[float, float, float]) -> Optional[Tuple[float, float, float]]:
        """Get target position for character in formation"""
        try:
            if formation_id not in self.formations:
                return None
            
            formation = self.formations[formation_id]
            
            if character_id not in formation.positions:
                return None
            
            # Get relative position
            rel_x, rel_y = formation.positions[character_id]
            
            # Apply scale
            rel_x *= formation.scale
            rel_y *= formation.scale
            
            # Apply rotation
            cos_rot = math.cos(math.radians(formation.rotation))
            sin_rot = math.sin(math.radians(formation.rotation))
            
            rotated_x = rel_x * cos_rot - rel_y * sin_rot
            rotated_y = rel_x * sin_rot + rel_y * cos_rot
            
            # Apply to world position (formation center)
            world_x = world_position[0] + rotated_x
            world_y = world_position[1] + rotated_y
            world_z = world_position[2]  # Keep same Z level
            
            return (world_x, world_y, world_z)
            
        except Exception as e:
            logger.error("Error getting character position", error=str(e))
            return None
    
    def update_formation_center(self, formation_id: str, new_center: Tuple[float, float, float]):
        """Update formation center position"""
        try:
            if formation_id in self.formations:
                formation = self.formations[formation_id]
                formation.center_position = (new_center[0], new_center[1])
                
                logger.debug("Formation center updated",
                           formation_id=formation_id,
                           new_center=new_center)
                
        except Exception as e:
            logger.error("Error updating formation center", error=str(e))

class MultiCharacterOrchestrator:
    """Main orchestration system coordinating multiple characters"""
    
    def __init__(self,
                 max_characters: int = 10,
                 strategy: OrchestrationStrategy = OrchestrationStrategy.COLLABORATIVE,
                 enable_formations: bool = True):
        
        self.max_characters = max_characters
        self.strategy = strategy
        self.enable_formations = enable_formations
        
        # Core components
        self.task_scheduler = TaskScheduler()
        self.assignment_engine = CharacterAssignmentEngine()
        self.formation_manager = FormationManager() if enable_formations else None
        
        # Character management
        self.characters: Dict[str, CharacterState] = {}
        self.character_groups: Dict[str, List[str]] = {}
        self.coordination_rules: Dict[str, CoordinationRule] = {}
        
        # Orchestration state
        self.orchestration_active = False
        self.orchestration_thread: Optional[threading.Thread] = None
        self.update_interval = 1.0  # seconds
        
        # Performance tracking
        self.orchestration_stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_task_duration": 0.0,
            "characters_managed": 0,
            "groups_active": 0,
            "last_update": None
        }
        
        # Callbacks
        self.task_callbacks: List[Callable[[OrchestrationTask], None]] = []
        self.character_callbacks: List[Callable[[CharacterState], None]] = []
        
        # Thread pool for async operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Observability
        self.observability_manager = get_observability_manager()
        
        logger.info("Multi-character orchestrator initialized",
                   strategy=strategy.value,
                   max_characters=max_characters)
    
    @trace_gaming_operation("register_character")
    def register_character(self, character: CharacterState):
        """Register character with orchestration system"""
        try:
            if len(self.characters) >= self.max_characters:
                logger.warning("Maximum character limit reached", 
                             limit=self.max_characters,
                             current=len(self.characters))
                return False
            
            self.characters[character.character_id] = character
            self.orchestration_stats["characters_managed"] = len(self.characters)
            
            # Notify callbacks
            for callback in self.character_callbacks:
                try:
                    callback(character)
                except Exception as e:
                    logger.error("Character callback error", error=str(e))
            
            logger.info("Character registered",
                       character_id=character.character_id,
                       name=character.name,
                       role=character.role.value)
            
            return True
            
        except Exception as e:
            logger.error("Failed to register character", 
                        character_id=character.character_id,
                        error=str(e))
            return False
    
    def unregister_character(self, character_id: str):
        """Unregister character from orchestration"""
        try:
            if character_id in self.characters:
                character = self.characters[character_id]
                
                # Cancel any active tasks
                if character.current_task_id:
                    self.cancel_task(character.current_task_id, f"Character {character_id} unregistered")
                
                # Remove from groups
                for group_id, members in self.character_groups.items():
                    if character_id in members:
                        members.remove(character_id)
                
                # Remove character
                del self.characters[character_id]
                self.orchestration_stats["characters_managed"] = len(self.characters)
                
                logger.info("Character unregistered", character_id=character_id)
                return True
                
        except Exception as e:
            logger.error("Failed to unregister character", error=str(e))
            
        return False
    
    def update_character_state(self, character_id: str, state_updates: Dict[str, Any]):
        """Update character state information"""
        try:
            if character_id not in self.characters:
                logger.warning("Character not found for update", character_id=character_id)
                return False
            
            character = self.characters[character_id]
            
            # Update fields
            for field, value in state_updates.items():
                if hasattr(character, field):
                    setattr(character, field, value)
            
            character.last_update = datetime.utcnow()
            
            logger.debug("Character state updated", 
                        character_id=character_id,
                        updates=list(state_updates.keys()))
            
            return True
            
        except Exception as e:
            logger.error("Failed to update character state", error=str(e))
            return False
    
    @trace_gaming_operation("add_orchestration_task")
    def add_task(self, task: OrchestrationTask):
        """Add task to orchestration system"""
        try:
            self.task_scheduler.add_task(task)
            
            # Notify callbacks
            for callback in self.task_callbacks:
                try:
                    callback(task)
                except Exception as e:
                    logger.error("Task callback error", error=str(e))
            
            logger.info("Task added to orchestration",
                       task_id=task.task_id,
                       type=task.task_type.value,
                       priority=task.priority.value)
            
        except Exception as e:
            logger.error("Failed to add orchestration task", error=str(e))
    
    def cancel_task(self, task_id: str, reason: str = "Cancelled"):
        """Cancel active or pending task"""
        try:
            # Update task status
            self.task_scheduler.update_task_progress(
                task_id, 
                0.0, 
                TaskStatus.CANCELLED
            )
            
            # Free up assigned characters
            if task_id in self.task_scheduler.active_tasks:
                task = self.task_scheduler.active_tasks[task_id]
                task.failure_reason = reason
                
                for char_id in task.assigned_characters:
                    if char_id in self.characters:
                        self.characters[char_id].current_task_id = None
                        self.characters[char_id].status = "idle"
            
            logger.info("Task cancelled", task_id=task_id, reason=reason)
            
        except Exception as e:
            logger.error("Failed to cancel task", task_id=task_id, error=str(e))
    
    def create_character_group(self, group_id: str, character_ids: List[str], formation_type: str = "line") -> bool:
        """Create group of characters"""
        try:
            # Validate characters exist
            valid_characters = [cid for cid in character_ids if cid in self.characters]
            
            if not valid_characters:
                logger.warning("No valid characters for group", group_id=group_id)
                return False
            
            # Create group
            self.character_groups[group_id] = valid_characters.copy()
            
            # Create formation if enabled
            if self.formation_manager:
                formation_id = self.formation_manager.create_formation(valid_characters, formation_type)
                
                # Store formation reference in group metadata
                for char_id in valid_characters:
                    character = self.characters[char_id]
                    if "group_data" not in character.metadata:
                        character.metadata["group_data"] = {}
                    
                    character.metadata["group_data"]["group_id"] = group_id
                    character.metadata["group_data"]["formation_id"] = formation_id
            
            self.orchestration_stats["groups_active"] = len(self.character_groups)
            
            logger.info("Character group created",
                       group_id=group_id,
                       characters=valid_characters,
                       formation=formation_type)
            
            return True
            
        except Exception as e:
            logger.error("Failed to create character group", error=str(e))
            return False
    
    def dissolve_character_group(self, group_id: str):
        """Dissolve character group"""
        try:
            if group_id in self.character_groups:
                character_ids = self.character_groups[group_id]
                
                # Clear group metadata from characters
                for char_id in character_ids:
                    if char_id in self.characters:
                        character = self.characters[char_id]
                        if "group_data" in character.metadata:
                            del character.metadata["group_data"]
                
                del self.character_groups[group_id]
                self.orchestration_stats["groups_active"] = len(self.character_groups)
                
                logger.info("Character group dissolved", group_id=group_id)
                
        except Exception as e:
            logger.error("Failed to dissolve character group", error=str(e))
    
    @trace_gaming_operation("orchestration_cycle")
    async def run_orchestration_cycle(self):
        """Run single orchestration cycle"""
        try:
            # Get ready tasks
            ready_tasks = self.task_scheduler.get_ready_tasks()
            
            if not ready_tasks:
                return
            
            # Get available characters
            available_characters = [
                char for char in self.characters.values()
                if char.current_task_id is None and char.status in ["idle", "ready"]
            ]
            
            if not available_characters:
                logger.debug("No available characters for task assignment")
                return
            
            # Assign tasks to characters
            assignments_made = 0
            
            for task in ready_tasks[:5]:  # Limit to 5 tasks per cycle
                try:
                    # Find best character assignment
                    assigned_characters = self.assignment_engine.find_best_assignment(
                        task, 
                        available_characters
                    )
                    
                    if assigned_characters:
                        # Assign task
                        self.task_scheduler.assign_task(task, assigned_characters)
                        
                        # Update character states
                        for char_id in assigned_characters:
                            if char_id in self.characters:
                                self.characters[char_id].current_task_id = task.task_id
                                self.characters[char_id].status = "assigned"
                        
                        # Remove assigned characters from available pool
                        available_characters = [
                            char for char in available_characters 
                            if char.character_id not in assigned_characters
                        ]
                        
                        assignments_made += 1
                        
                        logger.info("Task assigned in orchestration",
                                   task_id=task.task_id,
                                   characters=assigned_characters)
                        
                except Exception as e:
                    logger.error("Failed to assign task in cycle", 
                                task_id=task.task_id, 
                                error=str(e))
            
            if assignments_made > 0:
                logger.debug("Orchestration cycle completed", assignments=assignments_made)
                
        except Exception as e:
            logger.error("Orchestration cycle error", error=str(e))
    
    def start_orchestration(self):
        """Start continuous orchestration"""
        if self.orchestration_active:
            logger.warning("Orchestration already active")
            return
        
        self.orchestration_active = True
        self.orchestration_thread = threading.Thread(
            target=self._orchestration_loop,
            daemon=True
        )
        self.orchestration_thread.start()
        
        logger.info("Multi-character orchestration started")
    
    def stop_orchestration(self):
        """Stop continuous orchestration"""
        if not self.orchestration_active:
            return
        
        self.orchestration_active = False
        if self.orchestration_thread:
            self.orchestration_thread.join(timeout=2.0)
        
        logger.info("Multi-character orchestration stopped")
    
    def _orchestration_loop(self):
        """Main orchestration loop"""
        while self.orchestration_active:
            try:
                # Run orchestration cycle
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                loop.run_until_complete(self.run_orchestration_cycle())
                
                loop.close()
                
                # Update stats
                self.orchestration_stats["last_update"] = datetime.utcnow()
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error("Orchestration loop error", error=str(e))
                time.sleep(5.0)  # Longer sleep on error
    
    def add_task_callback(self, callback: Callable[[OrchestrationTask], None]):
        """Add callback for task events"""
        self.task_callbacks.append(callback)
    
    def add_character_callback(self, callback: Callable[[CharacterState], None]):
        """Add callback for character events"""
        self.character_callbacks.append(callback)
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current orchestration status"""
        try:
            task_stats = self.task_scheduler.get_task_statistics()
            
            return {
                "active": self.orchestration_active,
                "strategy": self.strategy.value,
                "characters": {
                    "total": len(self.characters),
                    "available": sum(1 for c in self.characters.values() 
                                   if c.current_task_id is None),
                    "busy": sum(1 for c in self.characters.values() 
                              if c.current_task_id is not None),
                    "by_role": {
                        role.value: sum(1 for c in self.characters.values() 
                                      if c.role == role)
                        for role in CharacterRole
                    }
                },
                "groups": {
                    "active": len(self.character_groups),
                    "formations_enabled": self.formation_manager is not None
                },
                "tasks": task_stats,
                "performance": self.orchestration_stats
            }
            
        except Exception as e:
            logger.error("Error getting orchestration status", error=str(e))
            return {"error": str(e)}
    
    def get_character_assignments(self) -> Dict[str, Any]:
        """Get current character task assignments"""
        try:
            assignments = {}
            
            for char_id, character in self.characters.items():
                assignment_info = {
                    "character_name": character.name,
                    "role": character.role.value,
                    "status": character.status,
                    "current_task": None,
                    "location": character.location,
                    "health": character.health_percentage
                }
                
                if character.current_task_id:
                    if character.current_task_id in self.task_scheduler.active_tasks:
                        task = self.task_scheduler.active_tasks[character.current_task_id]
                        assignment_info["current_task"] = {
                            "task_id": task.task_id,
                            "title": task.title,
                            "type": task.task_type.value,
                            "priority": task.priority.value,
                            "progress": task.progress_percentage
                        }
                
                assignments[char_id] = assignment_info
            
            return assignments
            
        except Exception as e:
            logger.error("Error getting character assignments", error=str(e))
            return {}
    
    async def shutdown(self):
        """Shutdown orchestration system"""
        try:
            # Stop orchestration
            self.stop_orchestration()
            
            # Cancel all active tasks
            for task_id in list(self.task_scheduler.active_tasks.keys()):
                self.cancel_task(task_id, "System shutdown")
            
            # Clear character states
            for character in self.characters.values():
                character.current_task_id = None
                character.status = "idle"
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            logger.info("Multi-character orchestration shutdown completed")
            
        except Exception as e:
            logger.error("Failed to shutdown orchestration system", error=str(e))

# Global orchestrator instance
_global_orchestrator: Optional[MultiCharacterOrchestrator] = None

def initialize_multi_character_orchestration(**kwargs) -> MultiCharacterOrchestrator:
    """Initialize global multi-character orchestrator"""
    global _global_orchestrator
    
    _global_orchestrator = MultiCharacterOrchestrator(**kwargs)
    return _global_orchestrator

def get_multi_character_orchestrator() -> Optional[MultiCharacterOrchestrator]:
    """Get global multi-character orchestrator instance"""
    return _global_orchestrator
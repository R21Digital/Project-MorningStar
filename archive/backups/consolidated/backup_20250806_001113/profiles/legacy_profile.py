"""
Legacy Quest Profile System

This module provides comprehensive loading, parsing, and runtime logic for full Legacy Quest automation.
It integrates with the dialogue handler, travel system, and quest tracker to provide complete quest automation.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

from core.database import load_quest
from core.dialogue_handler import dialogue_handler, detect_dialogue_box, advance_conversation
from core.trainer_system import trainer_system
from core.movement_controller import MovementController
from core.quest_state import get_step_status, STATUS_COMPLETED, STATUS_IN_PROGRESS, STATUS_FAILED


class QuestStepType(Enum):
    """Types of quest steps."""
    DIALOGUE = "dialogue"
    COLLECTION = "collection"
    COMBAT = "combat"
    MOVEMENT = "movement"
    EXPLORATION = "exploration"
    INTERACTION = "interaction"
    RITUAL = "ritual"


class QuestStepStatus(Enum):
    """Status of quest steps."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class QuestStep:
    """Represents a single quest step."""
    step_id: str
    step_type: QuestStepType
    title: str
    description: str
    coordinates: List[int]
    zone: str
    planet: str
    npc_id: Optional[str] = None
    target_item: Optional[str] = None
    target_npc: Optional[str] = None
    required_count: int = 1
    timeout_seconds: int = 300
    dialogue_options: List[str] = None
    required_response: int = 0
    collection_radius: int = 50
    combat_requirements: Dict[str, Any] = None
    prerequisites: List[str] = None
    status: QuestStepStatus = QuestStepStatus.NOT_STARTED
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    attempts: int = 0
    max_attempts: int = 3
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dialogue_options is None:
            self.dialogue_options = []
        if self.combat_requirements is None:
            self.combat_requirements = {}
        if self.prerequisites is None:
            self.prerequisites = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LegacyQuestProfile:
    """Represents a complete Legacy Quest profile."""
    quest_id: str
    name: str
    description: str
    quest_type: str
    difficulty: str
    level_requirement: int
    planet: str
    zone: str
    coordinates: List[int]
    quest_chain: str
    prerequisites: List[str]
    rewards: Dict[str, Any]
    steps: List[QuestStep]
    completion_conditions: List[Dict[str, Any]]
    failure_conditions: List[Dict[str, Any]]
    hints: List[str]
    status: QuestStepStatus = QuestStepStatus.NOT_STARTED
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    current_step_index: int = 0
    completed_steps: List[str] = None
    failed_steps: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = []
        if self.failed_steps is None:
            self.failed_steps = []
        if self.metadata is None:
            self.metadata = {}


class LegacyQuestManager:
    """
    Comprehensive Legacy Quest management system.
    
    Features:
    - Load and parse Legacy quest profiles
    - Track quest progress and step completion
    - Integrate with dialogue handler for quest acceptance/completion
    - Automate travel between quest locations
    - Update quest dashboard and logs
    - Handle quest failures and timeouts
    """
    
    def __init__(self):
        """Initialize the Legacy Quest Manager."""
        self.logger = logging.getLogger("legacy_quest_manager")
        self.movement_controller = MovementController()
        
        # Quest tracking
        self.active_quests: Dict[str, LegacyQuestProfile] = {}
        self.completed_quests: List[str] = []
        self.failed_quests: List[str] = []
        
        # Configuration
        self.auto_accept_quests = True
        self.auto_complete_quests = True
        self.auto_travel = True
        self.quest_timeout = 3600  # 1 hour default
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging for quest manager."""
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def load_legacy_quest(self, quest_id: str) -> Optional[LegacyQuestProfile]:
        """
        Load a Legacy quest profile from the database.
        
        Args:
            quest_id: The quest ID to load
            
        Returns:
            LegacyQuestProfile object or None if not found
        """
        try:
            # Load quest data from database
            quest_data = load_quest(quest_id)
            if not quest_data:
                self.logger.error(f"Quest not found: {quest_id}")
                return None
            
            # Convert quest data to LegacyQuestProfile
            steps = []
            for step_data in quest_data.steps or []:
                step = self._create_quest_step(step_data)
                if step:
                    steps.append(step)
            
            profile = LegacyQuestProfile(
                quest_id=quest_data.quest_id,
                name=quest_data.name,
                description=quest_data.description,
                quest_type=quest_data.quest_type,
                difficulty=quest_data.difficulty,
                level_requirement=quest_data.level_requirement,
                planet=quest_data.planet,
                zone=quest_data.zone,
                coordinates=quest_data.coordinates,
                quest_chain=quest_data.quest_chain or "",
                prerequisites=quest_data.prerequisites or [],
                rewards=quest_data.rewards or {},
                steps=steps,
                completion_conditions=quest_data.completion_conditions or [],
                failure_conditions=quest_data.failure_conditions or [],
                hints=quest_data.hints or [],
                metadata=quest_data.metadata or {}
            )
            
            self.logger.info(f"Loaded Legacy quest: {profile.name} with {len(steps)} steps")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error loading Legacy quest {quest_id}: {e}")
            return None
    
    def _create_quest_step(self, step_data: Dict[str, Any]) -> Optional[QuestStep]:
        """Create a QuestStep from step data."""
        try:
            step_type = QuestStepType(step_data.get("type", "dialogue"))
            
            return QuestStep(
                step_id=step_data.get("step_id", f"step_{len(self.active_quests)}"),
                step_type=step_type,
                title=step_data.get("title", ""),
                description=step_data.get("description", ""),
                coordinates=step_data.get("coordinates", [0, 0]),
                zone=step_data.get("zone", ""),
                planet=step_data.get("planet", ""),
                npc_id=step_data.get("npc_id"),
                target_item=step_data.get("target_item"),
                target_npc=step_data.get("target_npc"),
                required_count=step_data.get("required_count", 1),
                timeout_seconds=step_data.get("timeout_seconds", 300),
                dialogue_options=step_data.get("dialogue_options", []),
                required_response=step_data.get("required_response", 0),
                collection_radius=step_data.get("collection_radius", 50),
                combat_requirements=step_data.get("combat_requirements", {}),
                prerequisites=step_data.get("prerequisites", []),
                metadata=step_data.get("metadata", {})
            )
            
        except Exception as e:
            self.logger.error(f"Error creating quest step: {e}")
            return None
    
    def start_quest(self, quest_id: str) -> bool:
        """
        Start a Legacy quest.
        
        Args:
            quest_id: The quest ID to start
            
        Returns:
            True if quest started successfully, False otherwise
        """
        # Load quest profile
        profile = self.load_legacy_quest(quest_id)
        if not profile:
            return False
        
        # Check prerequisites
        if not self._check_prerequisites(profile):
            self.logger.warning(f"Prerequisites not met for quest: {quest_id}")
            return False
        
        # Check if quest is already active
        if quest_id in self.active_quests:
            self.logger.warning(f"Quest already active: {quest_id}")
            return False
        
        # Initialize quest
        profile.status = QuestStepStatus.IN_PROGRESS
        profile.start_time = time.time()
        profile.current_step_index = 0
        
        # Add to active quests
        self.active_quests[quest_id] = profile
        
        self.logger.info(f"Started Legacy quest: {profile.name}")
        self._log_quest_event("quest_started", profile)
        
        return True
    
    def _check_prerequisites(self, profile: LegacyQuestProfile) -> bool:
        """Check if quest prerequisites are met."""
        for prereq in profile.prerequisites:
            # Check if prerequisite quest is completed
            if prereq not in self.completed_quests:
                return False
        return True
    
    def execute_current_step(self, quest_id: str) -> bool:
        """
        Execute the current step of a quest.
        
        Args:
            quest_id: The quest ID to execute
            
        Returns:
            True if step completed successfully, False otherwise
        """
        if quest_id not in self.active_quests:
            self.logger.error(f"Quest not active: {quest_id}")
            return False
        
        profile = self.active_quests[quest_id]
        
        if profile.current_step_index >= len(profile.steps):
            self.logger.info(f"All steps completed for quest: {quest_id}")
            return self._complete_quest(quest_id)
        
        current_step = profile.steps[profile.current_step_index]
        
        # Check if step is already completed
        if current_step.status == QuestStepStatus.COMPLETED:
            profile.current_step_index += 1
            return self.execute_current_step(quest_id)
        
        # Execute step based on type
        success = self._execute_step(current_step, profile)
        
        if success:
            current_step.status = QuestStepStatus.COMPLETED
            current_step.completion_time = time.time()
            profile.completed_steps.append(current_step.step_id)
            profile.current_step_index += 1
            
            self.logger.info(f"Completed step: {current_step.title}")
            self._log_quest_event("step_completed", profile, current_step)
            
        else:
            current_step.attempts += 1
            if current_step.attempts >= current_step.max_attempts:
                current_step.status = QuestStepStatus.FAILED
                profile.failed_steps.append(current_step.step_id)
                self.logger.error(f"Step failed after {current_step.max_attempts} attempts: {current_step.title}")
                self._log_quest_event("step_failed", profile, current_step)
        
        return success
    
    def _execute_step(self, step: QuestStep, profile: LegacyQuestProfile) -> bool:
        """Execute a single quest step."""
        step.status = QuestStepStatus.IN_PROGRESS
        step.start_time = time.time()
        
        self.logger.info(f"Executing step: {step.title} ({step.step_type.value})")
        
        try:
            if step.step_type == QuestStepType.DIALOGUE:
                return self._execute_dialogue_step(step, profile)
            elif step.step_type == QuestStepType.COLLECTION:
                return self._execute_collection_step(step, profile)
            elif step.step_type == QuestStepType.COMBAT:
                return self._execute_combat_step(step, profile)
            elif step.step_type == QuestStepType.MOVEMENT:
                return self._execute_movement_step(step, profile)
            elif step.step_type == QuestStepType.EXPLORATION:
                return self._execute_exploration_step(step, profile)
            elif step.step_type == QuestStepType.INTERACTION:
                return self._execute_interaction_step(step, profile)
            elif step.step_type == QuestStepType.RITUAL:
                return self._execute_ritual_step(step, profile)
            else:
                self.logger.warning(f"Unknown step type: {step.step_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing step {step.step_id}: {e}")
            return False
    
    def _execute_dialogue_step(self, step: QuestStep, profile: LegacyQuestProfile) -> bool:
        """Execute a dialogue step."""
        # Travel to NPC location if needed
        if self.auto_travel and step.coordinates != [0, 0]:
            self.movement_controller.walk_to_coordinates(step.coordinates[0], step.coordinates[1])
        
        # Wait for dialogue to appear
        dialogue_window = dialogue_handler.wait_for_dialogue(timeout=10.0)
        if not dialogue_window:
            self.logger.warning("No dialogue window detected")
            return False
        
        # Advance conversation
        interaction = dialogue_handler.advance_conversation(dialogue_window, "auto")
        
        if interaction.success:
            self.logger.info(f"Dialogue step completed: {step.title}")
            return True
        else:
            self.logger.warning(f"Dialogue step failed: {step.title}")
            return False
    
    def _execute_collection_step(self, step: QuestStep, profile: LegacyQuestProfile) -> bool:
        """Execute a collection step."""
        # Travel to collection location
        if self.auto_travel and step.coordinates != [0, 0]:
            self.movement_controller.walk_to_coordinates(step.coordinates[0], step.coordinates[1])
        
        # Simulate collection (would integrate with actual collection system)
        self.logger.info(f"Collecting {step.target_item} at {step.coordinates}")
        time.sleep(2)  # Simulate collection time
        
        return True
    
    def _execute_combat_step(self, step: QuestStep, profile: LegacyQuestProfile) -> bool:
        """Execute a combat step."""
        # Travel to combat location
        if self.auto_travel and step.coordinates != [0, 0]:
            self.movement_controller.walk_to_coordinates(step.coordinates[0], step.coordinates[1])
        
        # Simulate combat (would integrate with actual combat system)
        self.logger.info(f"Combat with {step.target_npc} at {step.coordinates}")
        time.sleep(5)  # Simulate combat time
        
        return True
    
    def _execute_movement_step(self, step: QuestStep, profile: LegacyQuestProfile) -> bool:
        """Execute a movement step."""
        if step.coordinates != [0, 0]:
            success = self.movement_controller.walk_to_coordinates(step.coordinates[0], step.coordinates[1])
            if success:
                self.logger.info(f"Movement step completed: {step.title}")
                return True
            else:
                self.logger.warning(f"Movement step failed: {step.title}")
                return False
        else:
            self.logger.warning(f"No coordinates specified for movement step: {step.title}")
            return False
    
    def _execute_exploration_step(self, step: QuestStep, profile: LegacyQuestProfile) -> bool:
        """Execute an exploration step."""
        # Travel to exploration location
        if self.auto_travel and step.coordinates != [0, 0]:
            self.movement_controller.walk_to_coordinates(step.coordinates[0], step.coordinates[1])
        
        # Simulate exploration
        self.logger.info(f"Exploring area at {step.coordinates}")
        time.sleep(3)  # Simulate exploration time
        
        return True
    
    def _execute_interaction_step(self, step: QuestStep, profile: LegacyQuestProfile) -> bool:
        """Execute an interaction step."""
        # Travel to interaction location
        if self.auto_travel and step.coordinates != [0, 0]:
            self.movement_controller.walk_to_coordinates(step.coordinates[0], step.coordinates[1])
        
        # Simulate interaction
        self.logger.info(f"Interacting with {step.target_npc} at {step.coordinates}")
        time.sleep(2)  # Simulate interaction time
        
        return True
    
    def _execute_ritual_step(self, step: QuestStep, profile: LegacyQuestProfile) -> bool:
        """Execute a ritual step."""
        # Travel to ritual location
        if self.auto_travel and step.coordinates != [0, 0]:
            self.movement_controller.walk_to_coordinates(step.coordinates[0], step.coordinates[1])
        
        # Simulate ritual
        self.logger.info(f"Performing ritual at {step.coordinates}")
        time.sleep(4)  # Simulate ritual time
        
        return True
    
    def _complete_quest(self, quest_id: str) -> bool:
        """Complete a quest."""
        if quest_id not in self.active_quests:
            return False
        
        profile = self.active_quests[quest_id]
        
        # Check completion conditions
        if not self._check_completion_conditions(profile):
            self.logger.warning(f"Completion conditions not met for quest: {quest_id}")
            return False
        
        # Mark quest as completed
        profile.status = QuestStepStatus.COMPLETED
        profile.completion_time = time.time()
        
        # Move to completed quests
        self.completed_quests.append(quest_id)
        del self.active_quests[quest_id]
        
        # Apply rewards
        self._apply_quest_rewards(profile)
        
        self.logger.info(f"Completed Legacy quest: {profile.name}")
        self._log_quest_event("quest_completed", profile)
        
        return True
    
    def _check_completion_conditions(self, profile: LegacyQuestProfile) -> bool:
        """Check if quest completion conditions are met."""
        for condition in profile.completion_conditions:
            condition_type = condition.get("type")
            
            if condition_type == "steps_completed":
                required_steps = condition.get("steps", [])
                required_count = condition.get("count", len(required_steps))
                
                completed_count = sum(1 for step in required_steps if step in profile.completed_steps)
                if completed_count < required_count:
                    return False
            
            elif condition_type == "timeout":
                timeout_seconds = condition.get("timeout_seconds", 3600)
                if profile.start_time and (time.time() - profile.start_time) > timeout_seconds:
                    return False
        
        return True
    
    def _apply_quest_rewards(self, profile: LegacyQuestProfile):
        """Apply quest rewards."""
        rewards = profile.rewards
        
        self.logger.info(f"Applying rewards for quest: {profile.name}")
        
        if "experience" in rewards:
            self.logger.info(f"Experience gained: {rewards['experience']}")
        
        if "credits" in rewards:
            self.logger.info(f"Credits gained: {rewards['credits']}")
        
        if "reputation" in rewards:
            self.logger.info(f"Reputation gained: {rewards['reputation']}")
        
        if "items" in rewards:
            self.logger.info(f"Items gained: {rewards['items']}")
        
        if "unlocks" in rewards:
            self.logger.info(f"Unlocks gained: {rewards['unlocks']}")
    
    def get_quest_progress(self, quest_id: str) -> Dict[str, Any]:
        """Get progress information for a quest."""
        if quest_id not in self.active_quests:
            return {"status": "not_found"}
        
        profile = self.active_quests[quest_id]
        
        total_steps = len(profile.steps)
        completed_steps = len(profile.completed_steps)
        failed_steps = len(profile.failed_steps)
        
        progress_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        return {
            "quest_id": quest_id,
            "name": profile.name,
            "status": profile.status.value,
            "current_step": profile.current_step_index + 1,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "progress_percentage": progress_percentage,
            "start_time": profile.start_time,
            "completion_time": profile.completion_time,
            "current_step_info": self._get_current_step_info(profile)
        }
    
    def _get_current_step_info(self, profile: LegacyQuestProfile) -> Dict[str, Any]:
        """Get information about the current step."""
        if profile.current_step_index >= len(profile.steps):
            return {"status": "completed"}
        
        current_step = profile.steps[profile.current_step_index]
        
        return {
            "step_id": current_step.step_id,
            "title": current_step.title,
            "description": current_step.description,
            "type": current_step.step_type.value,
            "status": current_step.status.value,
            "coordinates": current_step.coordinates,
            "zone": current_step.zone,
            "attempts": current_step.attempts,
            "max_attempts": current_step.max_attempts
        }
    
    def get_all_quest_progress(self) -> Dict[str, Any]:
        """Get progress for all active quests."""
        return {
            "active_quests": {qid: self.get_quest_progress(qid) for qid in self.active_quests},
            "completed_quests": self.completed_quests,
            "failed_quests": self.failed_quests,
            "total_active": len(self.active_quests),
            "total_completed": len(self.completed_quests),
            "total_failed": len(self.failed_quests)
        }
    
    def _log_quest_event(self, event_type: str, profile: LegacyQuestProfile, step: QuestStep = None):
        """Log quest events for tracking."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "quest_id": profile.quest_id,
            "quest_name": profile.name,
            "step_info": asdict(step) if step else None,
            "quest_progress": self.get_quest_progress(profile.quest_id)
        }
        
        # Log to file
        log_file = Path("logs/legacy_quests.json")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            self.logger.error(f"Error logging quest event: {e}")


# Global Legacy Quest Manager instance
legacy_quest_manager = LegacyQuestManager()


def load_legacy_quest(quest_id: str) -> Optional[LegacyQuestProfile]:
    """Load a Legacy quest using the global manager."""
    return legacy_quest_manager.load_legacy_quest(quest_id)


def start_legacy_quest(quest_id: str) -> bool:
    """Start a Legacy quest using the global manager."""
    return legacy_quest_manager.start_quest(quest_id)


def execute_quest_step(quest_id: str) -> bool:
    """Execute the current step of a quest using the global manager."""
    return legacy_quest_manager.execute_current_step(quest_id)


def get_quest_progress(quest_id: str) -> Dict[str, Any]:
    """Get quest progress using the global manager."""
    return legacy_quest_manager.get_quest_progress(quest_id)


def get_all_quest_progress() -> Dict[str, Any]:
    """Get all quest progress using the global manager."""
    return legacy_quest_manager.get_all_quest_progress() 
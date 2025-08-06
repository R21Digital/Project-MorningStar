"""
Quest Engine - Database-Integrated Quest System

This module provides a quest execution engine that loads quest data from the database
and executes quest steps dynamically based on the loaded metadata.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from core.database import load_quest, QuestData
from core.dialogue_detector import DialogueDetector
from core.movement_controller import MovementController
from core.ocr import OCREngine


class QuestEngine:
    """
    Database-integrated quest execution engine.
    
    Features:
    - Loads quest data from database using load_quest()
    - Executes quest steps dynamically based on loaded metadata
    - Handles dialogue, movement, combat, and collection steps
    - Provides fallback for missing quest data
    - Logs all quest execution activities
    """
    
    def __init__(self):
        """Initialize the quest engine with required components."""
        self.logger = logging.getLogger("quest_engine")
        self.dialogue_detector = DialogueDetector()
        self.movement_controller = MovementController()
        self.ocr_engine = OCREngine()
        
        # Quest execution state
        self.current_quest: Optional[QuestData] = None
        self.current_step_index: int = 0
        self.quest_state: Dict[str, Any] = {}
        
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging for quest engine."""
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def load_quest(self, quest_id: str) -> Optional[QuestData]:
        """
        Load a quest from the database.
        
        Args:
            quest_id: The quest ID to load
            
        Returns:
            QuestData object or None if not found
        """
        try:
            quest = load_quest(quest_id)
            if quest:
                self.logger.info(f"Successfully loaded quest: {quest.name} (ID: {quest_id})")
                return quest
            else:
                self.logger.error(f"Quest not found: {quest_id}")
                return None
        except Exception as e:
            self.logger.error(f"Error loading quest {quest_id}: {e}")
            return None
    
    def start_quest(self, quest_id: str) -> bool:
        """
        Start a new quest execution.
        
        Args:
            quest_id: The quest ID to start
            
        Returns:
            True if quest started successfully, False otherwise
        """
        quest = self.load_quest(quest_id)
        if not quest:
            return False
        
        self.current_quest = quest
        self.current_step_index = 0
        self.quest_state = {
            "quest_id": quest_id,
            "start_time": time.time(),
            "completed_steps": [],
            "failed_steps": [],
            "current_step": None
        }
        
        self.logger.info(f"Started quest: {quest.name}")
        self.logger.info(f"Quest type: {quest.quest_type}")
        self.logger.info(f"Difficulty: {quest.difficulty}")
        self.logger.info(f"Level requirement: {quest.level_requirement}")
        self.logger.info(f"Total steps: {len(quest.steps) if quest.steps else 0}")
        
        return True
    
    def execute_current_step(self) -> bool:
        """
        Execute the current quest step.
        
        Returns:
            True if step completed successfully, False otherwise
        """
        if not self.current_quest or not self.current_quest.steps:
            self.logger.error("No quest loaded or no steps available")
            return False
        
        if self.current_step_index >= len(self.current_quest.steps):
            self.logger.info("All quest steps completed")
            return True
        
        step = self.current_quest.steps[self.current_step_index]
        step_id = step.get("step_id", f"step_{self.current_step_index + 1}")
        
        self.logger.info(f"Executing step {self.current_step_index + 1}: {step_id}")
        self.quest_state["current_step"] = step
        
        try:
            success = self._execute_step(step)
            if success:
                self.quest_state["completed_steps"].append(step_id)
                self.current_step_index += 1
                self.logger.info(f"Step {step_id} completed successfully")
            else:
                self.quest_state["failed_steps"].append(step_id)
                self.logger.warning(f"Step {step_id} failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error executing step {step_id}: {e}")
            self.quest_state["failed_steps"].append(step_id)
            return False
    
    def _execute_step(self, step: Dict[str, Any]) -> bool:
        """
        Execute a single quest step based on its type.
        
        Args:
            step: The step dictionary to execute
            
        Returns:
            True if step executed successfully, False otherwise
        """
        step_type = step.get("type", "unknown")
        
        if step_type == "dialogue":
            return self._execute_dialogue_step(step)
        elif step_type == "movement":
            return self._execute_movement_step(step)
        elif step_type == "combat":
            return self._execute_combat_step(step)
        elif step_type == "collection":
            return self._execute_collection_step(step)
        elif step_type == "exploration":
            return self._execute_exploration_step(step)
        elif step_type == "interaction":
            return self._execute_interaction_step(step)
        elif step_type == "ritual":
            return self._execute_ritual_step(step)
        else:
            self.logger.warning(f"Unknown step type: {step_type}")
            return False
    
    def _execute_dialogue_step(self, step: Dict[str, Any]) -> bool:
        """Execute a dialogue step."""
        npc_id = step.get("npc_id")
        coordinates = step.get("coordinates", [0, 0])
        dialogue_options = step.get("dialogue_options", [])
        required_response = step.get("required_response", 0)
        
        self.logger.info(f"Executing dialogue with NPC: {npc_id}")
        
        # Move to NPC location if coordinates provided
        if coordinates and coordinates != [0, 0]:
            self.movement_controller.walk_to_coordinates(coordinates[0], coordinates[1])
        
        # Detect dialogue window
        dialogue_window = self.dialogue_detector.detect_dialogue_window()
        if not dialogue_window:
            self.logger.warning("No dialogue window detected")
            return False
        
        # Select appropriate dialogue option
        if dialogue_options and required_response < len(dialogue_options):
            selected_option = dialogue_options[required_response]
            self.logger.info(f"Selecting dialogue option: {selected_option}")
            
            # Click the dialogue option
            success = self.dialogue_detector.click_dialogue_option_by_text(selected_option, dialogue_window)
            if success:
                self.logger.info("Dialogue option selected successfully")
                return True
            else:
                self.logger.warning("Failed to select dialogue option")
                return False
        
        return True
    
    def _execute_movement_step(self, step: Dict[str, Any]) -> bool:
        """Execute a movement step."""
        coordinates = step.get("coordinates", [0, 0])
        target_location = step.get("target_location")
        
        if coordinates and coordinates != [0, 0]:
            self.logger.info(f"Moving to coordinates: {coordinates}")
            return self.movement_controller.walk_to_coordinates(coordinates[0], coordinates[1])
        elif target_location:
            self.logger.info(f"Moving to location: {target_location}")
            return self.movement_controller.walk_to_coordinates(0, 0)  # Placeholder for location-based movement
        else:
            self.logger.warning("No movement target specified")
            return False
    
    def _execute_combat_step(self, step: Dict[str, Any]) -> bool:
        """Execute a combat step."""
        target_npc = step.get("target_npc")
        combat_requirements = step.get("combat_requirements", {})
        timeout_seconds = step.get("timeout_seconds", 300)
        
        self.logger.info(f"Executing combat with target: {target_npc}")
        
        # Start combat
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            # Check combat requirements
            if self._check_combat_requirements(combat_requirements):
                self.logger.info("Combat requirements met")
                return True
            
            # Continue combat
            time.sleep(1)
        
        self.logger.warning("Combat step timed out")
        return False
    
    def _execute_collection_step(self, step: Dict[str, Any]) -> bool:
        """Execute a collection step."""
        target_item = step.get("target_item")
        coordinates = step.get("coordinates", [0, 0])
        collection_radius = step.get("collection_radius", 50)
        required_count = step.get("required_count", 1)
        timeout_seconds = step.get("timeout_seconds", 180)
        
        self.logger.info(f"Executing collection for item: {target_item}")
        
        # Move to collection location
        if coordinates and coordinates != [0, 0]:
            self.movement_controller.walk_to_coordinates(coordinates[0], coordinates[1])
        
        # Attempt collection
        start_time = time.time()
        collected_count = 0
        
        while time.time() - start_time < timeout_seconds and collected_count < required_count:
            # Look for collectible items in the area
            if self._detect_collectible_item(target_item, collection_radius):
                if self._collect_item(target_item):
                    collected_count += 1
                    self.logger.info(f"Collected {target_item} ({collected_count}/{required_count})")
            
            time.sleep(1)
        
        return collected_count >= required_count
    
    def _execute_exploration_step(self, step: Dict[str, Any]) -> bool:
        """Execute an exploration step."""
        target_location = step.get("target_location")
        exploration_radius = step.get("exploration_radius", 100)
        required_actions = step.get("required_actions", [])
        timeout_seconds = step.get("timeout_seconds", 600)
        
        self.logger.info(f"Executing exploration for location: {target_location}")
        
        # Move to exploration area
        coordinates = step.get("coordinates", [0, 0])
        if coordinates and coordinates != [0, 0]:
            self.movement_controller.walk_to_coordinates(coordinates[0], coordinates[1])
        
        # Perform exploration actions
        start_time = time.time()
        completed_actions = []
        
        while time.time() - start_time < timeout_seconds:
            for action in required_actions:
                if action not in completed_actions:
                    if self._perform_exploration_action(action):
                        completed_actions.append(action)
                        self.logger.info(f"Completed exploration action: {action}")
            
            if len(completed_actions) >= len(required_actions):
                return True
            
            time.sleep(1)
        
        return len(completed_actions) >= len(required_actions)
    
    def _execute_interaction_step(self, step: Dict[str, Any]) -> bool:
        """Execute an interaction step."""
        target_location = step.get("target_location")
        interaction_requirements = step.get("interaction_requirements", {})
        timeout_seconds = step.get("timeout_seconds", 600)
        
        self.logger.info(f"Executing interaction at location: {target_location}")
        
        # Move to interaction location
        coordinates = step.get("coordinates", [0, 0])
        if coordinates and coordinates != [0, 0]:
            self.movement_controller.walk_to_coordinates(coordinates[0], coordinates[1])
        
        # Perform interaction
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            if self._check_interaction_requirements(interaction_requirements):
                self.logger.info("Interaction requirements met")
                return True
            
            time.sleep(1)
        
        self.logger.warning("Interaction step timed out")
        return False
    
    def _execute_ritual_step(self, step: Dict[str, Any]) -> bool:
        """Execute a ritual step."""
        target_location = step.get("target_location")
        ritual_requirements = step.get("ritual_requirements", {})
        timeout_seconds = step.get("timeout_seconds", 600)
        
        self.logger.info(f"Executing ritual at location: {target_location}")
        
        # Move to ritual location
        coordinates = step.get("coordinates", [0, 0])
        if coordinates and coordinates != [0, 0]:
            self.movement_controller.walk_to_coordinates(coordinates[0], coordinates[1])
        
        # Perform ritual
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            if self._check_ritual_requirements(ritual_requirements):
                self.logger.info("Ritual requirements met")
                return True
            
            time.sleep(1)
        
        self.logger.warning("Ritual step timed out")
        return False
    
    def _check_combat_requirements(self, requirements: Dict[str, Any]) -> bool:
        """Check if combat requirements are met."""
        # This would integrate with the combat system
        # For now, return True as placeholder
        return True
    
    def _detect_collectible_item(self, item_name: str, radius: int) -> bool:
        """Detect if a collectible item is in range."""
        # This would integrate with the OCR system to detect items
        # For now, return True as placeholder
        return True
    
    def _collect_item(self, item_name: str) -> bool:
        """Attempt to collect an item."""
        # This would integrate with the interaction system
        # For now, return True as placeholder
        return True
    
    def _perform_exploration_action(self, action: str) -> bool:
        """Perform an exploration action."""
        # This would integrate with various exploration systems
        # For now, return True as placeholder
        return True
    
    def _check_interaction_requirements(self, requirements: Dict[str, Any]) -> bool:
        """Check if interaction requirements are met."""
        # This would check various interaction requirements
        # For now, return True as placeholder
        return True
    
    def _check_ritual_requirements(self, requirements: Dict[str, Any]) -> bool:
        """Check if ritual requirements are met."""
        # This would check ritual-specific requirements
        # For now, return True as placeholder
        return True
    
    def get_quest_progress(self) -> Dict[str, Any]:
        """Get the current quest progress."""
        if not self.current_quest:
            return {"status": "no_quest"}
        
        total_steps = len(self.current_quest.steps) if self.current_quest.steps else 0
        completed_steps = len(self.quest_state.get("completed_steps", []))
        failed_steps = len(self.quest_state.get("failed_steps", []))
        
        return {
            "quest_id": self.current_quest.quest_id,
            "quest_name": self.current_quest.name,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "current_step": self.current_step_index + 1,
            "progress_percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            "status": "completed" if self.current_step_index >= total_steps else "in_progress"
        }
    
    def complete_quest(self) -> bool:
        """Complete the current quest."""
        if not self.current_quest:
            return False
        
        self.logger.info(f"Completing quest: {self.current_quest.name}")
        
        # Check completion conditions
        if self.current_quest.completion_conditions:
            for condition in self.current_quest.completion_conditions:
                if not self._check_completion_condition(condition):
                    self.logger.warning(f"Completion condition not met: {condition}")
                    return False
        
        # Apply quest rewards
        if self.current_quest.rewards:
            self._apply_quest_rewards(self.current_quest.rewards)
        
        self.logger.info("Quest completed successfully")
        return True
    
    def _check_completion_condition(self, condition: Dict[str, Any]) -> bool:
        """Check if a completion condition is met."""
        condition_type = condition.get("type")
        
        if condition_type == "steps_completed":
            required_steps = condition.get("steps", [])
            completed_steps = self.quest_state.get("completed_steps", [])
            required_count = condition.get("count", len(required_steps))
            
            completed_count = sum(1 for step in required_steps if step in completed_steps)
            return completed_count >= required_count
        
        # Add more condition types as needed
        return True
    
    def _apply_quest_rewards(self, rewards: Dict[str, Any]) -> None:
        """Apply quest rewards to the character."""
        self.logger.info(f"Applying quest rewards: {rewards}")
        
        # This would integrate with the character system
        # For now, just log the rewards
        if "experience" in rewards:
            self.logger.info(f"Experience gained: {rewards['experience']}")
        
        if "credits" in rewards:
            self.logger.info(f"Credits gained: {rewards['credits']}")
        
        if "items" in rewards:
            self.logger.info(f"Items gained: {rewards['items']}")
    
    def stop_quest(self) -> None:
        """Stop the current quest execution."""
        if self.current_quest:
            self.logger.info(f"Stopping quest: {self.current_quest.name}")
            self.current_quest = None
            self.current_step_index = 0
            self.quest_state = {}


# Global quest engine instance
quest_engine = QuestEngine()


def execute_quest_from_database(quest_id: str) -> Dict[str, Any]:
    """
    Execute a quest loaded from the database.
    
    Args:
        quest_id: The quest ID to execute
        
    Returns:
        Dictionary with execution results
    """
    if not quest_engine.start_quest(quest_id):
        return {"success": False, "error": f"Failed to load quest: {quest_id}"}
    
    try:
        # Execute all quest steps
        while quest_engine.current_step_index < len(quest_engine.current_quest.steps):
            if not quest_engine.execute_current_step():
                return {"success": False, "error": "Quest step failed"}
        
        # Complete the quest
        if quest_engine.complete_quest():
            return {"success": True, "progress": quest_engine.get_quest_progress()}
        else:
            return {"success": False, "error": "Failed to complete quest"}
    
    except Exception as e:
        return {"success": False, "error": f"Quest execution error: {e}"}
    finally:
        quest_engine.stop_quest()


def get_quest_progress() -> Dict[str, Any]:
    """Get the current quest progress."""
    return quest_engine.get_quest_progress() 
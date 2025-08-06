"""Manage space missions and mission types."""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from utils.logging_utils import log_event


@dataclass
class SpaceMission:
    """Represents a space mission."""
    mission_id: str
    name: str
    mission_type: str  # "patrol", "escort", "kill_target"
    description: str
    status: str  # "available", "active", "completed", "failed"
    location: str
    target_location: Optional[str]
    credits: int
    experience: int
    requirements: Dict[str, Any]
    steps: List[Dict[str, Any]]
    current_step: int
    start_time: Optional[float]
    completion_time: Optional[float]


@dataclass
class MissionStep:
    """Represents a mission step."""
    step_id: int
    step_type: str  # "travel", "combat", "interaction", "delivery"
    description: str
    location: str
    target: Optional[str]
    requirements: Dict[str, Any]
    completed: bool


class SpaceMissionManager:
    """Manage space missions and mission types."""

    def __init__(self, config_path: str = "config/session_config.json"):
        """Initialize the space mission manager.

        Parameters
        ----------
        config_path : str
            Path to session configuration file
        """
        self.config = self._load_config(config_path)
        self.space_config = self.config.get("space_mode", {})
        
        # Mission types
        self.mission_types = {
            "patrol": {
                "description": "Patrol a designated area",
                "steps": ["travel_to_area", "patrol_route", "return_to_station"],
                "requirements": {"ship": True, "combat_rating": 1}
            },
            "escort": {
                "description": "Escort a target to destination",
                "steps": ["meet_target", "escort_route", "deliver_target"],
                "requirements": {"ship": True, "combat_rating": 2}
            },
            "kill_target": {
                "description": "Eliminate specific targets",
                "steps": ["locate_target", "engage_combat", "confirm_kill"],
                "requirements": {"ship": True, "combat_rating": 3}
            }
        }
        
        # Active missions
        self.active_missions: Dict[str, SpaceMission] = {}
        self.completed_missions: List[SpaceMission] = []
        
        # Load existing missions
        self._load_missions()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load session configuration."""
        path = Path(config_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        return {}

    def _load_missions(self) -> None:
        """Load missions from data files."""
        missions_file = Path("data/space_quests/space_quests.json")
        if missions_file.exists():
            try:
                with missions_file.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    for mission_data in data.get("quests", []):
                        mission = self._create_mission_from_data(mission_data)
                        if mission.status == "active":
                            self.active_missions[mission.mission_id] = mission
                        elif mission.status == "completed":
                            self.completed_missions.append(mission)
            except Exception as e:
                log_event(f"[SPACE] Error loading missions: {e}")

    def _create_mission_from_data(self, data: Dict[str, Any]) -> SpaceMission:
        """Create a mission from data dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            Mission data

        Returns
        -------
        SpaceMission
            Created mission
        """
        return SpaceMission(
            mission_id=data.get("quest_id", ""),
            name=data.get("name", ""),
            mission_type=data.get("quest_type", ""),
            description=data.get("description", ""),
            status=data.get("status", "available"),
            location=data.get("start_location", ""),
            target_location=data.get("target_location"),
            credits=data.get("credits", 0),
            experience=data.get("experience", 0),
            requirements=data.get("requirements", {}),
            steps=data.get("steps", []),
            current_step=data.get("current_step", 0),
            start_time=data.get("start_time"),
            completion_time=data.get("completion_time")
        )

    def get_available_missions(self, location: str = None) -> List[SpaceMission]:
        """Get available missions at a location.

        Parameters
        ----------
        location : str, optional
            Location to filter missions

        Returns
        -------
        List[SpaceMission]
            Available missions
        """
        available_missions = []
        
        # Load missions from data file
        missions_file = Path("data/space_quests/space_quests.json")
        if missions_file.exists():
            try:
                with missions_file.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    for mission_data in data.get("quests", []):
                        if mission_data.get("status") == "available":
                            mission = self._create_mission_from_data(mission_data)
                            if not location or mission.location == location:
                                available_missions.append(mission)
            except Exception as e:
                log_event(f"[SPACE] Error loading available missions: {e}")

        log_event(f"[SPACE] Found {len(available_missions)} available missions")
        return available_missions

    def accept_mission(self, mission_id: str) -> bool:
        """Accept a mission.

        Parameters
        ----------
        mission_id : str
            ID of mission to accept

        Returns
        -------
        bool
            True if mission was accepted successfully
        """
        # Find the mission
        available_missions = self.get_available_missions()
        mission = next((m for m in available_missions if m.mission_id == mission_id), None)
        
        if not mission:
            log_event(f"[SPACE] Mission {mission_id} not found")
            return False

        # Check requirements
        if not self._check_mission_requirements(mission):
            log_event(f"[SPACE] Requirements not met for mission {mission_id}")
            return False

        # Accept the mission
        mission.status = "active"
        mission.start_time = time.time()
        mission.current_step = 0
        
        self.active_missions[mission_id] = mission
        
        log_event(f"[SPACE] Accepted mission: {mission.name}")
        return True

    def _check_mission_requirements(self, mission: SpaceMission) -> bool:
        """Check if requirements are met for a mission.

        Parameters
        ----------
        mission : SpaceMission
            Mission to check

        Returns
        -------
        bool
            True if requirements are met
        """
        # Load ship configuration
        ship_config = self._load_ship_config()
        
        # Check ship requirements
        if mission.requirements.get("ship"):
            if not ship_config.get("ships"):
                log_event("[SPACE] No ships available")
                return False
        
        # Check combat rating requirements
        required_combat = mission.requirements.get("combat_rating", 0)
        if required_combat > 0:
            # This would check actual combat rating
            current_combat = 1  # Placeholder
            if current_combat < required_combat:
                log_event(f"[SPACE] Combat rating too low: {current_combat} < {required_combat}")
                return False
        
        return True

    def _load_ship_config(self) -> Dict[str, Any]:
        """Load ship configuration."""
        ship_config_file = Path("data/ship_config.json")
        if ship_config_file.exists():
            try:
                with ship_config_file.open("r", encoding="utf-8") as fh:
                    return json.load(fh)
            except Exception as e:
                log_event(f"[SPACE] Error loading ship config: {e}")
        
        return {}

    def get_active_missions(self) -> List[SpaceMission]:
        """Get currently active missions.

        Returns
        -------
        List[SpaceMission]
            Active missions
        """
        return list(self.active_missions.values())

    def update_mission_progress(self, mission_id: str, step_completed: bool = True) -> bool:
        """Update mission progress.

        Parameters
        ----------
        mission_id : str
            ID of mission to update
        step_completed : bool
            Whether current step was completed

        Returns
        -------
        bool
            True if mission was updated successfully
        """
        if mission_id not in self.active_missions:
            log_event(f"[SPACE] Mission {mission_id} not active")
            return False

        mission = self.active_missions[mission_id]
        
        if step_completed:
            mission.current_step += 1
            
            # Check if mission is complete
            if mission.current_step >= len(mission.steps):
                mission.status = "completed"
                mission.completion_time = time.time()
                
                # Move to completed missions
                self.completed_missions.append(mission)
                del self.active_missions[mission_id]
                
                log_event(f"[SPACE] Mission completed: {mission.name}")
            else:
                log_event(f"[SPACE] Mission progress: {mission.current_step}/{len(mission.steps)}")
        
        return True

    def get_mission_by_type(self, mission_type: str) -> List[SpaceMission]:
        """Get missions of a specific type.

        Parameters
        ----------
        mission_type : str
            Type of missions to get

        Returns
        -------
        List[SpaceMission]
            Missions of specified type
        """
        if mission_type not in self.mission_types:
            log_event(f"[SPACE] Unknown mission type: {mission_type}")
            return []

        # Get available missions of this type
        available_missions = self.get_available_missions()
        type_missions = [m for m in available_missions if m.mission_type == mission_type]
        
        log_event(f"[SPACE] Found {len(type_missions)} {mission_type} missions")
        return type_missions

    def get_preferred_missions(self) -> List[SpaceMission]:
        """Get missions of preferred types.

        Returns
        -------
        List[SpaceMission]
            Preferred missions
        """
        preferred_types = self.space_config.get("preferred_mission_types", [])
        preferred_missions = []
        
        for mission_type in preferred_types:
            type_missions = self.get_mission_by_type(mission_type)
            preferred_missions.extend(type_missions)
        
        return preferred_missions

    def create_mission_steps(self, mission_type: str, location: str) -> List[MissionStep]:
        """Create mission steps for a mission type.

        Parameters
        ----------
        mission_type : str
            Type of mission
        location : str
            Mission location

        Returns
        -------
        List[MissionStep]
            Mission steps
        """
        if mission_type not in self.mission_types:
            return []

        mission_config = self.mission_types[mission_type]
        steps = []
        
        for i, step_type in enumerate(mission_config["steps"]):
            step = MissionStep(
                step_id=i,
                step_type=step_type,
                description=f"Step {i+1}: {step_type}",
                location=location,
                target=None,
                requirements={},
                completed=False
            )
            steps.append(step)
        
        return steps

    def get_mission_statistics(self) -> Dict[str, Any]:
        """Get mission statistics.

        Returns
        -------
        Dict[str, Any]
            Mission statistics
        """
        total_missions = len(self.active_missions) + len(self.completed_missions)
        total_credits = sum(m.credits for m in self.completed_missions)
        total_experience = sum(m.experience for m in self.completed_missions)
        
        mission_types = {}
        for mission in self.completed_missions:
            mission_types[mission.mission_type] = mission_types.get(mission.mission_type, 0) + 1
        
        return {
            "total_missions": total_missions,
            "active_missions": len(self.active_missions),
            "completed_missions": len(self.completed_missions),
            "total_credits": total_credits,
            "total_experience": total_experience,
            "mission_types": mission_types
        } 
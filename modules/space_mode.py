"""Space Mode Handler for Batch 062.

This module provides space mission mode functionality including:
- Integration with SpaceMissionManager
- Space mission execution
- Ship management
- Terminal interactions
- Combat simulation
"""

import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

from core.space_mission_manager import (
    SpaceMissionManager, 
    SpaceMissionType, 
    space_mission_manager
)
from utils.logging_utils import log_event


class SpaceMode:
    """Space mission mode handler."""
    
    def __init__(self):
        """Initialize space mode."""
        self.manager = space_mission_manager
        self.current_mission = None
        self.mission_history = []
        
        # Load space mode configuration
        self.config = self._load_space_config()
        
        log_event("[SPACE MODE] Space mode initialized")
    
    def _load_space_config(self) -> Dict[str, Any]:
        """Load space mode configuration."""
        config_path = Path("config/session_config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("space_mode", {})
            except Exception as e:
                log_event(f"[SPACE MODE] Failed to load config: {e}")
        
        return {}
    
    def run(self, profile: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Run space mode.
        
        Parameters
        ----------
        profile : Dict[str, Any], optional
            Runtime profile
        **kwargs
            Additional parameters
            
        Returns
        -------
        Dict[str, Any]
            Mode execution results
        """
        log_event("[SPACE MODE] Starting space mode execution")
        
        if not self.config.get("enabled", False):
            log_event("[SPACE MODE] Space mode is disabled in config")
            return {"status": "disabled", "message": "Space mode is disabled"}
        
        results = {
            "status": "success",
            "missions_processed": 0,
            "combat_simulations": 0,
            "ship_operations": 0,
            "terminal_interactions": 0,
            "events_detected": 0
        }
        
        try:
            # Check for available missions
            preferred_types = self.config.get("preferred_mission_types", [])
            available_missions = self.manager.get_available_missions(preferred_types)
            
            if not available_missions:
                log_event("[SPACE MODE] No available missions found")
                results["status"] = "no_missions"
                return results
            
            # Process missions
            for mission in available_missions[:3]:  # Limit to 3 missions per run
                mission_result = self._process_mission(mission)
                results["missions_processed"] += 1
                
                if mission_result.get("combat_simulated"):
                    results["combat_simulations"] += 1
                
                if mission_result.get("ship_operations"):
                    results["ship_operations"] += mission_result["ship_operations"]
                
                if mission_result.get("terminal_interactions"):
                    results["terminal_interactions"] += mission_result["terminal_interactions"]
            
            # Simulate some space events for testing
            self._simulate_space_events()
            results["events_detected"] = 5  # Simulated events
            
            log_event(f"[SPACE MODE] Completed with {results['missions_processed']} missions processed")
            
        except Exception as e:
            log_event(f"[SPACE MODE] Error during execution: {e}")
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    def _process_mission(self, mission) -> Dict[str, Any]:
        """Process a single space mission.
        
        Parameters
        ----------
        mission : SpaceMission
            Mission to process
            
        Returns
        -------
        Dict[str, Any]
            Mission processing results
        """
        log_event(f"[SPACE MODE] Processing mission: {mission.name}")
        
        result = {
            "mission_id": mission.mission_id,
            "mission_name": mission.name,
            "status": "processed",
            "combat_simulated": False,
            "ship_operations": 0,
            "terminal_interactions": 0
        }
        
        # Accept the mission
        if self.manager.accept_mission(mission.mission_id):
            result["accepted"] = True
            
            # Enter ship if required
            if mission.ship_requirement:
                if self.manager.enter_ship(mission.ship_requirement):
                    result["ship_operations"] += 1
                    log_event(f"[SPACE MODE] Entered ship: {mission.ship_requirement}")
            
            # Simulate mission steps based on type
            if mission.mission_type == SpaceMissionType.PATROL:
                result.update(self._simulate_patrol_mission(mission))
            elif mission.mission_type == SpaceMissionType.ESCORT:
                result.update(self._simulate_escort_mission(mission))
            elif mission.mission_type == SpaceMissionType.KILL_TARGET:
                result.update(self._simulate_kill_target_mission(mission))
            else:
                result.update(self._simulate_generic_mission(mission))
            
            # Complete the mission
            if self.manager.complete_mission(mission.mission_id):
                result["completed"] = True
                log_event(f"[SPACE MODE] Completed mission: {mission.name}")
            
            # Exit ship if we entered one
            if mission.ship_requirement and self.manager.current_ship:
                if self.manager.exit_ship():
                    result["ship_operations"] += 1
                    log_event(f"[SPACE MODE] Exited ship: {mission.ship_requirement}")
        
        return result
    
    def _simulate_patrol_mission(self, mission) -> Dict[str, Any]:
        """Simulate a patrol mission.
        
        Parameters
        ----------
        mission : SpaceMission
            Patrol mission to simulate
            
        Returns
        -------
        Dict[str, Any]
            Patrol simulation results
        """
        log_event(f"[SPACE MODE] Simulating patrol mission: {mission.name}")
        
        result = {
            "patrol_points": 3,
            "combat_encounters": 0,
            "combat_simulated": False
        }
        
        # Simulate patrol route
        patrol_points = ["Alpha Sector", "Beta Sector", "Gamma Sector"]
        
        for i, point in enumerate(patrol_points):
            log_event(f"[SPACE MODE] Patrolling {point} ({i+1}/{len(patrol_points)})")
            time.sleep(0.5)  # Simulate travel time
            
            # Random combat encounter
            if hash(f"{mission.mission_id}{i}") % 100 < 30:  # 30% chance
                combat_result = self.manager.simulate_combat(f"Pirate at {point}")
                result["combat_encounters"] += 1
                result["combat_simulated"] = True
                
                if combat_result["status"] == "victory":
                    log_event(f"[SPACE MODE] Defeated pirates at {point}")
                else:
                    log_event(f"[SPACE MODE] Lost combat at {point}")
        
        return result
    
    def _simulate_escort_mission(self, mission) -> Dict[str, Any]:
        """Simulate an escort mission.
        
        Parameters
        ----------
        mission : SpaceMission
            Escort mission to simulate
            
        Returns
        -------
        Dict[str, Any]
            Escort simulation results
        """
        log_event(f"[SPACE MODE] Simulating escort mission: {mission.name}")
        
        result = {
            "escort_target": "Merchant Vessel",
            "escort_distance": "3 sectors",
            "combat_encounters": 0,
            "combat_simulated": False,
            "escort_successful": True
        }
        
        # Simulate escort route
        escort_points = ["Departure", "Mid-point", "Destination"]
        
        for i, point in enumerate(escort_points):
            log_event(f"[SPACE MODE] Escorting to {point} ({i+1}/{len(escort_points)})")
            time.sleep(0.5)  # Simulate travel time
            
            # Random attack on escort
            if hash(f"{mission.mission_id}{i}") % 100 < 40:  # 40% chance
                combat_result = self.manager.simulate_combat(f"Raider at {point}")
                result["combat_encounters"] += 1
                result["combat_simulated"] = True
                
                if combat_result["status"] == "victory":
                    log_event(f"[SPACE MODE] Protected escort at {point}")
                else:
                    log_event(f"[SPACE MODE] Escort damaged at {point}")
                    result["escort_successful"] = False
        
        return result
    
    def _simulate_kill_target_mission(self, mission) -> Dict[str, Any]:
        """Simulate a kill target mission.
        
        Parameters
        ----------
        mission : SpaceMission
            Kill target mission to simulate
            
        Returns
        -------
        Dict[str, Any]
            Kill target simulation results
        """
        log_event(f"[SPACE MODE] Simulating kill target mission: {mission.name}")
        
        result = {
            "target_name": "Wanted Criminal",
            "target_location": "Asteroid Belt",
            "combat_simulated": True,
            "target_eliminated": True
        }
        
        # Simulate target location
        log_event(f"[SPACE MODE] Locating target in {result['target_location']}")
        time.sleep(0.5)  # Simulate search time
        
        # Combat with target
        combat_result = self.manager.simulate_combat(result["target_name"])
        
        if combat_result["status"] == "victory":
            log_event(f"[SPACE MODE] Successfully eliminated target: {result['target_name']}")
            result["target_eliminated"] = True
        else:
            log_event(f"[SPACE MODE] Failed to eliminate target: {result['target_name']}")
            result["target_eliminated"] = False
        
        return result
    
    def _simulate_generic_mission(self, mission) -> Dict[str, Any]:
        """Simulate a generic mission.
        
        Parameters
        ----------
        mission : SpaceMission
            Generic mission to simulate
            
        Returns
        -------
        Dict[str, Any]
            Generic simulation results
        """
        log_event(f"[SPACE MODE] Simulating generic mission: {mission.name}")
        
        result = {
            "mission_type": mission.mission_type.value,
            "combat_simulated": False,
            "steps_completed": 0
        }
        
        # Simulate basic mission steps
        steps = ["Travel to location", "Complete objective", "Return to station"]
        
        for i, step in enumerate(steps):
            log_event(f"[SPACE MODE] Mission step {i+1}: {step}")
            time.sleep(0.3)  # Simulate step completion time
            result["steps_completed"] += 1
            
            # Random combat during mission
            if hash(f"{mission.mission_id}{i}") % 100 < 20:  # 20% chance
                combat_result = self.manager.simulate_combat("Enemy vessel")
                result["combat_simulated"] = True
        
        return result
    
    def _simulate_space_events(self):
        """Simulate space events for testing."""
        log_event("[SPACE MODE] Simulating space events for testing")
        
        # Simulate various space events
        test_events = [
            "Entering ship x-wing",
            "Mission accepted: Patrol Sector Alpha",
            "Combat started with pirate vessel",
            "Terminal accessed: Mission Board",
            "Exiting ship x-wing"
        ]
        
        for event_text in test_events:
            detected_events = self.manager.detect_space_events(event_text)
            if detected_events:
                log_event(f"[SPACE MODE] Detected event: {event_text}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current space mode status.
        
        Returns
        -------
        Dict[str, Any]
            Current space mode status
        """
        return {
            "mode": "space",
            "enabled": self.config.get("enabled", False),
            "current_mission": self.current_mission.mission_id if self.current_mission else None,
            "available_missions": len(self.manager.get_available_missions()),
            "current_ship": self.manager.current_ship,
            "current_location": self.manager.current_location,
            "mission_history": len(self.mission_history)
        }


# Create global instance
space_mode = SpaceMode() 
"""Main space quest support module integrating all components."""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from utils.logging_utils import log_event

from .hyperspace_pathing import HyperspacePathingSimulator, NavigationRequest, HyperspaceRouteType
from .mission_locations import MissionLocationManager, MissionLocationType
from .ship_upgrades import ShipUpgradeManager, ShipTier
from .ai_piloting import AIPilotingFoundation, PilotSkill, MissionType


@dataclass
class SpaceQuestSession:
    """Represents a space quest session with all components."""
    session_id: str
    start_time: float
    current_location: str
    active_mission: Optional[str] = None
    active_pilot: Optional[str] = None
    current_ship: Optional[str] = None
    session_stats: Dict[str, Any] = None


class SpaceQuestSupport:
    """Main space quest support system integrating all components."""
    
    def __init__(self, config_path: str = "config/space_config.json"):
        """Initialize the space quest support system.
        
        Parameters
        ----------
        config_path : str
            Path to space configuration file
        """
        # Initialize all components
        self.hyperspace_pathing = HyperspacePathingSimulator(config_path)
        self.mission_locations = MissionLocationManager(config_path)
        self.ship_upgrades = ShipUpgradeManager(config_path)
        self.ai_piloting = AIPilotingFoundation(config_path)
        
        # Session management
        self.current_session: Optional[SpaceQuestSession] = None
        self.session_history: List[SpaceQuestSession] = []
        
        # Integration state
        self.last_integration_update = time.time()
        self.integration_stats: Dict[str, Any] = {}
    
    def start_session(self, location: str = "Corellia Starport") -> str:
        """Start a new space quest session.
        
        Parameters
        ----------
        location : str
            Starting location for the session
            
        Returns
        -------
        str
            Session ID
        """
        session_id = f"space_session_{int(time.time())}"
        
        self.current_session = SpaceQuestSession(
            session_id=session_id,
            start_time=time.time(),
            current_location=location,
            session_stats={
                "missions_completed": 0,
                "credits_earned": 0,
                "experience_gained": 0,
                "ships_unlocked": 0,
                "upgrades_installed": 0,
                "pilots_activated": 0
            }
        )
        
        # Set current location in hyperspace pathing
        self.hyperspace_pathing.current_location = location
        
        log_event(f"[SPACE_QUEST] Started session {session_id} at {location}")
        return session_id
    
    def end_session(self) -> Dict[str, Any]:
        """End the current space quest session.
        
        Returns
        -------
        Dict[str, Any]
            Session summary
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        session = self.current_session
        session.end_time = time.time()
        session.duration = session.end_time - session.start_time
        
        # Add to history
        self.session_history.append(session)
        
        # Generate summary
        summary = {
            "session_id": session.session_id,
            "duration": session.duration,
            "start_location": session.current_location,
            "stats": session.session_stats,
            "components_used": self._get_component_usage()
        }
        
        log_event(f"[SPACE_QUEST] Ended session {session.session_id}")
        self.current_session = None
        
        return summary
    
    def _get_component_usage(self) -> Dict[str, Any]:
        """Get usage statistics for all components."""
        return {
            "hyperspace_pathing": {
                "routes_calculated": len(self.hyperspace_pathing.navigation_history),
                "current_location": self.hyperspace_pathing.current_location
            },
            "mission_locations": {
                "locations_visited": len([loc for loc in self.mission_locations.locations.values() if loc.last_visited]),
                "missions_accepted": len(self.mission_locations.available_missions)
            },
            "ship_upgrades": {
                "ships_unlocked": len(self.ship_upgrades.get_unlocked_ships()),
                "upgrades_installed": sum(1 for upgrade in self.ship_upgrades.upgrades.values() if upgrade.is_installed)
            },
            "ai_piloting": {
                "active_pilots": len(self.ai_piloting.get_active_pilots()),
                "missions_completed": sum(1 for mission in self.ai_piloting.missions.values() if mission.status == "completed")
            }
        }
    
    def navigate_to_location(self, destination: str, route_type: str = "direct") -> Dict[str, Any]:
        """Navigate to a specific location using hyperspace pathing.
        
        Parameters
        ----------
        destination : str
            Destination location
        route_type : str
            Type of route to use
            
        Returns
        -------
        Dict[str, Any]
            Navigation result
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        # Create navigation request
        request = NavigationRequest(
            start_location=self.current_session.current_location,
            destination=destination,
            route_type=HyperspaceRouteType(route_type),
            ship_class="Basic Fighter",  # This would come from current ship
            fuel_capacity=100.0,
            max_risk_tolerance=0.5
        )
        
        # Calculate route
        result = self.hyperspace_pathing.calculate_route(request)
        
        if not result:
            return {"error": "No route found to destination"}
        
        # Start navigation
        self.hyperspace_pathing.start_navigation(result)
        
        # Update session
        self.current_session.current_location = destination
        
        return {
            "success": True,
            "destination": destination,
            "route": {
                "total_distance": result.total_distance,
                "total_time": result.total_time,
                "total_fuel_cost": result.total_fuel_cost,
                "waypoints": result.waypoints,
                "warnings": result.warnings
            }
        }
    
    def visit_mission_location(self, location_name: str) -> Dict[str, Any]:
        """Visit a mission location and interact with mission givers.
        
        Parameters
        ----------
        location_name : str
            Name of the location to visit
            
        Returns
        -------
        Dict[str, Any]
            Location visit result
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        # Mark location as visited
        self.mission_locations.visit_location(location_name)
        
        # Get location information
        location = self.mission_locations.get_location(location_name)
        if not location:
            return {"error": "Location not found"}
        
        # Get mission givers at location
        givers = self.mission_locations.get_mission_givers_at_location(location_name)
        
        return {
            "success": True,
            "location": {
                "name": location.name,
                "type": location.location_type.value,
                "zone": location.zone,
                "security_level": location.security_level,
                "facilities": location.facilities
            },
            "mission_givers": [
                {
                    "name": giver.name,
                    "faction": giver.faction,
                    "mission_types": giver.mission_types,
                    "reputation_required": giver.reputation_required,
                    "current_reputation": giver.current_reputation
                }
                for giver in givers
            ]
        }
    
    def interact_with_giver(self, giver_name: str) -> Dict[str, Any]:
        """Interact with a mission giver to get available missions.
        
        Parameters
        ----------
        giver_name : str
            Name of the mission giver
            
        Returns
        -------
        Dict[str, Any]
            Interaction result with available missions
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        return self.mission_locations.interact_with_giver(giver_name)
    
    def accept_mission(self, mission_id: str, giver_name: str) -> Dict[str, Any]:
        """Accept a mission from a mission giver.
        
        Parameters
        ----------
        mission_id : str
            ID of the mission to accept
        giver_name : str
            Name of the mission giver
            
        Returns
        -------
        Dict[str, Any]
            Mission acceptance result
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        result = self.mission_locations.accept_mission(mission_id, giver_name)
        
        if result.get("success"):
            self.current_session.active_mission = mission_id
            self.current_session.session_stats["missions_completed"] += 1
        
        return result
    
    def unlock_ship(self, ship_name: str, player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to unlock a ship class.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship to unlock
        player_stats : Dict[str, Any]
            Player statistics for requirement checking
            
        Returns
        -------
        Dict[str, Any]
            Ship unlock result
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        success = self.ship_upgrades.unlock_ship(ship_name, player_stats)
        
        if success:
            self.current_session.session_stats["ships_unlocked"] += 1
            self.current_session.current_ship = ship_name
        
        return {
            "success": success,
            "ship_name": ship_name,
            "unlocked": success
        }
    
    def install_upgrade(self, ship_name: str, upgrade_id: str, slot_id: str) -> Dict[str, Any]:
        """Install an upgrade on a ship.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship
        upgrade_id : str
            ID of the upgrade to install
        slot_id : str
            ID of the slot to install in
            
        Returns
        -------
        Dict[str, Any]
            Upgrade installation result
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        result = self.ship_upgrades.install_upgrade(ship_name, upgrade_id, slot_id)
        
        if result.get("success"):
            self.current_session.session_stats["upgrades_installed"] += 1
        
        return result
    
    def activate_pilot(self, pilot_id: str) -> Dict[str, Any]:
        """Activate an AI pilot for automated missions.
        
        Parameters
        ----------
        pilot_id : str
            ID of the pilot to activate
            
        Returns
        -------
        Dict[str, Any]
            Pilot activation result
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        success = self.ai_piloting.activate_pilot(pilot_id)
        
        if success:
            self.current_session.active_pilot = pilot_id
            self.current_session.session_stats["pilots_activated"] += 1
        
        pilot = self.ai_piloting.get_pilot(pilot_id)
        
        return {
            "success": success,
            "pilot_name": pilot.name if pilot else "Unknown",
            "pilot_id": pilot_id,
            "activated": success
        }
    
    def assign_ai_mission(self, pilot_id: str, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a mission to an AI pilot.
        
        Parameters
        ----------
        pilot_id : str
            ID of the pilot to assign mission to
        mission_data : Dict[str, Any]
            Mission data
            
        Returns
        -------
        Dict[str, Any]
            Mission assignment result
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        mission_id = self.ai_piloting.assign_mission(pilot_id, mission_data)
        
        if mission_id:
            return {
                "success": True,
                "mission_id": mission_id,
                "pilot_id": pilot_id
            }
        else:
            return {"error": "Failed to assign mission"}
    
    def start_ai_mission(self, mission_id: str) -> Dict[str, Any]:
        """Start an AI pilot mission.
        
        Parameters
        ----------
        mission_id : str
            ID of the mission to start
            
        Returns
        -------
        Dict[str, Any]
            Mission start result
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        success = self.ai_piloting.start_mission(mission_id)
        
        return {
            "success": success,
            "mission_id": mission_id,
            "started": success
        }
    
    def update_ai_mission(self, mission_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update AI mission progress.
        
        Parameters
        ----------
        mission_id : str
            ID of the mission to update
        progress_data : Dict[str, Any]
            Progress data and events
            
        Returns
        -------
        Dict[str, Any]
            Mission update result
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        return self.ai_piloting.update_mission_progress(mission_id, progress_data)
    
    def complete_ai_mission(self, mission_id: str) -> Dict[str, Any]:
        """Complete an AI pilot mission.
        
        Parameters
        ----------
        mission_id : str
            ID of the mission to complete
            
        Returns
        -------
        Dict[str, Any]
            Mission completion result
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        result = self.ai_piloting.complete_mission(mission_id)
        
        if result.get("success"):
            self.current_session.session_stats["missions_completed"] += 1
            self.current_session.session_stats["experience_gained"] += result.get("experience_gain", 0)
        
        return result
    
    def get_available_destinations(self, from_location: str = None) -> List[Dict[str, Any]]:
        """Get available destinations from current or specified location.
        
        Parameters
        ----------
        from_location : str, optional
            Starting location, uses current session location if None
            
        Returns
        -------
        List[Dict[str, Any]]
            List of available destinations
        """
        if from_location is None:
            if not self.current_session:
                return []
            from_location = self.current_session.current_location
        
        return self.hyperspace_pathing.get_available_destinations(from_location)
    
    def get_mission_locations(self, location_type: str = None) -> List[Dict[str, Any]]:
        """Get available mission locations.
        
        Parameters
        ----------
        location_type : str, optional
            Filter by location type
            
        Returns
        -------
        List[Dict[str, Any]]
            List of mission locations
        """
        if location_type:
            locations = self.mission_locations.get_locations_by_type(MissionLocationType(location_type))
        else:
            locations = self.mission_locations.get_available_locations()
        
        return [
            {
                "name": loc.name,
                "type": loc.location_type.value,
                "zone": loc.zone,
                "security_level": loc.security_level,
                "available_missions": loc.available_missions,
                "facilities": loc.facilities
            }
            for loc in locations
        ]
    
    def get_available_ships(self) -> List[Dict[str, Any]]:
        """Get available ship classes.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of available ships
        """
        ships = self.ship_upgrades.get_available_ships()
        
        return [
            {
                "name": ship.name,
                "ship_type": ship.ship_type,
                "base_tier": ship.base_tier.value,
                "max_tier": ship.max_tier.value,
                "is_unlocked": ship.is_unlocked,
                "upgrade_slots": {slot_type.value: count for slot_type, count in ship.upgrade_slots.items()}
            }
            for ship in ships
        ]
    
    def get_available_upgrades(self, ship_name: str) -> List[Dict[str, Any]]:
        """Get available upgrades for a ship.
        
        Parameters
        ----------
        ship_name : str
            Name of the ship
            
        Returns
        -------
        List[Dict[str, Any]]
            List of available upgrades
        """
        upgrades = self.ship_upgrades.get_available_upgrades(ship_name)
        
        return [
            {
                "upgrade_id": upgrade.upgrade_id,
                "name": upgrade.name,
                "upgrade_type": upgrade.upgrade_type.value,
                "rarity": upgrade.rarity.value,
                "tier": upgrade.tier.value,
                "description": upgrade.description,
                "stats": upgrade.stats,
                "cost": upgrade.cost
            }
            for upgrade in upgrades
        ]
    
    def get_available_pilots(self, skill: str = None, min_level: int = 1) -> List[Dict[str, Any]]:
        """Get available AI pilots.
        
        Parameters
        ----------
        skill : str, optional
            Filter by skill
        min_level : int
            Minimum skill level required
            
        Returns
        -------
        List[Dict[str, Any]]
            List of available pilots
        """
        if skill:
            pilots = self.ai_piloting.get_pilots_by_skill(PilotSkill(skill), min_level)
        else:
            pilots = self.ai_piloting.get_available_pilots()
        
        return [
            {
                "pilot_id": pilot.pilot_id,
                "name": pilot.name,
                "skill_levels": {skill.value: level for skill, level in pilot.skill_levels.items()},
                "behavior": pilot.behavior.value,
                "experience": pilot.experience,
                "is_active": pilot.is_active
            }
            for pilot in pilots
        ]
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status.
        
        Returns
        -------
        Dict[str, Any]
            Current session status
        """
        if not self.current_session:
            return {"status": "no_active_session"}
        
        session = self.current_session
        
        return {
            "session_id": session.session_id,
            "current_location": session.current_location,
            "active_mission": session.active_mission,
            "active_pilot": session.active_pilot,
            "current_ship": session.current_ship,
            "session_stats": session.session_stats,
            "duration": time.time() - session.start_time if session.start_time else 0
        }
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics for all components.
        
        Returns
        -------
        Dict[str, Any]
            Integration statistics
        """
        return {
            "hyperspace_pathing": {
                "total_nodes": len(self.hyperspace_pathing.nodes),
                "total_routes": len(self.hyperspace_pathing.routes),
                "navigation_history": len(self.hyperspace_pathing.navigation_history),
                "current_location": self.hyperspace_pathing.current_location
            },
            "mission_locations": self.mission_locations.get_location_statistics(),
            "ship_upgrades": self.ship_upgrades.get_upgrade_statistics(),
            "ai_piloting": self.ai_piloting.get_ai_piloting_statistics(),
            "session": {
                "current_session": self.current_session.session_id if self.current_session else None,
                "total_sessions": len(self.session_history)
            }
        }
    
    def save_session_data(self, filepath: str = None) -> bool:
        """Save current session data to file.
        
        Parameters
        ----------
        filepath : str, optional
            Path to save file, uses default if None
            
        Returns
        -------
        bool
            True if save successful
        """
        if not self.current_session:
            return False
        
        if filepath is None:
            filepath = f"data/space_quests/session_{self.current_session.session_id}.json"
        
        try:
            data = {
                "session": {
                    "session_id": self.current_session.session_id,
                    "start_time": self.current_session.start_time,
                    "current_location": self.current_session.current_location,
                    "active_mission": self.current_session.active_mission,
                    "active_pilot": self.current_session.active_pilot,
                    "current_ship": self.current_session.current_ship,
                    "session_stats": self.current_session.session_stats
                },
                "integration_stats": self.get_integration_statistics()
            }
            
            # Ensure directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            log_event(f"[SPACE_QUEST] Saved session data to {filepath}")
            return True
            
        except Exception as e:
            log_event(f"[SPACE_QUEST] Error saving session data: {e}")
            return False
    
    def load_session_data(self, filepath: str) -> bool:
        """Load session data from file.
        
        Parameters
        ----------
        filepath : str
            Path to load file from
            
        Returns
        -------
        bool
            True if load successful
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            session_data = data.get("session", {})
            
            self.current_session = SpaceQuestSession(
                session_id=session_data.get("session_id", f"loaded_session_{int(time.time())}"),
                start_time=session_data.get("start_time", time.time()),
                current_location=session_data.get("current_location", "Corellia Starport"),
                active_mission=session_data.get("active_mission"),
                active_pilot=session_data.get("active_pilot"),
                current_ship=session_data.get("current_ship"),
                session_stats=session_data.get("session_stats", {})
            )
            
            # Update hyperspace pathing current location
            self.hyperspace_pathing.current_location = self.current_session.current_location
            
            log_event(f"[SPACE_QUEST] Loaded session data from {filepath}")
            return True
            
        except Exception as e:
            log_event(f"[SPACE_QUEST] Error loading session data: {e}")
            return False 
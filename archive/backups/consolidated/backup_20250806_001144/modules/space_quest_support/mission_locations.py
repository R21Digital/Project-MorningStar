"""Mission location manager for specific space mission locations."""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from utils.logging_utils import log_event


class MissionLocationType(Enum):
    """Types of mission locations."""
    STARPORT = "starport"
    ORBITAL_STATION = "orbital_station"
    SPACE_STATION = "space_station"
    DEEP_SPACE_OUTPOST = "deep_space_outpost"
    PIRATE_HAVEN = "pirate_haven"


class MissionDifficulty(Enum):
    """Mission difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"
    LEGENDARY = "legendary"


@dataclass
class MissionLocation:
    """Represents a specific mission location."""
    name: str
    location_type: MissionLocationType
    zone: str
    coordinates: tuple
    security_level: float  # 0.0 (safe) to 1.0 (dangerous)
    available_missions: List[str]
    mission_givers: List[str]
    facilities: List[str]
    restrictions: Dict[str, Any]
    last_visited: Optional[float] = None
    mission_rotation: Optional[float] = None  # hours


@dataclass
class MissionGiver:
    """Represents a mission giver at a location."""
    name: str
    faction: str
    mission_types: List[str]
    reputation_required: int
    current_reputation: int
    available_missions: List[str]
    last_interaction: Optional[float] = None


@dataclass
class LocationMission:
    """Represents a mission available at a specific location."""
    mission_id: str
    name: str
    description: str
    difficulty: MissionDifficulty
    mission_type: str
    location: str
    giver: str
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    reputation_gain: int
    faction_standing: str
    time_limit: Optional[float] = None  # in hours


class MissionLocationManager:
    """Manage specific mission locations and their missions."""
    
    def __init__(self, config_path: str = "config/space_config.json"):
        """Initialize the mission location manager.
        
        Parameters
        ----------
        config_path : str
            Path to space configuration file
        """
        self.config = self._load_config(config_path)
        self.locations: Dict[str, MissionLocation] = {}
        self.mission_givers: Dict[str, MissionGiver] = {}
        self.available_missions: Dict[str, LocationMission] = {}
        
        # Load location data
        self._load_location_data()
        self._initialize_specific_locations()
        
        # Mission rotation tracking
        self.mission_rotation_timer = time.time()
        self.rotation_interval = 3600  # 1 hour
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load space configuration."""
        path = Path(config_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _load_location_data(self) -> None:
        """Load mission location data."""
        data_file = Path("data/space_quests/mission_locations.json")
        if data_file.exists():
            try:
                with data_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._parse_location_data(data)
            except Exception as e:
                log_event(f"[MISSION_LOCATIONS] Error loading location data: {e}")
    
    def _parse_location_data(self, data: Dict[str, Any]) -> None:
        """Parse mission location data from JSON."""
        # Parse locations
        for location_data in data.get("locations", []):
            location = MissionLocation(
                name=location_data["name"],
                location_type=MissionLocationType(location_data["location_type"]),
                zone=location_data["zone"],
                coordinates=tuple(location_data["coordinates"]),
                security_level=location_data["security_level"],
                available_missions=location_data.get("available_missions", []),
                mission_givers=location_data.get("mission_givers", []),
                facilities=location_data.get("facilities", []),
                restrictions=location_data.get("restrictions", {}),
                last_visited=location_data.get("last_visited"),
                mission_rotation=location_data.get("mission_rotation")
            )
            self.locations[location.name] = location
        
        # Parse mission givers
        for giver_data in data.get("mission_givers", []):
            giver = MissionGiver(
                name=giver_data["name"],
                faction=giver_data["faction"],
                mission_types=giver_data["mission_types"],
                reputation_required=giver_data["reputation_required"],
                current_reputation=giver_data.get("current_reputation", 0),
                available_missions=giver_data.get("available_missions", []),
                last_interaction=giver_data.get("last_interaction")
            )
            self.mission_givers[giver.name] = giver
    
    def _initialize_specific_locations(self) -> None:
        """Initialize specific mission locations."""
        # Corellia Starport
        corellia_starport = MissionLocation(
            name="Corellia Starport",
            location_type=MissionLocationType.STARPORT,
            zone="corellia_sector",
            coordinates=(100.0, 200.0, 50.0),
            security_level=0.2,
            available_missions=["patrol", "escort", "delivery", "combat"],
            mission_givers=["Commander Tarkin", "Captain Solo", "Lieutenant Organa"],
            facilities=["shipyard", "fuel_station", "repair_bay", "mission_terminal"],
            restrictions={"faction_standing": "neutral"},
            mission_rotation=4.0  # 4 hours
        )
        self.locations["Corellia Starport"] = corellia_starport
        
        # Naboo Orbital
        naboo_orbital = MissionLocation(
            name="Naboo Orbital",
            location_type=MissionLocationType.ORBITAL_STATION,
            zone="naboo_sector",
            coordinates=(150.0, 250.0, 75.0),
            security_level=0.1,
            available_missions=["patrol", "escort", "diplomatic", "exploration"],
            mission_givers=["Ambassador Amidala", "Captain Panaka", "Commander Typho"],
            facilities=["diplomatic_quarters", "mission_terminal", "fuel_station", "medical_bay"],
            restrictions={"faction_standing": "republic"},
            mission_rotation=6.0  # 6 hours
        )
        self.locations["Naboo Orbital"] = naboo_orbital
        
        # Initialize mission givers for these locations
        self._initialize_mission_givers()
    
    def _initialize_mission_givers(self) -> None:
        """Initialize mission givers for specific locations."""
        # Corellia Starport mission givers
        commander_tarkin = MissionGiver(
            name="Commander Tarkin",
            faction="imperial",
            mission_types=["combat", "patrol", "escort"],
            reputation_required=0,
            current_reputation=0,
            available_missions=["imperial_patrol_001", "combat_training_001", "escort_imperial_001"],
            last_interaction=None
        )
        self.mission_givers["Commander Tarkin"] = commander_tarkin
        
        captain_solo = MissionGiver(
            name="Captain Solo",
            faction="neutral",
            mission_types=["delivery", "escort", "smuggling"],
            reputation_required=100,
            current_reputation=0,
            available_missions=["smuggling_run_001", "delivery_corellia_001"],
            last_interaction=None
        )
        self.mission_givers["Captain Solo"] = captain_solo
        
        lieutenant_organa = MissionGiver(
            name="Lieutenant Organa",
            faction="republic",
            mission_types=["patrol", "diplomatic", "escort"],
            reputation_required=50,
            current_reputation=0,
            available_missions=["republic_patrol_001", "diplomatic_escort_001"],
            last_interaction=None
        )
        self.mission_givers["Lieutenant Organa"] = lieutenant_organa
        
        # Naboo Orbital mission givers
        ambassador_amidala = MissionGiver(
            name="Ambassador Amidala",
            faction="republic",
            mission_types=["diplomatic", "escort", "exploration"],
            reputation_required=200,
            current_reputation=0,
            available_missions=["diplomatic_mission_001", "exploration_naboo_001"],
            last_interaction=None
        )
        self.mission_givers["Ambassador Amidala"] = ambassador_amidala
        
        captain_panaka = MissionGiver(
            name="Captain Panaka",
            faction="republic",
            mission_types=["patrol", "combat", "escort"],
            reputation_required=100,
            current_reputation=0,
            available_missions=["naboo_patrol_001", "security_escort_001"],
            last_interaction=None
        )
        self.mission_givers["Captain Panaka"] = captain_panaka
        
        commander_typho = MissionGiver(
            name="Commander Typho",
            faction="republic",
            mission_types=["combat", "patrol", "security"],
            reputation_required=150,
            current_reputation=0,
            available_missions=["security_mission_001", "combat_training_002"],
            last_interaction=None
        )
        self.mission_givers["Commander Typho"] = commander_typho
    
    def get_location(self, location_name: str) -> Optional[MissionLocation]:
        """Get a specific mission location.
        
        Parameters
        ----------
        location_name : str
            Name of the location
            
        Returns
        -------
        MissionLocation, optional
            Mission location or None if not found
        """
        return self.locations.get(location_name)
    
    def get_available_locations(self) -> List[MissionLocation]:
        """Get all available mission locations.
        
        Returns
        -------
        List[MissionLocation]
            List of all available locations
        """
        return list(self.locations.values())
    
    def get_locations_by_type(self, location_type: MissionLocationType) -> List[MissionLocation]:
        """Get locations filtered by type.
        
        Parameters
        ----------
        location_type : MissionLocationType
            Type of location to filter by
            
        Returns
        -------
        List[MissionLocation]
            List of locations of the specified type
        """
        return [loc for loc in self.locations.values() if loc.location_type == location_type]
    
    def get_locations_by_zone(self, zone: str) -> List[MissionLocation]:
        """Get locations filtered by zone.
        
        Parameters
        ----------
        zone : str
            Zone to filter by
            
        Returns
        -------
        List[MissionLocation]
            List of locations in the specified zone
        """
        return [loc for loc in self.locations.values() if loc.zone == zone]
    
    def visit_location(self, location_name: str) -> bool:
        """Mark a location as visited.
        
        Parameters
        ----------
        location_name : str
            Name of the location to visit
            
        Returns
        -------
        bool
            True if location was found and visited
        """
        if location_name not in self.locations:
            return False
        
        self.locations[location_name].last_visited = time.time()
        log_event(f"[MISSION_LOCATIONS] Visited location: {location_name}")
        return True
    
    def get_mission_givers_at_location(self, location_name: str) -> List[MissionGiver]:
        """Get mission givers available at a specific location.
        
        Parameters
        ----------
        location_name : str
            Name of the location
            
        Returns
        -------
        List[MissionGiver]
            List of mission givers at the location
        """
        if location_name not in self.locations:
            return []
        
        location = self.locations[location_name]
        givers = []
        
        for giver_name in location.mission_givers:
            if giver_name in self.mission_givers:
                givers.append(self.mission_givers[giver_name])
        
        return givers
    
    def interact_with_giver(self, giver_name: str) -> Dict[str, Any]:
        """Interact with a mission giver.
        
        Parameters
        ----------
        giver_name : str
            Name of the mission giver
            
        Returns
        -------
        Dict[str, Any]
            Interaction result with available missions and dialogue
        """
        if giver_name not in self.mission_givers:
            return {"error": "Mission giver not found"}
        
        giver = self.mission_givers[giver_name]
        giver.last_interaction = time.time()
        
        # Check if missions need rotation
        self._check_mission_rotation()
        
        # Get available missions for this giver
        available_missions = self._get_available_missions_for_giver(giver)
        
        return {
            "giver_name": giver.name,
            "faction": giver.faction,
            "reputation_required": giver.reputation_required,
            "current_reputation": giver.current_reputation,
            "available_missions": available_missions,
            "dialogue": self._generate_giver_dialogue(giver),
            "interaction_time": time.time()
        }
    
    def _get_available_missions_for_giver(self, giver: MissionGiver) -> List[Dict[str, Any]]:
        """Get available missions for a specific giver.
        
        Parameters
        ----------
        giver : MissionGiver
            Mission giver to get missions for
            
        Returns
        -------
        List[Dict[str, Any]]
            List of available missions
        """
        missions = []
        
        for mission_id in giver.available_missions:
            mission = self._create_mission_for_giver(mission_id, giver)
            if mission:
                missions.append({
                    "mission_id": mission.mission_id,
                    "name": mission.name,
                    "description": mission.description,
                    "difficulty": mission.difficulty.value,
                    "mission_type": mission.mission_type,
                    "requirements": mission.requirements,
                    "rewards": mission.rewards,
                    "time_limit": mission.time_limit,
                    "reputation_gain": mission.reputation_gain,
                    "faction_standing": mission.faction_standing
                })
        
        return missions
    
    def _create_mission_for_giver(self, mission_id: str, giver: MissionGiver) -> Optional[LocationMission]:
        """Create a mission instance for a specific giver.
        
        Parameters
        ----------
        mission_id : str
            Mission ID to create
        giver : MissionGiver
            Mission giver providing the mission
            
        Returns
        -------
        LocationMission, optional
            Created mission or None if creation failed
        """
        # Mission templates based on giver and mission ID
        mission_templates = {
            "imperial_patrol_001": {
                "name": "Imperial Patrol Route Alpha",
                "description": "Patrol the Corellia sector for Imperial security",
                "difficulty": MissionDifficulty.EASY,
                "mission_type": "patrol",
                "requirements": {"ship": True, "combat_rating": 1},
                "rewards": {"credits": 500, "experience": 200, "reputation": 10},
                "time_limit": 2.0,
                "reputation_gain": 10,
                "faction_standing": "imperial"
            },
            "combat_training_001": {
                "name": "Combat Training Exercise",
                "description": "Participate in Imperial combat training",
                "difficulty": MissionDifficulty.MEDIUM,
                "mission_type": "combat",
                "requirements": {"ship": True, "combat_rating": 2},
                "rewards": {"credits": 800, "experience": 350, "reputation": 15},
                "time_limit": 3.0,
                "reputation_gain": 15,
                "faction_standing": "imperial"
            },
            "escort_imperial_001": {
                "name": "Imperial VIP Escort",
                "description": "Escort Imperial dignitary to secure location",
                "difficulty": MissionDifficulty.HARD,
                "mission_type": "escort",
                "requirements": {"ship": True, "combat_rating": 3, "escort_rating": 2},
                "rewards": {"credits": 1200, "experience": 500, "reputation": 25},
                "time_limit": 4.0,
                "reputation_gain": 25,
                "faction_standing": "imperial"
            },
            "smuggling_run_001": {
                "name": "Discrete Delivery",
                "description": "Deliver cargo through dangerous space lanes",
                "difficulty": MissionDifficulty.MEDIUM,
                "mission_type": "smuggling",
                "requirements": {"ship": True, "stealth_rating": 2},
                "rewards": {"credits": 1000, "experience": 300, "reputation": 5},
                "time_limit": 2.5,
                "reputation_gain": 5,
                "faction_standing": "neutral"
            },
            "delivery_corellia_001": {
                "name": "Corellia Trade Route",
                "description": "Deliver goods to Corellia merchants",
                "difficulty": MissionDifficulty.EASY,
                "mission_type": "delivery",
                "requirements": {"ship": True, "cargo_capacity": 100},
                "rewards": {"credits": 400, "experience": 150, "reputation": 8},
                "time_limit": 1.5,
                "reputation_gain": 8,
                "faction_standing": "neutral"
            },
            "republic_patrol_001": {
                "name": "Republic Security Patrol",
                "description": "Patrol Republic space for security threats",
                "difficulty": MissionDifficulty.MEDIUM,
                "mission_type": "patrol",
                "requirements": {"ship": True, "combat_rating": 2},
                "rewards": {"credits": 600, "experience": 250, "reputation": 12},
                "time_limit": 2.0,
                "reputation_gain": 12,
                "faction_standing": "republic"
            },
            "diplomatic_escort_001": {
                "name": "Diplomatic Escort Mission",
                "description": "Escort Republic diplomat to Naboo",
                "difficulty": MissionDifficulty.HARD,
                "mission_type": "escort",
                "requirements": {"ship": True, "escort_rating": 3, "diplomatic_rating": 1},
                "rewards": {"credits": 1000, "experience": 400, "reputation": 20},
                "time_limit": 3.5,
                "reputation_gain": 20,
                "faction_standing": "republic"
            },
            "diplomatic_mission_001": {
                "name": "Naboo Diplomatic Mission",
                "description": "Assist with diplomatic negotiations",
                "difficulty": MissionDifficulty.EXPERT,
                "mission_type": "diplomatic",
                "requirements": {"ship": True, "diplomatic_rating": 3, "reputation": 200},
                "rewards": {"credits": 1500, "experience": 600, "reputation": 30},
                "time_limit": 5.0,
                "reputation_gain": 30,
                "faction_standing": "republic"
            },
            "exploration_naboo_001": {
                "name": "Naboo System Exploration",
                "description": "Explore uncharted regions of Naboo system",
                "difficulty": MissionDifficulty.MEDIUM,
                "mission_type": "exploration",
                "requirements": {"ship": True, "exploration_rating": 2},
                "rewards": {"credits": 800, "experience": 300, "reputation": 15},
                "time_limit": 4.0,
                "reputation_gain": 15,
                "faction_standing": "republic"
            },
            "naboo_patrol_001": {
                "name": "Naboo Security Patrol",
                "description": "Patrol Naboo orbital space for threats",
                "difficulty": MissionDifficulty.EASY,
                "mission_type": "patrol",
                "requirements": {"ship": True, "combat_rating": 1},
                "rewards": {"credits": 500, "experience": 200, "reputation": 10},
                "time_limit": 1.5,
                "reputation_gain": 10,
                "faction_standing": "republic"
            },
            "security_escort_001": {
                "name": "Naboo Security Escort",
                "description": "Escort Naboo security forces",
                "difficulty": MissionDifficulty.MEDIUM,
                "mission_type": "escort",
                "requirements": {"ship": True, "escort_rating": 2},
                "rewards": {"credits": 700, "experience": 300, "reputation": 12},
                "time_limit": 2.5,
                "reputation_gain": 12,
                "faction_standing": "republic"
            },
            "security_mission_001": {
                "name": "Advanced Security Training",
                "description": "Participate in advanced security training",
                "difficulty": MissionDifficulty.HARD,
                "mission_type": "combat",
                "requirements": {"ship": True, "combat_rating": 3, "reputation": 150},
                "rewards": {"credits": 1200, "experience": 500, "reputation": 25},
                "time_limit": 3.0,
                "reputation_gain": 25,
                "faction_standing": "republic"
            },
            "combat_training_002": {
                "name": "Elite Combat Training",
                "description": "Advanced combat training for elite pilots",
                "difficulty": MissionDifficulty.EXPERT,
                "mission_type": "combat",
                "requirements": {"ship": True, "combat_rating": 4, "reputation": 150},
                "rewards": {"credits": 2000, "experience": 800, "reputation": 40},
                "time_limit": 4.0,
                "reputation_gain": 40,
                "faction_standing": "republic"
            }
        }
        
        if mission_id not in mission_templates:
            return None
        
        template = mission_templates[mission_id]
        
        return LocationMission(
            mission_id=mission_id,
            name=template["name"],
            description=template["description"],
            difficulty=template["difficulty"],
            mission_type=template["mission_type"],
            location=giver.name,  # Use giver name as location for now
            giver=giver.name,
            requirements=template["requirements"],
            rewards=template["rewards"],
            time_limit=template["time_limit"],
            reputation_gain=template["reputation_gain"],
            faction_standing=template["faction_standing"]
        )
    
    def _generate_giver_dialogue(self, giver: MissionGiver) -> str:
        """Generate dialogue for mission giver interaction.
        
        Parameters
        ----------
        giver : MissionGiver
            Mission giver to generate dialogue for
            
        Returns
        -------
        str
            Generated dialogue
        """
        dialogues = {
            "Commander Tarkin": [
                "Welcome, pilot. The Empire needs skilled pilots like yourself.",
                "We have several missions that require your expertise.",
                "Your service to the Empire will not go unnoticed."
            ],
            "Captain Solo": [
                "Hey there, kid. Looking for some work?",
                "I've got some jobs that need doing. Interested?",
                "Just remember - no questions asked, no answers given."
            ],
            "Lieutenant Organa": [
                "Greetings, citizen. The Republic values your service.",
                "We have missions that require a steady hand and clear mind.",
                "Your contribution to peace and justice is appreciated."
            ],
            "Ambassador Amidala": [
                "Welcome to Naboo Orbital. I trust your journey was pleasant?",
                "We have diplomatic missions that require discretion and skill.",
                "Your assistance in maintaining peace is most welcome."
            ],
            "Captain Panaka": [
                "Security is our top priority here. We need reliable pilots.",
                "The safety of Naboo depends on skilled pilots like yourself.",
                "Your service to Naboo's security is greatly appreciated."
            ],
            "Commander Typho": [
                "Welcome to our security training program.",
                "We need pilots who can handle high-pressure situations.",
                "Your skills will be put to the test here."
            ]
        }
        
        giver_dialogues = dialogues.get(giver.name, ["Greetings, pilot. How may I assist you?"])
        return giver_dialogues[0]  # Return first dialogue for now
    
    def _check_mission_rotation(self) -> None:
        """Check if missions need to be rotated."""
        current_time = time.time()
        
        if current_time - self.mission_rotation_timer > self.rotation_interval:
            self._rotate_missions()
            self.mission_rotation_timer = current_time
    
    def _rotate_missions(self) -> None:
        """Rotate available missions for all givers."""
        log_event("[MISSION_LOCATIONS] Rotating available missions")
        
        for giver in self.mission_givers.values():
            # Simple rotation - could be more sophisticated
            if giver.available_missions:
                # Rotate the list
                giver.available_missions = giver.available_missions[1:] + giver.available_missions[:1]
    
    def accept_mission(self, mission_id: str, giver_name: str) -> Dict[str, Any]:
        """Accept a mission from a giver.
        
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
        if giver_name not in self.mission_givers:
            return {"error": "Mission giver not found"}
        
        giver = self.mission_givers[giver_name]
        
        if mission_id not in giver.available_missions:
            return {"error": "Mission not available from this giver"}
        
        # Create the mission
        mission = self._create_mission_for_giver(mission_id, giver)
        
        if not mission:
            return {"error": "Failed to create mission"}
        
        # Check requirements
        requirements_check = self._check_mission_requirements(mission)
        if not requirements_check["met"]:
            return {
                "error": "Requirements not met",
                "missing_requirements": requirements_check["missing"]
            }
        
        # Accept the mission
        self.available_missions[mission_id] = mission
        
        return {
            "success": True,
            "mission": {
                "mission_id": mission.mission_id,
                "name": mission.name,
                "description": mission.description,
                "difficulty": mission.difficulty.value,
                "mission_type": mission.mission_type,
                "requirements": mission.requirements,
                "rewards": mission.rewards,
                "time_limit": mission.time_limit,
                "reputation_gain": mission.reputation_gain,
                "faction_standing": mission.faction_standing
            },
            "giver": giver_name
        }
    
    def _check_mission_requirements(self, mission: LocationMission) -> Dict[str, Any]:
        """Check if mission requirements are met.
        
        Parameters
        ----------
        mission : LocationMission
            Mission to check requirements for
            
        Returns
        -------
        Dict[str, Any]
            Requirements check result
        """
        # This would integrate with character stats and ship capabilities
        # For now, return a simple check
        missing_requirements = []
        
        # Check basic requirements
        if "ship" in mission.requirements and not self._has_ship():
            missing_requirements.append("ship")
        
        if "combat_rating" in mission.requirements:
            combat_rating = self._get_combat_rating()
            if combat_rating < mission.requirements["combat_rating"]:
                missing_requirements.append(f"combat_rating_{mission.requirements['combat_rating']}")
        
        return {
            "met": len(missing_requirements) == 0,
            "missing": missing_requirements
        }
    
    def _has_ship(self) -> bool:
        """Check if player has a ship available."""
        # This would integrate with ship handler
        return True  # Placeholder
    
    def _get_combat_rating(self) -> int:
        """Get player's combat rating."""
        # This would integrate with character stats
        return 2  # Placeholder
    
    def get_location_statistics(self) -> Dict[str, Any]:
        """Get statistics for all mission locations.
        
        Returns
        -------
        Dict[str, Any]
            Location statistics
        """
        stats = {
            "total_locations": len(self.locations),
            "locations_by_type": {},
            "locations_by_zone": {},
            "total_mission_givers": len(self.mission_givers),
            "active_missions": len(self.available_missions)
        }
        
        # Count by type
        for location in self.locations.values():
            location_type = location.location_type.value
            if location_type not in stats["locations_by_type"]:
                stats["locations_by_type"][location_type] = 0
            stats["locations_by_type"][location_type] += 1
        
        # Count by zone
        for location in self.locations.values():
            zone = location.zone
            if zone not in stats["locations_by_zone"]:
                stats["locations_by_zone"][zone] = 0
            stats["locations_by_zone"][zone] += 1
        
        return stats 
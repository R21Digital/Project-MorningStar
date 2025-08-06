"""AI piloting foundation for future AI piloting routines."""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from utils.logging_utils import log_event


class PilotSkill(Enum):
    """AI pilot skills."""
    NAVIGATION = "navigation"
    COMBAT = "combat"
    ESCORT = "escort"
    STEALTH = "stealth"
    EXPLORATION = "exploration"
    TRADING = "trading"


class PilotBehavior(Enum):
    """AI pilot behavior patterns."""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    CAUTIOUS = "cautious"
    STEALTHY = "stealthy"
    BALANCED = "balanced"
    SPECIALIZED = "specialized"


class MissionType(Enum):
    """Mission types for AI piloting."""
    PATROL = "patrol"
    ESCORT = "escort"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    TRADING = "trading"
    STEALTH = "stealth"


@dataclass
class AIPilot:
    """Represents an AI pilot with skills and behavior."""
    pilot_id: str
    name: str
    skill_levels: Dict[PilotSkill, int]  # 1-10 scale
    behavior: PilotBehavior
    experience: int
    mission_history: List[str]
    current_mission: Optional[str] = None
    is_active: bool = False
    last_activity: Optional[float] = None


@dataclass
class PilotMission:
    """Represents a mission for AI piloting."""
    mission_id: str
    mission_type: MissionType
    pilot_id: str
    ship_name: str
    destination: str
    objectives: List[str]
    constraints: Dict[str, Any]
    priority: int  # 1-10 scale
    estimated_duration: float  # in minutes
    status: str  # "pending", "active", "completed", "failed"
    start_time: Optional[float] = None
    completion_time: Optional[float] = None


@dataclass
class PilotDecision:
    """Represents a decision made by AI pilot."""
    decision_id: str
    pilot_id: str
    mission_id: str
    decision_type: str
    context: Dict[str, Any]
    reasoning: str
    action_taken: str
    timestamp: float
    success: bool


@dataclass
class PilotPerformance:
    """Tracks AI pilot performance metrics."""
    pilot_id: str
    missions_completed: int
    missions_failed: int
    total_credits_earned: int
    total_experience_gained: int
    average_mission_rating: float
    skill_improvements: Dict[PilotSkill, float]
    decision_accuracy: float
    last_updated: float


class AIPilotingFoundation:
    """Foundation for AI piloting routines."""
    
    def __init__(self, config_path: str = "config/space_config.json"):
        """Initialize the AI piloting foundation.
        
        Parameters
        ----------
        config_path : str
            Path to space configuration file
        """
        self.config = self._load_config(config_path)
        self.pilots: Dict[str, AIPilot] = {}
        self.missions: Dict[str, PilotMission] = {}
        self.decisions: List[PilotDecision] = []
        self.performance: Dict[str, PilotPerformance] = {}
        
        # Load AI piloting data
        self._load_piloting_data()
        self._initialize_pilots()
        
        # AI piloting state
        self.active_pilots: Dict[str, AIPilot] = {}
        self.mission_queue: List[PilotMission] = []
        self.last_ai_update = time.time()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load space configuration."""
        path = Path(config_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _load_piloting_data(self) -> None:
        """Load AI piloting data."""
        data_file = Path("data/space_quests/ai_piloting.json")
        if data_file.exists():
            try:
                with data_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._parse_piloting_data(data)
            except Exception as e:
                log_event(f"[AI_PILOTING] Error loading piloting data: {e}")
    
    def _parse_piloting_data(self, data: Dict[str, Any]) -> None:
        """Parse AI piloting data from JSON."""
        # Parse pilots
        for pilot_data in data.get("pilots", []):
            pilot = AIPilot(
                pilot_id=pilot_data["pilot_id"],
                name=pilot_data["name"],
                skill_levels={PilotSkill(k): v for k, v in pilot_data["skill_levels"].items()},
                behavior=PilotBehavior(pilot_data["behavior"]),
                experience=pilot_data["experience"],
                mission_history=pilot_data.get("mission_history", []),
                current_mission=pilot_data.get("current_mission"),
                is_active=pilot_data.get("is_active", False),
                last_activity=pilot_data.get("last_activity")
            )
            self.pilots[pilot.pilot_id] = pilot
        
        # Parse missions
        for mission_data in data.get("missions", []):
            mission = PilotMission(
                mission_id=mission_data["mission_id"],
                mission_type=MissionType(mission_data["mission_type"]),
                pilot_id=mission_data["pilot_id"],
                ship_name=mission_data["ship_name"],
                destination=mission_data["destination"],
                objectives=mission_data["objectives"],
                constraints=mission_data["constraints"],
                priority=mission_data["priority"],
                estimated_duration=mission_data["estimated_duration"],
                status=mission_data["status"],
                start_time=mission_data.get("start_time"),
                completion_time=mission_data.get("completion_time")
            )
            self.missions[mission.mission_id] = mission
    
    def _initialize_pilots(self) -> None:
        """Initialize default AI pilots."""
        # Navigation Specialist
        nav_pilot = AIPilot(
            pilot_id="nav_specialist_001",
            name="Navigator Prime",
            skill_levels={
                PilotSkill.NAVIGATION: 8,
                PilotSkill.COMBAT: 4,
                PilotSkill.ESCORT: 5,
                PilotSkill.STEALTH: 3,
                PilotSkill.EXPLORATION: 6,
                PilotSkill.TRADING: 4
            },
            behavior=PilotBehavior.CAUTIOUS,
            experience=1500,
            mission_history=[],
            is_active=False
        )
        self.pilots[nav_pilot.pilot_id] = nav_pilot
        
        # Combat Specialist
        combat_pilot = AIPilot(
            pilot_id="combat_specialist_001",
            name="Warrior Elite",
            skill_levels={
                PilotSkill.NAVIGATION: 5,
                PilotSkill.COMBAT: 9,
                PilotSkill.ESCORT: 7,
                PilotSkill.STEALTH: 4,
                PilotSkill.EXPLORATION: 3,
                PilotSkill.TRADING: 2
            },
            behavior=PilotBehavior.AGGRESSIVE,
            experience=2000,
            mission_history=[],
            is_active=False
        )
        self.pilots[combat_pilot.pilot_id] = combat_pilot
        
        # Stealth Specialist
        stealth_pilot = AIPilot(
            pilot_id="stealth_specialist_001",
            name="Shadow Runner",
            skill_levels={
                PilotSkill.NAVIGATION: 6,
                PilotSkill.COMBAT: 3,
                PilotSkill.ESCORT: 4,
                PilotSkill.STEALTH: 9,
                PilotSkill.EXPLORATION: 7,
                PilotSkill.TRADING: 5
            },
            behavior=PilotBehavior.STEALTHY,
            experience=1200,
            mission_history=[],
            is_active=False
        )
        self.pilots[stealth_pilot.pilot_id] = stealth_pilot
        
        # Balanced Pilot
        balanced_pilot = AIPilot(
            pilot_id="balanced_pilot_001",
            name="Adaptive One",
            skill_levels={
                PilotSkill.NAVIGATION: 6,
                PilotSkill.COMBAT: 6,
                PilotSkill.ESCORT: 6,
                PilotSkill.STEALTH: 5,
                PilotSkill.EXPLORATION: 6,
                PilotSkill.TRADING: 6
            },
            behavior=PilotBehavior.BALANCED,
            experience=800,
            mission_history=[],
            is_active=False
        )
        self.pilots[balanced_pilot.pilot_id] = balanced_pilot
    
    def get_pilot(self, pilot_id: str) -> Optional[AIPilot]:
        """Get a specific AI pilot.
        
        Parameters
        ----------
        pilot_id : str
            ID of the pilot
            
        Returns
        -------
        AIPilot, optional
            AI pilot or None if not found
        """
        return self.pilots.get(pilot_id)
    
    def get_available_pilots(self) -> List[AIPilot]:
        """Get all available AI pilots.
        
        Returns
        -------
        List[AIPilot]
            List of all available pilots
        """
        return list(self.pilots.values())
    
    def get_active_pilots(self) -> List[AIPilot]:
        """Get all active AI pilots.
        
        Returns
        -------
        List[AIPilot]
            List of active pilots
        """
        return [pilot for pilot in self.pilots.values() if pilot.is_active]
    
    def get_pilots_by_skill(self, skill: PilotSkill, min_level: int = 1) -> List[AIPilot]:
        """Get pilots filtered by skill level.
        
        Parameters
        ----------
        skill : PilotSkill
            Skill to filter by
        min_level : int
            Minimum skill level required
            
        Returns
        -------
        List[AIPilot]
            List of pilots with required skill level
        """
        return [pilot for pilot in self.pilots.values() 
                if pilot.skill_levels.get(skill, 0) >= min_level]
    
    def get_pilots_by_behavior(self, behavior: PilotBehavior) -> List[AIPilot]:
        """Get pilots filtered by behavior.
        
        Parameters
        ----------
        behavior : PilotBehavior
            Behavior to filter by
            
        Returns
        -------
        List[AIPilot]
            List of pilots with specified behavior
        """
        return [pilot for pilot in self.pilots.values() if pilot.behavior == behavior]
    
    def activate_pilot(self, pilot_id: str) -> bool:
        """Activate an AI pilot.
        
        Parameters
        ----------
        pilot_id : str
            ID of the pilot to activate
            
        Returns
        -------
        bool
            True if pilot was activated successfully
        """
        if pilot_id not in self.pilots:
            return False
        
        pilot = self.pilots[pilot_id]
        
        if pilot.is_active:
            return True
        
        pilot.is_active = True
        pilot.last_activity = time.time()
        self.active_pilots[pilot_id] = pilot
        
        log_event(f"[AI_PILOTING] Activated pilot: {pilot.name}")
        return True
    
    def deactivate_pilot(self, pilot_id: str) -> bool:
        """Deactivate an AI pilot.
        
        Parameters
        ----------
        pilot_id : str
            ID of the pilot to deactivate
            
        Returns
        -------
        bool
            True if pilot was deactivated successfully
        """
        if pilot_id not in self.pilots:
            return False
        
        pilot = self.pilots[pilot_id]
        
        if not pilot.is_active:
            return True
        
        pilot.is_active = False
        pilot.current_mission = None
        
        if pilot_id in self.active_pilots:
            del self.active_pilots[pilot_id]
        
        log_event(f"[AI_PILOTING] Deactivated pilot: {pilot.name}")
        return True
    
    def assign_mission(self, pilot_id: str, mission_data: Dict[str, Any]) -> Optional[str]:
        """Assign a mission to an AI pilot.
        
        Parameters
        ----------
        pilot_id : str
            ID of the pilot to assign mission to
        mission_data : Dict[str, Any]
            Mission data
            
        Returns
        -------
        str, optional
            Mission ID if assignment successful, None otherwise
        """
        if pilot_id not in self.pilots:
            return None
        
        pilot = self.pilots[pilot_id]
        
        if not pilot.is_active:
            return None
        
        # Create mission
        mission_id = f"mission_{int(time.time())}"
        mission = PilotMission(
            mission_id=mission_id,
            mission_type=MissionType(mission_data["mission_type"]),
            pilot_id=pilot_id,
            ship_name=mission_data["ship_name"],
            destination=mission_data["destination"],
            objectives=mission_data["objectives"],
            constraints=mission_data.get("constraints", {}),
            priority=mission_data.get("priority", 5),
            estimated_duration=mission_data.get("estimated_duration", 60.0),
            status="pending"
        )
        
        self.missions[mission_id] = mission
        pilot.current_mission = mission_id
        pilot.last_activity = time.time()
        
        # Add to mission queue
        self.mission_queue.append(mission)
        
        log_event(f"[AI_PILOTING] Assigned mission {mission_id} to {pilot.name}")
        return mission_id
    
    def start_mission(self, mission_id: str) -> bool:
        """Start a mission with AI piloting.
        
        Parameters
        ----------
        mission_id : str
            ID of the mission to start
            
        Returns
        -------
        bool
            True if mission started successfully
        """
        if mission_id not in self.missions:
            return False
        
        mission = self.missions[mission_id]
        pilot = self.pilots.get(mission.pilot_id)
        
        if not pilot or not pilot.is_active:
            return False
        
        mission.status = "active"
        mission.start_time = time.time()
        pilot.last_activity = time.time()
        
        log_event(f"[AI_PILOTING] Started mission {mission_id} with {pilot.name}")
        return True
    
    def update_mission_progress(self, mission_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update mission progress with AI piloting decisions.
        
        Parameters
        ----------
        mission_id : str
            ID of the mission to update
        progress_data : Dict[str, Any]
            Progress data and events
            
        Returns
        -------
        Dict[str, Any]
            Updated mission status and AI decisions
        """
        if mission_id not in self.missions:
            return {"error": "Mission not found"}
        
        mission = self.missions[mission_id]
        pilot = self.pilots.get(mission.pilot_id)
        
        if not pilot:
            return {"error": "Pilot not found"}
        
        # Generate AI decisions based on mission type and pilot skills
        decisions = self._generate_ai_decisions(mission, pilot, progress_data)
        
        # Update mission status based on decisions
        mission_status = self._update_mission_status(mission, decisions)
        
        # Record decisions
        for decision in decisions:
            self.decisions.append(decision)
        
        pilot.last_activity = time.time()
        
        return {
            "mission_id": mission_id,
            "pilot_name": pilot.name,
            "mission_status": mission.status,
            "decisions": [self._decision_to_dict(d) for d in decisions],
            "progress": mission_status
        }
    
    def _generate_ai_decisions(self, mission: PilotMission, pilot: AIPilot, progress_data: Dict[str, Any]) -> List[PilotDecision]:
        """Generate AI decisions based on mission and pilot characteristics.
        
        Parameters
        ----------
        mission : PilotMission
            Mission being executed
        pilot : AIPilot
            AI pilot executing the mission
        progress_data : Dict[str, Any]
            Current progress data
            
        Returns
        -------
        List[PilotDecision]
            List of AI decisions made
        """
        decisions = []
        current_time = time.time()
        
        # Decision 1: Route Selection
        route_decision = self._make_route_decision(mission, pilot, progress_data)
        if route_decision:
            decisions.append(route_decision)
        
        # Decision 2: Combat Strategy (if applicable)
        if mission.mission_type in [MissionType.COMBAT, MissionType.ESCORT]:
            combat_decision = self._make_combat_decision(mission, pilot, progress_data)
            if combat_decision:
                decisions.append(combat_decision)
        
        # Decision 3: Stealth Approach (if applicable)
        if mission.mission_type in [MissionType.STEALTH, MissionType.EXPLORATION]:
            stealth_decision = self._make_stealth_decision(mission, pilot, progress_data)
            if stealth_decision:
                decisions.append(stealth_decision)
        
        # Decision 4: Resource Management
        resource_decision = self._make_resource_decision(mission, pilot, progress_data)
        if resource_decision:
            decisions.append(resource_decision)
        
        return decisions
    
    def _make_route_decision(self, mission: PilotMission, pilot: AIPilot, progress_data: Dict[str, Any]) -> Optional[PilotDecision]:
        """Make route selection decision based on pilot skills and mission type."""
        nav_skill = pilot.skill_levels.get(PilotSkill.NAVIGATION, 1)
        
        # Determine route preference based on pilot behavior
        if pilot.behavior == PilotBehavior.CAUTIOUS:
            route_type = "safe_route"
            reasoning = "Pilot prefers safe, well-traveled routes"
        elif pilot.behavior == PilotBehavior.AGGRESSIVE:
            route_type = "direct_route"
            reasoning = "Pilot prefers direct, fast routes"
        elif pilot.behavior == PilotBehavior.STEALTHY:
            route_type = "stealth_route"
            reasoning = "Pilot prefers covert, less-traveled routes"
        else:
            route_type = "balanced_route"
            reasoning = "Pilot uses balanced route selection"
        
        # Adjust based on navigation skill
        if nav_skill >= 8:
            route_type += "_optimized"
            reasoning += " - High navigation skill allows route optimization"
        elif nav_skill <= 3:
            route_type += "_basic"
            reasoning += " - Limited navigation skill restricts route options"
        
        return PilotDecision(
            decision_id=f"route_{int(time.time())}",
            pilot_id=pilot.pilot_id,
            mission_id=mission.mission_id,
            decision_type="route_selection",
            context={"mission_type": mission.mission_type.value, "nav_skill": nav_skill},
            reasoning=reasoning,
            action_taken=f"Selected {route_type}",
            timestamp=time.time(),
            success=True
        )
    
    def _make_combat_decision(self, mission: PilotMission, pilot: AIPilot, progress_data: Dict[str, Any]) -> Optional[PilotDecision]:
        """Make combat strategy decision based on pilot skills and behavior."""
        combat_skill = pilot.skill_levels.get(PilotSkill.COMBAT, 1)
        
        if pilot.behavior == PilotBehavior.AGGRESSIVE:
            strategy = "offensive"
            reasoning = "Pilot prefers aggressive, offensive tactics"
        elif pilot.behavior == PilotBehavior.DEFENSIVE:
            strategy = "defensive"
            reasoning = "Pilot prefers defensive, protective tactics"
        else:
            strategy = "balanced"
            reasoning = "Pilot uses balanced combat approach"
        
        # Adjust based on combat skill
        if combat_skill >= 8:
            strategy += "_advanced"
            reasoning += " - High combat skill enables advanced tactics"
        elif combat_skill <= 3:
            strategy += "_basic"
            reasoning += " - Limited combat skill restricts tactical options"
        
        return PilotDecision(
            decision_id=f"combat_{int(time.time())}",
            pilot_id=pilot.pilot_id,
            mission_id=mission.mission_id,
            decision_type="combat_strategy",
            context={"mission_type": mission.mission_type.value, "combat_skill": combat_skill},
            reasoning=reasoning,
            action_taken=f"Applied {strategy} combat strategy",
            timestamp=time.time(),
            success=True
        )
    
    def _make_stealth_decision(self, mission: PilotMission, pilot: AIPilot, progress_data: Dict[str, Any]) -> Optional[PilotDecision]:
        """Make stealth approach decision based on pilot skills and behavior."""
        stealth_skill = pilot.skill_levels.get(PilotSkill.STEALTH, 1)
        
        if pilot.behavior == PilotBehavior.STEALTHY:
            approach = "covert"
            reasoning = "Pilot specializes in stealth operations"
        elif pilot.behavior == PilotBehavior.CAUTIOUS:
            approach = "careful"
            reasoning = "Pilot prefers careful, low-profile approach"
        else:
            approach = "standard"
            reasoning = "Pilot uses standard stealth approach"
        
        # Adjust based on stealth skill
        if stealth_skill >= 8:
            approach += "_advanced"
            reasoning += " - High stealth skill enables advanced covert operations"
        elif stealth_skill <= 3:
            approach += "_basic"
            reasoning += " - Limited stealth skill restricts covert options"
        
        return PilotDecision(
            decision_id=f"stealth_{int(time.time())}",
            pilot_id=pilot.pilot_id,
            mission_id=mission.mission_id,
            decision_type="stealth_approach",
            context={"mission_type": mission.mission_type.value, "stealth_skill": stealth_skill},
            reasoning=reasoning,
            action_taken=f"Applied {approach} stealth approach",
            timestamp=time.time(),
            success=True
        )
    
    def _make_resource_decision(self, mission: PilotMission, pilot: AIPilot, progress_data: Dict[str, Any]) -> Optional[PilotDecision]:
        """Make resource management decision based on pilot skills and mission."""
        # Simple resource management based on pilot experience
        if pilot.experience > 1500:
            resource_strategy = "efficient"
            reasoning = "Experienced pilot optimizes resource usage"
        elif pilot.experience > 500:
            resource_strategy = "balanced"
            reasoning = "Moderately experienced pilot uses balanced resource management"
        else:
            resource_strategy = "conservative"
            reasoning = "Inexperienced pilot uses conservative resource management"
        
        return PilotDecision(
            decision_id=f"resource_{int(time.time())}",
            pilot_id=pilot.pilot_id,
            mission_id=mission.mission_id,
            decision_type="resource_management",
            context={"mission_type": mission.mission_type.value, "pilot_experience": pilot.experience},
            reasoning=reasoning,
            action_taken=f"Applied {resource_strategy} resource strategy",
            timestamp=time.time(),
            success=True
        )
    
    def _update_mission_status(self, mission: PilotMission, decisions: List[PilotDecision]) -> Dict[str, Any]:
        """Update mission status based on AI decisions.
        
        Parameters
        ----------
        mission : PilotMission
            Mission to update
        decisions : List[PilotDecision]
            AI decisions made
            
        Returns
        -------
        Dict[str, Any]
            Updated mission status
        """
        # Calculate success probability based on pilot skills and decisions
        success_probability = self._calculate_success_probability(mission, decisions)
        
        # Simulate mission progress
        if mission.status == "active":
            elapsed_time = time.time() - (mission.start_time or time.time())
            progress_percentage = min(100, (elapsed_time / mission.estimated_duration) * 100)
            
            # Check for mission completion
            if progress_percentage >= 100:
                if random.random() < success_probability:
                    mission.status = "completed"
                    mission.completion_time = time.time()
                else:
                    mission.status = "failed"
        
        return {
            "status": mission.status,
            "progress_percentage": progress_percentage if mission.status == "active" else 100,
            "success_probability": success_probability,
            "elapsed_time": elapsed_time if mission.status == "active" else 0
        }
    
    def _calculate_success_probability(self, mission: PilotMission, decisions: List[PilotDecision]) -> float:
        """Calculate mission success probability based on pilot skills and decisions.
        
        Parameters
        ----------
        mission : PilotMission
            Mission to evaluate
        decisions : List[PilotDecision]
            AI decisions made
            
        Returns
        -------
        float
            Success probability (0.0 to 1.0)
        """
        pilot = self.pilots.get(mission.pilot_id)
        if not pilot:
            return 0.0
        
        # Base probability from pilot skills
        relevant_skill = self._get_relevant_skill(mission.mission_type)
        skill_level = pilot.skill_levels.get(relevant_skill, 1)
        base_probability = skill_level / 10.0
        
        # Adjust based on pilot behavior
        behavior_modifier = self._get_behavior_modifier(pilot.behavior, mission.mission_type)
        
        # Adjust based on decision quality
        decision_modifier = self._calculate_decision_modifier(decisions)
        
        # Calculate final probability
        final_probability = base_probability * behavior_modifier * decision_modifier
        
        return max(0.0, min(1.0, final_probability))
    
    def _get_relevant_skill(self, mission_type: MissionType) -> PilotSkill:
        """Get the most relevant skill for a mission type."""
        skill_mapping = {
            MissionType.PATROL: PilotSkill.NAVIGATION,
            MissionType.ESCORT: PilotSkill.ESCORT,
            MissionType.COMBAT: PilotSkill.COMBAT,
            MissionType.EXPLORATION: PilotSkill.EXPLORATION,
            MissionType.TRADING: PilotSkill.TRADING,
            MissionType.STEALTH: PilotSkill.STEALTH
        }
        return skill_mapping.get(mission_type, PilotSkill.NAVIGATION)
    
    def _get_behavior_modifier(self, behavior: PilotBehavior, mission_type: MissionType) -> float:
        """Get behavior modifier for mission type."""
        modifiers = {
            PilotBehavior.AGGRESSIVE: {
                MissionType.COMBAT: 1.2,
                MissionType.ESCORT: 1.1,
                MissionType.STEALTH: 0.7
            },
            PilotBehavior.DEFENSIVE: {
                MissionType.ESCORT: 1.2,
                MissionType.COMBAT: 0.9,
                MissionType.EXPLORATION: 1.0
            },
            PilotBehavior.STEALTHY: {
                MissionType.STEALTH: 1.3,
                MissionType.EXPLORATION: 1.1,
                MissionType.COMBAT: 0.8
            },
            PilotBehavior.CAUTIOUS: {
                MissionType.EXPLORATION: 1.1,
                MissionType.ESCORT: 1.0,
                MissionType.COMBAT: 0.9
            },
            PilotBehavior.BALANCED: {
                MissionType.PATROL: 1.0,
                MissionType.ESCORT: 1.0,
                MissionType.COMBAT: 1.0
            }
        }
        
        behavior_modifiers = modifiers.get(behavior, {})
        return behavior_modifiers.get(mission_type, 1.0)
    
    def _calculate_decision_modifier(self, decisions: List[PilotDecision]) -> float:
        """Calculate modifier based on decision quality."""
        if not decisions:
            return 1.0
        
        # Simple modifier based on decision success rate
        successful_decisions = sum(1 for d in decisions if d.success)
        success_rate = successful_decisions / len(decisions)
        
        return 0.8 + (success_rate * 0.4)  # Range: 0.8 to 1.2
    
    def _decision_to_dict(self, decision: PilotDecision) -> Dict[str, Any]:
        """Convert decision to dictionary for JSON serialization."""
        return {
            "decision_id": decision.decision_id,
            "pilot_id": decision.pilot_id,
            "mission_id": decision.mission_id,
            "decision_type": decision.decision_type,
            "context": decision.context,
            "reasoning": decision.reasoning,
            "action_taken": decision.action_taken,
            "timestamp": decision.timestamp,
            "success": decision.success
        }
    
    def complete_mission(self, mission_id: str) -> Dict[str, Any]:
        """Complete a mission and update pilot performance.
        
        Parameters
        ----------
        mission_id : str
            ID of the mission to complete
            
        Returns
        -------
        Dict[str, Any]
            Mission completion result
        """
        if mission_id not in self.missions:
            return {"error": "Mission not found"}
        
        mission = self.missions[mission_id]
        pilot = self.pilots.get(mission.pilot_id)
        
        if not pilot:
            return {"error": "Pilot not found"}
        
        # Update pilot experience and mission history
        experience_gain = self._calculate_experience_gain(mission, pilot)
        pilot.experience += experience_gain
        pilot.mission_history.append(mission_id)
        pilot.current_mission = None
        pilot.last_activity = time.time()
        
        # Update performance tracking
        self._update_pilot_performance(pilot, mission)
        
        # Remove from active missions
        if mission_id in [m.mission_id for m in self.mission_queue]:
            self.mission_queue = [m for m in self.mission_queue if m.mission_id != mission_id]
        
        log_event(f"[AI_PILOTING] Completed mission {mission_id} with {pilot.name}")
        
        return {
            "mission_id": mission_id,
            "pilot_name": pilot.name,
            "status": mission.status,
            "experience_gain": experience_gain,
            "completion_time": mission.completion_time
        }
    
    def _calculate_experience_gain(self, mission: PilotMission, pilot: AIPilot) -> int:
        """Calculate experience gain for mission completion."""
        base_experience = 50
        
        # Adjust based on mission type and difficulty
        type_multipliers = {
            MissionType.PATROL: 1.0,
            MissionType.ESCORT: 1.2,
            MissionType.COMBAT: 1.5,
            MissionType.EXPLORATION: 1.3,
            MissionType.TRADING: 1.1,
            MissionType.STEALTH: 1.4
        }
        
        type_multiplier = type_multipliers.get(mission.mission_type, 1.0)
        
        # Adjust based on pilot experience (less gain for experienced pilots)
        experience_modifier = max(0.5, 1.0 - (pilot.experience / 10000))
        
        return int(base_experience * type_multiplier * experience_modifier)
    
    def _update_pilot_performance(self, pilot: AIPilot, mission: PilotMission) -> None:
        """Update pilot performance metrics."""
        if pilot.pilot_id not in self.performance:
            self.performance[pilot.pilot_id] = PilotPerformance(
                pilot_id=pilot.pilot_id,
                missions_completed=0,
                missions_failed=0,
                total_credits_earned=0,
                total_experience_gained=0,
                average_mission_rating=0.0,
                skill_improvements={},
                decision_accuracy=0.0,
                last_updated=time.time()
            )
        
        perf = self.performance[pilot.pilot_id]
        
        if mission.status == "completed":
            perf.missions_completed += 1
        else:
            perf.missions_failed += 1
        
        perf.total_experience_gained += self._calculate_experience_gain(mission, pilot)
        perf.last_updated = time.time()
        
        # Calculate average mission rating
        total_missions = perf.missions_completed + perf.missions_failed
        if total_missions > 0:
            perf.average_mission_rating = perf.missions_completed / total_missions
    
    def get_pilot_performance(self, pilot_id: str) -> Optional[Dict[str, Any]]:
        """Get performance statistics for a pilot.
        
        Parameters
        ----------
        pilot_id : str
            ID of the pilot
            
        Returns
        -------
        Dict[str, Any], optional
            Performance statistics or None if not found
        """
        if pilot_id not in self.performance:
            return None
        
        perf = self.performance[pilot_id]
        pilot = self.pilots.get(pilot_id)
        
        return {
            "pilot_id": pilot_id,
            "pilot_name": pilot.name if pilot else "Unknown",
            "missions_completed": perf.missions_completed,
            "missions_failed": perf.missions_failed,
            "total_experience_gained": perf.total_experience_gained,
            "average_mission_rating": perf.average_mission_rating,
            "decision_accuracy": perf.decision_accuracy,
            "last_updated": perf.last_updated
        }
    
    def get_ai_piloting_statistics(self) -> Dict[str, Any]:
        """Get overall AI piloting statistics.
        
        Returns
        -------
        Dict[str, Any]
            AI piloting statistics
        """
        stats = {
            "total_pilots": len(self.pilots),
            "active_pilots": len(self.active_pilots),
            "total_missions": len(self.missions),
            "completed_missions": sum(1 for m in self.missions.values() if m.status == "completed"),
            "failed_missions": sum(1 for m in self.missions.values() if m.status == "failed"),
            "total_decisions": len(self.decisions),
            "successful_decisions": sum(1 for d in self.decisions if d.success),
            "pilots_by_behavior": {},
            "pilots_by_skill": {}
        }
        
        # Count pilots by behavior
        for pilot in self.pilots.values():
            behavior = pilot.behavior.value
            if behavior not in stats["pilots_by_behavior"]:
                stats["pilots_by_behavior"][behavior] = 0
            stats["pilots_by_behavior"][behavior] += 1
        
        # Count pilots by highest skill
        for pilot in self.pilots.values():
            highest_skill = max(pilot.skill_levels.items(), key=lambda x: x[1])[0].value
            if highest_skill not in stats["pilots_by_skill"]:
                stats["pilots_by_skill"][highest_skill] = 0
            stats["pilots_by_skill"][highest_skill] += 1
        
        return stats 
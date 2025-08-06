#!/usr/bin/env python3
"""
T-Unit (BH) PvP Phase 2
Mature Bounty Hunter mode for PvP targets (opt-in, off by default)

This module provides:
- Target acquisition from mission terminal → triangulation heuristics
- Range & LoS management; burst windows; escape path on counter-gank
- Strict safety checks: disable in high-risk policy, cooldowns between hunts
- Logs integrate with Seasonal BH Leaderboard (Batch 144)
"""

import json
import logging
import time
import random
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

# Import core modules with fallbacks
try:
    from core.location_selector import travel_to_target, locate_hotspot
except ImportError:
    travel_to_target = lambda *args, **kwargs: True
    locate_hotspot = lambda *args, **kwargs: {"coordinates": [0, 0]}

try:
    from core.waypoint_verifier import verify_waypoint_stability
except ImportError:
    verify_waypoint_stability = lambda *args, **kwargs: True

try:
    from modules.discord_alerts import send_discord_alert
except ImportError:
    send_discord_alert = lambda *args, **kwargs: None

try:
    from profession_logic.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from utils.license_hooks import requires_license
except ImportError:
    def requires_license(func):
        return func


class PvPTargetType(Enum):
    """PvP target types for bounty hunting."""
    PLAYER = "player"
    OVERT = "overt"
    TEF_FLAGGED = "tef_flagged"
    FACTION_ENEMY = "faction_enemy"
    GCW_TARGET = "gcw_target"


class HuntStatus(Enum):
    """Hunt status tracking."""
    SEARCHING = "searching"
    TRACKING = "tracking"
    ENGAGING = "engaging"
    ESCAPING = "escaping"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


class SafetyLevel(Enum):
    """Safety level for PvP operations."""
    SAFE = "safe"
    CAUTION = "caution"
    DANGER = "danger"
    CRITICAL = "critical"


@dataclass
class PvPTarget:
    """PvP target information."""
    name: str
    target_type: PvPTargetType
    location: Dict[str, Any]
    difficulty: str
    reward_credits: int
    risk_level: SafetyLevel
    last_seen: datetime
    triangulation_data: Dict[str, Any] = field(default_factory=dict)
    engagement_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class HuntSession:
    """Active hunt session data."""
    target: PvPTarget
    start_time: datetime
    status: HuntStatus
    current_location: Dict[str, Any]
    escape_path: List[Dict[str, Any]] = field(default_factory=list)
    burst_windows: List[Dict[str, Any]] = field(default_factory=list)
    safety_checks: List[Dict[str, Any]] = field(default_factory=list)
    cooldown_end: Optional[datetime] = None


class TUnitBHPvP:
    """T-Unit Bounty Hunter PvP Phase 2 implementation."""
    
    def __init__(self, 
                 config_file: str = "config/tunit_policy.json",
                 target_signals_file: str = "data/bh/target_signals.json"):
        """Initialize the T-Unit BH PvP mode.
        
        Parameters
        ----------
        config_file : str
            Path to T-Unit policy configuration
        target_signals_file : str
            Path to target signals data
        """
        self.config_file = Path(config_file)
        self.target_signals_file = Path(target_signals_file)
        self.config: Dict[str, Any] = {}
        self.target_signals: Dict[str, Any] = {}
        
        # Hunt state
        self.active_hunt: Optional[HuntSession] = None
        self.hunt_history: List[HuntSession] = []
        self.cooldown_until: Optional[datetime] = None
        
        # Safety state
        self.safety_level = SafetyLevel.SAFE
        self.last_safety_check = datetime.now()
        self.risk_assessment_data: Dict[str, Any] = {}
        
        # Load configuration
        self._load_config()
        self._load_target_signals()
        
        logger.info("[T-UNIT-BH-PVP] Initialized with safety-first approach")
    
    def _load_config(self) -> None:
        """Load T-Unit policy configuration."""
        if self.config_file.exists():
            with self.config_file.open("r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                "enabled": False,  # Off by default
                "opt_in_required": True,
                "safety_settings": {
                    "max_risk_level": "caution",
                    "cooldown_between_hunts": 300,  # 5 minutes
                    "max_hunt_duration": 1800,  # 30 minutes
                    "emergency_escape_threshold": 0.8,
                    "disable_in_high_risk": True,
                    "high_risk_zones": ["gcw_hotspots", "crowded_areas"],
                    "safe_zone_radius": 200,
                    "escape_path_length": 3
                },
                "target_acquisition": {
                    "mission_terminal_enabled": True,
                    "triangulation_heuristics": True,
                    "max_tracking_distance": 5000,
                    "min_target_confidence": 0.7,
                    "target_refresh_interval": 60
                },
                "combat_settings": {
                    "range_management": True,
                    "line_of_sight_check": True,
                    "burst_window_duration": 30,
                    "burst_window_cooldown": 120,
                    "escape_path_planning": True,
                    "counter_gank_response": True
                },
                "logging_settings": {
                    "integrate_with_leaderboard": True,
                    "log_hunt_details": True,
                    "log_safety_checks": True,
                    "log_triangulation_data": True,
                    "leaderboard_batch_144": True
                },
                "discord_alerts": {
                    "enabled": True,
                    "alert_types": ["hunt_start", "hunt_complete", "safety_alert"],
                    "include_risk_level": True,
                    "include_rewards": True
                }
            }
    
    def _load_target_signals(self) -> None:
        """Load target signals data."""
        if self.target_signals_file.exists():
            with self.target_signals_file.open("r", encoding="utf-8") as f:
                self.target_signals = json.load(f)
        else:
            # Default target signals
            self.target_signals = {
                "signal_patterns": {
                    "overt_player": {
                        "confidence_threshold": 0.8,
                        "refresh_rate": 30,
                        "location_accuracy": 0.9
                    },
                    "tef_flagged": {
                        "confidence_threshold": 0.7,
                        "refresh_rate": 45,
                        "location_accuracy": 0.8
                    },
                    "faction_enemy": {
                        "confidence_threshold": 0.6,
                        "refresh_rate": 60,
                        "location_accuracy": 0.7
                    }
                },
                "triangulation_heuristics": {
                    "max_distance": 5000,
                    "min_confidence": 0.7,
                    "location_update_interval": 30,
                    "path_prediction": True,
                    "zone_analysis": True
                }
            }
    
    def is_enabled(self) -> bool:
        """Check if PvP mode is enabled and safe to use."""
        if not self.config.get("enabled", False):
            return False
        
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            return False
        
        if self.safety_level in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]:
            return False
        
        return True
    
    def assess_safety_level(self) -> SafetyLevel:
        """Assess current safety level for PvP operations."""
        current_time = datetime.now()
        
        # Check if enough time has passed since last assessment
        if (current_time - self.last_safety_check).seconds < 30:
            return self.safety_level
        
        # Get current location and environment data
        current_location = self._get_current_location()
        nearby_players = self._scan_nearby_players()
        zone_risk = self._assess_zone_risk(current_location)
        
        # Calculate risk factors
        risk_score = 0.0
        
        # Player density risk
        if len(nearby_players) > 10:
            risk_score += 0.3
        elif len(nearby_players) > 5:
            risk_score += 0.2
        
        # Zone risk
        if zone_risk > 0.7:
            risk_score += 0.4
        elif zone_risk > 0.4:
            risk_score += 0.2
        
        # Recent activity risk
        if self._has_recent_pvp_activity():
            risk_score += 0.2
        
        # Determine safety level
        if risk_score >= 0.8:
            safety_level = SafetyLevel.CRITICAL
        elif risk_score >= 0.6:
            safety_level = SafetyLevel.DANGER
        elif risk_score >= 0.4:
            safety_level = SafetyLevel.CAUTION
        else:
            safety_level = SafetyLevel.SAFE
        
        self.safety_level = safety_level
        self.last_safety_check = current_time
        
        # Log safety assessment
        logger.info(f"[T-UNIT-BH-PVP] Safety assessment: {safety_level.value} (risk: {risk_score:.2f})")
        
        return safety_level
    
    def acquire_targets_from_terminal(self, terminal_text: str) -> List[PvPTarget]:
        """Acquire PvP targets from mission terminal with triangulation heuristics.
        
        Parameters
        ----------
        terminal_text : str
            Raw terminal text from BH mission terminal
            
        Returns
        -------
        List[PvPTarget]
            List of valid PvP targets
        """
        if not self.is_enabled():
            logger.warning("[T-UNIT-BH-PVP] Mode disabled or unsafe")
            return []
        
        targets = []
        
        # Parse terminal text for PvP targets
        parsed_targets = self._parse_terminal_text(terminal_text)
        
        for target_data in parsed_targets:
            # Apply triangulation heuristics
            triangulated_location = self._apply_triangulation_heuristics(target_data)
            
            if triangulated_location:
                # Create PvP target
                target = PvPTarget(
                    name=target_data["name"],
                    target_type=self._determine_target_type(target_data),
                    location=triangulated_location,
                    difficulty=target_data.get("difficulty", "medium"),
                    reward_credits=target_data.get("reward_credits", 0),
                    risk_level=self._assess_target_risk(target_data),
                    last_seen=datetime.now(),
                    triangulation_data=triangulated_location.get("triangulation", {})
                )
                
                targets.append(target)
        
        logger.info(f"[T-UNIT-BH-PVP] Acquired {len(targets)} targets from terminal")
        return targets
    
    def _parse_terminal_text(self, terminal_text: str) -> List[Dict[str, Any]]:
        """Parse BH terminal text for PvP targets."""
        targets = []
        lines = terminal_text.strip().split('\n')
        
        for line in lines:
            # Look for PvP target patterns
            if any(keyword in line.lower() for keyword in ['overt', 'tef', 'enemy', 'hostile']):
                target_data = self._extract_target_data(line)
                if target_data:
                    targets.append(target_data)
        
        return targets
    
    def _extract_target_data(self, line: str) -> Optional[Dict[str, Any]]:
        """Extract target data from terminal line."""
        try:
            # Parse line format: "TargetName X,Y distance reward"
            parts = line.strip().split()
            if len(parts) >= 4:
                name = parts[0]
                coords_str = parts[1]
                distance = int(parts[2].replace('m', ''))
                reward = int(parts[3].replace('c', ''))
                
                # Parse coordinates
                x, y = map(int, coords_str.split(','))
                
                return {
                    "name": name,
                    "coordinates": [x, y],
                    "distance": distance,
                    "reward_credits": reward,
                    "raw_line": line
                }
        except (ValueError, IndexError):
            pass
        
        return None
    
    def _apply_triangulation_heuristics(self, target_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply triangulation heuristics to improve target location accuracy."""
        base_location = target_data.get("coordinates", [0, 0])
        
        # Get signal patterns for target type
        target_type = self._determine_target_type(target_data)
        signal_pattern = self.target_signals["signal_patterns"].get(target_type.value, {})
        
        # Apply confidence threshold
        confidence = signal_pattern.get("confidence_threshold", 0.7)
        if confidence < self.target_signals["triangulation_heuristics"]["min_confidence"]:
            return None
        
        # Calculate triangulated location
        triangulated_coords = self._calculate_triangulated_location(base_location, target_data)
        
        # Add triangulation metadata
        location_data = {
            "planet": self._get_current_planet(),
            "coordinates": triangulated_coords,
            "confidence": confidence,
            "last_update": datetime.now().isoformat(),
            "triangulation": {
                "base_location": base_location,
                "confidence": confidence,
                "signal_strength": random.uniform(0.6, 0.9),
                "predicted_path": self._predict_target_path(triangulated_coords)
            }
        }
        
        return location_data
    
    def _calculate_triangulated_location(self, base_location: List[int], target_data: Dict[str, Any]) -> List[int]:
        """Calculate triangulated location using multiple reference points."""
        x, y = base_location
        
        # Apply triangulation algorithm
        # This is a simplified version - in practice, you'd use multiple reference points
        triangulation_factor = random.uniform(0.8, 1.2)
        
        triangulated_x = int(x * triangulation_factor)
        triangulated_y = int(y * triangulation_factor)
        
        return [triangulated_x, triangulated_y]
    
    def _predict_target_path(self, current_location: List[int]) -> List[List[int]]:
        """Predict target movement path."""
        # Simple path prediction based on current location
        # In practice, this would use historical movement data
        x, y = current_location
        
        predicted_path = [
            [x, y],
            [x + random.randint(-100, 100), y + random.randint(-100, 100)],
            [x + random.randint(-200, 200), y + random.randint(-200, 200)]
        ]
        
        return predicted_path
    
    def _determine_target_type(self, target_data: Dict[str, Any]) -> PvPTargetType:
        """Determine the type of PvP target."""
        name = target_data.get("name", "").lower()
        
        if "overt" in name or "hostile" in name:
            return PvPTargetType.OVERT
        elif "tef" in name or "flagged" in name:
            return PvPTargetType.TEF_FLAGGED
        elif "enemy" in name or "faction" in name:
            return PvPTargetType.FACTION_ENEMY
        elif "gcw" in name or "imperial" in name or "rebel" in name:
            return PvPTargetType.GCW_TARGET
        else:
            return PvPTargetType.PLAYER
    
    def _assess_target_risk(self, target_data: Dict[str, Any]) -> SafetyLevel:
        """Assess risk level for a specific target."""
        # Base risk assessment
        risk_score = 0.0
        
        # Distance risk
        distance = target_data.get("distance", 0)
        if distance > 3000:
            risk_score += 0.3
        elif distance > 1500:
            risk_score += 0.2
        
        # Reward risk (higher rewards = higher risk)
        reward = target_data.get("reward_credits", 0)
        if reward > 2000:
            risk_score += 0.4
        elif reward > 1000:
            risk_score += 0.2
        
        # Target type risk
        target_type = self._determine_target_type(target_data)
        if target_type == PvPTargetType.OVERT:
            risk_score += 0.3
        elif target_type == PvPTargetType.TEF_FLAGGED:
            risk_score += 0.2
        
        # Determine risk level
        if risk_score >= 0.8:
            return SafetyLevel.CRITICAL
        elif risk_score >= 0.6:
            return SafetyLevel.DANGER
        elif risk_score >= 0.4:
            return SafetyLevel.CAUTION
        else:
            return SafetyLevel.SAFE
    
    def start_hunt(self, target: PvPTarget) -> bool:
        """Start a PvP hunt session.
        
        Parameters
        ----------
        target : PvPTarget
            Target to hunt
            
        Returns
        -------
        bool
            True if hunt started successfully
        """
        if not self.is_enabled():
            logger.warning("[T-UNIT-BH-PVP] Cannot start hunt - mode disabled")
            return False
        
        if self.active_hunt:
            logger.warning("[T-UNIT-BH-PVP] Hunt already in progress")
            return False
        
        # Final safety check
        if self.assess_safety_level() in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]:
            logger.warning("[T-UNIT-BH-PVP] Safety level too high for hunt")
            return False
        
        # Create hunt session
        self.active_hunt = HuntSession(
            target=target,
            start_time=datetime.now(),
            status=HuntStatus.SEARCHING,
            current_location=self._get_current_location()
        )
        
        # Plan escape path
        self.active_hunt.escape_path = self._plan_escape_path()
        
        # Send Discord alert
        if self.config.get("discord_alerts", {}).get("enabled", False):
            self._send_hunt_alert("hunt_start", target)
        
        logger.info(f"[T-UNIT-BH-PVP] Started hunt for {target.name}")
        return True
    
    def _plan_escape_path(self) -> List[Dict[str, Any]]:
        """Plan escape path for emergency situations."""
        current_location = self._get_current_location()
        escape_path = []
        
        # Find safe zones within escape distance
        safe_zones = self._find_safe_zones(current_location)
        
        for zone in safe_zones[:self.config["safety_settings"]["escape_path_length"]]:
            escape_path.append({
                "location": zone["coordinates"],
                "type": "safe_zone",
                "distance": zone["distance"],
                "risk_level": zone["risk_level"]
            })
        
        return escape_path
    
    def _find_safe_zones(self, current_location: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find safe zones for escape planning."""
        # This would integrate with zone data
        # For now, return mock safe zones
        safe_zones = [
            {
                "coordinates": [current_location.get("x", 0) + 500, current_location.get("y", 0) + 500],
                "distance": 500,
                "risk_level": SafetyLevel.SAFE.value
            },
            {
                "coordinates": [current_location.get("x", 0) - 300, current_location.get("y", 0) - 300],
                "distance": 300,
                "risk_level": SafetyLevel.SAFE.value
            }
        ]
        
        return safe_zones
    
    def manage_range_and_los(self) -> Dict[str, Any]:
        """Manage range and line of sight for optimal engagement."""
        if not self.active_hunt:
            return {"status": "no_active_hunt"}
        
        target_location = self.active_hunt.target.location
        current_location = self._get_current_location()
        
        # Calculate optimal range
        optimal_range = self._calculate_optimal_range()
        current_distance = self._calculate_distance(current_location, target_location)
        
        # Check line of sight
        los_clear = self._check_line_of_sight(current_location, target_location)
        
        # Determine action
        if current_distance > optimal_range * 1.5:
            action = "approach"
        elif current_distance < optimal_range * 0.5:
            action = "retreat"
        elif not los_clear:
            action = "reposition"
        else:
            action = "engage"
        
        return {
            "status": "managing_range",
            "action": action,
            "current_distance": current_distance,
            "optimal_range": optimal_range,
            "line_of_sight": los_clear,
            "target_location": target_location
        }
    
    def _calculate_optimal_range(self) -> float:
        """Calculate optimal engagement range."""
        # Base optimal range (would vary by weapon/combat style)
        return 150.0
    
    def _calculate_distance(self, loc1: Dict[str, Any], loc2: Dict[str, Any]) -> float:
        """Calculate distance between two locations."""
        x1, y1 = loc1.get("coordinates", [0, 0])
        x2, y2 = loc2.get("coordinates", [0, 0])
        
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    
    def _check_line_of_sight(self, loc1: Dict[str, Any], loc2: Dict[str, Any]) -> bool:
        """Check if line of sight is clear between two points."""
        # Simplified LoS check
        # In practice, this would check for obstacles, terrain, etc.
        return random.choice([True, False])
    
    def manage_burst_windows(self) -> Dict[str, Any]:
        """Manage burst windows for optimal damage output."""
        if not self.active_hunt:
            return {"status": "no_active_hunt"}
        
        current_time = datetime.now()
        burst_duration = self.config["combat_settings"]["burst_window_duration"]
        burst_cooldown = self.config["combat_settings"]["burst_window_cooldown"]
        
        # Check if burst window is available
        available_bursts = []
        for burst in self.active_hunt.burst_windows:
            if (current_time - burst["start_time"]).seconds < burst_duration:
                available_bursts.append(burst)
        
        # Create new burst window if cooldown has passed
        last_burst = max(self.active_hunt.burst_windows, key=lambda x: x["start_time"]) if self.active_hunt.burst_windows else None
        can_create_burst = True
        
        if last_burst:
            time_since_last = (current_time - last_burst["start_time"]).seconds
            can_create_burst = time_since_last >= burst_cooldown
        
        if can_create_burst:
            new_burst = {
                "start_time": current_time,
                "duration": burst_duration,
                "damage_multiplier": 1.5,
                "accuracy_boost": 0.2
            }
            self.active_hunt.burst_windows.append(new_burst)
        
        return {
            "status": "burst_windows_managed",
            "available_bursts": len(available_bursts),
            "can_create_burst": can_create_burst,
            "total_bursts": len(self.active_hunt.burst_windows)
        }
    
    def handle_counter_gank(self) -> Dict[str, Any]:
        """Handle counter-gank situations with escape path."""
        if not self.active_hunt:
            return {"status": "no_active_hunt"}
        
        # Detect counter-gank
        counter_gank_detected = self._detect_counter_gank()
        
        if counter_gank_detected:
            # Execute escape plan
            escape_success = self._execute_escape_plan()
            
            if escape_success:
                self.active_hunt.status = HuntStatus.ESCAPING
                logger.warning("[T-UNIT-BH-PVP] Counter-gank detected - executing escape plan")
                
                return {
                    "status": "counter_gank_handled",
                    "escape_success": True,
                    "escape_path_used": self.active_hunt.escape_path
                }
            else:
                self.active_hunt.status = HuntStatus.FAILED
                logger.error("[T-UNIT-BH-PVP] Escape plan failed")
                
                return {
                    "status": "counter_gank_failed",
                    "escape_success": False
                }
        
        return {
            "status": "no_counter_gank",
            "counter_gank_detected": False
        }
    
    def _detect_counter_gank(self) -> bool:
        """Detect if a counter-gank is occurring."""
        # Check for multiple nearby hostile players
        nearby_players = self._scan_nearby_players()
        hostile_count = sum(1 for player in nearby_players if player.get("hostile", False))
        
        return hostile_count >= 2
    
    def _execute_escape_plan(self) -> bool:
        """Execute the planned escape route."""
        if not self.active_hunt.escape_path:
            return False
        
        # Use the first safe zone in escape path
        escape_target = self.active_hunt.escape_path[0]
        
        # Travel to escape location
        travel_success = self._travel_to_location(escape_target["location"])
        
        return travel_success
    
    def _travel_to_location(self, location: List[int]) -> bool:
        """Travel to a specific location."""
        # Simplified travel implementation
        # In practice, this would use the travel system
        logger.info(f"[T-UNIT-BH-PVP] Traveling to {location}")
        return True
    
    def complete_hunt(self, success: bool = True) -> bool:
        """Complete the current hunt session.
        
        Parameters
        ----------
        success : bool
            Whether the hunt was successful
            
        Returns
        -------
        bool
            True if hunt completed successfully
        """
        if not self.active_hunt:
            return False
        
        # Update hunt status
        if success:
            self.active_hunt.status = HuntStatus.COMPLETED
        else:
            self.active_hunt.status = HuntStatus.FAILED
        
        # Add to history
        self.hunt_history.append(self.active_hunt)
        
        # Set cooldown
        cooldown_duration = self.config["safety_settings"]["cooldown_between_hunts"]
        self.cooldown_until = datetime.now() + timedelta(seconds=cooldown_duration)
        
        # Log hunt completion
        self._log_hunt_completion(success)
        
        # Send Discord alert
        if self.config.get("discord_alerts", {}).get("enabled", False):
            self._send_hunt_alert("hunt_complete", self.active_hunt.target, success)
        
        # Clear active hunt
        self.active_hunt = None
        
        logger.info(f"[T-UNIT-BH-PVP] Hunt completed - success: {success}")
        return True
    
    def _log_hunt_completion(self, success: bool) -> None:
        """Log hunt completion for leaderboard integration."""
        if not self.config["logging_settings"]["integrate_with_leaderboard"]:
            return
        
        hunt_data = {
            "target_name": self.active_hunt.target.name,
            "target_type": self.active_hunt.target.target_type.value,
            "success": success,
            "duration": (datetime.now() - self.active_hunt.start_time).seconds,
            "reward_credits": self.active_hunt.target.reward_credits,
            "timestamp": datetime.now().isoformat(),
            "safety_level": self.safety_level.value,
            "escape_path_used": len(self.active_hunt.escape_path),
            "burst_windows_used": len(self.active_hunt.burst_windows)
        }
        
        # Save to leaderboard data
        self._save_to_leaderboard(hunt_data)
    
    def _save_to_leaderboard(self, hunt_data: Dict[str, Any]) -> None:
        """Save hunt data to leaderboard (Batch 144 integration)."""
        leaderboard_file = Path("data/bh/leaderboard_data.json")
        
        if not leaderboard_file.exists():
            leaderboard_data = {"hunts": []}
        else:
            with leaderboard_file.open("r", encoding="utf-8") as f:
                leaderboard_data = json.load(f)
        
        leaderboard_data["hunts"].append(hunt_data)
        
        with leaderboard_file.open("w", encoding="utf-8") as f:
            json.dump(leaderboard_data, f, indent=2)
    
    def _send_hunt_alert(self, alert_type: str, target: PvPTarget, success: bool = True) -> None:
        """Send Discord alert for hunt events."""
        alert_config = self.config.get("discord_alerts", {})
        
        if not alert_config.get("enabled", False):
            return
        
        if alert_type not in alert_config.get("alert_types", []):
            return
        
        message = f"T-Unit BH PvP: {alert_type.replace('_', ' ').title()}"
        message += f"\nTarget: {target.name}"
        message += f"\nType: {target.target_type.value}"
        message += f"\nRisk Level: {target.risk_level.value}"
        
        if alert_config.get("include_rewards", False):
            message += f"\nReward: {target.reward_credits} credits"
        
        if alert_config.get("include_risk_level", False):
            message += f"\nSafety Level: {self.safety_level.value}"
        
        if alert_type == "hunt_complete":
            message += f"\nSuccess: {success}"
        
        send_discord_alert(message, "bounty_hunter")
    
    def _get_current_location(self) -> Dict[str, Any]:
        """Get current player location."""
        # Mock location - in practice, this would get from game state
        return {
            "planet": "tatooine",
            "city": "mos_eisley",
            "coordinates": [100, 200],
            "zone": "cantina"
        }
    
    def _get_current_planet(self) -> str:
        """Get current planet."""
        return self._get_current_location().get("planet", "unknown")
    
    def _scan_nearby_players(self) -> List[Dict[str, Any]]:
        """Scan for nearby players."""
        # Mock player scan - in practice, this would use OCR/vision
        return [
            {"name": "Player1", "distance": 50, "hostile": False},
            {"name": "Player2", "distance": 100, "hostile": True},
            {"name": "Player3", "distance": 200, "hostile": False}
        ]
    
    def _assess_zone_risk(self, location: Dict[str, Any]) -> float:
        """Assess risk level of current zone."""
        # Mock zone risk assessment
        return random.uniform(0.1, 0.8)
    
    def _has_recent_pvp_activity(self) -> bool:
        """Check if there has been recent PvP activity."""
        # Mock recent activity check
        return random.choice([True, False])


@requires_license
def run_tunit_bh_pvp(config: Dict[str, Any] = None) -> None:
    """Run the T-Unit BH PvP mode.
    
    Parameters
    ----------
    config : Dict[str, Any], optional
        Configuration overrides
    """
    # Initialize T-Unit BH PvP
    tunit = TUnitBHPvP()
    
    if config:
        tunit.config.update(config)
    
    # Check if mode is enabled
    if not tunit.is_enabled():
        logger.info("[T-UNIT-BH-PVP] Mode disabled or unsafe")
        return
    
    # Assess safety
    safety_level = tunit.assess_safety_level()
    logger.info(f"[T-UNIT-BH-PVP] Safety level: {safety_level.value}")
    
    # Main hunt loop
    while tunit.is_enabled():
        try:
            # Check for available targets
            # This would integrate with mission terminal scanning
            terminal_text = ""  # Would get from OCR
            
            if terminal_text:
                targets = tunit.acquire_targets_from_terminal(terminal_text)
                
                for target in targets:
                    if tunit.start_hunt(target):
                        # Hunt loop
                        while tunit.active_hunt and tunit.active_hunt.status != HuntStatus.COMPLETED:
                            # Manage range and LoS
                            range_data = tunit.manage_range_and_los()
                            
                            # Manage burst windows
                            burst_data = tunit.manage_burst_windows()
                            
                            # Check for counter-gank
                            counter_gank_data = tunit.handle_counter_gank()
                            
                            # Safety check
                            if tunit.assess_safety_level() in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]:
                                tunit.complete_hunt(success=False)
                                break
                            
                            time.sleep(1)  # Hunt cycle delay
                        
                        # Complete hunt
                        tunit.complete_hunt(success=True)
                        break  # One hunt per cycle
            
            # Wait before next cycle
            time.sleep(30)
            
        except KeyboardInterrupt:
            logger.info("[T-UNIT-BH-PVP] Hunt interrupted by user")
            break
        except Exception as e:
            logger.error(f"[T-UNIT-BH-PVP] Error in hunt loop: {e}")
            time.sleep(60)  # Error recovery delay


if __name__ == "__main__":
    run_tunit_bh_pvp() 
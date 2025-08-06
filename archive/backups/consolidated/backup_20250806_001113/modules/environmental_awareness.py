#!/usr/bin/env python3
"""Environmental Awareness & Risk Avoidance System for MS11 Batch 115."""

import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import random
import cv2
import numpy as np

from core.ocr import get_ocr_engine
from core.anti_detection.defense_manager import DefenseManager


class RiskLevel(Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Type of environmental threat."""
    HOSTILE_NPC_CLUSTER = "hostile_npc_cluster"
    HIGH_GCW_ZONE = "high_gcw_zone"
    AFK_REPORTING_HOTSPOT = "afk_reporting_hotspot"
    STARPORT_PROXIMITY = "starport_proximity"
    CROWDED_ZONE = "crowded_zone"
    DEATH_LOCATION = "death_location"
    PLAYER_CLUSTER = "player_cluster"


@dataclass
class ThreatDetection:
    """Represents a detected environmental threat."""
    threat_type: ThreatType
    risk_level: RiskLevel
    location: Tuple[int, int]  # x, y coordinates
    zone: str
    planet: str
    description: str
    confidence: float
    timestamp: datetime
    player_count: Optional[int] = None
    npc_count: Optional[int] = None
    gcw_level: Optional[int] = None
    distance_to_starport: Optional[float] = None


@dataclass
class RiskZone:
    """Represents a high-risk zone with avoidance strategies."""
    zone_name: str
    planet: str
    coordinates: Tuple[int, int]
    risk_level: RiskLevel
    threat_types: List[ThreatType]
    avoidance_strategy: str
    safe_alternatives: List[str]
    last_updated: datetime
    player_reports: List[Dict[str, Any]] = None


@dataclass
class EnvironmentalState:
    """Current environmental awareness state."""
    current_zone: str
    current_planet: str
    current_coordinates: Tuple[int, int]
    detected_threats: List[ThreatDetection]
    risk_level: RiskLevel
    last_scan_time: Optional[datetime] = None
    movement_history: List[Tuple[int, int, datetime]] = None
    death_locations: List[Tuple[int, int, datetime]] = None
    safe_zones: List[Tuple[int, int, int, int]] = None  # x, y, width, height


class EnvironmentalAwareness:
    """Environmental awareness and risk avoidance system."""
    
    def __init__(self, config_path: str = "config/environmental_awareness_config.json"):
        """Initialize the environmental awareness system.
        
        Parameters
        ----------
        config_path : str
            Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Initialize components
        self.ocr_engine = get_ocr_engine()
        self.defense_manager = DefenseManager()
        
        # State management
        self.state = EnvironmentalState(
            current_zone="unknown",
            current_planet="unknown",
            current_coordinates=(0, 0),
            detected_threats=[],
            risk_level=RiskLevel.LOW,
            movement_history=[],
            death_locations=[],
            safe_zones=[]
        )
        
        # Risk zones database
        self.risk_zones: Dict[str, RiskZone] = {}
        self._load_risk_zones()
        
        # Monitoring thread
        self.monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring_flag = False
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        self.logger.info("[ENVIRONMENTAL_AWARENESS] System initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning("[ENVIRONMENTAL_AWARENESS] Config file not found, using defaults")
            return self._create_default_config()
        except json.JSONDecodeError as e:
            self.logger.error(f"[ENVIRONMENTAL_AWARENESS] Config file error: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default configuration."""
        return {
            "environmental_awareness": {
                "enabled": True,
                "scan_interval": 30.0,
                "risk_thresholds": {
                    "hostile_npc_cluster": 3,
                    "player_cluster": 5,
                    "gcw_zone_threshold": 50,
                    "starport_proximity": 100.0,
                    "crowded_zone_threshold": 8
                },
                "avoidance_strategies": {
                    "hostile_npc_cluster": "move_to_safe_zone",
                    "high_gcw_zone": "change_zone",
                    "afk_reporting_hotspot": "random_movement",
                    "starport_proximity": "reduce_activity",
                    "crowded_zone": "move_to_less_crowded",
                    "death_location": "avoid_area"
                },
                "safe_zones": {
                    "mos_eisley": [(3500, -4800, 200, 200)],
                    "anchorhead": [(3000, -5500, 150, 150)],
                    "theed": [(5000, -4000, 180, 180)]
                },
                "gcw_zones": {
                    "high_risk": ["restuss", "battlefield", "warzone"],
                    "medium_risk": ["combat_zone", "pvp_area"],
                    "low_risk": ["safe_zone", "city_center"]
                }
            }
        }
    
    def _setup_logging(self):
        """Setup logging for environmental awareness events."""
        log_dir = Path("logs/environmental_awareness")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a file handler for environmental logs
        log_file = log_dir / f"environmental_{time.strftime('%Y%m%d')}.json"
        
        # Log environmental events in JSON format
        self.log_events = []
    
    def _load_risk_zones(self):
        """Load risk zones from data file."""
        risk_zones_file = Path("data/environmental_risk_zones.json")
        if risk_zones_file.exists():
            try:
                with open(risk_zones_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for zone_data in data.get("risk_zones", []):
                        zone = RiskZone(
                            zone_name=zone_data["zone_name"],
                            planet=zone_data["planet"],
                            coordinates=tuple(zone_data["coordinates"]),
                            risk_level=RiskLevel(zone_data["risk_level"]),
                            threat_types=[ThreatType(t) for t in zone_data["threat_types"]],
                            avoidance_strategy=zone_data["avoidance_strategy"],
                            safe_alternatives=zone_data["safe_alternatives"],
                            last_updated=datetime.fromisoformat(zone_data["last_updated"]),
                            player_reports=zone_data.get("player_reports", [])
                        )
                        self.risk_zones[f"{zone.planet}_{zone.zone_name}"] = zone
            except Exception as e:
                self.logger.error(f"[ENVIRONMENTAL_AWARENESS] Failed to load risk zones: {e}")
    
    def start_monitoring(self, character_name: str) -> bool:
        """Start environmental monitoring.
        
        Parameters
        ----------
        character_name : str
            Name of the character to monitor
            
        Returns
        -------
        bool
            True if monitoring started successfully
        """
        if not self.config["environmental_awareness"]["enabled"]:
            self.logger.info("[ENVIRONMENTAL_AWARENESS] Environmental awareness disabled in config")
            return False
        
        # Start monitoring thread
        self._stop_monitoring_flag = False
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info(f"[ENVIRONMENTAL_AWARENESS] Started monitoring for {character_name}")
        return True
    
    def stop_monitoring(self) -> Optional[Dict]:
        """Stop environmental monitoring.
        
        Returns
        -------
        dict or None
            Summary of monitoring session
        """
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self._stop_monitoring_flag = True
            self.monitoring_thread.join(timeout=5.0)
            
            # Generate session summary
            summary = {
                "session_duration": self._get_session_duration(),
                "threats_detected": len(self.state.detected_threats),
                "risk_levels": self._get_risk_level_distribution(),
                "zones_visited": self._get_zones_visited(),
                "avoidance_actions": self._get_avoidance_actions()
            }
            
            self.logger.info("[ENVIRONMENTAL_AWARENESS] Monitoring stopped")
            return summary
        
        return None
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        scan_interval = self.config["environmental_awareness"]["scan_interval"]
        
        while not self._stop_monitoring_flag:
            try:
                # Perform environmental scan
                self._perform_environmental_scan()
                
                # Update risk assessment
                self._update_risk_assessment()
                
                # Check for immediate threats
                self._check_immediate_threats()
                
                # Sleep for scan interval
                time.sleep(scan_interval)
                
            except Exception as e:
                self.logger.error(f"[ENVIRONMENTAL_AWARENESS] Monitoring error: {e}")
                time.sleep(5.0)  # Brief pause on error
    
    def _perform_environmental_scan(self):
        """Perform a comprehensive environmental scan."""
        try:
            # Capture screen for analysis
            screen = self._capture_screen()
            if screen is None:
                return
            
            # Detect threats
            threats = []
            
            # Detect hostile NPC clusters
            npc_threats = self._detect_hostile_npc_clusters(screen)
            threats.extend(npc_threats)
            
            # Detect player clusters
            player_threats = self._detect_player_clusters(screen)
            threats.extend(player_threats)
            
            # Detect GCW zones
            gcw_threats = self._detect_gcw_zones(screen)
            threats.extend(gcw_threats)
            
            # Detect starport proximity
            starport_threats = self._detect_starport_proximity()
            threats.extend(starport_threats)
            
            # Detect AFK reporting hotspots
            afk_threats = self._detect_afk_reporting_hotspots(screen)
            threats.extend(afk_threats)
            
            # Update state
            self.state.detected_threats = threats
            self.state.last_scan_time = datetime.now()
            
            # Log scan results
            self._log_environmental_scan(threats)
            
        except Exception as e:
            self.logger.error(f"[ENVIRONMENTAL_AWARENESS] Scan error: {e}")
    
    def _capture_screen(self) -> Optional[np.ndarray]:
        """Capture current screen for analysis."""
        try:
            # This would integrate with the existing screen capture system
            # For now, return None to indicate no screen available
            return None
        except Exception as e:
            self.logger.error(f"[ENVIRONMENTAL_AWARENESS] Screen capture error: {e}")
            return None
    
    def _detect_hostile_npc_clusters(self, screen: np.ndarray) -> List[ThreatDetection]:
        """Detect clusters of hostile NPCs."""
        threats = []
        
        try:
            # Use OCR to detect NPC names and hostile indicators
            if screen is not None:
                # Extract text from screen
                text_result = self.ocr_engine.extract_text(screen)
                
                if text_result and text_result.text:
                    # Look for hostile NPC indicators
                    hostile_indicators = [
                        "Imperial", "Rebel", "Bounty Hunter", "Pirate",
                        "Sith", "Jedi", "Mercenary", "Assassin"
                    ]
                    
                    npc_count = 0
                    for indicator in hostile_indicators:
                        if indicator.lower() in text_result.text.lower():
                            npc_count += 1
                    
                    if npc_count >= self.config["environmental_awareness"]["risk_thresholds"]["hostile_npc_cluster"]:
                        threat = ThreatDetection(
                            threat_type=ThreatType.HOSTILE_NPC_CLUSTER,
                            risk_level=RiskLevel.HIGH if npc_count > 5 else RiskLevel.MEDIUM,
                            location=self.state.current_coordinates,
                            zone=self.state.current_zone,
                            planet=self.state.current_planet,
                            description=f"Detected {npc_count} hostile NPCs",
                            confidence=0.7,
                            timestamp=datetime.now(),
                            npc_count=npc_count
                        )
                        threats.append(threat)
            
        except Exception as e:
            self.logger.error(f"[ENVIRONMENTAL_AWARENESS] Hostile NPC detection error: {e}")
        
        return threats
    
    def _detect_player_clusters(self, screen: np.ndarray) -> List[ThreatDetection]:
        """Detect clusters of players (potential AFK reporting risk)."""
        threats = []
        
        try:
            # Use OCR to detect player names
            if screen is not None:
                text_result = self.ocr_engine.extract_text(screen)
                
                if text_result and text_result.text:
                    # Look for player name patterns
                    player_count = 0
                    lines = text_result.text.split('\n')
                    
                    for line in lines:
                        # Simple heuristic for player detection
                        if any(keyword in line.lower() for keyword in ["player", "character", "avatar"]):
                            player_count += 1
                    
                    if player_count >= self.config["environmental_awareness"]["risk_thresholds"]["player_cluster"]:
                        threat = ThreatDetection(
                            threat_type=ThreatType.PLAYER_CLUSTER,
                            risk_level=RiskLevel.MEDIUM,
                            location=self.state.current_coordinates,
                            zone=self.state.current_zone,
                            planet=self.state.current_planet,
                            description=f"Detected {player_count} players nearby",
                            confidence=0.6,
                            timestamp=datetime.now(),
                            player_count=player_count
                        )
                        threats.append(threat)
            
        except Exception as e:
            self.logger.error(f"[ENVIRONMENTAL_AWARENESS] Player cluster detection error: {e}")
        
        return threats
    
    def _detect_gcw_zones(self, screen: np.ndarray) -> List[ThreatDetection]:
        """Detect high GCW (Galactic Civil War) zones."""
        threats = []
        
        try:
            # Check if current zone is in high-risk GCW zones
            high_risk_zones = self.config["environmental_awareness"]["gcw_zones"]["high_risk"]
            
            if self.state.current_zone.lower() in [zone.lower() for zone in high_risk_zones]:
                threat = ThreatDetection(
                    threat_type=ThreatType.HIGH_GCW_ZONE,
                    risk_level=RiskLevel.CRITICAL,
                    location=self.state.current_coordinates,
                    zone=self.state.current_zone,
                    planet=self.state.current_planet,
                    description="High GCW zone detected",
                    confidence=0.9,
                    timestamp=datetime.now(),
                    gcw_level=100
                )
                threats.append(threat)
            
        except Exception as e:
            self.logger.error(f"[ENVIRONMENTAL_AWARENESS] GCW zone detection error: {e}")
        
        return threats
    
    def _detect_starport_proximity(self) -> List[ThreatDetection]:
        """Detect proximity to starports (potential AFK reporting risk)."""
        threats = []
        
        try:
            # Calculate distance to nearest starport
            starport_locations = {
                "mos_eisley": (3520, -4800),
                "anchorhead": (3000, -5500),
                "theed": (5000, -4000)
            }
            
            current_pos = self.state.current_coordinates
            min_distance = float('inf')
            
            for zone, starport_pos in starport_locations.items():
                if zone in self.state.current_zone.lower():
                    distance = self._calculate_distance(current_pos, starport_pos)
                    min_distance = min(min_distance, distance)
            
            proximity_threshold = self.config["environmental_awareness"]["risk_thresholds"]["starport_proximity"]
            
            if min_distance < proximity_threshold:
                threat = ThreatDetection(
                    threat_type=ThreatType.STARPORT_PROXIMITY,
                    risk_level=RiskLevel.MEDIUM,
                    location=self.state.current_coordinates,
                    zone=self.state.current_zone,
                    planet=self.state.current_planet,
                    description=f"Too close to starport ({min_distance:.1f} units)",
                    confidence=0.8,
                    timestamp=datetime.now(),
                    distance_to_starport=min_distance
                )
                threats.append(threat)
            
        except Exception as e:
            self.logger.error(f"[ENVIRONMENTAL_AWARENESS] Starport proximity detection error: {e}")
        
        return threats
    
    def _detect_afk_reporting_hotspots(self, screen: np.ndarray) -> List[ThreatDetection]:
        """Detect AFK reporting hotspots."""
        threats = []
        
        try:
            # Check for crowded areas with many players
            if screen is not None:
                text_result = self.ocr_engine.extract_text(screen)
                
                if text_result and text_result.text:
                    # Look for indicators of crowded areas
                    crowded_indicators = [
                        "crowded", "busy", "many players", "popular",
                        "trade center", "market", "gathering"
                    ]
                    
                    crowded_score = 0
                    for indicator in crowded_indicators:
                        if indicator.lower() in text_result.text.lower():
                            crowded_score += 1
                    
                    if crowded_score >= 2:  # Multiple indicators
                        threat = ThreatDetection(
                            threat_type=ThreatType.AFK_REPORTING_HOTSPOT,
                            risk_level=RiskLevel.HIGH,
                            location=self.state.current_coordinates,
                            zone=self.state.current_zone,
                            planet=self.state.current_planet,
                            description="Potential AFK reporting hotspot detected",
                            confidence=0.7,
                            timestamp=datetime.now()
                        )
                        threats.append(threat)
            
        except Exception as e:
            self.logger.error(f"[ENVIRONMENTAL_AWARENESS] AFK hotspot detection error: {e}")
        
        return threats
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between two positions."""
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
    
    def _update_risk_assessment(self):
        """Update overall risk assessment based on detected threats."""
        if not self.state.detected_threats:
            self.state.risk_level = RiskLevel.LOW
            return
        
        # Calculate risk level based on threats
        risk_scores = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 0,
            RiskLevel.HIGH: 0,
            RiskLevel.CRITICAL: 0
        }
        
        for threat in self.state.detected_threats:
            risk_scores[threat.risk_level] += 1
        
        # Determine overall risk level
        if risk_scores[RiskLevel.CRITICAL] > 0:
            self.state.risk_level = RiskLevel.CRITICAL
        elif risk_scores[RiskLevel.HIGH] > 0:
            self.state.risk_level = RiskLevel.HIGH
        elif risk_scores[RiskLevel.MEDIUM] > 0:
            self.state.risk_level = RiskLevel.MEDIUM
        else:
            self.state.risk_level = RiskLevel.LOW
    
    def _check_immediate_threats(self):
        """Check for immediate threats that require immediate action."""
        critical_threats = [t for t in self.state.detected_threats if t.risk_level == RiskLevel.CRITICAL]
        
        if critical_threats:
            self.logger.warning(f"[ENVIRONMENTAL_AWARENESS] Critical threats detected: {len(critical_threats)}")
            self._trigger_avoidance_action(critical_threats[0])
    
    def _trigger_avoidance_action(self, threat: ThreatDetection):
        """Trigger appropriate avoidance action for a threat."""
        strategy = self.config["environmental_awareness"]["avoidance_strategies"].get(
            threat.threat_type.value, "move_to_safe_zone"
        )
        
        self.logger.info(f"[ENVIRONMENTAL_AWARENESS] Triggering avoidance: {strategy}")
        
        if strategy == "move_to_safe_zone":
            self._move_to_safe_zone()
        elif strategy == "change_zone":
            self._change_zone()
        elif strategy == "random_movement":
            self._perform_random_movement()
        elif strategy == "reduce_activity":
            self._reduce_activity()
        elif strategy == "move_to_less_crowded":
            self._move_to_less_crowded()
        elif strategy == "avoid_area":
            self._avoid_area(threat.location)
    
    def _move_to_safe_zone(self):
        """Move to nearest safe zone."""
        safe_zones = self.config["environmental_awareness"]["safe_zones"].get(
            self.state.current_zone.lower(), []
        )
        
        if safe_zones:
            # Find closest safe zone
            current_pos = self.state.current_coordinates
            closest_zone = min(safe_zones, key=lambda zone: self._calculate_distance(
                current_pos, (zone[0], zone[1])
            ))
            
            self.logger.info(f"[ENVIRONMENTAL_AWARENESS] Moving to safe zone: {closest_zone}")
            # This would integrate with the movement system
            self._record_movement(closest_zone[0], closest_zone[1])
    
    def _change_zone(self):
        """Change to a different zone."""
        # Get alternative zones from risk zones
        alternatives = []
        for zone in self.risk_zones.values():
            if zone.planet == self.state.current_planet and zone.risk_level == RiskLevel.LOW:
                alternatives.append(zone.zone_name)
        
        if alternatives:
            target_zone = random.choice(alternatives)
            self.logger.info(f"[ENVIRONMENTAL_AWARENESS] Changing to safer zone: {target_zone}")
            # This would integrate with the travel system
    
    def _perform_random_movement(self):
        """Perform random movement to avoid detection."""
        # Generate random movement within current zone
        current_pos = self.state.current_coordinates
        random_offset = (
            random.randint(-100, 100),
            random.randint(-100, 100)
        )
        new_pos = (current_pos[0] + random_offset[0], current_pos[1] + random_offset[1])
        
        self.logger.info(f"[ENVIRONMENTAL_AWARENESS] Random movement to: {new_pos}")
        self._record_movement(new_pos[0], new_pos[1])
    
    def _reduce_activity(self):
        """Reduce activity to avoid detection."""
        self.logger.info("[ENVIRONMENTAL_AWARENESS] Reducing activity")
        # This would integrate with the anti-detection system
    
    def _move_to_less_crowded(self):
        """Move to a less crowded area."""
        self.logger.info("[ENVIRONMENTAL_AWARENESS] Moving to less crowded area")
        # This would integrate with the movement system
    
    def _avoid_area(self, location: Tuple[int, int]):
        """Avoid a specific area."""
        self.logger.info(f"[ENVIRONMENTAL_AWARENESS] Avoiding area: {location}")
        # This would integrate with the movement system
    
    def _record_movement(self, x: int, y: int):
        """Record movement for tracking."""
        self.state.movement_history.append((x, y, datetime.now()))
        
        # Keep only recent movement history
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.state.movement_history = [
            move for move in self.state.movement_history
            if move[2] > cutoff_time
        ]
    
    def _log_environmental_scan(self, threats: List[ThreatDetection]):
        """Log environmental scan results."""
        scan_event = {
            "timestamp": datetime.now().isoformat(),
            "zone": self.state.current_zone,
            "planet": self.state.current_planet,
            "coordinates": self.state.current_coordinates,
            "threats_detected": len(threats),
            "risk_level": self.state.risk_level.value,
            "threats": [asdict(threat) for threat in threats]
        }
        
        self.log_events.append(scan_event)
    
    def update_location(self, zone: str, planet: str, coordinates: Tuple[int, int]):
        """Update current location information.
        
        Parameters
        ----------
        zone : str
            Current zone name
        planet : str
            Current planet name
        coordinates : tuple
            Current coordinates (x, y)
        """
        self.state.current_zone = zone
        self.state.current_planet = planet
        self.state.current_coordinates = coordinates
        
        # Record movement
        self._record_movement(coordinates[0], coordinates[1])
        
        self.logger.debug(f"[ENVIRONMENTAL_AWARENESS] Location updated: {zone} on {planet} at {coordinates}")
    
    def add_death_location(self, coordinates: Tuple[int, int]):
        """Add a death location to avoid.
        
        Parameters
        ----------
        coordinates : tuple
            Death location coordinates (x, y)
        """
        self.state.death_locations.append((coordinates[0], coordinates[1], datetime.now()))
        
        # Keep only recent death locations
        cutoff_time = datetime.now() - timedelta(days=1)
        self.state.death_locations = [
            death for death in self.state.death_locations
            if death[2] > cutoff_time
        ]
        
        self.logger.info(f"[ENVIRONMENTAL_AWARENESS] Death location recorded: {coordinates}")
    
    def get_current_risk_level(self) -> RiskLevel:
        """Get current risk level.
        
        Returns
        -------
        RiskLevel
            Current risk level
        """
        return self.state.risk_level
    
    def get_detected_threats(self) -> List[ThreatDetection]:
        """Get currently detected threats.
        
        Returns
        -------
        list
            List of detected threats
        """
        return self.state.detected_threats.copy()
    
    def get_risk_assessment(self) -> Dict[str, Any]:
        """Get comprehensive risk assessment.
        
        Returns
        -------
        dict
            Risk assessment summary
        """
        return {
            "current_risk_level": self.state.risk_level.value,
            "threats_detected": len(self.state.detected_threats),
            "current_zone": self.state.current_zone,
            "current_planet": self.state.current_planet,
            "last_scan_time": self.state.last_scan_time.isoformat() if self.state.last_scan_time else None,
            "threats": [asdict(threat) for threat in self.state.detected_threats],
            "movement_history_count": len(self.state.movement_history),
            "death_locations_count": len(self.state.death_locations)
        }
    
    def get_avoidance_recommendations(self) -> List[str]:
        """Get recommendations for avoiding current threats.
        
        Returns
        -------
        list
            List of avoidance recommendations
        """
        recommendations = []
        
        for threat in self.state.detected_threats:
            strategy = self.config["environmental_awareness"]["avoidance_strategies"].get(
                threat.threat_type.value, "move_to_safe_zone"
            )
            
            if strategy == "move_to_safe_zone":
                recommendations.append(f"Move to safe zone due to {threat.threat_type.value}")
            elif strategy == "change_zone":
                recommendations.append(f"Change zone due to {threat.threat_type.value}")
            elif strategy == "random_movement":
                recommendations.append(f"Perform random movement due to {threat.threat_type.value}")
            elif strategy == "reduce_activity":
                recommendations.append(f"Reduce activity due to {threat.threat_type.value}")
            elif strategy == "move_to_less_crowded":
                recommendations.append(f"Move to less crowded area due to {threat.threat_type.value}")
            elif strategy == "avoid_area":
                recommendations.append(f"Avoid area due to {threat.threat_type.value}")
        
        return recommendations
    
    def _get_session_duration(self) -> float:
        """Get session duration in seconds."""
        if not self.state.last_scan_time:
            return 0.0
        
        return (datetime.now() - self.state.last_scan_time).total_seconds()
    
    def _get_risk_level_distribution(self) -> Dict[str, int]:
        """Get distribution of risk levels encountered."""
        distribution = {level.value: 0 for level in RiskLevel}
        
        for threat in self.state.detected_threats:
            distribution[threat.risk_level.value] += 1
        
        return distribution
    
    def _get_zones_visited(self) -> List[str]:
        """Get list of zones visited during session."""
        zones = set()
        for move in self.state.movement_history:
            # This would need to be enhanced to track zone changes
            zones.add(self.state.current_zone)
        
        return list(zones)
    
    def _get_avoidance_actions(self) -> List[str]:
        """Get list of avoidance actions taken."""
        # This would track actual avoidance actions taken
        return ["move_to_safe_zone", "random_movement"]  # Placeholder


# Global instance for easy access
_environmental_awareness: Optional[EnvironmentalAwareness] = None


def get_environmental_awareness() -> EnvironmentalAwareness:
    """Get the global environmental awareness instance.
    
    Returns
    -------
    EnvironmentalAwareness
        Global environmental awareness instance
    """
    global _environmental_awareness
    
    if _environmental_awareness is None:
        _environmental_awareness = EnvironmentalAwareness()
    
    return _environmental_awareness


def start_environmental_monitoring(character_name: str) -> bool:
    """Start environmental monitoring for a character.
    
    Parameters
    ----------
    character_name : str
        Name of the character to monitor
        
    Returns
    -------
    bool
        True if monitoring started successfully
    """
    return get_environmental_awareness().start_monitoring(character_name)


def stop_environmental_monitoring() -> Optional[Dict]:
    """Stop environmental monitoring.
    
    Returns
    -------
    dict or None
        Summary of monitoring session
    """
    return get_environmental_awareness().stop_monitoring()


def update_location(zone: str, planet: str, coordinates: Tuple[int, int]):
    """Update current location information.
    
    Parameters
    ----------
    zone : str
        Current zone name
    planet : str
        Current planet name
    coordinates : tuple
        Current coordinates (x, y)
    """
    get_environmental_awareness().update_location(zone, planet, coordinates)


def get_risk_assessment() -> Dict[str, Any]:
    """Get current risk assessment.
    
    Returns
    -------
    dict
        Risk assessment summary
    """
    return get_environmental_awareness().get_risk_assessment()


def get_avoidance_recommendations() -> List[str]:
    """Get avoidance recommendations.
    
    Returns
    -------
    list
        List of avoidance recommendations
    """
    return get_environmental_awareness().get_avoidance_recommendations() 
"""
Combat Range Intelligence & Engagement Distance Logic

This module provides intelligent combat range management including:
- Optimal range detection based on profession and weapon
- Auto-detection of equipped weapon type
- Distance threshold management per fight
- Range checking and repositioning logic
- Minimap OCR for proximity gauging
- Debug overlay for visual range tracking
"""

import json
import logging
import time
import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

try:
    from core.ocr import OCREngine, extract_text_from_screen
    from core.screenshot import capture_screen
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class WeaponType(Enum):
    """Types of weapons available in the game."""
    RIFLE = "rifle"
    PISTOL = "pistol"
    CARBINE = "carbine"
    MELEE = "melee"
    HEAVY_WEAPON = "heavy_weapon"
    UNARMED = "unarmed"
    UNKNOWN = "unknown"


class ProfessionType(Enum):
    """Types of professions available in the game."""
    RIFLEMAN = "rifleman"
    PISTOLEER = "pistoleer"
    COMMANDO = "commando"
    BOUNTY_HUNTER = "bounty_hunter"
    SMUGGLER = "smuggler"
    BRAWLER = "brawler"
    FENCER = "fencer"
    TKA = "tka"
    UNKNOWN = "unknown"


class RangeStatus(Enum):
    """Status of range checking operations."""
    IDLE = "idle"
    CHECKING = "checking"
    REPOSITIONING = "repositioning"
    ENGAGING = "engaging"
    FAILED = "failed"


@dataclass
class WeaponInfo:
    """Information about a weapon's range capabilities."""
    name: str
    weapon_type: WeaponType
    optimal_range: int  # meters
    max_range: int      # meters
    min_range: int      # meters
    accuracy_falloff: float  # accuracy reduction per meter beyond optimal
    reload_time: float  # seconds
    damage_type: str
    equipped: bool = False
    ammo_count: int = 0
    max_ammo: int = 0


@dataclass
class ProfessionRange:
    """Range information for a profession."""
    profession: ProfessionType
    weapon_type: WeaponType
    optimal_range: int
    max_range: int
    min_range: int
    preferred_stance: str
    movement_speed: float
    range_bonus: int = 0
    accuracy_bonus: float = 0.0


@dataclass
class RangeCheckResult:
    """Result of range checking operation."""
    current_distance: float
    optimal_range: int
    range_status: str  # "too_close", "optimal", "too_far", "out_of_range"
    reposition_needed: bool
    suggested_action: str
    confidence: float


class CombatRangeIntelligence:
    """
    Combat range intelligence and engagement distance logic.
    
    Features:
    - Combat range matrix by profession and weapon
    - Auto-detection of equipped weapon type
    - Distance threshold management per fight
    - Range checking and repositioning logic
    - Minimap OCR for proximity gauging
    - Debug overlay for visual range tracking
    """
    
    def __init__(self, config_path: str = "data/profession_ranges.yaml"):
        """Initialize the combat range intelligence system."""
        self.logger = logging.getLogger(__name__)
        self.ocr_engine = OCREngine() if OCR_AVAILABLE else None
        self.current_status = RangeStatus.IDLE
        self.config_path = Path(config_path)
        
        # Combat range matrix
        self.combat_range_matrix: Dict[str, Dict[str, Any]] = {}
        self.current_profession: Optional[ProfessionType] = None
        self.current_weapon: Optional[WeaponInfo] = None
        self.current_target_distance: float = 0.0
        
        # Range checking history
        self.range_history: List[RangeCheckResult] = []
        self.last_range_check: float = 0.0
        
        # Debug overlay settings
        self.debug_overlay_enabled = False
        self.debug_overlay_region = (50, 50, 300, 200)
        
        # Load combat range configuration
        self._load_combat_range_config()
        
        # Minimap regions for distance detection
        self.minimap_regions = {
            "player_position": (400, 300, 450, 350),  # Approximate player position
            "target_position": (350, 250, 500, 400),  # Target area
            "distance_indicators": (350, 250, 500, 400)  # Distance indicators
        }
        
        # Weapon detection keywords
        self.weapon_keywords = {
            WeaponType.RIFLE: ["rifle", "blaster rifle", "e-11", "t-21"],
            WeaponType.PISTOL: ["pistol", "blaster pistol", "dl-44", "se-14"],
            WeaponType.CARBINE: ["carbine", "blaster carbine", "e-11 carbine"],
            WeaponType.MELEE: ["sword", "vibro", "knife", "dagger"],
            WeaponType.HEAVY_WEAPON: ["heavy", "rocket", "grenade", "mortar"],
            WeaponType.UNARMED: ["unarmed", "fists", "hands", "punch"]
        }
        
        # Profession detection keywords
        self.profession_keywords = {
            ProfessionType.RIFLEMAN: ["rifleman", "rifle", "marksman"],
            ProfessionType.PISTOLEER: ["pistoleer", "pistol", "gunslinger"],
            ProfessionType.COMMANDO: ["commando", "heavy", "specialist"],
            ProfessionType.BOUNTY_HUNTER: ["bounty hunter", "hunter", "tracker"],
            ProfessionType.SMUGGLER: ["smuggler", "rogue", "scoundrel"],
            ProfessionType.BRAWLER: ["brawler", "unarmed", "fighter"],
            ProfessionType.FENCER: ["fencer", "sword", "duelist"],
            ProfessionType.TKA: ["tka", "teras kasi", "martial artist"]
        }
    
    def _load_combat_range_config(self):
        """Load combat range configuration from file."""
        try:
            if self.config_path.exists():
                import yaml
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Load combat range matrix
                self.combat_range_matrix = config.get("combat_range_matrix", {})
                
                # Load default settings
                default_settings = config.get("default_settings", {})
                self.debug_overlay_enabled = default_settings.get("debug_overlay_enabled", False)
                
                self.logger.info(f"Loaded combat range configuration with {len(self.combat_range_matrix)} profession-weapon combinations")
            else:
                self._create_default_combat_range_config()
                
        except Exception as e:
            self.logger.error(f"Error loading combat range config: {e}")
            self._create_default_combat_range_config()
    
    def _create_default_combat_range_config(self):
        """Create default combat range configuration."""
        self.combat_range_matrix = {
            "rifleman_rifle": {
                "profession": "rifleman",
                "weapon_type": "rifle",
                "optimal_range": 64,
                "max_range": 100,
                "min_range": 10,
                "preferred_stance": "kneeling",
                "movement_speed": 1.0,
                "range_bonus": 5,
                "accuracy_bonus": 0.1
            },
            "rifleman_pistol": {
                "profession": "rifleman",
                "weapon_type": "pistol",
                "optimal_range": 32,
                "max_range": 50,
                "min_range": 5,
                "preferred_stance": "standing",
                "movement_speed": 1.2,
                "range_bonus": 0,
                "accuracy_bonus": 0.0
            },
            "pistoleer_pistol": {
                "profession": "pistoleer",
                "weapon_type": "pistol",
                "optimal_range": 32,
                "max_range": 60,
                "min_range": 3,
                "preferred_stance": "standing",
                "movement_speed": 1.5,
                "range_bonus": 3,
                "accuracy_bonus": 0.15
            },
            "commando_heavy": {
                "profession": "commando",
                "weapon_type": "heavy_weapon",
                "optimal_range": 80,
                "max_range": 150,
                "min_range": 20,
                "preferred_stance": "prone",
                "movement_speed": 0.8,
                "range_bonus": 10,
                "accuracy_bonus": 0.2
            },
            "brawler_unarmed": {
                "profession": "brawler",
                "weapon_type": "unarmed",
                "optimal_range": 2,
                "max_range": 3,
                "min_range": 1,
                "preferred_stance": "standing",
                "movement_speed": 1.8,
                "range_bonus": 0,
                "accuracy_bonus": 0.0
            },
            "fencer_melee": {
                "profession": "fencer",
                "weapon_type": "melee",
                "optimal_range": 3,
                "max_range": 5,
                "min_range": 1,
                "preferred_stance": "standing",
                "movement_speed": 1.6,
                "range_bonus": 0,
                "accuracy_bonus": 0.0
            }
        }
        
        self.logger.info("Created default combat range configuration")
    
    def detect_equipped_weapon(self) -> Optional[WeaponInfo]:
        """
        Auto-detect equipped weapon type using OCR.
        
        Returns
        -------
        Optional[WeaponInfo]
            Detected weapon information, or None if detection failed
        """
        if not OCR_AVAILABLE:
            return None
        
        try:
            screenshot = capture_screen()
            if screenshot is None:
                return None
            
            # Scan weapon slot regions
            weapon_regions = [
                (100, 100, 200, 150),   # Primary weapon slot
                (200, 100, 300, 150),   # Secondary weapon slot
                (300, 100, 400, 150),   # Tertiary weapon slot
            ]
            
            detected_weapon = None
            
            for region in weapon_regions:
                ocr_result = self.ocr_engine.extract_text_from_screen(screenshot, region)
                
                if ocr_result.confidence > 60:
                    text = ocr_result.text.lower()
                    
                    # Check for weapon keywords
                    for weapon_type, keywords in self.weapon_keywords.items():
                        for keyword in keywords:
                            if keyword in text:
                                # Create weapon info
                                weapon_info = WeaponInfo(
                                    name=text.strip(),
                                    weapon_type=weapon_type,
                                    optimal_range=self._get_optimal_range_for_weapon(weapon_type),
                                    max_range=self._get_max_range_for_weapon(weapon_type),
                                    min_range=self._get_min_range_for_weapon(weapon_type),
                                    accuracy_falloff=self._get_accuracy_falloff_for_weapon(weapon_type),
                                    reload_time=self._get_reload_time_for_weapon(weapon_type),
                                    damage_type=self._get_damage_type_for_weapon(weapon_type),
                                    equipped=True
                                )
                                
                                detected_weapon = weapon_info
                                self.logger.info(f"Detected weapon: {weapon_info.name} ({weapon_type.value})")
                                break
                        
                        if detected_weapon:
                            break
                    
                    if detected_weapon:
                        break
            
            return detected_weapon
            
        except Exception as e:
            self.logger.error(f"Error detecting equipped weapon: {e}")
            return None
    
    def detect_profession(self) -> Optional[ProfessionType]:
        """
        Detect current profession using OCR.
        
        Returns
        -------
        Optional[ProfessionType]
            Detected profession, or None if detection failed
        """
        if not OCR_AVAILABLE:
            return None
        
        try:
            screenshot = capture_screen()
            if screenshot is None:
                return None
            
            # Scan profession indicator regions
            profession_regions = [
                (50, 50, 200, 100),    # Character sheet area
                (400, 50, 550, 100),   # Status area
                (50, 400, 200, 450),   # Skill area
            ]
            
            detected_profession = None
            
            for region in profession_regions:
                ocr_result = self.ocr_engine.extract_text_from_screen(screenshot, region)
                
                if ocr_result.confidence > 50:
                    text = ocr_result.text.lower()
                    
                    # Check for profession keywords
                    for profession_type, keywords in self.profession_keywords.items():
                        for keyword in keywords:
                            if keyword in text:
                                detected_profession = profession_type
                                self.logger.info(f"Detected profession: {profession_type.value}")
                                break
                        
                        if detected_profession:
                            break
                    
                    if detected_profession:
                        break
            
            return detected_profession
            
        except Exception as e:
            self.logger.error(f"Error detecting profession: {e}")
            return None
    
    def check_combat_range(self, target_distance: float = None) -> RangeCheckResult:
        """
        Check if current distance is optimal for combat.
        
        Parameters
        ----------
        target_distance : float, optional
            Distance to target. If None, will attempt to detect from minimap.
            
        Returns
        -------
        RangeCheckResult
            Result of range checking operation
        """
        self.current_status = RangeStatus.CHECKING
        
        try:
            # Get current distance if not provided
            if target_distance is None:
                target_distance = self._detect_distance_from_minimap()
            
            self.current_target_distance = target_distance
            
            # Get optimal range for current setup
            optimal_range = self._get_optimal_range()
            max_range = self._get_max_range()
            min_range = self._get_min_range()
            
            # Determine range status
            if target_distance < min_range:
                range_status = "too_close"
                reposition_needed = True
                suggested_action = "move_back"
            elif target_distance < optimal_range * 0.8:
                range_status = "too_close"
                reposition_needed = True
                suggested_action = "move_back"
            elif target_distance <= optimal_range * 1.2:
                range_status = "optimal"
                reposition_needed = False
                suggested_action = "engage"
            elif target_distance <= max_range:
                range_status = "acceptable"
                reposition_needed = False
                suggested_action = "engage"
            else:
                range_status = "out_of_range"
                reposition_needed = True
                suggested_action = "move_forward"
            
            # Calculate confidence based on detection quality
            confidence = min(95.0, 70.0 + (target_distance > 0) * 25.0)
            
            result = RangeCheckResult(
                current_distance=target_distance,
                optimal_range=optimal_range,
                range_status=range_status,
                reposition_needed=reposition_needed,
                suggested_action=suggested_action,
                confidence=confidence
            )
            
            self.range_history.append(result)
            self.last_range_check = time.time()
            
            self.logger.info(f"Range check: {target_distance:.1f}m (optimal: {optimal_range}m, status: {range_status})")
            self.current_status = RangeStatus.IDLE
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error checking combat range: {e}")
            self.current_status = RangeStatus.FAILED
            
            return RangeCheckResult(
                current_distance=0.0,
                optimal_range=0,
                range_status="unknown",
                reposition_needed=False,
                suggested_action="unknown",
                confidence=0.0
            )
    
    def should_reposition(self, target_distance: float = None) -> bool:
        """
        Determine if repositioning is needed for optimal combat range.
        
        Parameters
        ----------
        target_distance : float, optional
            Distance to target. If None, will attempt to detect from minimap.
            
        Returns
        -------
        bool
            True if repositioning is needed
        """
        range_result = self.check_combat_range(target_distance)
        return range_result.reposition_needed
    
    def get_reposition_direction(self, target_distance: float = None) -> str:
        """
        Get the direction to reposition for optimal range.
        
        Parameters
        ----------
        target_distance : float, optional
            Distance to target. If None, will attempt to detect from minimap.
            
        Returns
        -------
        str
            Direction to move: "forward", "backward", or "none"
        """
        range_result = self.check_combat_range(target_distance)
        
        if range_result.suggested_action == "move_forward":
            return "forward"
        elif range_result.suggested_action == "move_back":
            return "backward"
        else:
            return "none"
    
    def _detect_distance_from_minimap(self) -> float:
        """Detect distance to target from minimap using OCR."""
        if not OCR_AVAILABLE:
            return 0.0
        
        try:
            screenshot = capture_screen()
            if screenshot is None:
                return 0.0
            
            # Scan minimap for distance indicators
            minimap_region = self.minimap_regions["distance_indicators"]
            ocr_result = self.ocr_engine.extract_text_from_screen(screenshot, minimap_region)
            
            if ocr_result.confidence > 50:
                text = ocr_result.text.lower()
                
                # Look for distance patterns
                import re
                distance_patterns = [
                    r"(\d+)m",
                    r"distance: (\d+)",
                    r"range: (\d+)",
                    r"(\d+) meters"
                ]
                
                for pattern in distance_patterns:
                    match = re.search(pattern, text)
                    if match:
                        distance = float(match.group(1))
                        return distance
            
            # Fallback: estimate distance based on minimap icon spacing
            estimated_distance = self._estimate_distance_from_icon_spacing()
            return estimated_distance
            
        except Exception as e:
            self.logger.error(f"Error detecting distance from minimap: {e}")
            return 0.0
    
    def _estimate_distance_from_icon_spacing(self) -> float:
        """Estimate distance based on minimap icon spacing."""
        # This is a simplified estimation
        # In a real implementation, this would analyze minimap icon positions
        return 50.0  # Default estimate
    
    def _get_optimal_range(self) -> int:
        """Get optimal range for current profession and weapon combination."""
        if not self.current_profession or not self.current_weapon:
            return 32  # Default pistol range
        
        # Look up in combat range matrix
        key = f"{self.current_profession.value}_{self.current_weapon.weapon_type.value}"
        
        if key in self.combat_range_matrix:
            return self.combat_range_matrix[key]["optimal_range"]
        
        # Fallback to weapon default
        return self.current_weapon.optimal_range
    
    def _get_max_range(self) -> int:
        """Get maximum range for current profession and weapon combination."""
        if not self.current_profession or not self.current_weapon:
            return 50  # Default pistol max range
        
        # Look up in combat range matrix
        key = f"{self.current_profession.value}_{self.current_weapon.weapon_type.value}"
        
        if key in self.combat_range_matrix:
            return self.combat_range_matrix[key]["max_range"]
        
        # Fallback to weapon default
        return self.current_weapon.max_range
    
    def _get_min_range(self) -> int:
        """Get minimum range for current profession and weapon combination."""
        if not self.current_profession or not self.current_weapon:
            return 5  # Default pistol min range
        
        # Look up in combat range matrix
        key = f"{self.current_profession.value}_{self.current_weapon.weapon_type.value}"
        
        if key in self.combat_range_matrix:
            return self.combat_range_matrix[key]["min_range"]
        
        # Fallback to weapon default
        return self.current_weapon.min_range
    
    def _get_optimal_range_for_weapon(self, weapon_type: WeaponType) -> int:
        """Get optimal range for a weapon type."""
        ranges = {
            WeaponType.RIFLE: 64,
            WeaponType.PISTOL: 32,
            WeaponType.CARBINE: 48,
            WeaponType.MELEE: 3,
            WeaponType.HEAVY_WEAPON: 80,
            WeaponType.UNARMED: 2
        }
        return ranges.get(weapon_type, 32)
    
    def _get_max_range_for_weapon(self, weapon_type: WeaponType) -> int:
        """Get maximum range for a weapon type."""
        ranges = {
            WeaponType.RIFLE: 100,
            WeaponType.PISTOL: 50,
            WeaponType.CARBINE: 75,
            WeaponType.MELEE: 5,
            WeaponType.HEAVY_WEAPON: 150,
            WeaponType.UNARMED: 3
        }
        return ranges.get(weapon_type, 50)
    
    def _get_min_range_for_weapon(self, weapon_type: WeaponType) -> int:
        """Get minimum range for a weapon type."""
        ranges = {
            WeaponType.RIFLE: 10,
            WeaponType.PISTOL: 5,
            WeaponType.CARBINE: 8,
            WeaponType.MELEE: 1,
            WeaponType.HEAVY_WEAPON: 20,
            WeaponType.UNARMED: 1
        }
        return ranges.get(weapon_type, 5)
    
    def _get_accuracy_falloff_for_weapon(self, weapon_type: WeaponType) -> float:
        """Get accuracy falloff per meter for a weapon type."""
        falloffs = {
            WeaponType.RIFLE: 0.02,
            WeaponType.PISTOL: 0.05,
            WeaponType.CARBINE: 0.03,
            WeaponType.MELEE: 0.0,
            WeaponType.HEAVY_WEAPON: 0.01,
            WeaponType.UNARMED: 0.0
        }
        return falloffs.get(weapon_type, 0.03)
    
    def _get_reload_time_for_weapon(self, weapon_type: WeaponType) -> float:
        """Get reload time for a weapon type."""
        reload_times = {
            WeaponType.RIFLE: 2.0,
            WeaponType.PISTOL: 1.5,
            WeaponType.CARBINE: 1.8,
            WeaponType.MELEE: 0.0,
            WeaponType.HEAVY_WEAPON: 3.0,
            WeaponType.UNARMED: 0.0
        }
        return reload_times.get(weapon_type, 2.0)
    
    def _get_damage_type_for_weapon(self, weapon_type: WeaponType) -> str:
        """Get damage type for a weapon type."""
        damage_types = {
            WeaponType.RIFLE: "energy",
            WeaponType.PISTOL: "energy",
            WeaponType.CARBINE: "energy",
            WeaponType.MELEE: "kinetic",
            WeaponType.HEAVY_WEAPON: "explosive",
            WeaponType.UNARMED: "kinetic"
        }
        return damage_types.get(weapon_type, "energy")
    
    def update_current_setup(self, profession: ProfessionType = None, weapon: WeaponInfo = None):
        """
        Update current profession and weapon setup.
        
        Parameters
        ----------
        profession : ProfessionType, optional
            Current profession
        weapon : WeaponInfo, optional
            Current equipped weapon
        """
        if profession:
            self.current_profession = profession
        
        if weapon:
            self.current_weapon = weapon
        
        self.logger.info(f"Updated setup: {self.current_profession.value if self.current_profession else 'Unknown'} with {self.current_weapon.name if self.current_weapon else 'Unknown'} weapon")
    
    def get_combat_range_status(self) -> Dict[str, Any]:
        """Get current combat range status and information."""
        return {
            "current_status": self.current_status.value,
            "current_profession": self.current_profession.value if self.current_profession else "unknown",
            "current_weapon": self.current_weapon.name if self.current_weapon else "unknown",
            "current_target_distance": self.current_target_distance,
            "optimal_range": self._get_optimal_range(),
            "max_range": self._get_max_range(),
            "min_range": self._get_min_range(),
            "debug_overlay_enabled": self.debug_overlay_enabled,
            "range_history_count": len(self.range_history),
            "last_range_check": self.last_range_check
        }
    
    def enable_debug_overlay(self, enabled: bool = True):
        """Enable or disable debug overlay for visual range tracking."""
        self.debug_overlay_enabled = enabled
        self.logger.info(f"Debug overlay {'enabled' if enabled else 'disabled'}")
    
    def save_combat_range_config(self):
        """Save combat range configuration to file."""
        try:
            config = {
                "combat_range_matrix": self.combat_range_matrix,
                "default_settings": {
                    "debug_overlay_enabled": self.debug_overlay_enabled
                }
            }
            
            import yaml
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, indent=2)
            
            self.logger.info("Combat range configuration saved")
            
        except Exception as e:
            self.logger.error(f"Error saving combat range config: {e}")


# Global combat range intelligence instance
_combat_range_intelligence: Optional[CombatRangeIntelligence] = None


def get_combat_range_intelligence() -> CombatRangeIntelligence:
    """Get the global combat range intelligence instance."""
    global _combat_range_intelligence
    if _combat_range_intelligence is None:
        _combat_range_intelligence = CombatRangeIntelligence()
    return _combat_range_intelligence


def detect_equipped_weapon() -> Optional[WeaponInfo]:
    """Auto-detect equipped weapon type."""
    intelligence = get_combat_range_intelligence()
    return intelligence.detect_equipped_weapon()


def detect_profession() -> Optional[ProfessionType]:
    """Detect current profession."""
    intelligence = get_combat_range_intelligence()
    return intelligence.detect_profession()


def check_combat_range(target_distance: float = None) -> RangeCheckResult:
    """Check if current distance is optimal for combat."""
    intelligence = get_combat_range_intelligence()
    return intelligence.check_combat_range(target_distance)


def should_reposition(target_distance: float = None) -> bool:
    """Determine if repositioning is needed for optimal combat range."""
    intelligence = get_combat_range_intelligence()
    return intelligence.should_reposition(target_distance)


def get_reposition_direction(target_distance: float = None) -> str:
    """Get the direction to reposition for optimal range."""
    intelligence = get_combat_range_intelligence()
    return intelligence.get_reposition_direction(target_distance)


def get_combat_range_status() -> Dict[str, Any]:
    """Get current combat range status and information."""
    intelligence = get_combat_range_intelligence()
    return intelligence.get_combat_range_status() 
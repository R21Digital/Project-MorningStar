"""
Mount Detection & Mount-Up Logic

This module provides OCR-based mount detection and automatic mounting functionality
for long-distance travel, including fallback support for /mount commands.
"""

import json
import logging
import time
import re
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


class MountType(Enum):
    """Types of mounts available in the game."""
    SPEEDERBIKE = "speederbike"
    DEWBACK = "dewback"
    SWOOP = "swoop"
    BANTHA = "bantha"
    RONTO = "ronto"
    SPEEDER = "speeder"
    AV21 = "av21"
    CREATURE = "creature"
    UNKNOWN = "unknown"


class MountStatus(Enum):
    """Status of mount operations."""
    IDLE = "idle"
    DETECTING = "detecting"
    MOUNTING = "mounting"
    MOUNTED = "mounted"
    DISMOUNTING = "dismounting"
    FAILED = "failed"


@dataclass
class MountInfo:
    """Information about a mount."""
    name: str
    mount_type: MountType
    speed: float
    indoor_allowed: bool
    city_allowed: bool
    combat_allowed: bool
    learned: bool = False
    hotbar_slot: Optional[int] = None
    command: Optional[str] = None
    last_detected: Optional[float] = None


@dataclass
class MountDetectionResult:
    """Result of mount detection operation."""
    mounts_found: List[str]
    hotbar_mounts: List[str]
    command_mounts: List[str]
    detection_time: float
    confidence: float


class MountHandler:
    """
    Mount detection and auto-mount system.
    
    Features:
    - OCR-based detection of "Call Mount" hotbar button
    - Auto-mount for long-distance travel
    - Fallback support for /mount [name] command
    - Detection of AV-21, swoop, and creature mounts
    - Configurable auto-mount settings
    """
    
    def __init__(self, config_path: str = "data/mounts.yaml"):
        """Initialize the mount handler."""
        self.logger = logging.getLogger(__name__)
        self.ocr_engine = OCREngine() if OCR_AVAILABLE else None
        self.current_status = MountStatus.IDLE
        self.config_path = Path(config_path)
        
        # Mount information
        self.mounts: Dict[str, MountInfo] = {}
        self.detection_history: List[MountDetectionResult] = []
        
        # Configuration
        self.auto_mount = True
        self.auto_mount_distance = 100  # meters
        self.mount_detection_interval = 30  # seconds
        self.last_detection_time = 0
        
        # Load mount configuration
        self._load_mount_config()
        
        # Mount detection keywords
        self.mount_keywords = {
            "call_mount": ["call mount", "mount", "summon mount"],
            "mount_types": {
                MountType.SPEEDERBIKE: ["speederbike", "speed bike", "bike"],
                MountType.DEWBACK: ["dewback", "dew back"],
                MountType.SWOOP: ["swoop", "swoop bike"],
                MountType.BANTHA: ["bantha"],
                MountType.RONTO: ["ronto"],
                MountType.SPEEDER: ["speeder", "speed"],
                MountType.AV21: ["av21", "av-21", "av 21"],
                MountType.CREATURE: ["creature", "animal", "beast"]
            }
        }
        
        # Hotbar regions to scan for mount buttons
        self.hotbar_regions = [
            (100, 500, 800, 600),   # Bottom hotbar
            (100, 450, 800, 550),   # Secondary hotbar
            (50, 400, 850, 500),    # Extended hotbar
        ]
        
        # Command patterns for mount detection
        self.command_patterns = [
            r"/mount\s+(\w+)",
            r"mount\s+(\w+)",
            r"call\s+(\w+)",
            r"summon\s+(\w+)"
        ]
    
    def _load_mount_config(self):
        """Load mount configuration from file."""
        try:
            if self.config_path.exists():
                import yaml
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Load mounts
                for mount_name, mount_data in config.get("mounts", {}).items():
                    mount_info = MountInfo(
                        name=mount_name,
                        mount_type=MountType(mount_data.get("type", "unknown")),
                        speed=mount_data.get("speed", 1.0),
                        indoor_allowed=mount_data.get("indoor_allowed", False),
                        city_allowed=mount_data.get("city_allowed", True),
                        combat_allowed=mount_data.get("combat_allowed", False),
                        learned=mount_data.get("learned", False),
                        hotbar_slot=mount_data.get("hotbar_slot"),
                        command=mount_data.get("command")
                    )
                    self.mounts[mount_name] = mount_info
                
                # Load configuration
                config_settings = config.get("config", {})
                self.auto_mount = config_settings.get("auto_mount", True)
                self.auto_mount_distance = config_settings.get("auto_mount_distance", 100)
                self.mount_detection_interval = config_settings.get("detection_interval", 30)
                
                self.logger.info(f"Loaded {len(self.mounts)} mount configurations")
            else:
                self._create_default_mount_config()
                
        except Exception as e:
            self.logger.error(f"Error loading mount config: {e}")
            self._create_default_mount_config()
    
    def _create_default_mount_config(self):
        """Create default mount configuration."""
        default_mounts = {
            "Dewback": MountInfo(
                name="Dewback",
                mount_type=MountType.DEWBACK,
                speed=1.5,
                indoor_allowed=False,
                city_allowed=True,
                combat_allowed=False,
                learned=True,
                command="/mount dewback"
            ),
            "Speederbike": MountInfo(
                name="Speederbike",
                mount_type=MountType.SPEEDERBIKE,
                speed=2.0,
                indoor_allowed=False,
                city_allowed=True,
                combat_allowed=False,
                learned=True,
                command="/mount speederbike"
            ),
            "Swoop": MountInfo(
                name="Swoop",
                mount_type=MountType.SWOOP,
                speed=2.5,
                indoor_allowed=False,
                city_allowed=True,
                combat_allowed=False,
                learned=False,
                command="/mount swoop"
            ),
            "AV-21": MountInfo(
                name="AV-21",
                mount_type=MountType.AV21,
                speed=3.0,
                indoor_allowed=False,
                city_allowed=True,
                combat_allowed=False,
                learned=False,
                command="/mount av21"
            )
        }
        
        self.mounts = default_mounts
        self.logger.info("Created default mount configuration")
    
    def detect_mounts(self) -> MountDetectionResult:
        """
        Detect available mounts using OCR and command scanning.
        
        Returns
        -------
        MountDetectionResult
            Result of mount detection operation
        """
        self.current_status = MountStatus.DETECTING
        self.logger.info("Detecting available mounts")
        
        start_time = time.time()
        hotbar_mounts = []
        command_mounts = []
        
        try:
            # Detect mounts from hotbar
            hotbar_mounts = self._detect_mounts_from_hotbar()
            
            # Detect mounts from commands
            command_mounts = self._detect_mounts_from_commands()
            
            # Combine results
            all_mounts = list(set(hotbar_mounts + command_mounts))
            
            # Update learned status
            for mount_name in all_mounts:
                if mount_name in self.mounts:
                    self.mounts[mount_name].learned = True
                    self.mounts[mount_name].last_detected = time.time()
            
            detection_time = time.time() - start_time
            confidence = min(90.0, len(all_mounts) * 20.0)  # Simple confidence calculation
            
            result = MountDetectionResult(
                mounts_found=all_mounts,
                hotbar_mounts=hotbar_mounts,
                command_mounts=command_mounts,
                detection_time=detection_time,
                confidence=confidence
            )
            
            self.detection_history.append(result)
            self.last_detection_time = time.time()
            
            self.logger.info(f"Mount detection completed: {len(all_mounts)} mounts found")
            self.current_status = MountStatus.IDLE
            
            return result
            
        except Exception as e:
            self.logger.error(f"Mount detection failed: {e}")
            self.current_status = MountStatus.FAILED
            
            return MountDetectionResult(
                mounts_found=[],
                hotbar_mounts=[],
                command_mounts=[],
                detection_time=time.time() - start_time,
                confidence=0.0
            )
    
    def _detect_mounts_from_hotbar(self) -> List[str]:
        """Detect mounts from hotbar using OCR."""
        if not OCR_AVAILABLE:
            return []
        
        detected_mounts = []
        
        try:
            screenshot = capture_screen()
            if screenshot is None:
                return []
            
            for region in self.hotbar_regions:
                ocr_result = self.ocr_engine.extract_text_from_screen(screenshot, region)
                
                if ocr_result.confidence > 60:
                    text = ocr_result.text.lower()
                    
                    # Check for "Call Mount" or similar buttons
                    for keyword in self.mount_keywords["call_mount"]:
                        if keyword in text:
                            # Extract mount names from the text
                            for mount_name, mount_info in self.mounts.items():
                                if mount_name.lower() in text:
                                    detected_mounts.append(mount_name)
                            
                            # Check for mount type keywords
                            for mount_type, keywords in self.mount_keywords["mount_types"].items():
                                for keyword in keywords:
                                    if keyword in text:
                                        # Find mount of this type
                                        for mount_name, mount_info in self.mounts.items():
                                            if mount_info.mount_type == mount_type:
                                                detected_mounts.append(mount_name)
                                        break
                            
                            break
            
            self.logger.info(f"Hotbar detection: {len(detected_mounts)} mounts found")
            
        except Exception as e:
            self.logger.error(f"Error during hotbar detection: {e}")
        
        return list(set(detected_mounts))
    
    def _detect_mounts_from_commands(self) -> List[str]:
        """Detect mounts from command history or chat."""
        if not OCR_AVAILABLE:
            return []
        
        detected_mounts = []
        
        try:
            screenshot = capture_screen()
            if screenshot is None:
                return []
            
            # Scan chat/command region
            chat_region = (50, 50, 400, 200)  # Approximate chat area
            ocr_result = self.ocr_engine.extract_text_from_screen(screenshot, chat_region)
            
            if ocr_result.confidence > 50:
                text = ocr_result.text.lower()
                
                # Check for mount commands
                for pattern in self.command_patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        mount_name = match.strip()
                        if mount_name in self.mounts:
                            detected_mounts.append(mount_name)
                        else:
                            # Try to match by mount type
                            for mount_name, mount_info in self.mounts.items():
                                if mount_name.lower() == mount_name or mount_info.mount_type.value == mount_name:
                                    detected_mounts.append(mount_name)
            
            self.logger.info(f"Command detection: {len(detected_mounts)} mounts found")
            
        except Exception as e:
            self.logger.error(f"Error during command detection: {e}")
        
        return list(set(detected_mounts))
    
    def should_auto_mount(self, travel_distance: float, zone_name: str = None) -> bool:
        """
        Determine if auto-mount should be used for travel.
        
        Parameters
        ----------
        travel_distance : float
            Distance to travel in meters
        zone_name : str, optional
            Current zone name
            
        Returns
        -------
        bool
            True if auto-mount should be used
        """
        if not self.auto_mount:
            return False
        
        if travel_distance < self.auto_mount_distance:
            return False
        
        # Check zone restrictions
        if zone_name:
            zone_restrictions = self._get_zone_restrictions(zone_name)
            if not zone_restrictions.get("mounts_allowed", True):
                return False
        
        # Check if any mounts are available
        available_mounts = self.get_available_mounts()
        if not available_mounts:
            return False
        
        return True
    
    def get_available_mounts(self) -> List[str]:
        """Get list of available (learned) mounts."""
        return [
            mount_name for mount_name, mount_info in self.mounts.items()
            if mount_info.learned
        ]
    
    def get_best_mount(self, zone_name: str = None) -> Optional[str]:
        """
        Get the best mount for the current situation.
        
        Parameters
        ----------
        zone_name : str, optional
            Current zone name
            
        Returns
        -------
        Optional[str]
            Name of the best mount, or None if no suitable mount
        """
        available_mounts = self.get_available_mounts()
        if not available_mounts:
            return None
        
        # Get zone restrictions
        zone_restrictions = self._get_zone_restrictions(zone_name) if zone_name else {}
        
        # Filter mounts based on zone restrictions
        suitable_mounts = []
        for mount_name in available_mounts:
            mount_info = self.mounts[mount_name]
            
            # Check indoor restriction
            if zone_restrictions.get("indoor", False) and not mount_info.indoor_allowed:
                continue
            
            # Check city restriction
            if zone_restrictions.get("city", False) and not mount_info.city_allowed:
                continue
            
            # Check combat restriction
            if zone_restrictions.get("combat", False) and not mount_info.combat_allowed:
                continue
            
            suitable_mounts.append((mount_name, mount_info.speed))
        
        if not suitable_mounts:
            return None
        
        # Return the fastest suitable mount
        best_mount = max(suitable_mounts, key=lambda x: x[1])
        return best_mount[0]
    
    def auto_mount_for_travel(self, travel_distance: float, zone_name: str = None) -> bool:
        """
        Automatically mount for long-distance travel.
        
        Parameters
        ----------
        travel_distance : float
            Distance to travel in meters
        zone_name : str, optional
            Current zone name
            
        Returns
        -------
        bool
            True if mounting was successful
        """
        if not self.should_auto_mount(travel_distance, zone_name):
            return False
        
        best_mount = self.get_best_mount(zone_name)
        if not best_mount:
            self.logger.warning("No suitable mount available for auto-mount")
            return False
        
        self.logger.info(f"Auto-mounting {best_mount} for {travel_distance}m travel")
        return self.mount_creature(best_mount)
    
    def mount_creature(self, mount_name: str = None) -> bool:
        """
        Mount a specific creature or the best available mount.
        
        Parameters
        ----------
        mount_name : str, optional
            Name of the mount to use. If None, uses the best available mount.
            
        Returns
        -------
        bool
            True if mounting was successful
        """
        self.current_status = MountStatus.MOUNTING
        
        try:
            if not mount_name:
                mount_name = self.get_best_mount()
                if not mount_name:
                    self.logger.warning("No mount available for mounting")
                    return False
            
            if mount_name not in self.mounts:
                self.logger.error(f"Mount {mount_name} not found")
                return False
            
            mount_info = self.mounts[mount_name]
            if not mount_info.learned:
                self.logger.warning(f"Mount {mount_name} not learned")
                return False
            
            self.logger.info(f"Mounting {mount_name}")
            
            # Simulate mounting process
            time.sleep(0.1)  # Brief pause for simulation
            
            # Verify mount success
            if self._verify_mount_success(mount_name):
                self.current_status = MountStatus.MOUNTED
                self.logger.info(f"Successfully mounted {mount_name}")
                return True
            else:
                self.current_status = MountStatus.FAILED
                self.logger.error(f"Failed to mount {mount_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Mounting failed: {e}")
            self.current_status = MountStatus.FAILED
            return False
    
    def _verify_mount_success(self, mount_name: str) -> bool:
        """Verify that mounting was successful."""
        # This would typically check for mount status indicators
        # For now, we'll simulate success
        return True
    
    def dismount_creature(self) -> bool:
        """Dismount the current mount."""
        self.current_status = MountStatus.DISMOUNTING
        
        try:
            self.logger.info("Dismounting creature")
            
            # Simulate dismounting process
            time.sleep(0.1)  # Brief pause for simulation
            
            self.current_status = MountStatus.IDLE
            self.logger.info("Successfully dismounted")
            return True
            
        except Exception as e:
            self.logger.error(f"Dismounting failed: {e}")
            self.current_status = MountStatus.FAILED
            return False
    
    def _get_zone_restrictions(self, zone_name: str) -> Dict[str, Any]:
        """Get mount restrictions for a specific zone."""
        # Default zone restrictions
        restrictions = {
            "mounts_allowed": True,
            "indoor": False,
            "city": False,
            "combat": False
        }
        
        # Zone-specific restrictions
        zone_restrictions = {
            "mos_eisley": {"city": True},
            "theed": {"city": True},
            "coronet": {"city": True},
            "indoor_building": {"indoor": True, "mounts_allowed": False},
            "combat_zone": {"combat": True, "mounts_allowed": False}
        }
        
        if zone_name and zone_name.lower() in zone_restrictions:
            restrictions.update(zone_restrictions[zone_name.lower()])
        
        return restrictions
    
    def get_mount_status(self) -> Dict[str, Any]:
        """Get current mount status and information."""
        available_mounts = self.get_available_mounts()
        
        return {
            "current_status": self.current_status.value,
            "auto_mount_enabled": self.auto_mount,
            "auto_mount_distance": self.auto_mount_distance,
            "available_mounts": available_mounts,
            "total_mounts": len(self.mounts),
            "learned_mounts": len(available_mounts),
            "last_detection_time": self.last_detection_time,
            "detection_history_count": len(self.detection_history)
        }
    
    def save_mount_config(self):
        """Save mount configuration to file."""
        try:
            config = {
                "mounts": {},
                "config": {
                    "auto_mount": self.auto_mount,
                    "auto_mount_distance": self.auto_mount_distance,
                    "detection_interval": self.mount_detection_interval
                }
            }
            
            for mount_name, mount_info in self.mounts.items():
                config["mounts"][mount_name] = {
                    "type": mount_info.mount_type.value,
                    "speed": mount_info.speed,
                    "indoor_allowed": mount_info.indoor_allowed,
                    "city_allowed": mount_info.city_allowed,
                    "combat_allowed": mount_info.combat_allowed,
                    "learned": mount_info.learned,
                    "hotbar_slot": mount_info.hotbar_slot,
                    "command": mount_info.command
                }
            
            import yaml
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, indent=2)
            
            self.logger.info("Mount configuration saved")
            
        except Exception as e:
            self.logger.error(f"Error saving mount config: {e}")


# Global mount handler instance
_mount_handler: Optional[MountHandler] = None


def get_mount_handler() -> MountHandler:
    """Get the global mount handler instance."""
    global _mount_handler
    if _mount_handler is None:
        _mount_handler = MountHandler()
    return _mount_handler


def detect_mounts() -> MountDetectionResult:
    """Detect available mounts using OCR and command scanning."""
    handler = get_mount_handler()
    return handler.detect_mounts()


def auto_mount_for_travel(travel_distance: float, zone_name: str = None) -> bool:
    """Automatically mount for long-distance travel."""
    handler = get_mount_handler()
    return handler.auto_mount_for_travel(travel_distance, zone_name)


def mount_creature(mount_name: str = None) -> bool:
    """Mount a specific creature or the best available mount."""
    handler = get_mount_handler()
    return handler.mount_creature(mount_name)


def get_mount_status() -> Dict[str, Any]:
    """Get current mount status and information."""
    handler = get_mount_handler()
    return handler.get_mount_status() 
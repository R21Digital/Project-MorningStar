"""Crafting Manager for Batch 063 - Smart Crafting Integration.

This module provides:
- Crafting mode toggle and session management
- Crafting station detection and interaction
- Integration with schematic looper and validator
- Profession training coordination
"""

import logging
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

from core.ocr import OCREngine
from core.screenshot import capture_screen
from core.state_tracker import update_state, get_state
from .schematic_looper import SchematicLooper
from .crafting_validator import CraftingValidator
from .profession_trainer import ProfessionTrainer


@dataclass
class CraftingStation:
    """Represents a crafting station."""
    name: str
    station_type: str  # "artisan", "chef", "structures"
    location: str
    coords: Tuple[int, int]
    ui_elements: List[str]
    hotbar_slot: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "station_type": self.station_type,
            "location": self.location,
            "coords": self.coords,
            "ui_elements": self.ui_elements,
            "hotbar_slot": self.hotbar_slot
        }


@dataclass
class CraftingSession:
    """Represents an active crafting session."""
    station: CraftingStation
    profile_name: str
    start_time: float
    is_active: bool = True
    items_crafted: int = 0
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "station": self.station.to_dict(),
            "profile_name": self.profile_name,
            "start_time": self.start_time,
            "is_active": self.is_active,
            "items_crafted": self.items_crafted,
            "session_id": self.session_id
        }


class CraftingManager:
    """Main crafting manager for smart crafting integration."""
    
    def __init__(self, config_path: str = "config/crafting_config.json"):
        """Initialize the crafting manager.
        
        Parameters
        ----------
        config_path : str
            Path to crafting configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.ocr_engine = OCREngine()
        self.schematic_looper = SchematicLooper()
        self.validator = CraftingValidator()
        self.trainer = ProfessionTrainer()
        self.active_session: Optional[CraftingSession] = None
        self.logger = logging.getLogger(__name__)
        
        # Known crafting stations
        self.known_stations = {
            "artisan": ["Artisan Workbench", "Crafting Station", "Artisan Terminal"],
            "chef": ["Kitchen Station", "Cooking Terminal", "Chef Workbench"],
            "structures": ["Structure Terminal", "Building Station", "Architect Terminal"]
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load crafting configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Crafting config not found: {self.config_path}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default crafting configuration."""
        return {
            "crafting_mode": {
                "enabled": False,
                "auto_detect_stations": True,
                "preferred_station_types": ["artisan", "chef", "structures"],
                "max_crafting_time": 3600,  # 1 hour
                "break_interval": 300  # 5 minutes
            },
            "profiles": {
                "default": {
                    "station_type": "artisan",
                    "schematics": ["Basic Tool", "Survey Device"],
                    "max_quantity": 10,
                    "resource_check": True,
                    "power_check": True
                }
            },
            "validation": {
                "min_inventory_space": 5,
                "min_power": 100,
                "required_resources": ["metal", "chemical", "fiber"]
            }
        }
    
    def toggle_crafting_mode(self, enabled: bool = None) -> bool:
        """Toggle crafting mode on/off.
        
        Parameters
        ----------
        enabled : bool, optional
            Force specific state, otherwise toggles current state
            
        Returns
        -------
        bool
            New crafting mode state
        """
        current_state = self.config["crafting_mode"]["enabled"]
        new_state = enabled if enabled is not None else not current_state
        
        self.config["crafting_mode"]["enabled"] = new_state
        self._save_config()
        
        self.logger.info(f"Crafting mode {'enabled' if new_state else 'disabled'}")
        update_state("crafting_mode", new_state)
        
        return new_state
    
    def detect_crafting_stations(self) -> List[CraftingStation]:
        """Detect available crafting stations using OCR.
        
        Returns
        -------
        List[CraftingStation]
            List of detected crafting stations
        """
        screen = capture_screen()
        text_results = self.ocr_engine.scan_text(screen)
        
        detected_stations = []
        
        for result in text_results:
            text = result.text.lower()
            
            for station_type, keywords in self.known_stations.items():
                for keyword in keywords:
                    if keyword.lower() in text:
                        station = CraftingStation(
                            name=result.text,
                            station_type=station_type,
                            location=get_state("current_location", "Unknown"),
                            coords=(result.x, result.y),
                            ui_elements=["craft", "create", "build"],
                            hotbar_slot=self._find_hotbar_slot(result.text)
                        )
                        detected_stations.append(station)
                        break
        
        self.logger.info(f"Detected {len(detected_stations)} crafting stations")
        return detected_stations
    
    def _find_hotbar_slot(self, station_name: str) -> Optional[int]:
        """Find hotbar slot for crafting station.
        
        Parameters
        ----------
        station_name : str
            Name of the crafting station
            
        Returns
        -------
        Optional[int]
            Hotbar slot number or None if not found
        """
        # This would integrate with keybind manager
        # For now, return None
        return None
    
    def start_crafting_session(self, profile_name: str = "default", 
                             station_type: str = None) -> bool:
        """Start a new crafting session.
        
        Parameters
        ----------
        profile_name : str
            Name of crafting profile to use
        station_type : str, optional
            Specific station type to use
            
        Returns
        -------
        bool
            True if session started successfully
        """
        if not self.config["crafting_mode"]["enabled"]:
            self.logger.warning("Crafting mode is disabled")
            return False
        
        # Validate profile exists
        if profile_name not in self.config["profiles"]:
            self.logger.error(f"Crafting profile not found: {profile_name}")
            return False
        
        profile = self.config["profiles"][profile_name]
        
        # Detect available stations
        stations = self.detect_crafting_stations()
        if not stations:
            self.logger.warning("No crafting stations detected")
            return False
        
        # Filter by station type if specified
        if station_type:
            stations = [s for s in stations if s.station_type == station_type]
            if not stations:
                self.logger.warning(f"No {station_type} stations found")
                return False
        
        # Select best station
        selected_station = stations[0]  # Could implement priority logic
        
        # Validate resources and power
        if not self.validator.validate_crafting_requirements(profile):
            self.logger.error("Crafting requirements not met")
            return False
        
        # Start session
        self.active_session = CraftingSession(
            station=selected_station,
            profile_name=profile_name,
            start_time=time.time(),
            session_id=f"craft_{int(time.time())}"
        )
        
        self.logger.info(f"Started crafting session: {profile_name} at {selected_station.name}")
        update_state("active_crafting_session", self.active_session.to_dict())
        
        return True
    
    def run_crafting_loop(self) -> Dict[str, Any]:
        """Run the main crafting loop.
        
        Returns
        -------
        Dict[str, Any]
            Results of crafting session
        """
        if not self.active_session:
            self.logger.error("No active crafting session")
            return {"success": False, "error": "No active session"}
        
        profile = self.config["profiles"][self.active_session.profile_name]
        results = {
            "session_id": self.active_session.session_id,
            "profile_name": self.active_session.profile_name,
            "station": self.active_session.station.name,
            "items_crafted": 0,
            "schematics_completed": [],
            "errors": []
        }
        
        try:
            # Run schematic loop
            loop_results = self.schematic_looper.run_schematic_loop(
                profile["schematics"],
                max_quantity=profile.get("max_quantity", 10)
            )
            
            results["items_crafted"] = loop_results["items_crafted"]
            results["schematics_completed"] = loop_results["schematics_completed"]
            
            # Update session
            self.active_session.items_crafted += results["items_crafted"]
            
        except Exception as e:
            self.logger.error(f"Crafting loop error: {e}")
            results["errors"].append(str(e))
        
        return results
    
    def stop_crafting_session(self) -> Dict[str, Any]:
        """Stop the active crafting session.
        
        Returns
        -------
        Dict[str, Any]
            Session summary
        """
        if not self.active_session:
            return {"success": False, "error": "No active session"}
        
        session_duration = time.time() - self.active_session.start_time
        summary = {
            "session_id": self.active_session.session_id,
            "profile_name": self.active_session.profile_name,
            "station": self.active_session.station.name,
            "duration_seconds": session_duration,
            "items_crafted": self.active_session.items_crafted,
            "success": True
        }
        
        self.active_session.is_active = False
        self.active_session = None
        
        self.logger.info(f"Stopped crafting session: {summary['items_crafted']} items crafted")
        update_state("active_crafting_session", None)
        
        return summary
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def get_crafting_status(self) -> Dict[str, Any]:
        """Get current crafting status.
        
        Returns
        -------
        Dict[str, Any]
            Current crafting status
        """
        return {
            "mode_enabled": self.config["crafting_mode"]["enabled"],
            "active_session": self.active_session.to_dict() if self.active_session else None,
            "available_profiles": list(self.config["profiles"].keys()),
            "known_stations": self.known_stations
        }


def get_crafting_manager() -> CraftingManager:
    """Get singleton crafting manager instance."""
    if not hasattr(get_crafting_manager, "_instance"):
        get_crafting_manager._instance = CraftingManager()
    return get_crafting_manager._instance 
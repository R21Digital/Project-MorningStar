"""Schematic Looper for Batch 063 - Smart Crafting Integration.

This module provides:
- Schematic loop execution for known recipes
- Integration with crafting profiles
- Support for Artisan, Chef, and Structures professions
- Crafting progress tracking
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


@dataclass
class Schematic:
    """Represents a crafting schematic."""
    name: str
    profession: str  # "artisan", "chef", "structures"
    difficulty: int
    materials: List[str]
    crafting_time: int
    experience_gain: int
    ui_elements: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "profession": self.profession,
            "difficulty": self.difficulty,
            "materials": self.materials,
            "crafting_time": self.crafting_time,
            "experience_gain": self.experience_gain,
            "ui_elements": self.ui_elements
        }


@dataclass
class CraftingResult:
    """Represents the result of a crafting attempt."""
    schematic_name: str
    success: bool
    quantity: int
    experience_gained: int
    materials_used: List[str]
    crafting_time: float
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "schematic_name": self.schematic_name,
            "success": self.success,
            "quantity": self.quantity,
            "experience_gained": self.experience_gained,
            "materials_used": self.materials_used,
            "crafting_time": self.crafting_time,
            "timestamp": self.timestamp
        }


class SchematicLooper:
    """Handles schematic loop execution for crafting."""
    
    def __init__(self, schematics_path: str = "config/crafting_profiles/"):
        """Initialize the schematic looper.
        
        Parameters
        ----------
        schematics_path : str
            Path to schematics directory
        """
        self.schematics_path = Path(schematics_path)
        self.ocr_engine = OCREngine()
        self.logger = logging.getLogger(__name__)
        
        # Load known schematics
        self.known_schematics = self._load_known_schematics()
        
        # Crafting results tracking
        self.crafting_history: List[CraftingResult] = []
        
        # UI element mappings for different professions
        self.ui_mappings = {
            "artisan": ["craft", "create", "build", "assemble"],
            "chef": ["cook", "prepare", "bake", "brew"],
            "structures": ["construct", "build", "erect", "assemble"]
        }
    
    def _load_known_schematics(self) -> Dict[str, Schematic]:
        """Load known schematics from configuration."""
        schematics = {}
        
        # Default schematics for each profession
        default_schematics = {
            "artisan": [
                {
                    "name": "Basic Tool",
                    "profession": "artisan",
                    "difficulty": 1,
                    "materials": ["metal", "chemical"],
                    "crafting_time": 30,
                    "experience_gain": 50,
                    "ui_elements": ["craft", "create"]
                },
                {
                    "name": "Survey Device",
                    "profession": "artisan", 
                    "difficulty": 2,
                    "materials": ["metal", "chemical", "fiber"],
                    "crafting_time": 45,
                    "experience_gain": 75,
                    "ui_elements": ["craft", "assemble"]
                },
                {
                    "name": "Repair Kit",
                    "profession": "artisan",
                    "difficulty": 3,
                    "materials": ["metal", "chemical", "fiber", "mineral"],
                    "crafting_time": 60,
                    "experience_gain": 100,
                    "ui_elements": ["craft", "create"]
                }
            ],
            "chef": [
                {
                    "name": "Basic Meal",
                    "profession": "chef",
                    "difficulty": 1,
                    "materials": ["vegetable", "meat"],
                    "crafting_time": 20,
                    "experience_gain": 40,
                    "ui_elements": ["cook", "prepare"]
                },
                {
                    "name": "Quality Meal",
                    "profession": "chef",
                    "difficulty": 2,
                    "materials": ["vegetable", "meat", "spice"],
                    "crafting_time": 35,
                    "experience_gain": 60,
                    "ui_elements": ["cook", "prepare"]
                },
                {
                    "name": "Gourmet Meal",
                    "profession": "chef",
                    "difficulty": 3,
                    "materials": ["vegetable", "meat", "spice", "herb"],
                    "crafting_time": 50,
                    "experience_gain": 80,
                    "ui_elements": ["cook", "prepare"]
                }
            ],
            "structures": [
                {
                    "name": "Basic Structure",
                    "profession": "structures",
                    "difficulty": 1,
                    "materials": ["wood", "metal"],
                    "crafting_time": 40,
                    "experience_gain": 60,
                    "ui_elements": ["construct", "build"]
                },
                {
                    "name": "Advanced Structure",
                    "profession": "structures",
                    "difficulty": 2,
                    "materials": ["wood", "metal", "stone"],
                    "crafting_time": 60,
                    "experience_gain": 90,
                    "ui_elements": ["construct", "build"]
                },
                {
                    "name": "Complex Structure",
                    "profession": "structures",
                    "difficulty": 3,
                    "materials": ["wood", "metal", "stone", "crystal"],
                    "crafting_time": 80,
                    "experience_gain": 120,
                    "ui_elements": ["construct", "build"]
                }
            ]
        }
        
        # Convert to Schematic objects
        for profession, schematic_list in default_schematics.items():
            for schematic_data in schematic_list:
                schematic = Schematic(**schematic_data)
                schematics[schematic.name] = schematic
        
        self.logger.info(f"Loaded {len(schematics)} known schematics")
        return schematics
    
    def run_schematic_loop(self, schematic_names: List[str], 
                          max_quantity: int = 10) -> Dict[str, Any]:
        """Run crafting loop for specified schematics.
        
        Parameters
        ----------
        schematic_names : List[str]
            List of schematic names to craft
        max_quantity : int
            Maximum quantity to craft per schematic
            
        Returns
        -------
        Dict[str, Any]
            Results of crafting loop
        """
        results = {
            "items_crafted": 0,
            "schematics_completed": [],
            "total_experience": 0,
            "errors": []
        }
        
        for schematic_name in schematic_names:
            if schematic_name not in self.known_schematics:
                self.logger.warning(f"Unknown schematic: {schematic_name}")
                results["errors"].append(f"Unknown schematic: {schematic_name}")
                continue
            
            schematic = self.known_schematics[schematic_name]
            
            try:
                # Craft the schematic
                craft_result = self._craft_schematic(schematic, max_quantity)
                
                if craft_result.success:
                    results["items_crafted"] += craft_result.quantity
                    results["total_experience"] += craft_result.experience_gained
                    results["schematics_completed"].append(schematic_name)
                    
                    # Add to history
                    self.crafting_history.append(craft_result)
                    
                    self.logger.info(f"Crafted {craft_result.quantity} {schematic_name}")
                else:
                    results["errors"].append(f"Failed to craft {schematic_name}")
                    
            except Exception as e:
                self.logger.error(f"Error crafting {schematic_name}: {e}")
                results["errors"].append(f"Error crafting {schematic_name}: {str(e)}")
        
        # Update state
        update_state("crafting_results", results)
        
        return results
    
    def _craft_schematic(self, schematic: Schematic, max_quantity: int) -> CraftingResult:
        """Craft a single schematic.
        
        Parameters
        ----------
        schematic : Schematic
            Schematic to craft
        max_quantity : int
            Maximum quantity to craft
            
        Returns
        -------
        CraftingResult
            Result of crafting attempt
        """
        start_time = time.time()
        
        # Detect crafting UI
        if not self._detect_crafting_ui(schematic.profession):
            self.logger.warning(f"Could not detect {schematic.profession} crafting UI")
            return CraftingResult(
                schematic_name=schematic.name,
                success=False,
                quantity=0,
                experience_gained=0,
                materials_used=[],
                crafting_time=time.time() - start_time,
                timestamp=start_time
            )
        
        # Select schematic
        if not self._select_schematic(schematic):
            self.logger.warning(f"Could not select schematic: {schematic.name}")
            return CraftingResult(
                schematic_name=schematic.name,
                success=False,
                quantity=0,
                experience_gained=0,
                materials_used=[],
                crafting_time=time.time() - start_time,
                timestamp=start_time
            )
        
        # Start crafting
        if not self._start_crafting(schematic):
            self.logger.warning(f"Could not start crafting: {schematic.name}")
            return CraftingResult(
                schematic_name=schematic.name,
                success=False,
                quantity=0,
                experience_gained=0,
                materials_used=[],
                crafting_time=time.time() - start_time,
                timestamp=start_time
            )
        
        # Wait for crafting to complete
        crafting_time = self._wait_for_crafting_completion(schematic)
        
        # Complete crafting
        success = self._complete_crafting(schematic)
        
        # Calculate results
        quantity = 1 if success else 0
        experience_gained = schematic.experience_gain if success else 0
        materials_used = schematic.materials if success else []
        
        result = CraftingResult(
            schematic_name=schematic.name,
            success=success,
            quantity=quantity,
            experience_gained=experience_gained,
            materials_used=materials_used,
            crafting_time=crafting_time,
            timestamp=start_time
        )
        
        return result
    
    def _detect_crafting_ui(self, profession: str) -> bool:
        """Detect crafting UI for specific profession.
        
        Parameters
        ----------
        profession : str
            Profession type to detect UI for
            
        Returns
        -------
        bool
            True if UI detected
        """
        screen = capture_screen()
        text_results = self.ocr_engine.scan_text(screen)
        
        ui_elements = self.ui_mappings.get(profession, [])
        
        for result in text_results:
            text = result.text.lower()
            for element in ui_elements:
                if element.lower() in text:
                    self.logger.info(f"Detected {profession} crafting UI")
                    return True
        
        return False
    
    def _select_schematic(self, schematic: Schematic) -> bool:
        """Select a schematic in the crafting UI.
        
        Parameters
        ----------
        schematic : Schematic
            Schematic to select
            
        Returns
        -------
        bool
            True if schematic selected successfully
        """
        # Simulate schematic selection
        # In real implementation, this would click on the schematic in UI
        self.logger.info(f"Selecting schematic: {schematic.name}")
        
        # Simulate UI interaction
        time.sleep(0.5)
        
        return True
    
    def _start_crafting(self, schematic: Schematic) -> bool:
        """Start crafting process.
        
        Parameters
        ----------
        schematic : Schematic
            Schematic to craft
            
        Returns
        -------
        bool
            True if crafting started successfully
        """
        # Simulate starting crafting
        self.logger.info(f"Starting crafting: {schematic.name}")
        
        # Simulate UI interaction
        time.sleep(0.5)
        
        return True
    
    def _wait_for_crafting_completion(self, schematic: Schematic) -> float:
        """Wait for crafting to complete.
        
        Parameters
        ----------
        schematic : Schematic
            Schematic being crafted
            
        Returns
        -------
        float
            Time taken for crafting
        """
        start_time = time.time()
        
        # Simulate crafting time
        # In real implementation, this would monitor crafting progress
        time.sleep(schematic.crafting_time / 10)  # Accelerated for testing
        
        return time.time() - start_time
    
    def _complete_crafting(self, schematic: Schematic) -> bool:
        """Complete the crafting process.
        
        Parameters
        ----------
        schematic : Schematic
            Schematic being crafted
            
        Returns
        -------
        bool
            True if crafting completed successfully
        """
        # Simulate completing crafting
        self.logger.info(f"Completing crafting: {schematic.name}")
        
        # Simulate UI interaction
        time.sleep(0.5)
        
        # Simulate success (90% success rate for testing)
        import random
        success = random.random() > 0.1
        
        return success
    
    def get_crafting_history(self) -> List[Dict[str, Any]]:
        """Get crafting history.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of crafting results
        """
        return [result.to_dict() for result in self.crafting_history]
    
    def get_schematic_stats(self, schematic_name: str) -> Dict[str, Any]:
        """Get statistics for a specific schematic.
        
        Parameters
        ----------
        schematic_name : str
            Name of schematic to get stats for
            
        Returns
        -------
        Dict[str, Any]
            Schematic statistics
        """
        schematic_results = [
            result for result in self.crafting_history 
            if result.schematic_name == schematic_name
        ]
        
        if not schematic_results:
            return {
                "schematic_name": schematic_name,
                "total_crafted": 0,
                "success_rate": 0.0,
                "total_experience": 0,
                "average_crafting_time": 0.0
            }
        
        total_crafted = sum(result.quantity for result in schematic_results)
        successful_crafts = sum(1 for result in schematic_results if result.success)
        success_rate = successful_crafts / len(schematic_results)
        total_experience = sum(result.experience_gained for result in schematic_results)
        avg_crafting_time = sum(result.crafting_time for result in schematic_results) / len(schematic_results)
        
        return {
            "schematic_name": schematic_name,
            "total_crafted": total_crafted,
            "success_rate": success_rate,
            "total_experience": total_experience,
            "average_crafting_time": avg_crafting_time
        } 
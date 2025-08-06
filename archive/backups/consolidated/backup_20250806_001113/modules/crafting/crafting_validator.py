"""Crafting Validator for Batch 063 - Smart Crafting Integration.

This module provides:
- Inventory space validation
- Resource availability checking
- Power level validation
- Crafting requirements verification
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from core.ocr import OCREngine
from core.screenshot import capture_screen
from core.state_tracker import get_state


@dataclass
class ValidationResult:
    """Represents the result of a validation check."""
    valid: bool
    missing_resources: List[str]
    insufficient_power: bool
    insufficient_space: bool
    errors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "valid": self.valid,
            "missing_resources": self.missing_resources,
            "insufficient_power": self.insufficient_power,
            "insufficient_space": self.insufficient_space,
            "errors": self.errors
        }


@dataclass
class ResourceRequirement:
    """Represents a resource requirement for crafting."""
    name: str
    quantity: int
    type: str  # "material", "component", "fuel"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "quantity": self.quantity,
            "type": self.type
        }


class CraftingValidator:
    """Validates crafting requirements before starting crafting."""
    
    def __init__(self):
        """Initialize the crafting validator."""
        self.ocr_engine = OCREngine()
        self.logger = logging.getLogger(__name__)
        
        # Default validation thresholds
        self.default_thresholds = {
            "min_inventory_space": 5,
            "min_power": 100,
            "min_health": 50,
            "min_action": 50
        }
        
        # Known resource types
        self.resource_types = {
            "materials": ["metal", "chemical", "fiber", "wood", "stone", "crystal"],
            "components": ["circuit", "battery", "sensor", "motor", "gear"],
            "fuels": ["power_cell", "energy_core", "reactor_core"],
            "consumables": ["food", "medicine", "repair_kit"]
        }
    
    def validate_crafting_requirements(self, profile: Dict[str, Any]) -> bool:
        """Validate all crafting requirements for a profile.
        
        Parameters
        ----------
        profile : Dict[str, Any]
            Crafting profile to validate
            
        Returns
        -------
        bool
            True if all requirements are met
        """
        validation_result = ValidationResult(
            valid=True,
            missing_resources=[],
            insufficient_power=False,
            insufficient_space=False,
            errors=[]
        )
        
        # Check inventory space
        if not self._validate_inventory_space(profile):
            validation_result.insufficient_space = True
            validation_result.valid = False
            validation_result.errors.append("Insufficient inventory space")
        
        # Check power level
        if not self._validate_power_level(profile):
            validation_result.insufficient_power = True
            validation_result.valid = False
            validation_result.errors.append("Insufficient power")
        
        # Check resource availability
        missing_resources = self._validate_resources(profile)
        if missing_resources:
            validation_result.missing_resources = missing_resources
            validation_result.valid = False
            validation_result.errors.append(f"Missing resources: {', '.join(missing_resources)}")
        
        # Check health and action
        if not self._validate_character_status(profile):
            validation_result.valid = False
            validation_result.errors.append("Character status insufficient")
        
        if validation_result.valid:
            self.logger.info("All crafting requirements validated successfully")
        else:
            self.logger.warning(f"Crafting validation failed: {validation_result.errors}")
        
        return validation_result.valid
    
    def _validate_inventory_space(self, profile: Dict[str, Any]) -> bool:
        """Validate inventory space availability.
        
        Parameters
        ----------
        profile : Dict[str, Any]
            Crafting profile
            
        Returns
        -------
        bool
            True if sufficient inventory space
        """
        min_space = profile.get("min_inventory_space", 
                               self.default_thresholds["min_inventory_space"])
        
        # Get current inventory space from state
        current_space = get_state("inventory_space", 10)  # Default to 10
        
        if current_space < min_space:
            self.logger.warning(f"Insufficient inventory space: {current_space}/{min_space}")
            return False
        
        self.logger.info(f"Inventory space validated: {current_space}/{min_space}")
        return True
    
    def _validate_power_level(self, profile: Dict[str, Any]) -> bool:
        """Validate power level for crafting.
        
        Parameters
        ----------
        profile : Dict[str, Any]
            Crafting profile
            
        Returns
        -------
        bool
            True if sufficient power
        """
        min_power = profile.get("min_power", self.default_thresholds["min_power"])
        
        # Get current power from state
        current_power = get_state("current_power", 200)  # Default to 200
        
        if current_power < min_power:
            self.logger.warning(f"Insufficient power: {current_power}/{min_power}")
            return False
        
        self.logger.info(f"Power level validated: {current_power}/{min_power}")
        return True
    
    def _validate_resources(self, profile: Dict[str, Any]) -> List[str]:
        """Validate resource availability.
        
        Parameters
        ----------
        profile : Dict[str, Any]
            Crafting profile
            
        Returns
        -------
        List[str]
            List of missing resources
        """
        required_resources = profile.get("required_resources", [])
        if not required_resources:
            return []
        
        # Get current inventory from state
        current_inventory = get_state("inventory_items", {})
        
        missing_resources = []
        
        for resource in required_resources:
            if resource not in current_inventory or current_inventory[resource] <= 0:
                missing_resources.append(resource)
        
        if missing_resources:
            self.logger.warning(f"Missing resources: {missing_resources}")
        else:
            self.logger.info("All required resources available")
        
        return missing_resources
    
    def _validate_character_status(self, profile: Dict[str, Any]) -> bool:
        """Validate character health and action points.
        
        Parameters
        ----------
        profile : Dict[str, Any]
            Crafting profile
            
        Returns
        -------
        bool
            True if character status is sufficient
        """
        min_health = profile.get("min_health", self.default_thresholds["min_health"])
        min_action = profile.get("min_action", self.default_thresholds["min_action"])
        
        # Get current character status from state
        current_health = get_state("current_health", 100)
        current_action = get_state("current_action", 100)
        
        if current_health < min_health:
            self.logger.warning(f"Insufficient health: {current_health}/{min_health}")
            return False
        
        if current_action < min_action:
            self.logger.warning(f"Insufficient action: {current_action}/{min_action}")
            return False
        
        self.logger.info(f"Character status validated: Health {current_health}, Action {current_action}")
        return True
    
    def scan_inventory_for_resources(self) -> Dict[str, int]:
        """Scan inventory for available resources.
        
        Returns
        -------
        Dict[str, int]
            Dictionary of resource names and quantities
        """
        screen = capture_screen()
        text_results = self.ocr_engine.scan_text(screen)
        
        resources = {}
        
        for result in text_results:
            text = result.text.lower()
            
            # Check for resource patterns
            for resource_type, resource_list in self.resource_types.items():
                for resource in resource_list:
                    if resource in text:
                        # Try to extract quantity
                        quantity = self._extract_quantity(text)
                        resources[resource] = quantity
                        break
        
        self.logger.info(f"Scanned inventory: {len(resources)} resource types found")
        return resources
    
    def _extract_quantity(self, text: str) -> int:
        """Extract quantity from text.
        
        Parameters
        ----------
        text : str
            Text containing quantity information
            
        Returns
        -------
        int
            Extracted quantity
        """
        import re
        
        # Look for number patterns
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        
        return 1  # Default to 1 if no number found
    
    def get_validation_summary(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive validation summary.
        
        Parameters
        ----------
        profile : Dict[str, Any]
            Crafting profile to validate
            
        Returns
        -------
        Dict[str, Any]
            Validation summary
        """
        summary = {
            "inventory_space": {
                "current": get_state("inventory_space", 10),
                "required": profile.get("min_inventory_space", self.default_thresholds["min_inventory_space"]),
                "valid": self._validate_inventory_space(profile)
            },
            "power_level": {
                "current": get_state("current_power", 200),
                "required": profile.get("min_power", self.default_thresholds["min_power"]),
                "valid": self._validate_power_level(profile)
            },
            "resources": {
                "available": self.scan_inventory_for_resources(),
                "required": profile.get("required_resources", []),
                "missing": self._validate_resources(profile)
            },
            "character_status": {
                "health": get_state("current_health", 100),
                "action": get_state("current_action", 100),
                "valid": self._validate_character_status(profile)
            }
        }
        
        # Overall validation
        summary["overall_valid"] = (
            summary["inventory_space"]["valid"] and
            summary["power_level"]["valid"] and
            len(summary["resources"]["missing"]) == 0 and
            summary["character_status"]["valid"]
        )
        
        return summary
    
    def estimate_crafting_cost(self, schematic_name: str, 
                             schematic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate the cost of crafting an item.
        
        Parameters
        ----------
        schematic_name : str
            Name of the schematic
        schematic_data : Dict[str, Any]
            Schematic data
            
        Returns
        -------
        Dict[str, Any]
            Cost estimation
        """
        materials = schematic_data.get("materials", [])
        current_resources = self.scan_inventory_for_resources()
        
        cost_breakdown = {}
        total_cost = 0
        
        for material in materials:
            available = current_resources.get(material, 0)
            required = 1  # Default to 1, could be more sophisticated
            
            if available >= required:
                cost_breakdown[material] = {
                    "available": available,
                    "required": required,
                    "sufficient": True,
                    "cost": 0  # Already have it
                }
            else:
                # Estimate market cost (placeholder values)
                estimated_cost = self._estimate_material_cost(material)
                cost_breakdown[material] = {
                    "available": available,
                    "required": required,
                    "sufficient": False,
                    "cost": estimated_cost
                }
                total_cost += estimated_cost
        
        return {
            "schematic_name": schematic_name,
            "total_cost": total_cost,
            "materials": cost_breakdown,
            "can_craft": all(m["sufficient"] for m in cost_breakdown.values())
        }
    
    def _estimate_material_cost(self, material: str) -> int:
        """Estimate the cost of a material.
        
        Parameters
        ----------
        material : str
            Material name
            
        Returns
        -------
        int
            Estimated cost in credits
        """
        # Placeholder cost estimates
        cost_estimates = {
            "metal": 50,
            "chemical": 75,
            "fiber": 25,
            "wood": 30,
            "stone": 40,
            "crystal": 200,
            "circuit": 150,
            "battery": 100,
            "sensor": 120,
            "motor": 180,
            "gear": 80,
            "power_cell": 300,
            "energy_core": 500,
            "reactor_core": 1000
        }
        
        return cost_estimates.get(material, 100)  # Default to 100 credits 
"""
MS11 Batch 066 - Keybind Validator

Validates keybind configurations and detects conflicts, missing keybinds,
and provides recommendations for MS11 compatibility.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from .keybind_parser import Keybind, KeybindStatus, KeybindCategory


@dataclass
class KeybindValidationResult:
    """Result of keybind validation."""
    valid_keybinds: int
    missing_keybinds: int
    conflicting_keybinds: int
    unknown_keybinds: int
    total_keybinds: int
    validation_errors: List[str]
    recommendations: List[str]
    critical_issues: List[str]


class KeybindValidator:
    """Validator for keybind configurations."""
    
    def __init__(self):
        """Initialize the keybind validator."""
        self.key_conflicts: Dict[str, List[str]] = {}
        self.missing_required: List[str] = []
        self.recommendations: List[str] = []
        self.critical_issues: List[str] = []
    
    def validate_keybinds(self, keybinds: Dict[str, Keybind], required_keybinds: Dict[str, Keybind]) -> KeybindValidationResult:
        """Validate keybind configuration.
        
        Args:
            keybinds: Dictionary of detected keybinds
            required_keybinds: Dictionary of required keybinds
            
        Returns:
            KeybindValidationResult with validation details
        """
        self.key_conflicts.clear()
        self.missing_required.clear()
        self.recommendations.clear()
        self.critical_issues.clear()
        
        # Check for missing required keybinds
        self._check_missing_required(keybinds, required_keybinds)
        
        # Check for key conflicts
        self._check_key_conflicts(keybinds)
        
        # Update keybind statuses
        self._update_keybind_statuses(keybinds, required_keybinds)
        
        # Generate recommendations
        self._generate_recommendations(keybinds, required_keybinds)
        
        # Check for critical issues
        self._check_critical_issues(keybinds, required_keybinds)
        
        return self._create_validation_result(keybinds)
    
    def _check_missing_required(self, keybinds: Dict[str, Keybind], required_keybinds: Dict[str, Keybind]) -> None:
        """Check for missing required keybinds."""
        for name, required_keybind in required_keybinds.items():
            if name not in keybinds or not keybinds[name].key:
                self.missing_required.append(name)
                if required_keybind.required:
                    self.critical_issues.append(f"Missing required keybind: {name}")
    
    def _check_key_conflicts(self, keybinds: Dict[str, Keybind]) -> None:
        """Check for key conflicts (same key bound to multiple actions)."""
        key_to_actions: Dict[str, List[str]] = {}
        
        for name, keybind in keybinds.items():
            if keybind.key:
                if keybind.key not in key_to_actions:
                    key_to_actions[keybind.key] = []
                key_to_actions[keybind.key].append(name)
        
        # Find conflicts
        for key, actions in key_to_actions.items():
            if len(actions) > 1:
                self.key_conflicts[key] = actions
                self.critical_issues.append(f"Key conflict: {key} bound to {', '.join(actions)}")
    
    def _update_keybind_statuses(self, keybinds: Dict[str, Keybind], required_keybinds: Dict[str, Keybind]) -> None:
        """Update the status of each keybind based on validation."""
        for name, keybind in keybinds.items():
            if not keybind.key:
                keybind.status = KeybindStatus.MISSING
            elif name in self.key_conflicts.get(keybind.key, []):
                keybind.status = KeybindStatus.CONFLICT
            else:
                keybind.status = KeybindStatus.VALID
        
        # Update required keybinds that weren't found
        for name, required_keybind in required_keybinds.items():
            if name not in keybinds:
                required_keybind.status = KeybindStatus.MISSING
    
    def _generate_recommendations(self, keybinds: Dict[str, Keybind], required_keybinds: Dict[str, Keybind]) -> None:
        """Generate recommendations for missing or problematic keybinds."""
        # Recommendations for missing required keybinds
        for name in self.missing_required:
            if name in required_keybinds:
                suggestion = required_keybinds[name].suggestion
                if suggestion:
                    self.recommendations.append(f"Add keybind for '{name}': {suggestion}")
        
        # Recommendations for key conflicts
        for key, actions in self.key_conflicts.items():
            self.recommendations.append(f"Resolve conflict for key '{key}' used by: {', '.join(actions)}")
        
        # General recommendations
        if not keybinds.get('attack'):
            self.recommendations.append("Add attack keybind (F1 recommended) for combat functionality")
        
        if not keybinds.get('use'):
            self.recommendations.append("Add use keybind (Enter recommended) for interaction")
        
        if not keybinds.get('inventory'):
            self.recommendations.append("Add inventory keybind (I recommended) for inventory management")
        
        if not keybinds.get('map'):
            self.recommendations.append("Add map keybind (M recommended) for navigation")
    
    def _check_critical_issues(self, keybinds: Dict[str, Keybind], required_keybinds: Dict[str, Keybind]) -> None:
        """Check for critical issues that would break core bot functions."""
        critical_keybinds = ['attack', 'use', 'inventory', 'map', 'chat', 'target']
        
        missing_critical = []
        for name in critical_keybinds:
            if name not in keybinds or not keybinds[name].key:
                missing_critical.append(name)
        
        if missing_critical:
            self.critical_issues.append(f"Critical keybinds missing: {', '.join(missing_critical)}")
        
        # Check for excessive conflicts
        if len(self.key_conflicts) > 3:
            self.critical_issues.append(f"Too many key conflicts ({len(self.key_conflicts)}) detected")
    
    def _create_validation_result(self, keybinds: Dict[str, Keybind]) -> KeybindValidationResult:
        """Create the validation result object."""
        valid_count = sum(1 for kb in keybinds.values() if kb.status == KeybindStatus.VALID)
        missing_count = sum(1 for kb in keybinds.values() if kb.status == KeybindStatus.MISSING)
        conflict_count = sum(1 for kb in keybinds.values() if kb.status == KeybindStatus.CONFLICT)
        unknown_count = sum(1 for kb in keybinds.values() if kb.status == KeybindStatus.UNKNOWN)
        
        return KeybindValidationResult(
            valid_keybinds=valid_count,
            missing_keybinds=missing_count,
            conflicting_keybinds=conflict_count,
            unknown_keybinds=unknown_count,
            total_keybinds=len(keybinds),
            validation_errors=self.critical_issues,
            recommendations=self.recommendations,
            critical_issues=self.critical_issues
        )
    
    def get_keybind_suggestion(self, name: str) -> Optional[str]:
        """Get a suggestion for a specific keybind."""
        suggestions = {
            'attack': 'F1',
            'use': 'Enter',
            'inventory': 'I',
            'map': 'M',
            'chat': 'Enter',
            'target': 'Tab',
            'heal': 'H',
            'follow': 'F',
            'stop': 'Escape',
            'loot': 'L'
        }
        return suggestions.get(name)
    
    def is_critical_issue(self, validation_result: KeybindValidationResult) -> bool:
        """Check if there are critical issues that would break core bot functions."""
        return len(validation_result.critical_issues) > 0 
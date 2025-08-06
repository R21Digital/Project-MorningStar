#!/usr/bin/env python3
"""Keybind Validator for SWG Automation

This module provides comprehensive validation of keybindings for SWG automation.
It can validate essential bindings, detect conflicts, and provide recommendations.
"""

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

try:
    from core.ocr import get_ocr_engine, OCRResult
    from core.screenshot import capture_screen
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class ValidationStatus(Enum):
    """Status of keybind validation."""
    VALID = "valid"
    MISSING = "missing"
    CONFLICT = "conflict"
    OPTIONAL = "optional"
    UNKNOWN = "unknown"


class DetectionMethod(Enum):
    """Methods for detecting keybinds."""
    USER_CFG = "user_cfg"
    INPUTMAP_XML = "inputmap_xml"
    OCR_FALLBACK = "ocr_fallback"
    MANUAL_CONFIG = "manual_config"


@dataclass
class KeybindValidation:
    """Result of keybind validation."""
    action: str
    expected_key: str
    detected_key: Optional[str] = None
    status: ValidationStatus = ValidationStatus.UNKNOWN
    category: str = ""
    required: bool = False
    description: str = ""
    detection_method: Optional[DetectionMethod] = None
    confidence: float = 0.0
    suggestions: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Comprehensive validation report."""
    total_bindings: int
    valid_bindings: int
    missing_bindings: int
    conflicting_bindings: int
    optional_bindings: int
    essential_missing: List[str]
    warnings: List[str]
    recommendations: List[str]
    validation_time: float
    detection_methods_used: List[DetectionMethod]
    confidence_score: float


class KeybindValidator:
    """Comprehensive keybind validator for SWG automation."""
    
    def __init__(self, template_path: str = "config/keybind_template.json"):
        """Initialize the keybind validator.
        
        Parameters
        ----------
        template_path : str
            Path to the keybind template file
        """
        self.logger = self._setup_logging()
        self.template_path = Path(template_path)
        self.template = self._load_template()
        self.essential_bindings = self._extract_essential_bindings()
        self.optional_bindings = self._extract_optional_bindings()
        self.validation_rules = self.template.get("validation_rules", {})
        
        # Detection methods configuration
        self.detection_config = self.template.get("detection_methods", {})
        self.auto_detect_enabled = self.detection_config.get("auto_detect", {}).get("enabled", True)
        self.manual_config_enabled = self.detection_config.get("manual_config", {}).get("enabled", True)
        
        self.logger.info("Keybind Validator initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the validator."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_template(self) -> Dict[str, Any]:
        """Load the keybind template."""
        try:
            if self.template_path.exists():
                with open(self.template_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Template file not found: {self.template_path}")
                return self._get_default_template()
        except Exception as e:
            self.logger.error(f"Error loading template: {e}")
            return self._get_default_template()
    
    def _get_default_template(self) -> Dict[str, Any]:
        """Get default template if file is not found."""
        return {
            "essential_bindings": {
                "combat": {
                    "attack": {"key": "1", "required": True},
                    "target_next": {"key": "Tab", "required": True}
                },
                "movement": {
                    "forward": {"key": "W", "required": True},
                    "backward": {"key": "S", "required": True},
                    "left": {"key": "A", "required": True},
                    "right": {"key": "D", "required": True}
                }
            },
            "validation_rules": {
                "required_categories": ["combat", "movement"],
                "conflict_detection": True
            }
        }
    
    def _extract_essential_bindings(self) -> Dict[str, Dict[str, Any]]:
        """Extract essential bindings from template."""
        essential = {}
        for category, bindings in self.template.get("essential_bindings", {}).items():
            for action, config in bindings.items():
                essential[action] = {
                    "key": config.get("key", ""),
                    "category": category,
                    "required": config.get("required", False),
                    "description": config.get("description", "")
                }
        return essential
    
    def _extract_optional_bindings(self) -> Dict[str, Dict[str, Any]]:
        """Extract optional bindings from template."""
        optional = {}
        for category, bindings in self.template.get("optional_bindings", {}).items():
            for action, config in bindings.items():
                optional[action] = {
                    "key": config.get("key", ""),
                    "category": category,
                    "required": config.get("required", False),
                    "description": config.get("description", "")
                }
        return optional
    
    def validate_keybinds(self, detected_bindings: Dict[str, str]) -> ValidationReport:
        """Validate detected keybinds against template.
        
        Parameters
        ----------
        detected_bindings : Dict[str, str]
            Dictionary of action -> key mappings
            
        Returns
        -------
        ValidationReport
            Comprehensive validation report
        """
        start_time = time.time()
        self.logger.info("Starting keybind validation")
        
        validations = []
        essential_missing = []
        warnings = []
        recommendations = []
        
        # Validate essential bindings
        for action, config in self.essential_bindings.items():
            expected_key = config["key"]
            detected_key = detected_bindings.get(action)
            
            validation = self._validate_single_binding(
                action, expected_key, detected_key, config
            )
            validations.append(validation)
            
            if validation.status == ValidationStatus.MISSING and config["required"]:
                essential_missing.append(action)
            elif validation.status == ValidationStatus.CONFLICT:
                warnings.append(f"Conflict detected for {action}: {validation.conflicts}")
        
        # Validate optional bindings
        for action, config in self.optional_bindings.items():
            expected_key = config["key"]
            detected_key = detected_bindings.get(action)
            
            validation = self._validate_single_binding(
                action, expected_key, detected_key, config
            )
            validations.append(validation)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(validations, detected_bindings)
        
        # Calculate statistics
        total = len(validations)
        valid = len([v for v in validations if v.status == ValidationStatus.VALID])
        missing = len([v for v in validations if v.status == ValidationStatus.MISSING])
        conflicting = len([v for v in validations if v.status == ValidationStatus.CONFLICT])
        optional = len([v for v in validations if v.status == ValidationStatus.OPTIONAL])
        
        confidence_score = self._calculate_confidence_score(validations)
        
        report = ValidationReport(
            total_bindings=total,
            valid_bindings=valid,
            missing_bindings=missing,
            conflicting_bindings=conflicting,
            optional_bindings=optional,
            essential_missing=essential_missing,
            warnings=warnings,
            recommendations=recommendations,
            validation_time=time.time() - start_time,
            detection_methods_used=[DetectionMethod.USER_CFG],  # Placeholder
            confidence_score=confidence_score
        )
        
        self.logger.info(f"Validation complete: {valid}/{total} valid bindings")
        return report
    
    def _validate_single_binding(
        self, 
        action: str, 
        expected_key: str, 
        detected_key: Optional[str], 
        config: Dict[str, Any]
    ) -> KeybindValidation:
        """Validate a single keybinding.
        
        Parameters
        ----------
        action : str
            The action name
        expected_key : str
            Expected key binding
        detected_key : Optional[str]
            Actually detected key binding
        config : Dict[str, Any]
            Configuration for this binding
            
        Returns
        -------
        KeybindValidation
            Validation result for this binding
        """
        validation = KeybindValidation(
            action=action,
            expected_key=expected_key,
            detected_key=detected_key,
            category=config.get("category", ""),
            required=config.get("required", False),
            description=config.get("description", "")
        )
        
        if not detected_key:
            validation.status = ValidationStatus.MISSING
            validation.suggestions.append(f"Bind {action} to {expected_key}")
        elif detected_key.lower() == expected_key.lower():
            validation.status = ValidationStatus.VALID
            validation.confidence = 1.0
        else:
            validation.status = ValidationStatus.CONFLICT
            validation.conflicts.append(f"Expected {expected_key}, got {detected_key}")
            validation.suggestions.append(f"Change {action} from {detected_key} to {expected_key}")
        
        return validation
    
    def _generate_recommendations(
        self, 
        validations: List[KeybindValidation], 
        detected_bindings: Dict[str, str]
    ) -> List[str]:
        """Generate recommendations based on validation results.
        
        Parameters
        ----------
        validations : List[KeybindValidation]
            List of validation results
        detected_bindings : Dict[str, str]
            Detected keybindings
            
        Returns
        -------
        List[str]
            List of recommendations
        """
        recommendations = []
        
        # Check for missing essential bindings
        missing_essential = [v for v in validations 
                           if v.status == ValidationStatus.MISSING and v.required]
        if missing_essential:
            recommendations.append(
                f"Missing {len(missing_essential)} essential bindings. "
                "Please configure these for automation to work properly."
            )
        
        # Check for conflicts
        conflicts = [v for v in validations if v.status == ValidationStatus.CONFLICT]
        if conflicts:
            recommendations.append(
                f"Found {len(conflicts)} conflicting bindings. "
                "Consider updating these for consistency."
            )
        
        # Check for unused keys
        used_keys = set(detected_bindings.values())
        template_keys = set()
        for binding in self.essential_bindings.values():
            template_keys.add(binding["key"])
        
        unused_keys = template_keys - used_keys
        if unused_keys:
            recommendations.append(
                f"Unused keys detected: {', '.join(unused_keys)}. "
                "Consider binding these to additional actions."
            )
        
        return recommendations
    
    def _calculate_confidence_score(self, validations: List[KeybindValidation]) -> float:
        """Calculate overall confidence score.
        
        Parameters
        ----------
        validations : List[KeybindValidation]
            List of validation results
            
        Returns
        -------
        float
            Confidence score between 0 and 1
        """
        if not validations:
            return 0.0
        
        essential_validations = [v for v in validations if v.required]
        if not essential_validations:
            return 0.0
        
        valid_essential = len([v for v in essential_validations 
                             if v.status == ValidationStatus.VALID])
        return valid_essential / len(essential_validations)
    
    def detect_conflicts(self, bindings: Dict[str, str]) -> List[Tuple[str, str, str]]:
        """Detect keybinding conflicts.
        
        Parameters
        ----------
        bindings : Dict[str, str]
            Dictionary of action -> key mappings
            
        Returns
        -------
        List[Tuple[str, str, str]]
            List of (action1, action2, key) conflicts
        """
        conflicts = []
        key_to_actions = {}
        
        for action, key in bindings.items():
            if key in key_to_actions:
                conflicts.append((key_to_actions[key], action, key))
            else:
                key_to_actions[key] = action
        
        return conflicts
    
    def suggest_alternative_keys(self, action: str, current_key: str) -> List[str]:
        """Suggest alternative keys for a binding.
        
        Parameters
        ----------
        action : str
            The action name
        current_key : str
            Current key binding
            
        Returns
        -------
        List[str]
            List of alternative key suggestions
        """
        # Common alternative keys based on action type
        alternatives = {
            "attack": ["1", "F1", "Q"],
            "target_next": ["Tab", "F2", "T"],
            "use": ["E", "F3", "U"],
            "inventory": ["I", "F4", "B"],
            "mount": ["M", "F5", "V"],
            "forward": ["W", "Up", "Num8"],
            "backward": ["S", "Down", "Num2"],
            "left": ["A", "Left", "Num4"],
            "right": ["D", "Right", "Num6"]
        }
        
        return alternatives.get(action, ["F1", "F2", "F3", "F4", "F5"])
    
    def generate_validation_report(self, report: ValidationReport) -> str:
        """Generate a human-readable validation report.
        
        Parameters
        ----------
        report : ValidationReport
            Validation report to format
            
        Returns
        -------
        str
            Formatted report string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("SWG KEYBIND VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Validation Time: {report.validation_time:.2f}s")
        lines.append(f"Confidence Score: {report.confidence_score:.1%}")
        lines.append("")
        
        # Summary
        lines.append("SUMMARY:")
        lines.append(f"  Total Bindings: {report.total_bindings}")
        lines.append(f"  Valid: {report.valid_bindings}")
        lines.append(f"  Missing: {report.missing_bindings}")
        lines.append(f"  Conflicting: {report.conflicting_bindings}")
        lines.append(f"  Optional: {report.optional_bindings}")
        lines.append("")
        
        # Essential missing
        if report.essential_missing:
            lines.append("ESSENTIAL MISSING BINDINGS:")
            for action in report.essential_missing:
                config = self.essential_bindings.get(action, {})
                lines.append(f"  ❌ {action}: {config.get('key', 'Unknown')} - {config.get('description', '')}")
            lines.append("")
        
        # Warnings
        if report.warnings:
            lines.append("WARNINGS:")
            for warning in report.warnings:
                lines.append(f"  ⚠️  {warning}")
            lines.append("")
        
        # Recommendations
        if report.recommendations:
            lines.append("RECOMMENDATIONS:")
            for rec in report.recommendations:
                lines.append(f"  💡 {rec}")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)


def get_keybind_validator() -> KeybindValidator:
    """Get a keybind validator instance."""
    return KeybindValidator()


def validate_keybinds(bindings: Dict[str, str]) -> ValidationReport:
    """Validate keybinds using default validator.
    
    Parameters
    ----------
    bindings : Dict[str, str]
        Dictionary of action -> key mappings
        
    Returns
    -------
    ValidationReport
        Validation report
    """
    validator = get_keybind_validator()
    return validator.validate_keybinds(bindings)


def generate_report(bindings: Dict[str, str]) -> str:
    """Generate a validation report for keybinds.
    
    Parameters
    ----------
    bindings : Dict[str, str]
        Dictionary of action -> key mappings
        
    Returns
    -------
    str
        Formatted validation report
    """
    validator = get_keybind_validator()
    report = validator.validate_keybinds(bindings)
    return validator.generate_validation_report(report)


if __name__ == "__main__":
    # Test the validator
    test_bindings = {
        "attack": "1",
        "target_next": "Tab",
        "use": "E",
        "inventory": "I",
        "mount": "M",
        "forward": "W",
        "backward": "S",
        "left": "A",
        "right": "D"
    }
    
    print("Testing Keybind Validator...")
    report = validate_keybinds(test_bindings)
    print(generate_report(test_bindings)) 
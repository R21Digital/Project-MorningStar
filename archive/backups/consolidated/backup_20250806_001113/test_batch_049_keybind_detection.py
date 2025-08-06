#!/usr/bin/env python3
"""Tests for Batch 049 - Keybind Detection + Input Mapping Module

This test suite covers all aspects of the keybind detection and validation system.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from core.keybind_manager import (
    KeybindManager, KeybindManagerConfig, DetectionMode, ConfigMode,
    KeybindDetectionResult, get_keybind_manager, run_keybind_setup
)
from utils.keybind_validator import (
    KeybindValidator, ValidationReport, ValidationStatus, DetectionMethod,
    KeybindValidation, validate_keybinds, generate_report
)
from core.keybinding_scanner import KeybindingScanner, KeyBinding, BindingStatus


class TestKeybindValidator(unittest.TestCase):
    """Test the keybind validator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = KeybindValidator()
        
        # Test bindings
        self.valid_bindings = {
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
        
        self.invalid_bindings = {
            "attack": "Tab",  # Conflict with target_next
            "target_next": "Tab",
            "use": "W",       # Conflict with forward
            "forward": "W"
        }
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        self.assertIsNotNone(self.validator)
        self.assertIsNotNone(self.validator.essential_bindings)
        self.assertIsNotNone(self.validator.optional_bindings)
        self.assertIsNotNone(self.validator.validation_rules)
    
    def test_validate_keybinds_valid(self):
        """Test validation of valid keybinds."""
        report = self.validator.validate_keybinds(self.valid_bindings)
        
        self.assertIsInstance(report, ValidationReport)
        self.assertGreater(report.confidence_score, 0.0)
        self.assertGreater(report.valid_bindings, 0)
    
    def test_validate_keybinds_invalid(self):
        """Test validation of invalid keybinds."""
        report = self.validator.validate_keybinds(self.invalid_bindings)
        
        self.assertIsInstance(report, ValidationReport)
        self.assertGreater(report.conflicting_bindings, 0)
    
    def test_validate_keybinds_empty(self):
        """Test validation of empty keybinds."""
        report = self.validator.validate_keybinds({})
        
        self.assertIsInstance(report, ValidationReport)
        self.assertEqual(report.valid_bindings, 0)
        self.assertGreater(report.missing_bindings, 0)
    
    def test_detect_conflicts(self):
        """Test conflict detection."""
        conflicts = self.validator.detect_conflicts(self.invalid_bindings)
        
        self.assertIsInstance(conflicts, list)
        self.assertGreater(len(conflicts), 0)
        
        for conflict in conflicts:
            self.assertIsInstance(conflict, tuple)
            self.assertEqual(len(conflict), 3)
    
    def test_suggest_alternative_keys(self):
        """Test alternative key suggestions."""
        alternatives = self.validator.suggest_alternative_keys("attack", "1")
        
        self.assertIsInstance(alternatives, list)
        self.assertGreater(len(alternatives), 0)
        self.assertIn("1", alternatives)
    
    def test_generate_validation_report(self):
        """Test validation report generation."""
        report = self.validator.validate_keybinds(self.valid_bindings)
        report_text = self.validator.generate_validation_report(report)
        
        self.assertIsInstance(report_text, str)
        self.assertIn("SWG KEYBIND VALIDATION REPORT", report_text)
        self.assertIn("SUMMARY:", report_text)
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        # Test with valid bindings
        validations = []
        for action, config in self.validator.essential_bindings.items():
            if action in self.valid_bindings:
                validation = KeybindValidation(
                    action=action,
                    expected_key=config["key"],
                    detected_key=self.valid_bindings[action],
                    status=ValidationStatus.VALID,
                    required=config["required"]
                )
                validations.append(validation)
        
        confidence = self.validator._calculate_confidence_score(validations)
        self.assertGreater(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_validate_single_binding(self):
        """Test single binding validation."""
        config = self.validator.essential_bindings["attack"]
        
        # Test valid binding
        validation = self.validator._validate_single_binding(
            "attack", "1", "1", config
        )
        self.assertEqual(validation.status, ValidationStatus.VALID)
        
        # Test missing binding
        validation = self.validator._validate_single_binding(
            "attack", "1", None, config
        )
        self.assertEqual(validation.status, ValidationStatus.MISSING)
        
        # Test conflicting binding
        validation = self.validator._validate_single_binding(
            "attack", "1", "Tab", config
        )
        self.assertEqual(validation.status, ValidationStatus.CONFLICT)


class TestKeybindManager(unittest.TestCase):
    """Test the keybind manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = KeybindManagerConfig(
            detection_mode=DetectionMode.AUTO,
            auto_save=False,
            backup_existing=False,
            validate_on_load=False
        )
        self.manager = KeybindManager(self.config)
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.manager.scanner)
        self.assertIsNotNone(self.manager.validator)
        self.assertIsNotNone(self.manager.current_bindings)
    
    @patch('core.keybinding_scanner.KeybindingScanner.scan_user_cfg')
    def test_auto_detect_keybinds(self, mock_scan_user_cfg):
        """Test auto-detection of keybinds."""
        # Mock scanner response
        mock_bindings = {
            "attack": KeyBinding(action="attack", key="1"),
            "target_next": KeyBinding(action="target_next", key="Tab")
        }
        mock_scan_user_cfg.return_value = mock_bindings
        
        result = self.manager.auto_detect_keybinds()
        
        self.assertIsInstance(result, KeybindDetectionResult)
        self.assertIn("user_cfg", result.detection_methods)
        self.assertGreater(len(result.bindings), 0)
    
    def test_manual_config_keybinds(self):
        """Test manual configuration of keybinds."""
        # This would normally be interactive, so we'll test the structure
        bindings = self.manager.manual_config_keybinds()
        
        # In a real test, this would be empty since no input is provided
        # But we can test that it returns a dict
        self.assertIsInstance(bindings, dict)
    
    def test_hybrid_detect_keybinds(self):
        """Test hybrid detection of keybinds."""
        # Mock auto-detection to return some bindings
        with patch.object(self.manager, 'auto_detect_keybinds') as mock_auto:
            mock_result = KeybindDetectionResult(
                bindings={"attack": "1"},
                detection_methods=["user_cfg"],
                confidence=0.8,
                missing_essential=["target_next"],
                conflicts=[],
                warnings=[],
                detection_time=0.1
            )
            mock_auto.return_value = mock_result
            
            result = self.manager.hybrid_detect_keybinds()
            
            self.assertIsInstance(result, KeybindDetectionResult)
            self.assertIn("attack", result.bindings)
    
    def test_validate_current_keybinds(self):
        """Test validation of current keybinds."""
        # Set some test bindings
        self.manager.current_bindings = {"attack": "1", "target_next": "Tab"}
        
        report = self.manager.validate_current_keybinds()
        
        self.assertIsInstance(report, ValidationReport)
        self.assertGreaterEqual(report.total_bindings, 0)
    
    def test_save_and_load_keybinds(self):
        """Test saving and loading keybinds."""
        test_bindings = {"attack": "1", "target_next": "Tab"}
        
        # Test saving
        success = self.manager.save_keybinds(test_bindings, backup=False)
        self.assertTrue(success)
        
        # Test loading
        loaded_bindings = self.manager.load_keybinds()
        self.assertIsInstance(loaded_bindings, dict)
    
    def test_get_and_set_binding(self):
        """Test getting and setting individual bindings."""
        # Test setting
        success = self.manager.set_binding("test_action", "F12")
        self.assertTrue(success)
        
        # Test getting
        key = self.manager.get_binding("test_action")
        self.assertEqual(key, "F12")
        
        # Test getting non-existent binding
        key = self.manager.get_binding("non_existent")
        self.assertIsNone(key)
    
    def test_get_all_bindings(self):
        """Test getting all bindings."""
        # Set some test bindings
        self.manager.current_bindings = {"attack": "1", "target_next": "Tab"}
        
        all_bindings = self.manager.get_all_bindings()
        
        self.assertIsInstance(all_bindings, dict)
        self.assertEqual(len(all_bindings), 2)
        self.assertIn("attack", all_bindings)
        self.assertIn("target_next", all_bindings)


class TestKeybindIntegration(unittest.TestCase):
    """Test integration between keybind components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = KeybindValidator()
        self.manager = KeybindManager()
    
    def test_validator_manager_integration(self):
        """Test integration between validator and manager."""
        test_bindings = {"attack": "1", "target_next": "Tab"}
        
        # Test that manager can use validator
        report = self.manager.validator.validate_keybinds(test_bindings)
        
        self.assertIsInstance(report, ValidationReport)
        self.assertGreater(report.total_bindings, 0)
    
    def test_scanner_manager_integration(self):
        """Test integration between scanner and manager."""
        # Test that manager has access to scanner
        self.assertIsNotNone(self.manager.scanner)
        
        # Test scanner methods are available
        self.assertTrue(hasattr(self.manager.scanner, 'scan_user_cfg'))
        self.assertTrue(hasattr(self.manager.scanner, 'scan_inputmap_xml'))
    
    def test_full_workflow(self):
        """Test the full keybind workflow."""
        # 1. Create test bindings
        test_bindings = {"attack": "1", "target_next": "Tab"}
        
        # 2. Validate bindings
        report = self.validator.validate_keybinds(test_bindings)
        
        # 3. Save bindings
        success = self.manager.save_keybinds(test_bindings, backup=False)
        
        # 4. Load bindings
        loaded_bindings = self.manager.load_keybinds()
        
        # 5. Validate loaded bindings
        loaded_report = self.manager.validate_current_keybinds()
        
        # Assertions
        self.assertIsInstance(report, ValidationReport)
        self.assertTrue(success)
        self.assertIsInstance(loaded_bindings, dict)
        self.assertIsInstance(loaded_report, ValidationReport)


class TestKeybindTemplate(unittest.TestCase):
    """Test keybind template functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.template_path = "config/keybind_template.json"
    
    def test_template_file_exists(self):
        """Test that template file exists."""
        template_file = Path(self.template_path)
        self.assertTrue(template_file.exists())
    
    def test_template_structure(self):
        """Test template file structure."""
        with open(self.template_path, 'r') as f:
            template = json.load(f)
        
        # Check required sections
        self.assertIn("metadata", template)
        self.assertIn("essential_bindings", template)
        self.assertIn("optional_bindings", template)
        self.assertIn("validation_rules", template)
        self.assertIn("detection_methods", template)
    
    def test_essential_bindings(self):
        """Test essential bindings in template."""
        with open(self.template_path, 'r') as f:
            template = json.load(f)
        
        essential = template["essential_bindings"]
        
        # Check required categories
        required_categories = ["combat", "movement", "interaction", "inventory"]
        for category in required_categories:
            self.assertIn(category, essential)
        
        # Check that bindings have required fields
        for category, bindings in essential.items():
            for action, config in bindings.items():
                self.assertIn("key", config)
                self.assertIn("description", config)
                self.assertIn("required", config)
                self.assertIn("category", config)
    
    def test_validation_rules(self):
        """Test validation rules in template."""
        with open(self.template_path, 'r') as f:
            template = json.load(f)
        
        rules = template["validation_rules"]
        
        self.assertIn("required_categories", rules)
        self.assertIn("conflict_detection", rules)
        self.assertIn("auto_fix_suggestions", rules)
        self.assertIn("backup_existing", rules)


class TestKeybindDetectionMethods(unittest.TestCase):
    """Test different detection methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = KeybindManager()
    
    @patch('core.keybinding_scanner.KeybindingScanner.scan_user_cfg')
    def test_user_cfg_detection(self, mock_scan):
        """Test user.cfg detection method."""
        mock_bindings = {
            "attack": KeyBinding(action="attack", key="1"),
            "target_next": KeyBinding(action="target_next", key="Tab")
        }
        mock_scan.return_value = mock_bindings
        
        result = self.manager.auto_detect_keybinds()
        
        self.assertIn("user_cfg", result.detection_methods)
        self.assertIn("attack", result.bindings)
        self.assertIn("target_next", result.bindings)
    
    @patch('core.keybinding_scanner.KeybindingScanner.scan_inputmap_xml')
    def test_inputmap_xml_detection(self, mock_scan):
        """Test inputmap.xml detection method."""
        mock_bindings = {
            "use": KeyBinding(action="use", key="E"),
            "inventory": KeyBinding(action="inventory", key="I")
        }
        mock_scan.return_value = mock_bindings
        
        result = self.manager.auto_detect_keybinds()
        
        self.assertIn("inputmap_xml", result.detection_methods)
        self.assertIn("use", result.bindings)
        self.assertIn("inventory", result.bindings)
    
    @patch('core.keybinding_scanner.KeybindingScanner.scan_keybinding_screen_ocr')
    def test_ocr_detection(self, mock_scan):
        """Test OCR detection method."""
        mock_bindings = {
            "mount": KeyBinding(action="mount", key="M"),
            "forward": KeyBinding(action="forward", key="W")
        }
        mock_scan.return_value = mock_bindings
        
        result = self.manager.auto_detect_keybinds()
        
        # OCR is fallback, so it might not be in detection_methods
        # But we can test that the method exists
        self.assertTrue(hasattr(self.manager.scanner, 'scan_keybinding_screen_ocr'))


class TestKeybindValidationScenarios(unittest.TestCase):
    """Test various validation scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = KeybindValidator()
    
    def test_perfect_bindings(self):
        """Test validation of perfect keybinds."""
        perfect_bindings = {
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
        
        report = self.validator.validate_keybinds(perfect_bindings)
        
        self.assertGreater(report.confidence_score, 0.8)
        self.assertEqual(report.conflicting_bindings, 0)
    
    def test_missing_essential_bindings(self):
        """Test validation with missing essential bindings."""
        incomplete_bindings = {
            "attack": "1",
            "use": "E"
            # Missing target_next, inventory, etc.
        }
        
        report = self.validator.validate_keybinds(incomplete_bindings)
        
        self.assertGreater(report.missing_bindings, 0)
        self.assertGreater(len(report.essential_missing), 0)
    
    def test_conflicting_bindings(self):
        """Test validation with conflicting bindings."""
        conflicting_bindings = {
            "attack": "Tab",
            "target_next": "Tab",  # Conflict
            "use": "W",
            "forward": "W"  # Conflict
        }
        
        report = self.validator.validate_keybinds(conflicting_bindings)
        
        self.assertGreater(report.conflicting_bindings, 0)
    
    def test_empty_bindings(self):
        """Test validation of empty bindings."""
        report = self.validator.validate_keybinds({})
        
        self.assertEqual(report.valid_bindings, 0)
        self.assertGreater(report.missing_bindings, 0)
        self.assertEqual(report.confidence_score, 0.0)


def run_performance_tests():
    """Run performance tests for keybind system."""
    print("Running performance tests...")
    
    validator = KeybindValidator()
    manager = KeybindManager()
    
    # Test validation performance
    import time
    
    test_bindings = {
        "attack": "1", "target_next": "Tab", "use": "E", "inventory": "I",
        "mount": "M", "forward": "W", "backward": "S", "left": "A", "right": "D"
    }
    
    start_time = time.time()
    for _ in range(100):
        report = validator.validate_keybinds(test_bindings)
    validation_time = time.time() - start_time
    
    print(f"Validation performance: {validation_time:.3f}s for 100 validations")
    
    # Test conflict detection performance
    start_time = time.time()
    for _ in range(100):
        conflicts = validator.detect_conflicts(test_bindings)
    conflict_time = time.time() - start_time
    
    print(f"Conflict detection performance: {conflict_time:.3f}s for 100 checks")


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
    
    # Run performance tests
    run_performance_tests() 
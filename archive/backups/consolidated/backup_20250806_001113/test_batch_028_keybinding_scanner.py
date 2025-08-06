#!/usr/bin/env python3
"""
Test suite for Batch 028 - User Keybinding Scanner & Validation Assistant

This test suite covers:
- Keybinding scanner initialization and configuration
- SWG configuration file scanning (user.cfg, inputmap.xml)
- Essential keybinding validation
- OCR fallback functionality
- Setup mode and interactive features
- Error handling and edge cases
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Tuple
from dataclasses import asdict

# Import the keybinding scanner modules
try:
    from core.keybinding_scanner import (
        KeybindingScanner, KeyBinding, KeybindingValidation,
        BindingType, BindingStatus, get_keybinding_scanner,
        scan_keybindings, validate_keybindings, generate_report, setup_mode
    )
    KEYBINDING_SCANNER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import keybinding scanner modules: {e}")
    KEYBINDING_SCANNER_AVAILABLE = False


class TestKeybindingScanner(unittest.TestCase):
    """Test cases for the keybinding scanner system."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not KEYBINDING_SCANNER_AVAILABLE:
            self.skipTest("Keybinding scanner modules not available")
        
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.user_cfg_path = Path(self.test_dir) / "user.cfg"
        self.inputmap_path = Path(self.test_dir) / "inputmap.xml"
        
        # Create test configuration files
        self._create_test_user_cfg()
        self._create_test_inputmap_xml()
        
        # Initialize scanner with test data
        self.scanner = KeybindingScanner(self.test_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_test_user_cfg(self):
        """Create a test user.cfg file."""
        test_content = """
# SWG User Configuration File
KeyBinding "attack" "F1"
KeyBinding "mount" "M"
KeyBinding "use" "U"
KeyBinding "interact" "I"
KeyBinding "forward" "W"
KeyBinding "backward" "S"
KeyBinding "left" "A"
KeyBinding "right" "D"
KeyBinding "inventory" "B"
KeyBinding "chat" "Enter"
KeyBinding "camera_zoom_in" "MouseWheelUp"
KeyBinding "camera_zoom_out" "MouseWheelDown"
"""
        with open(self.user_cfg_path, 'w') as f:
            f.write(test_content)
    
    def _create_test_inputmap_xml(self):
        """Create a test inputmap.xml file."""
        test_content = """<?xml version="1.0" encoding="UTF-8"?>
<inputmap>
    <binding action="attack" key="f1" />
    <binding action="mount" key="m" />
    <binding action="use" key="u" />
    <binding action="interact" key="i" />
    <binding action="forward" key="w" />
    <binding action="backward" key="s" />
    <binding action="left" key="a" />
    <binding action="right" key="d" />
    <binding action="inventory" key="b" />
    <binding action="chat" key="enter" />
    <binding action="camera_zoom_in" key="mousewheelup" />
    <binding action="camera_zoom_out" key="mousewheeldown" />
</inputmap>
"""
        with open(self.inputmap_path, 'w') as f:
            f.write(test_content)
    
    def test_keybinding_scanner_initialization(self):
        """Test keybinding scanner initialization."""
        self.assertIsNotNone(self.scanner)
        self.assertEqual(self.scanner.swg_path, self.test_dir)
        self.assertIsNotNone(self.scanner.user_cfg_path)
        self.assertIsNotNone(self.scanner.inputmap_path)
        self.assertIsInstance(self.scanner.bindings, dict)
        self.assertIsInstance(self.scanner.essential_bindings, dict)
    
    def test_essential_bindings_definition(self):
        """Test that essential bindings are properly defined."""
        essential_bindings = self.scanner.essential_bindings
        
        # Check that all required bindings are present
        required_bindings = ["attack", "mount", "use", "interact", "forward", 
                           "backward", "left", "right"]
        
        for binding_name in required_bindings:
            self.assertIn(binding_name, essential_bindings)
            self.assertTrue(essential_bindings[binding_name]["required"])
        
        # Check optional bindings
        optional_bindings = ["inventory", "chat"]
        for binding_name in optional_bindings:
            self.assertIn(binding_name, essential_bindings)
            self.assertFalse(essential_bindings[binding_name]["required"])
    
    def test_user_cfg_scanning(self):
        """Test scanning user.cfg file."""
        bindings = self.scanner.scan_user_cfg()
        
        self.assertIsInstance(bindings, dict)
        self.assertGreater(len(bindings), 0)
        
        # Check that expected bindings are found
        expected_bindings = ["attack", "mount", "use", "interact", "forward", 
                           "backward", "left", "right", "inventory", "chat"]
        
        for binding_name in expected_bindings:
            if binding_name in bindings:
                binding = bindings[binding_name]
                self.assertIsInstance(binding, KeyBinding)
                self.assertEqual(binding.action, binding_name)
                self.assertIsNotNone(binding.key)
                self.assertEqual(binding.status, BindingStatus.VALID)
    
    def test_inputmap_xml_scanning(self):
        """Test scanning inputmap.xml file."""
        bindings = self.scanner.scan_inputmap_xml()
        
        self.assertIsInstance(bindings, dict)
        self.assertGreater(len(bindings), 0)
        
        # Check that expected bindings are found
        expected_bindings = ["attack", "mount", "use", "interact", "forward", 
                           "backward", "left", "right", "inventory", "chat"]
        
        for binding_name in expected_bindings:
            if binding_name in bindings:
                binding = bindings[binding_name]
                self.assertIsInstance(binding, KeyBinding)
                self.assertEqual(binding.action, binding_name)
                self.assertIsNotNone(binding.key)
                self.assertEqual(binding.status, BindingStatus.VALID)
    
    def test_binding_classification(self):
        """Test binding action classification."""
        test_cases = [
            ("attack", BindingType.ATTACK),
            ("fire", BindingType.ATTACK),
            ("mount", BindingType.MOUNT),
            ("dismount", BindingType.MOUNT),
            ("use", BindingType.USE),
            ("activate", BindingType.USE),
            ("interact", BindingType.INTERACT),
            ("target", BindingType.INTERACT),
            ("forward", BindingType.MOVEMENT),
            ("backward", BindingType.MOVEMENT),
            ("inventory", BindingType.INVENTORY),
            ("bag", BindingType.INVENTORY),
            ("chat", BindingType.CHAT),
            ("talk", BindingType.CHAT),
            ("camera", BindingType.CAMERA),
            ("look", BindingType.CAMERA),
            ("social", BindingType.SOCIAL),
            ("emote", BindingType.SOCIAL),
            ("unknown_action", BindingType.UNKNOWN)
        ]
        
        for action, expected_type in test_cases:
            binding_type = self.scanner._classify_binding(action)
            self.assertEqual(binding_type, expected_type, 
                           f"Action '{action}' should be classified as {expected_type}")
    
    def test_all_sources_scanning(self):
        """Test scanning all available sources."""
        bindings = self.scanner.scan_all_sources()
        
        self.assertIsInstance(bindings, dict)
        self.assertGreater(len(bindings), 0)
        
        # Check that bindings from both sources are merged
        expected_bindings = ["attack", "mount", "use", "interact", "forward", 
                           "backward", "left", "right", "inventory", "chat"]
        
        found_bindings = 0
        for binding_name in expected_bindings:
            if binding_name in bindings:
                found_bindings += 1
                binding = bindings[binding_name]
                self.assertIsInstance(binding, KeyBinding)
                self.assertEqual(binding.action, binding_name)
        
        self.assertGreater(found_bindings, 0, "Should find at least some bindings")
    
    def test_essential_binding_validation(self):
        """Test validation of essential keybindings."""
        # First scan bindings
        self.scanner.scan_all_sources()
        
        # Then validate
        validation = self.scanner.validate_essential_bindings()
        
        self.assertIsInstance(validation, KeybindingValidation)
        self.assertGreater(validation.total_bindings, 0)
        self.assertGreaterEqual(validation.valid_bindings, 0)
        self.assertGreaterEqual(validation.missing_bindings, 0)
        self.assertGreaterEqual(validation.conflicting_bindings, 0)
        self.assertIsInstance(validation.essential_missing, list)
        self.assertIsInstance(validation.warnings, list)
        self.assertIsInstance(validation.recommendations, list)
    
    def test_binding_conflict_detection(self):
        """Test detection of conflicting keybindings."""
        # Create a scenario with conflicting bindings
        self.scanner.bindings = {
            "attack": KeyBinding("attack", "f1", status=BindingStatus.VALID),
            "mount": KeyBinding("mount", "f1", status=BindingStatus.VALID),  # Conflict
            "use": KeyBinding("use", "u", status=BindingStatus.VALID),
            "interact": KeyBinding("interact", "i", status=BindingStatus.VALID),
            "forward": KeyBinding("forward", "w", status=BindingStatus.VALID),
            "backward": KeyBinding("backward", "s", status=BindingStatus.VALID),
            "left": KeyBinding("left", "a", status=BindingStatus.VALID),
            "right": KeyBinding("right", "d", status=BindingStatus.VALID)
        }
        
        validation = self.scanner.validate_essential_bindings()
        
        self.assertGreater(validation.conflicting_bindings, 0)
        # Check that there's at least one conflict warning
        conflict_warnings = [w for w in validation.warnings if "Key conflict" in w]
        self.assertGreater(len(conflict_warnings), 0)
    
    def test_missing_essential_bindings(self):
        """Test detection of missing essential bindings."""
        # Create a scenario with missing essential bindings
        self.scanner.bindings = {
            "attack": KeyBinding("attack", "f1", status=BindingStatus.VALID),
            # Missing mount, use, interact, etc.
        }
        
        validation = self.scanner.validate_essential_bindings()
        
        self.assertGreater(validation.missing_bindings, 0)
        self.assertGreater(len(validation.essential_missing), 0)
        self.assertIn("Missing essential binding", validation.warnings[0])
    
    def test_binding_report_generation(self):
        """Test generation of comprehensive binding report."""
        # Scan bindings first
        self.scanner.scan_all_sources()
        
        # Generate report
        report = self.scanner.generate_binding_report()
        
        self.assertIsInstance(report, str)
        self.assertIn("SWG Keybinding Report", report)
        self.assertIn("Total bindings found", report)
        self.assertIn("Valid bindings", report)
        self.assertIn("Missing bindings", report)
        self.assertIn("Conflicting bindings", report)
    
    def test_binding_config_save_load(self):
        """Test saving and loading binding configuration."""
        # Scan bindings first
        self.scanner.scan_all_sources()
        
        # Save configuration
        config_path = Path(self.test_dir) / "test_keybindings.json"
        self.scanner.save_binding_config(str(config_path))
        
        # Verify file was created
        self.assertTrue(config_path.exists())
        
        # Load and verify content
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        self.assertIn("scan_time", config_data)
        self.assertIn("swg_path", config_data)
        self.assertIn("bindings", config_data)
        self.assertIsInstance(config_data["bindings"], dict)


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not KEYBINDING_SCANNER_AVAILABLE:
            self.skipTest("Keybinding scanner modules not available")
        
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.user_cfg_path = Path(self.test_dir) / "user.cfg"
        self.inputmap_path = Path(self.test_dir) / "inputmap.xml"
        
        # Create test configuration files
        self._create_test_user_cfg()
        self._create_test_inputmap_xml()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_test_user_cfg(self):
        """Create a test user.cfg file."""
        test_content = """
KeyBinding "attack" "F1"
KeyBinding "mount" "M"
KeyBinding "use" "U"
"""
        with open(self.user_cfg_path, 'w') as f:
            f.write(test_content)
    
    def _create_test_inputmap_xml(self):
        """Create a test inputmap.xml file."""
        test_content = """<?xml version="1.0" encoding="UTF-8"?>
<inputmap>
    <binding action="attack" key="f1" />
    <binding action="mount" key="m" />
    <binding action="use" key="u" />
</inputmap>
"""
        with open(self.inputmap_path, 'w') as f:
            f.write(test_content)
    
    def test_get_keybinding_scanner(self):
        """Test getting the global keybinding scanner instance."""
        scanner = get_keybinding_scanner()
        self.assertIsInstance(scanner, KeybindingScanner)
    
    def test_scan_keybindings(self):
        """Test scanning keybindings using global function."""
        with patch('core.keybinding_scanner.get_keybinding_scanner') as mock_get_scanner:
            mock_scanner = Mock()
            mock_scanner.scan_all_sources.return_value = {
                "attack": KeyBinding("attack", "f1"),
                "mount": KeyBinding("mount", "m")
            }
            mock_get_scanner.return_value = mock_scanner
            
            bindings = scan_keybindings()
            
            self.assertIsInstance(bindings, dict)
            self.assertEqual(len(bindings), 2)
            mock_scanner.scan_all_sources.assert_called_once()
    
    def test_validate_keybindings(self):
        """Test validating keybindings using global function."""
        with patch('core.keybinding_scanner.get_keybinding_scanner') as mock_get_scanner:
            mock_scanner = Mock()
            mock_validation = KeybindingValidation(
                total_bindings=2,
                valid_bindings=2,
                missing_bindings=0,
                conflicting_bindings=0,
                essential_missing=[],
                warnings=[],
                recommendations=[],
                validation_time=datetime.now().timestamp()
            )
            mock_scanner.validate_essential_bindings.return_value = mock_validation
            mock_get_scanner.return_value = mock_scanner
            
            validation = validate_keybindings()
            
            self.assertIsInstance(validation, KeybindingValidation)
            self.assertEqual(validation.total_bindings, 2)
            mock_scanner.validate_essential_bindings.assert_called_once()
    
    def test_generate_report(self):
        """Test generating report using global function."""
        with patch('core.keybinding_scanner.get_keybinding_scanner') as mock_get_scanner:
            mock_scanner = Mock()
            mock_scanner.generate_binding_report.return_value = "Test Report"
            mock_get_scanner.return_value = mock_scanner
            
            report = generate_report()
            
            self.assertEqual(report, "Test Report")
            mock_scanner.generate_binding_report.assert_called_once()


class TestOCRIntegration(unittest.TestCase):
    """Test cases for OCR integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not KEYBINDING_SCANNER_AVAILABLE:
            self.skipTest("Keybinding scanner modules not available")
        
        self.scanner = KeybindingScanner()
    
    @patch('core.keybinding_scanner.get_ocr_engine')
    @patch('core.keybinding_scanner.capture_screen')
    def test_ocr_keybinding_scanning(self, mock_capture_screen, mock_get_ocr_engine):
        """Test OCR-based keybinding scanning."""
        # Mock OCR engine
        mock_ocr_engine = Mock()
        mock_ocr_engine.extract_text.return_value = Mock(
            text="Attack: F1\nMount: M\nUse: U",
            confidence=80.0
        )
        mock_get_ocr_engine.return_value = mock_ocr_engine
        
        # Mock screenshot
        mock_screenshot = Mock()
        mock_capture_screen.return_value = mock_screenshot
        
        # Test OCR scanning
        bindings = self.scanner.scan_keybinding_screen_ocr()
        
        self.assertIsInstance(bindings, dict)
        # Should find some bindings from the mocked OCR text
        self.assertGreater(len(bindings), 0)
        
        # Verify OCR was called
        mock_capture_screen.assert_called_once()
        mock_ocr_engine.extract_text.assert_called()
    
    @patch('core.keybinding_scanner.OCR_AVAILABLE', False)
    def test_ocr_unavailable(self):
        """Test behavior when OCR is not available."""
        bindings = self.scanner.scan_keybinding_screen_ocr()
        
        self.assertIsInstance(bindings, dict)
        self.assertEqual(len(bindings), 0)


class TestSetupMode(unittest.TestCase):
    """Test cases for setup mode functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not KEYBINDING_SCANNER_AVAILABLE:
            self.skipTest("Keybinding scanner modules not available")
        
        self.scanner = KeybindingScanner()
    
    @patch('builtins.input')
    def test_setup_mode_interactive(self, mock_input):
        """Test interactive setup mode."""
        # Mock user input
        mock_input.side_effect = ["f1", "m", "u", "i", "w", "s", "a", "d"]
        
        setup_bindings = self.scanner.setup_mode()
        
        self.assertIsInstance(setup_bindings, dict)
        self.assertGreater(len(setup_bindings), 0)
        
        # Check that essential bindings were configured
        expected_bindings = ["attack", "mount", "use", "interact", "forward", 
                           "backward", "left", "right"]
        
        for binding_name in expected_bindings:
            if binding_name in setup_bindings:
                self.assertIsInstance(setup_bindings[binding_name], str)
    
    @patch('builtins.input')
    def test_setup_mode_skip(self, mock_input):
        """Test setup mode with skipping."""
        # Mock user input with some skips
        mock_input.side_effect = ["f1", "skip", "u", "skip", "w", "s", "a", "d"]
        
        setup_bindings = self.scanner.setup_mode()
        
        self.assertIsInstance(setup_bindings, dict)
        # Should have fewer bindings due to skips
        self.assertLess(len(setup_bindings), 8)
    
    @patch('builtins.input')
    def test_setup_mode_quit(self, mock_input):
        """Test setup mode with early quit."""
        # Mock user input with early quit
        mock_input.side_effect = ["f1", "quit"]
        
        setup_bindings = self.scanner.setup_mode()
        
        self.assertIsInstance(setup_bindings, dict)
        # Should have only one binding due to early quit
        self.assertEqual(len(setup_bindings), 1)


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not KEYBINDING_SCANNER_AVAILABLE:
            self.skipTest("Keybinding scanner modules not available")
    
    def test_missing_swg_path(self):
        """Test behavior with missing SWG installation."""
        scanner = KeybindingScanner("C:/NonExistent/SWG")
        
        self.assertEqual(scanner.swg_path, "")
        self.assertIsNone(scanner.user_cfg_path)
        self.assertIsNone(scanner.inputmap_path)
    
    def test_missing_config_files(self):
        """Test behavior with missing configuration files."""
        scanner = KeybindingScanner()
        
        # Test scanning with missing files
        user_cfg_bindings = scanner.scan_user_cfg()
        inputmap_bindings = scanner.scan_inputmap_xml()
        
        self.assertEqual(len(user_cfg_bindings), 0)
        self.assertEqual(len(inputmap_bindings), 0)
    
    def test_invalid_user_cfg_format(self):
        """Test handling of invalid user.cfg format."""
        # Create temporary directory
        test_dir = tempfile.mkdtemp()
        try:
            # Create invalid user.cfg
            user_cfg_path = Path(test_dir) / "user.cfg"
            with open(user_cfg_path, 'w') as f:
                f.write("Invalid format\nNo KeyBinding lines\n")
            
            scanner = KeybindingScanner(test_dir)
            bindings = scanner.scan_user_cfg()
            
            self.assertEqual(len(bindings), 0)
            
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)
    
    def test_invalid_inputmap_xml_format(self):
        """Test handling of invalid inputmap.xml format."""
        # Create temporary directory
        test_dir = tempfile.mkdtemp()
        try:
            # Create invalid inputmap.xml
            inputmap_path = Path(test_dir) / "inputmap.xml"
            with open(inputmap_path, 'w') as f:
                f.write("Invalid XML format\n")
            
            scanner = KeybindingScanner(test_dir)
            bindings = scanner.scan_inputmap_xml()
            
            self.assertEqual(len(bindings), 0)
            
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    # Run the test suite
    unittest.main(verbosity=2) 
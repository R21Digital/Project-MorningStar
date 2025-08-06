#!/usr/bin/env python3
"""
Test suite for Batch 029 - Game State Requirements & Player Guidelines Enforcement

This test suite covers:
- Preflight validator initialization and configuration
- Window mode validation
- Resolution compatibility checking
- UI element visibility verification
- UI scale compatibility testing
- Game state validation
- Performance assessment
- CLI reporting and error handling
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

# Import the preflight check modules
try:
    from core.validation.preflight_check import (
        PreflightValidator, ValidationCheck, ValidationStatus, CheckType,
        PreflightReport, get_preflight_validator, run_preflight_check,
        generate_cli_report, save_preflight_report, is_system_ready
    )
    PREFLIGHT_CHECK_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import preflight check modules: {e}")
    PREFLIGHT_CHECK_AVAILABLE = False


class TestPreflightValidator(unittest.TestCase):
    """Test cases for the preflight validator system."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not PREFLIGHT_CHECK_AVAILABLE:
            self.skipTest("Preflight check modules not available")
        
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.report_path = Path(self.test_dir) / "test_preflight_report.json"
        
        # Initialize validator
        self.validator = PreflightValidator()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_preflight_validator_initialization(self):
        """Test preflight validator initialization."""
        self.assertIsNotNone(self.validator)
        self.assertIsInstance(self.validator.supported_resolutions, list)
        self.assertIsInstance(self.validator.required_ui_elements, dict)
        self.assertIsInstance(self.validator.checks, list)
        self.assertIsNotNone(self.validator.logger)
    
    def test_supported_resolutions(self):
        """Test that supported resolutions are properly defined."""
        resolutions = self.validator.supported_resolutions
        
        # Check that common resolutions are included
        expected_resolutions = [
            (1920, 1080),  # Full HD
            (1600, 900),   # HD+
            (1366, 768),   # HD
        ]
        
        for resolution in expected_resolutions:
            self.assertIn(resolution, resolutions)
        
        # Check that all resolutions are tuples of 2 integers
        for resolution in resolutions:
            self.assertIsInstance(resolution, tuple)
            self.assertEqual(len(resolution), 2)
            self.assertIsInstance(resolution[0], int)
            self.assertIsInstance(resolution[1], int)
    
    def test_required_ui_elements(self):
        """Test that required UI elements are properly defined."""
        ui_elements = self.validator.required_ui_elements
        
        # Check that essential elements are present
        essential_elements = ["minimap", "quest_journal"]
        optional_elements = ["chat_window", "inventory"]
        
        for element in essential_elements:
            self.assertIn(element, ui_elements)
            self.assertTrue(ui_elements[element]["required"])
        
        for element in optional_elements:
            self.assertIn(element, ui_elements)
            self.assertFalse(ui_elements[element]["required"])
        
        # Check element structure
        for element_name, element_info in ui_elements.items():
            self.assertIn("description", element_info)
            self.assertIn("required", element_info)
            self.assertIn("keywords", element_info)
            self.assertIn("regions", element_info)
            self.assertIsInstance(element_info["keywords"], list)
            self.assertIsInstance(element_info["regions"], list)
    
    def test_window_mode_check(self):
        """Test window mode validation."""
        # Test with mocked windowed mode detection
        with patch.object(self.validator, '_detect_window_mode', return_value=True):
            self.validator._check_window_mode()
            
            # Check that a check was added
            self.assertGreater(len(self.validator.checks), 0)
            
            # Find the window mode check
            window_check = None
            for check in self.validator.checks:
                if check.name == "Window Mode":
                    window_check = check
                    break
            
            self.assertIsNotNone(window_check)
            self.assertEqual(window_check.check_type, CheckType.WINDOW_MODE)
            self.assertEqual(window_check.status, ValidationStatus.PASS)
            self.assertIn("windowed mode", window_check.message.lower())
    
    def test_resolution_check(self):
        """Test resolution validation."""
        # Test with supported resolution
        with patch.object(self.validator, '_get_current_resolution', return_value=(1920, 1080)):
            self.validator._check_resolution()
            
            # Find the resolution check
            resolution_check = None
            for check in self.validator.checks:
                if check.name == "Resolution":
                    resolution_check = check
                    break
            
            self.assertIsNotNone(resolution_check)
            self.assertEqual(resolution_check.check_type, CheckType.RESOLUTION)
            self.assertEqual(resolution_check.status, ValidationStatus.PASS)
            self.assertIn("1920x1080", resolution_check.message)
    
    def test_ui_visibility_check(self):
        """Test UI visibility validation."""
        # Mock OCR availability
        with patch('core.validation.preflight_check.OCR_AVAILABLE', True):
            with patch.object(self.validator, 'ocr_engine') as mock_ocr:
                # Mock OCR result
                mock_result = Mock()
                mock_result.confidence = 80.0
                mock_result.text = "minimap radar"
                mock_ocr.extract_text.return_value = mock_result
                
                # Mock screenshot
                with patch('core.validation.preflight_check.capture_screen') as mock_screenshot:
                    mock_screenshot.return_value = Mock()
                    
                    self.validator._check_ui_visibility()
                    
                    # Check that UI visibility checks were added
                    ui_checks = [c for c in self.validator.checks if c.check_type == CheckType.UI_VISIBILITY]
                    self.assertGreater(len(ui_checks), 0)
    
    def test_ui_scale_check(self):
        """Test UI scale validation."""
        # Test with compatible UI scale
        with patch.object(self.validator, '_detect_ui_scale', return_value=1.0):
            self.validator._check_ui_scale()
            
            # Find the UI scale check
            scale_check = None
            for check in self.validator.checks:
                if check.name == "UI Scale":
                    scale_check = check
                    break
            
            self.assertIsNotNone(scale_check)
            self.assertEqual(scale_check.check_type, CheckType.UI_SCALE)
            self.assertEqual(scale_check.status, ValidationStatus.PASS)
    
    def test_game_state_check(self):
        """Test game state validation."""
        # Test with valid game state
        valid_state = {
            "ready": True,
            "loaded": True,
            "character_logged_in": True,
            "in_game": True
        }
        
        with patch.object(self.validator, '_detect_game_state', return_value=valid_state):
            self.validator._check_game_state()
            
            # Find the game state check
            state_check = None
            for check in self.validator.checks:
                if check.name == "Game State":
                    state_check = check
                    break
            
            self.assertIsNotNone(state_check)
            self.assertEqual(state_check.check_type, CheckType.GAME_STATE)
            self.assertEqual(state_check.status, ValidationStatus.PASS)
    
    def test_performance_check(self):
        """Test performance validation."""
        # Test with adequate performance
        adequate_performance = {
            "adequate": True,
            "fps": 60,
            "memory_usage": 50,
            "reason": None
        }
        
        with patch.object(self.validator, '_get_performance_metrics', return_value=adequate_performance):
            self.validator._check_performance()
            
            # Find the performance check
            perf_check = None
            for check in self.validator.checks:
                if check.name == "Performance":
                    perf_check = check
                    break
            
            self.assertIsNotNone(perf_check)
            self.assertEqual(perf_check.check_type, CheckType.PERFORMANCE)
            self.assertEqual(perf_check.status, ValidationStatus.PASS)
    
    def test_run_all_checks(self):
        """Test running all validation checks."""
        report = self.validator.run_all_checks()
        
        self.assertIsInstance(report, PreflightReport)
        self.assertGreater(report.total_checks, 0)
        self.assertGreaterEqual(report.passed_checks, 0)
        self.assertGreaterEqual(report.failed_checks, 0)
        self.assertGreaterEqual(report.warning_checks, 0)
        self.assertGreaterEqual(report.skipped_checks, 0)
        self.assertIsInstance(report.checks, list)
        self.assertIsInstance(report.critical_failures, list)
        self.assertIsInstance(report.recommendations, list)
    
    def test_report_generation(self):
        """Test report generation logic."""
        # Create a test report
        test_checks = [
            ValidationCheck("Test1", CheckType.WINDOW_MODE, ValidationStatus.PASS, "Passed"),
            ValidationCheck("Test2", CheckType.RESOLUTION, ValidationStatus.FAIL, "Failed", required=True),
            ValidationCheck("Test3", CheckType.UI_VISIBILITY, ValidationStatus.WARNING, "Warning")
        ]
        
        self.validator.checks = test_checks
        report = self.validator._generate_report()
        
        self.assertEqual(report.total_checks, 3)
        self.assertEqual(report.passed_checks, 1)
        self.assertEqual(report.failed_checks, 1)
        self.assertEqual(report.warning_checks, 1)
        self.assertEqual(report.overall_status, ValidationStatus.FAIL)
        self.assertGreater(len(report.critical_failures), 0)


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not PREFLIGHT_CHECK_AVAILABLE:
            self.skipTest("Preflight check modules not available")
    
    def test_get_preflight_validator(self):
        """Test getting the global preflight validator instance."""
        validator = get_preflight_validator()
        self.assertIsInstance(validator, PreflightValidator)
    
    def test_run_preflight_check(self):
        """Test running preflight check using global function."""
        with patch('core.validation.preflight_check.get_preflight_validator') as mock_get_validator:
            mock_validator = Mock()
            mock_report = PreflightReport(
                total_checks=6,
                passed_checks=4,
                failed_checks=1,
                warning_checks=1,
                skipped_checks=0,
                checks=[],
                overall_status=ValidationStatus.WARNING,
                critical_failures=[],
                recommendations=[],
                validation_time=datetime.now().timestamp()
            )
            mock_validator.run_all_checks.return_value = mock_report
            mock_get_validator.return_value = mock_validator
            
            report = run_preflight_check()
            
            self.assertIsInstance(report, PreflightReport)
            self.assertEqual(report.total_checks, 6)
            mock_validator.run_all_checks.assert_called_once()
    
    def test_generate_cli_report(self):
        """Test generating CLI report using global function."""
        with patch('core.validation.preflight_check.get_preflight_validator') as mock_get_validator:
            mock_validator = Mock()
            mock_validator.generate_cli_report.return_value = "Test CLI Report"
            mock_get_validator.return_value = mock_validator
            
            report = generate_cli_report()
            
            self.assertEqual(report, "Test CLI Report")
            mock_validator.generate_cli_report.assert_called_once()
    
    def test_save_preflight_report(self):
        """Test saving preflight report using global function."""
        with patch('core.validation.preflight_check.get_preflight_validator') as mock_get_validator:
            mock_validator = Mock()
            mock_get_validator.return_value = mock_validator
            
            save_preflight_report("test_report.json")
            
            mock_validator.save_report.assert_called_once_with("test_report.json")
    
    def test_is_system_ready(self):
        """Test system readiness check using global function."""
        with patch('core.validation.preflight_check.run_preflight_check') as mock_run_check:
            # Test with ready system
            mock_report = Mock()
            mock_report.overall_status = ValidationStatus.PASS
            mock_run_check.return_value = mock_report
            
            ready = is_system_ready()
            self.assertTrue(ready)
            
            # Test with not ready system
            mock_report.overall_status = ValidationStatus.FAIL
            
            ready = is_system_ready()
            self.assertFalse(ready)


class TestCLIReporting(unittest.TestCase):
    """Test cases for CLI reporting functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not PREFLIGHT_CHECK_AVAILABLE:
            self.skipTest("Preflight check modules not available")
        
        self.validator = PreflightValidator()
    
    def test_cli_report_generation(self):
        """Test CLI report generation."""
        # Create test checks
        test_checks = [
            ValidationCheck("Window Mode", CheckType.WINDOW_MODE, ValidationStatus.PASS, "Game is in windowed mode"),
            ValidationCheck("Resolution", CheckType.RESOLUTION, ValidationStatus.FAIL, "Unsupported resolution", fix_suggestion="Use 1920x1080"),
            ValidationCheck("UI Scale", CheckType.UI_SCALE, ValidationStatus.WARNING, "UI scale may cause issues", fix_suggestion="Set to 1.0")
        ]
        
        self.validator.checks = test_checks
        report = self.validator._generate_report()
        
        cli_report = self.validator.generate_cli_report()
        
        self.assertIsInstance(cli_report, str)
        self.assertIn("MS11 Preflight Check Report", cli_report)
        self.assertIn("Overall Status", cli_report)
        self.assertIn("Window Mode", cli_report)
        self.assertIn("Resolution", cli_report)
        self.assertIn("UI Scale", cli_report)
    
    def test_cli_report_with_failures(self):
        """Test CLI report with critical failures."""
        # Create test checks with failures
        test_checks = [
            ValidationCheck("Window Mode", CheckType.WINDOW_MODE, ValidationStatus.FAIL, "Not in windowed mode", required=True, fix_suggestion="Set to windowed mode"),
            ValidationCheck("Minimap", CheckType.UI_VISIBILITY, ValidationStatus.FAIL, "Minimap not visible", required=True, fix_suggestion="Show minimap")
        ]
        
        self.validator.checks = test_checks
        report = self.validator._generate_report()
        
        cli_report = self.validator.generate_cli_report()
        
        self.assertIn("CRITICAL FAILURES", cli_report)
        self.assertIn("RECOMMENDATIONS", cli_report)
        self.assertIn("RESOLUTION HELP", cli_report)
        self.assertIn("Set to windowed mode", cli_report)
        self.assertIn("Show minimap", cli_report)


class TestReportSaving(unittest.TestCase):
    """Test cases for report saving functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not PREFLIGHT_CHECK_AVAILABLE:
            self.skipTest("Preflight check modules not available")
        
        self.test_dir = tempfile.mkdtemp()
        self.report_path = Path(self.test_dir) / "test_report.json"
        self.validator = PreflightValidator()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_save_report(self):
        """Test saving preflight report to file."""
        # Create test checks
        test_checks = [
            ValidationCheck("Test1", CheckType.WINDOW_MODE, ValidationStatus.PASS, "Passed"),
            ValidationCheck("Test2", CheckType.RESOLUTION, ValidationStatus.FAIL, "Failed", required=True)
        ]
        
        self.validator.checks = test_checks
        report = self.validator._generate_report()
        
        # Save report
        self.validator.save_report(str(self.report_path))
        
        # Verify file was created
        self.assertTrue(self.report_path.exists())
        
        # Load and verify content
        with open(self.report_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn("validation_time", data)
        self.assertIn("overall_status", data)
        self.assertIn("summary", data)
        self.assertIn("checks", data)
        self.assertIn("critical_failures", data)
        self.assertIn("recommendations", data)
        
        self.assertEqual(data["overall_status"], "fail")
        self.assertEqual(data["summary"]["total_checks"], 2)
        self.assertEqual(len(data["checks"]), 2)
    
    def test_save_report_error_handling(self):
        """Test error handling when saving report."""
        # Test with invalid path
        invalid_path = "/invalid/path/report.json"
        
        # Should not raise exception, should log error
        self.validator.save_report(invalid_path)
        
        # Verify file was not created
        self.assertFalse(Path(invalid_path).exists())


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not PREFLIGHT_CHECK_AVAILABLE:
            self.skipTest("Preflight check modules not available")
        
        self.validator = PreflightValidator()
    
    def test_window_mode_detection_error(self):
        """Test error handling in window mode detection."""
        with patch.object(self.validator, '_detect_window_mode', side_effect=Exception("Detection failed")):
            self.validator._check_window_mode()
            
            # Should create a warning check
            window_check = None
            for check in self.validator.checks:
                if check.name == "Window Mode":
                    window_check = check
                    break
            
            self.assertIsNotNone(window_check)
            self.assertEqual(window_check.status, ValidationStatus.WARNING)
            self.assertIn("Could not determine", window_check.message)
    
    def test_resolution_detection_error(self):
        """Test error handling in resolution detection."""
        with patch.object(self.validator, '_get_current_resolution', side_effect=Exception("Detection failed")):
            self.validator._check_resolution()
            
            # Should create a warning check
            resolution_check = None
            for check in self.validator.checks:
                if check.name == "Resolution":
                    resolution_check = check
                    break
            
            self.assertIsNotNone(resolution_check)
            self.assertEqual(resolution_check.status, ValidationStatus.WARNING)
            self.assertIn("Could not determine", resolution_check.message)
    
    def test_ui_visibility_error(self):
        """Test error handling in UI visibility check."""
        with patch('core.validation.preflight_check.OCR_AVAILABLE', True):
            with patch.object(self.validator, 'ocr_engine') as mock_ocr:
                mock_ocr.extract_text.side_effect = Exception("OCR failed")
                
                with patch('core.validation.preflight_check.capture_screen') as mock_screenshot:
                    mock_screenshot.return_value = Mock()
                    
                    self.validator._check_ui_visibility()
                    
                    # Should create a warning check
                    ui_check = None
                    for check in self.validator.checks:
                        if check.check_type == CheckType.UI_VISIBILITY:
                            ui_check = check
                            break
                    
                    self.assertIsNotNone(ui_check)
                    self.assertEqual(ui_check.status, ValidationStatus.WARNING)
                    self.assertIn("Could not check UI visibility", ui_check.message)


if __name__ == "__main__":
    # Run the test suite
    unittest.main(verbosity=2) 
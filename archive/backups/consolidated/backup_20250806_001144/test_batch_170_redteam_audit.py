#!/usr/bin/env python3
"""
Batch 170 - Red-Team Detection Audit & Telemetry Review Tests

This test suite validates the comprehensive red-team audit system including
detection surface checks, safety defaults, variability simulation, and
audit reporting capabilities.
"""

import unittest
import json
import tempfile
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from safety.redteam.audit_runner import (
    RedTeamAuditor, get_redteam_auditor,
    AuditResult, RiskLevel, DetectionSurface,
    DetectionCheck, AuditFinding, AuditReport
)

class TestRedTeamAuditor(unittest.TestCase):
    """Test cases for RedTeamAuditor functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "safety_defaults.json"
        self.report_path = Path(self.temp_dir) / "audit_reports.json"
        
        # Create test configuration
        self.test_config = {
            "audit_settings": {
                "enabled": True,
                "auto_audit_interval": 3600,
                "max_audit_history": 10
            },
            "detection_surfaces": {
                "process_names": {
                    "enabled": True,
                    "suspicious_patterns": ["bot", "auto"],
                    "whitelist": ["swg", "client"]
                },
                "macro_cadence": {
                    "enabled": True,
                    "max_repetition": 3,
                    "min_variance": 0.1
                }
            },
            "safety_defaults": {
                "session_caps": {"enabled": True},
                "humanization": {"enabled": True},
                "anti_patterns": {"enabled": True}
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
        
        # Initialize auditor with test paths
        self.auditor = RedTeamAuditor(
            config_path=str(self.config_path),
            report_path=str(self.report_path)
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test auditor initialization."""
        self.assertIsNotNone(self.auditor)
        self.assertEqual(len(self.auditor.checks), 7)  # 7 detection surfaces
        self.assertTrue(self.auditor.config)
    
    def test_config_loading(self):
        """Test configuration loading."""
        self.assertIn("audit_settings", self.auditor.config)
        self.assertIn("detection_surfaces", self.auditor.config)
        self.assertIn("safety_defaults", self.auditor.config)
    
    def test_check_initialization(self):
        """Test detection check initialization."""
        self.assertIn("process_names", self.auditor.checks)
        self.assertIn("macro_cadence", self.auditor.checks)
        
        process_check = self.auditor.checks["process_names"]
        self.assertEqual(process_check.surface, DetectionSurface.PROCESS_NAMES)
        self.assertEqual(process_check.risk_level, RiskLevel.HIGH)
        self.assertTrue(process_check.enabled)
    
    def test_process_names_check(self):
        """Test process names detection check."""
        with patch('psutil.process_iter') as mock_process_iter:
            # Mock process list with suspicious names
            mock_processes = [
                MagicMock(info={'name': 'bot_manager.exe'}),
                MagicMock(info={'name': 'swg_client.exe'}),
                MagicMock(info={'name': 'auto_macro.exe'})
            ]
            mock_process_iter.return_value = mock_processes
            
            result, details, evidence = self.auditor._check_process_names()
            
            self.assertEqual(result, AuditResult.FAIL)
            self.assertIn("suspicious process names", details.lower())
            self.assertIn("suspicious_processes", evidence)
    
    def test_window_titles_check(self):
        """Test window titles detection check."""
        result, details, evidence = self.auditor._check_window_titles()
        
        # Should pass since we're using test data
        self.assertIn(result, [AuditResult.PASS, AuditResult.FAIL])
        self.assertIn("patterns_checked", evidence)
    
    def test_macro_cadence_check(self):
        """Test macro cadence detection check."""
        result, details, evidence = self.auditor._check_macro_cadence()
        
        # Should detect perfect timing
        self.assertEqual(result, AuditResult.CRITICAL)
        self.assertIn("perfect macro timing", details.lower())
        self.assertIn("variance", evidence)
    
    def test_session_length_check(self):
        """Test session length detection check."""
        result, details, evidence = self.auditor._check_session_length()
        
        # Should detect identical sessions
        self.assertEqual(result, AuditResult.FAIL)
        self.assertIn("identical session lengths", details.lower())
        self.assertIn("sessions", evidence)
    
    def test_input_timing_check(self):
        """Test input timing detection check."""
        result, details, evidence = self.auditor._check_input_timing()
        
        # Should detect perfect timing
        self.assertEqual(result, AuditResult.CRITICAL)
        self.assertIn("perfect input timing", details.lower())
        self.assertIn("delays", evidence)
    
    def test_repeat_routes_check(self):
        """Test repeat routes detection check."""
        result, details, evidence = self.auditor._check_repeat_routes()
        
        # Should detect repeated routes
        self.assertEqual(result, AuditResult.FAIL)
        self.assertIn("routes repeated", details.lower())
        self.assertIn("routes", evidence)
    
    def test_behavior_patterns_check(self):
        """Test behavior patterns detection check."""
        result, details, evidence = self.auditor._check_behavior_patterns()
        
        # Should detect dominant behaviors
        self.assertEqual(result, AuditResult.WARNING)
        self.assertIn("dominant behavior", details.lower())
        self.assertIn("behaviors", evidence)
    
    def test_variance_calculation(self):
        """Test variance calculation."""
        values = [1.0, 1.0, 1.0, 1.0, 1.0]  # Perfect timing
        variance = self.auditor._calculate_variance(values)
        self.assertEqual(variance, 0.0)
        
        values = [1.0, 2.0, 3.0, 4.0, 5.0]  # High variance
        variance = self.auditor._calculate_variance(values)
        self.assertGreater(variance, 0.0)
    
    def test_confidence_score_calculation(self):
        """Test confidence score calculation."""
        # Test pass result
        confidence = self.auditor._calculate_confidence_score(
            AuditResult.PASS, {"test": "data"}
        )
        self.assertGreater(confidence, 0.7)
        
        # Test fail result with error
        confidence = self.auditor._calculate_confidence_score(
            AuditResult.FAIL, {"error": "test error"}
        )
        self.assertLess(confidence, 0.8)
    
    def test_safety_defaults_check(self):
        """Test safety defaults checking."""
        status = self.auditor._check_safety_defaults()
        
        self.assertIn("session_caps_enabled", status)
        self.assertIn("humanization_enabled", status)
        self.assertIn("anti_patterns_enabled", status)
        
        # Should be True based on test config
        self.assertTrue(status["session_caps_enabled"])
        self.assertTrue(status["humanization_enabled"])
        self.assertTrue(status["anti_patterns_enabled"])
    
    def test_variability_simulation(self):
        """Test variability simulation."""
        variability = self.auditor._simulate_variability()
        
        self.assertIn("timing_variations", variability)
        self.assertIn("behavior_variations", variability)
        self.assertIn("session_variations", variability)
        self.assertIn("variability_score", variability)
        
        # Check timing variations
        timing = variability["timing_variations"]
        self.assertIn("action_delays", timing)
        self.assertIn("idle_delays", timing)
        self.assertIn("response_times", timing)
        
        # Check behavior variations
        behavior = variability["behavior_variations"]
        self.assertIn("emotes", behavior)
        self.assertIn("idle_actions", behavior)
        self.assertIn("travel_modes", behavior)
        
        # Check session variations
        session = variability["session_variations"]
        self.assertIn("session_lengths", session)
        self.assertIn("break_durations", session)
        self.assertIn("login_times", session)
        
        # Check variability score
        self.assertGreater(variability["variability_score"], 0.5)
        self.assertLess(variability["variability_score"], 1.0)

class TestAuditReporting(unittest.TestCase):
    """Test cases for audit reporting functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.auditor = RedTeamAuditor(
            config_path=str(Path(self.temp_dir) / "test_config.json"),
            report_path=str(Path(self.temp_dir) / "test_reports.json")
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_full_audit_run(self):
        """Test complete audit run."""
        report = self.auditor.run_full_audit()
        
        self.assertIsInstance(report, AuditReport)
        self.assertIsNotNone(report.audit_id)
        self.assertIsInstance(report.timestamp, datetime)
        self.assertGreater(report.total_checks, 0)
        self.assertIsInstance(report.overall_risk_level, RiskLevel)
        self.assertIsInstance(report.findings, list)
        self.assertIsInstance(report.recommendations, list)
    
    def test_audit_finding_creation(self):
        """Test audit finding creation."""
        check = DetectionCheck(
            surface=DetectionSurface.PROCESS_NAMES,
            name="Test Check",
            description="Test description",
            risk_level=RiskLevel.HIGH,
            enabled=True,
            check_function="test_check",
            remediation_steps=["Step 1", "Step 2"],
            default_status=AuditResult.PASS
        )
        
        finding = self.auditor._run_check(check)
        
        self.assertIsInstance(finding, AuditFinding)
        self.assertEqual(finding.check_name, "Test Check")
        self.assertEqual(finding.surface, DetectionSurface.PROCESS_NAMES)
        self.assertIn(finding.result, [AuditResult.PASS, AuditResult.FAIL])
        self.assertIsInstance(finding.timestamp, datetime)
        self.assertIsInstance(finding.remediation_steps, list)
        self.assertIsInstance(finding.confidence_score, float)
    
    def test_recommendation_generation(self):
        """Test recommendation generation."""
        # Create test findings
        findings = [
            AuditFinding(
                check_name="Critical Test",
                surface=DetectionSurface.MACRO_CADENCE,
                result=AuditResult.CRITICAL,
                risk_level=RiskLevel.CRITICAL,
                details="Critical issue found",
                timestamp=datetime.now(),
                remediation_steps=["Fix critical issue"],
                confidence_score=0.9,
                evidence={}
            ),
            AuditFinding(
                check_name="Failed Test",
                surface=DetectionSurface.PROCESS_NAMES,
                result=AuditResult.FAIL,
                risk_level=RiskLevel.HIGH,
                details="Failed issue found",
                timestamp=datetime.now(),
                remediation_steps=["Fix failed issue"],
                confidence_score=0.8,
                evidence={}
            )
        ]
        
        recommendations = self.auditor._generate_recommendations(findings)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Should have critical recommendation
        critical_recs = [r for r in recommendations if "CRITICAL" in r]
        self.assertGreater(len(critical_recs), 0)
    
    def test_report_export(self):
        """Test report export functionality."""
        # Create test report
        report = AuditReport(
            audit_id="test_audit_123",
            timestamp=datetime.now(),
            total_checks=5,
            passed_checks=3,
            failed_checks=1,
            warning_checks=1,
            critical_checks=0,
            overall_risk_level=RiskLevel.MEDIUM,
            findings=[],
            recommendations=["Test recommendation"],
            safety_defaults_status={"test": True},
            variability_simulation={"test": "data"}
        )
        
        # Test JSON export
        json_report = self.auditor.export_report(report, "json")
        self.assertIsInstance(json_report, str)
        self.assertIn("test_audit_123", json_report)
        
        # Test text export
        text_report = self.auditor.export_report(report, "text")
        self.assertIsInstance(text_report, str)
        self.assertIn("RED-TEAM DETECTION AUDIT REPORT", text_report)
        self.assertIn("test_audit_123", text_report)
    
    def test_audit_summary(self):
        """Test audit summary generation."""
        # Run multiple audits to build history
        for i in range(3):
            self.auditor.run_full_audit()
        
        summary = self.auditor.get_audit_summary()
        
        if "message" not in summary:
            self.assertIn("total_audits", summary)
            self.assertIn("recent_audits", summary)
            self.assertIn("average_pass_rate", summary)
            self.assertIn("critical_findings", summary)
            
            self.assertEqual(summary["total_audits"], 3)
            self.assertGreater(summary["recent_audits"], 0)

class TestSafetyDefaults(unittest.TestCase):
    """Test cases for safety defaults functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "safety_defaults.json"
        
        # Create comprehensive test config
        self.test_config = {
            "safety_defaults": {
                "version": "1.0.0",
                "enforcement_level": "strict"
            },
            "session_management": {
                "session_caps": {
                    "enabled": True,
                    "max_daily_hours": 8,
                    "max_session_hours": 6,
                    "mandatory_breaks": True
                }
            },
            "humanization": {
                "enabled": True,
                "random_delays": {
                    "enabled": True,
                    "min_delay_ms": 50,
                    "max_delay_ms": 2000
                },
                "emote_system": {
                    "enabled": True,
                    "emote_frequency": {
                        "min_per_hour": 1,
                        "max_per_hour": 5
                    }
                }
            },
            "anti_patterns": {
                "enabled": True,
                "repetitive_actions": {
                    "enabled": True,
                    "max_consecutive_identical": 3
                },
                "perfect_timing": {
                    "enabled": True,
                    "max_identical_timing": 2
                }
            },
            "enforcement": {
                "enabled": True,
                "strict_mode": {
                    "enabled": True,
                    "block_unsafe_operations": True
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
        
        self.auditor = RedTeamAuditor(config_path=str(self.config_path))
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_safety_defaults_validation(self):
        """Test safety defaults validation."""
        status = self.auditor._check_safety_defaults()
        
        # All critical settings should be enabled
        self.assertTrue(status["session_caps_enabled"])
        self.assertTrue(status["humanization_enabled"])
        self.assertTrue(status["anti_patterns_enabled"])
        self.assertTrue(status["random_delays_enabled"])
        self.assertTrue(status["emote_system_enabled"])
        self.assertTrue(status["mandatory_breaks_enabled"])
    
    def test_configuration_structure(self):
        """Test configuration structure validation."""
        config = self.auditor.config
        
        # Check required sections
        required_sections = [
            "session_management",
            "humanization",
            "anti_patterns",
            "enforcement"
        ]
        
        for section in required_sections:
            self.assertIn(section, config)
    
    def test_enforcement_settings(self):
        """Test enforcement settings validation."""
        enforcement = self.auditor.config.get("enforcement", {})
        
        self.assertTrue(enforcement.get("enabled", False))
        
        strict_mode = enforcement.get("strict_mode", {})
        self.assertTrue(strict_mode.get("enabled", False))
        self.assertTrue(strict_mode.get("block_unsafe_operations", False))

class TestDetectionSurfaces(unittest.TestCase):
    """Test cases for detection surface functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.auditor = RedTeamAuditor(
            config_path=str(Path(self.temp_dir) / "test_config.json"),
            report_path=str(Path(self.temp_dir) / "test_reports.json")
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_detection_surface_coverage(self):
        """Test that all detection surfaces are covered."""
        surfaces = [
            DetectionSurface.PROCESS_NAMES,
            DetectionSurface.WINDOW_TITLES,
            DetectionSurface.MACRO_CADENCE,
            DetectionSurface.SESSION_LENGTH,
            DetectionSurface.INPUT_TIMING,
            DetectionSurface.REPEAT_ROUTES,
            DetectionSurface.BEHAVIOR_PATTERNS
        ]
        
        for surface in surfaces:
            # Find corresponding check
            check_found = False
            for check in self.auditor.checks.values():
                if check.surface == surface:
                    check_found = True
                    break
            
            self.assertTrue(check_found, f"No check found for surface: {surface}")
    
    def test_risk_level_assignment(self):
        """Test that risk levels are properly assigned."""
        critical_surfaces = [
            DetectionSurface.MACRO_CADENCE,
            DetectionSurface.INPUT_TIMING
        ]
        
        for surface in critical_surfaces:
            for check in self.auditor.checks.values():
                if check.surface == surface:
                    self.assertEqual(check.risk_level, RiskLevel.CRITICAL)
                    break
    
    def test_remediation_steps(self):
        """Test that remediation steps are provided."""
        for check in self.auditor.checks.values():
            self.assertIsInstance(check.remediation_steps, list)
            self.assertGreater(len(check.remediation_steps), 0)
            
            for step in check.remediation_steps:
                self.assertIsInstance(step, str)
                self.assertGreater(len(step), 0)

class TestIntegration(unittest.TestCase):
    """Integration tests for red-team audit system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.auditor = RedTeamAuditor(
            config_path=str(Path(self.temp_dir) / "test_config.json"),
            report_path=str(Path(self.temp_dir) / "test_reports.json")
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_audit(self):
        """Test complete end-to-end audit process."""
        # Run full audit
        report = self.auditor.run_full_audit()
        
        # Validate report structure
        self.assertIsInstance(report, AuditReport)
        self.assertGreater(report.total_checks, 0)
        self.assertIsInstance(report.findings, list)
        self.assertIsInstance(report.recommendations, list)
        
        # Validate findings
        for finding in report.findings:
            self.assertIsInstance(finding, AuditFinding)
            self.assertIsInstance(finding.check_name, str)
            self.assertIsInstance(finding.result, AuditResult)
            self.assertIsInstance(finding.risk_level, RiskLevel)
            self.assertIsInstance(finding.timestamp, datetime)
            self.assertIsInstance(finding.remediation_steps, list)
            self.assertIsInstance(finding.confidence_score, float)
        
        # Validate recommendations
        self.assertIsInstance(report.recommendations, list)
        
        # Validate safety defaults
        self.assertIsInstance(report.safety_defaults_status, dict)
        
        # Validate variability simulation
        self.assertIsInstance(report.variability_simulation, dict)
        self.assertIn("variability_score", report.variability_simulation)
    
    def test_audit_history_persistence(self):
        """Test audit history persistence."""
        # Run multiple audits
        reports = []
        for i in range(3):
            report = self.auditor.run_full_audit()
            reports.append(report)
        
        # Check history
        summary = self.auditor.get_audit_summary()
        
        if "message" not in summary:
            self.assertEqual(summary["total_audits"], 3)
            self.assertGreater(summary["recent_audits"], 0)
    
    def test_configuration_integration(self):
        """Test configuration integration."""
        # Test with different config scenarios
        configs = [
            {"safety_defaults": {"session_caps": {"enabled": True}}},
            {"safety_defaults": {"session_caps": {"enabled": False}}},
            {"safety_defaults": {"humanization": {"enabled": True}}}
        ]
        
        for config in configs:
            # Create temporary config file
            config_path = Path(self.temp_dir) / f"test_config_{hash(str(config))}.json"
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            # Test auditor with this config
            test_auditor = RedTeamAuditor(config_path=str(config_path))
            status = test_auditor._check_safety_defaults()
            
            self.assertIsInstance(status, dict)
            self.assertIn("session_caps_enabled", status)

def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestRedTeamAuditor,
        TestAuditReporting,
        TestSafetyDefaults,
        TestDetectionSurfaces,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Results Summary")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 
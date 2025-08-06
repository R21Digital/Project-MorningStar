"""Test suite for Batch 071 - Stat Optimizer Module.

This test suite validates all components of the stat optimizer module including:
- Google Sheets integration and data import
- Stat analysis and optimization recommendations
- Alert management and Discord integration
- Error handling and edge cases
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

from modules.stat_optimizer import (
    StatOptimizer, create_stat_optimizer,
    GoogleSheetsImporter, create_sheets_importer,
    StatAnalyzer, create_stat_analyzer,
    AlertManager, create_alert_manager
)


class TestGoogleSheetsImporter(unittest.TestCase):
    """Test Google Sheets importer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "google_api_key": "test_api_key",
            "sheet_id": "test_sheet_id",
            "cache_dir": "test_cache"
        }
        self.importer = create_sheets_importer(self.config)
    
    def test_initialization(self):
        """Test importer initialization."""
        self.assertIsNotNone(self.importer)
        self.assertEqual(self.importer.api_key, "test_api_key")
        self.assertEqual(self.importer.sheet_id, "test_sheet_id")
    
    def test_default_thresholds_structure(self):
        """Test default thresholds structure."""
        thresholds = self.importer.default_thresholds
        
        # Check optimization types
        self.assertIn("pve_damage", thresholds)
        self.assertIn("buff_stack", thresholds)
        self.assertIn("healing", thresholds)
        
        # Check stat structure for each type
        for opt_type, stats in thresholds.items():
            self.assertIsInstance(stats, dict)
            for stat_name, values in stats.items():
                self.assertIn("min", values)
                self.assertIn("optimal", values)
                self.assertIn("max", values)
    
    @patch('modules.stat_optimizer.sheets_importer.requests.get')
    def test_validate_sheet_connection_success(self, mock_get):
        """Test successful Google Sheets connection validation."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.importer.validate_sheet_connection()
        self.assertTrue(result)
    
    @patch('modules.stat_optimizer.sheets_importer.requests.get')
    def test_validate_sheet_connection_failure(self, mock_get):
        """Test failed Google Sheets connection validation."""
        mock_get.side_effect = Exception("Connection failed")
        
        result = self.importer.validate_sheet_connection()
        self.assertFalse(result)
    
    def test_import_stat_thresholds_no_credentials(self):
        """Test importing thresholds without credentials."""
        importer = create_sheets_importer({})  # No config
        thresholds = importer.import_stat_thresholds()
        
        self.assertIsInstance(thresholds, dict)
        self.assertIn("pve_damage", thresholds)
        self.assertIn("buff_stack", thresholds)
        self.assertIn("healing", thresholds)
    
    def test_parse_sheet_data(self):
        """Test parsing sheet data."""
        sample_data = [
            ["pve damage"],
            ["stat", "min", "optimal", "max"],
            ["strength", "100", "150", "200"],
            ["agility", "80", "120", "160"],
            ["buff stack"],
            ["stat", "min", "optimal", "max"],
            ["strength", "120", "170", "220"],
            ["healing"],
            ["stat", "min", "optimal", "max"],
            ["mind", "120", "160", "200"]
        ]
        
        result = self.importer._parse_sheet_data(sample_data)
        
        self.assertIn("pve_damage", result)
        self.assertIn("buff_stack", result)
        self.assertIn("healing", result)
        
        # Check parsed values
        self.assertEqual(result["pve_damage"]["strength"]["min"], 100)
        self.assertEqual(result["pve_damage"]["strength"]["optimal"], 150)
        self.assertEqual(result["pve_damage"]["strength"]["max"], 200)
    
    def test_get_optimization_targets(self):
        """Test getting optimization targets for specific type."""
        targets = self.importer.get_optimization_targets("pve_damage")
        
        self.assertIsInstance(targets, dict)
        self.assertIn("strength", targets)
        self.assertIn("agility", targets)


class TestStatAnalyzer(unittest.TestCase):
    """Test stat analyzer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = create_stat_analyzer()
        self.sample_stats = {
            "strength": 120,
            "agility": 140,
            "constitution": 110,
            "stamina": 90,
            "mind": 70,
            "focus": 80,
            "willpower": 60
        }
        self.sample_thresholds = {
            "strength": {"min": 100, "optimal": 150, "max": 200},
            "agility": {"min": 80, "optimal": 120, "max": 160},
            "constitution": {"min": 90, "optimal": 130, "max": 180}
        }
    
    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertIn("pve_damage", self.analyzer.optimization_weights)
        self.assertIn("buff_stack", self.analyzer.optimization_weights)
        self.assertIn("healing", self.analyzer.optimization_weights)
    
    def test_analyze_character_stats(self):
        """Test character stats analysis."""
        analysis = self.analyzer.analyze_character_stats(
            self.sample_stats, "pve_damage", self.sample_thresholds
        )
        
        self.assertIn("timestamp", analysis)
        self.assertEqual(analysis["optimization_type"], "pve_damage")
        self.assertIn("analysis", analysis)
        self.assertIn("recommendations", analysis)
        self.assertIn("score", analysis)
        self.assertIn("issues", analysis)
        self.assertIn("warnings", analysis)
    
    def test_analyze_single_stat(self):
        """Test single stat analysis."""
        stat_analysis = self.analyzer._analyze_single_stat(
            "strength", 120, {"min": 100, "optimal": 150, "max": 200}, "pve_damage"
        )
        
        self.assertEqual(stat_analysis["current_value"], 120)
        self.assertEqual(stat_analysis["min_threshold"], 100)
        self.assertEqual(stat_analysis["optimal_value"], 150)
        self.assertEqual(stat_analysis["max_threshold"], 200)
        self.assertIn("status", stat_analysis)
        self.assertIn("message", stat_analysis)
        self.assertIn("score", stat_analysis)
    
    def test_analyze_with_defaults(self):
        """Test analysis using default thresholds."""
        analysis = self.analyzer._analyze_with_defaults(self.sample_stats, "pve_damage")
        
        self.assertIn("timestamp", analysis)
        self.assertEqual(analysis["optimization_type"], "pve_damage")
        self.assertIn("analysis", analysis)
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        analysis = {
            "score": 65.0,
            "optimization_type": "pve_damage",
            "analysis": {
                "strength": {"status": "warning", "message": "Below optimal"},
                "agility": {"status": "optimal", "message": "Good"}
            },
            "issues": [],
            "warnings": ["strength: Below optimal"]
        }
        
        recommendations = self.analyzer._generate_recommendations(analysis)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
    
    def test_get_analysis_summary(self):
        """Test analysis summary generation."""
        analysis = {
            "optimization_type": "pve_damage",
            "score": 75.0,
            "issues": ["strength: Below minimum"],
            "warnings": ["agility: Below optimal"],
            "recommendations": ["Increase strength", "Improve agility"],
            "timestamp": "2023-01-01T00:00:00"
        }
        
        summary = self.analyzer.get_analysis_summary(analysis)
        
        self.assertEqual(summary["optimization_type"], "pve_damage")
        self.assertEqual(summary["overall_score"], 75.0)
        self.assertEqual(summary["critical_issues"], 1)
        self.assertEqual(summary["warnings"], 1)
        self.assertEqual(summary["recommendations_count"], 2)


class TestAlertManager(unittest.TestCase):
    """Test alert manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "critical_threshold": 50.0,
            "warning_threshold": 70.0,
            "cli_alerts": True,
            "alert_log_file": "test_alerts.json"
        }
        self.alert_manager = create_alert_manager(self.config)
        self.sample_analysis = {
            "score": 45.0,
            "issues": ["strength: Below minimum threshold"],
            "warnings": ["agility: Below optimal range"],
            "recommendations": ["Critical: Major stat reallocation needed"],
            "optimization_type": "pve_damage"
        }
    
    def test_initialization(self):
        """Test alert manager initialization."""
        self.assertIsNotNone(self.alert_manager)
        self.assertEqual(self.alert_manager.critical_score_threshold, 50.0)
        self.assertEqual(self.alert_manager.warning_score_threshold, 70.0)
        self.assertTrue(self.alert_manager.cli_alerts_enabled)
    
    def test_check_and_alert_critical(self):
        """Test alert checking for critical issues."""
        # Mock Discord notifier
        self.alert_manager.discord_notifier = Mock()
        self.alert_manager.discord_notifier.send_simple_alert.return_value = True
        
        # Test with critical score
        analysis = {"score": 35.0, "issues": ["test"], "warnings": [], "recommendations": []}
        result = self.alert_manager.check_and_alert(analysis, "TestCharacter")
        
        self.assertTrue(result)
    
    def test_check_and_alert_warning(self):
        """Test alert checking for warnings."""
        # Mock Discord notifier
        self.alert_manager.discord_notifier = Mock()
        self.alert_manager.discord_notifier.send_simple_alert.return_value = True
        
        # Test with warning score
        analysis = {"score": 65.0, "issues": [], "warnings": ["test"], "recommendations": []}
        result = self.alert_manager.check_and_alert(analysis, "TestCharacter")
        
        self.assertTrue(result)
    
    def test_check_and_alert_good(self):
        """Test alert checking for good scores."""
        # Test with good score
        analysis = {"score": 85.0, "issues": [], "warnings": [], "recommendations": []}
        result = self.alert_manager.check_and_alert(analysis, "TestCharacter")
        
        self.assertFalse(result)
    
    def test_format_discord_message(self):
        """Test Discord message formatting."""
        message = self.alert_manager._format_discord_message(self.sample_analysis, "TestCharacter")
        
        self.assertIn("TestCharacter", message)
        self.assertIn("Pve Damage", message)  # Title case conversion
        self.assertIn("45.0", message)
        self.assertIn("Critical Issues", message)
    
    def test_send_cli_alert(self):
        """Test CLI alert sending."""
        result = self.alert_manager._send_cli_alert(self.sample_analysis, "TestCharacter", "critical")
        
        self.assertTrue(result)
    
    def test_get_alert_summary(self):
        """Test alert summary generation."""
        summary = self.alert_manager.get_alert_summary(7)
        
        self.assertIn("total_alerts", summary)
        self.assertIn("critical_alerts", summary)
        self.assertIn("warning_alerts", summary)
        self.assertIn("days_analyzed", summary)
    
    def test_test_discord_connection(self):
        """Test Discord connection testing."""
        # Mock Discord notifier
        self.alert_manager.discord_notifier = Mock()
        self.alert_manager.discord_notifier.test_connection.return_value = True
        
        result = self.alert_manager.test_discord_connection()
        self.assertTrue(result)


class TestStatOptimizer(unittest.TestCase):
    """Test main stat optimizer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "sheets_config": {"cache_dir": "test_cache"},
            "analyzer_config": {},
            "alert_config": {"cli_alerts": True}
        }
        self.optimizer = create_stat_optimizer(self.config)
        self.sample_stats = {
            "strength": 120,
            "agility": 140,
            "constitution": 110,
            "stamina": 90,
            "mind": 70,
            "focus": 80,
            "willpower": 60
        }
    
    def test_initialization(self):
        """Test optimizer initialization."""
        self.assertIsNotNone(self.optimizer)
        self.assertIsNotNone(self.optimizer.sheets_importer)
        self.assertIsNotNone(self.optimizer.stat_analyzer)
        self.assertIsNotNone(self.optimizer.alert_manager)
    
    def test_optimize_character_stats(self):
        """Test character stats optimization."""
        result = self.optimizer.optimize_character_stats(
            self.sample_stats, "TestCharacter", "pve_damage"
        )
        
        self.assertIn("timestamp", result)
        self.assertEqual(result["character_name"], "TestCharacter")
        self.assertEqual(result["optimization_type"], "pve_damage")
        self.assertIn("analysis", result)
        self.assertIn("alerts_sent", result)
        self.assertIn("recommendations", result)
        self.assertIn("overall_score", result)
    
    def test_analyze_all_optimization_types(self):
        """Test analysis for all optimization types."""
        result = self.optimizer.analyze_all_optimization_types(self.sample_stats, "TestCharacter")
        
        self.assertEqual(result["character_name"], "TestCharacter")
        self.assertIn("optimization_results", result)
        self.assertIn("best_optimization", result)
        
        # Check all optimization types are present
        optimization_results = result["optimization_results"]
        self.assertIn("pve_damage", optimization_results)
        self.assertIn("buff_stack", optimization_results)
        self.assertIn("healing", optimization_results)
    
    def test_find_best_optimization(self):
        """Test finding best optimization type."""
        results = {
            "pve_damage": {"overall_score": 75.0},
            "buff_stack": {"overall_score": 85.0},
            "healing": {"overall_score": 65.0}
        }
        
        best_type = self.optimizer._find_best_optimization(results)
        self.assertEqual(best_type, "buff_stack")
    
    def test_get_optimization_summary(self):
        """Test optimization summary generation."""
        # Add some test history
        self.optimizer.optimization_history = [
            {"character_name": "TestCharacter", "overall_score": 75.0, "optimization_type": "pve_damage"},
            {"character_name": "TestCharacter", "overall_score": 85.0, "optimization_type": "buff_stack"}
        ]
        
        summary = self.optimizer.get_optimization_summary("TestCharacter")
        
        self.assertEqual(summary["total_optimizations"], 2)
        self.assertEqual(summary["average_score"], 80.0)
        self.assertIn("optimization_type_counts", summary)
    
    def test_validate_connections(self):
        """Test connection validation."""
        # Mock the validation methods
        self.optimizer.sheets_importer.validate_sheet_connection = Mock(return_value=True)
        self.optimizer.alert_manager.test_discord_connection = Mock(return_value=False)
        
        sheets_connected = self.optimizer.validate_google_sheets_connection()
        discord_connected = self.optimizer.validate_discord_connection()
        
        self.assertTrue(sheets_connected)
        self.assertFalse(discord_connected)
    
    def test_export_optimization_report(self):
        """Test optimization report export."""
        # Add some test history
        self.optimizer.optimization_history = [
            {"character_name": "TestCharacter", "overall_score": 75.0}
        ]
        
        report_path = self.optimizer.export_optimization_report("TestCharacter")
        
        self.assertIsInstance(report_path, str)
        self.assertTrue(Path(report_path).exists())
        
        # Clean up
        Path(report_path).unlink(missing_ok=True)
    
    def test_character_stats_cache(self):
        """Test character stats cache functionality."""
        # Test getting empty cache
        cache = self.optimizer.get_character_stats_cache()
        self.assertEqual(cache, {})
        
        # Test getting specific character cache
        cache = self.optimizer.get_character_stats_cache("TestCharacter")
        self.assertEqual(cache, {})
        
        # Test clearing cache
        self.optimizer.clear_cache()
        cache = self.optimizer.get_character_stats_cache()
        self.assertEqual(cache, {})


class TestIntegration(unittest.TestCase):
    """Integration tests for the stat optimizer module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.optimizer = create_stat_optimizer()
        self.sample_stats = {
            "strength": 120,
            "agility": 140,
            "constitution": 110,
            "stamina": 90,
            "mind": 70,
            "focus": 80,
            "willpower": 60
        }
    
    def test_end_to_end_optimization(self):
        """Test end-to-end optimization workflow."""
        result = self.optimizer.optimize_character_stats(
            self.sample_stats, "IntegrationTest", "pve_damage", send_alerts=False
        )
        
        # Verify result structure
        self.assertIn("timestamp", result)
        self.assertEqual(result["character_name"], "IntegrationTest")
        self.assertEqual(result["optimization_type"], "pve_damage")
        self.assertIn("analysis", result)
        self.assertIn("overall_score", result)
        
        # Verify analysis structure
        analysis = result["analysis"]
        self.assertIn("score", analysis)
        self.assertIn("recommendations", analysis)
        self.assertIn("issues", analysis)
        self.assertIn("warnings", analysis)
    
    def test_error_handling(self):
        """Test error handling in optimization."""
        # Test with invalid stats
        invalid_stats = {"strength": "invalid"}
        
        result = self.optimizer.optimize_character_stats(
            invalid_stats, "ErrorTest", "pve_damage"
        )
        
        # Should handle gracefully and still return a result
        self.assertIn("timestamp", result)
        self.assertEqual(result["character_name"], "ErrorTest")
    
    def test_component_integration(self):
        """Test integration between components."""
        # Test sheets importer
        thresholds = self.optimizer.sheets_importer.import_stat_thresholds()
        self.assertIsInstance(thresholds, dict)
        
        # Test stat analyzer
        analysis = self.optimizer.stat_analyzer.analyze_character_stats(
            self.sample_stats, "pve_damage", thresholds.get("pve_damage", {})
        )
        self.assertIn("score", analysis)
        
        # Test alert manager
        alerts_sent = self.optimizer.alert_manager.check_and_alert(analysis, "TestCharacter")
        self.assertIsInstance(alerts_sent, bool)


def run_tests():
    """Run all tests and print summary."""
    print("=== Running Batch 071 Stat Optimizer Tests ===")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGoogleSheetsImporter))
    suite.addTests(loader.loadTestsFromTestCase(TestStatAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestAlertManager))
    suite.addTests(loader.loadTestsFromTestCase(TestStatOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n=== Test Summary ===")
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
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 
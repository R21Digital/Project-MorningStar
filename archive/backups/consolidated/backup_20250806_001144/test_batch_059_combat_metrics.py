#!/usr/bin/env python3
"""Test script for Batch 059 - Combat Metrics Logger + DPS Analysis.

This test script validates all aspects of the combat metrics tracking system including:
- Combat session tracking
- Skill usage monitoring
- DPS analysis
- Performance recommendations
- JSON log generation and loading
- Integration capabilities
"""

import json
import time
import random
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

from core.combat_metrics_logger import CombatMetricsLogger
from core.dps_analyzer import DPSAnalyzer
from core.combat_metrics_integration import CombatMetricsIntegration
from utils.logging_utils import log_event

class TestCombatMetrics:
    """Test suite for combat metrics system."""
    
    def __init__(self):
        """Initialize test suite."""
        self.test_results = []
        self.temp_dir = None
        
    def setup(self):
        """Setup test environment."""
        print("Setting up test environment...")
        
        # Create temporary directory for test logs
        self.temp_dir = tempfile.mkdtemp(prefix="combat_metrics_test_")
        
        # Override log directory for tests
        import core.combat_metrics_logger
        core.combat_metrics_logger.Path = lambda x: Path(self.temp_dir) / x
        
        print(f"Test directory: {self.temp_dir}")
    
    def teardown(self):
        """Cleanup test environment."""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print("Cleaned up test directory")
    
    def run_test(self, test_name: str, test_func):
        """Run a test and record results."""
        print(f"\n--- Running Test: {test_name} ---")
        
        try:
            result = test_func()
            self.test_results.append({
                "test": test_name,
                "status": "PASS",
                "message": "Test completed successfully"
            })
            print(f"✓ {test_name}: PASS")
            return result
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "FAIL",
                "message": str(e)
            })
            print(f"✗ {test_name}: FAIL - {e}")
            return None
    
    def test_combat_metrics_logger_initialization(self):
        """Test combat metrics logger initialization."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        assert logger.session_id == "test_session"
        assert logger.total_damage_dealt == 0
        assert len(logger.combat_sessions) == 0
        assert logger.current_combat is None
        
        return logger
    
    def test_combat_session_tracking(self):
        """Test combat session tracking functionality."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        # Start combat session
        combat_id = logger.start_combat_session("Stormtrooper", 5)
        assert combat_id is not None
        assert logger.current_combat is not None
        assert logger.current_combat["enemy_type"] == "Stormtrooper"
        assert logger.current_combat["enemy_level"] == 5
        
        # Record skill usage
        logger.record_skill_usage("Rifle Shot", 25, "Stormtrooper", 1.5)
        assert logger.current_combat["damage_dealt"] == 25
        assert len(logger.current_combat["skills_used"]) == 1
        
        # End combat session
        combat_summary = logger.end_combat_session("victory", 0)
        assert combat_summary is not None
        assert combat_summary["result"] == "victory"
        assert combat_summary["damage_dealt"] == 25
        assert logger.current_combat is None
        
        return logger
    
    def test_skill_effectiveness_ranking(self):
        """Test skill effectiveness ranking calculation."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        # Start combat and use multiple skills
        logger.start_combat_session("Test Enemy", 1)
        
        # Use skills with different damage values
        logger.record_skill_usage("High Damage Skill", 100, "Test Enemy", 5.0)
        logger.record_skill_usage("Medium Damage Skill", 50, "Test Enemy", 3.0)
        logger.record_skill_usage("Low Damage Skill", 25, "Test Enemy", 1.0)
        logger.record_skill_usage("High Damage Skill", 100, "Test Enemy", 5.0)  # Use twice
        
        logger.end_combat_session("victory", 0)
        
        # Get skill ranking
        ranking = logger.get_skill_effectiveness_ranking()
        assert len(ranking) == 3  # Three unique skills
        
        # Check that high damage skill is ranked highest
        top_skill = ranking[0][0]
        assert "High Damage Skill" in top_skill
        
        return logger
    
    def test_dps_calculation(self):
        """Test DPS calculation functionality."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        # Start combat session
        logger.start_combat_session("Test Enemy", 1)
        
        # Record skill usage over time
        logger.record_skill_usage("Test Skill", 50, "Test Enemy", 2.0)
        time.sleep(0.1)  # Small delay to ensure different timestamps
        
        logger.end_combat_session("victory", 0)
        
        # Check DPS calculation
        current_dps = logger.get_current_dps()
        assert current_dps >= 0  # Should be non-negative
        
        return logger
    
    def test_session_log_save_and_load(self):
        """Test session log saving and loading."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        # Add some combat data
        logger.start_combat_session("Test Enemy", 1)
        logger.record_skill_usage("Test Skill", 50, "Test Enemy", 2.0)
        logger.end_combat_session("victory", 0)
        
        # Save session log
        log_path = logger.save_session_log()
        assert Path(log_path).exists()
        
        # Load session log
        session_data = logger.load_session_log(log_path)
        assert session_data is not None
        assert session_data["session_id"] == "test_session"
        assert len(session_data["combat_sessions"]) == 1
        
        return logger, session_data
    
    def test_dps_analyzer_initialization(self):
        """Test DPS analyzer initialization."""
        logger = CombatMetricsLogger(session_id="test_session")
        analyzer = DPSAnalyzer(logger)
        
        assert analyzer.metrics_logger == logger
        assert analyzer.analysis_cache == {}
        
        return analyzer
    
    def test_performance_analysis(self):
        """Test performance analysis functionality."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        # Add combat data
        logger.start_combat_session("Test Enemy", 1)
        logger.record_skill_usage("Skill 1", 50, "Test Enemy", 2.0)
        logger.record_skill_usage("Skill 2", 75, "Test Enemy", 3.0)
        logger.end_combat_session("victory", 0)
        
        # Save and load session data
        log_path = logger.save_session_log()
        session_data = logger.load_session_log(log_path)
        
        # Analyze performance
        analyzer = DPSAnalyzer(logger)
        analysis = analyzer.analyze_session_performance(session_data)
        
        # Check analysis structure
        assert "overall_performance" in analysis
        assert "skill_analysis" in analysis
        assert "combat_efficiency" in analysis
        assert "trends" in analysis
        assert "recommendations" in analysis
        
        # Check overall performance
        overall = analysis["overall_performance"]
        assert overall["total_damage"] == 125  # 50 + 75
        assert overall["total_combats"] == 1
        
        return analyzer, analysis
    
    def test_skill_analysis(self):
        """Test skill analysis functionality."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        # Add combat data with multiple skills
        logger.start_combat_session("Test Enemy", 1)
        logger.record_skill_usage("Skill A", 100, "Test Enemy", 5.0)
        logger.record_skill_usage("Skill B", 50, "Test Enemy", 2.0)
        logger.record_skill_usage("Skill A", 100, "Test Enemy", 5.0)  # Use twice
        logger.end_combat_session("victory", 0)
        
        # Save and analyze
        log_path = logger.save_session_log()
        session_data = logger.load_session_log(log_path)
        analyzer = DPSAnalyzer(logger)
        analysis = analyzer.analyze_session_performance(session_data)
        
        # Check skill analysis
        skill_analysis = analysis["skill_analysis"]
        assert len(skill_analysis) == 2  # Two unique skills
        
        # Check Skill A (used twice, 100 damage each)
        skill_a = skill_analysis["Skill A"]
        assert skill_a["usage_count"] == 2
        assert skill_a["total_damage"] == 200
        assert skill_a["average_damage"] == 100
        
        # Check Skill B (used once, 50 damage)
        skill_b = skill_analysis["Skill B"]
        assert skill_b["usage_count"] == 1
        assert skill_b["total_damage"] == 50
        assert skill_b["average_damage"] == 50
        
        return analyzer, analysis
    
    def test_recommendations_generation(self):
        """Test recommendations generation."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        # Add combat data
        logger.start_combat_session("Test Enemy", 1)
        logger.record_skill_usage("Low Damage Skill", 10, "Test Enemy", 2.0)
        logger.record_skill_usage("High Damage Skill", 100, "Test Enemy", 5.0)
        logger.end_combat_session("victory", 0)
        
        # Save and analyze
        log_path = logger.save_session_log()
        session_data = logger.load_session_log(log_path)
        analyzer = DPSAnalyzer(logger)
        analysis = analyzer.analyze_session_performance(session_data)
        
        # Check recommendations
        recommendations = analysis["recommendations"]
        assert "skill_optimization" in recommendations
        assert "combat_efficiency" in recommendations
        assert "performance_improvements" in recommendations
        assert "priority_actions" in recommendations
        
        return analyzer, analysis
    
    def test_unused_abilities_detection(self):
        """Test unused abilities detection."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        # Add some combat data
        logger.start_combat_session("Test Enemy", 1)
        logger.record_skill_usage("Used Skill", 50, "Test Enemy", 2.0)
        logger.end_combat_session("victory", 0)
        
        # Define all available abilities
        all_abilities = ["Used Skill", "Unused Skill 1", "Unused Skill 2", "Another Used Skill"]
        
        # Add another used skill
        logger.start_combat_session("Test Enemy 2", 1)
        logger.record_skill_usage("Another Used Skill", 75, "Test Enemy 2", 3.0)
        logger.end_combat_session("victory", 0)
        
        # Get unused abilities
        unused_abilities = logger.get_unused_abilities_recommendations(all_abilities)
        
        # Should detect 2 unused abilities
        assert len(unused_abilities) == 2
        assert "Unused Skill 1" in unused_abilities
        assert "Unused Skill 2" in unused_abilities
        assert "Used Skill" not in unused_abilities
        assert "Another Used Skill" not in unused_abilities
        
        return logger
    
    def test_ai_combat_recommendations(self):
        """Test AI combat recommendations."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        # Add combat data
        logger.start_combat_session("Test Enemy", 1)
        logger.record_skill_usage("Test Skill", 50, "Test Enemy", 2.0)
        logger.end_combat_session("victory", 0)
        
        # Get AI recommendations
        recommendations = logger.get_ai_combat_recommendations()
        
        # Check recommendations structure
        assert "skill_spacing" in recommendations
        assert "cooldown_optimization" in recommendations
        assert "target_priorities" in recommendations
        assert "dps_optimization" in recommendations
        
        return logger
    
    def test_session_summary(self):
        """Test session summary generation."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        # Add combat data
        logger.start_combat_session("Test Enemy", 1)
        logger.record_skill_usage("Test Skill", 50, "Test Enemy", 2.0)
        logger.end_combat_session("victory", 0)
        
        # Get session summary
        summary = logger.get_session_summary()
        
        # Check summary structure
        assert "session_id" in summary
        assert "duration" in summary
        assert "total_combats" in summary
        assert "total_damage" in summary
        assert "current_dps" in summary
        assert "skills_used_count" in summary
        assert "enemies_killed_count" in summary
        
        # Check values
        assert summary["session_id"] == "test_session"
        assert summary["total_combats"] == 1
        assert summary["total_damage"] == 50
        assert summary["skills_used_count"] == 1
        
        return logger
    
    def test_report_generation(self):
        """Test report generation functionality."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        # Add combat data
        logger.start_combat_session("Test Enemy", 1)
        logger.record_skill_usage("Test Skill", 50, "Test Enemy", 2.0)
        logger.end_combat_session("victory", 0)
        
        # Save and analyze
        log_path = logger.save_session_log()
        session_data = logger.load_session_log(log_path)
        analyzer = DPSAnalyzer(logger)
        
        # Generate report
        report = analyzer.generate_report(session_data)
        
        # Check report content
        assert "COMBAT PERFORMANCE ANALYSIS REPORT" in report
        assert "SESSION OVERVIEW" in report
        assert "SKILL PERFORMANCE" in report
        assert "OPTIMIZATION RECOMMENDATIONS" in report
        
        # Save report to file
        report_path = analyzer.save_analysis_report(session_data)
        assert Path(report_path).exists()
        
        return analyzer, report
    
    def test_integration_initialization(self):
        """Test combat metrics integration initialization."""
        integration = CombatMetricsIntegration()
        
        assert integration.metrics_logger is not None
        assert integration.dps_analyzer is not None
        assert integration.is_integrated == False
        
        return integration
    
    def test_session_comparison(self):
        """Test session comparison functionality."""
        analyzer = DPSAnalyzer()
        
        # Create multiple session data
        session_data_list = []
        
        for i in range(3):
            logger = CombatMetricsLogger(session_id=f"test_session_{i}")
            logger.start_combat_session("Test Enemy", 1)
            logger.record_skill_usage("Test Skill", 50 + i * 10, "Test Enemy", 2.0)
            logger.end_combat_session("victory", 0)
            
            log_path = logger.save_session_log()
            session_data = logger.load_session_log(log_path)
            session_data_list.append(session_data)
        
        # Compare sessions
        comparison = analyzer.compare_sessions(session_data_list)
        
        # Check comparison structure
        assert "session_comparison" in comparison
        assert "performance_progression" in comparison
        assert "skill_evolution" in comparison
        assert "overall_trends" in comparison
        
        # Check session comparison
        session_comparison = comparison["session_comparison"]
        assert len(session_comparison) == 3
        
        return analyzer, comparison
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        logger = CombatMetricsLogger(session_id="test_session")
        
        # Test ending combat without starting
        try:
            result = logger.end_combat_session("victory", 0)
            assert result == {}
        except Exception as e:
            assert False, f"Should handle ending combat without starting: {e}"
        
        # Test recording skill without active combat
        try:
            logger.record_skill_usage("Test Skill", 50, "Test Enemy", 2.0)
            # Should log warning but not crash
        except Exception as e:
            assert False, f"Should handle skill usage without active combat: {e}"
        
        # Test loading non-existent log
        try:
            result = logger.load_session_log("non_existent_file.json")
            assert result == {}
        except Exception as e:
            assert False, f"Should handle loading non-existent file: {e}"
        
        return logger
    
    def run_all_tests(self):
        """Run all tests and return results."""
        print("BATCH 059 - COMBAT METRICS TEST SUITE")
        print("=" * 60)
        
        self.setup()
        
        try:
            # Core functionality tests
            self.run_test("Combat Metrics Logger Initialization", 
                         self.test_combat_metrics_logger_initialization)
            self.run_test("Combat Session Tracking", 
                         self.test_combat_session_tracking)
            self.run_test("Skill Effectiveness Ranking", 
                         self.test_skill_effectiveness_ranking)
            self.run_test("DPS Calculation", 
                         self.test_dps_calculation)
            self.run_test("Session Log Save and Load", 
                         self.test_session_log_save_and_load)
            
            # Analysis tests
            self.run_test("DPS Analyzer Initialization", 
                         self.test_dps_analyzer_initialization)
            self.run_test("Performance Analysis", 
                         self.test_performance_analysis)
            self.run_test("Skill Analysis", 
                         self.test_skill_analysis)
            self.run_test("Recommendations Generation", 
                         self.test_recommendations_generation)
            
            # Advanced functionality tests
            self.run_test("Unused Abilities Detection", 
                         self.test_unused_abilities_detection)
            self.run_test("AI Combat Recommendations", 
                         self.test_ai_combat_recommendations)
            self.run_test("Session Summary", 
                         self.test_session_summary)
            self.run_test("Report Generation", 
                         self.test_report_generation)
            
            # Integration tests
            self.run_test("Integration Initialization", 
                         self.test_integration_initialization)
            self.run_test("Session Comparison", 
                         self.test_session_comparison)
            
            # Error handling tests
            self.run_test("Error Handling", 
                         self.test_error_handling)
            
        finally:
            self.teardown()
        
        # Print test results summary
        self.print_test_results()
        
        return self.test_results
    
    def print_test_results(self):
        """Print test results summary."""
        print(f"\n{'='*60}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*60}")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\nFailed Tests:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  • {result['test']}: {result['message']}")
        
        print(f"\n{'='*60}")
        
        if failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Combat Metrics System is ready for use.")
        else:
            print(f"⚠️  {failed_tests} test(s) failed. Please review and fix issues.")

def main():
    """Main test function."""
    test_suite = TestCombatMetrics()
    results = test_suite.run_all_tests()
    
    # Return exit code based on test results
    failed_tests = len([r for r in results if r["status"] == "FAIL"])
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code) 
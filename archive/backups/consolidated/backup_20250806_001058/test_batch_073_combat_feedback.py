#!/usr/bin/env python3
"""
Test suite for Batch 073 - Combat Feedback + Respec Tracker

This test suite validates all components of the combat feedback and respec tracking system.
"""

import unittest
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from modules.combat_feedback import (
    create_combat_feedback,
    create_session_comparator,
    create_skill_analyzer,
    create_respec_advisor,
    create_performance_tracker
)


class TestSessionComparator(unittest.TestCase):
    """Test the SessionComparator component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.comparator = create_session_comparator()
    
    def test_compare_sessions_no_data(self):
        """Test session comparison with no previous data."""
        current_session = {"dps": 100.0, "xp_per_hour": 2000.0}
        previous_sessions = []
        
        result = self.comparator.compare_sessions(current_session, previous_sessions)
        
        self.assertEqual(result["status"], "no_comparison_data")
        self.assertEqual(len(result["alerts"]), 0)
        self.assertEqual(len(result["recommendations"]), 0)
    
    def test_compare_sessions_with_data(self):
        """Test session comparison with previous data."""
        current_session = {"dps": 100.0, "xp_per_hour": 2000.0}
        previous_sessions = [
            {"dps": 150.0, "xp_per_hour": 2500.0},
            {"dps": 140.0, "xp_per_hour": 2400.0}
        ]
        
        result = self.comparator.compare_sessions(current_session, previous_sessions)
        
        self.assertEqual(result["status"], "comparison_complete")
        self.assertIn("comparison", result)
        self.assertIn("alerts", result)
        self.assertIn("recommendations", result)
    
    def test_detect_performance_drop(self):
        """Test performance drop detection."""
        # Test critical drop
        alert_level, drop_pct = self.comparator.detect_performance_drop(75.0, 100.0)
        self.assertEqual(alert_level, "critical")
        self.assertAlmostEqual(drop_pct, 0.25)
        
        # Test warning drop
        alert_level, drop_pct = self.comparator.detect_performance_drop(85.0, 100.0)
        self.assertEqual(alert_level, "warning")
        self.assertAlmostEqual(drop_pct, 0.15)
        
        # Test normal performance
        alert_level, drop_pct = self.comparator.detect_performance_drop(95.0, 100.0)
        self.assertEqual(alert_level, "normal")
        self.assertAlmostEqual(drop_pct, 0.05)
    
    def test_detect_skill_stagnation(self):
        """Test skill stagnation detection."""
        sessions = [
            {"dps": 100.0, "xp_per_hour": 2000.0, "timestamp": datetime.now().isoformat()},
            {"dps": 100.0, "xp_per_hour": 2000.0, "timestamp": (datetime.now() - timedelta(days=1)).isoformat()},
            {"dps": 100.0, "xp_per_hour": 2000.0, "timestamp": (datetime.now() - timedelta(days=2)).isoformat()}
        ]
        
        result = self.comparator.detect_skill_stagnation(sessions, days_threshold=7)
        
        self.assertIn("stagnation_detected", result)
        self.assertIn("indicators", result)
        self.assertIn("sessions_analyzed", result)


class TestSkillAnalyzer(unittest.TestCase):
    """Test the SkillAnalyzer component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = create_skill_analyzer()
    
    def test_analyze_skill_tree(self):
        """Test skill tree analysis."""
        current_skills = ["rifle_shot", "rifle_hit", "pistol_shot", "pistol_hit"]
        build_skills = ["rifle_shot", "rifle_hit"]
        session_history = [
            {"skills_learned": [], "skill_usage_rate": 0.8, "skill_efficiency": 0.7},
            {"skills_learned": [], "skill_usage_rate": 0.8, "skill_efficiency": 0.7}
        ]
        
        result = self.analyzer.analyze_skill_tree(current_skills, build_skills, session_history)
        
        self.assertIn("skill_count", result)
        self.assertIn("build_completion", result)
        self.assertIn("health_score", result)
        self.assertIn("stagnation", result)
        self.assertIn("overlap", result)
        self.assertIn("inefficiency", result)
        self.assertIn("recommendations", result)
    
    def test_detect_skill_stagnation(self):
        """Test skill stagnation detection."""
        current_skills = ["rifle_shot", "rifle_hit"]
        session_history = [
            {"skills_learned": [], "skill_usage_rate": 0.8, "skill_efficiency": 0.7},
            {"skills_learned": [], "skill_usage_rate": 0.8, "skill_efficiency": 0.7}
        ]
        
        result = self.analyzer.detect_skill_stagnation(current_skills, session_history)
        
        self.assertIn("stagnation_detected", result)
        self.assertIn("indicators", result)
        self.assertIn("skill_progression", result)
    
    def test_analyze_skill_overlap(self):
        """Test skill overlap analysis."""
        current_skills = ["rifle_shot", "rifle_hit", "pistol_shot", "pistol_hit"]
        build_skills = ["rifle_shot", "rifle_hit"]
        
        result = self.analyzer.analyze_skill_overlap(current_skills, build_skills)
        
        self.assertIn("overlap_groups", result)
        self.assertIn("redundant_skills", result)
        self.assertIn("total_overlaps", result)
        self.assertIn("total_redundant", result)
    
    def test_analyze_skill_inefficiency(self):
        """Test skill inefficiency analysis."""
        current_skills = ["rifle_shot", "rifle_hit", "pistol_shot"]
        build_skills = ["rifle_shot", "rifle_hit"]
        session_history = [
            {"skills_used": ["rifle_shot"], "skill_efficiency": 0.7},
            {"skills_used": ["rifle_shot"], "skill_efficiency": 0.7}
        ]
        
        result = self.analyzer.analyze_skill_inefficiency(current_skills, build_skills, session_history)
        
        self.assertIn("inefficient_skills", result)
        self.assertIn("underutilized_skills", result)
        self.assertIn("total_inefficient", result)
        self.assertIn("total_underutilized", result)


class TestRespecAdvisor(unittest.TestCase):
    """Test the RespecAdvisor component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.advisor = create_respec_advisor()
    
    def test_analyze_respec_needs(self):
        """Test respec needs analysis."""
        session_comparison = {
            "comparison": {
                "dps": {
                    "current": 100.0,
                    "previous": 150.0,
                    "change_percentage": -0.33
                }
            }
        }
        skill_analysis = {
            "stagnation": {"stagnation_detected": True, "indicators": ["no_progression"]},
            "overlap": {"total_overlaps": 2},
            "inefficiency": {"total_inefficient": 1, "total_underutilized": 1},
            "health_score": 0.6
        }
        performance_metrics = {"dps": 100.0, "xp_per_hour": 2000.0}
        
        result = self.advisor.analyze_respec_needs(session_comparison, skill_analysis, performance_metrics)
        
        self.assertIn("respec_recommended", result)
        self.assertIn("confidence", result)
        self.assertIn("reasons", result)
        self.assertIn("recommendations", result)
        self.assertIn("alternative_suggestions", result)
    
    def test_check_respec_urgency(self):
        """Test respec urgency checking."""
        analysis = {
            "respec_recommended": True,
            "confidence": 0.8,
            "reasons": [{"type": "performance_drop", "severity": "critical"}]
        }
        
        urgency = self.advisor.check_respec_urgency(analysis)
        self.assertIn(urgency, ["critical", "high", "medium", "low", "none"])
    
    def test_get_respec_recommendations(self):
        """Test getting detailed respec recommendations."""
        current_build = {"type": "rifleman", "skills": ["rifle_shot", "rifle_hit"]}
        performance_history = [
            {"dps": 100.0, "xp_per_hour": 2000.0, "timestamp": datetime.now().isoformat()}
        ]
        skill_data = {
            "stagnation_detected": True,
            "stagnation_indicators": ["no_progression"],
            "overlap_count": 1,
            "inefficient_count": 1,
            "underutilized_count": 1,
            "health_score": 0.6
        }
        
        result = self.advisor.get_respec_recommendations(current_build, performance_history, skill_data)
        
        self.assertIn("respec_analysis", result)
        self.assertIn("specific_recommendations", result)
        self.assertIn("build_suggestions", result)
        self.assertIn("timing_recommendations", result)


class TestPerformanceTracker(unittest.TestCase):
    """Test the PerformanceTracker component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = create_performance_tracker(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_record_session(self):
        """Test session recording."""
        session_data = {
            "dps": 100.0,
            "xp_per_hour": 2000.0,
            "kills": 10,
            "deaths": 1,
            "duration": 3600
        }
        
        result = self.tracker.record_session(session_data)
        self.assertTrue(result)
        
        # Check that session was added
        history = self.tracker.get_performance_history(days=1)
        self.assertEqual(len(history), 1)
        self.assertIn("session_id", history[0])
        self.assertIn("efficiency_score", history[0])
    
    def test_get_performance_history(self):
        """Test getting performance history."""
        # Record some sessions
        for i in range(3):
            session_data = {
                "dps": 100.0 + i,
                "xp_per_hour": 2000.0 + i * 100,
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
            }
            self.tracker.record_session(session_data)
        
        history = self.tracker.get_performance_history(days=7)
        self.assertEqual(len(history), 3)
    
    def test_calculate_performance_trends(self):
        """Test performance trend calculation."""
        # Record sessions with increasing performance
        for i in range(3):
            session_data = {
                "dps": 100.0 + i * 10,
                "xp_per_hour": 2000.0 + i * 100,
                "efficiency_score": 0.7 + i * 0.1
            }
            self.tracker.record_session(session_data)
        
        trends = self.tracker.calculate_performance_trends(days=7)
        
        self.assertEqual(trends["status"], "trends_calculated")
        self.assertIn("trends", trends)
        self.assertIn("dps", trends["trends"])
        self.assertIn("xp_per_hour", trends["trends"])
        self.assertIn("efficiency", trends["trends"])
    
    def test_get_performance_summary(self):
        """Test performance summary generation."""
        # Record some sessions
        for i in range(3):
            session_data = {
                "dps": 100.0 + i * 10,
                "xp_per_hour": 2000.0 + i * 100,
                "efficiency_score": 0.7 + i * 0.1
            }
            self.tracker.record_session(session_data)
        
        summary = self.tracker.get_performance_summary(days=7)
        
        self.assertEqual(summary["status"], "summary_calculated")
        self.assertIn("dps", summary)
        self.assertIn("xp_per_hour", summary)
        self.assertIn("efficiency", summary)
    
    def test_detect_performance_anomalies(self):
        """Test performance anomaly detection."""
        # Record sessions with one anomaly
        sessions = [
            {"dps": 100.0, "xp_per_hour": 2000.0},
            {"dps": 100.0, "xp_per_hour": 2000.0},
            {"dps": 200.0, "xp_per_hour": 4000.0}  # Anomaly
        ]
        
        for session in sessions:
            self.tracker.record_session(session)
        
        anomalies = self.tracker.detect_performance_anomalies(days=7)
        
        self.assertEqual(anomalies["status"], "anomalies_detected")
        self.assertIn("anomalies", anomalies)
        self.assertGreaterEqual(anomalies["anomalies_found"], 0)
    
    def test_export_performance_data(self):
        """Test performance data export."""
        # Record a session
        session_data = {"dps": 100.0, "xp_per_hour": 2000.0}
        self.tracker.record_session(session_data)
        
        export_file = self.tracker.export_performance_data()
        
        self.assertTrue(Path(export_file).exists())
        
        # Verify export content
        with open(export_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn("export_timestamp", data)
        self.assertIn("total_sessions", data)
        self.assertIn("sessions", data)


class TestCombatFeedback(unittest.TestCase):
    """Test the main CombatFeedback component."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.combat_feedback = create_combat_feedback(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_analyze_combat_session(self):
        """Test combat session analysis."""
        session_data = {
            "dps": 100.0,
            "xp_per_hour": 2000.0,
            "kills": 10,
            "deaths": 1,
            "duration": 3600
        }
        current_skills = ["rifle_shot", "rifle_hit"]
        build_skills = ["rifle_shot"]
        
        result = self.combat_feedback.analyze_combat_session(
            session_data, current_skills, build_skills
        )
        
        self.assertIn("session_id", result)
        self.assertIn("session_comparison", result)
        self.assertIn("skill_analysis", result)
        self.assertIn("respec_analysis", result)
        self.assertIn("alerts", result)
        self.assertIn("recommendations", result)
    
    def test_get_performance_feedback(self):
        """Test performance feedback generation."""
        # Record some sessions
        for i in range(3):
            session_data = {
                "dps": 100.0 + i * 10,
                "xp_per_hour": 2000.0 + i * 100,
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
            }
            self.combat_feedback.performance_tracker.record_session(session_data)
        
        feedback = self.combat_feedback.get_performance_feedback(days=7)
        
        self.assertIn("timestamp", feedback)
        self.assertIn("days_analyzed", feedback)
        self.assertIn("performance_summary", feedback)
        self.assertIn("performance_trends", feedback)
        self.assertIn("anomalies", feedback)
        self.assertIn("alerts", feedback)
        self.assertIn("recommendations", feedback)
    
    def test_get_respec_recommendations(self):
        """Test respec recommendations generation."""
        current_build = {"type": "rifleman", "skills": ["rifle_shot", "rifle_hit"]}
        current_skills = ["rifle_shot", "rifle_hit", "pistol_shot"]
        
        # Record some sessions
        for i in range(3):
            session_data = {
                "dps": 100.0 + i * 10,
                "xp_per_hour": 2000.0 + i * 100,
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat()
            }
            self.combat_feedback.performance_tracker.record_session(session_data)
        
        recommendations = self.combat_feedback.get_respec_recommendations(
            current_build, current_skills
        )
        
        self.assertIn("respec_analysis", recommendations)
        self.assertIn("specific_recommendations", recommendations)
        self.assertIn("build_suggestions", recommendations)
        self.assertIn("timing_recommendations", recommendations)
    
    def test_check_respec_urgency(self):
        """Test respec urgency checking."""
        analysis = {
            "respec_recommended": True,
            "confidence": 0.8,
            "reasons": [{"type": "performance_drop", "severity": "critical"}]
        }
        
        urgency = self.combat_feedback.check_respec_urgency(analysis)
        self.assertIn(urgency, ["critical", "high", "medium", "low", "none"])
    
    def test_export_feedback_report(self):
        """Test feedback report export."""
        # Record some data
        session_data = {"dps": 100.0, "xp_per_hour": 2000.0}
        current_skills = ["rifle_shot", "rifle_hit"]
        build_skills = ["rifle_shot"]
        
        self.combat_feedback.analyze_combat_session(session_data, current_skills, build_skills)
        
        report_file = self.combat_feedback.export_feedback_report()
        
        self.assertTrue(Path(report_file).exists())
        
        # Verify report content
        with open(report_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn("export_timestamp", data)
        self.assertIn("feedback_history", data)
        self.assertIn("performance_summary", data)
        self.assertIn("performance_trends", data)
        self.assertIn("anomalies", data)
    
    def test_get_feedback_summary(self):
        """Test feedback summary generation."""
        # Record some feedback
        session_data = {"dps": 100.0, "xp_per_hour": 2000.0}
        current_skills = ["rifle_shot", "rifle_hit"]
        build_skills = ["rifle_shot"]
        
        self.combat_feedback.analyze_combat_session(session_data, current_skills, build_skills)
        
        summary = self.combat_feedback.get_feedback_summary()
        
        self.assertIn("total_feedback_entries", summary)
        self.assertIn("recent_feedback_count", summary)
        self.assertIn("alerts_generated", summary)
        self.assertIn("recommendations_generated", summary)
        self.assertIn("respec_recommendations", summary)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete combat feedback system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.combat_feedback = create_combat_feedback(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow(self):
        """Test the complete combat feedback workflow."""
        # Record multiple sessions with declining performance
        for i in range(5):
            session_data = {
                "dps": 200.0 - (i * 10),  # Declining DPS
                "xp_per_hour": 3000.0 - (i * 100),  # Declining XP
                "kills": 30 - i,
                "deaths": 1,
                "duration": 3600,
                "timestamp": (datetime.now() - timedelta(days=i+1)).isoformat()
            }
            self.combat_feedback.performance_tracker.record_session(session_data)
        
        # Analyze current session
        current_session = {
            "dps": 150.0,
            "xp_per_hour": 2500.0,
            "kills": 25,
            "deaths": 2,
            "duration": 3600
        }
        current_skills = ["rifle_shot", "rifle_hit", "pistol_shot", "pistol_hit"]
        build_skills = ["rifle_shot", "rifle_hit"]
        
        feedback = self.combat_feedback.analyze_combat_session(
            current_session, current_skills, build_skills
        )
        
        # Verify comprehensive feedback
        self.assertIn("session_comparison", feedback)
        self.assertIn("skill_analysis", feedback)
        self.assertIn("respec_analysis", feedback)
        self.assertIn("alerts", feedback)
        self.assertIn("recommendations", feedback)
        
        # Check that alerts are generated for performance drop
        alerts = feedback["alerts"]
        self.assertGreater(len(alerts), 0)
        
        # Check that respec analysis is performed
        respec_analysis = feedback["respec_analysis"]
        self.assertIn("respec_recommended", respec_analysis)
        self.assertIn("confidence", respec_analysis)
    
    def test_error_handling(self):
        """Test error handling in the system."""
        # Test with invalid session data
        invalid_session = {"invalid": "data"}
        
        result = self.combat_feedback.analyze_combat_session(invalid_session)
        
        # Should handle gracefully
        self.assertIn("timestamp", result)
        self.assertNotIn("error", result)  # Should handle gracefully
    
    def test_data_persistence(self):
        """Test that data persists between instances."""
        # Record data with first instance
        session_data = {"dps": 100.0, "xp_per_hour": 2000.0}
        self.combat_feedback.performance_tracker.record_session(session_data)
        
        # Create new instance with same data directory
        new_instance = create_combat_feedback(self.temp_dir)
        
        # Check that data is loaded
        history = new_instance.performance_tracker.get_performance_history(days=1)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["dps"], 100.0)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 
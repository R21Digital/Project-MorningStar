#!/usr/bin/env python3
"""
Test script for Batch 069 - Combat Metrics Logger + DPS Analysis

This test script validates all components of the combat metrics system:
1. Combat session logging functionality
2. DPS analysis capabilities
3. Session management features
4. Performance analysis and benchmarking
5. Rotation optimization and dead skills detection
"""

import json
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Import the combat metrics modules
from modules.combat_metrics import (
    CombatLogger,
    DPSAnalyzer,
    CombatSessionManager,
    PerformanceAnalyzer,
    RotationOptimizer
)


class TestCombatMetrics(unittest.TestCase):
    """Comprehensive test suite for Batch 069 combat metrics system."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_logs_dir = Path("logs/combat_test")
        self.test_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.logger = CombatLogger(str(self.test_logs_dir))
        self.analyzer = DPSAnalyzer()
        self.manager = CombatSessionManager(str(self.test_logs_dir))
        self.performance_analyzer = PerformanceAnalyzer()
        self.optimizer = RotationOptimizer()
    
    def tearDown(self):
        """Clean up test environment."""
        # Clean up test files
        import shutil
        if self.test_logs_dir.exists():
            shutil.rmtree(self.test_logs_dir)
    
    def test_combat_logger_session_management(self):
        """Test combat logger session management."""
        # Test session start
        session_id = self.logger.start_session("test_session_001")
        self.assertIsNotNone(session_id)
        self.assertEqual(session_id, "test_session_001")
        
        # Test session state
        self.assertIsNotNone(self.logger.current_session)
        self.assertEqual(self.logger.current_session.session_id, session_id)
        self.assertEqual(self.logger.current_session.session_state, "active")
        
        # Test session end
        summary = self.logger.end_session()
        self.assertIsNotNone(summary)
        self.assertIn("session_id", summary)
        self.assertIn("duration", summary)
        self.assertIn("total_damage_dealt", summary)
        self.assertIn("total_xp_gained", summary)
    
    def test_combat_logger_ability_logging(self):
        """Test ability usage logging."""
        session_id = self.logger.start_session("test_session_002")
        
        # Log ability use
        self.logger.log_ability_use(
            ability_name="headshot",
            target="stormtrooper",
            damage_dealt=400,
            damage_type="physical",
            success=True,
            cooldown_remaining=5.0,
            xp_gained=255
        )
        
        # Verify logging
        stats = self.logger.get_session_stats()
        self.assertIn("abilities_used", stats)
        self.assertIn("headshot", stats["abilities_used"])
        self.assertEqual(stats["abilities_used"]["headshot"], 1)
        self.assertIn("stormtrooper", stats["targets_engaged"])
        
        self.logger.end_session()
    
    def test_combat_logger_enemy_kills(self):
        """Test enemy kill logging."""
        session_id = self.logger.start_session("test_session_003")
        
        # Log enemy kill
        self.logger.log_enemy_kill("stormtrooper", 510)
        
        # Verify logging
        stats = self.logger.get_session_stats()
        self.assertEqual(stats["kills"], 1)
        
        self.logger.end_session()
    
    def test_combat_logger_dps_calculation(self):
        """Test DPS calculation."""
        session_id = self.logger.start_session("test_session_004")
        
        # Add multiple damage events
        for i in range(5):
            self.logger.log_ability_use(
                ability_name="headshot",
                target="enemy",
                damage_dealt=400,
                xp_gained=255
            )
            time.sleep(0.1)
        
        # Test DPS calculation
        current_dps = self.logger.get_current_dps()
        self.assertGreaterEqual(current_dps, 0)
        
        stats = self.logger.get_session_stats()
        self.assertIn("current_dps", stats)
        self.assertIn("average_dps", stats)
        
        self.logger.end_session()
    
    def test_dps_analyzer_basic_functionality(self):
        """Test DPS analyzer basic functionality."""
        # Add damage events
        for i in range(10):
            self.analyzer.add_damage_event(
                damage=400,
                ability_name="headshot",
                target="enemy"
            )
        
        # Test DPS calculations
        current_dps = self.analyzer.calculate_current_dps()
        burst_dps = self.analyzer.calculate_burst_dps()
        sustained_dps = self.analyzer.calculate_sustained_dps()
        
        self.assertGreaterEqual(current_dps, 0)
        self.assertGreaterEqual(burst_dps, 0)
        self.assertGreaterEqual(sustained_dps, 0)
    
    def test_dps_analyzer_trend_analysis(self):
        """Test DPS trend analysis."""
        # Add damage events over time
        for i in range(20):
            self.analyzer.add_damage_event(
                damage=400 + i * 10,  # Increasing damage
                ability_name="headshot",
                target="enemy"
            )
        
        # Test trend analysis
        trends = self.analyzer.analyze_dps_trends()
        self.assertIn("average_dps", trends)
        self.assertIn("peak_dps", trends)
        self.assertIn("trend_direction", trends)
        self.assertIn("consistency", trends)
    
    def test_dps_analyzer_efficiency_calculation(self):
        """Test damage efficiency calculation."""
        # Add damage events with different abilities
        abilities = ["headshot", "burst_fire", "rifle_shot"]
        for ability in abilities:
            for i in range(3):
                self.analyzer.add_damage_event(
                    damage=400,
                    ability_name=ability,
                    target="enemy"
                )
        
        # Test efficiency calculation
        efficiency = self.analyzer.calculate_damage_efficiency()
        self.assertIn("overall_avg_damage", efficiency)
        self.assertIn("damage_consistency", efficiency)
        
        # Check ability-specific metrics
        for ability in abilities:
            self.assertIn(f"{ability}_total_damage", efficiency)
            self.assertIn(f"{ability}_usage_count", efficiency)
            self.assertIn(f"{ability}_avg_damage", efficiency)
    
    def test_session_manager_basic_functionality(self):
        """Test session manager basic functionality."""
        # Create test session data
        session_data = {
            "session_id": "test_session_manager_001",
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration": 300.0,
            "total_damage_dealt": 15000,
            "total_xp_gained": 5000,
            "kills": 25,
            "deaths": 0,
            "abilities_used": {"headshot": 10, "burst_fire": 5},
            "targets_engaged": ["stormtrooper", "imperial_officer"],
            "session_state": "completed"
        }
        
        # Test session saving
        success = self.manager.save_session(session_data)
        self.assertTrue(success)
        
        # Test session loading
        loaded_data = self.manager.load_session("test_session_manager_001")
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data["session_id"], "test_session_manager_001")
    
    def test_session_manager_statistics(self):
        """Test session manager statistics."""
        # Create multiple test sessions
        for i in range(3):
            session_data = {
                "session_id": f"test_stats_{i+1:03d}",
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": 300.0,
                "total_damage_dealt": 15000 + i * 1000,
                "total_xp_gained": 5000 + i * 500,
                "kills": 25 + i * 5,
                "deaths": 0,
                "abilities_used": {"headshot": 10, "burst_fire": 5},
                "targets_engaged": ["stormtrooper"],
                "session_state": "completed"
            }
            self.manager.save_session(session_data)
        
        # Test statistics
        stats = self.manager.get_session_statistics()
        self.assertIn("total_sessions", stats)
        self.assertIn("total_damage_dealt", stats)
        self.assertIn("total_xp_gained", stats)
        self.assertIn("average_dps", stats)
        self.assertGreater(stats["total_sessions"], 0)
    
    def test_session_manager_dead_skills(self):
        """Test dead skills detection."""
        # Create sessions with different ability usage patterns
        sessions = []
        for i in range(5):
            session_data = {
                "session_id": f"test_dead_skills_{i+1:03d}",
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration": 300.0,
                "total_damage_dealt": 15000,
                "total_xp_gained": 5000,
                "kills": 25,
                "deaths": 0,
                "abilities_used": {
                    "headshot": 50,  # Frequently used
                    "burst_fire": 30,  # Moderately used
                    "rare_ability": 1  # Rarely used (should be dead skill)
                },
                "targets_engaged": ["stormtrooper"],
                "session_state": "completed"
            }
            sessions.append(session_data)
        
        # Save sessions to trigger session summary creation
        for session in sessions:
            self.manager.save_session(session)
        
        # Test dead skills detection
        dead_skills = self.manager.find_dead_skills()
        self.assertIsInstance(dead_skills, list)
        
        # Check if rare abilities are detected as dead skills
        self.assertIn("rare_ability", dead_skills)
    
    def test_performance_analyzer_basic_functionality(self):
        """Test performance analyzer basic functionality."""
        # Create test session data
        session_data = {
            "session_id": "test_performance_001",
            "duration": 300.0,
            "total_damage_dealt": 15000,
            "total_xp_gained": 5000,
            "kills": 25,
            "deaths": 0,
            "abilities_used": {"headshot": 10, "burst_fire": 5},
            "targets_engaged": ["stormtrooper"]
        }
        
        # Test performance analysis
        performance = self.performance_analyzer.analyze_session_performance(session_data)
        self.assertIsNotNone(performance)
        self.assertEqual(performance.session_id, "test_performance_001")
        self.assertIn("dps", performance.__dict__)
        self.assertIn("xp_per_hour", performance.__dict__)
        self.assertIn("efficiency_score", performance.__dict__)
        self.assertIn("performance_grade", performance.__dict__)
    
    def test_performance_analyzer_benchmark_comparison(self):
        """Test benchmark comparison."""
        # Create test session data
        session_data = {
            "session_id": "test_benchmark_001",
            "duration": 300.0,
            "total_damage_dealt": 15000,
            "total_xp_gained": 5000,
            "kills": 25,
            "deaths": 0,
            "abilities_used": {"headshot": 10},
            "targets_engaged": ["stormtrooper"]
        }
        
        performance = self.performance_analyzer.analyze_session_performance(session_data)
        
        # Test benchmark comparison
        comparison = self.performance_analyzer.compare_to_benchmark(performance, "beginner")
        self.assertIn("meets_benchmark", comparison)
        self.assertIn("metrics", comparison)
        self.assertIn("overall_score", comparison)
    
    def test_performance_analyzer_efficiency_calculation(self):
        """Test efficiency calculation."""
        session_data = {
            "session_id": "test_efficiency_001",
            "duration": 300.0,
            "total_damage_dealt": 15000,
            "total_xp_gained": 5000,
            "kills": 25,
            "deaths": 0,
            "abilities_used": {"headshot": 10},
            "targets_engaged": ["stormtrooper"]
        }
        
        # Test XP efficiency
        xp_efficiency = self.performance_analyzer.calculate_xp_efficiency(session_data)
        self.assertIn("xp_per_hour", xp_efficiency)
        self.assertIn("xp_per_kill", xp_efficiency)
        self.assertIn("kill_efficiency", xp_efficiency)
        
        # Test damage efficiency
        damage_efficiency = self.performance_analyzer.calculate_damage_efficiency(session_data)
        self.assertIn("dps", damage_efficiency)
        self.assertIn("damage_per_hour", damage_efficiency)
        self.assertIn("damage_per_ability", damage_efficiency)
    
    def test_rotation_optimizer_basic_functionality(self):
        """Test rotation optimizer basic functionality."""
        # Create test session data
        session_data = {
            "session_id": "test_rotation_001",
            "duration": 300.0,
            "total_damage_dealt": 15000,
            "total_xp_gained": 5000,
            "kills": 25,
            "deaths": 0,
            "abilities_used": {"headshot": 10, "burst_fire": 5, "rifle_shot": 3},
            "targets_engaged": ["stormtrooper"],
            "events": [
                {
                    "event_type": "ability_use",
                    "ability_name": "headshot",
                    "damage_dealt": 400,
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        # Test rotation analysis
        rotation = self.optimizer.analyze_session_rotation(session_data)
        self.assertIsNotNone(rotation)
        self.assertEqual(rotation.rotation_id, "rotation_test_rotation_001")
        self.assertIn("headshot", rotation.abilities_used)
        self.assertIn("efficiency_score", rotation.__dict__)
        self.assertIn("recommendations", rotation.__dict__)
    
    def test_rotation_optimizer_dead_skills(self):
        """Test dead skills detection in rotation optimizer."""
        # Create sessions with different ability usage
        sessions = []
        for i in range(3):
            session_data = {
                "session_id": f"test_rotation_dead_{i+1:03d}",
                "duration": 300.0,
                "total_damage_dealt": 15000,
                "total_xp_gained": 5000,
                "kills": 25,
                "deaths": 0,
                "abilities_used": {
                    "headshot": 50,  # Frequently used
                    "burst_fire": 30,  # Moderately used
                    "dead_skill": 1   # Rarely used
                },
                "targets_engaged": ["stormtrooper"],
                "events": []
            }
            sessions.append(session_data)
        
        # Test dead skills detection
        dead_skills = self.optimizer.find_dead_skills(sessions)
        self.assertIsInstance(dead_skills, list)
        
        # Check if dead skills are detected
        dead_skill_names = [skill.skill_name for skill in dead_skills]
        self.assertIn("dead_skill", dead_skill_names)
    
    def test_rotation_optimizer_efficient_rotations(self):
        """Test efficient rotations identification."""
        # Create sessions with different performance
        sessions = []
        for i in range(5):
            session_data = {
                "session_id": f"test_efficient_{i+1:03d}",
                "duration": 300.0,
                "total_damage_dealt": 15000 + i * 1000,  # Increasing damage
                "total_xp_gained": 5000 + i * 500,       # Increasing XP
                "kills": 25 + i * 5,
                "deaths": 0,
                "abilities_used": {"headshot": 10, "burst_fire": 5},
                "targets_engaged": ["stormtrooper"],
                "events": []
            }
            sessions.append(session_data)
        
        # Test efficient rotations
        efficient_rotations = self.optimizer.find_most_efficient_rotations(sessions, 3)
        self.assertIsInstance(efficient_rotations, list)
        self.assertLessEqual(len(efficient_rotations), 3)
        
        # Check that rotations are sorted by efficiency
        if len(efficient_rotations) > 1:
            for i in range(len(efficient_rotations) - 1):
                self.assertGreaterEqual(
                    efficient_rotations[i].efficiency_score,
                    efficient_rotations[i + 1].efficiency_score
                )
    
    def test_rotation_optimizer_optimization(self):
        """Test rotation optimization."""
        current_abilities = ["headshot", "burst_fire", "rifle_shot"]
        
        # Test rotation optimization
        optimization = self.optimizer.optimize_rotation(current_abilities)
        self.assertIn("current_abilities", optimization)
        self.assertIn("target_dps", optimization)
        self.assertIn("target_xp_per_hour", optimization)
        self.assertIn("recommendations", optimization)
        self.assertIn("priority_changes", optimization)
    
    def test_integrated_functionality(self):
        """Test integrated functionality across all components."""
        # Start combat session
        session_id = self.logger.start_session("test_integrated_001")
        
        # Log combat events
        for i in range(5):
            self.logger.log_ability_use(
                ability_name="headshot",
                target="stormtrooper",
                damage_dealt=400,
                xp_gained=255
            )
            time.sleep(0.1)
        
        # End session and get summary
        summary = self.logger.end_session()
        
        # Test session manager integration
        session_data = self.manager.load_session(session_id)
        self.assertIsNotNone(session_data)
        
        # Test performance analyzer integration
        performance = self.performance_analyzer.analyze_session_performance(session_data)
        self.assertIsNotNone(performance)
        
        # Test rotation optimizer integration
        rotation = self.optimizer.analyze_session_rotation(session_data)
        self.assertIsNotNone(rotation)
        
        # Verify all components work together
        self.assertEqual(performance.session_id, session_id)
        self.assertEqual(rotation.rotation_id, f"rotation_{session_id}")


def run_performance_tests():
    """Run performance tests to ensure system can handle realistic loads."""
    print("Running performance tests...")
    
    # Test with large number of events
    logger = CombatLogger()
    session_id = logger.start_session("performance_test")
    
    start_time = time.time()
    
    # Simulate 1000 combat events
    for i in range(1000):
        logger.log_ability_use(
            ability_name=f"ability_{i % 5}",
            target=f"enemy_{i % 10}",
            damage_dealt=400 + (i % 100),
            xp_gained=255 + (i % 50)
        )
        
        if i % 100 == 0:
            logger.log_enemy_kill(f"enemy_{i % 10}", 510)
    
    summary = logger.end_session()
    end_time = time.time()
    
    print(f"Performance test completed in {end_time - start_time:.2f} seconds")
    print(f"Processed {summary['total_damage_dealt']} total damage")
    print(f"Logged {len(summary['abilities_used'])} different abilities")
    
    return end_time - start_time < 5.0  # Should complete in under 5 seconds


def main():
    """Run all tests."""
    print("🧪 BATCH 069 - COMBAT METRICS TEST SUITE")
    print("="*60)
    
    # Run unit tests
    print("\nRunning unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    print("\nRunning performance tests...")
    performance_success = run_performance_tests()
    
    if performance_success:
        print("✅ Performance tests passed")
    else:
        print("❌ Performance tests failed")
    
    print("\n" + "="*60)
    print("✅ BATCH 069 TEST SUITE COMPLETED")
    print("="*60)


if __name__ == "__main__":
    main() 
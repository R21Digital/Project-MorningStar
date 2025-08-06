#!/usr/bin/env python3
"""
Test suite for Batch 156 - Multi-Char Follow Mode (Quester + Support)

This test suite validates the follow mode functionality including:
- Follow mode initialization and configuration
- Healing mechanics and thresholds
- Buffing system and intervals
- Party management
- Distance tracking and movement
- Error handling and edge cases
"""

import unittest
import time
import random
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Import the modules we're testing
try:
    from android_ms11.modes.follow_mode import FollowMode, FollowConfig, run
    from android_ms11.core.heal_manager import (
        get_leader_health, heal_leader, emergency_heal, 
        get_heal_spells, can_cast_heal, get_optimal_heal_spell
    )
    from android_ms11.core.buff_manager import (
        apply_buffs_to_leader, cast_buff, get_available_buffs,
        get_buff_cast_time, get_buff_success_rate, get_buff_duration
    )
    from android_ms11.core.follow_manager import (
        follow_leader_at_distance, get_leader_position,
        calculate_distance_to_leader, is_leader_in_range
    )
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import follow mode modules: {e}")
    MODULES_AVAILABLE = False


class TestFollowConfig(unittest.TestCase):
    """Test the FollowConfig dataclass."""
    
    def test_follow_config_creation(self):
        """Test creating a FollowConfig instance."""
        if not MODULES_AVAILABLE:
            self.skipTest("Follow mode modules not available")
        
        config = FollowConfig(
            leader_name="TestLeader",
            follow_distance=10,
            heal_threshold=75,
            buff_interval=180,
            support_priority="heal",
            auto_join_party=True,
            emergency_heal_threshold=40
        )
        
        self.assertEqual(config.leader_name, "TestLeader")
        self.assertEqual(config.follow_distance, 10)
        self.assertEqual(config.heal_threshold, 75)
        self.assertEqual(config.buff_interval, 180)
        self.assertEqual(config.support_priority, "heal")
        self.assertTrue(config.auto_join_party)
        self.assertEqual(config.emergency_heal_threshold, 40)
    
    def test_follow_config_defaults(self):
        """Test FollowConfig default values."""
        if not MODULES_AVAILABLE:
            self.skipTest("Follow mode modules not available")
        
        config = FollowConfig(leader_name="TestLeader")
        
        self.assertEqual(config.leader_name, "TestLeader")
        self.assertEqual(config.follow_distance, 5)
        self.assertEqual(config.heal_threshold, 80)
        self.assertEqual(config.buff_interval, 300)
        self.assertEqual(config.support_priority, "heal")
        self.assertTrue(config.auto_join_party)
        self.assertEqual(config.emergency_heal_threshold, 50)


class TestFollowMode(unittest.TestCase):
    """Test the FollowMode class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not MODULES_AVAILABLE:
            self.skipTest("Follow mode modules not available")
        
        self.config = FollowConfig(
            leader_name="TestLeader",
            follow_distance=5,
            heal_threshold=80,
            buff_interval=60,
            emergency_heal_threshold=50
        )
        self.follow_mode = FollowMode(self.config)
    
    def test_follow_mode_initialization(self):
        """Test FollowMode initialization."""
        self.assertEqual(self.follow_mode.config.leader_name, "TestLeader")
        self.assertEqual(self.follow_mode.last_buff_time, 0)
        self.assertEqual(self.follow_mode.leader_health, 100)
        self.assertIsNone(self.follow_mode.leader_position)
        self.assertFalse(self.follow_mode.is_in_party)
    
    @patch('android_ms11.core.heal_manager.get_leader_health')
    @patch('android_ms11.core.follow_manager.get_leader_position')
    def test_update_leader_status(self, mock_get_position, mock_get_health):
        """Test updating leader status."""
        mock_get_health.return_value = 85
        mock_get_position.return_value = (100, 200)
        
        self.follow_mode._update_leader_status()
        
        self.assertEqual(self.follow_mode.leader_health, 85)
        self.assertEqual(self.follow_mode.leader_position, (100, 200))
        mock_get_health.assert_called_once_with("TestLeader")
        mock_get_position.assert_called_once_with("TestLeader")
    
    @patch('android_ms11.core.heal_manager.emergency_heal')
    def test_emergency_heal(self, mock_emergency_heal):
        """Test emergency healing functionality."""
        mock_emergency_heal.return_value = True
        
        self.follow_mode._emergency_heal()
        
        mock_emergency_heal.assert_called_once_with("TestLeader")
    
    @patch('android_ms11.core.heal_manager.heal_leader')
    def test_heal_leader(self, mock_heal_leader):
        """Test regular healing functionality."""
        mock_heal_leader.return_value = True
        
        self.follow_mode._heal_leader()
        
        mock_heal_leader.assert_called_once_with("TestLeader")
    
    def test_should_apply_buffs(self):
        """Test buff application timing."""
        # Should not apply buffs initially
        self.assertFalse(self.follow_mode._should_apply_buffs())
        
        # Set last buff time to be old enough
        self.follow_mode.last_buff_time = time.time() - 70  # 70 seconds ago
        
        # Should apply buffs now
        self.assertTrue(self.follow_mode._should_apply_buffs())
    
    @patch('android_ms11.core.buff_manager.apply_buffs_to_leader')
    def test_apply_buffs(self, mock_apply_buffs):
        """Test buff application."""
        mock_apply_buffs.return_value = {"Enhance Health": True, "Enhance Stamina": False}
        
        self.follow_mode._apply_buffs()
        
        mock_apply_buffs.assert_called_once_with("TestLeader")
        self.assertGreater(self.follow_mode.last_buff_time, 0)
    
    @patch('android_ms11.core.follow_manager.follow_leader_at_distance')
    def test_follow_leader(self, mock_follow_leader):
        """Test following the leader."""
        mock_follow_leader.return_value = True
        
        result = self.follow_mode._follow_leader()
        
        self.assertTrue(result)
        mock_follow_leader.assert_called_once_with("TestLeader", 5)
    
    @patch('android_ms11.core.assist_manager.assist_leader')
    def test_assist_leader(self, mock_assist_leader):
        """Test assisting the leader."""
        self.follow_mode._assist_leader()
        
        mock_assist_leader.assert_called_once_with("TestLeader")
    
    @patch('android_ms11.core.party_manager.check_and_join_party')
    def test_check_party_status(self, mock_check_party):
        """Test party status checking."""
        self.follow_mode._check_party_status()
        
        mock_check_party.assert_called_once()
        self.assertTrue(self.follow_mode.is_in_party)
    
    def test_run_cycle_metrics(self):
        """Test that run_cycle returns proper metrics."""
        with patch.object(self.follow_mode, '_check_party_status'), \
             patch.object(self.follow_mode, '_update_leader_status'), \
             patch.object(self.follow_mode, '_follow_leader', return_value=True), \
             patch.object(self.follow_mode, '_assist_leader'):
            
            metrics = self.follow_mode.run_cycle()
            
            self.assertIn('heals_cast', metrics)
            self.assertIn('buffs_cast', metrics)
            self.assertIn('assists_given', metrics)
            self.assertIn('distance_maintained', metrics)
            self.assertIn('party_status', metrics)


class TestHealManager(unittest.TestCase):
    """Test the heal manager functionality."""
    
    def test_get_leader_health(self):
        """Test getting leader health."""
        if not MODULES_AVAILABLE:
            self.skipTest("Heal manager not available")
        
        health = get_leader_health("TestLeader")
        
        self.assertIsInstance(health, int)
        self.assertGreaterEqual(health, 0)
        self.assertLessEqual(health, 100)
    
    @patch('time.sleep')
    def test_heal_leader(self, mock_sleep):
        """Test healing the leader."""
        if not MODULES_AVAILABLE:
            self.skipTest("Heal manager not available")
        
        result = heal_leader("TestLeader")
        
        self.assertIsInstance(result, bool)
        mock_sleep.assert_called_once_with(0.5)
    
    @patch('time.sleep')
    def test_emergency_heal(self, mock_sleep):
        """Test emergency healing."""
        if not MODULES_AVAILABLE:
            self.skipTest("Heal manager not available")
        
        result = emergency_heal("TestLeader")
        
        self.assertIsInstance(result, bool)
        mock_sleep.assert_called_once_with(1.0)
    
    def test_get_heal_spells(self):
        """Test getting available heal spells."""
        if not MODULES_AVAILABLE:
            self.skipTest("Heal manager not available")
        
        spells = get_heal_spells()
        
        self.assertIsInstance(spells, list)
        self.assertGreater(len(spells), 0)
        self.assertIn("Cure Poison", spells)
        self.assertIn("Heal Light Wound", spells)
    
    def test_can_cast_heal(self):
        """Test heal casting ability check."""
        if not MODULES_AVAILABLE:
            self.skipTest("Heal manager not available")
        
        result = can_cast_heal()
        
        self.assertIsInstance(result, bool)
    
    def test_get_optimal_heal_spell(self):
        """Test optimal heal spell selection."""
        if not MODULES_AVAILABLE:
            self.skipTest("Heal manager not available")
        
        # Test different health levels
        self.assertEqual(get_optimal_heal_spell(10), "Emergency Heal")
        self.assertEqual(get_optimal_heal_spell(30), "Heal Critical Wound")
        self.assertEqual(get_optimal_heal_spell(50), "Heal Heavy Wound")
        self.assertEqual(get_optimal_heal_spell(70), "Heal Medium Wound")
        self.assertEqual(get_optimal_heal_spell(90), "Heal Light Wound")


class TestBuffManager(unittest.TestCase):
    """Test the buff manager functionality."""
    
    def test_get_available_buffs(self):
        """Test getting available buffs."""
        if not MODULES_AVAILABLE:
            self.skipTest("Buff manager not available")
        
        buffs = get_available_buffs()
        
        self.assertIsInstance(buffs, list)
        self.assertGreater(len(buffs), 0)
        self.assertIn("Enhance Health", buffs)
        self.assertIn("Enhance Stamina", buffs)
    
    def test_get_buff_cast_time(self):
        """Test buff cast time retrieval."""
        if not MODULES_AVAILABLE:
            self.skipTest("Buff manager not available")
        
        cast_time = get_buff_cast_time("Enhance Health")
        
        self.assertIsInstance(cast_time, float)
        self.assertGreater(cast_time, 0)
    
    def test_get_buff_success_rate(self):
        """Test buff success rate retrieval."""
        if not MODULES_AVAILABLE:
            self.skipTest("Buff manager not available")
        
        success_rate = get_buff_success_rate("Enhance Health")
        
        self.assertIsInstance(success_rate, float)
        self.assertGreater(success_rate, 0)
        self.assertLessEqual(success_rate, 1)
    
    def test_get_buff_duration(self):
        """Test buff duration retrieval."""
        if not MODULES_AVAILABLE:
            self.skipTest("Buff manager not available")
        
        duration = get_buff_duration("Enhance Health")
        
        self.assertIsInstance(duration, int)
        self.assertGreater(duration, 0)
    
    @patch('time.sleep')
    def test_cast_buff(self, mock_sleep):
        """Test casting a buff."""
        if not MODULES_AVAILABLE:
            self.skipTest("Buff manager not available")
        
        result = cast_buff("Enhance Health", "TestTarget")
        
        self.assertIsInstance(result, bool)
        mock_sleep.assert_called_once()
    
    @patch('android_ms11.core.buff_manager.get_available_buffs')
    @patch('android_ms11.core.buff_manager.cast_buff')
    def test_apply_buffs_to_leader(self, mock_cast_buff, mock_get_buffs):
        """Test applying buffs to leader."""
        if not MODULES_AVAILABLE:
            self.skipTest("Buff manager not available")
        
        mock_get_buffs.return_value = ["Enhance Health", "Enhance Stamina"]
        mock_cast_buff.side_effect = [True, False]
        
        result = apply_buffs_to_leader("TestLeader")
        
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)
        self.assertTrue(result["Enhance Health"])
        self.assertFalse(result["Enhance Stamina"])


class TestFollowManager(unittest.TestCase):
    """Test the follow manager functionality."""
    
    def test_follow_leader_at_distance(self):
        """Test following leader at distance."""
        if not MODULES_AVAILABLE:
            self.skipTest("Follow manager not available")
        
        result = follow_leader_at_distance("TestLeader", 5)
        
        self.assertIsInstance(result, bool)
    
    def test_get_leader_position(self):
        """Test getting leader position."""
        if not MODULES_AVAILABLE:
            self.skipTest("Follow manager not available")
        
        position = get_leader_position("TestLeader")
        
        if position is not None:
            self.assertIsInstance(position, tuple)
            self.assertEqual(len(position), 2)
            self.assertIsInstance(position[0], int)
            self.assertIsInstance(position[1], int)
    
    def test_calculate_distance_to_leader(self):
        """Test calculating distance to leader."""
        if not MODULES_AVAILABLE:
            self.skipTest("Follow manager not available")
        
        distance = calculate_distance_to_leader("TestLeader")
        
        if distance is not None:
            self.assertIsInstance(distance, float)
            self.assertGreaterEqual(distance, 0)
    
    def test_is_leader_in_range(self):
        """Test checking if leader is in range."""
        if not MODULES_AVAILABLE:
            self.skipTest("Follow manager not available")
        
        result = is_leader_in_range("TestLeader", 10)
        
        self.assertIsInstance(result, bool)


class TestFollowModeIntegration(unittest.TestCase):
    """Integration tests for follow mode."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        if not MODULES_AVAILABLE:
            self.skipTest("Follow mode modules not available")
        
        self.config = FollowConfig(
            leader_name="IntegrationTestLeader",
            follow_distance=5,
            heal_threshold=80,
            buff_interval=60,
            emergency_heal_threshold=50
        )
        self.follow_mode = FollowMode(self.config)
    
    @patch('android_ms11.core.heal_manager.get_leader_health')
    @patch('android_ms11.core.follow_manager.get_leader_position')
    @patch('android_ms11.core.follow_manager.follow_leader_at_distance')
    @patch('android_ms11.core.assist_manager.assist_leader')
    def test_full_follow_cycle(self, mock_assist, mock_follow, mock_position, mock_health):
        """Test a complete follow cycle."""
        mock_health.return_value = 85
        mock_position.return_value = (100, 200)
        mock_follow.return_value = True
        
        metrics = self.follow_mode.run_cycle()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('heals_cast', metrics)
        self.assertIn('buffs_cast', metrics)
        self.assertIn('assists_given', metrics)
        self.assertIn('distance_maintained', metrics)
        self.assertIn('party_status', metrics)
    
    def test_follow_mode_with_different_configs(self):
        """Test follow mode with different configurations."""
        configs = [
            FollowConfig(leader_name="Leader1", heal_threshold=70),
            FollowConfig(leader_name="Leader2", heal_threshold=90),
            FollowConfig(leader_name="Leader3", follow_distance=10),
        ]
        
        for config in configs:
            with self.subTest(leader=config.leader_name):
                follow_mode = FollowMode(config)
                self.assertEqual(follow_mode.config.leader_name, config.leader_name)


class TestFollowModeEdgeCases(unittest.TestCase):
    """Test edge cases for follow mode."""
    
    def test_follow_mode_with_missing_leader(self):
        """Test follow mode behavior with missing leader."""
        if not MODULES_AVAILABLE:
            self.skipTest("Follow mode modules not available")
        
        config = FollowConfig(leader_name="")
        follow_mode = FollowMode(config)
        
        # Should handle empty leader name gracefully
        metrics = follow_mode.run_cycle()
        self.assertIsInstance(metrics, dict)
    
    def test_follow_mode_with_extreme_values(self):
        """Test follow mode with extreme configuration values."""
        if not MODULES_AVAILABLE:
            self.skipTest("Follow mode modules not available")
        
        config = FollowConfig(
            leader_name="TestLeader",
            follow_distance=0,
            heal_threshold=0,
            buff_interval=1,
            emergency_heal_threshold=0
        )
        follow_mode = FollowMode(config)
        
        # Should handle extreme values gracefully
        metrics = follow_mode.run_cycle()
        self.assertIsInstance(metrics, dict)
    
    @patch('android_ms11.core.heal_manager.get_leader_health')
    def test_follow_mode_with_very_low_health(self, mock_health):
        """Test follow mode with very low leader health."""
        if not MODULES_AVAILABLE:
            self.skipTest("Follow mode modules not available")
        
        mock_health.return_value = 10  # Very low health
        
        config = FollowConfig(leader_name="TestLeader", emergency_heal_threshold=50)
        follow_mode = FollowMode(config)
        
        # Should trigger emergency healing
        with patch.object(follow_mode, '_emergency_heal') as mock_emergency:
            follow_mode.run_cycle()
            mock_emergency.assert_called_once()


def run_performance_benchmark():
    """Run performance benchmark for follow mode."""
    if not MODULES_AVAILABLE:
        print("Skipping performance benchmark - modules not available")
        return
    
    print("\n🔬 Running Performance Benchmark")
    print("-" * 40)
    
    config = FollowConfig(leader_name="BenchmarkLeader")
    follow_mode = FollowMode(config)
    
    # Benchmark run_cycle performance
    start_time = time.time()
    iterations = 1000
    
    for i in range(iterations):
        with patch.object(follow_mode, '_check_party_status'), \
             patch.object(follow_mode, '_update_leader_status'), \
             patch.object(follow_mode, '_follow_leader', return_value=True), \
             patch.object(follow_mode, '_assist_leader'):
            follow_mode.run_cycle()
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"⏱️  Time for {iterations} cycles: {elapsed:.3f}s")
    print(f"📈 Average time per cycle: {elapsed/iterations*1000:.2f}ms")
    print(f"🚀 Cycles per second: {iterations/elapsed:.1f}")


def main():
    """Run the test suite."""
    print("🧪 BATCH 156 - FOLLOW MODE TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestFollowConfig,
        TestFollowMode,
        TestHealManager,
        TestBuffManager,
        TestFollowManager,
        TestFollowModeIntegration,
        TestFollowModeEdgeCases,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Tests run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n⚠️  ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # Run performance benchmark
    run_performance_benchmark()
    
    print("\n✅ Test suite complete!")


if __name__ == "__main__":
    main() 
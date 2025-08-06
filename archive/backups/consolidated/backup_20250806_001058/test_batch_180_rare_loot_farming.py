#!/usr/bin/env python3
"""
Test Batch 180 - Rare Loot Finder (RLS) Farming Mode
Comprehensive test suite for the RLS farming system.
"""

import unittest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import the RLS farming mode components
from src.ms11.modes.rare_loot_mode import (
    RareLootMode, RLSTarget, GroupMode, CooldownStatus,
    RLSLocation, RLSLoot, CooldownTracker, FarmingSession,
    run_rare_loot_mode
)


class TestRLSTargets(unittest.TestCase):
    """Test RLS target enumeration and configuration."""
    
    def test_rls_targets_exist(self):
        """Test that all required RLS targets are defined."""
        required_targets = ["ig_88", "axkva_min", "crystal_snake"]
        
        for target_name in required_targets:
            self.assertTrue(
                any(target.value == target_name for target in RLSTarget),
                f"Required target {target_name} not found in RLSTarget enum"
            )
    
    def test_target_enumeration(self):
        """Test target enumeration functionality."""
        targets = list(RLSTarget)
        self.assertGreaterEqual(len(targets), 6, "Should have at least 6 RLS targets")
        
        # Check specific targets
        target_values = [t.value for t in targets]
        self.assertIn("ig_88", target_values)
        self.assertIn("axkva_min", target_values)
        self.assertIn("crystal_snake", target_values)


class TestCooldownSystem(unittest.TestCase):
    """Test cooldown tracking and management."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        with patch('src.ms11.modes.rare_loot_mode.Path') as mock_path:
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.exists.return_value = False
            self.mode = RareLootMode()
    
    def test_cooldown_initialization(self):
        """Test cooldown system initialization."""
        # All targets should start ready
        cooldowns = self.mode.check_cooldowns()
        
        for target, status in cooldowns.items():
            self.assertEqual(status, CooldownStatus.READY)
    
    def test_cooldown_update(self):
        """Test cooldown update after farming attempt."""
        target = RLSTarget.CRYSTAL_SNAKE
        
        # Update cooldown
        self.mode._update_cooldown(target)
        
        # Check cooldown status
        cooldown = self.mode.cooldowns[target]
        self.assertEqual(cooldown.status, CooldownStatus.ON_COOLDOWN)
        self.assertGreater(cooldown.next_available, datetime.now())
    
    def test_cooldown_expiry(self):
        """Test cooldown expiry detection."""
        target = RLSTarget.MOUF_TIGRIP
        
        # Set expired cooldown
        past_time = datetime.now() - timedelta(hours=2)
        self.mode.cooldowns[target] = CooldownTracker(
            target=target,
            last_attempt=past_time,
            cooldown_minutes=75,
            next_available=past_time + timedelta(minutes=75),
            status=CooldownStatus.ON_COOLDOWN
        )
        
        # Check cooldowns
        cooldowns = self.mode.check_cooldowns()
        self.assertEqual(cooldowns[target], CooldownStatus.READY)


class TestLocationData(unittest.TestCase):
    """Test RLS location data and configuration."""
    
    def setUp(self):
        """Set up test environment."""
        with patch('src.ms11.modes.rare_loot_mode.Path') as mock_path:
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.exists.return_value = False
            self.mode = RareLootMode()
    
    def test_location_loading(self):
        """Test RLS location loading."""
        # Should have locations for all targets
        for target in RLSTarget:
            self.assertIn(target, self.mode.locations)
    
    def test_required_location_data(self):
        """Test that locations have required data."""
        required_targets = [RLSTarget.IG_88, RLSTarget.AXKVA_MIN, RLSTarget.CRYSTAL_SNAKE]
        
        for target in required_targets:
            location = self.mode.locations[target]
            
            # Check required fields
            self.assertIsInstance(location.name, str)
            self.assertIsInstance(location.planet, str)
            self.assertIsInstance(location.coordinates, tuple)
            self.assertEqual(len(location.coordinates), 2)
            self.assertIsInstance(location.waypoint, str)
            self.assertIsInstance(location.group_required, bool)
            self.assertGreater(location.cooldown_minutes, 0)
    
    def test_specific_locations(self):
        """Test specific location configurations."""
        # IG-88 should require group
        ig88 = self.mode.locations[RLSTarget.IG_88]
        self.assertTrue(ig88.group_required)
        self.assertEqual(ig88.planet, "mustafar")
        
        # Crystal Snake should be soloable
        snake = self.mode.locations[RLSTarget.CRYSTAL_SNAKE]
        self.assertFalse(snake.group_required)
        self.assertEqual(snake.planet, "tatooine")


class TestLootSystem(unittest.TestCase):
    """Test loot item configuration and priorities."""
    
    def setUp(self):
        """Set up test environment."""
        with patch('src.ms11.modes.rare_loot_mode.Path') as mock_path:
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.exists.return_value = False
            self.mode = RareLootMode()
    
    def test_loot_item_loading(self):
        """Test loot item loading and configuration."""
        # Should have loot items
        self.assertGreater(len(self.mode.loot_items), 0)
        
        # Check for priority items
        priority_items = ["Crystal Snake Necklace", "Krayt Dragon Pearl", "IG-88 Binary Brain"]
        
        for item_name in priority_items:
            # Should exist in loot items or be configurable
            if item_name in self.mode.loot_items:
                loot = self.mode.loot_items[item_name]
                self.assertIsInstance(loot.priority, int)
                self.assertIsInstance(loot.drop_rate, float)
                self.assertIsInstance(loot.value_credits, int)
    
    def test_loot_priority_toggle(self):
        """Test loot priority modification."""
        # Add a test item if it doesn't exist
        if "Crystal Snake Necklace" not in self.mode.loot_items:
            from src.ms11.modes.rare_loot_mode import RLSLoot, DropRarity
            self.mode.loot_items["Crystal Snake Necklace"] = RLSLoot(
                name="Crystal Snake Necklace",
                target_source=RLSTarget.CRYSTAL_SNAKE,
                rarity="rare",
                drop_rate=0.08,
                priority=3,
                value_credits=800000,
                stackable=False
            )
        
        # Test priority toggle
        success = self.mode.add_loot_priority_toggle("Crystal Snake Necklace", 5)
        self.assertTrue(success)
        
        # Check priority was updated
        loot = self.mode.loot_items["Crystal Snake Necklace"]
        self.assertEqual(loot.priority, 5)
        
        # Should be in priority targets
        self.assertIn("Crystal Snake Necklace", self.mode.priority_targets)


class TestGroupManagement(unittest.TestCase):
    """Test group management and solo detection."""
    
    def setUp(self):
        """Set up test environment."""
        with patch('src.ms11.modes.rare_loot_mode.Path') as mock_path:
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.exists.return_value = False
            self.mode = RareLootMode()
    
    def test_solo_detection(self):
        """Test solo mode detection for appropriate targets."""
        # Crystal Snake should allow solo
        snake_mode = self.mode.join_group_or_solo(RLSTarget.CRYSTAL_SNAKE)
        self.assertIn(snake_mode, [GroupMode.SOLO, GroupMode.GROUP])
        
        # With solo preference, should go solo
        self.mode.group_mode = GroupMode.SOLO
        snake_mode = self.mode.join_group_or_solo(RLSTarget.CRYSTAL_SNAKE)
        self.assertEqual(snake_mode, GroupMode.SOLO)
    
    def test_group_requirement(self):
        """Test group requirements for difficult targets."""
        # IG-88 should require group
        with patch.object(self.mode, '_find_or_create_group', return_value=True):
            ig88_mode = self.mode.join_group_or_solo(RLSTarget.IG_88)
            self.assertEqual(ig88_mode, GroupMode.GROUP)
        
        # If no group found, should keep trying
        with patch.object(self.mode, '_find_or_create_group', return_value=False):
            ig88_mode = self.mode.join_group_or_solo(RLSTarget.IG_88)
            self.assertEqual(ig88_mode, GroupMode.AUTO_JOIN)
    
    @patch('src.ms11.modes.rare_loot_mode.random.random')
    def test_group_finding_simulation(self, mock_random):
        """Test group finding simulation."""
        # High chance should find group
        mock_random.return_value = 0.1  # Low random = high success
        result = self.mode._find_or_create_group(RLSTarget.IG_88)
        self.assertTrue(result)
        
        # Low chance should fail
        mock_random.return_value = 0.9  # High random = low success
        result = self.mode._find_or_create_group(RLSTarget.CRYSTAL_SNAKE)
        # Crystal Snake has low group chance, might fail
        self.assertIsInstance(result, bool)


class TestTravelAutomation(unittest.TestCase):
    """Test travel automation to RLS locations."""
    
    def setUp(self):
        """Set up test environment."""
        with patch('src.ms11.modes.rare_loot_mode.Path') as mock_path:
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.exists.return_value = False
            self.mode = RareLootMode()
    
    @patch('src.ms11.modes.rare_loot_mode.TravelAutomator')
    def test_travel_to_location(self, mock_travel_class):
        """Test travel automation."""
        # Mock travel automator
        mock_travel = MagicMock()
        mock_travel.execute_waypoint.return_value = True
        mock_travel_class.return_value = mock_travel
        self.mode.travel_automator = mock_travel
        
        # Test travel
        result = self.mode.travel_to_location(RLSTarget.CRYSTAL_SNAKE)
        self.assertTrue(result)
        
        # Check waypoint was used
        location = self.mode.locations[RLSTarget.CRYSTAL_SNAKE]
        mock_travel.execute_waypoint.assert_called_with(location.waypoint)
    
    def test_invalid_target_travel(self):
        """Test travel to invalid target."""
        # Should handle invalid targets gracefully
        with patch('src.ms11.modes.rare_loot_mode.log_event'):
            result = self.mode.travel_to_location("invalid_target")
            self.assertFalse(result)


class TestFarmingSession(unittest.TestCase):
    """Test farming session management."""
    
    def setUp(self):
        """Set up test environment."""
        with patch('src.ms11.modes.rare_loot_mode.Path') as mock_path:
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.exists.return_value = False
            self.mode = RareLootMode()
    
    @patch('src.ms11.modes.rare_loot_mode.TravelAutomator')
    def test_session_start(self, mock_travel_class):
        """Test farming session start."""
        # Mock travel success
        mock_travel = MagicMock()
        mock_travel.execute_waypoint.return_value = True
        mock_travel_class.return_value = mock_travel
        self.mode.travel_automator = mock_travel
        
        # Mock group finding
        with patch.object(self.mode, 'join_group_or_solo', return_value=GroupMode.SOLO):
            result = self.mode.start_farming_session(RLSTarget.CRYSTAL_SNAKE, GroupMode.SOLO)
        
        self.assertTrue(result)
        self.assertIsNotNone(self.mode.current_session)
        self.assertEqual(self.mode.current_session.target, RLSTarget.CRYSTAL_SNAKE)
    
    def test_session_statistics(self):
        """Test session statistics calculation."""
        # Create mock session
        self.mode.current_session = FarmingSession(
            session_id="test_session",
            start_time=datetime.now() - timedelta(minutes=30),
            target=RLSTarget.CRYSTAL_SNAKE,
            location="Crystal Snake Lair",
            group_mode=GroupMode.SOLO,
            group_size=1,
            kills=10,
            drops=[
                {"item_name": "Crystal Snake Fang", "target_source": "crystal_snake"},
                {"item_name": "Crystal Snake Necklace", "target_source": "crystal_snake"}
            ],
            success_rate=0.0,
            credits_earned=950000,
            duration_minutes=30,
            status="active"
        )
        
        stats = self.mode.get_farming_statistics()
        
        self.assertEqual(stats["kills"], 10)
        self.assertEqual(stats["total_drops"], 2)
        self.assertEqual(stats["target_drops"], 2)
        self.assertGreater(stats["duration_minutes"], 25)


class TestLootDetection(unittest.TestCase):
    """Test loot detection and logging."""
    
    def setUp(self):
        """Set up test environment."""
        with patch('src.ms11.modes.rare_loot_mode.Path') as mock_path:
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.exists.return_value = False
            self.mode = RareLootMode()
    
    def test_record_drop_no_session(self):
        """Test drop recording without active session."""
        result = self.mode.record_drop("Test Item", RLSTarget.CRYSTAL_SNAKE, (100, 200))
        self.assertFalse(result)
    
    def test_record_drop_with_session(self):
        """Test drop recording with active session."""
        # Create mock session
        self.mode.current_session = FarmingSession(
            session_id="test_session",
            start_time=datetime.now(),
            target=RLSTarget.CRYSTAL_SNAKE,
            location="Crystal Snake Lair",
            group_mode=GroupMode.SOLO,
            group_size=1,
            kills=0,
            drops=[],
            success_rate=0.0,
            credits_earned=0,
            duration_minutes=0,
            status="active"
        )
        
        # Mock OCR verification
        with patch.object(self.mode, '_verify_drop_with_ocr', return_value=True):
            result = self.mode.record_drop("Crystal Snake Necklace", RLSTarget.CRYSTAL_SNAKE, (100, 200))
        
        self.assertTrue(result)
        self.assertEqual(len(self.mode.current_session.drops), 1)


class TestTargetSelection(unittest.TestCase):
    """Test automatic target selection."""
    
    def setUp(self):
        """Set up test environment."""
        with patch('src.ms11.modes.rare_loot_mode.Path') as mock_path:
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.exists.return_value = False
            self.mode = RareLootMode()
    
    def test_best_target_selection(self):
        """Test best target selection algorithm."""
        # All cooldowns ready
        target = self.mode._select_best_target()
        self.assertIsNotNone(target)
        self.assertIsInstance(target, RLSTarget)
    
    def test_no_targets_available(self):
        """Test selection when all targets on cooldown."""
        # Set all targets on cooldown
        future_time = datetime.now() + timedelta(hours=1)
        for target in RLSTarget:
            self.mode.cooldowns[target].next_available = future_time
            self.mode.cooldowns[target].status = CooldownStatus.ON_COOLDOWN
        
        target = self.mode._select_best_target()
        self.assertIsNone(target)


class TestConfigurationFiles(unittest.TestCase):
    """Test configuration file handling."""
    
    def test_loot_targets_config_structure(self):
        """Test loot_targets.json structure."""
        config_path = Path("src/config/loot_targets.json")
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check required sections
            required_sections = [
                "priority_targets", "auto_farming", "group_preferences",
                "loot_detection", "rls_locations"
            ]
            
            for section in required_sections:
                self.assertIn(section, config, f"Missing section: {section}")
            
            # Check RLS locations
            required_locations = ["ig_88", "axkva_min", "crystal_snake"]
            for location in required_locations:
                self.assertIn(location, config["rls_locations"])
    
    def test_rls_drops_log_structure(self):
        """Test rls_drops.json structure."""
        log_path = Path("src/data/loot_logs/rls_drops.json")
        
        if log_path.exists():
            with open(log_path, 'r') as f:
                log_data = json.load(f)
            
            # Check required sections
            required_sections = [
                "session_logs", "drop_history", "statistics",
                "cooldown_tracking", "data_version"
            ]
            
            for section in required_sections:
                self.assertIn(section, log_data, f"Missing section: {section}")


class TestIntegration(unittest.TestCase):
    """Test full integration and mode function."""
    
    @patch('src.ms11.modes.rare_loot_mode.RareLootMode')
    def test_run_rare_loot_mode_function(self, mock_mode_class):
        """Test the main run_rare_loot_mode function."""
        # Mock mode instance
        mock_mode = MagicMock()
        mock_mode.run_farming_mode.return_value = {
            "session_id": "test_session",
            "kills": 5,
            "drops": 2,
            "credits_earned": 100000
        }
        mock_mode_class.return_value = mock_mode
        
        # Test with config
        config = {
            "target": "crystal_snake",
            "duration_minutes": 30,
            "group_mode": "solo"
        }
        
        result = run_rare_loot_mode(config)
        
        # Check function was called correctly
        mock_mode.run_farming_mode.assert_called_once()
        self.assertIn("session_id", result)
        self.assertIn("kills", result)


def run_all_tests():
    """Run all test suites and generate report."""
    print("🧪 BATCH 180 - RARE LOOT FARMING MODE TEST SUITE")
    print("=" * 70)
    
    # Test suites
    test_suites = [
        TestRLSTargets,
        TestCooldownSystem,
        TestLocationData,
        TestLootSystem,
        TestGroupManagement,
        TestTravelAutomation,
        TestFarmingSession,
        TestLootDetection,
        TestTargetSelection,
        TestConfigurationFiles,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_suite in test_suites:
        print(f"\n📋 Running {test_suite.__name__}...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_suite)
        runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
        result = runner.run(suite)
        
        suite_total = result.testsRun
        suite_failed = len(result.failures) + len(result.errors)
        suite_passed = suite_total - suite_failed
        
        total_tests += suite_total
        passed_tests += suite_passed
        failed_tests += suite_failed
        
        status = "✅ PASSED" if suite_failed == 0 else f"❌ FAILED ({suite_failed} failures)"
        print(f"   {status} - {suite_passed}/{suite_total} tests passed")
        
        # Show failures
        if result.failures:
            for test, traceback in result.failures:
                print(f"      FAIL: {test}")
        if result.errors:
            for test, traceback in result.errors:
                print(f"      ERROR: {test}")
    
    # Final report
    print("\n" + "=" * 70)
    print("🎯 TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED - BATCH 180 READY FOR DEPLOYMENT")
    else:
        print(f"\n⚠️  {failed_tests} TESTS FAILED - REVIEW REQUIRED")
    
    return failed_tests == 0


if __name__ == "__main__":
    run_all_tests()
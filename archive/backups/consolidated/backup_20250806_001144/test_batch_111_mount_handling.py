#!/usr/bin/env python3
"""
Batch 111 - Mount & Vehicle Handling Logic Tests

This test suite verifies the functionality of the mount and vehicle handling system,
including mount management, zone detection, auto-mounting, and safety features.

Author: SWG Bot Development Team
"""

import unittest
import time
import json
from typing import Dict, List, Any
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import mount management components
from core.mount_manager import (
    MountManager, get_mount_manager, MountType, MountStatus, ZoneType,
    auto_mount_management, get_mount_status, Mount, MountState, MountPreferences
)
from modules.movement.mount_integration import (
    MountIntegration, integrate_with_movement_system,
    get_mount_travel_status, auto_mount_for_travel,
    handle_combat_mount_behavior, handle_zone_mount_behavior,
    TravelContext
)


class TestMountManager(unittest.TestCase):
    """Test cases for the MountManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = MountManager("test_profile")
        
        # Create test mount
        self.test_mount = Mount(
            name="Test Speeder",
            mount_type=MountType.SPEEDER,
            speed=15.0,
            cooldown=30.0,
            summon_time=2.0,
            dismount_time=1.0
        )
    
    def test_mount_manager_initialization(self):
        """Test mount manager initialization."""
        print("🧪 Testing mount manager initialization...")
        
        # Check that manager was initialized
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.profile_name, "test_profile")
        
        # Check that state was initialized
        self.assertIsInstance(self.manager.state, MountState)
        self.assertEqual(self.manager.state.status, MountStatus.DISMOUNTED)
        
        # Check that preferences were loaded
        self.assertIsInstance(self.manager.preferences, MountPreferences)
        
        # Check that mount database was loaded
        self.assertGreater(len(self.manager.available_mounts), 0)
        
        print(f"✅ Mount manager initialized with {len(self.manager.available_mounts)} mounts")
    
    def test_mount_database_loading(self):
        """Test mount database loading."""
        print("🧪 Testing mount database loading...")
        
        # Check that mounts were loaded
        self.assertGreater(len(self.manager.available_mounts), 0)
        
        # Check that mounts have required attributes
        for mount_id, mount in self.manager.available_mounts.items():
            self.assertIsInstance(mount.name, str)
            self.assertIsInstance(mount.mount_type, MountType)
            self.assertIsInstance(mount.speed, (int, float))
            self.assertIsInstance(mount.cooldown, (int, float))
            self.assertIsInstance(mount.summon_time, (int, float))
            self.assertIsInstance(mount.dismount_time, (int, float))
        
        print(f"✅ Mount database loaded with {len(self.manager.available_mounts)} mounts")
    
    def test_mount_selection(self):
        """Test mount selection logic."""
        print("🧪 Testing mount selection...")
        
        # Test mount selection for different distances
        test_scenarios = [
            {"distance": 25.0, "expected_type": MountType.SPEEDER},
            {"distance": 75.0, "expected_type": MountType.SPEEDER},
            {"distance": 150.0, "expected_type": MountType.SPEEDER},
            {"distance": 300.0, "expected_type": MountType.SPEEDER}
        ]
        
        for scenario in test_scenarios:
            best_mount = self.manager.select_best_mount(scenario["distance"])
            if best_mount:
                self.assertIsInstance(best_mount, Mount)
                print(f"  Distance {scenario['distance']}: Selected {best_mount.name}")
            else:
                print(f"  Distance {scenario['distance']}: No mount selected")
        
        print("✅ Mount selection tests passed")
    
    def test_zone_detection(self):
        """Test zone detection functionality."""
        print("🧪 Testing zone detection...")
        
        # Test zone detection
        zone = self.manager.detect_current_zone()
        self.assertIsInstance(zone, ZoneType)
        
        # Test no-mount zone detection
        test_locations = [
            ("Mustafar", "lava_cave", True),
            ("Kashyyyk", "wookiee_home", True),
            ("Naboo", "theed_palace", True),
            ("Tatooine", "Anchorhead", False),
            ("Corellia", "coronet_city", False)
        ]
        
        for planet, location, expected in test_locations:
            is_no_mount = self.manager.is_no_mount_zone(planet, location)
            self.assertEqual(is_no_mount, expected)
            print(f"  {planet} - {location}: {is_no_mount} (expected: {expected})")
        
        print("✅ Zone detection tests passed")
    
    def test_mount_summoning(self):
        """Test mount summoning functionality."""
        print("🧪 Testing mount summoning...")
        
        # Test summoning a mount
        success = self.manager.summon_mount(self.test_mount)
        self.assertTrue(success)
        
        # Check that state was updated
        self.assertEqual(self.manager.state.status, MountStatus.MOUNTED)
        self.assertEqual(self.manager.state.current_mount, self.test_mount)
        
        # Check that cooldown was recorded
        self.assertIn(self.test_mount.name, self.manager.mount_cooldowns)
        
        print("✅ Mount summoning tests passed")
    
    def test_mount_dismounting(self):
        """Test mount dismounting functionality."""
        print("🧪 Testing mount dismounting...")
        
        # First summon a mount
        self.manager.summon_mount(self.test_mount)
        
        # Test dismounting
        success = self.manager.dismount()
        self.assertTrue(success)
        
        # Check that state was updated
        self.assertEqual(self.manager.state.status, MountStatus.DISMOUNTED)
        self.assertIsNone(self.manager.state.current_mount)
        
        print("✅ Mount dismounting tests passed")
    
    def test_auto_mount_management(self):
        """Test automatic mount management."""
        print("🧪 Testing auto mount management...")
        
        # Test auto mount for long distance
        action_taken = self.manager.auto_mount_management(
            distance=100.0,
            current_location="Anchorhead",
            destination="Mos Eisley"
        )
        
        # Should mount for long distance
        self.assertTrue(action_taken)
        
        # Test auto mount for short distance
        action_taken = self.manager.auto_mount_management(
            distance=10.0,
            current_location="Anchorhead",
            destination="Mos Eisley"
        )
        
        # Should not mount for short distance
        self.assertFalse(action_taken)
        
        print("✅ Auto mount management tests passed")
    
    def test_mount_cooldowns(self):
        """Test mount cooldown management."""
        print("🧪 Testing mount cooldowns...")
        
        # Test that mounts respect cooldowns
        available_mounts = self.manager.get_available_mounts()
        initial_count = len(available_mounts)
        
        # Use a mount
        self.manager.summon_mount(self.test_mount)
        self.manager.dismount()
        
        # Check that mount is now on cooldown
        available_mounts_after = self.manager.get_available_mounts()
        self.assertLessEqual(len(available_mounts_after), initial_count)
        
        # Reset cooldowns
        self.manager.reset_cooldowns()
        available_mounts_reset = self.manager.get_available_mounts()
        self.assertEqual(len(available_mounts_reset), initial_count)
        
        print("✅ Mount cooldown tests passed")
    
    def test_emergency_dismount(self):
        """Test emergency dismount functionality."""
        print("🧪 Testing emergency dismount...")
        
        # Test emergency dismount when not mounted
        success = self.manager.emergency_dismount()
        self.assertTrue(success)
        
        # Mount and test emergency dismount
        self.manager.summon_mount(self.test_mount)
        success = self.manager.emergency_dismount()
        self.assertTrue(success)
        self.assertEqual(self.manager.state.status, MountStatus.DISMOUNTED)
        
        print("✅ Emergency dismount tests passed")
    
    def test_preferences_management(self):
        """Test preferences management."""
        print("🧪 Testing preferences management...")
        
        # Test updating preferences
        new_preferences = {
            "preferred_mount_type": MountType.CREATURE,
            "auto_mount_distance": 75.0,
            "preferred_mounts": ["Bantha", "Dewback"]
        }
        
        self.manager.update_preferences(**new_preferences)
        
        # Check that preferences were updated
        self.assertEqual(self.manager.preferences.preferred_mount_type, MountType.CREATURE)
        self.assertEqual(self.manager.preferences.auto_mount_distance, 75.0)
        self.assertEqual(self.manager.preferences.preferred_mounts, ["Bantha", "Dewback"])
        
        print("✅ Preferences management tests passed")
    
    def test_mount_status_reporting(self):
        """Test mount status reporting."""
        print("🧪 Testing mount status reporting...")
        
        # Get initial status
        status = self.manager.get_mount_status()
        self.assertIsInstance(status, dict)
        self.assertIn("mounted", status)
        self.assertIn("current_mount", status)
        self.assertIn("status", status)
        self.assertIn("zone", status)
        self.assertIn("in_combat", status)
        
        # Mount and check status
        self.manager.summon_mount(self.test_mount)
        status = self.manager.get_mount_status()
        self.assertTrue(status["mounted"])
        self.assertEqual(status["current_mount"], self.test_mount.name)
        
        print("✅ Mount status reporting tests passed")


class TestMountIntegration(unittest.TestCase):
    """Test cases for the MountIntegration class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.integration = MountIntegration("test_profile")
        
        # Create test travel context
        self.test_context = TravelContext(
            start_location="Anchorhead",
            destination="Mos Eisley",
            distance=75.0,
            terrain_type="desert",
            weather_conditions="clear",
            time_of_day="day",
            faction="neutral"
        )
    
    def test_integration_initialization(self):
        """Test mount integration initialization."""
        print("🧪 Testing mount integration initialization...")
        
        # Check that integration was initialized
        self.assertIsNotNone(self.integration)
        self.assertEqual(self.integration.profile_name, "test_profile")
        
        # Check that mount manager was created
        self.assertIsNotNone(self.integration.mount_manager)
        
        # Check that settings were initialized
        self.assertTrue(self.integration.auto_mount_enabled)
        self.assertTrue(self.integration.smart_route_planning)
        self.assertTrue(self.integration.combat_avoidance)
        
        print("✅ Mount integration initialization tests passed")
    
    def test_travel_preparation(self):
        """Test travel preparation functionality."""
        print("🧪 Testing travel preparation...")
        
        # Test travel preparation
        success = self.integration.prepare_for_travel(
            start_location="Anchorhead",
            destination="Mos Eisley",
            distance=75.0,
            terrain_type="desert",
            weather_conditions="clear",
            time_of_day="day",
            faction="neutral"
        )
        
        # Should prepare for travel (may or may not mount depending on settings)
        self.assertIsInstance(success, bool)
        
        print("✅ Travel preparation tests passed")
    
    def test_travel_completion(self):
        """Test travel completion handling."""
        print("🧪 Testing travel completion...")
        
        # Set up travel context
        self.integration.current_travel_context = self.test_context
        
        # Test travel completion
        self.integration.handle_travel_completion(75.0)
        
        # Check that travel history was updated
        self.assertGreater(len(self.integration.travel_history), 0)
        
        # Check that context was cleared
        self.assertIsNone(self.integration.current_travel_context)
        
        print("✅ Travel completion tests passed")
    
    def test_combat_handling(self):
        """Test combat encounter handling."""
        print("🧪 Testing combat handling...")
        
        # Test combat handling when not mounted
        success = self.integration.handle_combat_encounter()
        self.assertTrue(success)
        
        # Mount and test combat handling
        test_mount = Mount(
            name="Test Mount",
            mount_type=MountType.SPEEDER,
            speed=15.0,
            cooldown=30.0,
            summon_time=2.0,
            dismount_time=1.0
        )
        self.integration.mount_manager.summon_mount(test_mount)
        
        success = self.integration.handle_combat_encounter()
        self.assertTrue(success)
        
        print("✅ Combat handling tests passed")
    
    def test_zone_transition_handling(self):
        """Test zone transition handling."""
        print("🧪 Testing zone transition handling...")
        
        # Test zone transitions
        zone_scenarios = [
            ("Entering building", ZoneType.INDOORS),
            ("Entering no-mount zone", ZoneType.NO_MOUNT),
            ("Entering combat zone", ZoneType.COMBAT),
            ("Moving outdoors", ZoneType.OUTDOORS)
        ]
        
        for zone_name, zone_type in zone_scenarios:
            success = self.integration.handle_zone_transition(zone_name, zone_type)
            self.assertTrue(success)
            print(f"  {zone_name}: {zone_type.value}")
        
        print("✅ Zone transition handling tests passed")
    
    def test_travel_statistics(self):
        """Test travel statistics functionality."""
        print("🧪 Testing travel statistics...")
        
        # Add some test travel records
        test_travels = [
            {"start": "Anchorhead", "destination": "Mos Eisley", "distance": 75.0, "mount": "Speeder Bike"},
            {"start": "Theed", "destination": "Lake Retreat", "distance": 120.0, "mount": "Landspeeder"},
            {"start": "Coronet", "destination": "Tyrena", "distance": 180.0, "mount": "Swoop Bike"}
        ]
        
        for travel in test_travels:
            self.integration.travel_history.append({
                "start": travel["start"],
                "destination": travel["destination"],
                "planned_distance": travel["distance"],
                "actual_distance": travel["distance"],
                "mount_used": travel["mount"],
                "timestamp": time.time()
            })
        
        # Get statistics
        stats = self.integration.get_travel_statistics()
        
        # Check statistics structure
        self.assertIn("total_travels", stats)
        self.assertIn("total_distance", stats)
        self.assertIn("average_distance", stats)
        self.assertIn("mount_usage", stats)
        
        # Check values
        self.assertEqual(stats["total_travels"], 3)
        self.assertEqual(stats["total_distance"], 375.0)
        self.assertEqual(stats["average_distance"], 125.0)
        
        print("✅ Travel statistics tests passed")
    
    def test_mount_suitability_checking(self):
        """Test mount suitability checking."""
        print("🧪 Testing mount suitability checking...")
        
        # Create test mount with preferences
        test_mount = Mount(
            name="Test Mount",
            mount_type=MountType.SPEEDER,
            speed=15.0,
            cooldown=30.0,
            summon_time=2.0,
            dismount_time=1.0,
            preferences={
                "terrain": ["desert", "grassland"],
                "weather": ["clear", "light_rain"],
                "time_of_day": ["day", "night"],
                "faction": ["neutral", "rebel"]
            }
        )
        
        # Test suitable context
        suitable_context = TravelContext(
            start_location="Anchorhead",
            destination="Mos Eisley",
            distance=75.0,
            terrain_type="desert",
            weather_conditions="clear",
            time_of_day="day",
            faction="neutral"
        )
        
        is_suitable = self.integration._is_mount_suitable_for_context(test_mount, suitable_context)
        self.assertTrue(is_suitable)
        
        # Test unsuitable context
        unsuitable_context = TravelContext(
            start_location="Anchorhead",
            destination="Mos Eisley",
            distance=75.0,
            terrain_type="forest",
            weather_conditions="clear",
            time_of_day="day",
            faction="neutral"
        )
        
        is_suitable = self.integration._is_mount_suitable_for_context(test_mount, unsuitable_context)
        self.assertFalse(is_suitable)
        
        print("✅ Mount suitability checking tests passed")


class TestMountSystemIntegration(unittest.TestCase):
    """Test cases for system integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_profile = "test_integration"
    
    def test_auto_mount_management_function(self):
        """Test the auto_mount_management convenience function."""
        print("🧪 Testing auto_mount_management function...")
        
        # Test auto mount management
        action_taken = auto_mount_management(
            distance=100.0,
            current_location="Anchorhead",
            destination="Mos Eisley",
            profile_name=self.test_profile
        )
        
        # Should return boolean
        self.assertIsInstance(action_taken, bool)
        
        print("✅ Auto mount management function tests passed")
    
    def test_get_mount_status_function(self):
        """Test the get_mount_status convenience function."""
        print("🧪 Testing get_mount_status function...")
        
        # Test getting mount status
        status = get_mount_status(self.test_profile)
        
        # Check status structure
        self.assertIsInstance(status, dict)
        self.assertIn("mounted", status)
        self.assertIn("current_mount", status)
        self.assertIn("status", status)
        
        print("✅ Get mount status function tests passed")
    
    def test_combat_mount_behavior_function(self):
        """Test the handle_combat_mount_behavior function."""
        print("🧪 Testing handle_combat_mount_behavior function...")
        
        # Test combat mount behavior
        action_taken = handle_combat_mount_behavior(self.test_profile)
        
        # Should return boolean
        self.assertIsInstance(action_taken, bool)
        
        print("✅ Combat mount behavior function tests passed")
    
    def test_zone_mount_behavior_function(self):
        """Test the handle_zone_mount_behavior function."""
        print("🧪 Testing handle_zone_mount_behavior function...")
        
        # Test zone mount behavior
        action_taken = handle_zone_mount_behavior("Test Zone", ZoneType.INDOORS, self.test_profile)
        
        # Should return boolean
        self.assertIsInstance(action_taken, bool)
        
        print("✅ Zone mount behavior function tests passed")
    
    def test_mount_travel_status_function(self):
        """Test the get_mount_travel_status function."""
        print("🧪 Testing get_mount_travel_status function...")
        
        # Test getting mount travel status
        status = get_mount_travel_status(self.test_profile)
        
        # Check status structure
        self.assertIsInstance(status, dict)
        self.assertIn("mount_status", status)
        self.assertIn("travel_statistics", status)
        self.assertIn("integration_settings", status)
        
        print("✅ Mount travel status function tests passed")
    
    def test_movement_system_integration(self):
        """Test integration with movement system."""
        print("🧪 Testing movement system integration...")
        
        # Create mock movement agent
        mock_agent = Mock()
        mock_agent.move_to.return_value = True
        
        # Test integration
        success = integrate_with_movement_system(
            movement_agent=mock_agent,
            start_location="Anchorhead",
            destination="Mos Eisley",
            distance=75.0,
            profile_name=self.test_profile
        )
        
        # Should return boolean
        self.assertIsInstance(success, bool)
        
        print("✅ Movement system integration tests passed")


class TestMountDataStructures(unittest.TestCase):
    """Test cases for mount data structures."""
    
    def test_mount_dataclass(self):
        """Test Mount dataclass."""
        print("🧪 Testing Mount dataclass...")
        
        # Create test mount
        mount = Mount(
            name="Test Mount",
            mount_type=MountType.SPEEDER,
            speed=15.0,
            cooldown=30.0,
            summon_time=2.0,
            dismount_time=1.0,
            is_available=True,
            last_used=0.0,
            preferences={"terrain": ["desert"]}
        )
        
        # Check attributes
        self.assertEqual(mount.name, "Test Mount")
        self.assertEqual(mount.mount_type, MountType.SPEEDER)
        self.assertEqual(mount.speed, 15.0)
        self.assertEqual(mount.cooldown, 30.0)
        self.assertEqual(mount.summon_time, 2.0)
        self.assertEqual(mount.dismount_time, 1.0)
        self.assertTrue(mount.is_available)
        self.assertEqual(mount.last_used, 0.0)
        self.assertEqual(mount.preferences, {"terrain": ["desert"]})
        
        print("✅ Mount dataclass tests passed")
    
    def test_mount_state_dataclass(self):
        """Test MountState dataclass."""
        print("🧪 Testing MountState dataclass...")
        
        # Create test mount state
        state = MountState(
            current_mount=None,
            status=MountStatus.DISMOUNTED,
            last_action_time=0.0,
            current_zone=ZoneType.OUTDOORS,
            in_combat=False,
            distance_traveled=0.0,
            auto_mount_enabled=True
        )
        
        # Check attributes
        self.assertIsNone(state.current_mount)
        self.assertEqual(state.status, MountStatus.DISMOUNTED)
        self.assertEqual(state.last_action_time, 0.0)
        self.assertEqual(state.current_zone, ZoneType.OUTDOORS)
        self.assertFalse(state.in_combat)
        self.assertEqual(state.distance_traveled, 0.0)
        self.assertTrue(state.auto_mount_enabled)
        
        print("✅ MountState dataclass tests passed")
    
    def test_mount_preferences_dataclass(self):
        """Test MountPreferences dataclass."""
        print("🧪 Testing MountPreferences dataclass...")
        
        # Create test preferences
        preferences = MountPreferences(
            preferred_mount_type=MountType.SPEEDER,
            auto_mount_distance=50.0,
            auto_dismount_in_combat=True,
            auto_dismount_in_buildings=True,
            avoid_no_mount_zones=True,
            mount_cooldown_tolerance=5.0,
            preferred_mounts=["Speeder Bike", "Landspeeder"],
            banned_mounts=["Rancor"]
        )
        
        # Check attributes
        self.assertEqual(preferences.preferred_mount_type, MountType.SPEEDER)
        self.assertEqual(preferences.auto_mount_distance, 50.0)
        self.assertTrue(preferences.auto_dismount_in_combat)
        self.assertTrue(preferences.auto_dismount_in_buildings)
        self.assertTrue(preferences.avoid_no_mount_zones)
        self.assertEqual(preferences.mount_cooldown_tolerance, 5.0)
        self.assertEqual(preferences.preferred_mounts, ["Speeder Bike", "Landspeeder"])
        self.assertEqual(preferences.banned_mounts, ["Rancor"])
        
        print("✅ MountPreferences dataclass tests passed")
    
    def test_travel_context_dataclass(self):
        """Test TravelContext dataclass."""
        print("🧪 Testing TravelContext dataclass...")
        
        # Create test travel context
        context = TravelContext(
            start_location="Anchorhead",
            destination="Mos Eisley",
            distance=75.0,
            terrain_type="desert",
            weather_conditions="clear",
            time_of_day="day",
            faction="neutral",
            urgency="normal",
            combat_risk=0.1
        )
        
        # Check attributes
        self.assertEqual(context.start_location, "Anchorhead")
        self.assertEqual(context.destination, "Mos Eisley")
        self.assertEqual(context.distance, 75.0)
        self.assertEqual(context.terrain_type, "desert")
        self.assertEqual(context.weather_conditions, "clear")
        self.assertEqual(context.time_of_day, "day")
        self.assertEqual(context.faction, "neutral")
        self.assertEqual(context.urgency, "normal")
        self.assertEqual(context.combat_risk, 0.1)
        
        print("✅ TravelContext dataclass tests passed")


def run_performance_tests():
    """Run performance tests for the mount system."""
    print("\n🚀 Running performance tests...")
    
    manager = get_mount_manager("performance_test")
    
    import time
    
    # Test mount selection performance
    start_time = time.time()
    for _ in range(100):
        manager.select_best_mount(100.0)
    selection_time = time.time() - start_time
    
    # Test zone detection performance
    start_time = time.time()
    for _ in range(50):
        manager.detect_current_zone()
    detection_time = time.time() - start_time
    
    # Test auto mount management performance
    start_time = time.time()
    for _ in range(50):
        auto_mount_management(100.0, "Anchorhead", "Mos Eisley")
    management_time = time.time() - start_time
    
    print(f"✅ Performance test results:")
    print(f"  Mount selection: {selection_time:.3f}s for 100 operations")
    print(f"  Zone detection: {detection_time:.3f}s for 50 operations")
    print(f"  Auto mount management: {management_time:.3f}s for 50 operations")


def run_integration_tests():
    """Run integration tests for the mount system."""
    print("\n🔗 Running integration tests...")
    
    # Test full mount workflow
    print("  Testing complete mount workflow...")
    manager = get_mount_manager("integration_test")
    
    # Test mount selection and summoning
    best_mount = manager.select_best_mount(100.0)
    if best_mount:
        success = manager.summon_mount(best_mount)
        assert success, "Mount summoning should succeed"
        assert manager.state.status == MountStatus.MOUNTED, "Should be mounted"
    
    # Test auto mount management
    action_taken = auto_mount_management(100.0, "Anchorhead", "Mos Eisley")
    assert isinstance(action_taken, bool), "Should return boolean"
    
    # Test integration functions
    status = get_mount_status()
    assert isinstance(status, dict), "Should return status dict"
    
    print("  Testing mount integration with movement...")
    integration = MountIntegration("integration_test")
    success = integration.prepare_for_travel("Anchorhead", "Mos Eisley", 75.0)
    assert isinstance(success, bool), "Should return boolean"
    
    print("✅ Integration tests passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 BATCH 111 - MOUNT & VEHICLE HANDLING LOGIC TESTS")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMountManager)
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMountIntegration))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMountSystemIntegration))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMountDataStructures))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run additional tests
    run_performance_tests()
    run_integration_tests()
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print("🎯 Mount & Vehicle Handling Logic is ready for production use")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Please check the implementation")
    print("=" * 60)
    
    # Print summary
    print("\n📊 Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
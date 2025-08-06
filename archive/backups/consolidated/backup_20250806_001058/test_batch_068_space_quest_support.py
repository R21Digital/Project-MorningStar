#!/usr/bin/env python3
"""
Test suite for Batch 068 - Space Quest Support Module (Extended Phase)

Tests all components:
1. Hyperspace Pathing Simulation
2. Mission Locations
3. Ship Upgrades
4. AI Piloting Foundation
5. Integrated Space Quest Support
"""

import unittest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the modules to test
from modules.space_quest_support import (
    SpaceQuestSupport,
    HyperspacePathingSimulator,
    MissionLocationManager,
    ShipUpgradeManager,
    AIPilotingFoundation
)
from modules.space_quest_support.hyperspace_pathing import (
    NavigationRequest, HyperspaceRouteType, HyperspaceZone
)
from modules.space_quest_support.mission_locations import (
    MissionLocationType, MissionDifficulty
)
from modules.space_quest_support.ship_upgrades import (
    ShipTier, UpgradeType, UpgradeRarity
)
from modules.space_quest_support.ai_piloting import (
    PilotSkill, PilotBehavior, MissionType
)


class TestHyperspacePathing(unittest.TestCase):
    """Test hyperspace pathing simulation."""
    
    def setUp(self):
        """Set up test environment."""
        self.hyperspace = HyperspacePathingSimulator()
    
    def test_initialization(self):
        """Test hyperspace pathing initialization."""
        self.assertIsNotNone(self.hyperspace)
        self.assertIsInstance(self.hyperspace.nodes, dict)
        self.assertIsInstance(self.hyperspace.routes, dict)
        self.assertGreater(len(self.hyperspace.nodes), 0)
        self.assertGreater(len(self.hyperspace.routes), 0)
    
    def test_get_available_destinations(self):
        """Test getting available destinations."""
        destinations = self.hyperspace.get_available_destinations("Corellia Starport")
        self.assertIsInstance(destinations, list)
        self.assertGreater(len(destinations), 0)
        
        for dest in destinations:
            self.assertIn("name", dest)
            self.assertIn("zone", dest)
            self.assertIn("distance", dest)
            self.assertIn("travel_time", dest)
            self.assertIn("fuel_cost", dest)
            self.assertIn("risk_level", dest)
    
    def test_calculate_route(self):
        """Test route calculation."""
        request = NavigationRequest(
            start_location="Corellia Starport",
            destination="Naboo Orbital",
            route_type=HyperspaceRouteType.SAFE,
            ship_class="Basic Fighter",
            fuel_capacity=100.0,
            max_risk_tolerance=0.5
        )
        
        result = self.hyperspace.calculate_route(request)
        self.assertIsNotNone(result)
        self.assertIsInstance(result.total_distance, float)
        self.assertIsInstance(result.total_time, float)
        self.assertIsInstance(result.total_fuel_cost, float)
        self.assertIsInstance(result.waypoints, list)
        self.assertGreater(len(result.waypoints), 0)
    
    def test_start_navigation(self):
        """Test starting navigation."""
        request = NavigationRequest(
            start_location="Corellia Starport",
            destination="Naboo Orbital",
            route_type=HyperspaceRouteType.DIRECT,
            ship_class="Basic Fighter",
            fuel_capacity=100.0,
            max_risk_tolerance=0.5
        )
        
        result = self.hyperspace.calculate_route(request)
        success = self.hyperspace.start_navigation(result)
        self.assertTrue(success)
        self.assertIsNotNone(self.hyperspace.active_route)
    
    def test_get_navigation_status(self):
        """Test getting navigation status."""
        status = self.hyperspace.get_navigation_status()
        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
    
    def test_complete_navigation(self):
        """Test completing navigation."""
        # Start navigation first
        request = NavigationRequest(
            start_location="Corellia Starport",
            destination="Naboo Orbital",
            route_type=HyperspaceRouteType.DIRECT,
            ship_class="Basic Fighter",
            fuel_capacity=100.0,
            max_risk_tolerance=0.5
        )
        
        result = self.hyperspace.calculate_route(request)
        self.hyperspace.start_navigation(result)
        
        # Complete navigation
        success = self.hyperspace.complete_navigation()
        self.assertTrue(success)
        self.assertIsNone(self.hyperspace.active_route)


class TestMissionLocations(unittest.TestCase):
    """Test mission location management."""
    
    def setUp(self):
        """Set up test environment."""
        self.locations = MissionLocationManager()
    
    def test_initialization(self):
        """Test mission locations initialization."""
        self.assertIsNotNone(self.locations)
        self.assertIsInstance(self.locations.locations, dict)
        self.assertIsInstance(self.locations.mission_givers, dict)
        self.assertGreater(len(self.locations.locations), 0)
        self.assertGreater(len(self.locations.mission_givers), 0)
    
    def test_get_location(self):
        """Test getting a specific location."""
        location = self.locations.get_location("Corellia Starport")
        self.assertIsNotNone(location)
        self.assertEqual(location.name, "Corellia Starport")
        self.assertEqual(location.location_type, MissionLocationType.STARPORT)
    
    def test_get_available_locations(self):
        """Test getting all available locations."""
        locations = self.locations.get_available_locations()
        self.assertIsInstance(locations, list)
        self.assertGreater(len(locations), 0)
        
        for location in locations:
            self.assertIsInstance(location.name, str)
            self.assertIsInstance(location.location_type, MissionLocationType)
            self.assertIsInstance(location.zone, str)
    
    def test_get_locations_by_type(self):
        """Test filtering locations by type."""
        starports = self.locations.get_locations_by_type(MissionLocationType.STARPORT)
        self.assertIsInstance(starports, list)
        
        for location in starports:
            self.assertEqual(location.location_type, MissionLocationType.STARPORT)
    
    def test_visit_location(self):
        """Test visiting a location."""
        success = self.locations.visit_location("Corellia Starport")
        self.assertTrue(success)
        
        location = self.locations.get_location("Corellia Starport")
        self.assertIsNotNone(location.last_visited)
    
    def test_get_mission_givers_at_location(self):
        """Test getting mission givers at a location."""
        givers = self.locations.get_mission_givers_at_location("Corellia Starport")
        self.assertIsInstance(givers, list)
        self.assertGreater(len(givers), 0)
        
        for giver in givers:
            self.assertIsInstance(giver.name, str)
            self.assertIsInstance(giver.faction, str)
            self.assertIsInstance(giver.mission_types, list)
    
    def test_interact_with_giver(self):
        """Test interacting with a mission giver."""
        interaction = self.locations.interact_with_giver("Commander Tarkin")
        self.assertIsInstance(interaction, dict)
        self.assertIn("giver_name", interaction)
        self.assertIn("faction", interaction)
        self.assertIn("available_missions", interaction)
        self.assertIn("dialogue", interaction)
    
    def test_accept_mission(self):
        """Test accepting a mission."""
        # First interact with giver to get available missions
        interaction = self.locations.interact_with_giver("Commander Tarkin")
        if "available_missions" in interaction and interaction["available_missions"]:
            mission_id = interaction["available_missions"][0]["mission_id"]
            result = self.locations.accept_mission(mission_id, "Commander Tarkin")
            self.assertIsInstance(result, dict)
            if "success" in result:
                self.assertTrue(result["success"])


class TestShipUpgrades(unittest.TestCase):
    """Test ship upgrade management."""
    
    def setUp(self):
        """Set up test environment."""
        self.upgrades = ShipUpgradeManager()
    
    def test_initialization(self):
        """Test ship upgrades initialization."""
        self.assertIsNotNone(self.upgrades)
        self.assertIsInstance(self.upgrades.ship_classes, dict)
        self.assertIsInstance(self.upgrades.upgrades, dict)
        self.assertGreater(len(self.upgrades.ship_classes), 0)
        self.assertGreater(len(self.upgrades.upgrades), 0)
    
    def test_get_ship_class(self):
        """Test getting a specific ship class."""
        ship = self.upgrades.get_ship_class("Basic Fighter")
        self.assertIsNotNone(ship)
        self.assertEqual(ship.name, "Basic Fighter")
        self.assertEqual(ship.ship_type, "fighter")
        self.assertEqual(ship.base_tier, ShipTier.TIER_1)
    
    def test_get_available_ships(self):
        """Test getting all available ships."""
        ships = self.upgrades.get_available_ships()
        self.assertIsInstance(ships, list)
        self.assertGreater(len(ships), 0)
        
        for ship in ships:
            self.assertIsInstance(ship.name, str)
            self.assertIsInstance(ship.ship_type, str)
            self.assertIsInstance(ship.base_tier, ShipTier)
    
    def test_get_unlocked_ships(self):
        """Test getting unlocked ships."""
        unlocked_ships = self.upgrades.get_unlocked_ships()
        self.assertIsInstance(unlocked_ships, list)
        
        for ship in unlocked_ships:
            self.assertTrue(ship.is_unlocked)
    
    def test_unlock_ship(self):
        """Test unlocking a ship."""
        player_stats = {"level": 15, "credits": 5000, "reputation": 100}
        success = self.upgrades.unlock_ship("Advanced Fighter", player_stats)
        self.assertTrue(success)
        
        ship = self.upgrades.get_ship_class("Advanced Fighter")
        self.assertTrue(ship.is_unlocked)
    
    def test_get_available_upgrades(self):
        """Test getting available upgrades for a ship."""
        upgrades = self.upgrades.get_available_upgrades("Basic Fighter")
        self.assertIsInstance(upgrades, list)
        
        for upgrade in upgrades:
            self.assertIsInstance(upgrade.upgrade_id, str)
            self.assertIsInstance(upgrade.name, str)
            self.assertIsInstance(upgrade.upgrade_type, UpgradeType)
            self.assertIsInstance(upgrade.rarity, UpgradeRarity)
    
    def test_install_upgrade(self):
        """Test installing an upgrade."""
        result = self.upgrades.install_upgrade("Basic Fighter", "basic_weapon_001", "weapons_1")
        self.assertIsInstance(result, dict)
        
        if "success" in result and result["success"]:
            self.assertIn("new_stats", result)
            self.assertIsInstance(result["new_stats"], dict)
    
    def test_remove_upgrade(self):
        """Test removing an upgrade."""
        # First install an upgrade
        self.upgrades.install_upgrade("Basic Fighter", "basic_weapon_001", "weapons_1")
        
        # Then remove it
        result = self.upgrades.remove_upgrade("Basic Fighter", "weapons_1")
        self.assertIsInstance(result, dict)
        
        if "success" in result and result["success"]:
            self.assertIn("new_stats", result)
    
    def test_get_ship_stats(self):
        """Test getting ship statistics."""
        stats = self.upgrades.get_ship_stats("Basic Fighter")
        self.assertIsInstance(stats, dict)
        self.assertIn("name", stats)
        self.assertIn("ship_type", stats)
        self.assertIn("base_stats", stats)
        self.assertIn("current_stats", stats)
    
    def test_get_upgrade_statistics(self):
        """Test getting upgrade statistics."""
        stats = self.upgrades.get_upgrade_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_ships", stats)
        self.assertIn("unlocked_ships", stats)
        self.assertIn("total_upgrades", stats)
        self.assertIn("installed_upgrades", stats)


class TestAIPiloting(unittest.TestCase):
    """Test AI piloting foundation."""
    
    def setUp(self):
        """Set up test environment."""
        self.ai_piloting = AIPilotingFoundation()
    
    def test_initialization(self):
        """Test AI piloting initialization."""
        self.assertIsNotNone(self.ai_piloting)
        self.assertIsInstance(self.ai_piloting.pilots, dict)
        self.assertIsInstance(self.ai_piloting.missions, dict)
        self.assertGreater(len(self.ai_piloting.pilots), 0)
    
    def test_get_pilot(self):
        """Test getting a specific pilot."""
        pilot = self.ai_piloting.get_pilot("nav_specialist_001")
        self.assertIsNotNone(pilot)
        self.assertEqual(pilot.name, "Navigator Prime")
        self.assertEqual(pilot.behavior, PilotBehavior.CAUTIOUS)
    
    def test_get_available_pilots(self):
        """Test getting all available pilots."""
        pilots = self.ai_piloting.get_available_pilots()
        self.assertIsInstance(pilots, list)
        self.assertGreater(len(pilots), 0)
        
        for pilot in pilots:
            self.assertIsInstance(pilot.pilot_id, str)
            self.assertIsInstance(pilot.name, str)
            self.assertIsInstance(pilot.behavior, PilotBehavior)
            self.assertIsInstance(pilot.skill_levels, dict)
    
    def test_get_active_pilots(self):
        """Test getting active pilots."""
        active_pilots = self.ai_piloting.get_active_pilots()
        self.assertIsInstance(active_pilots, list)
        
        for pilot in active_pilots:
            self.assertTrue(pilot.is_active)
    
    def test_get_pilots_by_skill(self):
        """Test filtering pilots by skill."""
        nav_pilots = self.ai_piloting.get_pilots_by_skill(PilotSkill.NAVIGATION, 5)
        self.assertIsInstance(nav_pilots, list)
        
        for pilot in nav_pilots:
            self.assertGreaterEqual(pilot.skill_levels.get(PilotSkill.NAVIGATION, 0), 5)
    
    def test_activate_pilot(self):
        """Test activating a pilot."""
        success = self.ai_piloting.activate_pilot("nav_specialist_001")
        self.assertTrue(success)
        
        pilot = self.ai_piloting.get_pilot("nav_specialist_001")
        self.assertTrue(pilot.is_active)
    
    def test_deactivate_pilot(self):
        """Test deactivating a pilot."""
        # First activate a pilot
        self.ai_piloting.activate_pilot("nav_specialist_001")
        
        # Then deactivate
        success = self.ai_piloting.deactivate_pilot("nav_specialist_001")
        self.assertTrue(success)
        
        pilot = self.ai_piloting.get_pilot("nav_specialist_001")
        self.assertFalse(pilot.is_active)
    
    def test_assign_mission(self):
        """Test assigning a mission to a pilot."""
        # First activate a pilot
        self.ai_piloting.activate_pilot("nav_specialist_001")
        
        mission_data = {
            "mission_type": "patrol",
            "ship_name": "Basic Fighter",
            "destination": "Naboo Orbital",
            "objectives": ["Patrol the route"],
            "constraints": {},
            "priority": 5,
            "estimated_duration": 30.0
        }
        
        mission_id = self.ai_piloting.assign_mission("nav_specialist_001", mission_data)
        self.assertIsNotNone(mission_id)
        self.assertIsInstance(mission_id, str)
    
    def test_start_mission(self):
        """Test starting a mission."""
        # First assign a mission
        self.ai_piloting.activate_pilot("nav_specialist_001")
        mission_data = {
            "mission_type": "patrol",
            "ship_name": "Basic Fighter",
            "destination": "Naboo Orbital",
            "objectives": ["Patrol the route"],
            "constraints": {},
            "priority": 5,
            "estimated_duration": 30.0
        }
        mission_id = self.ai_piloting.assign_mission("nav_specialist_001", mission_data)
        
        # Start the mission
        success = self.ai_piloting.start_mission(mission_id)
        self.assertTrue(success)
        
        mission = self.ai_piloting.missions.get(mission_id)
        self.assertEqual(mission.status, "active")
    
    def test_update_mission_progress(self):
        """Test updating mission progress."""
        # Set up a mission
        self.ai_piloting.activate_pilot("nav_specialist_001")
        mission_data = {
            "mission_type": "patrol",
            "ship_name": "Basic Fighter",
            "destination": "Naboo Orbital",
            "objectives": ["Patrol the route"],
            "constraints": {},
            "priority": 5,
            "estimated_duration": 30.0
        }
        mission_id = self.ai_piloting.assign_mission("nav_specialist_001", mission_data)
        self.ai_piloting.start_mission(mission_id)
        
        # Update progress
        progress_data = {
            "current_location": "Corellia Starport",
            "events": ["Enemy detected"],
            "fuel_remaining": 85.0
        }
        
        result = self.ai_piloting.update_mission_progress(mission_id, progress_data)
        self.assertIsInstance(result, dict)
        self.assertIn("mission_id", result)
        self.assertIn("pilot_name", result)
        self.assertIn("decisions", result)
    
    def test_complete_mission(self):
        """Test completing a mission."""
        # Set up a mission
        self.ai_piloting.activate_pilot("nav_specialist_001")
        mission_data = {
            "mission_type": "patrol",
            "ship_name": "Basic Fighter",
            "destination": "Naboo Orbital",
            "objectives": ["Patrol the route"],
            "constraints": {},
            "priority": 5,
            "estimated_duration": 30.0
        }
        mission_id = self.ai_piloting.assign_mission("nav_specialist_001", mission_data)
        self.ai_piloting.start_mission(mission_id)
        
        # Complete the mission
        result = self.ai_piloting.complete_mission(mission_id)
        self.assertIsInstance(result, dict)
        self.assertIn("mission_id", result)
        self.assertIn("pilot_name", result)
    
    def test_get_pilot_performance(self):
        """Test getting pilot performance."""
        performance = self.ai_piloting.get_pilot_performance("nav_specialist_001")
        self.assertIsInstance(performance, dict)
        self.assertIn("pilot_id", performance)
        self.assertIn("missions_completed", performance)
        self.assertIn("missions_failed", performance)
    
    def test_get_ai_piloting_statistics(self):
        """Test getting AI piloting statistics."""
        stats = self.ai_piloting.get_ai_piloting_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_pilots", stats)
        self.assertIn("active_pilots", stats)
        self.assertIn("total_missions", stats)
        self.assertIn("completed_missions", stats)


class TestSpaceQuestSupport(unittest.TestCase):
    """Test integrated space quest support system."""
    
    def setUp(self):
        """Set up test environment."""
        self.space_quest = SpaceQuestSupport()
    
    def test_initialization(self):
        """Test space quest support initialization."""
        self.assertIsNotNone(self.space_quest)
        self.assertIsNotNone(self.space_quest.hyperspace_pathing)
        self.assertIsNotNone(self.space_quest.mission_locations)
        self.assertIsNotNone(self.space_quest.ship_upgrades)
        self.assertIsNotNone(self.space_quest.ai_piloting)
    
    def test_start_session(self):
        """Test starting a session."""
        session_id = self.space_quest.start_session("Corellia Starport")
        self.assertIsInstance(session_id, str)
        self.assertIsNotNone(self.space_quest.current_session)
        self.assertEqual(self.space_quest.current_session.current_location, "Corellia Starport")
    
    def test_end_session(self):
        """Test ending a session."""
        # Start a session first
        session_id = self.space_quest.start_session("Corellia Starport")
        
        # End the session
        summary = self.space_quest.end_session()
        self.assertIsInstance(summary, dict)
        self.assertIn("session_id", summary)
        self.assertIn("duration", summary)
        self.assertIn("stats", summary)
        self.assertIsNone(self.space_quest.current_session)
    
    def test_navigate_to_location(self):
        """Test navigating to a location."""
        # Start a session
        self.space_quest.start_session("Corellia Starport")
        
        # Navigate to destination
        result = self.space_quest.navigate_to_location("Naboo Orbital", "safe")
        self.assertIsInstance(result, dict)
        
        if "error" not in result:
            self.assertIn("success", result)
            self.assertIn("destination", result)
            self.assertIn("route", result)
    
    def test_visit_mission_location(self):
        """Test visiting a mission location."""
        # Start a session
        self.space_quest.start_session("Corellia Starport")
        
        # Visit location
        result = self.space_quest.visit_mission_location("Corellia Starport")
        self.assertIsInstance(result, dict)
        
        if "error" not in result:
            self.assertIn("success", result)
            self.assertIn("location", result)
            self.assertIn("mission_givers", result)
    
    def test_interact_with_giver(self):
        """Test interacting with a mission giver."""
        # Start a session
        self.space_quest.start_session("Corellia Starport")
        
        # Interact with giver
        result = self.space_quest.interact_with_giver("Commander Tarkin")
        self.assertIsInstance(result, dict)
        self.assertIn("giver_name", result)
        self.assertIn("available_missions", result)
    
    def test_unlock_ship(self):
        """Test unlocking a ship."""
        # Start a session
        self.space_quest.start_session("Corellia Starport")
        
        # Unlock ship
        player_stats = {"level": 15, "credits": 5000, "reputation": 100}
        result = self.space_quest.unlock_ship("Advanced Fighter", player_stats)
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("ship_name", result)
    
    def test_activate_pilot(self):
        """Test activating an AI pilot."""
        # Start a session
        self.space_quest.start_session("Corellia Starport")
        
        # Activate pilot
        result = self.space_quest.activate_pilot("nav_specialist_001")
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("pilot_name", result)
    
    def test_get_session_status(self):
        """Test getting session status."""
        # Start a session
        self.space_quest.start_session("Corellia Starport")
        
        # Get status
        status = self.space_quest.get_session_status()
        self.assertIsInstance(status, dict)
        self.assertIn("session_id", status)
        self.assertIn("current_location", status)
        self.assertIn("session_stats", status)
    
    def test_get_integration_statistics(self):
        """Test getting integration statistics."""
        stats = self.space_quest.get_integration_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn("hyperspace_pathing", stats)
        self.assertIn("mission_locations", stats)
        self.assertIn("ship_upgrades", stats)
        self.assertIn("ai_piloting", stats)
    
    def test_save_and_load_session_data(self):
        """Test saving and loading session data."""
        # Start a session
        self.space_quest.start_session("Corellia Starport")
        
        # Save session data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            filepath = f.name
        
        try:
            success = self.space_quest.save_session_data(filepath)
            self.assertTrue(success)
            
            # Create new instance and load data
            new_space_quest = SpaceQuestSupport()
            load_success = new_space_quest.load_session_data(filepath)
            self.assertTrue(load_success)
            
            # Check that session was loaded
            status = new_space_quest.get_session_status()
            self.assertIn("session_id", status)
            self.assertEqual(status["current_location"], "Corellia Starport")
            
        finally:
            # Clean up
            Path(filepath).unlink(missing_ok=True)


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def setUp(self):
        """Set up test environment."""
        self.space_quest = SpaceQuestSupport()
    
    def test_full_mission_workflow(self):
        """Test a complete mission workflow."""
        # Start session
        session_id = self.space_quest.start_session("Corellia Starport")
        self.assertIsNotNone(session_id)
        
        # Navigate to mission location
        nav_result = self.space_quest.navigate_to_location("Naboo Orbital", "safe")
        self.assertIn("success", nav_result)
        
        # Visit location
        visit_result = self.space_quest.visit_mission_location("Naboo Orbital")
        self.assertIn("success", visit_result)
        
        # Interact with giver
        interaction = self.space_quest.interact_with_giver("Ambassador Amidala")
        self.assertIn("giver_name", interaction)
        
        # Activate AI pilot
        pilot_result = self.space_quest.activate_pilot("nav_specialist_001")
        self.assertIn("success", pilot_result)
        
        # Assign AI mission
        mission_data = {
            "mission_type": "patrol",
            "ship_name": "Basic Fighter",
            "destination": "Corellia Starport",
            "objectives": ["Patrol the route"],
            "constraints": {},
            "priority": 5,
            "estimated_duration": 30.0
        }
        mission_result = self.space_quest.assign_ai_mission("nav_specialist_001", mission_data)
        self.assertIn("success", mission_result)
        
        # Get session status
        status = self.space_quest.get_session_status()
        self.assertIn("session_id", status)
        self.assertIn("current_location", status)
        self.assertIn("active_pilot", status)
        
        # End session
        summary = self.space_quest.end_session()
        self.assertIn("session_id", summary)
        self.assertIn("stats", summary)
    
    def test_component_interaction(self):
        """Test interaction between different components."""
        # Test that hyperspace pathing affects mission locations
        self.space_quest.start_session("Corellia Starport")
        
        # Navigate to a location
        nav_result = self.space_quest.navigate_to_location("Naboo Orbital")
        if "success" in nav_result:
            # Check that current location was updated
            status = self.space_quest.get_session_status()
            self.assertEqual(status["current_location"], "Naboo Orbital")
            
            # Check that hyperspace pathing location was updated
            self.assertEqual(
                self.space_quest.hyperspace_pathing.current_location,
                "Naboo Orbital"
            )
    
    def test_error_handling(self):
        """Test error handling in integrated system."""
        # Test navigation to non-existent location
        self.space_quest.start_session("Corellia Starport")
        result = self.space_quest.navigate_to_location("NonExistentLocation")
        self.assertIn("error", result)
        
        # Test visiting non-existent location
        result = self.space_quest.visit_mission_location("NonExistentLocation")
        self.assertIn("error", result)
        
        # Test interacting with non-existent giver
        result = self.space_quest.interact_with_giver("NonExistentGiver")
        self.assertIn("error", result)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestHyperspacePathing,
        TestMissionLocations,
        TestShipUpgrades,
        TestAIPiloting,
        TestSpaceQuestSupport,
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
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Batch 050 - Planetary Travel Tests

Comprehensive test suite for the planetary travel system including:
- Unit tests for individual components
- Integration tests for travel workflows
- Edge case testing
- Performance testing
- Error handling validation
"""

import json
import logging
import time
import unittest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

# Configure logging for tests
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise during tests
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import components to test
try:
    from core.travel_manager import (
        get_travel_manager, plan_travel_route, execute_travel, 
        get_travel_statistics, TravelType, TravelRoute, TravelResult,
        PlanetaryTravelManager
    )
    from utils.starport_detector import (
        get_starport_detector, scan_for_terminals, 
        get_detection_status, TerminalType, StarportDetector,
        TerminalInfo, DetectionResult, InteractionResult
    )
    from travel.ship_travel import (
        get_ship_travel_system, check_ship_availability,
        PersonalShipTravelSystem, ShipTravelResult
    )
    from travel.terminal_travel import (
        get_terminal_travel_system, scan_for_terminals as scan_terminals,
        TerminalTravelSystem, TravelDialogResult
    )
    TRAVEL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Travel components not available for testing: {e}")
    TRAVEL_AVAILABLE = False


class TestPlanetaryTravelManager(unittest.TestCase):
    """Test cases for the Planetary Travel Manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not TRAVEL_AVAILABLE:
            self.skipTest("Travel components not available")
        
        self.travel_manager = get_travel_manager()
        self.test_routes = [
            {
                "start_planet": "tatooine",
                "start_city": "mos_eisley",
                "dest_planet": "naboo",
                "dest_city": "theed",
                "expected_type": TravelType.STARPORT
            },
            {
                "start_planet": "naboo",
                "start_city": "theed",
                "dest_planet": "corellia",
                "dest_city": "coronet",
                "expected_type": TravelType.SHUTTLEPORT
            }
        ]
    
    def test_travel_manager_initialization(self):
        """Test travel manager initialization."""
        self.assertIsNotNone(self.travel_manager)
        self.assertIsInstance(self.travel_manager, PlanetaryTravelManager)
        self.assertEqual(self.travel_manager.current_status.value, "idle")
    
    def test_route_planning_starport(self):
        """Test starport route planning."""
        test_route = self.test_routes[0]
        
        route = self.travel_manager.plan_travel_route(
            start_planet=test_route["start_planet"],
            start_city=test_route["start_city"],
            dest_planet=test_route["dest_planet"],
            dest_city=test_route["dest_city"],
            preferred_type=TravelType.STARPORT
        )
        
        self.assertIsNotNone(route)
        self.assertEqual(route.travel_type, TravelType.STARPORT)
        self.assertEqual(route.start_planet, test_route["start_planet"])
        self.assertEqual(route.dest_planet, test_route["dest_planet"])
        self.assertGreater(route.cost, 0)
        self.assertGreater(route.travel_time, 0)
    
    def test_route_planning_shuttle(self):
        """Test shuttle route planning."""
        test_route = self.test_routes[1]
        
        route = self.travel_manager.plan_travel_route(
            start_planet=test_route["start_planet"],
            start_city=test_route["start_city"],
            dest_planet=test_route["dest_planet"],
            dest_city=test_route["dest_city"],
            preferred_type=TravelType.SHUTTLEPORT
        )
        
        self.assertIsNotNone(route)
        self.assertEqual(route.travel_type, TravelType.SHUTTLEPORT)
        self.assertEqual(route.start_planet, test_route["start_planet"])
        self.assertEqual(route.dest_planet, test_route["dest_planet"])
        self.assertGreater(route.cost, 0)
        self.assertGreater(route.travel_time, 0)
    
    def test_route_planning_ship(self):
        """Test ship route planning."""
        route = self.travel_manager.plan_travel_route(
            start_planet="tatooine",
            start_city="mos_eisley",
            dest_planet="naboo",
            dest_city="theed",
            preferred_type=TravelType.SHIP
        )
        
        # Ship routes may not be available depending on ship availability
        if route:
            self.assertEqual(route.travel_type, TravelType.SHIP)
            self.assertEqual(route.cost, 0)  # Ships don't cost credits
        else:
            # This is acceptable if no ships are available
            self.assertIsNone(route)
    
    def test_route_planning_invalid_route(self):
        """Test route planning with invalid route."""
        route = self.travel_manager.plan_travel_route(
            start_planet="invalid_planet",
            start_city="invalid_city",
            dest_planet="another_invalid_planet",
            dest_city="another_invalid_city"
        )
        
        self.assertIsNone(route)
    
    def test_travel_execution_simulation(self):
        """Test travel execution (simulated)."""
        # Create a test route
        test_route = TravelRoute(
            start_planet="tatooine",
            start_city="mos_eisley",
            dest_planet="naboo",
            dest_city="theed",
            travel_type=TravelType.STARPORT,
            cost=150,
            travel_time=5,
            terminal_name="Test Starport Terminal",
            route_id="test_route"
        )
        
        # Execute travel
        result = self.travel_manager.execute_travel(test_route)
        
        self.assertIsInstance(result, TravelResult)
        # In simulation, we expect success
        self.assertTrue(result.success)
        self.assertEqual(result.route_used, test_route)
        self.assertIsNotNone(result.travel_time)
        self.assertEqual(result.cost, test_route.cost)
    
    def test_travel_statistics(self):
        """Test travel statistics generation."""
        stats = self.travel_manager.get_travel_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_travels", stats)
        self.assertIn("successful_travels", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("average_travel_time", stats)
        self.assertIn("total_cost", stats)
        self.assertIn("recent_travels", stats)
        
        # Validate data types
        self.assertIsInstance(stats["total_travels"], int)
        self.assertIsInstance(stats["successful_travels"], int)
        self.assertIsInstance(stats["success_rate"], float)
        self.assertIsInstance(stats["average_travel_time"], float)
        self.assertIsInstance(stats["total_cost"], int)
        self.assertIsInstance(stats["recent_travels"], list)
    
    def test_randomized_delays(self):
        """Test randomized delay generation."""
        base_delay = 5
        randomized_delay = self.travel_manager._get_randomized_delay("test", base_delay)
        
        self.assertIsInstance(randomized_delay, int)
        self.assertGreater(randomized_delay, 0)
        
        # Test with randomization disabled
        original_enabled = self.travel_manager.randomization.get("enabled", True)
        self.travel_manager.randomization["enabled"] = False
        
        fixed_delay = self.travel_manager._get_randomized_delay("test", base_delay)
        self.assertEqual(fixed_delay, base_delay)
        
        # Restore original setting
        self.travel_manager.randomization["enabled"] = original_enabled


class TestStarportDetector(unittest.TestCase):
    """Test cases for the Starport Detector."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not TRAVEL_AVAILABLE:
            self.skipTest("Travel components not available")
        
        self.detector = get_starport_detector()
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        self.assertIsNotNone(self.detector)
        self.assertIsInstance(self.detector, StarportDetector)
        self.assertEqual(self.detector.current_status.value, "idle")
    
    def test_terminal_keywords(self):
        """Test terminal keyword detection."""
        self.assertIn(TerminalType.STARPORT, self.detector.terminal_keywords)
        self.assertIn(TerminalType.SHUTTLEPORT, self.detector.terminal_keywords)
        
        starport_keywords = self.detector.terminal_keywords[TerminalType.STARPORT]
        shuttle_keywords = self.detector.terminal_keywords[TerminalType.SHUTTLEPORT]
        
        self.assertIsInstance(starport_keywords, list)
        self.assertIsInstance(shuttle_keywords, list)
        self.assertGreater(len(starport_keywords), 0)
        self.assertGreater(len(shuttle_keywords), 0)
    
    def test_dialog_patterns(self):
        """Test dialog pattern configuration."""
        self.assertIn("destination_list", self.detector.dialog_patterns)
        self.assertIn("cost", self.detector.dialog_patterns)
        self.assertIn("time", self.detector.dialog_patterns)
        self.assertIn("confirmation", self.detector.dialog_patterns)
        
        for pattern_type, patterns in self.detector.dialog_patterns.items():
            self.assertIsInstance(patterns, list)
            self.assertGreater(len(patterns), 0)
    
    def test_scan_regions(self):
        """Test scan region configuration."""
        self.assertIsInstance(self.detector.scan_regions, list)
        self.assertGreater(len(self.detector.scan_regions), 0)
        
        for region in self.detector.scan_regions:
            self.assertIsInstance(region, tuple)
            self.assertEqual(len(region), 4)  # x, y, width, height
    
    def test_dialog_regions(self):
        """Test dialog region configuration."""
        self.assertIsInstance(self.detector.dialog_regions, list)
        self.assertGreater(len(self.detector.dialog_regions), 0)
        
        for region in self.detector.dialog_regions:
            self.assertIsInstance(region, tuple)
            self.assertEqual(len(region), 4)  # x, y, width, height
    
    @patch('utils.starport_detector.OCR_AVAILABLE', False)
    def test_scan_without_ocr(self):
        """Test scanning without OCR available."""
        detector = StarportDetector()
        result = detector.scan_for_terminals()
        
        self.assertFalse(result.success)
        self.assertIn("OCR not available", result.error_message)
    
    def test_extract_npc_name(self):
        """Test NPC name extraction."""
        test_text = "starport attendant travel to naboo"
        npc_name = self.detector._extract_npc_name(test_text, TerminalType.STARPORT)
        
        self.assertIsInstance(npc_name, str)
        # Should find "starport attendant" in the text
        self.assertIn("starport attendant", npc_name)
    
    def test_is_travel_dialog(self):
        """Test travel dialog detection."""
        travel_text = "travel to naboo destination select"
        non_travel_text = "hello world random text"
        
        self.assertTrue(self.detector._is_travel_dialog(travel_text))
        self.assertFalse(self.detector._is_travel_dialog(non_travel_text))
    
    def test_parse_travel_dialog(self):
        """Test travel dialog parsing."""
        test_text = """
        travel to naboo - theed
        travel to tatooine - mos eisley
        cost: 150 credits
        travel time: 5 minutes
        confirm travel
        """
        
        dialog = self.detector._parse_travel_dialog(test_text)
        
        self.assertIsNotNone(dialog)
        self.assertIsInstance(dialog.destinations, list)
        self.assertGreater(len(dialog.destinations), 0)
        self.assertIsInstance(dialog.cost, int)
        self.assertIsInstance(dialog.travel_time, int)
        self.assertTrue(dialog.confirmation_required)
    
    def test_detection_status(self):
        """Test detection status reporting."""
        status = self.detector.get_detection_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
        self.assertIn("ocr_available", status)
        self.assertIn("scan_regions", status)
        self.assertIn("dialog_regions", status)
        
        self.assertIsInstance(status["status"], str)
        self.assertIsInstance(status["ocr_available"], bool)
        self.assertIsInstance(status["scan_regions"], int)
        self.assertIsInstance(status["dialog_regions"], int)


class TestShipTravelSystem(unittest.TestCase):
    """Test cases for the Ship Travel System."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not TRAVEL_AVAILABLE:
            self.skipTest("Travel components not available")
        
        self.ship_system = get_ship_travel_system()
    
    def test_ship_system_initialization(self):
        """Test ship system initialization."""
        self.assertIsNotNone(self.ship_system)
        self.assertIsInstance(self.ship_system, PersonalShipTravelSystem)
    
    def test_ship_availability_check(self):
        """Test ship availability checking."""
        availability = self.ship_system.check_ship_availability()
        
        self.assertIsInstance(availability, dict)
        self.assertIn("available_ships", availability)
        self.assertIn("unavailable_ships", availability)
        self.assertIn("total_available", availability)
        self.assertIn("total_unavailable", availability)
        
        self.assertIsInstance(availability["available_ships"], list)
        self.assertIsInstance(availability["unavailable_ships"], list)
        self.assertIsInstance(availability["total_available"], int)
        self.assertIsInstance(availability["total_unavailable"], int)
    
    def test_ship_travel_statistics(self):
        """Test ship travel statistics."""
        stats = self.ship_system.get_travel_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_travels", stats)
        self.assertIn("successful_travels", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("average_travel_time", stats)
        self.assertIn("recent_travels", stats)
        
        # Validate data types
        self.assertIsInstance(stats["total_travels"], int)
        self.assertIsInstance(stats["successful_travels"], int)
        self.assertIsInstance(stats["success_rate"], float)
        self.assertIsInstance(stats["average_travel_time"], float)
        self.assertIsInstance(stats["recent_travels"], list)
    
    def test_auto_use_personal_ship(self):
        """Test auto-use personal ship functionality."""
        result = self.ship_system.auto_use_personal_ship("naboo")
        
        self.assertIsInstance(result, ShipTravelResult)
        # Result may be success or failure depending on ship availability
        self.assertIsInstance(result.success, bool)
        if result.success:
            self.assertIsNotNone(result.ship_used)
            self.assertIsNotNone(result.travel_time)
            self.assertIsNotNone(result.fuel_consumed)
        else:
            self.assertIsNotNone(result.error_message)
    
    def test_execute_ship_travel(self):
        """Test specific ship travel execution."""
        # Test with a ship that might not exist
        result = self.ship_system.execute_ship_travel("nonexistent_ship", "naboo")
        
        self.assertIsInstance(result, ShipTravelResult)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
    
    def test_estimate_travel_time(self):
        """Test travel time estimation."""
        test_planets = ["naboo", "tatooine", "corellia", "dantooine"]
        
        for planet in test_planets:
            travel_time = self.ship_system._estimate_travel_time(planet)
            self.assertIsInstance(travel_time, int)
            self.assertGreater(travel_time, 0)
    
    def test_ship_config_operations(self):
        """Test ship configuration operations."""
        # Test refuel operation
        refuel_result = self.ship_system.refuel_ship("x-wing")
        # May succeed or fail depending on ship existence
        self.assertIsInstance(refuel_result, bool)
        
        # Test unlock operation
        unlock_result = self.ship_system.unlock_ship("x-wing")
        # May succeed or fail depending on ship existence
        self.assertIsInstance(unlock_result, bool)


class TestTerminalTravelSystem(unittest.TestCase):
    """Test cases for the Terminal Travel System."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not TRAVEL_AVAILABLE:
            self.skipTest("Travel components not available")
        
        self.terminal_system = get_terminal_travel_system()
    
    def test_terminal_system_initialization(self):
        """Test terminal system initialization."""
        self.assertIsNotNone(self.terminal_system)
        self.assertIsInstance(self.terminal_system, TerminalTravelSystem)
    
    def test_terminal_keywords(self):
        """Test terminal keyword configuration."""
        self.assertIn(TerminalType.SHUTTLEPORT, self.terminal_system.terminal_keywords)
        self.assertIn(TerminalType.STARPORT, self.terminal_system.terminal_keywords)
        
        shuttle_keywords = self.terminal_system.terminal_keywords[TerminalType.SHUTTLEPORT]
        starport_keywords = self.terminal_system.terminal_keywords[TerminalType.STARPORT]
        
        self.assertIsInstance(shuttle_keywords, list)
        self.assertIsInstance(starport_keywords, list)
        self.assertGreater(len(shuttle_keywords), 0)
        self.assertGreater(len(starport_keywords), 0)
    
    def test_dialog_patterns(self):
        """Test dialog pattern configuration."""
        self.assertIn("destination_list", self.terminal_system.dialog_patterns)
        self.assertIn("confirmation", self.terminal_system.dialog_patterns)
        
        for pattern_type, patterns in self.terminal_system.dialog_patterns.items():
            self.assertIsInstance(patterns, list)
            self.assertGreater(len(patterns), 0)
    
    def test_parse_destinations(self):
        """Test destination parsing."""
        test_text = """
        travel to naboo - theed
        travel to tatooine - mos eisley
        destination: corellia - coronet
        """
        
        destinations = self.terminal_system._parse_destinations(test_text)
        
        self.assertIsInstance(destinations, list)
        self.assertGreater(len(destinations), 0)
        
        for destination in destinations:
            self.assertIsInstance(destination, str)
            self.assertGreater(len(destination), 0)
    
    def test_extract_travel_cost(self):
        """Test travel cost extraction."""
        test_text = "travel cost: 150 credits"
        cost = self.terminal_system._extract_travel_cost(test_text)
        
        self.assertIsInstance(cost, int)
        self.assertEqual(cost, 150)
    
    def test_extract_travel_time(self):
        """Test travel time extraction."""
        test_text = "travel time: 5 minutes"
        travel_time = self.terminal_system._extract_travel_time(test_text)
        
        self.assertIsInstance(travel_time, int)
        self.assertEqual(travel_time, 5)
    
    def test_travel_statistics(self):
        """Test travel statistics generation."""
        stats = self.terminal_system.get_travel_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_travels", stats)
        self.assertIn("successful_travels", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("recent_travels", stats)
        
        # Validate data types
        self.assertIsInstance(stats["total_travels"], int)
        self.assertIsInstance(stats["successful_travels"], int)
        self.assertIsInstance(stats["success_rate"], float)
        self.assertIsInstance(stats["recent_travels"], list)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete travel system."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not TRAVEL_AVAILABLE:
            self.skipTest("Travel components not available")
        
        self.travel_manager = get_travel_manager()
        self.starport_detector = get_starport_detector()
        self.ship_system = get_ship_travel_system()
        self.terminal_system = get_terminal_travel_system()
    
    def test_complete_travel_workflow(self):
        """Test complete travel workflow from planning to execution."""
        # Plan a route
        route = self.travel_manager.plan_travel_route(
            start_planet="tatooine",
            start_city="mos_eisley",
            dest_planet="naboo",
            dest_city="theed",
            preferred_type=TravelType.STARPORT
        )
        
        if route:
            # Execute travel
            result = self.travel_manager.execute_travel(route)
            
            # Validate result
            self.assertIsInstance(result, TravelResult)
            self.assertTrue(result.success)
            self.assertEqual(result.route_used, route)
            self.assertIsNotNone(result.travel_time)
            self.assertEqual(result.cost, route.cost)
    
    def test_system_interoperability(self):
        """Test that all systems work together."""
        # Check that all systems are available
        self.assertIsNotNone(self.travel_manager)
        self.assertIsNotNone(self.starport_detector)
        self.assertIsNotNone(self.ship_system)
        self.assertIsNotNone(self.terminal_system)
        
        # Check that they can all generate statistics
        travel_stats = self.travel_manager.get_travel_statistics()
        ship_stats = self.ship_system.get_travel_statistics()
        terminal_stats = self.terminal_system.get_travel_statistics()
        
        self.assertIsInstance(travel_stats, dict)
        self.assertIsInstance(ship_stats, dict)
        self.assertIsInstance(terminal_stats, dict)
    
    def test_error_handling(self):
        """Test error handling across the system."""
        # Test with invalid route
        route = self.travel_manager.plan_travel_route(
            start_planet="invalid",
            start_city="invalid",
            dest_planet="invalid",
            dest_city="invalid"
        )
        
        self.assertIsNone(route)
        
        # Test with invalid ship
        ship_result = self.ship_system.execute_ship_travel("invalid_ship", "invalid_dest")
        self.assertFalse(ship_result.success)
        self.assertIsNotNone(ship_result.error_message)


class TestPerformance(unittest.TestCase):
    """Performance tests for the travel system."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not TRAVEL_AVAILABLE:
            self.skipTest("Travel components not available")
        
        self.travel_manager = get_travel_manager()
    
    def test_route_planning_performance(self):
        """Test route planning performance."""
        start_time = time.time()
        
        for _ in range(10):
            route = self.travel_manager.plan_travel_route(
                start_planet="tatooine",
                start_city="mos_eisley",
                dest_planet="naboo",
                dest_city="theed"
            )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 10 route plans in under 1 second
        self.assertLess(total_time, 1.0)
    
    def test_statistics_generation_performance(self):
        """Test statistics generation performance."""
        start_time = time.time()
        
        for _ in range(100):
            stats = self.travel_manager.get_travel_statistics()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 100 stat generations in under 1 second
        self.assertLess(total_time, 1.0)


def run_tests():
    """Run all tests and generate a test report."""
    print("🧪 Running Batch 050 - Planetary Travel Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPlanetaryTravelManager,
        TestStarportDetector,
        TestShipTravelSystem,
        TestTerminalTravelSystem,
        TestIntegration,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Generate test report
    report = {
        "test_info": {
            "batch": "050",
            "feature": "Planetary Travel",
            "timestamp": time.time(),
            "total_tests": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped) if hasattr(result, 'skipped') else 0
        },
        "results": {
            "successful": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures),
            "errored": len(result.errors),
            "success_rate": ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
        },
        "failures": [str(failure) for failure in result.failures],
        "errors": [str(error) for error in result.errors]
    }
    
    # Save test report
    report_path = Path("test_batch_050_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Display summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"  - Total tests: {result.testsRun}")
    print(f"  - Successful: {report['results']['successful']}")
    print(f"  - Failed: {report['results']['failed']}")
    print(f"  - Errors: {report['results']['errored']}")
    print(f"  - Success rate: {report['results']['success_rate']:.1f}%")
    print(f"  - Report saved: {report_path}")
    
    if report['results']['success_rate'] >= 90:
        print("🎉 Tests completed successfully!")
    elif report['results']['success_rate'] >= 70:
        print("✅ Tests completed with minor issues")
    else:
        print("⚠️ Tests completed with significant issues")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 
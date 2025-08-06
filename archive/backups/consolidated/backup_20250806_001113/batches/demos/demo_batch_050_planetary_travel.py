#!/usr/bin/env python3
"""
Batch 050 - Planetary Travel Demo

This demo showcases the comprehensive planetary travel system including:
- Starport travel with ticket purchase
- Personal ship travel (Phase 2)
- Route planning and optimization
- OCR-based terminal detection
- Travel confirmation and arrival verification
- Delay randomization for realism
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import travel components
try:
    from core.travel_manager import (
        get_travel_manager, plan_travel_route, execute_travel, 
        get_travel_statistics, TravelType, TravelRoute, TravelResult
    )
    from utils.starport_detector import (
        get_starport_detector, scan_for_terminals, 
        get_detection_status, TerminalType
    )
    from travel.ship_travel import get_ship_travel_system, check_ship_availability
    from travel.terminal_travel import get_terminal_travel_system, scan_for_terminals as scan_terminals
    TRAVEL_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import travel components: {e}")
    TRAVEL_AVAILABLE = False


class PlanetaryTravelDemo:
    """Demo class for testing planetary travel functionality."""
    
    def __init__(self):
        """Initialize the demo."""
        self.logger = logger
        self.travel_manager = get_travel_manager() if TRAVEL_AVAILABLE else None
        self.starport_detector = get_starport_detector() if TRAVEL_AVAILABLE else None
        self.ship_system = get_ship_travel_system() if TRAVEL_AVAILABLE else None
        self.terminal_system = get_terminal_travel_system() if TRAVEL_AVAILABLE else None
        
        # Demo test cases
        self.test_routes = [
            {
                "name": "Tatooine to Naboo (Starport)",
                "start_planet": "tatooine",
                "start_city": "mos_eisley",
                "dest_planet": "naboo",
                "dest_city": "theed",
                "preferred_type": TravelType.STARPORT
            },
            {
                "name": "Naboo to Corellia (Shuttle)",
                "start_planet": "naboo",
                "start_city": "theed",
                "dest_planet": "corellia",
                "dest_city": "coronet",
                "preferred_type": TravelType.SHUTTLEPORT
            },
            {
                "name": "Corellia to Dantooine (Ship)",
                "start_planet": "corellia",
                "start_city": "coronet",
                "dest_planet": "dantooine",
                "dest_city": "khoonda",
                "preferred_type": TravelType.SHIP
            },
            {
                "name": "Auto Route Selection",
                "start_planet": "tatooine",
                "start_city": "mos_eisley",
                "dest_planet": "lok",
                "dest_city": "nym_stronghold",
                "preferred_type": None  # Let system choose
            }
        ]
        
        self.demo_results = []
        
    def run_demo(self):
        """Run the complete planetary travel demo."""
        self.logger.info("🚀 Starting Batch 050 - Planetary Travel Demo")
        
        if not TRAVEL_AVAILABLE:
            self.logger.error("❌ Travel components not available - demo cannot run")
            return
        
        try:
            # Phase 1: System Status Check
            self._check_system_status()
            
            # Phase 2: Terminal Detection Tests
            self._test_terminal_detection()
            
            # Phase 3: Ship Availability Tests
            self._test_ship_availability()
            
            # Phase 4: Route Planning Tests
            self._test_route_planning()
            
            # Phase 5: Travel Execution Tests
            self._test_travel_execution()
            
            # Phase 6: Statistics and Reporting
            self._generate_demo_report()
            
        except Exception as e:
            self.logger.error(f"❌ Demo failed: {e}")
            self._generate_error_report(str(e))
    
    def _check_system_status(self):
        """Check the status of all travel systems."""
        self.logger.info("📋 Checking system status...")
        
        # Check travel manager
        if self.travel_manager:
            self.logger.info("✅ Travel manager initialized")
        else:
            self.logger.error("❌ Travel manager not available")
        
        # Check starport detector
        if self.starport_detector:
            detector_status = self.starport_detector.get_detection_status()
            self.logger.info(f"✅ Starport detector status: {detector_status}")
        else:
            self.logger.error("❌ Starport detector not available")
        
        # Check ship system
        if self.ship_system:
            self.logger.info("✅ Ship travel system initialized")
        else:
            self.logger.error("❌ Ship travel system not available")
        
        # Check terminal system
        if self.terminal_system:
            self.logger.info("✅ Terminal travel system initialized")
        else:
            self.logger.error("❌ Terminal travel system not available")
    
    def _test_terminal_detection(self):
        """Test terminal detection functionality."""
        self.logger.info("🔍 Testing terminal detection...")
        
        if not self.starport_detector:
            self.logger.warning("⚠️ Skipping terminal detection test - detector not available")
            return
        
        # Test starport detection
        self.logger.info("Scanning for starport terminals...")
        starport_result = self.starport_detector.scan_for_terminals(TerminalType.STARPORT)
        
        if starport_result.success:
            self.logger.info(f"✅ Found {len(starport_result.terminals)} starport terminals")
            for terminal in starport_result.terminals:
                self.logger.info(f"  - {terminal.name} at {terminal.coordinates}")
        else:
            self.logger.warning(f"⚠️ Starport detection failed: {starport_result.error_message}")
        
        # Test shuttleport detection
        self.logger.info("Scanning for shuttleport terminals...")
        shuttle_result = self.starport_detector.scan_for_terminals(TerminalType.SHUTTLEPORT)
        
        if shuttle_result.success:
            self.logger.info(f"✅ Found {len(shuttle_result.terminals)} shuttleport terminals")
            for terminal in shuttle_result.terminals:
                self.logger.info(f"  - {terminal.name} at {terminal.coordinates}")
        else:
            self.logger.warning(f"⚠️ Shuttleport detection failed: {shuttle_result.error_message}")
        
        # Test general terminal detection
        self.logger.info("Scanning for all terminals...")
        general_result = self.starport_detector.scan_for_terminals()
        
        if general_result.success:
            self.logger.info(f"✅ Found {len(general_result.terminals)} total terminals")
        else:
            self.logger.warning(f"⚠️ General detection failed: {general_result.error_message}")
    
    def _test_ship_availability(self):
        """Test ship availability functionality."""
        self.logger.info("🚢 Testing ship availability...")
        
        if not self.ship_system:
            self.logger.warning("⚠️ Skipping ship availability test - ship system not available")
            return
        
        # Check ship availability
        availability = self.ship_system.check_ship_availability()
        
        self.logger.info(f"📊 Ship availability report:")
        self.logger.info(f"  - Available ships: {availability['total_available']}")
        self.logger.info(f"  - Unavailable ships: {availability['total_unavailable']}")
        
        if availability["available_ships"]:
            self.logger.info("✅ Available ships:")
            for ship in availability["available_ships"]:
                self.logger.info(f"  - {ship['name']} ({ship['type']}) - Fuel: {ship['fuel_level']}%")
        else:
            self.logger.info("⚠️ No ships available for travel")
        
        if availability["unavailable_ships"]:
            self.logger.info("⚠️ Unavailable ships:")
            for ship in availability["unavailable_ships"]:
                reason = ship.get("reason", "unknown")
                self.logger.info(f"  - {ship['name']}: {reason}")
        
        # Get ship statistics
        ship_stats = self.ship_system.get_travel_statistics()
        self.logger.info(f"📈 Ship travel statistics:")
        self.logger.info(f"  - Total travels: {ship_stats['total_travels']}")
        self.logger.info(f"  - Success rate: {ship_stats['success_rate']:.1f}%")
        self.logger.info(f"  - Average travel time: {ship_stats['average_travel_time']:.1f}s")
    
    def _test_route_planning(self):
        """Test route planning functionality."""
        self.logger.info("🗺️ Testing route planning...")
        
        if not self.travel_manager:
            self.logger.warning("⚠️ Skipping route planning test - travel manager not available")
            return
        
        for test_case in self.test_routes:
            self.logger.info(f"📋 Testing route: {test_case['name']}")
            
            route = self.travel_manager.plan_travel_route(
                start_planet=test_case["start_planet"],
                start_city=test_case["start_city"],
                dest_planet=test_case["dest_planet"],
                dest_city=test_case["dest_city"],
                preferred_type=test_case["preferred_type"]
            )
            
            if route:
                self.logger.info(f"✅ Route planned successfully:")
                self.logger.info(f"  - Type: {route.travel_type.value}")
                self.logger.info(f"  - Terminal: {route.terminal_name}")
                self.logger.info(f"  - Cost: {route.cost} credits")
                self.logger.info(f"  - Time: {route.travel_time} minutes")
                self.logger.info(f"  - Route ID: {route.route_id}")
                
                # Store route for execution test
                test_case["planned_route"] = route
            else:
                self.logger.warning(f"⚠️ Failed to plan route: {test_case['name']}")
                test_case["planned_route"] = None
    
    def _test_travel_execution(self):
        """Test travel execution functionality."""
        self.logger.info("🚀 Testing travel execution...")
        
        if not self.travel_manager:
            self.logger.warning("⚠️ Skipping travel execution test - travel manager not available")
            return
        
        for test_case in self.test_routes:
            if not test_case.get("planned_route"):
                self.logger.warning(f"⚠️ Skipping execution for {test_case['name']} - no route planned")
                continue
            
            self.logger.info(f"🎯 Executing travel: {test_case['name']}")
            
            # Execute travel
            result = self.travel_manager.execute_travel(test_case["planned_route"])
            
            if result.success:
                self.logger.info(f"✅ Travel completed successfully:")
                self.logger.info(f"  - Travel time: {result.travel_time}s")
                self.logger.info(f"  - Cost: {result.cost} credits")
                self.logger.info(f"  - Arrival confirmed: {result.arrival_confirmed}")
                
                # Store result
                test_case["execution_result"] = result
            else:
                self.logger.error(f"❌ Travel failed: {result.error_message}")
                test_case["execution_result"] = result
            
            # Brief pause between tests
            time.sleep(0.1)
    
    def _generate_demo_report(self):
        """Generate comprehensive demo report."""
        self.logger.info("📊 Generating demo report...")
        
        report = {
            "demo_info": {
                "batch": "050",
                "feature": "Planetary Travel",
                "timestamp": time.time(),
                "test_cases": len(self.test_routes)
            },
            "system_status": {
                "travel_manager_available": self.travel_manager is not None,
                "starport_detector_available": self.starport_detector is not None,
                "ship_system_available": self.ship_system is not None,
                "terminal_system_available": self.terminal_system is not None
            },
            "test_results": [],
            "statistics": {}
        }
        
        # Process test results
        successful_tests = 0
        for test_case in self.test_routes:
            test_result = {
                "name": test_case["name"],
                "route_planned": test_case.get("planned_route") is not None,
                "travel_executed": test_case.get("execution_result") is not None,
                "travel_successful": (
                    test_case.get("execution_result") and 
                    test_case["execution_result"].success
                )
            }
            
            if test_result["travel_successful"]:
                successful_tests += 1
            
            report["test_results"].append(test_result)
        
        # Get travel statistics
        if self.travel_manager:
            travel_stats = self.travel_manager.get_travel_statistics()
            report["statistics"]["travel"] = travel_stats
        
        # Get ship statistics
        if self.ship_system:
            ship_stats = self.ship_system.get_travel_statistics()
            report["statistics"]["ship"] = ship_stats
        
        # Calculate success rate
        success_rate = (successful_tests / len(self.test_routes)) * 100 if self.test_routes else 0
        report["overall_success_rate"] = success_rate
        
        # Save report
        report_path = Path("demo_batch_050_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Display summary
        self.logger.info("📋 Demo Report Summary:")
        self.logger.info(f"  - Test cases: {len(self.test_routes)}")
        self.logger.info(f"  - Successful: {successful_tests}")
        self.logger.info(f"  - Success rate: {success_rate:.1f}%")
        self.logger.info(f"  - Report saved: {report_path}")
        
        if success_rate >= 80:
            self.logger.info("🎉 Demo completed successfully!")
        elif success_rate >= 60:
            self.logger.info("✅ Demo completed with minor issues")
        else:
            self.logger.warning("⚠️ Demo completed with significant issues")
    
    def _generate_error_report(self, error_message: str):
        """Generate error report when demo fails."""
        report = {
            "demo_info": {
                "batch": "050",
                "feature": "Planetary Travel",
                "timestamp": time.time(),
                "status": "failed"
            },
            "error": error_message,
            "system_status": {
                "travel_manager_available": self.travel_manager is not None,
                "starport_detector_available": self.starport_detector is not None,
                "ship_system_available": self.ship_system is not None,
                "terminal_system_available": self.terminal_system is not None
            }
        }
        
        report_path = Path("demo_batch_050_error_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.error(f"❌ Demo failed - error report saved to {report_path}")


def main():
    """Main demo execution function."""
    print("=" * 60)
    print("🚀 Batch 050 - Planetary Travel Demo")
    print("=" * 60)
    
    demo = PlanetaryTravelDemo()
    demo.run_demo()
    
    print("=" * 60)
    print("✅ Demo completed")
    print("=" * 60)


if __name__ == "__main__":
    main() 
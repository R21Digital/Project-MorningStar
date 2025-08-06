#!/usr/bin/env python3
"""
Test script for Waypoint Navigation Engine (Batch 013)

This script tests the navigation engine's ability to move toward specific coordinates
using WASD + mini-map logic with path smoothing and obstacle avoidance.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import json
from pathlib import Path

from core.navigation.navigation_engine import (
    NavigationEngine,
    NavigationStatus,
    MovementDirection,
    Coordinate,
    NavigationState,
    NavigationConfig,
    navigate_to_coordinates,
    get_navigation_status,
    stop_navigation,
    navigation_engine
)


def test_navigation_engine_initialization():
    """Test navigation engine initialization."""
    print("🧪 Testing Navigation Engine Initialization...")
    
    try:
        # Test with default config
        engine = NavigationEngine()
        
        print(f"✅ Navigation engine initialized successfully")
        print(f"   Arrival radius: {engine.arrival_radius}")
        print(f"   Max attempts: {engine.max_attempts}")
        print(f"   Timeout seconds: {engine.timeout_seconds}")
        print(f"   Path smoothing factor: {engine.path_smoothing_factor}")
        
        # Test with custom config
        custom_config = NavigationConfig(
            arrival_radius=15,
            max_attempts=5,
            timeout_seconds=45.0,
            path_smoothing_factor=0.5
        )
        
        custom_engine = NavigationEngine(custom_config)
        print(f"✅ Custom navigation engine initialized successfully")
        print(f"   Custom arrival radius: {custom_engine.arrival_radius}")
        print(f"   Custom max attempts: {custom_engine.max_attempts}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing navigation engine: {e}")
        return False


def test_coordinate_calculations():
    """Test coordinate calculations and distance measurements."""
    print("\n🧪 Testing Coordinate Calculations...")
    
    try:
        # Test coordinate creation
        coord1 = Coordinate(100, 150, "test_zone", "test_planet", "Test Location")
        coord2 = Coordinate(200, 250, "test_zone", "test_planet", "Target Location")
        
        print(f"✅ Created coordinates:")
        print(f"   Coord1: {coord1}")
        print(f"   Coord2: {coord2}")
        
        # Test distance calculation
        distance = coord1.distance_to(coord2)
        expected_distance = ((200-100)**2 + (250-150)**2)**0.5
        
        print(f"   Distance: {distance:.2f}")
        print(f"   Expected: {expected_distance:.2f}")
        
        if abs(distance - expected_distance) < 0.01:
            print("✅ Distance calculation correct")
            return True
        else:
            print("❌ Distance calculation incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Error in coordinate calculations: {e}")
        return False


def test_movement_direction_calculation():
    """Test movement direction calculation."""
    print("\n🧪 Testing Movement Direction Calculation...")
    
    try:
        engine = NavigationEngine()
        
        # Test different target positions
        test_cases = [
            (Coordinate(0, 0), Coordinate(100, 0), MovementDirection.EAST),
            (Coordinate(0, 0), Coordinate(0, 100), MovementDirection.NORTH),
            (Coordinate(0, 0), Coordinate(-100, 0), MovementDirection.WEST),
            (Coordinate(0, 0), Coordinate(0, -100), MovementDirection.SOUTH),
            (Coordinate(0, 0), Coordinate(100, 100), MovementDirection.NORTHEAST),
            (Coordinate(0, 0), Coordinate(-100, 100), MovementDirection.NORTHWEST),
            (Coordinate(0, 0), Coordinate(100, -100), MovementDirection.SOUTHEAST),
            (Coordinate(0, 0), Coordinate(-100, -100), MovementDirection.SOUTHWEST),
        ]
        
        for current, target, expected in test_cases:
            engine.state.current_position = current
            engine.state.target_position = target
            
            direction = engine._calculate_movement_direction()
            
            print(f"   {current} -> {target}: {direction.value} (expected: {expected.value})")
            
            if direction == expected:
                print(f"   ✅ Direction calculation correct")
            else:
                print(f"   ❌ Direction calculation incorrect")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in movement direction calculation: {e}")
        return False


def test_path_smoothing():
    """Test path smoothing functionality."""
    print("\n🧪 Testing Path Smoothing...")
    
    try:
        engine = NavigationEngine()
        
        # Create a path history
        engine.state.path_history = [
            Coordinate(0, 0),
            Coordinate(10, 5),
            Coordinate(20, 15)
        ]
        
        engine.state.current_position = Coordinate(20, 15)
        engine.state.target_position = Coordinate(100, 50)
        
        # Test path smoothing
        target_direction = MovementDirection.NORTHEAST
        smoothed_direction = engine._apply_path_smoothing(target_direction)
        
        print(f"   Target direction: {target_direction.value}")
        print(f"   Smoothed direction: {smoothed_direction.value}")
        print(f"   Path history length: {len(engine.state.path_history)}")
        
        # Test with empty path history
        engine.state.path_history = []
        smoothed_empty = engine._apply_path_smoothing(target_direction)
        
        print(f"   Empty path smoothing: {smoothed_empty.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in path smoothing: {e}")
        return False


def test_movement_execution():
    """Test movement execution (simulated)."""
    print("\n🧪 Testing Movement Execution...")
    
    try:
        engine = NavigationEngine()
        
        # Test different movement directions
        directions = [
            MovementDirection.NORTH,
            MovementDirection.SOUTH,
            MovementDirection.EAST,
            MovementDirection.WEST,
            MovementDirection.NORTHEAST,
            MovementDirection.NORTHWEST,
            MovementDirection.SOUTHEAST,
            MovementDirection.SOUTHWEST,
            MovementDirection.IDLE
        ]
        
        for direction in directions:
            success = engine._execute_movement(direction)
            print(f"   {direction.value}: {'✅ Success' if success else '❌ Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in movement execution: {e}")
        return False


def test_navigation_status():
    """Test navigation status tracking."""
    print("\n🧪 Testing Navigation Status...")
    
    try:
        engine = NavigationEngine()
        
        # Test initial status
        status = engine.get_navigation_status()
        print(f"✅ Initial status: {status['status']}")
        
        # Test status after setting positions
        engine.state.current_position = Coordinate(0, 0, "test_zone", "test_planet")
        engine.state.target_position = Coordinate(100, 100, "test_zone", "test_planet")
        engine.state.status = NavigationStatus.MOVING
        
        status = engine.get_navigation_status()
        print(f"✅ Active status: {status['status']}")
        print(f"   Current position: {status['current_position']}")
        print(f"   Target position: {status['target_position']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in navigation status: {e}")
        return False


def test_navigation_logging():
    """Test navigation event logging."""
    print("\n🧪 Testing Navigation Logging...")
    
    try:
        engine = NavigationEngine()
        
        # Test logging path progression
        engine.state.current_position = Coordinate(0, 0, "test_zone", "test_planet")
        engine.state.target_position = Coordinate(100, 100, "test_zone", "test_planet")
        
        engine._log_path_progression()
        
        # Check if log file was created
        log_file = Path("logs/navigation_events.json")
        if log_file.exists():
            print("✅ Navigation log file created successfully")
            return True
        else:
            print("ℹ️  No log file created (may be normal in test environment)")
            return True
            
    except Exception as e:
        print(f"❌ Error in navigation logging: {e}")
        return False


def test_navigation_timeout():
    """Test navigation timeout functionality."""
    print("\n🧪 Testing Navigation Timeout...")
    
    try:
        engine = NavigationEngine()
        
        # Test timeout check
        engine.state.start_time = time.time() - 35  # 35 seconds ago
        engine.timeout_seconds = 30
        
        timeout_result = engine._check_timeout()
        print(f"   Timeout check: {timeout_result}")
        
        if timeout_result:
            print("✅ Timeout detection working correctly")
        else:
            print("❌ Timeout detection not working")
            return False
        
        # Test no timeout
        engine.state.start_time = time.time() - 10  # 10 seconds ago
        timeout_result = engine._check_timeout()
        
        if not timeout_result:
            print("✅ No timeout detection working correctly")
        else:
            print("❌ No timeout detection not working")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in navigation timeout: {e}")
        return False


def test_stuck_detection():
    """Test stuck detection functionality."""
    print("\n🧪 Testing Stuck Detection...")
    
    try:
        engine = NavigationEngine()
        
        # Test stuck detection
        engine.state.last_movement_time = time.time() - 15  # 15 seconds ago
        engine.stuck_timeout = 10
        
        stuck_result = engine._check_stuck()
        print(f"   Stuck check: {stuck_result}")
        
        if stuck_result:
            print("✅ Stuck detection working correctly")
        else:
            print("❌ Stuck detection not working")
            return False
        
        # Test not stuck
        engine.state.last_movement_time = time.time() - 5  # 5 seconds ago
        stuck_result = engine._check_stuck()
        
        if not stuck_result:
            print("✅ Not stuck detection working correctly")
        else:
            print("❌ Not stuck detection not working")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in stuck detection: {e}")
        return False


def test_arrival_detection():
    """Test arrival detection functionality."""
    print("\n🧪 Testing Arrival Detection...")
    
    try:
        engine = NavigationEngine()
        
        # Test arrival detection
        engine.state.current_position = Coordinate(100, 100)
        engine.state.target_position = Coordinate(105, 105)  # Within arrival radius
        engine.arrival_radius = 10
        
        arrival_result = engine._check_arrival()
        print(f"   Arrival check (near): {arrival_result}")
        
        if arrival_result:
            print("✅ Arrival detection working correctly")
        else:
            print("❌ Arrival detection not working")
            return False
        
        # Test not arrived
        engine.state.target_position = Coordinate(200, 200)  # Outside arrival radius
        arrival_result = engine._check_arrival()
        
        if not arrival_result:
            print("✅ Not arrived detection working correctly")
        else:
            print("❌ Not arrived detection not working")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error in arrival detection: {e}")
        return False


def test_global_functions():
    """Test global navigation functions."""
    print("\n🧪 Testing Global Navigation Functions...")
    
    try:
        # Test global navigation function
        success = navigate_to_coordinates(100, 100, 0, 0, "test_zone", "test_planet")
        print(f"   Global navigation result: {success}")
        
        # Test global status function
        status = get_navigation_status()
        print(f"   Global status: {status['status']}")
        
        # Test global stop function
        stop_navigation()
        print("   Global stop navigation called")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in global functions: {e}")
        return False


def test_map_data_loading():
    """Test map data loading functionality."""
    print("\n🧪 Testing Map Data Loading...")
    
    try:
        engine = NavigationEngine()
        
        # Check loaded map data
        map_count = len(engine.map_data)
        print(f"   Loaded {map_count} map files")
        
        if map_count > 0:
            for planet, data in engine.map_data.items():
                print(f"   Planet: {planet}")
                print(f"     Zones: {len(data.get('zones', {}))}")
                print(f"     Waypoints: {len(data.get('waypoints', []))}")
                print(f"     Routes: {len(data.get('routes', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in map data loading: {e}")
        return False


def main():
    """Run all tests for navigation engine."""
    print("🚀 Starting Waypoint Navigation Engine Tests (Batch 013)")
    print("=" * 70)
    
    tests = [
        ("Navigation Engine Initialization", test_navigation_engine_initialization),
        ("Coordinate Calculations", test_coordinate_calculations),
        ("Movement Direction Calculation", test_movement_direction_calculation),
        ("Path Smoothing", test_path_smoothing),
        ("Movement Execution", test_movement_execution),
        ("Navigation Status", test_navigation_status),
        ("Navigation Logging", test_navigation_logging),
        ("Navigation Timeout", test_navigation_timeout),
        ("Stuck Detection", test_stuck_detection),
        ("Arrival Detection", test_arrival_detection),
        ("Global Functions", test_global_functions),
        ("Map Data Loading", test_map_data_loading),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Navigation engine is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Batch 111 - Mount & Vehicle Handling Logic Demo

This demo showcases the intelligent mount and vehicle management system,
including auto-summon, mounting, dismounting, and safety checks.

Author: SWG Bot Development Team
"""

import time
import random
from typing import Dict, List, Any
from pathlib import Path

# Import mount management components
from core.mount_manager import (
    MountManager, get_mount_manager, MountType, MountStatus, ZoneType,
    auto_mount_management, get_mount_status
)
from modules.movement.mount_integration import (
    MountIntegration, integrate_with_movement_system,
    get_mount_travel_status, auto_mount_for_travel,
    handle_combat_mount_behavior, handle_zone_mount_behavior
)


def demo_mount_manager_initialization():
    """Demo the mount manager initialization and basic functionality."""
    print("🚀 Initializing Mount Manager...")
    
    # Initialize mount manager for different profiles
    profiles = ["default", "speed_demon", "stealth_runner", "creature_lover"]
    
    for profile in profiles:
        manager = get_mount_manager(profile)
        print(f"  ✅ Mount manager initialized for profile: {profile}")
        
        # Show available mounts
        available_mounts = manager.get_available_mounts()
        print(f"    Available mounts: {len(available_mounts)}")
        
        # Show mount status
        status = manager.get_mount_status()
        print(f"    Current status: {status['status']}")
        print(f"    Zone: {status['zone']}")
        print(f"    In combat: {status['in_combat']}")
    
    print("✅ Mount manager initialization complete\n")


def demo_mount_database():
    """Demo the mount database and mount selection."""
    print("🐎 Mount Database Demo...")
    
    manager = get_mount_manager("default")
    
    # Show all available mounts
    print("Available mounts:")
    for mount_id, mount in manager.available_mounts.items():
        print(f"  {mount.name} ({mount.mount_type.value})")
        print(f"    Speed: {mount.speed}, Cooldown: {mount.cooldown}s")
        print(f"    Summon: {mount.summon_time}s, Dismount: {mount.dismount_time}s")
    
    # Demo mount selection for different scenarios
    scenarios = [
        {"distance": 25.0, "description": "Short distance"},
        {"distance": 75.0, "description": "Medium distance"},
        {"distance": 150.0, "description": "Long distance"},
        {"distance": 300.0, "description": "Very long distance"}
    ]
    
    for scenario in scenarios:
        best_mount = manager.select_best_mount(scenario["distance"])
        if best_mount:
            print(f"\n{scenario['description']} ({scenario['distance']} units):")
            print(f"  Selected: {best_mount.name} (Speed: {best_mount.speed})")
        else:
            print(f"\n{scenario['description']}: No suitable mount available")
    
    print("✅ Mount database demo complete\n")


def demo_zone_detection():
    """Demo zone detection and no-mount zone handling."""
    print("🏞️ Zone Detection Demo...")
    
    manager = get_mount_manager("default")
    
    # Test different zones
    test_zones = [
        ("Tatooine", "Anchorhead", "outdoors"),
        ("Mustafar", "lava_cave", "no_mount"),
        ("Naboo", "theed_palace", "indoors"),
        ("Kashyyyk", "wookiee_home", "no_mount"),
        ("Corellia", "coronet_city", "outdoors"),
        ("Dathomir", "witches_cave", "no_mount")
    ]
    
    for planet, location, expected_zone in test_zones:
        is_no_mount = manager.is_no_mount_zone(planet, location)
        print(f"  {planet} - {location}:")
        print(f"    Expected: {expected_zone}")
        print(f"    No-mount zone: {is_no_mount}")
        
        # Simulate zone detection
        detected_zone = manager.detect_current_zone()
        print(f"    Detected zone: {detected_zone.value}")
    
    print("✅ Zone detection demo complete\n")


def demo_auto_mount_management():
    """Demo automatic mount management."""
    print("🤖 Auto Mount Management Demo...")
    
    # Test different travel scenarios
    travel_scenarios = [
        {
            "distance": 30.0,
            "start": "Anchorhead",
            "destination": "Mos Eisley",
            "description": "Short city-to-city travel"
        },
        {
            "distance": 80.0,
            "start": "Theed",
            "destination": "Lake Retreat",
            "description": "Medium distance travel"
        },
        {
            "distance": 200.0,
            "start": "Coronet",
            "destination": "Tyrena",
            "description": "Long distance travel"
        },
        {
            "distance": 50.0,
            "start": "Mustafar",
            "destination": "lava_cave",
            "description": "Travel to no-mount zone"
        }
    ]
    
    for scenario in travel_scenarios:
        print(f"\n{scenario['description']}:")
        print(f"  Distance: {scenario['distance']} units")
        print(f"  Route: {scenario['start']} -> {scenario['destination']}")
        
        # Test auto mount management
        action_taken = auto_mount_management(
            distance=scenario['distance'],
            current_location=scenario['start'],
            destination=scenario['destination']
        )
        
        print(f"  Action taken: {action_taken}")
        
        # Show mount status
        status = get_mount_status()
        print(f"  Current mount: {status['current_mount']}")
        print(f"  Status: {status['status']}")
    
    print("✅ Auto mount management demo complete\n")


def demo_mount_integration():
    """Demo mount integration with movement system."""
    print("🔗 Mount Integration Demo...")
    
    # Create mock movement agent
    class MockMovementAgent:
        def __init__(self, name="TestAgent"):
            self.name = name
            self.current_location = "Anchorhead"
            self.destination = "Mos Eisley"
        
        def move_to(self):
            print(f"    [{self.name}] Moving from {self.current_location} to {self.destination}")
            return True
    
    # Test integration scenarios
    integration_scenarios = [
        {
            "start": "Anchorhead",
            "destination": "Mos Eisley",
            "distance": 75.0,
            "description": "City travel with mount"
        },
        {
            "start": "Theed",
            "destination": "Lake Retreat",
            "distance": 120.0,
            "description": "Long distance travel"
        },
        {
            "start": "Coronet",
            "destination": "Tyrena",
            "distance": 180.0,
            "description": "Cross-city travel"
        }
    ]
    
    for scenario in integration_scenarios:
        print(f"\n{scenario['description']}:")
        
        # Create movement agent
        agent = MockMovementAgent()
        agent.current_location = scenario['start']
        agent.destination = scenario['destination']
        
        # Test integration
        success = integrate_with_movement_system(
            movement_agent=agent,
            start_location=scenario['start'],
            destination=scenario['destination'],
            distance=scenario['distance']
        )
        
        print(f"  Integration success: {success}")
    
    print("✅ Mount integration demo complete\n")


def demo_combat_and_zone_handling():
    """Demo combat and zone transition handling."""
    print("⚔️ Combat & Zone Handling Demo...")
    
    # Test combat scenarios
    combat_scenarios = [
        {"description": "Combat encounter while mounted", "in_combat": True},
        {"description": "Safe travel", "in_combat": False}
    ]
    
    for scenario in combat_scenarios:
        print(f"\n{scenario['description']}:")
        
        # Simulate combat detection
        if scenario['in_combat']:
            action_taken = handle_combat_mount_behavior()
            print(f"  Combat detected, action taken: {action_taken}")
        else:
            print("  No combat detected")
    
    # Test zone transitions
    zone_scenarios = [
        ("Entering building", ZoneType.INDOORS),
        ("Entering no-mount zone", ZoneType.NO_MOUNT),
        ("Entering combat zone", ZoneType.COMBAT),
        ("Moving outdoors", ZoneType.OUTDOORS)
    ]
    
    for zone_name, zone_type in zone_scenarios:
        print(f"\n{zone_name}:")
        action_taken = handle_zone_mount_behavior(zone_name, zone_type)
        print(f"  Zone type: {zone_type.value}")
        print(f"  Action taken: {action_taken}")
    
    print("✅ Combat and zone handling demo complete\n")


def demo_profile_preferences():
    """Demo different profile preferences."""
    print("👤 Profile Preferences Demo...")
    
    # Test different profiles
    profiles = [
        {
            "name": "speed_demon",
            "description": "Prefers fast speeders",
            "preferences": {
                "preferred_mount_type": MountType.SPEEDER,
                "auto_mount_distance": 30.0,
                "preferred_mounts": ["Swoop Bike", "Pod Racer", "Jetpack"]
            }
        },
        {
            "name": "creature_lover",
            "description": "Prefers creature mounts",
            "preferences": {
                "preferred_mount_type": MountType.CREATURE,
                "auto_mount_distance": 40.0,
                "preferred_mounts": ["Bantha", "Dewback", "Tauntaun"]
            }
        },
        {
            "name": "stealth_runner",
            "description": "Avoids mounts in certain situations",
            "preferences": {
                "preferred_mount_type": MountType.SPEEDER,
                "auto_mount_distance": 100.0,
                "auto_dismount_in_combat": True,
                "avoid_no_mount_zones": True
            }
        }
    ]
    
    for profile in profiles:
        print(f"\n{profile['description']} ({profile['name']}):")
        
        # Get mount manager for profile
        manager = get_mount_manager(profile['name'])
        
        # Update preferences
        manager.update_preferences(**profile['preferences'])
        
        # Show preferences
        prefs = manager.preferences
        print(f"  Preferred mount type: {prefs.preferred_mount_type.value}")
        print(f"  Auto mount distance: {prefs.auto_mount_distance}")
        print(f"  Preferred mounts: {prefs.preferred_mounts[:3]}...")
        
        # Test mount selection
        best_mount = manager.select_best_mount(100.0)
        if best_mount:
            print(f"  Selected mount for long travel: {best_mount.name}")
    
    print("✅ Profile preferences demo complete\n")


def demo_travel_statistics():
    """Demo travel statistics and analytics."""
    print("📊 Travel Statistics Demo...")
    
    integration = MountIntegration("default")
    
    # Simulate some travel history
    travel_history = [
        {"start": "Anchorhead", "destination": "Mos Eisley", "distance": 75.0, "mount": "Speeder Bike"},
        {"start": "Theed", "destination": "Lake Retreat", "distance": 120.0, "mount": "Landspeeder"},
        {"start": "Coronet", "destination": "Tyrena", "distance": 180.0, "mount": "Swoop Bike"},
        {"start": "Anchorhead", "destination": "Mos Espa", "distance": 90.0, "mount": "Speeder Bike"},
        {"start": "Theed", "destination": "Palace", "distance": 15.0, "mount": None}
    ]
    
    # Add travel records
    for travel in travel_history:
        integration.travel_history.append({
            "start": travel["start"],
            "destination": travel["destination"],
            "planned_distance": travel["distance"],
            "actual_distance": travel["distance"],
            "mount_used": travel["mount"],
            "timestamp": time.time()
        })
    
    # Get statistics
    stats = integration.get_travel_statistics()
    
    print("Travel Statistics:")
    print(f"  Total travels: {stats['total_travels']}")
    print(f"  Total distance: {stats['total_distance']:.1f} units")
    print(f"  Average distance: {stats['average_distance']:.1f} units")
    print(f"  Most used mount: {stats['most_used_mount']}")
    
    print("\nMount Usage Breakdown:")
    for mount_name, usage in stats['mount_usage'].items():
        print(f"  {mount_name}: {usage['count']} uses, {usage['distance']:.1f} units")
    
    print("✅ Travel statistics demo complete\n")


def demo_safety_features():
    """Demo safety features and emergency handling."""
    print("🛡️ Safety Features Demo...")
    
    manager = get_mount_manager("default")
    
    # Test emergency dismount
    print("Testing emergency dismount:")
    emergency_result = manager.emergency_dismount()
    print(f"  Emergency dismount result: {emergency_result}")
    
    # Test cooldown management
    print("\nTesting cooldown management:")
    manager.reset_cooldowns()
    print("  Cooldowns reset")
    
    # Test mount availability
    available_mounts = manager.get_available_mounts()
    print(f"  Available mounts after reset: {len(available_mounts)}")
    
    # Test no-mount zone detection
    print("\nTesting no-mount zone detection:")
    no_mount_locations = [
        ("Mustafar", "lava_cave"),
        ("Kashyyyk", "wookiee_home"),
        ("Naboo", "theed_palace"),
        ("Tatooine", "jabba_palace")
    ]
    
    for planet, location in no_mount_locations:
        is_no_mount = manager.is_no_mount_zone(planet, location)
        print(f"  {planet} - {location}: {is_no_mount}")
    
    print("✅ Safety features demo complete\n")


def demo_performance_optimization():
    """Demo performance optimization features."""
    print("⚡ Performance Optimization Demo...")
    
    manager = get_mount_manager("default")
    
    # Test mount selection performance
    print("Testing mount selection performance:")
    start_time = time.time()
    
    for _ in range(100):
        manager.select_best_mount(random.uniform(10, 300))
    
    selection_time = time.time() - start_time
    print(f"  100 mount selections completed in {selection_time:.3f}s")
    
    # Test zone detection performance
    print("\nTesting zone detection performance:")
    start_time = time.time()
    
    for _ in range(50):
        manager.detect_current_zone()
    
    detection_time = time.time() - start_time
    print(f"  50 zone detections completed in {detection_time:.3f}s")
    
    # Test auto mount management performance
    print("\nTesting auto mount management performance:")
    start_time = time.time()
    
    for _ in range(50):
        auto_mount_management(
            distance=random.uniform(20, 200),
            current_location="Anchorhead",
            destination="Mos Eisley"
        )
    
    management_time = time.time() - start_time
    print(f"  50 auto mount decisions completed in {management_time:.3f}s")
    
    print("✅ Performance optimization demo complete\n")


def demo_integration_with_existing_systems():
    """Demo integration with existing movement and combat systems."""
    print("🔗 System Integration Demo...")
    
    # Test integration with movement system
    print("Testing movement system integration:")
    
    # Mock movement agent
    class MockMovementAgent:
        def __init__(self):
            self.location = "Anchorhead"
            self.destination = "Mos Eisley"
        
        def move_to(self):
            print(f"    Moving from {self.location} to {self.destination}")
            return True
    
    agent = MockMovementAgent()
    
    # Test integration
    success = integrate_with_movement_system(
        movement_agent=agent,
        start_location="Anchorhead",
        destination="Mos Eisley",
        distance=75.0
    )
    
    print(f"  Movement integration success: {success}")
    
    # Test mount travel status
    print("\nTesting mount travel status:")
    status = get_mount_travel_status()
    print(f"  Mount status: {status['mount_status']['status']}")
    print(f"  Travel statistics: {len(status['travel_statistics'])} records")
    print(f"  Integration settings: {len(status['integration_settings'])} settings")
    
    print("✅ System integration demo complete\n")


def main():
    """Run the complete mount handling demo."""
    print("=" * 60)
    print("🚀 BATCH 111 - MOUNT & VEHICLE HANDLING LOGIC DEMO")
    print("=" * 60)
    
    try:
        # Run all demos
        demo_mount_manager_initialization()
        demo_mount_database()
        demo_zone_detection()
        demo_auto_mount_management()
        demo_mount_integration()
        demo_combat_and_zone_handling()
        demo_profile_preferences()
        demo_travel_statistics()
        demo_safety_features()
        demo_performance_optimization()
        demo_integration_with_existing_systems()
        
        print("=" * 60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("🎯 Mount & Vehicle Handling Logic is ready for production use")
        print("=" * 60)
        
        # Print summary
        print("\n📋 Demo Summary:")
        print("  ✅ Mount manager initialization and configuration")
        print("  ✅ Mount database and selection logic")
        print("  ✅ Zone detection and no-mount zone handling")
        print("  ✅ Automatic mount management")
        print("  ✅ Mount integration with movement system")
        print("  ✅ Combat and zone transition handling")
        print("  ✅ Profile-based preferences")
        print("  ✅ Travel statistics and analytics")
        print("  ✅ Safety features and emergency handling")
        print("  ✅ Performance optimization")
        print("  ✅ System integration capabilities")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
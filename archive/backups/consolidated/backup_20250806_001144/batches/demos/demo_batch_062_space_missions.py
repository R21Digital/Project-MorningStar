#!/usr/bin/env python3
"""Demo script for Batch 062 - Smart Space Mission Support (Phase 1).

This script demonstrates the space mission functionality including:
- Space event detection via logs
- Mission type definitions (Patrol, Escort, Kill Target)
- Ship entry/exit functionality
- Terminal identification
- Combat simulation for Tansarii Point Station
- Integration with session_config.json space_mode settings
"""

import json
import time
from pathlib import Path
from typing import Dict, Any

from core.space_mission_manager import (
    SpaceMissionManager,
    SpaceMissionType,
    SpaceEventType,
    space_mission_manager
)
from modules.space_mode import space_mode
from utils.logging_utils import log_event


def demo_space_event_detection():
    """Demo space event detection from log text."""
    print("\n=== Space Event Detection Demo ===")
    
    # Test log texts that should trigger space events
    test_logs = [
        "Player entered ship x-wing",
        "Mission accepted: Patrol Sector Alpha",
        "Combat started with pirate vessel",
        "Terminal accessed: Mission Board",
        "Player exited ship x-wing",
        "Mission completed: Escort Merchant Vessel",
        "Ship boarded: transport_shuttle",
        "Battle ended with victory",
        "Space terminal interaction successful"
    ]
    
    manager = space_mission_manager
    
    for log_text in test_logs:
        print(f"\nTesting log: '{log_text}'")
        events = manager.detect_space_events(log_text)
        
        if events:
            for event in events:
                print(f"  ✓ Detected {event.event_type.value} event")
                print(f"    Location: {event.location}")
                print(f"    Timestamp: {event.timestamp}")
        else:
            print("  ✗ No space events detected")
    
    print(f"\nTotal events detected: {len(manager.events)}")


def demo_mission_creation():
    """Demo space mission creation and management."""
    print("\n=== Space Mission Creation Demo ===")
    
    manager = space_mission_manager
    
    # Create sample missions
    missions = [
        {
            "type": SpaceMissionType.PATROL,
            "name": "Sector Alpha Patrol",
            "description": "Patrol the Alpha sector for pirate activity",
            "credits_reward": 200,
            "experience_reward": 100,
            "ship_requirement": "x-wing"
        },
        {
            "type": SpaceMissionType.ESCORT,
            "name": "Merchant Escort",
            "description": "Escort merchant vessel through dangerous space",
            "credits_reward": 300,
            "experience_reward": 150,
            "ship_requirement": "millennium_falcon"
        },
        {
            "type": SpaceMissionType.KILL_TARGET,
            "name": "Bounty Hunt",
            "description": "Eliminate wanted criminal in asteroid belt",
            "credits_reward": 500,
            "experience_reward": 250,
            "ship_requirement": "x-wing"
        }
    ]
    
    created_missions = []
    for mission_data in missions:
        mission = manager.create_mission(
            mission_type=mission_data["type"],
            name=mission_data["name"],
            description=mission_data["description"],
            credits_reward=mission_data["credits_reward"],
            experience_reward=mission_data["experience_reward"],
            ship_requirement=mission_data["ship_requirement"]
        )
        created_missions.append(mission)
        print(f"  ✓ Created mission: {mission.name} ({mission.mission_id})")
        print(f"    Type: {mission.mission_type.value}")
        print(f"    Reward: {mission.credits_reward} credits, {mission.experience_reward} XP")
    
    print(f"\nTotal missions created: {len(created_missions)}")
    return created_missions


def demo_ship_operations():
    """Demo ship entry/exit functionality."""
    print("\n=== Ship Operations Demo ===")
    
    manager = space_mission_manager
    
    # Test ship entry
    ships = ["x-wing", "millennium_falcon", "transport_shuttle"]
    
    for ship in ships:
        print(f"\nTesting ship entry: {ship}")
        success = manager.enter_ship(ship)
        if success:
            print(f"  ✓ Successfully entered {ship}")
            print(f"    Current ship: {manager.current_ship}")
        else:
            print(f"  ✗ Failed to enter {ship}")
    
    # Test ship exit
    print(f"\nTesting ship exit")
    success = manager.exit_ship()
    if success:
        print(f"  ✓ Successfully exited ship")
        print(f"    Current ship: {manager.current_ship}")
    else:
        print(f"  ✗ Failed to exit ship")


def demo_terminal_identification():
    """Demo terminal identification functionality."""
    print("\n=== Terminal Identification Demo ===")
    
    manager = space_mission_manager
    
    # Test terminal identification
    terminal_texts = [
        "Mission Terminal - Available Space Missions",
        "Ship Control Terminal - Vessel Access",
        "Navigation Terminal - Travel Routes",
        "General Information Terminal",
        "Space Mission Board - Current Assignments"
    ]
    
    for text in terminal_texts:
        print(f"\nTesting terminal text: '{text}'")
        terminal_type = manager.identify_terminal(text)
        if terminal_type:
            print(f"  ✓ Identified terminal type: {terminal_type}")
        else:
            print(f"  ✗ Could not identify terminal type")


def demo_combat_simulation():
    """Demo combat simulation functionality."""
    print("\n=== Combat Simulation Demo ===")
    
    manager = space_mission_manager
    
    # Enter a ship first
    manager.enter_ship("x-wing")
    
    # Test combat scenarios
    combat_scenarios = [
        "Pirate Vessel",
        "Imperial TIE Fighter",
        "Smuggler's Ship",
        "Asteroid Field Raiders",
        "Unknown Hostile"
    ]
    
    for target in combat_scenarios:
        print(f"\nSimulating combat against: {target}")
        result = manager.simulate_combat(target)
        
        print(f"  Result: {result['status']}")
        print(f"  Duration: {result['duration']} seconds")
        print(f"  Damage taken: {result['damage_taken']}")
        print(f"  Credits earned: {result['credits_earned']}")
        print(f"  Experience earned: {result['experience_earned']}")
    
    # Exit ship
    manager.exit_ship()


def demo_mission_execution():
    """Demo full mission execution."""
    print("\n=== Mission Execution Demo ===")
    
    # Run space mode
    print("Running space mode...")
    results = space_mode.run()
    
    print(f"\nSpace mode results:")
    print(f"  Status: {results['status']}")
    
    if results['status'] == 'disabled':
        print(f"  Message: {results.get('message', 'Space mode is disabled')}")
    else:
        print(f"  Missions processed: {results.get('missions_processed', 0)}")
        print(f"  Combat simulations: {results.get('combat_simulations', 0)}")
        print(f"  Ship operations: {results.get('ship_operations', 0)}")
        print(f"  Terminal interactions: {results.get('terminal_interactions', 0)}")
        print(f"  Events detected: {results.get('events_detected', 0)}")


def demo_space_mode_status():
    """Demo space mode status and configuration."""
    print("\n=== Space Mode Status Demo ===")
    
    # Get space mode status
    status = space_mode.get_status()
    print(f"Space mode status:")
    print(f"  Mode: {status['mode']}")
    print(f"  Enabled: {status['enabled']}")
    print(f"  Current mission: {status['current_mission']}")
    print(f"  Available missions: {status['available_missions']}")
    print(f"  Current ship: {status['current_ship']}")
    print(f"  Current location: {status['current_location']}")
    print(f"  Mission history: {status['mission_history']}")
    
    # Get manager status
    manager_status = space_mission_manager.get_space_mode_status()
    print(f"\nManager status:")
    print(f"  Auto detect events: {manager_status['auto_detect_space_events']}")
    print(f"  Preferred mission types: {manager_status['preferred_mission_types']}")
    print(f"  Default station: {manager_status['default_station']}")
    print(f"  Combat simulation: {manager_status['combat_simulation']}")
    print(f"  Ship entry/exit: {manager_status['ship_entry_exit']}")
    print(f"  Terminal detection: {manager_status['terminal_detection']}")


def demo_configuration_integration():
    """Demo integration with session_config.json."""
    print("\n=== Configuration Integration Demo ===")
    
    config_path = Path("config/session_config.json")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            space_config = config.get("space_mode", {})
        
        print(f"Current space mode configuration:")
        print(f"  Enabled: {space_config.get('enabled', False)}")
        print(f"  Auto detect events: {space_config.get('auto_detect_space_events', True)}")
        print(f"  Preferred mission types: {space_config.get('preferred_mission_types', [])}")
        print(f"  Default station: {space_config.get('default_station', 'Tansarii Point Station')}")
        print(f"  Combat simulation: {space_config.get('combat_simulation', True)}")
        print(f"  Ship entry/exit: {space_config.get('ship_entry_exit', True)}")
        print(f"  Terminal detection: {space_config.get('terminal_detection', True)}")
    else:
        print("  ✗ Configuration file not found")


def main():
    """Run the Batch 062 space missions demo."""
    print("🚀 Batch 062 - Smart Space Mission Support (Phase 1) Demo")
    print("=" * 60)
    
    try:
        # Run all demos
        demo_space_event_detection()
        demo_mission_creation()
        demo_ship_operations()
        demo_terminal_identification()
        demo_combat_simulation()
        demo_mission_execution()
        demo_space_mode_status()
        demo_configuration_integration()
        
        # Save missions
        space_mission_manager.save_missions()
        
        print("\n✅ Batch 062 demo completed successfully!")
        print("\nFeatures demonstrated:")
        print("  ✓ Space event detection via logs")
        print("  ✓ Mission type definitions (Patrol, Escort, Kill Target)")
        print("  ✓ Ship entry/exit functionality")
        print("  ✓ Terminal identification")
        print("  ✓ Combat simulation for Tansarii Point Station")
        print("  ✓ Integration with session_config.json space_mode settings")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
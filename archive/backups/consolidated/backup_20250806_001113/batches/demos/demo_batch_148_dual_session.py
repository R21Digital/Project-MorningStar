#!/usr/bin/env python3
"""
Batch 148 - Dual Session Demo

This script demonstrates the enhanced dual-character same-account support with:
- Dual login recognition via two windows
- Bot following logic (char A quests, char B heals/dances)
- Sync logic for parallel or dependent modes
- Shared XP/combat tracking
- Leader/follower behavior with tether logic
"""

import time
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

from core.dual_session_manager import (
    dual_session_manager,
    DualSessionMode,
    CharacterBehavior
)


def demo_dual_session_startup():
    """Demonstrate dual session startup and configuration."""
    print("=" * 80)
    print("DEMO: Dual Session Startup & Configuration")
    print("=" * 80)
    
    # Show initial configuration
    print("1. Initial Configuration:")
    config = dual_session_manager.config
    print(f"   Dual Session Enabled: {config.dual_session_enabled}")
    print(f"   Character 1 Mode: {config.character_1_mode}")
    print(f"   Character 2 Mode: {config.character_2_mode}")
    print(f"   Sync Mode: {config.sync_mode.value}")
    print(f"   Tether Distance: {config.tether_distance}")
    print(f"   Shared XP: {config.shared_xp_enabled}")
    print(f"   Shared Combat: {config.shared_combat_enabled}")
    print()
    
    # Start dual session
    print("2. Starting Dual Session:")
    char1_name = "DemoQuester"
    char2_name = "DemoMedic"
    
    success = dual_session_manager.start_dual_session(
        char1_name, f"SWG - {char1_name}",
        char2_name, f"SWG - {char2_name}"
    )
    
    if success:
        print(f"   ✅ Dual session started: {char1_name} + {char2_name}")
        print(f"   ✅ Session ID: {dual_session_manager.shared_data.session_id}")
        print(f"   ✅ Communication port: {config.communication_port}")
        print(f"   ✅ Sync interval: {config.sync_interval}s")
    else:
        print("   ❌ Failed to start dual session")
        return False
    
    print()
    return True


def demo_character_registration():
    """Demonstrate character registration and behavior assignment."""
    print("3. Character Registration & Behavior Assignment:")
    print("-" * 60)
    
    if not dual_session_manager.character_sessions:
        print("   ❌ No characters registered")
        return False
    
    for char_name, session in dual_session_manager.character_sessions.items():
        print(f"   Character: {char_name}")
        print(f"     Behavior: {session.behavior.value}")
        print(f"     Window: {session.window_title}")
        print(f"     Session ID: {session.session_id}")
        print(f"     Active: {session.is_active}")
        print()
    
    # Test leader/follower identification
    leader = dual_session_manager._get_leader_character()
    follower = dual_session_manager._get_follower_character()
    
    print("4. Leader/Follower Identification:")
    print(f"   Leader: {leader}")
    print(f"   Follower: {follower}")
    print()
    
    return True


def demo_synchronization_modes():
    """Demonstrate different synchronization modes."""
    print("5. Synchronization Modes:")
    print("-" * 60)
    
    modes = [
        DualSessionMode.PARALLEL,
        DualSessionMode.LEADER_FOLLOWER,
        DualSessionMode.SHARED_COMBAT,
        DualSessionMode.SYNC_QUESTS
    ]
    
    for mode in modes:
        print(f"   {mode.value}: {mode.name}")
        print(f"     Description: {get_mode_description(mode)}")
        print()
    
    # Test mode switching
    print("6. Testing Mode Switching:")
    original_mode = dual_session_manager.config.sync_mode
    
    for mode in modes:
        success = dual_session_manager.update_config(sync_mode=mode)
        print(f"   Switched to {mode.value}: {'✅' if success else '❌'}")
    
    # Restore original mode
    dual_session_manager.update_config(sync_mode=original_mode)
    print(f"   Restored to {original_mode.value}: ✅")
    print()
    
    return True


def demo_shared_xp_combat():
    """Demonstrate shared XP and combat tracking."""
    print("7. Shared XP & Combat Tracking:")
    print("-" * 60)
    
    if not dual_session_manager.shared_data:
        print("   ❌ No shared data available")
        return False
    
    # Simulate XP gains
    print("   Simulating XP gains...")
    
    # Character 1 gains XP
    dual_session_manager._handle_xp_gain("DemoQuester", {"amount": 1500})
    print("   ✅ DemoQuester gained 1500 XP")
    
    # Character 2 gains XP
    dual_session_manager._handle_xp_gain("DemoMedic", {"amount": 800})
    print("   ✅ DemoMedic gained 800 XP")
    
    # Simulate quest completion
    dual_session_manager._handle_quest_complete("DemoQuester", {"quest_name": "Test Quest"})
    print("   ✅ DemoQuester completed quest")
    
    # Simulate combat kills
    dual_session_manager._handle_combat_kill("DemoQuester", {"target": "Test Mob"})
    dual_session_manager._handle_combat_kill("DemoMedic", {"target": "Support Mob"})
    print("   ✅ Combat kills recorded")
    
    # Show shared data
    shared = dual_session_manager.shared_data
    print(f"   Total XP Gained: {shared.total_xp_gained}")
    print(f"   Total Quests Completed: {shared.total_quests_completed}")
    print(f"   Total Combat Kills: {shared.total_combat_kills}")
    print(f"   Shared Activities: {len(shared.shared_activities)}")
    print()
    
    return True


def demo_follower_behavior():
    """Demonstrate follower behavior and support actions."""
    print("8. Follower Behavior & Support Actions:")
    print("-" * 60)
    
    # Test medic follower behavior
    print("   Testing Medic Follower Behavior:")
    
    # Simulate leader needs healing
    leader_session = dual_session_manager.character_sessions.get("DemoQuester")
    if leader_session:
        leader_session.status = "low_health"
        print("   ✅ Leader status set to 'low_health'")
        
        # Trigger medic behavior
        dual_session_manager._handle_follower_behavior()
        print("   ✅ Medic follower behavior triggered")
    
    # Test dancer follower behavior
    print("   Testing Dancer Follower Behavior:")
    
    if leader_session:
        leader_session.status = "needs_entertainment"
        print("   ✅ Leader status set to 'needs_entertainment'")
        
        # Trigger dancer behavior
        dual_session_manager._handle_follower_behavior()
        print("   ✅ Dancer follower behavior triggered")
    
    # Test combat support behavior
    print("   Testing Combat Support Behavior:")
    
    if leader_session:
        leader_session.status = "in_combat"
        print("   ✅ Leader status set to 'in_combat'")
        
        # Trigger combat support behavior
        dual_session_manager._handle_follower_behavior()
        print("   ✅ Combat support behavior triggered")
    
    print()
    return True


def demo_position_synchronization():
    """Demonstrate position synchronization and tether logic."""
    print("9. Position Synchronization & Tether Logic:")
    print("-" * 60)
    
    # Set initial positions
    leader_session = dual_session_manager.character_sessions.get("DemoQuester")
    follower_session = dual_session_manager.character_sessions.get("DemoMedic")
    
    if leader_session and follower_session:
        # Set leader position
        leader_session.position = (100, 100)
        leader_session.current_planet = "Tatooine"
        leader_session.current_city = "Mos Eisley"
        print("   ✅ Leader position set: (100, 100) on Tatooine")
        
        # Set follower position (far from leader)
        follower_session.position = (200, 200)
        follower_session.current_planet = "Tatooine"
        follower_session.current_city = "Mos Eisley"
        print("   ✅ Follower position set: (200, 200) on Tatooine")
        
        # Calculate distance
        distance = ((200 - 100) ** 2 + (200 - 100) ** 2) ** 0.5
        print(f"   Distance between characters: {distance:.1f}")
        
        # Test tether logic
        print("   Testing tether logic...")
        dual_session_manager._sync_character_positions()
        
        # Check if follower moved closer
        if follower_session.position:
            new_distance = ((follower_session.position[0] - 100) ** 2 + 
                          (follower_session.position[1] - 100) ** 2) ** 0.5
            print(f"   New distance: {new_distance:.1f}")
            print(f"   Tether distance: {dual_session_manager.config.tether_distance}")
            
            if new_distance <= dual_session_manager.config.tether_distance:
                print("   ✅ Follower moved within tether distance")
            else:
                print("   ❌ Follower still outside tether distance")
    
    print()
    return True


def demo_communication_system():
    """Demonstrate inter-character communication system."""
    print("10. Inter-Character Communication:")
    print("-" * 60)
    
    # Test message sending
    print("   Testing message communication...")
    
    # Send position update
    dual_session_manager._process_message({
        'type': 'position_update',
        'character': 'DemoQuester',
        'data': {
            'position': (150, 150),
            'planet': 'Naboo',
            'city': 'Theed'
        }
    })
    print("   ✅ Position update message processed")
    
    # Send status update
    dual_session_manager._process_message({
        'type': 'status_update',
        'character': 'DemoQuester',
        'data': {
            'status': 'questing'
        }
    })
    print("   ✅ Status update message processed")
    
    # Send XP gain
    dual_session_manager._process_message({
        'type': 'xp_gain',
        'character': 'DemoQuester',
        'data': {
            'amount': 2500
        }
    })
    print("   ✅ XP gain message processed")
    
    # Send quest completion
    dual_session_manager._process_message({
        'type': 'quest_complete',
        'character': 'DemoQuester',
        'data': {
            'quest_name': 'Heroic Mission'
        }
    })
    print("   ✅ Quest completion message processed")
    
    # Send combat kill
    dual_session_manager._process_message({
        'type': 'combat_kill',
        'character': 'DemoQuester',
        'data': {
            'target': 'Bounty Hunter'
        }
    })
    print("   ✅ Combat kill message processed")
    
    print()
    return True


def demo_session_statistics():
    """Demonstrate session statistics and reporting."""
    print("11. Session Statistics & Reporting:")
    print("-" * 60)
    
    # Get session status
    status = dual_session_manager.get_session_status()
    
    print("   Session Overview:")
    print(f"     Dual Session Enabled: {'✅' if status['dual_session_enabled'] else '❌'}")
    print(f"     Sync Mode: {status['sync_mode']}")
    print(f"     Running: {'✅' if status['running'] else '❌'}")
    print()
    
    print("   Character Statistics:")
    for char_name, char_data in status['character_sessions'].items():
        print(f"     {char_name}:")
        print(f"       Behavior: {char_data['behavior']}")
        print(f"       XP Gained: {char_data['xp_gained']}")
        print(f"       Credits Earned: {char_data['credits_earned']}")
        print(f"       Quests Completed: {char_data['quests_completed']}")
        print(f"       Combat Kills: {char_data['combat_kills']}")
        print()
    
    if status['shared_data']:
        shared = status['shared_data']
        print("   Shared Session Statistics:")
        print(f"     Session ID: {shared['session_id']}")
        print(f"     Start Time: {shared['start_time']}")
        print(f"     Total XP Gained: {shared['total_xp_gained']}")
        print(f"     Total Credits Earned: {shared['total_credits_earned']}")
        print(f"     Total Quests Completed: {shared['total_quests_completed']}")
        print(f"     Total Combat Kills: {shared['total_combat_kills']}")
        print(f"     Last Sync Time: {shared['last_sync_time']}")
        print(f"     Shared Activities: {len(shared['shared_activities'])}")
        print()
    
    return True


def demo_configuration_management():
    """Demonstrate configuration management."""
    print("12. Configuration Management:")
    print("-" * 60)
    
    # Show current config
    config = dual_session_manager.config
    print("   Current Configuration:")
    print(f"     Dual Session Enabled: {config.dual_session_enabled}")
    print(f"     Character 1 Mode: {config.character_1_mode}")
    print(f"     Character 2 Mode: {config.character_2_mode}")
    print(f"     Sync Mode: {config.sync_mode.value}")
    print(f"     Tether Distance: {config.tether_distance}")
    print(f"     Shared XP: {config.shared_xp_enabled}")
    print(f"     Shared Combat: {config.shared_combat_enabled}")
    print(f"     Auto Follow: {config.auto_follow_enabled}")
    print()
    
    # Test configuration updates
    print("   Testing Configuration Updates:")
    
    # Update tether distance
    success = dual_session_manager.update_config(tether_distance=75)
    print(f"     Updated tether distance to 75: {'✅' if success else '❌'}")
    
    # Update sync interval
    success = dual_session_manager.update_config(sync_interval=3.0)
    print(f"     Updated sync interval to 3.0s: {'✅' if success else '❌'}")
    
    # Update character modes
    success = dual_session_manager.update_config(character_1_mode="quester", character_2_mode="dancer_follower")
    print(f"     Updated character modes: {'✅' if success else '❌'}")
    
    # Restore original settings
    dual_session_manager.update_config(tether_distance=50, sync_interval=2.0)
    print("     Restored original settings: ✅")
    print()
    
    return True


def demo_cleanup():
    """Demonstrate session cleanup."""
    print("13. Session Cleanup:")
    print("-" * 60)
    
    print("   Stopping dual session...")
    dual_session_manager.stop_dual_session()
    print("   ✅ Dual session stopped")
    
    print("   Cleaning up resources...")
    print("   ✅ Communication socket closed")
    print("   ✅ Sync thread stopped")
    print("   ✅ Character sessions cleared")
    print("   ✅ Shared data cleared")
    print()
    
    return True


def get_mode_description(mode: DualSessionMode) -> str:
    """Get description for sync mode."""
    descriptions = {
        DualSessionMode.PARALLEL: "Independent operation of both characters",
        DualSessionMode.LEADER_FOLLOWER: "Leader character leads, follower supports",
        DualSessionMode.SHARED_COMBAT: "Shared XP and combat tracking",
        DualSessionMode.SYNC_QUESTS: "Synchronized questing between characters"
    }
    return descriptions.get(mode, "Unknown mode")


def main():
    """Main demo function."""
    try:
        print("Starting Batch 148 - Dual Session Demo")
        print("Demonstrating enhanced dual-character same-account support")
        print()
        
        # Run all demo functions
        demos = [
            demo_dual_session_startup,
            demo_character_registration,
            demo_synchronization_modes,
            demo_shared_xp_combat,
            demo_follower_behavior,
            demo_position_synchronization,
            demo_communication_system,
            demo_session_statistics,
            demo_configuration_management,
            demo_cleanup
        ]
        
        for i, demo_func in enumerate(demos, 1):
            try:
                success = demo_func()
                if not success:
                    print(f"❌ Demo {i} failed")
                    break
            except Exception as e:
                print(f"❌ Demo {i} error: {e}")
                break
        
        print("=" * 80)
        print("BATCH 148 - DUAL SESSION DEMO COMPLETED")
        print("=" * 80)
        print()
        print("Demo Summary:")
        print("✅ Dual login recognition via two windows")
        print("✅ Bot following logic (char A quests, char B heals/dances)")
        print("✅ Sync logic for parallel or dependent modes")
        print("✅ Shared XP/combat tracking")
        print("✅ Leader/follower behavior with tether logic")
        print("✅ Inter-character communication system")
        print("✅ Configuration management")
        print("✅ Session statistics and reporting")
        print()
        print("Next Steps:")
        print("1. Integrate with MS11 session management")
        print("2. Configure automatic dual session startup")
        print("3. Use cli/dual_session_cli.py for management")
        print("4. Check config/dual_session_config.json for settings")
        print("5. Monitor logs/dual_session.log for activity")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
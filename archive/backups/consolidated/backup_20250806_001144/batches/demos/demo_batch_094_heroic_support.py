#!/usr/bin/env python3
"""
MS11 Batch 094 - Heroic Support & Group Questing Mode (Phase 1) Demo

This script demonstrates the core functionalities of the heroic support system:
- Heroic database management
- Group detection and coordination
- Auto-follow functionality
- Configuration management
- Group state management
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

from core.heroic_support import heroic_support, HeroicDatabase, GroupDetector, GroupFollower, GroupCoordinator
from core.heroic_support import GroupStatus, HeroicDifficulty, GroupMember, HeroicInstance, GroupState, FollowTarget

def demo_heroic_database():
    """Demonstrate heroic database functionality."""
    print("\n" + "="*60)
    print("🏰 HEROIC DATABASE DEMONSTRATION")
    print("="*60)
    
    # Get available heroics for different character levels
    for level in [70, 75, 80, 85, 90]:
        heroics = heroic_support.get_available_heroics(level)
        print(f"\n📊 Available heroics for level {level}: {len(heroics)}")
        
        for heroic in heroics[:3]:  # Show first 3
            print(f"  • {heroic['name']} ({heroic['planet']}) - Level {heroic['level_requirement']}+")
    
    # Get specific heroic information
    print(f"\n📋 Heroic Details:")
    axkva_info = heroic_support.get_heroic_info("axkva_min")
    if "error" not in axkva_info:
        print(f"  • Axkva Min: {axkva_info['name']}")
        print(f"    Location: {axkva_info['planet']} - {axkva_info['location']}")
        print(f"    Level Requirement: {axkva_info['level_requirement']}")
        print(f"    Group Size: {axkva_info['group_size']}")
        print(f"    Difficulty: {axkva_info['difficulty']}")

def demo_group_detection():
    """Demonstrate group detection functionality."""
    print("\n" + "="*60)
    print("👥 GROUP DETECTION DEMONSTRATION")
    print("="*60)
    
    # Simulate different chat scenarios
    chat_scenarios = [
        "Player invites you to join their group",
        "Player joins the group",
        "Group chat: Ready to enter heroic?",
        "Everyone ready for the boss fight?",
        "Entering instance now",
        "Inside heroic - following leader",
        "Group disbanded"
    ]
    
    for scenario in chat_scenarios:
        status = heroic_support.group_coordinator.group_detector.detect_group_status(chat_text=scenario)
        print(f"\n💬 Chat: '{scenario}'")
        print(f"   Status: {status.value}")
    
    # Simulate UI elements
    ui_scenarios = [
        {"group_window": True, "member_list": True},
        {"group_ready_indicator": True},
        {"heroic_instance_indicator": True},
        {}
    ]
    
    for i, ui in enumerate(ui_scenarios):
        status = heroic_support.group_coordinator.group_detector.detect_group_status(ui_elements=ui)
        print(f"\n🖥️  UI Elements: {ui}")
        print(f"   Status: {status.value}")

def demo_group_following():
    """Demonstrate auto-follow functionality."""
    print("\n" + "="*60)
    print("👣 GROUP FOLLOWING DEMONSTRATION")
    print("="*60)
    
    follower = heroic_support.group_coordinator.group_follower
    
    # Start following a leader
    print(f"\n🎯 Starting to follow 'HeroicLeader'")
    success = follower.start_following("HeroicLeader", "leader")
    print(f"   Success: {success}")
    print(f"   Following: {follower.is_following}")
    print(f"   Target: {follower.current_target.target_name if follower.current_target else 'None'}")
    
    # Update target position
    print(f"\n📍 Updating target position")
    success = follower.update_target_position([100, 200])
    print(f"   Success: {success}")
    
    # Check timeout
    print(f"\n⏰ Checking follow timeout")
    timeout = follower.check_follow_timeout()
    print(f"   Timeout reached: {timeout}")
    
    # Stop following
    print(f"\n🛑 Stopping follow")
    success = follower.stop_following()
    print(f"   Success: {success}")
    print(f"   Following: {follower.is_following}")

def demo_group_coordination():
    """Demonstrate group coordination functionality."""
    print("\n" + "="*60)
    print("🤝 GROUP COORDINATION DEMONSTRATION")
    print("="*60)
    
    coordinator = heroic_support.group_coordinator
    
    # Simulate group formation
    print(f"\n📋 Simulating group formation")
    group_state = coordinator.update_group_state(
        chat_text="Player invites you to join their group"
    )
    print(f"   Group State: {group_state.status.value if group_state else 'None'}")
    
    # Get group info
    group_info = coordinator.get_group_info()
    print(f"\n📊 Group Information:")
    for key, value in group_info.items():
        print(f"   {key}: {value}")
    
    # Simulate group ready
    print(f"\n✅ Simulating group ready")
    group_state = coordinator.update_group_state(
        chat_text="Everyone ready for the boss fight?"
    )
    print(f"   Group State: {group_state.status.value if group_state else 'None'}")
    
    # Simulate group disband
    print(f"\n👋 Simulating group disband")
    group_state = coordinator.update_group_state(
        chat_text="Group disbanded"
    )
    print(f"   Group State: {group_state.status.value if group_state else 'None'}")

def demo_configuration_management():
    """Demonstrate configuration management."""
    print("\n" + "="*60)
    print("⚙️ CONFIGURATION MANAGEMENT DEMONSTRATION")
    print("="*60)
    
    # Show current configuration
    config = heroic_support.config
    print(f"\n📋 Current Configuration:")
    print(f"   Heroic Mode Enabled: {config.get('heroic_mode', {}).get('enabled', False)}")
    print(f"   Auto Follow Leader: {config.get('heroic_mode', {}).get('auto_follow_leader', True)}")
    print(f"   Wait for Group: {config.get('heroic_mode', {}).get('wait_for_group', True)}")
    print(f"   Group Timeout: {config.get('heroic_mode', {}).get('group_timeout', 300)}s")
    print(f"   Follow Distance: {config.get('group_behavior', {}).get('follow_distance', 10)}m")
    
    # Enable heroic mode
    print(f"\n🔧 Enabling Heroic Mode")
    success = heroic_support.enable_heroic_mode()
    print(f"   Success: {success}")
    print(f"   Enabled: {heroic_support.is_enabled}")
    
    # Disable heroic mode
    print(f"\n🔧 Disabling Heroic Mode")
    success = heroic_support.disable_heroic_mode()
    print(f"   Success: {success}")
    print(f"   Enabled: {heroic_support.is_enabled}")

def demo_wait_for_group():
    """Demonstrate wait for group functionality."""
    print("\n" + "="*60)
    print("⏳ WAIT FOR GROUP DEMONSTRATION")
    print("="*60)
    
    # Simulate waiting for group (with short timeout for demo)
    print(f"\n⏰ Waiting for group (5 second timeout)")
    start_time = datetime.now()
    
    # This would normally wait for the actual group to be ready
    # For demo purposes, we'll just show the interface
    success = heroic_support.wait_for_group_ready(timeout=5)
    
    duration = (datetime.now() - start_time).total_seconds()
    print(f"   Duration: {duration:.1f}s")
    print(f"   Group Ready: {success}")

def demo_state_management():
    """Demonstrate state management."""
    print("\n" + "="*60)
    print("📊 STATE MANAGEMENT DEMONSTRATION")
    print("="*60)
    
    # Update state with different scenarios
    scenarios = [
        {"chat_text": "Player invites you to join their group"},
        {"ui_elements": {"group_window": True, "member_list": True}},
        {"chat_text": "Everyone ready for the boss fight?"},
        {"ui_elements": {"heroic_instance_indicator": True}},
        {"chat_text": "Group disbanded"}
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"\n🔄 Scenario {i+1}: {scenario}")
        state = heroic_support.update_state(**scenario)
        print(f"   Enabled: {state.get('enabled', False)}")
        print(f"   Group Status: {state.get('group_info', {}).get('status', 'unknown')}")
        print(f"   Following Active: {state.get('following_active', False)}")
        print(f"   Available Heroics: {state.get('available_heroics', 0)}")

def demo_heroic_instances():
    """Demonstrate heroic instance management."""
    print("\n" + "="*60)
    print("🏰 HEROIC INSTANCES DEMONSTRATION")
    print("="*60)
    
    # Show all available heroics
    heroics = heroic_support.get_available_heroics(80)
    
    print(f"\n📋 Available Heroics for Level 80:")
    for heroic in heroics:
        print(f"\n🏰 {heroic['name']}")
        print(f"   ID: {heroic['heroic_id']}")
        print(f"   Planet: {heroic['planet']}")
        print(f"   Location: {heroic['location']}")
        print(f"   Level Requirement: {heroic['level_requirement']}")
        print(f"   Group Size: {heroic['group_size']}")
        print(f"   Difficulty: {heroic['difficulty']}")
        
        # Show prerequisites if available
        if heroic.get('prerequisites'):
            print(f"   Prerequisites:")
            for prereq_type, prereqs in heroic['prerequisites'].items():
                if isinstance(prereqs, list) and prereqs:
                    print(f"     {prereq_type}: {len(prereqs)} items")
        
        # Show bosses if available
        if heroic.get('bosses'):
            print(f"   Bosses: {len(heroic['bosses'])}")
            for boss in heroic['bosses'][:2]:  # Show first 2
                print(f"     • {boss.get('name', 'Unknown')} (Level {boss.get('level', '?')})")

def demo_integration():
    """Demonstrate full system integration."""
    print("\n" + "="*60)
    print("🔗 SYSTEM INTEGRATION DEMONSTRATION")
    print("="*60)
    
    print(f"\n🚀 Starting Heroic Support System")
    
    # Enable heroic mode
    heroic_support.enable_heroic_mode()
    print(f"   Heroic Mode: {'Enabled' if heroic_support.is_enabled else 'Disabled'}")
    
    # Simulate a complete heroic session
    print(f"\n📋 Simulating Heroic Session:")
    
    # 1. Group formation
    print(f"   1. Group Formation")
    state = heroic_support.update_state(chat_text="Player invites you to join their group")
    print(f"      Status: {state.get('group_info', {}).get('status', 'unknown')}")
    
    # 2. Group ready
    print(f"   2. Group Ready")
    state = heroic_support.update_state(chat_text="Everyone ready for the boss fight?")
    print(f"      Status: {state.get('group_info', {}).get('status', 'unknown')}")
    print(f"      Following: {state.get('following_active', False)}")
    
    # 3. In progress
    print(f"   3. In Progress")
    state = heroic_support.update_state(ui_elements={"heroic_instance_indicator": True})
    print(f"      Status: {state.get('group_info', {}).get('status', 'unknown')}")
    
    # 4. Completion
    print(f"   4. Completion")
    state = heroic_support.update_state(chat_text="Heroic completed successfully")
    print(f"      Status: {state.get('group_info', {}).get('status', 'unknown')}")
    
    # Disable heroic mode
    heroic_support.disable_heroic_mode()
    print(f"\n🛑 Heroic Mode: {'Enabled' if heroic_support.is_enabled else 'Disabled'}")

def main():
    """Run all demonstrations."""
    print("MS11 Batch 094 - Heroic Support & Group Questing Mode (Phase 1)")
    print("Demonstration Script")
    print("="*80)
    
    try:
        # Run all demos
        demo_heroic_database()
        demo_group_detection()
        demo_group_following()
        demo_group_coordination()
        demo_configuration_management()
        demo_wait_for_group()
        demo_state_management()
        demo_heroic_instances()
        demo_integration()
        
        print("\n" + "="*80)
        print("✅ All demonstrations completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
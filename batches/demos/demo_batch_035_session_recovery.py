#!/usr/bin/env python3
"""
Demo script for Batch 035 - Session Recovery & Continuation Engine

This script demonstrates the session recovery functionality including:
- Session state saving and loading
- Crash detection and recovery
- Auto-save functionality
- Session statistics and cleanup
- Recovery prompts and user interaction
"""

import sys
import time
import json
import tempfile
from pathlib import Path

# Add core to path for imports
sys.path.insert(0, str(Path(__file__).parent / "core"))

from session_recovery import SessionRecoveryEngine, SessionState, CrashInfo
from datetime import datetime


def demo_session_recovery():
    """Demonstrate the session recovery functionality."""
    print("🚀 Batch 035 - Session Recovery & Continuation Engine")
    print("=" * 60)
    
    # Initialize session recovery engine
    print("📚 Initializing Session Recovery Engine...")
    engine = SessionRecoveryEngine()
    
    # Show initial state
    print(f"\n📊 Initial State:")
    print(f"   Recovery Enabled: {engine.recovery_enabled}")
    print(f"   Auto Restart: {engine.auto_restart}")
    print(f"   Auto Relog: {engine.auto_relog}")
    print(f"   Save Interval: {engine.save_interval} seconds")
    print(f"   State File: {engine.state_file}")
    
    # Demonstrate session state saving
    print("\n💾 Session State Saving Demo:")
    success = engine.save_session_state(force=True)
    print(f"   Save Result: {'✅ Success' if success else '❌ Failed'}")
    
    if success:
        print(f"   State File Created: {engine.state_file.exists()}")
        if engine.state_file.exists():
            with open(engine.state_file, 'r') as f:
                state_data = json.load(f)
                print(f"   State Data Size: {len(json.dumps(state_data))} bytes")
    
    # Demonstrate session state loading
    print("\n📂 Session State Loading Demo:")
    loaded_state = engine.load_session_state()
    if loaded_state:
        print(f"   ✅ Loaded Session State:")
        print(f"      Planet: {loaded_state.planet}")
        print(f"      Zone: {loaded_state.zone}")
        print(f"      Quest: {loaded_state.current_quest.get('name', 'None') if loaded_state.current_quest else 'None'}")
        print(f"      Level: {loaded_state.xp_level}")
        print(f"      XP: {loaded_state.xp_current}/{loaded_state.xp_next_level}")
        print(f"      Weapon: {loaded_state.equipped_weapon.get('name', 'None') if loaded_state.equipped_weapon else 'None'}")
    else:
        print("   ❌ No session state to load")
    
    # Demonstrate crash detection
    print("\n💥 Crash Detection Demo:")
    crashes = engine.detect_crashes()
    print(f"   Detected Crashes: {len(crashes)}")
    
    if crashes:
        for i, crash in enumerate(crashes, 1):
            print(f"   Crash {i}: {crash.error_type}")
            print(f"      Message: {crash.error_message}")
            print(f"      Timestamp: {datetime.fromtimestamp(crash.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("   ✅ No crashes detected")
    
    # Demonstrate crash recovery
    print("\n🔄 Crash Recovery Demo:")
    recovery_success = engine.handle_crash_recovery()
    print(f"   Recovery Result: {'✅ Success' if recovery_success else '❌ Failed'}")
    
    # Demonstrate session statistics
    print("\n📊 Session Statistics Demo:")
    stats = engine.get_session_statistics()
    if stats:
        print(f"   Session Duration: {stats.get('session_duration', 0):.1f} seconds")
        print(f"   Crash Count: {stats.get('crash_count', 0)}")
        print(f"   Last Save: {stats.get('last_save', 'Unknown')}")
        print(f"   Recovery Enabled: {stats.get('recovery_enabled', False)}")
        print(f"   Auto Restart: {stats.get('auto_restart', False)}")
        print(f"   Auto Relog: {stats.get('auto_relog', False)}")
        print(f"   Save Interval: {stats.get('save_interval', 0)} seconds")
        print(f"   State File: {stats.get('state_file', 'Unknown')}")
    else:
        print("   ❌ No session statistics available")
    
    # Demonstrate auto-save functionality
    print("\n⏰ Auto-Save Demo:")
    print("   Starting auto-save thread...")
    engine.start_auto_save()
    
    # Simulate some activity
    print("   Simulating activity for 3 seconds...")
    time.sleep(3)
    
    print("   Stopping auto-save thread...")
    engine.stop_auto_save()
    print("   ✅ Auto-save demo completed")
    
    # Demonstrate cleanup functionality
    print("\n🧹 Cleanup Demo:")
    engine.cleanup_old_states(max_age_hours=24)
    print("   ✅ Cleanup completed")
    
    # Demonstrate recovery prompt (simulated)
    print("\n❓ Recovery Prompt Demo:")
    if engine.current_state:
        print("   Previous session detected!")
        print("   Would prompt user: 'Continue previous session? [Y/n]'")
        print("   User response would determine recovery action")
    else:
        print("   No previous session found")
        print("   No recovery prompt needed")
    
    # Demonstrate session recovery
    print("\n🔄 Session Recovery Demo:")
    if engine.current_state:
        print("   Attempting session recovery...")
        recovery_success = engine.recover_session()
        print(f"   Recovery Result: {'✅ Success' if recovery_success else '❌ Failed'}")
    else:
        print("   No session state to recover from")
    
    print("\n🎉 Session Recovery Engine Demo Completed!")


def demo_state_persistence():
    """Demonstrate session state persistence across restarts."""
    print("\n🔄 Session State Persistence Demo:")
    print("-" * 40)
    
    # Create a temporary state file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_state_file = f.name
    
    # Create a mock session state
    mock_state = {
        "timestamp": time.time(),
        "planet": "tatooine",
        "zone": "mos_eisley",
        "coordinates": [100, 200],
        "current_quest": {"name": "Artifact Hunt", "step": 2, "objectives": ["Find artifact", "Return to NPC"]},
        "quest_step": 2,
        "xp_level": 15,
        "xp_current": 7500,
        "xp_next_level": 8000,
        "equipped_weapon": {"type": "rifle", "name": "E-11 Blaster Rifle"},
        "active_modes": ["questing", "combat"],
        "task_queue": ["travel_to_location", "find_npc", "complete_quest"],
        "session_duration": 1800.0,
        "crash_count": 0,
        "last_save_time": time.time(),
        "recovery_enabled": True,
        "auto_restart": False,
        "auto_relog": True
    }
    
    # Save mock state
    with open(temp_state_file, 'w') as f:
        json.dump(mock_state, f, indent=2)
    
    print(f"   Created mock session state: {temp_state_file}")
    print(f"   State contains: {len(mock_state)} fields")
    
    # Simulate loading the state
    try:
        with open(temp_state_file, 'r') as f:
            loaded_data = json.load(f)
        
        print(f"   ✅ Successfully loaded state data")
        print(f"   Planet: {loaded_data['planet']}")
        print(f"   Quest: {loaded_data['current_quest']['name']}")
        print(f"   Level: {loaded_data['xp_level']}")
        print(f"   Session Duration: {loaded_data['session_duration']:.1f} seconds")
        
    except Exception as e:
        print(f"   ❌ Failed to load state: {e}")
    
    # Clean up
    import os
    os.unlink(temp_state_file)
    print(f"   🧹 Cleaned up temporary file")


def demo_crash_scenarios():
    """Demonstrate different crash scenarios and recovery."""
    print("\n💥 Crash Scenario Demo:")
    print("-" * 40)
    
    # Initialize engine
    engine = SessionRecoveryEngine()
    
    # Simulate different crash types
    crash_scenarios = [
        {
            "type": "Connection Lost",
            "message": "Connection to server lost. Please reconnect.",
            "auto_restart": False,
            "auto_relog": True
        },
        {
            "type": "Game Crashed",
            "message": "Game has crashed. Please restart the client.",
            "auto_restart": True,
            "auto_relog": False
        },
        {
            "type": "Memory Error",
            "message": "Memory allocation failed. Game will close.",
            "auto_restart": True,
            "auto_relog": False
        },
        {
            "type": "Graphics Error",
            "message": "Graphics driver error. Please update drivers.",
            "auto_restart": False,
            "auto_relog": False
        }
    ]
    
    for i, scenario in enumerate(crash_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['type']}")
        print(f"      Message: {scenario['message']}")
        print(f"      Auto Restart: {scenario['auto_restart']}")
        print(f"      Auto Relog: {scenario['auto_relog']}")
        
        # Simulate crash detection
        crash = CrashInfo(
            error_type=scenario['type'],
            error_message=scenario['message'],
            timestamp=time.time(),
            recovery_attempted=False,
            recovery_successful=False
        )
        
        engine.crash_history.append(crash)
        
        # Simulate recovery attempt
        if scenario['auto_restart']:
            print(f"      Action: Auto-restart would be attempted")
        elif scenario['auto_relog']:
            print(f"      Action: Auto-relog would be attempted")
        else:
            print(f"      Action: Manual intervention required")
    
    print(f"\n   Total Crashes Recorded: {len(engine.crash_history)}")
    
    # Show crash statistics
    crash_types = {}
    for crash in engine.crash_history:
        crash_types[crash.error_type] = crash_types.get(crash.error_type, 0) + 1
    
    print(f"   Crash Types:")
    for crash_type, count in crash_types.items():
        print(f"      {crash_type}: {count}")


def demo_configuration():
    """Demonstrate configuration options."""
    print("\n⚙️  Configuration Demo:")
    print("-" * 40)
    
    # Create a sample configuration
    sample_config = {
        "save_interval": 180,  # 3 minutes
        "state_file": "custom_session_state.json",
        "recovery_enabled": True,
        "auto_restart": True,
        "auto_relog": True,
        "crash_detection": {
            "enabled": True,
            "check_interval": 15,
            "error_patterns": [
                "connection lost",
                "server disconnected",
                "game crashed",
                "memory error",
                "graphics error",
                "network timeout"
            ]
        },
        "session_tracking": {
            "enabled": True,
            "track_quests": True,
            "track_xp": True,
            "track_location": True,
            "track_equipment": True,
            "track_modes": True
        }
    }
    
    print("   Sample Configuration:")
    for key, value in sample_config.items():
        if isinstance(value, dict):
            print(f"      {key}:")
            for sub_key, sub_value in value.items():
                print(f"        {sub_key}: {sub_value}")
        else:
            print(f"      {key}: {value}")
    
    # Demonstrate configuration loading
    print("\n   Configuration Loading:")
    engine = SessionRecoveryEngine()
    print(f"      Default Save Interval: {engine.save_interval} seconds")
    print(f"      Default State File: {engine.state_file}")
    print(f"      Recovery Enabled: {engine.recovery_enabled}")
    print(f"      Auto Restart: {engine.auto_restart}")
    print(f"      Auto Relog: {engine.auto_relog}")
    
    # Show crash detection patterns
    patterns = engine.config["crash_detection"]["error_patterns"]
    print(f"      Crash Detection Patterns: {len(patterns)}")
    for pattern in patterns:
        print(f"        - {pattern}")


if __name__ == "__main__":
    print("🎯 Batch 035 - Session Recovery & Continuation Engine")
    print("=" * 70)
    
    # Run main demo
    demo_session_recovery()
    
    # Run additional demos
    demo_state_persistence()
    demo_crash_scenarios()
    demo_configuration()
    
    print("\n🎉 All demonstrations completed successfully!")
    print("   The session recovery engine is ready for use.")
    print("\n📋 Key Features Implemented:")
    print("   ✅ Session state saving every 5 minutes")
    print("   ✅ Crash detection and recovery")
    print("   ✅ Recovery prompts on startup")
    print("   ✅ Auto-restart and auto-relog capabilities")
    print("   ✅ Session continuation from last known state")
    print("   ✅ Session statistics and cleanup")
    print("   ✅ Configuration management") 
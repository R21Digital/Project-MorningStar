#!/usr/bin/env python3
"""
Demo script for Batch 076 - Anti-Detection Defense Layer v1

This demo showcases the comprehensive anti-detection system including:
- Session randomization and limits
- Human-like delay injection
- AFK whisper scanning and RP replies
- Cooldown tracking and management
- Dynamic movement injection
- Session warning system
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

# Import our anti-detection components
from core.anti_detection import create_anti_detection_defense
from services.afk_reply_manager import create_afk_reply_manager


def demo_session_randomization():
    """Demo session randomization and limits."""
    print("\n" + "="*60)
    print("DEMO: Session Randomization & Limits")
    print("="*60)
    
    defense = create_anti_detection_defense()
    
    # Start a session
    print("Starting anti-detection session...")
    session_data = defense.start_session()
    print(f"Session ID: {session_data.get('session_id', 'N/A')}")
    print(f"Start Time: {session_data.get('start_time', 'N/A')}")
    print(f"Planned Duration: {session_data.get('planned_duration', 0)/3600:.2f} hours")
    
    # Show break scheduling
    break_data = session_data.get('break_scheduled', {})
    if break_data:
        print(f"Break Scheduled: {break_data.get('duration', 0)} minutes")
        print(f"Break Type: {break_data.get('break_type', 'N/A')}")
    
    # Check session limits
    print("\nChecking session limits...")
    limits_status = defense.check_session_limits()
    print(f"Session Status: {limits_status.get('status', 'N/A')}")
    print(f"Session Duration: {limits_status.get('session_duration', 0):.2f} hours")
    print(f"Total Today Hours: {limits_status.get('total_today_hours', 0):.2f}")
    
    if limits_status.get('warnings'):
        print("Warnings:")
        for warning in limits_status['warnings']:
            print(f"  - {warning}")
    
    return defense


def demo_human_like_delays():
    """Demo human-like delay injection."""
    print("\n" + "="*60)
    print("DEMO: Human-Like Delay Injection")
    print("="*60)
    
    defense = create_anti_detection_defense()
    
    # Test different types of delays
    delay_types = [
        ("typing", "Typing a message"),
        ("movement", "Moving character"),
        ("combat", "Using combat skill"),
        ("general", "General action")
    ]
    
    for delay_type, description in delay_types:
        print(f"\n{description}...")
        start_time = time.time()
        delay_duration = defense.inject_human_delay(delay_type)
        actual_delay = time.time() - start_time
        print(f"  Delay Type: {delay_type}")
        print(f"  Injected Delay: {delay_duration:.3f}s")
        print(f"  Actual Delay: {actual_delay:.3f}s")
    
    # Test random action injection
    print("\nTesting random action injection...")
    for i in range(5):
        action = defense.inject_random_action()
        if action:
            print(f"  Random Action {i+1}: {action}")
        else:
            print(f"  Random Action {i+1}: None (cooldown)")
        time.sleep(0.1)


def demo_afk_reply_management():
    """Demo AFK reply management and whisper scanning."""
    print("\n" + "="*60)
    print("DEMO: AFK Reply Management")
    print("="*60)
    
    afk_manager = create_afk_reply_manager()
    
    # Simulate activity
    print("Simulating normal activity...")
    afk_manager.update_activity()
    
    # Check AFK status
    afk_status = afk_manager.check_afk_status()
    print(f"AFK Status: {afk_status.get('afk', False)}")
    print(f"Inactivity Duration: {afk_status.get('inactivity_duration', 0):.1f}s")
    
    # Simulate whisper scanning
    print("\nScanning for whispers...")
    for i in range(3):
        whispers = afk_manager.scan_for_whispers()
        if whispers:
            for whisper in whispers:
                print(f"  Whisper from {whisper['sender']}: {whisper['message']}")
        else:
            print(f"  Scan {i+1}: No whispers detected")
        time.sleep(1)
    
    # Test AFK detection
    print("\nSimulating inactivity for AFK detection...")
    print("Waiting 6 seconds to simulate inactivity...")
    time.sleep(6)
    
    afk_status = afk_manager.check_afk_status()
    print(f"AFK Status after inactivity: {afk_status.get('afk', False)}")
    
    # Simulate activity return
    print("\nSimulating activity return...")
    afk_manager.update_activity()
    afk_status = afk_manager.check_afk_status()
    print(f"AFK Status after activity: {afk_status.get('afk', False)}")
    
    # Get AFK summary
    summary = afk_manager.get_afk_summary()
    print(f"\nAFK Summary:")
    print(f"  Whisper History Count: {summary.get('whisper_history_count', 0)}")
    print(f"  Reply History Count: {summary.get('reply_history_count', 0)}")
    print(f"  Features Enabled: {summary.get('features_enabled', {})}")


def demo_cooldown_tracking():
    """Demo cooldown tracking and management."""
    print("\n" + "="*60)
    print("DEMO: Cooldown Tracking & Management")
    print("="*60)
    
    defense = create_anti_detection_defense()
    
    # Test different action types
    action_types = [
        ("combat_skill", {"skill": "Rifle Shot", "damage": 150}),
        ("movement", {"direction": "north", "distance": 10}),
        ("crafting", {"item": "Stimpack", "quality": "high"}),
        ("trading", {"action": "buy", "item": "Durindfire"}),
        ("social_interaction", {"type": "emote", "emote": "/wave"})
    ]
    
    print("Testing action tracking...")
    for action_type, action_data in action_types:
        allowed = defense.track_action(action_type, action_data)
        print(f"  {action_type}: {'ALLOWED' if allowed else 'BLOCKED'}")
    
    # Test rapid actions (should hit limits)
    print("\nTesting rapid actions (should hit cooldown limits)...")
    for i in range(10):
        allowed = defense.track_action("combat_skill", {"skill": f"Skill_{i}"})
        print(f"  Rapid Combat Skill {i+1}: {'ALLOWED' if allowed else 'BLOCKED'}")
    
    # Get session summary
    summary = defense.get_session_summary()
    print(f"\nCooldown Status:")
    for action_type, status in summary.get('cooldown_status', {}).items():
        print(f"  {action_type}: {status['actions_count']}/{status['limit']}")


def demo_dynamic_movement():
    """Demo dynamic movement injection."""
    print("\n" + "="*60)
    print("DEMO: Dynamic Movement Injection")
    print("="*60)
    
    defense = create_anti_detection_defense()
    
    # Test movement injection
    print("Testing dynamic movement injection...")
    for i in range(5):
        movement = defense.inject_dynamic_movement()
        if movement:
            print(f"  Movement {i+1}: {movement['pattern']} for {movement['duration']}s")
        else:
            print(f"  Movement {i+1}: None (cooldown)")
        time.sleep(0.1)


def demo_session_warnings():
    """Demo session warning system."""
    print("\n" + "="*60)
    print("DEMO: Session Warning System")
    print("="*60)
    
    defense = create_anti_detection_defense()
    
    # Start session
    session_data = defense.start_session()
    print(f"Session started: {session_data.get('session_id', 'N/A')}")
    
    # Simulate high activity
    print("\nSimulating high activity...")
    for i in range(20):
        defense.track_action("combat_skill", {"skill": f"Skill_{i}"})
        defense.track_action("movement", {"direction": "random"})
    
    # Check for warnings
    limits_status = defense.check_session_limits()
    print(f"\nSession Status: {limits_status.get('status', 'N/A')}")
    
    if limits_status.get('warnings'):
        print("Warnings Detected:")
        for warning in limits_status['warnings']:
            print(f"  - {warning}")
    
    # Get comprehensive summary
    summary = defense.get_session_summary()
    print(f"\nSession Summary:")
    print(f"  Config Loaded: {summary.get('config_loaded', False)}")
    print(f"  Features Enabled: {summary.get('features_enabled', {})}")
    
    # End session
    end_data = defense.end_session()
    print(f"\nSession ended - Duration: {end_data.get('duration', 0)/3600:.2f}h")


def demo_integration():
    """Demo integration between all components."""
    print("\n" + "="*60)
    print("DEMO: Full Integration")
    print("="*60)
    
    # Initialize both systems
    defense = create_anti_detection_defense()
    afk_manager = create_afk_reply_manager()
    
    # Start session
    session_data = defense.start_session()
    print(f"Session started: {session_data.get('session_id', 'N/A')}")
    
    # Simulate a typical gaming session
    print("\nSimulating typical gaming session...")
    
    for i in range(10):
        print(f"\n--- Cycle {i+1} ---")
        
        # Update activity
        afk_manager.update_activity()
        
        # Check AFK status
        afk_status = afk_manager.check_afk_status()
        if afk_status.get('afk'):
            print(f"  AFK Status: {afk_status.get('message', 'AFK')}")
        
        # Scan for whispers
        whispers = afk_manager.scan_for_whispers()
        if whispers:
            print(f"  Whispers detected: {len(whispers)}")
        
        # Perform actions with delays
        actions = ["combat_skill", "movement", "crafting"]
        for action in actions:
            if defense.track_action(action, {"test": True}):
                delay = defense.inject_human_delay(action)
                print(f"  {action}: {delay:.3f}s delay")
        
        # Inject random actions
        random_action = defense.inject_random_action()
        if random_action:
            print(f"  Random Action: {random_action}")
        
        # Inject dynamic movement
        movement = defense.inject_dynamic_movement()
        if movement:
            print(f"  Dynamic Movement: {movement['pattern']}")
        
        # Check session limits
        limits_status = defense.check_session_limits()
        if limits_status.get('warnings'):
            print(f"  Warnings: {len(limits_status['warnings'])}")
        
        time.sleep(0.5)
    
    # Final summaries
    print("\n" + "="*40)
    print("FINAL SUMMARIES")
    print("="*40)
    
    defense_summary = defense.get_session_summary()
    afk_summary = afk_manager.get_afk_summary()
    
    print(f"Anti-Detection Summary:")
    print(f"  Config Loaded: {defense_summary.get('config_loaded', False)}")
    print(f"  Features Enabled: {defense_summary.get('features_enabled', {})}")
    
    print(f"\nAFK Manager Summary:")
    print(f"  AFK Status: {afk_summary.get('afk_status', False)}")
    print(f"  Whisper History: {afk_summary.get('whisper_history_count', 0)}")
    print(f"  Reply History: {afk_summary.get('reply_history_count', 0)}")
    
    # End session
    defense.end_session()


def demo_configuration():
    """Demo configuration loading and validation."""
    print("\n" + "="*60)
    print("DEMO: Configuration Loading")
    print("="*60)
    
    config_path = "config/defense_config.json"
    
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("Configuration loaded successfully!")
        print(f"Configuration sections:")
        for section in config.keys():
            print(f"  - {section}")
        
        # Show some key settings
        session_limits = config.get("session_limits", {})
        print(f"\nSession Limits:")
        print(f"  Max Hours/Day: {session_limits.get('max_hours_per_day', 'N/A')}")
        print(f"  Max Consecutive Hours: {session_limits.get('max_consecutive_hours', 'N/A')}")
        
        human_delays = config.get("human_like_delays", {})
        print(f"\nHuman-Like Delays:")
        print(f"  Enabled: {human_delays.get('enabled', False)}")
        print(f"  Min Delay: {human_delays.get('action_delays', {}).get('min_delay', 'N/A')}s")
        print(f"  Max Delay: {human_delays.get('action_delays', {}).get('max_delay', 'N/A')}s")
        
        afk_config = config.get("afk_reply_manager", {})
        print(f"\nAFK Reply Manager:")
        print(f"  Whisper Scanning: {afk_config.get('whisper_scanning', {}).get('enabled', False)}")
        print(f"  RP Replies: {afk_config.get('rp_replies', {}).get('enabled', False)}")
        print(f"  Auto AFK Detection: {afk_config.get('auto_afk_detection', {}).get('enabled', False)}")
        
    else:
        print(f"Configuration file not found: {config_path}")


def main():
    """Run all anti-detection demos."""
    print("MS11 Batch 076 - Anti-Detection Defense Layer v1")
    print("="*60)
    print("This demo showcases comprehensive anti-detection features")
    print("to help avoid server-side bot flagging.")
    print("="*60)
    
    try:
        # Run individual demos
        demo_configuration()
        demo_session_randomization()
        demo_human_like_delays()
        demo_afk_reply_management()
        demo_cooldown_tracking()
        demo_dynamic_movement()
        demo_session_warnings()
        
        # Run integration demo
        demo_integration()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("All anti-detection features have been demonstrated.")
        print("The system is ready for production use.")
        
    except Exception as e:
        print(f"\nERROR during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
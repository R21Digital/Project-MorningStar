#!/usr/bin/env python3
"""
Demo script for Batch 074 - Heroics Module: Prerequisites + Lockout Logic

This demo showcases the comprehensive heroics management system including:
- Prerequisite tracking and validation
- Lockout timer management
- Difficulty tier support
- Axkva Min-specific handling
- Future support structure for party finder and cooldown alerts
"""

import sys
import time
from datetime import datetime, timedelta

# Add the project root to the path
sys.path.insert(0, '.')

from core.heroics_manager import create_heroics_manager
from utils.lockout_tracker import create_lockout_tracker
from android_ms11.utils.logging_utils import log_event


def demo_heroics_manager():
    """Demo the main heroics manager functionality."""
    print("\n" + "="*60)
    print("BATCH 074 DEMO: Heroics Manager")
    print("="*60)
    
    # Initialize heroics manager
    heroics_manager = create_heroics_manager()
    
    # Demo 1: Get heroics summary
    print("\n1. Heroics Summary:")
    summary = heroics_manager.get_heroics_summary()
    print(f"   Total Heroics: {summary['total_heroics']}")
    print(f"   Heroics by Planet:")
    for planet, heroics in summary['heroics_by_planet'].items():
        print(f"     {planet}: {len(heroics)} heroics")
    
    # Demo 2: Get specific heroic info
    print("\n2. Axkva Min Heroic Info:")
    axkva_info = heroics_manager.get_heroic_info("axkva_min")
    if "error" not in axkva_info:
        print(f"   Name: {axkva_info['name']}")
        print(f"   Planet: {axkva_info['planet']}")
        print(f"   Location: {axkva_info['location']}")
        print(f"   Difficulty Tiers: {list(axkva_info['difficulty_tiers'].keys())}")
        print(f"   Prerequisites:")
        for category, prereqs in axkva_info['prerequisites'].items():
            print(f"     {category}: {len(prereqs)} requirements")
    else:
        print(f"   Error: {axkva_info['error']}")
    
    # Demo 3: Check prerequisites for a character
    print("\n3. Prerequisite Checking:")
    character_name = "TestCharacter"
    prerequisite_check = heroics_manager.check_prerequisites(character_name, "axkva_min", "normal")
    
    print(f"   Character: {character_name}")
    print(f"   Heroic: Axkva Min (Normal)")
    print(f"   Can Enter: {prerequisite_check['can_enter']}")
    print(f"   Prerequisites Met: {prerequisite_check['prerequisites_met']}")
    
    if not prerequisite_check['can_enter']:
        print(f"   Reason: {prerequisite_check.get('reason', 'unknown')}")
        if prerequisite_check.get('missing_prerequisites'):
            print(f"   Missing Prerequisites:")
            for missing in prerequisite_check['missing_prerequisites']:
                print(f"     - {missing}")
    
    # Demo 4: Get available heroics for a character
    print("\n4. Available Heroics for Character:")
    available_heroics = heroics_manager.get_available_heroics(character_name)
    print(f"   Character: {character_name}")
    print(f"   Available: {available_heroics['total_available']}")
    print(f"   Unavailable: {available_heroics['total_unavailable']}")
    
    if available_heroics['available_heroics']:
        print("   Available Heroics:")
        for heroic in available_heroics['available_heroics'][:3]:  # Show first 3
            print(f"     - {heroic['name']} ({heroic['difficulty']}) on {heroic['planet']}")
    
    # Demo 5: Axkva Min specific handling
    print("\n5. Axkva Min Specific Handling:")
    axkva_specific = heroics_manager.get_axkva_min_info()
    if "error" not in axkva_specific:
        print(f"   Special Mechanics:")
        for mechanic_name, mechanic_info in axkva_specific.get('special_handling', {}).items():
            print(f"     {mechanic_name}: {mechanic_info['description']}")
            print(f"       Effect: {mechanic_info['effect']}")
            print(f"       Management: {mechanic_info['management']}")
    else:
        print(f"   Error: {axkva_specific['error']}")


def demo_lockout_tracker():
    """Demo the lockout tracker functionality."""
    print("\n" + "="*60)
    print("BATCH 074 DEMO: Lockout Tracker")
    print("="*60)
    
    # Initialize lockout tracker
    lockout_tracker = create_lockout_tracker()
    
    # Demo 1: Record heroic completions
    print("\n1. Recording Heroic Completions:")
    character_name = "TestCharacter"
    heroic_id = "axkva_min"
    
    # Record normal difficulty completion
    success = lockout_tracker.record_heroic_completion(character_name, heroic_id, "normal")
    print(f"   Recorded Axkva Min (Normal) completion: {'✓' if success else '✗'}")
    
    # Record hard difficulty completion
    success = lockout_tracker.record_heroic_completion(character_name, heroic_id, "hard")
    print(f"   Recorded Axkva Min (Hard) completion: {'✓' if success else '✗'}")
    
    # Demo 2: Check lockout status
    print("\n2. Lockout Status Checking:")
    lockout_status = lockout_tracker.check_lockout_status(character_name, heroic_id, "normal")
    print(f"   Character: {character_name}")
    print(f"   Heroic: {heroic_id}")
    print(f"   Difficulty: Normal")
    print(f"   Locked Out: {lockout_status['locked_out']}")
    print(f"   Can Enter: {lockout_status['can_enter']}")
    
    if lockout_status['locked_out']:
        time_remaining = lockout_status['time_remaining']
        hours = int(time_remaining // 3600)
        minutes = int((time_remaining % 3600) // 60)
        print(f"   Time Remaining: {hours}h {minutes}m")
        print(f"   Reset Time: {lockout_status['reset_time']}")
    
    # Demo 3: Get character lockouts
    print("\n3. Character Lockouts:")
    character_lockouts = lockout_tracker.get_character_lockouts(character_name)
    print(f"   Character: {character_lockouts['character_name']}")
    print(f"   Active Lockouts: {character_lockouts['total_lockouts']}")
    
    if character_lockouts['active_lockouts']:
        print("   Active Lockouts:")
        for lockout in character_lockouts['active_lockouts']:
            time_remaining = lockout['time_remaining']
            hours = int(time_remaining // 3600)
            minutes = int((time_remaining % 3600) // 60)
            print(f"     - {lockout['heroic_id']} ({lockout['difficulty']}): {hours}h {minutes}m remaining")
    
    # Demo 4: Get instance lockouts
    print("\n4. Instance Lockouts:")
    instance_lockouts = lockout_tracker.get_instance_lockouts(heroic_id)
    print(f"   Heroic: {instance_lockouts['heroic_id']}")
    print(f"   Total Lockouts: {instance_lockouts['total_lockouts']}")
    
    if instance_lockouts['active_lockouts']:
        print("   Active Lockouts:")
        for lockout in instance_lockouts['active_lockouts']:
            time_remaining = lockout['time_remaining']
            hours = int(time_remaining // 3600)
            minutes = int((time_remaining % 3600) // 60)
            print(f"     - {lockout['character_name']} ({lockout['difficulty']}): {hours}h {minutes}m remaining")
    
    # Demo 5: Clear expired lockouts
    print("\n5. Clearing Expired Lockouts:")
    cleared_count = lockout_tracker.clear_expired_lockouts()
    print(f"   Cleared {cleared_count} expired lockouts")
    
    # Demo 6: Export lockout data
    print("\n6. Exporting Lockout Data:")
    export_path = lockout_tracker.export_lockout_data()
    if export_path:
        print(f"   Exported to: {export_path}")
    else:
        print("   Export failed")


def demo_integration():
    """Demo the integration between heroics manager and lockout tracker."""
    print("\n" + "="*60)
    print("BATCH 074 DEMO: Integration")
    print("="*60)
    
    # Initialize both systems
    heroics_manager = create_heroics_manager()
    lockout_tracker = create_lockout_tracker()
    
    # Demo 1: Complete workflow
    print("\n1. Complete Heroic Workflow:")
    character_name = "IntegrationTest"
    heroic_id = "axkva_min"
    difficulty = "normal"
    
    # Step 1: Check if character can enter
    print(f"   Step 1: Checking prerequisites for {character_name}")
    prerequisite_check = heroics_manager.check_prerequisites(character_name, heroic_id, difficulty)
    print(f"   Can Enter: {prerequisite_check['can_enter']}")
    
    if prerequisite_check['can_enter']:
        # Step 2: Simulate heroic completion
        print(f"   Step 2: Completing heroic")
        completion_data = {
            "loot": ["axkva_min_crystal", "dark_side_relic"],
            "experience": 50000,
            "credits": 100000,
            "completion_time": datetime.now().isoformat()
        }
        
        success = heroics_manager.record_heroic_completion(
            character_name, heroic_id, difficulty, completion_data
        )
        print(f"   Completion Recorded: {'✓' if success else '✗'}")
        
        # Step 3: Check lockout status
        print(f"   Step 3: Checking lockout status")
        lockout_status = lockout_tracker.check_lockout_status(character_name, heroic_id, difficulty)
        print(f"   Locked Out: {lockout_status['locked_out']}")
        print(f"   Can Enter Again: {lockout_status['can_enter']}")
        
        if lockout_status['locked_out']:
            time_remaining = lockout_status['time_remaining']
            hours = int(time_remaining // 3600)
            minutes = int((time_remaining % 3600) // 60)
            print(f"   Time Until Reset: {hours}h {minutes}m")
    
    # Demo 2: Multiple characters
    print("\n2. Multiple Character Support:")
    characters = ["Player1", "Player2", "Player3"]
    
    for i, character in enumerate(characters):
        print(f"   Character {i+1}: {character}")
        
        # Record completion for each character
        success = lockout_tracker.record_heroic_completion(character, heroic_id, difficulty)
        print(f"     Recorded completion: {'✓' if success else '✗'}")
        
        # Check their lockout status
        lockout_status = lockout_tracker.check_lockout_status(character, heroic_id, difficulty)
        print(f"     Locked out: {lockout_status['locked_out']}")
    
    # Demo 3: Instance overview
    print("\n3. Instance Overview:")
    instance_lockouts = lockout_tracker.get_instance_lockouts(heroic_id)
    print(f"   Heroic: {heroic_id}")
    print(f"   Total Active Lockouts: {instance_lockouts['total_lockouts']}")
    print(f"   Available Characters: {len(instance_lockouts['available_characters'])}")
    
    if instance_lockouts['active_lockouts']:
        print("   Currently Locked Out:")
        for lockout in instance_lockouts['active_lockouts']:
            time_remaining = lockout['time_remaining']
            hours = int(time_remaining // 3600)
            minutes = int((time_remaining % 3600) // 60)
            print(f"     - {lockout['character_name']} ({lockout['difficulty']}): {hours}h {minutes}m")


def demo_future_features():
    """Demo the structure for future features."""
    print("\n" + "="*60)
    print("BATCH 074 DEMO: Future Features Structure")
    print("="*60)
    
    print("\n1. Party Finder Integration:")
    print("   - Track available players for each heroic")
    print("   - Match players based on prerequisites")
    print("   - Coordinate lockout timers across party")
    print("   - Handle party formation and disbanding")
    
    print("\n2. Cooldown Alerts:")
    print("   - Discord notifications when lockouts expire")
    print("   - In-game alerts for available heroics")
    print("   - Calendar integration for reset times")
    print("   - Email notifications for weekly resets")
    
    print("\n3. Advanced Prerequisites:")
    print("   - Real-time quest completion tracking")
    print("   - Skill level validation")
    print("   - Inventory item checking")
    print("   - Reputation system integration")
    
    print("\n4. Heroic Analytics:")
    print("   - Completion time tracking")
    print("   - Success rate analysis")
    print("   - Difficulty tier comparison")
    print("   - Loot drop statistics")
    
    print("\n5. Automated Features:")
    print("   - Auto-queue for heroic instances")
    print("   - Smart party composition")
    print("   - Optimal timing recommendations")
    print("   - Performance optimization suggestions")


def main():
    """Run the complete Batch 074 demo."""
    print("MS11 Batch 074 - Heroics Module: Prerequisites + Lockout Logic")
    print("="*80)
    print("This demo showcases the comprehensive heroics management system")
    print("including prerequisite tracking, lockout timers, and future features.")
    print("="*80)
    
    try:
        # Run all demos
        demo_heroics_manager()
        demo_lockout_tracker()
        demo_integration()
        demo_future_features()
        
        print("\n" + "="*80)
        print("✓ Batch 074 Demo Completed Successfully!")
        print("="*80)
        
        print("\nKey Features Demonstrated:")
        print("✓ Heroics data loading and management")
        print("✓ Prerequisite checking and validation")
        print("✓ Lockout timer tracking (per character/instance)")
        print("✓ Difficulty tier support (normal/hard)")
        print("✓ Axkva Min-specific handling")
        print("✓ Future support structure")
        print("✓ Data persistence and export")
        print("✓ Multi-character support")
        
        print("\nFiles Created:")
        print("✓ data/heroics/axkva_min.yml")
        print("✓ data/heroics/heroics_index.yml")
        print("✓ utils/lockout_tracker.py")
        print("✓ core/heroics_manager.py")
        print("✓ demo_batch_074_heroics_module.py")
        
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
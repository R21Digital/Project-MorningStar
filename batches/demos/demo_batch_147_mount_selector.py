#!/usr/bin/env python3
"""
Demo script for Batch 147 - Mount Preference Selector (Mount Scan + Fallback)
Demonstrates the mount selection functionality and integration
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
import sys

# Add core directory to path for imports
sys.path.append(str(Path(__file__).parent / "core"))
from mount_scanner import MountScanner

def demo_mount_scanner():
    """Demonstrate the mount scanner functionality"""
    print("=" * 60)
    print("BATCH 147 - MOUNT PREFERENCE SELECTOR DEMO")
    print("=" * 60)
    
    # Initialize mount scanner
    scanner = MountScanner()
    
    print("\n1. Testing Mount Scanning")
    print("-" * 40)
    
    # Scan for available mounts
    available_mounts = scanner.scan_available_mounts()
    print(f"✓ Available mounts: {available_mounts}")
    
    print("\n2. Testing Mount Selection Types")
    print("-" * 40)
    
    # Test different selection types
    selection_types = ["Fastest", "Random", "Manual"]
    
    for selection_type in selection_types:
        print(f"\n🎯 Testing {selection_type} selection:")
        selected_mount, success = scanner.select_mount(selection_type)
        print(f"  Selected: {selected_mount}")
        print(f"  Success: {'✅' if success else '❌'}")
    
    print("\n3. Testing Retry Logic")
    print("-" * 40)
    
    # Test retry logic with fallback
    print("🔄 Testing retry mount selection:")
    selected_mount, success = scanner.retry_mount_selection(max_attempts=3)
    print(f"  Final result: {selected_mount}")
    print(f"  Success: {'✅' if success else '❌'}")
    
    print("\n4. Testing Configuration Management")
    print("-" * 40)
    
    # Test preference updates
    preferences = ["Random", "Fastest", "Manual"]
    for preference in preferences:
        success = scanner.update_mount_preference(preference)
        print(f"  Updated preference to {preference}: {'✅' if success else '❌'}")
    
    # Test mount management
    test_mounts = ["Test Mount 1", "Test Mount 2"]
    for mount in test_mounts:
        success = scanner.add_owned_mount(mount)
        print(f"  Added mount {mount}: {'✅' if success else '❌'}")
    
    for mount in test_mounts:
        success = scanner.remove_owned_mount(mount)
        print(f"  Removed mount {mount}: {'✅' if success else '❌'}")
    
    print("\n5. Testing Statistics")
    print("-" * 40)
    
    # Get mount statistics
    stats = scanner.get_mount_statistics()
    print(f"📊 Mount Statistics:")
    print(f"  Total attempts: {stats['total_attempts']}")
    print(f"  Successful: {stats['successful_attempts']}")
    print(f"  Success rate: {stats['success_rate']:.1f}%")
    print(f"  Most used: {stats['most_used_mount']}")
    print(f"  Recent mounts: {stats['recent_mounts']}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED SUCCESSFULLY")
    print("=" * 60)
    
    return True

def demo_integration_scenarios():
    """Demonstrate integration scenarios"""
    print("\n" + "=" * 60)
    print("INTEGRATION SCENARIOS DEMO")
    print("=" * 60)
    
    scanner = MountScanner()
    
    print("\n1. Scenario: Fast Travel Setup")
    print("-" * 40)
    
    # Simulate fast travel scenario
    print("🎯 Setting up for fast travel...")
    
    # Set preference to fastest
    scanner.update_mount_preference("Fastest")
    print("  ✓ Set preference to Fastest")
    
    # Select mount
    selected_mount, success = scanner.select_mount()
    print(f"  ✓ Selected mount: {selected_mount}")
    print(f"  ✓ Success: {'✅' if success else '❌'}")
    
    print("\n2. Scenario: Random Mount for Fun")
    print("-" * 40)
    
    # Simulate random mount selection
    print("🎲 Selecting random mount for variety...")
    
    # Set preference to random
    scanner.update_mount_preference("Random")
    print("  ✓ Set preference to Random")
    
    # Select mount multiple times
    for i in range(3):
        selected_mount, success = scanner.select_mount()
        print(f"  {i+1}. Selected: {selected_mount} ({'✅' if success else '❌'})")
        time.sleep(0.5)
    
    print("\n3. Scenario: Mount Failure Recovery")
    print("-" * 40)
    
    # Simulate mount failure and recovery
    print("🔄 Testing mount failure recovery...")
    
    # Simulate failed mount attempts
    print("  Simulating failed mount attempts...")
    for i in range(2):
        print(f"    Attempt {i+1}: Failed")
        time.sleep(0.3)
    
    # Use retry logic
    selected_mount, success = scanner.retry_mount_selection(max_attempts=3)
    print(f"  ✓ Recovery result: {selected_mount}")
    print(f"  ✓ Success: {'✅' if success else '❌'}")
    
    print("\n4. Scenario: Mount Collection Management")
    print("-" * 40)
    
    # Simulate mount collection management
    print("📚 Managing mount collection...")
    
    # Add new mounts
    new_mounts = ["Rare Mount", "Epic Mount", "Legendary Mount"]
    for mount in new_mounts:
        success = scanner.add_owned_mount(mount)
        print(f"  ✓ Added {mount}: {'✅' if success else '❌'}")
    
    # Show updated available mounts
    available_mounts = scanner.scan_available_mounts()
    print(f"  ✓ Available mounts: {len(available_mounts)}")
    
    # Remove test mounts
    for mount in new_mounts:
        success = scanner.remove_owned_mount(mount)
        print(f"  ✓ Removed {mount}: {'✅' if success else '❌'}")
    
    print("\n" + "=" * 60)
    print("INTEGRATION SCENARIOS DEMO COMPLETED")
    print("=" * 60)

def demo_advanced_features():
    """Demonstrate advanced features"""
    print("\n" + "=" * 60)
    print("ADVANCED FEATURES DEMO")
    print("=" * 60)
    
    scanner = MountScanner()
    
    print("\n1. Testing Mount Speed Analysis")
    print("-" * 40)
    
    # Analyze mount speeds
    mount_speeds = scanner.player_config.get("mount_speeds", {})
    available_mounts = scanner.scan_available_mounts()
    
    print("Speed analysis of available mounts:")
    for mount in available_mounts:
        speed = mount_speeds.get(mount, 0.0)
        print(f"  {mount}: {speed} speed units")
    
    # Find fastest mount manually
    fastest_mount = None
    fastest_speed = 0.0
    for mount in available_mounts:
        speed = mount_speeds.get(mount, 0.0)
        if speed > fastest_speed:
            fastest_speed = speed
            fastest_mount = mount
    
    print(f"\n🏆 Fastest available mount: {fastest_mount} ({fastest_speed} speed)")
    
    print("\n2. Testing Mount Categories")
    print("-" * 40)
    
    # Show mount categories
    categories = scanner.player_config.get("mount_categories", {})
    print("Mount categories:")
    for category, mounts in categories.items():
        print(f"  {category}: {len(mounts)} mounts")
        for mount in mounts[:3]:  # Show first 3
            print(f"    - {mount}")
    
    print("\n3. Testing Configuration Persistence")
    print("-" * 40)
    
    # Test configuration persistence
    original_preference = scanner.player_config.get("preferred_mount", "Fastest")
    print(f"  Original preference: {original_preference}")
    
    # Change preference
    scanner.update_mount_preference("Random")
    new_preference = scanner.player_config.get("preferred_mount", "Unknown")
    print(f"  New preference: {new_preference}")
    
    # Restore original
    scanner.update_mount_preference(original_preference)
    restored_preference = scanner.player_config.get("preferred_mount", "Unknown")
    print(f"  Restored preference: {restored_preference}")
    
    print("\n4. Testing Error Handling")
    print("-" * 40)
    
    # Test invalid operations
    print("Testing error handling:")
    
    # Test invalid preference
    success = scanner.update_mount_preference("Invalid")
    print(f"  Invalid preference: {'❌' if not success else '✅'}")
    
    # Test removing non-existent mount
    success = scanner.remove_owned_mount("NonExistentMount")
    print(f"  Remove non-existent mount: {'✅' if success else '❌'}")
    
    # Test adding duplicate mount
    test_mount = "TestMount"
    scanner.add_owned_mount(test_mount)
    success = scanner.add_owned_mount(test_mount)  # Duplicate
    print(f"  Add duplicate mount: {'✅' if success else '❌'}")
    scanner.remove_owned_mount(test_mount)  # Cleanup
    
    print("\n" + "=" * 60)
    print("ADVANCED FEATURES DEMO COMPLETED")
    print("=" * 60)

def demo_cli_integration():
    """Demonstrate CLI integration"""
    print("\n" + "=" * 60)
    print("CLI INTEGRATION DEMO")
    print("=" * 60)
    
    # Import CLI module
    sys.path.append(str(Path(__file__).parent / "cli"))
    from mount_selector import MountSelectorCLI
    
    cli = MountSelectorCLI()
    
    print("\n1. Testing CLI Mount Listing")
    print("-" * 40)
    
    # Test CLI functions
    cli.show_available_mounts()
    
    print("\n2. Testing CLI Statistics")
    print("-" * 40)
    
    cli.show_mount_statistics()
    
    print("\n3. Testing CLI Configuration")
    print("-" * 40)
    
    cli.show_config()
    
    print("\n4. Testing CLI Mount Selection")
    print("-" * 40)
    
    # Test different selection types
    for selection_type in ["Fastest", "Random", "Manual"]:
        print(f"\nTesting {selection_type} selection:")
        cli.select_mount(selection_type)
    
    print("\n5. Testing CLI Retry Logic")
    print("-" * 40)
    
    cli.retry_mount_selection()
    
    print("\n" + "=" * 60)
    print("CLI INTEGRATION DEMO COMPLETED")
    print("=" * 60)

def main():
    """Main demo function"""
    try:
        print("Starting Batch 147 - Mount Preference Selector Demo")
        print("This demo will test the MS11 mount selection integration")
        
        # Run basic demo
        demo_mount_scanner()
        
        # Run integration scenarios
        demo_integration_scenarios()
        
        # Run advanced features demo
        demo_advanced_features()
        
        # Run CLI integration demo
        demo_cli_integration()
        
        print("\n" + "=" * 60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Check config/player_config.json for mount settings")
        print("2. Use cli/mount_selector.py for interactive mount management")
        print("3. Integrate mount_scanner.py with MS11 session management")
        print("4. Configure automatic mount selection during gameplay")
        print("5. Future: Add mount unlock tracker in /collections/mounts")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
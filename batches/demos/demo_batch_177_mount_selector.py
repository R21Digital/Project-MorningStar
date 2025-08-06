#!/usr/bin/env python3
"""
Demo script for Batch 177 - Mount Selector Integration
Demonstrates auto-detection, selection modes, and graceful fallback handling
"""

import os
import sys
import json
import time
import random
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from core.navigation.mount_handler import MountHandler, MountSelectionMode


def demo_basic_functionality():
    """Demonstrate basic mount handler functionality"""
    print("🐎 Batch 177 - Mount Selector Integration Demo")
    print("=" * 60)
    
    # Initialize mount handler
    handler = MountHandler(character_name="DemoCharacter")
    
    print("\n📊 Mount Handler Status:")
    print(f"Character: {handler.character_name}")
    print(f"Selection Mode: {handler.character_settings.selection_mode}")
    print(f"Auto-detect Enabled: {handler.character_settings.auto_detect_enabled}")
    print(f"Preferred Mounts: {handler.character_settings.preferred_mounts}")
    print(f"Banned Mounts: {handler.character_settings.banned_mounts}")
    
    return handler


def demo_auto_detection(handler):
    """Demonstrate mount auto-detection"""
    print("\n🔍 Mount Auto-Detection:")
    print("-" * 40)
    
    # Perform auto-detection
    detected_mounts = handler.auto_detect_mounts()
    
    print(f"Detected {len(detected_mounts)} mounts:")
    for mount_id, mount_info in detected_mounts.items():
        print(f"  • {mount_info.name} ({mount_id}) - Speed: {mount_info.speed}, Type: {mount_info.mount_type}")
    
    return detected_mounts


def demo_selection_modes(handler):
    """Demonstrate different selection modes"""
    print("\n🎯 Mount Selection Modes:")
    print("-" * 40)
    
    # Test each selection mode
    modes = ["fastest", "random", "specific"]
    contexts = ["travel", "combat", "hunting", "city"]
    
    for mode in modes:
        print(f"\n📋 Mode: {mode.upper()}")
        handler.update_character_settings({"selection_mode": mode})
        
        for context in contexts:
            selected_mount = handler.select_mount(context=context)
            if selected_mount:
                print(f"  {context.capitalize()}: {selected_mount.name} (speed: {selected_mount.speed})")
            else:
                print(f"  {context.capitalize()}: No mount available (using fallback)")


def demo_situational_preferences(handler):
    """Demonstrate situational preferences"""
    print("\n🎭 Situational Preferences:")
    print("-" * 40)
    
    # Set up situational preferences
    situational_settings = {
        "situational_preferences": {
            "combat": {
                "preferred_mounts": ["jetpack", "swoop_bike"],
                "fallback": "fastest_available"
            },
            "travel": {
                "preferred_mounts": ["landspeeder", "speeder_bike"],
                "fallback": "fastest_available"
            },
            "hunting": {
                "preferred_mounts": ["dewback", "varactyl"],
                "fallback": "fastest_available"
            },
            "city": {
                "preferred_mounts": ["speeder_bike", "hover_speeder"],
                "fallback": "fastest_available"
            }
        }
    }
    
    # Update character settings
    characters = handler.user_settings.get("characters", {})
    if "DemoCharacter" not in characters:
        characters["DemoCharacter"] = {}
    characters["DemoCharacter"].update(situational_settings)
    
    # Test situational selection
    contexts = ["combat", "travel", "hunting", "city"]
    handler.update_character_settings({"selection_mode": "specific"})
    
    for context in contexts:
        selected_mount = handler.select_mount(context=context)
        if selected_mount:
            print(f"  {context.capitalize()}: {selected_mount.name} (speed: {selected_mount.speed})")
        else:
            print(f"  {context.capitalize()}: No preferred mount available")


def demo_mount_management(handler):
    """Demonstrate mount management features"""
    print("\n⚙️ Mount Management:")
    print("-" * 40)
    
    # Get available mounts
    available_mounts = handler.get_available_mounts()
    print(f"Available mounts: {len(available_mounts)}")
    
    # Show mount statistics
    stats = handler.get_mount_statistics()
    print(f"Total mounts: {stats['total_mounts']}")
    print(f"Available mounts: {stats['available_mounts']}")
    if stats['fastest_mount']:
        print(f"Fastest: {stats['fastest_mount']['name']} ({stats['fastest_mount']['speed']} speed)")
    if stats['slowest_mount']:
        print(f"Slowest: {stats['slowest_mount']['name']} ({stats['slowest_mount']['speed']} speed)")
    
    # Test mount availability
    test_mounts = ["jetpack", "swoop_bike", "landspeeder", "nonexistent_mount"]
    print("\nMount availability check:")
    for mount_name in test_mounts:
        is_available = handler.is_mount_available(mount_name)
        print(f"  {mount_name}: {'Available' if is_available else 'Not available'}")


def demo_fallback_handling(handler):
    """Demonstrate graceful fallback handling"""
    print("\n🛡️ Fallback Handling:")
    print("-" * 40)
    
    # Test scenarios where no mounts are available
    print("Testing fallback scenarios:")
    
    # Scenario 1: All mounts banned
    print("\n1. All mounts banned:")
    handler.update_character_settings({"banned_mounts": ["jetpack", "swoop_bike", "landspeeder", "speeder_bike", "dewback", "bantha"]})
    selected_mount = handler.select_mount()
    if selected_mount:
        print(f"   Selected: {selected_mount.name} (fallback)")
    
    # Scenario 2: Auto-detect disabled
    print("\n2. Auto-detect disabled:")
    handler.update_character_settings({"auto_detect_enabled": False, "banned_mounts": []})
    selected_mount = handler.select_mount()
    if selected_mount:
        print(f"   Selected: {selected_mount.name} (fallback)")
    
    # Scenario 3: No preferred mounts available
    print("\n3. No preferred mounts available:")
    handler.update_character_settings({"auto_detect_enabled": True, "selection_mode": "specific", "preferred_mounts": ["nonexistent_mount"]})
    selected_mount = handler.select_mount()
    if selected_mount:
        print(f"   Selected: {selected_mount.name} (fallback to fastest)")
    
    # Reset to normal settings
    handler.update_character_settings({
        "auto_detect_enabled": True,
        "banned_mounts": [],
        "preferred_mounts": [],
        "selection_mode": "fastest"
    })


def demo_character_settings(handler):
    """Demonstrate character-specific settings"""
    print("\n👤 Character Settings Management:")
    print("-" * 40)
    
    # Show current settings
    print("Current settings:")
    print(f"  Selection mode: {handler.character_settings.selection_mode}")
    print(f"  Preferred mounts: {handler.character_settings.preferred_mounts}")
    print(f"  Banned mounts: {handler.character_settings.banned_mounts}")
    
    # Update settings
    print("\nUpdating settings...")
    new_settings = {
        "selection_mode": "random",
        "preferred_mounts": ["jetpack", "swoop_bike"],
        "banned_mounts": ["slow_creature"]
    }
    
    success = handler.update_character_settings(new_settings)
    if success:
        print("Settings updated successfully!")
        print(f"  New selection mode: {handler.character_settings.selection_mode}")
        print(f"  New preferred mounts: {handler.character_settings.preferred_mounts}")
        print(f"  New banned mounts: {handler.character_settings.banned_mounts}")
    else:
        print("Failed to update settings")


def demo_performance_features(handler):
    """Demonstrate performance and caching features"""
    print("\n⚡ Performance Features:")
    print("-" * 40)
    
    # Test caching
    print("Testing mount detection caching:")
    
    start_time = time.time()
    mounts1 = handler.auto_detect_mounts()
    time1 = time.time() - start_time
    
    start_time = time.time()
    mounts2 = handler.auto_detect_mounts()
    time2 = time.time() - start_time
    
    print(f"  First detection: {time1:.3f}s ({len(mounts1)} mounts)")
    print(f"  Cached detection: {time2:.3f}s ({len(mounts2)} mounts)")
    print(f"  Cache speedup: {time1/time2:.1f}x faster")
    
    # Test multiple selections
    print("\nTesting multiple mount selections:")
    start_time = time.time()
    for i in range(10):
        handler.select_mount(context="travel")
    total_time = time.time() - start_time
    print(f"  10 mount selections: {total_time:.3f}s ({total_time/10:.3f}s per selection)")


def demo_integration_scenarios(handler):
    """Demonstrate integration scenarios"""
    print("\n🔗 Integration Scenarios:")
    print("-" * 40)
    
    # Scenario 1: Travel navigation
    print("1. Travel Navigation:")
    travel_mount = handler.select_mount(context="travel")
    if travel_mount:
        print(f"   Selected for travel: {travel_mount.name}")
        print(f"   Speed: {travel_mount.speed}")
        print(f"   Summon time: {travel_mount.summon_time}s")
    
    # Scenario 2: Combat situation
    print("\n2. Combat Situation:")
    combat_mount = handler.select_mount(context="combat")
    if combat_mount:
        print(f"   Selected for combat: {combat_mount.name}")
        print(f"   Speed: {combat_mount.speed}")
        print(f"   Type: {combat_mount.mount_type}")
    
    # Scenario 3: City travel
    print("\n3. City Travel:")
    city_mount = handler.select_mount(context="city")
    if city_mount:
        print(f"   Selected for city: {city_mount.name}")
        print(f"   Speed: {city_mount.speed}")
        print(f"   Available: {city_mount.is_available}")


def demo_error_handling(handler):
    """Demonstrate error handling and graceful degradation"""
    print("\n🛡️ Error Handling:")
    print("-" * 40)
    
    # Test various error scenarios
    print("Testing error scenarios:")
    
    # Scenario 1: Corrupted mount data
    print("\n1. Corrupted mount data:")
    original_mounts_data = handler.mounts_data
    handler.mounts_data = {"corrupted": {"invalid": "data"}}
    selected_mount = handler.select_mount()
    if selected_mount:
        print(f"   Fallback mount: {selected_mount.name}")
    handler.mounts_data = original_mounts_data
    
    # Scenario 2: Missing configuration
    print("\n2. Missing configuration:")
    original_user_settings = handler.user_settings
    handler.user_settings = {}
    selected_mount = handler.select_mount()
    if selected_mount:
        print(f"   Default mount: {selected_mount.name}")
    handler.user_settings = original_user_settings
    
    # Scenario 3: Invalid selection mode
    print("\n3. Invalid selection mode:")
    handler.update_character_settings({"selection_mode": "invalid_mode"})
    selected_mount = handler.select_mount()
    if selected_mount:
        print(f"   Fallback selection: {selected_mount.name}")
    
    # Reset to normal
    handler.update_character_settings({"selection_mode": "fastest"})


def demo_command_line_usage():
    """Demonstrate command line usage"""
    print("\n💻 Command Line Usage Examples:")
    print("-" * 40)
    
    examples = [
        ("List available mounts", "python core/navigation/mount_handler.py --list"),
        ("Show mount statistics", "python core/navigation/mount_handler.py --stats"),
        ("Set selection mode", "python core/navigation/mount_handler.py --set-mode random"),
        ("Add preferred mount", "python core/navigation/mount_handler.py --add-preferred jetpack"),
        ("Add banned mount", "python core/navigation/mount_handler.py --add-banned slow_creature"),
        ("Select mount for specific context", "python core/navigation/mount_handler.py --context combat"),
        ("Use specific character", "python core/navigation/mount_handler.py --character MyCharacter")
    ]
    
    for description, command in examples:
        print(f"• {description}:")
        print(f"  {command}")


def main():
    """Main demo function"""
    try:
        # Initialize and show basic functionality
        handler = demo_basic_functionality()
        
        # Demonstrate auto-detection
        demo_auto_detection(handler)
        
        # Demonstrate selection modes
        demo_selection_modes(handler)
        
        # Demonstrate situational preferences
        demo_situational_preferences(handler)
        
        # Demonstrate mount management
        demo_mount_management(handler)
        
        # Demonstrate fallback handling
        demo_fallback_handling(handler)
        
        # Demonstrate character settings
        demo_character_settings(handler)
        
        # Demonstrate performance features
        demo_performance_features(handler)
        
        # Demonstrate integration scenarios
        demo_integration_scenarios(handler)
        
        # Demonstrate error handling
        demo_error_handling(handler)
        
        # Show command line usage
        demo_command_line_usage()
        
        print("\n✅ Batch 177 Demo Completed Successfully!")
        print("\n🎯 Key Features Demonstrated:")
        print("• Auto-detect learned mounts from macro/keybind data")
        print("• Selection modes: fastest, random, specific")
        print("• Per-character configuration in user_settings.json")
        print("• Graceful fallback handling when no mount is set")
        print("• Situational preferences for different contexts")
        print("• Comprehensive error handling and logging")
        print("• Performance optimization with caching")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
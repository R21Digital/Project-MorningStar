#!/usr/bin/env python3
"""
Demonstration script for Batch 031 - Mount Detection & Mount-Up Logic

This script demonstrates the mount handler functionality including:
- OCR-based detection of "Call Mount" hotbar button
- Auto-mount for long-distance travel
- Fallback support for /mount [name] command
- Detection of AV-21, swoop, and creature mounts
- Configurable auto-mount settings
"""

import time
from pathlib import Path

# Import the mount handler modules
try:
    from movement.mount_handler import (
        get_mount_handler, detect_mounts, auto_mount_for_travel,
        mount_creature, get_mount_status, MountDetectionResult,
        MountStatus, MountType
    )
    MOUNT_HANDLER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import mount handler modules: {e}")
    MOUNT_HANDLER_AVAILABLE = False


def demonstrate_mount_handler():
    """Demonstrate mount handler functionality."""
    if not MOUNT_HANDLER_AVAILABLE:
        print("Mount handler modules not available. Skipping demonstration.")
        return
    
    print("=== Mount Handler Demonstration ===\n")
    
    # Get mount handler
    handler = get_mount_handler()
    
    print("1. Mount Handler Initialization")
    print("-" * 35)
    print(f"OCR Available: {handler.ocr_engine is not None}")
    print(f"Current Status: {handler.current_status.value}")
    print(f"Auto Mount Enabled: {handler.auto_mount}")
    print(f"Auto Mount Distance: {handler.auto_mount_distance}m")
    print(f"Total Mounts: {len(handler.mounts)}")
    print(f"Detection History: {len(handler.detection_history)}")
    print()
    
    # Show available mounts
    print("2. Available Mounts")
    print("-" * 20)
    
    for mount_name, mount_info in handler.mounts.items():
        status_icon = "✓" if mount_info.learned else "✗"
        print(f"{status_icon} {mount_info.name} ({mount_info.mount_type.value})")
        print(f"   Speed: {mount_info.speed}x")
        print(f"   Indoor Allowed: {mount_info.indoor_allowed}")
        print(f"   City Allowed: {mount_info.city_allowed}")
        print(f"   Combat Allowed: {mount_info.combat_allowed}")
        print(f"   Command: {mount_info.command}")
        print()
    
    # Demonstrate mount detection
    print("3. Mount Detection")
    print("-" * 18)
    
    print("Detecting mounts using OCR...")
    detection_result = handler.detect_mounts()
    
    print(f"Detection completed in {detection_result.detection_time:.2f}s")
    print(f"Confidence: {detection_result.confidence:.1f}%")
    print(f"Total mounts found: {len(detection_result.mounts_found)}")
    print(f"Hotbar mounts: {len(detection_result.hotbar_mounts)}")
    print(f"Command mounts: {len(detection_result.command_mounts)}")
    
    if detection_result.mounts_found:
        print("\nDetected mounts:")
        for mount in detection_result.mounts_found:
            print(f"  - {mount}")
    else:
        print("\nNo mounts detected (normal if not in game)")
    print()
    
    # Demonstrate auto-mount logic
    print("4. Auto-Mount Logic")
    print("-" * 18)
    
    # Test different travel distances
    test_distances = [50, 100, 150, 200]
    test_zones = ["mos_eisley", "tatooine_desert", "indoor_building"]
    
    for distance in test_distances:
        for zone in test_zones:
            should_mount = handler.should_auto_mount(distance, zone)
            status_icon = "✓" if should_mount else "✗"
            print(f"{status_icon} {distance}m in {zone}: {'Auto-mount' if should_mount else 'Walk'}")
    
    print()
    
    # Demonstrate mount selection
    print("5. Mount Selection")
    print("-" * 18)
    
    for zone in test_zones:
        best_mount = handler.get_best_mount(zone)
        if best_mount:
            mount_info = handler.mounts[best_mount]
            print(f"Best mount for {zone}: {best_mount} (speed: {mount_info.speed}x)")
        else:
            print(f"No suitable mount for {zone}")
    
    print()
    
    # Demonstrate auto-mount for travel
    print("6. Auto-Mount for Travel")
    print("-" * 24)
    
    # Test auto-mount for long distance
    travel_distance = 200
    zone_name = "tatooine_desert"
    
    print(f"Testing auto-mount for {travel_distance}m travel in {zone_name}...")
    mount_success = handler.auto_mount_for_travel(travel_distance, zone_name)
    
    if mount_success:
        print("✅ Auto-mount successful")
    else:
        print("❌ Auto-mount failed")
    
    # Test auto-mount for short distance
    travel_distance = 50
    print(f"Testing auto-mount for {travel_distance}m travel in {zone_name}...")
    mount_success = handler.auto_mount_for_travel(travel_distance, zone_name)
    
    if mount_success:
        print("✅ Auto-mount successful")
    else:
        print("❌ Auto-mount failed (expected for short distance)")
    
    print()
    
    # Demonstrate specific mount mounting
    print("7. Specific Mount Mounting")
    print("-" * 27)
    
    # Try to mount a specific mount
    mount_name = "Speederbike"
    print(f"Attempting to mount {mount_name}...")
    
    mount_success = handler.mount_creature(mount_name)
    
    if mount_success:
        print("✅ Mount successful")
    else:
        print("❌ Mount failed")
    
    # Try to mount best available mount
    print("Attempting to mount best available mount...")
    mount_success = handler.mount_creature()
    
    if mount_success:
        print("✅ Best mount successful")
    else:
        print("❌ Best mount failed")
    
    print()
    
    # Demonstrate dismounting
    print("8. Dismounting")
    print("-" * 12)
    
    print("Dismounting creature...")
    dismount_success = handler.dismount_creature()
    
    if dismount_success:
        print("✅ Dismount successful")
    else:
        print("❌ Dismount failed")
    
    print()
    
    # Show mount status
    print("9. Mount Status")
    print("-" * 14)
    
    status = handler.get_mount_status()
    print(f"Current Status: {status['current_status']}")
    print(f"Auto Mount Enabled: {status['auto_mount_enabled']}")
    print(f"Auto Mount Distance: {status['auto_mount_distance']}m")
    print(f"Available Mounts: {len(status['available_mounts'])}")
    print(f"Total Mounts: {status['total_mounts']}")
    print(f"Learned Mounts: {status['learned_mounts']}")
    print(f"Detection History: {status['detection_history_count']}")
    
    if status['available_mounts']:
        print("\nAvailable mounts:")
        for mount in status['available_mounts']:
            print(f"  - {mount}")
    
    print()


def demonstrate_data_files():
    """Demonstrate the data files for Batch 031."""
    print("=== Data Files Demonstration ===\n")
    
    # Check if data files exist
    mounts_file = Path("data/mounts.yaml")
    
    print("1. Data File Status")
    print("-" * 20)
    print(f"Mounts configuration: {'✅ Found' if mounts_file.exists() else '❌ Missing'}")
    print()
    
    if mounts_file.exists():
        print("2. Mounts Configuration")
        print("-" * 25)
        
        try:
            import yaml
            with open(mounts_file, 'r') as f:
                mounts_data = yaml.safe_load(f)
            
            mounts = mounts_data.get('mounts', {})
            config = mounts_data.get('config', {})
            
            print(f"Total mounts: {len(mounts)}")
            print(f"Auto mount enabled: {config.get('auto_mount', True)}")
            print(f"Auto mount distance: {config.get('auto_mount_distance', 100)}m")
            print()
            
            print("Mounts by type:")
            mount_types = {}
            for mount_name, mount_data in mounts.items():
                mount_type = mount_data.get('type', 'unknown')
                if mount_type not in mount_types:
                    mount_types[mount_type] = []
                mount_types[mount_type].append(mount_name)
            
            for mount_type, mount_list in mount_types.items():
                print(f"  {mount_type.title()}: {len(mount_list)} mounts")
                for mount_name in mount_list:
                    mount_data = mounts[mount_name]
                    learned = "✓" if mount_data.get('learned', False) else "✗"
                    speed = mount_data.get('speed', 1.0)
                    print(f"    {learned} {mount_name} (speed: {speed}x)")
            
            print()
            
            # Show zone restrictions
            zone_restrictions = mounts_data.get('zone_restrictions', {})
            print("Zone Restrictions:")
            for zone_type, restrictions in zone_restrictions.items():
                mounts_allowed = restrictions.get('mounts_allowed', True)
                status_icon = "✓" if mounts_allowed else "✗"
                print(f"  {status_icon} {zone_type.title()}: mounts {'allowed' if mounts_allowed else 'not allowed'}")
            
        except Exception as e:
            print(f"Error reading mounts data: {e}")
        print()


def demonstrate_ocr_integration():
    """Demonstrate OCR integration for mount detection."""
    print("=== OCR Integration Demonstration ===\n")
    
    if not MOUNT_HANDLER_AVAILABLE:
        print("Mount handler not available. Skipping OCR demonstration.")
        return
    
    handler = get_mount_handler()
    
    print("1. OCR Detection Keywords")
    print("-" * 28)
    
    print("Call mount keywords:")
    for keyword in handler.mount_keywords["call_mount"]:
        print(f"  - {keyword}")
    
    print("\nMount type keywords:")
    for mount_type, keywords in handler.mount_keywords["mount_types"].items():
        print(f"  {mount_type.value}:")
        for keyword in keywords:
            print(f"    - {keyword}")
    
    print()
    
    print("2. Hotbar Scan Regions")
    print("-" * 24)
    
    for i, region in enumerate(handler.hotbar_regions, 1):
        print(f"  Region {i}: {region}")
    
    print()
    
    print("3. Command Patterns")
    print("-" * 18)
    
    for pattern in handler.command_patterns:
        print(f"  - {pattern}")
    
    print()


def demonstrate_configuration():
    """Demonstrate mount configuration options."""
    print("=== Configuration Demonstration ===\n")
    
    if not MOUNT_HANDLER_AVAILABLE:
        print("Mount handler not available. Skipping configuration demonstration.")
        return
    
    handler = get_mount_handler()
    
    print("1. Current Configuration")
    print("-" * 24)
    print(f"Auto mount: {handler.auto_mount}")
    print(f"Auto mount distance: {handler.auto_mount_distance}m")
    print(f"Detection interval: {handler.mount_detection_interval}s")
    print()
    
    print("2. Configuration Options")
    print("-" * 24)
    print("Available settings:")
    print("  - auto_mount: Enable/disable auto-mounting")
    print("  - auto_mount_distance: Minimum distance for auto-mount")
    print("  - mount_detection_interval: How often to scan for mounts")
    print("  - hotbar_regions: Screen regions to scan for mount buttons")
    print("  - mount_keywords: Keywords for mount detection")
    print("  - command_patterns: Patterns for command detection")
    print()
    
    print("3. Zone Restrictions")
    print("-" * 20)
    print("Mount restrictions by zone type:")
    print("  - Indoor zones: No mounts allowed")
    print("  - City zones: Most mounts allowed")
    print("  - Combat zones: No mounts allowed")
    print("  - Outdoor zones: All mounts allowed")
    print()


def main():
    """Main demonstration function."""
    print("Batch 031 - Mount Detection & Mount-Up Logic")
    print("=" * 45)
    
    # Run demonstrations
    demonstrate_mount_handler()
    demonstrate_data_files()
    demonstrate_ocr_integration()
    demonstrate_configuration()
    
    print("Demonstration completed successfully!")


if __name__ == "__main__":
    main() 
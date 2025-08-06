#!/usr/bin/env python3
"""
Demonstration script for Batch 032 - Combat Range Intelligence & Engagement Distance Logic

This script demonstrates the combat range intelligence functionality including:
- Combat range matrix by profession and weapon
- Auto-detection of equipped weapon type
- Distance threshold management per fight
- Range checking and repositioning logic
- Minimap OCR for proximity gauging
- Debug overlay for visual range tracking
"""

import time
from pathlib import Path

# Import the combat range intelligence modules
try:
    from combat.combat_range import (
        get_combat_range_intelligence, detect_equipped_weapon, detect_profession,
        check_combat_range, should_reposition, get_reposition_direction,
        get_combat_range_status, WeaponType, ProfessionType, RangeCheckResult
    )
    COMBAT_RANGE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import combat range modules: {e}")
    COMBAT_RANGE_AVAILABLE = False


def demonstrate_combat_range_intelligence():
    """Demonstrate combat range intelligence functionality."""
    if not COMBAT_RANGE_AVAILABLE:
        print("Combat range modules not available. Skipping demonstration.")
        return

    print("=== Combat Range Intelligence Demonstration ===\n")

    # Get combat range intelligence
    intelligence = get_combat_range_intelligence()

    print("1. Combat Range Intelligence Initialization")
    print("-" * 45)
    print(f"OCR Available: {intelligence.ocr_engine is not None}")
    print(f"Current Status: {intelligence.current_status.value}")
    print(f"Debug Overlay Enabled: {intelligence.debug_overlay_enabled}")
    print(f"Combat Range Matrix: {len(intelligence.combat_range_matrix)} combinations")
    print(f"Range History: {len(intelligence.range_history)} entries")
    print()

    # Show combat range matrix
    print("2. Combat Range Matrix")
    print("-" * 22)

    for key, data in intelligence.combat_range_matrix.items():
        profession = data.get("profession", "unknown")
        weapon_type = data.get("weapon_type", "unknown")
        optimal_range = data.get("optimal_range", 0)
        max_range = data.get("max_range", 0)
        min_range = data.get("min_range", 0)
        
        print(f"{key}:")
        print(f"  Profession: {profession}")
        print(f"  Weapon: {weapon_type}")
        print(f"  Optimal Range: {optimal_range}m")
        print(f"  Max Range: {max_range}m")
        print(f"  Min Range: {min_range}m")
        print(f"  Preferred Stance: {data.get('preferred_stance', 'standing')}")
        print(f"  Movement Speed: {data.get('movement_speed', 1.0)}x")
        print()

    # Demonstrate weapon detection
    print("3. Weapon Detection")
    print("-" * 18)

    print("Detecting equipped weapon...")
    detected_weapon = intelligence.detect_equipped_weapon()

    if detected_weapon:
        print(f"✅ Detected weapon: {detected_weapon.name}")
        print(f"   Type: {detected_weapon.weapon_type.value}")
        print(f"   Optimal Range: {detected_weapon.optimal_range}m")
        print(f"   Max Range: {detected_weapon.max_range}m")
        print(f"   Min Range: {detected_weapon.min_range}m")
        print(f"   Damage Type: {detected_weapon.damage_type}")
        print(f"   Reload Time: {detected_weapon.reload_time}s")
        print(f"   Accuracy Falloff: {detected_weapon.accuracy_falloff}")
        
        # Update current weapon
        intelligence.update_current_setup(weapon=detected_weapon)
    else:
        print("❌ No weapon detected (normal if not in game)")
        # Use default weapon for demonstration
        from combat.combat_range import WeaponInfo
        default_weapon = WeaponInfo(
            name="Default Pistol",
            weapon_type=WeaponType.PISTOL,
            optimal_range=32,
            max_range=50,
            min_range=5,
            accuracy_falloff=0.05,
            reload_time=1.5,
            damage_type="energy",
            equipped=True
        )
        intelligence.update_current_setup(weapon=default_weapon)
        print(f"Using default weapon: {default_weapon.name}")

    print()

    # Demonstrate profession detection
    print("4. Profession Detection")
    print("-" * 22)

    print("Detecting profession...")
    detected_profession = intelligence.detect_profession()

    if detected_profession:
        print(f"✅ Detected profession: {detected_profession.value}")
        intelligence.update_current_setup(profession=detected_profession)
    else:
        print("❌ No profession detected (normal if not in game)")
        # Use default profession for demonstration
        intelligence.update_current_setup(profession=ProfessionType.RIFLEMAN)
        print("Using default profession: rifleman")

    print()

    # Demonstrate range checking
    print("5. Range Checking")
    print("-" * 16)

    # Test different distances
    test_distances = [10, 25, 50, 75, 100, 150]

    for distance in test_distances:
        print(f"Testing range check at {distance}m...")
        range_result = intelligence.check_combat_range(distance)
        
        status_icon = "✅" if range_result.range_status == "optimal" else "⚠️"
        print(f"{status_icon} Distance: {range_result.current_distance:.1f}m")
        print(f"   Optimal Range: {range_result.optimal_range}m")
        print(f"   Range Status: {range_result.range_status}")
        print(f"   Reposition Needed: {range_result.reposition_needed}")
        print(f"   Suggested Action: {range_result.suggested_action}")
        print(f"   Confidence: {range_result.confidence:.1f}%")
        print()

    # Demonstrate repositioning logic
    print("6. Repositioning Logic")
    print("-" * 22)

    for distance in [5, 20, 80, 120]:
        should_repos = intelligence.should_reposition(distance)
        direction = intelligence.get_reposition_direction(distance)
        
        status_icon = "✅" if not should_repos else "🔄"
        print(f"{status_icon} Distance {distance}m:")
        print(f"   Should Reposition: {should_repos}")
        print(f"   Direction: {direction}")
        print()

    # Demonstrate minimap distance detection
    print("7. Minimap Distance Detection")
    print("-" * 29)

    print("Detecting distance from minimap...")
    detected_distance = intelligence._detect_distance_from_minimap()
    
    if detected_distance > 0:
        print(f"✅ Detected distance: {detected_distance:.1f}m")
    else:
        print("❌ No distance detected from minimap (using fallback)")
        detected_distance = 50.0  # Fallback distance
        print(f"Using fallback distance: {detected_distance}m")

    # Check range with detected distance
    range_result = intelligence.check_combat_range(detected_distance)
    print(f"Range check result: {range_result.range_status}")
    print()

    # Show combat range status
    print("8. Combat Range Status")
    print("-" * 21)

    status = intelligence.get_combat_range_status()
    print(f"Current Status: {status['current_status']}")
    print(f"Current Profession: {status['current_profession']}")
    print(f"Current Weapon: {status['current_weapon']}")
    print(f"Current Target Distance: {status['current_target_distance']:.1f}m")
    print(f"Optimal Range: {status['optimal_range']}m")
    print(f"Max Range: {status['max_range']}m")
    print(f"Min Range: {status['min_range']}m")
    print(f"Debug Overlay Enabled: {status['debug_overlay_enabled']}")
    print(f"Range History Count: {status['range_history_count']}")
    print()

    # Demonstrate debug overlay
    print("9. Debug Overlay")
    print("-" * 15)

    print("Enabling debug overlay...")
    intelligence.enable_debug_overlay(True)
    
    print("Debug overlay enabled for visual range tracking")
    print("This would display real-time range information on screen")
    print()

    # Show range history
    print("10. Range History")
    print("-" * 16)

    if intelligence.range_history:
        print(f"Recent range checks ({len(intelligence.range_history)} entries):")
        for i, result in enumerate(intelligence.range_history[-5:], 1):
            print(f"  {i}. {result.current_distance:.1f}m -> {result.range_status} ({result.confidence:.1f}%)")
    else:
        print("No range history available")

    print()


def demonstrate_data_files():
    """Demonstrate the data files for Batch 032."""
    print("=== Data Files Demonstration ===\n")

    # Check if data files exist
    profession_ranges_file = Path("data/profession_ranges.yaml")

    print("1. Data File Status")
    print("-" * 20)
    print(f"Profession ranges configuration: {'✅ Found' if profession_ranges_file.exists() else '❌ Missing'}")
    print()

    if profession_ranges_file.exists():
        print("2. Profession Ranges Configuration")
        print("-" * 33)

        try:
            import yaml
            with open(profession_ranges_file, 'r') as f:
                ranges_data = yaml.safe_load(f)

            combat_matrix = ranges_data.get('combat_range_matrix', {})
            weapon_types = ranges_data.get('weapon_types', {})
            profession_types = ranges_data.get('profession_types', {})

            print(f"Combat range matrix: {len(combat_matrix)} combinations")
            print(f"Weapon types: {len(weapon_types)}")
            print(f"Profession types: {len(profession_types)}")
            print()

            print("Profession-Weapon Combinations:")
            for key, data in combat_matrix.items():
                profession = data.get('profession', 'unknown')
                weapon = data.get('weapon_type', 'unknown')
                optimal = data.get('optimal_range', 0)
                max_range = data.get('max_range', 0)
                min_range = data.get('min_range', 0)
                print(f"  {key}: {profession} + {weapon} (optimal: {optimal}m, max: {max_range}m, min: {min_range}m)")

            print()

            print("Weapon Types:")
            for weapon_type, weapon_data in weapon_types.items():
                name = weapon_data.get('name', weapon_type)
                optimal = weapon_data.get('base_optimal_range', 0)
                max_range = weapon_data.get('base_max_range', 0)
                min_range = weapon_data.get('base_min_range', 0)
                print(f"  {name}: {optimal}m optimal, {min_range}-{max_range}m range")

            print()

            print("Profession Types:")
            for profession_type, profession_data in profession_types.items():
                name = profession_data.get('name', profession_type)
                description = profession_data.get('description', 'No description')
                movement = profession_data.get('base_movement_speed', 1.0)
                range_bonus = profession_data.get('range_bonus', 0)
                print(f"  {name}: {description} (movement: {movement}x, range bonus: +{range_bonus}m)")

        except Exception as e:
            print(f"Error reading profession ranges data: {e}")
        print()


def demonstrate_ocr_integration():
    """Demonstrate OCR integration for combat range detection."""
    print("=== OCR Integration Demonstration ===\n")

    if not COMBAT_RANGE_AVAILABLE:
        print("Combat range modules not available. Skipping OCR demonstration.")
        return

    intelligence = get_combat_range_intelligence()

    print("1. Weapon Detection Keywords")
    print("-" * 28)

    for weapon_type, keywords in intelligence.weapon_keywords.items():
        print(f"  {weapon_type.value}:")
        for keyword in keywords:
            print(f"    - {keyword}")

    print()

    print("2. Profession Detection Keywords")
    print("-" * 30)

    for profession_type, keywords in intelligence.profession_keywords.items():
        print(f"  {profession_type.value}:")
        for keyword in keywords:
            print(f"    - {keyword}")

    print()

    print("3. Minimap Scan Regions")
    print("-" * 24)

    for region_name, region in intelligence.minimap_regions.items():
        print(f"  {region_name}: {region}")

    print()

    print("4. Distance Detection Patterns")
    print("-" * 28)

    distance_patterns = [
        r"(\d+)m",
        r"distance: (\d+)",
        r"range: (\d+)",
        r"(\d+) meters"
    ]

    for pattern in distance_patterns:
        print(f"  - {pattern}")

    print()


def demonstrate_configuration():
    """Demonstrate combat range configuration options."""
    print("=== Configuration Demonstration ===\n")

    if not COMBAT_RANGE_AVAILABLE:
        print("Combat range modules not available. Skipping configuration demonstration.")
        return

    intelligence = get_combat_range_intelligence()

    print("1. Current Configuration")
    print("-" * 24)
    print(f"Debug overlay enabled: {intelligence.debug_overlay_enabled}")
    print(f"Debug overlay region: {intelligence.debug_overlay_region}")
    print(f"Range check history: {len(intelligence.range_history)} entries")
    print(f"Last range check: {intelligence.last_range_check}")
    print()

    print("2. Configuration Options")
    print("-" * 24)
    print("Available settings:")
    print("  - debug_overlay_enabled: Enable/disable visual range tracking")
    print("  - debug_overlay_region: Screen region for overlay display")
    print("  - weapon_keywords: Keywords for weapon detection")
    print("  - profession_keywords: Keywords for profession detection")
    print("  - minimap_regions: Screen regions for minimap scanning")
    print("  - combat_range_matrix: Profession-weapon range combinations")
    print()

    print("3. Range Status Definitions")
    print("-" * 28)
    range_statuses = {
        "too_close": "Target is within minimum range",
        "optimal": "Target is at optimal combat distance",
        "acceptable": "Target is within acceptable range",
        "too_far": "Target is beyond optimal range",
        "out_of_range": "Target is beyond maximum range"
    }

    for status, description in range_statuses.items():
        print(f"  {status}: {description}")

    print()

    print("4. Suggested Actions")
    print("-" * 18)
    actions = {
        "move_back": "Move away from target",
        "engage": "Attack target at current range",
        "move_forward": "Move closer to target",
        "unknown": "Unknown action required"
    }

    for action, description in actions.items():
        print(f"  {action}: {description}")

    print()


def main():
    """Main demonstration function."""
    print("Batch 032 - Combat Range Intelligence & Engagement Distance Logic")
    print("=" * 60)

    # Run demonstrations
    demonstrate_combat_range_intelligence()
    demonstrate_data_files()
    demonstrate_ocr_integration()
    demonstrate_configuration()

    print("Demonstration completed successfully!")


if __name__ == "__main__":
    main() 
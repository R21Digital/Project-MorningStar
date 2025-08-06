#!/usr/bin/env python3
"""
Batch 151 - Rare Loot System (RLS) Farming Mode Demo

This demo showcases the comprehensive RLS farming system:
- Target zone management with coordinates and patrol radius
- Enemy type tracking with known drop percentages
- Session-based loot tracking and verification
- Configurable loot target lists
- Integration with SWG RLS database
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from core.rare_loot_farming import get_rare_loot_farmer, DropZone, EnemyInfo, LootTarget, DropRarity, EnemyType
from android_ms11.modes.rare_loot_farm import (
    list_available_zones,
    list_target_items,
    get_farming_recommendations,
    get_session_statistics
)


def demonstrate_basic_setup():
    """Demonstrate basic RLS farming system setup."""
    print("🚀 Batch 151 - RLS Farming System Demo")
    print("=" * 60)
    
    # Initialize the farmer
    farmer = get_rare_loot_farmer()
    print("✅ RLS Farmer initialized")
    
    # Show available zones
    zones = list_available_zones()
    print(f"\n🗺️  Available Drop Zones ({len(zones)}):")
    for zone in zones:
        print(f"   • {zone['display_name']} on {zone['planet']}")
    
    # Show available targets
    targets = list_target_items()
    print(f"\n🎯 Available Target Items ({len(targets)}):")
    for target in targets:
        print(f"   • {target['display_name']} ({target['rarity']}) - {target['value']:,} credits")
    
    print("\n" + "=" * 60)


def demonstrate_session_management():
    """Demonstrate session management capabilities."""
    print("📋 Session Management Demo")
    print("-" * 40)
    
    farmer = get_rare_loot_farmer()
    
    # Start a farming session
    print("🔄 Starting farming session...")
    session = farmer.start_farming_session(
        target_zone="krayt_dragon_zone",
        target_items=["Krayt Dragon Pearl", "Krayt Dragon Hide"]
    )
    
    print(f"✅ Session started: {session.session_id}")
    print(f"📍 Target Zone: {session.target_zone}")
    print(f"🎯 Target Items: {', '.join(session.target_items)}")
    
    # Simulate some loot acquisitions
    print("\n📦 Simulating loot acquisitions...")
    
    # Add some loot manually
    acquisitions = [
        ("Krayt Dragon Hide", "Greater Krayt Dragon", (2000, 1500)),
        ("Krayt Dragon Bone", "Greater Krayt Dragon", (2100, 1600)),
        ("Krayt Dragon Pearl", "Greater Krayt Dragon", (1900, 1400))
    ]
    
    for item_name, enemy_name, coords in acquisitions:
        acquisition = farmer.record_loot_acquisition(item_name, enemy_name, coords)
        print(f"   ✅ Found {acquisition.item_name} ({acquisition.rarity.value})")
    
    # Show session statistics
    stats = farmer.get_session_statistics(session.session_id)
    print(f"\n📊 Session Statistics:")
    print(f"   ⏱️  Duration: {stats.get('duration_minutes', 0)} minutes")
    print(f"   ⚔️  Enemies Killed: {stats.get('enemies_killed', 0)}")
    print(f"   📦 Items Found: {stats.get('items_found', 0)}")
    print(f"   💰 Total Value: {stats.get('total_value', 0):,} credits")
    
    # End the session
    print("\n🔄 Ending farming session...")
    completed_session = farmer.end_farming_session()
    
    if completed_session:
        print(f"✅ Session completed: {completed_session.session_id}")
        print(f"📊 Final Status: {completed_session.status}")
    
    print("\n" + "=" * 60)


def demonstrate_zone_management():
    """Demonstrate zone management capabilities."""
    print("🗺️  Zone Management Demo")
    print("-" * 40)
    
    farmer = get_rare_loot_farmer()
    
    # Show current zones
    print("📍 Current Drop Zones:")
    for zone_name, zone in farmer.drop_zones.items():
        print(f"   • {zone.name}")
        print(f"     Planet: {zone.planet}")
        print(f"     Coordinates: {zone.coordinates}")
        print(f"     Patrol Radius: {zone.patrol_radius}")
        print(f"     Difficulty: {zone.difficulty}")
        print(f"     Enemy Types: {', '.join(zone.enemy_types)}")
        print()
    
    # Add a new zone
    print("➕ Adding new drop zone...")
    new_zone = DropZone(
        name="Rancor Pit",
        planet="dathomir",
        coordinates=(3000, 2000),
        patrol_radius=400,
        enemy_types=["Rancor", "Rancor Matriarch"],
        spawn_rate=0.25,
        respawn_time=180,
        difficulty="legendary",
        notes="Home to the fearsome Rancors"
    )
    
    farmer.drop_zones["rancor_pit"] = new_zone
    farmer._save_drop_zones(farmer.drop_zones)
    
    print(f"✅ Added new zone: {new_zone.name}")
    print(f"   Planet: {new_zone.planet}")
    print(f"   Coordinates: {new_zone.coordinates}")
    print(f"   Difficulty: {new_zone.difficulty}")
    
    print("\n" + "=" * 60)


def demonstrate_target_management():
    """Demonstrate target item management."""
    print("🎯 Target Item Management Demo")
    print("-" * 40)
    
    farmer = get_rare_loot_farmer()
    
    # Show current targets
    print("📦 Current Target Items:")
    for target_name, target in farmer.loot_targets.items():
        print(f"   • {target.name}")
        print(f"     Rarity: {target.rarity.value}")
        print(f"     Value: {target.value:,} credits")
        print(f"     Drop Rate: {target.drop_percentage:.1%}")
        print(f"     Priority: {target.priority}/5")
        print()
    
    # Add a new target
    print("➕ Adding new target item...")
    new_target = LootTarget(
        name="Rancor Hide",
        rarity=DropRarity.VERY_RARE,
        drop_zones=["rancor_pit"],
        enemy_types=["Rancor", "Rancor Matriarch"],
        drop_percentage=0.3,
        value=35000,
        notes="Extremely durable hide from Rancors",
        priority=4
    )
    
    farmer.loot_targets["rancor_hide"] = new_target
    farmer._save_loot_targets(farmer.loot_targets)
    
    print(f"✅ Added new target: {new_target.name}")
    print(f"   Rarity: {new_target.rarity.value}")
    print(f"   Value: {new_target.value:,} credits")
    print(f"   Drop Rate: {new_target.drop_percentage:.1%}")
    print(f"   Priority: {new_target.priority}/5")
    
    print("\n" + "=" * 60)


def demonstrate_farming_recommendations():
    """Demonstrate farming recommendations."""
    print("💡 Farming Recommendations Demo")
    print("-" * 40)
    
    recommendations = get_farming_recommendations()
    
    if not recommendations:
        print("❌ No recommendations available")
        return
    
    print(f"📊 Top Farming Recommendations ({len(recommendations)}):")
    
    for i, rec in enumerate(recommendations[:5], 1):
        print(f"\n{i}. {rec['target_item']}")
        print(f"   Zone: {rec['drop_zone']}")
        print(f"   Planet: {rec['planet']}")
        print(f"   Coordinates: {rec['coordinates']}")
        print(f"   Efficiency Score: {rec['efficiency_score']:.2f}")
        print(f"   Estimated Time: {rec['estimated_time']} minutes")
        print(f"   Difficulty: {rec['difficulty']}")
        print(f"   Value: {rec['value']:,} credits")
    
    print("\n" + "=" * 60)


def demonstrate_optimal_routes():
    """Demonstrate optimal farming route calculation."""
    print("🗺️  Optimal Route Calculation Demo")
    print("-" * 40)
    
    farmer = get_rare_loot_farmer()
    
    # Test different target combinations
    target_combinations = [
        ["Krayt Dragon Pearl"],
        ["Krayt Dragon Pearl", "Kimogila Hide"],
        ["Krayt Dragon Pearl", "Kimogila Hide", "Tigrip Poison"]
    ]
    
    for targets in target_combinations:
        print(f"\n🎯 Targets: {', '.join(targets)}")
        optimal_route = farmer.get_optimal_farming_route(targets)
        
        print(f"   Optimal Route ({len(optimal_route)} zones):")
        for zone in optimal_route:
            print(f"     • {zone.name} at {zone.coordinates}")
    
    print("\n" + "=" * 60)


def demonstrate_session_tracking():
    """Demonstrate session tracking and statistics."""
    print("📊 Session Tracking Demo")
    print("-" * 40)
    
    farmer = get_rare_loot_farmer()
    
    # Create multiple sessions for demonstration
    sessions = []
    
    for i in range(3):
        print(f"\n🔄 Creating session {i+1}...")
        
        session = farmer.start_farming_session(
            target_zone=f"zone_{i}",
            target_items=[f"item_{i}"]
        )
        
        # Simulate some activity
        for j in range(2):
            acquisition = farmer.record_loot_acquisition(
                item_name=f"Loot Item {i}-{j}",
                enemy_name=f"Enemy {i}-{j}",
                coordinates=(1000 + i*100, 1000 + j*100)
            )
        
        # End session
        completed = farmer.end_farming_session()
        if completed:
            sessions.append(completed.session_id)
    
    # Show all sessions
    print(f"\n📋 All Sessions ({len(farmer.farming_sessions)}):")
    for session_id, session in farmer.farming_sessions.items():
        stats = farmer.get_session_statistics(session_id)
        print(f"   • {session_id}")
        print(f"     Zone: {session.target_zone}")
        print(f"     Items: {stats.get('items_found', 0)}")
        print(f"     Value: {stats.get('total_value', 0):,} credits")
        print(f"     Duration: {stats.get('duration_minutes', 0)} minutes")
    
    print("\n" + "=" * 60)


def demonstrate_data_export():
    """Demonstrate data export capabilities."""
    print("📤 Data Export Demo")
    print("-" * 40)
    
    farmer = get_rare_loot_farmer()
    
    if not farmer.farming_sessions:
        print("❌ No sessions to export")
        return
    
    # Export the first session
    session_id = list(farmer.farming_sessions.keys())[0]
    
    try:
        export_path = farmer.export_session_data(session_id)
        print(f"✅ Session exported to: {export_path}")
        
        # Show export file contents
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        print(f"📄 Export contains:")
        print(f"   • Session data: {len(export_data.get('session', {}))} fields")
        print(f"   • Statistics: {len(export_data.get('statistics', {}))} fields")
        print(f"   • Loot acquisitions: {len(export_data.get('loot_acquisitions', []))} items")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
    
    print("\n" + "=" * 60)


def demonstrate_integration_features():
    """Demonstrate integration with MS11 session management."""
    print("🔗 MS11 Integration Demo")
    print("-" * 40)
    
    # Simulate MS11 session manager
    from core.session_manager import SessionManager
    
    session_manager = SessionManager(mode="rare_loot_farm")
    farmer = get_rare_loot_farmer(session_manager)
    
    print("✅ Integrated with MS11 Session Manager")
    print(f"   Session ID: {session_manager.session_id}")
    print(f"   Mode: {session_manager.mode}")
    
    # Start farming session
    farming_session = farmer.start_farming_session(
        target_zone="krayt_dragon_zone",
        target_items=["Krayt Dragon Pearl"]
    )
    
    print(f"   Farming Session: {farming_session.session_id}")
    
    # Simulate some actions
    session_manager.add_action("Started RLS farming in krayt_dragon_zone")
    session_manager.add_action("Patrolling coordinates (2000, 1500)")
    session_manager.add_action("Encountered Greater Krayt Dragon")
    
    # Record loot
    acquisition = farmer.record_loot_acquisition(
        item_name="Krayt Dragon Pearl",
        enemy_name="Greater Krayt Dragon",
        coordinates=(2000, 1500)
    )
    
    session_manager.add_action(f"Found rare loot: {acquisition.item_name}")
    
    # End sessions
    farmer.end_farming_session()
    session_manager.end_session()
    
    print("✅ Integration demo completed")
    print(f"   MS11 Actions: {len(session_manager.actions)}")
    print(f"   Farming Session: {farming_session.status}")
    
    print("\n" + "=" * 60)


def demonstrate_error_handling():
    """Demonstrate error handling capabilities."""
    print("⚠️  Error Handling Demo")
    print("-" * 40)
    
    farmer = get_rare_loot_farmer()
    
    # Test invalid zone
    try:
        session = farmer.start_farming_session("invalid_zone", ["item"])
        print("❌ Should have failed")
    except ValueError as e:
        print(f"✅ Correctly caught error: {e}")
    
    # Test invalid session operations
    try:
        acquisition = farmer.record_loot_acquisition("item", "enemy", (0, 0))
        print("❌ Should have failed")
    except RuntimeError as e:
        print(f"✅ Correctly caught error: {e}")
    
    # Test invalid export
    try:
        export_path = farmer.export_session_data("invalid_session")
        print("❌ Should have failed")
    except ValueError as e:
        print(f"✅ Correctly caught error: {e}")
    
    print("✅ Error handling demo completed")
    print("\n" + "=" * 60)


def main():
    """Run the complete RLS farming demo."""
    print("🚀 Starting Batch 151 - RLS Farming System Demo")
    print("=" * 80)
    
    try:
        # Run all demonstrations
        demonstrate_basic_setup()
        demonstrate_session_management()
        demonstrate_zone_management()
        demonstrate_target_management()
        demonstrate_farming_recommendations()
        demonstrate_optimal_routes()
        demonstrate_session_tracking()
        demonstrate_data_export()
        demonstrate_integration_features()
        demonstrate_error_handling()
        
        print("🎉 Demo completed successfully!")
        print("=" * 80)
        
        # Show final summary
        farmer = get_rare_loot_farmer()
        print(f"📊 Final System State:")
        print(f"   • Drop Zones: {len(farmer.drop_zones)}")
        print(f"   • Enemy Types: {len(farmer.enemy_types)}")
        print(f"   • Target Items: {len(farmer.loot_targets)}")
        print(f"   • Farming Sessions: {len(farmer.farming_sessions)}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
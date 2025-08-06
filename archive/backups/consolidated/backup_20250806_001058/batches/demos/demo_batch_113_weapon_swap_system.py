"""Demo script for Batch 113 - Weapon Swap + Loadout Handling

This demo showcases the weapon swap system functionality including:
- Dynamic weapon switching based on enemy type and distance
- Loadout management and configuration
- Combat integration with existing AI
- Weapon effectiveness calculations
- Manual override capabilities
- Weapon history and analytics
"""

import json
import time
from datetime import datetime
from pathlib import Path

from modules.weapon_swap_system import WeaponSwapSystem
from src.ai.combat.weapon_swap_integration import CombatWeaponSwapIntegration


def demo_weapon_system_initialization():
    """Demo weapon system initialization and configuration loading."""
    print("\n=== Weapon System Initialization Demo ===")
    
    # Initialize weapon system
    weapon_system = WeaponSwapSystem()
    
    print(f"Loaded {len(weapon_system.weapons)} weapons:")
    for weapon_name, weapon_stats in weapon_system.weapons.items():
        print(f"  - {weapon_name}: {weapon_stats.damage_type.value} damage, {weapon_stats.range}m range")
    
    print(f"\nLoaded {len(weapon_system.loadouts)} loadouts:")
    for loadout_name, loadout in weapon_system.loadouts.items():
        print(f"  - {loadout_name}: {loadout.description}")
    
    return weapon_system


def demo_loadout_management(weapon_system):
    """Demo loadout management and weapon switching."""
    print("\n=== Loadout Management Demo ===")
    
    # Test different loadouts
    test_loadouts = [
        "rifleman_standard",
        "energy_specialist", 
        "sniper_loadout",
        "close_combat",
        "hybrid_loadout"
    ]
    
    for loadout_name in test_loadouts:
        print(f"\nLoading loadout: {loadout_name}")
        success = weapon_system.load_loadout(loadout_name)
        
        if success:
            loadout = weapon_system.loadouts[loadout_name]
            print(f"  Primary weapon: {loadout.primary_weapon}")
            print(f"  Secondary weapon: {loadout.secondary_weapon}")
            print(f"  Auto-swap enabled: {loadout.auto_swap_enabled}")
            
            # Show available weapons
            available_weapons = weapon_system.get_available_weapons()
            print(f"  Available weapons: {available_weapons}")
        else:
            print(f"  Failed to load loadout: {loadout_name}")


def demo_weapon_effectiveness_calculation(weapon_system):
    """Demo weapon effectiveness calculations for different scenarios."""
    print("\n=== Weapon Effectiveness Calculation Demo ===")
    
    # Test scenarios
    test_scenarios = [
        ("stormtrooper", 50.0),
        ("droid", 30.0),
        ("beast", 10.0),
        ("boss", 100.0),
        ("armored_target", 75.0),
        ("shielded_enemy", 25.0)
    ]
    
    # Load a loadout with multiple weapons
    weapon_system.load_loadout("hybrid_loadout")
    available_weapons = weapon_system.get_available_weapons()
    
    for enemy_type, distance in test_scenarios:
        print(f"\nEnemy: {enemy_type} at {distance}m distance")
        print("-" * 50)
        
        for weapon_name in available_weapons:
            effectiveness = weapon_system.calculate_weapon_effectiveness(
                weapon_name, enemy_type, distance
            )
            weapon_stats = weapon_system.get_weapon_stats(weapon_name)
            
            print(f"  {weapon_name}:")
            print(f"    Effectiveness: {effectiveness:.2f}")
            print(f"    Damage Type: {weapon_stats.damage_type.value}")
            print(f"    Range: {weapon_stats.range}m")
            print(f"    Ammo: {weapon_stats.current_ammo}/{weapon_stats.ammo_capacity}")
            print(f"    Condition: {weapon_stats.condition}%")


def demo_dynamic_weapon_swapping(weapon_system):
    """Demo dynamic weapon swapping based on combat conditions."""
    print("\n=== Dynamic Weapon Swapping Demo ===")
    
    # Load a loadout
    weapon_system.load_loadout("rifleman_standard")
    
    # Test different combat scenarios
    combat_scenarios = [
        {"enemy_type": "stormtrooper", "distance": 80.0, "description": "Long range vs stormtrooper"},
        {"enemy_type": "droid", "distance": 20.0, "description": "Close range vs droid"},
        {"enemy_type": "beast", "distance": 5.0, "description": "Very close vs beast"},
        {"enemy_type": "boss", "distance": 150.0, "description": "Long range vs boss"},
        {"enemy_type": "shielded_enemy", "distance": 40.0, "description": "Medium range vs shielded enemy"}
    ]
    
    for scenario in combat_scenarios:
        print(f"\nScenario: {scenario['description']}")
        print("-" * 50)
        
        # Set combat context
        weapon_system.set_combat_context(
            enemy_type=scenario["enemy_type"],
            distance=scenario["distance"]
        )
        
        # Get best weapon recommendation
        best_weapon = weapon_system.get_best_weapon(
            scenario["enemy_type"], scenario["distance"]
        )
        
        if best_weapon:
            effectiveness = weapon_system.calculate_weapon_effectiveness(
                best_weapon, scenario["enemy_type"], scenario["distance"]
            )
            print(f"  Recommended weapon: {best_weapon}")
            print(f"  Effectiveness: {effectiveness:.2f}")
            
            # Simulate weapon swap
            should_swap, swap_weapon = weapon_system.should_swap_weapon(
                scenario["enemy_type"], scenario["distance"]
            )
            
            if should_swap:
                print(f"  Auto-swap triggered: {swap_weapon}")
                weapon_system.swap_weapon(swap_weapon, "auto")
            else:
                print("  No swap needed")
        else:
            print("  No suitable weapon found")


def demo_emergency_swap_conditions(weapon_system):
    """Demo emergency weapon swap conditions."""
    print("\n=== Emergency Swap Conditions Demo ===")
    
    # Load a loadout
    weapon_system.load_loadout("rifleman_standard")
    
    # Test no ammo emergency
    print("\nTesting no ammo emergency:")
    weapon_system.update_weapon_ammo("rifle_standard", 0)
    weapon_system.update_weapon_ammo("carbine_rapid", 5)
    
    should_swap, emergency_weapon = weapon_system.should_swap_weapon("stormtrooper", 50.0)
    if should_swap:
        print(f"  Emergency swap triggered: {emergency_weapon}")
        weapon_system.swap_weapon(emergency_weapon, "emergency")
    
    # Test critical weapon condition
    print("\nTesting critical weapon condition:")
    weapon_system.update_weapon_condition("rifle_standard", 15.0)
    weapon_system.update_weapon_condition("carbine_rapid", 80.0)
    
    should_swap, emergency_weapon = weapon_system.should_swap_weapon("stormtrooper", 50.0)
    if should_swap:
        print(f"  Emergency swap triggered: {emergency_weapon}")
        weapon_system.swap_weapon(emergency_weapon, "emergency")


def demo_combat_integration(weapon_system):
    """Demo integration with combat AI."""
    print("\n=== Combat Integration Demo ===")
    
    # Create combat integration
    combat_integration = CombatWeaponSwapIntegration(weapon_system)
    
    # Load a loadout
    weapon_system.load_loadout("rifleman_standard")
    
    # Test combat scenarios
    combat_scenarios = [
        {
            "player_state": {"hp": 80, "ammo_status": {"rifle_standard": 15, "carbine_rapid": 20}},
            "target_state": {"hp": 60},
            "enemy_type": "stormtrooper",
            "distance": 70.0,
            "description": "Medium health player vs stormtrooper"
        },
        {
            "player_state": {"hp": 30, "ammo_status": {"rifle_standard": 0, "carbine_rapid": 5}},
            "target_state": {"hp": 80},
            "enemy_type": "droid",
            "distance": 25.0,
            "description": "Low health player with no ammo vs droid"
        },
        {
            "player_state": {"hp": 95, "ammo_status": {"rifle_standard": 30, "carbine_rapid": 25}},
            "target_state": {"hp": 20},
            "enemy_type": "beast",
            "distance": 5.0,
            "description": "High health player vs weak beast"
        }
    ]
    
    for scenario in combat_scenarios:
        print(f"\nCombat Scenario: {scenario['description']}")
        print("-" * 50)
        
        # Get enhanced combat action
        action = combat_integration.get_enhanced_combat_action(
            scenario["player_state"],
            scenario["target_state"],
            scenario["enemy_type"],
            scenario["distance"]
        )
        
        print(f"  Combat Action: {action}")
        print(f"  Current Weapon: {weapon_system.current_weapon}")
        
        # Get weapon recommendation
        recommendation = combat_integration.get_weapon_recommendation(
            scenario["enemy_type"], scenario["distance"]
        )
        
        print(f"  Recommended Weapon: {recommendation['best_weapon']}")
        print(f"  Effectiveness: {recommendation['recommendations'][recommendation['best_weapon']]['effectiveness']:.2f}")


def demo_manual_override(weapon_system):
    """Demo manual weapon override capabilities."""
    print("\n=== Manual Override Demo ===")
    
    # Load a loadout
    weapon_system.load_loadout("manual_loadout")
    
    print("Manual loadout loaded (auto-swap disabled)")
    print(f"Current weapon: {weapon_system.current_weapon}")
    
    # Test manual weapon swaps
    available_weapons = weapon_system.get_available_weapons()
    
    for weapon_name in available_weapons:
        if weapon_name != weapon_system.current_weapon:
            print(f"\nManually swapping to: {weapon_name}")
            success = weapon_system.swap_weapon(weapon_name, "manual")
            
            if success:
                print(f"  Successfully swapped to {weapon_name}")
                print(f"  Current weapon: {weapon_system.current_weapon}")
            else:
                print(f"  Failed to swap to {weapon_name}")


def demo_weapon_analytics(weapon_system):
    """Demo weapon analytics and history tracking."""
    print("\n=== Weapon Analytics Demo ===")
    
    # Get weapon effectiveness statistics
    effectiveness_stats = weapon_system.get_weapon_effectiveness_stats()
    
    print("Weapon Effectiveness by Enemy Type:")
    for weapon_name, enemy_stats in effectiveness_stats.items():
        print(f"\n  {weapon_name}:")
        for enemy_type, effectiveness in enemy_stats.items():
            print(f"    vs {enemy_type}: {effectiveness:.2f}")
    
    # Get weapon history
    history = weapon_system.get_weapon_history(limit=5)
    
    print(f"\nRecent Weapon Swaps ({len(history)} events):")
    for event in history:
        print(f"  {event.timestamp}: {event.from_weapon} -> {event.to_weapon} ({event.reason})")
        print(f"    Effectiveness: {event.effectiveness_score:.2f}")


def demo_export_functionality(weapon_system):
    """Demo weapon data export functionality."""
    print("\n=== Export Functionality Demo ===")
    
    # Export weapon data
    export_path = weapon_system.export_weapon_data()
    print(f"Exported weapon data to: {export_path}")
    
    # Read and display export data
    with open(export_path, 'r') as f:
        export_data = json.load(f)
    
    print(f"Export contains:")
    print(f"  - {len(export_data['weapons'])} weapons")
    print(f"  - {len(export_data['loadouts'])} loadouts")
    print(f"  - {len(export_data['weapon_history'])} swap events")
    print(f"  - {len(export_data['enemy_resistances'])} enemy types")


def demo_advanced_scenarios(weapon_system):
    """Demo advanced weapon swap scenarios."""
    print("\n=== Advanced Scenarios Demo ===")
    
    # Scenario 1: Distance-based swapping
    print("\nScenario 1: Distance-based weapon swapping")
    weapon_system.load_loadout("sniper_loadout")
    
    distances = [10, 50, 100, 200]
    for distance in distances:
        best_weapon = weapon_system.get_best_weapon("stormtrooper", distance)
        effectiveness = weapon_system.calculate_weapon_effectiveness(best_weapon, "stormtrooper", distance)
        print(f"  {distance}m: {best_weapon} (effectiveness: {effectiveness:.2f})")
    
    # Scenario 2: Enemy resistance-based swapping
    print("\nScenario 2: Enemy resistance-based weapon swapping")
    weapon_system.load_loadout("energy_specialist")
    
    enemy_types = ["stormtrooper", "droid", "shielded_enemy"]
    for enemy_type in enemy_types:
        best_weapon = weapon_system.get_best_weapon(enemy_type, 50.0)
        effectiveness = weapon_system.calculate_weapon_effectiveness(best_weapon, enemy_type, 50.0)
        print(f"  vs {enemy_type}: {best_weapon} (effectiveness: {effectiveness:.2f})")
    
    # Scenario 3: Ammo management
    print("\nScenario 3: Ammo management")
    weapon_system.load_loadout("rifleman_standard")
    
    # Set low ammo conditions
    weapon_system.update_weapon_ammo("rifle_standard", 2)
    weapon_system.update_weapon_ammo("carbine_rapid", 15)
    
    should_swap, swap_weapon = weapon_system.should_swap_weapon("stormtrooper", 50.0)
    if should_swap:
        print(f"  Low ammo detected, swapping to: {swap_weapon}")
        weapon_system.swap_weapon(swap_weapon, "ammo_management")


def main():
    """Run the complete weapon swap system demo."""
    print("=== Batch 113 - Weapon Swap System Demo ===")
    print("Testing dynamic weapon switching, loadout management, and combat integration")
    
    try:
        # Demo 1: System initialization
        weapon_system = demo_weapon_system_initialization()
        
        # Demo 2: Loadout management
        demo_loadout_management(weapon_system)
        
        # Demo 3: Weapon effectiveness calculation
        demo_weapon_effectiveness_calculation(weapon_system)
        
        # Demo 4: Dynamic weapon swapping
        demo_dynamic_weapon_swapping(weapon_system)
        
        # Demo 5: Emergency swap conditions
        demo_emergency_swap_conditions(weapon_system)
        
        # Demo 6: Combat integration
        demo_combat_integration(weapon_system)
        
        # Demo 7: Manual override
        demo_manual_override(weapon_system)
        
        # Demo 8: Weapon analytics
        demo_weapon_analytics(weapon_system)
        
        # Demo 9: Export functionality
        demo_export_functionality(weapon_system)
        
        # Demo 10: Advanced scenarios
        demo_advanced_scenarios(weapon_system)
        
        print("\n=== Demo Complete ===")
        print("✅ Weapon swap system successfully tested")
        print("✅ Dynamic weapon switching working")
        print("✅ Loadout management working")
        print("✅ Combat integration working")
        print("✅ Manual override working")
        print("✅ Analytics and export working")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
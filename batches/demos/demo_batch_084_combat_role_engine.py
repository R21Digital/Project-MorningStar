#!/usr/bin/env python3
"""
MS11 Batch 084 - Combat Role Engine Demo

This script demonstrates the combat role engine functionality including:
- Role-based combat logic and triggers
- Automatic role switching based on group composition
- Role-aware ability prioritization
- Integration with existing combat profiles
"""

import sys
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def log_event(message: str):
    """Simple logging function for demo."""
    print(f"[DEMO] {message}")

# Import the combat role engine components
from core.combat_role_engine import CombatRoleEngine
from core.combat_role_profile_manager import CombatRoleProfileManager

def demo_combat_role_engine():
    """Demonstrate the combat role engine functionality."""
    print("=" * 60)
    print("MS11 Batch 084 - Combat Role Engine Demo")
    print("=" * 60)
    
    # Initialize the combat role engine
    print("\n1. Initializing Combat Role Engine...")
    role_engine = CombatRoleEngine("config/combat_profiles/roles.json")
    
    # Display available roles
    print(f"\n2. Available Combat Roles:")
    available_roles = role_engine.get_available_roles()
    for role in available_roles:
        role_info = role_engine.get_role_info(role)
        print(f"   - {role_info['name']}: {role_info['description']}")
    
    # Test role setting
    print(f"\n3. Testing Role Setting...")
    test_roles = ["solo_dps", "healer", "tank", "group_dps", "pvp_roamer"]
    
    for role in test_roles:
        success = role_engine.set_current_role(role)
        if success:
            role_info = role_engine.get_current_role_info()
            print(f"   ✓ Set role to: {role_info['name']}")
            
            # Test role-specific triggers
            print(f"     - Use taunt: {role_engine.should_use_taunt()}")
            print(f"     - Maintain aggro: {role_engine.should_maintain_aggro()}")
            print(f"     - Use group healing: {role_engine.should_use_group_healing()}")
            
            # Test ability priorities
            priorities = role_engine.get_ability_priorities()
            print(f"     - Ability priorities: {priorities}")
        else:
            print(f"   ✗ Failed to set role: {role}")
    
    # Test auto-detection
    print(f"\n4. Testing Auto-Role Detection...")
    test_groups = [
        [{"name": "Player1", "role": "dps"}],  # Solo
        [{"name": "Player1", "role": "dps"}, {"name": "Player2", "role": "dps"}],  # Duo
        [{"name": "Player1", "role": "dps"}, {"name": "Player2", "role": "dps"}, {"name": "Player3", "role": "dps"}],  # Trio
        [{"name": "Player1", "role": "dps"}, {"name": "Player2", "role": "dps"}, {"name": "Player3", "role": "dps"}, {"name": "Player4", "role": "dps"}]  # Quartet
    ]
    
    for i, group in enumerate(test_groups, 1):
        suggested_role = role_engine.auto_detect_role(group)
        print(f"   Group {i} ({len(group)} members): {suggested_role}")
    
    # Test group composition updates
    print(f"\n5. Testing Group Composition Updates...")
    role_engine.update_group_composition([
        {"name": "Player1", "role": "dps"},
        {"name": "Player2", "role": "dps"},
        {"name": "Player3", "role": "dps"}
    ])
    print(f"   Updated group composition, current role: {role_engine.current_role}")
    
    # Test role-specific triggers
    print(f"\n6. Testing Role-Specific Triggers...")
    role_engine.set_current_role("tank")
    tank_triggers = role_engine.get_role_specific_triggers("tank_triggers")
    print(f"   Tank triggers: {tank_triggers}")
    
    role_engine.set_current_role("healer")
    healer_triggers = role_engine.get_role_specific_triggers("healer_triggers")
    print(f"   Healer triggers: {healer_triggers}")
    
    # Test combat decisions
    print(f"\n7. Testing Combat Decision Evaluation...")
    combat_context = {"player_health": 75, "target_health": 50}
    
    for role in ["tank", "healer", "solo_dps"]:
        role_engine.set_current_role(role)
        decisions = ["use_taunt", "maintain_aggro", "use_group_healing", "use_crowd_control"]
        
        print(f"   {role.upper()} decisions:")
        for decision in decisions:
            result = role_engine.evaluate_combat_decision(decision, combat_context)
            print(f"     - {decision}: {result}")
    
    # Test role suggestions
    print(f"\n8. Testing Role Suggestions...")
    suggestions = role_engine.get_role_suggestions(combat_context)
    for suggestion in suggestions:
        print(f"   - {suggestion['name']}: {suggestion['reason']}")
    
    # Test performance metrics
    print(f"\n9. Testing Performance Metrics...")
    role_engine.set_current_role("solo_dps")
    role_engine.update_role_performance({
        "damage_dealt": 1500,
        "abilities_used": 15,
        "survival_time": 120
    })
    
    metrics = role_engine.get_role_performance_metrics()
    print(f"   Performance metrics: {metrics}")
    
    # Test configuration validation
    print(f"\n10. Testing Configuration Validation...")
    is_valid, errors = role_engine.validate_role_configuration()
    if is_valid:
        print("   ✓ Role configuration is valid")
    else:
        print("   ✗ Role configuration has errors:")
        for error in errors:
            print(f"     - {error}")
    
    # Display statistics
    print(f"\n11. Role Engine Statistics:")
    stats = role_engine.get_statistics()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    print(f"\n" + "=" * 60)
    print("Combat Role Engine Demo Completed Successfully!")
    print("=" * 60)

def demo_combat_role_profile_manager():
    """Demonstrate the role-aware combat profile manager."""
    print("\n" + "=" * 60)
    print("Combat Role Profile Manager Demo")
    print("=" * 60)
    
    # Initialize the profile manager
    print("\n1. Initializing Combat Role Profile Manager...")
    profile_manager = CombatRoleProfileManager("config/combat_profiles/roles.json")
    
    # Load sample base profiles
    print("\n2. Loading Sample Base Profiles...")
    sample_profiles = {
        "rifleman_medic": {
            "name": "Rifleman Medic",
            "description": "Rifleman with medic abilities",
            "weapon_type": "ranged",
            "rotation": ["aim", "headshot", "burst_fire", "heal_self"],
            "cooldowns": {
                "aim": 0,
                "headshot": 5,
                "burst_fire": 15,
                "heal_self": 30
            },
            "emergency_abilities": {
                "critical_heal": "heal_self",
                "defensive": "stim_pack"
            }
        },
        "pistoleer_combat": {
            "name": "Pistoleer Combat",
            "description": "Pistoleer with combat focus",
            "weapon_type": "ranged",
            "rotation": ["pistol_shot", "burst_fire", "dodge"],
            "cooldowns": {
                "pistol_shot": 0,
                "burst_fire": 10,
                "dodge": 5
            },
            "emergency_abilities": {
                "defensive": "dodge",
                "escape": "sprint"
            }
        }
    }
    
    for profile_name, profile_data in sample_profiles.items():
        success = profile_manager.load_base_profile(profile_name, profile_data)
        if success:
            print(f"   ✓ Loaded base profile: {profile_name}")
        else:
            print(f"   ✗ Failed to load base profile: {profile_name}")
    
    # Test role-modified profile creation
    print("\n3. Testing Role-Modified Profile Creation...")
    test_combinations = [
        ("rifleman_medic", "healer"),
        ("rifleman_medic", "solo_dps"),
        ("pistoleer_combat", "tank"),
        ("pistoleer_combat", "pvp_roamer")
    ]
    
    for base_profile, role in test_combinations:
        modified_profile = profile_manager.create_role_modified_profile(base_profile, role)
        if modified_profile:
            print(f"   ✓ Created {base_profile}_{role}")
            print(f"     - Role: {modified_profile.get('role', 'Unknown')}")
            print(f"     - Rotation: {modified_profile.get('rotation', [])}")
            print(f"     - Role triggers: {list(modified_profile.get('role_triggers', {}).keys())}")
        else:
            print(f"   ✗ Failed to create {base_profile}_{role}")
    
    # Test profile setting
    print("\n4. Testing Profile Setting...")
    profile_manager.role_engine.set_current_role("healer")
    success = profile_manager.set_active_profile("rifleman_medic")
    if success:
        print(f"   ✓ Set active profile with healer role")
        active_profile = profile_manager.active_profile
        print(f"     - Profile name: {active_profile.get('name')}")
        print(f"     - Role: {active_profile.get('role')}")
        print(f"     - Rotation: {active_profile.get('rotation')}")
    else:
        print(f"   ✗ Failed to set active profile")
    
    # Test next ability selection
    print("\n5. Testing Next Ability Selection...")
    combat_context = {"player_health": 80, "target_health": 60}
    next_ability = profile_manager.get_next_ability(combat_context)
    print(f"   Next ability: {next_ability}")
    
    # Test profile suggestions
    print("\n6. Testing Profile Suggestions...")
    suggestions = profile_manager.get_profile_suggestions(combat_context)
    print(f"   Available profile combinations: {len(suggestions)}")
    for suggestion in suggestions[:3]:  # Show first 3
        print(f"     - {suggestion['description']}")
    
    # Test configuration validation
    print("\n7. Testing Configuration Validation...")
    is_valid, errors = profile_manager.validate_profile_configuration()
    if is_valid:
        print("   ✓ Profile configuration is valid")
    else:
        print("   ✗ Profile configuration has errors:")
        for error in errors:
            print(f"     - {error}")
    
    # Display statistics
    print("\n8. Profile Manager Statistics:")
    stats = profile_manager.get_statistics()
    for key, value in stats.items():
        if key == "role_engine_stats":
            print(f"   - {key}:")
            for sub_key, sub_value in value.items():
                print(f"     - {sub_key}: {sub_value}")
        else:
            print(f"   - {key}: {value}")
    
    print(f"\n" + "=" * 60)
    print("Combat Role Profile Manager Demo Completed Successfully!")
    print("=" * 60)

def main():
    """Main demo function."""
    try:
        # Run combat role engine demo
        demo_combat_role_engine()
        
        # Run combat role profile manager demo
        demo_combat_role_profile_manager()
        
        print(f"\n" + "=" * 60)
        print("MS11 Batch 084 - Combat Role Engine Demo Complete!")
        print("=" * 60)
        print("\nKey Features Demonstrated:")
        print("- Role-based combat logic and triggers")
        print("- Automatic role switching based on group composition")
        print("- Role-aware ability prioritization")
        print("- Integration with existing combat profiles")
        print("- Role-specific behavior modifications")
        print("- Performance tracking and analytics")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
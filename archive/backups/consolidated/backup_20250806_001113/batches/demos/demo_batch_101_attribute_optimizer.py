"""Demo script for Batch 101 - Attribute Optimizer Engine.

This demo showcases:
- Different weapon types and combat roles
- Armor recommendations with resistance focus
- Buff and food recommendations
- Build optimization workflows
- Integration with web dashboard
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

from core.attribute_optimizer import (
    AttributeOptimizer,
    WeaponType,
    CombatRole,
    ResistanceType,
    attribute_optimizer,
    optimize_character_build
)


def demo_basic_optimization():
    """Demonstrate basic build optimization."""
    print("=" * 60)
    print("DEMO: Basic Build Optimization")
    print("=" * 60)
    
    # Create a basic rifleman medic build
    optimization = optimize_character_build(
        build_name="Rifleman Medic",
        weapon_type=WeaponType.RIFLE,
        combat_role=CombatRole.HEALER
    )
    
    print(f"Build: {optimization.build_name}")
    print(f"Weapon Type: {optimization.weapon_type.value}")
    print(f"Combat Role: {optimization.combat_role.value}")
    print(f"Primary Attributes: {', '.join(optimization.primary_attributes)}")
    print(f"Overall Score: {optimization.overall_score:.2%}")
    print(f"Notes: {optimization.notes}")
    
    # Show armor recommendation
    armor = optimization.armor_recommendation
    print(f"\nArmor Recommendation:")
    print(f"  Primary Stats: {', '.join(armor.primary_stats)}")
    print(f"  Secondary Stats: {', '.join(armor.secondary_stats)}")
    print(f"  Resistance Focus: {', '.join([r.value for r in armor.resistance_priorities])}")
    print(f"  Effectiveness: {armor.effectiveness_score:.2%}")
    print(f"  Reasoning: {armor.reasoning}")
    
    # Show buff recommendations
    print(f"\nBuff Recommendations ({len(optimization.buff_recommendations)}):")
    for buff in optimization.buff_recommendations[:3]:  # Show first 3
        print(f"  - {buff.buff_name}: {buff.primary_effect} ({buff.duration}min, ~{buff.cost_estimate}cr)")
    
    print(f"\nFood Recommendations ({len(optimization.food_recommendations)}):")
    for food in optimization.food_recommendations[:3]:  # Show first 3
        print(f"  - {food.buff_name}: {food.primary_effect} ({food.duration}min, ~{food.cost_estimate}cr)")
    
    return optimization


def demo_different_build_types():
    """Demonstrate optimization for different build types."""
    print("\n" + "=" * 60)
    print("DEMO: Different Build Types")
    print("=" * 60)
    
    build_configs = [
        ("Melee Tank", WeaponType.MELEE, CombatRole.TANK),
        ("Ranged DPS", WeaponType.RANGED, CombatRole.DPS),
        ("Pistol Healer", WeaponType.PISTOL, CombatRole.HEALER),
        ("Heavy Support", WeaponType.HEAVY_WEAPON, CombatRole.SUPPORT),
        ("Light Saber Jedi", WeaponType.LIGHT_SABER, CombatRole.HYBRID),
    ]
    
    for build_name, weapon_type, combat_role in build_configs:
        print(f"\n--- {build_name} ---")
        
        optimization = optimize_character_build(
            build_name=build_name,
            weapon_type=weapon_type,
            combat_role=combat_role
        )
        
        print(f"Primary Attributes: {', '.join(optimization.primary_attributes)}")
        print(f"Resistance Focus: {', '.join([r.value for r in optimization.resistance_focus])}")
        print(f"Overall Score: {optimization.overall_score:.2%}")
        print(f"Armor Effectiveness: {optimization.armor_recommendation.effectiveness_score:.2%}")


def demo_resistance_focus():
    """Demonstrate how resistance focus affects recommendations."""
    print("\n" + "=" * 60)
    print("DEMO: Resistance Focus Impact")
    print("=" * 60)
    
    # Test without resistance focus
    print("\n--- Default Resistance Focus ---")
    optimization1 = optimize_character_build(
        build_name="Ranged DPS",
        weapon_type=WeaponType.RANGED,
        combat_role=CombatRole.DPS
    )
    
    print(f"Default Resistances: {', '.join([r.value for r in optimization1.resistance_focus])}")
    print(f"Effectiveness: {optimization1.armor_recommendation.effectiveness_score:.2%}")
    
    # Test with custom resistance focus
    print("\n--- Custom Resistance Focus ---")
    optimization2 = optimize_character_build(
        build_name="Ranged DPS",
        weapon_type=WeaponType.RANGED,
        combat_role=CombatRole.DPS,
        resistance_focus=[ResistanceType.KINETIC, ResistanceType.ENERGY, ResistanceType.BLAST]
    )
    
    print(f"Custom Resistances: {', '.join([r.value for r in optimization2.resistance_focus])}")
    print(f"Effectiveness: {optimization2.armor_recommendation.effectiveness_score:.2%}")
    
    # Compare the differences
    print(f"\n--- Comparison ---")
    print(f"Default vs Custom Effectiveness: {optimization1.armor_recommendation.effectiveness_score:.2%} vs {optimization2.armor_recommendation.effectiveness_score:.2%}")


def demo_armor_slot_recommendations():
    """Demonstrate detailed armor slot recommendations."""
    print("\n" + "=" * 60)
    print("DEMO: Detailed Armor Slot Recommendations")
    print("=" * 60)
    
    optimization = optimize_character_build(
        build_name="Tank Build",
        weapon_type=WeaponType.MELEE,
        combat_role=CombatRole.TANK
    )
    
    armor = optimization.armor_recommendation
    
    print(f"Build: {armor.build_name}")
    print(f"Reasoning: {armor.reasoning}")
    print(f"\nArmor Slot Recommendations:")
    
    for slot_name, slot_data in armor.armor_slots.items():
        print(f"\n{slot_name.title()}:")
        print(f"  Primary Stats: {', '.join(slot_data['primary_stats'])}")
        print(f"  Secondary Stats: {', '.join(slot_data['secondary_stats'])}")
        print(f"  Resistances: {', '.join(slot_data['resistances'])}")
        if slot_data.get('special'):
            print(f"  Special: {slot_data['special']}")


def demo_buff_recommendations():
    """Demonstrate detailed buff recommendations."""
    print("\n" + "=" * 60)
    print("DEMO: Detailed Buff Recommendations")
    print("=" * 60)
    
    optimization = optimize_character_build(
        build_name="Healer Build",
        weapon_type=WeaponType.RANGED,
        combat_role=CombatRole.HEALER
    )
    
    print(f"Build: {optimization.build_name}")
    print(f"Primary Attributes: {', '.join(optimization.primary_attributes)}")
    
    print(f"\nMedicine/Stim Buffs:")
    for buff in optimization.buff_recommendations:
        print(f"  - {buff.buff_name.replace('_', ' ').title()}")
        print(f"    Effect: {buff.primary_effect}")
        print(f"    Duration: {buff.duration} minutes")
        print(f"    Cost: ~{buff.cost_estimate} credits")
        print(f"    Availability: {buff.availability}")
        print(f"    Compatibility: {', '.join(buff.build_compatibility)}")
        print()
    
    print(f"Food Buffs:")
    for food in optimization.food_recommendations:
        print(f"  - {food.buff_name.replace('_', ' ').title()}")
        print(f"    Effect: {food.primary_effect}")
        print(f"    Duration: {food.duration} minutes")
        print(f"    Cost: ~{food.cost_estimate} credits")
        print(f"    Availability: {food.availability}")
        print()


def demo_attribute_effects():
    """Demonstrate attribute effects information."""
    print("\n" + "=" * 60)
    print("DEMO: Attribute Effects")
    print("=" * 60)
    
    effects = attribute_optimizer.get_attribute_effects()
    
    print(f"Available Attribute Effects ({len(effects)}):")
    for attr, effect in effects.items():
        print(f"  {attr.title()}:")
        print(f"    Weapon Type: {effect.weapon_type.value}")
        print(f"    Effect Type: {effect.effect_type}")
        print(f"    Effect Value: {effect.effect_value}")
        print(f"    Description: {effect.description}")
        print()


def demo_weapon_attributes():
    """Demonstrate weapon-attribute relationships."""
    print("\n" + "=" * 60)
    print("DEMO: Weapon-Attribute Relationships")
    print("=" * 60)
    
    weapon_types = [
        WeaponType.MELEE,
        WeaponType.RANGED,
        WeaponType.PISTOL,
        WeaponType.RIFLE,
        WeaponType.HEAVY_WEAPON,
        WeaponType.LIGHT_SABER
    ]
    
    for weapon_type in weapon_types:
        attributes = attribute_optimizer.get_weapon_attributes(weapon_type)
        print(f"{weapon_type.value.replace('_', ' ').title()}: {', '.join(attributes)}")


def demo_role_priorities():
    """Demonstrate role-based attribute priorities."""
    print("\n" + "=" * 60)
    print("DEMO: Role-Based Attribute Priorities")
    print("=" * 60)
    
    roles = [
        CombatRole.TANK,
        CombatRole.DPS,
        CombatRole.HEALER,
        CombatRole.SUPPORT,
        CombatRole.HYBRID
    ]
    
    for role in roles:
        priorities = attribute_optimizer.get_role_priorities(role)
        print(f"\n{role.value.upper()}:")
        
        # Sort by priority (descending)
        sorted_priorities = sorted(priorities.items(), key=lambda x: x[1], reverse=True)
        
        for attr, priority in sorted_priorities[:5]:  # Show top 5
            print(f"  {attr.title()}: {priority:.2f}")


def demo_cache_functionality():
    """Demonstrate caching functionality."""
    print("\n" + "=" * 60)
    print("DEMO: Caching Functionality")
    print("=" * 60)
    
    # Create a temporary cache directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Cache Directory: {temp_dir}")
        
        # Create optimizer with custom cache
        optimizer = AttributeOptimizer(cache_dir=temp_dir)
        
        # Parse some data
        optimizer._parse_attribute_effects("")
        optimizer._build_weapon_attributes_mapping()
        optimizer._build_role_priorities()
        
        # Save to cache
        optimizer._save_cached_data()
        
        # Check if cache is valid
        is_valid = optimizer._is_cache_valid()
        print(f"Cache Valid: {is_valid}")
        
        # Create new optimizer instance to test loading
        new_optimizer = AttributeOptimizer(cache_dir=temp_dir)
        print(f"Loaded {len(new_optimizer.attribute_effects)} attribute effects from cache")
        print(f"Loaded {len(new_optimizer.weapon_attributes)} weapon types from cache")
        print(f"Loaded {len(new_optimizer.role_priorities)} combat roles from cache")


def demo_web_dashboard_integration():
    """Demonstrate web dashboard integration."""
    print("\n" + "=" * 60)
    print("DEMO: Web Dashboard Integration")
    print("=" * 60)
    
    print("The Attribute Optimizer is integrated with the web dashboard at:")
    print("  http://localhost:8000/tools/attribute-planner")
    
    print("\nAvailable API Endpoints:")
    api_endpoints = [
        "/api/attribute-optimizer/optimize (POST)",
        "/api/attribute-optimizer/weapon-types",
        "/api/attribute-optimizer/combat-roles",
        "/api/attribute-optimizer/resistance-types",
        "/api/attribute-optimizer/attribute-effects",
        "/api/attribute-optimizer/weapon-attributes/<weapon_type>",
        "/api/attribute-optimizer/role-priorities/<combat_role>"
    ]
    
    for endpoint in api_endpoints:
        print(f"  {endpoint}")
    
    print("\nFeatures:")
    print("  - Interactive build configuration form")
    print("  - Real-time optimization generation")
    print("  - Detailed armor slot recommendations")
    print("  - Buff and food suggestions")
    print("  - Effectiveness scoring")
    print("  - Attribute effects information")


def demo_performance_test():
    """Demonstrate performance characteristics."""
    print("\n" + "=" * 60)
    print("DEMO: Performance Test")
    print("=" * 60)
    
    import time
    
    # Test multiple optimizations
    build_configs = [
        ("Build 1", WeaponType.RANGED, CombatRole.DPS),
        ("Build 2", WeaponType.MELEE, CombatRole.TANK),
        ("Build 3", WeaponType.PISTOL, CombatRole.HEALER),
        ("Build 4", WeaponType.RIFLE, CombatRole.SUPPORT),
        ("Build 5", WeaponType.HEAVY_WEAPON, CombatRole.HYBRID),
    ]
    
    start_time = time.time()
    
    optimizations = []
    for build_name, weapon_type, combat_role in build_configs:
        optimization = optimize_character_build(
            build_name=build_name,
            weapon_type=weapon_type,
            combat_role=combat_role
        )
        optimizations.append(optimization)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Generated {len(optimizations)} optimizations in {duration:.3f} seconds")
    print(f"Average time per optimization: {duration/len(optimizations):.3f} seconds")
    
    # Show effectiveness scores
    print(f"\nEffectiveness Scores:")
    for opt in optimizations:
        print(f"  {opt.build_name}: {opt.overall_score:.2%}")


def demo_export_optimization():
    """Demonstrate exporting optimization data."""
    print("\n" + "=" * 60)
    print("DEMO: Export Optimization Data")
    print("=" * 60)
    
    optimization = optimize_character_build(
        build_name="Demo Build",
        weapon_type=WeaponType.RANGED,
        combat_role=CombatRole.DPS
    )
    
    # Convert to dict for JSON export
    export_data = {
        'build_name': optimization.build_name,
        'weapon_type': optimization.weapon_type.value,
        'combat_role': optimization.combat_role.value,
        'primary_attributes': optimization.primary_attributes,
        'armor_recommendation': {
            'build_name': optimization.armor_recommendation.build_name,
            'weapon_type': optimization.armor_recommendation.weapon_type.value,
            'combat_role': optimization.armor_recommendation.combat_role.value,
            'primary_stats': optimization.armor_recommendation.primary_stats,
            'secondary_stats': optimization.armor_recommendation.secondary_stats,
            'resistance_priorities': [r.value for r in optimization.armor_recommendation.resistance_priorities],
            'armor_slots': optimization.armor_recommendation.armor_slots,
            'reasoning': optimization.armor_recommendation.reasoning,
            'effectiveness_score': optimization.armor_recommendation.effectiveness_score
        },
        'buff_recommendations': [
            {
                'buff_name': buff.buff_name,
                'buff_type': buff.buff_type,
                'primary_effect': buff.primary_effect,
                'secondary_effects': buff.secondary_effects,
                'duration': buff.duration,
                'cost_estimate': buff.cost_estimate,
                'availability': buff.availability,
                'build_compatibility': buff.build_compatibility
            }
            for buff in optimization.buff_recommendations
        ],
        'food_recommendations': [
            {
                'buff_name': buff.buff_name,
                'buff_type': buff.buff_type,
                'primary_effect': buff.primary_effect,
                'secondary_effects': buff.secondary_effects,
                'duration': buff.duration,
                'cost_estimate': buff.cost_estimate,
                'availability': buff.availability,
                'build_compatibility': buff.build_compatibility
            }
            for buff in optimization.food_recommendations
        ],
        'resistance_focus': [r.value for r in optimization.resistance_focus],
        'overall_score': optimization.overall_score,
        'notes': optimization.notes,
        'exported_at': datetime.now().isoformat()
    }
    
    # Save to file
    export_file = Path("demo_optimization_export.json")
    with open(export_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"Optimization exported to: {export_file}")
    print(f"Export includes:")
    print(f"  - Build configuration")
    print(f"  - Armor recommendations")
    print(f"  - Buff recommendations ({len(export_data['buff_recommendations'])} items)")
    print(f"  - Food recommendations ({len(export_data['food_recommendations'])} items)")
    print(f"  - Overall score: {export_data['overall_score']:.2%}")


def main():
    """Run the comprehensive attribute optimizer demo."""
    print("BATCH 101 - ATTRIBUTE OPTIMIZER ENGINE DEMO")
    print("=" * 60)
    print("This demo showcases the build-aware recommendation system")
    print("using SWG attribute effects for optimal character builds.")
    print()
    
    try:
        # Run all demos
        demo_basic_optimization()
        demo_different_build_types()
        demo_resistance_focus()
        demo_armor_slot_recommendations()
        demo_buff_recommendations()
        demo_attribute_effects()
        demo_weapon_attributes()
        demo_role_priorities()
        demo_cache_functionality()
        demo_web_dashboard_integration()
        demo_performance_test()
        demo_export_optimization()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("The Attribute Optimizer Engine provides:")
        print("  ✓ Build-aware armor recommendations")
        print("  ✓ Weapon-specific attribute optimization")
        print("  ✓ Role-based priority systems")
        print("  ✓ Resistance focus customization")
        print("  ✓ Buff and food suggestions")
        print("  ✓ Web dashboard integration")
        print("  ✓ Performance optimization")
        print("  ✓ Data export capabilities")
        print()
        print("Access the web interface at: http://localhost:8000/tools/attribute-planner")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
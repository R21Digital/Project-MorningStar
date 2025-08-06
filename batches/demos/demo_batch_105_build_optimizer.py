"""Demo script for Batch 105 - Build Optimizer Tool.

This script demonstrates the functionality of the Build Optimizer Tool
by analyzing various character builds and showing the recommendations.
"""

import json
from datetime import datetime
from core.build_optimizer import (
    BuildOptimizer,
    CharacterStats,
    CombatRole,
    build_optimizer,
    analyze_character_build,
    get_profession_recommendations,
    get_equipment_recommendations,
    get_buff_recommendations,
    get_food_recommendations
)


def print_separator(title):
    """Print a formatted separator with title."""
    print("\n" + "=" * 60)
    print(f" {title} ")
    print("=" * 60)


def print_character_stats(stats):
    """Print character stats in a formatted way."""
    print(f"Level {stats.level} {stats.combat_role.value.upper()}")
    print(f"Primary Stats: Health={stats.health}, Action={stats.action}, Mind={stats.mind}")
    print(f"Secondary Stats: Str={stats.strength}, Con={stats.constitution}, Agi={stats.agility}, Qui={stats.quickness}")
    print(f"Additional: Sta={stats.stamina}, Pre={stats.presence}, Foc={stats.focus}, Wil={stats.willpower}")
    if stats.current_profession:
        print(f"Current Profession: {stats.current_profession}")
    if stats.respec_available:
        print("Respec Available: Yes")


def print_recommendations(recommendations, category):
    """Print recommendations in a formatted way."""
    print(f"\n{category} Recommendations:")
    print("-" * 40)
    
    if not recommendations:
        print("No recommendations available.")
        return
    
    for i, rec in enumerate(recommendations, 1):
        score_percent = int(rec.score * 100)
        print(f"{i}. {rec.name} ({score_percent}%)")
        print(f"   Description: {rec.description}")
        print(f"   Reasoning: {rec.reasoning}")
        if rec.benefits:
            print(f"   Benefits: {', '.join(rec.benefits)}")
        if rec.drawbacks:
            print(f"   Drawbacks: {', '.join(rec.drawbacks)}")
        if rec.cost:
            print(f"   Cost: {rec.cost} credits")
        print()


def demo_dps_build():
    """Demo a DPS character build."""
    print_separator("DPS BUILD ANALYSIS")
    
    # Create a DPS character with high action and strength
    stats = CharacterStats(
        health=150,
        action=120,
        mind=80,
        strength=60,
        constitution=40,
        agility=50,
        quickness=45,
        stamina=35,
        presence=25,
        focus=30,
        willpower=25,
        combat_role=CombatRole.DPS,
        level=20,
        current_profession="rifleman",
        respec_available=False
    )
    
    print_character_stats(stats)
    
    # Analyze the build
    analysis = analyze_character_build(stats)
    
    print(f"\nOverall Build Score: {int(analysis.total_score * 100)}%")
    print(f"Analysis Summary: {analysis.summary}")
    
    # Print recommendations by category
    profession_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value == 'profession']
    equipment_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value in ['armor', 'weapon']]
    buff_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value in ['buff', 'food']]
    
    print_recommendations(profession_recs, "Profession")
    print_recommendations(equipment_recs, "Equipment")
    print_recommendations(buff_recs, "Buffs & Food")


def demo_tank_build():
    """Demo a tank character build."""
    print_separator("TANK BUILD ANALYSIS")
    
    # Create a tank character with high constitution and health
    stats = CharacterStats(
        health=200,
        action=80,
        mind=60,
        strength=50,
        constitution=80,
        agility=30,
        quickness=25,
        stamina=70,
        presence=30,
        focus=40,
        willpower=45,
        combat_role=CombatRole.TANK,
        level=25,
        current_profession="commando",
        respec_available=False
    )
    
    print_character_stats(stats)
    
    # Analyze the build
    analysis = analyze_character_build(stats)
    
    print(f"\nOverall Build Score: {int(analysis.total_score * 100)}%")
    print(f"Analysis Summary: {analysis.summary}")
    
    # Print recommendations by category
    profession_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value == 'profession']
    equipment_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value in ['armor', 'weapon']]
    buff_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value in ['buff', 'food']]
    
    print_recommendations(profession_recs, "Profession")
    print_recommendations(equipment_recs, "Equipment")
    print_recommendations(buff_recs, "Buffs & Food")


def demo_support_build():
    """Demo a support character build."""
    print_separator("SUPPORT BUILD ANALYSIS")
    
    # Create a support character with high mind and focus
    stats = CharacterStats(
        health=100,
        action=60,
        mind=150,
        strength=25,
        constitution=40,
        agility=30,
        quickness=25,
        stamina=35,
        presence=50,
        focus=80,
        willpower=75,
        combat_role=CombatRole.SUPPORT,
        level=20,
        current_profession="medic",
        respec_available=False
    )
    
    print_character_stats(stats)
    
    # Analyze the build
    analysis = analyze_character_build(stats)
    
    print(f"\nOverall Build Score: {int(analysis.total_score * 100)}%")
    print(f"Analysis Summary: {analysis.summary}")
    
    # Print recommendations by category
    profession_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value == 'profession']
    equipment_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value in ['armor', 'weapon']]
    buff_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value in ['buff', 'food']]
    
    print_recommendations(profession_recs, "Profession")
    print_recommendations(equipment_recs, "Equipment")
    print_recommendations(buff_recs, "Buffs & Food")


def demo_pvp_build():
    """Demo a PVP character build."""
    print_separator("PVP BUILD ANALYSIS")
    
    # Create a PVP character with high agility and quickness
    stats = CharacterStats(
        health=120,
        action=100,
        mind=60,
        strength=45,
        constitution=50,
        agility=70,
        quickness=75,
        stamina=40,
        presence=30,
        focus=35,
        willpower=30,
        combat_role=CombatRole.PVP,
        level=30,
        current_profession="pistoleer",
        respec_available=False
    )
    
    print_character_stats(stats)
    
    # Analyze the build
    analysis = analyze_character_build(stats)
    
    print(f"\nOverall Build Score: {int(analysis.total_score * 100)}%")
    print(f"Analysis Summary: {analysis.summary}")
    
    # Print recommendations by category
    profession_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value == 'profession']
    equipment_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value in ['armor', 'weapon']]
    buff_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value in ['buff', 'food']]
    
    print_recommendations(profession_recs, "Profession")
    print_recommendations(equipment_recs, "Equipment")
    print_recommendations(buff_recs, "Buffs & Food")


def demo_build_with_respec():
    """Demo a build analysis with respec available."""
    print_separator("BUILD WITH RESPEC ANALYSIS")
    
    # Create a character with suboptimal stats but respec available
    stats = CharacterStats(
        health=100,
        action=30,  # Below optimal for DPS
        mind=60,
        strength=40,
        constitution=30,
        agility=30,
        quickness=25,
        stamina=25,
        presence=25,
        focus=30,
        willpower=25,
        combat_role=CombatRole.DPS,
        level=15,
        current_profession="rifleman",
        respec_available=True  # Key difference
    )
    
    print_character_stats(stats)
    
    # Analyze the build
    analysis = analyze_character_build(stats)
    
    print(f"\nOverall Build Score: {int(analysis.total_score * 100)}%")
    print(f"Analysis Summary: {analysis.summary}")
    
    # Check for stat reallocation recommendations
    reallocation_recs = [rec for rec in analysis.recommendations if rec.recommendation_type.value == 'stat_reallocation']
    
    if reallocation_recs:
        print_recommendations(reallocation_recs, "Stat Reallocation")
    else:
        print("\nNo stat reallocation recommendations (stats are optimal)")


def demo_individual_recommendations():
    """Demo individual recommendation functions."""
    print_separator("INDIVIDUAL RECOMMENDATION FUNCTIONS")
    
    # Create a test character
    stats = CharacterStats(
        health=150,
        action=120,
        mind=80,
        strength=45,
        constitution=35,
        agility=40,
        quickness=35,
        stamina=30,
        presence=25,
        focus=30,
        willpower=25,
        combat_role=CombatRole.DPS,
        level=15
    )
    
    print_character_stats(stats)
    
    # Test profession recommendations
    print("\nTesting profession recommendations...")
    profession_recs = get_profession_recommendations(stats)
    print_recommendations(profession_recs, "Profession")
    
    # Test equipment recommendations
    print("\nTesting equipment recommendations...")
    equipment_recs = get_equipment_recommendations(stats)
    print_recommendations(equipment_recs, "Equipment")
    
    # Test buff recommendations
    print("\nTesting buff recommendations...")
    buff_recs = get_buff_recommendations(stats)
    print_recommendations(buff_recs, "Buffs")
    
    # Test food recommendations
    print("\nTesting food recommendations...")
    food_recs = get_food_recommendations(stats)
    print_recommendations(food_recs, "Food")


def demo_optimizer_configuration():
    """Demo the optimizer configuration and data structures."""
    print_separator("OPTIMIZER CONFIGURATION")
    
    optimizer = BuildOptimizer()
    
    print("Available Professions:")
    for profession, requirements in optimizer.profession_requirements.items():
        print(f"  - {profession.title()}: {requirements['description']}")
        print(f"    Primary Stats: {', '.join(requirements['primary_stats'])}")
        print(f"    Secondary Stats: {', '.join(requirements['secondary_stats'])}")
        print(f"    Combat Roles: {[role.value for role in requirements['combat_roles']]}")
        print()
    
    print("Buff Recommendations by Combat Role:")
    for role, buffs in optimizer.buff_recommendations.items():
        print(f"  - {role.upper()}: {', '.join(buffs)}")
    
    print("\nFood Recommendations by Combat Role:")
    for role, foods in optimizer.food_recommendations.items():
        print(f"  - {role.upper()}: {', '.join(foods)}")


def demo_serialization():
    """Demo serialization of build analysis results."""
    print_separator("SERIALIZATION DEMO")
    
    # Create a test character
    stats = CharacterStats(
        health=150,
        action=120,
        mind=80,
        strength=45,
        constitution=35,
        agility=40,
        quickness=35,
        stamina=30,
        presence=25,
        focus=30,
        willpower=25,
        combat_role=CombatRole.DPS,
        level=15
    )
    
    # Analyze the build
    analysis = analyze_character_build(stats)
    
    # Convert to dictionary
    analysis_dict = analysis.to_dict()
    
    print("Build Analysis as JSON:")
    print(json.dumps(analysis_dict, indent=2))
    
    # Test that we can reconstruct the analysis
    print("\nTesting reconstruction...")
    reconstructed_stats = CharacterStats.from_dict(analysis_dict['character_stats'])
    print(f"Reconstructed stats match: {reconstructed_stats.health == stats.health}")


def demo_performance():
    """Demo performance characteristics."""
    print_separator("PERFORMANCE DEMO")
    
    import time
    
    # Test multiple builds
    test_builds = [
        CharacterStats(health=150, action=120, mind=80, combat_role=CombatRole.DPS, level=15),
        CharacterStats(health=200, action=80, mind=100, combat_role=CombatRole.TANK, level=20),
        CharacterStats(health=100, action=60, mind=150, combat_role=CombatRole.SUPPORT, level=18),
        CharacterStats(health=120, action=100, mind=60, combat_role=CombatRole.PVP, level=25),
        CharacterStats(health=180, action=90, mind=70, combat_role=CombatRole.HYBRID, level=22)
    ]
    
    start_time = time.time()
    
    for i, stats in enumerate(test_builds, 1):
        print(f"Analyzing build {i} ({stats.combat_role.value})...")
        analysis = analyze_character_build(stats)
        print(f"  - Score: {int(analysis.total_score * 100)}%")
        print(f"  - Recommendations: {len(analysis.recommendations)}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nTotal analysis time: {duration:.2f} seconds")
    print(f"Average time per build: {duration / len(test_builds):.2f} seconds")


def main():
    """Run all demos."""
    print("Build Optimizer Tool - Batch 105 Demo")
    print("=" * 60)
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all demos
        demo_dps_build()
        demo_tank_build()
        demo_support_build()
        demo_pvp_build()
        demo_build_with_respec()
        demo_individual_recommendations()
        demo_optimizer_configuration()
        demo_serialization()
        demo_performance()
        
        print_separator("DEMO COMPLETE")
        print("All demos completed successfully!")
        print("The Build Optimizer Tool provides comprehensive character build analysis")
        print("with AI-generated recommendations for professions, equipment, buffs, and more.")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
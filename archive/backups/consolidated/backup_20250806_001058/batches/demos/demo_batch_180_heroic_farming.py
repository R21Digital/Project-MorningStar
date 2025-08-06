#!/usr/bin/env python3
"""
Demo script for Batch 180 - Build-Aware Heroic Farming Logic
Demonstrates the build-aware heroic farming system with various character builds and farming modes.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from core.modes.heroic_mode import (
    BuildAwareHeroicMode, 
    CharacterBuild, 
    FarmingMode, 
    GearTier
)

def create_character_builds() -> Dict[str, CharacterBuild]:
    """Create various character builds for testing."""
    return {
        "marksman_elite": CharacterBuild(
            name="EliteMarksman",
            profession="Marksman",
            level=85,
            faction="Rebel",
            gear_stats={
                "weapon_damage": 2200,
                "accuracy": 0.95,
                "critical_chance": 0.25
            },
            resistances={
                "energy": 0.45,
                "kinetic": 0.35,
                "blast": 0.40
            },
            skills={
                "marksman": 4000,
                "rifle": 4000,
                "pistol": 4000
            },
            buffs=["damage_buff", "accuracy_buff", "critical_buff"],
            debuffs=[]
        ),
        
        "medic_standard": CharacterBuild(
            name="StandardMedic",
            profession="Medic",
            level=80,
            faction="Neutral",
            gear_stats={
                "healing_power": 1400,
                "healing_efficiency": 0.85,
                "force_pool": 2200
            },
            resistances={
                "energy": 0.30,
                "kinetic": 0.20,
                "blast": 0.25
            },
            skills={
                "medical": 4000,
                "healing": 4000,
                "support": 3000
            },
            buffs=["healing_buff", "force_buff"],
            debuffs=[]
        ),
        
        "commando_advanced": CharacterBuild(
            name="AdvancedCommando",
            profession="Commando",
            level=82,
            faction="Imperial",
            gear_stats={
                "weapon_damage": 2000,
                "armor_penetration": 0.25,
                "critical_chance": 0.22,
                "armor": 1800
            },
            resistances={
                "energy": 0.40,
                "kinetic": 0.30,
                "blast": 0.35
            },
            skills={
                "commando": 4000,
                "heavy_weapons": 4000,
                "armor": 3500
            },
            buffs=["armor_buff", "damage_buff"],
            debuffs=[]
        ),
        
        "jedi_basic": CharacterBuild(
            name="BasicJedi",
            profession="Jedi",
            level=75,
            faction="Rebel",
            gear_stats={
                "force_power": 1200,
                "lightsaber_damage": 1000,
                "force_pool": 2000
            },
            resistances={
                "energy": 0.25,
                "kinetic": 0.20,
                "blast": 0.22
            },
            skills={
                "jedi": 3000,
                "lightsaber": 3000,
                "force": 3000
            },
            buffs=["force_buff"],
            debuffs=[]
        ),
        
        "brawler_undergeared": CharacterBuild(
            name="UndergearedBrawler",
            profession="Brawler",
            level=70,
            faction="Neutral",
            gear_stats={
                "melee_damage": 1000,
                "armor": 800,
                "dodge_chance": 0.15
            },
            resistances={
                "energy": 0.20,
                "kinetic": 0.15,
                "blast": 0.18
            },
            skills={
                "brawler": 2500,
                "unarmed": 2500,
                "melee": 2000
            },
            buffs=["dodge_buff"],
            debuffs=[]
        ),
        
        "artisan_noncombat": CharacterBuild(
            name="NonCombatArtisan",
            profession="Artisan",
            level=60,
            faction="Neutral",
            gear_stats={
                "crafting_skill": 1000,
                "resource_gathering": 800
            },
            resistances={
                "energy": 0.10,
                "kinetic": 0.10,
                "blast": 0.10
            },
            skills={
                "artisan": 4000,
                "crafting": 4000,
                "resource": 3000
            },
            buffs=["crafting_buff"],
            debuffs=[]
        )
    }

def demo_basic_functionality():
    """Demonstrate basic heroic farming functionality."""
    print("=" * 60)
    print("DEMO: Basic Heroic Farming Functionality")
    print("=" * 60)
    
    # Initialize heroic mode
    heroic_mode = BuildAwareHeroicMode()
    
    # Create character builds
    characters = create_character_builds()
    
    # Test with a marksman character
    marksman = characters["marksman_elite"]
    
    print(f"\nTesting with character: {marksman.name}")
    print(f"Profession: {marksman.profession}")
    print(f"Level: {marksman.level}")
    print(f"Faction: {marksman.faction}")
    print(f"Gear Stats: {marksman.gear_stats}")
    
    # Generate farming plan
    plan = heroic_mode.generate_farming_plan(marksman)
    
    print(f"\nFarming Plan Results:")
    print(f"  Viable Heroics: {len(plan.viable_heroics)}")
    print(f"  Recommended Heroics: {len(plan.recommended_heroics)}")
    print(f"  Estimated Success Rate: {plan.estimated_success_rate:.1%}")
    print(f"  Risk Level: {plan.risk_level}")
    
    print(f"\nRecommended Heroics:")
    for heroic in plan.recommended_heroics:
        print(f"  - {heroic.heroic_name}: {heroic.success_rate:.1%} success rate ({heroic.role})")
    
    print(f"\nStrategy Modifications:")
    for mod in plan.strategy_modifications[:5]:  # Show first 5
        print(f"  - {mod}")
    
    print(f"\nGear Improvements:")
    for improvement in plan.gear_improvements:
        print(f"  - {improvement}")

def demo_farming_modes():
    """Demonstrate different farming modes."""
    print("\n" + "=" * 60)
    print("DEMO: Farming Modes Comparison")
    print("=" * 60)
    
    heroic_mode = BuildAwareHeroicMode()
    characters = create_character_builds()
    marksman = characters["marksman_elite"]
    
    modes = [
        FarmingMode.CONSERVATIVE,
        FarmingMode.BALANCED,
        FarmingMode.AGGRESSIVE,
        FarmingMode.EXPERIMENTAL
    ]
    
    for mode in modes:
        print(f"\n--- {mode.value.upper()} MODE ---")
        heroic_mode.set_farming_mode(mode)
        plan = heroic_mode.generate_farming_plan(marksman)
        
        print(f"  Recommended Heroics: {len(plan.recommended_heroics)}")
        print(f"  Success Rate: {plan.estimated_success_rate:.1%}")
        print(f"  Risk Level: {plan.risk_level}")
        
        if plan.recommended_heroics:
            print(f"  Top Recommendation: {plan.recommended_heroics[0].heroic_name}")

def demo_profession_compatibility():
    """Demonstrate compatibility across different professions."""
    print("\n" + "=" * 60)
    print("DEMO: Profession Compatibility Analysis")
    print("=" * 60)
    
    heroic_mode = BuildAwareHeroicMode()
    characters = create_character_builds()
    
    # Test all combat professions
    combat_characters = {
        "Marksman": characters["marksman_elite"],
        "Medic": characters["medic_standard"],
        "Commando": characters["commando_advanced"],
        "Jedi": characters["jedi_basic"],
        "Brawler": characters["brawler_undergeared"]
    }
    
    for profession, character in combat_characters.items():
        print(f"\n--- {profession.upper()} ANALYSIS ---")
        plan = heroic_mode.generate_farming_plan(character)
        
        print(f"  Character: {character.name}")
        print(f"  Level: {character.level}")
        print(f"  Viable Heroics: {len(plan.viable_heroics)}")
        print(f"  Recommended Heroics: {len(plan.recommended_heroics)}")
        print(f"  Success Rate: {plan.estimated_success_rate:.1%}")
        print(f"  Risk Level: {plan.risk_level}")
        
        if plan.recommended_heroics:
            print(f"  Best Heroic: {plan.recommended_heroics[0].heroic_name}")

def demo_gear_analysis():
    """Demonstrate gear tier analysis and improvement suggestions."""
    print("\n" + "=" * 60)
    print("DEMO: Gear Analysis and Improvement Suggestions")
    print("=" * 60)
    
    heroic_mode = BuildAwareHeroicMode()
    characters = create_character_builds()
    
    # Test characters with different gear levels
    test_characters = [
        ("Elite Marksman", characters["marksman_elite"]),
        ("Standard Medic", characters["medic_standard"]),
        ("Basic Jedi", characters["jedi_basic"]),
        ("Undergeared Brawler", characters["brawler_undergeared"])
    ]
    
    for char_name, character in test_characters:
        print(f"\n--- {char_name.upper()} ---")
        
        # Assess gear tier
        gear_tier = heroic_mode.assess_gear_tier(character)
        print(f"  Gear Tier: {gear_tier.value}")
        print(f"  Gear Stats: {character.gear_stats}")
        
        # Generate plan and show improvements
        plan = heroic_mode.generate_farming_plan(character)
        print(f"  Viable Heroics: {len(plan.viable_heroics)}")
        print(f"  Success Rate: {plan.estimated_success_rate:.1%}")
        
        if plan.gear_improvements:
            print(f"  Gear Improvements:")
            for improvement in plan.gear_improvements:
                print(f"    - {improvement}")
        else:
            print(f"  Gear Status: Good - No improvements needed")

def demo_risk_assessment():
    """Demonstrate risk assessment for different character builds."""
    print("\n" + "=" * 60)
    print("DEMO: Risk Assessment Analysis")
    print("=" * 60)
    
    heroic_mode = BuildAwareHeroicMode()
    characters = create_character_builds()
    
    # Test characters with varying risk levels
    test_characters = [
        ("Elite Marksman", characters["marksman_elite"]),
        ("Standard Medic", characters["medic_standard"]),
        ("Basic Jedi", characters["jedi_basic"]),
        ("Undergeared Brawler", characters["brawler_undergeared"]),
        ("Non-Combat Artisan", characters["artisan_noncombat"])
    ]
    
    for char_name, character in test_characters:
        print(f"\n--- {char_name.upper()} ---")
        
        # Check compatibility with all heroics
        for heroic_id in ["axkva_min", "ancient_jedi_temple", "sith_academy", "mandalorian_bunker", "imperial_fortress"]:
            compatibility = heroic_mode.check_heroic_compatibility(character, heroic_id)
            
            if compatibility.is_viable:
                print(f"  ✓ {compatibility.heroic_name}: {compatibility.success_rate:.1%} success ({compatibility.risk_assessment})")
            else:
                print(f"  ✗ {compatibility.heroic_name}: Not viable - {compatibility.missing_requirements[0] if compatibility.missing_requirements else 'Unknown reason'}")

def demo_strategy_modifications():
    """Demonstrate strategy modifications based on character build."""
    print("\n" + "=" * 60)
    print("DEMO: Strategy Modifications")
    print("=" * 60)
    
    heroic_mode = BuildAwareHeroicMode()
    characters = create_character_builds()
    
    # Test different farming modes with same character
    character = characters["marksman_elite"]
    
    for mode in [FarmingMode.CONSERVATIVE, FarmingMode.BALANCED, FarmingMode.AGGRESSIVE]:
        print(f"\n--- {mode.value.upper()} MODE STRATEGIES ---")
        heroic_mode.set_farming_mode(mode)
        plan = heroic_mode.generate_farming_plan(character)
        
        print(f"  Character: {character.name} ({character.profession})")
        print(f"  Farming Mode: {mode.value}")
        print(f"  Risk Level: {plan.risk_level}")
        
        print(f"  Strategy Modifications:")
        for i, mod in enumerate(plan.strategy_modifications[:8], 1):  # Show first 8
            print(f"    {i}. {mod}")
        
        if len(plan.strategy_modifications) > 8:
            print(f"    ... and {len(plan.strategy_modifications) - 8} more")

def demo_comprehensive_analysis():
    """Demonstrate comprehensive build analysis."""
    print("\n" + "=" * 60)
    print("DEMO: Comprehensive Build Analysis")
    print("=" * 60)
    
    heroic_mode = BuildAwareHeroicMode()
    characters = create_character_builds()
    
    for char_name, character in characters.items():
        print(f"\n{'='*40}")
        print(f"COMPREHENSIVE ANALYSIS: {character.name}")
        print(f"{'='*40}")
        
        # Analyze build compatibility
        analysis = heroic_mode.analyze_build_compatibility(character)
        
        print(f"Character Details:")
        print(f"  Name: {analysis['character_name']}")
        print(f"  Profession: {analysis['profession']}")
        print(f"  Level: {analysis['level']}")
        print(f"  Faction: {analysis['faction']}")
        print(f"  Gear Tier: {analysis['gear_tier']}")
        
        print(f"\nHeroic Compatibility:")
        print(f"  Viable Heroics: {analysis['viable_heroics_count']}")
        print(f"  Recommended Heroics: {analysis['recommended_heroics_count']}")
        print(f"  Estimated Success Rate: {analysis['estimated_success_rate']:.1%}")
        print(f"  Risk Level: {analysis['risk_level']}")
        
        print(f"\nStrategy Modifications:")
        for mod in analysis['strategy_modifications'][:5]:
            print(f"  - {mod}")
        
        if analysis['gear_improvements']:
            print(f"\nGear Improvements:")
            for improvement in analysis['gear_improvements']:
                print(f"  - {improvement}")

def main():
    """Run all demo functions."""
    print("BATCH 180 - BUILD-AWARE HEROIC FARMING LOGIC")
    print("=" * 60)
    print("This demo showcases the build-aware heroic farming system")
    print("that analyzes character builds and optimizes heroic strategies.")
    print("=" * 60)
    
    try:
        # Run all demo functions
        demo_basic_functionality()
        demo_farming_modes()
        demo_profession_compatibility()
        demo_gear_analysis()
        demo_risk_assessment()
        demo_strategy_modifications()
        demo_comprehensive_analysis()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("The build-aware heroic farming system provides:")
        print("✓ Character build analysis")
        print("✓ Heroic compatibility assessment")
        print("✓ Gear tier evaluation")
        print("✓ Risk assessment")
        print("✓ Strategy modifications")
        print("✓ Farming mode optimization")
        print("✓ Gear improvement suggestions")
        
    except Exception as e:
        print(f"\nDemo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
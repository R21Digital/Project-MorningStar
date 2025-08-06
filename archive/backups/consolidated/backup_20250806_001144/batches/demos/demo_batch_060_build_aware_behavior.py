"""Demo script for Batch 060 - Build-Aware Behavior System.

This script demonstrates the functionality of the build-aware behavior system,
including parsing skill calculator links and adapting combat behavior based on builds.
"""

import json
import time
from pathlib import Path
from datetime import datetime

from core.skill_calculator_parser import SkillCalculatorParser
from core.build_aware_behavior import BuildAwareBehavior, create_build_aware_behavior
from android_ms11.core.combat_profile_engine import CombatProfileEngine
from android_ms11.utils.logging_utils import log_event


def demonstrate_skill_calculator_parsing():
    """Demonstrate parsing skill calculator links."""
    print("\n=== Skill Calculator Link Parsing Demo ===")
    
    parser = SkillCalculatorParser()
    
    # Example skill calculator URLs (these would be real URLs from swgr.org)
    example_urls = [
        "https://swgr.org/skill-calculator/rifleman?skills=rifle_shot,marksman_shot,sniper_shot",
        "https://swgr.org/skill-calculator/pistoleer?skills=pistol_shot,quick_shot,point_blank",
        "https://swgr.org/skill-calculator/medic?skills=heal,cure_poison,medical_treatment",
        "https://swgr.org/skill-calculator/brawler?skills=melee_hit,power_attack,unarmed"
    ]
    
    for i, url in enumerate(example_urls, 1):
        print(f"\n--- Example {i}: {url} ---")
        
        try:
            # Parse the skill calculator link
            build_data = parser.parse_skill_calculator_link(url)
            
            print(f"✓ Successfully parsed build")
            print(f"  Combat Style: {build_data.get('combat_style', 'Unknown')}")
            print(f"  Weapons Supported: {', '.join(build_data.get('weapons_supported', []))}")
            print(f"  Abilities Granted: {len(build_data.get('abilities_granted', []))} abilities")
            print(f"  Minimum Attack Distance: {build_data.get('minimum_attack_distance', 'Unknown')}")
            print(f"  Build Summary: {build_data.get('build_summary', 'No summary')}")
            
            # Save the build to a file
            filename = f"demo_build_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = parser.save_build_to_file(build_data, filename)
            print(f"  ✓ Saved build to: {filepath}")
            
        except Exception as e:
            print(f"✗ Error parsing build: {e}")


def demonstrate_build_aware_behavior():
    """Demonstrate build-aware behavior system."""
    print("\n=== Build-Aware Behavior System Demo ===")
    
    # Create a combat engine
    combat_engine = CombatProfileEngine("profiles/combat")
    
    # Create build-aware behavior system
    build_aware = create_build_aware_behavior(combat_engine)
    
    # Example builds to demonstrate different combat styles
    example_builds = [
        {
            "name": "Rifleman Build",
            "url": "https://swgr.org/skill-calculator/rifleman?skills=rifle_shot,marksman_shot,sniper_shot",
            "expected_style": "ranged"
        },
        {
            "name": "Brawler Build", 
            "url": "https://swgr.org/skill-calculator/brawler?skills=melee_hit,power_attack,unarmed",
            "expected_style": "melee"
        },
        {
            "name": "Medic Build",
            "url": "https://swgr.org/skill-calculator/medic?skills=heal,cure_poison,medical_treatment",
            "expected_style": "support"
        }
    ]
    
    for build_info in example_builds:
        print(f"\n--- Testing {build_info['name']} ---")
        
        try:
            # Load build from link
            build_data = build_aware.load_build_from_link(build_info['url'])
            
            print(f"✓ Successfully loaded build")
            print(f"  Expected Style: {build_info['expected_style']}")
            print(f"  Actual Style: {build_data.get('combat_style', 'Unknown')}")
            
            # Get build summary
            summary = build_aware.get_build_summary()
            print(f"  Build Summary: {summary}")
            
            # Get combat recommendations
            recommendations = build_aware.get_combat_recommendations()
            print(f"  Combat Style: {recommendations.get('combat_style', 'Unknown')}")
            print(f"  Recommended Weapons: {', '.join(recommendations.get('recommended_weapons', []))}")
            print(f"  Priority Abilities: {', '.join(recommendations.get('priority_abilities', []))}")
            
            # Show tactical advice
            tactical_advice = recommendations.get('tactical_advice', [])
            if tactical_advice:
                print(f"  Tactical Advice:")
                for advice in tactical_advice:
                    print(f"    • {advice}")
            
            # Save build configuration
            config_file = build_aware.save_build_config()
            print(f"  ✓ Saved build config to: {config_file}")
            
        except Exception as e:
            print(f"✗ Error testing build: {e}")


def demonstrate_combat_adaptation():
    """Demonstrate how combat behavior adapts to different builds."""
    print("\n=== Combat Adaptation Demo ===")
    
    # Create combat engine and build-aware system
    combat_engine = CombatProfileEngine("profiles/combat")
    build_aware = create_build_aware_behavior(combat_engine)
    
    # Test different combat styles
    combat_styles = [
        {
            "name": "Ranged Combat",
            "url": "https://swgr.org/skill-calculator/rifleman?skills=rifle_shot,marksman_shot",
            "description": "Long-range combat with rifles"
        },
        {
            "name": "Melee Combat", 
            "url": "https://swgr.org/skill-calculator/brawler?skills=melee_hit,power_attack",
            "description": "Close-range combat with fists"
        },
        {
            "name": "Support Combat",
            "url": "https://swgr.org/skill-calculator/medic?skills=heal,cure_poison",
            "description": "Healing and support abilities"
        }
    ]
    
    for style in combat_styles:
        print(f"\n--- {style['name']} ---")
        print(f"Description: {style['description']}")
        
        try:
            # Load the build
            build_data = build_aware.load_build_from_link(style['url'])
            
            # Show how combat behavior adapts
            combat_style = build_data.get('combat_style', 'hybrid')
            min_distance = build_data.get('minimum_attack_distance', 3)
            weapons = build_data.get('weapons_supported', [])
            
            print(f"  Combat Style: {combat_style}")
            print(f"  Minimum Attack Distance: {min_distance}")
            print(f"  Weapons Supported: {', '.join(weapons)}")
            
            # Show ability priorities
            abilities = build_data.get('abilities_granted', [])
            if abilities:
                print(f"  Key Abilities: {', '.join(abilities[:3])}")
                if len(abilities) > 3:
                    print(f"    ... and {len(abilities) - 3} more")
            
            # Show tactical recommendations
            recommendations = build_aware.get_combat_recommendations()
            distance_strategy = recommendations.get('distance_strategy', {})
            
            print(f"  Distance Strategy:")
            print(f"    • Minimum Distance: {distance_strategy.get('minimum_distance', 'Unknown')}")
            print(f"    • Preferred Distance: {distance_strategy.get('preferred_distance', 'Unknown')}")
            print(f"    • Movement Style: {distance_strategy.get('movement_style', 'Unknown')}")
            
        except Exception as e:
            print(f"✗ Error demonstrating combat adaptation: {e}")


def demonstrate_build_summary_display():
    """Demonstrate displaying parsed build summary to user."""
    print("\n=== Build Summary Display Demo ===")
    
    parser = SkillCalculatorParser()
    
    # Example build URL
    build_url = "https://swgr.org/skill-calculator/rifleman_medic?skills=rifle_shot,heal,cure_poison"
    
    try:
        # Parse the build
        build_data = parser.parse_skill_calculator_link(build_url)
        
        print("=== Parsed Build Summary ===")
        print(f"Source URL: {build_data.get('source_url', 'Unknown')}")
        print(f"Parsed At: {build_data.get('parsed_at', 'Unknown')}")
        print()
        
        # Display profession information
        profession_boxes = build_data.get('profession_boxes', [])
        if profession_boxes:
            print("Profession Boxes:")
            for profession in profession_boxes:
                print(f"  • {profession}")
        print()
        
        # Display weapon information
        weapons_supported = build_data.get('weapons_supported', [])
        if weapons_supported:
            print("Weapons Supported:")
            for weapon in weapons_supported:
                print(f"  • {weapon}")
        print()
        
        # Display abilities
        abilities_granted = build_data.get('abilities_granted', [])
        if abilities_granted:
            print("Abilities Granted:")
            for ability in abilities_granted:
                print(f"  • {ability}")
        print()
        
        # Display combat information
        combat_style = build_data.get('combat_style', 'Unknown')
        min_distance = build_data.get('minimum_attack_distance', 'Unknown')
        
        print("Combat Information:")
        print(f"  • Combat Style: {combat_style}")
        print(f"  • Minimum Attack Distance: {min_distance}")
        print()
        
        # Display build summary
        build_summary = build_data.get('build_summary', 'No summary available')
        print("Build Summary:")
        print(f"  {build_summary}")
        print()
        
        # Ask for user confirmation
        print("=== User Confirmation ===")
        print("Please review the parsed build information above.")
        print("This build will be used to adapt MS11's combat behavior.")
        print("Type 'confirm' to proceed or 'cancel' to abort:")
        
        # In a real implementation, you would get user input here
        # For demo purposes, we'll simulate confirmation
        user_confirmation = "confirm"  # Simulated user input
        
        if user_confirmation.lower() == "confirm":
            print("✓ Build confirmed! MS11 will now adapt to this build.")
            
            # Create build-aware behavior and load the build
            build_aware = create_build_aware_behavior()
            build_aware.load_build_from_link(build_url)
            
            print("✓ Combat behavior has been adapted to the build.")
            
        else:
            print("✗ Build loading cancelled.")
            
    except Exception as e:
        print(f"✗ Error displaying build summary: {e}")


def main():
    """Main demonstration function."""
    print("=== Batch 060 - Build-Aware Behavior System Demo ===")
    print("This demo showcases the skill calculator link parser and build-aware behavior system.")
    print()
    
    # Ensure necessary directories exist
    Path("profiles/combat").mkdir(parents=True, exist_ok=True)
    Path("config/builds").mkdir(parents=True, exist_ok=True)
    
    try:
        # Run demonstrations
        demonstrate_skill_calculator_parsing()
        demonstrate_build_aware_behavior()
        demonstrate_combat_adaptation()
        demonstrate_build_summary_display()
        
        print("\n=== Demo Complete ===")
        print("✓ All demonstrations completed successfully!")
        print()
        print("Key Features Demonstrated:")
        print("• Parsing skill calculator links from swgr.org")
        print("• Extracting profession boxes, weapons, and abilities")
        print("• Adapting combat style (melee vs. ranged)")
        print("• Determining minimum attack distance")
        print("• Prioritizing abilities aligned with the build")
        print("• Displaying parsed build summary for user confirmation")
        
    except Exception as e:
        print(f"✗ Demo failed with error: {e}")
        log_event(f"[DEMO] Demo failed: {e}")


if __name__ == "__main__":
    main() 
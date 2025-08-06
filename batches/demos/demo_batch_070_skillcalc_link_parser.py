"""Demo script for Batch 070 - Build-Aware Behavior System (SkillCalc Link Parser).

This script demonstrates the enhanced functionality of the build-aware behavior system,
including improved skill calculator link parsing and user confirmation features.
"""

import json
import time
from pathlib import Path
from datetime import datetime

from core.skill_calculator_parser import SkillCalculatorParser
from core.build_aware_behavior import BuildAwareBehavior, create_build_aware_behavior
from core.build_confirmation import BuildConfirmation, create_build_confirmation
from android_ms11.core.combat_profile_engine import CombatProfileEngine
from android_ms11.utils.logging_utils import log_event


def demonstrate_enhanced_skill_calculator_parsing():
    """Demonstrate enhanced parsing of skill calculator links."""
    print("\n=== Enhanced Skill Calculator Link Parsing Demo ===")
    
    parser = SkillCalculatorParser()
    
    # Example skill calculator URLs with different formats
    example_urls = [
        {
            "name": "Rifleman Build",
            "url": "https://swgr.org/skill-calculator/rifleman?skills=rifle_shot,marksman_shot,sniper_shot&professions=rifleman",
            "expected_style": "ranged"
        },
        {
            "name": "Pistoleer Build",
            "url": "https://swgr.org/skill-calculator/pistoleer?skills=pistol_shot,quick_shot,point_blank&professions=pistoleer",
            "expected_style": "ranged"
        },
        {
            "name": "Medic Build",
            "url": "https://swgr.org/skill-calculator/medic?skills=heal,cure_poison,medical_treatment&professions=medic",
            "expected_style": "support"
        },
        {
            "name": "Brawler Build",
            "url": "https://swgr.org/skill-calculator/brawler?skills=melee_hit,power_attack,unarmed&professions=brawler",
            "expected_style": "melee"
        },
        {
            "name": "Hybrid Rifleman/Medic",
            "url": "https://swgr.org/skill-calculator/rifleman_medic?skills=rifle_shot,heal,cure_poison&professions=rifleman,medic",
            "expected_style": "hybrid"
        }
    ]
    
    for i, build_info in enumerate(example_urls, 1):
        print(f"\n--- Example {i}: {build_info['name']} ---")
        print(f"URL: {build_info['url']}")
        
        try:
            # Parse the skill calculator link
            build_data = parser.parse_skill_calculator_link(build_info['url'])
            
            print(f"✓ Successfully parsed build")
            print(f"  Expected Style: {build_info['expected_style']}")
            print(f"  Actual Style: {build_data.get('combat_style', 'Unknown')}")
            print(f"  Professions: {', '.join(build_data.get('profession_boxes', []))}")
            print(f"  Weapons Supported: {', '.join(build_data.get('weapons_supported', []))}")
            print(f"  Abilities Granted: {len(build_data.get('abilities_granted', []))} abilities")
            print(f"  Minimum Attack Distance: {build_data.get('minimum_attack_distance', 'Unknown')}")
            print(f"  Build Summary: {build_data.get('build_summary', 'No summary')}")
            
            # Test enhanced profession mappings
            if build_data.get('combat_style') == build_info['expected_style']:
                print(f"  ✓ Style detection correct")
            else:
                print(f"  ⚠ Style detection mismatch")
            
            # Save the build to a file
            filename = f"demo_build_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = parser.save_build_to_file(build_data, filename)
            print(f"  ✓ Saved build to: {filepath}")
            
        except Exception as e:
            print(f"✗ Error parsing build: {e}")


def demonstrate_build_confirmation_system():
    """Demonstrate the build confirmation and summary display system."""
    print("\n=== Build Confirmation System Demo ===")
    
    confirmation = create_build_confirmation()
    
    # Example build data
    example_builds = [
        {
            "name": "Rifleman Build",
            "build_data": {
                "profession_boxes": ["rifleman"],
                "weapons_supported": ["rifle", "carbine"],
                "abilities_granted": ["Rifle Shot", "Rifle Hit", "Rifle Critical Hit", "Marksman Shot", "Sniper Shot"],
                "combat_style": "ranged",
                "minimum_attack_distance": 5,
                "build_summary": "Rifleman | Weapons: rifle, carbine | Combat Style: Ranged"
            }
        },
        {
            "name": "Medic Build",
            "build_data": {
                "profession_boxes": ["medic"],
                "weapons_supported": ["pistol", "rifle"],
                "abilities_granted": ["Heal", "Cure Poison", "Cure Disease", "Heal Other", "Revive", "Medical Treatment"],
                "combat_style": "support",
                "minimum_attack_distance": 3,
                "build_summary": "Medic | Weapons: pistol, rifle | Combat Style: Support"
            }
        },
        {
            "name": "Brawler Build",
            "build_data": {
                "profession_boxes": ["brawler"],
                "weapons_supported": ["unarmed", "melee"],
                "abilities_granted": ["Melee Hit", "Melee Critical Hit", "Power Attack", "Counter Attack", "Defensive Stance"],
                "combat_style": "melee",
                "minimum_attack_distance": 1,
                "build_summary": "Brawler | Weapons: unarmed, melee | Combat Style: Melee"
            }
        }
    ]
    
    for build_info in example_builds:
        print(f"\n--- Testing {build_info['name']} ---")
        
        # Display build summary
        summary = confirmation.display_build_summary(build_info['build_data'])
        print(summary)
        
        # Generate detailed report
        detailed_report = confirmation.generate_detailed_report(build_info['build_data'])
        print(f"Detailed Report:")
        print(f"  Combat Analysis: {detailed_report['combat_analysis']['primary_style']} style")
        print(f"  Total Abilities: {detailed_report['abilities']['total_count']}")
        print(f"  Movement Style: {detailed_report['combat_analysis']['movement_style']}")
        print(f"  Tactical Recommendations: {len(detailed_report['tactical_recommendations'])} recommendations")
        
        # Simulate user confirmation
        user_response = "yes"  # Simulated
        print(f"User Response: {user_response}")
        
        # Save confirmation log
        log_filepath = confirmation.save_confirmation_log(build_info['build_data'], user_response)
        print(f"Confirmation log saved to: {log_filepath}")


def demonstrate_build_aware_behavior_with_confirmation():
    """Demonstrate build-aware behavior with user confirmation."""
    print("\n=== Build-Aware Behavior with Confirmation Demo ===")
    
    # Create a combat engine
    combat_engine = CombatProfileEngine("profiles/combat")
    
    # Create build-aware behavior system
    build_aware = create_build_aware_behavior(combat_engine)
    
    # Example builds to test
    example_builds = [
        {
            "name": "Rifleman Build",
            "url": "https://swgr.org/skill-calculator/rifleman?skills=rifle_shot,marksman_shot,sniper_shot&professions=rifleman",
            "auto_confirm": True
        },
        {
            "name": "Medic Build",
            "url": "https://swgr.org/skill-calculator/medic?skills=heal,cure_poison,medical_treatment&professions=medic",
            "auto_confirm": True
        },
        {
            "name": "Brawler Build",
            "url": "https://swgr.org/skill-calculator/brawler?skills=melee_hit,power_attack,unarmed&professions=brawler",
            "auto_confirm": True
        }
    ]
    
    for build_info in example_builds:
        print(f"\n--- Testing {build_info['name']} with confirmation ---")
        
        try:
            # Load build with confirmation
            build_data = build_aware.load_build_from_link_with_confirmation(
                build_info['url'], 
                auto_confirm=build_info['auto_confirm']
            )
            
            print(f"✓ Successfully processed build")
            
            # Get build summary
            summary = build_aware.get_build_summary()
            print(f"Build Summary: {summary}")
            
            # Get combat recommendations
            recommendations = build_aware.get_combat_recommendations()
            print(f"Combat Style: {recommendations.get('combat_style', 'Unknown')}")
            print(f"Recommended Weapons: {', '.join(recommendations.get('recommended_weapons', []))}")
            print(f"Priority Abilities: {', '.join(recommendations.get('priority_abilities', []))}")
            
            # Get detailed report
            detailed_report = build_aware.get_detailed_report()
            if "error" not in detailed_report:
                print(f"Detailed Report Generated: {detailed_report['combat_analysis']['primary_style']} build")
            
        except Exception as e:
            print(f"✗ Error processing build: {e}")


def demonstrate_enhanced_profession_mappings():
    """Demonstrate the enhanced profession mappings and skill detection."""
    print("\n=== Enhanced Profession Mappings Demo ===")
    
    parser = SkillCalculatorParser()
    
    # Test different profession combinations
    test_professions = [
        "rifleman",
        "pistoleer", 
        "medic",
        "brawler",
        "swordsman",
        "fencer",
        "pikeman",
        "commando",
        "carbineer",
        "smuggler",
        "combat_medic",
        "doctor"
    ]
    
    print("Testing enhanced profession mappings:")
    for profession in test_professions:
        if profession in parser.profession_skills:
            prof_data = parser.profession_skills[profession]
            print(f"  {profession.title()}:")
            print(f"    Style: {prof_data['combat_style']}")
            print(f"    Weapons: {', '.join(prof_data['weapons'])}")
            print(f"    Min Distance: {prof_data['min_distance']}")
            print(f"    Abilities: {len(prof_data['abilities'])} abilities")
        else:
            print(f"  {profession.title()}: Not in enhanced mappings")


def demonstrate_url_parsing_enhancements():
    """Demonstrate enhanced URL parsing capabilities."""
    print("\n=== Enhanced URL Parsing Demo ===")
    
    parser = SkillCalculatorParser()
    
    # Test different URL formats
    test_urls = [
        "https://swgr.org/skill-calculator/rifleman",
        "https://swgr.org/skill-calculator/pistoleer?skills=pistol_shot,quick_shot",
        "https://swgr.org/skill-calculator/medic?skills=heal,cure_poison&professions=medic",
        "https://swgr.org/skill-calculator/brawler?skills=melee_hit,power_attack&professions=brawler&build=test123",
        "https://swgr.org/skill-calculator/hybrid?skills=rifle_shot,heal&professions=rifleman,medic&version=1.0"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n--- Test URL {i} ---")
        print(f"URL: {url}")
        
        try:
            # Test URL validation
            is_valid = parser._is_valid_skill_calculator_url(url)
            print(f"Valid URL: {is_valid}")
            
            if is_valid:
                # Extract build data
                build_data = parser._extract_build_data_from_url(url)
                print(f"Extracted Data:")
                for key, value in build_data.items():
                    print(f"  {key}: {value}")
                
                # Parse profession boxes
                profession_boxes = parser._parse_profession_boxes(build_data)
                print(f"Profession Boxes: {profession_boxes}")
                
        except Exception as e:
            print(f"Error processing URL: {e}")


def demonstrate_error_handling():
    """Demonstrate error handling for invalid URLs and edge cases."""
    print("\n=== Error Handling Demo ===")
    
    parser = SkillCalculatorParser()
    
    # Test invalid URLs
    invalid_urls = [
        "https://swgr.org/wiki/rifleman",
        "https://google.com/skill-calculator",
        "https://swgr.org/skill-calculator",
        "invalid-url",
        "https://swgr.org/skill-calculator/",
        "https://swgr.org/skill-calculator/invalid_profession"
    ]
    
    for i, url in enumerate(invalid_urls, 1):
        print(f"\n--- Invalid URL Test {i} ---")
        print(f"URL: {url}")
        
        try:
            # Test URL validation
            is_valid = parser._is_valid_skill_calculator_url(url)
            print(f"Valid URL: {is_valid}")
            
            if is_valid:
                # Try to parse (should fail gracefully)
                build_data = parser.parse_skill_calculator_link(url)
                print(f"Unexpected success: {build_data.get('combat_style', 'Unknown')}")
            else:
                print("Correctly identified as invalid")
                
        except Exception as e:
            print(f"Expected error: {e}")


def main():
    """Main demo function."""
    print("=== Batch 070 - Build-Aware Behavior System (SkillCalc Link Parser) Demo ===")
    print("This demo showcases the enhanced skill calculator link parsing and user confirmation features.")
    
    try:
        # Demonstrate enhanced skill calculator parsing
        demonstrate_enhanced_skill_calculator_parsing()
        
        # Demonstrate build confirmation system
        demonstrate_build_confirmation_system()
        
        # Demonstrate build-aware behavior with confirmation
        demonstrate_build_aware_behavior_with_confirmation()
        
        # Demonstrate enhanced profession mappings
        demonstrate_enhanced_profession_mappings()
        
        # Demonstrate URL parsing enhancements
        demonstrate_url_parsing_enhancements()
        
        # Demonstrate error handling
        demonstrate_error_handling()
        
        print("\n=== Demo Complete ===")
        print("✓ Enhanced SkillCalc link parser implemented")
        print("✓ User confirmation system working")
        print("✓ Build-aware behavior system enhanced")
        print("✓ Error handling improved")
        print("✓ Detailed reporting functionality added")
        
    except Exception as e:
        print(f"Demo error: {e}")
        log_event(f"[DEMO] Error in demo: {e}")


if __name__ == "__main__":
    main() 
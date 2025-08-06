#!/usr/bin/env python3
"""
Demo script for Batch 041 - Skill Calculator Integration Module

This demo showcases the SWGR skill calculator integration that allows users
to import their SWGR skill build and auto-configure combat logic for MS11.

Features demonstrated:
- SWGR skill calculator URL parsing
- Skill tree data extraction
- Profession analysis and role determination
- Combat profile generation
- Character configuration updates
- Profile management and validation
"""

import logging
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.combat_profile import (
    SkillCalculator,
    parse_swgr_url,
    generate_combat_profile,
    ProfessionAnalyzer,
    analyze_professions,
    determine_role,
    CombatGenerator,
    generate_combat_config,
    SkillCalculatorIntegration,
    import_swgr_build,
    analyze_skill_tree,
    validate_swgr_url,
    get_available_profiles,
    get_integration
)


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('demo_batch_041_skill_calculator.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def demo_skill_calculator_parsing():
    """Demo SWGR skill calculator URL parsing."""
    print("\n" + "="*60)
    print("🎯 DEMO: SWGR Skill Calculator URL Parsing")
    print("="*60)
    
    # Sample SWGR URLs (these would be real URLs in practice)
    sample_urls = [
        "https://swgr.org/skill-calculator/abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567",
        "https://swgr.org/skill-calculator/?build=xyz789abc123def456ghi789jkl012",
        "https://swgr.org/skill-calculator/#build_hash_123456789"
    ]
    
    calculator = SkillCalculator()
    
    for i, url in enumerate(sample_urls, 1):
        print(f"\n📋 Testing URL {i}: {url}")
        
        # Extract build hash
        build_hash = calculator._extract_build_hash(url)
        if build_hash:
            print(f"✅ Build hash extracted: {build_hash}")
        else:
            print("❌ Could not extract build hash")
        
        # Validate URL
        is_valid = validate_swgr_url(url)
        print(f"🔍 URL validation: {'✅ Valid' if is_valid else '❌ Invalid'}")


def demo_profession_analysis():
    """Demo profession analysis and role determination."""
    print("\n" + "="*60)
    print("🎯 DEMO: Profession Analysis and Role Determination")
    print("="*60)
    
    # Sample profession data
    sample_professions = {
        "Medic": {
            "points": 250,
            "skills": {
                "healing": {"level": 4, "points": 40},
                "medical": {"level": 3, "points": 30},
                "medical_combat": {"level": 2, "points": 20}
            }
        },
        "Marksman": {
            "points": 180,
            "skills": {
                "pistol_combat": {"level": 4, "points": 40},
                "rifle_combat": {"level": 3, "points": 30},
                "marksman_combat": {"level": 2, "points": 20}
            }
        },
        "Scout": {
            "points": 120,
            "skills": {
                "scout_combat": {"level": 2, "points": 20},
                "ranged_combat": {"level": 2, "points": 20}
            }
        }
    }
    
    analyzer = ProfessionAnalyzer()
    
    # Analyze professions
    print("\n📊 Analyzing professions...")
    profession_analysis = analyzer.analyze_professions(sample_professions)
    
    for profession_name, analysis in profession_analysis.items():
        print(f"\n🏥 {profession_name}:")
        print(f"   Points: {analysis.points}")
        print(f"   Primary skills: {analysis.primary_skills}")
        print(f"   Secondary skills: {analysis.secondary_skills}")
        print(f"   Combat capabilities: {analysis.combat_capabilities}")
        print(f"   Support capabilities: {analysis.support_capabilities}")
        print(f"   Role indicators: {analysis.role_indicators}")
    
    # Determine role
    print("\n🎭 Determining character role...")
    role_analysis = analyzer.determine_role(profession_analysis)
    
    print(f"\n🎯 Role Analysis Results:")
    print(f"   Primary role: {role_analysis.primary_role.value}")
    print(f"   Secondary roles: {[role.value for role in role_analysis.secondary_roles]}")
    print(f"   Primary profession: {role_analysis.primary_profession}")
    print(f"   Secondary professions: {role_analysis.secondary_professions}")
    print(f"   Combat abilities: {role_analysis.combat_abilities}")
    print(f"   Support abilities: {role_analysis.support_abilities}")
    print(f"   Weapon preferences: {role_analysis.weapon_preferences}")
    print(f"   Combat distance: {role_analysis.combat_distance}")
    print(f"   Support capacity: {role_analysis.support_capacity}")


def demo_combat_profile_generation():
    """Demo combat profile generation."""
    print("\n" + "="*60)
    print("🎯 DEMO: Combat Profile Generation")
    print("="*60)
    
    # Create sample skill tree
    from modules.combat_profile.skill_calculator import SkillTree
    
    sample_skill_tree = SkillTree(
        professions={
            "Medic": {
                "points": 250,
                "skills": {
                    "healing": {"level": 4, "points": 40},
                    "medical": {"level": 3, "points": 30},
                    "medical_combat": {"level": 2, "points": 20}
                },
                "key": "medic"
            },
            "Marksman": {
                "points": 180,
                "skills": {
                    "pistol_combat": {"level": 4, "points": 40},
                    "rifle_combat": {"level": 3, "points": 30}
                },
                "key": "marksman"
            }
        },
        total_points=430,
        character_level=80,
        build_hash="sample_build_123",
        url="https://swgr.org/skill-calculator/sample"
    )
    
    generator = CombatGenerator()
    
    # Generate combat configuration
    print("\n⚔️ Generating combat configuration...")
    
    # Analyze professions first
    analyzer = ProfessionAnalyzer()
    profession_analysis = analyzer.analyze_professions(sample_skill_tree.professions)
    role_analysis = analyzer.determine_role(profession_analysis)
    
    # Generate combat config
    combat_config = generator.generate_combat_config(sample_skill_tree, profession_analysis, role_analysis)
    
    print(f"\n🎯 Combat Configuration Generated:")
    print(f"   Role: {combat_config.get('role', 'Unknown')}")
    print(f"   Primary profession: {combat_config.get('primary_profession', 'Unknown')}")
    print(f"   Combat distance: {combat_config.get('combat_distance', 'Unknown')}")
    print(f"   Support capacity: {combat_config.get('support_capacity', 'Unknown')}")
    print(f"   Combat style: {combat_config.get('combat_style', 'Unknown')}")
    print(f"   Target priority: {combat_config.get('target_priority', 'Unknown')}")
    print(f"   Retreat threshold: {combat_config.get('retreat_threshold', 'Unknown')}")
    print(f"   Support threshold: {combat_config.get('support_threshold', 'Unknown')}")
    print(f"   Ability rotation: {combat_config.get('ability_rotation', 'Unknown')}")
    
    # Show weapon configuration
    weapon_config = combat_config.get('weapon_config', {})
    if weapon_config:
        print(f"\n🔫 Weapon Configuration:")
        for weapon, settings in weapon_config.items():
            if isinstance(settings, dict):
                print(f"   {weapon}: {settings}")
    
    # Show ability configuration
    ability_config = combat_config.get('ability_config', {})
    if ability_config:
        print(f"\n⚡ Ability Configuration:")
        print(f"   Primary abilities: {ability_config.get('primary_abilities', [])}")
        print(f"   Secondary abilities: {ability_config.get('secondary_abilities', [])}")
        print(f"   Special abilities: {ability_config.get('special_abilities', [])}")


def demo_integration_workflow():
    """Demo complete integration workflow."""
    print("\n" + "="*60)
    print("🎯 DEMO: Complete Integration Workflow")
    print("="*60)
    
    integration = get_integration()
    
    # Sample SWGR URL (in practice, this would be a real URL)
    sample_url = "https://swgr.org/skill-calculator/sample_build_123"
    character_name = "DemoCharacter"
    
    print(f"\n📥 Importing SWGR build for {character_name}...")
    print(f"   URL: {sample_url}")
    
    # Import SWGR build
    combat_profile = integration.import_swgr_build(sample_url, character_name)
    
    if combat_profile:
        print(f"\n✅ Successfully imported SWGR build!")
        print(f"   Character level: {combat_profile.get('character_level', 'Unknown')}")
        print(f"   Total points: {combat_profile.get('total_points', 'Unknown')}")
        print(f"   Role: {combat_profile.get('role', 'Unknown')}")
        print(f"   Primary profession: {combat_profile.get('primary_profession', 'Unknown')}")
        
        # Show available profiles
        available_profiles = integration.get_available_profiles()
        print(f"\n📁 Available combat profiles: {available_profiles}")
        
        # Load and display a profile
        if available_profiles:
            profile_name = available_profiles[0]
            loaded_profile = integration.load_combat_profile(profile_name)
            if loaded_profile:
                print(f"\n📋 Loaded profile '{profile_name}':")
                print(f"   Role: {loaded_profile.get('role', 'Unknown')}")
                print(f"   Combat distance: {loaded_profile.get('combat_distance', 'Unknown')}")
                print(f"   Support capacity: {loaded_profile.get('support_capacity', 'Unknown')}")
    else:
        print("❌ Failed to import SWGR build")


def demo_skill_tree_analysis():
    """Demo detailed skill tree analysis."""
    print("\n" + "="*60)
    print("🎯 DEMO: Detailed Skill Tree Analysis")
    print("="*60)
    
    # Create sample skill tree
    from modules.combat_profile.skill_calculator import SkillTree
    
    sample_skill_tree = SkillTree(
        professions={
            "Jedi": {
                "points": 300,
                "skills": {
                    "lightsaber_combat": {"level": 4, "points": 40},
                    "force_combat": {"level": 3, "points": 30},
                    "force_healing": {"level": 2, "points": 20}
                },
                "key": "jedi"
            },
            "Medic": {
                "points": 200,
                "skills": {
                    "healing": {"level": 3, "points": 30},
                    "medical": {"level": 2, "points": 20}
                },
                "key": "medic"
            }
        },
        total_points=500,
        character_level=80,
        build_hash="jedi_medic_build_456",
        url="https://swgr.org/skill-calculator/jedi_medic"
    )
    
    print("\n🔍 Performing detailed skill tree analysis...")
    analysis = analyze_skill_tree(sample_skill_tree)
    
    if analysis:
        print(f"\n📊 Analysis Results:")
        
        # Skill tree info
        skill_tree_info = analysis.get('skill_tree', {})
        print(f"   Character level: {skill_tree_info.get('character_level', 'Unknown')}")
        print(f"   Total points: {skill_tree_info.get('total_points', 'Unknown')}")
        print(f"   Professions: {list(skill_tree_info.get('professions', {}).keys())}")
        
        # Role analysis
        role_analysis = analysis.get('role_analysis', {})
        print(f"\n🎭 Role Analysis:")
        print(f"   Primary role: {role_analysis.get('primary_role', 'Unknown')}")
        print(f"   Secondary roles: {role_analysis.get('secondary_roles', [])}")
        print(f"   Primary profession: {role_analysis.get('primary_profession', 'Unknown')}")
        print(f"   Combat abilities: {role_analysis.get('combat_abilities', [])}")
        print(f"   Support abilities: {role_analysis.get('support_abilities', [])}")
        print(f"   Weapon preferences: {role_analysis.get('weapon_preferences', [])}")
        print(f"   Combat distance: {role_analysis.get('combat_distance', 'Unknown')}")
        print(f"   Support capacity: {role_analysis.get('support_capacity', 'Unknown')}")
        
        # Combat config
        combat_config = analysis.get('combat_config', {})
        if combat_config:
            print(f"\n⚔️ Combat Configuration:")
            print(f"   Combat style: {combat_config.get('combat_style', 'Unknown')}")
            print(f"   Target priority: {combat_config.get('target_priority', 'Unknown')}")
            print(f"   Ability rotation: {combat_config.get('ability_rotation', 'Unknown')}")


def demo_profile_management():
    """Demo combat profile management."""
    print("\n" + "="*60)
    print("🎯 DEMO: Combat Profile Management")
    print("="*60)
    
    integration = get_integration()
    
    # Sample combat profile
    sample_profile = {
        "role": "healer",
        "primary_profession": "Medic",
        "combat_distance": "medium",
        "support_capacity": "high",
        "weapon_preferences": ["pistol", "rifle"],
        "combat_abilities": ["healing", "medical"],
        "support_abilities": ["healing", "medical"],
        "combat_style": "defensive",
        "target_priority": "ally_lowest_health",
        "retreat_threshold": 0.5,
        "support_threshold": 0.2,
        "ability_rotation": "healing_focused"
    }
    
    profile_name = "demo_medic_profile"
    
    print(f"\n💾 Saving combat profile: {profile_name}")
    success = integration.save_combat_profile(sample_profile, profile_name)
    
    if success:
        print("✅ Profile saved successfully!")
        
        # Load the profile
        print(f"\n📂 Loading combat profile: {profile_name}")
        loaded_profile = integration.load_combat_profile(profile_name)
        
        if loaded_profile:
            print("✅ Profile loaded successfully!")
            print(f"   Role: {loaded_profile.get('role', 'Unknown')}")
            print(f"   Primary profession: {loaded_profile.get('primary_profession', 'Unknown')}")
            print(f"   Combat distance: {loaded_profile.get('combat_distance', 'Unknown')}")
            print(f"   Support capacity: {loaded_profile.get('support_capacity', 'Unknown')}")
        else:
            print("❌ Failed to load profile")
    else:
        print("❌ Failed to save profile")
    
    # Show available profiles
    available_profiles = integration.get_available_profiles()
    print(f"\n📁 Available profiles: {available_profiles}")


def demo_character_config_integration():
    """Demo character configuration integration."""
    print("\n" + "="*60)
    print("🎯 DEMO: Character Configuration Integration")
    print("="*60)
    
    integration = get_integration()
    
    # Sample combat profile
    sample_profile = {
        "role": "dps",
        "primary_profession": "Marksman",
        "combat_distance": "long",
        "support_capacity": "low",
        "weapon_preferences": ["rifle", "pistol"],
        "combat_abilities": ["pistol_combat", "rifle_combat"],
        "support_abilities": []
    }
    
    character_name = "DemoMarksman"
    
    print(f"\n⚙️ Updating character configuration for {character_name}...")
    success = integration.generate_character_config(sample_profile, character_name)
    
    if success:
        print("✅ Character configuration updated successfully!")
        print(f"   Character: {character_name}")
        print(f"   Role: {sample_profile.get('role', 'Unknown')}")
        print(f"   Primary profession: {sample_profile.get('primary_profession', 'Unknown')}")
        print(f"   Combat distance: {sample_profile.get('combat_distance', 'Unknown')}")
        print(f"   Support capacity: {sample_profile.get('support_capacity', 'Unknown')}")
        print(f"   Weapon preferences: {sample_profile.get('weapon_preferences', [])}")
    else:
        print("❌ Failed to update character configuration")


def main():
    """Main demo function."""
    print("🎯 Batch 041 - Skill Calculator Integration Module Demo")
    print("="*60)
    print("This demo showcases the SWGR skill calculator integration")
    print("that allows users to import their SWGR skill build and")
    print("auto-configure combat logic for MS11.")
    print("="*60)
    
    # Setup logging
    setup_logging()
    
    try:
        # Run demos
        demo_skill_calculator_parsing()
        time.sleep(1)
        
        demo_profession_analysis()
        time.sleep(1)
        
        demo_combat_profile_generation()
        time.sleep(1)
        
        demo_integration_workflow()
        time.sleep(1)
        
        demo_skill_tree_analysis()
        time.sleep(1)
        
        demo_profile_management()
        time.sleep(1)
        
        demo_character_config_integration()
        
        print("\n" + "="*60)
        print("✅ Batch 041 Demo Completed Successfully!")
        print("="*60)
        print("The skill calculator integration module is now ready")
        print("for production use. Users can import their SWGR skill")
        print("builds and automatically configure combat logic for MS11.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logging.error(f"Demo failed: {e}", exc_info=True)


if __name__ == "__main__":
    main() 
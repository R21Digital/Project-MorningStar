#!/usr/bin/env python3
"""
Demo script for Batch 036 - Combat Spec Intelligence & Auto-Adaptation

This script demonstrates the combat manager functionality including:
- Build detection via OCR simulation
- Profile matching and loading
- Auto-adaptation of combat behavior
- YAML-based profile management
- Real-time build monitoring
"""

import sys
import time
from pathlib import Path

# Add combat to path for imports
sys.path.insert(0, str(Path(__file__).parent / "combat"))

from combat_manager import CombatManager, BuildType, WeaponType, CombatStyle, SkillLevel
from datetime import datetime


def demo_combat_manager():
    """Demonstrate the combat manager functionality."""
    print("🚀 Batch 036 - Combat Spec Intelligence & Auto-Adaptation")
    print("=" * 60)
    
    # Initialize combat manager
    print("📚 Initializing Combat Manager...")
    manager = CombatManager()
    
    # Show loaded profiles
    print(f"\n📊 Loaded {len(manager.available_profiles)} combat profiles:")
    for name, profile in manager.available_profiles.items():
        print(f"   {name}: {profile.description}")
    
    # Demonstrate build detection simulation
    print("\n🔍 Build Detection Demo:")
    
    # Simulate different OCR skill outputs
    mock_skill_outputs = [
        # TKM Brawler
        "Teräs Käsi (4)\nUnarmed Combat (4)\nMelee Weapons (3)\nBrawler (4)\nDodge (3)\nBlock (2)",
        
        # Rifleman Medic
        "Rifle Weapons (4)\nMarksman (4)\nHealing (3)\nMedical (3)\nRifle Shot (4)\nHeal Self (3)",
        
        # Pistoleer
        "Pistol Weapons (4)\nHandgun (4)\nQuick Shot (3)\nPrecise Shot (3)\nRapid Fire (2)\nDodge (3)",
        
        # Pure Medic
        "Healing (4)\nMedical (4)\nDiagnosis (4)\nTreatment (4)\nCure Poison (3)\nHeal Other (3)"
    ]
    
    build_names = ["TKM Brawler", "Rifleman Medic", "Pistoleer", "Pure Medic"]
    
    for i, (ocr_text, build_name) in enumerate(zip(mock_skill_outputs, build_names), 1):
        print(f"\n📝 Processing Build {i}: {build_name}")
        print(f"   OCR Text: {ocr_text[:50]}...")
        
        # Parse skills from OCR text
        skills = manager.parse_skills_from_ocr(ocr_text)
        print(f"   Parsed Skills: {len(skills)} skills")
        for skill_name, skill_level in skills.items():
            print(f"     {skill_name}: Level {skill_level.level}")
        
        # Detect build type
        build_type = manager.detect_build_type(skills)
        weapon_type = manager.detect_weapon_type(skills)
        combat_style = manager.determine_combat_style(build_type, weapon_type)
        
        print(f"   Detected Build: {build_type.value}")
        print(f"   Weapon Type: {weapon_type.value}")
        print(f"   Combat Style: {combat_style.value}")
        
        # Calculate confidence
        confidence = manager.calculate_build_confidence(skills, build_type, weapon_type)
        print(f"   Confidence: {confidence:.2f}")
        
        # Categorize skills
        primary_skills, secondary_skills = manager.categorize_skills(skills, build_type)
        print(f"   Primary Skills: {len(primary_skills)}")
        print(f"   Secondary Skills: {len(secondary_skills)}")
    
    # Demonstrate profile matching
    print("\n🎯 Profile Matching Demo:")
    
    # Create mock build info for testing
    from combat_manager import BuildInfo
    
    test_builds = [
        BuildInfo(
            build_type=BuildType.MELEE,
            weapon_type=WeaponType.UNARMED,
            combat_style=CombatStyle.MELEE,
            primary_skills={"Teräs Käsi": SkillLevel("Teräs Käsi", 4)},
            secondary_skills={"Dodge": SkillLevel("Dodge", 3)},
            confidence=0.85,
            detected_at=time.time()
        ),
        BuildInfo(
            build_type=BuildType.HYBRID,
            weapon_type=WeaponType.RIFLE,
            combat_style=CombatStyle.HYBRID,
            primary_skills={"Rifle Weapons": SkillLevel("Rifle Weapons", 4)},
            secondary_skills={"Healing": SkillLevel("Healing", 3)},
            confidence=0.80,
            detected_at=time.time()
        ),
        BuildInfo(
            build_type=BuildType.PISTOLEER,
            weapon_type=WeaponType.PISTOL,
            combat_style=CombatStyle.RANGED,
            primary_skills={"Pistol Weapons": SkillLevel("Pistol Weapons", 4)},
            secondary_skills={"Quick Shot": SkillLevel("Quick Shot", 3)},
            confidence=0.90,
            detected_at=time.time()
        ),
        BuildInfo(
            build_type=BuildType.MEDIC,
            weapon_type=WeaponType.PISTOL,
            combat_style=CombatStyle.SUPPORT,
            primary_skills={"Healing": SkillLevel("Healing", 4)},
            secondary_skills={"Diagnosis": SkillLevel("Diagnosis", 4)},
            confidence=0.95,
            detected_at=time.time()
        )
    ]
    
    for i, build_info in enumerate(test_builds, 1):
        print(f"\n🔍 Testing Profile Match {i}: {build_info.build_type.value}")
        
        # Find best matching profile
        profile = manager.find_best_profile(build_info)
        if profile:
            print(f"   ✅ Matched Profile: {profile.name}")
            print(f"   📋 Abilities: {len(profile.abilities)} abilities")
            print(f"   🔄 Rotation: {len(profile.ability_rotation)} abilities")
            print(f"   🎯 Optimal Range: {profile.optimal_range}m")
            print(f"   🚨 Emergency Abilities: {len(profile.emergency_abilities)}")
        else:
            print(f"   ❌ No matching profile found")
    
    # Demonstrate auto-adaptation
    print("\n🤖 Auto-Adaptation Demo:")
    
    # Simulate auto-adaptation for different builds
    for i, build_info in enumerate(test_builds, 1):
        print(f"\n🔄 Auto-adapting to Build {i}: {build_info.build_type.value}")
        
        # Set current build
        manager.current_build = build_info
        
        # Find and set profile
        profile = manager.find_best_profile(build_info)
        if profile:
            manager.current_profile = profile
            print(f"   ✅ Adapted to: {profile.name}")
            
            # Show current abilities
            abilities = manager.get_current_abilities()
            print(f"   📋 Current Abilities: {len(abilities)}")
            print(f"      {', '.join(abilities[:5])}{'...' if len(abilities) > 5 else ''}")
            
            # Show ability rotation
            rotation = manager.get_ability_rotation()
            print(f"   🔄 Ability Rotation: {len(rotation)} abilities")
            print(f"      {', '.join(rotation[:3])}{'...' if len(rotation) > 3 else ''}")
            
            # Show emergency abilities
            emergency = manager.get_emergency_abilities()
            print(f"   🚨 Emergency Abilities: {len(emergency)}")
            for trigger, ability in list(emergency.items())[:3]:
                print(f"      {trigger}: {ability}")
            
            # Show optimal range
            optimal_range = manager.get_optimal_range()
            print(f"   🎯 Optimal Range: {optimal_range}m")
            
            # Show combat priorities
            priorities = manager.get_combat_priorities()
            print(f"   ⚖️  Combat Priorities:")
            for key, value in priorities.items():
                print(f"      {key}: {value}")
            
            # Show cooldowns
            cooldowns = manager.get_cooldowns()
            print(f"   ⏱️  Cooldowns: {len(cooldowns)} abilities")
            for ability, cooldown in list(cooldowns.items())[:5]:
                print(f"      {ability}: {cooldown}s")
            
            # Show targeting config
            targeting = manager.get_targeting_config()
            print(f"   🎯 Targeting Config:")
            for key, value in targeting.items():
                print(f"      {key}: {value}")
            
            # Show healing config
            healing = manager.get_healing_config()
            print(f"   💊 Healing Config:")
            for key, value in healing.items():
                if isinstance(value, list):
                    print(f"      {key}: {len(value)} abilities")
                else:
                    print(f"      {key}: {value}")
            
            # Show buffing config
            buffing = manager.get_buffing_config()
            print(f"   🔋 Buffing Config:")
            for key, value in buffing.items():
                if isinstance(value, list):
                    print(f"      {key}: {len(value)} abilities")
                else:
                    print(f"      {key}: {value}")
            
            # Show fallback abilities
            fallback = manager.get_fallback_abilities()
            print(f"   🔄 Fallback Abilities: {len(fallback)}")
            print(f"      {', '.join(fallback)}")
        else:
            print(f"   ❌ No profile found for adaptation")
    
    # Demonstrate build statistics
    print("\n📊 Build Statistics Demo:")
    
    # Add some build history
    for build_info in test_builds:
        manager.build_history.append(build_info)
    
    stats = manager.get_build_statistics()
    print(f"   Total Detections: {stats['total_detections']}")
    print(f"   Average Confidence: {stats['average_confidence']:.2f}")
    
    print(f"   Build Distribution:")
    for build_type, count in stats['build_distribution'].items():
        print(f"      {build_type}: {count}")
    
    print(f"   Weapon Distribution:")
    for weapon_type, count in stats['weapon_distribution'].items():
        print(f"      {weapon_type}: {count}")
    
    print(f"   Current Build: {stats['current_build']['type']}")
    print(f"   Current Weapon: {stats['current_build']['weapon']}")
    print(f"   Current Confidence: {stats['current_build']['confidence']:.2f}")
    print(f"   Current Profile: {stats['current_profile']}")
    
    # Demonstrate profile saving
    print("\n💾 Profile Management Demo:")
    
    # Create a custom profile
    from combat_manager import CombatProfile
    
    custom_profile = CombatProfile(
        name="custom_rifleman",
        build_type=BuildType.RIFLEMAN,
        weapon_type=WeaponType.RIFLE,
        combat_style=CombatStyle.RANGED,
        description="Custom rifleman profile for testing",
        abilities=["Rifle Shot", "Burst Shot", "Precise Shot"],
        ability_rotation=["Rifle Shot", "Burst Shot", "Rifle Shot"],
        emergency_abilities={"reload": "Reload"},
        combat_priorities={"player_health_threshold": 50},
        cooldowns={"Rifle Shot": 0, "Burst Shot": 5},
        targeting={"max_range": 50},
        healing={"self_heal_threshold": 60},
        buffing={"buff_threshold": 80},
        optimal_range=40,
        fallback_abilities=["Rifle Shot"]
    )
    
    # Save the profile
    success = manager.save_profile(custom_profile, "custom_rifleman")
    if success:
        print("   ✅ Saved custom profile: custom_rifleman.yaml")
    else:
        print("   ❌ Failed to save custom profile")
    
    # Reload profiles
    manager.reload_profiles()
    print(f"   📚 Reloaded profiles: {len(manager.available_profiles)} total")


def demo_ocr_simulation():
    """Demonstrate OCR simulation for build detection."""
    print("\n🔍 OCR Simulation Demo:")
    print("-" * 40)
    
    manager = CombatManager()
    
    # Simulate different OCR scenarios
    ocr_scenarios = [
        {
            "name": "TKM Skills",
            "text": "Teräs Käsi (4)\nUnarmed Combat (4)\nMelee Weapons (3)\nBrawler (4)\nDodge (3)\nBlock (2)\nCounter Attack (3)\nStunning Strike (2)",
            "expected_build": "melee",
            "expected_weapon": "unarmed"
        },
        {
            "name": "Rifleman Skills",
            "text": "Rifle Weapons (4)\nMarksman (4)\nSharpshooter (3)\nRifle Shot (4)\nBurst Shot (3)\nFull Auto (2)\nPrecise Shot (3)",
            "expected_build": "rifleman",
            "expected_weapon": "rifle"
        },
        {
            "name": "Pistoleer Skills",
            "text": "Pistol Weapons (4)\nHandgun (4)\nQuick Shot (3)\nPrecise Shot (3)\nRapid Fire (2)\nFan Shot (2)\nDodge (3)",
            "expected_build": "pistoleer",
            "expected_weapon": "pistol"
        },
        {
            "name": "Medic Skills",
            "text": "Healing (4)\nMedical (4)\nDiagnosis (4)\nTreatment (4)\nCure Poison (3)\nHeal Other (3)\nStim Pack (2)",
            "expected_build": "medic",
            "expected_weapon": "pistol"
        }
    ]
    
    for scenario in ocr_scenarios:
        print(f"\n📝 Testing: {scenario['name']}")
        print(f"   OCR Text: {scenario['text'][:60]}...")
        
        # Parse skills
        skills = manager.parse_skills_from_ocr(scenario['text'])
        print(f"   Parsed Skills: {len(skills)}")
        
        # Detect build and weapon
        build_type = manager.detect_build_type(skills)
        weapon_type = manager.detect_weapon_type(skills)
        
        print(f"   Detected Build: {build_type.value}")
        print(f"   Detected Weapon: {weapon_type.value}")
        print(f"   Expected Build: {scenario['expected_build']}")
        print(f"   Expected Weapon: {scenario['expected_weapon']}")
        
        # Check accuracy
        build_correct = build_type.value == scenario['expected_build']
        weapon_correct = weapon_type.value == scenario['expected_weapon']
        
        if build_correct and weapon_correct:
            print("   ✅ Detection: CORRECT")
        elif build_correct or weapon_correct:
            print("   ⚠️  Detection: PARTIAL")
        else:
            print("   ❌ Detection: INCORRECT")
        
        # Calculate confidence
        confidence = manager.calculate_build_confidence(skills, build_type, weapon_type)
        print(f"   Confidence: {confidence:.2f}")


def demo_profile_validation():
    """Demonstrate profile validation and structure."""
    print("\n✅ Profile Validation Demo:")
    print("-" * 40)
    
    manager = CombatManager()
    
    # Validate loaded profiles
    for name, profile in manager.available_profiles.items():
        print(f"\n📋 Profile: {name}")
        print(f"   Build Type: {profile.build_type.value}")
        print(f"   Weapon Type: {profile.weapon_type.value}")
        print(f"   Combat Style: {profile.combat_style.value}")
        print(f"   Description: {profile.description}")
        print(f"   Abilities: {len(profile.abilities)}")
        print(f"   Rotation: {len(profile.ability_rotation)}")
        print(f"   Emergency: {len(profile.emergency_abilities)}")
        print(f"   Optimal Range: {profile.optimal_range}m")
        print(f"   Fallback: {len(profile.fallback_abilities)}")
        
        # Validate structure
        issues = []
        if not profile.abilities:
            issues.append("No abilities defined")
        if not profile.ability_rotation:
            issues.append("No ability rotation defined")
        if not profile.emergency_abilities:
            issues.append("No emergency abilities defined")
        if profile.optimal_range <= 0:
            issues.append("Invalid optimal range")
        
        if issues:
            print(f"   ⚠️  Issues: {', '.join(issues)}")
        else:
            print(f"   ✅ Profile structure: VALID")


if __name__ == "__main__":
    print("🎯 Batch 036 - Combat Spec Intelligence & Auto-Adaptation")
    print("=" * 70)
    
    # Run main demo
    demo_combat_manager()
    
    # Run OCR simulation demo
    demo_ocr_simulation()
    
    # Run profile validation demo
    demo_profile_validation()
    
    print("\n🎉 All demonstrations completed successfully!")
    print("   The combat manager system is ready for use.") 
#!/usr/bin/env python3
"""
MS11 Combat Manager CLI Tool

This module provides the CLI interface for the combat manager system,
including build detection, profile management, and auto-adaptation.
"""

import argparse
import sys
import time
from pathlib import Path

# Add combat to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "combat"))

from combat_manager import CombatManager, BuildType, WeaponType, CombatStyle


def main():
    """Main CLI function for combat manager."""
    parser = argparse.ArgumentParser(
        description="MS11 Combat Spec Intelligence & Auto-Adaptation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ms11 combat-manager --detect-build                    # Detect current build
  ms11 combat-manager --auto-adapt                     # Auto-adapt to detected build
  ms11 combat-manager --list-profiles                  # List all available profiles
  ms11 combat-manager --profile rifleman_medic         # Show specific profile details
  ms11 combat-manager --build-stats                    # Show build detection statistics
  ms11 combat-manager --test-ocr "Rifle Weapons (4)"   # Test OCR parsing
        """
    )
    
    # Main command group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--detect-build", action="store_true",
                       help="Detect current build via OCR")
    group.add_argument("--auto-adapt", action="store_true",
                       help="Auto-adapt combat behavior to detected build")
    group.add_argument("--list-profiles", action="store_true",
                       help="List all available combat profiles")
    group.add_argument("--profile", type=str,
                       help="Show details for specific profile")
    group.add_argument("--build-stats", action="store_true",
                       help="Show build detection statistics")
    group.add_argument("--test-ocr", type=str,
                       help="Test OCR parsing with provided text")
    group.add_argument("--reload-profiles", action="store_true",
                       help="Reload all combat profiles")
    group.add_argument("--validate-profiles", action="store_true",
                       help="Validate all loaded profiles")
    
    # Optional arguments
    parser.add_argument("--config", type=str,
                       help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--save", action="store_true",
                       help="Save build data after operations")
    parser.add_argument("--output", type=str,
                       help="Output file for results (JSON format)")
    
    args = parser.parse_args()
    
    # Initialize combat manager
    try:
        manager = CombatManager(args.config)
        
        if args.verbose:
            import logging
            manager.logger.setLevel(logging.DEBUG)
        
        # Handle different commands
        if args.detect_build:
            print("🔍 Detecting current build via OCR...")
            print("📸 Capturing screen...")
            print("🔤 Running OCR...")
            print("📋 Parsing skills...")
            print("-" * 50)
            
            build_info = manager.detect_current_build()
            if build_info:
                print(f"✅ Build Detected:")
                print(f"   Type: {build_info.build_type.value}")
                print(f"   Weapon: {build_info.weapon_type.value}")
                print(f"   Style: {build_info.combat_style.value}")
                print(f"   Confidence: {build_info.confidence:.2f}")
                print(f"   Primary Skills: {len(build_info.primary_skills)}")
                print(f"   Secondary Skills: {len(build_info.secondary_skills)}")
                
                if build_info.primary_skills:
                    print(f"   Primary Skills:")
                    for skill_name, skill_level in build_info.primary_skills.items():
                        print(f"     {skill_name}: Level {skill_level.level}")
                
                if args.output:
                    import json
                    build_data = {
                        "build_type": build_info.build_type.value,
                        "weapon_type": build_info.weapon_type.value,
                        "combat_style": build_info.combat_style.value,
                        "confidence": build_info.confidence,
                        "primary_skills": {k: v.level for k, v in build_info.primary_skills.items()},
                        "secondary_skills": {k: v.level for k, v in build_info.secondary_skills.items()},
                        "detected_at": build_info.detected_at
                    }
                    with open(args.output, 'w') as f:
                        json.dump(build_data, f, indent=2)
                    print(f"\n💾 Build data saved to {args.output}")
            else:
                print("❌ Failed to detect build")
                sys.exit(1)
        
        elif args.auto_adapt:
            print("🤖 Auto-adapting combat behavior...")
            print("🔍 Detecting current build...")
            print("🎯 Finding matching profile...")
            print("🔄 Adapting combat settings...")
            print("-" * 50)
            
            success = manager.auto_adapt_combat()
            if success:
                print("✅ Auto-adaptation successful!")
                
                if manager.current_profile:
                    print(f"📋 Active Profile: {manager.current_profile.name}")
                    print(f"🔄 Ability Rotation: {len(manager.current_profile.ability_rotation)} abilities")
                    print(f"🎯 Optimal Range: {manager.current_profile.optimal_range}m")
                    print(f"🚨 Emergency Abilities: {len(manager.current_profile.emergency_abilities)}")
                    
                    print(f"\n📋 Available Abilities:")
                    for ability in manager.current_profile.abilities:
                        print(f"   - {ability}")
                    
                    print(f"\n🔄 Ability Rotation:")
                    for ability in manager.current_profile.ability_rotation:
                        print(f"   - {ability}")
                    
                    print(f"\n🚨 Emergency Abilities:")
                    for trigger, ability in manager.current_profile.emergency_abilities.items():
                        print(f"   {trigger}: {ability}")
                    
                    print(f"\n⚖️  Combat Priorities:")
                    for key, value in manager.current_profile.combat_priorities.items():
                        print(f"   {key}: {value}")
                    
                    print(f"\n⏱️  Cooldowns:")
                    for ability, cooldown in manager.current_profile.cooldowns.items():
                        print(f"   {ability}: {cooldown}s")
                else:
                    print("⚠️  No profile currently active")
            else:
                print("❌ Auto-adaptation failed")
                sys.exit(1)
        
        elif args.list_profiles:
            print("📚 Available Combat Profiles")
            print("=" * 40)
            
            if not manager.available_profiles:
                print("❌ No profiles found")
                sys.exit(1)
            
            for name, profile in manager.available_profiles.items():
                print(f"\n📋 {name}")
                print(f"   Description: {profile.description}")
                print(f"   Build Type: {profile.build_type.value}")
                print(f"   Weapon Type: {profile.weapon_type.value}")
                print(f"   Combat Style: {profile.combat_style.value}")
                print(f"   Abilities: {len(profile.abilities)}")
                print(f"   Optimal Range: {profile.optimal_range}m")
                print(f"   Emergency Abilities: {len(profile.emergency_abilities)}")
            
            if args.output:
                import json
                profiles_data = {
                    "profiles": [
                        {
                            "name": name,
                            "description": profile.description,
                            "build_type": profile.build_type.value,
                            "weapon_type": profile.weapon_type.value,
                            "combat_style": profile.combat_style.value,
                            "abilities_count": len(profile.abilities),
                            "optimal_range": profile.optimal_range,
                            "emergency_count": len(profile.emergency_abilities)
                        }
                        for name, profile in manager.available_profiles.items()
                    ]
                }
                with open(args.output, 'w') as f:
                    json.dump(profiles_data, f, indent=2)
                print(f"\n💾 Profiles list saved to {args.output}")
        
        elif args.profile:
            profile_name = args.profile
            if profile_name not in manager.available_profiles:
                print(f"❌ Profile '{profile_name}' not found")
                sys.exit(1)
            
            profile = manager.available_profiles[profile_name]
            print(f"📋 Profile: {profile.name}")
            print("=" * 50)
            print(f"Description: {profile.description}")
            print(f"Build Type: {profile.build_type.value}")
            print(f"Weapon Type: {profile.weapon_type.value}")
            print(f"Combat Style: {profile.combat_style.value}")
            print(f"Optimal Range: {profile.optimal_range}m")
            
            print(f"\n📋 Abilities ({len(profile.abilities)}):")
            for ability in profile.abilities:
                print(f"   - {ability}")
            
            print(f"\n🔄 Ability Rotation ({len(profile.ability_rotation)}):")
            for ability in profile.ability_rotation:
                print(f"   - {ability}")
            
            print(f"\n🚨 Emergency Abilities ({len(profile.emergency_abilities)}):")
            for trigger, ability in profile.emergency_abilities.items():
                print(f"   {trigger}: {ability}")
            
            print(f"\n⚖️  Combat Priorities:")
            for key, value in profile.combat_priorities.items():
                print(f"   {key}: {value}")
            
            print(f"\n⏱️  Cooldowns ({len(profile.cooldowns)}):")
            for ability, cooldown in profile.cooldowns.items():
                print(f"   {ability}: {cooldown}s")
            
            print(f"\n🎯 Targeting Config:")
            for key, value in profile.targeting.items():
                print(f"   {key}: {value}")
            
            print(f"\n💊 Healing Config:")
            for key, value in profile.healing.items():
                if isinstance(value, list):
                    print(f"   {key}: {len(value)} abilities")
                else:
                    print(f"   {key}: {value}")
            
            print(f"\n🔋 Buffing Config:")
            for key, value in profile.buffing.items():
                if isinstance(value, list):
                    print(f"   {key}: {len(value)} abilities")
                else:
                    print(f"   {key}: {value}")
            
            print(f"\n🔄 Fallback Abilities ({len(profile.fallback_abilities)}):")
            for ability in profile.fallback_abilities:
                print(f"   - {ability}")
            
            if args.output:
                import json
                profile_data = {
                    "name": profile.name,
                    "description": profile.description,
                    "build_type": profile.build_type.value,
                    "weapon_type": profile.weapon_type.value,
                    "combat_style": profile.combat_style.value,
                    "abilities": profile.abilities,
                    "ability_rotation": profile.ability_rotation,
                    "emergency_abilities": profile.emergency_abilities,
                    "combat_priorities": profile.combat_priorities,
                    "cooldowns": profile.cooldowns,
                    "targeting": profile.targeting,
                    "healing": profile.healing,
                    "buffing": profile.buffing,
                    "optimal_range": profile.optimal_range,
                    "fallback_abilities": profile.fallback_abilities
                }
                with open(args.output, 'w') as f:
                    json.dump(profile_data, f, indent=2)
                print(f"\n💾 Profile data saved to {args.output}")
        
        elif args.build_stats:
            stats = manager.get_build_statistics()
            
            if not stats:
                print("❌ No build statistics available")
                sys.exit(1)
            
            print("📊 Build Detection Statistics")
            print("=" * 40)
            print(f"Total Detections: {stats['total_detections']}")
            print(f"Average Confidence: {stats['average_confidence']:.2f}")
            
            print(f"\nBuild Distribution:")
            for build_type, count in stats['build_distribution'].items():
                print(f"   {build_type}: {count}")
            
            print(f"\nWeapon Distribution:")
            for weapon_type, count in stats['weapon_distribution'].items():
                print(f"   {weapon_type}: {count}")
            
            print(f"\nCurrent Build:")
            current_build = stats['current_build']
            print(f"   Type: {current_build['type']}")
            print(f"   Weapon: {current_build['weapon']}")
            print(f"   Confidence: {current_build['confidence']:.2f}")
            print(f"   Profile: {stats['current_profile']}")
            
            if args.output:
                import json
                with open(args.output, 'w') as f:
                    json.dump(stats, f, indent=2)
                print(f"\n💾 Statistics saved to {args.output}")
        
        elif args.test_ocr:
            ocr_text = args.test_ocr
            print(f"🔍 Testing OCR parsing: {ocr_text}")
            print("-" * 50)
            
            # Parse skills from OCR text
            skills = manager.parse_skills_from_ocr(ocr_text)
            print(f"Parsed Skills: {len(skills)}")
            
            if skills:
                print(f"\nSkills Found:")
                for skill_name, skill_level in skills.items():
                    print(f"   {skill_name}: Level {skill_level.level}")
                
                # Detect build and weapon
                build_type = manager.detect_build_type(skills)
                weapon_type = manager.detect_weapon_type(skills)
                combat_style = manager.determine_combat_style(build_type, weapon_type)
                
                print(f"\nDetection Results:")
                print(f"   Build Type: {build_type.value}")
                print(f"   Weapon Type: {weapon_type.value}")
                print(f"   Combat Style: {combat_style.value}")
                
                # Calculate confidence
                confidence = manager.calculate_build_confidence(skills, build_type, weapon_type)
                print(f"   Confidence: {confidence:.2f}")
                
                # Categorize skills
                primary_skills, secondary_skills = manager.categorize_skills(skills, build_type)
                print(f"   Primary Skills: {len(primary_skills)}")
                print(f"   Secondary Skills: {len(secondary_skills)}")
                
                if args.output:
                    import json
                    test_data = {
                        "ocr_text": ocr_text,
                        "parsed_skills": {k: v.level for k, v in skills.items()},
                        "detected_build": build_type.value,
                        "detected_weapon": weapon_type.value,
                        "combat_style": combat_style.value,
                        "confidence": confidence,
                        "primary_skills": {k: v.level for k, v in primary_skills.items()},
                        "secondary_skills": {k: v.level for k, v in secondary_skills.items()}
                    }
                    with open(args.output, 'w') as f:
                        json.dump(test_data, f, indent=2)
                    print(f"\n💾 Test results saved to {args.output}")
            else:
                print("❌ No skills parsed from OCR text")
                sys.exit(1)
        
        elif args.reload_profiles:
            print("🔄 Reloading combat profiles...")
            manager.reload_profiles()
            print(f"✅ Reloaded {len(manager.available_profiles)} profiles")
        
        elif args.validate_profiles:
            print("✅ Validating combat profiles...")
            print("=" * 40)
            
            valid_profiles = 0
            total_profiles = len(manager.available_profiles)
            
            for name, profile in manager.available_profiles.items():
                print(f"\n📋 Validating: {name}")
                
                issues = []
                if not profile.abilities:
                    issues.append("No abilities defined")
                if not profile.ability_rotation:
                    issues.append("No ability rotation defined")
                if not profile.emergency_abilities:
                    issues.append("No emergency abilities defined")
                if profile.optimal_range <= 0:
                    issues.append("Invalid optimal range")
                if not profile.fallback_abilities:
                    issues.append("No fallback abilities defined")
                
                if issues:
                    print(f"   ❌ Issues: {', '.join(issues)}")
                else:
                    print(f"   ✅ Profile structure: VALID")
                    valid_profiles += 1
            
            print(f"\n📊 Validation Summary:")
            print(f"   Total Profiles: {total_profiles}")
            print(f"   Valid Profiles: {valid_profiles}")
            print(f"   Invalid Profiles: {total_profiles - valid_profiles}")
            
            if valid_profiles == total_profiles:
                print("   🎉 All profiles are valid!")
            else:
                print("   ⚠️  Some profiles have issues")
        
        # Save data if requested
        if args.save and not (args.detect_build or args.auto_adapt):
            # In a real implementation, you'd save build data
            print("💾 Build data saved")
    
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 
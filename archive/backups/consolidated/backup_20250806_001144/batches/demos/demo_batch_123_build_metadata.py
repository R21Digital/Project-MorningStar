#!/usr/bin/env python3
"""
Demo script for Batch 123 - Build Metadata + Community Templates

This script demonstrates the functionality of the new build system including:
- Loading community builds from YAML
- Validating build configurations
- Searching and filtering builds
- Exporting builds to JSON format
- Displaying build information and performance metrics
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.build_loader import get_build_loader, BuildCategory, BuildSpecialization, BuildDifficulty


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_build_summary(build_id, build_data):
    """Print a formatted build summary."""
    print(f"\n📋 {build_data['name']} ({build_id})")
    print(f"   Description: {build_data['description']}")
    print(f"   Category: {build_data['category']}")
    print(f"   Specialization: {build_data['specialization']}")
    print(f"   Difficulty: {build_data['difficulty']}")
    print(f"   Professions: {', '.join(build_data['professions'])}")
    print(f"   Total Skills: {build_data['total_skills']}")
    print(f"   Combat Style: {build_data['combat_style']}")
    print(f"   Performance: {build_data['avg_performance']}/10")
    print(f"   Best Rating: {build_data['best_performance']}/10")


def demo_load_builds():
    """Demonstrate loading all builds."""
    print_header("Loading Community Builds")
    
    try:
        build_loader = get_build_loader()
        all_builds = build_loader.get_all_builds()
        
        print(f"✅ Successfully loaded {len(all_builds)} builds:")
        
        for build_id, build in all_builds.items():
            summary = build_loader.get_build_summary(build_id)
            print_build_summary(build_id, summary)
            
    except Exception as e:
        print(f"❌ Error loading builds: {e}")


def demo_build_validation():
    """Demonstrate build validation."""
    print_header("Build Validation")
    
    try:
        build_loader = get_build_loader()
        all_builds = build_loader.get_all_builds()
        
        for build_id in all_builds.keys():
            is_valid, errors = build_loader.validate_build(build_id)
            
            if is_valid:
                print(f"✅ {build_id}: Valid")
            else:
                print(f"❌ {build_id}: Invalid")
                for error in errors:
                    print(f"   - {error}")
                    
    except Exception as e:
        print(f"❌ Error validating builds: {e}")


def demo_build_search():
    """Demonstrate build searching and filtering."""
    print_header("Build Search and Filtering")
    
    try:
        build_loader = get_build_loader()
        
        # Search by category
        print("\n🔍 Combat builds:")
        combat_builds = build_loader.search_builds(category=BuildCategory.COMBAT)
        for build_id, build in combat_builds.items():
            print(f"   - {build.name} ({build_id})")
        
        # Search by specialization
        print("\n🔍 PvE builds:")
        pve_builds = build_loader.search_builds(specialization=BuildSpecialization.PVE)
        for build_id, build in pve_builds.items():
            print(f"   - {build.name} ({build_id})")
        
        # Search by difficulty
        print("\n🔍 Easy builds:")
        easy_builds = build_loader.search_builds(difficulty=BuildDifficulty.EASY)
        for build_id, build in easy_builds.items():
            print(f"   - {build.name} ({build_id})")
        
        # Search with minimum rating
        print("\n🔍 High-performance builds (rating >= 8.0):")
        high_perf_builds = build_loader.search_builds(min_rating=8.0)
        for build_id, build in high_perf_builds.items():
            print(f"   - {build.name} ({build_id}) - {max(build.performance.values()):.1f}/10")
            
    except Exception as e:
        print(f"❌ Error searching builds: {e}")


def demo_build_details():
    """Demonstrate getting detailed build information."""
    print_header("Build Details")
    
    try:
        build_loader = get_build_loader()
        all_builds = build_loader.get_all_builds()
        
        # Show details for the first build
        if all_builds:
            build_id = list(all_builds.keys())[0]
            build = all_builds[build_id]
            
            print(f"\n📋 Detailed information for {build.name}:")
            print(f"   ID: {build_id}")
            print(f"   Description: {build.description}")
            print(f"   Category: {build.category.value}")
            print(f"   Specialization: {build.specialization.value}")
            print(f"   Difficulty: {build.difficulty.value}")
            
            print(f"\n   Professions:")
            for role, profession in build.professions.items():
                print(f"     {role}: {profession}")
            
            print(f"\n   Skills:")
            for profession, skills in build.skills.items():
                print(f"     {profession}:")
                for skill in skills:
                    print(f"       - {skill}")
            
            print(f"\n   Equipment:")
            print(f"     Weapons: {build.equipment.get('weapons', {})}")
            print(f"     Armor: {build.equipment.get('armor', {})}")
            print(f"     Tapes: {build.equipment.get('tapes', [])}")
            print(f"     Resists: {build.equipment.get('resists', [])}")
            
            print(f"\n   Performance:")
            for metric, rating in build.performance.items():
                print(f"     {metric}: {rating}/10")
            
            print(f"\n   Combat:")
            print(f"     Style: {build.combat.get('style', 'unknown')}")
            print(f"     Stance: {build.combat.get('stance', 'unknown')}")
            print(f"     Rotation: {build.combat.get('rotation', [])}")
            
            print(f"\n   Cooldowns:")
            for ability, cooldown in build.cooldowns.items():
                print(f"     {ability}: {cooldown}s")
            
            print(f"\n   Emergency Abilities:")
            for situation, ability in build.emergency_abilities.items():
                print(f"     {situation}: {ability}")
            
            print(f"\n   Notes:")
            for note in build.notes:
                print(f"     - {note}")
                
    except Exception as e:
        print(f"❌ Error getting build details: {e}")


def demo_build_export():
    """Demonstrate exporting builds to JSON."""
    print_header("Build Export")
    
    try:
        build_loader = get_build_loader()
        all_builds = build_loader.get_all_builds()
        
        # Export the first build
        if all_builds:
            build_id = list(all_builds.keys())[0]
            output_path = f"demo_export_{build_id}.json"
            
            success = build_loader.export_build_to_json(build_id, output_path)
            
            if success:
                print(f"✅ Successfully exported {build_id} to {output_path}")
                
                # Show the exported content
                with open(output_path, 'r') as f:
                    exported_data = json.load(f)
                
                print(f"\n📄 Exported build structure:")
                print(f"   Name: {exported_data.get('name', 'N/A')}")
                print(f"   Category: {exported_data.get('category', 'N/A')}")
                print(f"   Specialization: {exported_data.get('specialization', 'N/A')}")
                print(f"   Difficulty: {exported_data.get('difficulty', 'N/A')}")
                print(f"   Skills: {len(exported_data.get('skills', {}))} profession(s)")
                print(f"   Equipment: {len(exported_data.get('equipment', {}))} category(ies)")
                print(f"   Performance: {len(exported_data.get('performance', {}))} metric(s)")
                
                # Clean up the demo file
                os.remove(output_path)
                print(f"\n🗑️  Cleaned up demo file: {output_path}")
            else:
                print(f"❌ Failed to export {build_id}")
                
    except Exception as e:
        print(f"❌ Error exporting build: {e}")


def demo_top_performing():
    """Demonstrate getting top performing builds."""
    print_header("Top Performing Builds")
    
    try:
        build_loader = get_build_loader()
        
        # Get top PvE builds
        print("\n🏆 Top PvE builds:")
        top_pve = build_loader.get_top_performing_builds('pve_rating', 3)
        for build_id, rating in top_pve:
            build = build_loader.get_build(build_id)
            if build:
                print(f"   - {build.name}: {rating}/10")
        
        # Get top PvP builds
        print("\n🏆 Top PvP builds:")
        top_pvp = build_loader.get_top_performing_builds('pvp_rating', 3)
        for build_id, rating in top_pvp:
            build = build_loader.get_build(build_id)
            if build:
                print(f"   - {build.name}: {rating}/10")
        
        # Get top solo builds
        print("\n🏆 Top solo builds:")
        top_solo = build_loader.get_top_performing_builds('solo_rating', 3)
        for build_id, rating in top_solo:
            build = build_loader.get_build(build_id)
            if build:
                print(f"   - {build.name}: {rating}/10")
                
    except Exception as e:
        print(f"❌ Error getting top performing builds: {e}")


def demo_build_statistics():
    """Demonstrate build statistics."""
    print_header("Build Statistics")
    
    try:
        build_loader = get_build_loader()
        all_builds = build_loader.get_all_builds()
        
        # Count by category
        categories = {}
        specializations = {}
        difficulties = {}
        total_skills = 0
        total_performance = 0
        
        for build_id, build in all_builds.items():
            # Category stats
            cat = build.category.value
            categories[cat] = categories.get(cat, 0) + 1
            
            # Specialization stats
            spec = build.specialization.value
            specializations[spec] = specializations.get(spec, 0) + 1
            
            # Difficulty stats
            diff = build.difficulty.value
            difficulties[diff] = difficulties.get(diff, 0) + 1
            
            # Skills stats
            total_skills += sum(len(skills) for skills in build.skills.values())
            
            # Performance stats
            if build.performance:
                total_performance += sum(build.performance.values()) / len(build.performance)
        
        print(f"\n📊 Build Statistics:")
        print(f"   Total builds: {len(all_builds)}")
        print(f"   Total skills: {total_skills}")
        print(f"   Average performance: {total_performance/len(all_builds):.1f}/10")
        
        print(f"\n   Categories:")
        for cat, count in categories.items():
            print(f"     {cat}: {count}")
        
        print(f"\n   Specializations:")
        for spec, count in specializations.items():
            print(f"     {spec}: {count}")
        
        print(f"\n   Difficulties:")
        for diff, count in difficulties.items():
            print(f"     {diff}: {count}")
            
    except Exception as e:
        print(f"❌ Error getting build statistics: {e}")


def main():
    """Run all demos."""
    print("🚀 Batch 123 - Build Metadata + Community Templates Demo")
    print("This demo showcases the new community build system functionality.")
    
    # Check if the builds file exists
    builds_file = Path("builds/combat_profiles.yaml")
    if not builds_file.exists():
        print(f"\n❌ Error: Builds file not found at {builds_file}")
        print("Please ensure the builds/combat_profiles.yaml file exists.")
        return
    
    print(f"\n✅ Found builds file: {builds_file}")
    
    # Run all demos
    demo_load_builds()
    demo_build_validation()
    demo_build_search()
    demo_build_details()
    demo_build_export()
    demo_top_performing()
    demo_build_statistics()
    
    print_header("Demo Complete")
    print("✅ All demos completed successfully!")
    print("\n🎯 Key Features Demonstrated:")
    print("   - Loading community builds from YAML")
    print("   - Build validation and error checking")
    print("   - Search and filtering capabilities")
    print("   - Detailed build information access")
    print("   - Build export to JSON format")
    print("   - Top performing build rankings")
    print("   - Build statistics and analytics")
    print("\n📚 Next Steps:")
    print("   - Access the dashboard at /community-builds")
    print("   - Use the BuildSelector React component")
    print("   - Integrate with existing build systems")
    print("   - Add more community builds to the YAML file")


if __name__ == "__main__":
    main() 
"""
Static Builds CLI - Command-line interface for managing the static builds library.

This module provides commands for:
- Creating new build profiles
- Listing existing builds
- Viewing build details
- Updating build information
- Deleting builds
- Searching builds
- Getting statistics
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.static_builds_library import (
    get_static_builds_library,
    StaticBuild,
    BuildMetadata,
    SkillTree,
    EquipmentRecommendation,
    PerformanceRatings,
    UserRatings,
    BuildCategory,
    BuildDifficulty,
    BuildSpecialization,
    BuildSource
)


def create_build_command(args):
    """Create a new build profile."""
    library = get_static_builds_library()
    
    # Get build data from arguments or prompt user
    build_id = args.build_id or input("Build ID: ")
    name = args.name or input("Build name: ")
    description = args.description or input("Description: ")
    
    # Get professions
    professions = {}
    if args.primary_profession:
        professions['primary'] = args.primary_profession
    if args.secondary_profession:
        professions['secondary'] = args.secondary_profession
    
    # Get skill trees
    skill_trees = {}
    if args.skills:
        # Parse skills from command line
        for prof, skills_str in args.skills:
            skills = [s.strip() for s in skills_str.split(',')]
            skill_trees[prof] = SkillTree(profession=prof, skills=skills)
    
    # Get buff priority
    buff_priority = []
    if args.buff_priority:
        buff_priority = [b.strip() for b in args.buff_priority.split(',')]
    
    # Get weapon type
    weapon_type = args.weapon_type or input("Weapon type: ")
    
    # Create equipment
    equipment = EquipmentRecommendation()
    if args.weapons:
        for weapon_type_name, weapons_str in args.weapons:
            weapons = [w.strip() for w in weapons_str.split(',')]
            equipment.weapons[weapon_type_name] = weapons
    
    # Create performance ratings
    performance = PerformanceRatings()
    if args.pve_rating:
        performance.pve_rating = float(args.pve_rating)
    if args.pvp_rating:
        performance.pvp_rating = float(args.pvp_rating)
    if args.solo_rating:
        performance.solo_rating = float(args.solo_rating)
    if args.group_rating:
        performance.group_rating = float(args.group_rating)
    if args.farming_rating:
        performance.farming_rating = float(args.farming_rating)
    
    # Create metadata
    metadata = BuildMetadata(
        id=build_id,
        name=name,
        description=description,
        author=args.author or "Unknown",
        source=BuildSource(args.source) if args.source else BuildSource.AI_GENERATED,
        difficulty=BuildDifficulty(args.difficulty) if args.difficulty else BuildDifficulty.INTERMEDIATE,
        category=BuildCategory(args.category) if args.category else BuildCategory.COMBAT,
        specialization=BuildSpecialization(args.specialization) if args.specialization else BuildSpecialization.PVE,
        tags=args.tags.split(',') if args.tags else []
    )
    
    # Create ratings
    ratings = UserRatings()
    
    # Create the build
    build = StaticBuild(
        metadata=metadata,
        professions=professions,
        skill_trees=skill_trees,
        buff_priority=buff_priority,
        weapon_type=weapon_type,
        equipment=equipment,
        performance=performance,
        ratings=ratings,
        notes=args.notes or ""
    )
    
    # Save the build
    if library.create_build(build):
        print(f"✅ Created build: {name} ({build_id})")
        print(f"📁 Markdown file: builds/{build_id}.md")
        print(f"💾 Database updated: data/static_builds_database.json")
    else:
        print("❌ Failed to create build")
        sys.exit(1)


def list_builds_command(args):
    """List all builds with optional filtering."""
    library = get_static_builds_library()
    
    # Apply filters
    category = None
    if args.category:
        try:
            category = BuildCategory(args.category)
        except ValueError:
            print(f"❌ Invalid category: {args.category}")
            sys.exit(1)
    
    difficulty = None
    if args.difficulty:
        try:
            difficulty = BuildDifficulty(args.difficulty)
        except ValueError:
            print(f"❌ Invalid difficulty: {args.difficulty}")
            sys.exit(1)
    
    specialization = None
    if args.specialization:
        try:
            specialization = BuildSpecialization(args.specialization)
        except ValueError:
            print(f"❌ Invalid specialization: {args.specialization}")
            sys.exit(1)
    
    # Get builds
    builds = library.list_builds(
        category=category,
        difficulty=difficulty,
        specialization=specialization
    )
    
    if not builds:
        print("📭 No builds found")
        return
    
    # Display builds
    print(f"📋 Found {len(builds)} builds:")
    print()
    
    for build in builds:
        print(f"🔸 {build.metadata.name} ({build.metadata.id})")
        print(f"   Description: {build.metadata.description}")
        print(f"   Category: {build.metadata.category.value.title()}")
        print(f"   Difficulty: {build.metadata.difficulty.value.title()}")
        print(f"   Weapon: {build.weapon_type}")
        print(f"   Rating: {build.ratings.average_rating:.1f}/5 ({build.ratings.total_votes} votes)")
        print(f"   Source: {build.metadata.source.value.replace('_', ' ').title()}")
        print()


def view_build_command(args):
    """View detailed information about a specific build."""
    library = get_static_builds_library()
    
    build = library.get_build(args.build_id)
    if not build:
        print(f"❌ Build '{args.build_id}' not found")
        sys.exit(1)
    
    print(f"🔸 {build.metadata.name}")
    print(f"   ID: {build.metadata.id}")
    print(f"   Description: {build.metadata.description}")
    print(f"   Category: {build.metadata.category.value.title()}")
    print(f"   Difficulty: {build.metadata.difficulty.value.title()}")
    print(f"   Specialization: {build.metadata.specialization.value.upper()}")
    print(f"   Weapon Type: {build.weapon_type}")
    print(f"   Author: {build.metadata.author}")
    print(f"   Source: {build.metadata.source.value.replace('_', ' ').title()}")
    print(f"   Created: {build.metadata.created_at}")
    print(f"   Updated: {build.metadata.updated_at}")
    print()
    
    print("📚 Professions:")
    for role, profession in build.professions.items():
        print(f"   {role.title()}: {profession}")
    print()
    
    print("🎯 Skill Trees:")
    for prof_name, skill_tree in build.skill_trees.items():
        print(f"   {prof_name.title()}:")
        for skill in skill_tree.skills:
            print(f"     - {skill}")
    print()
    
    if build.buff_priority:
        print("⚡ Buff Priority:")
        for i, buff in enumerate(build.buff_priority, 1):
            print(f"   {i}. {buff}")
        print()
    
    print("⚔️ Equipment:")
    if build.equipment.weapons:
        print("   Weapons:")
        for weapon_type, weapons in build.equipment.weapons.items():
            print(f"     {weapon_type.title()}: {', '.join(weapons)}")
    
    if build.equipment.armor:
        print("   Armor:")
        for armor_type, armor_list in build.equipment.armor.items():
            print(f"     {armor_type.title()}: {', '.join(armor_list)}")
    
    if build.equipment.tapes:
        print(f"   Tapes: {', '.join(build.equipment.tapes)}")
    
    if build.equipment.resists:
        print(f"   Resists: {', '.join(build.equipment.resists)}")
    print()
    
    print("📊 Performance Ratings:")
    print(f"   PvE: {build.performance.pve_rating}/10")
    print(f"   PvP: {build.performance.pvp_rating}/10")
    print(f"   Solo: {build.performance.solo_rating}/10")
    print(f"   Group: {build.performance.group_rating}/10")
    print(f"   Farming: {build.performance.farming_rating}/10")
    print()
    
    print("⭐ Community Ratings:")
    print(f"   Average: {build.ratings.average_rating:.1f}/5")
    print(f"   Total Votes: {build.ratings.total_votes}")
    print()
    
    if build.notes:
        print("📝 Notes:")
        print(f"   {build.notes}")
        print()
    
    if build.links:
        print("🔗 Links:")
        for link_name, link_url in build.links.items():
            print(f"   {link_name}: {link_url}")
        print()


def search_builds_command(args):
    """Search builds by name, description, or tags."""
    library = get_static_builds_library()
    
    builds = library.search_builds(args.query)
    
    if not builds:
        print(f"🔍 No builds found matching '{args.query}'")
        return
    
    print(f"🔍 Found {len(builds)} builds matching '{args.query}':")
    print()
    
    for build in builds:
        print(f"🔸 {build.metadata.name} ({build.metadata.id})")
        print(f"   Description: {build.metadata.description}")
        print(f"   Category: {build.metadata.category.value.title()}")
        print(f"   Weapon: {build.weapon_type}")
        print(f"   Rating: {build.ratings.average_rating:.1f}/5")
        print()


def update_build_command(args):
    """Update an existing build."""
    library = get_static_builds_library()
    
    build = library.get_build(args.build_id)
    if not build:
        print(f"❌ Build '{args.build_id}' not found")
        sys.exit(1)
    
    # Prepare updates
    updates = {}
    
    if args.name:
        updates['name'] = args.name
    if args.description:
        updates['description'] = args.description
    if args.buff_priority:
        updates['buff_priority'] = [b.strip() for b in args.buff_priority.split(',')]
    if args.pve_rating:
        updates['performance'] = {'pve_rating': float(args.pve_rating)}
    if args.pvp_rating:
        updates['performance'] = updates.get('performance', {})
        updates['performance']['pvp_rating'] = float(args.pvp_rating)
    if args.solo_rating:
        updates['performance'] = updates.get('performance', {})
        updates['performance']['solo_rating'] = float(args.solo_rating)
    if args.group_rating:
        updates['performance'] = updates.get('performance', {})
        updates['performance']['group_rating'] = float(args.group_rating)
    if args.farming_rating:
        updates['performance'] = updates.get('performance', {})
        updates['performance']['farming_rating'] = float(args.farming_rating)
    
    if library.update_build(args.build_id, updates):
        print(f"✅ Updated build: {args.build_id}")
    else:
        print("❌ Failed to update build")
        sys.exit(1)


def delete_build_command(args):
    """Delete a build."""
    library = get_static_builds_library()
    
    if not args.force:
        confirm = input(f"Are you sure you want to delete build '{args.build_id}'? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ Deletion cancelled")
            return
    
    if library.delete_build(args.build_id):
        print(f"✅ Deleted build: {args.build_id}")
    else:
        print(f"❌ Build '{args.build_id}' not found")
        sys.exit(1)


def stats_command(args):
    """Show build library statistics."""
    library = get_static_builds_library()
    
    stats = library.get_statistics()
    
    print("📊 Build Library Statistics:")
    print()
    print(f"📚 Total Builds: {stats['total_builds']}")
    print()
    
    print("📂 Categories:")
    for category, count in stats['categories'].items():
        print(f"   {category.title()}: {count}")
    print()
    
    print("📈 Difficulties:")
    for difficulty, count in stats['difficulties'].items():
        print(f"   {difficulty.title()}: {count}")
    print()
    
    print("🎯 Specializations:")
    for specialization, count in stats['specializations'].items():
        print(f"   {specialization.upper()}: {count}")
    print()
    
    print("📝 Sources:")
    for source, count in stats['sources'].items():
        source_name = source.replace('_', ' ').title()
        print(f"   {source_name}: {count}")
    print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Static Builds Library CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --build-id rifleman_medic --name "Rifleman/Medic" --description "Hybrid build"
  %(prog)s list --category combat
  %(prog)s view rifleman_medic
  %(prog)s search "rifleman"
  %(prog)s update rifleman_medic --pve-rating 9.0
  %(prog)s delete rifleman_medic --force
  %(prog)s stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new build')
    create_parser.add_argument('--build-id', help='Build ID')
    create_parser.add_argument('--name', help='Build name')
    create_parser.add_argument('--description', help='Build description')
    create_parser.add_argument('--primary-profession', help='Primary profession')
    create_parser.add_argument('--secondary-profession', help='Secondary profession')
    create_parser.add_argument('--skills', nargs=2, action='append', metavar=('PROFESSION', 'SKILLS'), help='Profession and skills (comma-separated)')
    create_parser.add_argument('--buff-priority', help='Buff priority (comma-separated)')
    create_parser.add_argument('--weapon-type', help='Weapon type')
    create_parser.add_argument('--weapons', nargs=2, action='append', metavar=('TYPE', 'WEAPONS'), help='Weapon type and weapons (comma-separated)')
    create_parser.add_argument('--pve-rating', type=float, help='PvE rating (0-10)')
    create_parser.add_argument('--pvp-rating', type=float, help='PvP rating (0-10)')
    create_parser.add_argument('--solo-rating', type=float, help='Solo rating (0-10)')
    create_parser.add_argument('--group-rating', type=float, help='Group rating (0-10)')
    create_parser.add_argument('--farming-rating', type=float, help='Farming rating (0-10)')
    create_parser.add_argument('--author', help='Build author')
    create_parser.add_argument('--source', choices=['ai_generated', 'player_created', 'community_submitted', 'official'], help='Build source')
    create_parser.add_argument('--category', choices=['combat', 'support', 'utility', 'crafting', 'social', 'hybrid'], help='Build category')
    create_parser.add_argument('--difficulty', choices=['beginner', 'intermediate', 'advanced', 'expert'], help='Build difficulty')
    create_parser.add_argument('--specialization', choices=['pve', 'pvp', 'solo', 'group', 'farming', 'crafting', 'social'], help='Build specialization')
    create_parser.add_argument('--tags', help='Tags (comma-separated)')
    create_parser.add_argument('--notes', help='Build notes')
    create_parser.set_defaults(func=create_build_command)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List builds')
    list_parser.add_argument('--category', choices=['combat', 'support', 'utility', 'crafting', 'social', 'hybrid'], help='Filter by category')
    list_parser.add_argument('--difficulty', choices=['beginner', 'intermediate', 'advanced', 'expert'], help='Filter by difficulty')
    list_parser.add_argument('--specialization', choices=['pve', 'pvp', 'solo', 'group', 'farming', 'crafting', 'social'], help='Filter by specialization')
    list_parser.set_defaults(func=list_builds_command)
    
    # View command
    view_parser = subparsers.add_parser('view', help='View build details')
    view_parser.add_argument('build_id', help='Build ID to view')
    view_parser.set_defaults(func=view_build_command)
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search builds')
    search_parser.add_argument('query', help='Search query')
    search_parser.set_defaults(func=search_builds_command)
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update a build')
    update_parser.add_argument('build_id', help='Build ID to update')
    update_parser.add_argument('--name', help='New build name')
    update_parser.add_argument('--description', help='New description')
    update_parser.add_argument('--buff-priority', help='New buff priority (comma-separated)')
    update_parser.add_argument('--pve-rating', type=float, help='New PvE rating')
    update_parser.add_argument('--pvp-rating', type=float, help='New PvP rating')
    update_parser.add_argument('--solo-rating', type=float, help='New solo rating')
    update_parser.add_argument('--group-rating', type=float, help='New group rating')
    update_parser.add_argument('--farming-rating', type=float, help='New farming rating')
    update_parser.set_defaults(func=update_build_command)
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a build')
    delete_parser.add_argument('build_id', help='Build ID to delete')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    delete_parser.set_defaults(func=delete_build_command)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.set_defaults(func=stats_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == '__main__':
    main() 
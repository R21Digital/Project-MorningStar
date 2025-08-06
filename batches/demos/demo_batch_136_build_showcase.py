#!/usr/bin/env python3
"""
Batch 136 - Build Showcase & Rotation Library Demo

This demo showcases the structured system for showcasing popular character builds
and rotations publicly. It demonstrates the build profiles, rotation libraries,
and public display functionality.

Features:
- Build profiles with profession trees, stat priorities, equipment
- YAML/Markdown content format for builds
- Public side: /builds/{profession}/{build-name}
- Admin upload tool to manage featured builds
- User-submitted builds (flagged for moderation)
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from core.build_showcase_manager import (
    build_showcase_manager,
    BuildCategory,
    BuildDifficulty,
    BuildStatus
)


def create_sample_builds():
    """Create sample builds to demonstrate the system."""
    
    # Sample Rifleman/Medic Build
    rifleman_medic_build = {
        "name": "Rifleman/Medic Hybrid",
        "description": "A versatile build combining ranged combat with healing capabilities. Perfect for solo PvE content and group support roles.",
        "author": "Project MorningStar",
        "version": "1.0.0",
        "category": "hybrid",
        "difficulty": "intermediate",
        "status": "published",
        "tags": ["rifleman", "medic", "pve", "solo", "group", "healing", "ranged"],
        
        "professions": {
            "primary": "rifleman",
            "secondary": "medic"
        },
        
        "profession_tree": {
            "rifleman": [
                "combat_marksman_novice",
                "combat_rifleman_novice",
                "combat_rifleman_marksman",
                "combat_rifleman_rifleman",
                "combat_rifleman_sniper",
                "combat_rifleman_master"
            ],
            "medic": [
                "science_medic_novice",
                "science_medic_healing",
                "science_medic_medicine",
                "science_medic_doctor",
                "science_medic_master"
            ]
        },
        
        "stat_priority": {
            "health": 8,
            "action": 7,
            "mind": 6,
            "strength": 4,
            "constitution": 5,
            "agility": 6,
            "quickness": 5,
            "stamina": 4,
            "presence": 3,
            "focus": 7,
            "willpower": 6
        },
        
        "recommended_stats": {
            "primary": {
                "health": 1000,
                "action": 800,
                "mind": 600
            },
            "secondary": {
                "strength": 300,
                "constitution": 400,
                "agility": 500,
                "quickness": 400,
                "stamina": 300,
                "presence": 200,
                "focus": 600,
                "willpower": 500
            }
        },
        
        "weapons": [
            {
                "name": "T21 Rifle",
                "type": "rifle",
                "damage": "high",
                "range": "long",
                "special": "burst_fire"
            },
            {
                "name": "E11 Carbine",
                "type": "carbine",
                "damage": "medium",
                "range": "medium",
                "special": "rapid_fire"
            }
        ],
        
        "armor": {
            "head": {
                "name": "Stormtrooper Helmet",
                "protection": "medium",
                "special": "energy_resist"
            },
            "chest": {
                "name": "Stormtrooper Armor",
                "protection": "high",
                "special": "kinetic_resist"
            },
            "legs": {
                "name": "Stormtrooper Legs",
                "protection": "medium",
                "special": "none"
            },
            "feet": {
                "name": "Stormtrooper Boots",
                "protection": "low",
                "special": "movement_speed"
            }
        },
        
        "buffs": [
            {
                "name": "Combat Stim",
                "type": "stim",
                "effect": "increased_action",
                "duration": "2_hours"
            },
            {
                "name": "Medical Kit",
                "type": "medical",
                "effect": "healing_bonus",
                "duration": "1_hour"
            },
            {
                "name": "Accuracy Tape",
                "type": "tape",
                "effect": "increased_accuracy",
                "duration": "30_minutes"
            }
        ],
        
        "tapes": [
            {
                "name": "Damage Tape",
                "type": "weapon",
                "effect": "increased_damage",
                "slot": "weapon"
            },
            {
                "name": "Accuracy Tape",
                "type": "weapon",
                "effect": "increased_accuracy",
                "slot": "weapon"
            },
            {
                "name": "Health Tape",
                "type": "armor",
                "effect": "increased_health",
                "slot": "chest"
            }
        ],
        
        "rotation": [
            {
                "ability": "Aim",
                "cooldown": 0,
                "description": "Increase accuracy for next shot"
            },
            {
                "ability": "Headshot",
                "cooldown": 5,
                "description": "High damage single target attack"
            },
            {
                "ability": "Burst Fire",
                "cooldown": 15,
                "description": "Multiple shots for sustained damage"
            },
            {
                "ability": "Heal Self",
                "cooldown": 30,
                "description": "Emergency self-healing when health is low"
            },
            {
                "ability": "Heal Other",
                "cooldown": 25,
                "description": "Heal group members when needed"
            },
            {
                "ability": "Cure Poison",
                "cooldown": 45,
                "description": "Remove poison effects from self or others"
            }
        ],
        
        "sample_macro": """/macro rifleman_medic
/pause 1
/aim
/pause 1
/headshot
/pause 5
/burst_fire
/pause 15
/if health < 50
/heal_self
/endif
/if target_health < 30
/switch_target
/endif""",
        
        "combat_notes": """This build excels in solo PvE content and group support roles. 
The combination of ranged damage and healing abilities provides excellent survivability.

Key strategies:
- Maintain distance from enemies to maximize rifle effectiveness
- Use healing abilities proactively to prevent health drops
- Prioritize targets based on threat level
- Keep buffs active for optimal performance

Recommended for players who enjoy tactical combat and support roles.""",
        
        "performance_metrics": {
            "pve_rating": 8.5,
            "pvp_rating": 6.0,
            "solo_rating": 9.0,
            "group_rating": 8.0,
            "farming_rating": 7.5,
            "healing_efficiency": 8.0,
            "damage_output": 7.0,
            "survivability": 8.5
        }
    }
    
    # Sample Bounty Hunter Build
    bounty_hunter_build = {
        "name": "Bounty Hunter PvP Specialist",
        "description": "A high-damage PvP focused build specializing in tracking and eliminating targets. Features excellent mobility and burst damage capabilities.",
        "author": "Project MorningStar",
        "version": "1.0.0",
        "category": "pvp",
        "difficulty": "advanced",
        "status": "published",
        "tags": ["bounty_hunter", "pvp", "tracking", "burst_damage", "mobility", "stealth"],
        
        "professions": {
            "primary": "bounty_hunter",
            "secondary": "spy"
        },
        
        "profession_tree": {
            "bounty_hunter": [
                "combat_bountyhunter_novice",
                "combat_bountyhunter_marksman",
                "combat_bountyhunter_survivalist",
                "combat_bountyhunter_droidhunter",
                "combat_bountyhunter_master"
            ],
            "spy": [
                "combat_spy_novice",
                "combat_spy_undercover",
                "combat_spy_saboteur",
                "combat_spy_master"
            ]
        },
        
        "stat_priority": {
            "health": 7,
            "action": 8,
            "mind": 5,
            "strength": 6,
            "constitution": 6,
            "agility": 8,
            "quickness": 7,
            "stamina": 5,
            "presence": 4,
            "focus": 6,
            "willpower": 5
        },
        
        "recommended_stats": {
            "primary": {
                "health": 900,
                "action": 900,
                "mind": 500
            },
            "secondary": {
                "strength": 400,
                "constitution": 400,
                "agility": 600,
                "quickness": 500,
                "stamina": 300,
                "presence": 200,
                "focus": 500,
                "willpower": 400
            }
        },
        
        "weapons": [
            {
                "name": "DL44 Heavy Pistol",
                "type": "pistol",
                "damage": "very_high",
                "range": "medium",
                "special": "critical_hit"
            },
            {
                "name": "Vibro Knife",
                "type": "melee",
                "damage": "high",
                "range": "close",
                "special": "bleeding"
            }
        ],
        
        "armor": {
            "head": {
                "name": "Mandalorian Helmet",
                "protection": "high",
                "special": "targeting_system"
            },
            "chest": {
                "name": "Mandalorian Armor",
                "protection": "very_high",
                "special": "energy_shield"
            },
            "legs": {
                "name": "Mandalorian Legs",
                "protection": "high",
                "special": "mobility_enhancement"
            },
            "feet": {
                "name": "Mandalorian Boots",
                "protection": "medium",
                "special": "stealth_field"
            }
        },
        
        "buffs": [
            {
                "name": "Combat Stim",
                "type": "stim",
                "effect": "increased_action_and_health",
                "duration": "2_hours"
            },
            {
                "name": "Adrenaline Rush",
                "type": "medical",
                "effect": "increased_damage_and_speed",
                "duration": "30_minutes"
            },
            {
                "name": "Stealth Field",
                "type": "tech",
                "effect": "reduced_detection",
                "duration": "1_hour"
            }
        ],
        
        "tapes": [
            {
                "name": "Critical Hit Tape",
                "type": "weapon",
                "effect": "increased_critical_chance",
                "slot": "weapon"
            },
            {
                "name": "Damage Tape",
                "type": "weapon",
                "effect": "increased_damage",
                "slot": "weapon"
            },
            {
                "name": "Stealth Tape",
                "type": "armor",
                "effect": "reduced_detection",
                "slot": "chest"
            }
        ],
        
        "rotation": [
            {
                "ability": "Track Target",
                "cooldown": 0,
                "description": "Mark target for tracking and damage bonus"
            },
            {
                "ability": "Stealth",
                "cooldown": 30,
                "description": "Enter stealth mode for surprise attacks"
            },
            {
                "ability": "Critical Shot",
                "cooldown": 8,
                "description": "High damage critical hit attack"
            },
            {
                "ability": "Vibro Blade",
                "cooldown": 3,
                "description": "Close combat melee attack with bleeding"
            },
            {
                "ability": "Adrenaline Rush",
                "cooldown": 120,
                "description": "Temporary damage and speed boost"
            },
            {
                "ability": "Escape",
                "cooldown": 60,
                "description": "Emergency escape ability"
            }
        ],
        
        "sample_macro": """/macro bounty_hunter_pvp
/pause 1
/stealth
/pause 2
/track_target
/pause 1
/critical_shot
/pause 8
/if target_distance < 5
/vibro_blade
/endif
/if health < 40
/escape
/endif
/if action < 30
/adrenaline_rush
/endif""",
        
        "combat_notes": """This build is designed for PvP combat and bounty hunting missions.
The combination of stealth, tracking, and high burst damage makes it deadly in 1v1 situations.

Key strategies:
- Use stealth to approach targets undetected
- Track targets for damage bonuses and location awareness
- Maintain distance when possible, use melee only when necessary
- Save escape ability for emergency situations
- Use adrenaline rush for burst damage windows

Recommended for experienced players who enjoy tactical PvP combat.""",
        
        "performance_metrics": {
            "pve_rating": 6.5,
            "pvp_rating": 9.0,
            "solo_rating": 8.5,
            "group_rating": 6.0,
            "farming_rating": 5.0,
            "burst_damage": 9.5,
            "mobility": 8.5,
            "survivability": 7.0
        }
    }
    
    return [rifleman_medic_build, bounty_hunter_build]


def demo_build_showcase_system():
    """Demonstrate the build showcase system functionality."""
    
    print("=" * 80)
    print("BATCH 136 - BUILD SHOWCASE & ROTATION LIBRARY DEMO")
    print("=" * 80)
    print()
    
    # Create sample builds
    print("1. Creating sample builds...")
    sample_builds = create_sample_builds()
    
    for build_data in sample_builds:
        try:
            build_id = build_showcase_manager.create_build(build_data)
            print(f"   ✓ Created build: {build_data['name']} (ID: {build_id})")
        except Exception as e:
            print(f"   ✗ Failed to create build {build_data['name']}: {e}")
    
    print()
    
    # Demonstrate build retrieval
    print("2. Retrieving builds...")
    builds = build_showcase_manager.get_all_builds()
    print(f"   Total builds: {len(builds)}")
    
    for build in builds:
        print(f"   - {build.name} by {build.author} ({build.category.value})")
    
    print()
    
    # Demonstrate search functionality
    print("3. Searching builds...")
    pve_builds = build_showcase_manager.search_builds(profession="rifleman")
    print(f"   Rifleman builds: {len(pve_builds)}")
    
    pvp_builds = build_showcase_manager.search_builds(profession="bounty_hunter")
    print(f"   Bounty Hunter builds: {len(pvp_builds)}")
    
    print()
    
    # Demonstrate build statistics
    print("4. Build statistics...")
    stats = build_showcase_manager.get_build_statistics()
    print(f"   Total builds: {stats['total_builds']}")
    print(f"   Total views: {stats['total_views']}")
    print(f"   Total likes: {stats['total_likes']}")
    print(f"   Category breakdown: {stats['category_breakdown']}")
    
    print()
    
    # Demonstrate markdown export
    print("5. Exporting build as markdown...")
    if builds:
        build = builds[0]
        markdown_content = build_showcase_manager.export_build_markdown(build.id)
        print(f"   ✓ Exported {build.name} as markdown ({len(markdown_content)} characters)")
        
        # Save to file for demonstration
        output_file = f"demo_build_{build.id}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"   ✓ Saved to {output_file}")
    
    print()
    
    # Demonstrate URL generation
    print("6. Generating public URLs...")
    for build in builds:
        url = build_showcase_manager.generate_build_url(build.id)
        print(f"   {build.name}: {url}")
    
    print()
    
    # Demonstrate build interactions
    print("7. Build interactions...")
    if builds:
        build = builds[0]
        
        # Like a build
        build_showcase_manager.like_build(build.id)
        print(f"   ✓ Liked build: {build.name}")
        
        # Add a comment
        build_showcase_manager.add_comment(build.id, "Demo User", "Great build! Very helpful for new players.")
        print(f"   ✓ Added comment to: {build.name}")
        
        # Increment views
        build_showcase_manager.increment_views(build.id)
        print(f"   ✓ Incremented views for: {build.name}")
    
    print()
    
    # Demonstrate validation
    print("8. Build validation...")
    invalid_build = {
        "name": "Invalid Build",
        "description": "This build is missing required fields"
        # Missing required fields like author, category, difficulty, professions
    }
    
    is_valid, errors = build_showcase_manager.validate_build_data(invalid_build)
    print(f"   Validation result: {'✓ Valid' if is_valid else '✗ Invalid'}")
    if not is_valid:
        print(f"   Errors: {errors}")
    
    print()
    
    # Demonstrate admin functionality
    print("9. Admin functionality...")
    if builds:
        build = builds[1] if len(builds) > 1 else builds[0]
        
        # Update build status
        success = build_showcase_manager.update_build(build.id, {"status": "featured"})
        print(f"   ✓ Updated {build.name} status to featured: {success}")
        
        # Get updated build
        updated_build = build_showcase_manager.get_build(build.id)
        print(f"   Current status: {updated_build.status.value}")
    
    print()
    
    # Demonstrate filtering
    print("10. Build filtering...")
    published_builds = build_showcase_manager.get_all_builds(status=BuildStatus.PUBLISHED)
    print(f"   Published builds: {len(published_builds)}")
    
    featured_builds = build_showcase_manager.get_all_builds(status=BuildStatus.FEATURED)
    print(f"   Featured builds: {len(featured_builds)}")
    
    pve_builds = build_showcase_manager.get_all_builds(category=BuildCategory.PVE)
    print(f"   PVE builds: {len(pve_builds)}")
    
    pvp_builds = build_showcase_manager.get_all_builds(category=BuildCategory.PVP)
    print(f"   PVP builds: {len(pvp_builds)}")
    
    print()
    
    print("=" * 80)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print()
    print("Key Features Demonstrated:")
    print("✓ Build profile creation with profession trees, stat priorities, equipment")
    print("✓ YAML/Markdown content format for builds")
    print("✓ Public URL generation: /builds/{profession}/{build-name}")
    print("✓ Admin upload tool functionality")
    print("✓ User-submitted builds with moderation flags")
    print("✓ Build search and filtering")
    print("✓ Community features (likes, comments, views)")
    print("✓ Markdown export functionality")
    print("✓ Build validation and error handling")
    print("✓ Statistics and analytics")
    print()
    print("Next Steps:")
    print("1. Access the web interface at /build-showcase")
    print("2. Use the admin panel at /build-showcase-admin")
    print("3. View individual builds at /build-showcase/{build_id}")
    print("4. Submit new builds via the API or admin interface")


def demo_api_endpoints():
    """Demonstrate the API endpoints."""
    
    print("API Endpoints Available:")
    print()
    print("Public Endpoints:")
    print("  GET  /api/build-showcase                    - List all published builds")
    print("  GET  /api/build-showcase/<build_id>         - Get build details")
    print("  POST /api/build-showcase/<build_id>/like    - Like a build")
    print("  POST /api/build-showcase/<build_id>/comment - Add comment")
    print("  GET  /api/build-showcase/<build_id>/export  - Export as markdown")
    print("  GET  /api/build-showcase/statistics         - Get build statistics")
    print("  POST /api/build-showcase/submit             - Submit new build")
    print()
    print("Admin Endpoints:")
    print("  POST   /api/admin/build-showcase            - Create build")
    print("  PUT    /api/admin/build-showcase/<build_id> - Update build")
    print("  DELETE /api/admin/build-showcase/<build_id> - Delete build")
    print("  GET    /api/admin/build-showcase/all        - List all builds")
    print()
    print("Example API Usage:")
    print("  curl http://localhost:5000/api/build-showcase")
    print("  curl http://localhost:5000/api/build-showcase/statistics")
    print("  curl -X POST http://localhost:5000/api/build-showcase/sample_rifleman_medic/like")


if __name__ == "__main__":
    try:
        demo_build_showcase_system()
        print()
        demo_api_endpoints()
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc() 
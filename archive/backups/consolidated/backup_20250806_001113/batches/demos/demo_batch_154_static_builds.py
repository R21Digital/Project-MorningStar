"""
Demo for Batch 154 - Static Builds Library

This script demonstrates the complete static builds library functionality:
- Creating sample builds with metadata
- Listing and filtering builds
- Searching builds
- Web interface integration
- CLI usage
- Statistics and reporting
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

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


def create_sample_builds():
    """Create sample builds to demonstrate the library."""
    library = get_static_builds_library()
    
    print("🎯 Creating sample builds...")
    
    # Sample 1: Rifleman/Medic Hybrid (AI Generated)
    rifleman_medic = StaticBuild(
        metadata=BuildMetadata(
            id="rifleman_medic_001",
            name="Rifleman/Medic Hybrid",
            description="Versatile combat build combining ranged damage with healing capabilities. Perfect for solo PvE content and group support roles.",
            author="SWGDB AI",
            source=BuildSource.AI_GENERATED,
            difficulty=BuildDifficulty.INTERMEDIATE,
            category=BuildCategory.COMBAT,
            specialization=BuildSpecialization.PVE,
            tags=["rifleman", "medic", "pve", "solo", "group", "healing", "ranged"]
        ),
        professions={
            "primary": "rifleman",
            "secondary": "medic"
        },
        skill_trees={
            "rifleman": SkillTree(
                profession="rifleman",
                skills=[
                    "combat_marksman_novice",
                    "combat_rifleman_novice",
                    "combat_rifleman_marksman",
                    "combat_rifleman_rifleman",
                    "combat_rifleman_sniper",
                    "combat_rifleman_master"
                ]
            ),
            "medic": SkillTree(
                profession="medic",
                skills=[
                    "science_medic_novice",
                    "science_medic_healing",
                    "science_medic_medicine",
                    "science_medic_doctor",
                    "science_medic_master"
                ]
            )
        },
        buff_priority=[
            "accuracy",
            "damage",
            "critical",
            "healing",
            "defense"
        ],
        weapon_type="rifle",
        equipment=EquipmentRecommendation(
            weapons={
                "primary": ["T21", "T21B", "E11"],
                "secondary": ["E11 Carbine", "DH17"]
            },
            armor={
                "head": ["Stormtrooper Helmet"],
                "chest": ["Stormtrooper Armor"],
                "legs": ["Stormtrooper Legs"],
                "feet": ["Stormtrooper Boots"]
            },
            tapes=["accuracy", "damage", "critical"],
            resists=["energy", "kinetic", "blast"],
            buffs=["Combat Stim", "Medical Stim"]
        ),
        performance=PerformanceRatings(
            pve_rating=8.5,
            pvp_rating=6.0,
            solo_rating=9.0,
            group_rating=8.0,
            farming_rating=7.5
        ),
        ratings=UserRatings(
            total_votes=12,
            average_rating=4.2,
            rating_breakdown={"5": 5, "4": 4, "3": 2, "2": 1, "1": 0},
            user_reviews=[
                {
                    "user_name": "CombatMedic",
                    "rating": 5,
                    "review": "Excellent hybrid build for solo play. Great survivability with healing abilities.",
                    "timestamp": "2025-01-15T10:30:00"
                },
                {
                    "user_name": "RifleMaster",
                    "rating": 4,
                    "review": "Solid build, good damage output and utility.",
                    "timestamp": "2025-01-14T15:45:00"
                }
            ]
        ),
        notes="This build excels in solo PvE content while providing valuable support in group situations. The combination of ranged damage and healing makes it very versatile.",
        links={
            "Skill Calculator": "https://swgdb.com/skills/rifleman",
            "Equipment Guide": "https://swgdb.com/equipment/rifleman",
            "Video Guide": "https://youtube.com/watch?v=example"
        }
    )
    
    # Sample 2: Pistoleer (Player Created)
    pistoleer = StaticBuild(
        metadata=BuildMetadata(
            id="pistoleer_agile_001",
            name="Agile Pistoleer",
            description="Fast-paced ranged combat build focusing on mobility and burst damage. Excellent for PvP and solo farming.",
            author="GunslingerPro",
            source=BuildSource.PLAYER_CREATED,
            difficulty=BuildDifficulty.ADVANCED,
            category=BuildCategory.COMBAT,
            specialization=BuildSpecialization.PVP,
            tags=["pistoleer", "pvp", "mobility", "burst", "agile", "ranged"]
        ),
        professions={
            "primary": "pistoleer"
        },
        skill_trees={
            "pistoleer": SkillTree(
                profession="pistoleer",
                skills=[
                    "combat_marksman_novice",
                    "combat_pistol_novice",
                    "combat_pistol_marksman",
                    "combat_pistol_pistoleer",
                    "combat_pistol_smuggler",
                    "combat_pistol_master"
                ]
            )
        },
        buff_priority=[
            "accuracy",
            "critical",
            "damage",
            "defense",
            "mobility"
        ],
        weapon_type="pistol",
        equipment=EquipmentRecommendation(
            weapons={
                "primary": ["DL44", "Power5", "SE14"],
                "secondary": ["E11 Carbine"]
            },
            armor={
                "head": ["Mandalorian Helmet"],
                "chest": ["Mandalorian Armor"],
                "legs": ["Mandalorian Legs"],
                "feet": ["Mandalorian Boots"]
            },
            tapes=["accuracy", "critical", "damage"],
            resists=["energy", "kinetic"],
            buffs=["Combat Stim", "Speed Stim"]
        ),
        performance=PerformanceRatings(
            pve_rating=7.0,
            pvp_rating=9.0,
            solo_rating=8.5,
            group_rating=6.5,
            farming_rating=8.0
        ),
        ratings=UserRatings(
            total_votes=8,
            average_rating=4.5,
            rating_breakdown={"5": 4, "4": 3, "3": 1, "2": 0, "1": 0},
            user_reviews=[
                {
                    "user_name": "PvPChampion",
                    "rating": 5,
                    "review": "Amazing PvP build! The mobility and burst damage are incredible.",
                    "timestamp": "2025-01-16T12:20:00"
                }
            ]
        ),
        notes="This build requires good positioning and timing. The high mobility allows for excellent kiting and escape options.",
        links={
            "PvP Guide": "https://swgdb.com/guides/pistoleer-pvp",
            "Skill Calculator": "https://swgdb.com/skills/pistoleer"
        }
    )
    
    # Sample 3: Artisan Crafter (Community Submitted)
    artisan = StaticBuild(
        metadata=BuildMetadata(
            id="artisan_crafter_001",
            name="Master Artisan",
            description="Comprehensive crafting build for resource gathering and item creation. Optimized for efficiency and quality.",
            author="CraftMaster",
            source=BuildSource.COMMUNITY_SUBMITTED,
            difficulty=BuildDifficulty.BEGINNER,
            category=BuildCategory.CRAFTING,
            specialization=BuildSpecialization.CRAFTING,
            tags=["artisan", "crafting", "gathering", "resources", "efficiency"]
        ),
        professions={
            "primary": "artisan"
        },
        skill_trees={
            "artisan": SkillTree(
                profession="artisan",
                skills=[
                    "crafting_artisan_novice",
                    "crafting_artisan_engineering",
                    "crafting_artisan_domestic",
                    "crafting_artisan_business",
                    "crafting_artisan_master"
                ]
            )
        },
        buff_priority=[
            "crafting",
            "efficiency",
            "quality",
            "speed"
        ],
        weapon_type="pistol",
        equipment=EquipmentRecommendation(
            weapons={
                "primary": ["DL44", "Power5"]
            },
            armor={
                "head": ["Crafting Helmet"],
                "chest": ["Crafting Vest"],
                "legs": ["Crafting Pants"],
                "feet": ["Crafting Boots"]
            },
            tapes=["crafting", "efficiency"],
            resists=["energy"],
            buffs=["Crafting Stim", "Efficiency Stim"]
        ),
        performance=PerformanceRatings(
            pve_rating=5.0,
            pvp_rating=2.0,
            solo_rating=8.0,
            group_rating=6.0,
            farming_rating=9.0
        ),
        ratings=UserRatings(
            total_votes=15,
            average_rating=4.8,
            rating_breakdown={"5": 10, "4": 4, "3": 1, "2": 0, "1": 0},
            user_reviews=[
                {
                    "user_name": "ResourceGatherer",
                    "rating": 5,
                    "review": "Perfect for resource gathering and crafting. Very efficient build.",
                    "timestamp": "2025-01-17T09:15:00"
                },
                {
                    "user_name": "CraftingPro",
                    "rating": 5,
                    "review": "Excellent crafting build. Highly recommended for artisans.",
                    "timestamp": "2025-01-16T14:30:00"
                }
            ]
        ),
        notes="This build is optimized for crafting efficiency and resource gathering. While not combat-focused, it excels in its specialized role.",
        links={
            "Crafting Guide": "https://swgdb.com/guides/artisan-crafting",
            "Resource Locations": "https://swgdb.com/resources/locations"
        }
    )
    
    # Create the builds
    builds = [rifleman_medic, pistoleer, artisan]
    
    for build in builds:
        if library.create_build(build):
            print(f"✅ Created: {build.metadata.name}")
        else:
            print(f"❌ Failed to create: {build.metadata.name}")
    
    print(f"\n📚 Created {len(builds)} sample builds")
    return builds


def demonstrate_listing():
    """Demonstrate build listing and filtering."""
    library = get_static_builds_library()
    
    print("\n📋 Demonstrating build listing...")
    
    # List all builds
    print("\n🔸 All builds:")
    all_builds = library.list_builds()
    for build in all_builds:
        print(f"  - {build.metadata.name} ({build.metadata.category.value})")
    
    # Filter by category
    print("\n🔸 Combat builds:")
    combat_builds = library.list_builds(category=BuildCategory.COMBAT)
    for build in combat_builds:
        print(f"  - {build.metadata.name}")
    
    # Filter by difficulty
    print("\n🔸 Advanced builds:")
    advanced_builds = library.list_builds(difficulty=BuildDifficulty.ADVANCED)
    for build in advanced_builds:
        print(f"  - {build.metadata.name}")
    
    # Filter by specialization
    print("\n🔸 PvE builds:")
    pve_builds = library.list_builds(specialization=BuildSpecialization.PVE)
    for build in pve_builds:
        print(f"  - {build.metadata.name}")


def demonstrate_searching():
    """Demonstrate build searching."""
    library = get_static_builds_library()
    
    print("\n🔍 Demonstrating build searching...")
    
    # Search for rifleman builds
    print("\n🔸 Searching for 'rifleman':")
    rifleman_builds = library.search_builds("rifleman")
    for build in rifleman_builds:
        print(f"  - {build.metadata.name}")
    
    # Search for PvP builds
    print("\n🔸 Searching for 'pvp':")
    pvp_builds = library.search_builds("pvp")
    for build in pvp_builds:
        print(f"  - {build.metadata.name}")
    
    # Search for crafting builds
    print("\n🔸 Searching for 'crafting':")
    crafting_builds = library.search_builds("crafting")
    for build in crafting_builds:
        print(f"  - {build.metadata.name}")


def demonstrate_statistics():
    """Demonstrate statistics and reporting."""
    library = get_static_builds_library()
    
    print("\n📊 Demonstrating statistics...")
    
    stats = library.get_statistics()
    
    print(f"\n📚 Total Builds: {stats['total_builds']}")
    
    print("\n📂 Categories:")
    for category, count in stats['categories'].items():
        print(f"  - {category.title()}: {count}")
    
    print("\n📈 Difficulties:")
    for difficulty, count in stats['difficulties'].items():
        print(f"  - {difficulty.title()}: {count}")
    
    print("\n🎯 Specializations:")
    for specialization, count in stats['specializations'].items():
        print(f"  - {specialization.upper()}: {count}")
    
    print("\n📝 Sources:")
    for source, count in stats['sources'].items():
        source_name = source.replace('_', ' ').title()
        print(f"  - {source_name}: {count}")


def demonstrate_web_integration():
    """Demonstrate web integration features."""
    print("\n🌐 Web Integration Features:")
    print("  - Public builds section at /builds/")
    print("  - Individual build pages at /builds/{build_id}")
    print("  - API endpoints for programmatic access")
    print("  - User ratings and reviews system")
    print("  - Search and filtering capabilities")
    print("  - Responsive design for mobile devices")
    print("  - Markdown file generation for each build")
    print("  - 'Generated by SWGDB' attribution for AI builds")


def demonstrate_cli_usage():
    """Demonstrate CLI usage."""
    print("\n💻 CLI Usage Examples:")
    print("  python cli/static_builds_cli.py create --build-id my_build --name 'My Build'")
    print("  python cli/static_builds_cli.py list --category combat")
    print("  python cli/static_builds_cli.py view rifleman_medic_001")
    print("  python cli/static_builds_cli.py search 'rifleman'")
    print("  python cli/static_builds_cli.py update rifleman_medic_001 --pve-rating 9.0")
    print("  python cli/static_builds_cli.py stats")


def demonstrate_markdown_generation():
    """Demonstrate markdown file generation."""
    library = get_static_builds_library()
    
    print("\n📝 Markdown File Generation:")
    
    # Check if markdown files were created
    builds_dir = Path("builds")
    if builds_dir.exists():
        md_files = list(builds_dir.glob("*.md"))
        print(f"  - Generated {len(md_files)} markdown files:")
        for md_file in md_files:
            print(f"    * {md_file.name}")
    else:
        print("  - No builds directory found")


def demonstrate_database_integration():
    """Demonstrate database integration."""
    print("\n💾 Database Integration:")
    
    # Check if database file was created
    db_file = Path("data/static_builds_database.json")
    if db_file.exists():
        with open(db_file, 'r') as f:
            data = json.load(f)
        
        print(f"  - Database file: {db_file}")
        print(f"  - Total builds in database: {data['metadata']['total_builds']}")
        print(f"  - Last updated: {data['metadata']['last_updated']}")
    else:
        print("  - Database file not found")


def main():
    """Main demo function."""
    print("🚀 Batch 154 - Static Builds Library Demo")
    print("=" * 50)
    
    # Create sample builds
    builds = create_sample_builds()
    
    # Demonstrate features
    demonstrate_listing()
    demonstrate_searching()
    demonstrate_statistics()
    demonstrate_web_integration()
    demonstrate_cli_usage()
    demonstrate_markdown_generation()
    demonstrate_database_integration()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("\n📋 Summary:")
    print(f"  - Created {len(builds)} sample builds")
    print("  - Web interface available at /builds/")
    print("  - CLI tool available at cli/static_builds_cli.py")
    print("  - Markdown files generated in builds/ directory")
    print("  - Database updated in data/static_builds_database.json")
    print("\n🎯 Key Features:")
    print("  - Public SWGDB builds section")
    print("  - Static build profiles with metadata")
    print("  - Profession and skill tree information")
    print("  - Buff priority and weapon type details")
    print("  - Performance ratings and user votes")
    print("  - 'Generated by SWGDB' attribution")
    print("  - Links to skill calculators")
    print("  - Community ratings and reviews")


if __name__ == "__main__":
    main() 
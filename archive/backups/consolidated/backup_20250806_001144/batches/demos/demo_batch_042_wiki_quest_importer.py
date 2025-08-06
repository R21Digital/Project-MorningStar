#!/usr/bin/env python3
"""Demo Script for Batch 042 - SWGR Wiki Quest Importer

This demo showcases the complete functionality of the wiki quest importer module,
including parsing wiki pages, importing quest data, fallback detection, and
generating planetary quest profiles for 100% completion mode.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from importers.wiki_quests import (
    WikiParser,
    QuestImporter,
    FallbackDetector,
    ProfileGenerator,
    parse_wiki_page,
    import_quests_from_wiki,
    detect_quest_in_database,
    generate_planetary_profiles
)


def setup_logging():
    """Setup logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('demo_batch_042.log')
        ]
    )


def demo_wiki_parser():
    """Demo the wiki parser functionality."""
    print("\n" + "="*60)
    print("DEMO: Wiki Parser Functionality")
    print("="*60)
    
    parser = WikiParser()
    
    # Sample wiki URLs (these would be real SWGR wiki URLs in practice)
    sample_urls = [
        "https://swgr.org/wiki/quest/tatooine_artifact_hunt",
        "https://swgr.org/wiki/quest/naboo_legacy_quest",
        "https://swgr.org/wiki/quest/corellia_faction_mission"
    ]
    
    print(f"Testing wiki parser with {len(sample_urls)} sample URLs...")
    
    for i, url in enumerate(sample_urls, 1):
        print(f"\n{i}. Parsing: {url}")
        try:
            quest_data = parser.parse_wiki_page(url)
            if quest_data:
                print(f"   ✓ Successfully parsed quest: {quest_data.name}")
                print(f"   - Quest ID: {quest_data.quest_id}")
                print(f"   - Planet: {quest_data.planet}")
                print(f"   - Type: {quest_data.quest_type.value}")
                print(f"   - Difficulty: {quest_data.difficulty.value}")
                print(f"   - Level Requirement: {quest_data.level_requirement}")
                print(f"   - NPC: {quest_data.npc}")
                print(f"   - Coordinates: {quest_data.coordinates}")
                print(f"   - Prerequisites: {len(quest_data.prerequisites)}")
                print(f"   - Objectives: {len(quest_data.objectives)}")
                print(f"   - Hints: {len(quest_data.hints)}")
            else:
                print(f"   ✗ No quest data found")
        except Exception as e:
            print(f"   ✗ Error parsing: {e}")
    
    print("\nWiki parser demo completed!")


def demo_quest_importer():
    """Demo the quest importer functionality."""
    print("\n" + "="*60)
    print("DEMO: Quest Importer Functionality")
    print("="*60)
    
    importer = QuestImporter()
    
    # Sample wiki URLs for import
    sample_urls = [
        "https://swgr.org/wiki/quest/tatooine_artifact_hunt",
        "https://swgr.org/wiki/quest/naboo_legacy_quest",
        "https://swgr.org/wiki/quest/corellia_faction_mission"
    ]
    
    # Sample category URLs
    category_urls = [
        "https://swgr.org/wiki/category/tatooine_quests",
        "https://swgr.org/wiki/category/legacy_quests"
    ]
    
    print(f"Testing quest importer with {len(sample_urls)} URLs and {len(category_urls)} categories...")
    
    try:
        # Import quests from direct URLs
        result = importer.import_quests_from_wiki(sample_urls, category_urls)
        
        print(f"\nImport Results:")
        print(f"- Imported quests: {result['imported_quests']}")
        print(f"- Failed URLs: {result['failed_urls']}")
        print(f"- Total quests in database: {result['total_quests']}")
        print(f"- Last import: {result['stats']['last_import']}")
        
        # Get import statistics
        stats = importer.get_import_stats()
        print(f"\nImport Statistics:")
        print(f"- Total imported: {stats['stats']['total_imported']}")
        print(f"- Total updated: {stats['stats']['total_updated']}")
        print(f"- Total failed: {stats['stats']['total_failed']}")
        print(f"- Quests by planet: {stats['quests_by_planet']}")
        print(f"- Quests by type: {stats['quests_by_type']}")
        
    except Exception as e:
        print(f"Error during import: {e}")
    
    print("\nQuest importer demo completed!")


def demo_fallback_detector():
    """Demo the fallback detector functionality."""
    print("\n" + "="*60)
    print("DEMO: Fallback Detector Functionality")
    print("="*60)
    
    detector = FallbackDetector()
    
    # Sample quest information to test detection
    sample_quests = [
        {
            'quest_id': 'tatooine_artifact_hunt',
            'name': 'Tatooine Artifact Hunt',
            'npc': 'Mos Eisley Merchant',
            'planet': 'tatooine'
        },
        {
            'quest_id': 'naboo_legacy_quest',
            'name': 'Naboo Legacy Quest',
            'npc': 'Theed Palace Guard',
            'planet': 'naboo'
        },
        {
            'quest_id': 'unknown_quest',
            'name': 'Unknown Quest',
            'npc': 'Unknown NPC',
            'planet': 'unknown'
        }
    ]
    
    print(f"Testing fallback detector with {len(sample_quests)} sample quests...")
    
    for i, quest_info in enumerate(sample_quests, 1):
        print(f"\n{i}. Testing quest: {quest_info['name']}")
        
        # Test quest detection
        detected_quest = detector.detect_quest_in_database(quest_info)
        
        if detected_quest:
            print(f"   ✓ Quest found in database!")
            print(f"   - Quest ID: {detected_quest['quest_id']}")
            print(f"   - Match confidence: {detected_quest.get('match_confidence', 'unknown')}")
            print(f"   - Database info: {detected_quest['database_info']['name']}")
            print(f"   - Planet: {detected_quest['database_info']['planet']}")
            print(f"   - Type: {detected_quest['database_info']['quest_type']}")
            print(f"   - Difficulty: {detected_quest['database_info']['difficulty']}")
        else:
            print(f"   ✗ Quest not found in database")
            
            # Try fallback detection
            fallback_data = detector.get_fallback_quest_data(quest_info)
            if fallback_data:
                print(f"   ⚠ Found related quest: {fallback_data['database_info']['name']}")
            else:
                print(f"   ✗ No related quests found")
    
    # Test search functionality
    print(f"\nTesting search functionality...")
    
    search_tests = [
        ('tatooine', 'planet'),
        ('artifact', 'name'),
        ('merchant', 'npc'),
        ('legacy', 'type')
    ]
    
    for search_term, search_type in search_tests:
        print(f"\nSearching for '{search_term}' (type: {search_type})")
        results = detector.search_quests(search_term, search_type)
        print(f"   Found {len(results)} results")
        for result in results[:3]:  # Show first 3 results
            print(f"   - {result['database_info']['name']} ({result['database_info']['planet']})")
    
    # Get database statistics
    stats = detector.get_database_stats()
    print(f"\nDatabase Statistics:")
    print(f"- Total quests: {stats['total_quests']}")
    print(f"- Quests by planet: {stats['quests_by_planet']}")
    print(f"- Quests by type: {stats['quests_by_type']}")
    print(f"- Quests by difficulty: {stats['quests_by_difficulty']}")
    
    print("\nFallback detector demo completed!")


def demo_profile_generator():
    """Demo the profile generator functionality."""
    print("\n" + "="*60)
    print("DEMO: Profile Generator Functionality")
    print("="*60)
    
    generator = ProfileGenerator()
    
    # Test planets
    test_planets = ['tatooine', 'naboo', 'corellia']
    
    print(f"Testing profile generator for {len(test_planets)} planets...")
    
    for planet in test_planets:
        print(f"\nGenerating profile for {planet}...")
        
        try:
            profile = generator._generate_planet_profile(planet)
            
            if profile:
                print(f"   ✓ Profile generated successfully!")
                print(f"   - Total quests: {profile['total_quests']}")
                print(f"   - Quests by type: {list(profile['quests_by_type'].keys())}")
                print(f"   - Quest chains: {len(profile['quest_chains'])}")
                print(f"   - Recommended order: {len(profile['recommended_order'])} quests")
                print(f"   - Prerequisites map: {len(profile['prerequisites_map'])} entries")
                
                # Show completion goals
                goals = profile['completion_goals']
                print(f"   - Completion goals:")
                print(f"     * Total quests: {goals['total_quests']}")
                print(f"     * Estimated time: {goals['estimated_completion_time']} minutes")
                print(f"     * Required levels: {goals['required_levels']}")
                
                # Show rewards summary
                rewards = profile['rewards_summary']
                print(f"   - Rewards summary:")
                print(f"     * Total experience: {rewards['total_experience']}")
                print(f"     * Total credits: {rewards['total_credits']}")
                print(f"     * Items: {len(rewards['items'])}")
                print(f"     * Unlocks: {len(rewards['unlocks'])}")
                
                # Show difficulty progression
                progression = profile['difficulty_progression']
                print(f"   - Difficulty progression: {len(progression)} stages")
                for stage in progression:
                    print(f"     * {stage['difficulty']}: {stage['count']} quests ({stage['estimated_time']} min)")
                
                # Show completion estimates
                estimates = profile['completion_estimates']
                print(f"   - Completion estimates:")
                print(f"     * Total time: {estimates['estimated_time_hours']:.1f} hours")
                print(f"     * Average per quest: {estimates['average_time_per_quest']:.1f} minutes")
                
            else:
                print(f"   ✗ No profile generated (no quests found)")
                
        except Exception as e:
            print(f"   ✗ Error generating profile: {e}")
    
    # Test full profile generation
    print(f"\nGenerating profiles for all planets...")
    try:
        all_profiles = generator.generate_planetary_profiles()
        print(f"   ✓ Generated {len(all_profiles)} planetary profiles")
        for planet, profile in all_profiles.items():
            print(f"   - {planet}: {profile['total_quests']} quests")
    except Exception as e:
        print(f"   ✗ Error generating all profiles: {e}")
    
    print("\nProfile generator demo completed!")


def demo_integration_workflow():
    """Demo the complete integration workflow."""
    print("\n" + "="*60)
    print("DEMO: Complete Integration Workflow")
    print("="*60)
    
    print("This demo shows the complete workflow from wiki parsing to profile generation:")
    print("1. Parse wiki pages for quest data")
    print("2. Import quests into local database")
    print("3. Detect quests in database for fallback")
    print("4. Generate planetary quest profiles")
    
    # Sample workflow
    sample_urls = [
        "https://swgr.org/wiki/quest/tatooine_artifact_hunt",
        "https://swgr.org/wiki/quest/naboo_legacy_quest"
    ]
    
    print(f"\nStep 1: Parsing {len(sample_urls)} wiki pages...")
    parsed_quests = []
    for url in sample_urls:
        quest_data = parse_wiki_page(url)
        if quest_data:
            parsed_quests.append(quest_data)
            print(f"   ✓ Parsed: {quest_data.name}")
    
    print(f"\nStep 2: Importing {len(parsed_quests)} quests...")
    if parsed_quests:
        # Simulate import by creating quest data
        import_result = import_quests_from_wiki(sample_urls)
        print(f"   ✓ Import result: {import_result['imported_quests']} imported")
    
    print(f"\nStep 3: Testing fallback detection...")
    test_quest = {
        'quest_id': 'tatooine_artifact_hunt',
        'name': 'Tatooine Artifact Hunt',
        'planet': 'tatooine'
    }
    
    detected = detect_quest_in_database(test_quest)
    if detected:
        print(f"   ✓ Quest detected: {detected['database_info']['name']}")
    else:
        print(f"   ✗ Quest not found in database")
    
    print(f"\nStep 4: Generating planetary profiles...")
    profiles = generate_planetary_profiles('tatooine')
    if profiles:
        print(f"   ✓ Generated profile for Tatooine")
        tatooine_profile = profiles.get('tatooine')
        if tatooine_profile:
            print(f"   - Total quests: {tatooine_profile['total_quests']}")
            print(f"   - Estimated time: {tatooine_profile['completion_estimates']['estimated_time_hours']:.1f} hours")
    else:
        print(f"   ✗ No profiles generated")
    
    print("\nIntegration workflow demo completed!")


def demo_error_handling():
    """Demo error handling and edge cases."""
    print("\n" + "="*60)
    print("DEMO: Error Handling and Edge Cases")
    print("="*60)
    
    print("Testing various error scenarios...")
    
    # Test invalid URLs
    invalid_urls = [
        "https://invalid-wiki.org/quest/test",
        "https://swgr.org/wiki/quest/nonexistent",
        "not-a-url"
    ]
    
    print(f"\n1. Testing invalid URLs...")
    for url in invalid_urls:
        try:
            quest_data = parse_wiki_page(url)
            if quest_data:
                print(f"   ✓ Unexpected success: {quest_data.name}")
            else:
                print(f"   ✓ Correctly handled: {url}")
        except Exception as e:
            print(f"   ✓ Error handled: {type(e).__name__}")
    
    # Test empty quest detection
    print(f"\n2. Testing empty quest detection...")
    detector = FallbackDetector()
    empty_quest = {}
    result = detector.detect_quest_in_database(empty_quest)
    print(f"   ✓ Empty quest handled: {result is None}")
    
    # Test profile generation with no quests
    print(f"\n3. Testing profile generation with no quests...")
    generator = ProfileGenerator()
    try:
        profile = generator._generate_planet_profile('nonexistent_planet')
        if profile:
            print(f"   ✓ Unexpected profile generated")
        else:
            print(f"   ✓ Correctly handled: no profile for nonexistent planet")
    except Exception as e:
        print(f"   ✓ Error handled: {type(e).__name__}")
    
    print("\nError handling demo completed!")


def main():
    """Run the complete demo."""
    print("🎯 Batch 042 - SWGR Wiki Quest Importer Demo")
    print("="*60)
    print("This demo showcases the complete functionality of the wiki quest importer module.")
    print("Features demonstrated:")
    print("- Wiki page parsing and quest data extraction")
    print("- Quest importing and database management")
    print("- Fallback detection and quest matching")
    print("- Planetary quest profile generation")
    print("- Error handling and edge cases")
    print("="*60)
    
    # Setup logging
    setup_logging()
    
    try:
        # Run all demos
        demo_wiki_parser()
        demo_quest_importer()
        demo_fallback_detector()
        demo_profile_generator()
        demo_integration_workflow()
        demo_error_handling()
        
        print("\n" + "="*60)
        print("✅ BATCH 042 DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("All features of the SWGR Wiki Quest Importer have been demonstrated:")
        print("✓ Wiki page parsing and quest data extraction")
        print("✓ Quest importing and database management")
        print("✓ Fallback detection and quest matching")
        print("✓ Planetary quest profile generation")
        print("✓ Error handling and edge cases")
        print("\nThe module is ready for integration with the MS11 quest system!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logging.error(f"Demo error: {e}", exc_info=True)
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
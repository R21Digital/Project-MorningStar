"""Demo script for Batch 104 - MTG Repo Knowledge Miner.

This script demonstrates the functionality of the MTG Knowledge Miner,
including crawling, extraction, and integration capabilities.
"""

import json
import time
from datetime import datetime
from pathlib import Path

from core.mtg_knowledge_miner import (
    MTGKnowledgeMiner,
    KnowledgeEntry,
    KnowledgeType,
    SourceType,
    run_mtg_knowledge_crawl,
    get_mtg_knowledge_by_type,
    search_mtg_knowledge,
    get_mtg_crawl_stats
)
from core.mtg_knowledge_integration import (
    MTGKnowledgeIntegration,
    KnowledgeIntegration,
    IntegrationType,
    IntegrationStatus,
    run_mtg_knowledge_integration,
    get_mtg_integration_stats,
    get_mtg_knowledge_layer,
    search_mtg_knowledge_layer
)


def demo_knowledge_mining():
    """Demonstrate knowledge mining capabilities."""
    print("=" * 60)
    print("MTG KNOWLEDGE MINER DEMO")
    print("=" * 60)
    
    # Initialize miner
    miner = MTGKnowledgeMiner(data_dir="data/knowledge_imports")
    print(f"✓ MTG Knowledge Miner initialized")
    print(f"  Data directory: {miner.data_dir}")
    print(f"  Knowledge types: {len(miner.knowledge_entries)}")
    print()
    
    # Demonstrate file classification
    print("File Classification Examples:")
    test_files = [
        ("quest_logic.py", "quests/quest_logic.py"),
        ("crafting_recipes.txt", "crafting/recipes/"),
        ("combat_weapons.py", "combat/weapons/"),
        ("item_database.json", "data/items/"),
        ("npc_spawns.yaml", "data/npcs/"),
        ("location_data.csv", "data/locations/"),
        ("system_config.ini", "config/system/"),
        ("unknown_file.txt", "random/path/")
    ]
    
    for file_name, file_path in test_files:
        knowledge_type = miner._classify_file_knowledge_type(file_name, file_path)
        status = "✓" if knowledge_type else "✗"
        type_name = knowledge_type.value if knowledge_type else "None"
        print(f"  {status} {file_name:<20} -> {type_name}")
    
    print()
    
    # Demonstrate content extraction
    print("Content Extraction Examples:")
    
    quest_content = "Quest ID 12345, Mission Type: Escort, Reward: 500 credits, Prerequisite: Level 10"
    quest_result = miner._extract_quest_logic(quest_content, "quest_file.txt")
    print(f"  Quest Logic: {quest_result['confidence']:.1f} confidence, {len(quest_result['tags'])} tags")
    
    crafting_content = "Craft Level 5, Recipe: Advanced Armor, Resource: Durasteel, Quality: 85"
    crafting_result = miner._extract_crafting_stats(crafting_content, "crafting.txt")
    print(f"  Crafting Stats: {crafting_result['confidence']:.1f} confidence, {len(crafting_result['tags'])} tags")
    
    combat_content = "Damage: 150, Weapon: Rifle, Armor: Composite, Attack: Ranged"
    combat_result = miner._extract_combat_data(combat_content, "combat.txt")
    print(f"  Combat Data: {combat_result['confidence']:.1f} confidence, {len(combat_result['tags'])} tags")
    
    print()
    
    # Demonstrate ID generation
    print("Entry ID Generation:")
    id1 = miner._generate_entry_id("https://github.com/test1", "Quest File 1")
    id2 = miner._generate_entry_id("https://github.com/test2", "Quest File 2")
    id3 = miner._generate_entry_id("https://github.com/test1", "Quest File 1")
    
    print(f"  Source 1 + Title 1: {id1}")
    print(f"  Source 2 + Title 2: {id2}")
    print(f"  Source 1 + Title 1: {id3} (should match first)")
    print(f"  IDs match: {id1 == id3}")
    
    print()


def demo_knowledge_integration():
    """Demonstrate knowledge integration capabilities."""
    print("=" * 60)
    print("MTG KNOWLEDGE INTEGRATION DEMO")
    print("=" * 60)
    
    # Initialize integration
    integration = MTGKnowledgeIntegration(data_dir="data/knowledge_imports")
    print(f"✓ MTG Knowledge Integration initialized")
    print(f"  Data directory: {integration.data_dir}")
    print(f"  Integration mappings: {len(integration.integration_mappings)}")
    print()
    
    # Demonstrate integration mappings
    print("Integration Mappings:")
    for knowledge_type, mapping in integration.integration_mappings.items():
        print(f"  {knowledge_type.value:<15} -> {mapping['target_system']:<15} (threshold: {mapping['confidence_threshold']})")
    
    print()
    
    # Create test knowledge entries
    print("Creating Test Knowledge Entries:")
    
    test_entries = [
        KnowledgeEntry(
            id="demo_quest_1",
            knowledge_type=KnowledgeType.QUEST_LOGIC,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://github.com/ModTheGalaxy/mtgserver/quests/escort_mission.py",
            title="Escort Mission Logic",
            content="Quest ID 12345, Mission Type: Escort, Reward: 500 credits, Prerequisite: Level 10, NPC: Security Guard",
            metadata={"repo": "mtgserver", "path": "quests/escort_mission.py"},
            extracted_at=datetime.now(),
            confidence_score=0.9,
            tags=["quest", "escort", "mtg"]
        ),
        KnowledgeEntry(
            id="demo_crafting_1",
            knowledge_type=KnowledgeType.CRAFTING_STATS,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://github.com/ModTheGalaxy/mtgserver/crafting/armor_recipes.py",
            title="Armor Crafting Recipes",
            content="Craft Level 5, Recipe: Advanced Armor, Resource: Durasteel, Quality: 85, Crafting Time: 2 hours",
            metadata={"repo": "mtgserver", "path": "crafting/armor_recipes.py"},
            extracted_at=datetime.now(),
            confidence_score=0.8,
            tags=["crafting", "armor", "mtg"]
        ),
        KnowledgeEntry(
            id="demo_combat_1",
            knowledge_type=KnowledgeType.COMBAT_DATA,
            source_type=SourceType.FORUM_POST,
            source_url="https://modthegalaxy.com/forums/combat-discussion/weapon-stats",
            title="Weapon Combat Statistics",
            content="Damage: 150, Weapon: Rifle, Armor: Composite, Attack: Ranged, Range: 50 meters",
            metadata={"forum": "combat-discussion", "thread": "weapon-stats"},
            extracted_at=datetime.now(),
            confidence_score=0.7,
            tags=["combat", "weapon", "mtg"]
        )
    ]
    
    for i, entry in enumerate(test_entries, 1):
        print(f"  {i}. {entry.title} ({entry.knowledge_type.value})")
        print(f"     Confidence: {entry.confidence_score:.1f}")
        print(f"     Source: {entry.source_type.value}")
        print(f"     Tags: {', '.join(entry.tags)}")
    
    print()
    
    # Demonstrate integration processing
    print("Integration Processing:")
    
    for entry in test_entries:
        integration_result = integration.integrate_knowledge_entry(entry)
        
        if integration_result:
            status_icon = "✓" if integration_result.status == IntegrationStatus.INTEGRATED else "✗"
            print(f"  {status_icon} {entry.title}")
            print(f"     Status: {integration_result.status.value}")
            print(f"     Target System: {integration_result.target_system}")
            print(f"     Confidence: {integration_result.confidence_score:.1f}")
        else:
            print(f"  ✗ {entry.title} (rejected)")
    
    print()
    
    # Demonstrate knowledge layer
    print("Knowledge Layer Contents:")
    knowledge_layer = integration.get_knowledge_layer()
    
    for system_name, system_data in knowledge_layer.items():
        print(f"  {system_name}:")
        if 'data' in system_data:
            for data_type, patterns in system_data['data'].items():
                if patterns:
                    print(f"    {data_type}: {len(patterns)} patterns")
                    if len(patterns) <= 3:  # Show first few patterns
                        for pattern in patterns[:3]:
                            print(f"      - {pattern}")
                    else:
                        print(f"      - {patterns[0]}, {patterns[1]}, ... ({len(patterns)} total)")
    
    print()


def demo_search_functionality():
    """Demonstrate search functionality."""
    print("=" * 60)
    print("SEARCH FUNCTIONALITY DEMO")
    print("=" * 60)
    
    # Initialize components
    miner = MTGKnowledgeMiner(data_dir="data/knowledge_imports")
    integration = MTGKnowledgeIntegration(data_dir="data/knowledge_imports")
    
    # Add some test data for searching
    test_entries = [
        KnowledgeEntry(
            id="search_quest_1",
            knowledge_type=KnowledgeType.QUEST_LOGIC,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://github.com/test/quest1",
            title="Escort Mission Quest",
            content="Quest ID 12345, Mission Type: Escort, Reward: 500 credits",
            metadata={},
            extracted_at=datetime.now(),
            confidence_score=0.8,
            tags=["quest", "escort"]
        ),
        KnowledgeEntry(
            id="search_crafting_1",
            knowledge_type=KnowledgeType.CRAFTING_STATS,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://github.com/test/crafting1",
            title="Advanced Armor Crafting",
            content="Craft Level 5, Recipe: Advanced Armor, Resource: Durasteel",
            metadata={},
            extracted_at=datetime.now(),
            confidence_score=0.8,
            tags=["crafting", "armor"]
        )
    ]
    
    # Add to miner
    for entry in test_entries:
        if entry.knowledge_type not in miner.knowledge_entries:
            miner.knowledge_entries[entry.knowledge_type] = []
        miner.knowledge_entries[entry.knowledge_type].append(entry)
    
    # Demonstrate knowledge search
    print("Knowledge Search Examples:")
    
    search_queries = [
        "Escort",
        "Armor",
        "Quest",
        "Crafting",
        "nonexistent"
    ]
    
    for query in search_queries:
        results = miner.search_knowledge(query)
        print(f"  '{query}': {len(results)} results")
        for result in results[:2]:  # Show first 2 results
            print(f"    - {result.title} ({result.knowledge_type.value})")
    
    print()
    
    # Demonstrate knowledge layer search
    print("Knowledge Layer Search Examples:")
    
    # Add some data to knowledge layer
    integration.knowledge_layer['quest_engine'] = {
        'data': {
            'quest_patterns': ['12345', '67890'],
            'mission_types': ['Escort', 'Defend', 'Collect']
        }
    }
    integration.knowledge_layer['crafting_system'] = {
        'data': {
            'craft_levels': ['5', '10', '15'],
            'recipe_patterns': ['Advanced Armor', 'Basic Weapon']
        }
    }
    
    layer_search_queries = [
        ("12345", None),
        ("Escort", "quest_engine"),
        ("Armor", "crafting_system"),
        ("Advanced", None)
    ]
    
    for query, system in layer_search_queries:
        results = integration.search_knowledge_layer(query, system)
        print(f"  '{query}' in {system or 'all systems'}: {len(results)} systems")
        for system_name, system_results in results.items():
            for data_type, patterns in system_results.items():
                print(f"    {system_name}.{data_type}: {len(patterns)} matches")
    
    print()


def demo_statistics():
    """Demonstrate statistics and monitoring."""
    print("=" * 60)
    print("STATISTICS AND MONITORING DEMO")
    print("=" * 60)
    
    # Initialize components
    miner = MTGKnowledgeMiner(data_dir="data/knowledge_imports")
    integration = MTGKnowledgeIntegration(data_dir="data/knowledge_imports")
    
    # Add some test data
    test_entries = []
    for i in range(5):
        entry = KnowledgeEntry(
            id=f"stats_test_{i}",
            knowledge_type=KnowledgeType.QUEST_LOGIC,
            source_type=SourceType.GITHUB_REPO,
            source_url=f"https://github.com/test/stats_{i}",
            title=f"Test Quest {i}",
            content=f"Quest ID {i}, Mission Type: Test",
            metadata={},
            extracted_at=datetime.now(),
            confidence_score=0.8,
            tags=["test", "stats"]
        )
        test_entries.append(entry)
    
    # Add to miner
    miner.knowledge_entries[KnowledgeType.QUEST_LOGIC] = test_entries
    
    # Demonstrate crawl statistics
    print("Crawl Statistics:")
    crawl_stats = miner.get_crawl_stats()
    for key, value in crawl_stats.items():
        print(f"  {key}: {value}")
    
    print()
    
    # Demonstrate integration statistics
    print("Integration Statistics:")
    integration_stats = integration.get_integration_stats()
    for key, value in integration_stats.items():
        print(f"  {key}: {value}")
    
    print()
    
    # Demonstrate knowledge type distribution
    print("Knowledge Type Distribution:")
    all_knowledge = miner.get_all_knowledge()
    for knowledge_type, entries in all_knowledge.items():
        print(f"  {knowledge_type.value}: {len(entries)} entries")
    
    print()


def demo_full_workflow():
    """Demonstrate the complete workflow."""
    print("=" * 60)
    print("COMPLETE WORKFLOW DEMO")
    print("=" * 60)
    
    print("Step 1: Initialize Components")
    miner = MTGKnowledgeMiner(data_dir="data/knowledge_imports")
    integration = MTGKnowledgeIntegration(data_dir="data/knowledge_imports")
    print("✓ Components initialized")
    
    print("\nStep 2: Create Sample Knowledge Entries")
    sample_entries = [
        KnowledgeEntry(
            id="workflow_quest_1",
            knowledge_type=KnowledgeType.QUEST_LOGIC,
            source_type=SourceType.GITHUB_REPO,
            source_url="https://github.com/ModTheGalaxy/mtgserver/quests/heroic_mission.py",
            title="Heroic Mission Quest",
            content="Quest ID 99999, Mission Type: Heroic, Reward: 2000 credits, Prerequisite: Level 50, NPC: Jedi Master",
            metadata={"repo": "mtgserver", "path": "quests/heroic_mission.py"},
            extracted_at=datetime.now(),
            confidence_score=0.9,
            tags=["quest", "heroic", "jedi", "mtg"]
        ),
        KnowledgeEntry(
            id="workflow_crafting_1",
            knowledge_type=KnowledgeType.CRAFTING_STATS,
            source_type=SourceType.FORUM_POST,
            source_url="https://modthegalaxy.com/forums/crafting-discussion/master-craftsman-recipes",
            title="Master Craftsman Recipes",
            content="Craft Level 10, Recipe: Master Armor, Resource: Beskar, Quality: 95, Crafting Time: 4 hours, Success Rate: 85%",
            metadata={"forum": "crafting-discussion", "thread": "master-craftsman-recipes"},
            extracted_at=datetime.now(),
            confidence_score=0.8,
            tags=["crafting", "master", "beskar", "mtg"]
        )
    ]
    
    for entry in sample_entries:
        print(f"  ✓ Created: {entry.title}")
    
    print("\nStep 3: Add Entries to Miner")
    for entry in sample_entries:
        if entry.knowledge_type not in miner.knowledge_entries:
            miner.knowledge_entries[entry.knowledge_type] = []
        miner.knowledge_entries[entry.knowledge_type].append(entry)
    print("✓ Entries added to miner")
    
    print("\nStep 4: Integrate Knowledge")
    integrated_count = 0
    for entry in sample_entries:
        integration_result = integration.integrate_knowledge_entry(entry)
        if integration_result and integration_result.status == IntegrationStatus.INTEGRATED:
            integrated_count += 1
            print(f"  ✓ Integrated: {entry.title} -> {integration_result.target_system}")
        else:
            print(f"  ✗ Failed: {entry.title}")
    
    print(f"\nStep 5: Integration Results")
    print(f"  Total entries: {len(sample_entries)}")
    print(f"  Successfully integrated: {integrated_count}")
    print(f"  Success rate: {integrated_count/len(sample_entries)*100:.1f}%")
    
    print("\nStep 6: Knowledge Layer Summary")
    knowledge_layer = integration.get_knowledge_layer()
    for system_name, system_data in knowledge_layer.items():
        if 'data' in system_data:
            total_patterns = sum(len(patterns) for patterns in system_data['data'].values() if isinstance(patterns, list))
            print(f"  {system_name}: {total_patterns} patterns")
    
    print("\n✓ Complete workflow demonstration finished!")


def main():
    """Run the complete demo."""
    print("MTG REPO KNOWLEDGE MINER - BATCH 104 DEMO")
    print("=" * 80)
    print()
    
    try:
        # Run all demo sections
        demo_knowledge_mining()
        demo_knowledge_integration()
        demo_search_functionality()
        demo_statistics()
        demo_full_workflow()
        
        print("=" * 80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
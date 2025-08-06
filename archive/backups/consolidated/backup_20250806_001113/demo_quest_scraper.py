#!/usr/bin/env python3
"""
Demo script for Batch 022 - Wiki Quest Scraper + Profile Generator

This script demonstrates the quest scraper functionality by:
1. Creating sample quest data
2. Generating YAML profiles
3. Saving quest files to the appropriate directory structure
4. Updating the internal index
"""

import logging
from pathlib import Path
from importers.quest_scraper import (
    WikiQuestScraper, QuestData, QuestType, QuestDifficulty
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_quests():
    """Create sample quest data for demonstration."""
    
    sample_quests = [
        QuestData(
            quest_id="imp_agent_kill",
            name="Imperial Agent Kill Mission",
            description="Eliminate a rebel agent operating in the Tatooine desert",
            quest_type=QuestType.FACTION,
            difficulty=QuestDifficulty.MEDIUM,
            level_requirement=20,
            planet="tatooine",
            coordinates=(123, -456),
            npc="Imperial Terminal Officer",
            rewards={
                'credits': 5000,
                'experience': 2000,
                'items': ['Imperial Medal', 'Rebel Intel']
            },
            prerequisites=['level_20', 'imperial_faction'],
            dialogue=[
                "We have a mission for you, citizen.",
                "A rebel agent has been spotted in the desert.",
                "Kill the rebel scum and bring us proof.",
                "The Empire will reward you handsomely."
            ],
            source_url="https://swgr.org/wiki/Imperial_Agent_Kill_Mission",
            last_updated="2024-01-01"
        ),
        
        QuestData(
            quest_id="moisture_farm_delivery",
            name="Moisture Farm Delivery",
            description="Deliver supplies to a moisture farm on Tatooine",
            quest_type=QuestType.DELIVERY,
            difficulty=QuestDifficulty.EASY,
            level_requirement=5,
            planet="tatooine",
            coordinates=(200, 300),
            npc="Mos Eisley Merchant",
            rewards={
                'credits': 1000,
                'experience': 500,
                'items': ['Moisture Vaporator Parts']
            },
            prerequisites=['level_5'],
            dialogue=[
                "I need you to deliver these supplies to a moisture farm.",
                "The farm is located in the Jundland Wastes.",
                "Be careful of Tusken Raiders on the way.",
                "Return here when you've completed the delivery."
            ],
            source_url="https://swgr.org/wiki/Moisture_Farm_Delivery",
            last_updated="2024-01-01"
        ),
        
        QuestData(
            quest_id="artifact_hunt",
            name="Ancient Artifact Hunt",
            description="Search for ancient artifacts in the Tatooine ruins",
            quest_type=QuestType.COLLECTION,
            difficulty=QuestDifficulty.HARD,
            level_requirement=25,
            planet="tatooine",
            coordinates=(400, 500),
            npc="Archaeologist",
            rewards={
                'credits': 8000,
                'experience': 3000,
                'items': ['Ancient Artifact', 'Desert Map']
            },
            prerequisites=['level_25', 'exploration_skill'],
            dialogue=[
                "I've discovered ancient ruins in the desert.",
                "I need you to search for artifacts there.",
                "The ruins are dangerous - bring friends.",
                "Any artifacts you find are yours to keep."
            ],
            source_url="https://swgr.org/wiki/Ancient_Artifact_Hunt",
            last_updated="2024-01-01"
        ),
        
        QuestData(
            quest_id="theed_palace_mission",
            name="Theed Palace Security Mission",
            description="Help secure the palace in Theed, Naboo",
            quest_type=QuestType.FACTION,
            difficulty=QuestDifficulty.MEDIUM,
            level_requirement=15,
            planet="naboo",
            coordinates=(5000, -4000),
            npc="Palace Guard Captain",
            rewards={
                'credits': 3000,
                'experience': 1500,
                'items': ['Palace Security Badge']
            },
            prerequisites=['level_15', 'naboo_citizen'],
            dialogue=[
                "The palace needs additional security.",
                "We've received reports of suspicious activity.",
                "Patrol the palace grounds and report any threats.",
                "Your service to Naboo will not be forgotten."
            ],
            source_url="https://swgr.org/wiki/Theed_Palace_Security_Mission",
            last_updated="2024-01-01"
        ),
        
        QuestData(
            quest_id="coronet_trade_mission",
            name="Coronet Trade Mission",
            description="Deliver trade goods to Coronet, Corellia",
            quest_type=QuestType.DELIVERY,
            difficulty=QuestDifficulty.EASY,
            level_requirement=10,
            planet="corellia",
            coordinates=(123, 456),
            npc="Trade Federation Representative",
            rewards={
                'credits': 2000,
                'experience': 800,
                'items': ['Trade Federation Credits']
            },
            prerequisites=['level_10'],
            dialogue=[
                "We need to establish trade routes to Corellia.",
                "Deliver these goods to Coronet.",
                "The Trade Federation will reward you well.",
                "Return with proof of delivery."
            ],
            source_url="https://swgr.org/wiki/Coronet_Trade_Mission",
            last_updated="2024-01-01"
        )
    ]
    
    return sample_quests


def demo_quest_scraper():
    """Demonstrate the quest scraper functionality."""
    
    print("🚀 Starting Quest Scraper Demo")
    print("=" * 50)
    
    # Initialize scraper
    scraper = WikiQuestScraper()
    print("✅ Quest scraper initialized")
    
    # Create sample quests
    sample_quests = create_sample_quests()
    print(f"✅ Created {len(sample_quests)} sample quests")
    
    # Process each quest
    for i, quest_data in enumerate(sample_quests, 1):
        print(f"\n📝 Processing Quest {i}: {quest_data.name}")
        
        # Generate YAML profile
        yaml_content = scraper.generate_yaml_profile(quest_data)
        print(f"   ✅ Generated YAML profile ({len(yaml_content)} characters)")
        
        # Save quest profile
        if scraper.save_quest_profile(quest_data):
            print(f"   ✅ Saved quest profile to {quest_data.planet}/{quest_data.quest_id}.yaml")
        else:
            print(f"   ❌ Failed to save quest profile")
        
        # Update internal index
        scraper.update_internal_index(quest_data)
        print(f"   ✅ Updated internal index")
    
    # Save internal index
    scraper.save_internal_index()
    print(f"\n✅ Saved internal index to data/internal_index.yaml")
    
    # Display summary
    print("\n" + "=" * 50)
    print("📊 Demo Summary:")
    print(f"   • Processed {len(sample_quests)} quests")
    print(f"   • Created quest files in data/quests/")
    print(f"   • Updated internal index")
    print(f"   • Quest types: {', '.join(set(q.quest_type.value for q in sample_quests))}")
    print(f"   • Planets: {', '.join(set(q.planet for q in sample_quests))}")
    
    # Show file structure
    print("\n📁 Generated File Structure:")
    quests_dir = Path("data/quests")
    for planet_dir in quests_dir.iterdir():
        if planet_dir.is_dir():
            print(f"   {planet_dir.name}/")
            for quest_file in planet_dir.glob("*.yaml"):
                print(f"     {quest_file.name}")
    
    print("\n🎉 Quest scraper demo completed successfully!")


if __name__ == "__main__":
    demo_quest_scraper() 
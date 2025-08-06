#!/usr/bin/env python3
"""
Demo script for Batch 033 - Quest Knowledge Builder & Smart Profile Learning

This script demonstrates the quest profiler functionality including:
- Quest database initialization
- OCR-based quest detection
- Quest statistics
- Auto-generation of quest YAML files
- CLI functionality simulation
"""

import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from quest_profiler import QuestProfiler, QuestMetadata
from datetime import datetime


def demo_quest_profiler():
    """Demonstrate the quest profiler functionality."""
    print("🚀 Batch 033 - Quest Knowledge Builder & Smart Profile Learning")
    print("=" * 60)
    
    # Initialize quest profiler
    print("📚 Initializing Quest Profiler...")
    profiler = QuestProfiler()
    
    # Show initial statistics
    print("\n📊 Initial Quest Database Statistics:")
    stats = profiler.get_quest_statistics()
    print(f"   Total Quests: {stats['total_quests']}")
    print(f"   Legacy Quests: {stats['legacy_quests']}")
    print(f"   YAML Quests: {stats['yaml_quests']}")
    print(f"   OCR Discovered: {stats['ocr_discovered']}")
    
    # Show quests by planet
    print("\n🌍 Quests by Planet:")
    for planet, count in sorted(stats['quests_by_planet'].items()):
        print(f"   {planet.title()}: {count}")
    
    # Show quests by type
    print("\n🏷️  Quests by Type:")
    for quest_type, count in sorted(stats['quests_by_type'].items()):
        print(f"   {quest_type.replace('_', ' ').title()}: {count}")
    
    # Simulate OCR quest detection
    print("\n🔍 Simulating OCR Quest Detection...")
    
    # Mock OCR text that would be detected
    mock_ocr_texts = [
        "Quest: Tatooine Artifact Hunt\nFrom: Mos Eisley Merchant\nLocation: Tatooine Desert\nReward: 1000 credits",
        "Mission: Naboo Palace Security\nFrom: Palace Guard Captain\nLocation: Theed Palace\nReward: 500 credits and reputation",
        "Task: Corellia Trade Route\nFrom: Trade Federation Agent\nLocation: Coronet City\nReward: 750 credits"
    ]
    
    for i, ocr_text in enumerate(mock_ocr_texts, 1):
        print(f"\n📝 Processing OCR Text {i}:")
        print(f"   {ocr_text}")
        
        # Extract quest information
        quest_info = profiler.extract_quest_info(ocr_text)
        if quest_info:
            print(f"   ✅ Extracted Quest Info:")
            for key, value in quest_info.items():
                print(f"      {key}: {value}")
            
            # Process the discovered quest
            profiler.process_discovered_quest(quest_info)
        else:
            print("   ❌ Failed to extract quest information")
    
    # Show updated statistics
    print("\n📊 Updated Quest Database Statistics:")
    stats = profiler.get_quest_statistics()
    print(f"   Total Quests: {stats['total_quests']}")
    print(f"   Discovered Quests: {stats['discovered_quests']}")
    print(f"   OCR Discovered: {stats['ocr_discovered']}")
    
    # Show discovered quests
    print("\n🆕 Recently Discovered Quests:")
    for quest in profiler.discovered_quests:
        print(f"   📚 {quest.name}")
        print(f"      📍 {quest.planet.title()} - {quest.location}")
        print(f"      👤 Giver: {quest.giver}")
        print(f"      🏷️  Type: {quest.quest_type}")
        print(f"      📅 Source: {quest.source}")
        print()
    
    # Demonstrate quest search functionality
    print("🔍 Quest Search Functionality:")
    search_terms = ["artifact", "palace", "trade"]
    
    for term in search_terms:
        matching_quests = []
        for quest in profiler.quest_database.values():
            if (term.lower() in quest.name.lower() or 
                term.lower() in quest.giver.lower() or
                term.lower() in quest.location.lower()):
                matching_quests.append(quest)
        
        print(f"\n   Search for '{term}': {len(matching_quests)} matches")
        for quest in matching_quests:
            print(f"      - {quest.name} ({quest.planet.title()})")
    
    # Demonstrate planet-specific quest listing
    print("\n🌍 Planet-Specific Quest Listing:")
    planets = ["tatooine", "naboo", "corellia"]
    
    for planet in planets:
        planet_quests = []
        for quest in profiler.quest_database.values():
            if planet.lower() in quest.planet.lower():
                planet_quests.append(quest)
        
        print(f"\n   Quests on {planet.title()}: {len(planet_quests)} total")
        for quest in planet_quests:
            print(f"      - {quest.name} (Giver: {quest.giver})")
    
    # Demonstrate quest type filtering
    print("\n🏷️  Quest Type Filtering:")
    quest_types = ["legacy", "discovered", "yaml"]
    
    for quest_type in quest_types:
        type_quests = []
        for quest in profiler.quest_database.values():
            if quest_type.lower() in quest.quest_type.lower():
                type_quests.append(quest)
        
        print(f"\n   Quests of type '{quest_type}': {len(type_quests)} total")
        for quest in type_quests:
            print(f"      - {quest.name} ({quest.planet.title()})")
    
    # Demonstrate YAML file generation
    print("\n📝 YAML File Generation:")
    print("   Auto-generated quest YAML files would be created in:")
    print(f"   {profiler.quests_dir}")
    
    # List any generated YAML files
    yaml_files = list(profiler.quests_dir.rglob("*.yaml"))
    if yaml_files:
        print(f"\n   Found {len(yaml_files)} YAML quest files:")
        for yaml_file in yaml_files:
            print(f"      - {yaml_file.relative_to(profiler.quests_dir)}")
    else:
        print("   No YAML quest files found yet")
    
    # Demonstrate database saving
    print("\n💾 Database Management:")
    try:
        profiler.save_quest_database()
        print("   ✅ Quest database saved successfully")
    except Exception as e:
        print(f"   ❌ Failed to save quest database: {e}")
    
    # Demonstrate configuration
    print("\n⚙️  Configuration:")
    print(f"   OCR Interval: {profiler.ocr_interval} seconds")
    print(f"   Quest Detection Keywords: {profiler.quest_detection_keywords}")
    print(f"   Wiki Sources: {profiler.config.get('wiki_sources', [])}")
    print(f"   GPT Enabled: {profiler.config.get('gpt_enabled', False)}")
    
    # Demonstrate CLI functionality
    print("\n🖥️  CLI Functionality Simulation:")
    print("   Available commands:")
    print("     ms11 learn-quest --live")
    print("     ms11 learn-quest --stats")
    print("     ms11 learn-quest --monitor")
    print("     ms11 learn-quest --list")
    print("     ms11 learn-quest --search <term>")
    print("     ms11 learn-quest --planet <planet>")
    print("     ms11 learn-quest --type <type>")
    
    print("\n✅ Batch 033 Quest Profiler Demo Complete!")
    print("   The system is ready for live quest learning and monitoring.")


def demo_ocr_simulation():
    """Demonstrate OCR text extraction and processing."""
    print("\n🔍 OCR Text Processing Demo:")
    print("-" * 40)
    
    # Sample OCR texts that might be captured during gameplay
    sample_texts = [
        "Quest: Tusken Raider Hunt\nFrom: Mos Eisley Bounty Hunter\nLocation: Tatooine Dune Sea\nReward: 2000 credits and Tusken reputation",
        "Mission: Imperial Agent Elimination\nFrom: Rebel Alliance Commander\nLocation: Corellia Imperial Base\nReward: 1500 credits and Rebel reputation",
        "Task: Medical Supply Delivery\nFrom: Naboo Medical Center\nLocation: Theed City\nReward: 800 credits and medical supplies"
    ]
    
    profiler = QuestProfiler()
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\n📝 Sample OCR Text {i}:")
        print(f"   {text}")
        
        # Check for quest keywords
        has_keywords = profiler.detect_quest_keywords(text)
        print(f"   Quest Keywords Detected: {has_keywords}")
        
        if has_keywords:
            # Extract quest information
            quest_info = profiler.extract_quest_info(text)
            if quest_info:
                print(f"   ✅ Extracted Information:")
                for key, value in quest_info.items():
                    print(f"      {key}: {value}")
                
                # Show planet extraction
                planet = profiler.extract_planet_from_location(quest_info.get("location", ""))
                print(f"      extracted_planet: {planet}")
            else:
                print("   ❌ Failed to extract quest information")


if __name__ == "__main__":
    print("🎯 Batch 033 - Quest Knowledge Builder & Smart Profile Learning")
    print("=" * 70)
    
    # Run main demo
    demo_quest_profiler()
    
    # Run OCR simulation demo
    demo_ocr_simulation()
    
    print("\n🎉 All demonstrations completed successfully!")
    print("   The quest profiler system is ready for use.") 
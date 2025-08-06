#!/usr/bin/env python3
"""
MS11 Quest Learning CLI Tool

This module provides the CLI interface for the quest learning system,
including the `ms11 learn-quest --live` functionality.
"""

import argparse
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from quest_profiler import QuestProfiler


def main():
    """Main CLI function for quest learning."""
    parser = argparse.ArgumentParser(
        description="MS11 Quest Learning System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ms11 learn-quest --live                    # Start live quest learning mode
  ms11 learn-quest --stats                   # Show quest statistics
  ms11 learn-quest --monitor                 # Start continuous monitoring
  ms11 learn-quest --config config.yaml      # Use custom configuration
  ms11 learn-quest --list                    # List all known quests
  ms11 learn-quest --search "artifact"       # Search for quests by name
  ms11 learn-quest --planet tatooine         # Show quests on specific planet
        """
    )
    
    # Main command group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--live", action="store_true", 
                      help="Start live quest learning mode (monitoring + auto-generation)")
    group.add_argument("--monitor", action="store_true",
                      help="Start continuous quest monitoring via OCR")
    group.add_argument("--stats", action="store_true",
                      help="Show quest statistics and database information")
    group.add_argument("--list", action="store_true",
                      help="List all known quests in the database")
    group.add_argument("--search", type=str,
                      help="Search for quests by name or description")
    group.add_argument("--planet", type=str,
                      help="Show quests on a specific planet")
    group.add_argument("--type", type=str,
                      help="Show quests of a specific type (legacy, theme_park, etc.)")
    
    # Optional arguments
    parser.add_argument("--config", type=str,
                       help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--save", action="store_true",
                       help="Save quest database after operations")
    parser.add_argument("--output", type=str,
                       help="Output file for results (JSON format)")
    
    args = parser.parse_args()
    
    # Initialize quest profiler
    try:
        profiler = QuestProfiler(args.config)
        
        if args.verbose:
            import logging
            profiler.logger.setLevel(logging.DEBUG)
        
        # Handle different commands
        if args.live:
            print("🚀 Starting MS11 Live Quest Learning Mode...")
            print("📡 Monitoring for new quests via OCR...")
            print("📝 Auto-generating quest YAML files...")
            print("🔍 Press Ctrl+C to stop monitoring")
            print("-" * 50)
            
            try:
                profiler.start_monitoring()
            except KeyboardInterrupt:
                print("\n⏹️  Quest learning stopped by user")
                if args.save:
                    profiler.save_quest_database()
                    print("💾 Quest database saved")
        
        elif args.monitor:
            print("📡 Starting quest monitoring...")
            print("🔍 Press Ctrl+C to stop monitoring")
            print("-" * 30)
            
            try:
                profiler.start_monitoring()
            except KeyboardInterrupt:
                print("\n⏹️  Monitoring stopped by user")
                if args.save:
                    profiler.save_quest_database()
                    print("💾 Quest database saved")
        
        elif args.stats:
            stats = profiler.get_quest_statistics()
            
            print("📊 MS11 Quest Database Statistics")
            print("=" * 40)
            print(f"📚 Total Quests: {stats['total_quests']}")
            print(f"🆕 Discovered Quests: {stats['discovered_quests']}")
            print(f"📜 Legacy Quests: {stats['legacy_quests']}")
            print(f"📄 YAML Quests: {stats['yaml_quests']}")
            print(f"👁️  OCR Discovered: {stats['ocr_discovered']}")
            
            print("\n🌍 Quests by Planet:")
            for planet, count in sorted(stats['quests_by_planet'].items()):
                print(f"  {planet.title()}: {count}")
            
            print("\n🏷️  Quests by Type:")
            for quest_type, count in sorted(stats['quests_by_type'].items()):
                print(f"  {quest_type.replace('_', ' ').title()}: {count}")
            
            if args.output:
                import json
                with open(args.output, 'w') as f:
                    json.dump(stats, f, indent=2, default=str)
                print(f"\n💾 Statistics saved to {args.output}")
        
        elif args.list:
            quests = list(profiler.quest_database.values())
            
            print(f"📚 All Known Quests ({len(quests)} total)")
            print("=" * 50)
            
            for i, quest in enumerate(quests, 1):
                print(f"{i:3d}. {quest.name}")
                print(f"     📍 {quest.planet.title()} - {quest.location}")
                print(f"     👤 Giver: {quest.giver}")
                print(f"     🏷️  Type: {quest.quest_type}")
                print(f"     📅 Source: {quest.source}")
                print()
        
        elif args.search:
            search_term = args.search.lower()
            matching_quests = []
            
            for quest in profiler.quest_database.values():
                if (search_term in quest.name.lower() or 
                    search_term in quest.giver.lower() or
                    search_term in quest.location.lower()):
                    matching_quests.append(quest)
            
            print(f"🔍 Search Results for '{args.search}' ({len(matching_quests)} matches)")
            print("=" * 50)
            
            for i, quest in enumerate(matching_quests, 1):
                print(f"{i:3d}. {quest.name}")
                print(f"     📍 {quest.planet.title()} - {quest.location}")
                print(f"     👤 Giver: {quest.giver}")
                print(f"     🏷️  Type: {quest.quest_type}")
                print()
        
        elif args.planet:
            planet_name = args.planet.lower()
            planet_quests = []
            
            for quest in profiler.quest_database.values():
                if planet_name in quest.planet.lower():
                    planet_quests.append(quest)
            
            print(f"🌍 Quests on {args.planet.title()} ({len(planet_quests)} total)")
            print("=" * 50)
            
            for i, quest in enumerate(planet_quests, 1):
                print(f"{i:3d}. {quest.name}")
                print(f"     📍 Location: {quest.location}")
                print(f"     👤 Giver: {quest.giver}")
                print(f"     🏷️  Type: {quest.quest_type}")
                print()
        
        elif args.type:
            quest_type = args.type.lower()
            type_quests = []
            
            for quest in profiler.quest_database.values():
                if quest_type in quest.quest_type.lower():
                    type_quests.append(quest)
            
            print(f"🏷️  Quests of type '{args.type}' ({len(type_quests)} total)")
            print("=" * 50)
            
            for i, quest in enumerate(type_quests, 1):
                print(f"{i:3d}. {quest.name}")
                print(f"     📍 {quest.planet.title()} - {quest.location}")
                print(f"     👤 Giver: {quest.giver}")
                print()
        
        # Save database if requested
        if args.save and not (args.live or args.monitor):
            profiler.save_quest_database()
            print("💾 Quest database saved")
    
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
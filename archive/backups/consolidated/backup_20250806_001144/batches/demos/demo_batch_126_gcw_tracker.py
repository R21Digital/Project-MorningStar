#!/usr/bin/env python3
"""
Demo Script for Batch 126 - GCW/Faction Rank Tracker + Strategy Advisor

This script demonstrates the comprehensive GCW tracking and strategy advisory system,
including faction detection, battle logging, gear recommendations, and strategy guides.

Author: SWG Bot Development Team
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Import the GCW Tracker
from core.gcw_tracker import (
    GCWTracker, FactionType, BattleType, GearCategory, StrategyType,
    GCWBattle, FactionProfile, GearRecommendation, StrategyGuide, GCWEvent
)

class GCWTrackerDemo:
    """Demo class for showcasing GCW Tracker functionality."""
    
    def __init__(self):
        """Initialize the demo with GCW Tracker."""
        self.tracker = GCWTracker()
        self.demo_characters = [
            "DemoRebel",
            "DemoImperial", 
            "DemoNeutral"
        ]
        
    def run_demo(self):
        """Run the complete GCW Tracker demo."""
        print("=" * 80)
        print("BATCH 126 DEMO: GCW/Faction Rank Tracker + Strategy Advisor")
        print("=" * 80)
        
        # Demo 1: Faction Detection and Profile Creation
        self.demo_faction_detection()
        
        # Demo 2: Battle Logging and Statistics
        self.demo_battle_logging()
        
        # Demo 3: Gear Recommendations
        self.demo_gear_recommendations()
        
        # Demo 4: Strategy Guides
        self.demo_strategy_guides()
        
        # Demo 5: Rank Progression Analysis
        self.demo_rank_progression()
        
        # Demo 6: Faction Statistics
        self.demo_faction_statistics()
        
        # Demo 7: GCW Events
        self.demo_gcw_events()
        
        # Demo 8: Advanced Features
        self.demo_advanced_features()
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    def demo_faction_detection(self):
        """Demo faction detection and profile creation."""
        print("\n1. FACTION DETECTION & PROFILE CREATION")
        print("-" * 50)
        
        # Rebel character detection
        rebel_indicators = {
            'faction': 'rebel',
            'rank': 4,
            'rank_points': 4500,
            'items': ['rebel_armor', 'rebel_weapon', 'rebel_ability'],
            'abilities': ['rebel_tactics', 'guerrilla_warfare']
        }
        
        profile = self.tracker.detect_faction_status("DemoRebel", rebel_indicators)
        print(f"✓ Rebel Profile Created: {profile.character_name}")
        print(f"  - Faction: {profile.faction.value}")
        print(f"  - Rank: {profile.current_rank}")
        print(f"  - Points: {profile.rank_points}")
        
        # Imperial character detection
        imperial_indicators = {
            'faction': 'imperial',
            'rank': 5,
            'rank_points': 6000,
            'items': ['imperial_armor', 'imperial_weapon'],
            'abilities': ['imperial_tactics', 'formation_discipline']
        }
        
        profile = self.tracker.detect_faction_status("DemoImperial", imperial_indicators)
        print(f"✓ Imperial Profile Created: {profile.character_name}")
        print(f"  - Faction: {profile.faction.value}")
        print(f"  - Rank: {profile.current_rank}")
        print(f"  - Points: {profile.rank_points}")
        
        # Neutral character detection
        neutral_indicators = {
            'faction': 'neutral',
            'rank': 0,
            'rank_points': 0,
            'items': ['civilian_clothing'],
            'abilities': []
        }
        
        profile = self.tracker.detect_faction_status("DemoNeutral", neutral_indicators)
        print(f"✓ Neutral Profile Created: {profile.character_name}")
        print(f"  - Faction: {profile.faction.value}")
        print(f"  - Rank: {profile.current_rank}")
        
    def demo_battle_logging(self):
        """Demo battle logging and statistics."""
        print("\n2. BATTLE LOGGING & STATISTICS")
        print("-" * 50)
        
        # Log various types of battles
        battles = [
            {
                'battle_type': 'pvp',
                'location': 'Anchorhead',
                'faction': 'rebel',
                'rank_at_time': 4,
                'outcome': 'victory',
                'duration': 15,
                'participants': 8,
                'rewards': {'points': 150, 'credits': 5000},
                'timestamp': datetime.now().isoformat()
            },
            {
                'battle_type': 'zone_control',
                'location': 'Bestine',
                'faction': 'imperial',
                'rank_at_time': 5,
                'outcome': 'victory',
                'duration': 45,
                'participants': 20,
                'rewards': {'points': 300, 'credits': 10000},
                'timestamp': datetime.now().isoformat()
            },
            {
                'battle_type': 'base_raid',
                'location': 'Mos Eisley',
                'faction': 'rebel',
                'rank_at_time': 4,
                'outcome': 'defeat',
                'duration': 30,
                'participants': 12,
                'rewards': {'points': 50, 'credits': 2000},
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        for i, battle_data in enumerate(battles, 1):
            character = "DemoRebel" if battle_data['faction'] == 'rebel' else "DemoImperial"
            battle = self.tracker.log_battle(character, battle_data)
            print(f"✓ Battle {i} Logged: {battle.battle_type.value}")
            print(f"  - Location: {battle.location}")
            print(f"  - Outcome: {battle.outcome}")
            print(f"  - Duration: {battle.duration} minutes")
            print(f"  - Points Earned: {battle.rewards.get('points', 0)}")
        
        # Show updated statistics
        rebel_profile = self.tracker.profiles.get("DemoRebel")
        if rebel_profile:
            print(f"\nRebel Statistics:")
            print(f"  - Total Battles: {rebel_profile.total_battles}")
            print(f"  - Win Rate: {rebel_profile.win_rate:.2%}")
            print(f"  - Average Duration: {rebel_profile.average_battle_duration:.1f} minutes")
        
    def demo_gear_recommendations(self):
        """Demo gear recommendations system."""
        print("\n3. GEAR RECOMMENDATIONS")
        print("-" * 50)
        
        # Get recommendations for different characters
        for character in ["DemoRebel", "DemoImperial"]:
            recommendations = self.tracker.get_gear_recommendations(character)
            print(f"\n{character} Gear Recommendations:")
            
            for gear in recommendations:
                print(f"  ✓ {gear.item_name}")
                print(f"    - Category: {gear.category.value}")
                print(f"    - Rank Required: {gear.rank_requirement}")
                print(f"    - Priority: {gear.priority}")
                print(f"    - Cost: {gear.cost}")
                print(f"    - Reasoning: {gear.reasoning}")
                
                if gear.stats:
                    stats_str = ", ".join([f"{k}: +{v}" for k, v in gear.stats.items()])
                    print(f"    - Stats: {stats_str}")
                
                if gear.resists:
                    resists_str = ", ".join([f"{k}: +{v}" for k, v in gear.resists.items()])
                    print(f"    - Resists: {resists_str}")
        
        # Add some advanced gear recommendations
        advanced_gear = [
            GearRecommendation(
                item_name="Advanced Energy Shield",
                category=GearCategory.UTILITIES,
                rank_requirement=6,
                faction_requirement=None,
                stats={"constitution": 15},
                resists={"energy": 40, "kinetic": 30},
                cost="very_high",
                priority="high",
                reasoning="Essential for high-rank PvP combat"
            ),
            GearRecommendation(
                item_name="Tactical Scanner",
                category=GearCategory.UTILITIES,
                rank_requirement=5,
                faction_requirement=None,
                stats={},
                resists={},
                cost="high",
                priority="medium",
                reasoning="Provides tactical advantage in combat"
            )
        ]
        
        for gear in advanced_gear:
            gear_id = f"{gear.item_name.lower().replace(' ', '_')}_{gear.rank_requirement}"
            self.tracker.gear_recommendations[gear_id] = gear
        
        print(f"\n✓ Added {len(advanced_gear)} advanced gear recommendations")
        
    def demo_strategy_guides(self):
        """Demo strategy guides system."""
        print("\n4. STRATEGY GUIDES")
        print("-" * 50)
        
        # Add comprehensive strategy guides for ranks 4-10
        strategy_guides = [
            # Rank 6 - Captain
            StrategyGuide(
                rank=6,
                faction=FactionType.REBEL,
                strategy_type=StrategyType.OFFENSIVE,
                title="Rebel Assault Tactics",
                description="Advanced offensive tactics for Rebel Captains",
                tactics=[
                    "Coordinate multi-squad assaults",
                    "Use terrain to advantage",
                    "Implement hit-and-run on larger scale",
                    "Maintain communication networks"
                ],
                gear_requirements=[
                    "Advanced Rebel Combat Armor",
                    "Tactical Scanner",
                    "Advanced Energy Shield"
                ],
                skill_requirements=[
                    "Ranged Combat: 4/4",
                    "Tactics: 4/4",
                    "Leadership: 3/4"
                ],
                difficulty="hard",
                estimated_success_rate=0.80
            ),
            StrategyGuide(
                rank=6,
                faction=FactionType.IMPERIAL,
                strategy_type=StrategyType.DEFENSIVE,
                title="Imperial Fortress Defense",
                description="Advanced defensive tactics for Imperial Captains",
                tactics=[
                    "Establish defensive perimeters",
                    "Coordinate heavy weapons placement",
                    "Maintain supply lines",
                    "Implement counter-attack protocols"
                ],
                gear_requirements=[
                    "Advanced Imperial Armor",
                    "Tactical Scanner",
                    "Advanced Energy Shield"
                ],
                skill_requirements=[
                    "Ranged Combat: 4/4",
                    "Tactics: 4/4",
                    "Leadership: 3/4"
                ],
                difficulty="hard",
                estimated_success_rate=0.75
            ),
            # Rank 8 - Colonel
            StrategyGuide(
                rank=8,
                faction=FactionType.REBEL,
                strategy_type=StrategyType.SUPPORT,
                title="Rebel Command & Control",
                description="Strategic command tactics for Rebel Colonels",
                tactics=[
                    "Coordinate multiple battle groups",
                    "Implement strategic retreats",
                    "Manage resource allocation",
                    "Maintain morale and discipline"
                ],
                gear_requirements=[
                    "Elite Rebel Combat Armor",
                    "Advanced Tactical Scanner",
                    "Command Console"
                ],
                skill_requirements=[
                    "Leadership: 4/4",
                    "Tactics: 4/4",
                    "Strategy: 3/4"
                ],
                difficulty="expert",
                estimated_success_rate=0.85
            )
        ]
        
        for guide in strategy_guides:
            guide_id = f"{guide.faction.value}_{guide.strategy_type.value}_rank_{guide.rank}"
            self.tracker.strategy_guides[guide_id] = guide
        
        print(f"✓ Added {len(strategy_guides)} advanced strategy guides")
        
        # Show available guides for different characters
        for character in ["DemoRebel", "DemoImperial"]:
            guides = self.tracker.get_strategy_guides(character)
            print(f"\n{character} Available Strategies:")
            
            for guide in guides:
                print(f"  ✓ {guide.title}")
                print(f"    - Rank: {guide.rank}")
                print(f"    - Type: {guide.strategy_type.value}")
                print(f"    - Success Rate: {guide.estimated_success_rate:.1%}")
                print(f"    - Difficulty: {guide.difficulty}")
        
    def demo_rank_progression(self):
        """Demo rank progression analysis."""
        print("\n5. RANK PROGRESSION ANALYSIS")
        print("-" * 50)
        
        for character in ["DemoRebel", "DemoImperial"]:
            progression = self.tracker.get_rank_progression(character)
            if progression:
                print(f"\n{character} Progression:")
                print(f"  - Current Rank: {progression['current_rank']}")
                print(f"  - Current Points: {progression['current_points']}")
                print(f"  - Next Rank: {progression['next_rank']}")
                print(f"  - Points Needed: {progression['points_needed']}")
                print(f"  - Win Rate: {progression['win_rate']:.2%}")
                print(f"  - Points per Battle: {progression['points_per_battle']:.1f}")
                print(f"  - Estimated Days to Next Rank: {progression['estimated_days_to_next_rank']:.1f}")
        
    def demo_faction_statistics(self):
        """Demo faction-wide statistics."""
        print("\n6. FACTION STATISTICS")
        print("-" * 50)
        
        # Get statistics for each faction
        for faction in [FactionType.REBEL, FactionType.IMPERIAL]:
            stats = self.tracker.get_faction_statistics(faction)
            print(f"\n{faction.value.title()} Faction Statistics:")
            print(f"  - Total Characters: {stats['total_characters']}")
            print(f"  - Total Battles: {stats['battle_statistics']['total_battles']}")
            print(f"  - Average Win Rate: {stats['battle_statistics']['avg_win_rate']:.2%}")
            
            if stats['rank_distribution']:
                print(f"  - Rank Distribution:")
                for rank, count in sorted(stats['rank_distribution'].items()):
                    print(f"    Rank {rank}: {count} characters")
            
            if stats['popular_locations']:
                print(f"  - Popular Locations:")
                for location, count in stats['popular_locations'].most_common(3):
                    print(f"    {location}: {count} battles")
        
    def demo_gcw_events(self):
        """Demo GCW events system."""
        print("\n7. GCW EVENTS")
        print("-" * 50)
        
        # Create some GCW events
        events = [
            {
                'event_id': 'major_battle_anchorhead',
                'name': 'Major Battle: Anchorhead',
                'description': 'Large-scale battle for control of Anchorhead',
                'start_time': datetime.now().isoformat(),
                'end_time': (datetime.now() + timedelta(hours=3)).isoformat(),
                'location': 'Anchorhead',
                'faction_restriction': None,
                'rank_requirement': 4,
                'rewards': {'points': 500, 'credits': 25000, 'special_items': ['Battle Commendation']},
                'participants': []
            },
            {
                'event_id': 'imperial_assault_bestine',
                'name': 'Imperial Assault: Bestine',
                'description': 'Imperial forces assault Bestine',
                'start_time': datetime.now().isoformat(),
                'end_time': (datetime.now() + timedelta(hours=2)).isoformat(),
                'location': 'Bestine',
                'faction_restriction': 'imperial',
                'rank_requirement': 5,
                'rewards': {'points': 300, 'credits': 15000},
                'participants': []
            }
        ]
        
        for event_data in events:
            event = self.tracker.add_gcw_event(event_data)
            print(f"✓ Event Created: {event.name}")
            print(f"  - Location: {event.location}")
            print(f"  - Duration: {event.start_time} to {event.end_time}")
            print(f"  - Rank Requirement: {event.rank_requirement}")
        
        # Show active events for characters
        for character in ["DemoRebel", "DemoImperial"]:
            active_events = self.tracker.get_active_events(character)
            print(f"\n{character} Active Events:")
            for event in active_events:
                print(f"  ✓ {event.name}")
                print(f"    - Location: {event.location}")
                print(f"    - Rewards: {event.rewards}")
        
    def demo_advanced_features(self):
        """Demo advanced GCW tracker features."""
        print("\n8. ADVANCED FEATURES")
        print("-" * 50)
        
        # Add custom gear recommendations
        custom_gear = GearRecommendation(
            item_name="Experimental Combat Suit",
            category=GearCategory.ARMOR,
            rank_requirement=7,
            faction_requirement=None,
            stats={"constitution": 35, "stamina": 30, "agility": 15},
            resists={"energy": 45, "kinetic": 40, "stun": 30},
            cost="very_high",
            priority="critical",
            reasoning="Experimental armor with advanced protection systems"
        )
        
        gear_id = "experimental_combat_suit_7"
        self.tracker.gear_recommendations[gear_id] = custom_gear
        print(f"✓ Added custom gear: {custom_gear.item_name}")
        
        # Add custom strategy guide
        custom_strategy = StrategyGuide(
            rank=10,
            faction=FactionType.REBEL,
            strategy_type=StrategyType.STEALTH,
            title="Rebel Elite Stealth Operations",
            description="Ultimate stealth tactics for Rebel Marshals",
            tactics=[
                "Infiltrate enemy bases undetected",
                "Execute precision strikes",
                "Maintain operational security",
                "Coordinate with intelligence networks"
            ],
            gear_requirements=[
                "Stealth Combat Suit",
                "Advanced Cloaking Device",
                "Silenced Weapons"
            ],
            skill_requirements=[
                "Stealth: 4/4",
                "Tactics: 4/4",
                "Leadership: 4/4"
            ],
            difficulty="expert",
            estimated_success_rate=0.90
        )
        
        strategy_id = "rebel_stealth_rank_10"
        self.tracker.strategy_guides[strategy_id] = custom_strategy
        print(f"✓ Added custom strategy: {custom_strategy.title}")
        
        # Save all data
        self.tracker.save_data()
        print("✓ All data saved successfully")
        
        # Show data file sizes
        data_files = [
            self.tracker.profiles_file,
            self.tracker.battles_file,
            self.tracker.events_file,
            self.tracker.gear_file,
            self.tracker.strategies_file
        ]
        
        print("\nData File Summary:")
        for file_path in data_files:
            if file_path.exists():
                size_kb = file_path.stat().st_size / 1024
                print(f"  - {file_path.name}: {size_kb:.1f} KB")

def main():
    """Main demo function."""
    try:
        demo = GCWTrackerDemo()
        demo.run_demo()
        
        print("\n" + "=" * 80)
        print("BATCH 126 IMPLEMENTATION SUMMARY")
        print("=" * 80)
        print("✓ GCW/Faction Rank Tracker implemented")
        print("✓ Faction detection and profile management")
        print("✓ Battle logging and statistics tracking")
        print("✓ Gear recommendations based on rank/faction")
        print("✓ Strategy guides for ranks 4-10")
        print("✓ Rank progression analysis")
        print("✓ Faction-wide statistics")
        print("✓ GCW events system")
        print("✓ Advanced features and customization")
        print("✓ Data persistence and file management")
        print("✓ UI components (FactionAdvisor.tsx)")
        print("✓ Documentation (faction_builds.md)")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
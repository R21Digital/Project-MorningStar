#!/usr/bin/env python3
"""
Batch 098 - Quest Heatmap & Popular Paths Tracker Demo

This script demonstrates the quest heatmap and popular paths tracking functionality
by creating sample session data and showing how the system analyzes quest usage patterns.
"""

import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent))
from core.quest_heatmap_tracker import quest_heatmap_tracker, QuestEvent, LocationVisit, StuckEvent, TravelPath

logger = logging.getLogger(__name__)

class QuestHeatmapDemo:
    """Demo class for showcasing quest heatmap functionality."""
    
    def __init__(self):
        """Initialize the demo."""
        self.demo_data_created = False
        
    def run_demo(self):
        """Run the complete demo."""
        print("=" * 80)
        print("BATCH 098 - QUEST HEATMAP & POPULAR PATHS TRACKER DEMO")
        print("=" * 80)
        
        try:
            # Step 1: Create sample session data
            print("\n1. Creating sample session data...")
            self.create_sample_session_data()
            
            # Step 2: Process session logs
            print("\n2. Processing session logs...")
            quest_heatmap_tracker.process_session_logs()
            
            # Step 3: Demonstrate heatmap features
            print("\n3. Demonstrating heatmap features...")
            self.demonstrate_quest_heatmap()
            self.demonstrate_city_heatmap()
            self.demonstrate_danger_zones()
            self.demonstrate_popular_paths()
            self.demonstrate_coordinate_heatmap()
            
            # Step 4: Show weekly statistics
            print("\n4. Weekly statistics...")
            self.show_weekly_stats()
            
            # Step 5: Demonstrate manual data addition
            print("\n5. Demonstrating manual data addition...")
            self.demonstrate_manual_data_addition()
            
            print("\n" + "=" * 80)
            print("DEMO COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print("\nNext steps:")
            print("- Visit /admin/quest-heatmap to view the dashboard")
            print("- Process real session logs to see actual data")
            print("- Use the API endpoints for programmatic access")
            
        except Exception as e:
            print(f"\nError during demo: {e}")
            logger.error(f"Demo error: {e}")
    
    def create_sample_session_data(self):
        """Create sample session log files for demonstration."""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create sample session logs
        sample_sessions = [
            {
                "start_time": (datetime.now() - timedelta(days=1)).isoformat(),
                "quests_completed": 3,
                "total_xp": 1500,
                "time_spent": 3600.0,
                "activity_breakdown": {"quest": 5, "move": 8, "dialogue": 3},
                "steps": [
                    {
                        "time": (datetime.now() - timedelta(hours=2)).isoformat(),
                        "type": "quest",
                        "id": "intro_quest",
                        "name": "Introduction Quest",
                        "action": "start",
                        "to": {"planet": "Tatooine", "city": "Mos Eisley", "x": 3600, "y": -4850}
                    },
                    {
                        "time": (datetime.now() - timedelta(hours=1, minutes=45)).isoformat(),
                        "type": "quest",
                        "id": "intro_quest",
                        "name": "Introduction Quest",
                        "action": "complete",
                        "xp": 500,
                        "to": {"planet": "Tatooine", "city": "Mos Eisley", "x": 3600, "y": -4850}
                    },
                    {
                        "time": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
                        "type": "move",
                        "to": {"planet": "Tatooine", "city": "Mos Espa", "x": 3520, "y": -4800}
                    },
                    {
                        "time": (datetime.now() - timedelta(hours=1, minutes=15)).isoformat(),
                        "type": "quest",
                        "id": "delivery_quest",
                        "name": "Delivery Quest",
                        "action": "start",
                        "to": {"planet": "Tatooine", "city": "Mos Espa", "x": 3520, "y": -4800}
                    },
                    {
                        "time": (datetime.now() - timedelta(hours=1)).isoformat(),
                        "type": "quest",
                        "id": "delivery_quest",
                        "name": "Delivery Quest",
                        "action": "complete",
                        "xp": 1000,
                        "to": {"planet": "Tatooine", "city": "Mos Espa", "x": 3520, "y": -4800}
                    }
                ]
            },
            {
                "start_time": (datetime.now() - timedelta(days=2)).isoformat(),
                "quests_completed": 2,
                "total_xp": 800,
                "time_spent": 2400.0,
                "activity_breakdown": {"quest": 3, "move": 5, "stuck": 1},
                "steps": [
                    {
                        "time": (datetime.now() - timedelta(days=2, hours=1)).isoformat(),
                        "type": "quest",
                        "id": "hunting_quest",
                        "name": "Hunting Quest",
                        "action": "start",
                        "to": {"planet": "Naboo", "city": "Theed", "x": 5000, "y": -3000}
                    },
                    {
                        "time": (datetime.now() - timedelta(days=2, minutes=30)).isoformat(),
                        "type": "stuck",
                        "location": {"planet": "Naboo", "city": "Theed", "zone": "theed_palace", "x": 5000, "y": -3000},
                        "duration_minutes": 15,
                        "attempts": 3,
                        "reason": "navigation_failed"
                    },
                    {
                        "time": (datetime.now() - timedelta(days=2, minutes=15)).isoformat(),
                        "type": "quest",
                        "id": "hunting_quest",
                        "name": "Hunting Quest",
                        "action": "complete",
                        "xp": 800,
                        "to": {"planet": "Naboo", "city": "Theed", "x": 5000, "y": -3000}
                    }
                ]
            },
            {
                "start_time": (datetime.now() - timedelta(days=3)).isoformat(),
                "quests_completed": 4,
                "total_xp": 2000,
                "time_spent": 4800.0,
                "activity_breakdown": {"quest": 6, "move": 10, "dialogue": 4},
                "steps": [
                    {
                        "time": (datetime.now() - timedelta(days=3, hours=2)).isoformat(),
                        "type": "quest",
                        "id": "crafting_quest",
                        "name": "Crafting Quest",
                        "action": "start",
                        "to": {"planet": "Corellia", "city": "Coronet", "x": 4000, "y": -2000}
                    },
                    {
                        "time": (datetime.now() - timedelta(days=3, hours=1, minutes=30)).isoformat(),
                        "type": "move",
                        "to": {"planet": "Corellia", "city": "Tyrena", "x": 4200, "y": -1800}
                    },
                    {
                        "time": (datetime.now() - timedelta(days=3, hours=1)).isoformat(),
                        "type": "quest",
                        "id": "crafting_quest",
                        "name": "Crafting Quest",
                        "action": "complete",
                        "xp": 1200,
                        "to": {"planet": "Corellia", "city": "Tyrena", "x": 4200, "y": -1800}
                    },
                    {
                        "time": (datetime.now() - timedelta(days=3, minutes=30)).isoformat(),
                        "type": "quest",
                        "id": "social_quest",
                        "name": "Social Quest",
                        "action": "start",
                        "to": {"planet": "Corellia", "city": "Tyrena", "x": 4200, "y": -1800}
                    },
                    {
                        "time": (datetime.now() - timedelta(days=3, minutes=15)).isoformat(),
                        "type": "quest",
                        "id": "social_quest",
                        "name": "Social Quest",
                        "action": "complete",
                        "xp": 800,
                        "to": {"planet": "Corellia", "city": "Tyrena", "x": 4200, "y": -1800}
                    }
                ]
            }
        ]
        
        # Write sample session files
        for i, session_data in enumerate(sample_sessions):
            session_file = logs_dir / f"session_demo_{i+1}_{int(time.time())}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            print(f"  Created: {session_file}")
        
        # Create sample navigation events
        nav_events = [
            {"timestamp": time.time() - 3600, "event_type": "path_progression", "details": {
                "current_position": {"x": 3600, "y": -4850, "zone": "mos_eisley", "planet": "tatooine"},
                "target_position": {"x": 3520, "y": -4800, "zone": "mos_espa", "planet": "tatooine"},
                "distance": 94.34, "status": "moving", "attempts": 0, "path_length": 2
            }},
            {"timestamp": time.time() - 7200, "event_type": "path_progression", "details": {
                "current_position": {"x": 5000, "y": -3000, "zone": "theed", "planet": "naboo"},
                "target_position": {"x": 4800, "y": -2800, "zone": "theed_palace", "planet": "naboo"},
                "distance": 200.0, "status": "stuck", "attempts": 3, "path_length": 5
            }}
        ]
        
        nav_file = logs_dir / "navigation_events_demo.json"
        with open(nav_file, 'w') as f:
            for event in nav_events:
                f.write(json.dumps(event) + '\n')
        print(f"  Created: {nav_file}")
        
        self.demo_data_created = True
        print("  ✓ Sample session data created successfully")
    
    def demonstrate_quest_heatmap(self):
        """Demonstrate quest heatmap functionality."""
        print("\n   Quest Heatmap Demo:")
        
        # Get quest heatmap data
        quest_data = quest_heatmap_tracker.get_quest_heatmap(days=7)
        
        print(f"     Total quests in last 7 days: {quest_data['total_quests']}")
        print("     Top quests:")
        for quest in quest_data['top_quests'][:5]:
            print(f"       - {quest['quest_id']} ({quest['planet']}): {quest['count']} times")
    
    def demonstrate_city_heatmap(self):
        """Demonstrate city heatmap functionality."""
        print("\n   City Heatmap Demo:")
        
        # Get city heatmap data
        city_data = quest_heatmap_tracker.get_city_heatmap(days=7)
        
        print(f"     Total location visits in last 7 days: {city_data['total_visits']}")
        print("     Most visited cities:")
        for city in city_data['top_cities'][:5]:
            print(f"       - {city['city']} ({city['planet']}): {city['count']} visits")
    
    def demonstrate_danger_zones(self):
        """Demonstrate danger zones functionality."""
        print("\n   Danger Zones Demo:")
        
        # Get danger zones data
        danger_data = quest_heatmap_tracker.get_danger_zones(days=7)
        
        print(f"     Total stuck events in last 7 days: {danger_data['total_stuck_events']}")
        print("     Top danger zones:")
        for zone in danger_data['danger_zones'][:3]:
            avg_duration = sum(detail['duration_minutes'] for detail in zone['details']) / len(zone['details']) if zone['details'] else 0
            print(f"       - {zone['city']} ({zone['planet']}): {zone['stuck_count']} stuck events, avg {avg_duration:.1f} min")
    
    def demonstrate_popular_paths(self):
        """Demonstrate popular paths functionality."""
        print("\n   Popular Paths Demo:")
        
        # Get popular paths data
        paths_data = quest_heatmap_tracker.get_popular_paths(days=7)
        
        print(f"     Total travel paths in last 7 days: {paths_data['total_paths']}")
        print("     Most popular paths:")
        for path in paths_data['popular_paths'][:3]:
            avg_duration = sum(detail['duration_minutes'] for detail in path['details']) / len(path['details']) if path['details'] else 0
            print(f"       - {path['from_city']} → {path['to_city']}: {path['count']} times, avg {avg_duration:.1f} min")
    
    def demonstrate_coordinate_heatmap(self):
        """Demonstrate coordinate heatmap functionality."""
        print("\n   Coordinate Heatmap Demo:")
        
        # Get coordinate heatmap for Tatooine
        coord_data = quest_heatmap_tracker.get_coordinate_heatmap("Tatooine", days=7)
        
        print(f"     Coordinate data points for Tatooine: {len(coord_data)}")
        if coord_data:
            print("     Sample coordinates:")
            for point in coord_data[:3]:
                print(f"       - ({point['x']}, {point['y']}): {point['count']} visits, intensity {point['intensity']:.2f}")
    
    def show_weekly_stats(self):
        """Show weekly statistics."""
        print("\n   Weekly Statistics:")
        
        stats = quest_heatmap_tracker.get_weekly_stats()
        
        print(f"     Quest Stats: {stats['quest_stats']['total_quests']} total quests")
        print(f"     City Stats: {stats['city_stats']['total_visits']} total visits")
        print(f"     Danger Stats: {stats['danger_stats']['total_stuck_events']} stuck events")
        print(f"     Path Stats: {stats['path_stats']['total_paths']} travel paths")
    
    def demonstrate_manual_data_addition(self):
        """Demonstrate manual data addition."""
        print("\n   Manual Data Addition Demo:")
        
        # Add a travel path manually
        from_location = {"planet": "Tatooine", "city": "Mos Eisley", "x": 3600, "y": -4850}
        to_location = {"planet": "Naboo", "city": "Theed", "x": 5000, "y": -3000}
        
        quest_heatmap_tracker.add_travel_path(
            from_location=from_location,
            to_location=to_location,
            session_hash="demo_session_123",
            duration_minutes=45,
            method="shuttle"
        )
        print("     ✓ Added travel path: Mos Eisley → Theed")
        
        # Add a stuck event manually
        stuck_location = {"planet": "Corellia", "city": "Coronet", "zone": "coronet_city", "x": 4000, "y": -2000}
        
        quest_heatmap_tracker.add_stuck_event(
            location=stuck_location,
            session_hash="demo_session_456",
            duration_minutes=20,
            attempts=5,
            reason="quest_blocked"
        )
        print("     ✓ Added stuck event: Coronet (quest_blocked)")
    
    def cleanup_demo_data(self):
        """Clean up demo data files."""
        if not self.demo_data_created:
            return
        
        print("\nCleaning up demo data...")
        
        logs_dir = Path("logs")
        
        # Remove demo session files
        for session_file in logs_dir.glob("session_demo_*.json"):
            session_file.unlink()
            print(f"  Removed: {session_file}")
        
        # Remove demo navigation file
        nav_file = logs_dir / "navigation_events_demo.json"
        if nav_file.exists():
            nav_file.unlink()
            print(f"  Removed: {nav_file}")
        
        print("  ✓ Demo data cleaned up")

def main():
    """Main demo function."""
    demo = QuestHeatmapDemo()
    
    try:
        demo.run_demo()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        logger.error(f"Demo failed: {e}")
    finally:
        # Ask if user wants to clean up demo data
        try:
            response = input("\nClean up demo data? (y/N): ").strip().lower()
            if response == 'y':
                demo.cleanup_demo_data()
        except (EOFError, KeyboardInterrupt):
            pass

if __name__ == "__main__":
    main() 
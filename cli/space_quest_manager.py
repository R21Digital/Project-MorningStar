"""Command-line interface for Space Quest Manager."""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.space_quest_manager import (
    get_space_quest_manager,
    SpaceQuest,
    SpaceQuestType,
    SpaceQuestStatus,
    SpaceLocation,
    SpaceWaypoint
)


def print_space_state() -> None:
    """Print current space state."""
    manager = get_space_quest_manager()
    state = manager.detect_space_state()
    summary = manager.get_space_state_summary()
    
    print("\n=== Space State ===")
    print(f"In Space: {'Yes' if state.is_in_space else 'No'}")
    
    if state.is_in_space:
        print(f"Location: {state.current_location.value if state.current_location else 'Unknown'}")
        print(f"Coordinates: {state.current_coordinates}")
        print(f"Ship: {state.current_ship or 'Unknown'}")
        print(f"Nearby Objects: {len(state.nearby_objects)}")
        print(f"Active Quests: {len(state.active_quests)}")
        print(f"Available Quests: {len(state.available_quests)}")
    else:
        print("Player is not currently in space")
    
    print(f"\nTotal Space Quests: {summary['total_quests']}")
    print(f"Total Waypoints: {summary['total_waypoints']}")


def list_quests(quest_type: str = None, location: str = None, status: str = None) -> None:
    """List space quests with optional filters."""
    manager = get_space_quest_manager()
    
    quests = list(manager.space_quests.values())
    
    # Apply filters
    if quest_type:
        try:
            quest_type_enum = SpaceQuestType(quest_type)
            quests = [q for q in quests if q.quest_type == quest_type_enum]
        except ValueError:
            print(f"Invalid quest type: {quest_type}")
            return
    
    if location:
        try:
            location_enum = SpaceLocation(location)
            quests = [q for q in quests if q.start_location == location_enum]
        except ValueError:
            print(f"Invalid location: {location}")
            return
    
    if status:
        try:
            status_enum = SpaceQuestStatus(status)
            quests = [q for q in quests if q.status == status_enum]
        except ValueError:
            print(f"Invalid status: {status}")
            return
    
    print(f"\n=== Space Quests ({len(quests)}) ===")
    
    if not quests:
        print("No quests found matching criteria")
        return
    
    for quest in quests:
        print(f"\nQuest ID: {quest.quest_id}")
        print(f"Name: {quest.name}")
        print(f"Type: {quest.quest_type.value}")
        print(f"Status: {quest.status.value}")
        print(f"Location: {quest.start_location.value}")
        print(f"Level Requirement: {quest.level_requirement}")
        print(f"Credits: {quest.credits}")
        print(f"Experience: {quest.experience}")
        print(f"Description: {quest.description[:100]}...")


def list_waypoints() -> None:
    """List all space waypoints."""
    manager = get_space_quest_manager()
    
    print(f"\n=== Space Waypoints ({len(manager.space_waypoints)}) ===")
    
    for waypoint in manager.space_waypoints.values():
        print(f"\nName: {waypoint.name}")
        print(f"Location: {waypoint.location.value}")
        print(f"Coordinates: {waypoint.coordinates}")
        print(f"Station: {'Yes' if waypoint.is_station else 'No'}")
        print(f"Safe Zone: {'Yes' if waypoint.is_safe_zone else 'No'}")
        print(f"Services: {', '.join(waypoint.services)}")
        print(f"Quest Givers: {', '.join(waypoint.quest_givers)}")
        print(f"Description: {waypoint.description}")


def show_quest_details(quest_id: str) -> None:
    """Show detailed information about a specific quest."""
    manager = get_space_quest_manager()
    quest = manager.get_quest_by_id(quest_id)
    
    if not quest:
        print(f"Quest not found: {quest_id}")
        return
    
    print(f"\n=== Quest Details: {quest.name} ===")
    print(f"Quest ID: {quest.quest_id}")
    print(f"Type: {quest.quest_type.value}")
    print(f"Status: {quest.status.value}")
    print(f"Level Requirement: {quest.level_requirement}")
    print(f"Faction Requirement: {quest.faction_requirement or 'None'}")
    print(f"Ship Requirement: {quest.ship_requirement or 'None'}")
    print(f"Combat Rating Requirement: {quest.combat_rating_requirement or 'None'}")
    print(f"Faction Standing Requirement: {quest.faction_standing_requirement or 'None'}")
    print(f"Start Location: {quest.start_location.value}")
    print(f"Target Location: {quest.target_location.value if quest.target_location else 'None'}")
    print(f"Credits: {quest.credits}")
    print(f"Experience: {quest.experience}")
    print(f"Faction Standing: {quest.faction_standing}")
    print(f"Items: {', '.join(quest.items)}")
    print(f"Time Limit: {quest.time_limit or 'None'} seconds")
    print(f"Current Step: {quest.current_step}")
    print(f"Total Steps: {len(quest.steps)}")
    print(f"Tags: {', '.join(quest.tags)}")
    print(f"Description: {quest.description}")
    
    if quest.steps:
        print(f"\nQuest Steps:")
        for i, step in enumerate(quest.steps):
            print(f"  Step {i+1}: {step.get('description', 'No description')}")


def start_quest(quest_id: str) -> None:
    """Start a space quest."""
    manager = get_space_quest_manager()
    
    success = manager.start_quest(quest_id)
    if success:
        print(f"Successfully started quest: {quest_id}")
    else:
        print(f"Failed to start quest: {quest_id}")


def complete_quest(quest_id: str) -> None:
    """Complete a space quest."""
    manager = get_space_quest_manager()
    
    success = manager.complete_quest(quest_id)
    if success:
        print(f"Successfully completed quest: {quest_id}")
    else:
        print(f"Failed to complete quest: {quest_id}")


def fail_quest(quest_id: str) -> None:
    """Fail a space quest."""
    manager = get_space_quest_manager()
    
    success = manager.fail_quest(quest_id)
    if success:
        print(f"Successfully failed quest: {quest_id}")
    else:
        print(f"Failed to fail quest: {quest_id}")


def navigate_to_waypoint(waypoint_name: str) -> None:
    """Navigate to a space waypoint."""
    manager = get_space_quest_manager()
    
    success = manager.navigate_to_waypoint(waypoint_name)
    if success:
        print(f"Successfully navigated to waypoint: {waypoint_name}")
    else:
        print(f"Failed to navigate to waypoint: {waypoint_name}")


def get_nearby_waypoints(max_distance: float = 1000.0) -> None:
    """Get nearby waypoints."""
    manager = get_space_quest_manager()
    
    nearby = manager.get_nearby_waypoints(max_distance)
    
    print(f"\n=== Nearby Waypoints (within {max_distance} units) ===")
    
    if not nearby:
        print("No nearby waypoints found")
        return
    
    for waypoint in nearby:
        distance = manager._calculate_distance(
            manager.space_state.current_coordinates or (0, 0, 0),
            waypoint.coordinates
        )
        print(f"\nName: {waypoint.name}")
        print(f"Distance: {distance:.2f} units")
        print(f"Location: {waypoint.location.value}")
        print(f"Station: {'Yes' if waypoint.is_station else 'No'}")
        print(f"Safe Zone: {'Yes' if waypoint.is_safe_zone else 'No'}")


def add_sample_quests() -> None:
    """Add sample space quests for testing."""
    manager = get_space_quest_manager()
    
    sample_quests = [
        SpaceQuest(
            quest_id="space_delivery_001",
            name="Space Delivery Mission",
            description="Deliver supplies to the orbital station",
            quest_type=SpaceQuestType.DELIVERY,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=10,
            start_location=SpaceLocation.SPACE_STATION_1,
            target_location=SpaceLocation.ORBITAL_STATION,
            credits=500,
            experience=200,
            items=["supply_crate"],
            tags=["delivery", "space_station"]
        ),
        SpaceQuest(
            quest_id="space_combat_001",
            name="Space Combat Training",
            description="Engage in combat training exercises",
            quest_type=SpaceQuestType.COMBAT,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=15,
            ship_requirement="basic_fighter",
            start_location=SpaceLocation.SPACE_STATION_1,
            credits=1000,
            experience=500,
            items=["combat_medal"],
            tags=["combat", "training"]
        ),
        SpaceQuest(
            quest_id="space_salvage_001",
            name="Asteroid Field Salvage",
            description="Salvage valuable materials from asteroid field",
            quest_type=SpaceQuestType.SALVAGE,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=20,
            start_location=SpaceLocation.ASTEROID_FIELD,
            credits=1500,
            experience=800,
            items=["rare_minerals", "salvage_tools"],
            tags=["salvage", "asteroid"]
        ),
        SpaceQuest(
            quest_id="space_exploration_001",
            name="Deep Space Exploration",
            description="Explore the deep space outpost",
            quest_type=SpaceQuestType.EXPLORATION,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=25,
            start_location=SpaceLocation.DEEP_SPACE,
            credits=2000,
            experience=1000,
            items=["exploration_data", "deep_space_map"],
            tags=["exploration", "deep_space"]
        )
    ]
    
    for quest in sample_quests:
        manager.add_quest(quest)
    
    manager.save_space_data()
    print(f"Added {len(sample_quests)} sample space quests")


def export_quest_data(output_file: str) -> None:
    """Export quest data to JSON file."""
    manager = get_space_quest_manager()
    
    data = {
        "quests": [manager._serialize_quest(quest) for quest in manager.space_quests.values()],
        "waypoints": [
            {
                "name": waypoint.name,
                "location": waypoint.location.value,
                "coordinates": waypoint.coordinates,
                "description": waypoint.description,
                "is_station": waypoint.is_station,
                "is_safe_zone": waypoint.is_safe_zone,
                "services": waypoint.services,
                "quest_givers": waypoint.quest_givers
            }
            for waypoint in manager.space_waypoints.values()
        ],
        "export_time": manager.memory_manager.get_current_time()
    }
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Exported quest data to: {output_file}")
    except Exception as e:
        print(f"Failed to export quest data: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Space Quest Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # State command
    subparsers.add_parser("state", help="Show current space state")
    
    # List commands
    list_parser = subparsers.add_parser("list", help="List quests or waypoints")
    list_parser.add_argument("type", choices=["quests", "waypoints"], help="What to list")
    list_parser.add_argument("--quest-type", help="Filter by quest type")
    list_parser.add_argument("--location", help="Filter by location")
    list_parser.add_argument("--status", help="Filter by status")
    
    # Quest commands
    quest_parser = subparsers.add_parser("quest", help="Quest operations")
    quest_parser.add_argument("action", choices=["show", "start", "complete", "fail"], help="Quest action")
    quest_parser.add_argument("quest_id", help="Quest ID")
    
    # Navigation commands
    nav_parser = subparsers.add_parser("navigate", help="Navigation operations")
    nav_parser.add_argument("action", choices=["to", "nearby"], help="Navigation action")
    nav_parser.add_argument("--waypoint", help="Waypoint name (for 'to' action)")
    nav_parser.add_argument("--distance", type=float, default=1000.0, help="Max distance for nearby waypoints")
    
    # Data commands
    data_parser = subparsers.add_parser("data", help="Data operations")
    data_parser.add_argument("action", choices=["add-samples", "export"], help="Data action")
    data_parser.add_argument("--output", help="Output file for export")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "state":
            print_space_state()
        
        elif args.command == "list":
            if args.type == "quests":
                list_quests(args.quest_type, args.location, args.status)
            elif args.type == "waypoints":
                list_waypoints()
        
        elif args.command == "quest":
            if args.action == "show":
                show_quest_details(args.quest_id)
            elif args.action == "start":
                start_quest(args.quest_id)
            elif args.action == "complete":
                complete_quest(args.quest_id)
            elif args.action == "fail":
                fail_quest(args.quest_id)
        
        elif args.command == "navigate":
            if args.action == "to":
                if not args.waypoint:
                    print("Error: --waypoint is required for 'to' action")
                    return
                navigate_to_waypoint(args.waypoint)
            elif args.action == "nearby":
                get_nearby_waypoints(args.distance)
        
        elif args.command == "data":
            if args.action == "add-samples":
                add_sample_quests()
            elif args.action == "export":
                if not args.output:
                    print("Error: --output is required for export action")
                    return
                export_quest_data(args.output)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
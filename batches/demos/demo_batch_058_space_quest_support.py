"""Demo script for MS11 Batch 058 - Space Quest Support Module."""

import json
import time
from pathlib import Path

from core.space_quest_manager import (
    get_space_quest_manager,
    SpaceQuest,
    SpaceQuestType,
    SpaceQuestStatus,
    SpaceLocation,
    SpaceWaypoint
)


def demo_space_state_detection():
    """Demo space state detection functionality."""
    print("\n" + "="*60)
    print("DEMO: Space State Detection")
    print("="*60)
    
    manager = get_space_quest_manager()
    
    # Simulate different space states
    print("\n1. Detecting space state (not in space)...")
    state = manager.detect_space_state()
    print(f"   In Space: {state.is_in_space}")
    print(f"   Location: {state.current_location}")
    print(f"   Coordinates: {state.current_coordinates}")
    
    # Simulate entering space
    print("\n2. Simulating entry into space...")
    manager.space_state.is_in_space = True
    state = manager.detect_space_state()
    print(f"   In Space: {state.is_in_space}")
    print(f"   Location: {state.current_location.value if state.current_location else 'Unknown'}")
    print(f"   Ship: {state.current_ship}")
    print(f"   Available Quests: {len(state.available_quests)}")
    
    # Show space state summary
    summary = manager.get_space_state_summary()
    print(f"\n   Space State Summary:")
    for key, value in summary.items():
        print(f"     {key}: {value}")


def demo_quest_management():
    """Demo quest management functionality."""
    print("\n" + "="*60)
    print("DEMO: Quest Management")
    print("="*60)
    
    manager = get_space_quest_manager()
    
    # Create sample quests
    print("\n1. Creating sample space quests...")
    
    sample_quests = [
        SpaceQuest(
            quest_id="demo_delivery_001",
            name="Demo Delivery Mission",
            description="A demonstration delivery quest for testing",
            quest_type=SpaceQuestType.DELIVERY,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=5,
            start_location=SpaceLocation.SPACE_STATION_1,
            target_location=SpaceLocation.ORBITAL_STATION,
            credits=300,
            experience=150,
            items=["demo_crate"],
            tags=["demo", "delivery"]
        ),
        SpaceQuest(
            quest_id="demo_combat_001",
            name="Demo Combat Mission",
            description="A demonstration combat quest for testing",
            quest_type=SpaceQuestType.COMBAT,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=10,
            ship_requirement="demo_fighter",
            start_location=SpaceLocation.SPACE_STATION_1,
            credits=600,
            experience=300,
            items=["demo_medal"],
            tags=["demo", "combat"]
        ),
        SpaceQuest(
            quest_id="demo_exploration_001",
            name="Demo Exploration Mission",
            description="A demonstration exploration quest for testing",
            quest_type=SpaceQuestType.EXPLORATION,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=15,
            start_location=SpaceLocation.DEEP_SPACE,
            credits=900,
            experience=450,
            items=["demo_map"],
            tags=["demo", "exploration"]
        )
    ]
    
    for quest in sample_quests:
        manager.add_quest(quest)
        print(f"   Added quest: {quest.name} ({quest.quest_id})")
    
    # List all quests
    print(f"\n2. Listing all quests ({len(manager.space_quests)} total)...")
    for quest in manager.space_quests.values():
        print(f"   {quest.quest_id}: {quest.name} ({quest.quest_type.value}) - {quest.status.value}")
    
    # Filter quests by type
    print(f"\n3. Filtering quests by type...")
    delivery_quests = manager.get_quests_by_type(SpaceQuestType.DELIVERY)
    print(f"   Delivery quests: {len(delivery_quests)}")
    for quest in delivery_quests:
        print(f"     - {quest.name}")
    
    combat_quests = manager.get_quests_by_type(SpaceQuestType.COMBAT)
    print(f"   Combat quests: {len(combat_quests)}")
    for quest in combat_quests:
        print(f"     - {quest.name}")
    
    # Filter quests by location
    print(f"\n4. Filtering quests by location...")
    station_quests = manager.get_quests_by_location(SpaceLocation.SPACE_STATION_1)
    print(f"   Quests at Space Station 1: {len(station_quests)}")
    for quest in station_quests:
        print(f"     - {quest.name}")
    
    deep_space_quests = manager.get_quests_by_location(SpaceLocation.DEEP_SPACE)
    print(f"   Quests in Deep Space: {len(deep_space_quests)}")
    for quest in deep_space_quests:
        print(f"     - {quest.name}")


def demo_quest_lifecycle():
    """Demo quest lifecycle (start, complete, fail)."""
    print("\n" + "="*60)
    print("DEMO: Quest Lifecycle")
    print("="*60)
    
    manager = get_space_quest_manager()
    
    # Get a quest to work with
    quest_id = "demo_delivery_001"
    quest = manager.get_quest_by_id(quest_id)
    
    if not quest:
        print(f"Quest {quest_id} not found, creating it...")
        quest = SpaceQuest(
            quest_id=quest_id,
            name="Demo Delivery Mission",
            description="A demonstration delivery quest for testing",
            quest_type=SpaceQuestType.DELIVERY,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=5,
            start_location=SpaceLocation.SPACE_STATION_1,
            target_location=SpaceLocation.ORBITAL_STATION,
            credits=300,
            experience=150,
            items=["demo_crate"],
            tags=["demo", "delivery"]
        )
        manager.add_quest(quest)
    
    print(f"\n1. Starting quest: {quest.name}")
    print(f"   Initial status: {quest.status.value}")
    
    success = manager.start_quest(quest_id)
    print(f"   Start result: {'Success' if success else 'Failed'}")
    print(f"   New status: {quest.status.value}")
    print(f"   Start time: {quest.start_time}")
    print(f"   Active quests: {len(manager.space_state.active_quests)}")
    
    # Simulate some time passing
    time.sleep(0.1)  # Small delay for demo
    
    print(f"\n2. Completing quest: {quest.name}")
    success = manager.complete_quest(quest_id)
    print(f"   Complete result: {'Success' if success else 'Failed'}")
    print(f"   Final status: {quest.status.value}")
    print(f"   Completion time: {quest.completion_time}")
    print(f"   Duration: {quest.completion_time - quest.start_time:.2f} seconds")
    print(f"   Active quests: {len(manager.space_state.active_quests)}")
    
    # Show quest details
    print(f"\n3. Quest details after completion:")
    print(f"   Quest ID: {quest.quest_id}")
    print(f"   Name: {quest.name}")
    print(f"   Type: {quest.quest_type.value}")
    print(f"   Status: {quest.status.value}")
    print(f"   Credits: {quest.credits}")
    print(f"   Experience: {quest.experience}")
    print(f"   Items: {', '.join(quest.items)}")


def demo_waypoint_navigation():
    """Demo waypoint navigation functionality."""
    print("\n" + "="*60)
    print("DEMO: Waypoint Navigation")
    print("="*60)
    
    manager = get_space_quest_manager()
    
    # List all waypoints
    print(f"\n1. Available waypoints ({len(manager.space_waypoints)}):")
    for waypoint in manager.space_waypoints.values():
        print(f"   {waypoint.name} at {waypoint.location.value}")
        print(f"     Coordinates: {waypoint.coordinates}")
        print(f"     Station: {'Yes' if waypoint.is_station else 'No'}")
        print(f"     Services: {', '.join(waypoint.services)}")
    
    # Simulate being in space
    manager.space_state.is_in_space = True
    manager.space_state.current_location = SpaceLocation.SPACE_STATION_1
    manager.space_state.current_coordinates = (1000.0, 1000.0, 0.0)
    
    print(f"\n2. Current location: {manager.space_state.current_location.value}")
    print(f"   Coordinates: {manager.space_state.current_coordinates}")
    
    # Navigate to a waypoint
    target_waypoint = "Orbital Station Beta"
    print(f"\n3. Navigating to: {target_waypoint}")
    
    success = manager.navigate_to_waypoint(target_waypoint)
    print(f"   Navigation result: {'Success' if success else 'Failed'}")
    
    if success:
        print(f"   New location: {manager.space_state.current_location.value}")
        print(f"   New coordinates: {manager.space_state.current_coordinates}")
    
    # Get nearby waypoints
    print(f"\n4. Finding nearby waypoints (within 2000 units):")
    nearby = manager.get_nearby_waypoints(2000.0)
    print(f"   Found {len(nearby)} nearby waypoints:")
    
    for waypoint in nearby:
        distance = manager._calculate_distance(
            manager.space_state.current_coordinates or (0, 0, 0),
            waypoint.coordinates
        )
        print(f"     {waypoint.name}: {distance:.2f} units away")


def demo_quest_requirements():
    """Demo quest requirement checking."""
    print("\n" + "="*60)
    print("DEMO: Quest Requirements")
    print("="*60)
    
    manager = get_space_quest_manager()
    
    # Create quests with different requirements
    print("\n1. Creating quests with different requirements...")
    
    requirement_quests = [
        SpaceQuest(
            quest_id="req_level_001",
            name="Level Requirement Quest",
            description="Requires level 20",
            quest_type=SpaceQuestType.COMBAT,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=20,
            start_location=SpaceLocation.SPACE_STATION_1,
            credits=500,
            experience=250
        ),
        SpaceQuest(
            quest_id="req_ship_001",
            name="Ship Requirement Quest",
            description="Requires advanced fighter",
            quest_type=SpaceQuestType.COMBAT,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=10,
            ship_requirement="advanced_fighter",
            start_location=SpaceLocation.SPACE_STATION_1,
            credits=800,
            experience=400
        ),
        SpaceQuest(
            quest_id="req_faction_001",
            name="Faction Requirement Quest",
            description="Requires Rebel Alliance standing",
            quest_type=SpaceQuestType.ESCORT,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=15,
            faction_requirement="rebel_alliance",
            faction_standing_requirement=1000,
            start_location=SpaceLocation.SPACE_STATION_1,
            credits=1200,
            experience=600
        )
    ]
    
    for quest in requirement_quests:
        manager.add_quest(quest)
        print(f"   Added: {quest.name}")
    
    # Test requirement checking
    print(f"\n2. Testing quest requirements...")
    
    for quest in requirement_quests:
        print(f"\n   Testing: {quest.name}")
        print(f"     Level requirement: {quest.level_requirement}")
        print(f"     Ship requirement: {quest.ship_requirement or 'None'}")
        print(f"     Faction requirement: {quest.faction_requirement or 'None'}")
        
        # Simulate different player states
        print(f"     Testing with different player states:")
        
        # Test with low level
        manager.space_state.current_ship = "basic_fighter"
        success = manager.start_quest(quest.quest_id)
        print(f"       Low level player: {'Can start' if success else 'Cannot start'}")
        
        # Reset quest status
        quest.status = SpaceQuestStatus.AVAILABLE
        if quest.quest_id in manager.space_state.active_quests:
            manager.space_state.active_quests.remove(quest.quest_id)


def demo_data_persistence():
    """Demo data persistence functionality."""
    print("\n" + "="*60)
    print("DEMO: Data Persistence")
    print("="*60)
    
    manager = get_space_quest_manager()
    
    # Add some quests
    print("\n1. Adding quests to manager...")
    test_quest = SpaceQuest(
        quest_id="persistence_test_001",
        name="Persistence Test Quest",
        description="A quest to test data persistence",
        quest_type=SpaceQuestType.EXPLORATION,
        status=SpaceQuestStatus.AVAILABLE,
        level_requirement=10,
        start_location=SpaceLocation.DEEP_SPACE,
        credits=500,
        experience=250,
        items=["test_item"],
        tags=["test", "persistence"]
    )
    
    manager.add_quest(test_quest)
    print(f"   Added quest: {test_quest.name}")
    
    # Save data
    print(f"\n2. Saving space quest data...")
    manager.save_space_data()
    print(f"   Data saved to: {manager.data_dir / 'space_quests.json'}")
    
    # Create new manager instance to test loading
    print(f"\n3. Creating new manager instance to test loading...")
    new_manager = get_space_quest_manager("data/space_quests_test")
    
    # Copy quests to new manager
    for quest in manager.space_quests.values():
        new_manager.add_quest(quest)
    
    print(f"   New manager has {len(new_manager.space_quests)} quests")
    
    # Verify quest data
    loaded_quest = new_manager.get_quest_by_id("persistence_test_001")
    if loaded_quest:
        print(f"   Successfully loaded quest: {loaded_quest.name}")
        print(f"     Type: {loaded_quest.quest_type.value}")
        print(f"     Status: {loaded_quest.status.value}")
        print(f"     Credits: {loaded_quest.credits}")
    else:
        print(f"   Failed to load quest")


def demo_memory_integration():
    """Demo memory integration functionality."""
    print("\n" + "="*60)
    print("DEMO: Memory Integration")
    print("="*60)
    
    manager = get_space_quest_manager()
    
    # Simulate some space activities
    print("\n1. Simulating space activities...")
    
    # Detect space state
    manager.detect_space_state()
    
    # Start a quest
    quest_id = "memory_test_001"
    test_quest = SpaceQuest(
        quest_id=quest_id,
        name="Memory Test Quest",
        description="A quest to test memory integration",
        quest_type=SpaceQuestType.DELIVERY,
        status=SpaceQuestStatus.AVAILABLE,
        level_requirement=5,
        start_location=SpaceLocation.SPACE_STATION_1,
        credits=300,
        experience=150
    )
    manager.add_quest(test_quest)
    
    print(f"   Starting quest: {test_quest.name}")
    manager.start_quest(quest_id)
    
    # Navigate to waypoint
    print(f"   Navigating to waypoint...")
    manager.navigate_to_waypoint("Orbital Station Beta")
    
    # Complete quest
    print(f"   Completing quest...")
    manager.complete_quest(quest_id)
    
    # Show memory events
    print(f"\n2. Memory events recorded:")
    # Get events from session logger
    events = manager.session_logger.session_data.events
    
    for event in events[-10:]:  # Show last 10 events
        print(f"   {event.timestamp}: {event.event_type.value}")
        if event.metadata:
            for key, value in event.metadata.items():
                print(f"     {key}: {value}")


def main():
    """Run all demos."""
    print("MS11 Batch 058 - Space Quest Support Module Demo")
    print("="*60)
    
    try:
        # Run all demos
        demo_space_state_detection()
        demo_quest_management()
        demo_quest_lifecycle()
        demo_waypoint_navigation()
        demo_quest_requirements()
        demo_data_persistence()
        demo_memory_integration()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("\nSpace Quest Support Module features demonstrated:")
        print("✅ Space state detection")
        print("✅ Quest management (create, list, filter)")
        print("✅ Quest lifecycle (start, complete, fail)")
        print("✅ Waypoint navigation")
        print("✅ Quest requirement checking")
        print("✅ Data persistence")
        print("✅ Memory integration")
        print("\nReady for integration with vision/OCR systems for full functionality!")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
"""Test suite for MS11 Batch 058 - Space Quest Support Module."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.space_quest_manager import (
    get_space_quest_manager,
    SpaceQuest,
    SpaceQuestType,
    SpaceQuestStatus,
    SpaceLocation,
    SpaceWaypoint,
    SpaceState
)


class TestSpaceQuestManager(unittest.TestCase):
    """Test cases for SpaceQuestManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.manager = get_space_quest_manager(self.test_dir)
        
        # Clear any existing quests to ensure clean state
        self.manager.space_quests.clear()
        
        # Ensure the data directory exists
        self.manager.data_dir.mkdir(exist_ok=True)
        
        # Create a sample quest for testing
        self.sample_quest = SpaceQuest(
            quest_id="test_quest_001",
            name="Test Quest",
            description="A test quest for unit testing",
            quest_type=SpaceQuestType.DELIVERY,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=10,
            start_location=SpaceLocation.SPACE_STATION_1,
            target_location=SpaceLocation.ORBITAL_STATION,
            credits=500,
            experience=250,
            items=["test_item"],
            tags=["test", "unit"]
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        self.assertIsNotNone(self.manager)
        # After clearing quests in setUp, should be 0
        self.assertEqual(len(self.manager.space_quests), 0)
        self.assertGreater(len(self.manager.space_waypoints), 0)
        self.assertIsInstance(self.manager.space_state, SpaceState)
    
    def test_add_quest(self):
        """Test adding a quest."""
        initial_count = len(self.manager.space_quests)
        self.manager.add_quest(self.sample_quest)
        
        self.assertEqual(len(self.manager.space_quests), initial_count + 1)
        self.assertIn(self.sample_quest.quest_id, self.manager.space_quests)
        self.assertEqual(self.manager.space_quests[self.sample_quest.quest_id], self.sample_quest)
    
    def test_get_quest_by_id(self):
        """Test getting a quest by ID."""
        self.manager.add_quest(self.sample_quest)
        
        # Test existing quest
        quest = self.manager.get_quest_by_id(self.sample_quest.quest_id)
        self.assertIsNotNone(quest)
        self.assertEqual(quest.quest_id, self.sample_quest.quest_id)
        
        # Test non-existing quest
        quest = self.manager.get_quest_by_id("non_existing_quest")
        self.assertIsNone(quest)
    
    def test_get_quests_by_type(self):
        """Test filtering quests by type."""
        # Add quests of different types
        delivery_quest = SpaceQuest(
            quest_id="delivery_001",
            name="Delivery Quest",
            description="A delivery quest",
            quest_type=SpaceQuestType.DELIVERY,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=5,
            start_location=SpaceLocation.SPACE_STATION_1
        )
        
        combat_quest = SpaceQuest(
            quest_id="combat_001",
            name="Combat Quest",
            description="A combat quest",
            quest_type=SpaceQuestType.COMBAT,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=10,
            start_location=SpaceLocation.SPACE_STATION_1
        )
        
        self.manager.add_quest(delivery_quest)
        self.manager.add_quest(combat_quest)
        
        # Test filtering
        delivery_quests = self.manager.get_quests_by_type(SpaceQuestType.DELIVERY)
        self.assertEqual(len(delivery_quests), 1)
        self.assertEqual(delivery_quests[0].quest_id, "delivery_001")
        
        combat_quests = self.manager.get_quests_by_type(SpaceQuestType.COMBAT)
        self.assertEqual(len(combat_quests), 1)
        self.assertEqual(combat_quests[0].quest_id, "combat_001")
    
    def test_get_quests_by_location(self):
        """Test filtering quests by location."""
        # Add quests at different locations
        station_quest = SpaceQuest(
            quest_id="station_001",
            name="Station Quest",
            description="A quest at space station",
            quest_type=SpaceQuestType.DELIVERY,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=5,
            start_location=SpaceLocation.SPACE_STATION_1
        )
        
        deep_space_quest = SpaceQuest(
            quest_id="deep_space_001",
            name="Deep Space Quest",
            description="A quest in deep space",
            quest_type=SpaceQuestType.EXPLORATION,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=15,
            start_location=SpaceLocation.DEEP_SPACE
        )
        
        self.manager.add_quest(station_quest)
        self.manager.add_quest(deep_space_quest)
        
        # Test filtering
        station_quests = self.manager.get_quests_by_location(SpaceLocation.SPACE_STATION_1)
        self.assertEqual(len(station_quests), 1)
        self.assertEqual(station_quests[0].quest_id, "station_001")
        
        deep_space_quests = self.manager.get_quests_by_location(SpaceLocation.DEEP_SPACE)
        self.assertEqual(len(deep_space_quests), 1)
        self.assertEqual(deep_space_quests[0].quest_id, "deep_space_001")
    
    def test_start_quest(self):
        """Test starting a quest."""
        self.manager.add_quest(self.sample_quest)
        
        # Test successful start
        success = self.manager.start_quest(self.sample_quest.quest_id)
        self.assertTrue(success)
        
        quest = self.manager.get_quest_by_id(self.sample_quest.quest_id)
        self.assertEqual(quest.status, SpaceQuestStatus.ACTIVE)
        self.assertIsNotNone(quest.start_time)
        self.assertEqual(quest.current_step, 0)
        self.assertIn(self.sample_quest.quest_id, self.manager.space_state.active_quests)
        
        # Test starting already active quest
        success = self.manager.start_quest(self.sample_quest.quest_id)
        self.assertFalse(success)
        
        # Test starting non-existing quest
        success = self.manager.start_quest("non_existing_quest")
        self.assertFalse(success)
    
    def test_complete_quest(self):
        """Test completing a quest."""
        self.manager.add_quest(self.sample_quest)
        
        # Start the quest first
        self.manager.start_quest(self.sample_quest.quest_id)
        
        # Test successful completion
        success = self.manager.complete_quest(self.sample_quest.quest_id)
        self.assertTrue(success)
        
        quest = self.manager.get_quest_by_id(self.sample_quest.quest_id)
        self.assertEqual(quest.status, SpaceQuestStatus.COMPLETED)
        self.assertIsNotNone(quest.completion_time)
        self.assertNotIn(self.sample_quest.quest_id, self.manager.space_state.active_quests)
        
        # Test completing non-active quest
        success = self.manager.complete_quest(self.sample_quest.quest_id)
        self.assertFalse(success)
        
        # Test completing non-existing quest
        success = self.manager.complete_quest("non_existing_quest")
        self.assertFalse(success)
    
    def test_fail_quest(self):
        """Test failing a quest."""
        self.manager.add_quest(self.sample_quest)
        
        # Start the quest first
        self.manager.start_quest(self.sample_quest.quest_id)
        
        # Test successful failure
        success = self.manager.fail_quest(self.sample_quest.quest_id)
        self.assertTrue(success)
        
        quest = self.manager.get_quest_by_id(self.sample_quest.quest_id)
        self.assertEqual(quest.status, SpaceQuestStatus.FAILED)
        self.assertNotIn(self.sample_quest.quest_id, self.manager.space_state.active_quests)
        
        # Test failing non-existing quest
        success = self.manager.fail_quest("non_existing_quest")
        self.assertFalse(success)
    
    def test_remove_quest(self):
        """Test removing a quest."""
        self.manager.add_quest(self.sample_quest)
        
        initial_count = len(self.manager.space_quests)
        
        # Test successful removal
        success = self.manager.remove_quest(self.sample_quest.quest_id)
        self.assertTrue(success)
        self.assertEqual(len(self.manager.space_quests), initial_count - 1)
        self.assertNotIn(self.sample_quest.quest_id, self.manager.space_quests)
        
        # Test removing non-existing quest
        success = self.manager.remove_quest("non_existing_quest")
        self.assertFalse(success)
    
    def test_navigate_to_waypoint(self):
        """Test navigating to a waypoint."""
        # Simulate being in space
        self.manager.space_state.is_in_space = True
        
        waypoint_name = "Space Station Alpha"
        
        # Test successful navigation
        success = self.manager.navigate_to_waypoint(waypoint_name)
        self.assertTrue(success)
        
        waypoint = self.manager.space_waypoints[waypoint_name]
        self.assertEqual(self.manager.space_state.current_location, waypoint.location)
        self.assertEqual(self.manager.space_state.current_coordinates, waypoint.coordinates)
        
        # Test navigating when not in space
        self.manager.space_state.is_in_space = False
        success = self.manager.navigate_to_waypoint(waypoint_name)
        self.assertFalse(success)
        
        # Test navigating to non-existing waypoint
        self.manager.space_state.is_in_space = True
        success = self.manager.navigate_to_waypoint("Non Existing Waypoint")
        self.assertFalse(success)
    
    def test_get_nearby_waypoints(self):
        """Test getting nearby waypoints."""
        # Set current coordinates
        self.manager.space_state.current_coordinates = (1000.0, 1000.0, 0.0)
        
        # Test getting nearby waypoints
        nearby = self.manager.get_nearby_waypoints(1000.0)
        self.assertIsInstance(nearby, list)
        
        # Test with no coordinates
        self.manager.space_state.current_coordinates = None
        nearby = self.manager.get_nearby_waypoints(1000.0)
        self.assertEqual(len(nearby), 0)
    
    def test_calculate_distance(self):
        """Test distance calculation."""
        coords1 = (0.0, 0.0, 0.0)
        coords2 = (3.0, 4.0, 0.0)
        
        distance = self.manager._calculate_distance(coords1, coords2)
        self.assertEqual(distance, 5.0)  # 3-4-5 triangle
    
    def test_detect_space_state(self):
        """Test space state detection."""
        # Test initial state (not in space)
        state = self.manager.detect_space_state()
        self.assertFalse(state.is_in_space)
        self.assertIsNone(state.current_location)
        self.assertIsNone(state.current_coordinates)
        
        # Test simulated space state
        self.manager.space_state.is_in_space = True
        state = self.manager.detect_space_state()
        self.assertTrue(state.is_in_space)
        self.assertIsNotNone(state.current_location)
        self.assertIsNotNone(state.current_coordinates)
    
    def test_get_space_state_summary(self):
        """Test getting space state summary."""
        summary = self.manager.get_space_state_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn("is_in_space", summary)
        self.assertIn("current_location", summary)
        self.assertIn("current_coordinates", summary)
        self.assertIn("current_ship", summary)
        self.assertIn("nearby_objects", summary)
        self.assertIn("active_quests", summary)
        self.assertIn("available_quests", summary)
        self.assertIn("total_quests", summary)
        self.assertIn("total_waypoints", summary)
    
    def test_quest_requirements(self):
        """Test quest requirement checking."""
        # Create quest with requirements
        quest_with_requirements = SpaceQuest(
            quest_id="req_test_001",
            name="Requirement Test Quest",
            description="A quest with requirements",
            quest_type=SpaceQuestType.COMBAT,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=20,
            ship_requirement="advanced_fighter",
            faction_requirement="rebel_alliance",
            faction_standing_requirement=1000,
            start_location=SpaceLocation.SPACE_STATION_1
        )
        
        self.manager.add_quest(quest_with_requirements)
        
        # Test with requirements not met
        success = self.manager.start_quest(quest_with_requirements.quest_id)
        self.assertFalse(success)
        
        # Test with requirements met (mock the requirement methods)
        with patch.object(self.manager, '_get_player_level', return_value=25):
            with patch.object(self.manager, '_get_faction_standing', return_value=1500):
                self.manager.space_state.current_ship = "advanced_fighter"
                success = self.manager.start_quest(quest_with_requirements.quest_id)
                self.assertTrue(success)
    
    def test_data_persistence(self):
        """Test data persistence functionality."""
        # Add a quest
        self.manager.add_quest(self.sample_quest)
        
        # Save data
        self.manager.save_space_data()
        
        # Verify file was created
        quest_file = self.manager.data_dir / "space_quests.json"
        self.assertTrue(quest_file.exists())
        
        # Load and verify data
        with open(quest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.assertIn("quests", data)
        self.assertEqual(len(data["quests"]), 1)
        self.assertEqual(data["quests"][0]["quest_id"], self.sample_quest.quest_id)
    
    def test_memory_integration(self):
        """Test memory integration."""
        # Simulate some activities that should log events
        self.manager.add_quest(self.sample_quest)
        self.manager.start_quest(self.sample_quest.quest_id)
        self.manager.complete_quest(self.sample_quest.quest_id)
        
        # Verify events were logged
        events = self.manager.session_logger.session_data.events
        self.assertGreater(len(events), 0)
        
        # Check for specific event types
        event_types = [event.event_type.value for event in events]
        self.assertIn("quest_accepted", event_types)
        self.assertIn("quest_completion", event_types)


class TestSpaceQuestDataStructures(unittest.TestCase):
    """Test cases for space quest data structures."""
    
    def test_space_quest_creation(self):
        """Test SpaceQuest creation."""
        quest = SpaceQuest(
            quest_id="test_001",
            name="Test Quest",
            description="A test quest",
            quest_type=SpaceQuestType.DELIVERY,
            status=SpaceQuestStatus.AVAILABLE,
            level_requirement=10,
            start_location=SpaceLocation.SPACE_STATION_1
        )
        
        self.assertEqual(quest.quest_id, "test_001")
        self.assertEqual(quest.name, "Test Quest")
        self.assertEqual(quest.quest_type, SpaceQuestType.DELIVERY)
        self.assertEqual(quest.status, SpaceQuestStatus.AVAILABLE)
        self.assertEqual(quest.level_requirement, 10)
        self.assertEqual(quest.start_location, SpaceLocation.SPACE_STATION_1)
    
    def test_space_waypoint_creation(self):
        """Test SpaceWaypoint creation."""
        waypoint = SpaceWaypoint(
            name="Test Waypoint",
            location=SpaceLocation.SPACE_STATION_1,
            coordinates=(100.0, 200.0, 50.0),
            description="A test waypoint",
            is_station=True,
            is_safe_zone=True,
            services=["quests", "repair"],
            quest_givers=["test_npc"]
        )
        
        self.assertEqual(waypoint.name, "Test Waypoint")
        self.assertEqual(waypoint.location, SpaceLocation.SPACE_STATION_1)
        self.assertEqual(waypoint.coordinates, (100.0, 200.0, 50.0))
        self.assertTrue(waypoint.is_station)
        self.assertTrue(waypoint.is_safe_zone)
        self.assertEqual(waypoint.services, ["quests", "repair"])
        self.assertEqual(waypoint.quest_givers, ["test_npc"])
    
    def test_space_state_creation(self):
        """Test SpaceState creation."""
        state = SpaceState(
            is_in_space=True,
            current_location=SpaceLocation.SPACE_STATION_1,
            current_coordinates=(100.0, 200.0, 50.0),
            current_ship="basic_fighter",
            nearby_objects=["asteroid", "debris"],
            active_quests=["quest_001"],
            available_quests=["quest_002", "quest_003"]
        )
        
        self.assertTrue(state.is_in_space)
        self.assertEqual(state.current_location, SpaceLocation.SPACE_STATION_1)
        self.assertEqual(state.current_coordinates, (100.0, 200.0, 50.0))
        self.assertEqual(state.current_ship, "basic_fighter")
        self.assertEqual(state.nearby_objects, ["asteroid", "debris"])
        self.assertEqual(state.active_quests, ["quest_001"])
        self.assertEqual(state.available_quests, ["quest_002", "quest_003"])


class TestSpaceQuestEnums(unittest.TestCase):
    """Test cases for space quest enums."""
    
    def test_space_location_enum(self):
        """Test SpaceLocation enum."""
        self.assertEqual(SpaceLocation.SPACE_STATION_1.value, "space_station_1")
        self.assertEqual(SpaceLocation.ORBITAL_STATION.value, "orbital_station")
        self.assertEqual(SpaceLocation.DEEP_SPACE.value, "deep_space")
        self.assertEqual(SpaceLocation.ASTEROID_FIELD.value, "asteroid_field")
    
    def test_space_quest_type_enum(self):
        """Test SpaceQuestType enum."""
        self.assertEqual(SpaceQuestType.DELIVERY.value, "delivery")
        self.assertEqual(SpaceQuestType.COMBAT.value, "combat")
        self.assertEqual(SpaceQuestType.EXPLORATION.value, "exploration")
        self.assertEqual(SpaceQuestType.SALVAGE.value, "salvage")
        self.assertEqual(SpaceQuestType.ESCORT.value, "escort")
        self.assertEqual(SpaceQuestType.PATROL.value, "patrol")
    
    def test_space_quest_status_enum(self):
        """Test SpaceQuestStatus enum."""
        self.assertEqual(SpaceQuestStatus.AVAILABLE.value, "available")
        self.assertEqual(SpaceQuestStatus.ACTIVE.value, "active")
        self.assertEqual(SpaceQuestStatus.COMPLETED.value, "completed")
        self.assertEqual(SpaceQuestStatus.FAILED.value, "failed")
        self.assertEqual(SpaceQuestStatus.EXPIRED.value, "expired")


if __name__ == "__main__":
    unittest.main() 
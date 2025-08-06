"""
Unit tests for Special Goals & Unlock Paths System.

Tests the special goals tracking and completion system including goal loading,
requirement checking, goal starting, progress tracking, and integration
with navigation, travel, and collection systems.
"""

import json
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Import the modules to test
from core.special_goals import (
    GoalType, GoalStatus, GoalPriority, GoalRequirement, SpecialGoal,
    GoalProgress, SpecialGoalsState, SpecialGoals, get_special_goals,
    start_special_goal, work_on_current_goal, get_special_goals_status,
    list_special_goals, get_available_goals
)


class TestGoalRequirement:
    """Test the GoalRequirement dataclass."""
    
    def test_goal_requirement_creation(self):
        """Test creating a GoalRequirement."""
        requirement = GoalRequirement(
            type="reputation",
            target="tatooine_2000",
            description="Reach 2000 reputation on Tatooine",
            current_progress=1500,
            required_progress=2000
        )
        
        assert requirement.type == "reputation"
        assert requirement.target == "tatooine_2000"
        assert requirement.description == "Reach 2000 reputation on Tatooine"
        assert requirement.current_progress == 1500
        assert requirement.required_progress == 2000
    
    def test_goal_requirement_defaults(self):
        """Test GoalRequirement with default values."""
        requirement = GoalRequirement(
            type="quest",
            target="tatooine_artifact_hunt",
            description="Complete the Tatooine Artifact Hunt quest"
        )
        
        assert requirement.type == "quest"
        assert requirement.target == "tatooine_artifact_hunt"
        assert requirement.description == "Complete the Tatooine Artifact Hunt quest"
        assert requirement.current_progress is None
        assert requirement.required_progress is None


class TestSpecialGoal:
    """Test the SpecialGoal dataclass."""
    
    def test_special_goal_creation(self):
        """Test creating a SpecialGoal."""
        requirements = [
            GoalRequirement(
                type="reputation",
                target="tatooine_2000",
                description="Reach 2000 reputation on Tatooine",
                required_progress=2000
            )
        ]
        
        goal = SpecialGoal(
            name="Third Character Slot Unlock",
            goal_type=GoalType.CHARACTER_SLOT,
            description="Unlock the third character slot",
            priority=GoalPriority.HIGH,
            planet="tatooine",
            zone="mos_eisley",
            coordinates=(100, 200),
            requirements=requirements,
            rewards=["third_character_slot"],
            estimated_time_hours=8.0
        )
        
        assert goal.name == "Third Character Slot Unlock"
        assert goal.goal_type == GoalType.CHARACTER_SLOT
        assert goal.description == "Unlock the third character slot"
        assert goal.priority == GoalPriority.HIGH
        assert goal.planet == "tatooine"
        assert goal.zone == "mos_eisley"
        assert goal.coordinates == (100, 200)
        assert len(goal.requirements) == 1
        assert goal.rewards == ["third_character_slot"]
        assert goal.estimated_time_hours == 8.0


class TestGoalProgress:
    """Test the GoalProgress dataclass."""
    
    def test_goal_progress_creation(self):
        """Test creating a GoalProgress."""
        now = datetime.now()
        progress = GoalProgress(
            goal_name="Test Goal",
            status=GoalStatus.IN_PROGRESS,
            current_step="Working on reputation",
            steps_completed=2,
            total_steps=5,
            start_time=now,
            last_updated=now
        )
        
        assert progress.goal_name == "Test Goal"
        assert progress.status == GoalStatus.IN_PROGRESS
        assert progress.current_step == "Working on reputation"
        assert progress.steps_completed == 2
        assert progress.total_steps == 5
        assert progress.start_time == now
        assert progress.last_updated == now
        assert progress.completion_time is None


class TestSpecialGoalsState:
    """Test the SpecialGoalsState dataclass."""
    
    def test_special_goals_state_creation(self):
        """Test creating a SpecialGoalsState."""
        now = datetime.now()
        state = SpecialGoalsState(
            total_goals=10,
            active_goals=2,
            completed_goals=3,
            session_start_time=now,
            last_goal_completion=now
        )
        
        assert state.total_goals == 10
        assert state.active_goals == 2
        assert state.completed_goals == 3
        assert state.session_start_time == now
        assert state.last_goal_completion == now
        assert state.current_goal is None


@pytest.fixture
def temp_goals_file():
    """Create a temporary goals file for testing."""
    test_data = {
        "goals": [
            {
                "name": "Test Character Slot",
                "type": "character_slot",
                "description": "Test character slot unlock",
                "priority": "high",
                "planet": "tatooine",
                "zone": "mos_eisley",
                "coordinates": [100, 200],
                "requirements": [
                    {
                        "type": "reputation",
                        "target": "tatooine_2000",
                        "description": "Reach 2000 reputation on Tatooine",
                        "required_progress": 2000
                    }
                ],
                "rewards": ["test_character_slot"],
                "estimated_time_hours": 5.0
            },
            {
                "name": "Test Key Quest",
                "type": "key_quest",
                "description": "Test key quest",
                "priority": "critical",
                "planet": "naboo",
                "zone": "theed",
                "coordinates": [200, 300],
                "requirements": [
                    {
                        "type": "quest",
                        "target": "test_quest",
                        "description": "Complete the test quest",
                        "required_progress": "completed"
                    }
                ],
                "rewards": ["test_access"],
                "estimated_time_hours": 3.0
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        f.flush()  # Ensure data is written
        temp_path = Path(f.name)
    
    yield temp_path
    
    try:
        temp_path.unlink(missing_ok=True)
    except PermissionError:
        pass  # File might be locked, ignore cleanup error


@pytest.fixture
def special_goals():
    """Create a SpecialGoals instance for testing."""
    with patch('core.special_goals.Path.mkdir') as mock_mkdir:
        with patch('core.special_goals.logging.FileHandler') as mock_file_handler:
            mock_handler = Mock()
            mock_handler.level = logging.INFO
            mock_file_handler.return_value = mock_handler
            
            goals = SpecialGoals()
            return goals


class TestSpecialGoals:
    """Test the SpecialGoals class."""
    
    def test_special_goals_initialization(self, special_goals):
        """Test SpecialGoals initialization."""
        # The goals should have loaded (either from file or defaults)
        assert len(special_goals.goals) >= 2
        assert special_goals.state.total_goals >= 2
        assert special_goals.state.active_goals == 0
        assert special_goals.state.completed_goals == 0
        assert special_goals.logger is not None
    
    def test_load_goals_from_file(self, temp_goals_file):
        """Test loading goals from a file."""
        with patch('core.special_goals.Path.mkdir') as mock_mkdir:
            with patch('core.special_goals.logging.FileHandler') as mock_file_handler:
                mock_handler = Mock()
                mock_handler.level = logging.INFO
                mock_file_handler.return_value = mock_handler
                
                with patch('core.special_goals.Path') as mock_path:
                    mock_path.return_value.exists.return_value = True
                    mock_path.return_value = temp_goals_file
                    
                    goals = SpecialGoals()
                    
                    assert len(goals.goals) == 2
                    assert "Test Character Slot" in goals.goals
                    assert "Test Key Quest" in goals.goals
    
    def test_create_default_goals(self):
        """Test creating default goals when file doesn't exist."""
        with patch('core.special_goals.Path.mkdir') as mock_mkdir:
            with patch('core.special_goals.logging.FileHandler') as mock_file_handler:
                mock_handler = Mock()
                mock_handler.level = logging.INFO
                mock_file_handler.return_value = mock_handler
                
                with patch('core.special_goals.Path') as mock_path:
                    mock_path.return_value.exists.return_value = False
                    
                    goals = SpecialGoals()
                    
                    # Should have loaded default goals
                    assert len(goals.goals) >= 2
    
    def test_check_goal_requirements(self, special_goals):
        """Test checking goal requirements."""
        # Add a test goal
        test_goal = SpecialGoal(
            name="Test Goal",
            goal_type=GoalType.CHARACTER_SLOT,
            description="Test goal",
            priority=GoalPriority.HIGH,
            planet="tatooine",
            zone="mos_eisley",
            coordinates=(100, 200),
            requirements=[
                GoalRequirement(
                    type="level",
                    target="level_25",
                    description="Reach level 25",
                    required_progress=25
                )
            ],
            rewards=["test_reward"]
        )
        special_goals.goals["Test Goal"] = test_goal
        
        # Test requirement checking
        result = special_goals.check_goal_requirements("Test Goal")
        
        assert result["valid"] is True
        assert "requirements" in result
        assert len(result["requirements"]) == 1
    
    def test_check_goal_requirements_not_found(self, special_goals):
        """Test checking requirements for non-existent goal."""
        result = special_goals.check_goal_requirements("Non-existent Goal")
        
        assert result["valid"] is False
        assert "error" in result
    
    def test_start_goal_success(self, special_goals):
        """Test successfully starting a goal."""
        # Add a test goal
        test_goal = SpecialGoal(
            name="Test Goal",
            goal_type=GoalType.CHARACTER_SLOT,
            description="Test goal",
            priority=GoalPriority.HIGH,
            planet="tatooine",
            zone="mos_eisley",
            coordinates=(100, 200),
            requirements=[
                GoalRequirement(
                    type="level",
                    target="level_25",
                    description="Reach level 25",
                    required_progress=25
                )
            ],
            rewards=["test_reward"]
        )
        special_goals.goals["Test Goal"] = test_goal
        
        # Mock requirement checking to return success
        with patch.object(special_goals, 'check_goal_requirements') as mock_check:
            mock_check.return_value = {
                "valid": True,
                "all_requirements_met": True,
                "requirements": []
            }
            
            success = special_goals.start_goal("Test Goal")
            
            assert success is True
            assert "Test Goal" in special_goals.progress
            assert special_goals.progress["Test Goal"].status == GoalStatus.IN_PROGRESS
            assert special_goals.state.current_goal == test_goal
    
    def test_start_goal_requirements_not_met(self, special_goals):
        """Test starting a goal when requirements are not met."""
        # Add a test goal
        test_goal = SpecialGoal(
            name="Test Goal",
            goal_type=GoalType.CHARACTER_SLOT,
            description="Test goal",
            priority=GoalPriority.HIGH,
            planet="tatooine",
            zone="mos_eisley",
            coordinates=(100, 200),
            requirements=[
                GoalRequirement(
                    type="level",
                    target="level_25",
                    description="Reach level 25",
                    required_progress=25
                )
            ],
            rewards=["test_reward"]
        )
        special_goals.goals["Test Goal"] = test_goal
        
        # Mock requirement checking to return failure
        with patch.object(special_goals, 'check_goal_requirements') as mock_check:
            mock_check.return_value = {
                "valid": True,
                "all_requirements_met": False,
                "requirements": []
            }
            
            success = special_goals.start_goal("Test Goal")
            
            assert success is False
    
    def test_start_goal_not_found(self, special_goals):
        """Test starting a non-existent goal."""
        success = special_goals.start_goal("Non-existent Goal")
        
        assert success is False
    
    @patch('core.special_goals.get_travel_automation')
    @patch('core.special_goals.get_navigator')
    @patch('core.special_goals.get_dialogue_detector')
    def test_work_on_current_goal_success(self, mock_dialogue_detector, mock_navigator, mock_travel_automation, special_goals):
        """Test successfully working on current goal."""
        # Set up a current goal
        test_goal = SpecialGoal(
            name="Test Goal",
            goal_type=GoalType.CHARACTER_SLOT,
            description="Test goal",
            priority=GoalPriority.HIGH,
            planet="tatooine",
            zone="mos_eisley",
            coordinates=(100, 200),
            requirements=[
                GoalRequirement(
                    type="level",
                    target="level_25",
                    description="Reach level 25",
                    required_progress=25
                )
            ],
            rewards=["test_reward"]
        )
        special_goals.state.current_goal = test_goal
        special_goals.progress["Test Goal"] = GoalProgress(
            goal_name="Test Goal",
            status=GoalStatus.IN_PROGRESS,
            total_steps=1
        )
        
        # Mock successful travel and interaction
        mock_travel_automation.return_value.travel_to_unlock.return_value = True
        mock_dialogue_detector.return_value.wait_for_dialogue.return_value = Mock(options=["Accept", "Cancel"])
        mock_dialogue_detector.return_value.click_dialogue_option.return_value = None
        
        success = special_goals.work_on_current_goal()
        
        assert success is True
        assert special_goals.progress["Test Goal"].steps_completed == 1
    
    def test_work_on_current_goal_no_current_goal(self, special_goals):
        """Test working on goal when no current goal exists."""
        success = special_goals.work_on_current_goal()
        
        assert success is False
    
    @patch('core.special_goals.get_travel_automation')
    @patch('core.special_goals.get_navigator')
    def test_work_on_current_goal_navigation_failure(self, mock_navigator, mock_travel_automation, special_goals):
        """Test working on goal when navigation fails."""
        # Set up a current goal
        test_goal = SpecialGoal(
            name="Test Goal",
            goal_type=GoalType.CHARACTER_SLOT,
            description="Test goal",
            priority=GoalPriority.HIGH,
            planet="tatooine",
            zone="mos_eisley",
            coordinates=(100, 200),
            requirements=[
                GoalRequirement(
                    type="level",
                    target="level_25",
                    description="Reach level 25",
                    required_progress=25
                )
            ],
            rewards=["test_reward"]
        )
        special_goals.state.current_goal = test_goal
        special_goals.progress["Test Goal"] = GoalProgress(
            goal_name="Test Goal",
            status=GoalStatus.IN_PROGRESS,
            total_steps=1
        )
        
        # Mock failed travel and navigation
        mock_travel_automation.return_value.travel_to_unlock.return_value = False
        mock_navigator.return_value.navigate_to_waypoint.return_value = False
        
        success = special_goals.work_on_current_goal()
        
        assert success is False
    
    def test_get_available_goals(self, special_goals):
        """Test getting available goals."""
        # Add test goals with different priorities
        high_priority_goal = SpecialGoal(
            name="High Priority Goal",
            goal_type=GoalType.CHARACTER_SLOT,
            description="High priority goal",
            priority=GoalPriority.HIGH,
            planet="tatooine",
            zone="mos_eisley",
            coordinates=(100, 200),
            requirements=[],
            rewards=["test_reward"]
        )
        
        critical_priority_goal = SpecialGoal(
            name="Critical Priority Goal",
            goal_type=GoalType.KEY_QUEST,
            description="Critical priority goal",
            priority=GoalPriority.CRITICAL,
            planet="naboo",
            zone="theed",
            coordinates=(200, 300),
            requirements=[],
            rewards=["test_reward"]
        )
        
        special_goals.goals["High Priority Goal"] = high_priority_goal
        special_goals.goals["Critical Priority Goal"] = critical_priority_goal
        
        # Mock requirement checking to return success for all goals
        with patch.object(special_goals, 'check_goal_requirements') as mock_check:
            mock_check.return_value = {
                "valid": True,
                "all_requirements_met": True,
                "requirements": []
            }
            
            available_goals = special_goals.get_available_goals()
            
            assert len(available_goals) == 2
            # Critical priority should come first
            assert available_goals[0].priority == GoalPriority.CRITICAL
    
    def test_get_goal_status(self, special_goals):
        """Test getting goal status."""
        status = special_goals.get_goal_status()
        
        assert "total_goals" in status
        assert "active_goals" in status
        assert "completed_goals" in status
        assert "progress_by_goal" in status
    
    def test_list_goals_with_filters(self, special_goals):
        """Test listing goals with filters."""
        # Add test goals
        character_slot_goal = SpecialGoal(
            name="Character Slot Goal",
            goal_type=GoalType.CHARACTER_SLOT,
            description="Character slot goal",
            priority=GoalPriority.HIGH,
            planet="tatooine",
            zone="mos_eisley",
            coordinates=(100, 200),
            requirements=[],
            rewards=["test_reward"]
        )
        
        key_quest_goal = SpecialGoal(
            name="Key Quest Goal",
            goal_type=GoalType.KEY_QUEST,
            description="Key quest goal",
            priority=GoalPriority.CRITICAL,
            planet="naboo",
            zone="theed",
            coordinates=(200, 300),
            requirements=[],
            rewards=["test_reward"]
        )
        
        special_goals.goals["Character Slot Goal"] = character_slot_goal
        special_goals.goals["Key Quest Goal"] = key_quest_goal
        
        # Test filtering by goal type
        character_slot_goals = special_goals.list_goals(goal_type=GoalType.CHARACTER_SLOT)
        assert len(character_slot_goals) == 1
        assert character_slot_goals[0].goal_type == GoalType.CHARACTER_SLOT
        
        # Test filtering by priority
        critical_goals = special_goals.list_goals(priority=GoalPriority.CRITICAL)
        assert len(critical_goals) == 1
        assert critical_goals[0].priority == GoalPriority.CRITICAL


class TestGlobalFunctions:
    """Test the global convenience functions."""
    
    @patch('core.special_goals.get_special_goals')
    def test_start_special_goal(self, mock_get_special_goals):
        """Test the start_special_goal global function."""
        mock_goals = Mock()
        mock_get_special_goals.return_value = mock_goals
        mock_goals.start_goal.return_value = True
        
        success = start_special_goal("Test Goal")
        
        assert success is True
        mock_goals.start_goal.assert_called_once_with("Test Goal")
    
    @patch('core.special_goals.get_special_goals')
    def test_work_on_current_goal(self, mock_get_special_goals):
        """Test the work_on_current_goal global function."""
        mock_goals = Mock()
        mock_get_special_goals.return_value = mock_goals
        mock_goals.work_on_current_goal.return_value = True
        
        success = work_on_current_goal()
        
        assert success is True
        mock_goals.work_on_current_goal.assert_called_once()
    
    @patch('core.special_goals.get_special_goals')
    def test_get_special_goals_status(self, mock_get_special_goals):
        """Test the get_special_goals_status global function."""
        mock_goals = Mock()
        mock_get_special_goals.return_value = mock_goals
        mock_goals.get_goal_status.return_value = {"test": "status"}
        
        status = get_special_goals_status()
        
        assert status == {"test": "status"}
        mock_goals.get_goal_status.assert_called_once()
    
    @patch('core.special_goals.get_special_goals')
    def test_list_special_goals(self, mock_get_special_goals):
        """Test the list_special_goals global function."""
        mock_goals = Mock()
        mock_get_special_goals.return_value = mock_goals
        mock_goals.list_goals.return_value = []
        
        goals = list_special_goals(goal_type=GoalType.CHARACTER_SLOT)
        
        assert goals == []
        mock_goals.list_goals.assert_called_once_with(GoalType.CHARACTER_SLOT, None, None)
    
    @patch('core.special_goals.get_special_goals')
    def test_get_available_goals(self, mock_get_special_goals):
        """Test the get_available_goals global function."""
        mock_goals = Mock()
        mock_get_special_goals.return_value = mock_goals
        mock_goals.get_available_goals.return_value = []
        
        goals = get_available_goals(priority=GoalPriority.HIGH)
        
        assert goals == []
        mock_goals.get_available_goals.assert_called_once_with(GoalPriority.HIGH)


class TestSingletonPattern:
    """Test the singleton pattern implementation."""
    
    def test_singleton_pattern(self):
        """Test that get_special_goals returns the same instance."""
        # Reset the singleton instance
        import core.special_goals
        core.special_goals._special_goals_instance = None
        
        # Get two instances
        instance1 = get_special_goals()
        instance2 = get_special_goals()
        
        # They should be the same instance
        assert instance1 is instance2


class TestIntegration:
    """Integration tests for the special goals system."""
    
    @patch('core.special_goals.Path.mkdir')
    @patch('core.special_goals.logging.FileHandler')
    def test_full_goal_lifecycle(self, mock_file_handler, mock_mkdir):
        """Test a complete goal lifecycle from start to completion."""
        mock_handler = Mock()
        mock_handler.level = logging.INFO
        mock_file_handler.return_value = mock_handler
        
        # Create goals system
        goals = SpecialGoals()
        
        # Add a test goal
        test_goal = SpecialGoal(
            name="Test Lifecycle Goal",
            goal_type=GoalType.CHARACTER_SLOT,
            description="Test goal for lifecycle",
            priority=GoalPriority.HIGH,
            planet="tatooine",
            zone="mos_eisley",
            coordinates=(100, 200),
            requirements=[
                GoalRequirement(
                    type="level",
                    target="level_25",
                    description="Reach level 25",
                    required_progress=25
                )
            ],
            rewards=["test_reward"]
        )
        goals.goals["Test Lifecycle Goal"] = test_goal
        
        # Mock requirement checking
        with patch.object(goals, 'check_goal_requirements') as mock_check:
            mock_check.return_value = {
                "valid": True,
                "all_requirements_met": True,
                "requirements": []
            }
            
            # Start the goal
            success = goals.start_goal("Test Lifecycle Goal")
            assert success is True
            assert goals.state.current_goal == test_goal
            assert goals.progress["Test Lifecycle Goal"].status == GoalStatus.IN_PROGRESS
            
            # Work on the goal
            with patch('core.special_goals.get_travel_automation') as mock_travel:
                with patch('core.special_goals.get_dialogue_detector') as mock_dialogue:
                    mock_travel.return_value.travel_to_unlock.return_value = True
                    mock_dialogue.return_value.wait_for_dialogue.return_value = Mock(options=["Accept"])
                    mock_dialogue.return_value.click_dialogue_option.return_value = None
                    
                    work_success = goals.work_on_current_goal()
                    assert work_success is True
                    assert goals.progress["Test Lifecycle Goal"].steps_completed == 1
                    assert goals.progress["Test Lifecycle Goal"].status == GoalStatus.COMPLETED
                    assert goals.state.completed_goals == 1
                    assert goals.state.current_goal is None


class TestJSONSerialization:
    """Test JSON serialization of special goals data."""
    
    def test_goal_requirement_serialization(self):
        """Test that GoalRequirement can be serialized to JSON."""
        requirement = GoalRequirement(
            type="reputation",
            target="tatooine_2000",
            description="Reach 2000 reputation on Tatooine",
            current_progress=1500,
            required_progress=2000
        )
        
        # Convert to dict and back to JSON
        requirement_dict = {
            "type": requirement.type,
            "target": requirement.target,
            "description": requirement.description,
            "current_progress": requirement.current_progress,
            "required_progress": requirement.required_progress
        }
        
        json_str = json.dumps(requirement_dict)
        parsed_dict = json.loads(json_str)
        
        assert parsed_dict["type"] == "reputation"
        assert parsed_dict["target"] == "tatooine_2000"
        assert parsed_dict["description"] == "Reach 2000 reputation on Tatooine"
        assert parsed_dict["current_progress"] == 1500
        assert parsed_dict["required_progress"] == 2000
    
    def test_special_goal_serialization(self):
        """Test that SpecialGoal can be serialized to JSON."""
        requirements = [
            GoalRequirement(
                type="reputation",
                target="tatooine_2000",
                description="Reach 2000 reputation on Tatooine",
                required_progress=2000
            )
        ]
        
        goal = SpecialGoal(
            name="Test Goal",
            goal_type=GoalType.CHARACTER_SLOT,
            description="Test goal",
            priority=GoalPriority.HIGH,
            planet="tatooine",
            zone="mos_eisley",
            coordinates=(100, 200),
            requirements=requirements,
            rewards=["test_reward"],
            estimated_time_hours=8.0
        )
        
        # Convert to dict and back to JSON
        goal_dict = {
            "name": goal.name,
            "type": goal.goal_type.value,
            "description": goal.description,
            "priority": goal.priority.value,
            "planet": goal.planet,
            "zone": goal.zone,
            "coordinates": list(goal.coordinates),
            "rewards": goal.rewards,
            "estimated_time_hours": goal.estimated_time_hours
        }
        
        json_str = json.dumps(goal_dict)
        parsed_dict = json.loads(json_str)
        
        assert parsed_dict["name"] == "Test Goal"
        assert parsed_dict["type"] == "character_slot"
        assert parsed_dict["priority"] == "high"
        assert parsed_dict["planet"] == "tatooine"
        assert parsed_dict["coordinates"] == [100, 200]
        assert parsed_dict["rewards"] == ["test_reward"]
        assert parsed_dict["estimated_time_hours"] == 8.0 
"""Test suite for Batch 102 - Quest Logic Parser (MTG Integration)."""

import json
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import pytest

from core.quest_logic_parser import (
    QuestLogicParser,
    QuestLogicTemplate,
    WaitForTrigger,
    TravelToZone,
    UseItem,
    EscortDefend,
    QuestTriggerType,
    QuestLogicType,
    QuestState,
    QuestTrigger,
    QuestLogicBlock,
    QuestExecutionState,
    quest_logic_parser,
    parse_and_execute_quest
)


class TestQuestLogicParser:
    """Test the main Quest Logic Parser functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = QuestLogicParser()
        self.sample_quest_data = {
            "quest_id": "test_quest",
            "steps": [
                {
                    "step_id": "test_dialogue",
                    "type": "dialogue",
                    "npc_id": "test_npc",
                    "timeout_seconds": 300,
                    "retry_count": 3
                },
                {
                    "step_id": "test_move",
                    "type": "move",
                    "data": {
                        "coords": [100, 200],
                        "planet": "tatooine"
                    },
                    "timeout_seconds": 600,
                    "retry_count": 3
                },
                {
                    "step_id": "test_use_item",
                    "type": "use_item",
                    "item_name": "test_key",
                    "use_effect": {
                        "type": "unlock_door",
                        "door_id": "test_door"
                    },
                    "timeout_seconds": 300,
                    "retry_count": 3
                },
                {
                    "step_id": "test_escort",
                    "type": "escort",
                    "target_info": {
                        "name": "Test Target",
                        "health": 100
                    },
                    "route_points": [[150, 250], [200, 300]],
                    "threat_level": "medium",
                    "timeout_seconds": 900,
                    "retry_count": 2
                }
            ]
        }
        self.test_context = {
            "current_location": [0, 0],
            "inventory": {"test_key": 1},
            "nearby_npcs": {"test_npc": True},
            "player_health": 100,
            "target_health": 100
        }
    
    def test_parser_initialization(self):
        """Test parser initialization."""
        assert self.parser.templates_dir.exists()
        assert len(self.parser.template_registry) == 4
        assert QuestLogicType.WAIT_FOR_TRIGGER in self.parser.template_registry
        assert QuestLogicType.TRAVEL_TO_ZONE in self.parser.template_registry
        assert QuestLogicType.USE_ITEM in self.parser.template_registry
        assert QuestLogicType.ESCORT_DEFEND in self.parser.template_registry
    
    def test_parse_quest_template(self):
        """Test parsing quest data into logic blocks."""
        logic_blocks = self.parser.parse_quest_template(self.sample_quest_data)
        
        assert len(logic_blocks) == 4
        assert logic_blocks[0].logic_type == QuestLogicType.WAIT_FOR_TRIGGER
        assert logic_blocks[1].logic_type == QuestLogicType.TRAVEL_TO_ZONE
        assert logic_blocks[2].logic_type == QuestLogicType.USE_ITEM
        assert logic_blocks[3].logic_type == QuestLogicType.ESCORT_DEFEND
    
    def test_create_wait_for_trigger_block(self):
        """Test creating WaitForTrigger logic block."""
        step = {
            "step_id": "test_trigger",
            "type": "dialogue",
            "npc_id": "test_npc",
            "timeout_seconds": 300,
            "retry_count": 3
        }
        
        block = self.parser._create_wait_for_trigger_block(step)
        
        assert block.logic_type == QuestLogicType.WAIT_FOR_TRIGGER
        assert block.timeout_seconds == 300
        assert block.retry_count == 3
        assert "test_npc" in block.parameters["conditions"]["npc_present"]
    
    def test_create_travel_to_zone_block(self):
        """Test creating TravelToZone logic block."""
        step = {
            "step_id": "test_travel",
            "type": "move",
            "data": {
                "coords": [100, 200],
                "planet": "tatooine"
            },
            "timeout_seconds": 600,
            "retry_count": 3
        }
        
        block = self.parser._create_travel_to_zone_block(step)
        
        assert block.logic_type == QuestLogicType.TRAVEL_TO_ZONE
        assert block.timeout_seconds == 600
        assert block.retry_count == 3
        assert block.parameters["destination"]["coordinates"] == [100, 200]
        assert block.parameters["destination"]["planet"] == "tatooine"
    
    def test_create_use_item_block(self):
        """Test creating UseItem logic block."""
        step = {
            "step_id": "test_use_item",
            "type": "use_item",
            "item_name": "test_key",
            "use_effect": {
                "type": "unlock_door",
                "door_id": "test_door"
            },
            "timeout_seconds": 300,
            "retry_count": 3
        }
        
        block = self.parser._create_use_item_block(step)
        
        assert block.logic_type == QuestLogicType.USE_ITEM
        assert block.timeout_seconds == 300
        assert block.retry_count == 3
        assert block.parameters["item_name"] == "test_key"
        assert block.parameters["use_effect"]["type"] == "unlock_door"
    
    def test_create_escort_defend_block(self):
        """Test creating EscortDefend logic block."""
        step = {
            "step_id": "test_escort",
            "type": "escort",
            "target_info": {
                "name": "Test Target",
                "health": 100
            },
            "route_points": [[150, 250], [200, 300]],
            "threat_level": "medium",
            "timeout_seconds": 900,
            "retry_count": 2
        }
        
        block = self.parser._create_escort_defend_block(step)
        
        assert block.logic_type == QuestLogicType.ESCORT_DEFEND
        assert block.timeout_seconds == 900
        assert block.retry_count == 2
        assert block.parameters["mission_type"] == "escort"
        assert block.parameters["target_info"]["name"] == "Test Target"
    
    def test_execute_quest_logic_success(self):
        """Test successful quest execution."""
        logic_blocks = self.parser.parse_quest_template(self.sample_quest_data)
        
        with patch.object(self.parser, '_execute_with_retry', return_value=True):
            success = self.parser.execute_quest_logic(
                "test_quest",
                logic_blocks,
                self.test_context
            )
            
            assert success
            execution_state = self.parser.get_execution_state("test_quest")
            assert execution_state.state == QuestState.COMPLETED
            assert len(execution_state.completed_steps) == 4
    
    def test_execute_quest_logic_failure(self):
        """Test quest execution failure."""
        logic_blocks = self.parser.parse_quest_template(self.sample_quest_data)
        
        with patch.object(self.parser, '_execute_with_retry', return_value=False):
            success = self.parser.execute_quest_logic(
                "test_quest",
                logic_blocks,
                self.test_context
            )
            
            assert not success
            execution_state = self.parser.get_execution_state("test_quest")
            assert execution_state.state == QuestState.FAILED
            assert len(execution_state.failed_steps) == 1
    
    def test_execute_with_retry_success(self):
        """Test retry logic with success."""
        template = MagicMock()
        template.execute.return_value = True
        template.check_success.return_value = True
        
        block = QuestLogicBlock(
            block_id="test_block",
            logic_type=QuestLogicType.WAIT_FOR_TRIGGER,
            parameters={},
            retry_count=2
        )
        
        success = self.parser._execute_with_retry(template, {}, block)
        assert success
        assert template.execute.call_count == 1
    
    def test_execute_with_retry_failure(self):
        """Test retry logic with failure."""
        template = MagicMock()
        template.execute.return_value = False
        template.check_success.return_value = False
        
        block = QuestLogicBlock(
            block_id="test_block",
            logic_type=QuestLogicType.WAIT_FOR_TRIGGER,
            parameters={},
            retry_count=2
        )
        
        success = self.parser._execute_with_retry(template, {}, block)
        assert not success
        assert template.execute.call_count == 3  # Initial + 2 retries
    
    def test_execute_fallback_blocks(self):
        """Test fallback block execution."""
        fallback_blocks = ["fallback_1", "fallback_2"]
        
        success = self.parser._execute_fallback_blocks(fallback_blocks, {})
        assert success
    
    def test_get_execution_state(self):
        """Test getting execution state."""
        # Create a test execution state
        execution_state = QuestExecutionState(quest_id="test_quest")
        self.parser.execution_states["test_quest"] = execution_state
        
        retrieved_state = self.parser.get_execution_state("test_quest")
        assert retrieved_state == execution_state
        
        # Test non-existent quest
        assert self.parser.get_execution_state("non_existent") is None
    
    def test_clear_execution_state(self):
        """Test clearing execution state."""
        execution_state = QuestExecutionState(quest_id="test_quest")
        self.parser.execution_states["test_quest"] = execution_state
        
        self.parser.clear_execution_state("test_quest")
        assert "test_quest" not in self.parser.execution_states


class TestWaitForTrigger:
    """Test the WaitForTrigger logic template."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parameters = {
            "trigger_type": "npc_interaction",
            "conditions": {
                "npc_present": "test_npc",
                "dialogue_completed": True
            },
            "timeout_seconds": 300,
            "retry_count": 3
        }
        self.template = WaitForTrigger("test_trigger", self.parameters)
        self.context = {
            "nearby_npcs": {"test_npc": True},
            "dialogue_completed": True
        }
    
    def test_initialization(self):
        """Test template initialization."""
        assert self.template.block_id == "test_trigger"
        assert self.template.trigger_type == QuestTriggerType.NPC_INTERACTION
        assert self.template.timeout == 300
        assert self.template.max_retries == 3
    
    def test_check_success(self):
        """Test success condition checking."""
        success = self.template.check_success(self.context)
        assert success
    
    def test_check_success_failure(self):
        """Test success condition failure."""
        context = {"nearby_npcs": {"test_npc": False}}
        success = self.template.check_success(context)
        assert not success
    
    def test_evaluate_condition_npc_present(self):
        """Test NPC present condition evaluation."""
        result = self.template._check_npc_present("test_npc", self.context)
        assert result
        
        result = self.template._check_npc_present("other_npc", self.context)
        assert not result
    
    def test_evaluate_condition_item_in_inventory(self):
        """Test item in inventory condition evaluation."""
        context = {"inventory": {"test_item": 1}}
        result = self.template._check_item_in_inventory("test_item", context)
        assert result
        
        result = self.template._check_item_in_inventory("missing_item", context)
        assert not result
    
    def test_evaluate_condition_combat_targets_eliminated(self):
        """Test combat targets eliminated condition evaluation."""
        context = {"combat_targets_eliminated": 5}
        result = self.template._check_combat_targets_eliminated(3, context)
        assert result
        
        result = self.template._check_combat_targets_eliminated(10, context)
        assert not result
    
    def test_evaluate_condition_location_reached(self):
        """Test location reached condition evaluation."""
        location = {"coordinates": [100, 200], "radius": 50}
        context = {"current_location": [120, 220]}
        result = self.template._check_location_reached(location, context)
        assert result
        
        context = {"current_location": [200, 300]}
        result = self.template._check_location_reached(location, context)
        assert not result
    
    def test_is_timeout(self):
        """Test timeout checking."""
        assert not self.template._is_timeout()
        
        self.template.start_time = datetime.now() - timedelta(seconds=400)
        assert self.template._is_timeout()
    
    @patch('time.sleep')
    def test_execute_success(self, mock_sleep):
        """Test successful execution."""
        with patch.object(self.template, '_check_trigger_conditions', return_value=True):
            success = self.template.execute(self.context)
            assert success
    
    @patch('time.sleep')
    def test_execute_timeout(self, mock_sleep):
        """Test execution timeout."""
        self.template.timeout = 1
        with patch.object(self.template, '_check_trigger_conditions', return_value=False):
            success = self.template.execute(self.context)
            assert not success


class TestTravelToZone:
    """Test the TravelToZone logic template."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parameters = {
            "destination": {
                "coordinates": [100, 200],
                "zone": "test_zone",
                "planet": "tatooine",
                "radius": 50
            },
            "travel_method": "walk",
            "route_optimization": True
        }
        self.template = TravelToZone("test_travel", self.parameters)
        self.context = {"current_location": [0, 0]}
    
    def test_initialization(self):
        """Test template initialization."""
        assert self.template.block_id == "test_travel"
        assert self.template.destination["coordinates"] == [100, 200]
        assert self.template.travel_method == "walk"
    
    def test_check_success(self):
        """Test success condition checking."""
        context = {"current_location": [120, 220]}
        success = self.template.check_success(context)
        assert success
    
    def test_check_success_failure(self):
        """Test success condition failure."""
        context = {"current_location": [200, 300]}
        success = self.template.check_success(context)
        assert not success
    
    def test_calculate_travel_time(self):
        """Test travel time calculation."""
        time = self.template._calculate_travel_time()
        assert time == 2.0  # Base time for walk
        
        self.template.travel_method = "shuttle"
        time = self.template._calculate_travel_time()
        assert time == 1.0  # 50% of base time
        
        self.template.travel_method = "mount"
        time = self.template._calculate_travel_time()
        assert time == 1.6  # 80% of base time
    
    @patch('time.sleep')
    def test_execute_success(self, mock_sleep):
        """Test successful execution."""
        success = self.template.execute(self.context)
        assert success
        assert self.context["current_location"] == [100, 200]
        assert self.context["current_zone"] == "test_zone"
        assert self.context["current_planet"] == "tatooine"
    
    @patch('time.sleep')
    def test_execute_failure(self, mock_sleep):
        """Test execution failure."""
        mock_sleep.side_effect = Exception("Travel error")
        success = self.template.execute(self.context)
        assert not success


class TestUseItem:
    """Test the UseItem logic template."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parameters = {
            "item_name": "test_key",
            "use_target": "test_door",
            "use_conditions": {"player_level": 10},
            "use_effect": {
                "type": "unlock_door",
                "door_id": "test_door",
                "consume_item": False
            }
        }
        self.template = UseItem("test_use_item", self.parameters)
        self.context = {
            "inventory": {"test_key": 1},
            "player_health": 100
        }
    
    def test_initialization(self):
        """Test template initialization."""
        assert self.template.block_id == "test_use_item"
        assert self.template.item_name == "test_key"
        assert self.template.use_target == "test_door"
    
    def test_check_success(self):
        """Test success condition checking."""
        success = self.template.check_success(self.context)
        assert success
    
    def test_check_item_available(self):
        """Test item availability checking."""
        result = self.template._check_item_available(self.context)
        assert result
        
        context = {"inventory": {"test_key": 0}}
        result = self.template._check_item_available(context)
        assert not result
    
    @patch('time.sleep')
    def test_execute_success(self, mock_sleep):
        """Test successful execution."""
        success = self.template.execute(self.context)
        assert success
        assert "test_door" in self.context.get("unlocked_doors", [])
    
    @patch('time.sleep')
    def test_execute_item_not_available(self, mock_sleep):
        """Test execution with unavailable item."""
        context = {"inventory": {"test_key": 0}}
        success = self.template.execute(context)
        assert not success
    
    def test_apply_use_effect_unlock_door(self):
        """Test unlock door effect."""
        self.template._apply_use_effect(self.context)
        assert "test_door" in self.context.get("unlocked_doors", [])
    
    def test_apply_use_effect_activate_device(self):
        """Test activate device effect."""
        self.template.use_effect = {
            "type": "activate_device",
            "device_id": "test_device"
        }
        self.template._apply_use_effect(self.context)
        assert "test_device" in self.context.get("activated_devices", [])
    
    def test_apply_use_effect_heal_player(self):
        """Test heal player effect."""
        self.template.use_effect = {
            "type": "heal_player",
            "heal_amount": 25
        }
        self.context["player_health"] = 50
        self.template._apply_use_effect(self.context)
        assert self.context["player_health"] == 75
    
    def test_check_use_effect(self):
        """Test use effect checking."""
        self.context["unlocked_doors"] = ["test_door"]
        result = self.template._check_use_effect(self.context)
        assert result
        
        self.context["unlocked_doors"] = []
        result = self.template._check_use_effect(self.context)
        assert not result


class TestEscortDefend:
    """Test the EscortDefend logic template."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parameters = {
            "mission_type": "escort",
            "target_info": {
                "name": "Test Target",
                "health": 100
            },
            "protection_requirements": {
                "defense_duration": 180,
                "min_target_health": 50
            },
            "route_points": [[150, 250], [200, 300]],
            "threat_level": "medium"
        }
        self.template = EscortDefend("test_escort", self.parameters)
        self.context = {
            "target_health": 100,
            "target_location": [0, 0]
        }
    
    def test_initialization(self):
        """Test template initialization."""
        assert self.template.block_id == "test_escort"
        assert self.template.mission_type == "escort"
        assert self.template.target_info["name"] == "Test Target"
    
    def test_check_success_escort(self):
        """Test escort success condition."""
        success = self.template._check_escort_success(self.context)
        assert success
        
        self.context["target_health"] = 0
        success = self.template._check_escort_success(self.context)
        assert not success
    
    def test_check_success_defend(self):
        """Test defend success condition."""
        success = self.template._check_defend_success(self.context)
        assert success
        
        self.context["target_health"] = 0
        success = self.template._check_defend_success(self.context)
        assert not success
    
    def test_check_threats(self):
        """Test threat checking."""
        # Test multiple times to ensure randomness works
        threats_detected = 0
        for _ in range(100):
            if self.template._check_threats(self.context):
                threats_detected += 1
        
        # Should have some threats detected (medium level = 30% chance)
        assert 10 <= threats_detected <= 50
    
    def test_handle_threat(self):
        """Test threat handling."""
        # Test multiple times to ensure randomness works
        successes = 0
        for _ in range(100):
            if self.template._handle_threat(self.context):
                successes += 1
        
        # Should have some successes (70% success rate)
        assert 50 <= successes <= 90
    
    @patch('time.sleep')
    def test_execute_escort_success(self, mock_sleep):
        """Test successful escort execution."""
        success = self.template.execute(self.context)
        assert success
    
    @patch('time.sleep')
    def test_execute_defend_success(self, mock_sleep):
        """Test successful defend execution."""
        self.template.mission_type = "defend"
        success = self.template.execute(self.context)
        assert success


class TestQuestLogicParserIntegration:
    """Integration tests for the Quest Logic Parser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = QuestLogicParser()
        self.sample_quest = {
            "quest_id": "integration_test",
            "steps": [
                {
                    "step_id": "wait_for_npc",
                    "type": "dialogue",
                    "npc_id": "test_npc",
                    "timeout_seconds": 10,
                    "retry_count": 1
                },
                {
                    "step_id": "travel_to_location",
                    "type": "move",
                    "data": {
                        "coords": [100, 200],
                        "planet": "tatooine"
                    },
                    "timeout_seconds": 10,
                    "retry_count": 1
                },
                {
                    "step_id": "use_item",
                    "type": "use_item",
                    "item_name": "test_key",
                    "use_effect": {
                        "type": "unlock_door",
                        "door_id": "test_door"
                    },
                    "timeout_seconds": 10,
                    "retry_count": 1
                }
            ]
        }
        self.context = {
            "current_location": [0, 0],
            "inventory": {"test_key": 1},
            "nearby_npcs": {"test_npc": True}
        }
    
    def test_full_quest_execution(self):
        """Test complete quest execution flow."""
        logic_blocks = self.parser.parse_quest_template(self.sample_quest)
        
        with patch.object(self.parser, '_execute_with_retry', return_value=True):
            success = self.parser.execute_quest_logic(
                "integration_test",
                logic_blocks,
                self.context
            )
            
            assert success
            execution_state = self.parser.get_execution_state("integration_test")
            assert execution_state.state == QuestState.COMPLETED
            assert len(execution_state.completed_steps) == 3
    
    def test_parse_and_execute_quest_function(self):
        """Test the convenience function."""
        with patch.object(self.parser, 'execute_quest_logic', return_value=True):
            success = parse_and_execute_quest(self.sample_quest, self.context)
            assert success


class TestQuestLogicParserPerformance:
    """Performance tests for the Quest Logic Parser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = QuestLogicParser()
        self.large_quest = {
            "quest_id": "performance_test",
            "steps": [
                {
                    "step_id": f"step_{i}",
                    "type": "dialogue" if i % 2 == 0 else "move",
                    "npc_id": f"npc_{i}",
                    "data": {
                        "coords": [i * 10, i * 20],
                        "planet": "tatooine"
                    },
                    "timeout_seconds": 10,
                    "retry_count": 1
                }
                for i in range(100)  # Large quest with 100 steps
            ]
        }
        self.context = {
            "current_location": [0, 0],
            "inventory": {},
            "nearby_npcs": {}
        }
    
    def test_large_quest_parsing_performance(self):
        """Test performance of parsing large quests."""
        start_time = time.time()
        logic_blocks = self.parser.parse_quest_template(self.large_quest)
        parse_time = time.time() - start_time
        
        assert len(logic_blocks) == 100
        assert parse_time < 1.0  # Should parse quickly
    
    def test_large_quest_execution_performance(self):
        """Test performance of executing large quests."""
        logic_blocks = self.parser.parse_quest_template(self.large_quest)
        
        with patch.object(self.parser, '_execute_with_retry', return_value=True):
            start_time = time.time()
            success = self.parser.execute_quest_logic(
                "performance_test",
                logic_blocks,
                self.context
            )
            execution_time = time.time() - start_time
            
            assert success
            assert execution_time < 5.0  # Should execute reasonably quickly


class TestQuestLogicParserErrorHandling:
    """Error handling tests for the Quest Logic Parser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = QuestLogicParser()
        self.malformed_quest = {
            "quest_id": "error_test",
            "steps": [
                {
                    "step_id": "invalid_step",
                    "type": "unknown_type",
                    "data": {}
                }
            ]
        }
        self.context = {}
    
    def test_unknown_step_type(self):
        """Test handling of unknown step types."""
        logic_blocks = self.parser.parse_quest_template(self.malformed_quest)
        assert len(logic_blocks) == 0  # Should skip unknown types
    
    def test_missing_required_parameters(self):
        """Test handling of missing parameters."""
        quest_data = {
            "quest_id": "missing_params",
            "steps": [
                {
                    "step_id": "incomplete_step",
                    "type": "dialogue"
                    # Missing required parameters
                }
            ]
        }
        
        logic_blocks = self.parser.parse_quest_template(quest_data)
        # Should still create blocks with defaults
        assert len(logic_blocks) == 1
    
    def test_execution_with_exceptions(self):
        """Test execution with exceptions."""
        logic_blocks = self.parser.parse_quest_template(self.malformed_quest)
        
        with patch.object(self.parser, '_execute_with_retry', side_effect=Exception("Test error")):
            success = self.parser.execute_quest_logic(
                "error_test",
                logic_blocks,
                self.context
            )
            assert not success


if __name__ == "__main__":
    pytest.main([__file__]) 
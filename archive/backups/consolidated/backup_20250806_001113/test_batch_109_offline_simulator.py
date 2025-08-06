#!/usr/bin/env python3
"""
Comprehensive test suite for Batch 109 - Offline Mode Simulator

This module provides thorough testing of the offline simulator's capabilities
including quest step testing, travel path testing, combat loop simulation,
decision tree generation, and report export functionality.

Author: SWG Bot Development Team
"""

import pytest
import tempfile
import shutil
import os
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.simulator import (
    OfflineSimulator, SimulationMode, QuestType, TravelMethod, 
    CombatAction, ActionResult, MockWorldState, CharacterConfig,
    SimulationStep, SimulationResult, DecisionNode
)
from datetime import datetime

class TestOfflineSimulator:
    """Test cases for the OfflineSimulator class."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_dir = tempfile.mkdtemp()
        config_dir = os.path.join(temp_dir, "config")
        logs_dir = os.path.join(temp_dir, "logs")
        
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)
        
        yield {
            "temp_dir": temp_dir,
            "config_dir": config_dir,
            "logs_dir": logs_dir
        }
        
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def simulator(self, temp_dirs):
        """Create a simulator instance for testing."""
        return OfflineSimulator(
            config_dir=temp_dirs["config_dir"],
            logs_dir=temp_dirs["logs_dir"],
            max_simulation_time=60
        )
    
    @pytest.fixture
    def sample_character(self):
        """Create a sample character for testing."""
        return CharacterConfig(
            name="TestCharacter",
            profession="Brawler",
            level=10,
            health=100,
            max_health=100,
            action_points=100,
            max_action_points=100,
            credits=5000,
            experience=10000,
            skills={"combat": 100, "healing": 50},
            equipment={"weapon": {"name": "Vibro Knuckler", "damage": 25}},
            location="Mos Eisley",
            inventory={"Stimpack": 5}
        )
    
    @pytest.fixture
    def sample_world_state(self):
        """Create a sample world state for testing."""
        return MockWorldState(
            current_location="Mos Eisley",
            available_locations=["Mos Eisley", "Anchorhead", "Bestine"],
            npc_spawns={"Mos Eisley": ["Stormtrooper", "Jawa"]},
            resource_nodes={"Mos Eisley": ["Water", "Ore"]},
            weather_conditions={"Mos Eisley": "Clear"},
            time_of_day="Day",
            server_population=50,
            faction_control={"Mos Eisley": "Imperial"}
        )
    
    def test_initialization(self, simulator):
        """Test simulator initialization."""
        assert simulator.config_dir.exists()
        assert simulator.logs_dir.exists()
        assert simulator.max_simulation_time == 60
        assert hasattr(simulator, 'configs')
        assert simulator.current_simulation is None
        assert simulator.decision_tree == []
    
    def test_create_mock_world_state(self, simulator):
        """Test mock world state creation."""
        world_state = simulator.create_mock_world_state(
            location="TestLocation",
            population=100
        )
        
        assert isinstance(world_state, MockWorldState)
        assert world_state.current_location == "TestLocation"
        assert world_state.server_population == 100
        assert len(world_state.available_locations) > 0
        assert len(world_state.npc_spawns) > 0
        assert len(world_state.resource_nodes) > 0
    
    def test_create_character_config(self, simulator):
        """Test character configuration creation."""
        character = simulator.create_character_config(
            name="TestChar",
            profession="Scout",
            level=15
        )
        
        assert isinstance(character, CharacterConfig)
        assert character.name == "TestChar"
        assert character.profession == "Scout"
        assert character.level == 15
        assert character.health == 100
        assert character.max_health == 100
        assert character.experience == 15000  # level * 1000
        assert "combat" in character.skills
        assert "weapon" in character.equipment
    
    def test_simulate_quest_step_kill(self, simulator, sample_character, sample_world_state):
        """Test kill quest simulation."""
        quest_params = {
            "target_count": 3,
            "target_type": "Stormtrooper",
            "time_limit": 1800,
            "reward_xp": 500,
            "reward_credits": 1000
        }
        
        result = simulator.simulate_quest_step(
            quest_type=QuestType.KILL,
            character=sample_character,
            world_state=sample_world_state,
            quest_params=quest_params
        )
        
        assert isinstance(result, SimulationResult)
        assert result.mode == SimulationMode.QUEST_STEP
        assert result.simulation_id.startswith("quest_")
        assert result.total_duration > 0
        assert 0 <= result.success_rate <= 1
        assert result.xp_gained == 500
        assert result.credits_earned == 1000
        assert len(result.steps) > 0
        
        # Check that steps are properly ordered
        for i, step in enumerate(result.steps):
            assert step.step_id == i + 1
    
    def test_simulate_quest_step_collect(self, simulator, sample_character, sample_world_state):
        """Test collection quest simulation."""
        quest_params = {
            "item_name": "Ore",
            "required_count": 2,
            "time_limit": 1200,
            "reward_xp": 300,
            "reward_credits": 750
        }
        
        result = simulator.simulate_quest_step(
            quest_type=QuestType.COLLECT,
            character=sample_character,
            world_state=sample_world_state,
            quest_params=quest_params
        )
        
        assert isinstance(result, SimulationResult)
        assert result.mode == SimulationMode.QUEST_STEP
        assert result.simulation_id.startswith("quest_")
        assert result.total_duration > 0
        assert 0 <= result.success_rate <= 1
        assert result.xp_gained == 300
        assert result.credits_earned == 750
    
    def test_simulate_travel_path(self, simulator, sample_character, sample_world_state):
        """Test travel path simulation."""
        result = simulator.simulate_travel_path(
            character=sample_character,
            world_state=sample_world_state,
            destination="Anchorhead",
            travel_method=TravelMethod.WALK
        )
        
        assert isinstance(result, SimulationResult)
        assert result.mode == SimulationMode.TRAVEL_PATH
        assert result.simulation_id.startswith("travel_")
        assert result.total_duration > 0
        assert 0 <= result.success_rate <= 1
        assert result.xp_gained == 0  # Travel doesn't give XP
        assert result.credits_earned == 0  # Travel doesn't give credits
        
        # Check that character location was updated
        assert sample_character.location == "Anchorhead"
    
    def test_simulate_combat_loop(self, simulator, sample_character):
        """Test combat loop simulation."""
        result = simulator.simulate_combat_loop(
            character=sample_character,
            enemy_count=2,
            enemy_level=8,
            difficulty="normal"
        )
        
        assert isinstance(result, SimulationResult)
        assert result.mode == SimulationMode.COMBAT_LOOP
        assert result.simulation_id.startswith("combat_")
        assert result.total_duration > 0
        assert 0 <= result.success_rate <= 1
        assert result.xp_gained > 0
        assert result.credits_earned > 0
    
    def test_generate_decision_tree(self, simulator, sample_character):
        """Test decision tree generation."""
        # Create a simulation result first
        combat_result = simulator.simulate_combat_loop(
            character=sample_character,
            enemy_count=1,
            enemy_level=5,
            difficulty="normal"
        )
        
        decision_tree = simulator.generate_decision_tree(combat_result)
        
        assert isinstance(decision_tree, list)
        assert all(isinstance(node, DecisionNode) for node in decision_tree)
        
        # Check that decision nodes have required attributes
        for node in decision_tree:
            assert hasattr(node, 'node_id')
            assert hasattr(node, 'decision_type')
            assert hasattr(node, 'options')
            assert hasattr(node, 'chosen_option')
            assert hasattr(node, 'reasoning')
            assert hasattr(node, 'confidence')
            assert hasattr(node, 'timestamp')
    
    def test_export_simulation_report(self, simulator, sample_character, sample_world_state):
        """Test simulation report export."""
        # Create a simulation result
        quest_result = simulator.simulate_quest_step(
            quest_type=QuestType.KILL,
            character=sample_character,
            world_state=sample_world_state,
            quest_params={
                "target_count": 1,
                "target_type": "NPC",
                "time_limit": 300,
                "reward_xp": 100,
                "reward_credits": 200
            }
        )
        
        # Export report
        report_file = simulator.export_simulation_report(quest_result)
        
        assert os.path.exists(report_file)
        
        # Load and validate report
        with open(report_file, 'r') as f:
            report_data = json.load(f)
        
        assert 'simulation_summary' in report_data
        assert 'decision_tree' in report_data
        assert 'performance_metrics' in report_data
        assert 'recommendations' in report_data
        assert 'export_timestamp' in report_data
        
        # Validate simulation summary
        summary = report_data['simulation_summary']
        assert summary['simulation_id'] == quest_result.simulation_id
        assert summary['mode'] == quest_result.mode.value
        
        # Validate performance metrics
        metrics = report_data['performance_metrics']
        assert 'total_steps' in metrics
        assert 'success_rate' in metrics
        assert 'total_duration' in metrics
    
    def test_calculate_success_rate(self, simulator):
        """Test success rate calculation."""
        # Test with all successful steps
        successful_steps = [
            SimulationStep(1, "test", {}, ActionResult.SUCCESS, 1.0, {}, datetime.now()),
            SimulationStep(2, "test", {}, ActionResult.SUCCESS, 1.0, {}, datetime.now())
        ]
        assert simulator._calculate_success_rate(successful_steps) == 1.0
        
        # Test with mixed results
        mixed_steps = [
            SimulationStep(1, "test", {}, ActionResult.SUCCESS, 1.0, {}, datetime.now()),
            SimulationStep(2, "test", {}, ActionResult.FAILURE, 1.0, {}, datetime.now()),
            SimulationStep(3, "test", {}, ActionResult.SUCCESS, 1.0, {}, datetime.now())
        ]
        assert simulator._calculate_success_rate(mixed_steps) == 2/3
        
        # Test with empty list
        assert simulator._calculate_success_rate([]) == 0.0
    
    def test_find_kill_target(self, simulator, sample_world_state):
        """Test kill target finding."""
        quest_params = {"target_type": "NPC"}
        target = simulator._find_kill_target(sample_world_state, quest_params)
        
        assert isinstance(target, str)
        assert target in sample_world_state.available_locations or target == "Mos Eisley"
    
    def test_find_collection_locations(self, simulator, sample_world_state):
        """Test collection location finding."""
        locations = simulator._find_collection_locations(sample_world_state, "Ore")
        
        assert isinstance(locations, list)
        assert len(locations) > 0
    
    def test_create_enemy(self, simulator):
        """Test enemy creation."""
        enemy = simulator._create_enemy(level=10, difficulty="normal")
        
        assert isinstance(enemy, dict)
        assert 'level' in enemy
        assert 'health' in enemy
        assert 'max_health' in enemy
        assert 'damage' in enemy
        assert 'difficulty' in enemy
        assert enemy['level'] == 10
        assert enemy['difficulty'] == "normal"
    
    def test_decide_combat_action(self, simulator, sample_character):
        """Test combat action decision."""
        enemy = simulator._create_enemy(level=5, difficulty="normal")
        
        # Test low health scenario
        sample_character.health = 20  # Low health
        action = simulator._decide_combat_action(sample_character, enemy, 1)
        assert action == CombatAction.HEAL
        
        # Test normal scenario
        sample_character.health = 80  # Normal health
        action = simulator._decide_combat_action(sample_character, enemy, 1)
        assert action == CombatAction.ATTACK
    
    def test_get_available_options(self, simulator):
        """Test available options retrieval."""
        combat_options = simulator._get_available_options("combat_action")
        assert all(action in combat_options for action in ["attack", "defend", "heal", "flee", "buff", "debuff"])
        
        travel_options = simulator._get_available_options("travel")
        assert all(method in travel_options for method in ["walk", "run", "mount", "vehicle"])
    
    def test_generate_reasoning(self, simulator):
        """Test reasoning generation."""
        step = SimulationStep(1, "combat_action", {"action": "attack"}, ActionResult.SUCCESS, 1.0, {}, simulator._get_current_time())
        reasoning = simulator._generate_reasoning(step)
        
        assert isinstance(reasoning, str)
        assert len(reasoning) > 0
    
    def test_generate_recommendations(self, simulator):
        """Test recommendation generation."""
        # Create a simulation result with low success rate
        character = simulator.create_character_config()
        world_state = simulator.create_mock_world_state()
        
        # Mock a result with poor performance
        result = SimulationResult(
            simulation_id="test",
            mode=SimulationMode.QUEST_STEP,
            character_config=character,
            world_state=world_state,
            steps=[],
            total_duration=400,  # Long duration
            success_rate=0.5,  # Low success rate
            xp_gained=50,
            credits_earned=100,
            items_collected={},
            decisions_made=0,
            errors_encountered=2
        )
        
        recommendations = simulator._generate_recommendations(result)
        
        assert isinstance(recommendations, dict)
        assert 'performance' in recommendations
        assert 'strategy' in recommendations
        assert 'optimization' in recommendations
        
        # Should have recommendations for poor performance
        assert len(recommendations['performance']) > 0
    
    def test_configuration_loading(self, simulator, temp_dirs):
        """Test configuration loading and saving."""
        # Test that default configs are created
        assert 'quest_templates' in simulator.configs
        assert 'travel_templates' in simulator.configs
        assert 'combat_templates' in simulator.configs
        
        # Test saving configurations
        simulator.save_configurations()
        config_file = Path(temp_dirs["config_dir"]) / "simulation_configs.json"
        assert config_file.exists()
        
        # Test loading configurations
        with open(config_file, 'r') as f:
            loaded_configs = json.load(f)
        
        assert loaded_configs == simulator.configs

class TestSimulationModes:
    """Test different simulation modes."""
    
    @pytest.fixture
    def simulator(self):
        """Create simulator instance."""
        return OfflineSimulator()
    
    def test_quest_step_modes(self, simulator):
        """Test different quest step types."""
        character = simulator.create_character_config()
        world_state = simulator.create_mock_world_state()
        
        # Test kill quest
        kill_result = simulator.simulate_quest_step(
            QuestType.KILL,
            character,
            world_state,
            {"target_count": 1, "reward_xp": 100}
        )
        assert kill_result.mode == SimulationMode.QUEST_STEP
        
        # Test collect quest
        collect_result = simulator.simulate_quest_step(
            QuestType.COLLECT,
            character,
            world_state,
            {"item_name": "Ore", "required_count": 1, "reward_xp": 100}
        )
        assert collect_result.mode == SimulationMode.QUEST_STEP
    
    def test_travel_methods(self, simulator):
        """Test different travel methods."""
        character = simulator.create_character_config()
        world_state = simulator.create_mock_world_state()
        
        for method in [TravelMethod.WALK, TravelMethod.RUN, TravelMethod.MOUNT]:
            result = simulator.simulate_travel_path(
                character,
                world_state,
                "Anchorhead",
                method
            )
            assert result.mode == SimulationMode.TRAVEL_PATH
    
    def test_combat_difficulties(self, simulator):
        """Test different combat difficulties."""
        character = simulator.create_character_config()
        
        for difficulty in ["easy", "normal", "hard"]:
            result = simulator.simulate_combat_loop(
                character,
                enemy_count=1,
                enemy_level=5,
                difficulty=difficulty
            )
            assert result.mode == SimulationMode.COMBAT_LOOP

class TestDataStructures:
    """Test data structure classes."""
    
    def test_mock_world_state(self):
        """Test MockWorldState dataclass."""
        world_state = MockWorldState(
            current_location="Test",
            available_locations=["Test"],
            npc_spawns={},
            resource_nodes={},
            weather_conditions={},
            time_of_day="Day",
            server_population=50,
            faction_control={}
        )
        
        data = world_state.to_dict()
        assert isinstance(data, dict)
        assert data['current_location'] == "Test"
        assert data['server_population'] == 50
    
    def test_character_config(self):
        """Test CharacterConfig dataclass."""
        character = CharacterConfig(
            name="Test",
            profession="Brawler",
            level=10,
            health=100,
            max_health=100,
            action_points=100,
            max_action_points=100,
            credits=5000,
            experience=10000,
            skills={},
            equipment={},
            location="Test",
            inventory={}
        )
        
        data = character.to_dict()
        assert isinstance(data, dict)
        assert data['name'] == "Test"
        assert data['level'] == 10
    
    def test_simulation_step(self):
        """Test SimulationStep dataclass."""
        step = SimulationStep(
            step_id=1,
            action="test",
            parameters={},
            result=ActionResult.SUCCESS,
            duration=1.0,
            details={},
            timestamp=datetime.now()
        )
        
        data = step.to_dict()
        assert isinstance(data, dict)
        assert data['step_id'] == 1
        assert data['action'] == "test"
        assert data['result'] == ActionResult.SUCCESS.value
    
    def test_simulation_result(self):
        """Test SimulationResult dataclass."""
        character = CharacterConfig(
            name="Test", profession="Brawler", level=10,
            health=100, max_health=100, action_points=100,
            max_action_points=100, credits=5000, experience=10000,
            skills={}, equipment={}, location="Test", inventory={}
        )
        
        world_state = MockWorldState(
            current_location="Test", available_locations=[],
            npc_spawns={}, resource_nodes={}, weather_conditions={},
            time_of_day="Day", server_population=50, faction_control={}
        )
        
        result = SimulationResult(
            simulation_id="test",
            mode=SimulationMode.QUEST_STEP,
            character_config=character,
            world_state=world_state,
            steps=[],
            total_duration=60.0,
            success_rate=1.0,
            xp_gained=100,
            credits_earned=200,
            items_collected={},
            decisions_made=0,
            errors_encountered=0
        )
        
        data = result.to_dict()
        assert isinstance(data, dict)
        assert data['simulation_id'] == "test"
        assert data['mode'] == SimulationMode.QUEST_STEP.value
        assert 'character_config' in data
        assert 'world_state' in data
    
    def test_decision_node(self):
        """Test DecisionNode dataclass."""
        node = DecisionNode(
            node_id="test_node",
            decision_type="combat_action",
            options=["attack", "defend"],
            chosen_option="attack",
            reasoning="Test reasoning",
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        data = node.to_dict()
        assert isinstance(data, dict)
        assert data['node_id'] == "test_node"
        assert data['decision_type'] == "combat_action"
        assert data['chosen_option'] == "attack"
        assert data['confidence'] == 0.8

class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.fixture
    def complete_setup(self):
        """Set up complete test environment."""
        temp_dir = tempfile.mkdtemp()
        config_dir = os.path.join(temp_dir, "config")
        logs_dir = os.path.join(temp_dir, "logs")
        
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)
        
        simulator = OfflineSimulator(
            config_dir=config_dir,
            logs_dir=logs_dir
        )
        
        yield {
            "simulator": simulator,
            "temp_dir": temp_dir,
            "config_dir": config_dir,
            "logs_dir": logs_dir
        }
        
        shutil.rmtree(temp_dir)
    
    def test_complete_quest_workflow(self, complete_setup):
        """Test complete quest workflow from start to finish."""
        simulator = complete_setup["simulator"]
        
        # Create character and world state
        character = simulator.create_character_config()
        world_state = simulator.create_mock_world_state()
        
        # Run quest simulation
        result = simulator.simulate_quest_step(
            QuestType.KILL,
            character,
            world_state,
            {"target_count": 2, "reward_xp": 200, "reward_credits": 400}
        )
        
        # Generate decision tree
        decision_tree = simulator.generate_decision_tree(result)
        
        # Export report
        report_file = simulator.export_simulation_report(result)
        
        # Validate complete workflow
        assert isinstance(result, SimulationResult)
        assert len(decision_tree) > 0
        assert os.path.exists(report_file)
        
        # Load and validate report
        with open(report_file, 'r') as f:
            report_data = json.load(f)
        
        assert 'simulation_summary' in report_data
        assert 'decision_tree' in report_data
        assert 'performance_metrics' in report_data
    
    def test_complete_combat_workflow(self, complete_setup):
        """Test complete combat workflow."""
        simulator = complete_setup["simulator"]
        
        # Create character
        character = simulator.create_character_config()
        
        # Run combat simulation
        result = simulator.simulate_combat_loop(
            character,
            enemy_count=3,
            enemy_level=8,
            difficulty="normal"
        )
        
        # Generate decision tree
        decision_tree = simulator.generate_decision_tree(result)
        
        # Export report
        report_file = simulator.export_simulation_report(result)
        
        # Validate results
        assert isinstance(result, SimulationResult)
        assert result.mode == SimulationMode.COMBAT_LOOP
        assert len(decision_tree) > 0
        assert os.path.exists(report_file)
        assert result.xp_gained > 0
        assert result.credits_earned > 0
    
    def test_performance_benchmarking(self, complete_setup):
        """Test performance benchmarking across different configurations."""
        simulator = complete_setup["simulator"]
        
        results = []
        
        # Test different character levels
        for level in [5, 15, 25]:
            character = simulator.create_character_config(level=level)
            world_state = simulator.create_mock_world_state()
            
            result = simulator.simulate_quest_step(
                QuestType.KILL,
                character,
                world_state,
                {"target_count": 1, "reward_xp": 100, "reward_credits": 200}
            )
            
            results.append({
                "level": level,
                "duration": result.total_duration,
                "success_rate": result.success_rate,
                "xp_gained": result.xp_gained
            })
        
        # Validate that we got results for all levels
        assert len(results) == 3
        assert all('level' in r for r in results)
        assert all('duration' in r for r in results)
        assert all('success_rate' in r for r in results)

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.fixture
    def simulator(self):
        """Create simulator instance."""
        return OfflineSimulator()
    
    def test_invalid_character_level(self, simulator):
        """Test handling of invalid character level."""
        # Should handle negative level gracefully
        character = simulator.create_character_config(level=-5)
        assert character.level == -5  # Should still create the character
    
    def test_empty_world_state(self, simulator):
        """Test handling of minimal world state."""
        world_state = simulator.create_mock_world_state(
            location="Test",
            population=0
        )
        assert world_state.server_population == 0
    
    def test_simulation_timeout(self, simulator):
        """Test simulation timeout handling."""
        character = simulator.create_character_config(level=50)  # High level
        world_state = simulator.create_mock_world_state()
        
        # Should complete within reasonable time
        result = simulator.simulate_quest_step(
            QuestType.KILL,
            character,
            world_state,
            {"target_count": 1, "reward_xp": 100, "reward_credits": 200}
        )
        
        assert result.total_duration < simulator.max_simulation_time
    
    def test_missing_parameters(self, simulator):
        """Test handling of missing parameters."""
        character = simulator.create_character_config()
        world_state = simulator.create_mock_world_state()
        
        # Test with minimal quest parameters
        result = simulator.simulate_quest_step(
            QuestType.KILL,
            character,
            world_state,
            {}  # Empty parameters
        )
        
        assert isinstance(result, SimulationResult)
        assert result.total_duration > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
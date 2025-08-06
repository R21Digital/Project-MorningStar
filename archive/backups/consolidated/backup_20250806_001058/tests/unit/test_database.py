"""
Unit tests for Database Access Module.

Tests the centralized database interface for loading and querying YAML/JSON game data.
"""

import json
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Import the modules to test
from core.database import (
    DatabaseAccess, QuestData, TrainerData, CollectionData,
    get_database, load_quest, load_trainers, find_trainers_for_profession,
    load_collections, load_dialogue_patterns, load_map
)


class TestQuestData:
    """Test the QuestData dataclass."""
    
    def test_quest_data_creation(self):
        """Test creating a QuestData object."""
        quest = QuestData(
            quest_id="test_quest",
            name="Test Quest",
            description="A test quest",
            quest_type="collection",
            difficulty="medium",
            level_requirement=15,
            planet="tatooine",
            zone="mos_eisley",
            coordinates=[100, 200],
            quest_chain="test_chain",
            prerequisites=["prereq1", "prereq2"],
            rewards={"experience": 500, "credits": 1000},
            steps=[{"step_id": "step1", "type": "dialogue"}],
            completion_conditions=[{"type": "items_collected", "count": 2}],
            failure_conditions=[{"type": "timeout", "timeout_seconds": 3600}],
            hints=["Hint 1", "Hint 2"],
            metadata={"version": "1.0"},
            state={"status": "available"}
        )
        
        assert quest.quest_id == "test_quest"
        assert quest.name == "Test Quest"
        assert quest.description == "A test quest"
        assert quest.quest_type == "collection"
        assert quest.difficulty == "medium"
        assert quest.level_requirement == 15
        assert quest.planet == "tatooine"
        assert quest.zone == "mos_eisley"
        assert quest.coordinates == [100, 200]
        assert quest.quest_chain == "test_chain"
        assert quest.prerequisites == ["prereq1", "prereq2"]
        assert quest.rewards == {"experience": 500, "credits": 1000}
        assert quest.steps == [{"step_id": "step1", "type": "dialogue"}]
        assert quest.completion_conditions == [{"type": "items_collected", "count": 2}]
        assert quest.failure_conditions == [{"type": "timeout", "timeout_seconds": 3600}]
        assert quest.hints == ["Hint 1", "Hint 2"]
        assert quest.metadata == {"version": "1.0"}
        assert quest.state == {"status": "available"}


class TestTrainerData:
    """Test the TrainerData dataclass."""
    
    def test_trainer_data_creation(self):
        """Test creating a TrainerData object."""
        trainer = TrainerData(
            trainer_id="test_trainer",
            name="Test Trainer",
            profession="combat",
            planet="tatooine",
            zone="mos_eisley",
            coordinates=[200, 300],
            level_requirement=5,
            reputation_requirement={"tatooine": 100},
            skills_taught=["unarmed_combat", "melee_weapons"],
            max_skill_level=4,
            training_cost={"credits": 100, "reputation": 50},
            schedule={"available_hours": [8, 9, 10], "rest_days": []},
            dialogue_options=["Learn skills", "Ask questions", "Leave"],
            metadata={"version": "1.0"}
        )
        
        assert trainer.trainer_id == "test_trainer"
        assert trainer.name == "Test Trainer"
        assert trainer.profession == "combat"
        assert trainer.planet == "tatooine"
        assert trainer.zone == "mos_eisley"
        assert trainer.coordinates == [200, 300]
        assert trainer.level_requirement == 5
        assert trainer.reputation_requirement == {"tatooine": 100}
        assert trainer.skills_taught == ["unarmed_combat", "melee_weapons"]
        assert trainer.max_skill_level == 4
        assert trainer.training_cost == {"credits": 100, "reputation": 50}
        assert trainer.schedule == {"available_hours": [8, 9, 10], "rest_days": []}
        assert trainer.dialogue_options == ["Learn skills", "Ask questions", "Leave"]
        assert trainer.metadata == {"version": "1.0"}


class TestCollectionData:
    """Test the CollectionData dataclass."""
    
    def test_collection_data_creation(self):
        """Test creating a CollectionData object."""
        collection = CollectionData(
            collection_id="test_collection",
            name="Test Collection",
            description="A test collection",
            collection_type="trophy",
            rarity="rare",
            planet="tatooine",
            zones=["mos_eisley", "bestine"],
            items=[{"item_id": "item1", "name": "Test Item"}],
            completion_rewards={"experience": 500, "credits": 1000},
            requirements={"level_requirement": 10},
            state={"status": "available"},
            metadata={"version": "1.0"},
            hints=["Hint 1", "Hint 2"],
            difficulty={"overall": "medium", "time_estimate_hours": 2.0}
        )
        
        assert collection.collection_id == "test_collection"
        assert collection.name == "Test Collection"
        assert collection.description == "A test collection"
        assert collection.collection_type == "trophy"
        assert collection.rarity == "rare"
        assert collection.planet == "tatooine"
        assert collection.zones == ["mos_eisley", "bestine"]
        assert collection.items == [{"item_id": "item1", "name": "Test Item"}]
        assert collection.completion_rewards == {"experience": 500, "credits": 1000}
        assert collection.requirements == {"level_requirement": 10}
        assert collection.state == {"status": "available"}
        assert collection.metadata == {"version": "1.0"}
        assert collection.hints == ["Hint 1", "Hint 2"]
        assert collection.difficulty == {"overall": "medium", "time_estimate_hours": 2.0}


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create subdirectories
        (temp_path / "quests").mkdir()
        (temp_path / "trainers").mkdir()
        (temp_path / "collections").mkdir()
        (temp_path / "dialogue").mkdir()
        (temp_path / "maps").mkdir()
        
        # Create sample quest file
        quest_data = {
            "quest_id": "test_quest",
            "name": "Test Quest",
            "description": "A test quest",
            "quest_type": "collection",
            "difficulty": "medium",
            "level_requirement": 15,
            "planet": "tatooine",
            "zone": "mos_eisley",
            "coordinates": [100, 200],
            "quest_chain": "test_chain",
            "prerequisites": ["prereq1"],
            "rewards": {"experience": 500, "credits": 1000},
            "steps": [{"step_id": "step1", "type": "dialogue"}],
            "completion_conditions": [{"type": "items_collected", "count": 2}],
            "failure_conditions": [{"type": "timeout", "timeout_seconds": 3600}],
            "hints": ["Hint 1"],
            "metadata": {"version": "1.0"},
            "state": {"status": "available"}
        }
        
        with open(temp_path / "quests" / "test_quest.yaml", 'w') as f:
            yaml.dump(quest_data, f)
        
        # Create sample trainers file
        trainers_data = {
            "trainers": [
                {
                    "trainer_id": "test_trainer",
                    "name": "Test Trainer",
                    "profession": "combat",
                    "planet": "tatooine",
                    "zone": "mos_eisley",
                    "coordinates": [200, 300],
                    "level_requirement": 5,
                    "reputation_requirement": {"tatooine": 100},
                    "skills_taught": ["unarmed_combat", "melee_weapons"],
                    "max_skill_level": 4,
                    "training_cost": {"credits": 100, "reputation": 50},
                    "schedule": {"available_hours": [8, 9, 10], "rest_days": []},
                    "dialogue_options": ["Learn skills", "Ask questions", "Leave"],
                    "metadata": {"version": "1.0"}
                }
            ]
        }
        
        with open(temp_path / "trainers" / "trainers.json", 'w') as f:
            json.dump(trainers_data, f)
        
        # Create sample collection file
        collection_data = {
            "collection_id": "test_collection",
            "name": "Test Collection",
            "description": "A test collection",
            "collection_type": "trophy",
            "rarity": "rare",
            "planet": "tatooine",
            "zones": ["mos_eisley", "bestine"],
            "items": [{"item_id": "item1", "name": "Test Item"}],
            "completion_rewards": {"experience": 500, "credits": 1000},
            "requirements": {"level_requirement": 10},
            "state": {"status": "available"},
            "metadata": {"version": "1.0"},
            "hints": ["Hint 1"],
            "difficulty": {"overall": "medium", "time_estimate_hours": 2.0}
        }
        
        with open(temp_path / "collections" / "test_collection.yaml", 'w') as f:
            yaml.dump(collection_data, f)
        
        # Create sample dialogue file
        dialogue_data = {
            "mos_eisley_merchant": {
                "greeting": ["Welcome to my shop!"],
                "quest_offer": ["I have a job for you."],
                "quest_accept": ["I'll help you."],
                "quest_decline": ["Not interested."],
                "quest_complete": ["Excellent work!"]
            }
        }
        
        with open(temp_path / "dialogue" / "patterns.yaml", 'w') as f:
            yaml.dump(dialogue_data, f)
        
        # Create sample map file
        map_data = {
            "planet": "tatooine",
            "name": "Tatooine",
            "description": "A desert planet",
            "zones": {
                "mos_eisley": {
                    "name": "Mos Eisley",
                    "description": "A spaceport town",
                    "coordinates": [0, 0]
                }
            },
            "waypoints": [
                {
                    "name": "Cantina",
                    "coordinates": [100, 200],
                    "zone": "mos_eisley",
                    "type": "landmark"
                }
            ]
        }
        
        with open(temp_path / "maps" / "tatooine.yaml", 'w') as f:
            yaml.dump(map_data, f)
        
        yield temp_path


class TestDatabaseAccess:
    """Test the DatabaseAccess class."""
    
    def test_database_initialization(self, temp_data_dir):
        """Test database initialization."""
        db = DatabaseAccess(str(temp_data_dir))
        
        assert db.data_dir == temp_data_dir
        assert db.logger is not None
        assert db._cache == {}
    
    def test_database_initialization_invalid_dir(self):
        """Test database initialization with invalid directory."""
        with pytest.raises(FileNotFoundError):
            DatabaseAccess("nonexistent_directory")
    
    def test_detect_file_format_yaml(self, temp_data_dir):
        """Test file format detection for YAML files."""
        db = DatabaseAccess(str(temp_data_dir))
        yaml_file = temp_data_dir / "quests" / "test_quest.yaml"
        
        format_type = db._detect_file_format(yaml_file)
        assert format_type == "yaml"
    
    def test_detect_file_format_json(self, temp_data_dir):
        """Test file format detection for JSON files."""
        db = DatabaseAccess(str(temp_data_dir))
        json_file = temp_data_dir / "trainers" / "trainers.json"
        
        format_type = db._detect_file_format(json_file)
        assert format_type == "json"
    
    def test_safe_load_file_yaml(self, temp_data_dir):
        """Test safe loading of YAML file."""
        db = DatabaseAccess(str(temp_data_dir))
        yaml_file = temp_data_dir / "quests" / "test_quest.yaml"
        
        data = db._safe_load_file(yaml_file)
        assert data is not None
        assert data["quest_id"] == "test_quest"
        assert data["name"] == "Test Quest"
    
    def test_safe_load_file_json(self, temp_data_dir):
        """Test safe loading of JSON file."""
        db = DatabaseAccess(str(temp_data_dir))
        json_file = temp_data_dir / "trainers" / "trainers.json"
        
        data = db._safe_load_file(json_file)
        assert data is not None
        assert "trainers" in data
        assert len(data["trainers"]) == 1
        assert data["trainers"][0]["trainer_id"] == "test_trainer"
    
    def test_safe_load_file_nonexistent(self, temp_data_dir):
        """Test safe loading of nonexistent file."""
        db = DatabaseAccess(str(temp_data_dir))
        nonexistent_file = temp_data_dir / "nonexistent.yaml"
        
        data = db._safe_load_file(nonexistent_file)
        assert data is None
    
    def test_load_with_cache(self, temp_data_dir):
        """Test loading with caching."""
        db = DatabaseAccess(str(temp_data_dir))
        yaml_file = temp_data_dir / "quests" / "test_quest.yaml"
        
        # First load
        data1 = db._load_with_cache(yaml_file)
        assert data1 is not None
        
        # Second load (should use cache)
        data2 = db._load_with_cache(yaml_file)
        assert data2 is not None
        assert data1 == data2
        
        # Check cache
        cache_key = db._get_cache_key(yaml_file)
        assert cache_key in db._cache
    
    def test_clear_cache(self, temp_data_dir):
        """Test cache clearing."""
        db = DatabaseAccess(str(temp_data_dir))
        yaml_file = temp_data_dir / "quests" / "test_quest.yaml"
        
        # Load file to populate cache
        db._load_with_cache(yaml_file)
        assert len(db._cache) > 0
        
        # Clear cache
        db.clear_cache()
        assert len(db._cache) == 0
    
    def test_load_quest(self, temp_data_dir):
        """Test loading a specific quest."""
        db = DatabaseAccess(str(temp_data_dir))
        
        quest = db.load_quest("test_quest")
        assert quest is not None
        assert quest.quest_id == "test_quest"
        assert quest.name == "Test Quest"
        assert quest.planet == "tatooine"
        assert quest.zone == "mos_eisley"
        assert quest.coordinates == [100, 200]
    
    def test_load_quest_not_found(self, temp_data_dir):
        """Test loading a quest that doesn't exist."""
        db = DatabaseAccess(str(temp_data_dir))
        
        quest = db.load_quest("nonexistent_quest")
        assert quest is None
    
    def test_load_trainers(self, temp_data_dir):
        """Test loading all trainers."""
        db = DatabaseAccess(str(temp_data_dir))
        
        trainers = db.load_trainers()
        assert len(trainers) == 1
        assert trainers[0].trainer_id == "test_trainer"
        assert trainers[0].name == "Test Trainer"
        assert trainers[0].profession == "combat"
        assert trainers[0].planet == "tatooine"
    
    def test_find_trainers_for_profession(self, temp_data_dir):
        """Test finding trainers for a specific profession."""
        db = DatabaseAccess(str(temp_data_dir))
        
        # Find combat trainers
        combat_trainers = db.find_trainers_for_profession("combat")
        assert len(combat_trainers) == 1
        assert combat_trainers[0].profession == "combat"
        
        # Find medic trainers (should be empty)
        medic_trainers = db.find_trainers_for_profession("medic")
        assert len(medic_trainers) == 0
    
    def test_find_trainers_for_profession_with_planet(self, temp_data_dir):
        """Test finding trainers for a specific profession and planet."""
        db = DatabaseAccess(str(temp_data_dir))
        
        # Find combat trainers on Tatooine
        tatooine_combat_trainers = db.find_trainers_for_profession("combat", "tatooine")
        assert len(tatooine_combat_trainers) == 1
        assert tatooine_combat_trainers[0].planet == "tatooine"
        
        # Find combat trainers on Naboo (should be empty)
        naboo_combat_trainers = db.find_trainers_for_profession("combat", "naboo")
        assert len(naboo_combat_trainers) == 0
    
    def test_load_collections(self, temp_data_dir):
        """Test loading all collections."""
        db = DatabaseAccess(str(temp_data_dir))
        
        collections = db.load_collections()
        assert len(collections) == 1
        assert collections[0].collection_id == "test_collection"
        assert collections[0].name == "Test Collection"
        assert collections[0].planet == "tatooine"
    
    def test_load_dialogue_patterns(self, temp_data_dir):
        """Test loading dialogue patterns for an NPC."""
        db = DatabaseAccess(str(temp_data_dir))
        
        patterns = db.load_dialogue_patterns("mos_eisley_merchant")
        assert patterns is not None
        assert "greeting" in patterns
        assert "quest_offer" in patterns
        assert "quest_accept" in patterns
        assert "quest_decline" in patterns
        assert "quest_complete" in patterns
    
    def test_load_dialogue_patterns_not_found(self, temp_data_dir):
        """Test loading dialogue patterns for a nonexistent NPC."""
        db = DatabaseAccess(str(temp_data_dir))
        
        patterns = db.load_dialogue_patterns("nonexistent_npc")
        assert patterns is None
    
    def test_load_map(self, temp_data_dir):
        """Test loading map data for a planet."""
        db = DatabaseAccess(str(temp_data_dir))
        
        map_data = db.load_map("tatooine")
        assert map_data is not None
        assert map_data["planet"] == "tatooine"
        assert map_data["name"] == "Tatooine"
        assert "zones" in map_data
        assert "waypoints" in map_data
    
    def test_load_map_not_found(self, temp_data_dir):
        """Test loading map data for a nonexistent planet."""
        db = DatabaseAccess(str(temp_data_dir))
        
        map_data = db.load_map("nonexistent_planet")
        assert map_data is None
    
    def test_list_available_quests(self, temp_data_dir):
        """Test listing available quest IDs."""
        db = DatabaseAccess(str(temp_data_dir))
        
        quest_ids = db.list_available_quests()
        assert len(quest_ids) == 1
        assert "test_quest" in quest_ids
    
    def test_get_quests_by_planet(self, temp_data_dir):
        """Test getting quests for a specific planet."""
        db = DatabaseAccess(str(temp_data_dir))
        
        quests = db.get_quests_by_planet("tatooine")
        assert len(quests) == 1
        assert quests[0].planet == "tatooine"
        
        # Test with nonexistent planet
        quests = db.get_quests_by_planet("nonexistent_planet")
        assert len(quests) == 0
    
    def test_get_collections_by_planet(self, temp_data_dir):
        """Test getting collections for a specific planet."""
        db = DatabaseAccess(str(temp_data_dir))
        
        collections = db.get_collections_by_planet("tatooine")
        assert len(collections) == 1
        assert collections[0].planet == "tatooine"
        
        # Test with nonexistent planet
        collections = db.get_collections_by_planet("nonexistent_planet")
        assert len(collections) == 0
    
    def test_search_trainers(self, temp_data_dir):
        """Test searching trainers with various filters."""
        db = DatabaseAccess(str(temp_data_dir))
        
        # Search by profession
        combat_trainers = db.search_trainers(profession="combat")
        assert len(combat_trainers) == 1
        assert combat_trainers[0].profession == "combat"
        
        # Search by planet
        tatooine_trainers = db.search_trainers(planet="tatooine")
        assert len(tatooine_trainers) == 1
        assert tatooine_trainers[0].planet == "tatooine"
        
        # Search by multiple criteria
        tatooine_combat_trainers = db.search_trainers(profession="combat", planet="tatooine")
        assert len(tatooine_combat_trainers) == 1
        assert tatooine_combat_trainers[0].profession == "combat"
        assert tatooine_combat_trainers[0].planet == "tatooine"
        
        # Search with no matches
        naboo_trainers = db.search_trainers(planet="naboo")
        assert len(naboo_trainers) == 0


class TestGlobalFunctions:
    """Test the global convenience functions."""
    
    @patch('core.database.get_database')
    def test_load_quest_global(self, mock_get_database):
        """Test the global load_quest function."""
        mock_db = Mock()
        mock_get_database.return_value = mock_db
        mock_db.load_quest.return_value = Mock(quest_id="test_quest")
        
        quest = load_quest("test_quest")
        
        assert quest is not None
        mock_db.load_quest.assert_called_once_with("test_quest")
    
    @patch('core.database.get_database')
    def test_load_trainers_global(self, mock_get_database):
        """Test the global load_trainers function."""
        mock_db = Mock()
        mock_get_database.return_value = mock_db
        mock_db.load_trainers.return_value = [Mock(trainer_id="test_trainer")]
        
        trainers = load_trainers()
        
        assert len(trainers) == 1
        mock_db.load_trainers.assert_called_once()
    
    @patch('core.database.get_database')
    def test_find_trainers_for_profession_global(self, mock_get_database):
        """Test the global find_trainers_for_profession function."""
        mock_db = Mock()
        mock_get_database.return_value = mock_db
        mock_db.find_trainers_for_profession.return_value = [Mock(trainer_id="test_trainer")]
        
        trainers = find_trainers_for_profession("combat", "tatooine")
        
        assert len(trainers) == 1
        mock_db.find_trainers_for_profession.assert_called_once_with("combat", "tatooine")
    
    @patch('core.database.get_database')
    def test_load_collections_global(self, mock_get_database):
        """Test the global load_collections function."""
        mock_db = Mock()
        mock_get_database.return_value = mock_db
        mock_db.load_collections.return_value = [Mock(collection_id="test_collection")]
        
        collections = load_collections()
        
        assert len(collections) == 1
        mock_db.load_collections.assert_called_once()
    
    @patch('core.database.get_database')
    def test_load_dialogue_patterns_global(self, mock_get_database):
        """Test the global load_dialogue_patterns function."""
        mock_db = Mock()
        mock_get_database.return_value = mock_db
        mock_db.load_dialogue_patterns.return_value = {"greeting": ["Hello"]}
        
        patterns = load_dialogue_patterns("test_npc")
        
        assert patterns is not None
        mock_db.load_dialogue_patterns.assert_called_once_with("test_npc")
    
    @patch('core.database.get_database')
    def test_load_map_global(self, mock_get_database):
        """Test the global load_map function."""
        mock_db = Mock()
        mock_get_database.return_value = mock_db
        mock_db.load_map.return_value = {"planet": "tatooine"}
        
        map_data = load_map("tatooine")
        
        assert map_data is not None
        mock_db.load_map.assert_called_once_with("tatooine")


class TestSingletonPattern:
    """Test the singleton pattern implementation."""
    
    def test_singleton_pattern(self):
        """Test that get_database returns the same instance."""
        # Reset the singleton instance
        import core.database
        core.database._database_instance = None
        
        # Get two instances
        instance1 = get_database()
        instance2 = get_database()
        
        # They should be the same instance
        assert instance1 is instance2


class TestIntegration:
    """Integration tests for the database system."""
    
    def test_full_quest_lifecycle(self, temp_data_dir):
        """Test a complete quest loading lifecycle."""
        db = DatabaseAccess(str(temp_data_dir))
        
        # List available quests
        quest_ids = db.list_available_quests()
        assert len(quest_ids) == 1
        assert "test_quest" in quest_ids
        
        # Load the quest
        quest = db.load_quest("test_quest")
        assert quest is not None
        assert quest.quest_id == "test_quest"
        
        # Get quests by planet
        planet_quests = db.get_quests_by_planet("tatooine")
        assert len(planet_quests) == 1
        assert planet_quests[0].quest_id == "test_quest"
    
    def test_full_trainer_lifecycle(self, temp_data_dir):
        """Test a complete trainer loading lifecycle."""
        db = DatabaseAccess(str(temp_data_dir))
        
        # Load all trainers
        trainers = db.load_trainers()
        assert len(trainers) == 1
        
        # Find trainers by profession
        combat_trainers = db.find_trainers_for_profession("combat")
        assert len(combat_trainers) == 1
        assert combat_trainers[0].profession == "combat"
        
        # Search trainers with filters
        tatooine_trainers = db.search_trainers(planet="tatooine")
        assert len(tatooine_trainers) == 1
        assert tatooine_trainers[0].planet == "tatooine"
    
    def test_full_collection_lifecycle(self, temp_data_dir):
        """Test a complete collection loading lifecycle."""
        db = DatabaseAccess(str(temp_data_dir))
        
        # Load all collections
        collections = db.load_collections()
        assert len(collections) == 1
        assert collections[0].collection_id == "test_collection"
        
        # Get collections by planet
        planet_collections = db.get_collections_by_planet("tatooine")
        assert len(planet_collections) == 1
        assert planet_collections[0].planet == "tatooine"
    
    def test_dialogue_and_map_integration(self, temp_data_dir):
        """Test dialogue and map loading integration."""
        db = DatabaseAccess(str(temp_data_dir))
        
        # Load dialogue patterns
        patterns = db.load_dialogue_patterns("mos_eisley_merchant")
        assert patterns is not None
        assert "greeting" in patterns
        
        # Load map data
        map_data = db.load_map("tatooine")
        assert map_data is not None
        assert map_data["planet"] == "tatooine"
        assert "zones" in map_data
        assert "waypoints" in map_data 
"""
Test suite for Batch 154 - Static Builds Library

This module provides comprehensive tests for:
- Data models and validation
- Library operations (CRUD)
- API endpoints
- Error handling
- Integration testing
"""

import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from core.static_builds_library import (
    get_static_builds_library,
    StaticBuild,
    BuildMetadata,
    SkillTree,
    EquipmentRecommendation,
    PerformanceRatings,
    UserRatings,
    BuildCategory,
    BuildDifficulty,
    BuildSpecialization,
    BuildSource,
    StaticBuildsLibrary
)


class TestDataModels:
    """Test data model classes."""
    
    def test_build_metadata_creation(self):
        """Test BuildMetadata creation and validation."""
        metadata = BuildMetadata(
            id="test_build",
            name="Test Build",
            description="A test build"
        )
        
        assert metadata.id == "test_build"
        assert metadata.name == "Test Build"
        assert metadata.description == "A test build"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Unknown"
        assert metadata.source == BuildSource.AI_GENERATED
        assert metadata.difficulty == BuildDifficulty.INTERMEDIATE
        assert metadata.category == BuildCategory.COMBAT
        assert metadata.specialization == BuildSpecialization.PVE
        assert metadata.tags == []
        assert metadata.created_at is not None
        assert metadata.updated_at is not None
    
    def test_skill_tree_creation(self):
        """Test SkillTree creation."""
        skill_tree = SkillTree(
            profession="rifleman",
            skills=["skill1", "skill2", "skill3"],
            xp_costs={"skill1": 100, "skill2": 200},
            prerequisites=["prereq1"]
        )
        
        assert skill_tree.profession == "rifleman"
        assert skill_tree.skills == ["skill1", "skill2", "skill3"]
        assert skill_tree.xp_costs == {"skill1": 100, "skill2": 200}
        assert skill_tree.prerequisites == ["prereq1"]
    
    def test_equipment_recommendation_creation(self):
        """Test EquipmentRecommendation creation."""
        equipment = EquipmentRecommendation(
            weapons={"primary": ["weapon1", "weapon2"]},
            armor={"head": ["helmet"]},
            tapes=["tape1", "tape2"],
            resists=["resist1"],
            buffs=["buff1"]
        )
        
        assert equipment.weapons == {"primary": ["weapon1", "weapon2"]}
        assert equipment.armor == {"head": ["helmet"]}
        assert equipment.tapes == ["tape1", "tape2"]
        assert equipment.resists == ["resist1"]
        assert equipment.buffs == ["buff1"]
    
    def test_performance_ratings_creation(self):
        """Test PerformanceRatings creation."""
        performance = PerformanceRatings(
            pve_rating=8.5,
            pvp_rating=7.0,
            solo_rating=9.0,
            group_rating=6.5,
            farming_rating=8.0
        )
        
        assert performance.pve_rating == 8.5
        assert performance.pvp_rating == 7.0
        assert performance.solo_rating == 9.0
        assert performance.group_rating == 6.5
        assert performance.farming_rating == 8.0
    
    def test_user_ratings_creation(self):
        """Test UserRatings creation."""
        ratings = UserRatings(
            total_votes=10,
            average_rating=4.2,
            rating_breakdown={"5": 5, "4": 3, "3": 2},
            user_reviews=[{"user": "test", "rating": 5}]
        )
        
        assert ratings.total_votes == 10
        assert ratings.average_rating == 4.2
        assert ratings.rating_breakdown == {"5": 5, "4": 3, "3": 2}
        assert ratings.user_reviews == [{"user": "test", "rating": 5}]


class TestStaticBuildsLibrary:
    """Test StaticBuildsLibrary functionality."""
    
    @pytest.fixture
    def temp_library(self):
        """Create a temporary library for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            builds_dir = Path(temp_dir) / "builds"
            data_file = Path(temp_dir) / "test_builds.json"
            
            library = StaticBuildsLibrary(
                builds_dir=str(builds_dir),
                data_file=str(data_file)
            )
            yield library
    
    def test_library_initialization(self, temp_library):
        """Test library initialization."""
        assert temp_library.builds_dir.exists()
        assert temp_library.data_file.parent.exists()
        assert len(temp_library.builds) == 0
    
    def test_create_build(self, temp_library):
        """Test creating a build."""
        build = StaticBuild(
            metadata=BuildMetadata(
                id="test_build",
                name="Test Build",
                description="A test build"
            ),
            professions={"primary": "rifleman"},
            skill_trees={
                "rifleman": SkillTree(
                    profession="rifleman",
                    skills=["skill1", "skill2"]
                )
            },
            buff_priority=["buff1", "buff2"],
            weapon_type="rifle",
            equipment=EquipmentRecommendation(),
            performance=PerformanceRatings(),
            ratings=UserRatings()
        )
        
        result = temp_library.create_build(build)
        assert result is True
        
        # Check that build was added to memory
        assert "test_build" in temp_library.builds
        assert temp_library.builds["test_build"] == build
        
        # Check that markdown file was created
        md_file = temp_library.builds_dir / "test_build.md"
        assert md_file.exists()
        
        # Check that database file was created
        assert temp_library.data_file.exists()
    
    def test_get_build(self, temp_library):
        """Test getting a build by ID."""
        # Create a test build
        build = StaticBuild(
            metadata=BuildMetadata(
                id="test_build",
                name="Test Build",
                description="A test build"
            ),
            professions={"primary": "rifleman"},
            skill_trees={},
            buff_priority=[],
            weapon_type="rifle",
            equipment=EquipmentRecommendation(),
            performance=PerformanceRatings(),
            ratings=UserRatings()
        )
        
        temp_library.builds["test_build"] = build
        
        # Test getting existing build
        retrieved_build = temp_library.get_build("test_build")
        assert retrieved_build == build
        
        # Test getting non-existent build
        assert temp_library.get_build("non_existent") is None
    
    def test_list_builds_filtering(self, temp_library):
        """Test listing builds with filtering."""
        # Create test builds
        build1 = StaticBuild(
            metadata=BuildMetadata(
                id="combat_build",
                name="Combat Build",
                category=BuildCategory.COMBAT,
                difficulty=BuildDifficulty.INTERMEDIATE,
                specialization=BuildSpecialization.PVE
            ),
            professions={"primary": "rifleman"},
            skill_trees={},
            buff_priority=[],
            weapon_type="rifle",
            equipment=EquipmentRecommendation(),
            performance=PerformanceRatings(),
            ratings=UserRatings()
        )
        
        build2 = StaticBuild(
            metadata=BuildMetadata(
                id="support_build",
                name="Support Build",
                category=BuildCategory.SUPPORT,
                difficulty=BuildDifficulty.BEGINNER,
                specialization=BuildSpecialization.GROUP
            ),
            professions={"primary": "medic"},
            skill_trees={},
            buff_priority=[],
            weapon_type="pistol",
            equipment=EquipmentRecommendation(),
            performance=PerformanceRatings(),
            ratings=UserRatings()
        )
        
        temp_library.builds["combat_build"] = build1
        temp_library.builds["support_build"] = build2
        
        # Test filtering by category
        combat_builds = temp_library.list_builds(category=BuildCategory.COMBAT)
        assert len(combat_builds) == 1
        assert combat_builds[0].metadata.id == "combat_build"
        
        # Test filtering by difficulty
        beginner_builds = temp_library.list_builds(difficulty=BuildDifficulty.BEGINNER)
        assert len(beginner_builds) == 1
        assert beginner_builds[0].metadata.id == "support_build"
        
        # Test filtering by specialization
        pve_builds = temp_library.list_builds(specialization=BuildSpecialization.PVE)
        assert len(pve_builds) == 1
        assert pve_builds[0].metadata.id == "combat_build"
    
    def test_search_builds(self, temp_library):
        """Test searching builds."""
        # Create test builds
        build1 = StaticBuild(
            metadata=BuildMetadata(
                id="rifleman_build",
                name="Rifleman Build",
                description="A rifleman build for combat",
                tags=["rifleman", "combat"]
            ),
            professions={"primary": "rifleman"},
            skill_trees={},
            buff_priority=[],
            weapon_type="rifle",
            equipment=EquipmentRecommendation(),
            performance=PerformanceRatings(),
            ratings=UserRatings()
        )
        
        build2 = StaticBuild(
            metadata=BuildMetadata(
                id="medic_build",
                name="Medic Build",
                description="A medic build for healing",
                tags=["medic", "healing"]
            ),
            professions={"primary": "medic"},
            skill_trees={},
            buff_priority=[],
            weapon_type="pistol",
            equipment=EquipmentRecommendation(),
            performance=PerformanceRatings(),
            ratings=UserRatings()
        )
        
        temp_library.builds["rifleman_build"] = build1
        temp_library.builds["medic_build"] = build2
        
        # Test searching by name
        rifleman_results = temp_library.search_builds("rifleman")
        assert len(rifleman_results) == 1
        assert rifleman_results[0].metadata.id == "rifleman_build"
        
        # Test searching by description
        healing_results = temp_library.search_builds("healing")
        assert len(healing_results) == 1
        assert healing_results[0].metadata.id == "medic_build"
        
        # Test searching by tags
        combat_results = temp_library.search_builds("combat")
        assert len(combat_results) == 1
        assert combat_results[0].metadata.id == "rifleman_build"
    
    def test_update_build(self, temp_library):
        """Test updating a build."""
        # Create a test build
        build = StaticBuild(
            metadata=BuildMetadata(
                id="test_build",
                name="Original Name",
                description="Original description"
            ),
            professions={"primary": "rifleman"},
            skill_trees={},
            buff_priority=[],
            weapon_type="rifle",
            equipment=EquipmentRecommendation(),
            performance=PerformanceRatings(),
            ratings=UserRatings()
        )
        
        temp_library.builds["test_build"] = build
        
        # Update the build
        updates = {
            "name": "Updated Name",
            "description": "Updated description",
            "buff_priority": ["new_buff1", "new_buff2"],
            "performance": {"pve_rating": 9.0}
        }
        
        result = temp_library.update_build("test_build", updates)
        assert result is True
        
        # Check that updates were applied
        updated_build = temp_library.builds["test_build"]
        assert updated_build.metadata.name == "Updated Name"
        assert updated_build.metadata.description == "Updated description"
        assert updated_build.buff_priority == ["new_buff1", "new_buff2"]
        assert updated_build.performance.pve_rating == 9.0
    
    def test_delete_build(self, temp_library):
        """Test deleting a build."""
        # Create a test build
        build = StaticBuild(
            metadata=BuildMetadata(
                id="test_build",
                name="Test Build",
                description="A test build"
            ),
            professions={"primary": "rifleman"},
            skill_trees={},
            buff_priority=[],
            weapon_type="rifle",
            equipment=EquipmentRecommendation(),
            performance=PerformanceRatings(),
            ratings=UserRatings()
        )
        
        temp_library.builds["test_build"] = build
        
        # Create a markdown file
        md_file = temp_library.builds_dir / "test_build.md"
        md_file.write_text("# Test Build")
        
        # Delete the build
        result = temp_library.delete_build("test_build")
        assert result is True
        
        # Check that build was removed from memory
        assert "test_build" not in temp_library.builds
        
        # Check that markdown file was deleted
        assert not md_file.exists()
    
    def test_get_statistics(self, temp_library):
        """Test getting library statistics."""
        # Create test builds with different categories and difficulties
        builds = [
            StaticBuild(
                metadata=BuildMetadata(
                    id="build1",
                    name="Build 1",
                    category=BuildCategory.COMBAT,
                    difficulty=BuildDifficulty.INTERMEDIATE,
                    specialization=BuildSpecialization.PVE,
                    source=BuildSource.AI_GENERATED
                ),
                professions={"primary": "rifleman"},
                skill_trees={},
                buff_priority=[],
                weapon_type="rifle",
                equipment=EquipmentRecommendation(),
                performance=PerformanceRatings(),
                ratings=UserRatings()
            ),
            StaticBuild(
                metadata=BuildMetadata(
                    id="build2",
                    name="Build 2",
                    category=BuildCategory.SUPPORT,
                    difficulty=BuildDifficulty.BEGINNER,
                    specialization=BuildSpecialization.GROUP,
                    source=BuildSource.PLAYER_CREATED
                ),
                professions={"primary": "medic"},
                skill_trees={},
                buff_priority=[],
                weapon_type="pistol",
                equipment=EquipmentRecommendation(),
                performance=PerformanceRatings(),
                ratings=UserRatings()
            )
        ]
        
        for build in builds:
            temp_library.builds[build.metadata.id] = build
        
        stats = temp_library.get_statistics()
        
        assert stats["total_builds"] == 2
        assert stats["categories"]["combat"] == 1
        assert stats["categories"]["support"] == 1
        assert stats["difficulties"]["intermediate"] == 1
        assert stats["difficulties"]["beginner"] == 1
        assert stats["specializations"]["pve"] == 1
        assert stats["specializations"]["group"] == 1
        assert stats["sources"]["ai_generated"] == 1
        assert stats["sources"]["player_created"] == 1


class TestMarkdownGeneration:
    """Test markdown file generation."""
    
    @pytest.fixture
    def temp_library(self):
        """Create a temporary library for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            builds_dir = Path(temp_dir) / "builds"
            data_file = Path(temp_dir) / "test_builds.json"
            
            library = StaticBuildsLibrary(
                builds_dir=str(builds_dir),
                data_file=str(data_file)
            )
            yield library
    
    def test_markdown_generation(self, temp_library):
        """Test markdown file generation."""
        build = StaticBuild(
            metadata=BuildMetadata(
                id="test_build",
                name="Test Build",
                description="A test build for demonstration",
                author="Test Author",
                source=BuildSource.AI_GENERATED,
                difficulty=BuildDifficulty.INTERMEDIATE,
                category=BuildCategory.COMBAT,
                specialization=BuildSpecialization.PVE,
                tags=["test", "demo"]
            ),
            professions={"primary": "rifleman", "secondary": "medic"},
            skill_trees={
                "rifleman": SkillTree(
                    profession="rifleman",
                    skills=["skill1", "skill2", "skill3"]
                ),
                "medic": SkillTree(
                    profession="medic",
                    skills=["heal1", "heal2"]
                )
            },
            buff_priority=["accuracy", "damage", "healing"],
            weapon_type="rifle",
            equipment=EquipmentRecommendation(
                weapons={"primary": ["T21", "E11"]},
                armor={"head": ["Helmet"], "chest": ["Armor"]},
                tapes=["accuracy", "damage"],
                resists=["energy", "kinetic"],
                buffs=["Combat Stim"]
            ),
            performance=PerformanceRatings(
                pve_rating=8.5,
                pvp_rating=6.0,
                solo_rating=9.0,
                group_rating=8.0,
                farming_rating=7.5
            ),
            ratings=UserRatings(
                total_votes=10,
                average_rating=4.2
            ),
            notes="This is a test build for demonstration purposes.",
            links={
                "Skill Calculator": "https://example.com/skills",
                "Guide": "https://example.com/guide"
            }
        )
        
        # Create the build
        temp_library.create_build(build)
        
        # Check that markdown file was created
        md_file = temp_library.builds_dir / "test_build.md"
        assert md_file.exists()
        
        # Read and verify content
        content = md_file.read_text()
        
        # Check for key sections
        assert "# Test Build" in content
        assert "Generated by SWGDB" in content
        assert "## Professions" in content
        assert "## Skill Trees" in content
        assert "## Buff Priority" in content
        assert "## Equipment" in content
        assert "## Performance Ratings" in content
        assert "## Community Ratings" in content
        assert "## Links" in content
        assert "## Notes" in content


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.fixture
    def temp_library(self):
        """Create a temporary library for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            builds_dir = Path(temp_dir) / "builds"
            data_file = Path(temp_dir) / "test_builds.json"
            
            library = StaticBuildsLibrary(
                builds_dir=str(builds_dir),
                data_file=str(data_file)
            )
            yield library
    
    def test_corrupted_database_loading(self, temp_library):
        """Test handling of corrupted database file."""
        # Create a corrupted JSON file
        temp_library.data_file.write_text("{ invalid json }")
        
        # Library should handle this gracefully
        temp_library._load_existing_builds()
        assert len(temp_library.builds) == 0
    
    def test_missing_build_file(self, temp_library):
        """Test handling of missing build files."""
        # Try to get a non-existent build
        build = temp_library.get_build("non_existent")
        assert build is None
    
    def test_update_nonexistent_build(self, temp_library):
        """Test updating a non-existent build."""
        result = temp_library.update_build("non_existent", {"name": "New Name"})
        assert result is False
    
    def test_delete_nonexistent_build(self, temp_library):
        """Test deleting a non-existent build."""
        result = temp_library.delete_build("non_existent")
        assert result is False


class TestIntegration:
    """Integration tests for the static builds library."""
    
    @pytest.fixture
    def temp_library(self):
        """Create a temporary library for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            builds_dir = Path(temp_dir) / "builds"
            data_file = Path(temp_dir) / "test_builds.json"
            
            library = StaticBuildsLibrary(
                builds_dir=str(builds_dir),
                data_file=str(data_file)
            )
            yield library
    
    def test_full_workflow(self, temp_library):
        """Test a complete workflow: create, update, search, delete."""
        # Create a build
        build = StaticBuild(
            metadata=BuildMetadata(
                id="workflow_test",
                name="Workflow Test Build",
                description="A build for testing the complete workflow"
            ),
            professions={"primary": "rifleman"},
            skill_trees={
                "rifleman": SkillTree(
                    profession="rifleman",
                    skills=["skill1", "skill2"]
                )
            },
            buff_priority=["buff1"],
            weapon_type="rifle",
            equipment=EquipmentRecommendation(),
            performance=PerformanceRatings(),
            ratings=UserRatings()
        )
        
        # Step 1: Create
        assert temp_library.create_build(build) is True
        assert "workflow_test" in temp_library.builds
        
        # Step 2: Retrieve
        retrieved_build = temp_library.get_build("workflow_test")
        assert retrieved_build is not None
        assert retrieved_build.metadata.name == "Workflow Test Build"
        
        # Step 3: Search
        search_results = temp_library.search_builds("workflow")
        assert len(search_results) == 1
        assert search_results[0].metadata.id == "workflow_test"
        
        # Step 4: Update
        updates = {"name": "Updated Workflow Test Build"}
        assert temp_library.update_build("workflow_test", updates) is True
        
        updated_build = temp_library.get_build("workflow_test")
        assert updated_build.metadata.name == "Updated Workflow Test Build"
        
        # Step 5: Delete
        assert temp_library.delete_build("workflow_test") is True
        assert "workflow_test" not in temp_library.builds
        assert temp_library.get_build("workflow_test") is None
    
    def test_multiple_builds_management(self, temp_library):
        """Test managing multiple builds."""
        # Create multiple builds
        builds = []
        for i in range(3):
            build = StaticBuild(
                metadata=BuildMetadata(
                    id=f"build_{i}",
                    name=f"Build {i}",
                    description=f"Build {i} description",
                    category=BuildCategory.COMBAT if i % 2 == 0 else BuildCategory.SUPPORT
                ),
                professions={"primary": "rifleman" if i % 2 == 0 else "medic"},
                skill_trees={},
                buff_priority=[],
                weapon_type="rifle" if i % 2 == 0 else "pistol",
                equipment=EquipmentRecommendation(),
                performance=PerformanceRatings(),
                ratings=UserRatings()
            )
            builds.append(build)
            temp_library.create_build(build)
        
        # Test listing all builds
        all_builds = temp_library.list_builds()
        assert len(all_builds) == 3
        
        # Test filtering
        combat_builds = temp_library.list_builds(category=BuildCategory.COMBAT)
        assert len(combat_builds) == 2
        
        support_builds = temp_library.list_builds(category=BuildCategory.SUPPORT)
        assert len(support_builds) == 1
        
        # Test statistics
        stats = temp_library.get_statistics()
        assert stats["total_builds"] == 3
        assert stats["categories"]["combat"] == 2
        assert stats["categories"]["support"] == 1


if __name__ == "__main__":
    pytest.main([__file__]) 
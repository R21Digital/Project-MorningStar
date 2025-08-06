"""Test suite for Batch 125 - SWG Armory implementation.

This test suite verifies the player build showcase and ranking system functionality,
including the public build browser API, SWGDB site pages, and data structures.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch

from api.public_build_browser import (
    PublicBuildBrowser, 
    PlayerBuild, 
    BuildVisibility, 
    BuildRanking,
    get_build_browser
)


class TestBuildVisibility:
    """Test BuildVisibility enum functionality."""
    
    def test_build_visibility_values(self):
        """Test that BuildVisibility enum has correct values."""
        assert BuildVisibility.PRIVATE.value == "private"
        assert BuildVisibility.PUBLIC.value == "public"
        assert BuildVisibility.FEATURED.value == "featured"


class TestBuildRanking:
    """Test BuildRanking enum functionality."""
    
    def test_build_ranking_values(self):
        """Test that BuildRanking enum has correct values."""
        assert BuildRanking.TOP_DPS.value == "top_dps"
        assert BuildRanking.POPULAR_BUFF_BOT.value == "popular_buff_bot"
        assert BuildRanking.BEST_TANK.value == "best_tank"
        assert BuildRanking.MOST_VERSATILE.value == "most_versatile"
        assert BuildRanking.COMMUNITY_CHOICE.value == "community_choice"


class TestPlayerBuild:
    """Test PlayerBuild dataclass functionality."""
    
    def test_player_build_creation(self):
        """Test creating a PlayerBuild instance."""
        build = PlayerBuild(
            player_name="TestPlayer",
            character_name="TestCharacter",
            server="TestServer",
            faction="rebel",
            gcw_rank=10,
            professions={"primary": "rifleman", "secondary": "medic"},
            skills={"rifleman": ["rifle_shot", "marksman_shot"]},
            stats={"health": 2000, "action": 1500},
            armor={"helmet": {"name": "Test Helmet", "kinetic": 40.0}},
            tapes=[{"name": "Test Tape", "effect": "+10% Accuracy"}],
            resists={"kinetic": 35.0, "energy": 30.0},
            weapons=[{"name": "Test Rifle", "damage_type": "kinetic"}],
            build_summary="Test build summary",
            performance_metrics={"pve_rating": 8.5},
            tags=["pve", "rifleman"],
            visibility=BuildVisibility.PUBLIC,
            rankings=[BuildRanking.TOP_DPS],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            views=100,
            likes=25,
            comments=[]
        )
        
        assert build.player_name == "TestPlayer"
        assert build.character_name == "TestCharacter"
        assert build.server == "TestServer"
        assert build.faction == "rebel"
        assert build.gcw_rank == 10
        assert build.visibility == BuildVisibility.PUBLIC
        assert BuildRanking.TOP_DPS in build.rankings


class TestPublicBuildBrowser:
    """Test PublicBuildBrowser functionality."""
    
    @pytest.fixture
    def temp_builds_dir(self, tmp_path):
        """Create a temporary builds directory for testing."""
        builds_dir = tmp_path / "player_builds"
        builds_dir.mkdir()
        return builds_dir
    
    @pytest.fixture
    def build_browser(self, temp_builds_dir):
        """Create a PublicBuildBrowser instance for testing."""
        return PublicBuildBrowser(str(temp_builds_dir))
    
    @pytest.fixture
    def sample_build_data(self):
        """Sample build data for testing."""
        return {
            "player_name": "TestPlayer",
            "character_name": "TestCharacter",
            "server": "TestServer",
            "faction": "rebel",
            "gcw_rank": 10,
            "professions": {"primary": "rifleman", "secondary": "medic"},
            "skills": {
                "rifleman": ["rifle_shot", "marksman_shot"],
                "medic": ["heal_wound", "heal_battle_fatigue"]
            },
            "stats": {"health": 2000, "action": 1500},
            "armor": {
                "helmet": {"name": "Test Helmet", "kinetic": 40.0, "energy": 35.0, "special": 25.0}
            },
            "tapes": [{"name": "Test Tape", "effect": "+10% Accuracy"}],
            "resists": {"kinetic": 35.0, "energy": 30.0},
            "weapons": [{"name": "Test Rifle", "damage_type": "kinetic", "min_damage": 800, "max_damage": 1000}],
            "build_summary": "Test build summary",
            "performance_metrics": {"pve_rating": 8.5, "pvp_rating": 7.0},
            "tags": ["pve", "rifleman"],
            "visibility": "public",
            "rankings": ["top_dps"],
            "created_at": "2025-01-15T10:30:00",
            "updated_at": "2025-01-20T14:45:00",
            "views": 100,
            "likes": 25,
            "comments": []
        }
    
    def test_build_browser_initialization(self, build_browser):
        """Test PublicBuildBrowser initialization."""
        assert build_browser.builds_dir.exists()
        assert isinstance(build_browser.builds, dict)
    
    def test_publish_build(self, build_browser, sample_build_data):
        """Test publishing a new build."""
        build_id = build_browser.publish_build(sample_build_data)
        
        assert build_id == "TestPlayer_TestCharacter"
        assert build_id in build_browser.builds
        
        build = build_browser.builds[build_id]
        assert build.player_name == "TestPlayer"
        assert build.character_name == "TestCharacter"
        assert build.visibility == BuildVisibility.PUBLIC
        assert BuildRanking.TOP_DPS in build.rankings
    
    def test_get_build(self, build_browser, sample_build_data):
        """Test retrieving a specific build."""
        build_id = build_browser.publish_build(sample_build_data)
        build = build_browser.get_build(build_id)
        
        assert build is not None
        assert build.player_name == "TestPlayer"
        assert build.character_name == "TestCharacter"
    
    def test_get_build_not_found(self, build_browser):
        """Test retrieving a non-existent build."""
        build = build_browser.get_build("nonexistent_build")
        assert build is None
    
    def test_get_all_builds(self, build_browser, sample_build_data):
        """Test retrieving all builds."""
        build_browser.publish_build(sample_build_data)
        builds = build_browser.get_all_builds()
        
        assert len(builds) == 1
        assert builds[0].player_name == "TestPlayer"
    
    def test_get_all_builds_with_visibility_filter(self, build_browser, sample_build_data):
        """Test retrieving builds with visibility filter."""
        build_browser.publish_build(sample_build_data)
        builds = build_browser.get_all_builds(visibility=BuildVisibility.PUBLIC)
        
        assert len(builds) == 1
        assert builds[0].visibility == BuildVisibility.PUBLIC
    
    def test_search_builds_by_profession(self, build_browser, sample_build_data):
        """Test searching builds by profession."""
        build_browser.publish_build(sample_build_data)
        builds = build_browser.search_builds(profession="rifleman")
        
        assert len(builds) == 1
        assert "rifleman" in builds[0].professions.values()
    
    def test_search_builds_by_faction(self, build_browser, sample_build_data):
        """Test searching builds by faction."""
        build_browser.publish_build(sample_build_data)
        builds = build_browser.search_builds(faction="rebel")
        
        assert len(builds) == 1
        assert builds[0].faction == "rebel"
    
    def test_search_builds_by_query(self, build_browser, sample_build_data):
        """Test searching builds by text query."""
        build_browser.publish_build(sample_build_data)
        builds = build_browser.search_builds(query="Test build")
        
        assert len(builds) == 1
        assert "Test build" in builds[0].build_summary
    
    def test_search_builds_by_min_gcw_rank(self, build_browser, sample_build_data):
        """Test searching builds by minimum GCW rank."""
        build_browser.publish_build(sample_build_data)
        builds = build_browser.search_builds(min_gcw_rank=5)
        
        assert len(builds) == 1
        assert builds[0].gcw_rank >= 5
    
    def test_get_top_builds(self, build_browser, sample_build_data):
        """Test getting top builds by ranking."""
        build_browser.publish_build(sample_build_data)
        builds = build_browser.get_top_builds(BuildRanking.TOP_DPS)
        
        assert len(builds) == 1
        assert BuildRanking.TOP_DPS in builds[0].rankings
    
    def test_increment_views(self, build_browser, sample_build_data):
        """Test incrementing build views."""
        build_id = build_browser.publish_build(sample_build_data)
        initial_views = build_browser.builds[build_id].views
        
        build_browser.increment_views(build_id)
        
        assert build_browser.builds[build_id].views == initial_views + 1
    
    def test_like_build(self, build_browser, sample_build_data):
        """Test liking a build."""
        build_id = build_browser.publish_build(sample_build_data)
        initial_likes = build_browser.builds[build_id].likes
        
        build_browser.like_build(build_id)
        
        assert build_browser.builds[build_id].likes == initial_likes + 1
    
    def test_add_comment(self, build_browser, sample_build_data):
        """Test adding a comment to a build."""
        build_id = build_browser.publish_build(sample_build_data)
        initial_comments = len(build_browser.builds[build_id].comments)
        
        build_browser.add_comment(build_id, "TestUser", "Great build!")
        
        assert len(build_browser.builds[build_id].comments) == initial_comments + 1
        assert build_browser.builds[build_id].comments[-1]["commenter"] == "TestUser"
        assert build_browser.builds[build_id].comments[-1]["comment"] == "Great build!"
    
    def test_update_build_rankings(self, build_browser, sample_build_data):
        """Test updating build rankings."""
        build_id = build_browser.publish_build(sample_build_data)
        new_rankings = [BuildRanking.TOP_DPS, BuildRanking.COMMUNITY_CHOICE]
        
        build_browser.update_build_rankings(build_id, new_rankings)
        
        assert build_browser.builds[build_id].rankings == new_rankings
    
    def test_get_build_statistics(self, build_browser, sample_build_data):
        """Test getting build statistics."""
        build_browser.publish_build(sample_build_data)
        stats = build_browser.get_build_statistics()
        
        assert stats["total_builds"] == 1
        assert stats["public_builds"] == 1
        assert "rebel" in stats["faction_distribution"]
        assert "rifleman" in stats["profession_distribution"]


class TestBuildDataPersistence:
    """Test build data persistence functionality."""
    
    @pytest.fixture
    def temp_builds_dir(self, tmp_path):
        """Create a temporary builds directory for testing."""
        builds_dir = tmp_path / "player_builds"
        builds_dir.mkdir()
        return builds_dir
    
    def test_build_save_and_load(self, temp_builds_dir):
        """Test saving and loading build data."""
        browser = PublicBuildBrowser(str(temp_builds_dir))
        
        # Create sample build data
        build_data = {
            "player_name": "TestPlayer",
            "character_name": "TestCharacter",
            "server": "TestServer",
            "faction": "rebel",
            "gcw_rank": 10,
            "professions": {"primary": "rifleman"},
            "skills": {"rifleman": ["rifle_shot"]},
            "stats": {"health": 2000},
            "armor": {"helmet": {"name": "Test Helmet", "kinetic": 40.0}},
            "tapes": [],
            "resists": {"kinetic": 35.0},
            "weapons": [],
            "build_summary": "Test build",
            "performance_metrics": {"pve_rating": 8.5},
            "tags": ["pve"],
            "visibility": "public",
            "rankings": ["top_dps"],
            "created_at": "2025-01-15T10:30:00",
            "updated_at": "2025-01-20T14:45:00",
            "views": 100,
            "likes": 25,
            "comments": []
        }
        
        # Publish build
        build_id = browser.publish_build(build_data)
        
        # Verify file was created
        build_file = temp_builds_dir / f"{build_id}.json"
        assert build_file.exists()
        
        # Load the file and verify content
        with open(build_file, 'r') as f:
            loaded_data = json.load(f)
        
        assert loaded_data["player_name"] == "TestPlayer"
        assert loaded_data["character_name"] == "TestCharacter"
        assert loaded_data["visibility"] == "public"
        assert "top_dps" in loaded_data["rankings"]


class TestSWGArmoryIntegration:
    """Test SWG Armory integration functionality."""
    
    def test_get_build_browser_singleton(self):
        """Test that get_build_browser returns a singleton instance."""
        browser1 = get_build_browser()
        browser2 = get_build_browser()
        
        assert browser1 is browser2
        assert isinstance(browser1, PublicBuildBrowser)
    
    def test_build_id_generation(self):
        """Test build ID generation from player and character names."""
        browser = PublicBuildBrowser()
        
        build_data = {
            "player_name": "TestPlayer",
            "character_name": "TestCharacter",
            "server": "TestServer",
            "faction": "rebel",
            "gcw_rank": 10,
            "professions": {"primary": "rifleman"},
            "skills": {"rifleman": ["rifle_shot"]},
            "stats": {"health": 2000},
            "armor": {"helmet": {"name": "Test Helmet", "kinetic": 40.0}},
            "tapes": [],
            "resists": {"kinetic": 35.0},
            "weapons": [],
            "build_summary": "Test build",
            "performance_metrics": {"pve_rating": 8.5},
            "tags": ["pve"],
            "visibility": "public",
            "rankings": ["top_dps"],
            "created_at": "2025-01-15T10:30:00",
            "updated_at": "2025-01-20T14:45:00",
            "views": 100,
            "likes": 25,
            "comments": []
        }
        
        build_id = browser.publish_build(build_data)
        expected_id = "TestPlayer_TestCharacter"
        
        assert build_id == expected_id


class TestBuildSearchFunctionality:
    """Test build search and filtering functionality."""
    
    @pytest.fixture
    def build_browser_with_data(self, tmp_path):
        """Create a build browser with sample data."""
        browser = PublicBuildBrowser(str(tmp_path / "player_builds"))
        
        # Add multiple builds for testing
        builds_data = [
            {
                "player_name": "Player1",
                "character_name": "Char1",
                "server": "Server1",
                "faction": "rebel",
                "gcw_rank": 15,
                "professions": {"primary": "rifleman"},
                "skills": {"rifleman": ["rifle_shot"]},
                "stats": {"health": 2000},
                "armor": {"helmet": {"name": "Test Helmet", "kinetic": 40.0}},
                "tapes": [],
                "resists": {"kinetic": 35.0},
                "weapons": [{"name": "Rifle", "damage_type": "kinetic"}],
                "build_summary": "PvE rifleman build",
                "performance_metrics": {"pve_rating": 9.0},
                "tags": ["pve", "rifleman"],
                "visibility": "public",
                "rankings": ["top_dps"],
                "created_at": "2025-01-15T10:30:00",
                "updated_at": "2025-01-20T14:45:00",
                "views": 100,
                "likes": 25,
                "comments": []
            },
            {
                "player_name": "Player2",
                "character_name": "Char2",
                "server": "Server2",
                "faction": "imperial",
                "gcw_rank": 8,
                "professions": {"primary": "medic"},
                "skills": {"medic": ["heal_wound"]},
                "stats": {"health": 1800},
                "armor": {"helmet": {"name": "Medic Helmet", "kinetic": 30.0}},
                "tapes": [],
                "resists": {"kinetic": 25.0},
                "weapons": [{"name": "Pistol", "damage_type": "energy"}],
                "build_summary": "PvP medic build",
                "performance_metrics": {"pvp_rating": 8.5},
                "tags": ["pvp", "medic"],
                "visibility": "public",
                "rankings": ["popular_buff_bot"],
                "created_at": "2025-01-15T10:30:00",
                "updated_at": "2025-01-20T14:45:00",
                "views": 50,
                "likes": 15,
                "comments": []
            }
        ]
        
        for build_data in builds_data:
            browser.publish_build(build_data)
        
        return browser
    
    def test_search_by_damage_type(self, build_browser_with_data):
        """Test searching builds by damage type."""
        kinetic_builds = build_browser_with_data.search_builds(damage_type="kinetic")
        energy_builds = build_browser_with_data.search_builds(damage_type="energy")
        
        assert len(kinetic_builds) == 1
        assert len(energy_builds) == 1
        assert kinetic_builds[0].weapons[0]["damage_type"] == "kinetic"
        assert energy_builds[0].weapons[0]["damage_type"] == "energy"
    
    def test_search_by_pve_pvp_focus(self, build_browser_with_data):
        """Test searching builds by PvE/PvP focus."""
        pve_builds = build_browser_with_data.search_builds(pve_pvp="pve")
        pvp_builds = build_browser_with_data.search_builds(pve_pvp="pvp")
        
        assert len(pve_builds) == 1
        assert len(pvp_builds) == 1
        assert "pve" in pve_builds[0].tags
        assert "pvp" in pvp_builds[0].tags
    
    def test_search_by_tags(self, build_browser_with_data):
        """Test searching builds by tags."""
        rifleman_builds = build_browser_with_data.search_builds(tags=["rifleman"])
        medic_builds = build_browser_with_data.search_builds(tags=["medic"])
        
        assert len(rifleman_builds) == 1
        assert len(medic_builds) == 1
        assert "rifleman" in rifleman_builds[0].tags
        assert "medic" in medic_builds[0].tags


if __name__ == "__main__":
    pytest.main([__file__]) 
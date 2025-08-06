"""Test Batch 077 - Public Website Integration Layer.

This test suite validates the public data export functionality for SWGDB integration,
including quest tracking summaries, bot metrics, heroic readiness export, and
markdown/JSON generation for Eleventy.
"""

import json
import yaml
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from exporters.public_data_exporter import (
    PublicDataExporter,
    QuestTrackingSummary,
    BotMetrics,
    HeroicReadiness,
    create_public_data_exporter
)
from website_sync.sync_to_swgdb import (
    SWGDBSync,
    SyncStatus,
    WebsiteConfig,
    create_swgdb_sync
)


class TestPublicDataExporter:
    """Test the PublicDataExporter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.session_logs_dir = Path(self.temp_dir) / "session_logs"
        self.export_dir = Path(self.temp_dir) / "data" / "exported"
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session_logs_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test data
        self._create_test_data()
        
        # Initialize exporter
        self.exporter = PublicDataExporter(
            data_dir=str(self.data_dir),
            session_logs_dir=str(self.session_logs_dir)
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def _create_test_data(self):
        """Create test data files."""
        # Create enhanced progress tracker
        progress_data = {
            "checklists": {
                "quest_tracker": {
                    "items": [
                        {
                            "name": "Test Quest 1",
                            "status": "completed",
                            "progress": 100.0,
                            "xp_reward": 1000,
                            "credit_reward": 500,
                            "category": "general",
                            "location": "Test Planet",
                            "created_at": "2025-01-01T00:00:00",
                            "completed_at": "2025-01-02T00:00:00"
                        },
                        {
                            "name": "Test Quest 2",
                            "status": "in_progress",
                            "progress": 50.0,
                            "xp_reward": 2000,
                            "credit_reward": 1000,
                            "category": "combat",
                            "location": "Test Planet",
                            "created_at": "2025-01-03T00:00:00",
                            "completed_at": None
                        },
                        {
                            "name": "Heroic Quest 1",
                            "status": "completed",
                            "progress": 100.0,
                            "xp_reward": 5000,
                            "credit_reward": 2500,
                            "category": "heroic",
                            "location": "Heroic Planet",
                            "created_at": "2025-01-01T00:00:00",
                            "completed_at": "2025-01-05T00:00:00"
                        }
                    ]
                }
            }
        }
        
        with open(self.data_dir / "enhanced_progress_tracker.json", 'w') as f:
            json.dump(progress_data, f)
        
        # Create session logs
        session_data = {
            "session_id": "test_session_001",
            "start_time": "2025-01-01T10:00:00",
            "end_time": "2025-01-01T12:00:00",
            "character_name": "TestCharacter",
            "character_level": 80,
            "profession": "Jedi",
            "total_xp_gained": 5000,
            "total_credits_gained": 2500,
            "success_rate": 0.85,
            "efficiency_score": 0.75
        }
        
        with open(self.session_logs_dir / "session_test_001.json", 'w') as f:
            json.dump(session_data, f)
        
        # Create heroics index
        heroics_data = {
            "heroics": {
                "heroic_001": {
                    "name": "Test Heroic 1",
                    "planet": "Test Planet",
                    "level_requirement": 80,
                    "group_size": "4-8",
                    "difficulty_tiers": ["T1", "T2", "T3"]
                },
                "heroic_002": {
                    "name": "Test Heroic 2",
                    "planet": "Test Planet 2",
                    "level_requirement": 85,
                    "group_size": "4-8",
                    "difficulty_tiers": ["T1", "T2"]
                }
            }
        }
        
        heroics_dir = self.data_dir / "heroics"
        heroics_dir.mkdir(exist_ok=True)
        with open(heroics_dir / "heroics_index.yml", 'w') as f:
            yaml.dump(heroics_data, f)

    def test_export_quest_tracking_summary(self):
        """Test quest tracking summary export."""
        summary = self.exporter.export_quest_tracking_summary()
        
        assert isinstance(summary, QuestTrackingSummary)
        assert summary.total_quests == 3
        assert summary.completed_quests == 2
        assert summary.active_quests == 1
        assert summary.quest_completion_rate == pytest.approx(0.667, rel=0.01)
        assert summary.total_xp_from_quests == 6000
        assert summary.total_credits_from_quests == 3000
        assert len(summary.recent_completions) == 2
        assert "general" in summary.quest_categories
        assert "combat" in summary.quest_categories
        assert "heroic" in summary.quest_categories

    def test_export_bot_metrics(self):
        """Test bot metrics export."""
        metrics = self.exporter.export_bot_metrics()
        
        assert isinstance(metrics, BotMetrics)
        assert metrics.total_xp_gained == 5000
        assert metrics.total_credits_gained == 2500
        assert metrics.session_count == 1
        assert metrics.success_rate == 0.85
        assert metrics.efficiency_score == 0.75
        assert "Jedi" in metrics.profession_levels
        assert metrics.profession_levels["Jedi"] == 80
        assert len(metrics.recent_activity) == 1

    def test_export_heroic_readiness(self):
        """Test heroic readiness export."""
        readiness = self.exporter.export_heroic_readiness()
        
        assert isinstance(readiness, HeroicReadiness)
        assert readiness.total_heroics == 2
        assert readiness.completed_heroics == 1
        assert readiness.heroic_completion_rate == 0.5
        assert readiness.character_level == 80
        assert readiness.readiness_score == pytest.approx(0.889, rel=0.01)
        assert len(readiness.recommended_heroics) == 1

    def test_export_all_data(self):
        """Test full data export."""
        result = self.exporter.export_all_data()
        
        assert "export_metadata" in result
        assert "quest_tracking" in result
        assert "bot_metrics" in result
        assert "heroic_readiness" in result
        
        # Check that files were created
        assert (self.export_dir / "quest_tracking_summary.json").exists()
        assert (self.export_dir / "bot_metrics.json").exists()
        assert (self.export_dir / "heroic_readiness.json").exists()
        assert (self.export_dir / "public_data_export.json").exists()
        assert (self.export_dir / "public_data_summary.md").exists()

    def test_export_with_missing_data(self):
        """Test export with missing data files."""
        # Remove data files
        shutil.rmtree(self.data_dir)
        self.data_dir.mkdir()
        
        exporter = PublicDataExporter(
            data_dir=str(self.data_dir),
            session_logs_dir=str(self.session_logs_dir)
        )
        
        # Should return empty summaries
        summary = exporter.export_quest_tracking_summary()
        assert summary.total_quests == 0
        assert summary.completed_quests == 0
        
        metrics = exporter.export_bot_metrics()
        assert metrics.total_xp_gained == 0
        assert metrics.session_count == 0
        
        readiness = exporter.export_heroic_readiness()
        assert readiness.total_heroics == 0
        assert readiness.completed_heroics == 0

    def test_markdown_generation(self):
        """Test markdown summary generation."""
        self.exporter.export_all_data()
        
        md_file = self.export_dir / "public_data_summary.md"
        assert md_file.exists()
        
        with open(md_file, 'r') as f:
            content = f.read()
        
        assert "# MS11 Public Data Export" in content
        assert "Quest Tracking Summary" in content
        assert "Bot Metrics" in content
        assert "Heroic Readiness" in content
        assert "Recent Activity" in content

    def test_json_export_format(self):
        """Test JSON export format."""
        self.exporter.export_all_data()
        
        # Test quest tracking JSON
        with open(self.export_dir / "quest_tracking_summary.json", 'r') as f:
            data = json.load(f)
        
        assert "total_quests" in data
        assert "completed_quests" in data
        assert "quest_completion_rate" in data
        assert "last_updated" in data
        
        # Test bot metrics JSON
        with open(self.export_dir / "bot_metrics.json", 'r') as f:
            data = json.load(f)
        
        assert "total_xp_gained" in data
        assert "total_credits_gained" in data
        assert "profession_levels" in data
        assert "success_rate" in data

    def test_create_public_data_exporter(self):
        """Test factory function."""
        exporter = create_public_data_exporter(
            data_dir=str(self.data_dir),
            session_logs_dir=str(self.session_logs_dir)
        )
        
        assert isinstance(exporter, PublicDataExporter)
        assert exporter.data_dir == self.data_dir
        assert exporter.session_logs_dir == self.session_logs_dir


class TestSWGDBSync:
    """Test the SWGDBSync class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.export_dir = Path(self.temp_dir) / "data" / "exported"
        self.target_dir = Path(self.temp_dir) / "website_data"
        self.backup_dir = Path(self.temp_dir) / "website_backups"
        
        # Create directories
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test export files
        self._create_test_export_files()
        
        # Initialize sync
        config = WebsiteConfig(
            target_directory=str(self.target_dir),
            backup_directory=str(self.backup_dir),
            allowed_file_types=[".json", ".md"],
            max_file_size=1024 * 1024,
            sync_interval=3600,
            enable_backup=True,
            enable_validation=True
        )
        
        self.sync = SWGDBSync(config)

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def _create_test_export_files(self):
        """Create test export files."""
        test_data = {
            "test_key": "test_value",
            "timestamp": datetime.now().isoformat()
        }
        
        # Create JSON file
        with open(self.export_dir / "test_data.json", 'w') as f:
            json.dump(test_data, f)
        
        # Create markdown file
        md_content = "# Test Data\n\nThis is test content."
        with open(self.export_dir / "test_data.md", 'w') as f:
            f.write(md_content)

    def test_sync_exported_data(self):
        """Test syncing exported data."""
        status = self.sync.sync_exported_data()
        
        assert isinstance(status, SyncStatus)
        assert status.status == "success"
        assert status.success_count == 2
        assert status.failure_count == 0
        assert len(status.files_synced) == 2
        assert "test_data.json" in status.files_synced
        assert "test_data.md" in status.files_synced
        
        # Check that files were copied
        assert (self.target_dir / "test_data.json").exists()
        assert (self.target_dir / "test_data.md").exists()

    def test_sync_with_validation_errors(self):
        """Test sync with validation errors."""
        # Create invalid JSON file
        with open(self.export_dir / "invalid.json", 'w') as f:
            f.write("{ invalid json }")
        
        status = self.sync.sync_exported_data()
        
        assert status.status == "failed"
        assert status.failure_count > 0
        assert len(status.error_messages) > 0

    def test_sync_with_backup(self):
        """Test sync with backup functionality."""
        # Create initial target file
        with open(self.target_dir / "existing.json", 'w') as f:
            json.dump({"existing": "data"}, f)
        
        status = self.sync.sync_exported_data()
        
        assert status.status == "success"
        
        # Check that backup was created
        backup_dirs = list(self.backup_dir.iterdir())
        assert len(backup_dirs) > 0

    def test_sync_force_mode(self):
        """Test sync in force mode."""
        # First sync
        status1 = self.sync.sync_exported_data()
        assert status1.status == "success"
        
        # Second sync (should skip unchanged files)
        status2 = self.sync.sync_exported_data()
        assert status2.success_count == 0  # No changes
        
        # Force sync
        status3 = self.sync.sync_exported_data(force_sync=True)
        assert status3.status == "success"
        assert status3.success_count > 0

    def test_get_sync_status(self):
        """Test getting sync status."""
        # Perform a sync first
        self.sync.sync_exported_data()
        
        status = self.sync.get_sync_status()
        
        assert "export_files_count" in status
        assert "target_files_count" in status
        assert "total_syncs" in status
        assert "successful_syncs" in status
        assert "config" in status

    def test_validate_website_data(self):
        """Test website data validation."""
        # Sync some data first
        self.sync.sync_exported_data()
        
        validation = self.sync.validate_website_data()
        
        assert "timestamp" in validation
        assert "files_validated" in validation
        assert "files_valid" in validation
        assert "files_invalid" in validation
        assert validation["files_valid"] > 0

    def test_create_swgdb_sync(self):
        """Test factory function."""
        config = WebsiteConfig(
            target_directory=str(self.target_dir),
            backup_directory=str(self.backup_dir),
            allowed_file_types=[".json"],
            max_file_size=1024,
            sync_interval=1800,
            enable_backup=False,
            enable_validation=False
        )
        
        sync = create_swgdb_sync(config)
        
        assert isinstance(sync, SWGDBSync)
        assert sync.config == config


class TestIntegration:
    """Integration tests for the public website integration layer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.session_logs_dir = Path(self.temp_dir) / "session_logs"
        self.export_dir = Path(self.temp_dir) / "data" / "exported"
        self.website_dir = Path(self.temp_dir) / "website_data"
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session_logs_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.website_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test data
        self._create_integration_test_data()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def _create_integration_test_data(self):
        """Create comprehensive test data for integration testing."""
        # Create enhanced progress tracker with realistic data
        progress_data = {
            "checklists": {
                "quest_tracker": {
                    "items": [
                        {
                            "name": "Jedi Initiate Quest",
                            "status": "completed",
                            "progress": 100.0,
                            "xp_reward": 5000,
                            "credit_reward": 2500,
                            "category": "jedi",
                            "location": "Coruscant",
                            "created_at": "2025-01-01T00:00:00",
                            "completed_at": "2025-01-02T00:00:00"
                        },
                        {
                            "name": "Combat Training",
                            "status": "completed",
                            "progress": 100.0,
                            "xp_reward": 3000,
                            "credit_reward": 1500,
                            "category": "combat",
                            "location": "Naboo",
                            "created_at": "2025-01-03T00:00:00",
                            "completed_at": "2025-01-04T00:00:00"
                        },
                        {
                            "name": "Heroic: Axkva Min",
                            "status": "completed",
                            "progress": 100.0,
                            "xp_reward": 15000,
                            "credit_reward": 7500,
                            "category": "heroic",
                            "location": "Dathomir",
                            "created_at": "2025-01-05T00:00:00",
                            "completed_at": "2025-01-06T00:00:00"
                        },
                        {
                            "name": "Crafting Mastery",
                            "status": "in_progress",
                            "progress": 75.0,
                            "xp_reward": 8000,
                            "credit_reward": 4000,
                            "category": "crafting",
                            "location": "Corellia",
                            "created_at": "2025-01-07T00:00:00",
                            "completed_at": None
                        }
                    ]
                }
            }
        }
        
        with open(self.data_dir / "enhanced_progress_tracker.json", 'w') as f:
            json.dump(progress_data, f)
        
        # Create multiple session logs
        sessions = [
            {
                "session_id": "session_001",
                "start_time": "2025-01-01T10:00:00",
                "end_time": "2025-01-01T12:00:00",
                "character_name": "TestJedi",
                "character_level": 80,
                "profession": "Jedi",
                "total_xp_gained": 5000,
                "total_credits_gained": 2500,
                "success_rate": 0.85,
                "efficiency_score": 0.75
            },
            {
                "session_id": "session_002",
                "start_time": "2025-01-02T14:00:00",
                "end_time": "2025-01-02T16:00:00",
                "character_name": "TestJedi",
                "character_level": 82,
                "profession": "Jedi",
                "total_xp_gained": 8000,
                "total_credits_gained": 4000,
                "success_rate": 0.90,
                "efficiency_score": 0.82
            }
        ]
        
        for i, session in enumerate(sessions):
            with open(self.session_logs_dir / f"session_{i+1:03d}.json", 'w') as f:
                json.dump(session, f)
        
        # Create heroics index
        heroics_data = {
            "heroics": {
                "axkva_min": {
                    "name": "Heroic: Axkva Min",
                    "planet": "Dathomir",
                    "level_requirement": 80,
                    "group_size": "4-8",
                    "difficulty_tiers": ["T1", "T2", "T3"]
                },
                "nightsister_ritual": {
                    "name": "Heroic: Nightsister Ritual",
                    "planet": "Dathomir",
                    "level_requirement": 85,
                    "group_size": "4-8",
                    "difficulty_tiers": ["T1", "T2"]
                },
                "jedi_trials": {
                    "name": "Heroic: Jedi Trials",
                    "planet": "Coruscant",
                    "level_requirement": 90,
                    "group_size": "4-8",
                    "difficulty_tiers": ["T1", "T2", "T3", "T4"]
                }
            }
        }
        
        heroics_dir = self.data_dir / "heroics"
        heroics_dir.mkdir(exist_ok=True)
        with open(heroics_dir / "heroics_index.yml", 'w') as f:
            yaml.dump(heroics_data, f)

    def test_full_integration_workflow(self):
        """Test the complete integration workflow."""
        # Step 1: Export data
        exporter = PublicDataExporter(
            data_dir=str(self.data_dir),
            session_logs_dir=str(self.session_logs_dir)
        )
        
        export_result = exporter.export_all_data()
        assert "export_metadata" in export_result
        assert "quest_tracking" in export_result
        assert "bot_metrics" in export_result
        assert "heroic_readiness" in export_result
        
        # Step 2: Sync to website
        config = WebsiteConfig(
            target_directory=str(self.website_dir),
            backup_directory=str(self.temp_dir) / "backups",
            allowed_file_types=[".json", ".md"],
            max_file_size=1024 * 1024,
            sync_interval=3600,
            enable_backup=True,
            enable_validation=True
        )
        
        sync = SWGDBSync(config)
        sync_status = sync.sync_exported_data()
        
        assert sync_status.status == "success"
        assert sync_status.success_count > 0
        
        # Step 3: Validate website data
        validation = sync.validate_website_data()
        assert validation["files_valid"] > 0
        assert validation["files_invalid"] == 0
        
        # Step 4: Check sync status
        status = sync.get_sync_status()
        assert status["successful_syncs"] > 0
        assert status["target_files_count"] > 0

    def test_data_consistency(self):
        """Test data consistency across export and sync."""
        # Export data
        exporter = PublicDataExporter(
            data_dir=str(self.data_dir),
            session_logs_dir=str(self.session_logs_dir)
        )
        
        export_result = exporter.export_all_data()
        
        # Verify quest tracking data
        quest_data = export_result["quest_tracking"]
        assert quest_data["total_quests"] == 4
        assert quest_data["completed_quests"] == 3
        assert quest_data["quest_completion_rate"] == 0.75
        
        # Verify bot metrics data
        metrics_data = export_result["bot_metrics"]
        assert metrics_data["total_xp_gained"] == 13000
        assert metrics_data["session_count"] == 2
        assert metrics_data["profession_levels"]["Jedi"] == 82
        
        # Verify heroic readiness data
        readiness_data = export_result["heroic_readiness"]
        assert readiness_data["total_heroics"] == 3
        assert readiness_data["completed_heroics"] == 1
        assert readiness_data["heroic_completion_rate"] == pytest.approx(0.333, rel=0.01)

    def test_markdown_content_quality(self):
        """Test the quality of generated markdown content."""
        exporter = PublicDataExporter(
            data_dir=str(self.data_dir),
            session_logs_dir=str(self.session_logs_dir)
        )
        
        exporter.export_all_data()
        
        md_file = self.export_dir / "public_data_summary.md"
        assert md_file.exists()
        
        with open(md_file, 'r') as f:
            content = f.read()
        
        # Check for required sections
        assert "# MS11 Public Data Export" in content
        assert "## Quest Tracking Summary" in content
        assert "## Bot Metrics" in content
        assert "## Heroic Readiness" in content
        assert "## Recent Activity" in content
        
        # Check for specific data
        assert "Total Quests: 4" in content
        assert "Completed: 3" in content
        assert "Completion Rate: 75.0%" in content
        assert "Total XP Gained: 13,000" in content

    def test_json_structure_validation(self):
        """Test JSON structure validation."""
        exporter = PublicDataExporter(
            data_dir=str(self.data_dir),
            session_logs_dir=str(self.session_logs_dir)
        )
        
        exporter.export_all_data()
        
        # Validate quest tracking JSON
        with open(self.export_dir / "quest_tracking_summary.json", 'r') as f:
            quest_data = json.load(f)
        
        required_fields = [
            "total_quests", "completed_quests", "active_quests",
            "quest_completion_rate", "total_xp_from_quests",
            "total_credits_from_quests", "recent_completions",
            "quest_categories", "last_updated"
        ]
        
        for field in required_fields:
            assert field in quest_data
        
        # Validate bot metrics JSON
        with open(self.export_dir / "bot_metrics.json", 'r') as f:
            metrics_data = json.load(f)
        
        required_fields = [
            "total_xp_gained", "total_credits_gained", "profession_levels",
            "session_count", "total_session_time", "average_session_duration",
            "success_rate", "efficiency_score", "recent_activity", "last_updated"
        ]
        
        for field in required_fields:
            assert field in metrics_data

    def test_error_handling(self):
        """Test error handling in the integration workflow."""
        # Test with corrupted data
        with open(self.data_dir / "enhanced_progress_tracker.json", 'w') as f:
            f.write("{ invalid json }")
        
        exporter = PublicDataExporter(
            data_dir=str(self.data_dir),
            session_logs_dir=str(self.session_logs_dir)
        )
        
        # Should handle errors gracefully
        summary = exporter.export_quest_tracking_summary()
        assert summary.total_quests == 0
        assert summary.completed_quests == 0
        
        # Test sync with invalid files
        config = WebsiteConfig(
            target_directory=str(self.website_dir),
            backup_directory=str(self.temp_dir) / "backups",
            allowed_file_types=[".json"],
            max_file_size=1024,
            sync_interval=3600,
            enable_backup=False,
            enable_validation=True
        )
        
        sync = SWGDBSync(config)
        status = sync.sync_exported_data()
        
        # Should report validation errors
        assert status.status == "failed"
        assert len(status.error_messages) > 0


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 
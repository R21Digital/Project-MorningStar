#!/usr/bin/env python3
"""MS11 Batch 082 - Public SWGDB Mods/Addons Section Test Suite

This test suite validates all components of the mods section implementation:
- Mods manager functionality
- Upload handling and validation
- SWGDB integration
- Website interface
- Statistics and reporting
"""

import unittest
import tempfile
import json
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from core.mods import ModsManager, create_mods_manager, ModUpload, ModCategory, ValidationResult
from core.mods.swgdb_integration import ModsSWGDBIntegration, create_mods_swgdb_integration, ModsSyncData


class TestModsManager(unittest.TestCase):
    """Test the ModsManager class."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "test_mods_config.json"
        self.create_test_config()
        
        self.mods_manager = ModsManager(str(self.config_file))

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_config(self):
        """Create a test configuration file."""
        config = {
            "mods_section": {
                "enabled": True,
                "version": "1.0",
                "section_title": "Test Mods Section",
                "section_description": "Test mods section"
            },
            "categories": {
                "ui_skins": {
                    "name": "UI Skins",
                    "description": "Test UI skins",
                    "icon": "🎨",
                    "enabled": True,
                    "file_types": [".zip", ".rar"],
                    "max_file_size": 50 * 1024 * 1024,
                    "required_files": ["README.md"],
                    "optional_files": ["preview.png"],
                    "subcategories": ["dark_themes", "light_themes"],
                    "validation_rules": {
                        "check_archive_integrity": True,
                        "validate_readme": True
                    }
                },
                "macro_packs": {
                    "name": "Macro Packs",
                    "description": "Test macro packs",
                    "icon": "⚡",
                    "enabled": True,
                    "file_types": [".txt", ".json"],
                    "max_file_size": 10 * 1024 * 1024,
                    "required_files": ["macros.txt"],
                    "optional_files": ["config.json"],
                    "subcategories": ["combat_macros", "utility_macros"],
                    "validation_rules": {
                        "validate_macro_syntax": True,
                        "check_for_malicious_commands": True
                    }
                }
            },
            "upload_settings": {
                "enabled": True,
                "max_uploads_per_user": 10,
                "max_uploads_per_day": 50
            },
            "validation_settings": {
                "enabled": True,
                "auto_validation": True
            },
            "hosting_settings": {
                "storage_path": str(self.temp_dir / "storage"),
                "backup_path": str(self.temp_dir / "backup")
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def test_initialization(self):
        """Test mods manager initialization."""
        self.assertIsNotNone(self.mods_manager)
        self.assertEqual(len(self.mods_manager.categories), 2)
        self.assertTrue("ui_skins" in self.mods_manager.categories)
        self.assertTrue("macro_packs" in self.mods_manager.categories)

    def test_category_loading(self):
        """Test category loading from config."""
        ui_skins = self.mods_manager.categories["ui_skins"]
        self.assertEqual(ui_skins.name, "UI Skins")
        self.assertEqual(ui_skins.description, "Test UI skins")
        self.assertEqual(ui_skins.icon, "🎨")
        self.assertTrue(ui_skins.enabled)
        self.assertIn(".zip", ui_skins.file_types)

    def test_upload_mod_success(self):
        """Test successful mod upload."""
        # Create test file
        test_file = self.temp_dir / "test_ui.zip"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        metadata = {
            "title": "Test UI Skin",
            "description": "A test UI skin for demonstration",
            "category": "ui_skins",
            "subcategory": "dark_themes",
            "version": "1.0",
            "tags": ["test", "ui"],
            "compatibility": {"swg_versions": ["SWGEmu"]}
        }
        
        success, message, upload_id = self.mods_manager.upload_mod(
            str(test_file), metadata, "test_author"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(upload_id)
        self.assertIn(upload_id, self.mods_manager.uploads)

    def test_upload_mod_invalid_category(self):
        """Test upload with invalid category."""
        test_file = self.temp_dir / "test.zip"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        metadata = {
            "title": "Test Mod",
            "description": "Test description",
            "category": "invalid_category",
            "version": "1.0"
        }
        
        success, message, upload_id = self.mods_manager.upload_mod(
            str(test_file), metadata, "test_author"
        )
        
        self.assertFalse(success)
        self.assertIn("Invalid category", message)

    def test_upload_mod_file_not_found(self):
        """Test upload with non-existent file."""
        metadata = {
            "title": "Test Mod",
            "description": "Test description",
            "category": "ui_skins",
            "version": "1.0"
        }
        
        success, message, upload_id = self.mods_manager.upload_mod(
            "non_existent_file.zip", metadata, "test_author"
        )
        
        self.assertFalse(success)
        self.assertIn("File not found", message)

    def test_get_mods_by_category(self):
        """Test getting mods by category."""
        # Create test uploads
        test_file = self.temp_dir / "test.zip"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        metadata = {
            "title": "Test Mod",
            "description": "Test description",
            "category": "ui_skins",
            "version": "1.0"
        }
        
        success, message, upload_id = self.mods_manager.upload_mod(
            str(test_file), metadata, "test_author"
        )
        
        if success:
            self.mods_manager.update_mod_status(upload_id, "approved")
            mods = self.mods_manager.get_mods_by_category("ui_skins")
            self.assertEqual(len(mods), 1)
            self.assertEqual(mods[0].upload_id, upload_id)

    def test_search_mods(self):
        """Test mod search functionality."""
        # Create test upload
        test_file = self.temp_dir / "test.zip"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        metadata = {
            "title": "Combat Macro Pack",
            "description": "A collection of combat macros",
            "category": "macro_packs",
            "version": "1.0",
            "tags": ["combat", "macros"]
        }
        
        success, message, upload_id = self.mods_manager.upload_mod(
            str(test_file), metadata, "test_author"
        )
        
        if success:
            self.mods_manager.update_mod_status(upload_id, "approved")
            
            # Test search
            results = self.mods_manager.search_mods("combat")
            self.assertEqual(len(results), 1)
            
            results = self.mods_manager.search_mods("nonexistent")
            self.assertEqual(len(results), 0)

    def test_get_mods_statistics(self):
        """Test statistics generation."""
        stats = self.mods_manager.get_mods_statistics()
        
        self.assertIn("total_uploads", stats)
        self.assertIn("approved_uploads", stats)
        self.assertIn("pending_uploads", stats)
        self.assertIn("rejected_uploads", stats)
        self.assertIn("category_stats", stats)
        self.assertIn("total_downloads", stats)
        self.assertIn("total_views", stats)
        self.assertIn("average_rating", stats)

    def test_increment_counts(self):
        """Test download and view count increments."""
        # Create test upload
        test_file = self.temp_dir / "test.zip"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        metadata = {
            "title": "Test Mod",
            "description": "Test description",
            "category": "ui_skins",
            "version": "1.0"
        }
        
        success, message, upload_id = self.mods_manager.upload_mod(
            str(test_file), metadata, "test_author"
        )
        
        if success:
            # Test increment functions
            self.assertTrue(self.mods_manager.increment_download_count(upload_id))
            self.assertTrue(self.mods_manager.increment_view_count(upload_id))
            
            upload = self.mods_manager.get_mod_by_id(upload_id)
            self.assertEqual(upload.download_count, 1)
            self.assertEqual(upload.view_count, 1)

    def test_rate_mod(self):
        """Test mod rating functionality."""
        # Create test upload
        test_file = self.temp_dir / "test.zip"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        metadata = {
            "title": "Test Mod",
            "description": "Test description",
            "category": "ui_skins",
            "version": "1.0"
        }
        
        success, message, upload_id = self.mods_manager.upload_mod(
            str(test_file), metadata, "test_author"
        )
        
        if success:
            # Test rating
            self.assertTrue(self.mods_manager.rate_mod(upload_id, 4.5, "test_user"))
            
            # Test invalid rating
            self.assertFalse(self.mods_manager.rate_mod(upload_id, 6.0, "test_user"))
            self.assertFalse(self.mods_manager.rate_mod(upload_id, 0.0, "test_user"))

    def test_update_mod_status(self):
        """Test mod status updates."""
        # Create test upload
        test_file = self.temp_dir / "test.zip"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        metadata = {
            "title": "Test Mod",
            "description": "Test description",
            "category": "ui_skins",
            "version": "1.0"
        }
        
        success, message, upload_id = self.mods_manager.upload_mod(
            str(test_file), metadata, "test_author"
        )
        
        if success:
            # Test status update
            self.assertTrue(self.mods_manager.update_mod_status(upload_id, "approved"))
            upload = self.mods_manager.get_mod_by_id(upload_id)
            self.assertEqual(upload.status, "approved")
            
            # Test with notes
            self.assertTrue(self.mods_manager.update_mod_status(upload_id, "rejected", "Test notes"))
            upload = self.mods_manager.get_mod_by_id(upload_id)
            self.assertEqual(upload.status, "rejected")
            self.assertEqual(upload.moderation_notes, "Test notes")

    def test_cleanup_old_uploads(self):
        """Test cleanup of old uploads."""
        # Create test upload
        test_file = self.temp_dir / "test.zip"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        metadata = {
            "title": "Test Mod",
            "description": "Test description",
            "category": "ui_skins",
            "version": "1.0"
        }
        
        success, message, upload_id = self.mods_manager.upload_mod(
            str(test_file), metadata, "test_author"
        )
        
        if success:
            # Test cleanup
            removed_count = self.mods_manager.cleanup_old_uploads(days_to_keep=0)
            self.assertGreaterEqual(removed_count, 0)


class TestModsSWGDBIntegration(unittest.TestCase):
    """Test the ModsSWGDBIntegration class."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "test_mods_config.json"
        self.create_test_config()
        
        self.mods_manager = ModsManager(str(self.config_file))
        self.integration = ModsSWGDBIntegration(self.mods_manager)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_config(self):
        """Create a test configuration file."""
        config = {
            "mods_section": {
                "enabled": True,
                "version": "1.0"
            },
            "categories": {
                "ui_skins": {
                    "name": "UI Skins",
                    "description": "Test UI skins",
                    "icon": "🎨",
                    "enabled": True,
                    "file_types": [".zip"],
                    "max_file_size": 50 * 1024 * 1024,
                    "required_files": ["README.md"],
                    "optional_files": [],
                    "subcategories": ["dark_themes"],
                    "validation_rules": {}
                }
            },
            "hosting_settings": {
                "storage_path": str(self.temp_dir / "storage"),
                "backup_path": str(self.temp_dir / "backup")
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def test_initialization(self):
        """Test integration initialization."""
        self.assertIsNotNone(self.integration)
        self.assertEqual(self.integration.mods_manager, self.mods_manager)
        self.assertIsNotNone(self.integration.swgdb_sync)

    def test_sync_mods_to_swgdb(self):
        """Test syncing mods to SWGDB."""
        # Create test upload
        test_file = self.temp_dir / "test.zip"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        metadata = {
            "title": "Test Mod",
            "description": "Test description",
            "category": "ui_skins",
            "version": "1.0"
        }
        
        success, message, upload_id = self.mods_manager.upload_mod(
            str(test_file), metadata, "test_author"
        )
        
        if success:
            self.mods_manager.update_mod_status(upload_id, "approved")
            
            # Test sync
            sync_result = self.integration.sync_mods_to_swgdb(force_sync=True)
            
            self.assertIsInstance(sync_result, ModsSyncData)
            self.assertIsNotNone(sync_result.sync_id)
            self.assertIsNotNone(sync_result.timestamp)
            self.assertGreaterEqual(sync_result.total_mods, 0)

    def test_get_sync_status(self):
        """Test getting sync status."""
        status = self.integration.get_sync_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("mods_statistics", status)
        self.assertIn("swgdb_sync_status", status)
        self.assertIn("last_sync", status)

    def test_validate_mods_data(self):
        """Test mods data validation."""
        validation = self.integration.validate_mods_data()
        
        self.assertIsInstance(validation, dict)
        self.assertIn("timestamp", validation)
        self.assertIn("total_mods", validation)
        self.assertIn("valid_mods", validation)
        self.assertIn("invalid_mods", validation)
        self.assertIn("errors", validation)

    def test_cleanup_old_exports(self):
        """Test cleanup of old exports."""
        removed_count = self.integration.cleanup_old_exports(days_to_keep=7)
        self.assertIsInstance(removed_count, int)
        self.assertGreaterEqual(removed_count, 0)


class TestModUpload(unittest.TestCase):
    """Test the ModUpload dataclass."""

    def test_mod_upload_creation(self):
        """Test ModUpload creation."""
        upload = ModUpload(
            upload_id="test_123",
            title="Test Mod",
            description="Test description",
            category="ui_skins",
            subcategory="dark_themes",
            author="test_author",
            version="1.0",
            file_path="/path/to/file.zip",
            file_size=1024,
            file_hash="abc123",
            upload_date="2025-01-27T00:00:00",
            status="pending",
            rating=0.0,
            download_count=0,
            view_count=0,
            compatibility={},
            tags=["test"],
            preview_image=None,
            readme_content=None,
            validation_errors=[],
            moderation_notes=None
        )
        
        self.assertEqual(upload.upload_id, "test_123")
        self.assertEqual(upload.title, "Test Mod")
        self.assertEqual(upload.category, "ui_skins")
        self.assertEqual(upload.status, "pending")


class TestModCategory(unittest.TestCase):
    """Test the ModCategory dataclass."""

    def test_mod_category_creation(self):
        """Test ModCategory creation."""
        category = ModCategory(
            name="UI Skins",
            description="Test UI skins",
            icon="🎨",
            enabled=True,
            file_types=[".zip", ".rar"],
            max_file_size=50 * 1024 * 1024,
            required_files=["README.md"],
            optional_files=["preview.png"],
            subcategories=["dark_themes", "light_themes"],
            validation_rules={"check_archive_integrity": True}
        )
        
        self.assertEqual(category.name, "UI Skins")
        self.assertEqual(category.icon, "🎨")
        self.assertTrue(category.enabled)
        self.assertIn(".zip", category.file_types)


class TestValidationResult(unittest.TestCase):
    """Test the ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult(
            upload_id="test_123",
            timestamp="2025-01-27T00:00:00",
            is_valid=True,
            errors=[],
            warnings=[],
            validation_duration=1.5,
            file_integrity_check=True,
            malware_scan_result=None,
            metadata_validation=True,
            preview_image_valid=True,
            readme_valid=True
        )
        
        self.assertEqual(result.upload_id, "test_123")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.validation_duration, 1.5)


class TestIntegration(unittest.TestCase):
    """Integration tests for the mods section."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "test_mods_config.json"
        self.create_test_config()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_config(self):
        """Create a test configuration file."""
        config = {
            "mods_section": {
                "enabled": True,
                "version": "1.0"
            },
            "categories": {
                "ui_skins": {
                    "name": "UI Skins",
                    "description": "Test UI skins",
                    "icon": "🎨",
                    "enabled": True,
                    "file_types": [".zip"],
                    "max_file_size": 50 * 1024 * 1024,
                    "required_files": ["README.md"],
                    "optional_files": [],
                    "subcategories": ["dark_themes"],
                    "validation_rules": {}
                }
            },
            "hosting_settings": {
                "storage_path": str(self.temp_dir / "storage"),
                "backup_path": str(self.temp_dir / "backup")
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def test_full_workflow(self):
        """Test the complete mods workflow."""
        # Initialize components
        mods_manager = ModsManager(str(self.config_file))
        integration = ModsSWGDBIntegration(mods_manager)
        
        # Create test file
        test_file = self.temp_dir / "test.zip"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Upload mod
        metadata = {
            "title": "Test Mod",
            "description": "Test description",
            "category": "ui_skins",
            "version": "1.0",
            "tags": ["test"]
        }
        
        success, message, upload_id = mods_manager.upload_mod(
            str(test_file), metadata, "test_author"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(upload_id)
        
        # Update status
        self.assertTrue(mods_manager.update_mod_status(upload_id, "approved"))
        
        # Test statistics
        stats = mods_manager.get_mods_statistics()
        self.assertEqual(stats["total_uploads"], 1)
        self.assertEqual(stats["approved_uploads"], 1)
        
        # Test sync
        sync_result = integration.sync_mods_to_swgdb(force_sync=True)
        self.assertIsInstance(sync_result, ModsSyncData)
        self.assertEqual(sync_result.total_mods, 1)
        self.assertEqual(sync_result.approved_mods, 1)

    def test_error_handling(self):
        """Test error handling in the workflow."""
        mods_manager = ModsManager(str(self.config_file))
        
        # Test upload with invalid data
        success, message, upload_id = mods_manager.upload_mod(
            "non_existent_file.zip",
            {"title": "Test", "category": "invalid_category"},
            "test_author"
        )
        
        self.assertFalse(success)
        self.assertIn("File not found", message)

    def test_configuration_loading(self):
        """Test configuration loading and validation."""
        # Test with valid config
        mods_manager = ModsManager(str(self.config_file))
        self.assertIsNotNone(mods_manager.config)
        self.assertTrue(mods_manager.config["mods_section"]["enabled"])
        
        # Test with missing config file
        with patch('pathlib.Path.exists', return_value=False):
            mods_manager = ModsManager("non_existent_config.json")
            self.assertIsNotNone(mods_manager.config)  # Should use default config


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestModsManager,
        TestModsSWGDBIntegration,
        TestModUpload,
        TestModCategory,
        TestValidationResult,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 
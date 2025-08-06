#!/usr/bin/env python3
"""
Test suite for Batch 108 - Mods & Plugin Hub (Public)

This test suite covers:
- Mod submission and approval workflow
- Category management
- File upload and storage
- Public browsing and downloading
- Admin approval system
- Rating and review system
"""

import pytest
import tempfile
import shutil
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from core.mods_hub_manager import (
    ModsHubManager,
    ModSubmission,
    ModCategory,
    ModType,
    ModStatus,
    ModCategoryInfo
)


class TestModsHubManager:
    """Test the ModsHubManager class."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        temp_dir = tempfile.mkdtemp()
        mods_dir = os.path.join(temp_dir, "data", "mods")
        uploads_dir = os.path.join(temp_dir, "uploads", "mods")
        config_file = os.path.join(temp_dir, "data", "mods_config.json")
        
        os.makedirs(mods_dir, exist_ok=True)
        os.makedirs(uploads_dir, exist_ok=True)
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        yield {
            'temp_dir': temp_dir,
            'mods_dir': mods_dir,
            'uploads_dir': uploads_dir,
            'config_file': config_file
        }
        
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def manager(self, temp_dirs):
        """Create a ModsHubManager instance for testing."""
        return ModsHubManager(
            mods_dir=temp_dirs['mods_dir'],
            uploads_dir=temp_dirs['uploads_dir'],
            config_file=temp_dirs['config_file']
        )
    
    @pytest.fixture
    def sample_mod_data(self):
        """Sample mod data for testing."""
        return {
            "title": "Test Mod",
            "description": "A test mod for unit testing",
            "category": ModCategory.UI_ENHANCEMENTS,
            "mod_type": ModType.FILE,
            "author": "TestAuthor",
            "author_email": "test@example.com",
            "version": "1.0.0",
            "swg_version": "NGE",
            "tags": ["test", "ui", "demo"],
            "dependencies": ["SWG Base Client"],
            "installation_notes": "Test installation notes",
            "changelog": "v1.0.0 - Initial release"
        }
    
    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager.mods_dir.exists()
        assert manager.uploads_dir.exists()
        assert len(manager.categories) > 0
        assert len(manager.mods) == 0
    
    def test_submit_mod(self, manager, sample_mod_data):
        """Test mod submission."""
        mod_id = manager.submit_mod(**sample_mod_data)
        
        assert mod_id is not None
        assert mod_id in manager.mods
        
        mod = manager.mods[mod_id]
        assert mod.title == sample_mod_data["title"]
        assert mod.author == sample_mod_data["author"]
        assert mod.status == ModStatus.PENDING
    
    def test_submit_mod_with_file(self, manager, temp_dirs):
        """Test mod submission with file upload."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test mod content")
            temp_file_path = f.name
        
        try:
            mod_id = manager.submit_mod(
                title="Test File Mod",
                description="A test mod with file",
                category=ModCategory.UTILITIES,
                mod_type=ModType.FILE,
                author="TestAuthor",
                file_path=temp_file_path
            )
            
            mod = manager.mods[mod_id]
            assert mod.file_path is not None
            assert mod.file_size is not None
            assert mod.file_size > 0
            
        finally:
            os.unlink(temp_file_path)
    
    def test_submit_mod_with_content(self, manager):
        """Test mod submission with text content."""
        mod_id = manager.submit_mod(
            title="Test Content Mod",
            description="A test mod with content",
            category=ModCategory.MACROS_KEYBINDS,
            mod_type=ModType.TEXT,
            author="TestAuthor",
            content="Test mod content"
        )
        
        mod = manager.mods[mod_id]
        assert mod.content == "Test mod content"
    
    def test_submit_mod_with_link(self, manager):
        """Test mod submission with external link."""
        mod_id = manager.submit_mod(
            title="Test Link Mod",
            description="A test mod with link",
            category=ModCategory.UTILITIES,
            mod_type=ModType.LINK,
            author="TestAuthor",
            download_url="https://example.com/test-mod.zip"
        )
        
        mod = manager.mods[mod_id]
        assert mod.download_url == "https://example.com/test-mod.zip"
    
    def test_approve_mod(self, manager, sample_mod_data):
        """Test mod approval."""
        mod_id = manager.submit_mod(**sample_mod_data)
        
        success = manager.approve_mod(mod_id, "test_admin")
        
        assert success
        mod = manager.mods[mod_id]
        assert mod.status == ModStatus.APPROVED
        assert mod.approved_by == "test_admin"
        assert mod.approved_at is not None
    
    def test_reject_mod(self, manager, sample_mod_data):
        """Test mod rejection."""
        mod_id = manager.submit_mod(**sample_mod_data)
        
        success = manager.approve_mod(mod_id, "test_admin", "Test rejection reason")
        
        assert success
        mod = manager.mods[mod_id]
        assert mod.status == ModStatus.REJECTED
        assert mod.rejection_reason == "Test rejection reason"
    
    def test_get_mod(self, manager, sample_mod_data):
        """Test getting a specific mod."""
        mod_id = manager.submit_mod(**sample_mod_data)
        
        mod = manager.get_mod(mod_id)
        assert mod is not None
        assert mod.title == sample_mod_data["title"]
    
    def test_get_mods_filtering(self, manager):
        """Test mod filtering functionality."""
        # Submit multiple mods
        mod1_id = manager.submit_mod(
            title="UI Mod",
            description="UI enhancement",
            category=ModCategory.UI_ENHANCEMENTS,
            mod_type=ModType.FILE,
            author="Author1"
        )
        
        mod2_id = manager.submit_mod(
            title="Combat Mod",
            description="Combat enhancement",
            category=ModCategory.UTILITIES,
            mod_type=ModType.TEXT,
            author="Author2"
        )
        
        # Approve both mods
        manager.approve_mod(mod1_id, "admin")
        manager.approve_mod(mod2_id, "admin")
        
        # Test category filtering
        ui_mods = manager.get_mods(category=ModCategory.UI_ENHANCEMENTS)
        assert len(ui_mods) == 1
        assert ui_mods[0].category == ModCategory.UI_ENHANCEMENTS
        
        # Test author filtering
        author1_mods = manager.get_mods(author="Author1")
        assert len(author1_mods) == 1
        assert author1_mods[0].author == "Author1"
        
        # Test search filtering
        search_results = manager.get_mods(search="enhancement")
        assert len(search_results) == 2  # Both contain "enhancement"
    
    def test_get_approved_mods(self, manager):
        """Test getting approved mods."""
        # Submit and approve a mod
        mod_id = manager.submit_mod(
            title="Test Mod",
            description="Test description",
            category=ModCategory.UTILITIES,
            mod_type=ModType.FILE,
            author="TestAuthor"
        )
        
        manager.approve_mod(mod_id, "admin")
        
        approved_mods = manager.get_approved_mods()
        assert len(approved_mods) == 1
        assert approved_mods[0].status == ModStatus.APPROVED
    
    def test_get_pending_mods(self, manager):
        """Test getting pending mods."""
        # Submit a mod (should be pending by default)
        mod_id = manager.submit_mod(
            title="Test Mod",
            description="Test description",
            category=ModCategory.UTILITIES,
            mod_type=ModType.FILE,
            author="TestAuthor"
        )
        
        pending_mods = manager.get_pending_mods()
        assert len(pending_mods) == 1
        assert pending_mods[0].status == ModStatus.PENDING
    
    def test_increment_views(self, manager, sample_mod_data):
        """Test view count increment."""
        mod_id = manager.submit_mod(**sample_mod_data)
        
        initial_views = manager.mods[mod_id].views
        success = manager.increment_views(mod_id)
        
        assert success
        assert manager.mods[mod_id].views == initial_views + 1
    
    def test_increment_downloads(self, manager, sample_mod_data):
        """Test download count increment."""
        mod_id = manager.submit_mod(**sample_mod_data)
        
        initial_downloads = manager.mods[mod_id].downloads
        success = manager.increment_downloads(mod_id)
        
        assert success
        assert manager.mods[mod_id].downloads == initial_downloads + 1
    
    def test_rate_mod(self, manager, sample_mod_data):
        """Test mod rating."""
        mod_id = manager.submit_mod(**sample_mod_data)
        
        # Rate the mod
        success = manager.rate_mod(mod_id, 4.5, "user1")
        assert success
        
        mod = manager.mods[mod_id]
        assert mod.rating == 4.5
        assert mod.rating_count == 1
        
        # Rate again
        success = manager.rate_mod(mod_id, 5.0, "user2")
        assert success
        
        mod = manager.mods[mod_id]
        assert mod.rating == 4.75  # Average of 4.5 and 5.0
        assert mod.rating_count == 2
    
    def test_get_categories(self, manager):
        """Test getting categories."""
        categories = manager.get_categories()
        
        assert len(categories) > 0
        for cat_id, cat_info in categories.items():
            assert isinstance(cat_info, ModCategoryInfo)
            assert cat_info.id == cat_id
            assert cat_info.name is not None
            assert cat_info.description is not None
    
    def test_get_popular_mods(self, manager):
        """Test getting popular mods."""
        # Submit and approve multiple mods with different popularity
        mod1_id = manager.submit_mod(
            title="Popular Mod",
            description="Very popular",
            category=ModCategory.UTILITIES,
            mod_type=ModType.FILE,
            author="Author1"
        )
        manager.approve_mod(mod1_id, "admin")
        manager.mods[mod1_id].downloads = 100
        manager.mods[mod1_id].views = 1000
        
        mod2_id = manager.submit_mod(
            title="Less Popular Mod",
            description="Less popular",
            category=ModCategory.UTILITIES,
            mod_type=ModType.FILE,
            author="Author2"
        )
        manager.approve_mod(mod2_id, "admin")
        manager.mods[mod2_id].downloads = 10
        manager.mods[mod2_id].views = 100
        
        popular_mods = manager.get_popular_mods(limit=2)
        assert len(popular_mods) == 2
        assert popular_mods[0].title == "Popular Mod"  # Should be first
    
    def test_get_recent_mods(self, manager):
        """Test getting recent mods."""
        # Submit and approve multiple mods
        mod1_id = manager.submit_mod(
            title="Recent Mod",
            description="Most recent",
            category=ModCategory.UTILITIES,
            mod_type=ModType.FILE,
            author="Author1"
        )
        manager.approve_mod(mod1_id, "admin")
        
        mod2_id = manager.submit_mod(
            title="Older Mod",
            description="Older mod",
            category=ModCategory.UTILITIES,
            mod_type=ModType.FILE,
            author="Author2"
        )
        manager.approve_mod(mod2_id, "admin")
        
        recent_mods = manager.get_recent_mods(limit=2)
        assert len(recent_mods) == 2
        assert recent_mods[0].title == "Recent Mod"  # Should be first
    
    def test_get_featured_mods(self, manager):
        """Test getting featured mods."""
        # Submit and approve a mod
        mod_id = manager.submit_mod(
            title="Featured Mod",
            description="Featured mod",
            category=ModCategory.UTILITIES,
            mod_type=ModType.FILE,
            author="Author1"
        )
        manager.approve_mod(mod_id, "admin")
        
        # Set as featured
        success = manager.set_featured(mod_id, True)
        assert success
        
        featured_mods = manager.get_featured_mods()
        assert len(featured_mods) == 1
        assert featured_mods[0].featured is True
    
    def test_set_featured(self, manager, sample_mod_data):
        """Test setting mod as featured."""
        mod_id = manager.submit_mod(**sample_mod_data)
        
        # Set as featured
        success = manager.set_featured(mod_id, True)
        assert success
        assert manager.mods[mod_id].featured is True
        
        # Unfeature
        success = manager.set_featured(mod_id, False)
        assert success
        assert manager.mods[mod_id].featured is False
    
    def test_delete_mod(self, manager, sample_mod_data):
        """Test mod deletion."""
        mod_id = manager.submit_mod(**sample_mod_data)
        
        # Add a file to the mod
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_file_path = f.name
        
        try:
            manager.mods[mod_id].file_path = temp_file_path
            
            # Delete the mod
            success = manager.delete_mod(mod_id)
            assert success
            assert mod_id not in manager.mods
            
            # Check that file was deleted
            assert not os.path.exists(temp_file_path)
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_get_stats(self, manager):
        """Test getting hub statistics."""
        # Submit and approve a mod
        mod_id = manager.submit_mod(
            title="Test Mod",
            description="Test description",
            category=ModCategory.UTILITIES,
            mod_type=ModType.FILE,
            author="TestAuthor"
        )
        manager.approve_mod(mod_id, "admin")
        
        stats = manager.get_stats()
        
        assert stats['total_mods'] == 1
        assert stats['approved_mods'] == 1
        assert stats['pending_mods'] == 0
        assert stats['featured_mods'] == 0
        assert 'category_breakdown' in stats
    
    def test_validate_file_upload(self, manager):
        """Test file upload validation."""
        # Create a valid file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_file_path = f.name
        
        try:
            # Test valid file
            is_valid, error_msg = manager.validate_file_upload(temp_file_path)
            assert is_valid
            assert error_msg == ""
            
            # Test non-existent file
            is_valid, error_msg = manager.validate_file_upload("nonexistent.txt")
            assert not is_valid
            assert "does not exist" in error_msg
            
        finally:
            os.unlink(temp_file_path)
    
    def test_save_uploaded_file(self, manager):
        """Test saving uploaded files."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_file_path = f.name
        
        try:
            # Save the file
            saved_path = manager.save_uploaded_file(temp_file_path, "test_mod.txt")
            
            # Check that file was saved
            assert os.path.exists(saved_path)
            
            # Check content
            with open(saved_path, 'r') as f:
                content = f.read()
            assert content == "Test content"
            
            # Clean up
            os.unlink(saved_path)
            
        finally:
            os.unlink(temp_file_path)
    
    def test_data_persistence(self, manager, sample_mod_data):
        """Test that data persists between manager instances."""
        # Submit a mod
        mod_id = manager.submit_mod(**sample_mod_data)
        
        # Create a new manager instance
        new_manager = ModsHubManager(
            mods_dir=manager.mods_dir,
            uploads_dir=manager.uploads_dir,
            config_file=manager.config_file
        )
        
        # Check that the mod is still there
        assert mod_id in new_manager.mods
        mod = new_manager.mods[mod_id]
        assert mod.title == sample_mod_data["title"]


class TestModSubmission:
    """Test the ModSubmission dataclass."""
    
    def test_mod_submission_creation(self):
        """Test creating a ModSubmission instance."""
        mod = ModSubmission(
            id="test_id",
            title="Test Mod",
            description="Test description",
            category=ModCategory.UTILITIES,
            mod_type=ModType.FILE,
            author="TestAuthor"
        )
        
        assert mod.id == "test_id"
        assert mod.title == "Test Mod"
        assert mod.category == ModCategory.UTILITIES
        assert mod.mod_type == ModType.FILE
        assert mod.status == ModStatus.PENDING
        assert mod.views == 0
        assert mod.downloads == 0
        assert mod.rating == 0.0
        assert mod.rating_count == 0
        assert mod.featured is False
    
    def test_mod_submission_defaults(self):
        """Test ModSubmission default values."""
        mod = ModSubmission(
            id="test_id",
            title="Test Mod",
            description="Test description",
            category=ModCategory.UTILITIES,
            mod_type=ModType.FILE,
            author="TestAuthor"
        )
        
        assert mod.tags == []
        assert mod.screenshots == []
        assert mod.dependencies == []
        assert mod.submitted_at is not None
    
    def test_mod_submission_with_optional_fields(self):
        """Test ModSubmission with optional fields."""
        mod = ModSubmission(
            id="test_id",
            title="Test Mod",
            description="Test description",
            category=ModCategory.UTILITIES,
            mod_type=ModType.FILE,
            author="TestAuthor",
            author_email="test@example.com",
            version="2.0.0",
            swg_version="Pre-CU",
            tags=["test", "demo"],
            dependencies=["SWG Base"],
            installation_notes="Test installation",
            changelog="v2.0.0 - Major update"
        )
        
        assert mod.author_email == "test@example.com"
        assert mod.version == "2.0.0"
        assert mod.swg_version == "Pre-CU"
        assert mod.tags == ["test", "demo"]
        assert mod.dependencies == ["SWG Base"]
        assert mod.installation_notes == "Test installation"
        assert mod.changelog == "v2.0.0 - Major update"


class TestModCategoryInfo:
    """Test the ModCategoryInfo dataclass."""
    
    def test_mod_category_info_creation(self):
        """Test creating a ModCategoryInfo instance."""
        cat_info = ModCategoryInfo(
            id="test_category",
            name="Test Category",
            description="Test category description",
            icon="fas fa-test",
            color="#ff0000",
            mod_count=5
        )
        
        assert cat_info.id == "test_category"
        assert cat_info.name == "Test Category"
        assert cat_info.description == "Test category description"
        assert cat_info.icon == "fas fa-test"
        assert cat_info.color == "#ff0000"
        assert cat_info.mod_count == 5
    
    def test_mod_category_info_defaults(self):
        """Test ModCategoryInfo default values."""
        cat_info = ModCategoryInfo(
            id="test_category",
            name="Test Category",
            description="Test description",
            icon="fas fa-test",
            color="#ff0000"
        )
        
        assert cat_info.mod_count == 0


class TestEnums:
    """Test the enum classes."""
    
    def test_mod_status_enum(self):
        """Test ModStatus enum."""
        assert ModStatus.PENDING.value == "pending"
        assert ModStatus.APPROVED.value == "approved"
        assert ModStatus.REJECTED.value == "rejected"
        assert ModStatus.ARCHIVED.value == "archived"
    
    def test_mod_category_enum(self):
        """Test ModCategory enum."""
        assert ModCategory.UI_ENHANCEMENTS.value == "ui_enhancements"
        assert ModCategory.MACROS_KEYBINDS.value == "macros_keybinds"
        assert ModCategory.CRAFTING_HELPERS.value == "crafting_helpers"
        assert ModCategory.VISUAL_MODS.value == "visual_mods"
        assert ModCategory.UTILITIES.value == "utilities"
        assert ModCategory.OTHER.value == "other"
    
    def test_mod_type_enum(self):
        """Test ModType enum."""
        assert ModType.FILE.value == "file"
        assert ModType.LINK.value == "link"
        assert ModType.TEXT.value == "text"
        assert ModType.SCRIPT.value == "script"


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    @pytest.fixture
    def complete_setup(self, temp_dirs):
        """Set up a complete mods hub for integration testing."""
        manager = ModsHubManager(
            mods_dir=temp_dirs['mods_dir'],
            uploads_dir=temp_dirs['uploads_dir'],
            config_file=temp_dirs['config_file']
        )
        
        # Submit multiple mods
        mod1_id = manager.submit_mod(
            title="UI Enhancement Pack",
            description="Comprehensive UI improvements",
            category=ModCategory.UI_ENHANCEMENTS,
            mod_type=ModType.FILE,
            author="UIExpert",
            tags=["ui", "enhancement"],
            dependencies=["SWG Base Client"]
        )
        
        mod2_id = manager.submit_mod(
            title="Combat Macros",
            description="Advanced combat macros",
            category=ModCategory.MACROS_KEYBINDS,
            mod_type=ModType.TEXT,
            author="CombatMaster",
            content="Combat macro content here",
            tags=["combat", "macros"]
        )
        
        mod3_id = manager.submit_mod(
            title="Crafting Calculator",
            description="Crafting optimization tool",
            category=ModCategory.CRAFTING_HELPERS,
            mod_type=ModType.LINK,
            author="CraftingGuru",
            download_url="https://example.com/crafting-tool.zip",
            tags=["crafting", "calculator"]
        )
        
        # Approve some mods
        manager.approve_mod(mod1_id, "admin")
        manager.approve_mod(mod2_id, "admin")
        
        # Set one as featured
        manager.set_featured(mod1_id, True)
        
        # Add some ratings
        manager.rate_mod(mod1_id, 4.5, "user1")
        manager.rate_mod(mod1_id, 5.0, "user2")
        manager.rate_mod(mod2_id, 4.0, "user3")
        
        return manager
    
    def test_complete_workflow(self, complete_setup):
        """Test the complete mods hub workflow."""
        manager = complete_setup
        
        # Test getting approved mods
        approved_mods = manager.get_approved_mods()
        assert len(approved_mods) == 2
        
        # Test getting pending mods
        pending_mods = manager.get_pending_mods()
        assert len(pending_mods) == 1
        
        # Test getting featured mods
        featured_mods = manager.get_featured_mods()
        assert len(featured_mods) == 1
        
        # Test getting popular mods
        popular_mods = manager.get_popular_mods(limit=3)
        assert len(popular_mods) == 2  # Only approved mods
        
        # Test category filtering
        ui_mods = manager.get_approved_mods(category=ModCategory.UI_ENHANCEMENTS)
        assert len(ui_mods) == 1
        
        # Test search functionality
        search_results = manager.get_approved_mods(search="enhancement")
        assert len(search_results) == 1
        
        # Test getting stats
        stats = manager.get_stats()
        assert stats['total_mods'] == 3
        assert stats['approved_mods'] == 2
        assert stats['pending_mods'] == 1
        assert stats['featured_mods'] == 1
    
    def test_mod_lifecycle(self, complete_setup):
        """Test the complete mod lifecycle."""
        manager = complete_setup
        
        # Submit a new mod
        mod_id = manager.submit_mod(
            title="New Test Mod",
            description="A new test mod",
            category=ModCategory.UTILITIES,
            mod_type=ModType.FILE,
            author="NewAuthor"
        )
        
        # Verify it's pending
        mod = manager.get_mod(mod_id)
        assert mod.status == ModStatus.PENDING
        
        # Approve the mod
        success = manager.approve_mod(mod_id, "admin")
        assert success
        
        # Verify it's approved
        mod = manager.get_mod(mod_id)
        assert mod.status == ModStatus.APPROVED
        
        # Add some activity
        manager.increment_views(mod_id)
        manager.increment_downloads(mod_id)
        manager.rate_mod(mod_id, 4.0, "user1")
        
        # Verify activity
        mod = manager.get_mod(mod_id)
        assert mod.views == 1
        assert mod.downloads == 1
        assert mod.rating == 4.0
        assert mod.rating_count == 1
        
        # Set as featured
        manager.set_featured(mod_id, True)
        mod = manager.get_mod(mod_id)
        assert mod.featured is True
        
        # Delete the mod
        success = manager.delete_mod(mod_id)
        assert success
        assert mod_id not in manager.mods


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
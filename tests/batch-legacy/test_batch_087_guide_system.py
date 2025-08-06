#!/usr/bin/env python3
"""
Test suite for Batch 087 - Public Guide Generator + Editor

This test suite covers:
1. Guide manager functionality (CRUD operations)
2. Authentication and authorization
3. Markdown processing
4. Web interface functionality
5. API endpoints
"""

import json
import logging
import os
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.guide_manager import GuideManager, GuideMetadata, Guide, GuideCategory

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)

class TestGuideManager(unittest.TestCase):
    """Test the GuideManager class functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test guides
        self.test_dir = tempfile.mkdtemp()
        self.guide_manager = GuideManager(self.test_dir)
        
        # Sample guide metadata for testing
        self.sample_metadata = GuideMetadata(
            title="Test Guide",
            description="A test guide for unit testing",
            keywords=["test", "unit", "guide"],
            author="testuser",
            created_date="",
            modified_date="",
            category="combat",
            tags=["test", "combat"],
            status="draft",
            difficulty="beginner",
            estimated_read_time=5
        )
        
        self.sample_content = """# Test Guide

This is a test guide for unit testing.

## Section 1

Some content here.

### Subsection

More content.

- List item 1
- List item 2
- List item 3

## Section 2

More content with **bold** and *italic* text.

```python
def test_function():
    return "Hello, World!"
```

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
"""
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test guide manager initialization."""
        self.assertIsNotNone(self.guide_manager)
        self.assertTrue(Path(self.test_dir).exists())
        self.assertTrue(Path(self.test_dir) / "drafts").exists()
        self.assertTrue(Path(self.test_dir) / "published").exists()
        self.assertTrue(Path(self.test_dir) / "archived").exists())
    
    def test_authenticate_admin(self):
        """Test admin authentication."""
        # Test valid credentials
        self.assertTrue(self.guide_manager.authenticate_admin("admin", "admin123"))
        self.assertTrue(self.guide_manager.authenticate_admin("editor", "editor123"))
        
        # Test invalid credentials
        self.assertFalse(self.guide_manager.authenticate_admin("admin", "wrongpassword"))
        self.assertFalse(self.guide_manager.authenticate_admin("nonexistent", "password"))
        self.assertFalse(self.guide_manager.authenticate_admin("", ""))
    
    def test_create_guide(self):
        """Test guide creation."""
        guide_id = self.guide_manager.create_guide(
            self.sample_metadata, 
            self.sample_content, 
            "testuser"
        )
        
        self.assertIsNotNone(guide_id)
        self.assertTrue(len(guide_id) > 0)
        
        # Verify guide was saved
        guide = self.guide_manager.get_guide(guide_id)
        self.assertIsNotNone(guide)
        self.assertEqual(guide.metadata.title, "Test Guide")
        self.assertEqual(guide.content, self.sample_content)
        self.assertEqual(guide.metadata.author, "testuser")
        self.assertEqual(guide.metadata.status, "draft")
    
    def test_get_guide(self):
        """Test retrieving a guide."""
        # Create a guide first
        guide_id = self.guide_manager.create_guide(
            self.sample_metadata, 
            self.sample_content, 
            "testuser"
        )
        
        # Retrieve the guide
        guide = self.guide_manager.get_guide(guide_id)
        
        self.assertIsNotNone(guide)
        self.assertEqual(guide.id, guide_id)
        self.assertEqual(guide.metadata.title, "Test Guide")
        self.assertEqual(guide.content, self.sample_content)
        self.assertIsNotNone(guide.html_content)
        self.assertIn("<h1>Test Guide</h1>", guide.html_content)
    
    def test_get_nonexistent_guide(self):
        """Test retrieving a guide that doesn't exist."""
        guide = self.guide_manager.get_guide("nonexistent-id")
        self.assertIsNone(guide)
    
    def test_update_guide(self):
        """Test guide updating."""
        # Create a guide first
        guide_id = self.guide_manager.create_guide(
            self.sample_metadata, 
            self.sample_content, 
            "testuser"
        )
        
        # Update the guide
        updated_metadata = GuideMetadata(
            title="Updated Test Guide",
            description="Updated description",
            keywords=["updated", "test"],
            author="testuser",
            created_date="",
            modified_date="",
            category="crafting",
            tags=["updated", "crafting"],
            status="published",
            difficulty="intermediate",
            estimated_read_time=10
        )
        
        updated_content = """# Updated Test Guide

This is an updated test guide.

## New Section

Updated content here.
"""
        
        success = self.guide_manager.update_guide(
            guide_id, 
            updated_metadata, 
            updated_content, 
            "testuser"
        )
        
        self.assertTrue(success)
        
        # Verify the guide was updated
        guide = self.guide_manager.get_guide(guide_id)
        self.assertEqual(guide.metadata.title, "Updated Test Guide")
        self.assertEqual(guide.content, updated_content)
        self.assertEqual(guide.metadata.status, "published")
        self.assertEqual(guide.version, 2)
    
    def test_update_nonexistent_guide(self):
        """Test updating a guide that doesn't exist."""
        success = self.guide_manager.update_guide(
            "nonexistent-id",
            self.sample_metadata,
            self.sample_content,
            "testuser"
        )
        
        self.assertFalse(success)
    
    def test_delete_guide(self):
        """Test guide deletion."""
        # Create a guide first
        guide_id = self.guide_manager.create_guide(
            self.sample_metadata, 
            self.sample_content, 
            "testuser"
        )
        
        # Verify guide exists
        guide = self.guide_manager.get_guide(guide_id)
        self.assertIsNotNone(guide)
        
        # Delete the guide
        success = self.guide_manager.delete_guide(guide_id)
        self.assertTrue(success)
        
        # Verify guide is archived
        guide = self.guide_manager.get_guide(guide_id)
        self.assertIsNone(guide)
        
        # Check that archived file exists
        archived_file = Path(self.test_dir) / "archived" / f"{guide_id}.json"
        self.assertTrue(archived_file.exists())
    
    def test_delete_nonexistent_guide(self):
        """Test deleting a guide that doesn't exist."""
        success = self.guide_manager.delete_guide("nonexistent-id")
        self.assertFalse(success)
    
    def test_publish_guide(self):
        """Test publishing a draft guide."""
        # Create a draft guide
        guide_id = self.guide_manager.create_guide(
            self.sample_metadata, 
            self.sample_content, 
            "testuser"
        )
        
        # Verify it's a draft
        guide = self.guide_manager.get_guide(guide_id)
        self.assertEqual(guide.metadata.status, "draft")
        
        # Publish the guide
        success = self.guide_manager.publish_guide(guide_id)
        self.assertTrue(success)
        
        # Verify it's now published
        guide = self.guide_manager.get_guide(guide_id)
        self.assertEqual(guide.metadata.status, "published")
    
    def test_publish_already_published_guide(self):
        """Test publishing an already published guide."""
        # Create and publish a guide
        guide_id = self.guide_manager.create_guide(
            self.sample_metadata, 
            self.sample_content, 
            "testuser"
        )
        self.guide_manager.publish_guide(guide_id)
        
        # Try to publish again
        success = self.guide_manager.publish_guide(guide_id)
        self.assertFalse(success)
    
    def test_list_guides(self):
        """Test listing guides with filters."""
        # Create multiple guides
        guide1_id = self.guide_manager.create_guide(
            self.sample_metadata, 
            self.sample_content, 
            "testuser"
        )
        
        # Create a published guide
        published_metadata = GuideMetadata(
            title="Published Guide",
            description="A published guide",
            keywords=["published"],
            author="testuser",
            created_date="",
            modified_date="",
            category="crafting",
            tags=["published"],
            status="published",
            difficulty="beginner",
            estimated_read_time=5
        )
        
        guide2_id = self.guide_manager.create_guide(
            published_metadata,
            "Published content",
            "testuser"
        )
        self.guide_manager.publish_guide(guide2_id)
        
        # Test listing all guides
        all_guides = self.guide_manager.list_guides()
        self.assertEqual(len(all_guides), 2)
        
        # Test filtering by status
        draft_guides = self.guide_manager.list_guides(status="draft")
        self.assertEqual(len(draft_guides), 1)
        self.assertEqual(draft_guides[0]["title"], "Test Guide")
        
        published_guides = self.guide_manager.list_guides(status="published")
        self.assertEqual(len(published_guides), 1)
        self.assertEqual(published_guides[0]["title"], "Published Guide")
        
        # Test filtering by category
        combat_guides = self.guide_manager.list_guides(category="combat")
        self.assertEqual(len(combat_guides), 1)
        self.assertEqual(combat_guides[0]["title"], "Test Guide")
        
        crafting_guides = self.guide_manager.list_guides(category="crafting")
        self.assertEqual(len(crafting_guides), 1)
        self.assertEqual(crafting_guides[0]["title"], "Published Guide")
        
        # Test filtering by author
        user_guides = self.guide_manager.list_guides(author="testuser")
        self.assertEqual(len(user_guides), 2)
    
    def test_search_guides(self):
        """Test guide search functionality."""
        # Create guides with different content
        guide1_id = self.guide_manager.create_guide(
            self.sample_metadata, 
            self.sample_content, 
            "testuser"
        )
        
        # Create another guide with different content
        guide2_metadata = GuideMetadata(
            title="Crafting Guide",
            description="A guide about crafting",
            keywords=["crafting", "resources"],
            author="testuser",
            created_date="",
            modified_date="",
            category="crafting",
            tags=["crafting", "resources"],
            status="published",
            difficulty="intermediate",
            estimated_read_time=10
        )
        
        guide2_id = self.guide_manager.create_guide(
            guide2_metadata,
            "Crafting content with resources and materials",
            "testuser"
        )
        self.guide_manager.publish_guide(guide2_id)
        
        # Test search by title
        combat_results = self.guide_manager.search_guides("combat")
        self.assertEqual(len(combat_results), 1)
        self.assertEqual(combat_results[0]["title"], "Test Guide")
        
        # Test search by content
        crafting_results = self.guide_manager.search_guides("crafting")
        self.assertEqual(len(crafting_results), 1)
        self.assertEqual(crafting_results[0]["title"], "Crafting Guide")
        
        # Test search by tag
        resource_results = self.guide_manager.search_guides("resources")
        self.assertEqual(len(resource_results), 1)
        self.assertEqual(resource_results[0]["title"], "Crafting Guide")
        
        # Test search with no results
        no_results = self.guide_manager.search_guides("nonexistent")
        self.assertEqual(len(no_results), 0)
    
    def test_get_categories(self):
        """Test getting available categories."""
        categories = self.guide_manager.get_categories()
        self.assertIsInstance(categories, list)
        self.assertIn("combat", categories)
        self.assertIn("crafting", categories)
        self.assertIn("questing", categories)
        self.assertIn("travel", categories)
    
    def test_get_stats(self):
        """Test getting guide statistics."""
        # Create some guides first
        self.guide_manager.create_guide(
            self.sample_metadata, 
            self.sample_content, 
            "testuser"
        )
        
        # Create a published guide
        published_metadata = GuideMetadata(
            title="Published Guide",
            description="A published guide",
            keywords=["published"],
            author="testuser",
            created_date="",
            modified_date="",
            category="crafting",
            tags=["published"],
            status="published",
            difficulty="beginner",
            estimated_read_time=5
        )
        
        guide_id = self.guide_manager.create_guide(
            published_metadata,
            "Published content",
            "testuser"
        )
        self.guide_manager.publish_guide(guide_id)
        
        # Get stats
        stats = self.guide_manager.get_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_guides", stats)
        self.assertIn("published_guides", stats)
        self.assertIn("draft_guides", stats)
        self.assertIn("archived_guides", stats)
        self.assertIn("total_views", stats)
        self.assertIn("categories", stats)
        self.assertIn("recent_guides", stats)
        
        self.assertEqual(stats["total_guides"], 2)
        self.assertEqual(stats["published_guides"], 1)
        self.assertEqual(stats["draft_guides"], 1)
        self.assertEqual(stats["archived_guides"], 0)
    
    def test_markdown_processing(self):
        """Test markdown to HTML processing."""
        markdown_content = """# Test Heading

This is a **bold** paragraph with *italic* text.

## Subheading

- List item 1
- List item 2

```python
def hello():
    print("Hello, World!")
```

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
"""
        
        html_content = self.guide_manager._process_markdown(markdown_content)
        
        self.assertIn("<h1>Test Heading</h1>", html_content)
        self.assertIn("<strong>bold</strong>", html_content)
        self.assertIn("<em>italic</em>", html_content)
        self.assertIn("<h2>Subheading</h2>", html_content)
        self.assertIn("<li>List item 1</li>", html_content)
        self.assertIn("<li>List item 2</li>", html_content)
        self.assertIn("<pre><code>", html_content)
        self.assertIn("<table>", html_content)

class TestGuideMetadata(unittest.TestCase):
    """Test the GuideMetadata dataclass."""
    
    def test_guide_metadata_creation(self):
        """Test creating GuideMetadata objects."""
        metadata = GuideMetadata(
            title="Test Guide",
            description="Test description",
            keywords=["test", "guide"],
            author="testuser",
            created_date="2023-01-01T00:00:00Z",
            modified_date="2023-01-01T00:00:00Z",
            category="combat",
            tags=["test", "combat"],
            status="draft",
            difficulty="beginner",
            estimated_read_time=5
        )
        
        self.assertEqual(metadata.title, "Test Guide")
        self.assertEqual(metadata.description, "Test description")
        self.assertEqual(metadata.keywords, ["test", "guide"])
        self.assertEqual(metadata.author, "testuser")
        self.assertEqual(metadata.category, "combat")
        self.assertEqual(metadata.tags, ["test", "combat"])
        self.assertEqual(metadata.status, "draft")
        self.assertEqual(metadata.difficulty, "beginner")
        self.assertEqual(metadata.estimated_read_time, 5)
        self.assertEqual(metadata.view_count, 0)
        self.assertEqual(metadata.rating, 0.0)
    
    def test_guide_metadata_defaults(self):
        """Test GuideMetadata default values."""
        metadata = GuideMetadata(
            title="Test",
            description="Test",
            keywords=[],
            author="test",
            created_date="",
            modified_date="",
            category="combat",
            tags=[],
            status="draft"
        )
        
        self.assertEqual(metadata.view_count, 0)
        self.assertEqual(metadata.rating, 0.0)
        self.assertEqual(metadata.difficulty, "beginner")
        self.assertEqual(metadata.estimated_read_time, 5)

class TestGuideCategory(unittest.TestCase):
    """Test the GuideCategory enum."""
    
    def test_guide_categories(self):
        """Test guide category values."""
        self.assertEqual(GuideCategory.COMBAT.value, "combat")
        self.assertEqual(GuideCategory.CRAFTING.value, "crafting")
        self.assertEqual(GuideCategory.QUESTING.value, "questing")
        self.assertEqual(GuideCategory.TRAVEL.value, "travel")
        self.assertEqual(GuideCategory.PROFESSION.value, "profession")
        self.assertEqual(GuideCategory.ECONOMY.value, "economy")
        self.assertEqual(GuideCategory.SOCIAL.value, "social")
        self.assertEqual(GuideCategory.UTILITY.value, "utility")
        self.assertEqual(GuideCategory.BEGINNER.value, "beginner")
        self.assertEqual(GuideCategory.ADVANCED.value, "advanced")

class TestWebInterface(unittest.TestCase):
    """Test web interface functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.guide_manager = GuideManager(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    @patch('flask.Flask')
    def test_dashboard_routes(self, mock_flask):
        """Test that dashboard routes are properly configured."""
        # This is a basic test to ensure the routes are defined
        # In a real test, you would use Flask's test client
        from dashboard.app import app
        
        # Check that the app has the expected routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        self.assertIn('/guides', routes)
        self.assertIn('/guides/new', routes)
        self.assertIn('/api/guides', routes)
    
    def test_guide_manager_integration(self):
        """Test integration between guide manager and web interface."""
        # Create a test guide
        metadata = GuideMetadata(
            title="Integration Test Guide",
            description="A guide for testing integration",
            keywords=["integration", "test"],
            author="testuser",
            created_date="",
            modified_date="",
            category="combat",
            tags=["integration", "test"],
            status="published",
            difficulty="beginner",
            estimated_read_time=5
        )
        
        guide_id = self.guide_manager.create_guide(
            metadata,
            "# Integration Test\n\nThis is a test guide.",
            "testuser"
        )
        
        # Test that the guide can be retrieved
        guide = self.guide_manager.get_guide(guide_id)
        self.assertIsNotNone(guide)
        self.assertEqual(guide.metadata.title, "Integration Test Guide")
        
        # Test that the guide appears in listings
        guides = self.guide_manager.list_guides()
        self.assertGreater(len(guides), 0)
        
        guide_titles = [g["title"] for g in guides]
        self.assertIn("Integration Test Guide", guide_titles)

def run_integration_tests():
    """Run integration tests with a live server."""
    import subprocess
    import time
    import requests
    
    print("Running integration tests...")
    
    # Start the server in a subprocess
    process = subprocess.Popen([
        sys.executable, "dashboard/app.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    try:
        # Wait for server to start
        time.sleep(3)
        
        # Test basic connectivity
        try:
            response = requests.get("http://127.0.0.1:8000/")
            print(f"Dashboard accessible: {response.status_code == 200}")
        except requests.exceptions.ConnectionError:
            print("Dashboard not accessible")
        
        # Test guides endpoint
        try:
            response = requests.get("http://127.0.0.1:8000/guides")
            print(f"Guides page accessible: {response.status_code == 200}")
        except requests.exceptions.ConnectionError:
            print("Guides page not accessible")
        
        # Test API endpoint
        try:
            response = requests.get("http://127.0.0.1:8000/api/guides")
            print(f"API endpoint accessible: {response.status_code == 200}")
        except requests.exceptions.ConnectionError:
            print("API endpoint not accessible")
        
    finally:
        # Stop the server
        process.terminate()
        process.wait()

if __name__ == "__main__":
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    # Run integration tests
    print("\n" + "="*50)
    run_integration_tests() 
#!/usr/bin/env python3
"""
MS11 Batch 092 - Public Blog & SEO Guide Generator Tests

This test suite validates the blog system functionality including:
- Data ingestion and processing
- Blog post generation and management
- Statistics and analytics
- API endpoints and web interface
"""

import json
import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import pytest
from core.blog_engine import (
    BlogPost, BlogStats, BlogDataIngestion, BlogPostGenerator, BlogManager,
    blog_manager
)

class TestBlogPost:
    """Test BlogPost dataclass functionality."""
    
    def test_blog_post_creation(self):
        """Test creating a BlogPost with required fields."""
        post = BlogPost(
            post_id="test_post_001",
            title="Test Blog Post",
            content="This is a test blog post content.",
            excerpt="A test blog post excerpt."
        )
        
        assert post.post_id == "test_post_001"
        assert post.title == "Test Blog Post"
        assert post.content == "This is a test blog post content."
        assert post.excerpt == "A test blog post excerpt."
        assert post.author == "SWGDB Team"
        assert post.category == "general"
        assert post.status == "draft"
        assert post.tags == []
        assert post.seo_keywords == []
        assert post.metadata == {}
        assert post.word_count > 0
        assert post.created_at is not None
    
    def test_blog_post_with_optional_fields(self):
        """Test creating a BlogPost with optional fields."""
        post = BlogPost(
            post_id="test_post_002",
            title="Test Post with Options",
            content="Content with options.",
            excerpt="Excerpt with options.",
            author="Test Author",
            category="statistics",
            tags=["test", "blog", "swg"],
            status="published",
            seo_title="SEO Title",
            seo_description="SEO Description",
            seo_keywords=["SWG", "blog", "test"],
            read_time_minutes=10,
            view_count=5,
            share_count=2
        )
        
        assert post.author == "Test Author"
        assert post.category == "statistics"
        assert post.tags == ["test", "blog", "swg"]
        assert post.status == "published"
        assert post.seo_title == "SEO Title"
        assert post.seo_description == "SEO Description"
        assert post.seo_keywords == ["SWG", "blog", "test"]
        assert post.read_time_minutes == 10
        assert post.view_count == 5
        assert post.share_count == 2
    
    def test_blog_post_word_count(self):
        """Test automatic word count calculation."""
        content = "This is a test blog post with multiple words."
        post = BlogPost(
            post_id="test_post_003",
            title="Word Count Test",
            content=content,
            excerpt="Test excerpt."
        )
        
        # Should count words in content
        expected_words = len(content.split())
        assert post.word_count == expected_words
    
    def test_blog_post_serialization(self):
        """Test BlogPost serialization to dictionary."""
        post = BlogPost(
            post_id="test_post_004",
            title="Serialization Test",
            content="Test content for serialization.",
            excerpt="Test excerpt."
        )
        
        # Convert to dictionary
        post_dict = {
            'post_id': post.post_id,
            'title': post.title,
            'content': post.content,
            'excerpt': post.excerpt,
            'author': post.author,
            'category': post.category,
            'tags': post.tags,
            'status': post.status,
            'created_at': post.created_at,
            'published_at': post.published_at,
            'updated_at': post.updated_at,
            'seo_title': post.seo_title,
            'seo_description': post.seo_description,
            'seo_keywords': post.seo_keywords,
            'featured_image': post.featured_image,
            'read_time_minutes': post.read_time_minutes,
            'word_count': post.word_count,
            'view_count': post.view_count,
            'share_count': post.share_count,
            'metadata': post.metadata
        }
        
        assert post_dict['post_id'] == "test_post_004"
        assert post_dict['title'] == "Serialization Test"
        assert post_dict['content'] == "Test content for serialization."

class TestBlogDataIngestion:
    """Test BlogDataIngestion functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.data_dir.mkdir()
        
        # Create test data files
        self.create_test_data_files()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_data_files(self):
        """Create test data files for ingestion."""
        # Create test session logs
        sessions_dir = self.data_dir / "logs" / "sessions"
        sessions_dir.mkdir(parents=True)
        
        session_data = {
            "session_id": "test_session_001",
            "start_time": (datetime.now() - timedelta(days=1)).isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration": 120.5,
            "locations_visited": [
                {"city": "Mos Eisley", "planet": "Tatooine"},
                {"city": "Anchorhead", "planet": "Tatooine"},
                {"city": "Theed", "planet": "Naboo"}
            ],
            "quests_completed": ["Quest 1", "Quest 2"],
            "player_encounters": [{"name": "Player1"}, {"name": "Player2"}],
            "summary": {
                "total_credits_earned": 5000,
                "total_xp_gained": 2500
            }
        }
        
        with open(sessions_dir / "session_test_001.json", 'w') as f:
            json.dump(session_data, f)
        
        # Create test quest database
        quest_data = {
            "quest_001": {
                "name": "Test Quest 1",
                "description": "A test quest",
                "level_requirement": 10,
                "location": "Mos Eisley",
                "planet": "Tatooine",
                "xp_reward": 1000,
                "credit_reward": 500,
                "rewards": ["Experience", "Credits"]
            },
            "quest_002": {
                "name": "Test Quest 2",
                "description": "Another test quest",
                "level_requirement": 15,
                "location": "Theed",
                "planet": "Naboo",
                "xp_reward": 1500,
                "credit_reward": 750,
                "rewards": ["Experience", "Credits", "Item"]
            }
        }
        
        with open(self.data_dir / "quest_database.json", 'w') as f:
            json.dump(quest_data, f)
        
        # Create test collection data
        collections_dir = self.data_dir / "collections"
        collections_dir.mkdir()
        
        collection_data = {
            "zone": "Tatooine",
            "planet": "Tatooine",
            "collections": [
                {
                    "name": "Tatooine Trophy",
                    "type": "trophy",
                    "subzone": "Mos Eisley",
                    "coordinates": [100, 200],
                    "required_level": 5,
                    "description": "A rare trophy",
                    "rarity": "common"
                }
            ]
        }
        
        with open(collections_dir / "tatooine.json", 'w') as f:
            json.dump(collection_data, f)
        
        # Create test macro data
        macros_dir = self.data_dir / "macros"
        macros_dir.mkdir()
        
        with open(macros_dir / "test_macro.txt", 'w') as f:
            f.write("// Test macro content\n/ui action toolbarSlot01;\n")
    
    def test_data_ingestion_initialization(self):
        """Test BlogDataIngestion initialization."""
        ingestion = BlogDataIngestion(str(self.data_dir))
        assert ingestion.data_dir == self.data_dir
        assert ingestion.ingested_data == {}
    
    def test_session_stats_ingestion(self):
        """Test session statistics ingestion."""
        ingestion = BlogDataIngestion(str(self.data_dir))
        
        # Mock the session logs directory path
        with patch.object(ingestion, 'data_dir', self.data_dir):
            session_stats = ingestion._ingest_session_stats()
        
        assert session_stats['total_sessions'] > 0
        assert session_stats['total_credits_earned'] > 0
        assert session_stats['total_xp_gained'] > 0
        assert len(session_stats['top_cities']) > 0
        assert len(session_stats['top_planets']) > 0
    
    def test_quest_data_ingestion(self):
        """Test quest data ingestion."""
        ingestion = BlogDataIngestion(str(self.data_dir))
        quest_data = ingestion._ingest_quest_data()
        
        assert len(quest_data) > 0
        assert "quest_001" in quest_data
        assert quest_data["quest_001"]["name"] == "Test Quest 1"
    
    def test_collection_data_ingestion(self):
        """Test collection data ingestion."""
        ingestion = BlogDataIngestion(str(self.data_dir))
        collection_data = ingestion._ingest_collection_data()
        
        assert len(collection_data) > 0
        assert "Tatooine" in collection_data
        assert len(collection_data["Tatooine"]["collections"]) > 0
    
    def test_macro_data_ingestion(self):
        """Test macro data ingestion."""
        ingestion = BlogDataIngestion(str(self.data_dir))
        macro_data = ingestion._ingest_macro_data()
        
        assert len(macro_data) > 0
        assert "test_macro" in macro_data
        assert macro_data["test_macro"]["name"] == "test_macro"
        assert "content" in macro_data["test_macro"]
    
    def test_complete_data_ingestion(self):
        """Test complete data ingestion process."""
        ingestion = BlogDataIngestion(str(self.data_dir))
        ingested_data = ingestion.ingest_all_data()
        
        assert 'session_stats' in ingested_data
        assert 'quests' in ingested_data
        assert 'collections' in ingested_data
        assert 'macros' in ingested_data
        assert len(ingested_data) >= 4

class TestBlogPostGenerator:
    """Test BlogPostGenerator functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.data_dir.mkdir()
        
        # Create test data
        self.create_test_data()
        
        # Create data ingestion and generator
        self.data_ingestion = BlogDataIngestion(str(self.data_dir))
        self.post_generator = BlogPostGenerator(self.data_ingestion)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_data(self):
        """Create test data for post generation."""
        # Create session stats
        session_stats = {
            "top_cities": [("Mos Eisley", 10), ("Theed", 5), ("Anchorhead", 3)],
            "top_planets": [("Tatooine", 15), ("Naboo", 8), ("Corellia", 2)],
            "popular_activities": [("questing", 25), ("social", 15), ("crafting", 10)],
            "total_sessions": 5,
            "average_session_duration": 90.0,
            "total_credits_earned": 25000,
            "total_xp_gained": 12500
        }
        
        # Create quest data
        quests = {
            "quest_001": {
                "name": "Test Quest",
                "description": "A challenging test quest",
                "level_requirement": 10,
                "location": "Mos Eisley",
                "planet": "Tatooine",
                "xp_reward": 1000,
                "credit_reward": 500,
                "rewards": ["Experience", "Credits"]
            }
        }
        
        # Create collection data
        collections = {
            "Tatooine": {
                "planet": "Tatooine",
                "collections": [
                    {
                        "name": "Tatooine Trophy",
                        "type": "trophy",
                        "subzone": "Mos Eisley",
                        "coordinates": [100, 200],
                        "required_level": 5,
                        "description": "A rare trophy",
                        "rarity": "common"
                    }
                ]
            }
        }
        
        # Create macro data
        macros = {
            "test_macro": {
                "name": "test_macro",
                "content": "// Test macro\n/ui action toolbarSlot01;",
                "length": 30,
                "lines": 2
            }
        }
        
        # Set up ingested data
        self.data_ingestion.ingested_data = {
            'session_stats': session_stats,
            'quests': quests,
            'collections': collections,
            'macros': macros,
            'builds': {},
            'heroics': {},
            'crafting': {}
        }
    
    def test_post_type_selection(self):
        """Test post type selection logic."""
        post_type = self.post_generator._choose_post_type()
        
        # Should return one of the available types
        available_types = ["stats_weekly", "quest_guide", "collection_guide", "macro_guide"]
        assert post_type in available_types
    
    def test_stats_post_generation(self):
        """Test weekly stats post generation."""
        post = self.post_generator._generate_stats_post()
        
        assert post.title == "Weekly SWG Community Stats"
        assert post.category == "statistics"
        assert "stats" in post.tags
        assert post.status == "draft"
        assert post.word_count > 0
        assert "Mos Eisley" in post.content or "Tatooine" in post.content
    
    def test_quest_post_generation(self):
        """Test quest guide post generation."""
        post = self.post_generator._generate_quest_post()
        
        assert "Quest Guide:" in post.title
        assert post.category == "quests"
        assert "quest" in post.tags
        assert post.status == "draft"
        assert post.word_count > 0
    
    def test_collection_post_generation(self):
        """Test collection guide post generation."""
        post = self.post_generator._generate_collection_post()
        
        assert "Collection Guide:" in post.title
        assert post.category == "collections"
        assert "collection" in post.tags
        assert post.status == "draft"
        assert post.word_count > 0
    
    def test_macro_post_generation(self):
        """Test macro guide post generation."""
        post = self.post_generator._generate_macro_post()
        
        assert "Macro Guide:" in post.title
        assert post.category == "macros"
        assert "macro" in post.tags
        assert post.status == "draft"
        assert post.word_count > 0
    
    def test_daily_post_generation(self):
        """Test daily post generation."""
        post = self.post_generator.generate_daily_post()
        
        assert post is not None
        assert post.title is not None
        assert post.content is not None
        assert post.excerpt is not None
        assert post.category is not None
        assert post.tags is not None
        assert post.status == "draft"

class TestBlogManager:
    """Test BlogManager functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.blog_dir = Path(self.temp_dir) / "blog"
        self.blog_dir.mkdir()
        
        # Create blog manager with test directory
        self.blog_manager = BlogManager(str(self.blog_dir))
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_blog_manager_initialization(self):
        """Test BlogManager initialization."""
        assert self.blog_manager.blog_dir == self.blog_dir
        assert self.blog_manager.blog_dir.exists()
    
    def test_create_and_get_post(self):
        """Test creating and retrieving a blog post."""
        post = BlogPost(
            post_id="test_post_001",
            title="Test Post",
            content="Test content",
            excerpt="Test excerpt"
        )
        
        # Create post
        success = self.blog_manager.create_post(post)
        assert success is True
        
        # Get post
        retrieved_post = self.blog_manager.get_post("test_post_001")
        assert retrieved_post is not None
        assert retrieved_post.title == "Test Post"
        assert retrieved_post.content == "Test content"
    
    def test_list_posts(self):
        """Test listing blog posts."""
        # Create multiple posts
        posts = [
            BlogPost(post_id="post_1", title="Post 1", content="Content 1", excerpt="Excerpt 1"),
            BlogPost(post_id="post_2", title="Post 2", content="Content 2", excerpt="Excerpt 2"),
            BlogPost(post_id="post_3", title="Post 3", content="Content 3", excerpt="Excerpt 3")
        ]
        
        for post in posts:
            self.blog_manager.create_post(post)
        
        # List all posts
        all_posts = self.blog_manager.list_posts()
        assert len(all_posts) == 3
        
        # List published posts only
        published_posts = self.blog_manager.list_posts(status="published")
        assert len(published_posts) == 0  # All posts are drafts by default
    
    def test_update_post(self):
        """Test updating a blog post."""
        post = BlogPost(
            post_id="test_update_post",
            title="Original Title",
            content="Original content",
            excerpt="Original excerpt"
        )
        
        self.blog_manager.create_post(post)
        
        # Update post
        success = self.blog_manager.update_post(
            "test_update_post",
            title="Updated Title",
            content="Updated content"
        )
        
        assert success is True
        
        # Verify update
        updated_post = self.blog_manager.get_post("test_update_post")
        assert updated_post.title == "Updated Title"
        assert updated_post.content == "Updated content"
        assert updated_post.updated_at is not None
    
    def test_publish_post(self):
        """Test publishing a blog post."""
        post = BlogPost(
            post_id="test_publish_post",
            title="Draft Post",
            content="Draft content",
            excerpt="Draft excerpt"
        )
        
        self.blog_manager.create_post(post)
        
        # Publish post
        success = self.blog_manager.publish_post("test_publish_post")
        assert success is True
        
        # Verify publication
        published_post = self.blog_manager.get_post("test_publish_post")
        assert published_post.status == "published"
        assert published_post.published_at is not None
    
    def test_delete_post(self):
        """Test deleting a blog post."""
        post = BlogPost(
            post_id="test_delete_post",
            title="Post to Delete",
            content="Content to delete",
            excerpt="Excerpt to delete"
        )
        
        self.blog_manager.create_post(post)
        
        # Verify post exists
        assert self.blog_manager.get_post("test_delete_post") is not None
        
        # Delete post
        success = self.blog_manager.delete_post("test_delete_post")
        assert success is True
        
        # Verify post is deleted
        assert self.blog_manager.get_post("test_delete_post") is None
    
    def test_blog_statistics(self):
        """Test blog statistics calculation."""
        # Create posts with different statuses and metrics
        posts = [
            BlogPost(post_id="post_1", title="Post 1", content="Content 1", excerpt="Excerpt 1", status="published", view_count=10, share_count=2),
            BlogPost(post_id="post_2", title="Post 2", content="Content 2", excerpt="Excerpt 2", status="draft", view_count=5, share_count=1),
            BlogPost(post_id="post_3", title="Post 3", content="Content 3", excerpt="Excerpt 3", status="published", view_count=15, share_count=3)
        ]
        
        for post in posts:
            self.blog_manager.create_post(post)
        
        # Get statistics
        stats = self.blog_manager.get_blog_stats()
        
        assert stats.total_posts == 3
        assert stats.published_posts == 2
        assert stats.draft_posts == 1
        assert stats.total_views == 30
        assert stats.total_shares == 6
        assert stats.average_read_time > 0
        assert stats.most_popular_category is not None
        assert len(stats.most_popular_tags) >= 0
    
    def test_generate_daily_post(self):
        """Test daily post generation."""
        # Mock the post generator to return a test post
        test_post = BlogPost(
            post_id="daily_test_post",
            title="Daily Test Post",
            content="Daily test content",
            excerpt="Daily test excerpt"
        )
        
        with patch.object(self.blog_manager.post_generator, 'generate_daily_post', return_value=test_post):
            generated_post = self.blog_manager.generate_daily_post()
        
        assert generated_post is not None
        assert generated_post.title == "Daily Test Post"

class TestBlogStats:
    """Test BlogStats dataclass functionality."""
    
    def test_blog_stats_creation(self):
        """Test creating BlogStats with all fields."""
        stats = BlogStats(
            total_posts=10,
            published_posts=7,
            draft_posts=3,
            total_views=150,
            total_shares=25,
            average_read_time=5.5,
            most_popular_category="statistics",
            most_popular_tags=["swg", "blog", "community"],
            last_post_date="2025-01-01T12:00:00",
            next_scheduled_post="2025-01-02T12:00:00"
        )
        
        assert stats.total_posts == 10
        assert stats.published_posts == 7
        assert stats.draft_posts == 3
        assert stats.total_views == 150
        assert stats.total_shares == 25
        assert stats.average_read_time == 5.5
        assert stats.most_popular_category == "statistics"
        assert stats.most_popular_tags == ["swg", "blog", "community"]
        assert stats.last_post_date == "2025-01-01T12:00:00"
        assert stats.next_scheduled_post == "2025-01-02T12:00:00"

def test_integration():
    """Integration test for the complete blog system."""
    # Create temporary environment
    temp_dir = tempfile.mkdtemp()
    blog_dir = Path(temp_dir) / "blog"
    blog_dir.mkdir()
    
    try:
        # Create blog manager
        manager = BlogManager(str(blog_dir))
        
        # Test complete workflow
        # 1. Generate a daily post
        post = manager.generate_daily_post()
        assert post is not None
        
        # 2. Save the post
        success = manager.create_post(post)
        assert success is True
        
        # 3. Retrieve the post
        retrieved_post = manager.get_post(post.post_id)
        assert retrieved_post is not None
        assert retrieved_post.title == post.title
        
        # 4. Update the post
        success = manager.update_post(post.post_id, view_count=5)
        assert success is True
        
        # 5. Publish the post
        success = manager.publish_post(post.post_id)
        assert success is True
        
        # 6. Get statistics
        stats = manager.get_blog_stats()
        assert stats.total_posts == 1
        assert stats.published_posts == 1
        assert stats.draft_posts == 0
        
        # 7. List posts
        posts = manager.list_posts()
        assert len(posts) == 1
        
        # 8. Delete the post
        success = manager.delete_post(post.post_id)
        assert success is True
        
        # 9. Verify deletion
        posts = manager.list_posts()
        assert len(posts) == 0
        
    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 
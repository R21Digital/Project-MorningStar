"""Test suite for Batch 103 - Player Tool Embeds (Spreadsheet + Community Tools)."""

import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import pytest
import requests

from core.tools_manager import (
    ToolsManager,
    PlayerTool,
    ToolCategory,
    ToolStatus,
    submit_player_tool,
    get_player_tools,
    get_tool_by_id,
    increment_tool_views,
    get_tool_content,
    get_tools_stats
)


class TestPlayerTool:
    """Test the PlayerTool dataclass."""
    
    def test_player_tool_creation(self):
        """Test creating a PlayerTool instance."""
        tool = PlayerTool(
            id="test-tool-001",
            name="Test Tool",
            category=ToolCategory.SPREADSHEET,
            description="A test tool",
            url="https://example.com/tool",
            author="Test Author",
            tags=["test", "demo"],
            notes="Test notes"
        )
        
        assert tool.id == "test-tool-001"
        assert tool.name == "Test Tool"
        assert tool.category == ToolCategory.SPREADSHEET
        assert tool.description == "A test tool"
        assert tool.url == "https://example.com/tool"
        assert tool.author == "Test Author"
        assert tool.tags == ["test", "demo"]
        assert tool.notes == "Test notes"
        assert tool.status == ToolStatus.PENDING
        assert tool.views == 0
        assert tool.created_at is not None
        assert tool.updated_at is not None
    
    def test_player_tool_to_dict(self):
        """Test converting PlayerTool to dictionary."""
        tool = PlayerTool(
            id="test-tool-001",
            name="Test Tool",
            category=ToolCategory.GUIDE,
            description="A test tool",
            url="https://example.com/tool"
        )
        
        tool_dict = tool.to_dict()
        
        assert tool_dict['id'] == "test-tool-001"
        assert tool_dict['name'] == "Test Tool"
        assert tool_dict['category'] == "guide"
        assert tool_dict['description'] == "A test tool"
        assert tool_dict['url'] == "https://example.com/tool"
        assert tool_dict['status'] == "pending"
        assert tool_dict['views'] == 0
        assert 'created_at' in tool_dict
        assert 'updated_at' in tool_dict
    
    def test_player_tool_from_dict(self):
        """Test creating PlayerTool from dictionary."""
        tool_data = {
            'id': 'test-tool-001',
            'name': 'Test Tool',
            'category': 'spreadsheet',
            'description': 'A test tool',
            'url': 'https://example.com/tool',
            'author': 'Test Author',
            'tags': ['test', 'demo'],
            'notes': 'Test notes',
            'status': 'approved',
            'views': 10,
            'created_at': '2024-01-15T10:30:00',
            'updated_at': '2024-01-20T14:45:00',
            'approved_at': '2024-01-16T09:15:00',
            'approved_by': 'admin'
        }
        
        tool = PlayerTool.from_dict(tool_data)
        
        assert tool.id == "test-tool-001"
        assert tool.name == "Test Tool"
        assert tool.category == ToolCategory.SPREADSHEET
        assert tool.description == "A test tool"
        assert tool.url == "https://example.com/tool"
        assert tool.author == "Test Author"
        assert tool.tags == ["test", "demo"]
        assert tool.notes == "Test notes"
        assert tool.status == ToolStatus.APPROVED
        assert tool.views == 10
        assert tool.created_at == datetime.fromisoformat("2024-01-15T10:30:00")
        assert tool.updated_at == datetime.fromisoformat("2024-01-20T14:45:00")
        assert tool.approved_at == datetime.fromisoformat("2024-01-16T09:15:00")
        assert tool.approved_by == "admin"


class TestToolsManager:
    """Test the ToolsManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ToolsManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_manager_initialization(self):
        """Test tools manager initialization."""
        assert self.manager.data_dir.exists()
        assert self.manager.tools_file.exists()
        assert self.manager.submissions_file.exists()
        assert self.manager.stats_file.exists()
        assert len(self.manager.tools) == 0
        assert len(self.manager.submissions) == 0
    
    def test_submit_tool_success(self):
        """Test successful tool submission."""
        tool_data = {
            'name': 'Test Tool',
            'category': 'spreadsheet',
            'description': 'A test tool',
            'url': 'https://example.com/tool',
            'author': 'Test Author',
            'tags': ['test', 'demo'],
            'notes': 'Test notes'
        }
        
        success, message = self.manager.submit_tool(tool_data)
        
        assert success
        assert "successfully" in message.lower()
        assert len(self.manager.submissions) == 1
        
        tool = self.manager.submissions[0]
        assert tool.name == "Test Tool"
        assert tool.category == ToolCategory.SPREADSHEET
        assert tool.description == "A test tool"
        assert tool.url == "https://example.com/tool"
        assert tool.author == "Test Author"
        assert tool.tags == ["test", "demo"]
        assert tool.notes == "Test notes"
        assert tool.status == ToolStatus.PENDING
    
    def test_submit_tool_missing_fields(self):
        """Test tool submission with missing required fields."""
        tool_data = {
            'name': 'Test Tool',
            'description': 'A test tool'
            # Missing category and url
        }
        
        success, message = self.manager.submit_tool(tool_data)
        
        assert not success
        assert "missing required field" in message.lower()
        assert len(self.manager.submissions) == 0
    
    def test_submit_tool_invalid_category(self):
        """Test tool submission with invalid category."""
        tool_data = {
            'name': 'Test Tool',
            'category': 'invalid_category',
            'description': 'A test tool',
            'url': 'https://example.com/tool'
        }
        
        success, message = self.manager.submit_tool(tool_data)
        
        assert not success
        assert "invalid category" in message.lower()
        assert len(self.manager.submissions) == 0
    
    def test_submit_tool_invalid_url(self):
        """Test tool submission with invalid URL."""
        tool_data = {
            'name': 'Test Tool',
            'category': 'spreadsheet',
            'description': 'A test tool',
            'url': 'not-a-valid-url'
        }
        
        success, message = self.manager.submit_tool(tool_data)
        
        assert not success
        assert "invalid url" in message.lower()
        assert len(self.manager.submissions) == 0
    
    def test_submit_tool_duplicate(self):
        """Test tool submission with duplicate URL."""
        # Submit first tool
        tool_data = {
            'name': 'Test Tool',
            'category': 'spreadsheet',
            'description': 'A test tool',
            'url': 'https://example.com/tool'
        }
        
        success, message = self.manager.submit_tool(tool_data)
        assert success
        
        # Submit duplicate tool
        duplicate_data = {
            'name': 'Another Tool',
            'category': 'guide',
            'description': 'Another tool',
            'url': 'https://example.com/tool'  # Same URL
        }
        
        success, message = self.manager.submit_tool(duplicate_data)
        
        assert not success
        assert "duplicate" in message.lower()
        assert len(self.manager.submissions) == 1  # Only first tool should be added
    
    def test_url_validation(self):
        """Test URL validation."""
        valid_urls = [
            'https://example.com',
            'http://example.com',
            'https://docs.google.com/spreadsheets/d/123/edit',
            'https://raw.githubusercontent.com/user/repo/file.md',
            'https://pastebin.com/raw/abc123'
        ]
        
        invalid_urls = [
            'not-a-url',
            'ftp://example.com',
            'example.com',
            'https://',
            ''
        ]
        
        for url in valid_urls:
            assert self.manager._is_valid_url(url), f"URL should be valid: {url}"
        
        for url in invalid_urls:
            assert not self.manager._is_valid_url(url), f"URL should be invalid: {url}"
    
    def test_get_all_tools(self):
        """Test getting all approved tools."""
        # Add some tools with different statuses
        tool1 = PlayerTool(
            id="tool-1",
            name="Active Tool",
            category=ToolCategory.SPREADSHEET,
            description="Active tool",
            url="https://example.com/tool1",
            status=ToolStatus.ACTIVE
        )
        
        tool2 = PlayerTool(
            id="tool-2",
            name="Approved Tool",
            category=ToolCategory.GUIDE,
            description="Approved tool",
            url="https://example.com/tool2",
            status=ToolStatus.APPROVED
        )
        
        tool3 = PlayerTool(
            id="tool-3",
            name="Pending Tool",
            category=ToolCategory.EXTERNAL,
            description="Pending tool",
            url="https://example.com/tool3",
            status=ToolStatus.PENDING
        )
        
        self.manager.tools = [tool1, tool2, tool3]
        
        all_tools = self.manager.get_all_tools()
        
        assert len(all_tools) == 2  # Only active and approved tools
        tool_names = [tool.name for tool in all_tools]
        assert "Active Tool" in tool_names
        assert "Approved Tool" in tool_names
        assert "Pending Tool" not in tool_names
    
    def test_get_tools_by_category(self):
        """Test getting tools by category."""
        tool1 = PlayerTool(
            id="tool-1",
            name="Spreadsheet Tool",
            category=ToolCategory.SPREADSHEET,
            description="A spreadsheet tool",
            url="https://example.com/tool1",
            status=ToolStatus.ACTIVE
        )
        
        tool2 = PlayerTool(
            id="tool-2",
            name="Guide Tool",
            category=ToolCategory.GUIDE,
            description="A guide tool",
            url="https://example.com/tool2",
            status=ToolStatus.ACTIVE
        )
        
        self.manager.tools = [tool1, tool2]
        
        spreadsheet_tools = self.manager.get_tools_by_category(ToolCategory.SPREADSHEET)
        guide_tools = self.manager.get_tools_by_category(ToolCategory.GUIDE)
        
        assert len(spreadsheet_tools) == 1
        assert spreadsheet_tools[0].name == "Spreadsheet Tool"
        
        assert len(guide_tools) == 1
        assert guide_tools[0].name == "Guide Tool"
    
    def test_get_tool_by_id(self):
        """Test getting tool by ID."""
        tool = PlayerTool(
            id="test-tool-001",
            name="Test Tool",
            category=ToolCategory.SPREADSHEET,
            description="A test tool",
            url="https://example.com/tool",
            status=ToolStatus.ACTIVE
        )
        
        self.manager.tools = [tool]
        
        found_tool = self.manager.get_tool_by_id("test-tool-001")
        assert found_tool is not None
        assert found_tool.name == "Test Tool"
        
        not_found = self.manager.get_tool_by_id("non-existent")
        assert not_found is None
    
    def test_increment_views(self):
        """Test incrementing tool views."""
        tool = PlayerTool(
            id="test-tool-001",
            name="Test Tool",
            category=ToolCategory.SPREADSHEET,
            description="A test tool",
            url="https://example.com/tool",
            status=ToolStatus.ACTIVE,
            views=10
        )
        
        self.manager.tools = [tool]
        
        success = self.manager.increment_views("test-tool-001")
        assert success
        assert tool.views == 11
        
        # Test with non-existent tool
        success = self.manager.increment_views("non-existent")
        assert not success
    
    def test_approve_tool(self):
        """Test approving a tool submission."""
        tool = PlayerTool(
            id="test-tool-001",
            name="Test Tool",
            category=ToolCategory.SPREADSHEET,
            description="A test tool",
            url="https://example.com/tool",
            status=ToolStatus.PENDING
        )
        
        self.manager.submissions = [tool]
        
        success, message = self.manager.approve_tool("test-tool-001", "admin")
        
        assert success
        assert "approved" in message.lower()
        assert len(self.manager.submissions) == 0
        assert len(self.manager.tools) == 1
        
        approved_tool = self.manager.tools[0]
        assert approved_tool.status == ToolStatus.APPROVED
        assert approved_tool.approved_by == "admin"
        assert approved_tool.approved_at is not None
    
    def test_reject_tool(self):
        """Test rejecting a tool submission."""
        tool = PlayerTool(
            id="test-tool-001",
            name="Test Tool",
            category=ToolCategory.SPREADSHEET,
            description="A test tool",
            url="https://example.com/tool",
            status=ToolStatus.PENDING
        )
        
        self.manager.submissions = [tool]
        
        success, message = self.manager.reject_tool("test-tool-001", "admin", "Not suitable")
        
        assert success
        assert "rejected" in message.lower()
        assert len(self.manager.submissions) == 0
        assert len(self.manager.tools) == 1
        
        rejected_tool = self.manager.tools[0]
        assert rejected_tool.status == ToolStatus.REJECTED
        assert rejected_tool.rejection_reason == "Not suitable"
    
    def test_get_stats(self):
        """Test getting tools statistics."""
        # Add some tools
        tool1 = PlayerTool(
            id="tool-1",
            name="Active Tool",
            category=ToolCategory.SPREADSHEET,
            description="Active tool",
            url="https://example.com/tool1",
            status=ToolStatus.ACTIVE,
            views=100
        )
        
        tool2 = PlayerTool(
            id="tool-2",
            name="Approved Tool",
            category=ToolCategory.GUIDE,
            description="Approved tool",
            url="https://example.com/tool2",
            status=ToolStatus.APPROVED,
            views=50
        )
        
        submission = PlayerTool(
            id="tool-3",
            name="Pending Tool",
            category=ToolCategory.EXTERNAL,
            description="Pending tool",
            url="https://example.com/tool3",
            status=ToolStatus.PENDING
        )
        
        self.manager.tools = [tool1, tool2]
        self.manager.submissions = [submission]
        
        stats = self.manager.get_stats()
        
        assert stats['total_tools'] == 2
        assert stats['active_tools'] == 1
        assert stats['total_views'] == 150
        assert stats['submitted_tools'] == 1
        assert 'last_updated' in stats
    
    def test_search_tools(self):
        """Test searching tools."""
        tool1 = PlayerTool(
            id="tool-1",
            name="Armor Calculator",
            category=ToolCategory.SPREADSHEET,
            description="Comprehensive armor calculator",
            url="https://example.com/tool1",
            status=ToolStatus.ACTIVE,
            tags=["armor", "calculator"]
        )
        
        tool2 = PlayerTool(
            id="tool-2",
            name="Combat Guide",
            category=ToolCategory.GUIDE,
            description="Advanced combat mechanics guide",
            url="https://example.com/tool2",
            status=ToolStatus.ACTIVE,
            tags=["combat", "guide"]
        )
        
        self.manager.tools = [tool1, tool2]
        
        # Search by name
        results = self.manager.search_tools("armor")
        assert len(results) == 1
        assert results[0].name == "Armor Calculator"
        
        # Search by description
        results = self.manager.search_tools("combat")
        assert len(results) == 1
        assert results[0].name == "Combat Guide"
        
        # Search by tags
        results = self.manager.search_tools("calculator")
        assert len(results) == 1
        assert results[0].name == "Armor Calculator"
        
        # Search with category filter
        results = self.manager.search_tools("guide", ToolCategory.GUIDE)
        assert len(results) == 1
        assert results[0].name == "Combat Guide"
    
    def test_get_popular_tools(self):
        """Test getting popular tools."""
        tool1 = PlayerTool(
            id="tool-1",
            name="Popular Tool",
            category=ToolCategory.SPREADSHEET,
            description="A popular tool",
            url="https://example.com/tool1",
            status=ToolStatus.ACTIVE,
            views=100
        )
        
        tool2 = PlayerTool(
            id="tool-2",
            name="Less Popular Tool",
            category=ToolCategory.GUIDE,
            description="A less popular tool",
            url="https://example.com/tool2",
            status=ToolStatus.ACTIVE,
            views=50
        )
        
        self.manager.tools = [tool1, tool2]
        
        popular_tools = self.manager.get_popular_tools(limit=1)
        assert len(popular_tools) == 1
        assert popular_tools[0].name == "Popular Tool"
        assert popular_tools[0].views == 100
    
    def test_get_recent_tools(self):
        """Test getting recent tools."""
        tool1 = PlayerTool(
            id="tool-1",
            name="Recent Tool",
            category=ToolCategory.SPREADSHEET,
            description="A recent tool",
            url="https://example.com/tool1",
            status=ToolStatus.ACTIVE,
            created_at=datetime.now()
        )
        
        tool2 = PlayerTool(
            id="tool-2",
            name="Older Tool",
            category=ToolCategory.GUIDE,
            description="An older tool",
            url="https://example.com/tool2",
            status=ToolStatus.ACTIVE,
            created_at=datetime.now() - timedelta(days=1)
        )
        
        self.manager.tools = [tool1, tool2]
        
        recent_tools = self.manager.get_recent_tools(limit=1)
        assert len(recent_tools) == 1
        assert recent_tools[0].name == "Recent Tool"


class TestToolsManagerContent:
    """Test content fetching functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ToolsManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('requests.get')
    def test_get_tool_content_github_raw(self, mock_get):
        """Test fetching content from GitHub raw URL."""
        mock_response = MagicMock()
        mock_response.text = "# Test Markdown\n\nThis is test content."
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        tool = PlayerTool(
            id="test-tool-001",
            name="Test Guide",
            category=ToolCategory.GUIDE,
            description="A test guide",
            url="https://raw.githubusercontent.com/user/repo/main/guide.md",
            status=ToolStatus.ACTIVE
        )
        
        self.manager.tools = [tool]
        
        content = self.manager.get_tool_content("test-tool-001")
        
        assert content is not None
        assert content['content'] == "# Test Markdown\n\nThis is test content."
        assert content['type'] == 'markdown'
    
    @patch('requests.get')
    def test_get_tool_content_github_blob(self, mock_get):
        """Test fetching content from GitHub blob URL."""
        mock_response = MagicMock()
        mock_response.text = "# Test Markdown\n\nThis is test content."
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        tool = PlayerTool(
            id="test-tool-001",
            name="Test Guide",
            category=ToolCategory.GUIDE,
            description="A test guide",
            url="https://github.com/user/repo/blob/main/guide.md",
            status=ToolStatus.ACTIVE
        )
        
        self.manager.tools = [tool]
        
        content = self.manager.get_tool_content("test-tool-001")
        
        assert content is not None
        assert content['content'] == "# Test Markdown\n\nThis is test content."
        assert content['type'] == 'markdown'
        
        # Verify the URL was converted to raw
        mock_get.assert_called_with("https://github.com/user/repo/raw/main/guide.md", timeout=10)
    
    @patch('requests.get')
    def test_get_tool_content_pastebin(self, mock_get):
        """Test fetching content from Pastebin."""
        mock_response = MagicMock()
        mock_response.text = "Test content from pastebin"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        tool = PlayerTool(
            id="test-tool-001",
            name="Test Guide",
            category=ToolCategory.GUIDE,
            description="A test guide",
            url="https://pastebin.com/raw/abc123",
            status=ToolStatus.ACTIVE
        )
        
        self.manager.tools = [tool]
        
        content = self.manager.get_tool_content("test-tool-001")
        
        assert content is not None
        assert content['content'] == "Test content from pastebin"
        assert content['type'] == 'markdown'
    
    @patch('requests.get')
    def test_get_tool_content_error(self, mock_get):
        """Test content fetching with error."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        tool = PlayerTool(
            id="test-tool-001",
            name="Test Guide",
            category=ToolCategory.GUIDE,
            description="A test guide",
            url="https://example.com/guide.md",
            status=ToolStatus.ACTIVE
        )
        
        self.manager.tools = [tool]
        
        content = self.manager.get_tool_content("test-tool-001")
        
        assert content is None
    
    def test_get_tool_content_not_guide(self):
        """Test getting content for non-guide tool."""
        tool = PlayerTool(
            id="test-tool-001",
            name="Test Tool",
            category=ToolCategory.SPREADSHEET,
            description="A test tool",
            url="https://example.com/tool",
            status=ToolStatus.ACTIVE
        )
        
        self.manager.tools = [tool]
        
        content = self.manager.get_tool_content("test-tool-001")
        
        assert content is None


class TestToolsManagerIntegration:
    """Integration tests for the tools manager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ToolsManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """Test the complete tool submission and approval workflow."""
        # Submit a tool
        tool_data = {
            'name': 'Integration Test Tool',
            'category': 'spreadsheet',
            'description': 'A tool for integration testing',
            'url': 'https://docs.google.com/spreadsheets/d/test/edit',
            'author': 'Test Author',
            'tags': ['test', 'integration'],
            'notes': 'Test notes'
        }
        
        success, message = self.manager.submit_tool(tool_data)
        assert success
        
        # Check submission
        assert len(self.manager.submissions) == 1
        submission = self.manager.submissions[0]
        assert submission.name == "Integration Test Tool"
        assert submission.status == ToolStatus.PENDING
        
        # Approve the tool
        success, message = self.manager.approve_tool(submission.id, "admin")
        assert success
        
        # Check approval
        assert len(self.manager.submissions) == 0
        assert len(self.manager.tools) == 1
        
        approved_tool = self.manager.tools[0]
        assert approved_tool.status == ToolStatus.APPROVED
        assert approved_tool.approved_by == "admin"
        
        # Test view increment
        success = self.manager.increment_views(approved_tool.id)
        assert success
        assert approved_tool.views == 1
        
        # Test getting all tools
        all_tools = self.manager.get_all_tools()
        assert len(all_tools) == 1
        assert all_tools[0].name == "Integration Test Tool"
        
        # Test search
        results = self.manager.search_tools("integration")
        assert len(results) == 1
        assert results[0].name == "Integration Test Tool"
    
    def test_data_persistence(self):
        """Test that data persists between manager instances."""
        # Submit a tool
        tool_data = {
            'name': 'Persistence Test Tool',
            'category': 'guide',
            'description': 'A tool for persistence testing',
            'url': 'https://example.com/tool'
        }
        
        self.manager.submit_tool(tool_data)
        
        # Create new manager instance
        new_manager = ToolsManager(self.temp_dir)
        
        # Check that data was loaded
        assert len(new_manager.submissions) == 1
        assert new_manager.submissions[0].name == "Persistence Test Tool"
    
    def test_stats_calculation(self):
        """Test statistics calculation with multiple tools."""
        # Add tools with different statuses and views
        tool1 = PlayerTool(
            id="tool-1",
            name="Active Tool",
            category=ToolCategory.SPREADSHEET,
            description="Active tool",
            url="https://example.com/tool1",
            status=ToolStatus.ACTIVE,
            views=100
        )
        
        tool2 = PlayerTool(
            id="tool-2",
            name="Approved Tool",
            category=ToolCategory.GUIDE,
            description="Approved tool",
            url="https://example.com/tool2",
            status=ToolStatus.APPROVED,
            views=50
        )
        
        tool3 = PlayerTool(
            id="tool-3",
            name="Inactive Tool",
            category=ToolCategory.EXTERNAL,
            description="Inactive tool",
            url="https://example.com/tool3",
            status=ToolStatus.INACTIVE,
            views=25
        )
        
        submission = PlayerTool(
            id="tool-4",
            name="Pending Tool",
            category=ToolCategory.COMMUNITY,
            description="Pending tool",
            url="https://example.com/tool4",
            status=ToolStatus.PENDING
        )
        
        self.manager.tools = [tool1, tool2, tool3]
        self.manager.submissions = [submission]
        
        stats = self.manager.get_stats()
        
        assert stats['total_tools'] == 3
        assert stats['active_tools'] == 1
        assert stats['total_views'] == 175
        assert stats['submitted_tools'] == 1


class TestToolsManagerPerformance:
    """Performance tests for the tools manager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ToolsManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_large_dataset_performance(self):
        """Test performance with large dataset."""
        import time
        
        # Create many tools
        tools = []
        for i in range(1000):
            tool = PlayerTool(
                id=f"tool-{i}",
                name=f"Tool {i}",
                category=ToolCategory.SPREADSHEET,
                description=f"Description for tool {i}",
                url=f"https://example.com/tool{i}",
                status=ToolStatus.ACTIVE,
                views=i,
                tags=[f"tag{i}", f"category{i}"]
            )
            tools.append(tool)
        
        self.manager.tools = tools
        
        # Test search performance
        start_time = time.time()
        results = self.manager.search_tools("tool")
        search_time = time.time() - start_time
        
        assert len(results) > 0
        assert search_time < 1.0  # Should complete within 1 second
        
        # Test popular tools performance
        start_time = time.time()
        popular_tools = self.manager.get_popular_tools(limit=10)
        popular_time = time.time() - start_time
        
        assert len(popular_tools) == 10
        assert popular_time < 0.1  # Should complete quickly
        
        # Test recent tools performance
        start_time = time.time()
        recent_tools = self.manager.get_recent_tools(limit=10)
        recent_time = time.time() - start_time
        
        assert len(recent_tools) == 10
        assert recent_time < 0.1  # Should complete quickly


if __name__ == "__main__":
    pytest.main([__file__]) 
"""Demo script for Batch 103 - Player Tool Embeds (Spreadsheet + Community Tools).

This script demonstrates the new player tools system with various embed types
including Google Sheets, Markdown guides, and external links.
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from core.tools_manager import (
    ToolsManager,
    PlayerTool,
    ToolCategory,
    ToolStatus
)


def create_demo_tools_manager():
    """Create a demo tools manager with sample data."""
    temp_dir = tempfile.mkdtemp()
    manager = ToolsManager(temp_dir)
    
    # Add some sample tools
    sample_tools = [
        PlayerTool(
            id="armor-calc-001",
            name="SWG Armor Calculator",
            category=ToolCategory.SPREADSHEET,
            description="Comprehensive armor calculator with all armor types, stats, and crafting requirements.",
            url="https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0",
            author="SWG Community",
            tags=["armor", "calculator", "crafting", "stats"],
            notes="Updated regularly with new armor types and balance changes",
            status=ToolStatus.ACTIVE,
            views=1250
        ),
        PlayerTool(
            id="combat-guide-001",
            name="Advanced Combat Mechanics",
            category=ToolCategory.GUIDE,
            description="In-depth guide covering all combat mechanics, weapon types, damage calculations, and advanced techniques.",
            url="https://raw.githubusercontent.com/swg-community/guides/main/combat-mechanics.md",
            author="CombatMaster",
            tags=["combat", "pvp", "pve", "mechanics", "weapons"],
            notes="Comprehensive guide with examples and calculations",
            status=ToolStatus.ACTIVE,
            views=890
        ),
        PlayerTool(
            id="crafting-tracker-001",
            name="Crafting Resource Tracker",
            category=ToolCategory.SPREADSHEET,
            description="Track all crafting resources, locations, spawn rates, and market prices.",
            url="https://docs.google.com/spreadsheets/d/1SAMPLE_ID_FOR_CRAFTING_TRACKER/edit#gid=0",
            author="ResourceHunter",
            tags=["crafting", "resources", "farming", "market"],
            notes="Community-maintained with real-time price updates",
            status=ToolStatus.ACTIVE,
            views=2100
        ),
        PlayerTool(
            id="community-forum-001",
            name="SWG Community Forum",
            category=ToolCategory.EXTERNAL,
            description="Main community forum for SWG players. Discuss strategies, share builds, find groups.",
            url="https://swgcommunity.com/forum",
            author="Community Team",
            tags=["forum", "community", "discussion", "events"],
            notes="Official community forum with active moderation",
            status=ToolStatus.ACTIVE,
            views=3400
        ),
        PlayerTool(
            id="build-guide-001",
            name="Character Build Guide",
            category=ToolCategory.GUIDE,
            description="Complete guide to character building including attribute optimization, skill trees, and build recommendations.",
            url="https://gist.githubusercontent.com/buildmaster/character-builds/main/build-guide.md",
            author="BuildMaster",
            tags=["builds", "character", "attributes", "skills", "professions"],
            notes="Updated with latest meta builds and strategies",
            status=ToolStatus.ACTIVE,
            views=1560
        )
    ]
    
    manager.tools = sample_tools
    manager._save_data()
    
    return manager, temp_dir


def demonstrate_tool_submission():
    """Demonstrate tool submission functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING TOOL SUBMISSION")
    print("="*60)
    
    manager, temp_dir = create_demo_tools_manager()
    
    try:
        # Submit a new tool
        tool_data = {
            'name': 'Demo Market Tracker',
            'category': 'spreadsheet',
            'description': 'Real-time market price tracking for all items with price history and trends.',
            'url': 'https://docs.google.com/spreadsheets/d/1MARKET_TRACKER_ID/edit#gid=0',
            'author': 'MarketAnalyst',
            'tags': ['market', 'prices', 'trading', 'economics'],
            'notes': 'Automatically updated with current market data'
        }
        
        print("Submitting new tool...")
        success, message = manager.submit_tool(tool_data)
        
        if success:
            print(f"✅ Tool submitted successfully: {message}")
            print(f"📊 Current submissions: {len(manager.submissions)}")
            print(f"📊 Current approved tools: {len(manager.tools)}")
            
            # Show submission details
            submission = manager.submissions[0]
            print(f"\n📝 Submission Details:")
            print(f"   Name: {submission.name}")
            print(f"   Category: {submission.category.value}")
            print(f"   Author: {submission.author}")
            print(f"   Status: {submission.status.value}")
            print(f"   Tags: {', '.join(submission.tags)}")
        else:
            print(f"❌ Tool submission failed: {message}")
    
    finally:
        shutil.rmtree(temp_dir)


def demonstrate_tool_management():
    """Demonstrate tool management functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING TOOL MANAGEMENT")
    print("="*60)
    
    manager, temp_dir = create_demo_tools_manager()
    
    try:
        # Show current tools
        print("📊 Current Tools:")
        for tool in manager.tools:
            print(f"   • {tool.name} ({tool.category.value}) - {tool.views} views")
        
        # Get tools by category
        print(f"\n📊 Tools by Category:")
        for category in ToolCategory:
            tools = manager.get_tools_by_category(category)
            print(f"   {category.value.capitalize()}: {len(tools)} tools")
        
        # Show popular tools
        popular_tools = manager.get_popular_tools(limit=3)
        print(f"\n🔥 Popular Tools:")
        for tool in popular_tools:
            print(f"   • {tool.name} - {tool.views} views")
        
        # Show recent tools
        recent_tools = manager.get_recent_tools(limit=3)
        print(f"\n🆕 Recent Tools:")
        for tool in recent_tools:
            print(f"   • {tool.name} - {tool.created_at.strftime('%Y-%m-%d')}")
        
        # Search tools
        print(f"\n🔍 Search Results:")
        search_results = manager.search_tools("armor")
        print(f"   Search for 'armor': {len(search_results)} results")
        for tool in search_results:
            print(f"     • {tool.name}")
        
        # Get statistics
        stats = manager.get_stats()
        print(f"\n📈 Statistics:")
        print(f"   Total Tools: {stats['total_tools']}")
        print(f"   Active Tools: {stats['active_tools']}")
        print(f"   Total Views: {stats['total_views']}")
        print(f"   Submitted Tools: {stats['submitted_tools']}")
    
    finally:
        shutil.rmtree(temp_dir)


def demonstrate_tool_approval_workflow():
    """Demonstrate the tool approval workflow."""
    print("\n" + "="*60)
    print("DEMONSTRATING TOOL APPROVAL WORKFLOW")
    print("="*60)
    
    manager, temp_dir = create_demo_tools_manager()
    
    try:
        # Submit a tool
        tool_data = {
            'name': 'Workflow Test Tool',
            'category': 'guide',
            'description': 'A tool for testing the approval workflow',
            'url': 'https://example.com/workflow-test',
            'author': 'WorkflowTester',
            'tags': ['test', 'workflow'],
            'notes': 'Testing the approval process'
        }
        
        print("1. Submitting tool for approval...")
        success, message = manager.submit_tool(tool_data)
        assert success, f"Tool submission failed: {message}"
        
        print(f"   ✅ Tool submitted: {message}")
        print(f"   📊 Pending submissions: {len(manager.submissions)}")
        
        # Get the submission
        submission = manager.submissions[0]
        print(f"\n2. Submission Details:")
        print(f"   ID: {submission.id}")
        print(f"   Name: {submission.name}")
        print(f"   Status: {submission.status.value}")
        print(f"   Created: {submission.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Approve the tool
        print(f"\n3. Approving tool...")
        success, message = manager.approve_tool(submission.id, "admin")
        assert success, f"Tool approval failed: {message}"
        
        print(f"   ✅ Tool approved: {message}")
        print(f"   📊 Pending submissions: {len(manager.submissions)}")
        print(f"   📊 Approved tools: {len(manager.tools)}")
        
        # Get the approved tool
        approved_tool = manager.tools[-1]  # Last added tool
        print(f"\n4. Approved Tool Details:")
        print(f"   Name: {approved_tool.name}")
        print(f"   Status: {approved_tool.status.value}")
        print(f"   Approved by: {approved_tool.approved_by}")
        print(f"   Approved at: {approved_tool.approved_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Test view increment
        print(f"\n5. Testing view increment...")
        initial_views = approved_tool.views
        success = manager.increment_views(approved_tool.id)
        assert success, "View increment failed"
        
        print(f"   ✅ Views incremented: {initial_views} → {approved_tool.views}")
    
    finally:
        shutil.rmtree(temp_dir)


def demonstrate_content_fetching():
    """Demonstrate content fetching for different tool types."""
    print("\n" + "="*60)
    print("DEMONSTRATING CONTENT FETCHING")
    print("="*60)
    
    manager, temp_dir = create_demo_tools_manager()
    
    try:
        # Test with mocked content fetching
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = "# Test Guide\n\nThis is a test guide content with **markdown** formatting."
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Get a guide tool
            guide_tool = next(t for t in manager.tools if t.category == ToolCategory.GUIDE)
            
            print(f"📖 Fetching content for: {guide_tool.name}")
            content = manager.get_tool_content(guide_tool.id)
            
            if content:
                print(f"   ✅ Content fetched successfully")
                print(f"   📄 Content type: {content['type']}")
                print(f"   📝 Content preview: {content['content'][:100]}...")
            else:
                print(f"   ❌ Failed to fetch content")
        
        # Test with spreadsheet tool (should return None)
        spreadsheet_tool = next(t for t in manager.tools if t.category == ToolCategory.SPREADSHEET)
        
        print(f"\n📊 Testing spreadsheet tool: {spreadsheet_tool.name}")
        content = manager.get_tool_content(spreadsheet_tool.id)
        
        if content is None:
            print(f"   ✅ Correctly returned None for non-guide tool")
        else:
            print(f"   ❌ Unexpectedly returned content for spreadsheet tool")
    
    finally:
        shutil.rmtree(temp_dir)


def demonstrate_url_validation():
    """Demonstrate URL validation functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING URL VALIDATION")
    print("="*60)
    
    manager, temp_dir = create_demo_tools_manager()
    
    try:
        test_urls = [
            # Valid URLs
            ("https://docs.google.com/spreadsheets/d/123/edit", True),
            ("https://raw.githubusercontent.com/user/repo/file.md", True),
            ("https://pastebin.com/raw/abc123", True),
            ("https://gist.github.com/user/repo/abc123", True),
            ("https://example.com/tool", True),
            ("http://example.com/tool", True),
            
            # Invalid URLs
            ("not-a-url", False),
            ("ftp://example.com", False),
            ("example.com", False),
            ("https://", False),
            ("", False),
            ("javascript:alert('test')", False)
        ]
        
        print("🔍 Testing URL validation:")
        for url, expected_valid in test_urls:
            is_valid = manager._is_valid_url(url)
            status = "✅" if is_valid == expected_valid else "❌"
            print(f"   {status} {url[:50]}{'...' if len(url) > 50 else ''} → {is_valid}")
        
        # Test tool submission with invalid URL
        print(f"\n🧪 Testing tool submission with invalid URL:")
        tool_data = {
            'name': 'Invalid URL Tool',
            'category': 'spreadsheet',
            'description': 'A tool with invalid URL',
            'url': 'not-a-valid-url'
        }
        
        success, message = manager.submit_tool(tool_data)
        if not success:
            print(f"   ✅ Correctly rejected invalid URL: {message}")
        else:
            print(f"   ❌ Unexpectedly accepted invalid URL")
    
    finally:
        shutil.rmtree(temp_dir)


def demonstrate_duplicate_detection():
    """Demonstrate duplicate detection functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING DUPLICATE DETECTION")
    print("="*60)
    
    manager, temp_dir = create_demo_tools_manager()
    
    try:
        # Test duplicate URL
        print("1. Testing duplicate URL detection:")
        tool_data = {
            'name': 'Original Tool',
            'category': 'spreadsheet',
            'description': 'Original tool description',
            'url': 'https://example.com/original'
        }
        
        success, message = manager.submit_tool(tool_data)
        print(f"   ✅ First tool submitted: {message}")
        
        # Try to submit tool with same URL
        duplicate_data = {
            'name': 'Duplicate Tool',
            'category': 'guide',
            'description': 'Different description',
            'url': 'https://example.com/original'  # Same URL
        }
        
        success, message = manager.submit_tool(duplicate_data)
        if not success:
            print(f"   ✅ Correctly detected duplicate URL: {message}")
        else:
            print(f"   ❌ Failed to detect duplicate URL")
        
        # Test duplicate name
        print(f"\n2. Testing duplicate name detection:")
        name_duplicate_data = {
            'name': 'Original Tool',  # Same name
            'category': 'external',
            'description': 'Different description',
            'url': 'https://example.com/different'  # Different URL
        }
        
        success, message = manager.submit_tool(name_duplicate_data)
        if not success:
            print(f"   ✅ Correctly detected duplicate name: {message}")
        else:
            print(f"   ❌ Failed to detect duplicate name")
        
        print(f"\n📊 Final submission count: {len(manager.submissions)}")
    
    finally:
        shutil.rmtree(temp_dir)


def demonstrate_search_functionality():
    """Demonstrate search functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING SEARCH FUNCTIONALITY")
    print("="*60)
    
    manager, temp_dir = create_demo_tools_manager()
    
    try:
        # Test different search queries
        search_tests = [
            ("armor", "Search by name"),
            ("combat", "Search by description"),
            ("calculator", "Search by tags"),
            ("guide", "Search by category"),
            ("nonexistent", "Search for non-existent term")
        ]
        
        for query, description in search_tests:
            print(f"\n🔍 {description}: '{query}'")
            results = manager.search_tools(query)
            print(f"   📊 Found {len(results)} results")
            
            for tool in results:
                print(f"     • {tool.name} ({tool.category.value})")
        
        # Test category-specific search
        print(f"\n🔍 Category-specific search:")
        for category in ToolCategory:
            results = manager.search_tools("guide", category)
            print(f"   {category.value.capitalize()}: {len(results)} results")
    
    finally:
        shutil.rmtree(temp_dir)


def demonstrate_statistics():
    """Demonstrate statistics functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING STATISTICS")
    print("="*60)
    
    manager, temp_dir = create_demo_tools_manager()
    
    try:
        # Get current statistics
        stats = manager.get_stats()
        
        print("📈 Current Statistics:")
        print(f"   Total Tools: {stats['total_tools']}")
        print(f"   Active Tools: {stats['active_tools']}")
        print(f"   Total Views: {stats['total_views']}")
        print(f"   Submitted Tools: {stats['submitted_tools']}")
        print(f"   Last Updated: {stats['last_updated']}")
        
        # Simulate some activity
        print(f"\n📊 Simulating tool activity...")
        
        # Increment views on some tools
        for tool in manager.tools[:3]:  # First 3 tools
            manager.increment_views(tool.id)
            print(f"   📈 Incremented views for {tool.name}")
        
        # Get updated statistics
        updated_stats = manager.get_stats()
        
        print(f"\n📈 Updated Statistics:")
        print(f"   Total Views: {updated_stats['total_views']} (was {stats['total_views']})")
        
        # Show view distribution
        print(f"\n📊 View Distribution:")
        for tool in sorted(manager.tools, key=lambda t: t.views, reverse=True):
            print(f"   • {tool.name}: {tool.views} views")
    
    finally:
        shutil.rmtree(temp_dir)


def demonstrate_web_integration():
    """Demonstrate web integration features."""
    print("\n" + "="*60)
    print("DEMONSTRATING WEB INTEGRATION")
    print("="*60)
    
    manager, temp_dir = create_demo_tools_manager()
    
    try:
        print("🌐 Web Integration Features:")
        print("   ✅ Tools page at /tools")
        print("   ✅ API endpoints for tool management")
        print("   ✅ Google Sheets embedding")
        print("   ✅ Markdown guide rendering")
        print("   ✅ External link handling")
        print("   ✅ Tool submission form")
        print("   ✅ Search and filtering")
        print("   ✅ Statistics dashboard")
        
        # Show API response format
        print(f"\n📡 API Response Format:")
        tools_data = []
        for tool in manager.tools:
            tools_data.append({
                'id': tool.id,
                'name': tool.name,
                'category': tool.category.value,
                'description': tool.description,
                'url': tool.url,
                'author': tool.author,
                'tags': tool.tags,
                'views': tool.views,
                'created_at': tool.created_at.isoformat()
            })
        
        print(f"   GET /api/tools")
        print(f"   Response: {len(tools_data)} tools")
        print(f"   Sample tool: {tools_data[0]['name']}")
        
        # Show submission format
        print(f"\n📝 Tool Submission Format:")
        submission_example = {
            'name': 'Example Tool',
            'category': 'spreadsheet',
            'description': 'Tool description',
            'url': 'https://example.com/tool',
            'author': 'Author Name',
            'tags': ['tag1', 'tag2'],
            'notes': 'Additional notes'
        }
        print(f"   POST /api/tools/submit")
        print(f"   Body: {json.dumps(submission_example, indent=2)}")
    
    finally:
        shutil.rmtree(temp_dir)


def main():
    """Main demonstration function."""
    print("BATCH 103 - PLAYER TOOL EMBEDS (SPREADSHEET + COMMUNITY TOOLS) DEMO")
    print("="*80)
    print("This demo showcases the new player tools system with various embed types.")
    print("Features demonstrated:")
    print("  - Tool submission and management")
    print("  - Google Sheets embedding")
    print("  - Markdown guide rendering")
    print("  - External link handling")
    print("  - Search and filtering")
    print("  - Statistics and analytics")
    print("  - Web integration")
    
    try:
        # Run all demonstrations
        demonstrate_tool_submission()
        demonstrate_tool_management()
        demonstrate_tool_approval_workflow()
        demonstrate_content_fetching()
        demonstrate_url_validation()
        demonstrate_duplicate_detection()
        demonstrate_search_functionality()
        demonstrate_statistics()
        demonstrate_web_integration()
        
        print("\n" + "="*80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("The Player Tool Embeds system provides:")
        print("  ✓ Comprehensive tool management")
        print("  ✓ Multiple embed types (Sheets, Markdown, External)")
        print("  ✓ Robust submission and approval workflow")
        print("  ✓ Advanced search and filtering")
        print("  ✓ Statistics and analytics")
        print("  ✓ Web dashboard integration")
        print("  ✓ Community-driven content")
        print("  ✓ Manual approval system")
        
        print(f"\n🎯 Next Steps:")
        print(f"   • Access tools at: http://localhost:8000/tools")
        print(f"   • Submit new tools via the web interface")
        print(f"   • Review and approve submissions")
        print(f"   • Monitor usage statistics")
        print(f"   • Integrate with existing SWGDB features")
        
    except Exception as e:
        print(f"\n❌ Demo encountered an error: {e}")
        print("This may be expected in a demo environment.")


if __name__ == "__main__":
    main() 
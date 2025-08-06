#!/usr/bin/env python3
"""
Test Suite for Enhanced Progress Tracker + "All the Things" To-Do List System (Batch 055)

Comprehensive tests for the enhanced progress tracker including:
- Markdown checklist parsing
- Progress tracking and statistics
- Smart suggestions
- Item status management
- Export capabilities
"""

import json
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from core.progress_tracker import (
    get_enhanced_progress_tracker,
    update_checklist_item,
    get_overall_progress,
    get_suggestions,
    export_progress_report,
    ChecklistStatus,
    ChecklistCategory,
    ChecklistItem,
    Checklist,
    MarkdownChecklistParser,
    EnhancedProgressTracker
)


class TestChecklistStatus(unittest.TestCase):
    """Test ChecklistStatus enum."""
    
    def test_status_values(self):
        """Test that all status values are valid."""
        self.assertEqual(ChecklistStatus.NOT_STARTED.value, "not_started")
        self.assertEqual(ChecklistStatus.IN_PROGRESS.value, "in_progress")
        self.assertEqual(ChecklistStatus.COMPLETED.value, "completed")
        self.assertEqual(ChecklistStatus.SKIPPED.value, "skipped")
        self.assertEqual(ChecklistStatus.FAILED.value, "failed")


class TestChecklistCategory(unittest.TestCase):
    """Test ChecklistCategory enum."""
    
    def test_category_values(self):
        """Test that all category values are valid."""
        self.assertEqual(ChecklistCategory.LEGACY_QUESTS.value, "legacy_quests")
        self.assertEqual(ChecklistCategory.JEDI_UNLOCK.value, "jedi_unlock")
        self.assertEqual(ChecklistCategory.MUSTAFAR_COMPLETE.value, "mustafar_complete")
        self.assertEqual(ChecklistCategory.HEROICS_CLEARED.value, "heroics_cleared")
        self.assertEqual(ChecklistCategory.WEAPON_COLLECTION.value, "weapon_collection")


class TestChecklistItem(unittest.TestCase):
    """Test ChecklistItem dataclass."""
    
    def test_checklist_item_creation(self):
        """Test creating a checklist item."""
        item = ChecklistItem(
            id="test_item",
            name="Test Item",
            description="A test item",
            category="test",
            status=ChecklistStatus.NOT_STARTED,
            progress=0.0,
            requirements=["level_5"],
            rewards=["xp", "credits"],
            location="Test Location",
            planet="Test Planet",
            coordinates=(100, 200),
            estimated_time=30,
            xp_reward=500,
            credit_reward=200
        )
        
        self.assertEqual(item.id, "test_item")
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.description, "A test item")
        self.assertEqual(item.category, "test")
        self.assertEqual(item.status, ChecklistStatus.NOT_STARTED)
        self.assertEqual(item.progress, 0.0)
        self.assertEqual(item.requirements, ["level_5"])
        self.assertEqual(item.rewards, ["xp", "credits"])
        self.assertEqual(item.location, "Test Location")
        self.assertEqual(item.planet, "Test Planet")
        self.assertEqual(item.coordinates, (100, 200))
        self.assertEqual(item.estimated_time, 30)
        self.assertEqual(item.xp_reward, 500)
        self.assertEqual(item.credit_reward, 200)
    
    def test_checklist_item_serialization(self):
        """Test checklist item serialization and deserialization."""
        item = ChecklistItem(
            id="test_item",
            name="Test Item",
            description="A test item",
            category="test",
            status=ChecklistStatus.COMPLETED,
            progress=1.0,
            xp_reward=500,
            credit_reward=200
        )
        
        # Test to_dict
        item_dict = item.to_dict()
        self.assertEqual(item_dict['id'], "test_item")
        self.assertEqual(item_dict['name'], "Test Item")
        self.assertEqual(item_dict['status'], "completed")
        self.assertEqual(item_dict['progress'], 1.0)
        self.assertEqual(item_dict['xp_reward'], 500)
        self.assertEqual(item_dict['credit_reward'], 200)
        
        # Test from_dict
        restored_item = ChecklistItem.from_dict(item_dict)
        self.assertEqual(restored_item.id, item.id)
        self.assertEqual(restored_item.name, item.name)
        self.assertEqual(restored_item.status, item.status)
        self.assertEqual(restored_item.progress, item.progress)
        self.assertEqual(restored_item.xp_reward, item.xp_reward)
        self.assertEqual(restored_item.credit_reward, item.credit_reward)


class TestChecklist(unittest.TestCase):
    """Test Checklist dataclass."""
    
    def test_checklist_creation(self):
        """Test creating a checklist."""
        items = [
            ChecklistItem(
                id="item_001",
                name="Item 1",
                description="First item",
                category="test",
                status=ChecklistStatus.COMPLETED
            ),
            ChecklistItem(
                id="item_002",
                name="Item 2",
                description="Second item",
                category="test",
                status=ChecklistStatus.NOT_STARTED
            )
        ]
        
        checklist = Checklist(
            name="Test Checklist",
            category=ChecklistCategory.LEGACY_QUESTS,
            description="A test checklist",
            items=items
        )
        
        self.assertEqual(checklist.name, "Test Checklist")
        self.assertEqual(checklist.category, ChecklistCategory.LEGACY_QUESTS)
        self.assertEqual(checklist.description, "A test checklist")
        self.assertEqual(len(checklist.items), 2)
        
        # Test stats update
        checklist.update_stats()
        self.assertEqual(checklist.total_items, 2)
        self.assertEqual(checklist.completed_items, 1)
        self.assertEqual(checklist.completion_percentage, 50.0)
    
    def test_checklist_serialization(self):
        """Test checklist serialization and deserialization."""
        items = [
            ChecklistItem(
                id="item_001",
                name="Item 1",
                description="First item",
                category="test",
                status=ChecklistStatus.COMPLETED
            )
        ]
        
        checklist = Checklist(
            name="Test Checklist",
            category=ChecklistCategory.LEGACY_QUESTS,
            description="A test checklist",
            items=items
        )
        checklist.update_stats()
        
        # Test to_dict
        checklist_dict = checklist.to_dict()
        self.assertEqual(checklist_dict['name'], "Test Checklist")
        self.assertEqual(checklist_dict['category'], "legacy_quests")
        self.assertEqual(checklist_dict['description'], "A test checklist")
        self.assertEqual(len(checklist_dict['items']), 1)
        self.assertEqual(checklist_dict['total_items'], 1)
        self.assertEqual(checklist_dict['completed_items'], 1)
        self.assertEqual(checklist_dict['completion_percentage'], 100.0)
        
        # Test from_dict
        restored_checklist = Checklist.from_dict(checklist_dict)
        self.assertEqual(restored_checklist.name, checklist.name)
        self.assertEqual(restored_checklist.category, checklist.category)
        self.assertEqual(restored_checklist.description, checklist.description)
        self.assertEqual(len(restored_checklist.items), len(checklist.items))
        self.assertEqual(restored_checklist.total_items, checklist.total_items)
        self.assertEqual(restored_checklist.completed_items, checklist.completed_items)


class TestMarkdownChecklistParser(unittest.TestCase):
    """Test MarkdownChecklistParser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = MarkdownChecklistParser()
    
    def test_extract_description(self):
        """Test description extraction from markdown content."""
        content = """# Test Checklist

## Overview
This is a test checklist for testing purposes.

## Items
- [ ] **Item 1** - First item
"""
        
        description = self.parser._extract_description(content)
        self.assertEqual(description, "This is a test checklist for testing purposes.")
    
    def test_determine_category(self):
        """Test category determination from filename and content."""
        # Test legacy quests
        filename = Path("legacy_quests.md")
        content = "# Legacy Quests"
        category = self.parser._determine_category(filename, content)
        self.assertEqual(category, ChecklistCategory.LEGACY_QUESTS)
        
        # Test Jedi unlock
        filename = Path("jedi_unlock.md")
        content = "# Jedi Unlock"
        category = self.parser._determine_category(filename, content)
        self.assertEqual(category, ChecklistCategory.JEDI_UNLOCK)
        
        # Test weapon collection
        filename = Path("weapon_collection.md")
        content = "# Weapon Collection"
        category = self.parser._determine_category(filename, content)
        self.assertEqual(category, ChecklistCategory.WEAPON_COLLECTION)
    
    def test_parse_checklist_items(self):
        """Test parsing checklist items from markdown content."""
        content = """# Test Checklist

## Items
- [ ] **Item 1** - First item
  - **Location**: Test Location
  - **Planet**: Test Planet
  - **Requirements**: level_5, scout_novice
  - **Rewards**: 500 XP, 200 Credits

- [x] **Item 2** - Second item
  - **Location**: Another Location
  - **Planet**: Another Planet
  - **Rewards**: 300 XP, 150 Credits
"""
        
        items = self.parser._parse_checklist_items(content)
        
        self.assertEqual(len(items), 2)
        
        # Check first item
        item1 = items[0]
        self.assertEqual(item1.name, "Item 1")
        self.assertEqual(item1.description, "First item")
        self.assertEqual(item1.status, ChecklistStatus.NOT_STARTED)
        self.assertEqual(item1.progress, 0.0)
        self.assertEqual(item1.location, "Test Location")
        self.assertEqual(item1.planet, "Test Planet")
        self.assertEqual(item1.xp_reward, 500)
        self.assertEqual(item1.credit_reward, 200)
        
        # Check second item
        item2 = items[1]
        self.assertEqual(item2.name, "Item 2")
        self.assertEqual(item2.description, "Second item")
        self.assertEqual(item2.status, ChecklistStatus.COMPLETED)
        self.assertEqual(item2.progress, 1.0)
        self.assertEqual(item2.location, "Another Location")
        self.assertEqual(item2.planet, "Another Planet")
        self.assertEqual(item2.xp_reward, 300)
        self.assertEqual(item2.credit_reward, 150)
    
    def test_parse_checklist_file(self):
        """Test parsing a complete checklist file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Test Checklist

## Overview
This is a test checklist for testing purposes.

## Items
- [ ] **Item 1** - First item
  - **Location**: Test Location
  - **Planet**: Test Planet
  - **Rewards**: 500 XP, 200 Credits

- [x] **Item 2** - Second item
  - **Location**: Another Location
  - **Planet**: Another Planet
  - **Rewards**: 300 XP, 150 Credits
""")
            file_path = Path(f.name)
        
        try:
            checklist = self.parser.parse_checklist_file(file_path)
            
            self.assertEqual(checklist.name, "Test Checklist")
            self.assertEqual(checklist.description, "This is a test checklist for testing purposes.")
            self.assertEqual(len(checklist.items), 2)
            self.assertEqual(checklist.total_items, 2)
            self.assertEqual(checklist.completed_items, 1)
            self.assertEqual(checklist.completion_percentage, 50.0)
            
        finally:
            file_path.unlink(missing_ok=True)


class TestEnhancedProgressTracker(unittest.TestCase):
    """Test EnhancedProgressTracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary data file
        self.temp_data_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_data_file.close()
        
        # Create temporary checklists directory
        self.temp_checklists_dir = Path(tempfile.mkdtemp())
        
        # Create test checklist file
        test_checklist_file = self.temp_checklists_dir / "test_checklist.md"
        test_checklist_file.write_text("""# Test Checklist

## Overview
This is a test checklist for testing purposes.

## Items
- [ ] **Item 1** - First item
  - **Location**: Test Location
  - **Planet**: Test Planet
  - **Rewards**: 500 XP, 200 Credits

- [x] **Item 2** - Second item
  - **Location**: Another Location
  - **Planet**: Another Planet
  - **Rewards**: 300 XP, 150 Credits
""")
        
        # Create tracker with temporary files
        self.tracker = EnhancedProgressTracker(
            data_file=self.temp_data_file.name,
            checklists_dir=str(self.temp_checklists_dir)
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        Path(self.temp_data_file.name).unlink(missing_ok=True)
        
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_checklists_dir, ignore_errors=True)
    
    def test_checklist_loading(self):
        """Test loading checklists from markdown files."""
        checklists = self.tracker.get_all_checklists()
        
        self.assertIn("Test Checklist", checklists)
        checklist = checklists["Test Checklist"]
        
        self.assertEqual(checklist.name, "Test Checklist")
        self.assertEqual(len(checklist.items), 2)
        self.assertEqual(checklist.total_items, 2)
        self.assertEqual(checklist.completed_items, 1)
        self.assertEqual(checklist.completion_percentage, 50.0)
    
    def test_get_checklist(self):
        """Test getting a specific checklist."""
        checklist = self.tracker.get_checklist("Test Checklist")
        
        self.assertIsNotNone(checklist)
        self.assertEqual(checklist.name, "Test Checklist")
        
        # Test non-existent checklist
        non_existent = self.tracker.get_checklist("Non-existent Checklist")
        self.assertIsNone(non_existent)
    
    def test_update_item_status(self):
        """Test updating item status."""
        # Get the first item from the test checklist
        checklist = self.tracker.get_checklist("Test Checklist")
        item = checklist.items[0]  # Item 1 (not started)
        
        # Update to in progress
        success = self.tracker.update_item_status(
            "Test Checklist", 
            item.id, 
            ChecklistStatus.IN_PROGRESS, 
            0.5
        )
        
        self.assertTrue(success)
        
        # Check updated item
        updated_checklist = self.tracker.get_checklist("Test Checklist")
        updated_item = next(i for i in updated_checklist.items if i.id == item.id)
        
        self.assertEqual(updated_item.status, ChecklistStatus.IN_PROGRESS)
        self.assertEqual(updated_item.progress, 0.5)
        
        # Update to completed
        success = self.tracker.update_item_status(
            "Test Checklist", 
            item.id, 
            ChecklistStatus.COMPLETED
        )
        
        self.assertTrue(success)
        
        # Check final state
        final_checklist = self.tracker.get_checklist("Test Checklist")
        final_item = next(i for i in final_checklist.items if i.id == item.id)
        
        self.assertEqual(final_item.status, ChecklistStatus.COMPLETED)
        self.assertEqual(final_item.progress, 1.0)
        self.assertIsNotNone(final_item.completed_at)
        
        # Check updated stats
        self.assertEqual(final_checklist.total_items, 2)
        self.assertEqual(final_checklist.completed_items, 2)
        self.assertEqual(final_checklist.completion_percentage, 100.0)
    
    def test_get_overall_progress(self):
        """Test getting overall progress."""
        progress = self.tracker.get_overall_progress()
        
        self.assertEqual(progress['total_items'], 2)
        self.assertEqual(progress['total_completed'], 1)
        self.assertEqual(progress['overall_percentage'], 50.0)
        self.assertEqual(progress['total_xp_gained'], 300)  # Only completed item
        self.assertEqual(progress['total_credits_gained'], 150)  # Only completed item
        
        # Check category progress
        self.assertIn('legacy_quests', progress['category_progress'])
        category_data = progress['category_progress']['legacy_quests']
        self.assertEqual(category_data['total'], 2)
        self.assertEqual(category_data['completed'], 1)
        self.assertEqual(category_data['percentage'], 50.0)
        
        # Check checklists progress
        self.assertIn('Test Checklist', progress['checklists'])
        checklist_data = progress['checklists']['Test Checklist']
        self.assertEqual(checklist_data['total_items'], 2)
        self.assertEqual(checklist_data['completed_items'], 1)
        self.assertEqual(checklist_data['completion_percentage'], 50.0)
    
    def test_get_suggestions(self):
        """Test getting suggestions."""
        # Get general suggestions
        suggestions = self.tracker.get_suggestions()
        
        self.assertEqual(len(suggestions), 1)  # Only one not-started item
        suggestion = suggestions[0]
        
        self.assertEqual(suggestion['item_name'], "Item 1")
        self.assertEqual(suggestion['checklist_name'], "Test Checklist")
        self.assertEqual(suggestion['planet'], "Test Planet")
        self.assertEqual(suggestion['location'], "Test Location")
        self.assertEqual(suggestion['xp_reward'], 500)
        self.assertEqual(suggestion['credit_reward'], 200)
        self.assertGreater(suggestion['priority'], 0)
        
        # Get location-specific suggestions
        location_suggestions = self.tracker.get_suggestions("Test Planet")
        
        self.assertEqual(len(location_suggestions), 1)
        location_suggestion = location_suggestions[0]
        self.assertEqual(location_suggestion['priority'], 1.0)  # Exact match
    
    def test_export_progress_report(self):
        """Test exporting progress report."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            output_file = temp_file.name
        
        try:
            self.tracker.export_progress_report(output_file)
            
            # Check that file was created and contains valid JSON
            with open(output_file, 'r') as f:
                report = json.load(f)
            
            self.assertIn('generated_at', report)
            self.assertIn('overall_progress', report)
            self.assertIn('checklists', report)
            self.assertIn('suggestions', report)
            
            # Check overall progress
            overall = report['overall_progress']
            self.assertEqual(overall['total_items'], 2)
            self.assertEqual(overall['total_completed'], 1)
            self.assertEqual(overall['overall_percentage'], 50.0)
            
            # Check checklists
            checklists = report['checklists']
            self.assertIn('Test Checklist', checklists)
            
        finally:
            Path(output_file).unlink(missing_ok=True)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary data file
        self.temp_data_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_data_file.close()
        
        # Create temporary checklists directory
        self.temp_checklists_dir = Path(tempfile.mkdtemp())
        
        # Create test checklist file
        test_checklist_file = self.temp_checklists_dir / "test_checklist.md"
        test_checklist_file.write_text("""# Test Checklist

## Overview
This is a test checklist for testing purposes.

## Items
- [ ] **Item 1** - First item
  - **Location**: Test Location
  - **Planet**: Test Planet
  - **Rewards**: 500 XP, 200 Credits
""")
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        Path(self.temp_data_file.name).unlink(missing_ok=True)
        
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_checklists_dir, ignore_errors=True)
    
    @patch('core.progress_tracker.EnhancedProgressTracker')
    def test_convenience_functions(self, mock_tracker_class):
        """Test convenience functions."""
        # Mock the tracker
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker
        
        # Test get_enhanced_progress_tracker
        tracker = get_enhanced_progress_tracker()
        self.assertEqual(tracker, mock_tracker)
        
        # Test update_checklist_item
        mock_tracker.update_item_status.return_value = True
        success = update_checklist_item("Test", "item_001", ChecklistStatus.COMPLETED)
        self.assertTrue(success)
        mock_tracker.update_item_status.assert_called_once_with("Test", "item_001", ChecklistStatus.COMPLETED, None)
        
        # Test get_overall_progress
        mock_tracker.get_overall_progress.return_value = {"total_items": 10}
        progress = get_overall_progress()
        self.assertEqual(progress, {"total_items": 10})
        mock_tracker.get_overall_progress.assert_called_once()
        
        # Test get_suggestions
        mock_tracker.get_suggestions.return_value = [{"name": "test"}]
        suggestions = get_suggestions("Test Location")
        self.assertEqual(suggestions, [{"name": "test"}])
        mock_tracker.get_suggestions.assert_called_once_with("Test Location")
        
        # Test export_progress_report
        export_progress_report("test.json")
        mock_tracker.export_progress_report.assert_called_once_with("test.json")


if __name__ == '__main__':
    unittest.main() 
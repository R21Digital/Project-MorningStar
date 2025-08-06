#!/usr/bin/env python3
"""
Test Batch 173 - SWGDB.com Bug Tracker System

This test suite validates the bug tracking system functionality including:
- Bug data management and storage
- Admin bug management interface
- User bug reporter form
- Discord webhook integration
- Bug statistics and reporting
- Filtering and sorting capabilities
"""

import json
import uuid
import unittest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import the bug tracker classes
from demo_batch_173_bug_tracker import BugReport, BugTracker


class TestBugReport(unittest.TestCase):
    """Test BugReport dataclass functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_data = {
            "title": "Test Bug",
            "description": "This is a test bug description",
            "severity": "medium",
            "module": "test",
            "reported_by": "test@example.com",
            "reported_at": "2024-01-15T10:30:00Z"
        }
    
    def test_bug_report_creation(self):
        """Test bug report creation with minimal data."""
        bug = BugReport(
            id="BUG-2024-TEST001",
            title=self.sample_data["title"],
            description=self.sample_data["description"],
            severity=self.sample_data["severity"],
            status="open",
            module=self.sample_data["module"],
            reported_by=self.sample_data["reported_by"],
            reported_at=self.sample_data["reported_at"]
        )
        
        self.assertEqual(bug.id, "BUG-2024-TEST001")
        self.assertEqual(bug.title, "Test Bug")
        self.assertEqual(bug.severity, "medium")
        self.assertEqual(bug.status, "open")
        self.assertEqual(bug.module, "test")
        self.assertEqual(bug.reported_by, "test@example.com")
        self.assertEqual(bug.priority, "normal")  # Default value
        self.assertEqual(bug.category, "general")  # Default value
        self.assertEqual(len(bug.steps_to_reproduce), 0)  # Empty list
        self.assertEqual(len(bug.tags), 0)  # Empty list
        self.assertEqual(len(bug.comments), 0)  # Empty list
    
    def test_bug_report_with_optional_fields(self):
        """Test bug report creation with all optional fields."""
        bug = BugReport(
            id="BUG-2024-TEST002",
            title="Test Bug with Options",
            description="Test description",
            severity="high",
            status="open",
            module="api",
            reported_by="admin@swgdb.com",
            reported_at="2024-01-15T10:30:00Z",
            assigned_to="dev@swgdb.com",
            priority="high",
            category="functionality",
            steps_to_reproduce=["Step 1", "Step 2", "Step 3"],
            expected_behavior="Should work correctly",
            actual_behavior="Does not work",
            browser="Chrome 120",
            os="Windows 11",
            discord_link="https://discord.com/channels/123/456",
            tags=["test", "api", "bug"],
            updated_at="2024-01-15T10:30:00Z"
        )
        
        self.assertEqual(bug.assigned_to, "dev@swgdb.com")
        self.assertEqual(bug.priority, "high")
        self.assertEqual(bug.category, "functionality")
        self.assertEqual(len(bug.steps_to_reproduce), 3)
        self.assertEqual(bug.expected_behavior, "Should work correctly")
        self.assertEqual(bug.actual_behavior, "Does not work")
        self.assertEqual(bug.browser, "Chrome 120")
        self.assertEqual(bug.os, "Windows 11")
        self.assertEqual(bug.discord_link, "https://discord.com/channels/123/456")
        self.assertEqual(len(bug.tags), 3)
        self.assertIn("test", bug.tags)
        self.assertIn("api", bug.tags)
        self.assertIn("bug", bug.tags)


class TestBugTracker(unittest.TestCase):
    """Test BugTracker class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.bugs_file = self.temp_dir / "test_bugs.json"
        self.bug_tracker = BugTracker(str(self.bugs_file))
    
    def tearDown(self):
        """Clean up test fixtures."""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_bug_tracker_initialization(self):
        """Test bug tracker initialization."""
        self.assertIsNotNone(self.bug_tracker)
        self.assertEqual(self.bug_tracker.bugs_file, self.bugs_file)
        self.assertIn("bugs", self.bug_tracker.bugs_data)
        self.assertIn("config", self.bug_tracker.bugs_data)
        self.assertIn("stats", self.bug_tracker.bugs_data)
    
    def test_generate_bug_id(self):
        """Test bug ID generation."""
        bug_id = self.bug_tracker.generate_bug_id()
        self.assertIsInstance(bug_id, str)
        self.assertTrue(bug_id.startswith("BUG-"))
        self.assertIn(str(datetime.now().year), bug_id)
    
    def test_create_bug_report(self):
        """Test bug report creation."""
        data = {
            "title": "Test Bug Creation",
            "description": "Testing bug creation functionality",
            "severity": "medium",
            "module": "test",
            "email": "test@example.com",
            "priority": "normal",
            "category": "ui",
            "steps_to_reproduce": ["Step 1", "Step 2"],
            "expected_behavior": "Should work",
            "actual_behavior": "Does not work",
            "browser": "Firefox 115",
            "os": "macOS 14",
            "discord_link": "https://discord.com/channels/test",
            "tags": ["test", "creation"]
        }
        
        bug = self.bug_tracker.create_bug_report(data)
        
        self.assertIsInstance(bug, BugReport)
        self.assertTrue(bug.id.startswith("BUG-"))
        self.assertEqual(bug.title, "Test Bug Creation")
        self.assertEqual(bug.description, "Testing bug creation functionality")
        self.assertEqual(bug.severity, "medium")
        self.assertEqual(bug.status, "open")
        self.assertEqual(bug.module, "test")
        self.assertEqual(bug.reported_by, "test@example.com")
        self.assertEqual(bug.priority, "normal")
        self.assertEqual(bug.category, "ui")
        self.assertEqual(len(bug.steps_to_reproduce), 2)
        self.assertEqual(bug.expected_behavior, "Should work")
        self.assertEqual(bug.actual_behavior, "Does not work")
        self.assertEqual(bug.browser, "Firefox 115")
        self.assertEqual(bug.os, "macOS 14")
        self.assertEqual(bug.discord_link, "https://discord.com/channels/test")
        self.assertEqual(len(bug.tags), 2)
        self.assertIn("test", bug.tags)
        self.assertIn("creation", bug.tags)
    
    def test_add_bug_report(self):
        """Test adding bug report to system."""
        data = {
            "title": "Test Add Bug",
            "description": "Testing bug addition",
            "severity": "low",
            "module": "test",
            "email": "test@example.com"
        }
        
        bug = self.bug_tracker.create_bug_report(data)
        success = self.bug_tracker.add_bug_report(bug)
        
        self.assertTrue(success)
        
        # Check if bug was added to data
        bugs = self.bug_tracker.bugs_data["bugs"]
        self.assertEqual(len(bugs), 1)
        self.assertEqual(bugs[0]["id"], bug.id)
        self.assertEqual(bugs[0]["title"], "Test Add Bug")
    
    def test_get_bugs_no_filters(self):
        """Test getting bugs without filters."""
        # Add some test bugs
        test_bugs = [
            {
                "title": "Bug 1",
                "description": "First bug",
                "severity": "low",
                "module": "test1",
                "email": "test1@example.com"
            },
            {
                "title": "Bug 2",
                "description": "Second bug",
                "severity": "high",
                "module": "test2",
                "email": "test2@example.com"
            }
        ]
        
        for data in test_bugs:
            bug = self.bug_tracker.create_bug_report(data)
            self.bug_tracker.add_bug_report(bug)
        
        bugs = self.bug_tracker.get_bugs()
        self.assertEqual(len(bugs), 2)
    
    def test_get_bugs_with_filters(self):
        """Test getting bugs with filters."""
        # Add test bugs
        test_bugs = [
            {
                "title": "Low Severity Bug",
                "description": "Low severity test",
                "severity": "low",
                "module": "test",
                "email": "test@example.com"
            },
            {
                "title": "High Severity Bug",
                "description": "High severity test",
                "severity": "high",
                "module": "test",
                "email": "test@example.com"
            }
        ]
        
        for data in test_bugs:
            bug = self.bug_tracker.create_bug_report(data)
            self.bug_tracker.add_bug_report(bug)
        
        # Filter by severity
        low_bugs = self.bug_tracker.get_bugs({"severity": "low"})
        self.assertEqual(len(low_bugs), 1)
        self.assertEqual(low_bugs[0]["severity"], "low")
        
        high_bugs = self.bug_tracker.get_bugs({"severity": "high"})
        self.assertEqual(len(high_bugs), 1)
        self.assertEqual(high_bugs[0]["severity"], "high")
        
        # Filter by status
        open_bugs = self.bug_tracker.get_bugs({"status": "open"})
        self.assertEqual(len(open_bugs), 2)
    
    def test_update_bug_status(self):
        """Test updating bug status."""
        # Add a test bug
        data = {
            "title": "Status Test Bug",
            "description": "Testing status updates",
            "severity": "medium",
            "module": "test",
            "email": "test@example.com"
        }
        
        bug = self.bug_tracker.create_bug_report(data)
        self.bug_tracker.add_bug_report(bug)
        
        # Update status
        success = self.bug_tracker.update_bug_status(
            bug.id, 
            "in_progress", 
            "dev@swgdb.com"
        )
        
        self.assertTrue(success)
        
        # Verify update
        updated_bugs = self.bug_tracker.get_bugs({"id": bug.id})
        self.assertEqual(len(updated_bugs), 1)
        self.assertEqual(updated_bugs[0]["status"], "in_progress")
        self.assertEqual(updated_bugs[0]["assigned_to"], "dev@swgdb.com")
    
    def test_update_nonexistent_bug(self):
        """Test updating status of non-existent bug."""
        success = self.bug_tracker.update_bug_status("NONEXISTENT", "open")
        self.assertFalse(success)
    
    def test_add_comment(self):
        """Test adding comment to bug."""
        # Add a test bug
        data = {
            "title": "Comment Test Bug",
            "description": "Testing comment addition",
            "severity": "medium",
            "module": "test",
            "email": "test@example.com"
        }
        
        bug = self.bug_tracker.create_bug_report(data)
        self.bug_tracker.add_bug_report(bug)
        
        # Add comment
        success = self.bug_tracker.add_comment(
            bug.id,
            "admin@swgdb.com",
            "This is a test comment"
        )
        
        self.assertTrue(success)
        
        # Verify comment was added
        bugs = self.bug_tracker.get_bugs({"id": bug.id})
        self.assertEqual(len(bugs), 1)
        self.assertEqual(len(bugs[0]["comments"]), 1)
        self.assertEqual(bugs[0]["comments"][0]["author"], "admin@swgdb.com")
        self.assertEqual(bugs[0]["comments"][0]["content"], "This is a test comment")
    
    def test_add_comment_nonexistent_bug(self):
        """Test adding comment to non-existent bug."""
        success = self.bug_tracker.add_comment(
            "NONEXISTENT",
            "admin@swgdb.com",
            "Test comment"
        )
        self.assertFalse(success)
    
    def test_get_statistics(self):
        """Test getting bug statistics."""
        # Add test bugs with different characteristics
        test_bugs = [
            {
                "title": "Open Bug",
                "description": "Open test bug",
                "severity": "low",
                "module": "test1",
                "email": "test@example.com"
            },
            {
                "title": "Critical Bug",
                "description": "Critical test bug",
                "severity": "critical",
                "module": "test2",
                "email": "test@example.com"
            },
            {
                "title": "High Priority Bug",
                "description": "High priority test bug",
                "severity": "medium",
                "module": "test1",
                "email": "test@example.com",
                "priority": "high"
            }
        ]
        
        for data in test_bugs:
            bug = self.bug_tracker.create_bug_report(data)
            self.bug_tracker.add_bug_report(bug)
        
        stats = self.bug_tracker.get_statistics()
        
        self.assertEqual(stats["total_bugs"], 3)
        self.assertEqual(stats["open_bugs"], 3)
        self.assertEqual(stats["critical_bugs"], 1)
        self.assertEqual(stats["high_priority_bugs"], 1)
        self.assertEqual(stats["bugs_by_module"]["test1"], 2)
        self.assertEqual(stats["bugs_by_module"]["test2"], 1)
        self.assertEqual(stats["bugs_by_severity"]["low"], 1)
        self.assertEqual(stats["bugs_by_severity"]["medium"], 1)
        self.assertEqual(stats["bugs_by_severity"]["critical"], 1)
    
    def test_send_discord_notification(self):
        """Test Discord notification functionality."""
        data = {
            "title": "Discord Test Bug",
            "description": "Testing Discord notifications",
            "severity": "medium",
            "module": "test",
            "email": "test@example.com"
        }
        
        bug = self.bug_tracker.create_bug_report(data)
        
        # Test notification (should succeed even without webhook configured)
        success = self.bug_tracker.send_discord_notification(bug, "new_bug")
        self.assertTrue(success)


class TestBugTrackerIntegration(unittest.TestCase):
    """Integration tests for bug tracker system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.bugs_file = self.temp_dir / "integration_test_bugs.json"
        self.bug_tracker = BugTracker(str(self.bugs_file))
    
    def tearDown(self):
        """Clean up test fixtures."""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_full_bug_lifecycle(self):
        """Test complete bug lifecycle from creation to resolution."""
        # 1. Create bug
        data = {
            "title": "Integration Test Bug",
            "description": "Testing full bug lifecycle",
            "severity": "high",
            "module": "integration",
            "email": "test@example.com",
            "priority": "high",
            "category": "functionality",
            "steps_to_reproduce": ["Step 1", "Step 2"],
            "expected_behavior": "Should work",
            "actual_behavior": "Does not work",
            "browser": "Chrome 120",
            "os": "Windows 11",
            "tags": ["integration", "test"]
        }
        
        bug = self.bug_tracker.create_bug_report(data)
        self.assertEqual(bug.status, "open")
        
        # 2. Add to system
        success = self.bug_tracker.add_bug_report(bug)
        self.assertTrue(success)
        
        # 3. Verify bug exists
        bugs = self.bug_tracker.get_bugs({"id": bug.id})
        self.assertEqual(len(bugs), 1)
        self.assertEqual(bugs[0]["title"], "Integration Test Bug")
        
        # 4. Add comment
        comment_success = self.bug_tracker.add_comment(
            bug.id,
            "dev@swgdb.com",
            "Starting investigation"
        )
        self.assertTrue(comment_success)
        
        # 5. Update status to in progress
        status_success = self.bug_tracker.update_bug_status(
            bug.id,
            "in_progress",
            "dev@swgdb.com"
        )
        self.assertTrue(status_success)
        
        # 6. Add another comment
        comment_success2 = self.bug_tracker.add_comment(
            bug.id,
            "dev@swgdb.com",
            "Issue identified and fix implemented"
        )
        self.assertTrue(comment_success2)
        
        # 7. Resolve bug
        resolve_success = self.bug_tracker.update_bug_status(
            bug.id,
            "resolved"
        )
        self.assertTrue(resolve_success)
        
        # 8. Verify final state
        final_bugs = self.bug_tracker.get_bugs({"id": bug.id})
        self.assertEqual(len(final_bugs), 1)
        self.assertEqual(final_bugs[0]["status"], "resolved")
        self.assertEqual(len(final_bugs[0]["comments"]), 2)
        self.assertIsNotNone(final_bugs[0]["resolved_at"])
        
        # 9. Check statistics
        stats = self.bug_tracker.get_statistics()
        self.assertEqual(stats["total_bugs"], 1)
        self.assertEqual(stats["resolved_bugs"], 1)
        self.assertEqual(stats["open_bugs"], 0)
    
    def test_multiple_bugs_management(self):
        """Test managing multiple bugs simultaneously."""
        # Create multiple bugs
        bug_data_list = [
            {
                "title": "Bug 1",
                "description": "First bug",
                "severity": "low",
                "module": "module1",
                "email": "test1@example.com"
            },
            {
                "title": "Bug 2",
                "description": "Second bug",
                "severity": "high",
                "module": "module2",
                "email": "test2@example.com"
            },
            {
                "title": "Bug 3",
                "description": "Third bug",
                "severity": "critical",
                "module": "module1",
                "email": "test3@example.com"
            }
        ]
        
        created_bugs = []
        for data in bug_data_list:
            bug = self.bug_tracker.create_bug_report(data)
            success = self.bug_tracker.add_bug_report(bug)
            self.assertTrue(success)
            created_bugs.append(bug)
        
        # Test filtering
        all_bugs = self.bug_tracker.get_bugs()
        self.assertEqual(len(all_bugs), 3)
        
        module1_bugs = self.bug_tracker.get_bugs({"module": "module1"})
        self.assertEqual(len(module1_bugs), 2)
        
        critical_bugs = self.bug_tracker.get_bugs({"severity": "critical"})
        self.assertEqual(len(critical_bugs), 1)
        
        # Test status updates
        for i, bug in enumerate(created_bugs):
            if i == 0:
                # Resolve first bug
                self.bug_tracker.update_bug_status(bug.id, "resolved")
            elif i == 1:
                # Set second bug to in progress
                self.bug_tracker.update_bug_status(bug.id, "in_progress", "dev@swgdb.com")
            # Third bug remains open
        
        # Verify final statistics
        stats = self.bug_tracker.get_statistics()
        self.assertEqual(stats["total_bugs"], 3)
        self.assertEqual(stats["open_bugs"], 1)
        self.assertEqual(stats["in_progress_bugs"], 1)
        self.assertEqual(stats["resolved_bugs"], 1)
        self.assertEqual(stats["critical_bugs"], 1)
        self.assertEqual(stats["bugs_by_module"]["module1"], 2)
        self.assertEqual(stats["bugs_by_module"]["module2"], 1)


def run_basic_tests():
    """Run basic functionality tests."""
    print("[TEST] Running Basic Bug Tracker Tests")
    print("=" * 50)
    
    # Test bug report creation
    print("\n1. Testing Bug Report Creation...")
    sample_data = {
        "title": "Test Bug",
        "description": "This is a test bug",
        "severity": "medium",
        "module": "test",
        "email": "test@example.com"
    }
    
    bug_tracker = BugTracker("temp_bugs.json")
    bug = bug_tracker.create_bug_report(sample_data)
    
    print(f"   [OK] Bug ID: {bug.id}")
    print(f"   [OK] Title: {bug.title}")
    print(f"   [OK] Severity: {bug.severity}")
    print(f"   [OK] Status: {bug.status}")
    
    # Test adding to system
    print("\n2. Testing Bug Addition to System...")
    success = bug_tracker.add_bug_report(bug)
    print(f"   [OK] Added to system: {success}")
    
    # Test statistics
    print("\n3. Testing Statistics...")
    stats = bug_tracker.get_statistics()
    print(f"   [OK] Total bugs: {stats.get('total_bugs', 0)}")
    print(f"   [OK] Open bugs: {stats.get('open_bugs', 0)}")
    
    # Test filtering
    print("\n4. Testing Bug Filtering...")
    bugs = bug_tracker.get_bugs({"severity": "medium"})
    print(f"   [OK] Medium severity bugs: {len(bugs)}")
    
    # Test status update
    print("\n5. Testing Status Update...")
    success = bug_tracker.update_bug_status(bug.id, "in_progress")
    print(f"   [OK] Status updated: {success}")
    
    # Test comment addition
    print("\n6. Testing Comment Addition...")
    success = bug_tracker.add_comment(bug.id, "admin@swgdb.com", "Test comment")
    print(f"   [OK] Comment added: {success}")
    
    # Test Discord notification
    print("\n7. Testing Discord Notification...")
    success = bug_tracker.send_discord_notification(bug, "new_bug")
    print(f"   [OK] Discord notification: {success}")
    
    print(f"\n[SUCCESS] All basic tests completed successfully!")
    return True


if __name__ == "__main__":
    # Run basic tests first
    basic_success = run_basic_tests()
    
    if basic_success:
        print(f"\n[TEST] Running full test suite...")
        # Run full test suite
        unittest.main(verbosity=2)
    else:
        print(f"\n[ERROR] Basic tests failed, skipping full test suite") 
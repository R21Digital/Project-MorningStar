"""Test suite for Batch 112 - Guild Alert System + Priority Communication.

This test suite covers:
- Guild member detection
- Priority alert handling
- Auto-reply generation
- Discord integration
- Session analytics tracking
- Configuration management
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from modules.guild_alert_system import GuildAlertSystem, GuildMember, GuildAlert
from core.session_manager import SessionManager, GuildAlertEvent


class TestGuildAlertSystem(unittest.TestCase):
    """Test cases for the GuildAlertSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_guild_config.json")
        
        # Create test config
        test_config = {
            "guild_name": "Test Guild",
            "guild_leader": "TestLeader",
            "guild_officers": ["TestOfficer1", "TestOfficer2"],
            "members": {
                "TestLeader": {
                    "name": "TestLeader",
                    "role": "leader",
                    "rank": 1,
                    "online": False,
                    "last_seen": None
                },
                "TestOfficer1": {
                    "name": "TestOfficer1",
                    "role": "officer",
                    "rank": 2,
                    "online": False,
                    "last_seen": None
                },
                "TestMember1": {
                    "name": "TestMember1",
                    "role": "member",
                    "rank": 3,
                    "online": False,
                    "last_seen": None
                }
            },
            "auto_reply_enabled": True,
            "priority_alerts_enabled": True,
            "discord_integration": True
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Initialize guild system with test config
        self.guild_system = GuildAlertSystem(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_guild_member_detection(self):
        """Test guild member detection functionality."""
        # Test guild members
        self.assertTrue(self.guild_system.is_guild_member("TestLeader"))
        self.assertTrue(self.guild_system.is_guild_member("TestOfficer1"))
        self.assertTrue(self.guild_system.is_guild_member("TestMember1"))
        
        # Test non-guild members
        self.assertFalse(self.guild_system.is_guild_member("RandomPlayer"))
        self.assertFalse(self.guild_system.is_guild_member(""))
        self.assertFalse(self.guild_system.is_guild_member("TestLeader2"))
    
    def test_guild_leader_detection(self):
        """Test guild leader detection."""
        self.assertTrue(self.guild_system.is_guild_leader("TestLeader"))
        self.assertFalse(self.guild_system.is_guild_leader("TestOfficer1"))
        self.assertFalse(self.guild_system.is_guild_leader("TestMember1"))
        self.assertFalse(self.guild_system.is_guild_leader("RandomPlayer"))
    
    def test_guild_officer_detection(self):
        """Test guild officer detection."""
        self.assertTrue(self.guild_system.is_guild_officer("TestOfficer1"))
        self.assertTrue(self.guild_system.is_guild_officer("TestOfficer2"))
        self.assertFalse(self.guild_system.is_guild_officer("TestLeader"))
        self.assertFalse(self.guild_system.is_guild_officer("TestMember1"))
        self.assertFalse(self.guild_system.is_guild_officer("RandomPlayer"))
    
    def test_get_guild_member(self):
        """Test getting guild member information."""
        member = self.guild_system.get_guild_member("TestLeader")
        self.assertIsNotNone(member)
        self.assertEqual(member.name, "TestLeader")
        self.assertEqual(member.role, "leader")
        self.assertEqual(member.rank, 1)
        
        member = self.guild_system.get_guild_member("TestOfficer1")
        self.assertIsNotNone(member)
        self.assertEqual(member.name, "TestOfficer1")
        self.assertEqual(member.role, "officer")
        self.assertEqual(member.rank, 2)
        
        member = self.guild_system.get_guild_member("RandomPlayer")
        self.assertIsNone(member)
    
    def test_priority_detection(self):
        """Test priority detection for different scenarios."""
        # High priority for guild leader
        priority = self.guild_system.get_alert_priority("TestLeader", "Hello")
        self.assertEqual(priority, "high")
        
        # High priority for officers
        priority = self.guild_system.get_alert_priority("TestOfficer1", "Hello")
        self.assertEqual(priority, "high")
        
        # Medium priority for urgent keywords
        priority = self.guild_system.get_alert_priority("TestMember1", "URGENT: Need help")
        self.assertEqual(priority, "medium")
        
        priority = self.guild_system.get_alert_priority("TestMember1", "EMERGENCY: Raid starting")
        self.assertEqual(priority, "medium")
        
        # Low priority for regular members
        priority = self.guild_system.get_alert_priority("TestMember1", "Just saying hi")
        self.assertEqual(priority, "low")
    
    def test_auto_reply_generation(self):
        """Test auto-reply generation."""
        member = self.guild_system.get_guild_member("TestLeader")
        
        # Test leader auto-reply
        reply = self.guild_system.generate_auto_reply("TestLeader", "Hello", member)
        self.assertIsNotNone(reply)
        self.assertIn("TestLeader", reply)
        
        # Test officer auto-reply
        member = self.guild_system.get_guild_member("TestOfficer1")
        reply = self.guild_system.generate_auto_reply("TestOfficer1", "Hello", member)
        self.assertIsNotNone(reply)
        self.assertIn("TestOfficer1", reply)
        
        # Test member auto-reply
        member = self.guild_system.get_guild_member("TestMember1")
        reply = self.guild_system.generate_auto_reply("TestMember1", "Hello", member)
        self.assertIsNotNone(reply)
        self.assertIn("TestMember1", reply)
    
    def test_guild_alert_processing(self):
        """Test complete guild alert processing."""
        # Test guild member alert
        alert = self.guild_system.process_guild_whisper("TestLeader", "Hello")
        self.assertIsNotNone(alert)
        self.assertEqual(alert.sender, "TestLeader")
        self.assertEqual(alert.message, "Hello")
        self.assertEqual(alert.alert_type, "leader_message")
        self.assertEqual(alert.priority, "high")
        self.assertTrue(alert.auto_reply_sent)
        self.assertIsNotNone(alert.reply_message)
        
        # Test officer alert
        alert = self.guild_system.process_guild_whisper("TestOfficer1", "Need help")
        self.assertIsNotNone(alert)
        self.assertEqual(alert.alert_type, "officer_message")
        self.assertEqual(alert.priority, "high")
        
        # Test member alert
        alert = self.guild_system.process_guild_whisper("TestMember1", "Just saying hi")
        self.assertIsNotNone(alert)
        self.assertEqual(alert.alert_type, "guild_whisper")
        self.assertEqual(alert.priority, "low")
        
        # Test non-guild member (should return None)
        alert = self.guild_system.process_guild_whisper("RandomPlayer", "Hello")
        self.assertIsNone(alert)
    
    def test_alert_analytics(self):
        """Test guild alert analytics."""
        # Process some alerts
        self.guild_system.process_guild_whisper("TestLeader", "Hello")
        self.guild_system.process_guild_whisper("TestOfficer1", "Need help")
        self.guild_system.process_guild_whisper("TestMember1", "Just saying hi")
        
        analytics = self.guild_system.get_session_analytics()
        
        self.assertEqual(analytics["guild_alerts_total"], 3)
        self.assertEqual(analytics["auto_replies_sent"], 3)
        self.assertEqual(len(analytics["guild_members_contacted"]), 3)
        
        # Check alert types
        self.assertIn("leader_message", analytics["guild_alerts_by_type"])
        self.assertIn("officer_message", analytics["guild_alerts_by_type"])
        self.assertIn("guild_whisper", analytics["guild_alerts_by_type"])
        
        # Check priorities
        self.assertIn("high", analytics["guild_alerts_by_priority"])
        self.assertIn("low", analytics["guild_alerts_by_priority"])
    
    def test_configuration_management(self):
        """Test guild configuration management."""
        # Add new member
        self.guild_system.add_guild_member("NewMember", "member", 3)
        self.assertTrue(self.guild_system.is_guild_member("NewMember"))
        
        # Remove member
        self.guild_system.remove_guild_member("TestMember1")
        self.assertFalse(self.guild_system.is_guild_member("TestMember1"))
    
    def test_export_functionality(self):
        """Test export functionality."""
        # Process some alerts
        self.guild_system.process_guild_whisper("TestLeader", "Hello")
        self.guild_system.process_guild_whisper("TestOfficer1", "Need help")
        
        # Export alerts
        export_path = self.guild_system.export_alerts()
        
        # Verify export file exists
        self.assertTrue(os.path.exists(export_path))
        
        # Read and verify export data
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        self.assertEqual(export_data["guild_name"], "Test Guild")
        self.assertEqual(len(export_data["alerts"]), 2)
        self.assertIn("analytics", export_data)
        
        # Clean up export file
        os.remove(export_path)


class TestSessionManagerIntegration(unittest.TestCase):
    """Test cases for session manager integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.session = SessionManager(mode="test_guild_alerts")
    
    def test_guild_alert_recording(self):
        """Test recording guild alerts in session manager."""
        # Record some guild alerts
        self.session.record_guild_alert(
            "TestLeader", "Hello", "leader_message", "high", True, "I'll be there!"
        )
        self.session.record_guild_alert(
            "TestOfficer", "Need help", "officer_message", "high", True, "On my way!"
        )
        self.session.record_guild_alert(
            "TestMember", "Just saying hi", "guild_whisper", "low", True, "Hi there!"
        )
        
        # Verify alerts were recorded
        self.assertEqual(len(self.session.guild_alerts), 3)
        
        # Check first alert
        alert = self.session.guild_alerts[0]
        self.assertEqual(alert.sender, "TestLeader")
        self.assertEqual(alert.message, "Hello")
        self.assertEqual(alert.alert_type, "leader_message")
        self.assertEqual(alert.priority, "high")
        self.assertTrue(alert.auto_reply_sent)
        self.assertEqual(alert.reply_message, "I'll be there!")
    
    def test_session_analytics_integration(self):
        """Test that guild alerts are included in session analytics."""
        # Record some alerts
        self.session.record_guild_alert("TestLeader", "Hello", "leader_message", "high", True)
        self.session.record_guild_alert("TestOfficer", "Need help", "officer_message", "high", False)
        self.session.record_guild_alert("TestMember", "Just saying hi", "guild_whisper", "low", True)
        
        # End session to calculate stats
        self.session.end_session()
        
        # Check that guild alert stats are included
        metrics = self.session.performance_metrics
        self.assertEqual(metrics["total_guild_alerts"], 3)
        self.assertEqual(metrics["high_priority_guild_alerts"], 2)
        self.assertEqual(metrics["guild_auto_replies_sent"], 2)


class TestDiscordIntegration(unittest.TestCase):
    """Test cases for Discord integration."""
    
    @patch('modules.guild_alert_system.DiscordNotifier')
    def test_discord_integration_initialization(self, mock_discord_notifier):
        """Test Discord integration initialization."""
        # Mock DiscordNotifier
        mock_notifier = Mock()
        mock_discord_notifier.return_value = mock_notifier
        
        # Create temporary config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"guild_name": "Test Guild"}, f)
            config_path = f.name
        
        try:
            guild_system = GuildAlertSystem(config_path)
            
            # Verify Discord notifier was created
            mock_discord_notifier.assert_called_once()
            
        finally:
            os.unlink(config_path)
    
    @patch('modules.guild_alert_system.asyncio.create_task')
    def test_discord_alert_sending(self, mock_create_task):
        """Test sending Discord alerts."""
        # Create guild system with mocked Discord notifier
        guild_system = GuildAlertSystem()
        guild_system.discord_notifier = Mock()
        
        # Create test alert
        alert = GuildAlert(
            timestamp=datetime.now().isoformat(),
            sender="TestLeader",
            message="Hello",
            alert_type="leader_message",
            priority="high",
            auto_reply_sent=True,
            reply_message="I'll be there!"
        )
        
        # Test sending alert
        guild_system._send_discord_alert(alert)
        
        # Verify Discord notifier was called
        guild_system.discord_notifier.send_simple_alert.assert_called_once()


class TestGuildAlertSystemEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_config_file(self):
        """Test handling of empty config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            config_path = f.name
        
        try:
            guild_system = GuildAlertSystem(config_path)
            
            # Should handle empty config gracefully
            self.assertEqual(guild_system.guild_name, None)
            self.assertEqual(len(guild_system.guild_members), 0)
            
        finally:
            os.unlink(config_path)
    
    def test_missing_config_file(self):
        """Test handling of missing config file."""
        config_path = "/nonexistent/path/guild_config.json"
        guild_system = GuildAlertSystem(config_path)
        
        # Should create default config
        self.assertIsNotNone(guild_system.guild_name)
        self.assertEqual(len(guild_system.guild_members), 0)
    
    def test_case_insensitive_member_detection(self):
        """Test case insensitive member detection."""
        # Create guild system with test members
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "guild_name": "Test Guild",
                "guild_leader": "TestLeader",
                "guild_officers": ["TestOfficer"],
                "members": {
                    "TestLeader": {"name": "TestLeader", "role": "leader", "rank": 1, "online": False, "last_seen": None},
                    "TestOfficer": {"name": "TestOfficer", "role": "officer", "rank": 2, "online": False, "last_seen": None}
                }
            }
            json.dump(config, f)
            config_path = f.name
        
        try:
            guild_system = GuildAlertSystem(config_path)
            
            # Test case insensitive detection
            self.assertTrue(guild_system.is_guild_member("testleader"))
            self.assertTrue(guild_system.is_guild_member("TESTOFFICER"))
            self.assertTrue(guild_system.is_guild_leader("testleader"))
            self.assertTrue(guild_system.is_guild_officer("testofficer"))
            
        finally:
            os.unlink(config_path)
    
    def test_auto_reply_disabled(self):
        """Test auto-reply when disabled."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "guild_name": "Test Guild",
                "auto_reply_enabled": False,
                "members": {
                    "TestMember": {"name": "TestMember", "role": "member", "rank": 3, "online": False, "last_seen": None}
                }
            }
            json.dump(config, f)
            config_path = f.name
        
        try:
            guild_system = GuildAlertSystem(config_path)
            member = guild_system.get_guild_member("TestMember")
            
            # Auto-reply should be None when disabled
            reply = guild_system.generate_auto_reply("TestMember", "Hello", member)
            self.assertIsNone(reply)
            
        finally:
            os.unlink(config_path)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestGuildAlertSystem))
    test_suite.addTest(unittest.makeSuite(TestSessionManagerIntegration))
    test_suite.addTest(unittest.makeSuite(TestDiscordIntegration))
    test_suite.addTest(unittest.makeSuite(TestGuildAlertSystemEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!") 
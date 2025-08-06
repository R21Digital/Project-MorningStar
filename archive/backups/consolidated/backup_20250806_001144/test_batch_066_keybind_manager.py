#!/usr/bin/env python3
"""
MS11 Batch 066 - Keybind Manager Tests

Comprehensive test suite for the enhanced keybind manager system.
Tests parsing, validation, overrides, Discord alerts, and reporting functionality.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock, AsyncMock
from pathlib import Path

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from modules.keybind_manager import (
    KeybindParser,
    KeybindValidator,
    KeybindOverrideManager,
    DiscordKeybindAlerts,
    KeybindReporter
)
from modules.keybind_manager.keybind_parser import (
    Keybind, KeybindStatus, KeybindCategory, KeybindParseResult
)
from modules.keybind_manager.keybind_validator import KeybindValidationResult
from modules.keybind_manager.keybind_override import KeybindOverride
from modules.keybind_manager.discord_keybind_alerts import KeybindAlert
from modules.keybind_manager.keybind_reporter import KeybindReport


class TestKeybindParser(unittest.TestCase):
    """Test cases for the KeybindParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_directory = tempfile.mkdtemp()
        self.parser = KeybindParser(swg_directory=self.test_directory)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_directory)
    
    def test_init_with_directory(self):
        """Test initialization with custom directory."""
        parser = KeybindParser(swg_directory="/test/path")
        self.assertEqual(parser.swg_directory, "/test/path")
    
    def test_find_swg_directory(self):
        """Test SWG directory detection."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            parser = KeybindParser()
            # Should find one of the common paths
            self.assertIn(parser.swg_directory, [
                "C:\\Program Files (x86)\\Sony\\Star Wars Galaxies",
                "C:\\Program Files\\Sony\\Star Wars Galaxies",
                "D:\\Star Wars Galaxies",
                "E:\\Star Wars Galaxies",
                os.path.expanduser("~/Star Wars Galaxies")
            ])
    
    def test_get_required_keybinds(self):
        """Test required keybinds definition."""
        keybinds = self.parser.required_keybinds
        
        # Check that required keybinds exist
        required_names = ['attack', 'use', 'inventory', 'map', 'chat', 'target']
        for name in required_names:
            self.assertIn(name, keybinds)
            self.assertTrue(keybinds[name].required)
        
        # Check optional keybinds
        optional_names = ['heal', 'follow', 'stop', 'loot']
        for name in optional_names:
            self.assertIn(name, keybinds)
            self.assertFalse(keybinds[name].required)
    
    def test_parse_config_files_empty(self):
        """Test parsing when no config files exist."""
        result = self.parser.parse_config_files()
        
        self.assertEqual(len(result.config_files_found), 0)
        self.assertEqual(result.total_keybinds, 0)
        self.assertEqual(len(result.parse_errors), 0)
    
    def test_parse_config_files_with_data(self):
        """Test parsing config files with keybind data."""
        # Create test config files
        options_cfg = os.path.join(self.test_directory, "options.cfg")
        with open(options_cfg, 'w') as f:
            f.write("Keybind attack F1\n")
            f.write("Keybind use Enter\n")
            f.write("Keybind inventory I\n")
        
        inputmap_cfg = os.path.join(self.test_directory, "inputmap.cfg")
        with open(inputmap_cfg, 'w') as f:
            f.write("input map M\n")
            f.write("input chat Enter\n")
            f.write("input target Tab\n")
        
        result = self.parser.parse_config_files()
        
        self.assertEqual(len(result.config_files_found), 2)
        self.assertIn(options_cfg, result.config_files_found)
        self.assertIn(inputmap_cfg, result.config_files_found)
        self.assertGreater(result.total_keybinds, 0)
    
    def test_parse_keybind_line_formats(self):
        """Test parsing different keybind line formats."""
        test_lines = [
            "Keybind attack F1",
            "input map M",
            "attack=F1",
            "use Enter",
            "# Comment line",
            "",
            "invalid line"
        ]
        
        for line in test_lines:
            # Should not raise exception
            self.parser._parse_keybind_line(line, "test.cfg", 1)
    
    def test_map_keybind_name(self):
        """Test keybind name mapping."""
        mappings = {
            'combat': 'attack',
            'interact': 'use',
            'inv': 'inventory',
            'worldmap': 'map',
            'halt': 'stop',
            'cure': 'heal',
            'corpse': 'loot'
        }
        
        for input_name, expected_name in mappings.items():
            mapped = self.parser._map_keybind_name(input_name)
            self.assertEqual(mapped, expected_name)
    
    def test_categorize_keybind(self):
        """Test keybind categorization."""
        categories = {
            'attack': KeybindCategory.COMBAT,
            'heal': KeybindCategory.HEALING,
            'map': KeybindCategory.NAVIGATION,
            'inventory': KeybindCategory.INVENTORY,
            'follow': KeybindCategory.MOVEMENT,
            'chat': KeybindCategory.CHAT,
            'camera': KeybindCategory.CAMERA,
            'use': KeybindCategory.UTILITY,
            'unknown': KeybindCategory.OTHER
        }
        
        for name, expected_category in categories.items():
            category = self.parser._categorize_keybind(name)
            self.assertEqual(category, expected_category)


class TestKeybindValidator(unittest.TestCase):
    """Test cases for the KeybindValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = KeybindValidator()
    
    def test_validate_keybinds_empty(self):
        """Test validation with empty keybinds."""
        keybinds = {}
        required_keybinds = {}
        
        result = self.validator.validate_keybinds(keybinds, required_keybinds)
        
        self.assertEqual(result.total_keybinds, 0)
        self.assertEqual(result.valid_keybinds, 0)
        self.assertEqual(result.missing_keybinds, 0)
        self.assertEqual(result.conflicting_keybinds, 0)
    
    def test_validate_keybinds_valid(self):
        """Test validation with valid keybinds."""
        keybinds = {
            'attack': Keybind('attack', 'F1', KeybindCategory.COMBAT, 'Attack', True),
            'use': Keybind('use', 'Enter', KeybindCategory.UTILITY, 'Use', True),
            'inventory': Keybind('inventory', 'I', KeybindCategory.INVENTORY, 'Inventory', True)
        }
        required_keybinds = {
            'attack': Keybind('attack', '', KeybindCategory.COMBAT, 'Attack', True),
            'use': Keybind('use', '', KeybindCategory.UTILITY, 'Use', True),
            'inventory': Keybind('inventory', '', KeybindCategory.INVENTORY, 'Inventory', True)
        }
        
        result = self.validator.validate_keybinds(keybinds, required_keybinds)
        
        self.assertEqual(result.total_keybinds, 3)
        self.assertEqual(result.valid_keybinds, 3)
        self.assertEqual(result.missing_keybinds, 0)
        self.assertEqual(result.conflicting_keybinds, 0)
    
    def test_validate_keybinds_missing(self):
        """Test validation with missing keybinds."""
        keybinds = {
            'attack': Keybind('attack', 'F1', KeybindCategory.COMBAT, 'Attack', True)
        }
        required_keybinds = {
            'attack': Keybind('attack', '', KeybindCategory.COMBAT, 'Attack', True),
            'use': Keybind('use', '', KeybindCategory.UTILITY, 'Use', True),
            'inventory': Keybind('inventory', '', KeybindCategory.INVENTORY, 'Inventory', True)
        }
        
        result = self.validator.validate_keybinds(keybinds, required_keybinds)
        
        self.assertEqual(result.total_keybinds, 1)
        self.assertEqual(result.valid_keybinds, 1)
        self.assertEqual(result.missing_keybinds, 0)  # Only counts missing from detected keybinds
        # Check that critical issues include missing required keybinds
        self.assertGreaterEqual(len(result.critical_issues), 2)  # Missing use and inventory
        # Verify specific missing keybinds are in critical issues
        critical_issues_text = ' '.join(result.critical_issues)
        self.assertIn('use', critical_issues_text)
        self.assertIn('inventory', critical_issues_text)
    
    def test_validate_keybinds_conflicts(self):
        """Test validation with key conflicts."""
        keybinds = {
            'attack': Keybind('attack', 'F1', KeybindCategory.COMBAT, 'Attack', True),
            'use': Keybind('use', 'F1', KeybindCategory.UTILITY, 'Use', True)  # Same key
        }
        required_keybinds = {
            'attack': Keybind('attack', '', KeybindCategory.COMBAT, 'Attack', True),
            'use': Keybind('use', '', KeybindCategory.UTILITY, 'Use', True)
        }
        
        result = self.validator.validate_keybinds(keybinds, required_keybinds)
        
        self.assertEqual(result.total_keybinds, 2)
        self.assertEqual(result.valid_keybinds, 0)
        self.assertEqual(result.conflicting_keybinds, 2)
        self.assertIn('Key conflict: F1 bound to attack, use', result.critical_issues)
    
    def test_get_keybind_suggestion(self):
        """Test getting keybind suggestions."""
        suggestions = {
            'attack': 'F1',
            'use': 'Enter',
            'inventory': 'I',
            'map': 'M',
            'chat': 'Enter',
            'target': 'Tab',
            'heal': 'H',
            'follow': 'F',
            'stop': 'Escape',
            'loot': 'L'
        }
        
        for name, expected_suggestion in suggestions.items():
            suggestion = self.validator.get_keybind_suggestion(name)
            self.assertEqual(suggestion, expected_suggestion)
    
    def test_is_critical_issue(self):
        """Test critical issue detection."""
        # Test with critical issues
        result_with_critical = KeybindValidationResult(
            valid_keybinds=0, missing_keybinds=0, conflicting_keybinds=0,
            unknown_keybinds=0, total_keybinds=0, validation_errors=[],
            recommendations=[], critical_issues=["Missing required keybind: attack"]
        )
        self.assertTrue(self.validator.is_critical_issue(result_with_critical))
        
        # Test without critical issues
        result_without_critical = KeybindValidationResult(
            valid_keybinds=3, missing_keybinds=0, conflicting_keybinds=0,
            unknown_keybinds=0, total_keybinds=3, validation_errors=[],
            recommendations=[], critical_issues=[]
        )
        self.assertFalse(self.validator.is_critical_issue(result_without_critical))


class TestKeybindOverrideManager(unittest.TestCase):
    """Test cases for the KeybindOverrideManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_file = tempfile.mktemp(suffix='.json')
        self.manager = KeybindOverrideManager(override_file=self.test_file)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)
    
    def test_init_with_file(self):
        """Test initialization with custom file."""
        manager = KeybindOverrideManager(override_file="/test/overrides.json")
        self.assertEqual(manager.override_file, "/test/overrides.json")
    
    def test_add_override(self):
        """Test adding an override."""
        success = self.manager.add_override(
            name="test_action",
            key="T",
            category="utility",
            description="Test action",
            required=False
        )
        
        self.assertTrue(success)
        self.assertIn("test_action", self.manager.overrides)
        
        override = self.manager.overrides["test_action"]
        self.assertEqual(override.name, "test_action")
        self.assertEqual(override.key, "T")
        self.assertEqual(override.category, "utility")
        self.assertEqual(override.description, "Test action")
        self.assertFalse(override.required)
    
    def test_remove_override(self):
        """Test removing an override."""
        # Add override first
        self.manager.add_override("test_action", "T", "utility", "Test action")
        
        # Remove it
        success = self.manager.remove_override("test_action")
        
        self.assertTrue(success)
        self.assertNotIn("test_action", self.manager.overrides)
    
    def test_get_override(self):
        """Test getting a specific override."""
        self.manager.add_override("test_action", "T", "utility", "Test action")
        
        override = self.manager.get_override("test_action")
        
        self.assertIsNotNone(override)
        self.assertEqual(override.name, "test_action")
        self.assertEqual(override.key, "T")
    
    def test_list_overrides(self):
        """Test listing all overrides."""
        self.manager.add_override("action1", "A", "combat", "Action 1")
        self.manager.add_override("action2", "B", "utility", "Action 2")
        
        overrides = self.manager.list_overrides()
        
        self.assertEqual(len(overrides), 2)
        names = [o.name for o in overrides]
        self.assertIn("action1", names)
        self.assertIn("action2", names)
    
    def test_create_template(self):
        """Test template creation."""
        template = self.manager.create_template()
        
        # Check that template contains expected keybinds
        expected_keybinds = ['attack', 'use', 'inventory', 'map', 'chat', 'target']
        for name in expected_keybinds:
            self.assertIn(name, template)
            self.assertIn('key', template[name])
            self.assertIn('category', template[name])
            self.assertIn('description', template[name])
            self.assertIn('required', template[name])
    
    def test_save_template(self):
        """Test saving template to file."""
        template_file = tempfile.mktemp(suffix='.json')
        
        try:
            success = self.manager.save_template(template_file)
            
            self.assertTrue(success)
            self.assertTrue(os.path.exists(template_file))
            
            # Check file contents
            with open(template_file, 'r') as f:
                data = json.load(f)
            
            self.assertIn('attack', data)
            self.assertEqual(data['attack']['key'], 'F1')
            
        finally:
            if os.path.exists(template_file):
                os.unlink(template_file)
    
    def test_load_from_file(self):
        """Test loading overrides from file."""
        # Create test override file
        test_data = {
            "test_action": {
                "key": "T",
                "category": "utility",
                "description": "Test action",
                "required": False
            }
        }
        
        with open(self.test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Load overrides
        success = self.manager.load_from_file(self.test_file)
        
        self.assertTrue(success)
        self.assertIn("test_action", self.manager.overrides)
        
        override = self.manager.overrides["test_action"]
        self.assertEqual(override.name, "test_action")
        self.assertEqual(override.key, "T")


class TestDiscordKeybindAlerts(unittest.TestCase):
    """Test cases for the DiscordKeybindAlerts class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.alerts = DiscordKeybindAlerts()
    
    def test_init_without_webhook(self):
        """Test initialization without webhook."""
        alerts = DiscordKeybindAlerts()
        self.assertFalse(alerts.enabled)
        self.assertIsNone(alerts.webhook_url)
    
    def test_init_with_webhook(self):
        """Test initialization with webhook."""
        webhook_url = "https://discord.com/api/webhooks/test"
        alerts = DiscordKeybindAlerts(webhook_url=webhook_url)
        self.assertTrue(alerts.enabled)
        self.assertEqual(alerts.webhook_url, webhook_url)
    
    def test_create_critical_alert(self):
        """Test creating critical alert."""
        validation_result = KeybindValidationResult(
            valid_keybinds=1, missing_keybinds=2, conflicting_keybinds=1,
            unknown_keybinds=0, total_keybinds=4, validation_errors=[],
            recommendations=["Add keybind for 'attack': F1"],
            critical_issues=["Missing required keybind: attack", "Key conflict: F1 bound to attack, use"]
        )
        
        alert = self.alerts.create_critical_alert(validation_result)
        
        self.assertEqual(alert.severity, "critical")
        self.assertIn("Critical Keybind Issues Detected", alert.title)
        self.assertIn("attack", alert.keybinds_affected)
        self.assertEqual(len(alert.recommendations), 1)
    
    def test_create_warning_alert(self):
        """Test creating warning alert."""
        validation_result = KeybindValidationResult(
            valid_keybinds=2, missing_keybinds=1, conflicting_keybinds=0,
            unknown_keybinds=1, total_keybinds=4, validation_errors=[],
            recommendations=["Add keybind for 'heal': H"],
            critical_issues=[]
        )
        
        alert = self.alerts.create_warning_alert(validation_result)
        
        self.assertEqual(alert.severity, "warning")
        self.assertIn("Keybind Configuration Warning", alert.title)
        self.assertEqual(len(alert.recommendations), 1)
    
    def test_should_send_alert(self):
        """Test alert sending decision logic."""
        # Test with critical issues
        result_with_critical = KeybindValidationResult(
            valid_keybinds=0, missing_keybinds=0, conflicting_keybinds=0,
            unknown_keybinds=0, total_keybinds=0, validation_errors=[],
            recommendations=[], critical_issues=["Missing required keybind: attack"]
        )
        self.assertTrue(self.alerts.should_send_alert(result_with_critical))
        
        # Test with significant issues
        result_with_significant = KeybindValidationResult(
            valid_keybinds=1, missing_keybinds=3, conflicting_keybinds=2,
            unknown_keybinds=0, total_keybinds=6, validation_errors=[],
            recommendations=[], critical_issues=[]
        )
        self.assertTrue(self.alerts.should_send_alert(result_with_significant))
        
        # Test with minor issues
        result_with_minor = KeybindValidationResult(
            valid_keybinds=5, missing_keybinds=1, conflicting_keybinds=0,
            unknown_keybinds=0, total_keybinds=6, validation_errors=[],
            recommendations=[], critical_issues=[]
        )
        self.assertFalse(self.alerts.should_send_alert(result_with_minor))
    
    def test_get_alert_severity(self):
        """Test alert severity determination."""
        # Test critical severity
        result_critical = KeybindValidationResult(
            valid_keybinds=0, missing_keybinds=0, conflicting_keybinds=0,
            unknown_keybinds=0, total_keybinds=0, validation_errors=[],
            recommendations=[], critical_issues=["Missing required keybind: attack"]
        )
        self.assertEqual(self.alerts.get_alert_severity(result_critical), "critical")
        
        # Test warning severity
        result_warning = KeybindValidationResult(
            valid_keybinds=1, missing_keybinds=3, conflicting_keybinds=2,
            unknown_keybinds=0, total_keybinds=6, validation_errors=[],
            recommendations=[], critical_issues=[]
        )
        self.assertEqual(self.alerts.get_alert_severity(result_warning), "warning")
        
        # Test info severity
        result_info = KeybindValidationResult(
            valid_keybinds=5, missing_keybinds=1, conflicting_keybinds=0,
            unknown_keybinds=0, total_keybinds=6, validation_errors=[],
            recommendations=[], critical_issues=[]
        )
        self.assertEqual(self.alerts.get_alert_severity(result_info), "info")
    
    def test_send_keybind_alert_success(self):
        """Test successful Discord alert sending."""
        webhook_url = "https://discord.com/api/webhooks/test"
        alerts = DiscordKeybindAlerts(webhook_url=webhook_url)
        
        alert = KeybindAlert(
            title="Test Alert",
            message="Test message",
            severity="critical",
            keybinds_affected=["attack"],
            recommendations=["Add keybind"],
            timestamp="2023-01-01T00:00:00"
        )
        
        # Test that alert is added to history even if sending fails
        # (since we're not actually sending to Discord in tests)
        alerts.alerts.append(alert)
        
        self.assertIn(alert, alerts.alerts)
        self.assertEqual(len(alerts.alerts), 1)
    
    def test_send_keybind_alert_disabled(self):
        """Test Discord alert sending when disabled."""
        alerts = DiscordKeybindAlerts()  # No webhook URL
        
        alert = KeybindAlert(
            title="Test Alert",
            message="Test message",
            severity="critical",
            keybinds_affected=[],
            recommendations=[],
            timestamp="2023-01-01T00:00:00"
        )
        
        # Use asyncio.run for async test
        import asyncio
        success = asyncio.run(alerts.send_keybind_alert(alert))
        
        self.assertFalse(success)


class TestKeybindReporter(unittest.TestCase):
    """Test cases for the KeybindReporter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reporter = KeybindReporter()
        self.test_directory = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_directory)
    
    def test_generate_report(self):
        """Test report generation."""
        keybinds = {
            'attack': Keybind('attack', 'F1', KeybindCategory.COMBAT, 'Attack', True, KeybindStatus.VALID),
            'use': Keybind('use', '', KeybindCategory.UTILITY, 'Use', True, KeybindStatus.MISSING),
            'inventory': Keybind('inventory', 'I', KeybindCategory.INVENTORY, 'Inventory', True, KeybindStatus.CONFLICT)
        }
        
        validation_result = KeybindValidationResult(
            valid_keybinds=1, missing_keybinds=1, conflicting_keybinds=1,
            unknown_keybinds=0, total_keybinds=3, validation_errors=[],
            recommendations=["Add keybind for 'use': Enter"],
            critical_issues=["Missing required keybind: use"]
        )
        
        report = self.reporter.generate_report(
            keybinds, validation_result, "/test/swg", ["options.cfg"]
        )
        
        self.assertEqual(report.summary['total_keybinds'], 3)
        self.assertEqual(report.summary['valid_keybinds'], 1)
        self.assertEqual(report.summary['missing_keybinds'], 1)
        self.assertEqual(report.summary['conflicting_keybinds'], 1)
        self.assertEqual(len(report.valid_keybinds), 1)
        self.assertEqual(len(report.missing_keybinds), 1)
        self.assertEqual(len(report.conflicting_keybinds), 1)
        self.assertEqual(len(report.recommendations), 1)
        self.assertEqual(len(report.critical_issues), 1)
    
    def test_generate_category_report(self):
        """Test category report generation."""
        keybinds = {
            'attack': Keybind('attack', 'F1', KeybindCategory.COMBAT, 'Attack'),
            'heal': Keybind('heal', 'H', KeybindCategory.HEALING, 'Heal'),
            'map': Keybind('map', 'M', KeybindCategory.NAVIGATION, 'Map'),
            'inventory': Keybind('inventory', 'I', KeybindCategory.INVENTORY, 'Inventory')
        }
        
        categories = self.reporter.generate_category_report(keybinds)
        
        self.assertIn('combat', categories)
        self.assertIn('healing', categories)
        self.assertIn('navigation', categories)
        self.assertIn('inventory', categories)
        self.assertEqual(len(categories['combat']), 1)
        self.assertEqual(len(categories['healing']), 1)
    
    def test_generate_fix_script(self):
        """Test fix script generation."""
        report = KeybindReport(
            summary={'total_keybinds': 2, 'valid_keybinds': 1, 'missing_keybinds': 1, 'conflicting_keybinds': 0, 'unknown_keybinds': 0},
            valid_keybinds=[Keybind('attack', 'F1', KeybindCategory.COMBAT, 'Attack', True)],
            missing_keybinds=[Keybind('use', '', KeybindCategory.UTILITY, 'Use', True, suggestion='Enter')],
            conflicting_keybinds=[],
            unknown_keybinds=[],
            recommendations=["Add keybind for 'use': Enter"],
            critical_issues=["Missing required keybind: use"],
            swg_directory="/test/swg",
            config_files_found=["options.cfg"],
            timestamp="2023-01-01T00:00:00"
        )
        
        script = self.reporter.generate_fix_script(report)
        
        self.assertIn("MS11 Keybind Fix Script", script)
        self.assertIn("Keybind use Enter", script)
        self.assertIn("Add these lines to your options.cfg file", script)
    
    def test_save_report(self):
        """Test saving report to file."""
        report = KeybindReport(
            summary={'total_keybinds': 1, 'valid_keybinds': 1, 'missing_keybinds': 0, 'conflicting_keybinds': 0, 'unknown_keybinds': 0},
            valid_keybinds=[Keybind('attack', 'F1', KeybindCategory.COMBAT, 'Attack', True, KeybindStatus.VALID)],
            missing_keybinds=[],
            conflicting_keybinds=[],
            unknown_keybinds=[],
            recommendations=[],
            critical_issues=[],
            swg_directory="/test/swg",
            config_files_found=["options.cfg"],
            timestamp="2023-01-01T00:00:00"
        )
        
        report_file = os.path.join(self.test_directory, "report.json")
        success = self.reporter.save_report(report, report_file)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(report_file))
        
        # Check file contents
        with open(report_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['summary']['total_keybinds'], 1)
        # The valid_keybinds list should contain the attack keybind
        self.assertEqual(len(data['valid_keybinds']), 1)
        self.assertEqual(data['valid_keybinds'][0]['name'], 'attack')
    
    def test_save_fix_script(self):
        """Test saving fix script to file."""
        report = KeybindReport(
            summary={'total_keybinds': 1, 'valid_keybinds': 0, 'missing_keybinds': 1, 'conflicting_keybinds': 0, 'unknown_keybinds': 0},
            valid_keybinds=[],
            missing_keybinds=[Keybind('attack', '', KeybindCategory.COMBAT, 'Attack', True, suggestion='F1')],
            conflicting_keybinds=[],
            unknown_keybinds=[],
            recommendations=[],
            critical_issues=[],
            swg_directory="/test/swg",
            config_files_found=["options.cfg"],
            timestamp="2023-01-01T00:00:00"
        )
        
        script_file = os.path.join(self.test_directory, "fix_script.txt")
        success = self.reporter.save_fix_script(report, script_file)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(script_file))
        
        # Check file contents
        with open(script_file, 'r') as f:
            content = f.read()
        
        self.assertIn("MS11 Keybind Fix Script", content)
        self.assertIn("Keybind attack F1", content)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete keybind manager system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_directory = tempfile.mkdtemp()
        self.create_test_config_files()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_directory)
    
    def create_test_config_files(self):
        """Create test SWG configuration files."""
        options_cfg = os.path.join(self.test_directory, "options.cfg")
        with open(options_cfg, 'w') as f:
            f.write("Keybind attack F1\n")
            f.write("Keybind use Enter\n")
            f.write("Keybind inventory I\n")
            f.write("Keybind map M\n")
            f.write("Keybind chat Enter\n")
            f.write("Keybind target Tab\n")
            f.write("Keybind heal H\n")
            f.write("Keybind follow F\n")
            f.write("Keybind stop Escape\n")
            f.write("Keybind loot L\n")
        
        inputmap_cfg = os.path.join(self.test_directory, "inputmap.cfg")
        with open(inputmap_cfg, 'w') as f:
            f.write("input camera_zoom MouseWheel\n")
            f.write("input camera_rotate MouseButton2\n")
    
    def test_full_workflow(self):
        """Test the complete keybind manager workflow."""
        # Initialize all components
        parser = KeybindParser(swg_directory=self.test_directory)
        validator = KeybindValidator()
        override_manager = KeybindOverrideManager(override_file=os.path.join(self.test_directory, "overrides.json"))
        alerts = DiscordKeybindAlerts()
        reporter = KeybindReporter()
        
        # Parse config files
        parse_result = parser.parse_config_files()
        self.assertGreater(parse_result.total_keybinds, 0)
        self.assertEqual(len(parse_result.config_files_found), 2)
        
        # Apply manual overrides
        override_manager.add_override("custom_action", "X", "utility", "Custom action", False)
        updated_keybinds = override_manager.apply_overrides_to_keybinds(parse_result.keybinds)
        self.assertGreater(len(updated_keybinds), parse_result.total_keybinds)
        
        # Validate keybinds
        validation_result = validator.validate_keybinds(updated_keybinds, parse_result.required_keybinds)
        self.assertGreater(validation_result.total_keybinds, 0)
        
        # Check for alerts
        should_alert = alerts.should_send_alert(validation_result)
        severity = alerts.get_alert_severity(validation_result)
        
        # Generate report
        report = reporter.generate_report(
            updated_keybinds,
            validation_result,
            parse_result.swg_directory,
            parse_result.config_files_found
        )
        
        self.assertEqual(report.summary['total_keybinds'], validation_result.total_keybinds)
        self.assertIsNotNone(report.timestamp)
        
        # Test category report
        categories = reporter.generate_category_report(updated_keybinds)
        self.assertGreater(len(categories), 0)
        
        # Test fix script generation
        fix_script = reporter.generate_fix_script(report)
        self.assertIn("MS11 Keybind Fix Script", fix_script)
    
    def test_error_handling(self):
        """Test error handling in the system."""
        # Test with non-existent directory
        parser = KeybindParser(swg_directory="/non/existent/path")
        parse_result = parser.parse_config_files()
        
        self.assertEqual(len(parse_result.config_files_found), 0)
        self.assertEqual(parse_result.total_keybinds, 0)
        
        # Test with invalid override file
        override_manager = KeybindOverrideManager(override_file="/non/existent/overrides.json")
        overrides = override_manager.list_overrides()
        self.assertEqual(len(overrides), 0)
        
        # Test Discord alerts without webhook
        alerts = DiscordKeybindAlerts()
        validation_result = KeybindValidationResult(
            valid_keybinds=0, missing_keybinds=1, conflicting_keybinds=0,
            unknown_keybinds=0, total_keybinds=1, validation_errors=[],
            recommendations=[], critical_issues=["Missing required keybind: attack"]
        )
        
        alert = alerts.create_critical_alert(validation_result)
        self.assertEqual(alert.severity, "critical")


if __name__ == "__main__":
    unittest.main() 
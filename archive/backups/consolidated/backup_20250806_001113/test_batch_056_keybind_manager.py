#!/usr/bin/env python3
"""
MS11 Batch 056 - Keybind Manager Tests

Comprehensive test suite for the keybind manager system.
Tests parsing, validation, overrides, and reporting functionality.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from core.keybind_manager import (
    KeybindManager,
    get_keybind_manager,
    validate_keybinds,
    save_keybind_report,
    Keybind,
    KeybindReport,
    KeybindStatus,
    KeybindCategory
)


class TestKeybindManager(unittest.TestCase):
    """Test cases for the KeybindManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_directory = tempfile.mkdtemp()
        self.manager = KeybindManager(self.test_directory)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_directory)
    
    def test_init_with_directory(self):
        """Test initialization with custom directory."""
        manager = KeybindManager("/test/path")
        self.assertEqual(manager.swg_directory, "/test/path")
    
    def test_find_swg_directory(self):
        """Test SWG directory detection."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            manager = KeybindManager()
            # Should find one of the common paths
            self.assertIn(manager.swg_directory, [
                "C:\\Program Files (x86)\\Sony\\Star Wars Galaxies",
                "C:\\Program Files\\Sony\\Star Wars Galaxies",
                "D:\\Star Wars Galaxies",
                "E:\\Star Wars Galaxies"
            ])
    
    def test_get_required_keybinds(self):
        """Test required keybinds definition."""
        keybinds = self.manager.required_keybinds
        
        # Check that required keybinds exist
        required_names = ['attack', 'use', 'inventory', 'map', 'chat', 'target']
        for name in required_names:
            self.assertIn(name, keybinds)
            self.assertTrue(keybinds[name].required)
        
        # Check optional keybinds
        optional_names = ['follow', 'stop', 'heal', 'loot']
        for name in optional_names:
            self.assertIn(name, keybinds)
            self.assertFalse(keybinds[name].required)
    
    def test_parse_config_files(self):
        """Test config file parsing."""
        # Create test config files
        options_cfg = os.path.join(self.test_directory, "options.cfg")
        inputmap_cfg = os.path.join(self.test_directory, "inputmap.cfg")
        
        with open(options_cfg, 'w') as f:
            f.write("Keybind attack F1\n")
            f.write("Keybind use Enter\n")
            f.write("Keybind inventory I\n")
        
        with open(inputmap_cfg, 'w') as f:
            f.write("input map M\n")
            f.write("input chat Enter\n")
            f.write("input target Tab\n")
        
        config_files = self.manager.parse_config_files()
        
        self.assertEqual(len(config_files), 2)
        self.assertIn(options_cfg, config_files)
        self.assertIn(inputmap_cfg, config_files)
        
        # Check that keybinds were parsed
        self.assertIn('attack', self.manager.keybinds)
        self.assertIn('map', self.manager.keybinds)
    
    def test_parse_keybind_line(self):
        """Test individual keybind line parsing."""
        test_lines = [
            "Keybind attack F1",
            "input use Enter",
            "map = M",
            "invalid line"
        ]
        
        for line in test_lines:
            self.manager._parse_keybind_line(line)
        
        # Check that valid lines were parsed
        self.assertIn('attack', self.manager.keybinds)
        self.assertIn('use', self.manager.keybinds)
        self.assertIn('map', self.manager.keybinds)
    
    def test_map_keybind_name(self):
        """Test keybind name mapping."""
        mappings = {
            'attack': 'attack',
            'combat': 'attack',
            'fire': 'attack',
            'use': 'use',
            'interact': 'use',
            'inventory': 'inventory',
            'inv': 'inventory',
            'unknown': 'unknown'
        }
        
        for input_name, expected_name in mappings.items():
            mapped = self.manager._map_keybind_name(input_name)
            self.assertEqual(mapped, expected_name)
    
    def test_validate_keybinds(self):
        """Test keybind validation."""
        # Add some test keybinds
        self.manager.keybinds['attack'] = Keybind(
            name='attack',
            key='F1',
            category=KeybindCategory.COMBAT,
            description='Attack action',
            required=True,
            status=KeybindStatus.VALID
        )
        
        self.manager.keybinds['use'] = Keybind(
            name='use',
            key='F1',  # Conflict with attack
            category=KeybindCategory.INTERACTION,
            description='Use action',
            required=True,
            status=KeybindStatus.CONFLICT
        )
        
        report = self.manager.validate_keybinds()
        
        self.assertIsInstance(report, KeybindReport)
        self.assertEqual(report.total_keybinds, len(self.manager.required_keybinds))
        self.assertEqual(report.valid_keybinds, 1)
        self.assertEqual(report.conflicting_keybinds, 1)
        self.assertEqual(report.missing_keybinds, len(self.manager.required_keybinds) - 2)
    
    def test_get_keybind_suggestion(self):
        """Test keybind suggestion generation."""
        suggestions = {
            'attack': 'Set to F1 or primary mouse button',
            'use': 'Set to Enter or secondary mouse button',
            'inventory': 'Set to I or B',
            'unknown': 'Set to an available key'
        }
        
        for keybind_name, expected_suggestion in suggestions.items():
            suggestion = self.manager._get_keybind_suggestion(keybind_name)
            self.assertEqual(suggestion, expected_suggestion)
    
    def test_generate_suggestions(self):
        """Test suggestion generation."""
        # Test with missing keybinds
        self.manager.keybinds.clear()
        suggestions = self.manager._generate_suggestions()
        # When no keybinds are detected, it shows "No keybinds detected" message
        self.assertIn("No keybinds detected", suggestions[0])
        
        # Test with conflicts
        self.manager.keybinds['attack'] = Keybind(
            name='attack',
            key='F1',
            category=KeybindCategory.COMBAT,
            description='Attack',
            status=KeybindStatus.CONFLICT
        )
        suggestions = self.manager._generate_suggestions()
        self.assertIn("conflicts", suggestions[0])
    
    def test_save_report(self):
        """Test report saving."""
        # Create a test report
        self.manager.keybinds['attack'] = Keybind(
            name='attack',
            key='F1',
            category=KeybindCategory.COMBAT,
            description='Attack action',
            required=True,
            status=KeybindStatus.VALID
        )
        
        report_file = os.path.join(self.test_directory, "test_report.json")
        self.manager.save_report(report_file)
        
        # Verify file was created and contains valid JSON
        self.assertTrue(os.path.exists(report_file))
        with open(report_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('total_keybinds', data)
        self.assertIn('keybinds', data)
        self.assertIn('suggestions', data)
    
    def test_load_manual_overrides(self):
        """Test manual override loading."""
        # Create test override file
        override_file = os.path.join(self.test_directory, "overrides.json")
        overrides = {
            "attack": "F1",
            "use": "Enter",
            "inventory": "I"
        }
        
        with open(override_file, 'w') as f:
            json.dump(overrides, f)
        
        self.manager.load_manual_overrides(override_file)
        
        # Check that overrides were applied
        for name, key in overrides.items():
            if name in self.manager.keybinds:
                self.assertEqual(self.manager.keybinds[name].key, key)
                self.assertEqual(self.manager.keybinds[name].status, KeybindStatus.VALID)


class TestKeybindDataStructures(unittest.TestCase):
    """Test cases for keybind data structures."""
    
    def test_keybind_dataclass(self):
        """Test Keybind dataclass."""
        keybind = Keybind(
            name='test',
            key='F1',
            category=KeybindCategory.COMBAT,
            description='Test keybind',
            required=True,
            status=KeybindStatus.VALID,
            suggestion='Test suggestion'
        )
        
        self.assertEqual(keybind.name, 'test')
        self.assertEqual(keybind.key, 'F1')
        self.assertEqual(keybind.category, KeybindCategory.COMBAT)
        self.assertEqual(keybind.description, 'Test keybind')
        self.assertTrue(keybind.required)
        self.assertEqual(keybind.status, KeybindStatus.VALID)
        self.assertEqual(keybind.suggestion, 'Test suggestion')
    
    def test_keybind_report_dataclass(self):
        """Test KeybindReport dataclass."""
        keybinds = [
            Keybind(
                name='test1',
                key='F1',
                category=KeybindCategory.COMBAT,
                description='Test 1',
                status=KeybindStatus.VALID
            ),
            Keybind(
                name='test2',
                key='',
                category=KeybindCategory.INTERACTION,
                description='Test 2',
                status=KeybindStatus.MISSING
            )
        ]
        
        report = KeybindReport(
            total_keybinds=2,
            valid_keybinds=1,
            missing_keybinds=1,
            conflicting_keybinds=0,
            unknown_keybinds=0,
            keybinds=keybinds,
            suggestions=['Test suggestion'],
            swg_directory='/test/path',
            config_files_found=['/test/options.cfg']
        )
        
        self.assertEqual(report.total_keybinds, 2)
        self.assertEqual(report.valid_keybinds, 1)
        self.assertEqual(report.missing_keybinds, 1)
        self.assertEqual(len(report.keybinds), 2)
        self.assertEqual(len(report.suggestions), 1)
        self.assertEqual(report.swg_directory, '/test/path')
        self.assertEqual(len(report.config_files_found), 1)


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global convenience functions."""
    
    def test_get_keybind_manager(self):
        """Test get_keybind_manager function."""
        manager1 = get_keybind_manager()
        manager2 = get_keybind_manager()
        
        # Should return the same instance (singleton)
        self.assertIs(manager1, manager2)
        
        # Test with custom directory - note that the manager will still use auto-detected path
        # since the singleton pattern returns the first created instance
        custom_manager = get_keybind_manager("/custom/path")
        # The singleton pattern means we get the first manager instance
        self.assertEqual(custom_manager.swg_directory, manager1.swg_directory)
    
    def test_validate_keybinds(self):
        """Test validate_keybinds function."""
        report = validate_keybinds()
        self.assertIsInstance(report, KeybindReport)
    
    def test_save_keybind_report(self):
        """Test save_keybind_report function."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            report_file = f.name
        
        try:
            save_keybind_report(report_file)
            self.assertTrue(os.path.exists(report_file))
            
            # Verify file contains valid JSON
            with open(report_file, 'r') as f:
                data = json.load(f)
            self.assertIn('total_keybinds', data)
            
        finally:
            os.unlink(report_file)


class TestKeybindStatus(unittest.TestCase):
    """Test cases for KeybindStatus enum."""
    
    def test_keybind_status_values(self):
        """Test KeybindStatus enum values."""
        self.assertEqual(KeybindStatus.VALID.value, 'valid')
        self.assertEqual(KeybindStatus.MISSING.value, 'missing')
        self.assertEqual(KeybindStatus.CONFLICT.value, 'conflict')
        self.assertEqual(KeybindStatus.UNKNOWN.value, 'unknown')


class TestKeybindCategory(unittest.TestCase):
    """Test cases for KeybindCategory enum."""
    
    def test_keybind_category_values(self):
        """Test KeybindCategory enum values."""
        categories = {
            KeybindCategory.COMBAT: 'combat',
            KeybindCategory.INTERACTION: 'interaction',
            KeybindCategory.INVENTORY: 'inventory',
            KeybindCategory.NAVIGATION: 'navigation',
            KeybindCategory.MOVEMENT: 'movement',
            KeybindCategory.CHAT: 'chat',
            KeybindCategory.CAMERA: 'camera',
            KeybindCategory.OTHER: 'other'
        }
        
        for category, expected_value in categories.items():
            self.assertEqual(category.value, expected_value)


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling."""
    
    def test_parse_config_file_error(self):
        """Test error handling in config file parsing."""
        manager = KeybindManager()
        
        # Test with non-existent file
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            manager._parse_config_file("/nonexistent/file.cfg")
            # Should not raise exception, just log warning
    
    def test_load_manual_overrides_error(self):
        """Test error handling in manual override loading."""
        manager = KeybindManager()
        
        # Test with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            override_file = f.name
        
        try:
            manager.load_manual_overrides(override_file)
            # Should not raise exception, just log warning
        finally:
            os.unlink(override_file)


if __name__ == '__main__':
    unittest.main() 
#!/usr/bin/env python3
"""
Test suite for Batch 040 - Planetary & Galactic Fallback Pathing

This test suite validates the fallback navigation system that provides default
navigation logic for zones without quest profiles by using generic waypoints
and fallback loops.

Test coverage:
- Zone profile loading and validation
- Generic exploration patterns
- Navigation loop execution
- Dynamic scanning capabilities
- State tracking and reporting
- Error handling and edge cases
- Integration with existing systems
"""

import unittest
import tempfile
import yaml
import time
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from navigation.fallback_nav import (
    FallbackNavigator,
    FallbackStatus,
    Hotspot,
    ZoneProfile,
    FallbackState,
    get_fallback_navigator,
    start_fallback_navigation,
    execute_navigation_loop,
    get_fallback_status,
    get_zone_profile
)
from core.state_tracker import update_state, get_state


class TestFallbackNavigationDataStructures(unittest.TestCase):
    """Test the data structures used in fallback navigation."""
    
    def test_hotspot_creation(self):
        """Test Hotspot dataclass creation and methods."""
        hotspot = Hotspot(
            name="test_hotspot",
            x=100,
            y=200,
            description="Test hotspot description",
            scan_radius=50,
            scan_time=5
        )
        
        self.assertEqual(hotspot.name, "test_hotspot")
        self.assertEqual(hotspot.x, 100)
        self.assertEqual(hotspot.y, 200)
        self.assertEqual(hotspot.description, "Test hotspot description")
        self.assertEqual(hotspot.scan_radius, 50)
        self.assertEqual(hotspot.scan_time, 5)
    
    def test_hotspot_to_waypoint(self):
        """Test Hotspot.to_waypoint() method."""
        hotspot = Hotspot(
            name="test_hotspot",
            x=100,
            y=200,
            description="Test hotspot description",
            scan_radius=50,
            scan_time=5
        )
        
        waypoint = hotspot.to_waypoint("test_planet", "test_zone")
        
        self.assertEqual(waypoint.x, 100)
        self.assertEqual(waypoint.y, 200)
        self.assertEqual(waypoint.name, "test_hotspot")
        self.assertEqual(waypoint.planet, "test_planet")
        self.assertEqual(waypoint.zone, "test_zone")
        self.assertEqual(waypoint.description, "Test hotspot description")
    
    def test_zone_profile_creation(self):
        """Test ZoneProfile dataclass creation and methods."""
        hotspots = [
            Hotspot("hotspot1", 100, 200, "First hotspot", 50, 5),
            Hotspot("hotspot2", 300, 400, "Second hotspot", 60, 6)
        ]
        
        profile = ZoneProfile(
            name="test_zone",
            description="Test zone description",
            hotspots=hotspots,
            navigation_loop=["hotspot1", "hotspot2"],
            scan_interval=45,
            max_loop_iterations=3
        )
        
        self.assertEqual(profile.name, "test_zone")
        self.assertEqual(profile.description, "Test zone description")
        self.assertEqual(len(profile.hotspots), 2)
        self.assertEqual(profile.navigation_loop, ["hotspot1", "hotspot2"])
        self.assertEqual(profile.scan_interval, 45)
        self.assertEqual(profile.max_loop_iterations, 3)
    
    def test_zone_profile_get_hotspot_by_name(self):
        """Test ZoneProfile.get_hotspot_by_name() method."""
        hotspots = [
            Hotspot("hotspot1", 100, 200, "First hotspot", 50, 5),
            Hotspot("hotspot2", 300, 400, "Second hotspot", 60, 6)
        ]
        
        profile = ZoneProfile(
            name="test_zone",
            description="Test zone description",
            hotspots=hotspots,
            navigation_loop=["hotspot1", "hotspot2"],
            scan_interval=45,
            max_loop_iterations=3
        )
        
        # Test existing hotspot
        hotspot = profile.get_hotspot_by_name("hotspot1")
        self.assertIsNotNone(hotspot)
        self.assertEqual(hotspot.name, "hotspot1")
        
        # Test non-existing hotspot
        hotspot = profile.get_hotspot_by_name("nonexistent")
        self.assertIsNone(hotspot)
    
    def test_fallback_state_creation(self):
        """Test FallbackState dataclass creation and initialization."""
        state = FallbackState()
        
        self.assertIsNone(state.current_zone)
        self.assertIsNone(state.current_hotspot)
        self.assertEqual(state.status, FallbackStatus.IDLE)
        self.assertIsNone(state.start_time)
        self.assertEqual(state.loop_iterations, 0)
        self.assertEqual(state.hotspots_visited, [])
        self.assertEqual(state.quests_found, [])
        self.assertEqual(state.npcs_found, [])
        self.assertEqual(state.pois_found, [])
    
    def test_fallback_status_enum(self):
        """Test FallbackStatus enum values."""
        self.assertEqual(FallbackStatus.IDLE.value, "idle")
        self.assertEqual(FallbackStatus.EXPLORING.value, "exploring")
        self.assertEqual(FallbackStatus.SCANNING.value, "scanning")
        self.assertEqual(FallbackStatus.INTERACTING.value, "interacting")
        self.assertEqual(FallbackStatus.COMBAT.value, "combat")
        self.assertEqual(FallbackStatus.COMPLETED.value, "completed")
        self.assertEqual(FallbackStatus.FAILED.value, "failed")


class TestFallbackNavigatorInitialization(unittest.TestCase):
    """Test FallbackNavigator initialization and configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary fallback paths file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_file_path = self.temp_file.name
        
        # Write test data
        test_data = {
            "planets": {
                "test_planet": {
                    "name": "Test Planet",
                    "description": "Test planet description",
                    "zones": {
                        "test_zone": {
                            "name": "Test Zone",
                            "description": "Test zone description",
                            "hotspots": [
                                {
                                    "name": "test_hotspot",
                                    "x": 100,
                                    "y": 200,
                                    "description": "Test hotspot",
                                    "scan_radius": 50,
                                    "scan_time": 5
                                }
                            ],
                            "navigation_loop": ["test_hotspot"],
                            "scan_interval": 45,
                            "max_loop_iterations": 3
                        }
                    }
                }
            },
            "patterns": {
                "test_pattern": {
                    "name": "Test Pattern",
                    "description": "Test pattern description",
                    "hotspots": [
                        {
                            "name": "pattern_hotspot",
                            "description": "Pattern hotspot",
                            "scan_radius": 50,
                            "scan_time": 5
                        }
                    ],
                    "navigation_loop": ["pattern_hotspot"],
                    "scan_interval": 45,
                    "max_loop_iterations": 3
                }
            },
            "scanning": {
                "npc_detection": {
                    "enabled": True,
                    "npc_types": ["quest_giver", "vendor"]
                },
                "quest_detection": {
                    "enabled": True,
                    "quest_indicators": ["quest_marker", "exclamation_mark"]
                },
                "poi_detection": {
                    "enabled": True,
                    "poi_types": ["cave_entrance", "ruins"]
                }
            },
            "settings": {
                "default_behavior": "explore",
                "max_fallback_time": 1800,
                "min_hotspot_time": 30,
                "max_hotspot_time": 120
            }
        }
        
        yaml.dump(test_data, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import os
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_fallback_navigator_initialization(self):
        """Test FallbackNavigator initialization with valid file."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        self.assertIsNotNone(navigator.fallback_data)
        self.assertIn("planets", navigator.fallback_data)
        self.assertIn("patterns", navigator.fallback_data)
        self.assertIn("scanning", navigator.fallback_data)
        self.assertIn("settings", navigator.fallback_data)
    
    def test_fallback_navigator_initialization_invalid_file(self):
        """Test FallbackNavigator initialization with invalid file."""
        navigator = FallbackNavigator("nonexistent_file.yaml")
        
        # Should handle gracefully and return empty dict
        self.assertEqual(navigator.fallback_data, {})
    
    def test_fallback_navigator_scanning_config(self):
        """Test scanning configuration loading."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        # Test NPC detection config
        self.assertTrue(navigator.npc_detection.get("enabled"))
        self.assertIn("quest_giver", navigator.npc_detection.get("npc_types", []))
        self.assertIn("vendor", navigator.npc_detection.get("npc_types", []))
        
        # Test quest detection config
        self.assertTrue(navigator.quest_detection.get("enabled"))
        self.assertIn("quest_marker", navigator.quest_detection.get("quest_indicators", []))
        self.assertIn("exclamation_mark", navigator.quest_detection.get("quest_indicators", []))
        
        # Test POI detection config
        self.assertTrue(navigator.poi_detection.get("enabled"))
        self.assertIn("cave_entrance", navigator.poi_detection.get("poi_types", []))
        self.assertIn("ruins", navigator.poi_detection.get("poi_types", []))
    
    def test_fallback_navigator_settings(self):
        """Test settings loading."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        self.assertEqual(navigator.settings.get("default_behavior"), "explore")
        self.assertEqual(navigator.settings.get("max_fallback_time"), 1800)
        self.assertEqual(navigator.settings.get("min_hotspot_time"), 30)
        self.assertEqual(navigator.settings.get("max_hotspot_time"), 120)


class TestZoneProfileLoading(unittest.TestCase):
    """Test zone profile loading functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_file_path = self.temp_file.name
        
        # Write test data with multiple planets and zones
        test_data = {
            "planets": {
                "tatooine": {
                    "name": "Tatooine",
                    "description": "Desert planet",
                    "zones": {
                        "mos_eisley": {
                            "name": "Mos Eisley",
                            "description": "Spaceport city",
                            "hotspots": [
                                {
                                    "name": "cantina",
                                    "x": 100,
                                    "y": 200,
                                    "description": "Cantina",
                                    "scan_radius": 50,
                                    "scan_time": 5
                                },
                                {
                                    "name": "market",
                                    "x": 300,
                                    "y": 400,
                                    "description": "Market",
                                    "scan_radius": 60,
                                    "scan_time": 6
                                }
                            ],
                            "navigation_loop": ["cantina", "market"],
                            "scan_interval": 45,
                            "max_loop_iterations": 3
                        }
                    }
                },
                "naboo": {
                    "name": "Naboo",
                    "description": "Peaceful planet",
                    "zones": {
                        "theed": {
                            "name": "Theed",
                            "description": "Royal capital",
                            "hotspots": [
                                {
                                    "name": "palace",
                                    "x": 500,
                                    "y": 600,
                                    "description": "Royal palace",
                                    "scan_radius": 70,
                                    "scan_time": 7
                                }
                            ],
                            "navigation_loop": ["palace"],
                            "scan_interval": 60,
                            "max_loop_iterations": 2
                        }
                    }
                }
            }
        }
        
        yaml.dump(test_data, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import os
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_get_zone_profile_existing(self):
        """Test getting existing zone profile."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        profile = navigator.get_zone_profile("tatooine", "mos_eisley")
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, "Mos Eisley")
        self.assertEqual(profile.description, "Spaceport city")
        self.assertEqual(len(profile.hotspots), 2)
        self.assertEqual(profile.navigation_loop, ["cantina", "market"])
        self.assertEqual(profile.scan_interval, 45)
        self.assertEqual(profile.max_loop_iterations, 3)
    
    def test_get_zone_profile_nonexistent_planet(self):
        """Test getting zone profile for nonexistent planet."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        profile = navigator.get_zone_profile("nonexistent_planet", "mos_eisley")
        
        self.assertIsNone(profile)
    
    def test_get_zone_profile_nonexistent_zone(self):
        """Test getting zone profile for nonexistent zone."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        profile = navigator.get_zone_profile("tatooine", "nonexistent_zone")
        
        self.assertIsNone(profile)
    
    def test_get_zone_profile_case_insensitive(self):
        """Test zone profile lookup is case insensitive."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        # Test with different case combinations
        profile1 = navigator.get_zone_profile("TATOOINE", "MOS_EISLEY")
        profile2 = navigator.get_zone_profile("tatooine", "mos_eisley")
        
        self.assertIsNotNone(profile1)
        self.assertIsNotNone(profile2)
        self.assertEqual(profile1.name, profile2.name)
    
    def test_zone_profile_hotspots(self):
        """Test zone profile hotspots are correctly loaded."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        profile = navigator.get_zone_profile("tatooine", "mos_eisley")
        
        self.assertEqual(len(profile.hotspots), 2)
        
        # Check first hotspot
        hotspot1 = profile.hotspots[0]
        self.assertEqual(hotspot1.name, "cantina")
        self.assertEqual(hotspot1.x, 100)
        self.assertEqual(hotspot1.y, 200)
        self.assertEqual(hotspot1.description, "Cantina")
        self.assertEqual(hotspot1.scan_radius, 50)
        self.assertEqual(hotspot1.scan_time, 5)
        
        # Check second hotspot
        hotspot2 = profile.hotspots[1]
        self.assertEqual(hotspot2.name, "market")
        self.assertEqual(hotspot2.x, 300)
        self.assertEqual(hotspot2.y, 400)
        self.assertEqual(hotspot2.description, "Market")
        self.assertEqual(hotspot2.scan_radius, 60)
        self.assertEqual(hotspot2.scan_time, 6)


class TestGenericPatterns(unittest.TestCase):
    """Test generic exploration patterns."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_file_path = self.temp_file.name
        
        # Write test data with generic patterns
        test_data = {
            "patterns": {
                "standard_exploration": {
                    "name": "Standard Exploration",
                    "description": "Basic exploration pattern",
                    "hotspots": [
                        {
                            "name": "zone_center",
                            "description": "Zone center",
                            "scan_radius": 50,
                            "scan_time": 5
                        },
                        {
                            "name": "zone_cantina",
                            "description": "Local cantina",
                            "scan_radius": 40,
                            "scan_time": 4
                        }
                    ],
                    "navigation_loop": ["zone_center", "zone_cantina"],
                    "scan_interval": 45,
                    "max_loop_iterations": 3
                },
                "combat_exploration": {
                    "name": "Combat Exploration",
                    "description": "Combat-focused pattern",
                    "hotspots": [
                        {
                            "name": "combat_zone_center",
                            "description": "Combat zone center",
                            "scan_radius": 60,
                            "scan_time": 6
                        }
                    ],
                    "navigation_loop": ["combat_zone_center"],
                    "scan_interval": 30,
                    "max_loop_iterations": 5
                }
            }
        }
        
        yaml.dump(test_data, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import os
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_get_generic_pattern_existing(self):
        """Test getting existing generic pattern."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        pattern = navigator.get_generic_pattern("standard_exploration")
        
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.name, "Standard Exploration")
        self.assertEqual(pattern.description, "Basic exploration pattern")
        self.assertEqual(len(pattern.hotspots), 2)
        self.assertEqual(pattern.navigation_loop, ["zone_center", "zone_cantina"])
        self.assertEqual(pattern.scan_interval, 45)
        self.assertEqual(pattern.max_loop_iterations, 3)
    
    def test_get_generic_pattern_nonexistent(self):
        """Test getting nonexistent generic pattern."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        pattern = navigator.get_generic_pattern("nonexistent_pattern")
        
        self.assertIsNone(pattern)
    
    def test_generic_pattern_hotspots(self):
        """Test generic pattern hotspots are correctly loaded."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        pattern = navigator.get_generic_pattern("standard_exploration")
        
        self.assertEqual(len(pattern.hotspots), 2)
        
        # Check first hotspot
        hotspot1 = pattern.hotspots[0]
        self.assertEqual(hotspot1.name, "zone_center")
        self.assertEqual(hotspot1.x, 0)  # Generic patterns don't have specific coordinates
        self.assertEqual(hotspot1.y, 0)
        self.assertEqual(hotspot1.description, "Zone center")
        self.assertEqual(hotspot1.scan_radius, 50)
        self.assertEqual(hotspot1.scan_time, 5)
        
        # Check second hotspot
        hotspot2 = pattern.hotspots[1]
        self.assertEqual(hotspot2.name, "zone_cantina")
        self.assertEqual(hotspot2.description, "Local cantina")
        self.assertEqual(hotspot2.scan_radius, 40)
        self.assertEqual(hotspot2.scan_time, 4)


class TestFallbackNavigationExecution(unittest.TestCase):
    """Test fallback navigation execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_file_path = self.temp_file.name
        
        # Write test data
        test_data = {
            "planets": {
                "test_planet": {
                    "name": "Test Planet",
                    "zones": {
                        "test_zone": {
                            "name": "Test Zone",
                            "description": "Test zone description",
                            "hotspots": [
                                {
                                    "name": "hotspot1",
                                    "x": 100,
                                    "y": 200,
                                    "description": "First hotspot",
                                    "scan_radius": 50,
                                    "scan_time": 5
                                },
                                {
                                    "name": "hotspot2",
                                    "x": 300,
                                    "y": 400,
                                    "description": "Second hotspot",
                                    "scan_radius": 60,
                                    "scan_time": 6
                                }
                            ],
                            "navigation_loop": ["hotspot1", "hotspot2"],
                            "scan_interval": 45,
                            "max_loop_iterations": 2
                        }
                    }
                }
            },
            "patterns": {
                "test_pattern": {
                    "name": "Test Pattern",
                    "description": "Test pattern description",
                    "hotspots": [
                        {
                            "name": "pattern_hotspot",
                            "description": "Pattern hotspot",
                            "scan_radius": 50,
                            "scan_time": 5
                        }
                    ],
                    "navigation_loop": ["pattern_hotspot"],
                    "scan_interval": 45,
                    "max_loop_iterations": 3
                }
            },
            "scanning": {
                "npc_detection": {"enabled": True, "npc_types": ["quest_giver"]},
                "quest_detection": {"enabled": True, "quest_indicators": ["quest_marker"]},
                "poi_detection": {"enabled": True, "poi_types": ["cave_entrance"]}
            },
            "settings": {
                "enable_npc_interaction": True,
                "enable_combat": True,
                "enable_resource_gathering": True,
                "min_hotspot_time": 1,
                "max_hotspot_time": 2
            }
        }
        
        yaml.dump(test_data, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import os
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    @patch('navigation.fallback_nav.get_navigator')
    @patch('navigation.fallback_nav.OCREngine')
    @patch('navigation.fallback_nav.capture_screen')
    def test_start_fallback_navigation_success(self, mock_capture, mock_ocr, mock_navigator):
        """Test successful fallback navigation start."""
        # Mock dependencies
        mock_nav = Mock()
        mock_navigator.return_value = mock_nav
        
        navigator = FallbackNavigator(self.temp_file_path)
        
        success = navigator.start_fallback_navigation("test_planet", "test_zone")
        
        self.assertTrue(success)
        self.assertIsNotNone(navigator.state.current_zone)
        self.assertEqual(navigator.state.status, FallbackStatus.EXPLORING)
        self.assertIsNotNone(navigator.state.start_time)
    
    @patch('navigation.fallback_nav.get_navigator')
    @patch('navigation.fallback_nav.OCREngine')
    def test_start_fallback_navigation_with_generic_pattern(self, mock_ocr, mock_navigator):
        """Test fallback navigation start with generic pattern."""
        # Mock dependencies
        mock_nav = Mock()
        mock_navigator.return_value = mock_nav
        
        navigator = FallbackNavigator(self.temp_file_path)
        
        success = navigator.start_fallback_navigation(
            "nonexistent_planet", 
            "nonexistent_zone",
            "test_pattern"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(navigator.state.current_zone)
        self.assertEqual(navigator.state.current_zone.name, "Test Pattern")
    
    @patch('navigation.fallback_nav.get_navigator')
    @patch('navigation.fallback_nav.OCREngine')
    def test_start_fallback_navigation_failure(self, mock_ocr, mock_navigator):
        """Test fallback navigation start failure."""
        # Mock dependencies
        mock_nav = Mock()
        mock_navigator.return_value = mock_nav
        
        navigator = FallbackNavigator(self.temp_file_path)
        
        success = navigator.start_fallback_navigation(
            "nonexistent_planet", 
            "nonexistent_zone",
            "nonexistent_pattern"
        )
        
        self.assertFalse(success)
    
    @patch('navigation.fallback_nav.get_navigator')
    @patch('navigation.fallback_nav.OCREngine')
    @patch('navigation.fallback_nav.capture_screen')
    def test_execute_navigation_loop(self, mock_capture, mock_ocr, mock_navigator):
        """Test navigation loop execution."""
        # Mock dependencies
        mock_nav = Mock()
        mock_nav.navigate_to_waypoint.return_value = True
        mock_navigator.return_value = mock_nav
        
        mock_ocr_instance = Mock()
        mock_ocr_instance.extract_text.return_value = Mock(text="test text")
        mock_ocr.return_value = mock_ocr_instance
        
        navigator = FallbackNavigator(self.temp_file_path)
        
        # Start navigation
        success = navigator.start_fallback_navigation("test_planet", "test_zone")
        self.assertTrue(success)
        
        # Execute loop
        success = navigator.execute_navigation_loop()
        
        self.assertTrue(success)
        self.assertEqual(navigator.state.loop_iterations, 1)
    
    @patch('navigation.fallback_nav.get_navigator')
    @patch('navigation.fallback_nav.OCREngine')
    @patch('navigation.fallback_nav.capture_screen')
    def test_navigation_loop_max_iterations(self, mock_capture, mock_ocr, mock_navigator):
        """Test navigation loop respects max iterations."""
        # Mock dependencies
        mock_nav = Mock()
        mock_nav.navigate_to_waypoint.return_value = True
        mock_navigator.return_value = mock_nav
        
        mock_ocr_instance = Mock()
        mock_ocr_instance.extract_text.return_value = Mock(text="test text")
        mock_ocr.return_value = mock_ocr_instance
        
        navigator = FallbackNavigator(self.temp_file_path)
        
        # Start navigation
        success = navigator.start_fallback_navigation("test_planet", "test_zone")
        self.assertTrue(success)
        
        # Execute loops up to max iterations
        for i in range(3):  # Max iterations is 2, so third should complete
            success = navigator.execute_navigation_loop()
            self.assertTrue(success)
        
        # Should be completed after max iterations
        self.assertEqual(navigator.state.status, FallbackStatus.COMPLETED)


class TestDynamicScanning(unittest.TestCase):
    """Test dynamic scanning capabilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_file_path = self.temp_file.name
        
        # Write test data with scanning configuration
        test_data = {
            "scanning": {
                "npc_detection": {
                    "enabled": True,
                    "npc_types": ["quest_giver", "vendor", "trainer"]
                },
                "quest_detection": {
                    "enabled": True,
                    "quest_indicators": ["quest_marker", "exclamation_mark", "question_mark"]
                },
                "poi_detection": {
                    "enabled": True,
                    "poi_types": ["cave_entrance", "ruins", "camp"]
                }
            },
            "settings": {
                "enable_npc_interaction": True,
                "enable_combat": True,
                "enable_resource_gathering": True
            }
        }
        
        yaml.dump(test_data, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import os
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    @patch('navigation.fallback_nav.capture_screen')
    @patch('navigation.fallback_nav.OCREngine')
    def test_scan_at_hotspot(self, mock_ocr, mock_capture):
        """Test scanning at hotspot."""
        # Mock dependencies
        mock_capture.return_value = "mock_image"
        mock_ocr_instance = Mock()
        mock_ocr_instance.extract_text.return_value = Mock(text="quest_marker found here")
        mock_ocr.return_value = mock_ocr_instance
        
        navigator = FallbackNavigator(self.temp_file_path)
        
        hotspot = Hotspot("test_hotspot", 100, 200, "Test hotspot", 50, 1)
        
        # Initialize state
        navigator.state = FallbackState()
        
        # Perform scan
        navigator._scan_at_hotspot(hotspot)
        
        # Check that quest was detected
        self.assertIn("test_hotspot_quest_0", navigator.state.quests_found)
    
    def test_check_for_quests(self):
        """Test quest detection in scanned text."""
        navigator = FallbackNavigator(self.temp_file_path)
        navigator.state = FallbackState()
        
        hotspot = Hotspot("test_hotspot", 100, 200, "Test hotspot", 50, 5)
        
        # Test with quest indicator
        navigator._check_for_quests("quest_marker found", hotspot)
        
        self.assertEqual(len(navigator.state.quests_found), 1)
        self.assertIn("test_hotspot_quest_0", navigator.state.quests_found)
    
    def test_check_for_npcs(self):
        """Test NPC detection in scanned text."""
        navigator = FallbackNavigator(self.temp_file_path)
        navigator.state = FallbackState()
        
        hotspot = Hotspot("test_hotspot", 100, 200, "Test hotspot", 50, 5)
        
        # Test with NPC type
        navigator._check_for_npcs("quest_giver found", hotspot)
        
        self.assertEqual(len(navigator.state.npcs_found), 1)
        self.assertIn("test_hotspot_quest_giver_0", navigator.state.npcs_found)
    
    def test_check_for_pois(self):
        """Test POI detection in scanned text."""
        navigator = FallbackNavigator(self.temp_file_path)
        navigator.state = FallbackState()
        
        hotspot = Hotspot("test_hotspot", 100, 200, "Test hotspot", 50, 5)
        
        # Test with POI type
        navigator._check_for_pois("cave_entrance found", hotspot)
        
        self.assertEqual(len(navigator.state.pois_found), 1)
        self.assertIn("test_hotspot_cave_entrance_0", navigator.state.pois_found)


class TestStateTracking(unittest.TestCase):
    """Test state tracking functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_file_path = self.temp_file.name
        
        # Write minimal test data
        test_data = {
            "planets": {},
            "patterns": {},
            "scanning": {},
            "settings": {}
        }
        
        yaml.dump(test_data, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import os
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_update_fallback_state(self):
        """Test fallback state update."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        # Set up state
        hotspot = Hotspot("test_hotspot", 100, 200, "Test hotspot", 50, 5)
        zone_profile = ZoneProfile(
            name="Test Zone",
            description="Test zone",
            hotspots=[hotspot],
            navigation_loop=["test_hotspot"],
            scan_interval=45,
            max_loop_iterations=3
        )
        
        navigator.state = FallbackState(
            current_zone=zone_profile,
            current_hotspot=hotspot,
            status=FallbackStatus.EXPLORING,
            start_time=time.time(),
            loop_iterations=1,
            hotspots_visited=["test_hotspot"],
            quests_found=["quest1"],
            npcs_found=["npc1"],
            pois_found=["poi1"]
        )
        
        # Update state
        navigator._update_fallback_state()
        
        # Verify state was updated (this would require mocking update_state)
        # For now, just verify no exceptions are raised
        self.assertTrue(True)
    
    def test_get_fallback_status(self):
        """Test getting fallback status."""
        navigator = FallbackNavigator(self.temp_file_path)
        
        # Set up state
        hotspot = Hotspot("test_hotspot", 100, 200, "Test hotspot", 50, 5)
        zone_profile = ZoneProfile(
            name="Test Zone",
            description="Test zone",
            hotspots=[hotspot],
            navigation_loop=["test_hotspot"],
            scan_interval=45,
            max_loop_iterations=3
        )
        
        navigator.state = FallbackState(
            current_zone=zone_profile,
            current_hotspot=hotspot,
            status=FallbackStatus.EXPLORING,
            start_time=time.time(),
            loop_iterations=1,
            hotspots_visited=["test_hotspot"],
            quests_found=["quest1"],
            npcs_found=["npc1"],
            pois_found=["poi1"]
        )
        
        # Get status
        status = navigator.get_fallback_status()
        
        self.assertEqual(status["status"], "exploring")
        self.assertEqual(status["zone"], "Test Zone")
        self.assertEqual(status["hotspot"], "test_hotspot")
        self.assertEqual(status["loop_iterations"], 1)
        self.assertEqual(status["hotspots_visited"], 1)
        self.assertEqual(status["quests_found"], 1)
        self.assertEqual(status["npcs_found"], 1)
        self.assertEqual(status["pois_found"], 1)


class TestGlobalFunctions(unittest.TestCase):
    """Test global functions for fallback navigation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_file_path = self.temp_file.name
        
        # Write test data
        test_data = {
            "planets": {
                "test_planet": {
                    "name": "Test Planet",
                    "zones": {
                        "test_zone": {
                            "name": "Test Zone",
                            "description": "Test zone description",
                            "hotspots": [
                                {
                                    "name": "test_hotspot",
                                    "x": 100,
                                    "y": 200,
                                    "description": "Test hotspot",
                                    "scan_radius": 50,
                                    "scan_time": 5
                                }
                            ],
                            "navigation_loop": ["test_hotspot"],
                            "scan_interval": 45,
                            "max_loop_iterations": 3
                        }
                    }
                }
            },
            "patterns": {
                "test_pattern": {
                    "name": "Test Pattern",
                    "description": "Test pattern description",
                    "hotspots": [
                        {
                            "name": "pattern_hotspot",
                            "description": "Pattern hotspot",
                            "scan_radius": 50,
                            "scan_time": 5
                        }
                    ],
                    "navigation_loop": ["pattern_hotspot"],
                    "scan_interval": 45,
                    "max_loop_iterations": 3
                }
            },
            "scanning": {},
            "settings": {}
        }
        
        yaml.dump(test_data, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import os
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    @patch('navigation.fallback_nav.FallbackNavigator')
    def test_get_fallback_navigator(self, mock_navigator_class):
        """Test get_fallback_navigator function."""
        # Mock the navigator class
        mock_navigator = Mock()
        mock_navigator_class.return_value = mock_navigator
        
        # Get navigator
        navigator = get_fallback_navigator()
        
        self.assertEqual(navigator, mock_navigator)
        mock_navigator_class.assert_called_once()
    
    @patch('navigation.fallback_nav.get_fallback_navigator')
    def test_start_fallback_navigation_global(self, mock_get_navigator):
        """Test global start_fallback_navigation function."""
        # Mock navigator
        mock_navigator = Mock()
        mock_navigator.start_fallback_navigation.return_value = True
        mock_get_navigator.return_value = mock_navigator
        
        # Test function
        success = start_fallback_navigation("test_planet", "test_zone", "test_pattern")
        
        self.assertTrue(success)
        mock_navigator.start_fallback_navigation.assert_called_once_with(
            "test_planet", "test_zone", "test_pattern"
        )
    
    @patch('navigation.fallback_nav.get_fallback_navigator')
    def test_execute_navigation_loop_global(self, mock_get_navigator):
        """Test global execute_navigation_loop function."""
        # Mock navigator
        mock_navigator = Mock()
        mock_navigator.execute_navigation_loop.return_value = True
        mock_get_navigator.return_value = mock_navigator
        
        # Test function
        success = execute_navigation_loop()
        
        self.assertTrue(success)
        mock_navigator.execute_navigation_loop.assert_called_once()
    
    @patch('navigation.fallback_nav.get_fallback_navigator')
    def test_get_fallback_status_global(self, mock_get_navigator):
        """Test global get_fallback_status function."""
        # Mock navigator
        mock_navigator = Mock()
        mock_status = {"status": "exploring", "zone": "Test Zone"}
        mock_navigator.get_fallback_status.return_value = mock_status
        mock_get_navigator.return_value = mock_navigator
        
        # Test function
        status = get_fallback_status()
        
        self.assertEqual(status, mock_status)
        mock_navigator.get_fallback_status.assert_called_once()
    
    @patch('navigation.fallback_nav.get_fallback_navigator')
    def test_get_zone_profile_global(self, mock_get_navigator):
        """Test global get_zone_profile function."""
        # Mock navigator
        mock_navigator = Mock()
        mock_profile = Mock()
        mock_navigator.get_zone_profile.return_value = mock_profile
        mock_get_navigator.return_value = mock_navigator
        
        # Test function
        profile = get_zone_profile("test_planet", "test_zone")
        
        self.assertEqual(profile, mock_profile)
        mock_navigator.get_zone_profile.assert_called_once_with("test_planet", "test_zone")


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_fallback_navigator_invalid_file(self):
        """Test FallbackNavigator with invalid file path."""
        navigator = FallbackNavigator("nonexistent_file.yaml")
        
        # Should handle gracefully
        self.assertEqual(navigator.fallback_data, {})
    
    def test_get_zone_profile_empty_data(self):
        """Test get_zone_profile with empty data."""
        navigator = FallbackNavigator("nonexistent_file.yaml")
        
        profile = navigator.get_zone_profile("test_planet", "test_zone")
        
        self.assertIsNone(profile)
    
    def test_get_generic_pattern_empty_data(self):
        """Test get_generic_pattern with empty data."""
        navigator = FallbackNavigator("nonexistent_file.yaml")
        
        pattern = navigator.get_generic_pattern("test_pattern")
        
        self.assertIsNone(pattern)
    
    def test_navigation_loop_no_current_zone(self):
        """Test navigation loop execution without current zone."""
        navigator = FallbackNavigator("nonexistent_file.yaml")
        
        success = navigator.execute_navigation_loop()
        
        self.assertFalse(success)
    
    def test_scan_at_hotspot_exception_handling(self):
        """Test scan_at_hotspot exception handling."""
        navigator = FallbackNavigator("nonexistent_file.yaml")
        
        hotspot = Hotspot("test_hotspot", 100, 200, "Test hotspot", 50, 5)
        
        # Should handle exceptions gracefully
        try:
            navigator._scan_at_hotspot(hotspot)
        except Exception:
            self.fail("_scan_at_hotspot should handle exceptions gracefully")


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 
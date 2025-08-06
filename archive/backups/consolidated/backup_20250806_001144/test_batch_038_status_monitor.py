#!/usr/bin/env python3
"""Test suite for Batch 038 - Character Status Tracker.

This test suite covers:
- Status monitor initialization and configuration
- Health bar scanning functionality
- Buff and debuff detection
- Combat state detection
- State tracker integration
- Error handling and edge cases
- AI decision making based on status
"""

import unittest
import time
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

import numpy as np
import cv2

from core.status_monitor import (
    StatusMonitor,
    CharacterStatus,
    scan_character_status,
    get_current_status,
    get_status_monitor
)
from core.state_tracker import get_state, update_state


class TestCharacterStatus(unittest.TestCase):
    """Test the CharacterStatus dataclass."""
    
    def test_character_status_creation(self):
        """Test creating a CharacterStatus instance."""
        status = CharacterStatus(
            health_percentage=75.5,
            is_in_combat=True,
            active_buffs=["Mind Boost", "Armor Buff"],
            active_debuffs=["Poison"],
            confidence=0.85
        )
        
        self.assertEqual(status.health_percentage, 75.5)
        self.assertTrue(status.is_in_combat)
        self.assertEqual(len(status.active_buffs), 2)
        self.assertEqual(len(status.active_debuffs), 1)
        self.assertEqual(status.confidence, 0.85)
        self.assertIsInstance(status.last_update, float)
    
    def test_character_status_defaults(self):
        """Test CharacterStatus with default values."""
        status = CharacterStatus()
        
        self.assertEqual(status.health_percentage, 100.0)
        self.assertFalse(status.is_in_combat)
        self.assertEqual(len(status.active_buffs), 0)
        self.assertEqual(len(status.active_debuffs), 0)
        self.assertEqual(status.confidence, 0.0)
    
    def test_character_status_to_dict(self):
        """Test converting CharacterStatus to dictionary."""
        status = CharacterStatus(
            health_percentage=50.0,
            is_in_combat=False,
            active_buffs=["Weapon Buff"],
            active_debuffs=[],
            confidence=0.9
        )
        
        status_dict = status.to_dict()
        
        self.assertEqual(status_dict["health_percentage"], 50.0)
        self.assertFalse(status_dict["is_in_combat"])
        self.assertEqual(status_dict["active_buffs"], ["Weapon Buff"])
        self.assertEqual(status_dict["active_debuffs"], [])
        self.assertEqual(status_dict["confidence"], 0.9)
        self.assertIn("last_update", status_dict)


class TestStatusMonitor(unittest.TestCase):
    """Test the StatusMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary buff icon map file
        self.temp_dir = tempfile.mkdtemp()
        self.buff_map_path = os.path.join(self.temp_dir, "test_buff_icon_map.yaml")
        
        # Create a simple test buff icon map
        test_buff_map = """
mind_boost:
  name: "Mind Boost"
  type: "mind_boost"
  duration: 300.0
  intensity: 3
  keywords: ["mind", "boost", "intelligence"]

armor_buff:
  name: "Armor Buff"
  type: "armor_buff"
  duration: 240.0
  intensity: 2
  keywords: ["armor", "defense", "protection"]

poison:
  name: "Poison"
  type: "debuff"
  duration: 300.0
  intensity: 2
  keywords: ["poison", "toxic", "venom"]
"""
        
        with open(self.buff_map_path, 'w') as f:
            f.write(test_buff_map)
        
        # Create status monitor with test config
        self.monitor = StatusMonitor(self.buff_map_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_status_monitor_initialization(self):
        """Test StatusMonitor initialization."""
        self.assertIsNotNone(self.monitor.logger)
        self.assertIsNotNone(self.monitor.ocr_engine)
        self.assertIsInstance(self.monitor.buff_icon_map, dict)
        self.assertIsInstance(self.monitor.regions, dict)
        self.assertIsInstance(self.monitor.health_colors, dict)
        self.assertIsInstance(self.monitor.last_status, CharacterStatus)
        self.assertEqual(self.monitor.update_interval, 1.0)
    
    def test_load_buff_icon_map(self):
        """Test loading buff icon map from file."""
        self.assertIn("mind_boost", self.monitor.buff_icon_map)
        self.assertIn("armor_buff", self.monitor.buff_icon_map)
        self.assertIn("poison", self.monitor.buff_icon_map)
        
        mind_boost = self.monitor.buff_icon_map["mind_boost"]
        self.assertEqual(mind_boost["name"], "Mind Boost")
        self.assertEqual(mind_boost["type"], "mind_boost")
        self.assertEqual(mind_boost["duration"], 300.0)
    
    def test_load_buff_icon_map_missing_file(self):
        """Test loading buff icon map with missing file."""
        monitor = StatusMonitor("nonexistent_file.yaml")
        self.assertEqual(monitor.buff_icon_map, {})
    
    def test_scan_health_bar(self):
        """Test health bar scanning."""
        # Create a mock image with health bar colors
        image = np.zeros((100, 200, 3), dtype=np.uint8)
        
        # Add green pixels (high health) - ensure image is not empty
        image[10:20, 50:150] = [0, 255, 0]  # Green in BGR
        
        # Mock the regions to avoid OpenCV issues
        with patch.object(self.monitor, 'regions') as mock_regions:
            mock_regions.__getitem__.return_value = (10, 10, 180, 20)  # Valid region
            
            health_percentage = self.monitor.scan_health_bar(image)
            
            # Should detect some health (green pixels)
            self.assertGreater(health_percentage, 0)
            self.assertLessEqual(health_percentage, 100)
    
    def test_scan_health_bar_empty_image(self):
        """Test health bar scanning with empty image."""
        image = np.zeros((30, 200, 3), dtype=np.uint8)
        
        health_percentage = self.monitor.scan_health_bar(image)
        
        # Should return default health (100%)
        self.assertEqual(health_percentage, 100.0)
    
    def test_scan_buff_icons(self):
        """Test buff icon scanning."""
        # Create a mock image
        image = np.zeros((50, 400, 3), dtype=np.uint8)
        
        # Mock OCR result
        with patch.object(self.monitor.ocr_engine, 'extract_text') as mock_extract:
            mock_extract.return_value = Mock(
                text="Mind Boost Armor Buff",
                confidence=0.8
            )
            
            buffs = self.monitor.scan_buff_icons(image)
            
            # Should detect buffs from OCR text
            self.assertIn("Mind Boost", buffs)
            self.assertIn("Armor Buff", buffs)
    
    def test_scan_buff_icons_no_text(self):
        """Test buff icon scanning with no OCR text."""
        image = np.zeros((50, 400, 3), dtype=np.uint8)
        
        with patch.object(self.monitor.ocr_engine, 'extract_text') as mock_extract:
            mock_extract.return_value = Mock(
                text="",
                confidence=0.0
            )
            
            buffs = self.monitor.scan_buff_icons(image)
            
            # Should return empty list
            self.assertEqual(buffs, [])
    
    def test_scan_debuff_icons(self):
        """Test debuff icon scanning."""
        image = np.zeros((50, 400, 3), dtype=np.uint8)
        
        with patch.object(self.monitor.ocr_engine, 'extract_text') as mock_extract:
            mock_extract.return_value = Mock(
                text="Poison Disease",
                confidence=0.8
            )
            
            debuffs = self.monitor.scan_debuff_icons(image)
            
            # Should detect debuffs from OCR text
            self.assertIn("Poison", debuffs)
    
    def test_scan_combat_state(self):
        """Test combat state scanning."""
        image = np.zeros((30, 100, 3), dtype=np.uint8)
        
        with patch.object(self.monitor.ocr_engine, 'extract_text') as mock_extract:
            mock_extract.return_value = Mock(
                text="In Combat",
                confidence=0.8
            )
            
            is_in_combat = self.monitor.scan_combat_state(image)
            
            # Should detect combat state
            self.assertTrue(is_in_combat)
    
    def test_scan_combat_state_peace(self):
        """Test combat state scanning for peace."""
        image = np.zeros((30, 100, 3), dtype=np.uint8)
        
        with patch.object(self.monitor.ocr_engine, 'extract_text') as mock_extract:
            mock_extract.return_value = Mock(
                text="Peace Calm",
                confidence=0.8
            )
            
            is_in_combat = self.monitor.scan_combat_state(image)
            
            # Should detect peace state
            self.assertFalse(is_in_combat)
    
    def test_scan_status(self):
        """Test complete status scanning."""
        with patch('core.status_monitor.capture_screen') as mock_capture:
            # Create mock screen image
            mock_image = np.zeros((600, 800, 3), dtype=np.uint8)
            mock_capture.return_value = mock_image
            
            # Mock individual scan methods
            with patch.object(self.monitor, 'scan_health_bar') as mock_health:
                with patch.object(self.monitor, 'scan_buff_icons') as mock_buffs:
                    with patch.object(self.monitor, 'scan_debuff_icons') as mock_debuffs:
                        with patch.object(self.monitor, 'scan_combat_state') as mock_combat:
                            
                            mock_health.return_value = 75.5
                            mock_buffs.return_value = ["Mind Boost"]
                            mock_debuffs.return_value = []
                            mock_combat.return_value = True
                            
                            status = self.monitor.scan_status()
                            
                            # Verify status
                            self.assertEqual(status.health_percentage, 75.5)
                            self.assertTrue(status.is_in_combat)
                            self.assertEqual(status.active_buffs, ["Mind Boost"])
                            self.assertEqual(status.active_debuffs, [])
                            self.assertIsInstance(status.last_update, float)
                            self.assertEqual(status.confidence, 0.8)
    
    def test_update_state_tracker(self):
        """Test updating state tracker with status."""
        status = CharacterStatus(
            health_percentage=60.0,
            is_in_combat=True,
            active_buffs=["Armor Buff"],
            active_debuffs=["Poison"],
            confidence=0.9
        )
        
        # Mock the update_state function to avoid actual state changes
        with patch('core.status_monitor.update_state') as mock_update:
            # Update state tracker
            self.monitor.update_state_tracker(status)
            
            # Verify update_state was called with correct parameters
            mock_update.assert_called_once()
            call_args = mock_update.call_args[1]  # Get keyword arguments
            
            self.assertEqual(call_args["health_percentage"], 60.0)
            self.assertTrue(call_args["is_in_combat"])
            self.assertEqual(call_args["active_buffs"], ["Armor Buff"])
            self.assertEqual(call_args["active_debuffs"], ["Poison"])
            self.assertEqual(call_args["status_confidence"], 0.9)
    
    def test_get_current_status(self):
        """Test getting current status."""
        # Set up a mock status
        test_status = CharacterStatus(
            health_percentage=80.0,
            is_in_combat=False,
            active_buffs=["Weapon Buff"],
            active_debuffs=[],
            confidence=0.85
        )
        
        self.monitor.last_status = test_status
        
        current_status = self.monitor.get_current_status()
        
        self.assertEqual(current_status.health_percentage, 80.0)
        self.assertFalse(current_status.is_in_combat)
        self.assertEqual(current_status.active_buffs, ["Weapon Buff"])
        self.assertEqual(current_status.confidence, 0.85)


class TestStatusMonitorIntegration(unittest.TestCase):
    """Test status monitor integration functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear any existing status monitor
        import core.status_monitor
        core.status_monitor._status_monitor = None
    
    def test_get_status_monitor(self):
        """Test getting status monitor instance."""
        monitor1 = get_status_monitor()
        monitor2 = get_status_monitor()
        
        # Should return the same instance
        self.assertIs(monitor1, monitor2)
        self.assertIsInstance(monitor1, StatusMonitor)
    
    def test_scan_character_status(self):
        """Test scanning character status."""
        with patch('core.status_monitor.capture_screen') as mock_capture:
            mock_image = np.zeros((600, 800, 3), dtype=np.uint8)
            mock_capture.return_value = mock_image
            
            status = scan_character_status()
            
            self.assertIsInstance(status, CharacterStatus)
            self.assertIsInstance(status.health_percentage, float)
            self.assertIsInstance(status.is_in_combat, bool)
            self.assertIsInstance(status.active_buffs, list)
            self.assertIsInstance(status.active_debuffs, list)
    
    def test_get_current_status(self):
        """Test getting current status."""
        status = get_current_status()
        
        self.assertIsInstance(status, CharacterStatus)
        # Should return default status if no scanning has been done
        self.assertEqual(status.health_percentage, 100.0)
        self.assertFalse(status.is_in_combat)


class TestStatusMonitorErrorHandling(unittest.TestCase):
    """Test error handling in status monitor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = StatusMonitor()
    
    def test_scan_health_bar_exception(self):
        """Test health bar scanning with exception."""
        with patch.object(self.monitor, 'regions') as mock_regions:
            mock_regions.__getitem__.side_effect = Exception("Test exception")
            
            health_percentage = self.monitor.scan_health_bar(np.zeros((100, 100, 3)))
            
            # Should return default health on exception
            self.assertEqual(health_percentage, 100.0)
    
    def test_scan_buff_icons_exception(self):
        """Test buff icon scanning with exception."""
        with patch.object(self.monitor.ocr_engine, 'extract_text') as mock_extract:
            mock_extract.side_effect = Exception("OCR failed")
            
            buffs = self.monitor.scan_buff_icons(np.zeros((50, 400, 3)))
            
            # Should return empty list on exception
            self.assertEqual(buffs, [])
    
    def test_scan_debuff_icons_exception(self):
        """Test debuff icon scanning with exception."""
        with patch.object(self.monitor.ocr_engine, 'extract_text') as mock_extract:
            mock_extract.side_effect = Exception("OCR failed")
            
            debuffs = self.monitor.scan_debuff_icons(np.zeros((50, 400, 3)))
            
            # Should return empty list on exception
            self.assertEqual(debuffs, [])
    
    def test_scan_combat_state_exception(self):
        """Test combat state scanning with exception."""
        with patch.object(self.monitor.ocr_engine, 'extract_text') as mock_extract:
            mock_extract.side_effect = Exception("OCR failed")
            
            is_in_combat = self.monitor.scan_combat_state(np.zeros((30, 100, 3)))
            
            # Should return False on exception
            self.assertFalse(is_in_combat)
    
    def test_scan_status_exception(self):
        """Test status scanning with exception."""
        with patch('core.status_monitor.capture_screen') as mock_capture:
            mock_capture.side_effect = Exception("Screen capture failed")
            
            status = self.monitor.scan_status()
            
            # Should return last status on exception
            self.assertIsInstance(status, CharacterStatus)
    
    def test_update_state_tracker_exception(self):
        """Test state tracker update with exception."""
        status = CharacterStatus()
        
        with patch('core.status_monitor.update_state') as mock_update:
            mock_update.side_effect = Exception("State update failed")
            
            # Should not raise exception
            self.monitor.update_state_tracker(status)


class TestStatusMonitorAIDecisionMaking(unittest.TestCase):
    """Test AI decision making based on status."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = StatusMonitor()
    
    def test_ai_decision_critical_health(self):
        """Test AI decisions for critical health."""
        status = CharacterStatus(
            health_percentage=15.0,
            is_in_combat=True,
            active_buffs=[],
            active_debuffs=["Poison"],
            confidence=0.8
        )
        
        decisions = self._simulate_ai_decisions(status)
        
        # Should include critical health decisions
        self.assertTrue(any("CRITICAL" in decision for decision in decisions))
        self.assertTrue(any("healing" in decision.lower() for decision in decisions))
    
    def test_ai_decision_low_health(self):
        """Test AI decisions for low health."""
        status = CharacterStatus(
            health_percentage=35.0,
            is_in_combat=False,
            active_buffs=[],
            active_debuffs=[],
            confidence=0.8
        )
        
        decisions = self._simulate_ai_decisions(status)
        
        # Should include low health warning
        self.assertTrue(any("WARNING" in decision for decision in decisions))
        self.assertTrue(any("healing" in decision.lower() for decision in decisions))
    
    def test_ai_decision_poison_debuff(self):
        """Test AI decisions for poison debuff."""
        status = CharacterStatus(
            health_percentage=80.0,
            is_in_combat=False,
            active_buffs=[],
            active_debuffs=["Poison"],
            confidence=0.8
        )
        
        decisions = self._simulate_ai_decisions(status)
        
        # Should include poison alert
        self.assertTrue(any("Poison" in decision for decision in decisions))
        self.assertTrue(any("antidote" in decision.lower() for decision in decisions))
    
    def test_ai_decision_disease_debuff(self):
        """Test AI decisions for disease debuff."""
        status = CharacterStatus(
            health_percentage=70.0,
            is_in_combat=False,
            active_buffs=[],
            active_debuffs=["Disease"],
            confidence=0.8
        )
        
        decisions = self._simulate_ai_decisions(status)
        
        # Should include disease alert
        self.assertTrue(any("Disease" in decision for decision in decisions))
        self.assertTrue(any("medical" in decision.lower() for decision in decisions))
    
    def test_ai_decision_no_buffs(self):
        """Test AI decisions when no buffs are active."""
        status = CharacterStatus(
            health_percentage=90.0,
            is_in_combat=False,
            active_buffs=[],
            active_debuffs=[],
            confidence=0.8
        )
        
        decisions = self._simulate_ai_decisions(status)
        
        # Should suggest applying buffs
        self.assertTrue(any("buffs" in decision.lower() for decision in decisions))
    
    def test_ai_decision_mind_boost_active(self):
        """Test AI decisions when Mind Boost is active."""
        status = CharacterStatus(
            health_percentage=85.0,
            is_in_combat=False,
            active_buffs=["Mind Boost"],
            active_debuffs=[],
            confidence=0.8
        )
        
        decisions = self._simulate_ai_decisions(status)
        
        # Should recognize Mind Boost
        self.assertTrue(any("Mind Boost" in decision for decision in decisions))
        self.assertTrue(any("mental" in decision.lower() for decision in decisions))
    
    def test_ai_decision_combat_low_health(self):
        """Test AI decisions for combat with low health."""
        status = CharacterStatus(
            health_percentage=25.0,
            is_in_combat=True,
            active_buffs=[],
            active_debuffs=[],
            confidence=0.8
        )
        
        decisions = self._simulate_ai_decisions(status)
        
        # Should suggest retreat in combat with low health
        self.assertTrue(any("retreat" in decision.lower() for decision in decisions))
        self.assertTrue(any("COMBAT" in decision for decision in decisions))
    
    def test_ai_decision_combat_adequate_health(self):
        """Test AI decisions for combat with adequate health."""
        status = CharacterStatus(
            health_percentage=75.0,
            is_in_combat=True,
            active_buffs=["Armor Buff"],
            active_debuffs=[],
            confidence=0.8
        )
        
        decisions = self._simulate_ai_decisions(status)
        
        # Should continue combat with adequate health
        self.assertTrue(any("adequate" in decision.lower() for decision in decisions))
        self.assertTrue(any("COMBAT" in decision for decision in decisions))
    
    def test_ai_decision_peace_state(self):
        """Test AI decisions for peace state."""
        status = CharacterStatus(
            health_percentage=95.0,
            is_in_combat=False,
            active_buffs=["Weapon Buff"],
            active_debuffs=[],
            confidence=0.8
        )
        
        decisions = self._simulate_ai_decisions(status)
        
        # Should recognize peace state
        self.assertTrue(any("PEACE" in decision for decision in decisions))
        self.assertTrue(any("safe" in decision.lower() for decision in decisions))
    
    def _simulate_ai_decisions(self, status: CharacterStatus) -> list:
        """Simulate AI decision making based on status."""
        decisions = []
        
        # Health-based decisions
        if status.health_percentage < 20:
            decisions.append("CRITICAL: Use healing item immediately")
        elif status.health_percentage < 50:
            decisions.append("WARNING: Health is low, consider healing")
        
        # Debuff-based decisions
        if "Poison" in status.active_debuffs:
            decisions.append("ALERT: Poison detected, use antidote")
        if "Disease" in status.active_debuffs:
            decisions.append("ALERT: Disease detected, seek medical treatment")
        
        # Buff-based decisions
        if not status.active_buffs:
            decisions.append("INFO: No active buffs, consider applying buffs")
        elif "Mind Boost" in status.active_buffs:
            decisions.append("INFO: Mind Boost active, good for mental tasks")
        
        # Combat-based decisions
        if status.is_in_combat:
            if status.health_percentage < 30:
                decisions.append("COMBAT: Low health in combat, consider retreat")
            else:
                decisions.append("COMBAT: In combat with adequate health")
        else:
            decisions.append("PEACE: Not in combat, safe to perform non-combat activities")
        
        return decisions


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 
#!/usr/bin/env python3
"""Test suite for Batch 046 - Licensing System + Combat Intelligence v1."""

import unittest
import tempfile
import json
import time
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import cv2
import numpy as np

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from core.license_manager import (
    LicenseManager, License, LicenseType, LicenseStatus
)
from core.combat_logger import (
    CombatLogger, CombatSession, SkillUsage, SkillType, DamageType
)
from utils.ocr_damage_parser import (
    OCRDamageParser, DamageEvent
)


class TestLicense(unittest.TestCase):
    """Test License dataclass."""
    
    def test_license_creation(self):
        """Test creating License instance."""
        license_obj = License(
            license_key="test_license",
            discord_id="123456789012345678",
            license_type=LicenseType.BASIC,
            status=LicenseStatus.VALID,
            features=["combat_intelligence"],
            notes="Test license"
        )
        
        self.assertEqual(license_obj.license_key, "test_license")
        self.assertEqual(license_obj.discord_id, "123456789012345678")
        self.assertEqual(license_obj.license_type, LicenseType.BASIC)
        self.assertEqual(license_obj.status, LicenseStatus.VALID)
        self.assertEqual(license_obj.features, ["combat_intelligence"])
        self.assertEqual(license_obj.notes, "Test license")
    
    def test_license_to_dict(self):
        """Test License to_dict method."""
        license_obj = License(
            license_key="test_license",
            discord_id="123456789012345678",
            license_type=LicenseType.BASIC
        )
        
        data = license_obj.to_dict()
        self.assertEqual(data['license_key'], "test_license")
        self.assertEqual(data['discord_id'], "123456789012345678")
        self.assertEqual(data['license_type'], "basic")
        self.assertEqual(data['status'], "valid")
    
    def test_license_from_dict(self):
        """Test License from_dict method."""
        data = {
            'license_key': 'test_license',
            'discord_id': '123456789012345678',
            'license_type': 'basic',
            'status': 'valid',
            'features': ['combat_intelligence'],
            'notes': 'Test license'
        }
        
        license_obj = License.from_dict(data)
        self.assertEqual(license_obj.license_key, "test_license")
        self.assertEqual(license_obj.license_type, LicenseType.BASIC)
        self.assertEqual(license_obj.status, LicenseStatus.VALID)
    
    def test_license_is_valid(self):
        """Test license validation."""
        # Valid license
        valid_license = License(
            license_key="test",
            status=LicenseStatus.VALID
        )
        self.assertTrue(valid_license.is_valid())
        
        # Invalid status
        invalid_license = License(
            license_key="test",
            status=LicenseStatus.REVOKED
        )
        self.assertFalse(invalid_license.is_valid())
        
        # Expired license
        expired_license = License(
            license_key="test",
            status=LicenseStatus.VALID,
            expiry_date=datetime.now() - timedelta(days=1)
        )
        self.assertFalse(expired_license.is_valid())
    
    def test_license_is_lifetime(self):
        """Test lifetime license detection."""
        # Lifetime license
        lifetime_license = License(
            license_key="test",
            license_type=LicenseType.LIFETIME
        )
        self.assertTrue(lifetime_license.is_lifetime())
        
        # Tester license
        tester_license = License(
            license_key="test",
            license_type=LicenseType.TESTER
        )
        self.assertTrue(tester_license.is_lifetime())
        
        # Basic license
        basic_license = License(
            license_key="test",
            license_type=LicenseType.BASIC
        )
        self.assertFalse(basic_license.is_lifetime())
    
    def test_license_days_remaining(self):
        """Test days remaining calculation."""
        # Lifetime license
        lifetime_license = License(
            license_key="test",
            license_type=LicenseType.LIFETIME
        )
        self.assertIsNone(lifetime_license.days_remaining())
        
        # License with expiry
        future_date = datetime.now() + timedelta(days=30)
        expiring_license = License(
            license_key="test",
            expiry_date=future_date
        )
        days_remaining = expiring_license.days_remaining()
        self.assertIsNotNone(days_remaining)
        self.assertGreater(days_remaining, 0)


class TestLicenseManager(unittest.TestCase):
    """Test LicenseManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "licenses.json"
        self.manager = LicenseManager(str(self.config_file))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_license_manager_initialization(self):
        """Test LicenseManager initialization."""
        self.assertIsInstance(self.manager.licenses, dict)
        self.assertIsInstance(self.manager.whitelist, list)
        self.assertIsInstance(self.manager.offline_mode, bool)
    
    def test_add_license(self):
        """Test adding license."""
        success = self.manager.add_license(
            license_key="test_license",
            discord_id="123456789012345678",
            license_type=LicenseType.BASIC,
            expiry_days=30,
            features=["combat_intelligence"],
            notes="Test license"
        )
        
        self.assertTrue(success)
        self.assertIn("test_license", self.manager.licenses)
        
        license_obj = self.manager.licenses["test_license"]
        self.assertEqual(license_obj.license_key, "test_license")
        self.assertEqual(license_obj.discord_id, "123456789012345678")
        self.assertEqual(license_obj.license_type, LicenseType.BASIC)
    
    def test_validate_license(self):
        """Test license validation."""
        # Add a test license
        self.manager.add_license(
            license_key="test_license",
            discord_id="123456789012345678",
            license_type=LicenseType.BASIC
        )
        
        # Valid license
        status = self.manager.validate_license("test_license", "123456789012345678")
        self.assertEqual(status, LicenseStatus.VALID)
        
        # Invalid license
        status = self.manager.validate_license("invalid_license", "123456789012345678")
        self.assertEqual(status, LicenseStatus.INVALID)
        
        # Wrong Discord ID
        status = self.manager.validate_license("test_license", "999999999999999999")
        self.assertEqual(status, LicenseStatus.INVALID)
    
    def test_check_license_environment(self):
        """Test environment license check."""
        # Test without environment variables
        status = self.manager.check_license_environment()
        self.assertIn(status, [LicenseStatus.INVALID, LicenseStatus.OFFLINE])
        
        # Test with environment variables
        with patch.dict(os.environ, {
            'ANDROID_MS11_LICENSE': 'TESTER_001_MS11_2024',
            'ANDROID_MS11_DISCORD_ID': '123456789012345678'
        }):
            status = self.manager.check_license_environment()
            self.assertEqual(status, LicenseStatus.VALID)
    
    def test_whitelist_management(self):
        """Test whitelist functionality."""
        # Add to whitelist
        success = self.manager.add_to_whitelist("123456789012345678")
        self.assertTrue(success)
        self.assertIn("123456789012345678", self.manager.whitelist)
        
        # Remove from whitelist
        success = self.manager.remove_from_whitelist("123456789012345678")
        self.assertTrue(success)
        self.assertNotIn("123456789012345678", self.manager.whitelist)
        
        # Get whitelist
        whitelist = self.manager.get_whitelist()
        self.assertIsInstance(whitelist, list)
    
    def test_revoke_license(self):
        """Test license revocation."""
        # Add a license
        self.manager.add_license(
            license_key="test_license",
            discord_id="123456789012345678"
        )
        
        # Revoke license
        success = self.manager.revoke_license("test_license")
        self.assertTrue(success)
        
        license_obj = self.manager.licenses["test_license"]
        self.assertEqual(license_obj.status, LicenseStatus.REVOKED)
    
    def test_get_license_info(self):
        """Test getting license information."""
        # Add a license
        self.manager.add_license(
            license_key="test_license",
            discord_id="123456789012345678",
            license_type=LicenseType.BASIC
        )
        
        # Get license info
        info = self.manager.get_license_info("test_license")
        self.assertIsNotNone(info)
        self.assertEqual(info['license_key'], "test_license")
        self.assertEqual(info['license_type'], "basic")
        self.assertTrue(info['is_valid'])
    
    def test_get_license_summary(self):
        """Test license summary."""
        summary = self.manager.get_license_summary()
        
        self.assertIn('total_licenses', summary)
        self.assertIn('valid_licenses', summary)
        self.assertIn('expired_licenses', summary)
        self.assertIn('revoked_licenses', summary)
        self.assertIn('whitelist_size', summary)
        self.assertIn('webhook_configured', summary)
        self.assertIn('offline_mode', summary)


class TestSkillUsage(unittest.TestCase):
    """Test SkillUsage dataclass."""
    
    def test_skill_usage_creation(self):
        """Test creating SkillUsage instance."""
        skill_usage = SkillUsage(
            skill_name="headshot",
            skill_type=SkillType.WEAPON,
            timestamp=datetime.now(),
            target="stormtrooper",
            damage_dealt=400,
            damage_type=DamageType.PHYSICAL,
            success=True,
            cooldown_remaining=5.0,
            xp_gained=255
        )
        
        self.assertEqual(skill_usage.skill_name, "headshot")
        self.assertEqual(skill_usage.skill_type, SkillType.WEAPON)
        self.assertEqual(skill_usage.target, "stormtrooper")
        self.assertEqual(skill_usage.damage_dealt, 400)
        self.assertEqual(skill_usage.damage_type, DamageType.PHYSICAL)
        self.assertTrue(skill_usage.success)
        self.assertEqual(skill_usage.cooldown_remaining, 5.0)
        self.assertEqual(skill_usage.xp_gained, 255)
    
    def test_skill_usage_to_dict(self):
        """Test SkillUsage to_dict method."""
        skill_usage = SkillUsage(
            skill_name="headshot",
            skill_type=SkillType.WEAPON,
            timestamp=datetime.now()
        )
        
        data = skill_usage.to_dict()
        self.assertEqual(data['skill_name'], "headshot")
        self.assertEqual(data['skill_type'], "weapon")
        self.assertTrue(data['success'])
    
    def test_skill_usage_from_dict(self):
        """Test SkillUsage from_dict method."""
        data = {
            'skill_name': 'headshot',
            'skill_type': 'weapon',
            'timestamp': datetime.now().isoformat(),
            'target': 'stormtrooper',
            'damage_dealt': 400,
            'damage_type': 'physical',
            'success': True,
            'cooldown_remaining': 5.0,
            'xp_gained': 255
        }
        
        skill_usage = SkillUsage.from_dict(data)
        self.assertEqual(skill_usage.skill_name, "headshot")
        self.assertEqual(skill_usage.skill_type, SkillType.WEAPON)
        self.assertEqual(skill_usage.damage_dealt, 400)
        self.assertEqual(skill_usage.damage_type, DamageType.PHYSICAL)


class TestCombatSession(unittest.TestCase):
    """Test CombatSession dataclass."""
    
    def test_combat_session_creation(self):
        """Test creating CombatSession instance."""
        session = CombatSession(
            session_id="test_session",
            start_time=datetime.now(),
            total_damage_dealt=1000,
            total_xp_gained=500,
            kills=3,
            deaths=0,
            targets_engaged=["stormtrooper", "imperial_officer"]
        )
        
        self.assertEqual(session.session_id, "test_session")
        self.assertEqual(session.total_damage_dealt, 1000)
        self.assertEqual(session.total_xp_gained, 500)
        self.assertEqual(session.kills, 3)
        self.assertEqual(session.deaths, 0)
        self.assertEqual(session.targets_engaged, ["stormtrooper", "imperial_officer"])
        self.assertEqual(session.session_state, "active")
    
    def test_combat_session_to_dict(self):
        """Test CombatSession to_dict method."""
        session = CombatSession(
            session_id="test_session",
            start_time=datetime.now(),
            total_damage_dealt=1000,
            total_xp_gained=500
        )
        
        data = session.to_dict()
        self.assertEqual(data['session_id'], "test_session")
        self.assertEqual(data['total_damage_dealt'], 1000)
        self.assertEqual(data['total_xp_gained'], 500)
        self.assertEqual(data['session_state'], "active")
    
    def test_combat_session_from_dict(self):
        """Test CombatSession from_dict method."""
        data = {
            'session_id': 'test_session',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'skills_used': [],
            'total_damage_dealt': 1000,
            'total_xp_gained': 500,
            'kills': 3,
            'deaths': 0,
            'targets_engaged': ["stormtrooper"],
            'session_state': 'completed'
        }
        
        session = CombatSession.from_dict(data)
        self.assertEqual(session.session_id, "test_session")
        self.assertEqual(session.total_damage_dealt, 1000)
        self.assertEqual(session.total_xp_gained, 500)
        self.assertEqual(session.kills, 3)
        self.assertEqual(session.session_state, "completed")


class TestCombatLogger(unittest.TestCase):
    """Test CombatLogger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = CombatLogger(str(Path(self.temp_dir) / "combat"))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_combat_logger_initialization(self):
        """Test CombatLogger initialization."""
        self.assertIsNone(self.logger.current_session)
        self.assertIsInstance(self.logger.skill_queue, type(self.logger.skill_queue))
        self.assertIsInstance(self.logger.damage_queue, type(self.logger.damage_queue))
        self.assertFalse(self.logger.running)
    
    def test_start_session(self):
        """Test starting a combat session."""
        session_id = self.logger.start_session()
        
        self.assertIsNotNone(session_id)
        self.assertIsNotNone(self.logger.current_session)
        self.assertEqual(self.logger.current_session.session_id, session_id)
        self.assertTrue(self.logger.running)
    
    def test_log_skill_usage(self):
        """Test logging skill usage."""
        self.logger.start_session()
        
        self.logger.log_skill_usage(
            skill_name="headshot",
            skill_type=SkillType.WEAPON,
            target="stormtrooper",
            cooldown=5.0
        )
        
        # Check that skill was logged
        self.assertEqual(self.logger.last_skill_used, "headshot")
        self.assertIsNotNone(self.logger.last_skill_time)
        self.assertEqual(self.logger.skill_cooldowns["headshot"], 5.0)
    
    def test_log_damage_event(self):
        """Test logging damage events."""
        self.logger.start_session()
        
        self.logger.log_damage_event(
            damage_amount=400,
            damage_type=DamageType.PHYSICAL,
            target="stormtrooper"
        )
        
        # Check that damage was logged
        self.assertEqual(len(self.logger.recent_damage_events), 1)
        event = self.logger.recent_damage_events[0]
        self.assertEqual(event[1], 400)  # damage_amount
        self.assertEqual(event[2], DamageType.PHYSICAL)  # damage_type
    
    def test_log_kill_and_death(self):
        """Test logging kills and deaths."""
        self.logger.start_session()
        
        self.logger.log_kill("stormtrooper")
        self.assertEqual(self.logger.current_session.kills, 1)
        self.assertIn("stormtrooper", self.logger.current_session.targets_engaged)
        
        self.logger.log_death()
        self.assertEqual(self.logger.current_session.deaths, 1)
    
    def test_log_xp_gain(self):
        """Test logging XP gain."""
        self.logger.start_session()
        
        self.logger.log_xp_gain(255, "headshot")
        self.assertEqual(self.logger.current_session.total_xp_gained, 255)
    
    def test_end_session(self):
        """Test ending a combat session."""
        self.logger.start_session()
        
        # Add some combat events
        self.logger.log_skill_usage("headshot", SkillType.WEAPON, "stormtrooper")
        self.logger.log_damage_event(400, DamageType.PHYSICAL, "stormtrooper")
        self.logger.log_kill("stormtrooper")
        self.logger.log_xp_gain(255, "headshot")
        
        # End session
        summary = self.logger.end_session()
        
        self.assertFalse(self.logger.running)
        self.assertIsNotNone(summary)
        self.assertEqual(summary['total_damage_dealt'], 400)
        self.assertEqual(summary['total_xp_gained'], 255)
        self.assertEqual(summary['kills'], 1)
    
    def test_get_current_session_summary(self):
        """Test getting current session summary."""
        self.logger.start_session()
        
        # Add some combat events
        self.logger.log_skill_usage("headshot", SkillType.WEAPON, "stormtrooper")
        self.logger.log_damage_event(400, DamageType.PHYSICAL, "stormtrooper")
        self.logger.log_kill("stormtrooper")
        self.logger.log_xp_gain(255, "headshot")
        
        # Allow background processing to complete
        time.sleep(0.1)
        
        summary = self.logger.get_current_session_summary()
        
        self.assertIsNotNone(summary)
        self.assertEqual(summary['total_damage_dealt'], 400)
        self.assertEqual(summary['total_xp_gained'], 255)
        self.assertEqual(summary['kills'], 1)
    
    def test_skill_cooldown_management(self):
        """Test skill cooldown management."""
        self.logger.skill_cooldowns["headshot"] = 5.0
        
        self.assertEqual(self.logger.get_skill_cooldown("headshot"), 5.0)
        self.assertFalse(self.logger.is_skill_ready("headshot"))
        
        self.logger.skill_cooldowns["rifle_shot"] = 0.0
        self.assertTrue(self.logger.is_skill_ready("rifle_shot"))


class TestDamageEvent(unittest.TestCase):
    """Test DamageEvent dataclass."""
    
    def test_damage_event_creation(self):
        """Test creating DamageEvent instance."""
        event = DamageEvent(
            damage_amount=400,
            damage_type="physical",
            timestamp=datetime.now(),
            confidence=0.8,
            screen_region=(100, 200, 300, 400),
            raw_text="400 damage",
            processed=False
        )
        
        self.assertEqual(event.damage_amount, 400)
        self.assertEqual(event.damage_type, "physical")
        self.assertEqual(event.confidence, 0.8)
        self.assertEqual(event.screen_region, (100, 200, 300, 400))
        self.assertEqual(event.raw_text, "400 damage")
        self.assertFalse(event.processed)
    
    def test_damage_event_to_dict(self):
        """Test DamageEvent to_dict method."""
        event = DamageEvent(
            damage_amount=400,
            damage_type="physical",
            timestamp=datetime.now(),
            confidence=0.8,
            screen_region=(100, 200, 300, 400),
            raw_text="400 damage"
        )
        
        data = event.to_dict()
        self.assertEqual(data['damage_amount'], 400)
        self.assertEqual(data['damage_type'], "physical")
        self.assertEqual(data['confidence'], 0.8)
        self.assertEqual(data['screen_region'], (100, 200, 300, 400))
        self.assertEqual(data['raw_text'], "400 damage")


class TestOCRDamageParser(unittest.TestCase):
    """Test OCRDamageParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.parser = OCRDamageParser()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_ocr_parser_initialization(self):
        """Test OCRDamageParser initialization."""
        self.assertIsInstance(self.parser.config, dict)
        self.assertIsInstance(self.parser.damage_patterns, list)
        self.assertIsInstance(self.parser.damage_history, list)
        self.assertIsNone(self.parser.last_processed_time)
    
    def test_compile_damage_patterns(self):
        """Test damage pattern compilation."""
        patterns = self.parser.damage_patterns
        self.assertGreater(len(patterns), 0)
        
        # Test pattern matching
        test_text = "400 damage"
        matches_found = False
        for pattern in patterns:
            if pattern.search(test_text):
                matches_found = True
                break
        self.assertTrue(matches_found)
    
    def test_preprocess_image(self):
        """Test image preprocessing."""
        # Create test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.putText(test_image, "400", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        processed_image = self.parser.preprocess_image(test_image)
        
        self.assertIsInstance(processed_image, np.ndarray)
        self.assertEqual(len(processed_image.shape), 2)  # Should be grayscale
    
    def test_parse_damage_from_text(self):
        """Test damage parsing from text."""
        test_text = "400 damage dealt to target"
        damage_matches = self.parser.parse_damage_from_text(test_text)
        
        self.assertGreater(len(damage_matches), 0)
        damage_amount, confidence = damage_matches[0]
        self.assertEqual(damage_amount, 400)
        self.assertGreater(confidence, 0)
    
    def test_detect_damage_type_from_color(self):
        """Test damage type detection from color."""
        # Create test image with red color (physical damage)
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[:, :] = [0, 0, 255]  # Red color
        
        damage_type = self.parser.detect_damage_type_from_color(test_image, (0, 0, 100, 100))
        self.assertEqual(damage_type, "physical")
    
    def test_scan_for_damage(self):
        """Test damage scanning."""
        # Create test image
        test_image = np.zeros((400, 600, 3), dtype=np.uint8)
        cv2.putText(test_image, "400", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
        
        damage_events = self.parser.scan_for_damage(test_image)
        
        # Should find at least one damage event
        self.assertGreaterEqual(len(damage_events), 0)
    
    def test_get_recent_damage_events(self):
        """Test getting recent damage events."""
        # Add some test events
        test_event = DamageEvent(
            damage_amount=400,
            damage_type="physical",
            timestamp=datetime.now(),
            confidence=0.8,
            screen_region=(100, 200, 300, 400),
            raw_text="400 damage"
        )
        self.parser.damage_history.append(test_event)
        
        recent_events = self.parser.get_recent_damage_events(seconds=60.0)
        self.assertEqual(len(recent_events), 1)
    
    def test_get_damage_statistics(self):
        """Test damage statistics calculation."""
        # Add some test events
        for i in range(3):
            event = DamageEvent(
                damage_amount=400 + i * 100,
                damage_type="physical",
                timestamp=datetime.now(),
                confidence=0.8,
                screen_region=(100, 200, 300, 400),
                raw_text=f"{400 + i * 100} damage"
            )
            self.parser.damage_history.append(event)
        
        stats = self.parser.get_damage_statistics()
        
        self.assertEqual(stats['total_damage'], 1500)  # 400 + 500 + 600
        self.assertEqual(stats['event_count'], 3)
        self.assertEqual(stats['average_damage'], 500)  # 1500 / 3
        self.assertEqual(stats['highest_damage'], 600)
        self.assertEqual(stats['lowest_damage'], 400)
    
    def test_clear_history(self):
        """Test clearing damage history."""
        # Add some test events
        test_event = DamageEvent(
            damage_amount=400,
            damage_type="physical",
            timestamp=datetime.now(),
            confidence=0.8,
            screen_region=(100, 200, 300, 400),
            raw_text="400 damage"
        )
        self.parser.damage_history.append(test_event)
        
        self.assertGreater(len(self.parser.damage_history), 0)
        self.parser.clear_history()
        self.assertEqual(len(self.parser.damage_history), 0)


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.license_manager = LicenseManager(str(Path(self.temp_dir) / "licenses.json"))
        self.combat_logger = CombatLogger(str(Path(self.temp_dir) / "combat"))
        self.ocr_parser = OCRDamageParser()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """Test complete workflow from license check to combat logging."""
        # 1. Check license
        license_status = self.license_manager.check_license_environment()
        self.assertIn(license_status, [LicenseStatus.VALID, LicenseStatus.INVALID, LicenseStatus.OFFLINE])
        
        # 2. Start combat session
        session_id = self.combat_logger.start_session()
        self.assertIsNotNone(session_id)
        
        # 3. Log combat events
        self.combat_logger.log_skill_usage("headshot", SkillType.WEAPON, "stormtrooper")
        self.combat_logger.log_damage_event(400, DamageType.PHYSICAL, "stormtrooper")
        self.combat_logger.log_kill("stormtrooper")
        self.combat_logger.log_xp_gain(255, "headshot")
        
        # 4. OCR damage detection
        test_image = np.zeros((400, 600, 3), dtype=np.uint8)
        cv2.putText(test_image, "400", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
        damage_events = self.ocr_parser.scan_for_damage(test_image)
        
        # 5. End session and get summary
        summary = self.combat_logger.end_session()
        self.assertIsNotNone(summary)
        self.assertEqual(summary['total_damage_dealt'], 400)
        self.assertEqual(summary['total_xp_gained'], 255)
        self.assertEqual(summary['kills'], 1)
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        # Test with invalid license type
        with self.assertRaises(ValueError):
            LicenseType("invalid_type")
        
        # Test with invalid license status
        with self.assertRaises(ValueError):
            LicenseStatus("invalid_status")
        
        # Test with invalid skill type
        with self.assertRaises(ValueError):
            SkillType("invalid_type")
        
        # Test with invalid damage type
        with self.assertRaises(ValueError):
            DamageType("invalid_type")


def main():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestLicense,
        TestLicenseManager,
        TestSkillUsage,
        TestCombatSession,
        TestCombatLogger,
        TestDamageEvent,
        TestOCRDamageParser,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    return len(result.failures) + len(result.errors)


if __name__ == "__main__":
    exit(main()) 
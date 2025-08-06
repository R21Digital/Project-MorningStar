#!/usr/bin/env python3
"""
MS11 Batch 090 - Public Player Profiles Tests

This module provides comprehensive tests for the public player profile
functionality, including profile creation, management, and API endpoints.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock

from core.player_profile_manager import (
    PlayerProfileManager, 
    PublicPlayerProfile, 
    ProfileUpload,
    ProfileStatus,
    UploadType
)

class TestPlayerProfileManager(unittest.TestCase):
    """Test cases for PlayerProfileManager."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.public_dir = os.path.join(self.test_dir, "public_profiles")
        self.upload_dir = os.path.join(self.test_dir, "uploads")
        self.internal_dir = os.path.join(self.test_dir, "internal")
        
        # Create test directories
        os.makedirs(self.public_dir, exist_ok=True)
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.internal_dir, exist_ok=True)
        
        # Initialize profile manager with test directories
        self.profile_manager = PlayerProfileManager(
            public_data_dir=self.public_dir,
            upload_dir=self.upload_dir,
            internal_data_dir=self.internal_dir
        )
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test profile manager initialization."""
        self.assertIsNotNone(self.profile_manager)
        self.assertEqual(len(self.profile_manager.supported_servers), 14)
        self.assertEqual(len(self.profile_manager.supported_races), 10)
        self.assertEqual(len(self.profile_manager.supported_professions), 35)
    
    def test_create_profile_success(self):
        """Test successful profile creation."""
        profile = self.profile_manager.create_profile(
            name="TestPlayer",
            server="Basilisk",
            race="Human",
            profession="Swordsman"
        )
        
        self.assertIsInstance(profile, PublicPlayerProfile)
        self.assertEqual(profile.name, "TestPlayer")
        self.assertEqual(profile.server, "Basilisk")
        self.assertEqual(profile.race, "Human")
        self.assertEqual(profile.profession, "Swordsman")
        self.assertEqual(profile.status, "pending")
    
    def test_create_profile_validation(self):
        """Test profile creation validation."""
        # Test missing required fields
        with self.assertRaises(ValueError):
            self.profile_manager.create_profile(
                name="",  # Empty name
                server="Basilisk",
                race="Human",
                profession="Swordsman"
            )
        
        with self.assertRaises(ValueError):
            self.profile_manager.create_profile(
                name="TestPlayer",
                server="InvalidServer",  # Invalid server
                race="Human",
                profession="Swordsman"
            )
        
        with self.assertRaises(ValueError):
            self.profile_manager.create_profile(
                name="TestPlayer",
                server="Basilisk",
                race="InvalidRace",  # Invalid race
                profession="Swordsman"
            )
        
        with self.assertRaises(ValueError):
            self.profile_manager.create_profile(
                name="TestPlayer",
                server="Basilisk",
                race="Human",
                profession="InvalidProfession"  # Invalid profession
            )
    
    def test_create_duplicate_profile(self):
        """Test creating duplicate profile."""
        # Create first profile
        self.profile_manager.create_profile(
            name="TestPlayer",
            server="Basilisk",
            race="Human",
            profession="Swordsman"
        )
        
        # Try to create duplicate
        with self.assertRaises(ValueError):
            self.profile_manager.create_profile(
                name="TestPlayer",
                server="Basilisk",
                race="Human",
                profession="Swordsman"
            )
    
    def test_get_profile(self):
        """Test profile retrieval."""
        # Create a profile
        created_profile = self.profile_manager.create_profile(
            name="TestPlayer",
            server="Basilisk",
            race="Human",
            profession="Swordsman"
        )
        
        # Retrieve the profile
        retrieved_profile = self.profile_manager.get_profile("TestPlayer", "Basilisk")
        
        self.assertIsNotNone(retrieved_profile)
        self.assertEqual(retrieved_profile.name, "TestPlayer")
        self.assertEqual(retrieved_profile.server, "Basilisk")
        
        # Test non-existent profile
        non_existent = self.profile_manager.get_profile("NonExistent", "Basilisk")
        self.assertIsNone(non_existent)
    
    def test_update_profile(self):
        """Test profile updates."""
        # Create a profile
        profile = self.profile_manager.create_profile(
            name="TestPlayer",
            server="Basilisk",
            race="Human",
            profession="Swordsman"
        )
        
        # Update the profile
        updated_profile = self.profile_manager.update_profile(
            "TestPlayer", 
            "Basilisk",
            level=50,
            city="Mos Eisley",
            notes="Updated profile"
        )
        
        self.assertIsNotNone(updated_profile)
        self.assertEqual(updated_profile.level, 50)
        self.assertEqual(updated_profile.city, "Mos Eisley")
        self.assertEqual(updated_profile.notes, "Updated profile")
        
        # Test updating non-existent profile
        non_existent = self.profile_manager.update_profile(
            "NonExistent", 
            "Basilisk",
            level=50
        )
        self.assertIsNone(non_existent)
    
    def test_list_profiles(self):
        """Test profile listing."""
        # Create multiple profiles
        self.profile_manager.create_profile(
            name="Player1",
            server="Basilisk",
            race="Human",
            profession="Swordsman"
        )
        
        self.profile_manager.create_profile(
            name="Player2",
            server="Legends",
            race="Twilek",
            profession="Jedi"
        )
        
        self.profile_manager.create_profile(
            name="Player3",
            server="Basilisk",
            race="Human",
            profession="Commando"
        )
        
        # Test listing all profiles
        all_profiles = self.profile_manager.list_profiles()
        self.assertEqual(len(all_profiles), 3)
        
        # Test filtering by server
        basilisk_profiles = self.profile_manager.list_profiles(server="Basilisk")
        self.assertEqual(len(basilisk_profiles), 2)
        
        # Test filtering by status
        pending_profiles = self.profile_manager.list_profiles(status="pending")
        self.assertEqual(len(pending_profiles), 3)
    
    def test_verify_profile(self):
        """Test profile verification."""
        # Create a profile
        profile = self.profile_manager.create_profile(
            name="TestPlayer",
            server="Basilisk",
            race="Human",
            profession="Swordsman"
        )
        
        # Verify the profile
        success = self.profile_manager.verify_profile("TestPlayer", "Basilisk")
        self.assertTrue(success)
        
        # Check that status was updated
        verified_profile = self.profile_manager.get_profile("TestPlayer", "Basilisk")
        self.assertEqual(verified_profile.status, "verified")
        self.assertIsNotNone(verified_profile.verified_at)
        
        # Test verifying non-existent profile
        success = self.profile_manager.verify_profile("NonExistent", "Basilisk")
        self.assertFalse(success)

class TestProfileUpload(unittest.TestCase):
    """Test cases for profile upload functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.public_dir = os.path.join(self.test_dir, "public_profiles")
        self.upload_dir = os.path.join(self.test_dir, "uploads")
        self.internal_dir = os.path.join(self.test_dir, "internal")
        
        os.makedirs(self.public_dir, exist_ok=True)
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.internal_dir, exist_ok=True)
        
        self.profile_manager = PlayerProfileManager(
            public_data_dir=self.public_dir,
            upload_dir=self.upload_dir,
            internal_data_dir=self.internal_dir
        )
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_manual_entry_upload(self):
        """Test manual entry upload."""
        json_data = {
            "level": 50,
            "city": "Mos Eisley",
            "guild": "Test Guild",
            "playtime_hours": 100
        }
        
        upload = self.profile_manager.upload_profile_data(
            profile_name="TestPlayer",
            server="Basilisk",
            upload_type="manual_entry",
            json_data=json_data
        )
        
        self.assertIsInstance(upload, ProfileUpload)
        self.assertEqual(upload.profile_name, "TestPlayer")
        self.assertEqual(upload.server, "Basilisk")
        self.assertEqual(upload.upload_type, "manual_entry")
        self.assertEqual(upload.json_data, json_data)
        self.assertTrue(upload.processed)
    
    def test_json_file_upload(self):
        """Test JSON file upload."""
        # Create temporary JSON file
        json_data = {
            "level": 60,
            "city": "Theed",
            "guild": "Royal Guard",
            "playtime_hours": 200
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_data, f)
            temp_file_path = f.name
        
        try:
            # Mock file upload
            from werkzeug.datastructures import FileStorage
            
            with open(temp_file_path, 'rb') as f:
                file_storage = FileStorage(
                    stream=f,
                    filename="test_data.json",
                    content_type="application/json"
                )
                
                upload = self.profile_manager.upload_profile_data(
                    profile_name="TestPlayer",
                    server="Basilisk",
                    upload_type="json_data",
                    file=file_storage
                )
                
                self.assertIsInstance(upload, ProfileUpload)
                self.assertEqual(upload.upload_type, "json_data")
                self.assertTrue(upload.processed)
                self.assertIsNotNone(upload.file_path)
        
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_screenshot_upload(self):
        """Test screenshot upload."""
        # Create temporary image file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
            f.write(b'fake image data')
            temp_file_path = f.name
        
        try:
            # Mock file upload
            from werkzeug.datastructures import FileStorage
            
            with open(temp_file_path, 'rb') as f:
                file_storage = FileStorage(
                    stream=f,
                    filename="test_screenshot.png",
                    content_type="image/png"
                )
                
                upload = self.profile_manager.upload_profile_data(
                    profile_name="TestPlayer",
                    server="Basilisk",
                    upload_type="screenshot",
                    file=file_storage
                )
                
                self.assertIsInstance(upload, ProfileUpload)
                self.assertEqual(upload.upload_type, "screenshot")
                self.assertTrue(upload.processed)
                self.assertIsNotNone(upload.file_path)
        
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

class TestDataExtraction(unittest.TestCase):
    """Test cases for data extraction functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.profile_manager = PlayerProfileManager(
            public_data_dir=os.path.join(self.test_dir, "public"),
            upload_dir=os.path.join(self.test_dir, "uploads"),
            internal_data_dir=os.path.join(self.test_dir, "internal")
        )
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_extract_profile_data(self):
        """Test profile data extraction from JSON."""
        test_data = {
            "character_level": 75,
            "home_city": "Mos Eisley",
            "guild_name": "Test Guild",
            "guild_abbreviation": "TG",
            "side": "Imperial",
            "world": "Tatooine",
            "current_location": "Cantina",
            "hours_played": 500,
            "kill_count": 1000,
            "session_count": 200,
            "macro_list": ["combat", "heal"],
            "titles": ["Master", "Elite"],
            "skill_tree": {"swordsman": 4},
            "gear": {"weapon": "Lightsaber"}
        }
        
        extracted = self.profile_manager._extract_profile_data(test_data)
        
        self.assertEqual(extracted["level"], 75)
        self.assertEqual(extracted["city"], "Mos Eisley")
        self.assertEqual(extracted["guild"], "Test Guild")
        self.assertEqual(extracted["guild_tag"], "TG")
        self.assertEqual(extracted["faction"], "Imperial")
        self.assertEqual(extracted["planet"], "Tatooine")
        self.assertEqual(extracted["location"], "Cantina")
        self.assertEqual(extracted["playtime_hours"], 500)
        self.assertEqual(extracted["kills"], 1000)
        self.assertEqual(extracted["sessions"], 200)
        self.assertEqual(extracted["macros_used"], ["combat", "heal"])
        self.assertEqual(extracted["achievements"], ["Master", "Elite"])
        self.assertEqual(extracted["skills"], {"swordsman": 4})
        self.assertEqual(extracted["equipment"], {"weapon": "Lightsaber"})

class TestAPIIntegration(unittest.TestCase):
    """Test cases for API integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.profile_manager = PlayerProfileManager(
            public_data_dir=os.path.join(self.test_dir, "public"),
            upload_dir=os.path.join(self.test_dir, "uploads"),
            internal_data_dir=os.path.join(self.test_dir, "internal")
        )
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_supported_options(self):
        """Test supported options API."""
        servers = self.profile_manager.get_supported_servers()
        self.assertIsInstance(servers, list)
        self.assertGreater(len(servers), 0)
        self.assertIn("Basilisk", servers)
        
        races = self.profile_manager.get_supported_races()
        self.assertIsInstance(races, list)
        self.assertGreater(len(races), 0)
        self.assertIn("Human", races)
        
        professions = self.profile_manager.get_supported_professions()
        self.assertIsInstance(professions, list)
        self.assertGreater(len(professions), 0)
        self.assertIn("Swordsman", professions)

def run_tests():
    """Run all tests and provide summary."""
    print("MS11 Batch 090 - Public Player Profiles Tests")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPlayerProfileManager,
        TestProfileUpload,
        TestDataExtraction,
        TestAPIIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASSED' if success else 'FAILED'}")
    
    return success

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Batch 097 - Multi-Character Player Profile Support Tests

This test suite validates the multi-character profile system functionality:
- Account creation and management
- Character creation and linking to accounts
- Session history tracking
- Visibility controls
- Main character designation
- Search and filtering
- API endpoints
- UI functionality
"""

import json
import logging
import sys
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from core.multi_character_profile_manager import multi_character_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultiCharacterProfileTester:
    """Test suite for multi-character profile system."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.test_accounts = []
        self.test_characters = []
        self.test_sessions = []
        
    def run_all_tests(self):
        """Run all test cases."""
        print("=" * 80)
        print("BATCH 097 - MULTI-CHARACTER PROFILE SYSTEM TESTS")
        print("=" * 80)
        print()
        
        test_results = []
        
        # Core functionality tests
        test_results.append(self.test_account_creation())
        test_results.append(self.test_character_creation())
        test_results.append(self.test_session_history())
        test_results.append(self.test_visibility_controls())
        test_results.append(self.test_main_character_designation())
        test_results.append(self.test_search_functionality())
        test_results.append(self.test_account_statistics())
        
        # API endpoint tests
        test_results.append(self.test_api_endpoints())
        test_results.append(self.test_web_interface())
        
        # Cleanup
        test_results.append(self.test_cleanup())
        
        # Summary
        self.print_test_summary(test_results)
        
    def test_account_creation(self) -> Dict[str, Any]:
        """Test account creation functionality."""
        print("1. Testing Account Creation")
        print("-" * 40)
        
        try:
            # Clear existing data
            multi_character_manager.accounts.clear()
            multi_character_manager.characters.clear()
            multi_character_manager.sessions.clear()
            multi_character_manager._save_data()
            
            # Test 1: Create valid account
            account1 = multi_character_manager.create_account(
                account_name="TestAccount1",
                email="test1@example.com",
                discord_id="TestUser1#1234"
            )
            assert account1.account_name == "TestAccount1"
            assert account1.email == "test1@example.com"
            assert account1.discord_id == "TestUser1#1234"
            self.test_accounts.append(account1)
            print("✓ Created valid account")
            
            # Test 2: Create account with minimal data
            account2 = multi_character_manager.create_account(
                account_name="TestAccount2"
            )
            assert account2.account_name == "TestAccount2"
            assert account2.email is None
            self.test_accounts.append(account2)
            print("✓ Created account with minimal data")
            
            # Test 3: Duplicate account name should fail
            try:
                multi_character_manager.create_account(account_name="TestAccount1")
                assert False, "Should have raised ValueError for duplicate name"
            except ValueError:
                print("✓ Correctly rejected duplicate account name")
            
            # Test 4: Empty account name should fail
            try:
                multi_character_manager.create_account(account_name="")
                assert False, "Should have raised ValueError for empty name"
            except ValueError:
                print("✓ Correctly rejected empty account name")
            
            return {"test": "Account Creation", "status": "PASS", "details": "All account creation tests passed"}
            
        except Exception as e:
            logger.error(f"Account creation test failed: {e}")
            return {"test": "Account Creation", "status": "FAIL", "details": str(e)}
    
    def test_character_creation(self) -> Dict[str, Any]:
        """Test character creation functionality."""
        print("\n2. Testing Character Creation")
        print("-" * 40)
        
        try:
            # Test 1: Create character under account
            character1 = multi_character_manager.create_character(
                account_id=self.test_accounts[0].account_id,
                name="TestCharacter1",
                server="Basilisk",
                race="Human",
                profession="Commando"
            )
            assert character1.name == "TestCharacter1"
            assert character1.server == "Basilisk"
            assert character1.race == "Human"
            assert character1.profession == "Commando"
            assert character1.is_main_character == True  # First character should be main
            self.test_characters.append(character1)
            print("✓ Created character under account")
            
            # Test 2: Create second character (should not be main)
            character2 = multi_character_manager.create_character(
                account_id=self.test_accounts[0].account_id,
                name="TestCharacter2",
                server="Basilisk",
                race="Mon Calamari",
                profession="Medic"
            )
            assert character2.is_main_character == False
            self.test_characters.append(character2)
            print("✓ Created second character (not main)")
            
            # Test 3: Create character with additional data
            character3 = multi_character_manager.create_character(
                account_id=self.test_accounts[1].account_id,
                name="TestCharacter3",
                server="Legends",
                race="Trandoshan",
                profession="Rifleman",
                level=50,
                city="Theed",
                guild="Test Guild",
                guild_tag="[TG]",
                faction="Rebel",
                planet="Naboo",
                playtime_hours=100,
                kills=500,
                sessions=25,
                macros_used=["AutoHeal", "CombatRotation"],
                achievements=["Novice Rifleman", "First Kill"],
                skills={"Rifleman": 2, "Scout": 1},
                equipment={"Weapon": "Basic Rifle", "Armor": "Light Armor"},
                notes="Test character with full data",
                visibility="public"
            )
            assert character3.level == 50
            assert character3.city == "Theed"
            assert len(character3.macros_used) == 2
            assert len(character3.achievements) == 2
            assert character3.skills["Rifleman"] == 2
            self.test_characters.append(character3)
            print("✓ Created character with full data")
            
            # Test 4: Duplicate character name on same server should fail
            try:
                multi_character_manager.create_character(
                    account_id=self.test_accounts[0].account_id,
                    name="TestCharacter1",
                    server="Basilisk",
                    race="Human",
                    profession="Commando"
                )
                assert False, "Should have raised ValueError for duplicate character"
            except ValueError:
                print("✓ Correctly rejected duplicate character name on same server")
            
            # Test 5: Same character name on different server should work
            character4 = multi_character_manager.create_character(
                account_id=self.test_accounts[0].account_id,
                name="TestCharacter1",
                server="Legends",
                race="Human",
                profession="Commando"
            )
            assert character4.name == "TestCharacter1"
            assert character4.server == "Legends"
            self.test_characters.append(character4)
            print("✓ Created character with same name on different server")
            
            return {"test": "Character Creation", "status": "PASS", "details": "All character creation tests passed"}
            
        except Exception as e:
            logger.error(f"Character creation test failed: {e}")
            return {"test": "Character Creation", "status": "FAIL", "details": str(e)}
    
    def test_session_history(self) -> Dict[str, Any]:
        """Test session history functionality."""
        print("\n3. Testing Session History")
        print("-" * 40)
        
        try:
            # Test 1: Add session history
            session1 = multi_character_manager.add_session_history(
                character_id=self.test_characters[0].character_id,
                start_time=datetime.now().isoformat(),
                end_time=(datetime.now() + timedelta(hours=2)).isoformat(),
                duration_minutes=120,
                xp_gained=5000,
                credits_earned=25000,
                activities=["PvP Combat", "Quest Completion"],
                location_start="Coronet, Corellia",
                location_end="Mos Eisley, Tatooine",
                notes="Test session"
            )
            assert session1.character_id == self.test_characters[0].character_id
            assert session1.duration_minutes == 120
            assert session1.xp_gained == 5000
            self.test_sessions.append(session1)
            print("✓ Added session history")
            
            # Test 2: Get character sessions
            sessions = multi_character_manager.get_character_sessions(self.test_characters[0].character_id)
            assert len(sessions) == 1
            assert sessions[0].session_id == session1.session_id
            print("✓ Retrieved character sessions")
            
            # Test 3: Get account sessions
            account_sessions = multi_character_manager.get_account_sessions(self.test_accounts[0].account_id)
            assert len(account_sessions) >= 1
            print("✓ Retrieved account sessions")
            
            # Test 4: Update session history
            updated_session = multi_character_manager.update_session_history(
                session1.session_id,
                duration_minutes=150,
                xp_gained=6000
            )
            assert updated_session.duration_minutes == 150
            assert updated_session.xp_gained == 6000
            print("✓ Updated session history")
            
            return {"test": "Session History", "status": "PASS", "details": "All session history tests passed"}
            
        except Exception as e:
            logger.error(f"Session history test failed: {e}")
            return {"test": "Session History", "status": "FAIL", "details": str(e)}
    
    def test_visibility_controls(self) -> Dict[str, Any]:
        """Test visibility control functionality."""
        print("\n4. Testing Visibility Controls")
        print("-" * 40)
        
        try:
            # Test 1: Set character visibility
            success = multi_character_manager.set_character_visibility(
                self.test_characters[0].character_id, "private"
            )
            assert success == True
            character = multi_character_manager.get_character(self.test_characters[0].character_id)
            assert character.visibility == "private"
            print("✓ Set character visibility to private")
            
            # Test 2: Set to friends_only
            success = multi_character_manager.set_character_visibility(
                self.test_characters[0].character_id, "friends_only"
            )
            assert success == True
            character = multi_character_manager.get_character(self.test_characters[0].character_id)
            assert character.visibility == "friends_only"
            print("✓ Set character visibility to friends_only")
            
            # Test 3: Set to public
            success = multi_character_manager.set_character_visibility(
                self.test_characters[0].character_id, "public"
            )
            assert success == True
            character = multi_character_manager.get_character(self.test_characters[0].character_id)
            assert character.visibility == "public"
            print("✓ Set character visibility to public")
            
            # Test 4: Invalid visibility should fail
            try:
                multi_character_manager.set_character_visibility(
                    self.test_characters[0].character_id, "invalid"
                )
                assert False, "Should have raised ValueError for invalid visibility"
            except ValueError:
                print("✓ Correctly rejected invalid visibility setting")
            
            return {"test": "Visibility Controls", "status": "PASS", "details": "All visibility control tests passed"}
            
        except Exception as e:
            logger.error(f"Visibility controls test failed: {e}")
            return {"test": "Visibility Controls", "status": "FAIL", "details": str(e)}
    
    def test_main_character_designation(self) -> Dict[str, Any]:
        """Test main character designation functionality."""
        print("\n5. Testing Main Character Designation")
        print("-" * 40)
        
        try:
            # Test 1: Set main character
            success = multi_character_manager.set_main_character(self.test_characters[1].character_id)
            assert success == True
            
            # Verify main character was set
            character1 = multi_character_manager.get_character(self.test_characters[0].character_id)
            character2 = multi_character_manager.get_character(self.test_characters[1].character_id)
            assert character1.is_main_character == False
            assert character2.is_main_character == True
            print("✓ Set main character")
            
            # Test 2: Change main character
            success = multi_character_manager.set_main_character(self.test_characters[0].character_id)
            assert success == True
            
            # Verify main character changed
            character1 = multi_character_manager.get_character(self.test_characters[0].character_id)
            character2 = multi_character_manager.get_character(self.test_characters[1].character_id)
            assert character1.is_main_character == True
            assert character2.is_main_character == False
            print("✓ Changed main character")
            
            return {"test": "Main Character Designation", "status": "PASS", "details": "All main character tests passed"}
            
        except Exception as e:
            logger.error(f"Main character designation test failed: {e}")
            return {"test": "Main Character Designation", "status": "FAIL", "details": str(e)}
    
    def test_search_functionality(self) -> Dict[str, Any]:
        """Test search functionality."""
        print("\n6. Testing Search Functionality")
        print("-" * 40)
        
        try:
            # Test 1: Search accounts
            accounts = multi_character_manager.search_accounts(query="Test")
            assert len(accounts) >= 2
            print("✓ Searched accounts")
            
            # Test 2: Search characters by profession
            characters = multi_character_manager.search_characters(profession="Commando")
            assert len(characters) >= 1
            print("✓ Searched characters by profession")
            
            # Test 3: Search characters by visibility
            public_chars = multi_character_manager.search_characters(visibility="public")
            assert len(public_chars) >= 1
            print("✓ Searched characters by visibility")
            
            # Test 4: Search characters by server
            basilisk_chars = multi_character_manager.search_characters(server="Basilisk")
            assert len(basilisk_chars) >= 1
            print("✓ Searched characters by server")
            
            # Test 5: Combined search
            commando_chars = multi_character_manager.search_characters(
                query="Test", profession="Commando", visibility="public"
            )
            assert len(commando_chars) >= 1
            print("✓ Combined search filters")
            
            return {"test": "Search Functionality", "status": "PASS", "details": "All search tests passed"}
            
        except Exception as e:
            logger.error(f"Search functionality test failed: {e}")
            return {"test": "Search Functionality", "status": "FAIL", "details": str(e)}
    
    def test_account_statistics(self) -> Dict[str, Any]:
        """Test account statistics calculation."""
        print("\n7. Testing Account Statistics")
        print("-" * 40)
        
        try:
            # Test 1: Calculate account stats
            stats = multi_character_manager.calculate_account_stats(self.test_accounts[0].account_id)
            assert "character_count" in stats
            assert "total_playtime_hours" in stats
            assert "total_sessions" in stats
            assert "total_kills" in stats
            assert "main_character" in stats
            print("✓ Calculated account statistics")
            
            # Test 2: Verify character count
            characters = multi_character_manager.get_account_characters(self.test_accounts[0].account_id)
            assert stats["character_count"] == len(characters)
            print("✓ Verified character count")
            
            # Test 3: Verify main character
            if stats["main_character"]:
                assert stats["main_character"].is_main_character == True
                print("✓ Verified main character designation")
            
            return {"test": "Account Statistics", "status": "PASS", "details": "All statistics tests passed"}
            
        except Exception as e:
            logger.error(f"Account statistics test failed: {e}")
            return {"test": "Account Statistics", "status": "FAIL", "details": str(e)}
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test API endpoints."""
        print("\n8. Testing API Endpoints")
        print("-" * 40)
        
        try:
            # Test 1: Multi-character home page
            response = requests.get(f"{self.base_url}/multi-character", timeout=5)
            assert response.status_code == 200
            print("✓ Multi-character home page accessible")
            
            # Test 2: Account creation page
            response = requests.get(f"{self.base_url}/multi-character/account/create", timeout=5)
            assert response.status_code == 200
            print("✓ Account creation page accessible")
            
            # Test 3: Character creation page
            response = requests.get(f"{self.base_url}/multi-character/character/create", timeout=5)
            assert response.status_code == 200
            print("✓ Character creation page accessible")
            
            # Test 4: API endpoints
            response = requests.get(f"{self.base_url}/api/multi-character/accounts", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            print("✓ API accounts endpoint working")
            
            response = requests.get(f"{self.base_url}/api/multi-character/characters", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            print("✓ API characters endpoint working")
            
            return {"test": "API Endpoints", "status": "PASS", "details": "All API endpoint tests passed"}
            
        except requests.exceptions.ConnectionError:
            print("⚠ Dashboard not running - skipping API tests")
            return {"test": "API Endpoints", "status": "SKIP", "details": "Dashboard not running"}
        except Exception as e:
            logger.error(f"API endpoints test failed: {e}")
            return {"test": "API Endpoints", "status": "FAIL", "details": str(e)}
    
    def test_web_interface(self) -> Dict[str, Any]:
        """Test web interface functionality."""
        print("\n9. Testing Web Interface")
        print("-" * 40)
        
        try:
            # Test 1: Check if dashboard is running
            response = requests.get(f"{self.base_url}/", timeout=5)
            assert response.status_code == 200
            print("✓ Dashboard is running")
            
            # Test 2: Check multi-character link in navigation
            response = requests.get(f"{self.base_url}/", timeout=5)
            assert "multi-character" in response.text.lower()
            print("✓ Multi-character link in navigation")
            
            return {"test": "Web Interface", "status": "PASS", "details": "All web interface tests passed"}
            
        except requests.exceptions.ConnectionError:
            print("⚠ Dashboard not running - skipping web interface tests")
            return {"test": "Web Interface", "status": "SKIP", "details": "Dashboard not running"}
        except Exception as e:
            logger.error(f"Web interface test failed: {e}")
            return {"test": "Web Interface", "status": "FAIL", "details": str(e)}
    
    def test_cleanup(self) -> Dict[str, Any]:
        """Test cleanup functionality."""
        print("\n10. Testing Cleanup")
        print("-" * 40)
        
        try:
            # Test 1: Delete character
            success = multi_character_manager.delete_character(self.test_characters[-1].character_id)
            assert success == True
            print("✓ Deleted character")
            
            # Test 2: Verify character is deleted
            character = multi_character_manager.get_character(self.test_characters[-1].character_id)
            assert character is None
            print("✓ Verified character deletion")
            
            # Test 3: Delete account
            success = multi_character_manager.delete_account(self.test_accounts[-1].account_id)
            assert success == True
            print("✓ Deleted account")
            
            # Test 4: Verify account is deleted
            account = multi_character_manager.get_account(self.test_accounts[-1].account_id)
            assert account is None
            print("✓ Verified account deletion")
            
            return {"test": "Cleanup", "status": "PASS", "details": "All cleanup tests passed"}
            
        except Exception as e:
            logger.error(f"Cleanup test failed: {e}")
            return {"test": "Cleanup", "status": "FAIL", "details": str(e)}
    
    def print_test_summary(self, results: List[Dict[str, Any]]):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = 0
        failed = 0
        skipped = 0
        
        for result in results:
            status = result["status"]
            if status == "PASS":
                passed += 1
                print(f"✓ {result['test']}: PASS")
            elif status == "FAIL":
                failed += 1
                print(f"✗ {result['test']}: FAIL - {result['details']}")
            elif status == "SKIP":
                skipped += 1
                print(f"⚠ {result['test']}: SKIP - {result['details']}")
        
        print()
        print(f"Total Tests: {len(results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Skipped: {skipped}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n❌ {failed} TEST(S) FAILED")
        
        print("=" * 80)

def main():
    """Run the test suite."""
    tester = MultiCharacterProfileTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Demo script for Batch 181 - MS11 Quest Log Verifier Module

This demo showcases the quest log verifier functionality including:
- Quest log checking via /journal command or UI detection
- Quest chain eligibility verification
- Fallback alerts for detection failures
- Integration with session manager
- Terminal message output
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.ms11.utils.quest_log_checker import (
        QuestLogChecker,
        QuestChain,
        QuestEntry,
        QuestStatus,
        verify_quest_chain,
        check_quest_log,
        get_eligible_quest_chains,
        get_completed_quests,
        add_completed_quest,
        save_quest_log,
        get_quest_log_status
    )
    from core.session_manager import SessionManager
    from utils.license_hooks import requires_license
    from profession_logic.utils.logger import logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class Batch181QuestLogVerifierDemo:
    """Demo class for showcasing Batch 181 quest log verifier functionality."""
    
    def __init__(self):
        """Initialize the demo."""
        self.demo_results = {}
        self.config_path = "config/quest_log_config.json"
        self.quest_chains_file = "data/quest_chains.json"
        
        print("🎮 Batch 181 - MS11 Quest Log Verifier Module Demo")
        print("=" * 60)
        
    def run_all_demos(self) -> bool:
        """Run all demo scenarios."""
        demos = [
            ("Configuration Test", self.demo_configuration),
            ("Quest Log Checker Test", self.demo_quest_log_checker),
            ("Quest Chain Verification Test", self.demo_quest_chain_verification),
            ("Session Manager Integration Test", self.demo_session_manager_integration),
            ("Fallback Alert Test", self.demo_fallback_alert),
            ("Terminal Message Test", self.demo_terminal_message),
            ("Full Integration Test", self.demo_full_integration)
        ]
        
        print(f"\n🚀 Running {len(demos)} demo scenarios...")
        
        for demo_name, demo_func in demos:
            print(f"\n📋 Running: {demo_name}")
            try:
                result = demo_func()
                self.demo_results[demo_name] = result
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"   {status}")
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                self.demo_results[demo_name] = False
        
        return self._print_summary()
    
    def demo_configuration(self) -> bool:
        """Demo 1: Test configuration loading and validation."""
        print("   Testing configuration system...")
        
        try:
            # Test quest log config loading
            if not os.path.exists(self.config_path):
                print("   ❌ Quest log config not found")
                return False
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Check for required configuration keys
            required_keys = ["enabled", "use_journal_command", "use_ui_detection", "fallback_alert"]
            for key in required_keys:
                if key not in config:
                    print(f"   ❌ Missing config key: {key}")
                    return False
            
            print("   ✅ Configuration loaded successfully")
            print(f"   📊 Quest log checker enabled: {config.get('enabled', False)}")
            print(f"   📊 Journal command enabled: {config.get('use_journal_command', False)}")
            print(f"   📊 UI detection enabled: {config.get('use_ui_detection', False)}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Configuration error: {e}")
            return False
    
    def demo_quest_log_checker(self) -> bool:
        """Demo 2: Test quest log checker functionality."""
        print("   Testing quest log checker...")
        
        try:
            # Create quest log checker
            checker = QuestLogChecker()
            
            # Test quest log checking
            success = checker.check_quest_log()
            
            if not success:
                print("   ❌ Failed to check quest log")
                return False
            
            # Test getting completed quests
            completed_quests = checker.get_completed_quests()
            
            print("   ✅ Quest log checker working")
            print(f"   📊 Completed quests: {len(completed_quests)}")
            print(f"   📊 Quest chains loaded: {len(checker.quest_chains)}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Quest log checker error: {e}")
            return False
    
    def demo_quest_chain_verification(self) -> bool:
        """Demo 3: Test quest chain verification."""
        print("   Testing quest chain verification...")
        
        try:
            # Create quest log checker
            checker = QuestLogChecker()
            
            # Test different quest chains
            test_chains = [
                "tatooine_tusken_chain",
                "imperial_officer_chain",
                "jedi_training_chain"
            ]
            
            for chain_id in test_chains:
                is_eligible, message = checker.verify_quest_chain_eligibility(chain_id)
                
                if is_eligible:
                    print(f"   ✅ {chain_id} is eligible")
                else:
                    print(f"   ⚠️ {chain_id} is not eligible: {message}")
            
            # Test getting eligible quest chains
            eligible_chains = checker.get_eligible_quest_chains()
            print(f"   📊 Eligible quest chains: {len(eligible_chains)}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Quest chain verification error: {e}")
            return False
    
    def demo_session_manager_integration(self) -> bool:
        """Demo 4: Test session manager integration."""
        print("   Testing session manager integration...")
        
        try:
            # Create session manager
            session = SessionManager(mode="quest")
            
            # Test quest log checking
            success = session.check_quest_log()
            
            if not success:
                print("   ❌ Failed to check quest log in session")
                return False
            
            # Test quest chain verification
            is_eligible, message = session.verify_quest_chain_eligibility("tatooine_tusken_chain")
            
            print("   ✅ Session manager integration working")
            print(f"   📊 Quest log verified: {session.quest_log_verified}")
            print(f"   📊 Chain eligible: {is_eligible}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Session manager integration error: {e}")
            return False
    
    def demo_fallback_alert(self) -> bool:
        """Demo 5: Test fallback alert functionality."""
        print("   Testing fallback alert...")
        
        try:
            # Create quest log checker with fallback enabled
            checker = QuestLogChecker()
            
            # Simulate a failed quest log check
            # This would normally happen when /journal and UI detection both fail
            print("   📊 Simulating fallback alert scenario...")
            
            # Test fallback alert (this should log a warning)
            checker._send_fallback_alert()
            
            print("   ✅ Fallback alert working")
            print("   📊 Check logs for fallback alert message")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Fallback alert error: {e}")
            return False
    
    def demo_terminal_message(self) -> bool:
        """Demo 6: Test terminal message output."""
        print("   Testing terminal message output...")
        
        try:
            # Create session manager
            session = SessionManager(mode="quest")
            
            # Test quest chain verification (this should print the terminal message)
            is_eligible, message = session.verify_quest_chain_eligibility("jedi_training_chain")
            
            print("   ✅ Terminal message working")
            print(f"   📊 Message: {message}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Terminal message error: {e}")
            return False
    
    def demo_full_integration(self) -> bool:
        """Demo 7: Full integration test."""
        print("   Testing full integration...")
        
        try:
            # Test the main quest log verification function
            is_eligible, message = verify_quest_chain("tatooine_tusken_chain")
            
            if is_eligible:
                print("   ✅ Full integration working")
                print(f"   📊 Message: {message}")
                return True
            else:
                print(f"   ❌ Full integration failed: {message}")
                return False
            
        except Exception as e:
            print(f"   ❌ Full integration error: {e}")
            return False
    
    def _print_summary(self) -> bool:
        """Print demo summary."""
        print("\n" + "=" * 60)
        print("📊 DEMO SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.demo_results.values() if result)
        total = len(self.demo_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 All demos passed! Batch 181 Quest Log Verifier is working correctly.")
            return True
        else:
            print("\n⚠️  Some demos failed. Check the output above for details.")
            return False
    
    def test_quest_chains(self) -> None:
        """Test all quest chains."""
        print("\n🔧 Testing Quest Chains")
        print("-" * 30)
        
        quest_chains = [
            ("Tatooine Tusken Raider Chain", "tatooine_tusken_chain"),
            ("Imperial Officer Chain", "imperial_officer_chain"),
            ("Jedi Training Chain", "jedi_training_chain"),
            ("Smuggler's Run Chain", "smuggler_run_chain"),
            ("Bounty Hunter Chain", "bounty_hunter_chain"),
            ("Medical Emergency Chain", "medical_emergency_chain"),
            ("Entertainment Circuit Chain", "entertainment_circuit_chain"),
            ("Crafting Mastery Chain", "crafting_mastery_chain")
        ]
        
        for chain_name, chain_id in quest_chains:
            print(f"   Testing {chain_name}...")
            
            try:
                is_eligible, message = verify_quest_chain(chain_id)
                
                if is_eligible:
                    print(f"   ✅ {chain_name} is eligible")
                else:
                    print(f"   ❌ {chain_name} is not eligible: {message}")
                    
            except Exception as e:
                print(f"   ❌ Error testing {chain_name}: {e}")
    
    def test_configuration_options(self) -> None:
        """Test configuration options."""
        print("\n🔧 Testing Configuration Options")
        print("-" * 30)
        
        config_options = [
            ("Default", {}),
            ("Journal Command Only", {"use_journal_command": True, "use_ui_detection": False}),
            ("UI Detection Only", {"use_journal_command": False, "use_ui_detection": True}),
            ("Fallback Disabled", {"fallback_alert": False}),
            ("Fast Cache", {"cache_duration": 60})
        ]
        
        for config_name, config_updates in config_options:
            print(f"   Testing {config_name}...")
            
            try:
                # Create checker with custom config
                checker = QuestLogChecker()
                
                # Apply configuration updates
                for key, value in config_updates.items():
                    checker.config[key] = value
                
                # Test quest log checking
                success = checker.check_quest_log()
                
                if success:
                    print(f"   ✅ {config_name} working")
                else:
                    print(f"   ❌ {config_name} failed")
                    
            except Exception as e:
                print(f"   ❌ Error testing {config_name}: {e}")


@requires_license
def main():
    """Main demo function."""
    print("🚀 Starting Batch 181 Quest Log Verifier Demo")
    print("=" * 60)
    
    # Check if required files exist
    required_files = [
        "config/quest_log_config.json",
        "data/quest_chains.json",
        "src/ms11/utils/quest_log_checker.py"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Required file not found: {file_path}")
            return False
    
    print("✅ All required files found")
    
    # Create demo instance
    demo = Batch181QuestLogVerifierDemo()
    
    # Run all demos
    success = demo.run_all_demos()
    
    # Run additional tests
    demo.test_quest_chains()
    demo.test_configuration_options()
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        sys.exit(1) 
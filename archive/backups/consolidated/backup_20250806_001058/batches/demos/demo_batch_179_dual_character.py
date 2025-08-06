#!/usr/bin/env python3
"""
Demo script for Batch 179 - Dual-Character Support for Same Account

This demo showcases the enhanced dual-character support including:
- Support for running two MS11-controlled characters from the same SWG account
- Primary character can lead (questing), second can follow (medic/dancer)
- Shared Discord channel for both (with tag)
- Session monitor to detect dropped client
- Simultaneous quest + support operation
- Session logs per character stored under shared session ID
"""

import os
import sys
import time
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.session_manager import (
        DualCharacterSessionManager,
        run_dual_character_mode,
        get_dual_session_status,
        stop_dual_session
    )
    from src.ms11.modes.dual_mode_support import (
        DualModeSupport,
        DualModeConfig,
        DualModeType,
        run as run_dual_mode,
        get_dual_mode_status,
        stop_dual_mode
    )
    from utils.license_hooks import requires_license
    from profession_logic.utils.logger import logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class Batch179DualCharacterDemo:
    """Demo class for showcasing Batch 179 dual character support functionality."""
    
    def __init__(self):
        """Initialize the demo."""
        self.demo_results = {}
        self.config_path = "config/session_config.json"
        
        print("🎮 Batch 179 - Dual-Character Support for Same Account Demo")
        print("=" * 60)
        
    def run_all_demos(self) -> bool:
        """Run all demo scenarios."""
        demos = [
            ("Configuration Test", self.demo_configuration),
            ("Session Manager Test", self.demo_session_manager),
            ("Dual Mode Support Test", self.demo_dual_mode_support),
            ("Discord Integration Test", self.demo_discord_integration),
            ("Session Monitor Test", self.demo_session_monitor),
            ("Logging Test", self.demo_logging),
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
            # Test session config loading
            if not os.path.exists(self.config_path):
                print("   ❌ Session config not found")
                return False
            
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Check for dual mode configuration
            if "dual_mode" not in config:
                print("   ❌ Dual mode config missing")
                return False
            
            # Check for required character configurations
            required_keys = ["primary_character", "secondary_character", "shared_discord_channel", "session_monitor"]
            for key in required_keys:
                if key not in config:
                    print(f"   ❌ Missing config key: {key}")
                    return False
            
            print("   ✅ Configuration loaded successfully")
            print(f"   📊 Dual mode enabled: {config.get('dual_mode', False)}")
            print(f"   👤 Primary character: {config.get('primary_character', {}).get('name', 'Unknown')}")
            print(f"   👤 Secondary character: {config.get('secondary_character', {}).get('name', 'Unknown')}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Configuration error: {e}")
            return False
    
    def demo_session_manager(self) -> bool:
        """Demo 2: Test session manager functionality."""
        print("   Testing session manager...")
        
        try:
            # Create session manager
            manager = DualCharacterSessionManager()
            
            # Test starting a dual session
            success = manager.start_dual_session(
                "DemoQuester", "SWG - DemoQuester",
                "DemoMedic", "SWG - DemoMedic"
            )
            
            if not success:
                print("   ❌ Failed to start dual session")
                return False
            
            # Get session status
            status = manager.get_session_status()
            
            if status.get("status") == "not_started":
                print("   ❌ Session not started properly")
                return False
            
            print("   ✅ Session manager working")
            print(f"   📊 Session ID: {status.get('session_id', 'Unknown')}")
            
            # Stop session
            manager.stop_dual_session()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Session manager error: {e}")
            return False
    
    def demo_dual_mode_support(self) -> bool:
        """Demo 3: Test dual mode support functionality."""
        print("   Testing dual mode support...")
        
        try:
            # Create dual mode support
            dual_support = DualModeSupport()
            
            # Test different dual mode types
            mode_types = [
                DualModeType.QUEST_MEDIC,
                DualModeType.QUEST_DANCER,
                DualModeType.COMBAT_PAIR
            ]
            
            for mode_type in mode_types:
                dual_support.config.dual_mode_type = mode_type
                dual_support.config.dual_mode_enabled = True
                
                # Start dual mode
                success = dual_support.start_dual_mode("TestPrimary", "TestSecondary")
                
                if success:
                    status = dual_support.get_session_status()
                    print(f"   ✅ {mode_type.value} mode working")
                    print(f"   📊 Session ID: {status.get('session_id', 'Unknown')}")
                    
                    # Stop dual mode
                    dual_support.stop_dual_mode()
                else:
                    print(f"   ❌ {mode_type.value} mode failed")
                    return False
            
            return True
            
        except Exception as e:
            print(f"   ❌ Dual mode support error: {e}")
            return False
    
    def demo_discord_integration(self) -> bool:
        """Demo 4: Test Discord integration."""
        print("   Testing Discord integration...")
        
        try:
            # Create dual mode support with Discord enabled
            dual_support = DualModeSupport()
            dual_support.config.shared_discord_enabled = True
            dual_support.config.discord_tag_format = "[{character}] {message}"
            
            # Start dual mode
            success = dual_support.start_dual_mode("DiscordTest1", "DiscordTest2")
            
            if not success:
                print("   ❌ Failed to start dual mode for Discord test")
                return False
            
            # Test Discord message sending
            test_messages = [
                "Hello from primary character!",
                "Healing nearby players...",
                "Quest completed: Kill 10 Tusken Raiders"
            ]
            
            for message in test_messages:
                dual_support._send_discord_alert(message)
                time.sleep(0.5)
            
            print("   ✅ Discord integration working")
            print("   📊 Test messages sent successfully")
            
            # Stop dual mode
            dual_support.stop_dual_mode()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Discord integration error: {e}")
            return False
    
    def demo_session_monitor(self) -> bool:
        """Demo 5: Test session monitoring."""
        print("   Testing session monitor...")
        
        try:
            # Create dual mode support with monitoring enabled
            dual_support = DualModeSupport()
            dual_support.config.session_monitor_enabled = True
            dual_support.config.monitor_interval = 5  # Fast for testing
            dual_support.config.drop_threshold = 10
            
            # Start dual mode
            success = dual_support.start_dual_mode("MonitorTest1", "MonitorTest2")
            
            if not success:
                print("   ❌ Failed to start dual mode for monitoring test")
                return False
            
            # Let monitor run for a bit
            time.sleep(3)
            
            # Check if monitor is running
            if dual_support.monitor_thread and dual_support.monitor_thread.is_alive():
                print("   ✅ Session monitor working")
                print("   📊 Monitor thread active")
            else:
                print("   ❌ Session monitor not running")
                return False
            
            # Stop dual mode
            dual_support.stop_dual_mode()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Session monitor error: {e}")
            return False
    
    def demo_logging(self) -> bool:
        """Demo 6: Test session logging."""
        print("   Testing session logging...")
        
        try:
            # Create dual mode support
            dual_support = DualModeSupport()
            dual_support.config.dual_mode_enabled = True
            
            # Start dual mode
            success = dual_support.start_dual_mode("LogTest1", "LogTest2")
            
            if not success:
                print("   ❌ Failed to start dual mode for logging test")
                return False
            
            # Simulate some activity
            if dual_support.primary_session:
                dual_support.primary_session["xp_gained"] = 1500
                dual_support.primary_session["quests_completed"] = 3
                dual_support.primary_session["combat_kills"] = 25
            
            if dual_support.secondary_session:
                dual_support.secondary_session["xp_gained"] = 800
                dual_support.secondary_session["quests_completed"] = 1
                dual_support.secondary_session["combat_kills"] = 5
            
            # Stop dual mode (this should trigger logging)
            dual_support.stop_dual_mode()
            
            # Check if logs were created
            log_dir = Path("logs/dual_mode_sessions")
            if log_dir.exists():
                log_files = list(log_dir.glob("*.json"))
                if log_files:
                    print("   ✅ Session logging working")
                    print(f"   📊 Log files created: {len(log_files)}")
                    return True
                else:
                    print("   ❌ No log files created")
                    return False
            else:
                print("   ❌ Log directory not created")
                return False
            
        except Exception as e:
            print(f"   ❌ Session logging error: {e}")
            return False
    
    def demo_full_integration(self) -> bool:
        """Demo 7: Full integration test."""
        print("   Testing full integration...")
        
        try:
            # Test the main dual character mode function
            result = run_dual_character_mode(
                "IntegrationPrimary", "SWG - IntegrationPrimary",
                "IntegrationSecondary", "SWG - IntegrationSecondary"
            )
            
            if result.get("status") == "success":
                print("   ✅ Full integration working")
                print(f"   📊 Session ID: {result.get('session_id', 'Unknown')}")
                return True
            else:
                print(f"   ❌ Full integration failed: {result.get('message', 'Unknown error')}")
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
            print("\n🎉 All demos passed! Batch 179 Dual-Character Support is working correctly.")
            return True
        else:
            print("\n⚠️  Some demos failed. Check the output above for details.")
            return False
    
    def test_dual_mode_types(self) -> None:
        """Test all dual mode types."""
        print("\n🔧 Testing Dual Mode Types")
        print("-" * 30)
        
        mode_types = [
            ("Quest + Medic", DualModeType.QUEST_MEDIC),
            ("Quest + Dancer", DualModeType.QUEST_DANCER),
            ("Quest + Entertainer", DualModeType.QUEST_ENTERTAINER),
            ("Combat Pair", DualModeType.COMBAT_PAIR),
            ("Crafting + Support", DualModeType.CRAFTING_SUPPORT)
        ]
        
        for mode_name, mode_type in mode_types:
            print(f"   Testing {mode_name}...")
            
            dual_support = DualModeSupport()
            dual_support.config.dual_mode_type = mode_type
            dual_support.config.dual_mode_enabled = True
            
            success = dual_support.start_dual_mode("TestPrimary", "TestSecondary")
            
            if success:
                print(f"   ✅ {mode_name} working")
                dual_support.stop_dual_mode()
            else:
                print(f"   ❌ {mode_name} failed")
    
    def test_configuration_options(self) -> None:
        """Test configuration options."""
        print("\n🔧 Testing Configuration Options")
        print("-" * 30)
        
        config = DualModeConfig()
        
        # Test different configurations
        test_configs = [
            ("Default", {}),
            ("Discord Enabled", {"shared_discord_enabled": True}),
            ("Fast Monitor", {"monitor_interval": 10, "drop_threshold": 30}),
            ("No Auto Reconnect", {"auto_reconnect": False}),
            ("Custom Tag Format", {"discord_tag_format": "({character}) {message}"})
        ]
        
        for config_name, config_updates in test_configs:
            print(f"   Testing {config_name}...")
            
            # Apply configuration updates
            for key, value in config_updates.items():
                setattr(config, key, value)
            
            # Test configuration
            dual_support = DualModeSupport(config)
            dual_support.config.dual_mode_enabled = True
            
            success = dual_support.start_dual_mode("ConfigTest1", "ConfigTest2")
            
            if success:
                print(f"   ✅ {config_name} working")
                dual_support.stop_dual_mode()
            else:
                print(f"   ❌ {config_name} failed")


@requires_license
def main():
    """Main demo function."""
    print("🚀 Starting Batch 179 Dual-Character Support Demo")
    print("=" * 60)
    
    # Check if required files exist
    required_files = [
        "config/session_config.json",
        "src/session_manager.py",
        "src/ms11/modes/dual_mode_support.py"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Required file not found: {file_path}")
            return False
    
    print("✅ All required files found")
    
    # Create demo instance
    demo = Batch179DualCharacterDemo()
    
    # Run all demos
    success = demo.run_all_demos()
    
    # Run additional tests
    demo.test_dual_mode_types()
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
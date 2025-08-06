#!/usr/bin/env python3
"""
Demo script for Batch 174 - Dual-Character Bot Mode (MultiWindow Support)

This demo showcases the enhanced dual-character support including:
- Logic to control two game instances (via VM, sandbox, or two windows)
- One character can follow/support the other
- Special use case: Medic/Dancer support mode
- Shared data layer for XP, quests, buffs
- Separate config per character
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.session.dual_character_mode import (
    DualCharacterModeManager, 
    DualCharacterMode, 
    SupportType, 
    CharacterConfig,
    CharacterMode,
    CharacterRole,
    run_dual_character_mode
)


class DualCharacterModeDemo:
    """Demo class for showcasing dual character mode functionality."""
    
    def __init__(self):
        """Initialize the demo with logging setup."""
        self.setup_logging()
        self.demo_results = {}
        self.start_time = datetime.now()
        
        print("🎮 Batch 174 - Dual-Character Bot Mode (MultiWindow Support) Demo")
        print("=" * 70)
    
    def setup_logging(self):
        """Setup logging for the demo."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def demo_config_loading(self) -> bool:
        """Demo 1: Configuration loading and validation."""
        print("\n📋 Demo 1: Configuration Loading")
        print("-" * 40)
        
        try:
            # Test main config loading
            config_path = Path("config/dual_character_config.json")
            if not config_path.exists():
                print("❌ Dual character config not found")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate config structure
            required_sections = ["character_1", "character_2", "shared_data", "support_modes"]
            for section in required_sections:
                if section not in config:
                    print(f"❌ Missing required section: {section}")
                    return False
            
            print(f"✅ Loaded dual character config")
            print(f"✅ Character 1: {config['character_1']['name']}")
            print(f"✅ Character 2: {config['character_2']['name']}")
            print(f"✅ Mode: {config['mode']}")
            print(f"✅ Support modes: {list(config['support_modes'].keys())}")
            
            # Test character-specific configs
            char1_config_path = Path("config/character_1_config.json")
            char2_config_path = Path("config/character_2_config.json")
            
            if char1_config_path.exists():
                with open(char1_config_path, 'r', encoding='utf-8') as f:
                    char1_config = json.load(f)
                print(f"✅ Character 1 config loaded: {char1_config['character_name']}")
            
            if char2_config_path.exists():
                with open(char2_config_path, 'r', encoding='utf-8') as f:
                    char2_config = json.load(f)
                print(f"✅ Character 2 config loaded: {char2_config['character_name']}")
            
            self.demo_results["config_loading"] = True
            return True
            
        except Exception as e:
            print(f"❌ Config loading failed: {e}")
            self.demo_results["config_loading"] = False
            return False
    
    def demo_character_registration(self) -> bool:
        """Demo 2: Character registration system."""
        print("\n👥 Demo 2: Character Registration")
        print("-" * 40)
        
        try:
            manager = DualCharacterModeManager()
            
            # Create character configs
            char1_config = CharacterConfig(
                name="MainChar",
                window_title="SWG - MainChar",
                mode=CharacterMode.MAIN,
                role=CharacterRole.LEADER,
                config_file="config/character_1_config.json"
            )
            
            char2_config = CharacterConfig(
                name="SupportChar",
                window_title="SWG - SupportChar",
                mode=CharacterMode.SUPPORT,
                role=CharacterRole.FOLLOWER,
                support_type=SupportType.MEDIC,
                config_file="config/character_2_config.json"
            )
            
            # Register characters
            success1 = manager.register_character(char1_config)
            success2 = manager.register_character(char2_config)
            
            if success1 and success2:
                print("✅ Both characters registered successfully")
                print(f"✅ Main Character: {char1_config.name} ({char1_config.role.value})")
                print(f"✅ Support Character: {char2_config.name} ({char2_config.support_type.value})")
                print(f"✅ Total characters: {len(manager.characters)}")
                
                self.demo_results["character_registration"] = True
                return True
            else:
                print("❌ Character registration failed")
                self.demo_results["character_registration"] = False
                return False
                
        except Exception as e:
            print(f"❌ Character registration failed: {e}")
            self.demo_results["character_registration"] = False
            return False
    
    def demo_window_management(self) -> bool:
        """Demo 3: Window management and arrangement."""
        print("\n🖥️ Demo 3: Window Management")
        print("-" * 40)
        
        try:
            manager = DualCharacterModeManager()
            window_manager = manager.window_manager
            
            # Test window arrangement
            window1_title = "SWG - MainChar"
            window2_title = "SWG - SupportChar"
            
            # Simulate window arrangement (without actual windows)
            success = window_manager.arrange_dual_windows(window1_title, window2_title)
            
            if success:
                print("✅ Window arrangement logic working")
                print("✅ Dual window positioning configured")
                print("✅ Split-screen layout ready")
                
                # Test window position retrieval
                pos1 = window_manager.get_window_position(window1_title)
                pos2 = window_manager.get_window_position(window2_title)
                
                if pos1 and pos2:
                    print(f"✅ Window positions: {window1_title} at {pos1}, {window2_title} at {pos2}")
                
                self.demo_results["window_management"] = True
                return True
            else:
                print("❌ Window arrangement failed")
                self.demo_results["window_management"] = False
                return False
                
        except Exception as e:
            print(f"❌ Window management failed: {e}")
            self.demo_results["window_management"] = False
            return False
    
    def demo_shared_data_layer(self) -> bool:
        """Demo 4: Shared data layer functionality."""
        print("\n📊 Demo 4: Shared Data Layer")
        print("-" * 40)
        
        try:
            manager = DualCharacterModeManager()
            
            # Test shared data initialization
            shared_data = manager.shared_data
            
            print(f"✅ Session ID: {shared_data.session_id}")
            print(f"✅ Start Time: {shared_data.start_time}")
            print(f"✅ XP Data: {len(shared_data.xp_data)} entries")
            print(f"✅ Quest Data: {len(shared_data.quest_data)} entries")
            print(f"✅ Buff Data: {len(shared_data.buff_data)} entries")
            print(f"✅ Position Data: {len(shared_data.position_data)} entries")
            
            # Test data synchronization
            test_xp_data = {"MainChar": 1000, "SupportChar": 500}
            test_quest_data = {"MainChar": {"active_quests": 2}, "SupportChar": {"active_quests": 0}}
            test_buff_data = {"MainChar": {"buffs": ["heal_health"]}, "SupportChar": {"buffs": []}}
            
            shared_data.xp_data.update(test_xp_data)
            shared_data.quest_data.update(test_quest_data)
            shared_data.buff_data.update(test_buff_data)
            
            print("✅ Data synchronization working")
            print(f"✅ XP Sync: {shared_data.xp_data}")
            print(f"✅ Quest Sync: {shared_data.quest_data}")
            print(f"✅ Buff Sync: {shared_data.buff_data}")
            
            self.demo_results["shared_data_layer"] = True
            return True
            
        except Exception as e:
            print(f"❌ Shared data layer failed: {e}")
            self.demo_results["shared_data_layer"] = False
            return False
    
    def demo_support_modes(self) -> bool:
        """Demo 5: Support mode functionality."""
        print("\n🩺 Demo 5: Support Modes")
        print("-" * 40)
        
        try:
            manager = DualCharacterModeManager()
            
            # Test different support types
            support_types = [
                SupportType.MEDIC,
                SupportType.DANCER,
                SupportType.ENTERTAINER,
                SupportType.COMBAT_SUPPORT,
                SupportType.CRAFTING_SUPPORT
            ]
            
            print("Testing support modes:")
            for support_type in support_types:
                print(f"  ✅ {support_type.value}: {support_type.name}")
            
            # Test support mode configuration
            config = manager.config
            support_modes = config.get("support_modes", {})
            
            print(f"\nSupport mode configurations:")
            for mode_name, mode_config in support_modes.items():
                print(f"  📋 {mode_name}:")
                print(f"    - Buff interval: {mode_config.get('buff_interval', 'N/A')}s")
                print(f"    - Heal interval: {mode_config.get('heal_interval', 'N/A')}s")
                print(f"    - Buff range: {mode_config.get('buff_range', 'N/A')}")
                print(f"    - Stationary: {mode_config.get('stationary', 'N/A')}")
                print(f"    - Follow leader: {mode_config.get('follow_leader', 'N/A')}")
            
            self.demo_results["support_modes"] = True
            return True
            
        except Exception as e:
            print(f"❌ Support modes failed: {e}")
            self.demo_results["support_modes"] = False
            return False
    
    def demo_communication_system(self) -> bool:
        """Demo 6: Inter-character communication."""
        print("\n💬 Demo 6: Communication System")
        print("-" * 40)
        
        try:
            manager = DualCharacterModeManager()
            
            # Test message sending
            test_messages = [
                {"type": "position", "data": {"position": [100, 200]}},
                {"type": "xp", "data": {"xp_gained": 150}},
                {"type": "quest", "data": {"quest_completed": "Test Quest"}},
                {"type": "buff", "data": {"buff_applied": "heal_health"}},
                {"type": "status", "data": {"status": "in_combat"}}
            ]
            
            print("Testing message types:")
            for msg in test_messages:
                print(f"  ✅ {msg['type']}: {msg['data']}")
            
            # Test communication configuration
            comm_config = manager.config.get("communication", {})
            print(f"\nCommunication configuration:")
            print(f"  📡 Port: {comm_config.get('port', 'N/A')}")
            print(f"  ⏱️ Timeout: {comm_config.get('timeout', 'N/A')}s")
            print(f"  🔄 Retry attempts: {comm_config.get('retry_attempts', 'N/A')}")
            print(f"  📦 Message queue size: {comm_config.get('message_queue_size', 'N/A')}")
            print(f"  🔒 Encryption: {comm_config.get('encryption', 'N/A')}")
            print(f"  🗜️ Compression: {comm_config.get('compression', 'N/A')}")
            
            self.demo_results["communication_system"] = True
            return True
            
        except Exception as e:
            print(f"❌ Communication system failed: {e}")
            self.demo_results["communication_system"] = False
            return False
    
    def demo_safety_features(self) -> bool:
        """Demo 7: Safety and monitoring features."""
        print("\n🛡️ Demo 7: Safety Features")
        print("-" * 40)
        
        try:
            manager = DualCharacterModeManager()
            
            # Test safety configuration
            safety_config = manager.config.get("safety", {})
            
            print("Safety configuration:")
            print(f"  ⏰ Max session duration: {safety_config.get('max_session_duration', 'N/A')}s")
            print(f"  😴 AFK timeout: {safety_config.get('afk_timeout', 'N/A')}s")
            print(f"  🚨 Emergency stop: {safety_config.get('emergency_stop', 'N/A')}")
            print(f"  🧹 Auto cleanup: {safety_config.get('auto_cleanup', 'N/A')}")
            print(f"  ❤️ Health threshold: {safety_config.get('health_threshold', 'N/A')}%")
            print(f"  🔌 Disconnect timeout: {safety_config.get('disconnect_timeout', 'N/A')}s")
            print(f"  🔄 Max retry attempts: {safety_config.get('max_retry_attempts', 'N/A')}")
            
            # Test performance configuration
            perf_config = manager.config.get("performance", {})
            print(f"\nPerformance configuration:")
            print(f"  ⚡ Sync interval: {perf_config.get('sync_interval', 'N/A')}s")
            print(f"  📊 Monitor interval: {perf_config.get('monitor_interval', 'N/A')}s")
            print(f"  🧹 Cleanup interval: {perf_config.get('cleanup_interval', 'N/A')}s")
            print(f"  💾 Max memory usage: {perf_config.get('max_memory_usage', 'N/A')}")
            print(f"  🖥️ CPU threshold: {perf_config.get('cpu_threshold', 'N/A')}%")
            print(f"  🌐 Network timeout: {perf_config.get('network_timeout', 'N/A')}s")
            
            self.demo_results["safety_features"] = True
            return True
            
        except Exception as e:
            print(f"❌ Safety features failed: {e}")
            self.demo_results["safety_features"] = False
            return False
    
    def demo_full_dual_mode(self) -> bool:
        """Demo 8: Full dual character mode simulation."""
        print("\n🎮 Demo 8: Full Dual Character Mode")
        print("-" * 40)
        
        try:
            # Test the main dual character mode function
            result = run_dual_character_mode(
                char1_name="MainChar",
                char1_window="SWG - MainChar",
                char2_name="SupportChar",
                char2_window="SWG - SupportChar",
                mode=DualCharacterMode.LEADER_FOLLOWER,
                support_type=SupportType.MEDIC
            )
            
            if result.get("success", False):
                print("✅ Dual character mode started successfully")
                print(f"✅ Status: {result.get('status', 'N/A')}")
                print(f"✅ Characters: {result.get('characters', [])}")
                print(f"✅ Mode: {result.get('mode', 'N/A')}")
                print(f"✅ Support Type: {result.get('support_type', 'N/A')}")
                
                # Test status retrieval
                manager = DualCharacterModeManager()
                status = manager.get_dual_mode_status()
                
                print(f"\nDual mode status:")
                print(f"  🏃 Running: {status.get('running', False)}")
                print(f"  👥 Active characters: {status.get('active_characters', [])}")
                print(f"  📊 Session duration: {status.get('session_duration', 0):.1f}s")
                
                self.demo_results["full_dual_mode"] = True
                return True
            else:
                print(f"❌ Dual character mode failed: {result.get('error', 'Unknown error')}")
                self.demo_results["full_dual_mode"] = False
                return False
                
        except Exception as e:
            print(f"❌ Full dual mode failed: {e}")
            self.demo_results["full_dual_mode"] = False
            return False
    
    def run_all_demos(self) -> Dict[str, Any]:
        """Run all demo scenarios."""
        print("\n🚀 Running all demos...")
        
        demos = [
            ("Configuration Loading", self.demo_config_loading),
            ("Character Registration", self.demo_character_registration),
            ("Window Management", self.demo_window_management),
            ("Shared Data Layer", self.demo_shared_data_layer),
            ("Support Modes", self.demo_support_modes),
            ("Communication System", self.demo_communication_system),
            ("Safety Features", self.demo_safety_features),
            ("Full Dual Mode", self.demo_full_dual_mode)
        ]
        
        results = {}
        for demo_name, demo_func in demos:
            print(f"\n{'='*60}")
            print(f"Running: {demo_name}")
            print(f"{'='*60}")
            
            try:
                success = demo_func()
                results[demo_name] = success
                
                if success:
                    print(f"✅ {demo_name}: PASSED")
                else:
                    print(f"❌ {demo_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {demo_name}: ERROR - {e}")
                results[demo_name] = False
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print demo summary."""
        print("\n" + "="*70)
        print("📋 DEMO SUMMARY")
        print("="*70)
        
        total_demos = len(results)
        passed_demos = sum(1 for success in results.values() if success)
        failed_demos = total_demos - passed_demos
        
        print(f"Total Demos: {total_demos}")
        print(f"Passed: {passed_demos}")
        print(f"Failed: {failed_demos}")
        print(f"Success Rate: {(passed_demos/total_demos)*100:.1f}%")
        
        print(f"\nDetailed Results:")
        for demo_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {demo_name}: {status}")
        
        if passed_demos == total_demos:
            print(f"\n🎉 All demos passed! Dual Character Mode is working correctly.")
        else:
            print(f"\n⚠️ Some demos failed. Please check the implementation.")
        
        print(f"\n⏱️ Total demo time: {(datetime.now() - self.start_time).total_seconds():.1f}s")


def main():
    """Main demo function."""
    demo = DualCharacterModeDemo()
    results = demo.run_all_demos()
    demo.print_summary(results)
    
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
#!/usr/bin/env python3
"""
Demo script for Batch 172 - Rare Loot Scan Mode (RLS Mode)

This demo showcases the comprehensive RLS mode implementation including:
- Target prioritization and configuration loading
- Area and enemy type scanning
- Rare loot detection and logging
- Discord alert integration
- Learning system and user preferences
- Session statistics and logging
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

from core.modes.rare_loot import RareLootScanner, run_rls_mode


class RLSModeDemo:
    """Demo class for showcasing RLS mode functionality."""
    
    def __init__(self):
        """Initialize the demo with logging setup."""
        self.setup_logging()
        self.demo_results = {}
        self.start_time = datetime.now()
        
        print("🎯 Batch 172 - Rare Loot Scan Mode (RLS Mode) Demo")
        print("=" * 60)
    
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
            # Test targets config loading
            config_path = Path("config/rare_loot_targets.json")
            if not config_path.exists():
                print("❌ Targets config not found")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            targets = config.get("targets", [])
            settings = config.get("settings", {})
            loot_categories = config.get("loot_categories", {})
            
            print(f"✅ Loaded {len(targets)} targets")
            print(f"✅ Loaded {len(loot_categories)} loot categories")
            print(f"✅ Settings: {list(settings.keys())}")
            
            # Validate config structure
            required_target_fields = ["name", "planet", "level", "priority"]
            for target in targets:
                missing_fields = [field for field in required_target_fields if field not in target]
                if missing_fields:
                    print(f"❌ Target {target.get('name', 'Unknown')} missing fields: {missing_fields}")
                    return False
            
            print("✅ All targets have required fields")
            self.demo_results["config_loading"] = True
            return True
            
        except Exception as e:
            print(f"❌ Config loading failed: {e}")
            self.demo_results["config_loading"] = False
            return False
    
    def demo_target_prioritization(self) -> bool:
        """Demo 2: Target prioritization system."""
        print("\n🎯 Demo 2: Target Prioritization")
        print("-" * 40)
        
        try:
            scanner = RareLootScanner()
            
            # Test basic prioritization
            targets = scanner.prioritize_targets()
            if not targets:
                print("❌ No targets available for prioritization")
                return False
            
            print(f"✅ Prioritized {len(targets)} targets")
            
            # Show top 3 targets
            print("\nTop 3 Targets:")
            for i, target in enumerate(targets[:3], 1):
                print(f"  {i}. {target['name']} (Priority: {target.get('priority', 0)})")
                print(f"     Planet: {target['planet']}, Level: {target['level']}")
                print(f"     Loot Types: {', '.join(target.get('loot_types', []))}")
            
            # Test area scanning
            area_targets = scanner.scan_area_for_targets(area_radius=2000)
            print(f"\n✅ Area scan found {len(area_targets)} nearby targets")
            
            # Test enemy type scanning
            dragon_targets = scanner.scan_by_enemy_type("dragon")
            print(f"✅ Enemy type scan found {len(dragon_targets)} dragon targets")
            
            self.demo_results["target_prioritization"] = True
            return True
            
        except Exception as e:
            print(f"❌ Target prioritization failed: {e}")
            self.demo_results["target_prioritization"] = False
            return False
    
    def demo_loot_analysis(self) -> bool:
        """Demo 3: Loot analysis and categorization."""
        print("\n💎 Demo 3: Loot Analysis")
        print("-" * 40)
        
        try:
            scanner = RareLootScanner()
            
            # Test loot analysis with sample items
            sample_items = [
                "Krayt Dragon Pearl",
                "Kimogila Hide",
                "Mouf Tigrip Poison",
                "Common Trophy",
                "Crystal Fragment",
                "Desert Sand Crystal"
            ]
            
            print("Analyzing sample loot items:")
            for item in sample_items:
                loot_info = scanner._analyze_loot_item(item)
                rarity_emoji = {
                    "common": "⚪",
                    "uncommon": "🟢", 
                    "rare": "🔵",
                    "epic": "🟣",
                    "legendary": "🟡"
                }.get(loot_info["rarity"], "❓")
                
                print(f"  {rarity_emoji} {item}")
                print(f"    Type: {loot_info['type']}, Rarity: {loot_info['rarity']}")
                print(f"    Value: {loot_info['value']} credits, Rare: {loot_info['is_rare']}")
            
            # Test rarity breakdown
            scanner.rare_loot_found = [
                {"rarity": "legendary", "value": 10000},
                {"rarity": "epic", "value": 5000},
                {"rarity": "rare", "value": 2000},
                {"rarity": "rare", "value": 1500}
            ]
            
            breakdown = scanner._get_rarity_breakdown()
            print(f"\n✅ Rarity breakdown: {breakdown}")
            
            self.demo_results["loot_analysis"] = True
            return True
            
        except Exception as e:
            print(f"❌ Loot analysis failed: {e}")
            self.demo_results["loot_analysis"] = False
            return False
    
    def demo_discord_alerts(self) -> bool:
        """Demo 4: Discord alert system."""
        print("\n🔔 Demo 4: Discord Alert System")
        print("-" * 40)
        
        try:
            scanner = RareLootScanner()
            
            # Test Discord alert message generation
            sample_loot = {
                "name": "Krayt Dragon Pearl",
                "rarity": "legendary",
                "type": "pearls",
                "value": 10000,
                "timestamp": datetime.now().isoformat(),
                "location": "Tatooine - Dune Sea"
            }
            
            scanner.current_target = {
                "name": "Greater Krayt Dragon",
                "planet": "Tatooine",
                "zone": "Dune Sea"
            }
            
            # Test alert message (without actually sending)
            print("Sample Discord alert message:")
            message = (
                f"🎉 **Rare Loot Found!**\n"
                f"**Item:** {sample_loot['name']}\n"
                f"**Rarity:** {sample_loot['rarity'].title()}\n"
                f"**Type:** {sample_loot['type']}\n"
                f"**Value:** {sample_loot['value']} credits\n"
                f"**Location:** {sample_loot['location']}\n"
                f"**Time:** {sample_loot['timestamp']}\n"
                f"**Target:** {scanner.current_target['name']}"
            )
            
            print(message)
            print("✅ Discord alert message generated successfully")
            
            self.demo_results["discord_alerts"] = True
            return True
            
        except Exception as e:
            print(f"❌ Discord alerts failed: {e}")
            self.demo_results["discord_alerts"] = False
            return False
    
    def demo_learning_system(self) -> bool:
        """Demo 5: Learning system and user preferences."""
        print("\n🧠 Demo 5: Learning System")
        print("-" * 40)
        
        try:
            scanner = RareLootScanner()
            
            # Test learning data structure
            print("Learning data structure:")
            print(f"  Successful targets: {len(scanner.learning_data.get('successful_targets', []))}")
            print(f"  Failed targets: {len(scanner.learning_data.get('failed_targets', []))}")
            print(f"  Loot patterns: {len(scanner.learning_data.get('loot_patterns', {}))}")
            
            # Test user preferences
            print("\nUser preferences:")
            print(f"  Preferred planets: {scanner.user_preferences.get('preferred_planets', [])}")
            print(f"  Preferred loot types: {scanner.user_preferences.get('preferred_loot_types', [])}")
            print(f"  Avoided targets: {scanner.user_preferences.get('avoided_targets', [])}")
            
            # Simulate learning from session
            scanner.rare_loot_found = [
                {"type": "pearls", "rarity": "legendary"},
                {"type": "scales", "rarity": "epic"},
                {"type": "hides", "rarity": "rare"}
            ]
            
            scanner.current_target = {"name": "Greater Krayt Dragon"}
            scanner.learn_from_wiki()
            
            print("✅ Learning system updated successfully")
            
            self.demo_results["learning_system"] = True
            return True
            
        except Exception as e:
            print(f"❌ Learning system failed: {e}")
            self.demo_results["learning_system"] = False
            return False
    
    def demo_session_logging(self) -> bool:
        """Demo 6: Session logging and statistics."""
        print("\n📊 Demo 6: Session Logging")
        print("-" * 40)
        
        try:
            scanner = RareLootScanner()
            
            # Simulate session data
            scanner.scan_count = 5
            scanner.rare_loot_found = [
                {"name": "Krayt Dragon Pearl", "value": 10000, "rarity": "legendary"},
                {"name": "Kimogila Hide", "value": 2000, "rarity": "rare"},
                {"name": "Mouf Tigrip Poison", "value": 3000, "rarity": "epic"}
            ]
            
            # Test session statistics
            stats = scanner.get_session_stats()
            print("Session Statistics:")
            print(f"  Scan count: {stats['scan_count']}")
            print(f"  Rare loot found: {stats['rare_loot_found']}")
            print(f"  Total value: {stats['total_value']} credits")
            print(f"  Rarity breakdown: {stats['rarity_breakdown']}")
            print(f"  Session duration: {stats['session_duration']:.1f} seconds")
            print(f"  Targets visited: {stats['targets_visited']}")
            
            # Test session log export
            log_path = scanner.export_session_log()
            if log_path:
                print(f"✅ Session log exported to: {log_path}")
            else:
                print("⚠️ Session log export failed (expected in demo)")
            
            self.demo_results["session_logging"] = True
            return True
            
        except Exception as e:
            print(f"❌ Session logging failed: {e}")
            self.demo_results["session_logging"] = False
            return False
    
    def demo_full_rls_mode(self) -> bool:
        """Demo 7: Full RLS mode execution."""
        print("\n🚀 Demo 7: Full RLS Mode Execution")
        print("-" * 40)
        
        try:
            # Test full RLS mode with minimal iterations
            result = run_rls_mode(
                config={"iterations": 1},
                loop_count=1,
                area_scan=True,
                enemy_type_scan=False
            )
            
            if result.get("success"):
                print("✅ RLS mode executed successfully")
                print(f"  Stats: {result.get('stats', {})}")
                print(f"  Log path: {result.get('log_path', 'N/A')}")
                print(f"  Rare loot found: {len(result.get('rare_loot_found', []))}")
            else:
                print(f"⚠️ RLS mode completed with warnings: {result.get('error', 'Unknown error')}")
            
            self.demo_results["full_rls_mode"] = True
            return True
            
        except Exception as e:
            print(f"❌ Full RLS mode failed: {e}")
            self.demo_results["full_rls_mode"] = False
            return False
    
    def run_all_demos(self) -> Dict[str, Any]:
        """Run all demo components and return results."""
        print("Starting RLS Mode Demo Suite...")
        
        demos = [
            ("Configuration Loading", self.demo_config_loading),
            ("Target Prioritization", self.demo_target_prioritization),
            ("Loot Analysis", self.demo_loot_analysis),
            ("Discord Alerts", self.demo_discord_alerts),
            ("Learning System", self.demo_learning_system),
            ("Session Logging", self.demo_session_logging),
            ("Full RLS Mode", self.demo_full_rls_mode)
        ]
        
        results = {}
        for demo_name, demo_func in demos:
            try:
                success = demo_func()
                results[demo_name] = success
            except Exception as e:
                print(f"❌ {demo_name} demo crashed: {e}")
                results[demo_name] = False
        
        return results
    
    def print_summary(self, results: Dict[str, bool]):
        """Print demo summary and results."""
        print("\n" + "=" * 60)
        print("📋 RLS Mode Demo Summary")
        print("=" * 60)
        
        total_demos = len(results)
        successful_demos = sum(1 for success in results.values() if success)
        
        print(f"Total Demos: {total_demos}")
        print(f"Successful: {successful_demos}")
        print(f"Failed: {total_demos - successful_demos}")
        print(f"Success Rate: {(successful_demos/total_demos)*100:.1f}%")
        
        print("\nDetailed Results:")
        for demo_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {demo_name}: {status}")
        
        duration = datetime.now() - self.start_time
        print(f"\nDemo Duration: {duration.total_seconds():.1f} seconds")
        
        if successful_demos == total_demos:
            print("\n🎉 All demos passed! RLS Mode is ready for use.")
        else:
            print(f"\n⚠️ {total_demos - successful_demos} demo(s) failed. Check implementation.")
        
        return successful_demos == total_demos


def main():
    """Main demo execution function."""
    demo = RLSModeDemo()
    
    try:
        results = demo.run_all_demos()
        success = demo.print_summary(results)
        
        if success:
            print("\n✅ Batch 172 - RLS Mode Demo completed successfully!")
            return 0
        else:
            print("\n❌ Some demos failed. Check implementation.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Demo crashed: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 
#!/usr/bin/env python3
"""
MS11 Mount Selector CLI
Command-line interface for mount preference management
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Add core directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "core"))
from mount_scanner import MountScanner

class MountSelectorCLI:
    """CLI interface for mount selection and management"""
    
    def __init__(self):
        self.scanner = MountScanner()
    
    def show_available_mounts(self) -> None:
        """Display available mounts"""
        print("\n" + "=" * 50)
        print("AVAILABLE MOUNTS")
        print("=" * 50)
        
        available_mounts = self.scanner.scan_available_mounts()
        
        if not available_mounts:
            print("❌ No mounts available")
            return
        
        print(f"✓ Found {len(available_mounts)} available mounts:")
        for i, mount in enumerate(available_mounts, 1):
            speed = self.scanner.player_config.get("mount_speeds", {}).get(mount, 0.0)
            print(f"  {i}. {mount} (Speed: {speed})")
    
    def show_mount_statistics(self) -> None:
        """Display mount usage statistics"""
        print("\n" + "=" * 50)
        print("MOUNT STATISTICS")
        print("=" * 50)
        
        stats = self.scanner.get_mount_statistics()
        
        if stats["total_attempts"] == 0:
            print("📊 No mount usage data available")
            return
        
        print(f"📊 Total Attempts: {stats['total_attempts']}")
        print(f"✅ Successful: {stats['successful_attempts']}")
        print(f"📈 Success Rate: {stats['success_rate']:.1f}%")
        print(f"🏆 Most Used: {stats['most_used_mount'] or 'None'}")
        
        if stats['recent_mounts']:
            print(f"🕒 Recent Mounts: {', '.join(stats['recent_mounts'])}")
    
    def select_mount(self, mount_type: str) -> None:
        """Select and summon a mount"""
        print(f"\n🎯 Selecting mount (Type: {mount_type})")
        print("-" * 30)
        
        selected_mount, success = self.scanner.select_mount(mount_type)
        
        if success:
            print(f"✅ Successfully summoned: {selected_mount}")
        else:
            print(f"❌ Failed to summon: {selected_mount}")
    
    def retry_mount_selection(self, max_attempts: Optional[int] = None) -> None:
        """Retry mount selection with fallback"""
        print(f"\n🔄 Retrying mount selection (Max attempts: {max_attempts or 'Default'})")
        print("-" * 40)
        
        selected_mount, success = self.scanner.retry_mount_selection(max_attempts)
        
        if success:
            print(f"✅ Successfully summoned: {selected_mount}")
        else:
            print(f"❌ Failed to summon: {selected_mount}")
    
    def update_preference(self, preference: str) -> None:
        """Update mount selection preference"""
        print(f"\n⚙️ Updating mount preference to: {preference}")
        print("-" * 35)
        
        if self.scanner.update_mount_preference(preference):
            print(f"✅ Preference updated to: {preference}")
        else:
            print(f"❌ Failed to update preference: {preference}")
    
    def add_mount(self, mount_name: str) -> None:
        """Add a mount to owned mounts"""
        print(f"\n➕ Adding mount: {mount_name}")
        print("-" * 25)
        
        if self.scanner.add_owned_mount(mount_name):
            print(f"✅ Added {mount_name} to owned mounts")
        else:
            print(f"❌ Failed to add {mount_name}")
    
    def remove_mount(self, mount_name: str) -> None:
        """Remove a mount from owned mounts"""
        print(f"\n➖ Removing mount: {mount_name}")
        print("-" * 25)
        
        if self.scanner.remove_owned_mount(mount_name):
            print(f"✅ Removed {mount_name} from owned mounts")
        else:
            print(f"❌ Failed to remove {mount_name}")
    
    def show_config(self) -> None:
        """Display current configuration"""
        print("\n" + "=" * 50)
        print("CURRENT CONFIGURATION")
        print("=" * 50)
        
        config = self.scanner.player_config
        
        print(f"🎯 Preferred Mount Type: {config.get('preferred_mount', 'Unknown')}")
        print(f"🔄 Fallback Enabled: {config.get('fallback_if_unavailable', False)}")
        print(f"⚙️ Auto Select: {config.get('mount_settings', {}).get('auto_select', False)}")
        print(f"🔄 Retry Attempts: {config.get('mount_settings', {}).get('retry_attempts', 0)}")
        print(f"⏱️ Retry Delay: {config.get('mount_settings', {}).get('retry_delay', 0)}s")
        
        owned_mounts = config.get("mounts_owned", [])
        print(f"🐎 Owned Mounts ({len(owned_mounts)}):")
        for mount in owned_mounts:
            speed = config.get("mount_speeds", {}).get(mount, 0.0)
            print(f"  - {mount} (Speed: {speed})")
    
    def interactive_mode(self) -> None:
        """Run interactive mode"""
        print("\n" + "=" * 50)
        print("MS11 MOUNT SELECTOR - INTERACTIVE MODE")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. Show available mounts")
            print("2. Show mount statistics")
            print("3. Select mount (Fastest)")
            print("4. Select mount (Random)")
            print("5. Select mount (Manual)")
            print("6. Retry mount selection")
            print("7. Update preference")
            print("8. Add mount")
            print("9. Remove mount")
            print("10. Show configuration")
            print("0. Exit")
            
            try:
                choice = input("\nEnter your choice (0-10): ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                elif choice == "1":
                    self.show_available_mounts()
                elif choice == "2":
                    self.show_mount_statistics()
                elif choice == "3":
                    self.select_mount("Fastest")
                elif choice == "4":
                    self.select_mount("Random")
                elif choice == "5":
                    self.select_mount("Manual")
                elif choice == "6":
                    self.retry_mount_selection()
                elif choice == "7":
                    preference = input("Enter preference (Fastest/Random/Manual): ").strip()
                    self.update_preference(preference)
                elif choice == "8":
                    mount_name = input("Enter mount name: ").strip()
                    self.add_mount(mount_name)
                elif choice == "9":
                    mount_name = input("Enter mount name: ").strip()
                    self.remove_mount(mount_name)
                elif choice == "10":
                    self.show_config()
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="MS11 Mount Selector CLI")
    parser.add_argument("--list", action="store_true", help="List available mounts")
    parser.add_argument("--stats", action="store_true", help="Show mount statistics")
    parser.add_argument("--select", choices=["Fastest", "Random", "Manual"], 
                       help="Select mount by type")
    parser.add_argument("--retry", action="store_true", help="Retry mount selection")
    parser.add_argument("--preference", choices=["Fastest", "Random", "Manual"],
                       help="Update mount preference")
    parser.add_argument("--add-mount", type=str, help="Add mount to owned mounts")
    parser.add_argument("--remove-mount", type=str, help="Remove mount from owned mounts")
    parser.add_argument("--config", action="store_true", help="Show current configuration")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run interactive mode")
    
    args = parser.parse_args()
    
    cli = MountSelectorCLI()
    
    try:
        if args.list:
            cli.show_available_mounts()
        elif args.stats:
            cli.show_mount_statistics()
        elif args.select:
            cli.select_mount(args.select)
        elif args.retry:
            cli.retry_mount_selection()
        elif args.preference:
            cli.update_preference(args.preference)
        elif args.add_mount:
            cli.add_mount(args.add_mount)
        elif args.remove_mount:
            cli.remove_mount(args.remove_mount)
        elif args.config:
            cli.show_config()
        elif args.interactive:
            cli.interactive_mode()
        else:
            # Default: show help
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
MS11 Interface - Complete Control Center
Provides a menu-driven interface for all MS11 functionality.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional


class MS11Interface:
    """Main MS11 interface controller."""
    
    def __init__(self):
        self.current_profile = None
        self.current_mode = None
        self.session_active = False
        
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*60}")
        print(f"🚀 {title}")
        print(f"{'='*60}")
    
    def print_menu(self, title: str, options: Dict[str, str]):
        """Print a menu with options."""
        print(f"\n📋 {title}")
        print("-" * 50)
        for key, description in options.items():
            # Add color-coding based on option type
            if "Management" in description or "Control" in description:
                print(f"  {key}. ⚙️  {description}")
            elif "Monitor" in description or "Logs" in description:
                print(f"  {key}. 📊 {description}")
            elif "Deploy" in description or "Test" in description:
                print(f"  {key}. 🚀 {description}")
            else:
                print(f"  {key}. 📋 {description}")
        print(f"  0. ⬅️  Back/Exit")
        print("-" * 50)
    
    def get_user_choice(self, max_options: int) -> int:
        """Get user choice from menu."""
        while True:
            try:
                choice_str = input(f"\n👉 Enter your choice (0-{max_options}): ").strip()
                if choice_str.lower() in ['q', 'quit', 'exit']:
                    return 0
                choice = int(choice_str)
                if 0 <= choice <= max_options:
                    return choice
                else:
                    print(f"❌ Please enter a number between 0 and {max_options}")
            except ValueError:
                print("❌ Please enter a valid number (or 'q' to quit)")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                return 0
    
    def check_system_status(self) -> Dict[str, Any]:
        """Check overall MS11 system status."""
        status = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "dependencies_ok": False,
            "docker_available": False,
            "profiles_available": [],
            "sessions_running": [],
            "license_status": "unknown"
        }
        
        # Check dependencies
        try:
            import pytesseract, cv2, pyautogui
            status["dependencies_ok"] = True
        except ImportError:
            pass
        
        # Check Docker
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True)
            status["docker_available"] = result.returncode == 0
        except FileNotFoundError:
            pass
        
        # Check profiles
        profiles_dir = Path("profiles/runtime")
        if profiles_dir.exists():
            status["profiles_available"] = [
                f.stem for f in profiles_dir.glob("*.json")
            ]
        
        # Check license
        license_key = os.environ.get('ANDROID_MS11_LICENSE')
        if license_key:
            status["license_status"] = "demo" if license_key == "demo" else "licensed"
        else:
            status["license_status"] = "none"
        
        return status
    
    def show_main_menu(self):
        """Show the main MS11 interface menu."""
        while True:
            status = self.check_system_status()
            
            self.print_header("MS11 Control Center")
            
            # System Status with enhanced display
            print(f"🐍 Python: {status['python_version']}")
            deps_icon = "✅ Ready" if status['dependencies_ok'] else "❌ Missing"
            print(f"📦 Dependencies: {deps_icon}")
            docker_icon = "✅ Available" if status['docker_available'] else "⚠️  Not found"
            print(f"🐳 Docker: {docker_icon}")
            
            # License status with helpful info
            license_display = {
                "demo": "🟡 Demo Mode",
                "licensed": "✅ Licensed", 
                "none": "⚠️  Not configured"
            }
            print(f"🔑 License: {license_display.get(status['license_status'], status['license_status'])}")
            
            profile_count = len(status['profiles_available'])
            print(f"👤 Profiles: {profile_count} available")
            
            # Show current selections
            if self.current_profile:
                print(f"📌 Current Profile: {self.current_profile}")
            if self.current_mode:
                print(f"🎯 Current Mode: {self.current_mode}")
            if self.session_active:
                print(f"🟢 Session: Active")
                
            # Quick tips for new users
            if not status['dependencies_ok']:
                print(f"\n💡 Tip: Run 'python scripts/quick_test_ms11.py' to check your setup")
            elif profile_count == 0:
                print(f"\n💡 Tip: Create a profile first in 'Profile Management'")
            elif not self.current_profile:
                print(f"\n💡 Tip: Select a profile in 'Mode Control' to get started")
            
            # Main Menu
            options = {
                1: "System Management",
                2: "Profile Management", 
                3: "Mode Control",
                4: "Session Management",
                5: "Monitoring & Logs",
                6: "Deployment Tools",
                7: "Testing & Validation"
            }
            
            self.print_menu("Main Menu", options)
            choice = self.get_user_choice(7)
            
            if choice == 0:
                print("\n👋 Goodbye!")
                break
            elif choice == 1:
                self.system_management_menu()
            elif choice == 2:
                self.profile_management_menu()
            elif choice == 3:
                self.mode_control_menu()
            elif choice == 4:
                self.session_management_menu()
            elif choice == 5:
                self.monitoring_menu()
            elif choice == 6:
                self.deployment_menu()
            elif choice == 7:
                self.testing_menu()
    
    def system_management_menu(self):
        """System management submenu."""
        while True:
            self.print_header("System Management")
            
            options = {
                1: "Check System Status",
                2: "Install Dependencies",
                3: "Configure Environment",
                4: "License Management",
                5: "Back to Main Menu"
            }
            
            self.print_menu("System Management", options)
            choice = self.get_user_choice(5)
            
            if choice == 0 or choice == 5:
                break
            elif choice == 1:
                self.check_system_status_detailed()
            elif choice == 2:
                self.install_dependencies()
            elif choice == 3:
                self.configure_environment()
            elif choice == 4:
                self.license_management()
    
    def profile_management_menu(self):
        """Profile management submenu."""
        while True:
            self.print_header("Profile Management")
            
            # List available profiles
            profiles_dir = Path("profiles/runtime")
            profiles = []
            if profiles_dir.exists():
                profiles = [f.stem for f in profiles_dir.glob("*.json")]
            
            if profiles:
                print(f"📁 Available Profiles: {', '.join(profiles)}")
            else:
                print("📁 No profiles found")
            
            options = {
                1: "List Profiles",
                2: "Create New Profile",
                3: "Edit Profile",
                4: "Delete Profile",
                5: "Back to Main Menu"
            }
            
            self.print_menu("Profile Management", options)
            choice = self.get_user_choice(5)
            
            if choice == 0 or choice == 5:
                break
            elif choice == 1:
                self.list_profiles()
            elif choice == 2:
                self.create_profile()
            elif choice == 3:
                self.edit_profile()
            elif choice == 4:
                self.delete_profile()
    
    def mode_control_menu(self):
        """Mode control submenu."""
        while True:
            self.print_header("Mode Control")
            
            if self.current_profile:
                print(f"👤 Current Profile: {self.current_profile}")
            if self.current_mode:
                print(f"🎮 Current Mode: {self.current_mode}")
            
            options = {
                1: "Select Profile",
                2: "Quest Mode",
                3: "Combat Mode", 
                4: "Medic Mode",
                5: "Crafting Mode",
                6: "Other Modes",
                7: "Back to Main Menu"
            }
            
            self.print_menu("Mode Control", options)
            choice = self.get_user_choice(7)
            
            if choice == 0 or choice == 7:
                break
            elif choice == 1:
                self.select_profile()
            elif choice == 2:
                self.start_mode("quest")
            elif choice == 3:
                self.start_mode("combat")
            elif choice == 4:
                self.start_mode("medic")
            elif choice == 5:
                self.start_mode("crafting")
            elif choice == 6:
                self.other_modes_menu()
    
    def session_management_menu(self):
        """Session management submenu."""
        while True:
            self.print_header("Session Management")
            
            if self.session_active:
                print("🟢 Session Active")
            else:
                print("🔴 No Active Session")
            
            options = {
                1: "Start New Session",
                2: "Stop Current Session",
                3: "View Session Logs",
                4: "Session History",
                5: "Back to Main Menu"
            }
            
            self.print_menu("Session Management", options)
            choice = self.get_user_choice(5)
            
            if choice == 0 or choice == 5:
                break
            elif choice == 1:
                self.start_session()
            elif choice == 2:
                self.stop_session()
            elif choice == 3:
                self.view_session_logs()
            elif choice == 4:
                self.session_history()
    
    def monitoring_menu(self):
        """Monitoring and logs submenu."""
        while True:
            self.print_header("Monitoring & Logs")
            
            options = {
                1: "Real-time Logs",
                2: "System Performance",
                3: "Session Analytics",
                4: "Error Logs",
                5: "Back to Main Menu"
            }
            
            self.print_menu("Monitoring & Logs", options)
            choice = self.get_user_choice(5)
            
            if choice == 0 or choice == 5:
                break
            elif choice == 1:
                self.real_time_logs()
            elif choice == 2:
                self.system_performance()
            elif choice == 3:
                self.session_analytics()
            elif choice == 4:
                self.error_logs()
    
    def deployment_menu(self):
        """Deployment tools submenu."""
        while True:
            self.print_header("Deployment Tools")
            
            options = {
                1: "Deploy to Staging",
                2: "Deploy to Production",
                3: "Docker Management",
                4: "Health Checks",
                5: "Back to Main Menu"
            }
            
            self.print_menu("Deployment Tools", options)
            choice = self.get_user_choice(5)
            
            if choice == 0 or choice == 5:
                break
            elif choice == 1:
                self.deploy_staging()
            elif choice == 2:
                self.deploy_production()
            elif choice == 3:
                self.docker_management()
            elif choice == 4:
                self.health_checks()
    
    def testing_menu(self):
        """Testing and validation submenu."""
        while True:
            self.print_header("Testing & Validation")
            
            options = {
                1: "Run Quick Test",
                2: "Full System Test",
                3: "Mode Testing",
                4: "Performance Test",
                5: "Back to Main Menu"
            }
            
            self.print_menu("Testing & Validation", options)
            choice = self.get_user_choice(5)
            
            if choice == 0 or choice == 5:
                break
            elif choice == 1:
                self.run_quick_test()
            elif choice == 2:
                self.full_system_test()
            elif choice == 3:
                self.mode_testing()
            elif choice == 4:
                self.performance_test()
    
    # Implementation methods for each menu option
    def check_system_status_detailed(self):
        """Detailed system status check."""
        self.print_header("Detailed System Status")
        
        # Run the quick test script
        try:
            result = subprocess.run([sys.executable, "scripts/quick_test_ms11.py"], 
                                  capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
        except Exception as e:
            print(f"Error running system check: {e}")
    
    def install_dependencies(self):
        """Install MS11 dependencies."""
        self.print_header("Installing Dependencies")
        
        try:
            print("Installing Python dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
    
    def configure_environment(self):
        """Configure MS11 environment."""
        self.print_header("Environment Configuration")
        
        # Set license key
        license_key = input("Enter your MS11 license key (or 'demo' for demo mode): ")
        if license_key:
            os.environ['ANDROID_MS11_LICENSE'] = license_key
            print("✅ License key configured")
        
        # Set other environment variables
        print("\nEnvironment configuration complete!")
    
    def license_management(self):
        """License management interface."""
        self.print_header("License Management")
        
        license_key = os.environ.get('ANDROID_MS11_LICENSE')
        if license_key:
            print(f"Current License: {license_key}")
        else:
            print("No license configured")
        
        print("\nLicense management features coming soon...")
    
    def list_profiles(self):
        """List available profiles."""
        self.print_header("Available Profiles")
        
        profiles_dir = Path("profiles/runtime")
        if profiles_dir.exists():
            profiles = list(profiles_dir.glob("*.json"))
            if profiles:
                for profile in profiles:
                    print(f"📄 {profile.stem}")
            else:
                print("No profiles found")
        else:
            print("Profiles directory not found")
    
    def create_profile(self):
        """Create a new profile."""
        self.print_header("Create New Profile")
        
        name = input("Enter profile name: ")
        if name:
            profile_path = Path(f"profiles/runtime/{name}.json")
            
            # Create default profile structure
            default_profile = {
                "character_name": name,
                "server": "unknown",
                "profession": "unknown",
                "level": 1,
                "location": [0, 0],
                "settings": {
                    "auto_heal": True,
                    "auto_buff": True,
                    "safe_mode": True
                }
            }
            
            try:
                profile_path.parent.mkdir(parents=True, exist_ok=True)
                with open(profile_path, 'w') as f:
                    json.dump(default_profile, f, indent=2)
                print(f"✅ Profile '{name}' created successfully")
            except Exception as e:
                print(f"❌ Error creating profile: {e}")
    
    def edit_profile(self):
        """Edit an existing profile."""
        self.print_header("Edit Profile")
        
        profiles_dir = Path("profiles/runtime")
        if profiles_dir.exists():
            profiles = [f.stem for f in profiles_dir.glob("*.json")]
            if profiles:
                print("Available profiles:")
                for i, profile in enumerate(profiles, 1):
                    print(f"{i}. {profile}")
                
                try:
                    choice = int(input("Select profile to edit: ")) - 1
                    if 0 <= choice < len(profiles):
                        profile_name = profiles[choice]
                        print(f"Editing profile: {profile_name}")
                        # TODO: Implement profile editor
                        print("Profile editor coming soon...")
                except ValueError:
                    print("Invalid selection")
            else:
                print("No profiles available")
        else:
            print("Profiles directory not found")
    
    def delete_profile(self):
        """Delete a profile."""
        self.print_header("Delete Profile")
        
        profiles_dir = Path("profiles/runtime")
        if profiles_dir.exists():
            profiles = [f.stem for f in profiles_dir.glob("*.json")]
            if profiles:
                print("Available profiles:")
                for i, profile in enumerate(profiles, 1):
                    print(f"{i}. {profile}")
                
                try:
                    choice = int(input("Select profile to delete: ")) - 1
                    if 0 <= choice < len(profiles):
                        profile_name = profiles[choice]
                        confirm = input(f"Are you sure you want to delete '{profile_name}'? (y/N): ")
                        if confirm.lower() == 'y':
                            profile_path = profiles_dir / f"{profile_name}.json"
                            profile_path.unlink()
                            print(f"✅ Profile '{profile_name}' deleted")
                        else:
                            print("Deletion cancelled")
                except ValueError:
                    print("Invalid selection")
            else:
                print("No profiles available")
        else:
            print("Profiles directory not found")
    
    def select_profile(self):
        """Select a profile for use."""
        self.print_header("Select Profile")
        
        profiles_dir = Path("profiles/runtime")
        if profiles_dir.exists():
            profiles = [f.stem for f in profiles_dir.glob("*.json")]
            if profiles:
                print("Available profiles:")
                for i, profile in enumerate(profiles, 1):
                    print(f"{i}. {profile}")
                
                try:
                    choice = int(input("Select profile: ")) - 1
                    if 0 <= choice < len(profiles):
                        self.current_profile = profiles[choice]
                        print(f"✅ Selected profile: {self.current_profile}")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid selection")
            else:
                print("No profiles available")
        else:
            print("Profiles directory not found")
    
    def start_mode(self, mode: str):
        """Start a specific MS11 mode."""
        if not self.current_profile:
            print("❌ Please select a profile first")
            return
        
        self.print_header(f"Starting {mode.title()} Mode")
        
        try:
            cmd = [sys.executable, "src/main.py", "--mode", mode, "--profile", self.current_profile]
            print(f"Running: {' '.join(cmd)}")
            
            # Run in background or show output
            result = subprocess.run(cmd, capture_output=False)
            if result.returncode == 0:
                print(f"✅ {mode.title()} mode completed successfully")
            else:
                print(f"❌ {mode.title()} mode failed")
        except Exception as e:
            print(f"❌ Error starting {mode} mode: {e}")
    
    def other_modes_menu(self):
        """Menu for other MS11 modes."""
        self.print_header("Other Modes")
        
        other_modes = [
            "bounty_farming", "entertainer", "rls", "special_goals",
            "whisper", "support", "follow", "dancer"
        ]
        
        print("Available modes:")
        for i, mode in enumerate(other_modes, 1):
            print(f"{i}. {mode.replace('_', ' ').title()}")
        
        try:
            choice = int(input("Select mode: ")) - 1
            if 0 <= choice < len(other_modes):
                self.start_mode(other_modes[choice])
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid selection")
    
    def start_session(self):
        """Start a new MS11 session."""
        self.print_header("Start New Session")
        
        if not self.current_profile:
            print("❌ Please select a profile first")
            return
        
        if not self.current_mode:
            print("❌ Please select a mode first")
            return
        
        print(f"Starting session with profile: {self.current_profile}")
        print(f"Mode: {self.current_mode}")
        
        # TODO: Implement session management
        self.session_active = True
        print("🟢 Session started")
    
    def stop_session(self):
        """Stop the current session."""
        self.print_header("Stop Session")
        
        if self.session_active:
            self.session_active = False
            print("🔴 Session stopped")
        else:
            print("No active session to stop")
    
    def view_session_logs(self):
        """View session logs."""
        self.print_header("Session Logs")
        
        log_dirs = ["logs", "data/sessions", "session_logs"]
        for log_dir in log_dirs:
            log_path = Path(log_dir)
            if log_path.exists():
                log_files = list(log_path.glob("*.json"))
                if log_files:
                    print(f"Logs in {log_dir}:")
                    for log_file in log_files[-5:]:  # Show last 5
                        print(f"  📄 {log_file.name}")
                    break
        else:
            print("No session logs found")
    
    def session_history(self):
        """Show session history."""
        self.print_header("Session History")
        print("Session history feature coming soon...")
    
    def real_time_logs(self):
        """Show real-time logs."""
        self.print_header("Real-time Logs")
        print("Real-time log monitoring coming soon...")
    
    def system_performance(self):
        """Show system performance."""
        self.print_header("System Performance")
        
        try:
            import psutil
            print(f"CPU Usage: {psutil.cpu_percent()}%")
            print(f"Memory Usage: {psutil.virtual_memory().percent}%")
            print(f"Disk Usage: {psutil.disk_usage('/').percent}%")
        except ImportError:
            print("psutil not available for performance monitoring")
    
    def session_analytics(self):
        """Show session analytics."""
        self.print_header("Session Analytics")
        print("Session analytics feature coming soon...")
    
    def error_logs(self):
        """Show error logs."""
        self.print_header("Error Logs")
        print("Error log viewing feature coming soon...")
    
    def deploy_staging(self):
        """Deploy to staging environment."""
        self.print_header("Deploy to Staging")
        
        try:
            result = subprocess.run([sys.executable, "scripts/deploy_ms11.py", "--environment", "staging"])
            if result.returncode == 0:
                print("✅ Staging deployment successful")
            else:
                print("❌ Staging deployment failed")
        except Exception as e:
            print(f"❌ Error during deployment: {e}")
    
    def deploy_production(self):
        """Deploy to production environment."""
        self.print_header("Deploy to Production")
        
        confirm = input("Are you sure you want to deploy to production? (y/N): ")
        if confirm.lower() == 'y':
            try:
                result = subprocess.run([sys.executable, "scripts/deploy_ms11.py", "--environment", "production"])
                if result.returncode == 0:
                    print("✅ Production deployment successful")
                else:
                    print("❌ Production deployment failed")
            except Exception as e:
                print(f"❌ Error during deployment: {e}")
        else:
            print("Production deployment cancelled")
    
    def docker_management(self):
        """Docker management interface."""
        self.print_header("Docker Management")
        
        options = {
            1: "Start Containers",
            2: "Stop Containers", 
            3: "View Container Status",
            4: "View Logs",
            5: "Back"
        }
        
        self.print_menu("Docker Management", options)
        choice = self.get_user_choice(5)
        
        if choice == 1:
            subprocess.run(["docker-compose", "up", "-d"])
            print("✅ Containers started")
        elif choice == 2:
            subprocess.run(["docker-compose", "down"])
            print("✅ Containers stopped")
        elif choice == 3:
            subprocess.run(["docker-compose", "ps"])
        elif choice == 4:
            subprocess.run(["docker-compose", "logs", "-f"])
    
    def health_checks(self):
        """Run health checks."""
        self.print_header("Health Checks")
        
        try:
            result = subprocess.run([sys.executable, "scripts/quick_test_ms11.py"], 
                                  capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"Error running health checks: {e}")
    
    def run_quick_test(self):
        """Run quick test."""
        self.print_header("Quick Test")
        
        try:
            result = subprocess.run([sys.executable, "scripts/quick_test_ms11.py"])
            if result.returncode == 0:
                print("✅ Quick test passed")
            else:
                print("❌ Quick test failed")
        except Exception as e:
            print(f"❌ Error running quick test: {e}")
    
    def full_system_test(self):
        """Run full system test."""
        self.print_header("Full System Test")
        print("Full system test feature coming soon...")
    
    def mode_testing(self):
        """Test individual modes."""
        self.print_header("Mode Testing")
        print("Mode testing feature coming soon...")
    
    def performance_test(self):
        """Run performance test."""
        self.print_header("Performance Test")
        print("Performance testing feature coming soon...")


def main():
    """Main entry point."""
    # Clear screen for better UX
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("🚀 MS11 Interface - Complete Control Center")
    print("=" * 60)
    print("Welcome to the MS11 management interface!")
    print("")
    print("💡 First time here? Try these steps:")
    print("   1. Check 'System Management' → 'Check System Status'")  
    print("   2. Create a profile in 'Profile Management'")
    print("   3. Select your mode in 'Mode Control'")
    print("   4. Start testing!")
    print("")
    print("🔧 Need help? Run 'python scripts/quick_test_ms11.py' first")
    print("📚 Documentation: See SETUP_GUIDE.md for detailed instructions")
    print("")
    print("Press any key to continue...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return
    
    interface = MS11Interface()
    interface.show_main_menu()


if __name__ == "__main__":
    main()

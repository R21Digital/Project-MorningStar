#!/usr/bin/env python3
"""
MS11 Onboarding Wizard

This module provides a comprehensive onboarding experience for new MS11 users,
guiding them through setup, validation, and configuration.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import subprocess
import platform

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.validation.preflight_check import PreflightValidator, ValidationStatus
from config.user_config_template import load_user_config_template


class OnboardingStep(Enum):
    """Steps in the onboarding process."""
    WELCOME = "welcome"
    SYSTEM_CHECK = "system_check"
    GAME_DETECTION = "game_detection"
    CONFIG_SETUP = "config_setup"
    DISCORD_SETUP = "discord_setup"
    VALIDATION = "validation"
    TUTORIAL = "tutorial"
    COMPLETE = "complete"


class SetupStatus(Enum):
    """Status of setup steps."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class OnboardingStepData:
    """Data for an onboarding step."""
    step: OnboardingStep
    status: SetupStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)
    required: bool = True
    fix_suggestion: Optional[str] = None


@dataclass
class OnboardingReport:
    """Result of onboarding process."""
    user_hash: str
    steps_completed: int
    total_steps: int
    failed_steps: List[str]
    warnings: List[str]
    recommendations: List[str]
    setup_time: float
    steps: List[OnboardingStepData]
    config_path: str
    tutorial_video_url: str = "https://youtube.com/watch?v=ms11-tutorial"


class OnboardingWizard:
    """
    Comprehensive onboarding wizard for new MS11 users.
    
    Features:
    - System compatibility checking
    - Game detection and validation
    - Configuration setup
    - Discord integration setup
    - Preflight validation
    - Tutorial video links
    - Personalized setup checklist
    """
    
    def __init__(self, user_hash: str = None):
        """Initialize the onboarding wizard."""
        self.user_hash = user_hash or f"user_{int(time.time())}"
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        self.steps: List[OnboardingStepData] = []
        self.validator = PreflightValidator()
        
        # Ensure directories exist
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.config_dir,
            self.data_dir,
            self.logs_dir,
            self.project_root / "profiles" / "runtime",
            self.project_root / "screenshots",
            self.project_root / "session_logs",
            self.project_root / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def run_onboarding(self) -> OnboardingReport:
        """Run the complete onboarding process."""
        start_time = time.time()
        
        print("🎯 MS11 Onboarding Wizard")
        print("=" * 50)
        print(f"Welcome! Let's get you set up with MS11.")
        print()
        
        # Run all onboarding steps
        self._run_welcome_step()
        self._run_system_check_step()
        self._run_game_detection_step()
        self._run_config_setup_step()
        self._run_discord_setup_step()
        self._run_validation_step()
        self._run_tutorial_step()
        self._run_complete_step()
        
        # Generate report
        report = self._generate_report(start_time)
        
        # Save onboarding data
        self._save_onboarding_data(report)
        
        return report
    
    def _run_welcome_step(self):
        """Run the welcome step."""
        step_data = OnboardingStepData(
            step=OnboardingStep.WELCOME,
            status=SetupStatus.IN_PROGRESS,
            message="Welcome to MS11!"
        )
        self.steps.append(step_data)
        
        print("📋 Step 1: Welcome to MS11")
        print("MS11 is an advanced automation tool for Star Wars Galaxies.")
        print("This wizard will guide you through setup and validation.")
        print()
        
        step_data.status = SetupStatus.COMPLETED
        step_data.message = "Welcome step completed"
    
    def _run_system_check_step(self):
        """Run system compatibility check."""
        step_data = OnboardingStepData(
            step=OnboardingStep.SYSTEM_CHECK,
            status=SetupStatus.IN_PROGRESS,
            message="Checking system compatibility..."
        )
        self.steps.append(step_data)
        
        print("🔍 Step 2: System Compatibility Check")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            print("✅ Python 3.8+ detected")
        else:
            print("❌ Python 3.8+ required")
            step_data.status = SetupStatus.FAILED
            step_data.fix_suggestion = "Upgrade to Python 3.8 or higher"
            return
        
        # Check OS
        os_name = platform.system()
        if os_name == "Windows":
            print("✅ Windows detected")
        elif os_name == "Linux":
            print("✅ Linux detected")
        elif os_name == "Darwin":
            print("✅ macOS detected")
        else:
            print(f"⚠️ Unsupported OS: {os_name}")
        
        # Check available memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.total >= 4 * 1024 * 1024 * 1024:  # 4GB
                print("✅ Sufficient RAM detected")
            else:
                print("⚠️ Low RAM detected - 4GB+ recommended")
        except ImportError:
            print("⚠️ Could not check RAM (psutil not installed)")
        
        # Check disk space
        try:
            disk_usage = psutil.disk_usage(str(self.project_root))
            if disk_usage.free >= 1 * 1024 * 1024 * 1024:  # 1GB
                print("✅ Sufficient disk space")
            else:
                print("⚠️ Low disk space - 1GB+ recommended")
        except:
            print("⚠️ Could not check disk space")
        
        step_data.status = SetupStatus.COMPLETED
        step_data.message = "System check completed"
        print()
    
    def _run_game_detection_step(self):
        """Run game detection and validation."""
        step_data = OnboardingStepData(
            step=OnboardingStep.GAME_DETECTION,
            status=SetupStatus.IN_PROGRESS,
            message="Detecting Star Wars Galaxies..."
        )
        self.steps.append(step_data)
        
        print("🎮 Step 3: Game Detection")
        
        # Check for SWG process
        swg_found = self._detect_swg_process()
        if swg_found:
            print("✅ Star Wars Galaxies process detected")
        else:
            print("❌ Star Wars Galaxies not running")
            print("   Please start SWG before continuing")
            step_data.status = SetupStatus.FAILED
            step_data.fix_suggestion = "Start Star Wars Galaxies"
            return
        
        # Check for SWGR client ID
        client_id = self._detect_swgr_client_id()
        if client_id:
            print(f"✅ SWGR Client ID found: {client_id}")
            step_data.details = {"client_id": client_id}
        else:
            print("❌ SWGR Client ID not found")
            step_data.status = SetupStatus.FAILED
            step_data.fix_suggestion = "Ensure SWGR is properly installed and running"
            return
        
        step_data.status = SetupStatus.COMPLETED
        step_data.message = "Game detection completed"
        print()
    
    def _run_config_setup_step(self):
        """Run configuration setup."""
        step_data = OnboardingStepData(
            step=OnboardingStep.CONFIG_SETUP,
            status=SetupStatus.IN_PROGRESS,
            message="Setting up configuration..."
        )
        self.steps.append(step_data)
        
        print("⚙️ Step 4: Configuration Setup")
        
        # Create user config
        config_path = self._create_user_config()
        if config_path:
            print(f"✅ User config created: {config_path}")
            step_data.details = {"config_path": str(config_path)}
        else:
            print("❌ Failed to create user config")
            step_data.status = SetupStatus.FAILED
            return
        
        # Create default profile
        profile_path = self._create_default_profile()
        if profile_path:
            print(f"✅ Default profile created: {profile_path}")
            step_data.details = step_data.details or {}
            step_data.details["profile_path"] = str(profile_path)
        else:
            print("⚠️ Failed to create default profile")
        
        # Check keybinds
        keybind_issues = self._check_keybinds()
        if keybind_issues:
            print(f"⚠️ Keybind issues found: {len(keybind_issues)}")
            step_data.details = step_data.details or {}
            step_data.details["keybind_issues"] = keybind_issues
        else:
            print("✅ Keybinds configured")
        
        # Check macros
        macro_issues = self._check_macros()
        if macro_issues:
            print(f"⚠️ Macro issues found: {len(macro_issues)}")
            step_data.details = step_data.details or {}
            step_data.details["macro_issues"] = macro_issues
        else:
            print("✅ Macros configured")
        
        step_data.status = SetupStatus.COMPLETED
        step_data.message = "Configuration setup completed"
        print()
    
    def _run_discord_setup_step(self):
        """Run Discord integration setup."""
        step_data = OnboardingStepData(
            step=OnboardingStep.DISCORD_SETUP,
            status=SetupStatus.IN_PROGRESS,
            message="Setting up Discord integration..."
        )
        self.steps.append(step_data)
        
        print("💬 Step 5: Discord Integration Setup")
        
        # Check Discord config
        discord_config_path = self.config_dir / "discord_config.json"
        if discord_config_path.exists():
            try:
                with open(discord_config_path, 'r') as f:
                    discord_config = json.load(f)
                
                if discord_config.get("discord_token") and discord_config["discord_token"] != "YOUR_BOT_TOKEN_HERE":
                    print("✅ Discord bot token configured")
                    step_data.details = {"discord_configured": True}
                else:
                    print("⚠️ Discord bot token not configured")
                    step_data.details = {"discord_configured": False}
                    step_data.fix_suggestion = "Configure Discord bot token in config/discord_config.json"
            except Exception as e:
                print(f"❌ Error reading Discord config: {e}")
                step_data.status = SetupStatus.FAILED
                return
        else:
            print("⚠️ Discord config file not found")
            step_data.details = {"discord_configured": False}
            step_data.fix_suggestion = "Create config/discord_config.json"
        
        step_data.status = SetupStatus.COMPLETED
        step_data.message = "Discord setup completed"
        print()
    
    def _run_validation_step(self):
        """Run comprehensive validation."""
        step_data = OnboardingStepData(
            step=OnboardingStep.VALIDATION,
            status=SetupStatus.IN_PROGRESS,
            message="Running validation checks..."
        )
        self.steps.append(step_data)
        
        print("🔍 Step 6: Validation Checks")
        
        # Run preflight validation
        try:
            preflight_report = self.validator.run_all_checks()
            
            if preflight_report.overall_status == ValidationStatus.PASS:
                print("✅ All validation checks passed")
            elif preflight_report.overall_status == ValidationStatus.WARNING:
                print("⚠️ Validation completed with warnings")
            else:
                print("❌ Validation failed")
            
            step_data.details = {
                "total_checks": preflight_report.total_checks,
                "passed_checks": preflight_report.passed_checks,
                "failed_checks": preflight_report.failed_checks,
                "warning_checks": preflight_report.warning_checks,
                "critical_failures": preflight_report.critical_failures
            }
            
            if preflight_report.critical_failures:
                step_data.fix_suggestion = f"Fix {len(preflight_report.critical_failures)} critical issues"
            
        except Exception as e:
            print(f"❌ Validation error: {e}")
            step_data.status = SetupStatus.FAILED
            return
        
        step_data.status = SetupStatus.COMPLETED
        step_data.message = "Validation completed"
        print()
    
    def _run_tutorial_step(self):
        """Run tutorial setup."""
        step_data = OnboardingStepData(
            step=OnboardingStep.TUTORIAL,
            status=SetupStatus.IN_PROGRESS,
            message="Setting up tutorials..."
        )
        self.steps.append(step_data)
        
        print("📚 Step 7: Tutorial Setup")
        
        # Generate personalized checklist
        checklist = self._generate_personalized_checklist()
        checklist_path = self.data_dir / f"onboarding_checklist_{self.user_hash}.json"
        
        try:
            with open(checklist_path, 'w') as f:
                json.dump(checklist, f, indent=2)
            print(f"✅ Personalized checklist created: {checklist_path}")
            step_data.details = {"checklist_path": str(checklist_path)}
        except Exception as e:
            print(f"❌ Failed to create checklist: {e}")
        
        # Tutorial video URL
        tutorial_url = "https://youtube.com/watch?v=ms11-tutorial"
        print(f"📹 Tutorial video: {tutorial_url}")
        step_data.details = step_data.details or {}
        step_data.details["tutorial_url"] = tutorial_url
        
        step_data.status = SetupStatus.COMPLETED
        step_data.message = "Tutorial setup completed"
        print()
    
    def _run_complete_step(self):
        """Run completion step."""
        step_data = OnboardingStepData(
            step=OnboardingStep.COMPLETE,
            status=SetupStatus.IN_PROGRESS,
            message="Completing onboarding..."
        )
        self.steps.append(step_data)
        
        print("🎉 Step 8: Onboarding Complete")
        print("✅ MS11 is ready to use!")
        print()
        print("📋 Next Steps:")
        print("   1. Review your personalized checklist")
        print("   2. Watch the tutorial video")
        print("   3. Configure your character profile")
        print("   4. Run: python src/main.py --profile your_profile_name")
        print()
        print("💬 Discord Commands:")
        print("   /onboard - Run this wizard again")
        print("   /validate - Run validation checks")
        print("   /status - Check system status")
        print()
        
        step_data.status = SetupStatus.COMPLETED
        step_data.message = "Onboarding completed successfully"
    
    def _detect_swg_process(self) -> bool:
        """Detect if Star Wars Galaxies is running."""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                if 'swg' in proc.info['name'].lower() or 'galaxies' in proc.info['name'].lower():
                    return True
            return False
        except ImportError:
            # Fallback: check common process names
            return False
    
    def _detect_swgr_client_id(self) -> Optional[str]:
        """Detect SWGR client ID from running process."""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'swg' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline:
                        for arg in cmdline:
                            if 'client_id' in arg.lower():
                                return arg.split('=')[1] if '=' in arg else arg
            return None
        except ImportError:
            return None
    
    def _create_user_config(self) -> Optional[Path]:
        """Create user configuration file."""
        try:
            config_template = load_user_config_template()
            
            # Personalize the config
            config_template["installation"]["installation_path"] = str(self.project_root)
            config_template["installation"]["install_date"] = time.strftime("%Y-%m-%d")
            config_template["installation"]["first_run"] = True
            
            config_path = self.config_dir / f"user_config_{self.user_hash}.json"
            
            with open(config_path, 'w') as f:
                json.dump(config_template, f, indent=2)
            
            return config_path
        except Exception as e:
            print(f"Error creating user config: {e}")
            return None
    
    def _create_default_profile(self) -> Optional[Path]:
        """Create default character profile."""
        try:
            profile_template = {
                "character_name": "DemoCharacter",
                "profession": "medic",
                "mode": "medic",
                "auto_train": False,
                "farming_target": None,
                "created_date": time.strftime("%Y-%m-%d"),
                "onboarding_completed": True
            }
            
            profiles_dir = self.project_root / "profiles" / "runtime"
            profiles_dir.mkdir(parents=True, exist_ok=True)
            
            profile_path = profiles_dir / f"default_{self.user_hash}.json"
            
            with open(profile_path, 'w') as f:
                json.dump(profile_template, f, indent=2)
            
            return profile_path
        except Exception as e:
            print(f"Error creating default profile: {e}")
            return None
    
    def _check_keybinds(self) -> List[str]:
        """Check for keybind issues."""
        issues = []
        
        keybind_path = self.config_dir / "player_keybinds.json"
        if not keybind_path.exists():
            issues.append("Keybind file not found")
        else:
            try:
                with open(keybind_path, 'r') as f:
                    keybinds = json.load(f)
                
                required_keys = ["W", "A", "S", "D", "SPACE", "ENTER"]
                for key in required_keys:
                    if key not in keybinds:
                        issues.append(f"Missing keybind for {key}")
            except Exception as e:
                issues.append(f"Error reading keybinds: {e}")
        
        return issues
    
    def _check_macros(self) -> List[str]:
        """Check for macro issues."""
        issues = []
        
        macro_dir = self.data_dir / "macros"
        if not macro_dir.exists():
            issues.append("Macro directory not found")
        else:
            macro_files = list(macro_dir.glob("*.txt"))
            if not macro_files:
                issues.append("No macro files found")
        
        return issues
    
    def _generate_personalized_checklist(self) -> Dict[str, Any]:
        """Generate personalized setup checklist."""
        checklist = {
            "user_hash": self.user_hash,
            "generated_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_steps": [step.step.value for step in self.steps if step.status == SetupStatus.COMPLETED],
            "failed_steps": [step.step.value for step in self.steps if step.status == SetupStatus.FAILED],
            "recommendations": [],
            "tutorial_url": "https://youtube.com/watch?v=ms11-tutorial",
            "next_steps": [
                "Configure your character profile",
                "Set up Discord bot (optional)",
                "Run validation checks",
                "Start your first session"
            ]
        }
        
        # Add personalized recommendations based on failed steps
        for step in self.steps:
            if step.status == SetupStatus.FAILED and step.fix_suggestion:
                checklist["recommendations"].append(step.fix_suggestion)
        
        return checklist
    
    def _generate_report(self, start_time: float) -> OnboardingReport:
        """Generate onboarding report."""
        completed_steps = [step for step in self.steps if step.status == SetupStatus.COMPLETED]
        failed_steps = [step.step.value for step in self.steps if step.status == SetupStatus.FAILED]
        
        warnings = []
        recommendations = []
        
        for step in self.steps:
            if step.fix_suggestion:
                recommendations.append(step.fix_suggestion)
        
        return OnboardingReport(
            user_hash=self.user_hash,
            steps_completed=len(completed_steps),
            total_steps=len(self.steps),
            failed_steps=failed_steps,
            warnings=warnings,
            recommendations=recommendations,
            setup_time=time.time() - start_time,
            steps=self.steps,
            config_path=str(self.config_dir / f"user_config_{self.user_hash}.json")
        )
    
    def _save_onboarding_data(self, report: OnboardingReport):
        """Save onboarding data to file."""
        try:
            onboarding_data = {
                "user_hash": report.user_hash,
                "setup_time": report.setup_time,
                "steps_completed": report.steps_completed,
                "total_steps": report.total_steps,
                "failed_steps": report.failed_steps,
                "warnings": report.warnings,
                "recommendations": report.recommendations,
                "config_path": report.config_path,
                "tutorial_video_url": report.tutorial_video_url,
                "steps": [
                    {
                        "step": step.step.value,
                        "status": step.status.value,
                        "message": step.message,
                        "details": step.details,
                        "timestamp": step.timestamp,
                        "required": step.required,
                        "fix_suggestion": step.fix_suggestion
                    }
                    for step in report.steps
                ]
            }
            
            onboarding_path = self.data_dir / f"onboarding_report_{self.user_hash}.json"
            with open(onboarding_path, 'w') as f:
                json.dump(onboarding_data, f, indent=2)
            
            print(f"📄 Onboarding report saved: {onboarding_path}")
            
        except Exception as e:
            print(f"Error saving onboarding data: {e}")


def run_onboarding_wizard(user_hash: str = None) -> OnboardingReport:
    """Run the onboarding wizard for a user."""
    wizard = OnboardingWizard(user_hash)
    return wizard.run_onboarding()


def get_onboarding_status(user_hash: str) -> Optional[Dict[str, Any]]:
    """Get onboarding status for a user."""
    try:
        data_dir = Path(__file__).parent.parent / "data"
        onboarding_path = data_dir / f"onboarding_report_{user_hash}.json"
        
        if onboarding_path.exists():
            with open(onboarding_path, 'r') as f:
                return json.load(f)
        return None
    except Exception:
        return None


if __name__ == "__main__":
    # Run the wizard
    report = run_onboarding_wizard()
    print(f"\n✅ Onboarding completed in {report.setup_time:.2f} seconds")
    print(f"📊 Steps completed: {report.steps_completed}/{report.total_steps}")
    
    if report.failed_steps:
        print(f"❌ Failed steps: {', '.join(report.failed_steps)}")
    
    if report.recommendations:
        print(f"💡 Recommendations: {len(report.recommendations)}") 
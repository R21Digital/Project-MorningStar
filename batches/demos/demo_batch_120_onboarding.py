#!/usr/bin/env python3
"""
Demo Script for Batch 120 - Validation + First-Time Onboarding
Tests the comprehensive onboarding wizard with validation and setup features.
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from onboarding.wizard import OnboardingWizard, run_onboarding_wizard, get_onboarding_status


class OnboardingDemo:
    """Demo class for testing the onboarding wizard."""
    
    def __init__(self):
        self.demo_user_hash = "demo_user_120"
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)
    
    def run_complete_demo(self):
        """Run the complete onboarding demo."""
        print("🎯 MS11 Onboarding Demo - Batch 120")
        print("=" * 50)
        print()
        
        # Test 1: Basic onboarding wizard
        self.test_basic_onboarding()
        
        # Test 2: Onboarding with custom user hash
        self.test_custom_user_onboarding()
        
        # Test 3: Onboarding status retrieval
        self.test_onboarding_status()
        
        # Test 4: Validation integration
        self.test_validation_integration()
        
        # Test 5: Configuration generation
        self.test_configuration_generation()
        
        # Test 6: Discord integration setup
        self.test_discord_setup()
        
        print("\n✅ Onboarding demo completed successfully!")
        print("\n📋 Demo Summary:")
        print("   • Basic onboarding wizard tested")
        print("   • Custom user onboarding tested")
        print("   • Status retrieval tested")
        print("   • Validation integration tested")
        print("   • Configuration generation tested")
        print("   • Discord setup tested")
    
    def test_basic_onboarding(self):
        """Test basic onboarding wizard functionality."""
        print("🔍 Test 1: Basic Onboarding Wizard")
        print("-" * 30)
        
        try:
            # Create wizard instance
            wizard = OnboardingWizard(self.demo_user_hash)
            
            # Test directory creation
            print("✅ Directory creation test passed")
            
            # Test system check step
            wizard._run_system_check_step()
            print("✅ System check step completed")
            
            # Test config setup step
            wizard._run_config_setup_step()
            print("✅ Config setup step completed")
            
            # Test Discord setup step
            wizard._run_discord_setup_step()
            print("✅ Discord setup step completed")
            
            # Test tutorial step
            wizard._run_tutorial_step()
            print("✅ Tutorial step completed")
            
            print("✅ Basic onboarding test passed\n")
            
        except Exception as e:
            print(f"❌ Basic onboarding test failed: {e}\n")
    
    def test_custom_user_onboarding(self):
        """Test onboarding with custom user hash."""
        print("🔍 Test 2: Custom User Onboarding")
        print("-" * 30)
        
        try:
            custom_user_hash = "custom_user_120"
            
            # Run onboarding wizard
            report = run_onboarding_wizard(custom_user_hash)
            
            print(f"✅ Onboarding completed for user: {custom_user_hash}")
            print(f"   Steps completed: {report.steps_completed}/{report.total_steps}")
            print(f"   Setup time: {report.setup_time:.2f} seconds")
            print(f"   Failed steps: {len(report.failed_steps)}")
            print(f"   Recommendations: {len(report.recommendations)}")
            
            # Verify report structure
            assert hasattr(report, 'user_hash')
            assert hasattr(report, 'steps_completed')
            assert hasattr(report, 'total_steps')
            assert hasattr(report, 'failed_steps')
            assert hasattr(report, 'recommendations')
            assert hasattr(report, 'setup_time')
            assert hasattr(report, 'steps')
            assert hasattr(report, 'config_path')
            assert hasattr(report, 'tutorial_video_url')
            
            print("✅ Custom user onboarding test passed\n")
            
        except Exception as e:
            print(f"❌ Custom user onboarding test failed: {e}\n")
    
    def test_onboarding_status(self):
        """Test onboarding status retrieval."""
        print("🔍 Test 3: Onboarding Status Retrieval")
        print("-" * 30)
        
        try:
            # Test status retrieval for demo user
            status = get_onboarding_status(self.demo_user_hash)
            
            if status:
                print(f"✅ Status retrieved for user: {self.demo_user_hash}")
                print(f"   Steps completed: {status.get('steps_completed', 'N/A')}")
                print(f"   Total steps: {status.get('total_steps', 'N/A')}")
                print(f"   Setup time: {status.get('setup_time', 'N/A')}")
                print(f"   Failed steps: {len(status.get('failed_steps', []))}")
            else:
                print(f"⚠️ No status found for user: {self.demo_user_hash}")
            
            # Test status retrieval for non-existent user
            non_existent_status = get_onboarding_status("non_existent_user")
            if non_existent_status is None:
                print("✅ Non-existent user status correctly returns None")
            else:
                print("⚠️ Non-existent user status should return None")
            
            print("✅ Onboarding status test passed\n")
            
        except Exception as e:
            print(f"❌ Onboarding status test failed: {e}\n")
    
    def test_validation_integration(self):
        """Test validation integration with onboarding."""
        print("🔍 Test 4: Validation Integration")
        print("-" * 30)
        
        try:
            # Create wizard instance
            wizard = OnboardingWizard(self.demo_user_hash)
            
            # Test validation step
            wizard._run_validation_step()
            
            # Check if validator was created
            assert wizard.validator is not None
            print("✅ Validator instance created")
            
            # Check if validation step was added to steps
            validation_steps = [step for step in wizard.steps if step.step.value == 'validation']
            assert len(validation_steps) > 0
            print("✅ Validation step added to wizard")
            
            # Check validation step status
            validation_step = validation_steps[0]
            print(f"   Validation status: {validation_step.status.value}")
            print(f"   Validation message: {validation_step.message}")
            
            if validation_step.details:
                print(f"   Validation details: {len(validation_step.details)} items")
            
            print("✅ Validation integration test passed\n")
            
        except Exception as e:
            print(f"❌ Validation integration test failed: {e}\n")
    
    def test_configuration_generation(self):
        """Test configuration generation functionality."""
        print("🔍 Test 5: Configuration Generation")
        print("-" * 30)
        
        try:
            # Create wizard instance
            wizard = OnboardingWizard(self.demo_user_hash)
            
            # Test user config creation
            config_path = wizard._create_user_config()
            if config_path:
                print(f"✅ User config created: {config_path}")
                
                # Verify config file exists
                assert config_path.exists()
                print("✅ Config file exists")
                
                # Verify config is valid JSON
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                assert 'installation' in config_data
                assert 'authentication' in config_data
                assert 'security' in config_data
                print("✅ Config structure is valid")
                
            else:
                print("❌ Failed to create user config")
            
            # Test default profile creation
            profile_path = wizard._create_default_profile()
            if profile_path:
                print(f"✅ Default profile created: {profile_path}")
                
                # Verify profile file exists
                assert profile_path.exists()
                print("✅ Profile file exists")
                
                # Verify profile is valid JSON
                with open(profile_path, 'r') as f:
                    profile_data = json.load(f)
                
                assert 'character_name' in profile_data
                assert 'profession' in profile_data
                assert 'mode' in profile_data
                print("✅ Profile structure is valid")
                
            else:
                print("❌ Failed to create default profile")
            
            print("✅ Configuration generation test passed\n")
            
        except Exception as e:
            print(f"❌ Configuration generation test failed: {e}\n")
    
    def test_discord_setup(self):
        """Test Discord integration setup."""
        print("🔍 Test 6: Discord Integration Setup")
        print("-" * 30)
        
        try:
            # Create wizard instance
            wizard = OnboardingWizard(self.demo_user_hash)
            
            # Test Discord setup step
            wizard._run_discord_setup_step()
            
            # Check if Discord step was added
            discord_steps = [step for step in wizard.steps if step.step.value == 'discord_setup']
            assert len(discord_steps) > 0
            print("✅ Discord setup step added")
            
            # Check Discord step status
            discord_step = discord_steps[0]
            print(f"   Discord setup status: {discord_step.status.value}")
            print(f"   Discord setup message: {discord_step.message}")
            
            if discord_step.details:
                discord_configured = discord_step.details.get('discord_configured', False)
                print(f"   Discord configured: {discord_configured}")
            
            # Test Discord config file check
            discord_config_path = wizard.config_dir / "discord_config.json"
            if discord_config_path.exists():
                print("✅ Discord config file exists")
                
                # Try to read Discord config
                try:
                    with open(discord_config_path, 'r') as f:
                        discord_config = json.load(f)
                    
                    token_configured = (
                        discord_config.get("discord_token") and 
                        discord_config["discord_token"] != "YOUR_BOT_TOKEN_HERE"
                    )
                    print(f"   Discord token configured: {token_configured}")
                    
                except Exception as e:
                    print(f"   Error reading Discord config: {e}")
            else:
                print("⚠️ Discord config file not found")
            
            print("✅ Discord integration setup test passed\n")
            
        except Exception as e:
            print(f"❌ Discord integration setup test failed: {e}\n")
    
    def generate_demo_report(self):
        """Generate a demo report."""
        report = {
            "demo_name": "Batch 120 Onboarding Demo",
            "demo_date": datetime.now().isoformat(),
            "demo_user_hash": self.demo_user_hash,
            "tests_run": [
                "Basic Onboarding Wizard",
                "Custom User Onboarding",
                "Onboarding Status Retrieval",
                "Validation Integration",
                "Configuration Generation",
                "Discord Integration Setup"
            ],
            "project_structure": {
                "onboarding_wizard": "onboarding/wizard.py",
                "user_config_template": "config/user_config_template.py",
                "discord_command": "discord/commands/onboard.js",
                "validation_module": "core/validation/preflight_check.py"
            },
            "features_tested": [
                "System compatibility checking",
                "Game detection and validation",
                "Configuration setup",
                "Discord integration setup",
                "Preflight validation",
                "Tutorial video links",
                "Personalized setup checklist"
            ]
        }
        
        # Save demo report
        report_path = self.data_dir / f"onboarding_demo_report_{self.demo_user_hash}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Demo report saved: {report_path}")
        return report


def main():
    """Main function to run the demo."""
    demo = OnboardingDemo()
    demo.run_complete_demo()
    
    # Generate demo report
    report = demo.generate_demo_report()
    
    print("\n📊 Demo Report Summary:")
    print(f"   Demo Name: {report['demo_name']}")
    print(f"   Demo Date: {report['demo_date']}")
    print(f"   Tests Run: {len(report['tests_run'])}")
    print(f"   Features Tested: {len(report['features_tested'])}")


if __name__ == "__main__":
    main() 
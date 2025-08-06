#!/usr/bin/env python3
"""
Test Script for Batch 120 - Validation + First-Time Onboarding
Comprehensive testing of the onboarding wizard features.
"""

import json
import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from onboarding.wizard import (
    OnboardingWizard, 
    OnboardingStep, 
    SetupStatus, 
    OnboardingStepData, 
    OnboardingReport,
    run_onboarding_wizard,
    get_onboarding_status
)
from config.user_config_template import load_user_config_template, create_user_config, save_user_config


class TestOnboardingWizard(unittest.TestCase):
    """Test class for the onboarding wizard."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_user_hash = "test_user_120"
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create test directory structure
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        self.profiles_dir = self.project_root / "profiles" / "runtime"
        
        for directory in [self.config_dir, self.data_dir, self.logs_dir, self.profiles_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
    
    @patch('onboarding.wizard.Path')
    def test_wizard_initialization(self, mock_path):
        """Test wizard initialization."""
        mock_path.return_value.parent.parent = self.project_root
        
        wizard = OnboardingWizard(self.test_user_hash)
        
        self.assertEqual(wizard.user_hash, self.test_user_hash)
        self.assertIsNotNone(wizard.validator)
        self.assertEqual(len(wizard.steps), 0)
    
    def test_directory_creation(self):
        """Test directory creation functionality."""
        wizard = OnboardingWizard(self.test_user_hash)
        
        # Test that directories are created
        expected_dirs = [
            self.config_dir,
            self.data_dir,
            self.logs_dir,
            self.profiles_dir,
            self.project_root / "screenshots",
            self.project_root / "session_logs",
            self.project_root / "backups"
        ]
        
        for directory in expected_dirs:
            self.assertTrue(directory.exists())
    
    @patch('sys.version_info')
    def test_system_check_step(self, mock_version_info):
        """Test system check step."""
        # Mock Python version
        mock_version_info.major = 3
        mock_version_info.minor = 8
        
        wizard = OnboardingWizard(self.test_user_hash)
        wizard._run_system_check_step()
        
        # Check that step was added
        system_steps = [step for step in wizard.steps if step.step == OnboardingStep.SYSTEM_CHECK]
        self.assertEqual(len(system_steps), 1)
        
        system_step = system_steps[0]
        self.assertEqual(system_step.status, SetupStatus.COMPLETED)
        self.assertIn("System check completed", system_step.message)
    
    @patch('onboarding.wizard.OnboardingWizard._detect_swg_process')
    @patch('onboarding.wizard.OnboardingWizard._detect_swgr_client_id')
    def test_game_detection_step(self, mock_client_id, mock_swg_process):
        """Test game detection step."""
        # Mock successful game detection
        mock_swg_process.return_value = True
        mock_client_id.return_value = "test_client_id"
        
        wizard = OnboardingWizard(self.test_user_hash)
        wizard._run_game_detection_step()
        
        # Check that step was added
        game_steps = [step for step in wizard.steps if step.step == OnboardingStep.GAME_DETECTION]
        self.assertEqual(len(game_steps), 1)
        
        game_step = game_steps[0]
        self.assertEqual(game_step.status, SetupStatus.COMPLETED)
        self.assertIn("Game detection completed", game_step.message)
        self.assertEqual(game_step.details["client_id"], "test_client_id")
    
    def test_config_setup_step(self):
        """Test configuration setup step."""
        wizard = OnboardingWizard(self.test_user_hash)
        wizard._run_config_setup_step()
        
        # Check that step was added
        config_steps = [step for step in wizard.steps if step.step == OnboardingStep.CONFIG_SETUP]
        self.assertEqual(len(config_steps), 1)
        
        config_step = config_steps[0]
        self.assertEqual(config_step.status, SetupStatus.COMPLETED)
        self.assertIn("Configuration setup completed", config_step.message)
        
        # Check that config file was created
        config_path = self.config_dir / f"user_config_{self.test_user_hash}.json"
        self.assertTrue(config_path.exists())
        
        # Check that profile was created
        profile_path = self.profiles_dir / f"default_{self.test_user_hash}.json"
        self.assertTrue(profile_path.exists())
    
    def test_discord_setup_step(self):
        """Test Discord setup step."""
        # Create mock Discord config
        discord_config = {
            "discord_token": "YOUR_BOT_TOKEN_HERE",
            "relay_mode": "notify",
            "target_user_id": 0
        }
        
        discord_config_path = self.config_dir / "discord_config.json"
        with open(discord_config_path, 'w') as f:
            json.dump(discord_config, f)
        
        wizard = OnboardingWizard(self.test_user_hash)
        wizard._run_discord_setup_step()
        
        # Check that step was added
        discord_steps = [step for step in wizard.steps if step.step == OnboardingStep.DISCORD_SETUP]
        self.assertEqual(len(discord_steps), 1)
        
        discord_step = discord_steps[0]
        self.assertEqual(discord_step.status, SetupStatus.COMPLETED)
        self.assertIn("Discord setup completed", discord_step.message)
        self.assertFalse(discord_step.details["discord_configured"])
    
    @patch('onboarding.wizard.PreflightValidator')
    def test_validation_step(self, mock_validator_class):
        """Test validation step."""
        # Mock preflight validator
        mock_validator = MagicMock()
        mock_report = MagicMock()
        mock_report.overall_status.value = "pass"
        mock_report.total_checks = 10
        mock_report.passed_checks = 10
        mock_report.failed_checks = 0
        mock_report.warning_checks = 0
        mock_report.critical_failures = []
        mock_validator.run_all_checks.return_value = mock_report
        mock_validator_class.return_value = mock_validator
        
        wizard = OnboardingWizard(self.test_user_hash)
        wizard._run_validation_step()
        
        # Check that step was added
        validation_steps = [step for step in wizard.steps if step.step == OnboardingStep.VALIDATION]
        self.assertEqual(len(validation_steps), 1)
        
        validation_step = validation_steps[0]
        self.assertEqual(validation_step.status, SetupStatus.COMPLETED)
        self.assertIn("Validation completed", validation_step.message)
    
    def test_tutorial_step(self):
        """Test tutorial step."""
        wizard = OnboardingWizard(self.test_user_hash)
        wizard._run_tutorial_step()
        
        # Check that step was added
        tutorial_steps = [step for step in wizard.steps if step.step == OnboardingStep.TUTORIAL]
        self.assertEqual(len(tutorial_steps), 1)
        
        tutorial_step = tutorial_steps[0]
        self.assertEqual(tutorial_step.status, SetupStatus.COMPLETED)
        self.assertIn("Tutorial setup completed", tutorial_step.message)
        
        # Check that checklist was created
        checklist_path = self.data_dir / f"onboarding_checklist_{self.test_user_hash}.json"
        self.assertTrue(checklist_path.exists())
    
    def test_complete_step(self):
        """Test completion step."""
        wizard = OnboardingWizard(self.test_user_hash)
        wizard._run_complete_step()
        
        # Check that step was added
        complete_steps = [step for step in wizard.steps if step.step == OnboardingStep.COMPLETE]
        self.assertEqual(len(complete_steps), 1)
        
        complete_step = complete_steps[0]
        self.assertEqual(complete_step.status, SetupStatus.COMPLETED)
        self.assertIn("Onboarding completed successfully", complete_step.message)
    
    def test_swg_process_detection(self):
        """Test SWG process detection."""
        wizard = OnboardingWizard(self.test_user_hash)
        
        # Test without psutil (should return False)
        result = wizard._detect_swg_process()
        self.assertIsInstance(result, bool)
    
    def test_swgr_client_id_detection(self):
        """Test SWGR client ID detection."""
        wizard = OnboardingWizard(self.test_user_hash)
        
        # Test without psutil (should return None)
        result = wizard._detect_swgr_client_id()
        self.assertIsNone(result)
    
    def test_user_config_creation(self):
        """Test user configuration creation."""
        wizard = OnboardingWizard(self.test_user_hash)
        
        config_path = wizard._create_user_config()
        self.assertIsNotNone(config_path)
        self.assertTrue(config_path.exists())
        
        # Verify config structure
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        required_sections = ['installation', 'authentication', 'security', 'logging']
        for section in required_sections:
            self.assertIn(section, config_data)
    
    def test_default_profile_creation(self):
        """Test default profile creation."""
        wizard = OnboardingWizard(self.test_user_hash)
        
        profile_path = wizard._create_default_profile()
        self.assertIsNotNone(profile_path)
        self.assertTrue(profile_path.exists())
        
        # Verify profile structure
        with open(profile_path, 'r') as f:
            profile_data = json.load(f)
        
        required_fields = ['character_name', 'profession', 'mode', 'created_date']
        for field in required_fields:
            self.assertIn(field, profile_data)
    
    def test_keybind_check(self):
        """Test keybind checking."""
        wizard = OnboardingWizard(self.test_user_hash)
        
        # Test without keybind file
        issues = wizard._check_keybinds()
        self.assertIn("Keybind file not found", issues)
        
        # Create mock keybind file
        keybind_path = self.config_dir / "player_keybinds.json"
        keybinds = {"W": "forward", "A": "left", "S": "backward", "D": "right"}
        with open(keybind_path, 'w') as f:
            json.dump(keybinds, f)
        
        issues = wizard._check_keybinds()
        self.assertIn("Missing keybind for SPACE", issues)
        self.assertIn("Missing keybind for ENTER", issues)
    
    def test_macro_check(self):
        """Test macro checking."""
        wizard = OnboardingWizard(self.test_user_hash)
        
        # Test without macro directory
        issues = wizard._check_macros()
        self.assertIn("Macro directory not found", issues)
        
        # Create mock macro directory
        macro_dir = self.data_dir / "macros"
        macro_dir.mkdir(exist_ok=True)
        
        issues = wizard._check_macros()
        self.assertIn("No macro files found", issues)
        
        # Create mock macro file
        macro_file = macro_dir / "test_macro.txt"
        macro_file.write_text("test macro content")
        
        issues = wizard._check_macros()
        self.assertEqual(len(issues), 0)
    
    def test_personalized_checklist_generation(self):
        """Test personalized checklist generation."""
        wizard = OnboardingWizard(self.test_user_hash)
        
        # Add some steps to the wizard
        wizard._run_welcome_step()
        wizard._run_system_check_step()
        
        checklist = wizard._generate_personalized_checklist()
        
        required_fields = ['user_hash', 'generated_date', 'completed_steps', 'failed_steps', 'recommendations', 'tutorial_url', 'next_steps']
        for field in required_fields:
            self.assertIn(field, checklist)
        
        self.assertEqual(checklist['user_hash'], self.test_user_hash)
        self.assertIn('welcome', checklist['completed_steps'])
        self.assertIn('system_check', checklist['completed_steps'])
    
    def test_report_generation(self):
        """Test report generation."""
        wizard = OnboardingWizard(self.test_user_hash)
        
        # Add some steps
        wizard._run_welcome_step()
        wizard._run_system_check_step()
        
        start_time = datetime.now().timestamp()
        report = wizard._generate_report(start_time)
        
        self.assertIsInstance(report, OnboardingReport)
        self.assertEqual(report.user_hash, self.test_user_hash)
        self.assertEqual(report.steps_completed, 2)
        self.assertEqual(report.total_steps, 2)
        self.assertIsInstance(report.setup_time, float)
    
    def test_onboarding_data_saving(self):
        """Test onboarding data saving."""
        wizard = OnboardingWizard(self.test_user_hash)
        
        # Add some steps
        wizard._run_welcome_step()
        wizard._run_system_check_step()
        
        start_time = datetime.now().timestamp()
        report = wizard._generate_report(start_time)
        
        wizard._save_onboarding_data(report)
        
        # Check that file was saved
        onboarding_path = self.data_dir / f"onboarding_report_{self.test_user_hash}.json"
        self.assertTrue(onboarding_path.exists())
        
        # Verify saved data
        with open(onboarding_path, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['user_hash'], self.test_user_hash)
        self.assertEqual(saved_data['steps_completed'], 2)
        self.assertEqual(saved_data['total_steps'], 2)


class TestUserConfigTemplate(unittest.TestCase):
    """Test class for user config template functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
    
    def test_load_user_config_template(self):
        """Test loading user config template."""
        template = load_user_config_template()
        
        required_sections = ['installation', 'authentication', 'security', 'logging']
        for section in required_sections:
            self.assertIn(section, template)
        
        self.assertIn('install_date', template['installation'])
        self.assertIn('last_modified', template['_metadata'])
    
    def test_create_user_config(self):
        """Test creating personalized user config."""
        user_hash = "test_user"
        installation_path = "/test/path"
        
        config = create_user_config(user_hash, installation_path)
        
        self.assertEqual(config['installation']['installation_path'], installation_path)
        self.assertEqual(config['installation']['install_date'], datetime.now().strftime("%Y-%m-%d"))
        self.assertTrue(config['installation']['first_run'])
        self.assertEqual(config['_metadata']['user_hash'], user_hash)
    
    def test_save_user_config(self):
        """Test saving user config to file."""
        config = {
            "installation": {"path": "/test"},
            "authentication": {"enabled": True}
        }
        
        config_path = self.config_dir / "test_config.json"
        
        success = save_user_config(config, str(config_path))
        self.assertTrue(success)
        self.assertTrue(config_path.exists())
        
        # Verify saved config
        with open(config_path, 'r') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config, config)


class TestOnboardingFunctions(unittest.TestCase):
    """Test class for onboarding utility functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.data_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)
    
    @patch('onboarding.wizard.OnboardingWizard')
    def test_run_onboarding_wizard(self, mock_wizard_class):
        """Test running onboarding wizard."""
        # Mock wizard instance
        mock_wizard = MagicMock()
        mock_report = MagicMock()
        mock_report.user_hash = "test_user"
        mock_report.steps_completed = 8
        mock_report.total_steps = 8
        mock_report.setup_time = 30.5
        mock_wizard.run_onboarding.return_value = mock_report
        mock_wizard_class.return_value = mock_wizard
        
        report = run_onboarding_wizard("test_user")
        
        self.assertEqual(report.user_hash, "test_user")
        self.assertEqual(report.steps_completed, 8)
        self.assertEqual(report.total_steps, 8)
        self.assertEqual(report.setup_time, 30.5)
    
    def test_get_onboarding_status(self):
        """Test getting onboarding status."""
        # Test with non-existent user
        status = get_onboarding_status("non_existent_user")
        self.assertIsNone(status)
        
        # Test with existing user (mock data)
        onboarding_data = {
            "user_hash": "test_user",
            "steps_completed": 6,
            "total_steps": 8,
            "setup_time": 45.2,
            "failed_steps": [],
            "recommendations": []
        }
        
        onboarding_path = self.data_dir / "onboarding_report_test_user.json"
        with open(onboarding_path, 'w') as f:
            json.dump(onboarding_data, f)
        
        status = get_onboarding_status("test_user")
        self.assertIsNotNone(status)
        self.assertEqual(status['user_hash'], "test_user")
        self.assertEqual(status['steps_completed'], 6)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestOnboardingWizard,
        TestUserConfigTemplate,
        TestOnboardingFunctions
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print(f"\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 
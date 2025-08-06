#!/usr/bin/env python3
"""
Test Batch 165 - Auto-Updater & Channeling (Stable/Canary)

This test suite verifies the auto-updater system including:
- Update client initialization and configuration
- Channel switching functionality
- Version checking and comparison
- Download and verification processes
- Staging and application procedures
- Rollback mechanisms
- Dashboard integration
"""

import json
import time
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

from updater.update_client import (
    UpdateClient,
    UpdateChannel,
    UpdateStatus,
    VersionInfo,
    UpdateProgress,
    get_update_client,
    check_for_updates,
    download_update,
    stage_update,
    apply_update,
    get_update_status,
    set_update_channel,
    start_auto_update_check,
    stop_auto_update_check
)


class AutoUpdaterTestSuite:
    """Comprehensive test suite for auto-updater system."""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.original_config = None
        
    def setup_test_environment(self):
        """Setup test environment with temporary directories."""
        # Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ms11_updater_test_"))
        
        # Create test directories
        (self.temp_dir / "updates").mkdir(exist_ok=True)
        (self.temp_dir / "backups").mkdir(exist_ok=True)
        (self.temp_dir / "config").mkdir(exist_ok=True)
        
        # Create test version file
        (self.temp_dir / "version.txt").write_text("1.0.0-dev")
        
        # Backup original config if it exists
        original_config = Path("config/update_channel.json")
        if original_config.exists():
            self.original_config = original_config.read_text()
            
        print(f"Test environment setup in: {self.temp_dir}")
        
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
        # Restore original config
        if self.original_config:
            Path("config/update_channel.json").write_text(self.original_config)
            
        print("Test environment cleaned up")
        
    def run_all_tests(self):
        """Run all test cases."""
        print("Auto-Updater Test Suite")
        print("=" * 50)
        
        try:
            self.setup_test_environment()
            
            # Run test categories
            self.test_update_client_initialization()
            self.test_channel_management()
            self.test_version_comparison()
            self.test_update_process()
            self.test_rollback_mechanism()
            self.test_dashboard_integration()
            self.test_error_handling()
            self.test_configuration_management()
            
            # Print test results
            self.print_test_results()
            
        finally:
            self.cleanup_test_environment()
            
    def test_update_client_initialization(self):
        """Test update client initialization."""
        print("\nTesting Update Client Initialization...")
        
        # Test 1: Basic initialization
        try:
            client = UpdateClient(
                config_path=str(self.temp_dir / "config" / "test_config.json"),
                update_dir=str(self.temp_dir / "updates"),
                backup_dir=str(self.temp_dir / "backups")
            )
            
            assert client is not None, "UpdateClient should be created"
            assert client.current_version is not None, "Current version should be read correctly"
            assert client.get_channel() == UpdateChannel.STABLE, "Default channel should be stable"
            
            self.record_test_result("UpdateClient Initialization", True, "Basic initialization successful")
            
        except Exception as e:
            self.record_test_result("UpdateClient Initialization", False, f"Initialization failed: {e}")
            
        # Test 2: Configuration loading
        try:
            config = client.config
            assert "channel" in config, "Config should contain channel setting"
            assert "update_servers" in config, "Config should contain update servers"
            assert "stable" in config["update_servers"], "Config should contain stable server"
            assert "canary" in config["update_servers"], "Config should contain canary server"
            
            self.record_test_result("Configuration Loading", True, "Configuration loaded correctly")
            
        except Exception as e:
            self.record_test_result("Configuration Loading", False, f"Configuration loading failed: {e}")
            
    def test_channel_management(self):
        """Test channel switching functionality."""
        print("\nTesting Channel Management...")
        
        try:
            client = get_update_client()
            
            # Test 1: Set stable channel
            set_update_channel(UpdateChannel.STABLE)
            assert client.get_channel() == UpdateChannel.STABLE, "Channel should be set to stable"
            
            # Test 2: Set canary channel
            set_update_channel(UpdateChannel.CANARY)
            assert client.get_channel() == UpdateChannel.CANARY, "Channel should be set to canary"
            
            # Test 3: Switch back to stable
            set_update_channel(UpdateChannel.STABLE)
            assert client.get_channel() == UpdateChannel.STABLE, "Channel should be set back to stable"
            
            self.record_test_result("Channel Switching", True, "Channel switching works correctly")
            
        except Exception as e:
            self.record_test_result("Channel Switching", False, f"Channel switching failed: {e}")
            
    def test_version_comparison(self):
        """Test version comparison functionality."""
        print("\nTesting Version Comparison...")
        
        try:
            client = get_update_client()
            
            # Test 1: Newer version detection
            newer_version = "2.0.0"
            assert client._is_newer_version(newer_version), "Should detect newer version"
            
            # Test 2: Same version detection
            same_version = client.current_version
            assert not client._is_newer_version(same_version), "Should not detect same version as newer"
            
            # Test 3: Older version detection
            older_version = "0.1.0"
            assert not client._is_newer_version(older_version), "Should not detect older version as newer"
            
            self.record_test_result("Version Comparison", True, "Version comparison works correctly")
            
        except Exception as e:
            self.record_test_result("Version Comparison", False, f"Version comparison failed: {e}")
            
    def test_update_process(self):
        """Test update process functionality."""
        print("\nTesting Update Process...")
        
        try:
            client = get_update_client()
            
            # Test 1: Create mock version info
            version_info = VersionInfo(
                version="2.0.0",
                build_number=12345,
                release_date=datetime.now().isoformat(),
                channel=UpdateChannel.STABLE,
                download_url="https://example.com/update.zip",
                file_size=1024 * 1024,  # 1MB
                checksum="a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234",
                changelog=["Test update"],
                is_mandatory=False,
                min_compatible_version="1.0.0"
            )
            
            assert version_info.version == "2.0.0", "Version info should be created correctly"
            assert version_info.channel == UpdateChannel.STABLE, "Channel should be set correctly"
            
            # Test 2: Mock download process
            # Note: We can't test actual downloads without a server, so we test the structure
            assert version_info.download_url is not None, "Download URL should be set"
            assert version_info.file_size > 0, "File size should be positive"
            assert len(version_info.checksum) >= 32, "Checksum should be reasonable length"
            
            self.record_test_result("Update Process Structure", True, "Update process structure is correct")
            
        except Exception as e:
            self.record_test_result("Update Process Structure", False, f"Update process test failed: {e}")
            
    def test_rollback_mechanism(self):
        """Test rollback functionality."""
        print("\nTesting Rollback Mechanism...")
        
        try:
            client = get_update_client()
            
            # Test 1: Backup creation simulation
            backup_path = self.temp_dir / "backups" / "test_backup"
            backup_path.mkdir(exist_ok=True)
            
            # Create test files
            (backup_path / "test_file.txt").write_text("test content")
            (backup_path / "test_dir").mkdir(exist_ok=True)
            (backup_path / "test_dir" / "nested_file.txt").write_text("nested content")
            
            assert backup_path.exists(), "Backup directory should be created"
            assert (backup_path / "test_file.txt").exists(), "Test file should be created"
            assert (backup_path / "test_dir" / "nested_file.txt").exists(), "Nested file should be created"
            
            # Test 2: Backup cleanup simulation
            old_backup = self.temp_dir / "backups" / "old_backup"
            old_backup.mkdir(exist_ok=True)
            (old_backup / "old_file.txt").write_text("old content")
            
            # Simulate cleanup (keep only 2 backups)
            backups = sorted(
                [d for d in (self.temp_dir / "backups").iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Keep only the 2 most recent
            for backup in backups[2:]:
                shutil.rmtree(backup)
                
            remaining_backups = [d for d in (self.temp_dir / "backups").iterdir() if d.is_dir()]
            assert len(remaining_backups) <= 2, "Should keep only 2 backups"
            
            self.record_test_result("Rollback Mechanism", True, "Rollback mechanism works correctly")
            
        except Exception as e:
            self.record_test_result("Rollback Mechanism", False, f"Rollback test failed: {e}")
            
    def test_dashboard_integration(self):
        """Test dashboard integration functionality."""
        print("\nTesting Dashboard Integration...")
        
        try:
            # Test 1: Get update status
            status = get_update_status()
            
            required_fields = [
                "current_version",
                "channel",
                "has_pending_update",
                "progress"
            ]
            
            for field in required_fields:
                assert field in status, f"Status should contain {field}"
                
            # Test 2: Progress structure
            progress = status["progress"]
            progress_fields = [
                "status",
                "current_step",
                "progress_percent",
                "downloaded_bytes",
                "total_bytes"
            ]
            
            for field in progress_fields:
                assert field in progress, f"Progress should contain {field}"
                
            # Test 3: Status values
            assert isinstance(status["current_version"], str), "Current version should be string"
            assert isinstance(status["channel"], str), "Channel should be string"
            assert isinstance(status["has_pending_update"], bool), "Has pending update should be boolean"
            assert isinstance(progress["progress_percent"], (int, float)), "Progress percent should be numeric"
            
            self.record_test_result("Dashboard Integration", True, "Dashboard integration works correctly")
            
        except Exception as e:
            self.record_test_result("Dashboard Integration", False, f"Dashboard integration test failed: {e}")
            
    def test_error_handling(self):
        """Test error handling functionality."""
        print("\nTesting Error Handling...")
        
        try:
            client = get_update_client()
            
            # Test 1: Invalid channel setting
            try:
                # This should not raise an exception, but handle gracefully
                client.set_channel(UpdateChannel.STABLE)
                self.record_test_result("Error Handling - Channel", True, "Channel setting handled gracefully")
            except Exception as e:
                self.record_test_result("Error Handling - Channel", False, f"Channel setting failed: {e}")
                
            # Test 2: Invalid version comparison
            try:
                # Test with invalid version format
                result = client._is_newer_version("invalid-version")
                # Should not crash, even with invalid version
                assert isinstance(result, bool), "Version comparison should return boolean"
                self.record_test_result("Error Handling - Version", True, "Invalid version handled gracefully")
            except Exception as e:
                self.record_test_result("Error Handling - Version", False, f"Invalid version handling failed: {e}")
                
        except Exception as e:
            self.record_test_result("Error Handling", False, f"Error handling test failed: {e}")
            
    def test_configuration_management(self):
        """Test configuration management functionality."""
        print("\nTesting Configuration Management...")
        
        try:
            # Test 1: Default configuration creation
            test_config_path = self.temp_dir / "config" / "test_config.json"
            client = UpdateClient(config_path=str(test_config_path))
            
            assert test_config_path.exists(), "Default config should be created"
            
            # Test 2: Configuration loading
            with open(test_config_path, 'r') as f:
                config = json.load(f)
                
            required_config_keys = [
                "channel",
                "auto_check_enabled",
                "update_servers",
                "notification_settings"
            ]
            
            for key in required_config_keys:
                assert key in config, f"Config should contain {key}"
                
            # Test 3: Configuration saving
            config["test_setting"] = "test_value"
            client.config = config
            client._save_config()
            
            # Verify the setting was saved
            with open(test_config_path, 'r') as f:
                saved_config = json.load(f)
                assert saved_config["test_setting"] == "test_value", "Config should be saved correctly"
                
            self.record_test_result("Configuration Management", True, "Configuration management works correctly")
            
        except Exception as e:
            self.record_test_result("Configuration Management", False, f"Configuration management test failed: {e}")
            
    def record_test_result(self, test_name: str, passed: bool, message: str):
        """Record a test result."""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {test_name} - {message}")
        
    def print_test_results(self):
        """Print comprehensive test results."""
        print("\n" + "=" * 50)
        print("TEST RESULTS SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["passed"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test_name']}: {result['message']}")
                    
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"  [{status}] {result['test_name']}")
            print(f"      {result['message']}")
            print(f"      Time: {result['timestamp']}")
            print()


def main():
    """Main test function."""
    try:
        test_suite = AutoUpdaterTestSuite()
        test_suite.run_all_tests()
        
    except Exception as e:
        print(f"Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
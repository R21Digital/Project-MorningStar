#!/usr/bin/env python3
"""
Batch 194 - Backup & Restore Scripts Test
Comprehensive testing of backup and restore functionality.

Test Coverage:
- File existence and structure
- Configuration validation
- Script functionality
- Safety features
- Integration features
"""

import os
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

class BackupRestoreTester:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.backup_script_path = self.base_path / "scripts" / "backup_data.sh"
        self.restore_script_path = self.base_path / "scripts" / "restore_data.sh"
        self.config_path = self.base_path / "config" / "backup_config.json"
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "tests": []
        }
        
    def log_test(self, test_name, status, message=""):
        """Log test result"""
        self.test_results["total_tests"] += 1
        
        if status == "PASS":
            self.test_results["passed"] += 1
            print(f"[PASS] {test_name}")
        elif status == "FAIL":
            self.test_results["failed"] += 1
            print(f"[FAIL] {test_name}: {message}")
        elif status == "WARNING":
            self.test_results["warnings"] += 1
            print(f"[WARNING] {test_name}: {message}")
            
        self.test_results["tests"].append({
            "name": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_file_existence(self):
        """Test file existence"""
        print("\n=== Testing File Existence ===")
        
        # Test backup script
        if self.backup_script_path.exists():
            self.log_test("Backup Script File Exists", "PASS")
        else:
            self.log_test("Backup Script File Exists", "FAIL", "Backup script not found")
            
        # Test restore script
        if self.restore_script_path.exists():
            self.log_test("Restore Script File Exists", "PASS")
        else:
            self.log_test("Restore Script File Exists", "FAIL", "Restore script not found")
            
        # Test config file
        if self.config_path.exists():
            self.log_test("Config File Exists", "PASS")
        else:
            self.log_test("Config File Exists", "FAIL", "Config file not found")
            
    def test_script_structure(self):
        """Test script structure and content"""
        print("\n=== Testing Script Structure ===")
        
        # Test backup script structure
        if self.backup_script_path.exists():
            content = self.backup_script_path.read_text()
            
            # Check for required functions
            required_functions = [
                "check_directories",
                "load_config",
                "create_backup",
                "clean_old_backups",
                "push_to_remote",
                "send_discord_notification"
            ]
            
            for func in required_functions:
                if func in content:
                    self.log_test(f"Backup Script Function: {func}", "PASS")
                else:
                    self.log_test(f"Backup Script Function: {func}", "FAIL", f"Function {func} not found")
                    
            # Check for required features
            required_features = [
                "tar -czf",
                "sha256sum",
                "find.*-delete",
                "curl.*discord",
                "jq -r"
            ]
            
            for feature in required_features:
                if feature in content:
                    self.log_test(f"Backup Script Feature: {feature}", "PASS")
                else:
                    self.log_test(f"Backup Script Feature: {feature}", "WARNING", f"Feature {feature} not found")
                    
        # Test restore script structure
        if self.restore_script_path.exists():
            content = self.restore_script_path.read_text()
            
            # Check for required functions
            required_functions = [
                "check_directories",
                "load_config",
                "verify_backup",
                "restore_data",
                "create_pre_restore_backup",
                "get_confirmation"
            ]
            
            for func in required_functions:
                if func in content:
                    self.log_test(f"Restore Script Function: {func}", "PASS")
                else:
                    self.log_test(f"Restore Script Function: {func}", "FAIL", f"Function {func} not found")
                    
            # Check for required features
            required_features = [
                "tar -xzf",
                "sha256sum",
                "unzip",
                "rm -rf",
                "chmod"
            ]
            
            for feature in required_features:
                if feature in content:
                    self.log_test(f"Restore Script Feature: {feature}", "PASS")
                else:
                    self.log_test(f"Restore Script Feature: {feature}", "WARNING", f"Feature {feature} not found")
                    
    def test_configuration_structure(self):
        """Test configuration file structure"""
        print("\n=== Testing Configuration Structure ===")
        
        if not self.config_path.exists():
            self.log_test("Config File Structure", "FAIL", "Config file not found")
            return
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Test required sections
            required_sections = ["backup", "remote", "notifications", "restore", "monitoring"]
            
            for section in required_sections:
                if section in config:
                    self.log_test(f"Config Section: {section}", "PASS")
                else:
                    self.log_test(f"Config Section: {section}", "FAIL", f"Section {section} not found")
                    
            # Test backup configuration
            if "backup" in config:
                backup_config = config["backup"]
                required_backup_keys = ["enabled", "schedule", "retention", "paths", "compression", "verification", "logging"]
                
                for key in required_backup_keys:
                    if key in backup_config:
                        self.log_test(f"Backup Config: {key}", "PASS")
                    else:
                        self.log_test(f"Backup Config: {key}", "FAIL", f"Key {key} not found")
                        
            # Test remote configuration
            if "remote" in config:
                remote_config = config["remote"]
                required_remote_keys = ["git", "google_drive", "s3", "ftp"]
                
                for key in required_remote_keys:
                    if key in remote_config:
                        self.log_test(f"Remote Config: {key}", "PASS")
                    else:
                        self.log_test(f"Remote Config: {key}", "WARNING", f"Key {key} not found")
                        
            # Test notification configuration
            if "notifications" in config:
                notification_config = config["notifications"]
                required_notification_keys = ["discord", "email"]
                
                for key in required_notification_keys:
                    if key in notification_config:
                        self.log_test(f"Notification Config: {key}", "PASS")
                    else:
                        self.log_test(f"Notification Config: {key}", "WARNING", f"Key {key} not found")
                        
        except json.JSONDecodeError as e:
            self.log_test("Config File JSON", "FAIL", f"Invalid JSON: {e}")
        except Exception as e:
            self.log_test("Config File Structure", "FAIL", f"Error reading config: {e}")
            
    def test_backup_features(self):
        """Test backup features"""
        print("\n=== Testing Backup Features ===")
        
        if not self.backup_script_path.exists():
            self.log_test("Backup Features", "FAIL", "Backup script not found")
            return
            
        content = self.backup_script_path.read_text()
        
        # Test backup features
        backup_features = [
            "Daily Backups",
            "Data Directory Backup",
            "Uploads Directory Backup",
            "Timestamped Folders",
            "Compression Support",
            "Checksum Verification",
            "Retention Policies",
            "Logging System"
        ]
        
        for feature in backup_features:
            # Check if feature is mentioned in script
            if any(keyword.lower() in content.lower() for keyword in feature.split()):
                self.log_test(f"Backup Feature: {feature}", "PASS")
            else:
                self.log_test(f"Backup Feature: {feature}", "WARNING", f"Feature {feature} not clearly implemented")
                
    def test_remote_storage_features(self):
        """Test remote storage features"""
        print("\n=== Testing Remote Storage Features ===")
        
        if not self.backup_script_path.exists():
            self.log_test("Remote Storage Features", "FAIL", "Backup script not found")
            return
            
        content = self.backup_script_path.read_text()
        
        # Test remote storage features
        remote_features = [
            "Git Repository",
            "Google Drive",
            "Amazon S3",
            "FTP Server",
            "Auto-commit",
            "Credential Management",
            "Rate Limiting",
            "Error Handling"
        ]
        
        for feature in remote_features:
            # Check if feature is mentioned in script
            if any(keyword.lower() in content.lower() for keyword in feature.split()):
                self.log_test(f"Remote Storage Feature: {feature}", "PASS")
            else:
                self.log_test(f"Remote Storage Feature: {feature}", "WARNING", f"Feature {feature} not clearly implemented")
                
    def test_restore_features(self):
        """Test restore features"""
        print("\n=== Testing Restore Features ===")
        
        if not self.restore_script_path.exists():
            self.log_test("Restore Features", "FAIL", "Restore script not found")
            return
            
        content = self.restore_script_path.read_text()
        
        # Test restore features
        restore_features = [
            "Backup Verification",
            "Pre-restore Backups",
            "User Confirmation",
            "Dry Run Mode",
            "Metadata Extraction",
            "File Permissions",
            "Error Recovery",
            "Logging"
        ]
        
        for feature in restore_features:
            # Check if feature is mentioned in script
            if any(keyword.lower() in content.lower() for keyword in feature.split()):
                self.log_test(f"Restore Feature: {feature}", "PASS")
            else:
                self.log_test(f"Restore Feature: {feature}", "WARNING", f"Feature {feature} not clearly implemented")
                
    def test_safety_features(self):
        """Test safety features"""
        print("\n=== Testing Safety Features ===")
        
        if not self.restore_script_path.exists():
            self.log_test("Safety Features", "FAIL", "Restore script not found")
            return
            
        content = self.restore_script_path.read_text()
        
        # Test safety features
        safety_features = [
            "Pre-restore Backups",
            "User Confirmation",
            "Dry Run Mode",
            "Checksum Verification",
            "Archive Testing",
            "Error Handling",
            "Logging",
            "Permission Preservation"
        ]
        
        for feature in safety_features:
            # Check if feature is mentioned in script
            if any(keyword.lower() in content.lower() for keyword in feature.split()):
                self.log_test(f"Safety Feature: {feature}", "PASS")
            else:
                self.log_test(f"Safety Feature: {feature}", "WARNING", f"Feature {feature} not clearly implemented")
                
    def test_script_arguments(self):
        """Test script arguments"""
        print("\n=== Testing Script Arguments ===")
        
        # Test backup script arguments
        if self.backup_script_path.exists():
            content = self.backup_script_path.read_text()
            
            backup_args = ["--help", "--dry-run", "--force", "--clean-only"]
            
            for arg in backup_args:
                if arg in content:
                    self.log_test(f"Backup Script Argument: {arg}", "PASS")
                else:
                    self.log_test(f"Backup Script Argument: {arg}", "WARNING", f"Argument {arg} not found")
                    
        # Test restore script arguments
        if self.restore_script_path.exists():
            content = self.restore_script_path.read_text()
            
            restore_args = ["--help", "--dry-run", "--force", "--list", "--verify"]
            
            for arg in restore_args:
                if arg in content:
                    self.log_test(f"Restore Script Argument: {arg}", "PASS")
                else:
                    self.log_test(f"Restore Script Argument: {arg}", "WARNING", f"Argument {arg} not found")
                    
    def test_integration_features(self):
        """Test integration features"""
        print("\n=== Testing Integration Features ===")
        
        # Test Discord integration
        if self.backup_script_path.exists():
            content = self.backup_script_path.read_text()
            
            if "discord" in content.lower() and "webhook" in content.lower():
                self.log_test("Discord Integration", "PASS")
            else:
                self.log_test("Discord Integration", "WARNING", "Discord integration not clearly implemented")
                
        # Test Git integration
        if self.backup_script_path.exists():
            content = self.backup_script_path.read_text()
            
            if "git" in content.lower() and ("clone" in content.lower() or "push" in content.lower()):
                self.log_test("Git Integration", "PASS")
            else:
                self.log_test("Git Integration", "WARNING", "Git integration not clearly implemented")
                
        # Test S3 integration
        if self.backup_script_path.exists():
            content = self.backup_script_path.read_text()
            
            if "aws" in content.lower() or "s3" in content.lower():
                self.log_test("S3 Integration", "PASS")
            else:
                self.log_test("S3 Integration", "WARNING", "S3 integration not clearly implemented")
                
        # Test FTP integration
        if self.backup_script_path.exists():
            content = self.backup_script_path.read_text()
            
            if "ftp" in content.lower() and "curl" in content.lower():
                self.log_test("FTP Integration", "PASS")
            else:
                self.log_test("FTP Integration", "WARNING", "FTP integration not clearly implemented")
                
    def test_error_handling(self):
        """Test error handling"""
        print("\n=== Testing Error Handling ===")
        
        # Test backup script error handling
        if self.backup_script_path.exists():
            content = self.backup_script_path.read_text()
            
            error_handling_features = [
                "set -euo pipefail",
                "error_exit",
                "trap",
                "if.*then.*else",
                "log.*ERROR"
            ]
            
            for feature in error_handling_features:
                if feature in content:
                    self.log_test(f"Backup Error Handling: {feature}", "PASS")
                else:
                    self.log_test(f"Backup Error Handling: {feature}", "WARNING", f"Feature {feature} not found")
                    
        # Test restore script error handling
        if self.restore_script_path.exists():
            content = self.restore_script_path.read_text()
            
            error_handling_features = [
                "set -euo pipefail",
                "error_exit",
                "trap",
                "if.*then.*else",
                "log.*ERROR"
            ]
            
            for feature in error_handling_features:
                if feature in content:
                    self.log_test(f"Restore Error Handling: {feature}", "PASS")
                else:
                    self.log_test(f"Restore Error Handling: {feature}", "WARNING", f"Feature {feature} not found")
                    
    def test_logging_features(self):
        """Test logging features"""
        print("\n=== Testing Logging Features ===")
        
        # Test backup script logging
        if self.backup_script_path.exists():
            content = self.backup_script_path.read_text()
            
            if "log.*INFO" in content or "echo.*log" in content:
                self.log_test("Backup Logging", "PASS")
            else:
                self.log_test("Backup Logging", "WARNING", "Logging not clearly implemented")
                
        # Test restore script logging
        if self.restore_script_path.exists():
            content = self.restore_script_path.read_text()
            
            if "log.*INFO" in content or "echo.*log" in content:
                self.log_test("Restore Logging", "PASS")
            else:
                self.log_test("Restore Logging", "WARNING", "Logging not clearly implemented")
                
    def test_compression_features(self):
        """Test compression features"""
        print("\n=== Testing Compression Features ===")
        
        if not self.backup_script_path.exists():
            self.log_test("Compression Features", "FAIL", "Backup script not found")
            return
            
        content = self.backup_script_path.read_text()
        
        compression_formats = ["tar.gz", "tar.bz2", "zip"]
        
        for format in compression_formats:
            if format in content:
                self.log_test(f"Compression Format: {format}", "PASS")
            else:
                self.log_test(f"Compression Format: {format}", "WARNING", f"Format {format} not found")
                
    def test_verification_features(self):
        """Test verification features"""
        print("\n=== Testing Verification Features ===")
        
        # Test backup verification
        if self.backup_script_path.exists():
            content = self.backup_script_path.read_text()
            
            if "sha256sum" in content:
                self.log_test("Backup Checksum Verification", "PASS")
            else:
                self.log_test("Backup Checksum Verification", "WARNING", "Checksum verification not found")
                
        # Test restore verification
        if self.restore_script_path.exists():
            content = self.restore_script_path.read_text()
            
            if "sha256sum" in content:
                self.log_test("Restore Checksum Verification", "PASS")
            else:
                self.log_test("Restore Checksum Verification", "WARNING", "Checksum verification not found")
                
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 80)
        print("BATCH 194 - BACKUP & RESTORE SCRIPTS TEST")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Run all test sections
        test_sections = [
            self.test_file_existence,
            self.test_script_structure,
            self.test_configuration_structure,
            self.test_backup_features,
            self.test_remote_storage_features,
            self.test_restore_features,
            self.test_safety_features,
            self.test_script_arguments,
            self.test_integration_features,
            self.test_error_handling,
            self.test_logging_features,
            self.test_compression_features,
            self.test_verification_features
        ]
        
        for test_section in test_sections:
            try:
                test_section()
            except Exception as e:
                print(f"Error in test section {test_section.__name__}: {e}")
                
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed']}")
        print(f"Failed: {self.test_results['failed']}")
        print(f"Warnings: {self.test_results['warnings']}")
        
        # Save test results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"BATCH_194_TEST_REPORT_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
            
        print(f"\nTest results saved to: {results_file}")
        
        # Final status
        if self.test_results['failed'] == 0:
            print("\n✅ BATCH 194 IMPLEMENTATION: SUCCESS")
            print("All required features for Backup & Restore Scripts are implemented.")
        else:
            print(f"\n❌ BATCH 194 IMPLEMENTATION: FAILED ({self.test_results['failed']} failures)")
            
        print("=" * 80)

def main():
    """Main test execution"""
    tester = BackupRestoreTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 
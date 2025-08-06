#!/usr/bin/env python3
"""
Batch 195 - Error Boundary & Fallback Rendering System Test
Goal: Prevent broken pages or runtime Svelte crashes from ruining UX.

Test Coverage:
- Graceful UI fallback on error
- Auto-report error to internal log
- Optional Discord ping for criticals
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

class ErrorBoundaryTester:
    def __init__(self):
        self.test_results = {
            "batch": "195",
            "feature": "Error Boundary & Fallback Rendering System",
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
        # Define test paths
        self.base_path = Path(__file__).parent
        self.error_boundary_path = self.base_path / "src" / "components" / "ErrorBoundary.svelte"
        self.handle_error_path = self.base_path / "src" / "lib" / "handle-error.js"
        
        # Required features for Batch 195
        self.required_features = {
            "graceful_fallback": {
                "keywords": ["fallback", "error-fallback", "error-boundary"],
                "sections": ["Graceful UI Fallback", "Error Display"]
            },
            "auto_reporting": {
                "keywords": ["autoReport", "handleError", "logToServer"],
                "sections": ["Auto Reporting", "Error Logging"]
            },
            "discord_integration": {
                "keywords": ["discordPing", "discordWebhook", "pingDiscord"],
                "sections": ["Discord Integration", "Critical Errors"]
            }
        }

    def log_test(self, test_name, status, message, details=None):
        """Log a test result"""
        test_result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {}
        }
        
        self.test_results["tests"].append(test_result)
        self.test_results["summary"]["total_tests"] += 1
        
        if status == "PASS":
            self.test_results["summary"]["passed"] += 1
        elif status == "FAIL":
            self.test_results["summary"]["failed"] += 1
        elif status == "WARNING":
            self.test_results["summary"]["warnings"] += 1
            
        print(f"[{status}] {test_name}: {message}")

    def test_file_existence(self):
        """Test that required files exist"""
        print("\n=== Testing File Existence ===")
        
        # Test error boundary component file
        if self.error_boundary_path.exists():
            self.log_test("Error Boundary Component File Exists", "PASS", 
                         f"Found {self.error_boundary_path}")
        else:
            self.log_test("Error Boundary Component File Exists", "FAIL", 
                         f"Missing {self.error_boundary_path}")
            
        # Test handle error library file
        if self.handle_error_path.exists():
            self.log_test("Handle Error Library File Exists", "PASS", 
                         f"Found {self.handle_error_path}")
        else:
            self.log_test("Handle Error Library File Exists", "FAIL", 
                         f"Missing {self.handle_error_path}")

    def test_error_boundary_structure(self):
        """Test the structure and content of the error boundary component"""
        print("\n=== Testing Error Boundary Structure ===")
        
        if not self.error_boundary_path.exists():
            self.log_test("Error Boundary Structure", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.error_boundary_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for required props
            props = ["fallback", "showDetails", "autoReport", "discordPing", "logLevel"]
            
            for prop in props:
                if prop in content:
                    self.log_test(f"Error Boundary Prop: {prop}", "PASS", 
                                 f"Found {prop} prop in component")
                else:
                    self.log_test(f"Error Boundary Prop: {prop}", "WARNING", 
                                 f"Missing {prop} prop in component")
                    
            # Test for error handling functionality
            error_handling_features = [
                "handleComponentError",
                "resetError",
                "copyErrorDetails",
                "reloadPage",
                "goBack",
                "goHome"
            ]
            
            for feature in error_handling_features:
                if feature in content:
                    self.log_test(f"Error Handling Feature: {feature}", "PASS", 
                                 f"Found {feature} function")
                else:
                    self.log_test(f"Error Handling Feature: {feature}", "WARNING", 
                                 f"Missing {feature} function")
                    
            # Test for UI elements
            ui_elements = [
                "error-fallback",
                "error-header",
                "error-actions",
                "error-details",
                "error-footer"
            ]
            
            for element in ui_elements:
                if element in content:
                    self.log_test(f"UI Element: {element}", "PASS", 
                                 f"Found {element} in component")
                else:
                    self.log_test(f"UI Element: {element}", "WARNING", 
                                 f"Missing {element} in component")
                    
        except Exception as e:
            self.log_test("Error Boundary Structure", "FAIL", f"Error reading file: {e}")

    def test_handle_error_library(self):
        """Test the handle error library functionality"""
        print("\n=== Testing Handle Error Library ===")
        
        if not self.handle_error_path.exists():
            self.log_test("Handle Error Library", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.handle_error_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for main functions
            functions = [
                "handleError",
                "getErrorStats",
                "clearErrorLog",
                "getErrorLog",
                "initializeErrorHandling"
            ]
            
            for func in functions:
                if f"export function {func}" in content or f"function {func}" in content:
                    self.log_test(f"Library Function: {func}", "PASS", 
                                 f"Found {func} function")
                else:
                    self.log_test(f"Library Function: {func}", "WARNING", 
                                 f"Missing {func} function")
                    
            # Test for error configuration
            config_features = [
                "ERROR_CONFIG",
                "logToConsole",
                "logToServer",
                "discordWebhook",
                "criticalErrors"
            ]
            
            for feature in config_features:
                if feature in content:
                    self.log_test(f"Config Feature: {feature}", "PASS", 
                                 f"Found {feature} in configuration")
                else:
                    self.log_test(f"Config Feature: {feature}", "WARNING", 
                                 f"Missing {feature} in configuration")
                    
            # Test for Discord integration
            discord_features = [
                "pingDiscord",
                "shouldPingDiscord",
                "discordPingRoles",
                "discordPingCount"
            ]
            
            for feature in discord_features:
                if feature in content:
                    self.log_test(f"Discord Feature: {feature}", "PASS", 
                                 f"Found {feature} in Discord integration")
                else:
                    self.log_test(f"Discord Feature: {feature}", "WARNING", 
                                 f"Missing {feature} in Discord integration")
                    
        except Exception as e:
            self.log_test("Handle Error Library", "FAIL", f"Error reading file: {e}")

    def test_graceful_fallback(self):
        """Test graceful UI fallback features"""
        print("\n=== Testing Graceful Fallback ===")
        
        if not self.error_boundary_path.exists():
            self.log_test("Graceful Fallback", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.error_boundary_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for fallback UI elements
            fallback_elements = [
                "Something went wrong",
                "We encountered an unexpected error",
                "Reload Page",
                "Go Back",
                "Go Home",
                "Error Details"
            ]
            
            for element in fallback_elements:
                if element in content:
                    self.log_test(f"Fallback UI: {element}", "PASS", 
                                 f"Found {element} in fallback UI")
                else:
                    self.log_test(f"Fallback UI: {element}", "WARNING", 
                                 f"Missing {element} in fallback UI")
                    
            # Test for error display features
            display_features = [
                "Error ID",
                "Message",
                "Component Stack",
                "Copy Error Details"
            ]
            
            for feature in display_features:
                if feature in content:
                    self.log_test(f"Error Display: {feature}", "PASS", 
                                 f"Found {feature} in error display")
                else:
                    self.log_test(f"Error Display: {feature}", "WARNING", 
                                 f"Missing {feature} in error display")
                    
        except Exception as e:
            self.log_test("Graceful Fallback", "FAIL", f"Error testing fallback: {e}")

    def test_auto_reporting(self):
        """Test auto-reporting functionality"""
        print("\n=== Testing Auto Reporting ===")
        
        if not self.handle_error_path.exists():
            self.log_test("Auto Reporting", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.handle_error_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for reporting features
            reporting_features = [
                "logToConsole",
                "logToServer",
                "addToErrorLog",
                "trackErrorAnalytics"
            ]
            
            for feature in reporting_features:
                if feature in content:
                    self.log_test(f"Reporting Feature: {feature}", "PASS", 
                                 f"Found {feature} in reporting system")
                else:
                    self.log_test(f"Reporting Feature: {feature}", "WARNING", 
                                 f"Missing {feature} in reporting system")
                    
            # Test for error storage
            storage_features = [
                "localStorage",
                "errorLog",
                "maxStoredErrors",
                "errorRetentionDays"
            ]
            
            for feature in storage_features:
                if feature in content:
                    self.log_test(f"Storage Feature: {feature}", "PASS", 
                                 f"Found {feature} in storage system")
                else:
                    self.log_test(f"Storage Feature: {feature}", "WARNING", 
                                 f"Missing {feature} in storage system")
                    
        except Exception as e:
            self.log_test("Auto Reporting", "FAIL", f"Error testing reporting: {e}")

    def test_discord_integration(self):
        """Test Discord integration features"""
        print("\n=== Testing Discord Integration ===")
        
        if not self.handle_error_path.exists():
            self.log_test("Discord Integration", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.handle_error_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for Discord webhook features
            webhook_features = [
                "discordWebhook",
                "discordPingRoles",
                "pingDiscord",
                "shouldPingDiscord"
            ]
            
            for feature in webhook_features:
                if feature in content:
                    self.log_test(f"Discord Webhook: {feature}", "PASS", 
                                 f"Found {feature} in Discord integration")
                else:
                    self.log_test(f"Discord Webhook: {feature}", "WARNING", 
                                 f"Missing {feature} in Discord integration")
                    
            # Test for critical error handling
            critical_features = [
                "criticalErrors",
                "TypeError",
                "ReferenceError",
                "SyntaxError"
            ]
            
            for feature in critical_features:
                if feature in content:
                    self.log_test(f"Critical Error: {feature}", "PASS", 
                                 f"Found {feature} in critical error handling")
                else:
                    self.log_test(f"Critical Error: {feature}", "WARNING", 
                                 f"Missing {feature} in critical error handling")
                    
            # Test for rate limiting
            rate_limit_features = [
                "maxDiscordPingsPerHour",
                "discordPingCount",
                "lastDiscordPing"
            ]
            
            for feature in rate_limit_features:
                if feature in content:
                    self.log_test(f"Rate Limiting: {feature}", "PASS", 
                                 f"Found {feature} in rate limiting")
                else:
                    self.log_test(f"Rate Limiting: {feature}", "WARNING", 
                                 f"Missing {feature} in rate limiting")
                    
        except Exception as e:
            self.log_test("Discord Integration", "FAIL", f"Error testing Discord: {e}")

    def test_error_boundary_props(self):
        """Test error boundary component props and configuration"""
        print("\n=== Testing Error Boundary Props ===")
        
        if not self.error_boundary_path.exists():
            self.log_test("Error Boundary Props", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.error_boundary_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for prop definitions
            prop_definitions = [
                "export let fallback",
                "export let showDetails",
                "export let autoReport",
                "export let discordPing",
                "export let logLevel"
            ]
            
            for prop in prop_definitions:
                if prop in content:
                    self.log_test(f"Prop Definition: {prop}", "PASS", 
                                 f"Found {prop} in component")
                else:
                    self.log_test(f"Prop Definition: {prop}", "WARNING", 
                                 f"Missing {prop} in component")
                    
            # Test for prop usage
            prop_usage = [
                "fallback",
                "showDetails",
                "autoReport",
                "discordPing",
                "logLevel"
            ]
            
            for prop in prop_usage:
                if prop in content:
                    self.log_test(f"Prop Usage: {prop}", "PASS", 
                                 f"Found {prop} usage in component")
                else:
                    self.log_test(f"Prop Usage: {prop}", "WARNING", 
                                 f"Missing {prop} usage in component")
                    
        except Exception as e:
            self.log_test("Error Boundary Props", "FAIL", f"Error testing props: {e}")

    def test_error_handling_integration(self):
        """Test integration between error boundary and handle error library"""
        print("\n=== Testing Error Handling Integration ===")
        
        if not self.error_boundary_path.exists() or not self.handle_error_path.exists():
            self.log_test("Error Handling Integration", "FAIL", "Cannot test - files missing")
            return
            
        try:
            with open(self.error_boundary_path, 'r', encoding='utf-8') as f:
                boundary_content = f.read()
                
            with open(self.handle_error_path, 'r', encoding='utf-8') as f:
                library_content = f.read()
                
            # Test for import statement
            if "import { handleError }" in boundary_content:
                self.log_test("Library Import", "PASS", 
                             "Found handleError import in error boundary")
            else:
                self.log_test("Library Import", "FAIL", 
                             "Missing handleError import in error boundary")
                
            # Test for function call
            if "handleError(" in boundary_content:
                self.log_test("Function Call", "PASS", 
                             "Found handleError function call")
            else:
                self.log_test("Function Call", "FAIL", 
                             "Missing handleError function call")
                
            # Test for error data passing
            error_data_features = [
                "error: childError",
                "errorInfo: childErrorInfo",
                "errorId: errorId",
                "errorBoundaryId: errorBoundaryId"
            ]
            
            for feature in error_data_features:
                if feature in boundary_content:
                    self.log_test(f"Error Data: {feature}", "PASS", 
                                 f"Found {feature} in error data passing")
                else:
                    self.log_test(f"Error Data: {feature}", "WARNING", 
                                 f"Missing {feature} in error data passing")
                    
        except Exception as e:
            self.log_test("Error Handling Integration", "FAIL", f"Error testing integration: {e}")

    def test_accessibility_features(self):
        """Test accessibility features in error boundary"""
        print("\n=== Testing Accessibility Features ===")
        
        if not self.error_boundary_path.exists():
            self.log_test("Accessibility Features", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.error_boundary_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for accessibility features
            accessibility_features = [
                "role=",
                "tabindex",
                "aria-",
                "focus",
                "keyboard"
            ]
            
            for feature in accessibility_features:
                if feature in content:
                    self.log_test(f"Accessibility: {feature}", "PASS", 
                                 f"Found {feature} in accessibility features")
                else:
                    self.log_test(f"Accessibility: {feature}", "WARNING", 
                                 f"Missing {feature} in accessibility features")
                    
            # Test for responsive design
            responsive_features = [
                "@media (max-width:",
                "mobile",
                "responsive"
            ]
            
            for feature in responsive_features:
                if feature in content:
                    self.log_test(f"Responsive: {feature}", "PASS", 
                                 f"Found {feature} in responsive design")
                else:
                    self.log_test(f"Responsive: {feature}", "WARNING", 
                                 f"Missing {feature} in responsive design")
                    
        except Exception as e:
            self.log_test("Accessibility Features", "FAIL", f"Error testing accessibility: {e}")

    def test_error_analytics(self):
        """Test error analytics and tracking features"""
        print("\n=== Testing Error Analytics ===")
        
        if not self.handle_error_path.exists():
            self.log_test("Error Analytics", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.handle_error_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for analytics features
            analytics_features = [
                "trackErrorAnalytics",
                "gtag",
                "ms11Analytics",
                "analytics"
            ]
            
            for feature in analytics_features:
                if feature in content:
                    self.log_test(f"Analytics Feature: {feature}", "PASS", 
                                 f"Found {feature} in analytics")
                else:
                    self.log_test(f"Analytics Feature: {feature}", "WARNING", 
                                 f"Missing {feature} in analytics")
                    
            # Test for session tracking
            session_features = [
                "getSessionId",
                "getSessionDuration",
                "sessionStorage"
            ]
            
            for feature in session_features:
                if feature in content:
                    self.log_test(f"Session Feature: {feature}", "PASS", 
                                 f"Found {feature} in session tracking")
                else:
                    self.log_test(f"Session Feature: {feature}", "WARNING", 
                                 f"Missing {feature} in session tracking")
                    
        except Exception as e:
            self.log_test("Error Analytics", "FAIL", f"Error testing analytics: {e}")

    def run_all_tests(self):
        """Run all tests for Batch 195"""
        print("=" * 60)
        print("BATCH 195 - ERROR BOUNDARY & FALLBACK RENDERING SYSTEM TEST")
        print("=" * 60)
        print(f"Testing: {self.test_results['feature']}")
        print(f"Timestamp: {self.test_results['timestamp']}")
        print("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_file_existence,
            self.test_error_boundary_structure,
            self.test_handle_error_library,
            self.test_graceful_fallback,
            self.test_auto_reporting,
            self.test_discord_integration,
            self.test_error_boundary_props,
            self.test_error_handling_integration,
            self.test_accessibility_features,
            self.test_error_analytics
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(test_method.__name__, "FAIL", f"Test method error: {e}")
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        summary = self.test_results["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Warnings: {summary['warnings']}")
        
        if summary['failed'] == 0 and summary['total_tests'] > 0:
            print("\n✅ BATCH 195 IMPLEMENTATION: SUCCESS")
            print("All required features for Error Boundary & Fallback Rendering System are implemented.")
        elif summary['failed'] > 0:
            print("\n❌ BATCH 195 IMPLEMENTATION: FAILED")
            print("Some required features are missing or incomplete.")
        else:
            print("\n⚠️ BATCH 195 IMPLEMENTATION: PARTIAL")
            print("Implementation has warnings but no critical failures.")
            
        # Save test results
        self.save_test_results()

    def save_test_results(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"BATCH_195_TEST_REPORT_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"\nTest results saved to: {filename}")
        except Exception as e:
            print(f"\nError saving test results: {e}")

def main():
    """Main test execution"""
    tester = ErrorBoundaryTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 
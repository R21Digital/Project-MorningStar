#!/usr/bin/env python3
"""
Batch 200 - Public Launch Prep & Go-Live Script Test Suite
Tests the launch preparation and deployment system.
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class LaunchPrepTester:
    """Test suite for launch preparation system"""
    
    def __init__(self):
        self.test_results = []
        self.project_root = Path(__file__).parent
        
    def log_test(self, test_name: str, status: str, details: Dict[str, Any] = None):
        """Log test results"""
        result = {
            'test_name': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def test_go_live_script_exists(self) -> bool:
        """Test go-live script exists and is executable"""
        print("\n🚀 Testing Go-Live Script...")
        
        script_path = self.project_root / "scripts/go_live.sh"
        if script_path.exists():
            self.log_test("Go-Live Script - Exists", "PASS",
                         {"path": str(script_path)})
            
            # Check if executable (Unix-like systems)
            if os.name != 'nt':  # Not Windows
                if os.access(script_path, os.X_OK):
                    self.log_test("Go-Live Script - Executable", "PASS")
                else:
                    self.log_test("Go-Live Script - Executable", "WARN",
                                {"note": "Script not executable - may need chmod +x"})
            
            # Check script syntax
            try:
                result = subprocess.run(['bash', '-n', str(script_path)], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.log_test("Go-Live Script - Syntax", "PASS")
                else:
                    self.log_test("Go-Live Script - Syntax", "FAIL",
                                {"error": result.stderr})
            except subprocess.TimeoutExpired:
                self.log_test("Go-Live Script - Syntax", "WARN",
                            {"note": "Syntax check timed out"})
            except Exception as e:
                self.log_test("Go-Live Script - Syntax", "WARN",
                            {"note": f"Could not validate syntax: {str(e)}"})
            
            return True
        else:
            self.log_test("Go-Live Script - Exists", "FAIL",
                         {"error": f"Script not found: {script_path}"})
            return False
    
    def test_deployment_configuration(self) -> bool:
        """Test deployment configuration file"""
        print("\n⚙️ Testing Deployment Configuration...")
        
        config_path = self.project_root / "config/deploy/live.json"
        if config_path.exists():
            self.log_test("Deploy Config - Exists", "PASS")
            
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                self.log_test("Deploy Config - Valid JSON", "PASS")
                
                # Check required sections
                required_sections = [
                    'domain', 'hosting', 'cdn', 'analytics', 'security',
                    'notifications', 'monitoring', 'deployment_checklist'
                ]
                
                missing_sections = []
                for section in required_sections:
                    if section in config:
                        self.log_test(f"Deploy Config - {section}", "PASS")
                    else:
                        missing_sections.append(section)
                        self.log_test(f"Deploy Config - {section}", "FAIL",
                                    {"error": f"Missing section: {section}"})
                
                # Check deployment checklist
                checklist = config.get('deployment_checklist', [])
                if checklist and len(checklist) >= 10:
                    self.log_test("Deploy Config - Checklist", "PASS",
                                {"checklist_items": len(checklist)})
                else:
                    self.log_test("Deploy Config - Checklist", "WARN",
                                {"note": f"Checklist has {len(checklist)} items"})
                
                return len(missing_sections) == 0
                
            except json.JSONDecodeError as e:
                self.log_test("Deploy Config - Valid JSON", "FAIL",
                            {"error": f"Invalid JSON: {str(e)}"})
                return False
        else:
            self.log_test("Deploy Config - Exists", "FAIL",
                         {"error": f"Config not found: {config_path}"})
            return False
    
    def test_analytics_integration(self) -> bool:
        """Test analytics integration functionality"""
        print("\n📊 Testing Analytics Integration...")
        
        # Check go-live script for analytics injection
        script_path = self.project_root / "scripts/go_live.sh"
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            analytics_features = [
                'inject_analytics',
                'google_tag_manager',
                'search_console',
                'GTM_CONTAINER_ID',
                'GSC_VERIFICATION_CODE'
            ]
            
            for feature in analytics_features:
                if feature in script_content:
                    self.log_test(f"Analytics - {feature}", "PASS")
                else:
                    self.log_test(f"Analytics - {feature}", "FAIL",
                                {"error": f"Missing analytics feature: {feature}"})
            
            return all(feature in script_content for feature in analytics_features)
        else:
            self.log_test("Analytics - Script Check", "FAIL",
                         {"error": "Go-live script not found"})
            return False
    
    def test_cdn_purge_functionality(self) -> bool:
        """Test CDN purge functionality"""
        print("\n🌐 Testing CDN Purge Functionality...")
        
        script_path = self.project_root / "scripts/go_live.sh"
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            cdn_features = [
                'purge_cdn',
                'cloudflare',
                'fastly',
                'CDN_ENABLED'
            ]
            
            for feature in cdn_features:
                if feature in script_content:
                    self.log_test(f"CDN - {feature}", "PASS")
                else:
                    self.log_test(f"CDN - {feature}", "WARN",
                                {"note": f"CDN feature not found: {feature}"})
            
            # Check deployment config for CDN settings
            config_path = self.project_root / "config/deploy/live.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                cdn_config = config.get('cdn', {})
                if cdn_config.get('enabled'):
                    self.log_test("CDN Config - Enabled", "PASS")
                    
                    providers = ['cloudflare', 'fastly']
                    provider_found = any(provider in cdn_config for provider in providers)
                    if provider_found:
                        self.log_test("CDN Config - Provider", "PASS")
                    else:
                        self.log_test("CDN Config - Provider", "WARN",
                                    {"note": "No CDN provider configuration found"})
                else:
                    self.log_test("CDN Config - Enabled", "INFO",
                                {"note": "CDN disabled in configuration"})
            
            return True
        else:
            self.log_test("CDN - Script Check", "FAIL",
                         {"error": "Go-live script not found"})
            return False
    
    def test_discord_notifications(self) -> bool:
        """Test Discord notification functionality"""
        print("\n📢 Testing Discord Notifications...")
        
        # Check go-live script for Discord integration
        script_path = self.project_root / "scripts/go_live.sh"
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            discord_features = [
                'send_discord_notification',
                'DISCORD_WEBHOOK_URL',
                'embed_json',
                'Launch',
                'curl'
            ]
            
            for feature in discord_features:
                if feature in script_content:
                    self.log_test(f"Discord - {feature}", "PASS")
                else:
                    self.log_test(f"Discord - {feature}", "FAIL",
                                {"error": f"Missing Discord feature: {feature}"})
            
            # Check deployment config for Discord settings
            config_path = self.project_root / "config/deploy/live.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                notifications = config.get('notifications', {})
                discord_config = notifications.get('discord', {})
                
                if discord_config.get('enabled'):
                    self.log_test("Discord Config - Enabled", "PASS")
                    
                    if 'webhook_url' in discord_config:
                        self.log_test("Discord Config - Webhook URL", "PASS")
                    else:
                        self.log_test("Discord Config - Webhook URL", "FAIL",
                                    {"error": "Missing webhook URL configuration"})
                else:
                    self.log_test("Discord Config - Enabled", "WARN",
                                {"note": "Discord notifications disabled"})
            
            return all(feature in script_content for feature in discord_features)
        else:
            self.log_test("Discord - Script Check", "FAIL",
                         {"error": "Go-live script not found"})
            return False
    
    def test_security_headers(self) -> bool:
        """Test security headers configuration"""
        print("\n🔒 Testing Security Headers...")
        
        script_path = self.project_root / "scripts/go_live.sh"
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            security_features = [
                'setup_security_headers',
                'X-Content-Type-Options',
                'X-Frame-Options',
                'Content-Security-Policy',
                'Strict-Transport-Security',
                '.htaccess',
                '_headers'
            ]
            
            for feature in security_features:
                if feature in script_content:
                    self.log_test(f"Security - {feature}", "PASS")
                else:
                    self.log_test(f"Security - {feature}", "FAIL",
                                {"error": f"Missing security feature: {feature}"})
            
            return all(feature in script_content for feature in security_features)
        else:
            self.log_test("Security - Script Check", "FAIL",
                         {"error": "Go-live script not found"})
            return False
    
    def test_file_structure_validation(self) -> bool:
        """Test file structure validation"""
        print("\n📁 Testing File Structure Validation...")
        
        script_path = self.project_root / "scripts/go_live.sh"
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            validation_features = [
                'validate_project_structure',
                'required_dirs',
                'required_files',
                'missing_items'
            ]
            
            for feature in validation_features:
                if feature in script_content:
                    self.log_test(f"Validation - {feature}", "PASS")
                else:
                    self.log_test(f"Validation - {feature}", "FAIL",
                                {"error": f"Missing validation feature: {feature}"})
            
            return all(feature in script_content for feature in validation_features)
        else:
            self.log_test("Validation - Script Check", "FAIL",
                         {"error": "Go-live script not found"})
            return False
    
    def test_backup_functionality(self) -> bool:
        """Test backup functionality"""
        print("\n💾 Testing Backup Functionality...")
        
        script_path = self.project_root / "scripts/go_live.sh"
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            backup_features = [
                'backup_current_state',
                'BACKUP_DIR',
                'BACKUP_MANIFEST',
                'cp -r',
                'pre_launch'
            ]
            
            for feature in backup_features:
                if feature in script_content:
                    self.log_test(f"Backup - {feature}", "PASS")
                else:
                    self.log_test(f"Backup - {feature}", "FAIL",
                                {"error": f"Missing backup feature: {feature}"})
            
            return all(feature in script_content for feature in backup_features)
        else:
            self.log_test("Backup - Script Check", "FAIL",
                         {"error": "Go-live script not found"})
            return False
    
    def test_build_optimization(self) -> bool:
        """Test build optimization functionality"""
        print("\n⚡ Testing Build Optimization...")
        
        script_path = self.project_root / "scripts/go_live.sh"
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            optimization_features = [
                'optimize_assets',
                'minify',
                'gzip',
                'cleancss',
                'uglifyjs',
                'optipng'
            ]
            
            for feature in optimization_features:
                if feature in script_content:
                    self.log_test(f"Optimization - {feature}", "PASS")
                else:
                    self.log_test(f"Optimization - {feature}", "WARN",
                                {"note": f"Optional optimization: {feature}"})
            
            # Check for sitemap generation
            if 'generate_sitemap' in script_content:
                self.log_test("Optimization - Sitemap", "PASS")
            else:
                self.log_test("Optimization - Sitemap", "FAIL",
                            {"error": "Missing sitemap generation"})
            
            return True
        else:
            self.log_test("Optimization - Script Check", "FAIL",
                         {"error": "Go-live script not found"})
            return False
    
    def test_pre_launch_checklist(self) -> bool:
        """Test pre-launch checklist script"""
        print("\n✅ Testing Pre-Launch Checklist...")
        
        checklist_path = self.project_root / "scripts/pre_launch_checklist.py"
        if checklist_path.exists():
            self.log_test("Checklist Script - Exists", "PASS")
            
            # Check if script is valid Python
            try:
                with open(checklist_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic syntax check
                compile(content, str(checklist_path), 'exec')
                self.log_test("Checklist Script - Syntax", "PASS")
                
                # Check for required classes/functions
                required_elements = [
                    'PreLaunchValidator',
                    'validate_project_structure',
                    'validate_configuration_files',
                    'generate_launch_readiness_report'
                ]
                
                for element in required_elements:
                    if element in content:
                        self.log_test(f"Checklist - {element}", "PASS")
                    else:
                        self.log_test(f"Checklist - {element}", "FAIL",
                                    {"error": f"Missing element: {element}"})
                
                return all(element in content for element in required_elements)
                
            except SyntaxError as e:
                self.log_test("Checklist Script - Syntax", "FAIL",
                            {"error": f"Syntax error: {str(e)}"})
                return False
        else:
            self.log_test("Checklist Script - Exists", "FAIL",
                         {"error": f"Script not found: {checklist_path}"})
            return False
    
    def test_environment_variables(self) -> bool:
        """Test environment variable handling"""
        print("\n🌍 Testing Environment Variables...")
        
        # Check deployment config for environment variable placeholders
        config_path = self.project_root / "config/deploy/live.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Look for environment variable patterns
            env_vars = [
                'CLOUDFLARE_ZONE_ID',
                'CLOUDFLARE_API_TOKEN',
                'GTM_CONTAINER_ID',
                'GSC_VERIFICATION_CODE',
                'DISCORD_WEBHOOK_URL'
            ]
            
            for var in env_vars:
                if f"${{{var}}}" in content or f"${var}" in content:
                    self.log_test(f"Env Var - {var}", "PASS")
                else:
                    self.log_test(f"Env Var - {var}", "WARN",
                                {"note": f"Environment variable not found: {var}"})
            
            return True
        else:
            self.log_test("Env Vars - Config Check", "FAIL",
                         {"error": "Deployment config not found"})
            return False
    
    def test_script_error_handling(self) -> bool:
        """Test script error handling"""
        print("\n🚨 Testing Script Error Handling...")
        
        script_path = self.project_root / "scripts/go_live.sh"
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            error_handling_features = [
                'set -euo pipefail',
                'trap',
                'log "ERROR"',
                'exit 1',
                'try',
                'catch'
            ]
            
            found_features = 0
            for feature in error_handling_features:
                if feature in script_content:
                    self.log_test(f"Error Handling - {feature}", "PASS")
                    found_features += 1
                else:
                    self.log_test(f"Error Handling - {feature}", "WARN",
                                {"note": f"Error handling pattern not found: {feature}"})
            
            # At least some error handling should be present
            if found_features >= 3:
                self.log_test("Error Handling - Overall", "PASS",
                            {"features_found": found_features})
                return True
            else:
                self.log_test("Error Handling - Overall", "WARN",
                            {"features_found": found_features})
                return False
        else:
            self.log_test("Error Handling - Script Check", "FAIL",
                         {"error": "Go-live script not found"})
            return False
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print("\n📊 Generating Test Report...")
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warning_tests = len([t for t in self.test_results if t['status'] in ['WARN', 'INFO']])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'batch_id': 'BATCH_200',
            'test_name': 'Public Launch Prep & Go-Live Script',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'warnings': warning_tests,
                'success_rate': round(success_rate, 2)
            },
            'test_results': self.test_results,
            'overall_status': 'PASS' if failed_tests == 0 else 'FAIL',
            'launch_readiness': {
                'ready': failed_tests == 0 and passed_tests >= total_tests * 0.8,
                'critical_issues': failed_tests,
                'minor_issues': warning_tests
            },
            'recommendations': []
        }
        
        # Add recommendations based on results
        if failed_tests > 0:
            report['recommendations'].append("Address failed test cases before launch")
        
        if warning_tests > 0:
            report['recommendations'].append("Review warning items for potential improvements")
        
        if report['launch_readiness']['ready']:
            report['recommendations'].append("Launch system appears ready for deployment")
            report['recommendations'].append("Run pre_launch_checklist.py for final validation")
            report['recommendations'].append("Execute go_live.sh when ready to deploy")
        else:
            report['recommendations'].append("Launch system requires fixes before deployment")
        
        # Save report
        report_file = f"BATCH_200_TEST_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Test Report saved to: {report_file}")
        return report
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all launch preparation tests"""
        print("🚀 Starting Public Launch Prep Test Suite...")
        print("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_go_live_script_exists,
            self.test_deployment_configuration,
            self.test_analytics_integration,
            self.test_cdn_purge_functionality,
            self.test_discord_notifications,
            self.test_security_headers,
            self.test_file_structure_validation,
            self.test_backup_functionality,
            self.test_build_optimization,
            self.test_pre_launch_checklist,
            self.test_environment_variables,
            self.test_script_error_handling
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(f"Test Method {test_method.__name__}", "FAIL",
                            {"error": str(e)})
        
        # Generate final report
        report = self.generate_test_report()
        
        print("\n" + "=" * 60)
        print(f"🎯 Test Suite Complete!")
        print(f"📊 Overall Status: {'✅ PASS' if report['overall_status'] == 'PASS' else '❌ FAIL'}")
        print(f"📈 Success Rate: {report['summary']['success_rate']}%")
        print(f"📋 Tests: {report['summary']['passed']}/{report['summary']['total_tests']} passed")
        
        # Launch readiness assessment
        readiness = report['launch_readiness']
        readiness_emoji = "🚀" if readiness['ready'] else "🚫"
        print(f"{readiness_emoji} Launch Ready: {'Yes' if readiness['ready'] else 'No'}")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        return report

def main():
    """Main test runner"""
    tester = LaunchPrepTester()
    
    try:
        # Run all tests
        report = tester.run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if report['overall_status'] == 'PASS' else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
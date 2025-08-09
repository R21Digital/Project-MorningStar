#!/usr/bin/env python3
"""
Pre-Launch Checklist Validator
Comprehensive validation script to ensure all systems are ready for public launch.
"""

import os
import sys
import json
import yaml
import subprocess
import requests
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class PreLaunchValidator:
    """Comprehensive pre-launch validation system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.validation_results = []
        self.critical_failures = []
        self.warnings = []
        
    def log_result(self, category: str, test_name: str, status: str, details: Dict[str, Any] = None):
        """Log validation result"""
        result = {
            'category': category,
            'test_name': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.validation_results.append(result)
        
        # Track critical failures
        if status == "CRITICAL_FAIL":
            self.critical_failures.append(f"{category}: {test_name}")
        elif status == "WARN":
            self.warnings.append(f"{category}: {test_name}")
        
        # Console output
        status_emoji = {
            "PASS": "✅",
            "FAIL": "❌", 
            "CRITICAL_FAIL": "🚨",
            "WARN": "⚠️",
            "INFO": "ℹ️"
        }.get(status, "❓")
        
        print(f"{status_emoji} [{category}] {test_name}: {status}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def validate_project_structure(self):
        """Validate core project structure"""
        print("\n🏗️ Validating Project Structure...")
        
        # Critical directories
        critical_dirs = [
            "src", "config", "data", "scripts", "api", 
            "website", "swgdb_site", "tests"
        ]
        
        for dir_name in critical_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                self.log_result("Structure", f"Directory: {dir_name}", "PASS")
            else:
                self.log_result("Structure", f"Directory: {dir_name}", "CRITICAL_FAIL",
                              {"error": f"Missing critical directory: {dir_name}"})
        
        # Critical files
        critical_files = [
            "README.md", "requirements.txt", "package.json", 
            "Makefile", ".github/workflows/tests.yml"
        ]
        
        for file_name in critical_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.log_result("Structure", f"File: {file_name}", "PASS")
            else:
                self.log_result("Structure", f"File: {file_name}", "FAIL",
                              {"error": f"Missing file: {file_name}"})
    
    def validate_configuration_files(self):
        """Validate configuration files"""
        print("\n⚙️ Validating Configuration Files...")
        
        # Check deployment config
        deploy_config = self.project_root / "config/deploy/live.json"
        if deploy_config.exists():
            try:
                with open(deploy_config, 'r') as f:
                    config = json.load(f)
                
                # Validate required sections
                required_sections = [
                    'domain', 'hosting', 'analytics', 'security', 
                    'notifications', 'deployment_checklist'
                ]
                
                for section in required_sections:
                    if section in config:
                        self.log_result("Config", f"Deploy Config - {section}", "PASS")
                    else:
                        self.log_result("Config", f"Deploy Config - {section}", "FAIL",
                                      {"error": f"Missing section: {section}"})
            except json.JSONDecodeError as e:
                self.log_result("Config", "Deploy Config - JSON", "CRITICAL_FAIL",
                              {"error": f"Invalid JSON: {str(e)}"})
        else:
            self.log_result("Config", "Deploy Config - Exists", "CRITICAL_FAIL",
                          {"error": "Missing deployment configuration"})
        
        # Check webhook config
        webhook_config = self.project_root / "config/webhooks.json"
        if webhook_config.exists():
            try:
                with open(webhook_config, 'r') as f:
                    config = json.load(f)
                
                webhooks = config.get('webhooks', {})
                if 'modSubmissions' in webhooks and 'bugReports' in webhooks:
                    self.log_result("Config", "Webhook Config", "PASS")
                else:
                    self.log_result("Config", "Webhook Config", "WARN",
                                  {"note": "Some webhook configurations missing"})
            except json.JSONDecodeError as e:
                self.log_result("Config", "Webhook Config - JSON", "FAIL",
                              {"error": f"Invalid JSON: {str(e)}"})
        else:
            self.log_result("Config", "Webhook Config", "WARN",
                          {"note": "Webhook configuration not found"})
    
    def validate_data_integrity(self):
        """Validate data files integrity"""
        print("\n📊 Validating Data Integrity...")
        
        # Check heroics data
        heroics_index = self.project_root / "data/heroics/heroics_index.yml"
        if heroics_index.exists():
            try:
                with open(heroics_index, 'r') as f:
                    data = yaml.safe_load(f)
                
                heroics = data.get('heroics', {})
                if heroics:
                    self.log_result("Data", "Heroics Index", "PASS",
                                  {"heroics_count": len(heroics)})
                    
                    # Validate individual heroic files
                    for heroic_id in heroics.keys():
                        heroic_file = self.project_root / f"data/heroics/{heroic_id}.yml"
                        if heroic_file.exists():
                            self.log_result("Data", f"Heroic Data - {heroic_id}", "PASS")
                        else:
                            self.log_result("Data", f"Heroic Data - {heroic_id}", "WARN",
                                          {"note": f"Heroic file missing: {heroic_id}.yml"})
                else:
                    self.log_result("Data", "Heroics Index", "FAIL",
                                  {"error": "No heroics data found"})
            except yaml.YAMLError as e:
                self.log_result("Data", "Heroics Index - YAML", "FAIL",
                              {"error": f"Invalid YAML: {str(e)}"})
        else:
            self.log_result("Data", "Heroics Index", "FAIL",
                          {"error": "Heroics index file missing"})
        
        # Check loot tables
        loot_dir = self.project_root / "data/loot_tables"
        if loot_dir.exists():
            loot_files = list(loot_dir.glob("*.json"))
            if loot_files:
                self.log_result("Data", "Loot Tables", "PASS",
                              {"table_count": len(loot_files)})
            else:
                self.log_result("Data", "Loot Tables", "WARN",
                              {"note": "No loot table files found"})
        else:
            self.log_result("Data", "Loot Tables Directory", "FAIL",
                          {"error": "Loot tables directory missing"})
    
    def validate_scripts_and_tools(self):
        """Validate scripts and build tools"""
        print("\n🔧 Validating Scripts and Tools...")
        
        # Check go-live script
        go_live_script = self.project_root / "scripts/go_live.sh"
        if go_live_script.exists():
            # Check if executable
            if os.access(go_live_script, os.X_OK):
                self.log_result("Scripts", "Go-Live Script - Executable", "PASS")
            else:
                self.log_result("Scripts", "Go-Live Script - Executable", "WARN",
                              {"note": "Script not executable - may need chmod +x"})
            
            # Check script syntax
            try:
                result = subprocess.run(['bash', '-n', str(go_live_script)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_result("Scripts", "Go-Live Script - Syntax", "PASS")
                else:
                    self.log_result("Scripts", "Go-Live Script - Syntax", "FAIL",
                                  {"error": result.stderr})
            except Exception as e:
                self.log_result("Scripts", "Go-Live Script - Syntax", "WARN",
                              {"note": f"Could not validate syntax: {str(e)}"})
        else:
            self.log_result("Scripts", "Go-Live Script", "CRITICAL_FAIL",
                          {"error": "Go-live script missing"})
        
        # Check Python dependencies
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', 'check'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.log_result("Scripts", "Python Dependencies", "PASS")
                else:
                    self.log_result("Scripts", "Python Dependencies", "WARN",
                                  {"note": "Some dependency conflicts detected"})
            except Exception as e:
                self.log_result("Scripts", "Python Dependencies", "WARN",
                              {"note": f"Could not check dependencies: {str(e)}"})
    
    def validate_api_endpoints(self):
        """Validate API endpoints"""
        print("\n🌐 Validating API Endpoints...")
        
        # Check API files exist
        api_files = [
            "api/submit_bug.js",
            "api/submit_mod.js", 
            "api/hooks/discord-webhook.js"
        ]
        
        for api_file in api_files:
            file_path = self.project_root / api_file
            if file_path.exists():
                self.log_result("API", f"File - {Path(api_file).name}", "PASS")
                
                # Basic syntax check for JS files
                if api_file.endswith('.js'):
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        # Check for basic required patterns
                        if 'module.exports' in content or 'export' in content:
                            self.log_result("API", f"Syntax - {Path(api_file).name}", "PASS")
                        else:
                            self.log_result("API", f"Syntax - {Path(api_file).name}", "WARN",
                                          {"note": "No export statement found"})
                    except Exception as e:
                        self.log_result("API", f"Syntax - {Path(api_file).name}", "WARN",
                                      {"note": f"Could not validate: {str(e)}"})
            else:
                self.log_result("API", f"File - {Path(api_file).name}", "FAIL",
                              {"error": f"API file missing: {api_file}"})
    
    def validate_static_site_generation(self):
        """Validate static site generation"""
        print("\n📄 Validating Static Site Generation...")
        
        # Check for 11ty pages
        pages_dir = self.project_root / "src/pages"
        if pages_dir.exists():
            # Check for heroic pages
            heroic_page = pages_dir / "heroics/[name]/index.11ty.js"
            if heroic_page.exists():
                self.log_result("Static", "Heroic Pages Generator", "PASS")
            else:
                self.log_result("Static", "Heroic Pages Generator", "FAIL",
                              {"error": "Heroic pages generator missing"})
            
            # Check for other critical pages
            page_files = list(pages_dir.glob("*.11ty.js"))
            if page_files:
                self.log_result("Static", "Page Templates", "PASS",
                              {"template_count": len(page_files)})
            else:
                self.log_result("Static", "Page Templates", "WARN",
                              {"note": "No 11ty page templates found"})
        else:
            self.log_result("Static", "Pages Directory", "FAIL",
                          {"error": "Pages directory missing"})
        
        # Check for Svelte components
        components_dir = self.project_root / "src/components"
        if components_dir.exists():
            svelte_files = list(components_dir.glob("*.svelte"))
            if svelte_files:
                self.log_result("Static", "Svelte Components", "PASS",
                              {"component_count": len(svelte_files)})
            else:
                self.log_result("Static", "Svelte Components", "WARN",
                              {"note": "No Svelte components found"})
        else:
            self.log_result("Static", "Components Directory", "WARN",
                          {"note": "Components directory missing"})
    
    def validate_testing_infrastructure(self):
        """Validate testing infrastructure"""
        print("\n🧪 Validating Testing Infrastructure...")
        
        # Check for test files
        test_patterns = [
            "test_batch_*.py",
            "demo_batch_*.py",
            "tests/*.py"
        ]
        
        for pattern in test_patterns:
            test_files = list(self.project_root.glob(pattern))
            if test_files:
                self.log_result("Testing", f"Tests - {pattern}", "PASS",
                              {"file_count": len(test_files)})
            else:
                self.log_result("Testing", f"Tests - {pattern}", "WARN",
                              {"note": f"No files matching {pattern}"})
        
        # Check if pytest is available
        try:
            result = subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log_result("Testing", "Pytest Available", "PASS")
            else:
                self.log_result("Testing", "Pytest Available", "WARN",
                              {"note": "Pytest not available"})
        except Exception as e:
            self.log_result("Testing", "Pytest Available", "WARN",
                          {"note": f"Could not check pytest: {str(e)}"})
    
    def validate_security_configuration(self):
        """Validate security configuration"""
        print("\n🔒 Validating Security Configuration...")
        
        # Check for security-sensitive files
        security_files = [
            (".env", "CRITICAL_FAIL", "Environment file should not be in repository"),
            (".env.example", "PASS", "Example environment file present"),
            ("config/safety_defaults.json", "PASS", "Safety configuration present"),
            ("config/discord_auth.json", "PASS", "Discord auth configuration present")
        ]
        
        for file_name, expected_status, message in security_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                self.log_result("Security", f"File Check - {file_name}", expected_status,
                              {"note": message})
            else:
                if expected_status == "CRITICAL_FAIL":
                    self.log_result("Security", f"File Check - {file_name}", "PASS",
                                  {"note": f"Good: {file_name} not found in repository"})
                else:
                    self.log_result("Security", f"File Check - {file_name}", "WARN",
                                  {"note": f"Optional file missing: {file_name}"})
        
        # Check .gitignore
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                content = f.read()
            
            security_patterns = ['.env', '__pycache__', 'node_modules', '*.pyc', '.DS_Store']
            missing_patterns = [p for p in security_patterns if p not in content]
            
            if missing_patterns:
                self.log_result("Security", "Gitignore Security", "WARN",
                              {"missing_patterns": missing_patterns})
            else:
                self.log_result("Security", "Gitignore Security", "PASS")
        else:
            self.log_result("Security", "Gitignore Exists", "WARN",
                          {"note": "No .gitignore file found"})
    
    def validate_documentation(self):
        """Validate documentation completeness"""
        print("\n📚 Validating Documentation...")
        
        # Check README
        readme = self.project_root / "README.md"
        if readme.exists():
            with open(readme, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_sections = [
                "installation", "usage", "features", "requirements",
                "batch", "contributing", "license"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section.lower() not in content.lower():
                    missing_sections.append(section)
            
            if missing_sections:
                self.log_result("Documentation", "README Completeness", "WARN",
                              {"missing_sections": missing_sections})
            else:
                self.log_result("Documentation", "README Completeness", "PASS")
        else:
            self.log_result("Documentation", "README Exists", "CRITICAL_FAIL",
                          {"error": "README.md missing"})
        
        # Check implementation summaries
        summary_files = list(self.project_root.glob("BATCH_*_IMPLEMENTATION_SUMMARY.md"))
        if summary_files:
            self.log_result("Documentation", "Implementation Summaries", "PASS",
                          {"summary_count": len(summary_files)})
        else:
            self.log_result("Documentation", "Implementation Summaries", "WARN",
                          {"note": "No implementation summaries found"})
    
    def run_critical_tests(self):
        """Run critical functionality tests"""
        print("\n🚨 Running Critical Tests...")
        
        # Try to import critical Python modules
        critical_modules = ['yaml', 'json', 'requests', 'pathlib']
        for module in critical_modules:
            try:
                __import__(module)
                self.log_result("Critical", f"Python Module - {module}", "PASS")
            except ImportError:
                self.log_result("Critical", f"Python Module - {module}", "CRITICAL_FAIL",
                              {"error": f"Cannot import {module}"})
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            self.log_result("Critical", "Python Version", "PASS",
                          {"version": f"{python_version.major}.{python_version.minor}"})
        else:
            self.log_result("Critical", "Python Version", "CRITICAL_FAIL",
                          {"error": f"Python {python_version.major}.{python_version.minor} too old"})
    
    def generate_launch_readiness_report(self) -> Dict[str, Any]:
        """Generate comprehensive launch readiness report"""
        print("\n📊 Generating Launch Readiness Report...")
        
        total_tests = len(self.validation_results)
        passed_tests = len([r for r in self.validation_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.validation_results if r['status'] in ['FAIL', 'CRITICAL_FAIL']])
        warning_tests = len([r for r in self.validation_results if r['status'] in ['WARN', 'INFO']])
        
        readiness_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Determine launch readiness
        if self.critical_failures:
            launch_ready = False
            readiness_level = "NOT READY"
        elif failed_tests > total_tests * 0.2:  # More than 20% failures
            launch_ready = False
            readiness_level = "NOT READY"
        elif failed_tests > 0:
            launch_ready = False
            readiness_level = "NEEDS FIXES"
        elif warning_tests > total_tests * 0.3:  # More than 30% warnings
            launch_ready = True
            readiness_level = "READY WITH WARNINGS"
        else:
            launch_ready = True
            readiness_level = "FULLY READY"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'launch_readiness': {
                'ready': launch_ready,
                'level': readiness_level,
                'score': round(readiness_score, 2)
            },
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'warnings': warning_tests,
                'critical_failures': len(self.critical_failures)
            },
            'critical_failures': self.critical_failures,
            'warnings': self.warnings,
            'validation_results': self.validation_results,
            'recommendations': []
        }
        
        # Add recommendations
        if self.critical_failures:
            report['recommendations'].append("❌ CRITICAL: Fix all critical failures before launch")
        
        if failed_tests > 0:
            report['recommendations'].append("⚠️ Fix failed validation checks")
        
        if warning_tests > 0:
            report['recommendations'].append("📝 Review and address warnings")
        
        if launch_ready:
            report['recommendations'].append("✅ System appears ready for launch")
            report['recommendations'].append("🚀 Run go_live.sh script to deploy")
        
        # Save report
        report_file = f"LAUNCH_READINESS_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print launch readiness summary"""
        print("\n" + "=" * 60)
        print("🚀 LAUNCH READINESS SUMMARY")
        print("=" * 60)
        
        # Status
        status_color = "🟢" if report['launch_readiness']['ready'] else "🔴"
        print(f"\n{status_color} Launch Status: {report['launch_readiness']['level']}")
        print(f"📊 Readiness Score: {report['launch_readiness']['score']}%")
        
        # Statistics
        summary = report['summary']
        print(f"\n📈 Validation Results:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   ⚠️ Warnings: {summary['warnings']}")
        print(f"   🚨 Critical: {summary['critical_failures']}")
        
        # Critical failures
        if report['critical_failures']:
            print(f"\n🚨 CRITICAL FAILURES:")
            for failure in report['critical_failures']:
                print(f"   • {failure}")
        
        # Recommendations
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        
        print(f"\n📋 Detailed report saved to: LAUNCH_READINESS_REPORT_*.json")
        print("=" * 60)
    
    def run_full_validation(self):
        """Run complete launch validation"""
        print("🚀 Pre-Launch Validation Suite")
        print("Batch 200 - Public Launch Prep & Go-Live Script")
        print("=" * 60)
        
        # Run all validation categories
        validation_methods = [
            self.validate_project_structure,
            self.validate_configuration_files,
            self.validate_data_integrity,
            self.validate_scripts_and_tools,
            self.validate_api_endpoints,
            self.validate_static_site_generation,
            self.validate_testing_infrastructure,
            self.validate_security_configuration,
            self.validate_documentation,
            self.run_critical_tests
        ]
        
        for method in validation_methods:
            try:
                method()
            except Exception as e:
                self.log_result("System", f"Validation Method {method.__name__}", "CRITICAL_FAIL",
                              {"error": f"Validation failed: {str(e)}"})
        
        # Generate and display report
        report = self.generate_launch_readiness_report()
        self.print_summary(report)
        
        return report

def main():
    """Main validation runner"""
    validator = PreLaunchValidator()
    
    try:
        report = validator.run_full_validation()
        
        # Exit with appropriate code
        if report['launch_readiness']['ready']:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
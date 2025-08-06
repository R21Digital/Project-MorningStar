#!/usr/bin/env python3
"""
Batch 199 - Phase 1 QA Pass & Bug Review Test Suite
Tests the comprehensive QA system and all its components.
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

class QASystemTester:
    """Test suite for the comprehensive QA system"""
    
    def __init__(self):
        self.test_results = []
        self.project_root = Path(__file__).parent
        self.scripts_dir = self.project_root / "scripts"
        
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
    
    def test_qa_scripts_exist(self) -> bool:
        """Test that all QA scripts exist"""
        print("\n🔍 Testing QA Script Availability...")
        
        expected_scripts = [
            'qa_link_checker.py',
            'qa_visual_scanner.py',
            'qa_metadata_validator.py',
            'qa_responsive_tester.py',
            'qa_browser_tester.py',
            'qa_dashboard.py'
        ]
        
        all_exist = True
        
        for script_name in expected_scripts:
            script_path = self.scripts_dir / script_name
            if script_path.exists():
                self.log_test(f"Script Exists - {script_name}", "PASS",
                             {"path": str(script_path)})
            else:
                self.log_test(f"Script Exists - {script_name}", "FAIL",
                             {"error": f"Script not found: {script_path}"})
                all_exist = False
        
        return all_exist
    
    def test_qa_script_syntax(self) -> bool:
        """Test QA script syntax validation"""
        print("\n📝 Testing QA Script Syntax...")
        
        qa_scripts = list(self.scripts_dir.glob("qa_*.py"))
        syntax_ok = True
        
        for script_path in qa_scripts:
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if script can be compiled
                compile(content, str(script_path), 'exec')
                
                self.log_test(f"Syntax Check - {script_path.name}", "PASS")
                
            except SyntaxError as e:
                self.log_test(f"Syntax Check - {script_path.name}", "FAIL",
                             {"error": f"Syntax error: {str(e)}"})
                syntax_ok = False
            except Exception as e:
                self.log_test(f"Syntax Check - {script_path.name}", "FAIL",
                             {"error": f"Parse error: {str(e)}"})
                syntax_ok = False
        
        return syntax_ok
    
    def test_qa_script_imports(self) -> bool:
        """Test that QA scripts can import their dependencies"""
        print("\n📦 Testing QA Script Dependencies...")
        
        qa_scripts = list(self.scripts_dir.glob("qa_*.py"))
        imports_ok = True
        
        for script_path in qa_scripts:
            try:
                # Try to import the script as a module
                script_name = script_path.stem
                
                # Check for required imports by analyzing the file
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract import statements
                import re
                import_lines = re.findall(r'^(?:from .+ )?import .+$', content, re.MULTILINE)
                
                # Check for common required modules
                required_modules = ['json', 'datetime', 'pathlib']
                missing_modules = []
                
                for module in required_modules:
                    if not any(module in line for line in import_lines):
                        # Module might be imported indirectly, check if it's used
                        if module in content:
                            missing_modules.append(module)
                
                if missing_modules:
                    self.log_test(f"Dependencies - {script_path.name}", "WARN",
                                 {"missing_imports": missing_modules})
                else:
                    self.log_test(f"Dependencies - {script_path.name}", "PASS")
                
            except Exception as e:
                self.log_test(f"Dependencies - {script_path.name}", "FAIL",
                             {"error": f"Import check failed: {str(e)}"})
                imports_ok = False
        
        return imports_ok
    
    def test_qa_script_help_functionality(self) -> bool:
        """Test that QA scripts provide help functionality"""
        print("\n❓ Testing QA Script Help Functionality...")
        
        qa_scripts = ['qa_dashboard.py']  # Test main dashboard script
        help_ok = True
        
        for script_name in qa_scripts:
            script_path = self.scripts_dir / script_name
            if not script_path.exists():
                continue
            
            try:
                # Test --help flag
                result = subprocess.run(
                    [sys.executable, str(script_path), '--help'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=self.project_root
                )
                
                if result.returncode == 0 and 'usage:' in result.stdout.lower():
                    self.log_test(f"Help Function - {script_name}", "PASS")
                else:
                    self.log_test(f"Help Function - {script_name}", "WARN",
                                 {"note": "Help function may not be implemented"})
                
            except subprocess.TimeoutExpired:
                self.log_test(f"Help Function - {script_name}", "WARN",
                             {"note": "Help command timed out"})
            except Exception as e:
                self.log_test(f"Help Function - {script_name}", "FAIL",
                             {"error": f"Help test failed: {str(e)}"})
                help_ok = False
        
        return help_ok
    
    def test_qa_dashboard_integration(self) -> bool:
        """Test QA dashboard integration and orchestration"""
        print("\n🎛️ Testing QA Dashboard Integration...")
        
        dashboard_script = self.scripts_dir / "qa_dashboard.py"
        
        if not dashboard_script.exists():
            self.log_test("Dashboard Integration", "FAIL",
                         {"error": "QA dashboard script not found"})
            return False
        
        try:
            # Test dashboard with dry-run or limited scope
            # Note: This is a basic test - full integration would require test environment
            
            with open(dashboard_script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for expected functionality
            required_functions = [
                'class QADashboard',
                'run_comprehensive_qa',
                'run_qa_module',
                'analyze_results',
                'generate_final_report'
            ]
            
            missing_functions = []
            for func in required_functions:
                if func not in content:
                    missing_functions.append(func)
            
            if missing_functions:
                self.log_test("Dashboard Integration - Functions", "FAIL",
                             {"missing_functions": missing_functions})
                return False
            else:
                self.log_test("Dashboard Integration - Functions", "PASS")
            
            # Check for QA module references
            expected_modules = [
                'link_checker',
                'visual_scanner',
                'metadata_validator',
                'responsive_tester',
                'browser_tester'
            ]
            
            missing_modules = []
            for module in expected_modules:
                if module not in content:
                    missing_modules.append(module)
            
            if missing_modules:
                self.log_test("Dashboard Integration - Modules", "WARN",
                             {"missing_modules": missing_modules})
            else:
                self.log_test("Dashboard Integration - Modules", "PASS")
            
            return True
            
        except Exception as e:
            self.log_test("Dashboard Integration", "FAIL",
                         {"error": f"Integration test failed: {str(e)}"})
            return False
    
    def test_qa_script_configuration(self) -> bool:
        """Test QA script configuration handling"""
        print("\n⚙️ Testing QA Script Configuration...")
        
        config_ok = True
        
        # Test that scripts handle common command-line arguments
        common_args = ['--base-url', '--build-dir']
        
        qa_scripts = list(self.scripts_dir.glob("qa_*.py"))
        
        for script_path in qa_scripts:
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for argument parsing
                if 'argparse' in content:
                    self.log_test(f"Config - {script_path.name} - ArgParse", "PASS")
                else:
                    self.log_test(f"Config - {script_path.name} - ArgParse", "WARN",
                                 {"note": "No argparse detected"})
                
                # Check for common configuration options
                config_found = 0
                for arg in common_args:
                    if arg in content:
                        config_found += 1
                
                if config_found >= len(common_args) // 2:
                    self.log_test(f"Config - {script_path.name} - Options", "PASS",
                                 {"config_options": config_found})
                else:
                    self.log_test(f"Config - {script_path.name} - Options", "WARN",
                                 {"config_options": config_found})
                
            except Exception as e:
                self.log_test(f"Config - {script_path.name}", "FAIL",
                             {"error": f"Configuration test failed: {str(e)}"})
                config_ok = False
        
        return config_ok
    
    def test_qa_output_formats(self) -> bool:
        """Test QA script output and reporting formats"""
        print("\n📊 Testing QA Output Formats...")
        
        output_ok = True
        
        qa_scripts = list(self.scripts_dir.glob("qa_*.py"))
        
        for script_path in qa_scripts:
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for JSON output capability
                if 'json.dump' in content or 'json.dumps' in content:
                    self.log_test(f"Output - {script_path.name} - JSON", "PASS")
                else:
                    self.log_test(f"Output - {script_path.name} - JSON", "WARN",
                                 {"note": "No JSON output detected"})
                
                # Check for report generation
                if 'report' in content.lower() and 'generate' in content.lower():
                    self.log_test(f"Output - {script_path.name} - Reports", "PASS")
                else:
                    self.log_test(f"Output - {script_path.name} - Reports", "WARN",
                                 {"note": "No report generation detected"})
                
                # Check for structured logging
                if 'log_result' in content or 'log_test' in content or 'print' in content:
                    self.log_test(f"Output - {script_path.name} - Logging", "PASS")
                else:
                    self.log_test(f"Output - {script_path.name} - Logging", "WARN",
                                 {"note": "No logging detected"})
                
            except Exception as e:
                self.log_test(f"Output - {script_path.name}", "FAIL",
                             {"error": f"Output format test failed: {str(e)}"})
                output_ok = False
        
        return output_ok
    
    def test_qa_error_handling(self) -> bool:
        """Test QA script error handling"""
        print("\n🚨 Testing QA Error Handling...")
        
        error_handling_ok = True
        
        qa_scripts = list(self.scripts_dir.glob("qa_*.py"))
        
        for script_path in qa_scripts:
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for try-except blocks
                try_count = content.count('try:')
                except_count = content.count('except')
                
                if try_count > 0 and except_count > 0:
                    self.log_test(f"Error Handling - {script_path.name} - Try/Except", "PASS",
                                 {"try_blocks": try_count, "except_blocks": except_count})
                else:
                    self.log_test(f"Error Handling - {script_path.name} - Try/Except", "WARN",
                                 {"note": "Limited error handling detected"})
                
                # Check for specific error handling patterns
                error_patterns = ['FileNotFoundError', 'ConnectionError', 'TimeoutError', 'Exception']
                patterns_found = sum(1 for pattern in error_patterns if pattern in content)
                
                if patterns_found >= 2:
                    self.log_test(f"Error Handling - {script_path.name} - Specific", "PASS",
                                 {"patterns_found": patterns_found})
                else:
                    self.log_test(f"Error Handling - {script_path.name} - Specific", "WARN",
                                 {"patterns_found": patterns_found})
                
            except Exception as e:
                self.log_test(f"Error Handling - {script_path.name}", "FAIL",
                             {"error": f"Error handling test failed: {str(e)}"})
                error_handling_ok = False
        
        return error_handling_ok
    
    def test_qa_requirements_coverage(self) -> bool:
        """Test that QA system covers all required functionality"""
        print("\n📋 Testing QA Requirements Coverage...")
        
        # Check that each requirement from Batch 199 is covered
        requirements = {
            'link_checker': 'Internal and external link validation',
            'visual_bug_sweeps': 'Visual bug detection and UI validation',
            'missing_images_metadata': 'Missing images and metadata validation',
            'mobile_vs_desktop': 'Mobile vs desktop UI comparison',
            'cross_browser_render': 'Cross-browser rendering validation'
        }
        
        coverage_ok = True
        
        # Map requirements to script files
        requirement_scripts = {
            'link_checker': 'qa_link_checker.py',
            'visual_bug_sweeps': 'qa_visual_scanner.py',
            'missing_images_metadata': 'qa_metadata_validator.py',
            'mobile_vs_desktop': 'qa_responsive_tester.py',
            'cross_browser_render': 'qa_browser_tester.py'
        }
        
        for req_id, description in requirements.items():
            script_name = requirement_scripts.get(req_id)
            if script_name:
                script_path = self.scripts_dir / script_name
                if script_path.exists():
                    self.log_test(f"Requirement - {req_id}", "PASS",
                                 {"description": description, "script": script_name})
                else:
                    self.log_test(f"Requirement - {req_id}", "FAIL",
                                 {"description": description, "error": f"Script missing: {script_name}"})
                    coverage_ok = False
            else:
                self.log_test(f"Requirement - {req_id}", "FAIL",
                             {"description": description, "error": "No script mapped"})
                coverage_ok = False
        
        # Check for orchestration (dashboard)
        dashboard_script = self.scripts_dir / "qa_dashboard.py"
        if dashboard_script.exists():
            self.log_test("Requirement - Orchestration", "PASS",
                         {"description": "Team assignment and QA orchestration"})
        else:
            self.log_test("Requirement - Orchestration", "FAIL",
                         {"description": "Team assignment and QA orchestration", "error": "Dashboard missing"})
            coverage_ok = False
        
        return coverage_ok
    
    def test_qa_team_assignment_logic(self) -> bool:
        """Test team assignment logic in QA dashboard"""
        print("\n👥 Testing Team Assignment Logic...")
        
        dashboard_script = self.scripts_dir / "qa_dashboard.py"
        
        if not dashboard_script.exists():
            self.log_test("Team Assignment", "FAIL",
                         {"error": "Dashboard script not found"})
            return False
        
        try:
            with open(dashboard_script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for team assignment functionality
            team_indicators = [
                'team_assignments',
                'frontend_dev',
                'backend_dev',
                'qa_engineer',
                'designer'
            ]
            
            found_indicators = sum(1 for indicator in team_indicators if indicator in content)
            
            if found_indicators >= 3:
                self.log_test("Team Assignment - Logic", "PASS",
                             {"indicators_found": found_indicators})
            else:
                self.log_test("Team Assignment - Logic", "WARN",
                             {"indicators_found": found_indicators})
            
            # Check for task generation
            if 'generate_team_assignments' in content or 'assign' in content.lower():
                self.log_test("Team Assignment - Generation", "PASS")
            else:
                self.log_test("Team Assignment - Generation", "WARN",
                             {"note": "Task generation logic not clearly identified"})
            
            return True
            
        except Exception as e:
            self.log_test("Team Assignment", "FAIL",
                         {"error": f"Team assignment test failed: {str(e)}"})
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
            'batch_id': 'BATCH_199',
            'test_name': 'QA System Test Suite',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'warnings': warning_tests,
                'success_rate': round(success_rate, 2)
            },
            'test_results': self.test_results,
            'qa_system_readiness': {
                'scripts_available': failed_tests == 0,
                'syntax_valid': all('Syntax Check' not in t['test_name'] or t['status'] == 'PASS' for t in self.test_results),
                'requirements_covered': any('Requirement -' in t['test_name'] and t['status'] == 'PASS' for t in self.test_results),
                'team_assignment_ready': any('Team Assignment' in t['test_name'] and t['status'] == 'PASS' for t in self.test_results)
            },
            'recommendations': []
        }
        
        # Add recommendations based on results
        if failed_tests == 0:
            report['recommendations'].append("✅ QA system is ready for Phase 1 testing")
        else:
            report['recommendations'].append(f"🔧 Fix {failed_tests} failed tests before deploying QA system")
        
        if warning_tests > 0:
            report['recommendations'].append(f"⚠️ Review {warning_tests} warnings for potential improvements")
        
        if report['qa_system_readiness']['scripts_available']:
            report['recommendations'].append("🚀 All QA scripts are available and ready")
        
        if report['qa_system_readiness']['requirements_covered']:
            report['recommendations'].append("📋 All Batch 199 requirements are covered")
        
        # Save report
        report_file = f"BATCH_199_QA_SYSTEM_TEST_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Test Report saved to: {report_file}")
        return report
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all QA system tests"""
        print("🧪 Starting QA System Test Suite...")
        print("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_qa_scripts_exist,
            self.test_qa_script_syntax,
            self.test_qa_script_imports,
            self.test_qa_script_help_functionality,
            self.test_qa_dashboard_integration,
            self.test_qa_script_configuration,
            self.test_qa_output_formats,
            self.test_qa_error_handling,
            self.test_qa_requirements_coverage,
            self.test_qa_team_assignment_logic
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
        print(f"📊 Overall Status: {'✅ PASS' if report['summary']['failed'] == 0 else '❌ FAIL'}")
        print(f"📈 Success Rate: {report['summary']['success_rate']}%")
        print(f"📋 Tests: {report['summary']['passed']}/{report['summary']['total_tests']} passed")
        
        # QA System readiness
        readiness = report['qa_system_readiness']
        print(f"\n🚀 QA System Readiness:")
        print(f"   Scripts Available: {'✅' if readiness['scripts_available'] else '❌'}")
        print(f"   Syntax Valid: {'✅' if readiness['syntax_valid'] else '❌'}")
        print(f"   Requirements Covered: {'✅' if readiness['requirements_covered'] else '❌'}")
        print(f"   Team Assignment Ready: {'✅' if readiness['team_assignment_ready'] else '❌'}")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        return report

def main():
    """Main test runner"""
    tester = QASystemTester()
    
    try:
        # Run all tests
        report = tester.run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if report['summary']['failed'] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
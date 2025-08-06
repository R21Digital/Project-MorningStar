#!/usr/bin/env python3
"""
QA Dashboard - Comprehensive QA orchestration and reporting system
Batch 199 - Phase 1 QA Pass & Bug Review
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import concurrent.futures
from collections import defaultdict

class QADashboard:
    """Comprehensive QA testing orchestration and reporting dashboard"""
    
    def __init__(self, base_url: str = None, build_dir: str = "dist"):
        self.base_url = base_url or "https://morningstar.swg.ms11.com"
        self.build_dir = build_dir
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = Path(__file__).parent
        
        # QA test modules
        self.qa_modules = {
            'link_checker': {
                'script': 'qa_link_checker.py',
                'name': 'Link Checker',
                'description': 'Validates all internal and external links',
                'priority': 'high',
                'estimated_time': 300  # seconds
            },
            'visual_scanner': {
                'script': 'qa_visual_scanner.py',
                'name': 'Visual Bug Scanner',
                'description': 'Detects UI issues and visual bugs',
                'priority': 'high',
                'estimated_time': 180
            },
            'metadata_validator': {
                'script': 'qa_metadata_validator.py',
                'name': 'Metadata Validator',
                'description': 'Validates images and metadata completeness',
                'priority': 'medium',
                'estimated_time': 120
            },
            'responsive_tester': {
                'script': 'qa_responsive_tester.py',
                'name': 'Responsive Tester',
                'description': 'Tests mobile vs desktop compatibility',
                'priority': 'high',
                'estimated_time': 90
            },
            'browser_tester': {
                'script': 'qa_browser_tester.py',
                'name': 'Cross-Browser Tester',
                'description': 'Validates cross-browser compatibility',
                'priority': 'medium',
                'estimated_time': 150
            }
        }
        
        # Test results storage
        self.test_results = {}
        self.overall_status = "unknown"
        self.start_time = None
        self.end_time = None
        
        # Issues tracking
        self.critical_issues = []
        self.high_issues = []
        self.medium_issues = []
        self.low_issues = []
        self.warnings = []
        
        # Team assignment tracking
        self.team_assignments = {
            'frontend_dev': ['visual_scanner', 'responsive_tester'],
            'backend_dev': ['link_checker'],
            'qa_engineer': ['metadata_validator', 'browser_tester'],
            'designer': ['visual_scanner', 'responsive_tester'],
            'devops': ['link_checker', 'browser_tester']
        }
    
    def log_message(self, level: str, message: str, details: Dict[str, Any] = None):
        """Log QA dashboard messages"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        level_emoji = {
            'INFO': '📋',
            'WARN': '⚠️',
            'ERROR': '❌',
            'SUCCESS': '✅',
            'DEBUG': '🔍'
        }.get(level, '📋')
        
        print(f"{level_emoji} [{timestamp}] {message}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def check_script_availability(self) -> Dict[str, bool]:
        """Check if all QA scripts are available"""
        availability = {}
        
        for module_id, module_info in self.qa_modules.items():
            script_path = self.scripts_dir / module_info['script']
            availability[module_id] = script_path.exists()
            
            if not script_path.exists():
                self.log_message('WARN', f"QA script not found: {module_info['script']}")
        
        return availability
    
    def run_qa_module(self, module_id: str, args: List[str] = None) -> Dict[str, Any]:
        """Run a single QA module and capture results"""
        module_info = self.qa_modules[module_id]
        script_path = self.scripts_dir / module_info['script']
        
        if not script_path.exists():
            return {
                'module_id': module_id,
                'status': 'error',
                'error': f"Script not found: {module_info['script']}",
                'duration': 0,
                'timestamp': datetime.now().isoformat()
            }
        
        self.log_message('INFO', f"Starting {module_info['name']}...")
        
        start_time = time.time()
        
        try:
            # Prepare command
            cmd = [sys.executable, str(script_path)]
            if args:
                cmd.extend(args)
            
            # Add common arguments
            cmd.extend([
                '--base-url', self.base_url,
                '--build-dir', self.build_dir
            ])
            
            # Run the QA module
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=module_info['estimated_time'] + 60,  # Add buffer time
                cwd=self.project_root
            )
            
            duration = time.time() - start_time
            
            # Parse output for key information
            output_lines = result.stdout.split('\n') if result.stdout else []
            error_lines = result.stderr.split('\n') if result.stderr else []
            
            # Look for generated report files
            report_files = []
            report_patterns = [
                f"QA_{module_id.upper()}_*_REPORT_*.json",
                f"*{module_id}*REPORT*.json"
            ]
            
            for pattern in report_patterns:
                report_files.extend(self.project_root.glob(pattern))
            
            # Load the most recent report if available
            report_data = None
            if report_files:
                latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
                try:
                    with open(latest_report, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                except Exception as e:
                    self.log_message('WARN', f"Could not parse report: {str(e)}")
            
            module_result = {
                'module_id': module_id,
                'name': module_info['name'],
                'status': 'pass' if result.returncode == 0 else 'fail',
                'return_code': result.returncode,
                'duration': round(duration, 2),
                'timestamp': datetime.now().isoformat(),
                'output': output_lines,
                'errors': error_lines,
                'report_file': str(latest_report) if report_files else None,
                'report_data': report_data
            }
            
            if result.returncode == 0:
                self.log_message('SUCCESS', f"{module_info['name']} completed successfully",
                               {"duration": f"{duration:.1f}s"})
            else:
                self.log_message('ERROR', f"{module_info['name']} failed",
                               {"return_code": result.returncode, "duration": f"{duration:.1f}s"})
            
            return module_result
        
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            self.log_message('ERROR', f"{module_info['name']} timed out",
                           {"timeout": f"{duration:.1f}s"})
            
            return {
                'module_id': module_id,
                'name': module_info['name'],
                'status': 'timeout',
                'duration': round(duration, 2),
                'timestamp': datetime.now().isoformat(),
                'error': f"Test timed out after {duration:.1f} seconds"
            }
        
        except Exception as e:
            duration = time.time() - start_time
            self.log_message('ERROR', f"{module_info['name']} error: {str(e)}")
            
            return {
                'module_id': module_id,
                'name': module_info['name'],
                'status': 'error',
                'duration': round(duration, 2),
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def run_qa_modules_parallel(self, module_ids: List[str], max_workers: int = 3) -> Dict[str, Any]:
        """Run multiple QA modules in parallel"""
        self.log_message('INFO', f"Running {len(module_ids)} QA modules in parallel...")
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all modules
            future_to_module = {
                executor.submit(self.run_qa_module, module_id): module_id
                for module_id in module_ids
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_module):
                module_id = future_to_module[future]
                try:
                    result = future.result()
                    results[module_id] = result
                except Exception as e:
                    self.log_message('ERROR', f"Parallel execution error for {module_id}: {str(e)}")
                    results[module_id] = {
                        'module_id': module_id,
                        'status': 'error',
                        'error': f"Parallel execution error: {str(e)}",
                        'duration': 0,
                        'timestamp': datetime.now().isoformat()
                    }
        
        return results
    
    def run_qa_modules_sequential(self, module_ids: List[str]) -> Dict[str, Any]:
        """Run QA modules sequentially"""
        self.log_message('INFO', f"Running {len(module_ids)} QA modules sequentially...")
        
        results = {}
        
        for module_id in module_ids:
            result = self.run_qa_module(module_id)
            results[module_id] = result
            
            # Short pause between modules
            time.sleep(2)
        
        return results
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze all QA test results and categorize issues"""
        analysis = {
            'overall_status': 'unknown',
            'total_modules': len(self.test_results),
            'passed_modules': 0,
            'failed_modules': 0,
            'error_modules': 0,
            'timeout_modules': 0,
            'total_duration': 0,
            'issue_summary': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'warnings': 0
            },
            'by_category': defaultdict(int),
            'team_focus_areas': defaultdict(list)
        }
        
        for module_id, result in self.test_results.items():
            analysis['total_duration'] += result.get('duration', 0)
            
            # Count module statuses
            status = result.get('status', 'unknown')
            if status == 'pass':
                analysis['passed_modules'] += 1
            elif status == 'fail':
                analysis['failed_modules'] += 1
            elif status == 'timeout':
                analysis['timeout_modules'] += 1
            else:
                analysis['error_modules'] += 1
            
            # Analyze report data if available
            report_data = result.get('report_data')
            if report_data:
                # Extract issues from different QA modules
                if 'broken_links' in report_data:
                    broken_count = report_data['broken_links'].get('total', 0)
                    if broken_count > 0:
                        analysis['by_category']['broken_links'] = broken_count
                        if broken_count > 10:
                            analysis['issue_summary']['high'] += broken_count
                        else:
                            analysis['issue_summary']['medium'] += broken_count
                
                if 'ui_issues' in report_data:
                    ui_issues = report_data['ui_issues'].get('total', 0)
                    if ui_issues > 0:
                        analysis['by_category']['ui_issues'] = ui_issues
                        analysis['issue_summary']['medium'] += ui_issues
                
                if 'missing_images' in report_data:
                    missing_images = report_data['missing_images'].get('count', 0)
                    if missing_images > 0:
                        analysis['by_category']['missing_images'] = missing_images
                        analysis['issue_summary']['high'] += missing_images
                
                if 'responsive_issues' in report_data:
                    responsive_issues = report_data.get('issues_found', {}).get('responsive_issues', 0)
                    if responsive_issues > 0:
                        analysis['by_category']['responsive_issues'] = responsive_issues
                        analysis['issue_summary']['medium'] += responsive_issues
                
                if 'browser_scores' in report_data:
                    # Analyze browser compatibility scores
                    scores = report_data['browser_scores']
                    low_scores = [browser for browser, data in scores.items() if data['score'] < 70]
                    if low_scores:
                        analysis['by_category']['browser_compatibility'] = len(low_scores)
                        analysis['issue_summary']['medium'] += len(low_scores)
        
        # Determine overall status
        if analysis['error_modules'] > 0 or analysis['timeout_modules'] > 0:
            analysis['overall_status'] = 'error'
        elif analysis['failed_modules'] > 0:
            analysis['overall_status'] = 'fail'
        elif analysis['passed_modules'] == analysis['total_modules']:
            analysis['overall_status'] = 'pass'
        else:
            analysis['overall_status'] = 'partial'
        
        # Assign focus areas to teams
        for team, modules in self.team_assignments.items():
            team_issues = []
            for module_id in modules:
                if module_id in self.test_results:
                    result = self.test_results[module_id]
                    if result.get('status') != 'pass':
                        team_issues.append(result.get('name', module_id))
            
            if team_issues:
                analysis['team_focus_areas'][team] = team_issues
        
        return analysis
    
    def generate_team_assignments(self, analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate specific task assignments for team members"""
        assignments = defaultdict(list)
        
        # Assign based on issues found
        for module_id, result in self.test_results.items():
            if result.get('status') != 'pass':
                module_name = result.get('name', module_id)
                
                # Assign to appropriate team members
                if module_id == 'link_checker':
                    assignments['Backend Developer'].append(f"Fix broken links found in {module_name}")
                    assignments['Content Team'].append("Review and update outdated external links")
                
                elif module_id == 'visual_scanner':
                    assignments['Frontend Developer'].append(f"Address UI issues found in {module_name}")
                    assignments['UX Designer'].append("Review visual inconsistencies and layout issues")
                
                elif module_id == 'metadata_validator':
                    assignments['Frontend Developer'].append("Add missing images and optimize existing ones")
                    assignments['SEO Specialist'].append("Complete missing metadata tags")
                
                elif module_id == 'responsive_tester':
                    assignments['Frontend Developer'].append("Fix responsive design issues")
                    assignments['UX Designer'].append("Review mobile user experience")
                
                elif module_id == 'browser_tester':
                    assignments['Frontend Developer'].append("Add browser compatibility fixes")
                    assignments['QA Engineer'].append("Test fixes across different browsers")
        
        # Add general assignments based on issue categories
        if analysis['by_category']['broken_links'] > 5:
            assignments['Project Manager'].append("Coordinate link maintenance process")
        
        if analysis['issue_summary']['critical'] > 0:
            assignments['Tech Lead'].append("Review and prioritize critical issues")
        
        return dict(assignments)
    
    def run_comprehensive_qa(self, parallel: bool = True, modules: List[str] = None) -> Dict[str, Any]:
        """Run comprehensive QA testing across all modules"""
        print("🔍 Starting Comprehensive QA Testing Suite")
        print("Batch 199 - Phase 1 QA Pass & Bug Review")
        print("=" * 70)
        
        self.start_time = datetime.now()
        
        # Check script availability
        self.log_message('INFO', "Checking QA script availability...")
        availability = self.check_script_availability()
        
        available_modules = [mod_id for mod_id, available in availability.items() if available]
        unavailable_modules = [mod_id for mod_id, available in availability.items() if not available]
        
        if unavailable_modules:
            self.log_message('WARN', f"Some QA modules unavailable: {', '.join(unavailable_modules)}")
        
        # Use specified modules or all available modules
        modules_to_run = modules if modules else available_modules
        
        if not modules_to_run:
            self.log_message('ERROR', "No QA modules available to run")
            return self.generate_final_report()
        
        self.log_message('INFO', f"Running QA modules: {', '.join(modules_to_run)}")
        
        # Estimate total time
        estimated_time = sum(self.qa_modules[mod]['estimated_time'] for mod in modules_to_run)
        if parallel:
            estimated_time = estimated_time // 3  # Rough parallel speedup
        
        self.log_message('INFO', f"Estimated completion time: {estimated_time // 60}m {estimated_time % 60}s")
        
        # Run QA modules
        if parallel and len(modules_to_run) > 1:
            self.test_results = self.run_qa_modules_parallel(modules_to_run)
        else:
            self.test_results = self.run_qa_modules_sequential(modules_to_run)
        
        self.end_time = datetime.now()
        
        # Analyze results
        self.log_message('INFO', "Analyzing QA results...")
        analysis = self.analyze_results()
        
        # Generate team assignments
        team_assignments = self.generate_team_assignments(analysis)
        
        # Generate final report
        final_report = self.generate_final_report(analysis, team_assignments)
        
        # Print summary
        self.print_qa_summary(final_report)
        
        return final_report
    
    def generate_final_report(self, analysis: Dict[str, Any] = None, team_assignments: Dict[str, List[str]] = None) -> Dict[str, Any]:
        """Generate comprehensive final QA report"""
        if analysis is None:
            analysis = self.analyze_results()
        
        total_duration = (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0
        
        report = {
            'batch_id': 'BATCH_199',
            'test_name': 'Comprehensive QA Testing Suite',
            'timestamp': datetime.now().isoformat(),
            'execution': {
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'total_duration': round(total_duration, 2),
                'modules_run': len(self.test_results)
            },
            'overall_status': analysis.get('overall_status', 'unknown'),
            'summary': analysis,
            'module_results': self.test_results,
            'team_assignments': team_assignments or {},
            'qa_modules_info': self.qa_modules,
            'recommendations': [],
            'next_steps': []
        }
        
        # Add recommendations based on results
        if analysis['overall_status'] == 'pass':
            report['recommendations'].append("✅ All QA checks passed - ready for launch!")
        elif analysis['overall_status'] == 'fail':
            report['recommendations'].append("🔧 Address failed QA checks before launch")
        elif analysis['overall_status'] == 'error':
            report['recommendations'].append("🚨 Resolve QA system errors and re-run tests")
        
        # Specific recommendations
        if analysis['by_category'].get('broken_links', 0) > 0:
            report['recommendations'].append(f"🔗 Fix {analysis['by_category']['broken_links']} broken links")
        
        if analysis['by_category'].get('ui_issues', 0) > 0:
            report['recommendations'].append(f"🎨 Address {analysis['by_category']['ui_issues']} UI issues")
        
        if analysis['by_category'].get('missing_images', 0) > 0:
            report['recommendations'].append(f"🖼️ Add {analysis['by_category']['missing_images']} missing images")
        
        if analysis['by_category'].get('responsive_issues', 0) > 0:
            report['recommendations'].append(f"📱 Fix {analysis['by_category']['responsive_issues']} responsive design issues")
        
        if analysis['by_category'].get('browser_compatibility', 0) > 0:
            report['recommendations'].append(f"🌐 Improve compatibility for {analysis['by_category']['browser_compatibility']} browsers")
        
        # Next steps
        if team_assignments:
            report['next_steps'].append("👥 Assign tasks to team members as specified")
        
        report['next_steps'].append("🧪 Re-run QA tests after fixes")
        report['next_steps'].append("📋 Update QA checklist with any new findings")
        
        if analysis['overall_status'] in ['pass', 'partial']:
            report['next_steps'].append("🚀 Proceed with launch preparation")
        
        # Save comprehensive report
        report_file = f"QA_COMPREHENSIVE_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log_message('SUCCESS', f"Comprehensive QA report saved: {report_file}")
        
        return report
    
    def print_qa_summary(self, report: Dict[str, Any]):
        """Print QA testing summary"""
        print("\n" + "=" * 70)
        print("🎯 QA TESTING SUMMARY")
        print("=" * 70)
        
        summary = report['summary']
        execution = report['execution']
        
        # Overall status
        status_emoji = {
            'pass': '✅',
            'fail': '❌',
            'error': '🚨',
            'partial': '⚠️',
            'unknown': '❓'
        }.get(report['overall_status'], '❓')
        
        print(f"\n{status_emoji} Overall Status: {report['overall_status'].upper()}")
        print(f"⏱️ Total Duration: {execution['total_duration']:.1f} seconds")
        print(f"🔧 Modules Run: {execution['modules_run']}")
        
        # Module results
        print(f"\n📊 Module Results:")
        print(f"   ✅ Passed: {summary['passed_modules']}")
        print(f"   ❌ Failed: {summary['failed_modules']}")
        print(f"   🚨 Errors: {summary['error_modules']}")
        print(f"   ⏰ Timeouts: {summary['timeout_modules']}")
        
        # Issue summary
        if any(summary['issue_summary'].values()):
            print(f"\n🐛 Issues Found:")
            issue_summary = summary['issue_summary']
            if issue_summary['critical'] > 0:
                print(f"   🚨 Critical: {issue_summary['critical']}")
            if issue_summary['high'] > 0:
                print(f"   🔴 High: {issue_summary['high']}")
            if issue_summary['medium'] > 0:
                print(f"   🟡 Medium: {issue_summary['medium']}")
            if issue_summary['low'] > 0:
                print(f"   🟢 Low: {issue_summary['low']}")
            if issue_summary['warnings'] > 0:
                print(f"   ⚠️ Warnings: {issue_summary['warnings']}")
        
        # Issue categories
        if summary['by_category']:
            print(f"\n📋 Issues by Category:")
            for category, count in summary['by_category'].items():
                print(f"   • {category.replace('_', ' ').title()}: {count}")
        
        # Team assignments
        if report['team_assignments']:
            print(f"\n👥 Team Assignments:")
            for team, tasks in report['team_assignments'].items():
                print(f"   {team}:")
                for task in tasks:
                    print(f"     • {task}")
        
        # Recommendations
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        
        # Next steps
        if report['next_steps']:
            print(f"\n📋 Next Steps:")
            for step in report['next_steps']:
                print(f"   {step}")
        
        print("\n" + "=" * 70)

def main():
    """Main QA dashboard runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive QA Dashboard')
    parser.add_argument('--base-url', default='https://morningstar.swg.ms11.com',
                       help='Base URL for the site')
    parser.add_argument('--build-dir', default='dist',
                       help='Build directory to test')
    parser.add_argument('--parallel', action='store_true', default=True,
                       help='Run QA modules in parallel')
    parser.add_argument('--sequential', action='store_true',
                       help='Run QA modules sequentially')
    parser.add_argument('--modules', nargs='+',
                       choices=['link_checker', 'visual_scanner', 'metadata_validator', 'responsive_tester', 'browser_tester'],
                       help='Specific modules to run')
    
    args = parser.parse_args()
    
    # Handle parallel/sequential flag
    parallel = args.parallel and not args.sequential
    
    dashboard = QADashboard(base_url=args.base_url, build_dir=args.build_dir)
    
    try:
        report = dashboard.run_comprehensive_qa(parallel=parallel, modules=args.modules)
        
        # Exit with appropriate code based on overall status
        exit_codes = {
            'pass': 0,
            'partial': 1,
            'fail': 2,
            'error': 3,
            'unknown': 4
        }
        
        exit_code = exit_codes.get(report['overall_status'], 4)
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️ QA testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ QA dashboard failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
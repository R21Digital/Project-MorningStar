#!/usr/bin/env python3
"""
QA Responsive Tester - Mobile vs Desktop UI comparison system
Batch 199 - Phase 1 QA Pass & Bug Review
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
import re

class ResponsiveTester:
    """Mobile vs Desktop UI comparison and responsive design validation"""
    
    def __init__(self, build_dir: str = "dist", base_url: str = None):
        self.build_dir = Path(build_dir)
        self.project_root = Path(__file__).parent.parent
        self.base_url = base_url or "https://morningstar.swg.ms11.com"
        self.results = []
        
        # Device breakpoints (common responsive breakpoints)
        self.breakpoints = {
            'mobile': {'min_width': 320, 'max_width': 767, 'name': 'Mobile'},
            'tablet': {'min_width': 768, 'max_width': 1023, 'name': 'Tablet'},
            'desktop': {'min_width': 1024, 'max_width': 1440, 'name': 'Desktop'},
            'large_desktop': {'min_width': 1441, 'max_width': 1920, 'name': 'Large Desktop'}
        }
        
        # Common viewport sizes to test
        self.test_viewports = [
            {'width': 375, 'height': 667, 'name': 'iPhone SE', 'device_type': 'mobile'},
            {'width': 414, 'height': 896, 'name': 'iPhone 11 Pro Max', 'device_type': 'mobile'},
            {'width': 768, 'height': 1024, 'name': 'iPad', 'device_type': 'tablet'},
            {'width': 1024, 'height': 768, 'name': 'iPad Landscape', 'device_type': 'tablet'},
            {'width': 1280, 'height': 720, 'name': 'Desktop Small', 'device_type': 'desktop'},
            {'width': 1920, 'height': 1080, 'name': 'Desktop Large', 'device_type': 'desktop'}
        ]
        
        # Responsive design issues
        self.responsive_issues = []
        self.layout_problems = []
        self.readability_issues = []
        self.navigation_problems = []
        self.performance_issues = []
        
        # CSS patterns that indicate responsive design
        self.responsive_patterns = {
            'media_queries': r'@media\s*\([^}]+\)',
            'flexible_layouts': r'(display:\s*flex|display:\s*grid)',
            'relative_units': r'(\d+(?:\.\d+)?(?:em|rem|%|vw|vh|vmin|vmax))',
            'max_width': r'max-width:\s*\d+(?:px|em|rem|%)',
            'min_width': r'min-width:\s*\d+(?:px|em|rem|%)',
            'viewport_units': r'\d+(?:vw|vh|vmin|vmax)',
            'responsive_images': r'(max-width:\s*100%|width:\s*100%)',
            'container_queries': r'@container\s*\([^}]+\)'
        }
    
    def log_result(self, category: str, test_name: str, status: str, details: Dict[str, Any] = None):
        """Log validation result"""
        result = {
            'category': category,
            'test_name': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} [{category}] {test_name}: {status}")
        if details and details.get('file'):
            print(f"   File: {details['file']}")
        if details and details.get('issue'):
            print(f"   Issue: {details['issue']}")
    
    def discover_files(self) -> Tuple[List[Path], List[Path]]:
        """Discover HTML and CSS files for responsive testing"""
        html_files = []
        css_files = []
        
        # HTML files
        if self.build_dir.exists():
            html_files.extend(self.build_dir.rglob("*.html"))
        
        src_pages = self.project_root / "src/pages"
        if src_pages.exists():
            html_files.extend(src_pages.rglob("*.html"))
            html_files.extend(src_pages.rglob("*.njk"))
        
        # CSS files
        if self.build_dir.exists():
            css_files.extend(self.build_dir.rglob("*.css"))
        
        src_styles = self.project_root / "src/styles"
        if src_styles.exists():
            css_files.extend(src_styles.rglob("*.css"))
        
        return list(set(html_files)), list(set(css_files))
    
    def analyze_css_responsive_patterns(self, css_files: List[Path]) -> Dict[str, Any]:
        """Analyze CSS files for responsive design patterns"""
        analysis = {
            'media_queries': [],
            'flexible_layouts': [],
            'relative_units': [],
            'responsive_images': [],
            'breakpoints': set(),
            'issues': [],
            'best_practices': []
        }
        
        for css_file in css_files:
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find media queries
                media_queries = re.findall(self.responsive_patterns['media_queries'], content, re.DOTALL)
                analysis['media_queries'].extend([
                    {'file': str(css_file), 'query': mq.strip()} for mq in media_queries
                ])
                
                # Extract breakpoints from media queries
                breakpoint_pattern = r'(?:min-width|max-width):\s*(\d+)px'
                breakpoints = re.findall(breakpoint_pattern, content)
                analysis['breakpoints'].update([int(bp) for bp in breakpoints])
                
                # Check for flexible layouts
                if re.search(self.responsive_patterns['flexible_layouts'], content):
                    analysis['flexible_layouts'].append(str(css_file))
                
                # Check for relative units
                relative_units = re.findall(self.responsive_patterns['relative_units'], content)
                if relative_units:
                    analysis['relative_units'].append({
                        'file': str(css_file),
                        'count': len(relative_units)
                    })
                
                # Check for responsive images
                if re.search(self.responsive_patterns['responsive_images'], content):
                    analysis['responsive_images'].append(str(css_file))
                
                # Check for common issues
                # Too many fixed pixel values
                fixed_values = re.findall(r'\d+px', content)
                if len(fixed_values) > 100:
                    analysis['issues'].append({
                        'file': str(css_file),
                        'issue': f'Many fixed pixel values ({len(fixed_values)}) - may not be responsive',
                        'severity': 'medium'
                    })
                
                # Missing viewport meta tag support
                if not re.search(r'viewport|device-width', content):
                    analysis['issues'].append({
                        'file': str(css_file),
                        'issue': 'No viewport-related CSS found',
                        'severity': 'low'
                    })
                
                # Best practices found
                if '@media' in content:
                    analysis['best_practices'].append(f'{css_file.name}: Uses media queries')
                
                if re.search(r'display:\s*flex', content):
                    analysis['best_practices'].append(f'{css_file.name}: Uses Flexbox')
                
                if re.search(r'display:\s*grid', content):
                    analysis['best_practices'].append(f'{css_file.name}: Uses CSS Grid')
            
            except Exception as e:
                analysis['issues'].append({
                    'file': str(css_file),
                    'issue': f'Parse error: {str(e)}',
                    'severity': 'high'
                })
        
        return analysis
    
    def validate_html_responsive_structure(self, html_files: List[Path]) -> Dict[str, Any]:
        """Validate HTML structure for responsive design"""
        validation = {
            'viewport_meta': [],
            'responsive_images': [],
            'flexible_containers': [],
            'navigation_patterns': [],
            'issues': [],
            'recommendations': []
        }
        
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip non-HTML files
                if html_file.suffix not in ['.html', '.htm']:
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Check viewport meta tag
                viewport = soup.find('meta', attrs={'name': 'viewport'})
                if viewport:
                    viewport_content = viewport.get('content', '')
                    validation['viewport_meta'].append({
                        'file': str(html_file),
                        'content': viewport_content,
                        'valid': 'width=device-width' in viewport_content
                    })
                    
                    if 'width=device-width' not in viewport_content:
                        validation['issues'].append({
                            'file': str(html_file),
                            'issue': 'Viewport meta tag missing width=device-width',
                            'severity': 'high'
                        })
                else:
                    validation['issues'].append({
                        'file': str(html_file),
                        'issue': 'Missing viewport meta tag',
                        'severity': 'high'
                    })
                
                # Check responsive images
                images = soup.find_all('img')
                responsive_img_count = 0
                
                for img in images:
                    srcset = img.get('srcset')
                    sizes = img.get('sizes')
                    style = img.get('style', '')
                    
                    if srcset or sizes or 'max-width' in style or 'width: 100%' in style:
                        responsive_img_count += 1
                
                if images:
                    validation['responsive_images'].append({
                        'file': str(html_file),
                        'total_images': len(images),
                        'responsive_images': responsive_img_count,
                        'percentage': (responsive_img_count / len(images)) * 100
                    })
                    
                    if responsive_img_count < len(images) * 0.5:
                        validation['issues'].append({
                            'file': str(html_file),
                            'issue': f'Only {responsive_img_count}/{len(images)} images are responsive',
                            'severity': 'medium'
                        })
                
                # Check for flexible containers
                container_classes = ['container', 'wrapper', 'flex', 'grid', 'row', 'col']
                flexible_containers = 0
                
                for class_name in container_classes:
                    elements = soup.find_all(attrs={'class': lambda x: x and class_name in ' '.join(x)})
                    flexible_containers += len(elements)
                
                validation['flexible_containers'].append({
                    'file': str(html_file),
                    'count': flexible_containers
                })
                
                # Check navigation patterns
                nav_elements = soup.find_all(['nav', 'header'])
                mobile_nav_indicators = ['menu', 'hamburger', 'toggle', 'mobile']
                
                has_mobile_nav = False
                for nav in nav_elements:
                    nav_text = nav.get_text().lower()
                    nav_classes = ' '.join(nav.get('class', [])).lower()
                    
                    if any(indicator in nav_text or indicator in nav_classes for indicator in mobile_nav_indicators):
                        has_mobile_nav = True
                        break
                
                validation['navigation_patterns'].append({
                    'file': str(html_file),
                    'nav_elements': len(nav_elements),
                    'mobile_nav_detected': has_mobile_nav
                })
                
                if nav_elements and not has_mobile_nav:
                    validation['recommendations'].append({
                        'file': str(html_file),
                        'recommendation': 'Consider adding mobile navigation pattern'
                    })
                
                # Check for tables that need responsive treatment
                tables = soup.find_all('table')
                if tables:
                    responsive_tables = 0
                    for table in tables:
                        table_classes = ' '.join(table.get('class', [])).lower()
                        if 'responsive' in table_classes or 'table-responsive' in table_classes:
                            responsive_tables += 1
                    
                    if responsive_tables < len(tables):
                        validation['issues'].append({
                            'file': str(html_file),
                            'issue': f'{len(tables) - responsive_tables} tables may not be mobile-friendly',
                            'severity': 'medium'
                        })
                
                # Check for fixed-width elements
                fixed_width_pattern = r'width:\s*\d+px'
                if re.search(fixed_width_pattern, content):
                    validation['issues'].append({
                        'file': str(html_file),
                        'issue': 'Fixed pixel widths found in inline styles',
                        'severity': 'low'
                    })
            
            except Exception as e:
                validation['issues'].append({
                    'file': str(html_file),
                    'issue': f'Parse error: {str(e)}',
                    'severity': 'high'
                })
        
        return validation
    
    def simulate_viewport_tests(self, html_files: List[Path]) -> Dict[str, Any]:
        """Simulate different viewport sizes and identify potential issues"""
        simulation = {
            'viewport_tests': [],
            'potential_issues': [],
            'layout_warnings': []
        }
        
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if html_file.suffix not in ['.html', '.htm']:
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                
                for viewport in self.test_viewports:
                    test_result = {
                        'file': str(html_file),
                        'viewport': viewport,
                        'issues': [],
                        'warnings': []
                    }
                    
                    # Simulate common responsive issues
                    # Check for elements that might overflow
                    fixed_width_elements = soup.find_all(attrs={'style': lambda x: x and 'width:' in x})
                    for element in fixed_width_elements:
                        style = element.get('style', '')
                        width_match = re.search(r'width:\s*(\d+)px', style)
                        if width_match:
                            width = int(width_match.group(1))
                            if width > viewport['width']:
                                test_result['issues'].append(
                                    f"Element width ({width}px) exceeds viewport ({viewport['width']}px)"
                                )
                    
                    # Check for small text that might be hard to read on mobile
                    if viewport['device_type'] == 'mobile':
                        style_tags = soup.find_all('style')
                        for style_tag in style_tags:
                            font_sizes = re.findall(r'font-size:\s*(\d+)px', style_tag.get_text())
                            for size in font_sizes:
                                if int(size) < 14:
                                    test_result['warnings'].append(
                                        f"Small font size ({size}px) may be hard to read on mobile"
                                    )
                    
                    # Check for touch targets that might be too small
                    if viewport['device_type'] == 'mobile':
                        buttons = soup.find_all(['button', 'a', 'input'])
                        for button in buttons:
                            style = button.get('style', '')
                            # This is a basic check - would need more sophisticated analysis
                            if 'padding' not in style and len(button.get_text(strip=True)) < 3:
                                test_result['warnings'].append(
                                    "Small interactive element may be hard to tap on mobile"
                                )
                    
                    # Check for horizontal scrolling issues
                    if viewport['device_type'] in ['mobile', 'tablet']:
                        wide_elements = soup.find_all(attrs={'style': lambda x: x and 'min-width:' in x})
                        for element in wide_elements:
                            style = element.get('style', '')
                            min_width_match = re.search(r'min-width:\s*(\d+)px', style)
                            if min_width_match:
                                min_width = int(min_width_match.group(1))
                                if min_width > viewport['width']:
                                    test_result['issues'].append(
                                        f"Element min-width ({min_width}px) may cause horizontal scrolling"
                                    )
                    
                    simulation['viewport_tests'].append(test_result)
                    
                    # Collect issues for summary
                    if test_result['issues']:
                        simulation['potential_issues'].extend(test_result['issues'])
                    
                    if test_result['warnings']:
                        simulation['layout_warnings'].extend(test_result['warnings'])
            
            except Exception as e:
                continue
        
        return simulation
    
    def check_responsive_frameworks(self, html_files: List[Path], css_files: List[Path]) -> Dict[str, Any]:
        """Check for responsive CSS frameworks and their implementation"""
        framework_check = {
            'frameworks_detected': [],
            'implementation_quality': [],
            'recommendations': []
        }
        
        # Common responsive frameworks
        frameworks = {
            'bootstrap': ['bootstrap', 'bs-', 'col-', 'row'],
            'foundation': ['foundation', 'small-', 'medium-', 'large-'],
            'bulma': ['bulma', 'column', 'columns', 'tile'],
            'tailwind': ['tailwind', 'sm:', 'md:', 'lg:', 'xl:'],
            'materialize': ['materialize', 'col', 's1', 'm1', 'l1'],
            'semantic-ui': ['ui', 'stackable', 'doubling'],
            'pure': ['pure-', 'pure-g', 'pure-u']
        }
        
        # Check HTML files for framework classes
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if html_file.suffix not in ['.html', '.htm']:
                    continue
                
                detected_frameworks = []
                
                for framework, indicators in frameworks.items():
                    for indicator in indicators:
                        if indicator in content:
                            if framework not in detected_frameworks:
                                detected_frameworks.append(framework)
                                break
                
                if detected_frameworks:
                    framework_check['frameworks_detected'].append({
                        'file': str(html_file),
                        'frameworks': detected_frameworks
                    })
            
            except Exception as e:
                continue
        
        # Check CSS files for framework imports
        for css_file in css_files:
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for framework imports
                if '@import' in content:
                    imports = re.findall(r'@import\s+["\']([^"\']+)["\']', content)
                    for imp in imports:
                        for framework in frameworks.keys():
                            if framework in imp.lower():
                                framework_check['frameworks_detected'].append({
                                    'file': str(css_file),
                                    'framework': framework,
                                    'import': imp
                                })
            
            except Exception as e:
                continue
        
        # Analyze implementation quality
        if framework_check['frameworks_detected']:
            framework_check['recommendations'].append(
                "Framework detected - ensure proper responsive implementation"
            )
        else:
            framework_check['recommendations'].append(
                "No responsive framework detected - consider using one for better mobile support"
            )
        
        return framework_check
    
    def run_responsive_testing(self) -> Dict[str, Any]:
        """Run comprehensive responsive design testing"""
        print("📱 Starting Responsive Design Tester")
        print("Batch 199 - Phase 1 QA Pass & Bug Review")
        print("=" * 60)
        
        # Discover files
        print("\n📁 Discovering files...")
        html_files, css_files = self.discover_files()
        
        self.log_result("Discovery", "HTML Files", "PASS" if html_files else "WARN",
                       {"count": len(html_files)})
        self.log_result("Discovery", "CSS Files", "PASS" if css_files else "WARN",
                       {"count": len(css_files)})
        
        # Analyze CSS responsive patterns
        print(f"\n🎨 Analyzing CSS responsive patterns...")
        css_analysis = self.analyze_css_responsive_patterns(css_files)
        
        # Report CSS analysis results
        if css_analysis['media_queries']:
            self.log_result("CSS Analysis", "Media Queries Found", "PASS",
                           {"count": len(css_analysis['media_queries'])})
        else:
            self.log_result("CSS Analysis", "Media Queries", "FAIL",
                           {"error": "No media queries found - site may not be responsive"})
        
        if css_analysis['flexible_layouts']:
            self.log_result("CSS Analysis", "Flexible Layouts", "PASS",
                           {"files": len(css_analysis['flexible_layouts'])})
        else:
            self.log_result("CSS Analysis", "Flexible Layouts", "WARN",
                           {"warning": "No flexible layout patterns found"})
        
        # Report CSS issues
        for issue in css_analysis['issues']:
            self.log_result("CSS Issues", f"{Path(issue['file']).name}", 
                           "FAIL" if issue['severity'] == 'high' else "WARN",
                           {"error": issue['issue'], "file": issue['file']})
        
        # Validate HTML responsive structure
        print(f"\n🏗️ Validating HTML responsive structure...")
        html_validation = self.validate_html_responsive_structure(html_files)
        
        # Report HTML validation results
        for issue in html_validation['issues']:
            self.log_result("HTML Structure", f"{Path(issue['file']).name}",
                           "FAIL" if issue['severity'] == 'high' else "WARN",
                           {"error": issue['issue'], "file": issue['file']})
        
        # Check viewport meta tags
        viewport_files = [v for v in html_validation['viewport_meta'] if v['valid']]
        if viewport_files:
            self.log_result("Viewport Meta", "Valid viewport tags found", "PASS",
                           {"count": len(viewport_files)})
        else:
            self.log_result("Viewport Meta", "No valid viewport tags", "FAIL",
                           {"error": "Missing or invalid viewport meta tags"})
        
        # Simulate viewport tests
        print(f"\n📐 Simulating viewport tests...")
        viewport_simulation = self.simulate_viewport_tests(html_files)
        
        if viewport_simulation['potential_issues']:
            for i, issue in enumerate(viewport_simulation['potential_issues'][:10]):  # Limit output
                self.log_result("Viewport Issues", f"Layout Issue {i+1}", "FAIL",
                               {"error": issue})
        else:
            self.log_result("Viewport Simulation", "No critical issues detected", "PASS")
        
        # Check for responsive frameworks
        print(f"\n🛠️ Checking for responsive frameworks...")
        framework_check = self.check_responsive_frameworks(html_files, css_files)
        
        if framework_check['frameworks_detected']:
            frameworks = set()
            for detection in framework_check['frameworks_detected']:
                if 'frameworks' in detection:
                    frameworks.update(detection['frameworks'])
                if 'framework' in detection:
                    frameworks.add(detection['framework'])
            
            self.log_result("Frameworks", "Responsive frameworks detected", "PASS",
                           {"frameworks": list(frameworks)})
        else:
            self.log_result("Frameworks", "No frameworks detected", "INFO",
                           {"note": "Using custom responsive CSS"})
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive responsive testing report"""
        print("\n📊 Generating Responsive Testing Report...")
        
        total_checks = len(self.results)
        passed_checks = len([r for r in self.results if r['status'] == 'PASS'])
        failed_checks = len([r for r in self.results if r['status'] == 'FAIL'])
        warning_checks = len([r for r in self.results if r['status'] in ['WARN', 'INFO']])
        
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        report = {
            'batch_id': 'BATCH_199',
            'test_name': 'Responsive Design Tester',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_checks': total_checks,
                'passed': passed_checks,
                'failed': failed_checks,
                'warnings': warning_checks,
                'success_rate': round(success_rate, 2)
            },
            'responsive_health': {
                'media_queries_found': failed_checks == 0,
                'viewport_configured': any(r['test_name'] == 'Valid viewport tags found' and r['status'] == 'PASS' for r in self.results),
                'flexible_layouts': any(r['test_name'] == 'Flexible Layouts' and r['status'] == 'PASS' for r in self.results),
                'framework_support': any(r['test_name'] == 'Responsive frameworks detected' and r['status'] == 'PASS' for r in self.results)
            },
            'issues_found': {
                'responsive_issues': len(self.responsive_issues),
                'layout_problems': len(self.layout_problems),
                'readability_issues': len(self.readability_issues),
                'navigation_problems': len(self.navigation_problems)
            },
            'detailed_results': self.results,
            'test_viewports': self.test_viewports,
            'recommendations': []
        }
        
        # Add recommendations based on results
        if failed_checks == 0:
            report['recommendations'].append("✅ Responsive design implementation looks good")
        
        if not report['responsive_health']['media_queries_found']:
            report['recommendations'].append("📱 Add media queries for responsive breakpoints")
        
        if not report['responsive_health']['viewport_configured']:
            report['recommendations'].append("🔧 Add proper viewport meta tag: <meta name='viewport' content='width=device-width, initial-scale=1'>")
        
        if not report['responsive_health']['flexible_layouts']:
            report['recommendations'].append("🏗️ Implement flexible layouts using Flexbox or CSS Grid")
        
        if failed_checks > 0:
            report['recommendations'].append(f"🐛 Fix {failed_checks} responsive design issues")
        
        if warning_checks > 0:
            report['recommendations'].append(f"⚠️ Address {warning_checks} responsive design warnings")
        
        # Save report
        report_file = f"QA_RESPONSIVE_TEST_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Responsive Testing Report saved to: {report_file}")
        return report

def main():
    """Main responsive tester runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Responsive Design Tester')
    parser.add_argument('--build-dir', default='dist',
                       help='Build directory to analyze')
    parser.add_argument('--base-url', default='https://morningstar.swg.ms11.com',
                       help='Base URL for the site')
    
    args = parser.parse_args()
    
    tester = ResponsiveTester(build_dir=args.build_dir, base_url=args.base_url)
    
    try:
        report = tester.run_responsive_testing()
        
        print("\n" + "=" * 60)
        print("🎯 Responsive Testing Complete!")
        print(f"📊 Success Rate: {report['summary']['success_rate']}%")
        print(f"📋 Checks: {report['summary']['passed']}/{report['summary']['total_checks']} passed")
        
        responsive_health = report['responsive_health']
        print(f"\n📱 Responsive Health Check:")
        print(f"   Media Queries: {'✅' if responsive_health['media_queries_found'] else '❌'}")
        print(f"   Viewport Config: {'✅' if responsive_health['viewport_configured'] else '❌'}")
        print(f"   Flexible Layouts: {'✅' if responsive_health['flexible_layouts'] else '❌'}")
        print(f"   Framework Support: {'✅' if responsive_health['framework_support'] else '❌'}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        
        # Exit with appropriate code
        sys.exit(0 if report['summary']['failed'] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Responsive testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Responsive testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
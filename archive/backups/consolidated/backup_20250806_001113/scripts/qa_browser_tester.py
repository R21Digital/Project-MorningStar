#!/usr/bin/env python3
"""
QA Browser Tester - Cross-browser rendering validation
Batch 199 - Phase 1 QA Pass & Bug Review
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import re

class BrowserTester:
    """Cross-browser rendering validation and compatibility testing"""
    
    def __init__(self, build_dir: str = "dist", base_url: str = None):
        self.build_dir = Path(build_dir)
        self.project_root = Path(__file__).parent.parent
        self.base_url = base_url or "https://morningstar.swg.ms11.com"
        self.results = []
        
        # Browser compatibility requirements
        self.target_browsers = {
            'chrome': {'min_version': 80, 'usage': 65.0, 'priority': 'high'},
            'firefox': {'min_version': 75, 'usage': 8.0, 'priority': 'high'},
            'safari': {'min_version': 13, 'usage': 15.0, 'priority': 'high'},
            'edge': {'min_version': 80, 'usage': 5.0, 'priority': 'medium'},
            'opera': {'min_version': 65, 'usage': 2.0, 'priority': 'low'},
            'ie11': {'min_version': 11, 'usage': 0.5, 'priority': 'low'}
        }
        
        # CSS features and their browser support
        self.css_features = {
            'flexbox': {
                'chrome': 29, 'firefox': 28, 'safari': 9, 'edge': 12, 'ie11': 11
            },
            'grid': {
                'chrome': 57, 'firefox': 52, 'safari': 10.1, 'edge': 16, 'ie11': None
            },
            'custom_properties': {
                'chrome': 49, 'firefox': 31, 'safari': 9.1, 'edge': 15, 'ie11': None
            },
            'transforms': {
                'chrome': 36, 'firefox': 16, 'safari': 9, 'edge': 12, 'ie11': 10
            },
            'transitions': {
                'chrome': 26, 'firefox': 16, 'safari': 6.1, 'edge': 12, 'ie11': 10
            },
            'animations': {
                'chrome': 43, 'firefox': 16, 'safari': 9, 'edge': 12, 'ie11': 10
            },
            'vh_vw_units': {
                'chrome': 26, 'firefox': 19, 'safari': 6.1, 'edge': 12, 'ie11': 9
            },
            'calc': {
                'chrome': 26, 'firefox': 16, 'safari': 6.1, 'edge': 12, 'ie11': 9
            },
            'media_queries': {
                'chrome': 1, 'firefox': 1, 'safari': 3.1, 'edge': 12, 'ie11': 9
            },
            'border_radius': {
                'chrome': 5, 'firefox': 4, 'safari': 5, 'edge': 12, 'ie11': 9
            }
        }
        
        # JavaScript features and their support
        self.js_features = {
            'es6_arrow_functions': {
                'chrome': 45, 'firefox': 22, 'safari': 10, 'edge': 12, 'ie11': None
            },
            'es6_const_let': {
                'chrome': 49, 'firefox': 36, 'safari': 10, 'edge': 12, 'ie11': 11
            },
            'es6_template_literals': {
                'chrome': 41, 'firefox': 34, 'safari': 9, 'edge': 12, 'ie11': None
            },
            'es6_promises': {
                'chrome': 33, 'firefox': 29, 'safari': 7.1, 'edge': 12, 'ie11': None
            },
            'fetch_api': {
                'chrome': 42, 'firefox': 39, 'safari': 10.1, 'edge': 14, 'ie11': None
            },
            'async_await': {
                'chrome': 55, 'firefox': 52, 'safari': 10.1, 'edge': 15, 'ie11': None
            }
        }
        
        # HTML5 features
        self.html5_features = {
            'semantic_elements': {
                'chrome': 5, 'firefox': 4, 'safari': 4.1, 'edge': 12, 'ie11': 9
            },
            'canvas': {
                'chrome': 4, 'firefox': 2, 'safari': 3.1, 'edge': 12, 'ie11': 9
            },
            'video': {
                'chrome': 4, 'firefox': 3.5, 'safari': 3.1, 'edge': 12, 'ie11': 9
            },
            'audio': {
                'chrome': 4, 'firefox': 3.5, 'safari': 3.1, 'edge': 12, 'ie11': 9
            },
            'local_storage': {
                'chrome': 4, 'firefox': 3.5, 'safari': 4, 'edge': 12, 'ie11': 8
            },
            'geolocation': {
                'chrome': 5, 'firefox': 3.5, 'safari': 5, 'edge': 12, 'ie11': 9
            }
        }
        
        # Compatibility issues found
        self.compatibility_issues = []
        self.unsupported_features = []
        self.vendor_prefix_needed = []
        self.polyfill_recommendations = []
    
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
    
    def discover_files(self) -> tuple[List[Path], List[Path], List[Path]]:
        """Discover HTML, CSS, and JS files for browser testing"""
        html_files = []
        css_files = []
        js_files = []
        
        # HTML files
        if self.build_dir.exists():
            html_files.extend(self.build_dir.rglob("*.html"))
            css_files.extend(self.build_dir.rglob("*.css"))
            js_files.extend(self.build_dir.rglob("*.js"))
        
        # Source files
        src_dir = self.project_root / "src"
        if src_dir.exists():
            html_files.extend(src_dir.rglob("*.html"))
            html_files.extend(src_dir.rglob("*.njk"))
            css_files.extend(src_dir.rglob("*.css"))
            js_files.extend(src_dir.rglob("*.js"))
        
        return list(set(html_files)), list(set(css_files)), list(set(js_files))
    
    def analyze_css_compatibility(self, css_files: List[Path]) -> Dict[str, Any]:
        """Analyze CSS files for browser compatibility issues"""
        analysis = {
            'features_used': [],
            'compatibility_issues': [],
            'vendor_prefixes_needed': [],
            'unsupported_in_target_browsers': []
        }
        
        # CSS properties that need vendor prefixes
        vendor_prefix_properties = {
            'transform': ['-webkit-transform', '-moz-transform', '-ms-transform'],
            'transition': ['-webkit-transition', '-moz-transition', '-ms-transition'],
            'animation': ['-webkit-animation', '-moz-animation', '-ms-animation'],
            'border-radius': ['-webkit-border-radius', '-moz-border-radius'],
            'box-shadow': ['-webkit-box-shadow', '-moz-box-shadow'],
            'user-select': ['-webkit-user-select', '-moz-user-select', '-ms-user-select'],
            'appearance': ['-webkit-appearance', '-moz-appearance'],
            'filter': ['-webkit-filter'],
            'backdrop-filter': ['-webkit-backdrop-filter']
        }
        
        for css_file in css_files:
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for CSS features
                for feature, browser_support in self.css_features.items():
                    feature_patterns = {
                        'flexbox': r'display:\s*flex',
                        'grid': r'display:\s*grid',
                        'custom_properties': r'var\(\s*--[\w-]+\s*\)',
                        'transforms': r'transform\s*:',
                        'transitions': r'transition\s*:',
                        'animations': r'animation\s*:',
                        'vh_vw_units': r'\d+(?:vh|vw)',
                        'calc': r'calc\s*\(',
                        'media_queries': r'@media',
                        'border_radius': r'border-radius\s*:'
                    }
                    
                    pattern = feature_patterns.get(feature)
                    if pattern and re.search(pattern, content, re.IGNORECASE):
                        analysis['features_used'].append({
                            'file': str(css_file),
                            'feature': feature,
                            'browser_support': browser_support
                        })
                        
                        # Check if feature is unsupported in target browsers
                        for browser, min_version in self.target_browsers.items():
                            if browser in browser_support:
                                required_version = browser_support[browser]
                                if required_version is None:
                                    analysis['unsupported_in_target_browsers'].append({
                                        'file': str(css_file),
                                        'feature': feature,
                                        'browser': browser,
                                        'issue': f'{feature} not supported in {browser}'
                                    })
                                elif required_version > min_version['min_version']:
                                    analysis['compatibility_issues'].append({
                                        'file': str(css_file),
                                        'feature': feature,
                                        'browser': browser,
                                        'required_version': required_version,
                                        'min_target_version': min_version['min_version']
                                    })
                
                # Check for vendor prefix needs
                for property_name, prefixes in vendor_prefix_properties.items():
                    if f'{property_name}:' in content:
                        has_prefixes = any(prefix in content for prefix in prefixes)
                        if not has_prefixes:
                            analysis['vendor_prefixes_needed'].append({
                                'file': str(css_file),
                                'property': property_name,
                                'needed_prefixes': prefixes
                            })
                
                # Check for modern CSS that might not work in older browsers
                modern_css_patterns = {
                    'css_grid': r'grid-template|grid-area|grid-column|grid-row',
                    'css_custom_properties': r'--[\w-]+\s*:',
                    'css_logical_properties': r'margin-inline|padding-block|border-inline',
                    'css_subgrid': r'grid-template.*subgrid',
                    'css_container_queries': r'@container',
                    'css_has_selector': r':has\(',
                    'css_cascade_layers': r'@layer'
                }
                
                for feature_name, pattern in modern_css_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        analysis['features_used'].append({
                            'file': str(css_file),
                            'feature': feature_name,
                            'note': 'Modern CSS feature - check browser support'
                        })
            
            except Exception as e:
                analysis['compatibility_issues'].append({
                    'file': str(css_file),
                    'error': f'Parse error: {str(e)}'
                })
        
        return analysis
    
    def analyze_js_compatibility(self, js_files: List[Path]) -> Dict[str, Any]:
        """Analyze JavaScript files for browser compatibility issues"""
        analysis = {
            'features_used': [],
            'compatibility_issues': [],
            'polyfills_needed': [],
            'es6_usage': []
        }
        
        for js_file in js_files:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for JavaScript features
                js_patterns = {
                    'es6_arrow_functions': r'=>',
                    'es6_const_let': r'\b(const|let)\s+',
                    'es6_template_literals': r'`[^`]*\$\{[^}]*\}[^`]*`',
                    'es6_promises': r'\b(Promise|\.then\(|\.catch\()',
                    'fetch_api': r'\bfetch\s*\(',
                    'async_await': r'\b(async\s+function|await\s+)',
                    'destructuring': r'\{[^}]*\}\s*=',
                    'spread_operator': r'\.\.\.',
                    'class_syntax': r'\bclass\s+\w+',
                    'for_of_loop': r'\bfor\s*\([^)]*\bof\b[^)]*\)',
                    'array_methods': r'\.(map|filter|reduce|find|forEach)\s*\(',
                    'object_assign': r'Object\.assign\s*\(',
                    'array_from': r'Array\.from\s*\(',
                    'includes_method': r'\.includes\s*\(',
                    'padstart_padend': r'\.(padStart|padEnd)\s*\('
                }
                
                for feature, pattern in js_patterns.items():
                    if re.search(pattern, content):
                        analysis['features_used'].append({
                            'file': str(js_file),
                            'feature': feature
                        })
                        
                        # Check browser support for this feature
                        if feature in self.js_features:
                            browser_support = self.js_features[feature]
                            
                            for browser, min_version in self.target_browsers.items():
                                if browser in browser_support:
                                    required_version = browser_support[browser]
                                    if required_version is None:
                                        analysis['polyfills_needed'].append({
                                            'file': str(js_file),
                                            'feature': feature,
                                            'browser': browser,
                                            'reason': f'{feature} not supported in {browser}'
                                        })
                                    elif required_version > min_version['min_version']:
                                        analysis['compatibility_issues'].append({
                                            'file': str(js_file),
                                            'feature': feature,
                                            'browser': browser,
                                            'required_version': required_version,
                                            'min_target_version': min_version['min_version']
                                        })
                
                # Check for jQuery usage (compatibility helper)
                if '$(' in content or 'jQuery(' in content:
                    analysis['features_used'].append({
                        'file': str(js_file),
                        'feature': 'jquery',
                        'note': 'jQuery detected - generally good for cross-browser compatibility'
                    })
                
                # Check for modern APIs that might need polyfills
                modern_apis = {
                    'intersection_observer': r'IntersectionObserver',
                    'mutation_observer': r'MutationObserver',
                    'web_components': r'customElements',
                    'service_worker': r'serviceWorker',
                    'web_workers': r'new Worker\(',
                    'websockets': r'new WebSocket\(',
                    'geolocation': r'navigator\.geolocation',
                    'file_api': r'FileReader|new File\(',
                    'canvas_api': r'getContext\(["\']2d["\']\)',
                    'local_storage': r'localStorage',
                    'session_storage': r'sessionStorage'
                }
                
                for api_name, pattern in modern_apis.items():
                    if re.search(pattern, content):
                        analysis['features_used'].append({
                            'file': str(js_file),
                            'feature': api_name,
                            'note': 'Modern web API - check browser support'
                        })
            
            except Exception as e:
                analysis['compatibility_issues'].append({
                    'file': str(js_file),
                    'error': f'Parse error: {str(e)}'
                })
        
        return analysis
    
    def analyze_html_compatibility(self, html_files: List[Path]) -> Dict[str, Any]:
        """Analyze HTML files for browser compatibility issues"""
        analysis = {
            'html5_features': [],
            'compatibility_issues': [],
            'semantic_elements': [],
            'form_features': []
        }
        
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Skip non-HTML files
                if html_file.suffix not in ['.html', '.htm']:
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Check for HTML5 semantic elements
                semantic_elements = ['header', 'nav', 'main', 'section', 'article', 'aside', 'footer']
                for element in semantic_elements:
                    if soup.find(element):
                        analysis['semantic_elements'].append({
                            'file': str(html_file),
                            'element': element
                        })
                
                # Check for HTML5 form features
                form_inputs = soup.find_all('input')
                modern_input_types = ['email', 'url', 'tel', 'search', 'range', 'color', 'date', 'time', 'datetime-local']
                
                for input_elem in form_inputs:
                    input_type = input_elem.get('type', 'text')
                    if input_type in modern_input_types:
                        analysis['form_features'].append({
                            'file': str(html_file),
                            'input_type': input_type,
                            'note': 'HTML5 input type - may need fallback for older browsers'
                        })
                
                # Check for HTML5 attributes
                modern_attributes = ['placeholder', 'required', 'pattern', 'min', 'max', 'step']
                for attr in modern_attributes:
                    if soup.find(attrs={attr: True}):
                        analysis['html5_features'].append({
                            'file': str(html_file),
                            'feature': f'attribute_{attr}',
                            'note': f'HTML5 {attr} attribute used'
                        })
                
                # Check for multimedia elements
                if soup.find('video'):
                    analysis['html5_features'].append({
                        'file': str(html_file),
                        'feature': 'video_element',
                        'note': 'HTML5 video - ensure fallback for older browsers'
                    })
                
                if soup.find('audio'):
                    analysis['html5_features'].append({
                        'file': str(html_file),
                        'feature': 'audio_element',
                        'note': 'HTML5 audio - ensure fallback for older browsers'
                    })
                
                if soup.find('canvas'):
                    analysis['html5_features'].append({
                        'file': str(html_file),
                        'feature': 'canvas_element',
                        'note': 'HTML5 canvas - may need polyfill for IE'
                    })
                
                # Check for problematic patterns
                # Inline SVG
                if soup.find('svg'):
                    analysis['html5_features'].append({
                        'file': str(html_file),
                        'feature': 'inline_svg',
                        'note': 'Inline SVG - limited support in older IE versions'
                    })
                
                # Web fonts
                if soup.find('link', rel='stylesheet') or '@font-face' in content:
                    analysis['html5_features'].append({
                        'file': str(html_file),
                        'feature': 'web_fonts',
                        'note': 'Web fonts detected - generally well supported'
                    })
            
            except Exception as e:
                analysis['compatibility_issues'].append({
                    'file': str(html_file),
                    'error': f'Parse error: {str(e)}'
                })
        
        return analysis
    
    def generate_compatibility_recommendations(self, css_analysis: Dict, js_analysis: Dict, html_analysis: Dict) -> List[str]:
        """Generate recommendations for browser compatibility"""
        recommendations = []
        
        # CSS recommendations
        if css_analysis['vendor_prefixes_needed']:
            recommendations.append("🔧 Add vendor prefixes for CSS properties to support older browsers")
        
        if css_analysis['unsupported_in_target_browsers']:
            recommendations.append("⚠️ Some CSS features are not supported in target browsers - consider fallbacks")
        
        # JavaScript recommendations
        if js_analysis['polyfills_needed']:
            unsupported_browsers = set()
            for polyfill in js_analysis['polyfills_needed']:
                unsupported_browsers.add(polyfill['browser'])
            recommendations.append(f"📦 Add polyfills for JavaScript features not supported in: {', '.join(unsupported_browsers)}")
        
        # Check for specific browser issues
        ie11_issues = []
        if any(issue['browser'] == 'ie11' for issue in css_analysis.get('unsupported_in_target_browsers', [])):
            ie11_issues.append('CSS features')
        if any(polyfill['browser'] == 'ie11' for polyfill in js_analysis.get('polyfills_needed', [])):
            ie11_issues.append('JavaScript features')
        
        if ie11_issues:
            recommendations.append(f"🔄 Consider dropping IE11 support or add extensive polyfills for: {', '.join(ie11_issues)}")
        
        # General recommendations
        if css_analysis['features_used'] or js_analysis['features_used']:
            recommendations.append("🧪 Test thoroughly in target browsers, especially Safari and Firefox")
        
        # Performance recommendations
        if len(js_analysis['features_used']) > 20:
            recommendations.append("⚡ Consider using a build tool like Babel to ensure broader compatibility")
        
        return recommendations
    
    def run_browser_compatibility_testing(self) -> Dict[str, Any]:
        """Run comprehensive cross-browser compatibility testing"""
        print("🌐 Starting Cross-Browser Compatibility Testing")
        print("Batch 199 - Phase 1 QA Pass & Bug Review")
        print("=" * 60)
        
        # Discover files
        print("\n📁 Discovering files...")
        html_files, css_files, js_files = self.discover_files()
        
        self.log_result("Discovery", "HTML Files", "PASS" if html_files else "WARN",
                       {"count": len(html_files)})
        self.log_result("Discovery", "CSS Files", "PASS" if css_files else "WARN",
                       {"count": len(css_files)})
        self.log_result("Discovery", "JavaScript Files", "PASS" if js_files else "WARN",
                       {"count": len(js_files)})
        
        # Analyze CSS compatibility
        print(f"\n🎨 Analyzing CSS compatibility...")
        css_analysis = self.analyze_css_compatibility(css_files)
        
        # Report CSS compatibility issues
        for issue in css_analysis['unsupported_in_target_browsers']:
            self.log_result("CSS Compatibility", f"{Path(issue['file']).name} - {issue['feature']}", "FAIL",
                           {"file": issue['file'], "issue": issue['issue']})
        
        for prefix_needed in css_analysis['vendor_prefixes_needed']:
            self.log_result("CSS Vendor Prefixes", f"{Path(prefix_needed['file']).name} - {prefix_needed['property']}", "WARN",
                           {"file": prefix_needed['file'], "issue": f"Needs vendor prefixes: {', '.join(prefix_needed['needed_prefixes'])}"})
        
        # Analyze JavaScript compatibility
        print(f"\n💻 Analyzing JavaScript compatibility...")
        js_analysis = self.analyze_js_compatibility(js_files)
        
        # Report JavaScript compatibility issues
        for polyfill in js_analysis['polyfills_needed']:
            self.log_result("JS Compatibility", f"{Path(polyfill['file']).name} - {polyfill['feature']}", "FAIL",
                           {"file": polyfill['file'], "issue": polyfill['reason']})
        
        for issue in js_analysis['compatibility_issues']:
            self.log_result("JS Version Support", f"{Path(issue['file']).name} - {issue['feature']}", "WARN",
                           {"file": issue['file'], "issue": f"{issue['browser']} needs v{issue['required_version']}+"})
        
        # Analyze HTML compatibility
        print(f"\n📄 Analyzing HTML compatibility...")
        html_analysis = self.analyze_html_compatibility(html_files)
        
        # Report HTML5 usage
        html5_features = len(html_analysis['html5_features'])
        if html5_features > 0:
            self.log_result("HTML5 Features", f"{html5_features} modern features detected", "INFO",
                           {"count": html5_features})
        
        # Generate overall browser support assessment
        print(f"\n🎯 Generating browser support assessment...")
        
        # Calculate compatibility scores for each browser
        browser_scores = {}
        for browser in self.target_browsers.keys():
            issues = 0
            
            # Count CSS issues for this browser
            issues += len([i for i in css_analysis['unsupported_in_target_browsers'] if i['browser'] == browser])
            issues += len([i for i in css_analysis['compatibility_issues'] if i['browser'] == browser])
            
            # Count JS issues for this browser
            issues += len([p for p in js_analysis['polyfills_needed'] if p['browser'] == browser])
            issues += len([i for i in js_analysis['compatibility_issues'] if i['browser'] == browser])
            
            # Calculate score (lower issues = higher score)
            max_possible_issues = 20  # Rough estimate
            score = max(0, (max_possible_issues - issues) / max_possible_issues * 100)
            browser_scores[browser] = {
                'score': round(score, 1),
                'issues': issues,
                'priority': self.target_browsers[browser]['priority']
            }
            
            # Log browser compatibility
            if score >= 90:
                self.log_result("Browser Support", f"{browser.title()} compatibility", "PASS",
                               {"score": f"{score:.1f}%", "issues": issues})
            elif score >= 70:
                self.log_result("Browser Support", f"{browser.title()} compatibility", "WARN",
                               {"score": f"{score:.1f}%", "issues": issues})
            else:
                self.log_result("Browser Support", f"{browser.title()} compatibility", "FAIL",
                               {"score": f"{score:.1f}%", "issues": issues})
        
        return self.generate_report(css_analysis, js_analysis, html_analysis, browser_scores)
    
    def generate_report(self, css_analysis: Dict, js_analysis: Dict, html_analysis: Dict, browser_scores: Dict) -> Dict[str, Any]:
        """Generate comprehensive browser compatibility report"""
        print("\n📊 Generating Browser Compatibility Report...")
        
        total_checks = len(self.results)
        passed_checks = len([r for r in self.results if r['status'] == 'PASS'])
        failed_checks = len([r for r in self.results if r['status'] == 'FAIL'])
        warning_checks = len([r for r in self.results if r['status'] in ['WARN', 'INFO']])
        
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Generate recommendations
        recommendations = self.generate_compatibility_recommendations(css_analysis, js_analysis, html_analysis)
        
        report = {
            'batch_id': 'BATCH_199',
            'test_name': 'Cross-Browser Compatibility Testing',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_checks': total_checks,
                'passed': passed_checks,
                'failed': failed_checks,
                'warnings': warning_checks,
                'success_rate': round(success_rate, 2)
            },
            'browser_scores': browser_scores,
            'compatibility_analysis': {
                'css': css_analysis,
                'javascript': js_analysis,
                'html': html_analysis
            },
            'target_browsers': self.target_browsers,
            'detailed_results': self.results,
            'recommendations': recommendations
        }
        
        # Save report
        report_file = f"QA_BROWSER_COMPATIBILITY_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Browser Compatibility Report saved to: {report_file}")
        return report

def main():
    """Main browser tester runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cross-Browser Compatibility Tester')
    parser.add_argument('--build-dir', default='dist',
                       help='Build directory to analyze')
    parser.add_argument('--base-url', default='https://morningstar.swg.ms11.com',
                       help='Base URL for the site')
    
    args = parser.parse_args()
    
    tester = BrowserTester(build_dir=args.build_dir, base_url=args.base_url)
    
    try:
        report = tester.run_browser_compatibility_testing()
        
        print("\n" + "=" * 60)
        print("🎯 Browser Compatibility Testing Complete!")
        print(f"📊 Success Rate: {report['summary']['success_rate']}%")
        print(f"📋 Checks: {report['summary']['passed']}/{report['summary']['total_checks']} passed")
        
        print(f"\n🌐 Browser Compatibility Scores:")
        for browser, data in report['browser_scores'].items():
            score_emoji = "✅" if data['score'] >= 90 else "⚠️" if data['score'] >= 70 else "❌"
            print(f"   {score_emoji} {browser.title()}: {data['score']}% ({data['issues']} issues)")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        
        # Exit with appropriate code
        sys.exit(0 if report['summary']['failed'] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Browser compatibility testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Browser compatibility testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
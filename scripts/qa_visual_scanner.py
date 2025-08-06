#!/usr/bin/env python3
"""
QA Visual Bug Scanner - UI validation and visual bug detection
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
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO

class VisualBugScanner:
    """Visual bug detection and UI validation system"""
    
    def __init__(self, build_dir: str = "dist"):
        self.build_dir = Path(build_dir)
        self.project_root = Path(__file__).parent.parent
        self.results = []
        
        # UI validation patterns
        self.ui_issues = {
            'layout': [],
            'typography': [],
            'colors': [],
            'spacing': [],
            'responsive': [],
            'accessibility': []
        }
        
        # Common CSS properties to validate
        self.critical_css_properties = [
            'display', 'position', 'width', 'height', 'margin', 'padding',
            'font-size', 'font-family', 'color', 'background-color',
            'border', 'z-index', 'overflow'
        ]
        
        # Accessibility requirements
        self.a11y_requirements = {
            'min_contrast_ratio': 4.5,
            'min_touch_target': 44,  # pixels
            'max_line_length': 80,   # characters
            'min_font_size': 12      # pixels
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
        if details and details.get('error'):
            print(f"   Issue: {details['error']}")
    
    def discover_html_files(self) -> List[Path]:
        """Discover all HTML files for visual analysis"""
        html_files = []
        
        # Check build directory
        if self.build_dir.exists():
            html_files.extend(self.build_dir.rglob("*.html"))
        
        # Check source templates
        src_dir = self.project_root / "src"
        if src_dir.exists():
            html_files.extend(src_dir.rglob("*.html"))
            html_files.extend(src_dir.rglob("*.njk"))
        
        # Check website directory
        website_dir = self.project_root / "website"
        if website_dir.exists():
            html_files.extend(website_dir.rglob("*.html"))
        
        return list(set(html_files))
    
    def discover_css_files(self) -> List[Path]:
        """Discover CSS files for style analysis"""
        css_files = []
        
        # Check build directory
        if self.build_dir.exists():
            css_files.extend(self.build_dir.rglob("*.css"))
        
        # Check source styles
        src_styles = self.project_root / "src/styles"
        if src_styles.exists():
            css_files.extend(src_styles.rglob("*.css"))
        
        # Check main styles directory
        styles_dir = self.project_root / "styles"
        if styles_dir.exists():
            css_files.extend(styles_dir.rglob("*.css"))
        
        return list(set(css_files))
    
    def analyze_html_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze HTML structure for common issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for basic HTML structure
            if not soup.find('html'):
                issues.append("Missing <html> tag")
            
            if not soup.find('head'):
                issues.append("Missing <head> section")
            
            if not soup.find('body'):
                issues.append("Missing <body> section")
            
            # Check for required meta tags
            if not soup.find('meta', attrs={'charset': True}):
                issues.append("Missing charset meta tag")
            
            if not soup.find('meta', attrs={'name': 'viewport'}):
                issues.append("Missing viewport meta tag for mobile responsiveness")
            
            # Check for title tag
            title_tag = soup.find('title')
            if not title_tag:
                issues.append("Missing <title> tag")
            elif not title_tag.get_text(strip=True):
                issues.append("Empty <title> tag")
            elif len(title_tag.get_text()) > 60:
                issues.append("Title tag too long (>60 characters)")
            
            # Check for headings hierarchy
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if headings:
                h1_count = len(soup.find_all('h1'))
                if h1_count == 0:
                    issues.append("No H1 heading found")
                elif h1_count > 1:
                    issues.append(f"Multiple H1 headings found ({h1_count})")
                
                # Check heading order
                heading_levels = [int(h.name[1]) for h in headings]
                for i in range(1, len(heading_levels)):
                    if heading_levels[i] - heading_levels[i-1] > 1:
                        issues.append("Heading hierarchy skips levels")
                        break
            
            # Check for images without alt text
            images = soup.find_all('img')
            images_without_alt = [img for img in images if not img.get('alt')]
            if images_without_alt:
                issues.append(f"{len(images_without_alt)} images missing alt text")
            
            # Check for links without meaningful text
            links = soup.find_all('a')
            problematic_links = []
            for link in links:
                text = link.get_text(strip=True).lower()
                if text in ['click here', 'read more', 'here', 'more']:
                    problematic_links.append(text)
            
            if problematic_links:
                issues.append(f"Links with non-descriptive text: {', '.join(set(problematic_links))}")
            
            # Check for form inputs without labels
            inputs = soup.find_all(['input', 'select', 'textarea'])
            inputs_without_labels = []
            for inp in inputs:
                if inp.get('type') not in ['hidden', 'submit', 'button']:
                    input_id = inp.get('id')
                    if not input_id or not soup.find('label', attrs={'for': input_id}):
                        if not inp.find_parent('label'):
                            inputs_without_labels.append(inp.get('type', 'input'))
            
            if inputs_without_labels:
                issues.append(f"Form inputs without labels: {', '.join(inputs_without_labels)}")
            
            # Check for missing language attribute
            html_tag = soup.find('html')
            if html_tag and not html_tag.get('lang'):
                issues.append("Missing language attribute on <html> tag")
            
            # Check for inline styles (potential maintenance issues)
            elements_with_style = soup.find_all(attrs={'style': True})
            if len(elements_with_style) > 5:
                issues.append(f"Many elements with inline styles ({len(elements_with_style)}) - consider moving to CSS")
            
            return {
                'file': str(file_path),
                'issues': issues,
                'stats': {
                    'total_elements': len(soup.find_all()),
                    'images': len(images),
                    'links': len(links),
                    'headings': len(headings),
                    'inputs': len(inputs)
                }
            }
        
        except Exception as e:
            return {
                'file': str(file_path),
                'issues': [f"Parse error: {str(e)}"],
                'stats': {}
            }
    
    def analyze_css_styles(self, file_path: Path) -> Dict[str, Any]:
        """Analyze CSS for common issues and best practices"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common CSS issues
            lines = content.split('\n')
            
            # Check for !important overuse
            important_count = content.count('!important')
            if important_count > 10:
                issues.append(f"Overuse of !important ({important_count} instances)")
            
            # Check for hardcoded pixel values that should be responsive
            pixel_pattern = r'\d+px'
            pixel_matches = re.findall(pixel_pattern, content)
            if len(pixel_matches) > 50:
                issues.append(f"Many hardcoded pixel values ({len(pixel_matches)}) - consider using relative units")
            
            # Check for missing vendor prefixes for common properties
            modern_properties = ['transform', 'transition', 'animation', 'flex', 'grid']
            for prop in modern_properties:
                if f'{prop}:' in content and f'-webkit-{prop}:' not in content:
                    # Only flag if property exists but no prefixes
                    pass  # Modern browsers handle this well now
            
            # Check for unused or duplicate selectors
            selectors = re.findall(r'([.#]?[\w-]+)\s*{', content)
            if len(selectors) != len(set(selectors)):
                duplicate_count = len(selectors) - len(set(selectors))
                issues.append(f"Duplicate selectors found ({duplicate_count})")
            
            # Check for very long lines
            long_lines = [i for i, line in enumerate(lines) if len(line) > 120]
            if long_lines:
                issues.append(f"Long lines (>120 chars) on lines: {long_lines[:5]}")
            
            # Check for missing semicolons
            missing_semicolon_pattern = r'[^;}]\s*\n\s*[a-zA-Z-]+\s*:'
            if re.search(missing_semicolon_pattern, content):
                issues.append("Potential missing semicolons detected")
            
            # Check for color contrast issues (basic detection)
            color_pattern = r'color\s*:\s*(#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|[a-zA-Z]+)'
            bg_color_pattern = r'background-color\s*:\s*(#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|[a-zA-Z]+)'
            
            colors = re.findall(color_pattern, content)
            bg_colors = re.findall(bg_color_pattern, content)
            
            # Check for very small font sizes
            font_size_pattern = r'font-size\s*:\s*(\d+)px'
            font_sizes = re.findall(font_size_pattern, content)
            small_fonts = [int(size) for size in font_sizes if int(size) < 12]
            if small_fonts:
                issues.append(f"Very small font sizes detected: {small_fonts}")
            
            return {
                'file': str(file_path),
                'issues': issues,
                'stats': {
                    'lines': len(lines),
                    'selectors': len(set(selectors)),
                    'important_count': important_count,
                    'colors': len(colors),
                    'background_colors': len(bg_colors)
                }
            }
        
        except Exception as e:
            return {
                'file': str(file_path),
                'issues': [f"Parse error: {str(e)}"],
                'stats': {}
            }
    
    def check_responsive_design(self, file_path: Path) -> Dict[str, Any]:
        """Check for responsive design indicators"""
        issues = []
        responsive_indicators = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for viewport meta tag
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            if viewport:
                responsive_indicators.append("Viewport meta tag present")
                content_attr = viewport.get('content', '')
                if 'width=device-width' in content_attr:
                    responsive_indicators.append("Device-width viewport")
                if 'initial-scale=1' in content_attr:
                    responsive_indicators.append("Initial scale set")
            else:
                issues.append("Missing viewport meta tag")
            
            # Check for media queries in inline styles or linked CSS
            style_tags = soup.find_all('style')
            has_media_queries = False
            
            for style in style_tags:
                if '@media' in style.get_text():
                    has_media_queries = True
                    break
            
            if has_media_queries:
                responsive_indicators.append("Media queries found in inline styles")
            
            # Check for responsive CSS frameworks
            css_links = soup.find_all('link', attrs={'rel': 'stylesheet'})
            frameworks = []
            
            for link in css_links:
                href = link.get('href', '').lower()
                if 'bootstrap' in href:
                    frameworks.append('Bootstrap')
                elif 'foundation' in href:
                    frameworks.append('Foundation')
                elif 'bulma' in href:
                    frameworks.append('Bulma')
                elif 'tailwind' in href:
                    frameworks.append('Tailwind')
            
            if frameworks:
                responsive_indicators.append(f"Responsive frameworks: {', '.join(frameworks)}")
            
            # Check for flexible layouts
            if 'flexbox' in content.lower() or 'display: flex' in content:
                responsive_indicators.append("Flexbox layout detected")
            
            if 'grid' in content.lower() or 'display: grid' in content:
                responsive_indicators.append("CSS Grid layout detected")
            
            # Check for relative units
            relative_units = ['%', 'em', 'rem', 'vh', 'vw', 'vmin', 'vmax']
            found_relative = []
            
            for unit in relative_units:
                if unit in content:
                    found_relative.append(unit)
            
            if found_relative:
                responsive_indicators.append(f"Relative units used: {', '.join(found_relative)}")
            
            # Flag potential issues
            if not responsive_indicators:
                issues.append("No responsive design indicators found")
            
            # Check for fixed widths that might break on mobile
            fixed_width_pattern = r'width\s*:\s*\d+px'
            fixed_widths = re.findall(fixed_width_pattern, content)
            if len(fixed_widths) > 10:
                issues.append(f"Many fixed pixel widths ({len(fixed_widths)}) may not be mobile-friendly")
            
            return {
                'file': str(file_path),
                'issues': issues,
                'responsive_indicators': responsive_indicators,
                'stats': {
                    'media_queries': has_media_queries,
                    'frameworks': frameworks,
                    'fixed_widths': len(fixed_widths)
                }
            }
        
        except Exception as e:
            return {
                'file': str(file_path),
                'issues': [f"Parse error: {str(e)}"],
                'responsive_indicators': [],
                'stats': {}
            }
    
    def check_accessibility_compliance(self, file_path: Path) -> Dict[str, Any]:
        """Check basic accessibility compliance"""
        issues = []
        good_practices = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check ARIA attributes
            aria_elements = soup.find_all(attrs={'aria-label': True})
            if aria_elements:
                good_practices.append(f"ARIA labels found on {len(aria_elements)} elements")
            
            # Check for skip links
            skip_links = soup.find_all('a', href=True)
            has_skip_link = any('skip' in link.get_text().lower() for link in skip_links)
            if has_skip_link:
                good_practices.append("Skip navigation link found")
            else:
                issues.append("No skip navigation link found")
            
            # Check for proper heading structure
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if headings:
                h1_count = len(soup.find_all('h1'))
                if h1_count == 1:
                    good_practices.append("Single H1 heading (good practice)")
                elif h1_count == 0:
                    issues.append("No H1 heading for screen readers")
                else:
                    issues.append(f"Multiple H1 headings ({h1_count}) confuse screen readers")
            
            # Check for form accessibility
            forms = soup.find_all('form')
            for form in forms:
                inputs = form.find_all(['input', 'select', 'textarea'])
                inputs_with_labels = 0
                
                for inp in inputs:
                    if inp.get('type') in ['hidden', 'submit', 'button']:
                        continue
                    
                    # Check for associated label
                    input_id = inp.get('id')
                    if input_id and soup.find('label', attrs={'for': input_id}):
                        inputs_with_labels += 1
                    elif inp.find_parent('label'):
                        inputs_with_labels += 1
                    elif inp.get('aria-label') or inp.get('aria-labelledby'):
                        inputs_with_labels += 1
                
                if inputs_with_labels == len([i for i in inputs if i.get('type') not in ['hidden', 'submit', 'button']]):
                    good_practices.append("All form inputs have proper labels")
                else:
                    issues.append("Some form inputs missing labels or ARIA attributes")
            
            # Check for alt text on images
            images = soup.find_all('img')
            images_with_alt = len([img for img in images if img.get('alt') is not None])
            if images and images_with_alt == len(images):
                good_practices.append("All images have alt attributes")
            elif images and images_with_alt < len(images):
                issues.append(f"{len(images) - images_with_alt} images missing alt text")
            
            # Check for color-only information
            # This is a basic check - would need more sophisticated analysis
            color_words = ['red', 'green', 'blue', 'yellow', 'click the red', 'green button']
            text_content = soup.get_text().lower()
            color_references = [word for word in color_words if word in text_content]
            if color_references:
                issues.append("Potential color-only information detected - ensure alternatives exist")
            
            # Check for focus indicators
            if ':focus' in content:
                good_practices.append("Focus styles defined")
            else:
                issues.append("No focus styles found - keyboard navigation may be difficult")
            
            # Check for language declaration
            html_tag = soup.find('html')
            if html_tag and html_tag.get('lang'):
                good_practices.append(f"Language declared: {html_tag.get('lang')}")
            else:
                issues.append("No language attribute on HTML tag")
            
            # Check for proper link context
            links = soup.find_all('a', href=True)
            vague_links = []
            for link in links:
                text = link.get_text(strip=True).lower()
                if text in ['click here', 'here', 'read more', 'more', 'link']:
                    vague_links.append(text)
            
            if vague_links:
                issues.append(f"Vague link text found: {', '.join(set(vague_links))}")
            
            return {
                'file': str(file_path),
                'issues': issues,
                'good_practices': good_practices,
                'stats': {
                    'headings': len(headings),
                    'images': len(images),
                    'links': len(links),
                    'forms': len(forms)
                }
            }
        
        except Exception as e:
            return {
                'file': str(file_path),
                'issues': [f"Parse error: {str(e)}"],
                'good_practices': [],
                'stats': {}
            }
    
    def check_performance_indicators(self, file_path: Path) -> Dict[str, Any]:
        """Check for performance-related issues"""
        issues = []
        optimizations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check for large inline styles/scripts
            style_tags = soup.find_all('style')
            large_inline_styles = [tag for tag in style_tags if len(tag.get_text()) > 1000]
            if large_inline_styles:
                issues.append(f"{len(large_inline_styles)} large inline style blocks (>1KB)")
            
            script_tags = soup.find_all('script', src=False)
            large_inline_scripts = [tag for tag in script_tags if len(tag.get_text()) > 1000]
            if large_inline_scripts:
                issues.append(f"{len(large_inline_scripts)} large inline script blocks (>1KB)")
            
            # Check for resource loading optimizations
            css_links = soup.find_all('link', attrs={'rel': 'stylesheet'})
            preload_links = soup.find_all('link', attrs={'rel': 'preload'})
            
            if preload_links:
                optimizations.append(f"Resource preloading used ({len(preload_links)} resources)")
            
            # Check for async/defer on scripts
            external_scripts = soup.find_all('script', src=True)
            async_scripts = [s for s in external_scripts if s.has_attr('async')]
            defer_scripts = [s for s in external_scripts if s.has_attr('defer')]
            
            if async_scripts or defer_scripts:
                optimizations.append(f"Non-blocking scripts: {len(async_scripts)} async, {len(defer_scripts)} defer")
            elif external_scripts:
                issues.append(f"{len(external_scripts)} blocking scripts found - consider async/defer")
            
            # Check for image optimization attributes
            images = soup.find_all('img')
            lazy_images = [img for img in images if img.get('loading') == 'lazy']
            if lazy_images:
                optimizations.append(f"Lazy loading used on {len(lazy_images)} images")
            
            responsive_images = [img for img in images if img.get('srcset')]
            if responsive_images:
                optimizations.append(f"Responsive images used on {len(responsive_images)} images")
            
            # Check for critical CSS
            if any('critical' in link.get('href', '').lower() for link in css_links):
                optimizations.append("Critical CSS detected")
            
            # Check for minification indicators
            if '.min.' in content or content.count('\n') < len(content) / 50:
                optimizations.append("Content appears minified")
            
            return {
                'file': str(file_path),
                'issues': issues,
                'optimizations': optimizations,
                'stats': {
                    'css_files': len(css_links),
                    'js_files': len(external_scripts),
                    'images': len(images),
                    'inline_styles': len(style_tags),
                    'inline_scripts': len(script_tags)
                }
            }
        
        except Exception as e:
            return {
                'file': str(file_path),
                'issues': [f"Parse error: {str(e)}"],
                'optimizations': [],
                'stats': {}
            }
    
    def run_visual_analysis(self) -> Dict[str, Any]:
        """Run comprehensive visual bug analysis"""
        print("👁️ Starting Visual Bug Scanner")
        print("Batch 199 - Phase 1 QA Pass & Bug Review")
        print("=" * 60)
        
        # Discover files
        print("\n📁 Discovering files...")
        html_files = self.discover_html_files()
        css_files = self.discover_css_files()
        
        if not html_files and not css_files:
            self.log_result("Discovery", "Files Found", "FAIL",
                           {"error": "No HTML or CSS files found"})
            return self.generate_report()
        
        self.log_result("Discovery", "HTML Files", "PASS",
                       {"count": len(html_files)})
        self.log_result("Discovery", "CSS Files", "PASS",
                       {"count": len(css_files)})
        
        # Analyze HTML structure
        print(f"\n🏗️ Analyzing HTML structure...")
        total_html_issues = 0
        
        for file_path in html_files:
            analysis = self.analyze_html_structure(file_path)
            
            if analysis['issues']:
                total_html_issues += len(analysis['issues'])
                for issue in analysis['issues']:
                    self.log_result("HTML Structure", f"{file_path.name} - {issue}", "FAIL",
                                   {"file": str(file_path), "error": issue})
                    self.ui_issues['layout'].append({
                        'file': str(file_path),
                        'issue': issue,
                        'category': 'structure'
                    })
            else:
                self.log_result("HTML Structure", f"{file_path.name}", "PASS",
                               {"file": str(file_path)})
        
        # Analyze CSS styles
        print(f"\n🎨 Analyzing CSS styles...")
        total_css_issues = 0
        
        for file_path in css_files:
            analysis = self.analyze_css_styles(file_path)
            
            if analysis['issues']:
                total_css_issues += len(analysis['issues'])
                for issue in analysis['issues']:
                    self.log_result("CSS Styles", f"{file_path.name} - {issue}", "WARN",
                                   {"file": str(file_path), "error": issue})
                    self.ui_issues['typography'].append({
                        'file': str(file_path),
                        'issue': issue,
                        'category': 'styles'
                    })
            else:
                self.log_result("CSS Styles", f"{file_path.name}", "PASS",
                               {"file": str(file_path)})
        
        # Check responsive design
        print(f"\n📱 Checking responsive design...")
        responsive_issues = 0
        
        for file_path in html_files:
            analysis = self.check_responsive_design(file_path)
            
            if analysis['issues']:
                responsive_issues += len(analysis['issues'])
                for issue in analysis['issues']:
                    self.log_result("Responsive Design", f"{file_path.name} - {issue}", "FAIL",
                                   {"file": str(file_path), "error": issue})
                    self.ui_issues['responsive'].append({
                        'file': str(file_path),
                        'issue': issue,
                        'category': 'responsive'
                    })
            else:
                self.log_result("Responsive Design", f"{file_path.name}", "PASS",
                               {"file": str(file_path), "indicators": len(analysis['responsive_indicators'])})
        
        # Check accessibility
        print(f"\n♿ Checking accessibility compliance...")
        accessibility_issues = 0
        
        for file_path in html_files:
            analysis = self.check_accessibility_compliance(file_path)
            
            if analysis['issues']:
                accessibility_issues += len(analysis['issues'])
                for issue in analysis['issues']:
                    self.log_result("Accessibility", f"{file_path.name} - {issue}", "FAIL",
                                   {"file": str(file_path), "error": issue})
                    self.ui_issues['accessibility'].append({
                        'file': str(file_path),
                        'issue': issue,
                        'category': 'accessibility'
                    })
            else:
                self.log_result("Accessibility", f"{file_path.name}", "PASS",
                               {"file": str(file_path), "good_practices": len(analysis['good_practices'])})
        
        # Check performance indicators
        print(f"\n⚡ Checking performance indicators...")
        performance_issues = 0
        
        for file_path in html_files:
            analysis = self.check_performance_indicators(file_path)
            
            if analysis['issues']:
                performance_issues += len(analysis['issues'])
                for issue in analysis['issues']:
                    self.log_result("Performance", f"{file_path.name} - {issue}", "WARN",
                                   {"file": str(file_path), "error": issue})
            
            if analysis['optimizations']:
                for optimization in analysis['optimizations']:
                    self.log_result("Performance", f"{file_path.name} - {optimization}", "PASS",
                                   {"file": str(file_path)})
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive visual analysis report"""
        print("\n📊 Generating Visual Analysis Report...")
        
        total_checks = len(self.results)
        passed_checks = len([r for r in self.results if r['status'] == 'PASS'])
        failed_checks = len([r for r in self.results if r['status'] == 'FAIL'])
        warning_checks = len([r for r in self.results if r['status'] in ['WARN', 'INFO']])
        
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Count issues by category
        total_ui_issues = sum(len(issues) for issues in self.ui_issues.values())
        
        report = {
            'batch_id': 'BATCH_199',
            'test_name': 'Visual Bug Scanner',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_checks': total_checks,
                'passed': passed_checks,
                'failed': failed_checks,
                'warnings': warning_checks,
                'success_rate': round(success_rate, 2)
            },
            'ui_issues': {
                'total': total_ui_issues,
                'by_category': {category: len(issues) for category, issues in self.ui_issues.items()},
                'details': self.ui_issues
            },
            'detailed_results': self.results,
            'recommendations': []
        }
        
        # Add recommendations
        if failed_checks == 0 and total_ui_issues == 0:
            report['recommendations'].append("✅ No critical visual bugs detected")
        
        if self.ui_issues['layout']:
            report['recommendations'].append(f"🏗️ Fix {len(self.ui_issues['layout'])} HTML structure issues")
        
        if self.ui_issues['responsive']:
            report['recommendations'].append(f"📱 Address {len(self.ui_issues['responsive'])} responsive design issues")
        
        if self.ui_issues['accessibility']:
            report['recommendations'].append(f"♿ Improve {len(self.ui_issues['accessibility'])} accessibility issues")
        
        if self.ui_issues['typography']:
            report['recommendations'].append(f"🎨 Review {len(self.ui_issues['typography'])} CSS style issues")
        
        # Save report
        report_file = f"QA_VISUAL_SCAN_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Visual Analysis Report saved to: {report_file}")
        return report

def main():
    """Main visual scanner runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visual Bug Scanner')
    parser.add_argument('--build-dir', default='dist',
                       help='Build directory to analyze')
    
    args = parser.parse_args()
    
    scanner = VisualBugScanner(build_dir=args.build_dir)
    
    try:
        report = scanner.run_visual_analysis()
        
        print("\n" + "=" * 60)
        print("🎯 Visual Analysis Complete!")
        print(f"📊 Success Rate: {report['summary']['success_rate']}%")
        print(f"📋 Checks: {report['summary']['passed']}/{report['summary']['total_checks']} passed")
        print(f"🐛 UI Issues: {report['ui_issues']['total']}")
        
        if report['ui_issues']['total'] > 0:
            print(f"\n🔍 Issues by Category:")
            for category, count in report['ui_issues']['by_category'].items():
                if count > 0:
                    print(f"   {category.title()}: {count}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        
        # Exit with appropriate code
        sys.exit(0 if report['summary']['failed'] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Visual analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Visual analysis failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
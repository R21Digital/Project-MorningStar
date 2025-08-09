#!/usr/bin/env python3
"""
QA Link Checker - Comprehensive link validation for internal and external links
Batch 199 - Phase 1 QA Pass & Bug Review
"""

import os
import sys
import json
import requests
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, urlunparse
from collections import defaultdict
import concurrent.futures
from bs4 import BeautifulSoup

class LinkChecker:
    """Comprehensive link validation system"""
    
    def __init__(self, base_url: str = None, build_dir: str = "dist"):
        self.base_url = base_url or "https://morningstar.swg.ms11.com"
        self.build_dir = Path(build_dir)
        self.project_root = Path(__file__).parent.parent
        self.results = []
        self.external_cache = {}  # Cache external link checks
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Link categories
        self.internal_links = set()
        self.external_links = set()
        self.anchor_links = set()
        self.file_links = set()
        self.email_links = set()
        
        # Error tracking
        self.broken_links = []
        self.slow_links = []
        self.redirect_chains = []
        self.suspicious_links = []
        
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
        if details and details.get('url'):
            print(f"   URL: {details['url']}")
        if details and details.get('error'):
            print(f"   Error: {details['error']}")
    
    def discover_html_files(self) -> List[Path]:
        """Discover all HTML files to check"""
        html_files = []
        
        # Check build directory if it exists
        if self.build_dir.exists():
            html_files.extend(self.build_dir.rglob("*.html"))
        
        # Check src/pages for 11ty templates
        src_pages = self.project_root / "src/pages"
        if src_pages.exists():
            html_files.extend(src_pages.rglob("*.html"))
            html_files.extend(src_pages.rglob("*.11ty.js"))
        
        # Check website directory
        website_dir = self.project_root / "website"
        if website_dir.exists():
            html_files.extend(website_dir.rglob("*.html"))
        
        # Check API documentation
        api_dir = self.project_root / "api"
        if api_dir.exists():
            html_files.extend(api_dir.rglob("*.html"))
        
        return list(set(html_files))  # Remove duplicates
    
    def extract_links_from_html(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract all links from an HTML file"""
        links = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract different types of links
            # <a> tags
            for tag in soup.find_all('a', href=True):
                links.append({
                    'url': tag['href'],
                    'text': tag.get_text(strip=True),
                    'type': 'link',
                    'tag': 'a',
                    'file': str(file_path),
                    'title': tag.get('title', ''),
                    'target': tag.get('target', '')
                })
            
            # <img> tags
            for tag in soup.find_all('img', src=True):
                links.append({
                    'url': tag['src'],
                    'text': tag.get('alt', ''),
                    'type': 'image',
                    'tag': 'img',
                    'file': str(file_path),
                    'title': tag.get('title', ''),
                    'loading': tag.get('loading', '')
                })
            
            # <link> tags (CSS, etc.)
            for tag in soup.find_all('link', href=True):
                links.append({
                    'url': tag['href'],
                    'text': '',
                    'type': 'resource',
                    'tag': 'link',
                    'file': str(file_path),
                    'rel': tag.get('rel', []),
                    'media': tag.get('media', '')
                })
            
            # <script> tags with src
            for tag in soup.find_all('script', src=True):
                links.append({
                    'url': tag['src'],
                    'text': '',
                    'type': 'script',
                    'tag': 'script',
                    'file': str(file_path),
                    'async': tag.has_attr('async'),
                    'defer': tag.has_attr('defer')
                })
            
            # Extract links from JavaScript/JSON content (11ty files)
            if file_path.suffix == '.js':
                # Look for URL patterns in JavaScript
                url_patterns = [
                    r'["\']https?://[^"\']+["\']',
                    r'["\'][/][^"\']+["\']',
                    r'href\s*:\s*["\'][^"\']+["\']'
                ]
                
                for pattern in url_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        clean_url = match.strip('"\'')
                        if clean_url:
                            links.append({
                                'url': clean_url,
                                'text': '',
                                'type': 'js_reference',
                                'tag': 'javascript',
                                'file': str(file_path)
                            })
            
        except Exception as e:
            self.log_result("Discovery", f"Parse HTML - {file_path.name}", "FAIL",
                           {"error": str(e), "file": str(file_path)})
        
        return links
    
    def categorize_link(self, url: str) -> str:
        """Categorize a link by type"""
        if not url:
            return 'empty'
        
        url = url.strip()
        
        # Email links
        if url.startswith('mailto:'):
            return 'email'
        
        # Anchor links
        if url.startswith('#'):
            return 'anchor'
        
        # Protocol-relative URLs
        if url.startswith('//'):
            return 'external'
        
        # Absolute external URLs
        if url.startswith(('http://', 'https://')):
            parsed = urlparse(url)
            if parsed.netloc != urlparse(self.base_url).netloc:
                return 'external'
            else:
                return 'internal_absolute'
        
        # Data URLs
        if url.startswith('data:'):
            return 'data'
        
        # JavaScript links
        if url.startswith('javascript:'):
            return 'javascript'
        
        # File extensions that are typically resources
        if any(url.lower().endswith(ext) for ext in ['.css', '.js', '.json', '.xml', '.txt']):
            return 'resource'
        
        # Image extensions
        if any(url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico']):
            return 'image'
        
        # Relative internal links
        if url.startswith('/') or not url.startswith(('http', 'ftp', 'mailto')):
            return 'internal_relative'
        
        return 'unknown'
    
    def resolve_relative_url(self, url: str, base_file: Path) -> str:
        """Resolve relative URL to absolute URL"""
        if url.startswith(('http://', 'https://', '//')):
            return url
        
        if url.startswith('/'):
            return urljoin(self.base_url, url)
        
        # For relative paths, resolve based on file location
        if self.build_dir.exists() and str(base_file).startswith(str(self.build_dir)):
            # File is in build directory
            relative_to_build = base_file.relative_to(self.build_dir)
            base_path = '/' + str(relative_to_build.parent).replace('\\', '/')
            if base_path == '/.':
                base_path = '/'
            return urljoin(self.base_url + base_path + '/', url)
        
        # Default resolution
        return urljoin(self.base_url, url)
    
    def check_internal_link(self, url: str, original_file: str) -> Dict[str, Any]:
        """Check if an internal link is valid"""
        result = {
            'url': url,
            'status': 'unknown',
            'status_code': None,
            'error': None,
            'file_exists': False,
            'redirect_url': None,
            'response_time': None
        }
        
        try:
            # Parse URL to get path
            parsed = urlparse(url)
            path = parsed.path
            
            # Remove base URL if present
            if url.startswith(self.base_url):
                path = url[len(self.base_url):]
            
            # Handle root path
            if path == '' or path == '/':
                path = '/index.html'
            
            # Add .html if no extension
            if not Path(path).suffix and not path.endswith('/'):
                path = path + '.html'
            
            # Check if file exists in build directory
            if self.build_dir.exists():
                file_path = self.build_dir / path.lstrip('/')
                if file_path.exists() and file_path.is_file():
                    result['file_exists'] = True
                    result['status'] = 'pass'
                    self.log_result("Internal Links", f"File exists - {path}", "PASS",
                                   {"url": url, "file_path": str(file_path)})
                else:
                    result['status'] = 'fail'
                    result['error'] = f"File not found: {file_path}"
                    self.log_result("Internal Links", f"File missing - {path}", "FAIL",
                                   {"url": url, "file_path": str(file_path), "error": result['error']})
            else:
                # No build directory - try HTTP check
                start_time = time.time()
                response = self.session.head(url, timeout=10, allow_redirects=True)
                result['response_time'] = time.time() - start_time
                result['status_code'] = response.status_code
                
                if response.status_code == 200:
                    result['status'] = 'pass'
                    self.log_result("Internal Links", f"HTTP check - {path}", "PASS",
                                   {"url": url, "status_code": response.status_code})
                else:
                    result['status'] = 'fail'
                    result['error'] = f"HTTP {response.status_code}"
                    self.log_result("Internal Links", f"HTTP error - {path}", "FAIL",
                                   {"url": url, "status_code": response.status_code})
                
                if response.url != url:
                    result['redirect_url'] = response.url
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.log_result("Internal Links", f"Check error - {urlparse(url).path}", "FAIL",
                           {"url": url, "error": str(e)})
        
        return result
    
    def check_external_link(self, url: str) -> Dict[str, Any]:
        """Check if an external link is valid"""
        # Use cache to avoid repeated checks
        if url in self.external_cache:
            return self.external_cache[url]
        
        result = {
            'url': url,
            'status': 'unknown',
            'status_code': None,
            'error': None,
            'redirect_url': None,
            'response_time': None,
            'final_url': None
        }
        
        try:
            start_time = time.time()
            response = self.session.head(url, timeout=15, allow_redirects=True)
            result['response_time'] = time.time() - start_time
            result['status_code'] = response.status_code
            result['final_url'] = response.url
            
            if response.status_code == 200:
                result['status'] = 'pass'
                self.log_result("External Links", f"Valid - {urlparse(url).netloc}", "PASS",
                               {"url": url, "status_code": response.status_code, 
                                "response_time": f"{result['response_time']:.2f}s"})
            elif response.status_code in [301, 302, 303, 307, 308]:
                result['status'] = 'redirect'
                result['redirect_url'] = response.url
                self.log_result("External Links", f"Redirect - {urlparse(url).netloc}", "WARN",
                               {"url": url, "redirect_to": response.url, "status_code": response.status_code})
            else:
                result['status'] = 'fail'
                result['error'] = f"HTTP {response.status_code}"
                self.log_result("External Links", f"Error - {urlparse(url).netloc}", "FAIL",
                               {"url": url, "status_code": response.status_code})
            
            # Check for slow responses
            if result['response_time'] > 5.0:
                self.slow_links.append({
                    'url': url,
                    'response_time': result['response_time']
                })
                self.log_result("Performance", f"Slow response - {urlparse(url).netloc}", "WARN",
                               {"url": url, "response_time": f"{result['response_time']:.2f}s"})
        
        except requests.exceptions.Timeout:
            result['status'] = 'timeout'
            result['error'] = 'Request timeout'
            self.log_result("External Links", f"Timeout - {urlparse(url).netloc}", "FAIL",
                           {"url": url, "error": "Request timeout"})
        
        except requests.exceptions.ConnectionError:
            result['status'] = 'connection_error'
            result['error'] = 'Connection failed'
            self.log_result("External Links", f"Connection error - {urlparse(url).netloc}", "FAIL",
                           {"url": url, "error": "Connection failed"})
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.log_result("External Links", f"Error - {urlparse(url).netloc}", "FAIL",
                           {"url": url, "error": str(e)})
        
        # Cache the result
        self.external_cache[url] = result
        return result
    
    def check_anchor_link(self, url: str, file_path: str) -> Dict[str, Any]:
        """Check if an anchor link exists in the page"""
        result = {
            'url': url,
            'status': 'unknown',
            'error': None,
            'anchor_found': False
        }
        
        anchor = url.lstrip('#')
        if not anchor:
            result['status'] = 'pass'
            result['anchor_found'] = True
            return result
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for element with matching id
            element_with_id = soup.find(id=anchor)
            if element_with_id:
                result['status'] = 'pass'
                result['anchor_found'] = True
                self.log_result("Anchor Links", f"Found - #{anchor}", "PASS",
                               {"url": url, "file": file_path})
            else:
                # Look for anchor with name attribute (older HTML)
                anchor_with_name = soup.find('a', {'name': anchor})
                if anchor_with_name:
                    result['status'] = 'pass'
                    result['anchor_found'] = True
                    self.log_result("Anchor Links", f"Found (name) - #{anchor}", "PASS",
                                   {"url": url, "file": file_path})
                else:
                    result['status'] = 'fail'
                    result['error'] = f"Anchor #{anchor} not found"
                    self.log_result("Anchor Links", f"Missing - #{anchor}", "FAIL",
                                   {"url": url, "file": file_path, "error": result['error']})
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.log_result("Anchor Links", f"Error - #{anchor}", "FAIL",
                           {"url": url, "file": file_path, "error": str(e)})
        
        return result
    
    def validate_email_link(self, url: str) -> Dict[str, Any]:
        """Validate email link format"""
        result = {
            'url': url,
            'status': 'unknown',
            'error': None,
            'valid_format': False
        }
        
        try:
            # Basic email format validation
            email = url.replace('mailto:', '')
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            if re.match(email_pattern, email):
                result['status'] = 'pass'
                result['valid_format'] = True
                self.log_result("Email Links", f"Valid format - {email}", "PASS",
                               {"url": url})
            else:
                result['status'] = 'fail'
                result['error'] = 'Invalid email format'
                self.log_result("Email Links", f"Invalid format - {email}", "FAIL",
                               {"url": url, "error": result['error']})
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.log_result("Email Links", f"Validation error - {url}", "FAIL",
                           {"url": url, "error": str(e)})
        
        return result
    
    def check_all_links_parallel(self, links: List[Dict[str, Any]], max_workers: int = 10):
        """Check all links in parallel for better performance"""
        external_links_to_check = []
        
        for link in links:
            url = link['url']
            category = self.categorize_link(url)
            
            if category == 'external':
                # Resolve relative URLs
                if not url.startswith(('http://', 'https://')):
                    url = self.resolve_relative_url(url, Path(link['file']))
                external_links_to_check.append((url, link))
        
        # Check external links in parallel
        if external_links_to_check:
            print(f"\n🌐 Checking {len(external_links_to_check)} external links...")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_link = {
                    executor.submit(self.check_external_link, url): (url, link_data)
                    for url, link_data in external_links_to_check
                }
                
                for future in concurrent.futures.as_completed(future_to_link):
                    url, link_data = future_to_link[future]
                    try:
                        result = future.result()
                        if result['status'] == 'fail':
                            self.broken_links.append({
                                'url': url,
                                'file': link_data['file'],
                                'error': result['error'],
                                'type': 'external'
                            })
                    except Exception as e:
                        self.log_result("External Links", f"Parallel check error - {urlparse(url).netloc}", "FAIL",
                                       {"url": url, "error": str(e)})
    
    def analyze_link_patterns(self, links: List[Dict[str, Any]]):
        """Analyze links for suspicious patterns"""
        print("\n🔍 Analyzing link patterns...")
        
        # Check for suspicious external domains
        suspicious_domains = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 't.co',  # URL shorteners
            'example.com', 'test.com', 'localhost',     # Test domains
            'placeholder.com', 'sample.com'             # Placeholder domains
        ]
        
        domain_counts = defaultdict(int)
        
        for link in links:
            url = link['url']
            category = self.categorize_link(url)
            
            if category == 'external':
                try:
                    domain = urlparse(url).netloc.lower()
                    domain_counts[domain] += 1
                    
                    if any(sus_domain in domain for sus_domain in suspicious_domains):
                        self.suspicious_links.append({
                            'url': url,
                            'file': link['file'],
                            'reason': 'Suspicious domain',
                            'domain': domain
                        })
                        self.log_result("Suspicious Links", f"Suspicious domain - {domain}", "WARN",
                                       {"url": url, "file": link['file'], "domain": domain})
                
                except Exception as e:
                    continue
        
        # Report most linked domains
        if domain_counts:
            print(f"\n📊 Most linked external domains:")
            for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {domain}: {count} links")
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run comprehensive link checking"""
        print("🔗 Starting Comprehensive Link Check")
        print("Batch 199 - Phase 1 QA Pass & Bug Review")
        print("=" * 60)
        
        # Discover HTML files
        print("\n📁 Discovering HTML files...")
        html_files = self.discover_html_files()
        
        if not html_files:
            self.log_result("Discovery", "HTML Files", "FAIL",
                           {"error": "No HTML files found to check"})
            return self.generate_report()
        
        self.log_result("Discovery", "HTML Files", "PASS",
                       {"files_found": len(html_files)})
        
        # Extract all links
        print(f"\n🔍 Extracting links from {len(html_files)} files...")
        all_links = []
        
        for file_path in html_files:
            links = self.extract_links_from_html(file_path)
            all_links.extend(links)
        
        if not all_links:
            self.log_result("Discovery", "Links Found", "WARN",
                           {"warning": "No links found in HTML files"})
            return self.generate_report()
        
        self.log_result("Discovery", "Links Found", "PASS",
                       {"total_links": len(all_links)})
        
        # Categorize links
        print(f"\n📊 Categorizing {len(all_links)} links...")
        categories = defaultdict(list)
        
        for link in all_links:
            category = self.categorize_link(link['url'])
            categories[category].append(link)
        
        # Report categories
        for category, links in categories.items():
            self.log_result("Categories", f"{category.title()} Links", "INFO",
                           {"count": len(links)})
        
        # Check internal links
        print(f"\n🏠 Checking internal links...")
        for link in categories.get('internal_relative', []) + categories.get('internal_absolute', []):
            url = link['url']
            if not url.startswith(('http://', 'https://')):
                url = self.resolve_relative_url(url, Path(link['file']))
            
            result = self.check_internal_link(url, link['file'])
            if result['status'] == 'fail':
                self.broken_links.append({
                    'url': url,
                    'file': link['file'],
                    'error': result['error'],
                    'type': 'internal'
                })
        
        # Check anchor links
        print(f"\n⚓ Checking anchor links...")
        for link in categories.get('anchor', []):
            result = self.check_anchor_link(link['url'], link['file'])
            if result['status'] == 'fail':
                self.broken_links.append({
                    'url': link['url'],
                    'file': link['file'],
                    'error': result['error'],
                    'type': 'anchor'
                })
        
        # Check email links
        print(f"\n📧 Checking email links...")
        for link in categories.get('email', []):
            result = self.validate_email_link(link['url'])
            if result['status'] == 'fail':
                self.broken_links.append({
                    'url': link['url'],
                    'file': link['file'],
                    'error': result['error'],
                    'type': 'email'
                })
        
        # Check external links (parallel)
        self.check_all_links_parallel(categories.get('external', []))
        
        # Analyze patterns
        self.analyze_link_patterns(all_links)
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive link check report"""
        print("\n📊 Generating Link Check Report...")
        
        total_checks = len(self.results)
        passed_checks = len([r for r in self.results if r['status'] == 'PASS'])
        failed_checks = len([r for r in self.results if r['status'] == 'FAIL'])
        warning_checks = len([r for r in self.results if r['status'] in ['WARN', 'INFO']])
        
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        report = {
            'batch_id': 'BATCH_199',
            'test_name': 'Comprehensive Link Check',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_checks': total_checks,
                'passed': passed_checks,
                'failed': failed_checks,
                'warnings': warning_checks,
                'success_rate': round(success_rate, 2)
            },
            'broken_links': {
                'total': len(self.broken_links),
                'by_type': defaultdict(int),
                'details': self.broken_links
            },
            'performance_issues': {
                'slow_links': self.slow_links,
                'redirect_chains': self.redirect_chains
            },
            'security_concerns': {
                'suspicious_links': self.suspicious_links
            },
            'detailed_results': self.results,
            'recommendations': []
        }
        
        # Categorize broken links
        for broken_link in self.broken_links:
            report['broken_links']['by_type'][broken_link['type']] += 1
        
        # Add recommendations
        if failed_checks == 0 and len(self.broken_links) == 0:
            report['recommendations'].append("✅ All links are valid and working correctly")
        else:
            report['recommendations'].append(f"🔧 Fix {len(self.broken_links)} broken links")
        
        if self.slow_links:
            report['recommendations'].append(f"⚡ Optimize {len(self.slow_links)} slow-loading external links")
        
        if self.suspicious_links:
            report['recommendations'].append(f"🔒 Review {len(self.suspicious_links)} suspicious links")
        
        # Save report
        report_file = f"QA_LINK_CHECK_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Link Check Report saved to: {report_file}")
        return report

def main():
    """Main link checker runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Link Checker')
    parser.add_argument('--base-url', default='https://morningstar.swg.ms11.com',
                       help='Base URL for the site')
    parser.add_argument('--build-dir', default='dist',
                       help='Build directory to check')
    parser.add_argument('--max-workers', type=int, default=10,
                       help='Maximum parallel workers for external link checks')
    
    args = parser.parse_args()
    
    checker = LinkChecker(base_url=args.base_url, build_dir=args.build_dir)
    
    try:
        report = checker.run_comprehensive_check()
        
        print("\n" + "=" * 60)
        print("🎯 Link Check Complete!")
        print(f"📊 Success Rate: {report['summary']['success_rate']}%")
        print(f"📋 Checks: {report['summary']['passed']}/{report['summary']['total_checks']} passed")
        print(f"🔗 Broken Links: {report['broken_links']['total']}")
        
        if report['broken_links']['total'] > 0:
            print(f"\n💥 Broken Links by Type:")
            for link_type, count in report['broken_links']['by_type'].items():
                print(f"   {link_type}: {count}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        
        # Exit with appropriate code
        sys.exit(0 if report['broken_links']['total'] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Link check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Link check failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
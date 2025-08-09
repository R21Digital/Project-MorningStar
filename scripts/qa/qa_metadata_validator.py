#!/usr/bin/env python3
"""
QA Metadata Validator - Missing images and metadata validation
Batch 199 - Phase 1 QA Pass & Bug Review
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from bs4 import BeautifulSoup
from PIL import Image
import requests
from urllib.parse import urljoin, urlparse

class MetadataValidator:
    """Missing images and metadata validation system"""
    
    def __init__(self, build_dir: str = "dist", base_url: str = None):
        self.build_dir = Path(build_dir)
        self.project_root = Path(__file__).parent.parent
        self.base_url = base_url or "https://morningstar.swg.ms11.com"
        self.results = []
        
        # Track resources
        self.missing_images = []
        self.missing_metadata = []
        self.duplicate_images = []
        self.oversized_images = []
        self.unoptimized_images = []
        
        # SEO and metadata requirements
        self.required_meta_tags = [
            'title', 'description', 'keywords', 'author',
            'viewport', 'charset'
        ]
        
        self.og_tags = [
            'og:title', 'og:description', 'og:image', 'og:url',
            'og:type', 'og:site_name'
        ]
        
        self.twitter_tags = [
            'twitter:card', 'twitter:title', 'twitter:description',
            'twitter:image'
        ]
        
        # Image optimization thresholds
        self.max_image_size = 2 * 1024 * 1024  # 2MB
        self.recommended_image_size = 500 * 1024  # 500KB
        self.max_image_dimensions = (2000, 2000)
        
        # Supported image formats
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico'}
    
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
        """Discover all HTML files for metadata validation"""
        html_files = []
        
        # Check build directory
        if self.build_dir.exists():
            html_files.extend(self.build_dir.rglob("*.html"))
        
        # Check source templates
        src_pages = self.project_root / "src/pages"
        if src_pages.exists():
            html_files.extend(src_pages.rglob("*.html"))
            html_files.extend(src_pages.rglob("*.njk"))
            html_files.extend(src_pages.rglob("*.11ty.js"))
        
        # Check website directory
        website_dir = self.project_root / "website"
        if website_dir.exists():
            html_files.extend(website_dir.rglob("*.html"))
        
        return list(set(html_files))
    
    def discover_image_files(self) -> List[Path]:
        """Discover all image files in the project"""
        image_files = []
        
        # Common image directories
        image_dirs = [
            self.build_dir / "assets",
            self.build_dir / "images",
            self.build_dir / "img",
            self.project_root / "assets",
            self.project_root / "images",
            self.project_root / "img",
            self.project_root / "src/assets",
            self.project_root / "static",
            self.project_root / "public"
        ]
        
        for image_dir in image_dirs:
            if image_dir.exists():
                for ext in self.supported_formats:
                    image_files.extend(image_dir.rglob(f"*{ext}"))
        
        return list(set(image_files))
    
    def extract_referenced_images(self, html_files: List[Path]) -> Set[str]:
        """Extract all image references from HTML files"""
        referenced_images = set()
        
        for file_path in html_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Handle different file types
                if file_path.suffix == '.11ty.js':
                    # Extract image references from JavaScript templates
                    import re
                    img_patterns = [
                        r'["\']([^"\']*\.(?:jpg|jpeg|png|gif|svg|webp|ico))["\']',
                        r'src\s*:\s*["\']([^"\']+)["\']',
                        r'image\s*:\s*["\']([^"\']+)["\']'
                    ]
                    
                    for pattern in img_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        referenced_images.update(matches)
                else:
                    # Parse HTML content
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract img src attributes
                    for img in soup.find_all('img', src=True):
                        referenced_images.add(img['src'])
                    
                    # Extract CSS background images
                    for element in soup.find_all(style=True):
                        style = element['style']
                        if 'background-image' in style:
                            import re
                            bg_images = re.findall(r'url\(["\']?([^"\']+)["\']?\)', style)
                            referenced_images.update(bg_images)
                    
                    # Extract link icons
                    for link in soup.find_all('link', href=True):
                        rel = link.get('rel', [])
                        if 'icon' in rel or 'apple-touch-icon' in rel:
                            referenced_images.add(link['href'])
                    
                    # Extract Open Graph images
                    for meta in soup.find_all('meta', attrs={'property': True}):
                        if meta['property'] == 'og:image':
                            content_attr = meta.get('content')
                            if content_attr:
                                referenced_images.add(content_attr)
            
            except Exception as e:
                self.log_result("Image Discovery", f"Parse error - {file_path.name}", "WARN",
                               {"file": str(file_path), "error": str(e)})
        
        # Clean up relative paths and data URLs
        cleaned_images = set()
        for img_url in referenced_images:
            if img_url.startswith('data:'):
                continue  # Skip data URLs
            if img_url.startswith('http'):
                # Extract path from absolute URLs
                parsed = urlparse(img_url)
                cleaned_images.add(parsed.path.lstrip('/'))
            else:
                cleaned_images.add(img_url.lstrip('/'))
        
        return cleaned_images
    
    def validate_image_exists(self, image_path: str, all_image_files: List[Path]) -> bool:
        """Check if an image file exists"""
        # Normalize path
        normalized_path = Path(image_path.lstrip('/'))
        
        # Check in build directory
        if self.build_dir.exists():
            build_image_path = self.build_dir / normalized_path
            if build_image_path.exists():
                return True
        
        # Check against discovered image files
        for image_file in all_image_files:
            if normalized_path.name == image_file.name:
                return True
            if str(normalized_path) in str(image_file):
                return True
        
        return False
    
    def analyze_image_properties(self, image_path: Path) -> Dict[str, Any]:
        """Analyze image properties for optimization"""
        analysis = {
            'file': str(image_path),
            'size_bytes': 0,
            'dimensions': (0, 0),
            'format': '',
            'issues': [],
            'optimizations': []
        }
        
        try:
            # Get file size
            analysis['size_bytes'] = image_path.stat().st_size
            
            # Check file size
            if analysis['size_bytes'] > self.max_image_size:
                analysis['issues'].append(f"File too large: {analysis['size_bytes'] / 1024 / 1024:.1f}MB")
            elif analysis['size_bytes'] > self.recommended_image_size:
                analysis['optimizations'].append(f"Could be optimized: {analysis['size_bytes'] / 1024:.0f}KB")
            
            # Analyze image with PIL (skip SVG files)
            if image_path.suffix.lower() != '.svg':
                try:
                    with Image.open(image_path) as img:
                        analysis['dimensions'] = img.size
                        analysis['format'] = img.format
                        
                        # Check dimensions
                        width, height = img.size
                        if width > self.max_image_dimensions[0] or height > self.max_image_dimensions[1]:
                            analysis['issues'].append(f"Dimensions too large: {width}x{height}")
                        
                        # Check for modern formats
                        if img.format in ['JPEG', 'PNG'] and analysis['size_bytes'] > 100 * 1024:
                            analysis['optimizations'].append("Consider WebP format for better compression")
                        
                        # Check for unnecessary transparency
                        if img.format == 'PNG' and img.mode == 'RGBA':
                            # Check if transparency is actually used
                            if img.getextrema()[-1] == (255, 255):  # No transparency
                                analysis['optimizations'].append("PNG with unused transparency - consider JPEG")
                
                except Exception as e:
                    analysis['issues'].append(f"Cannot analyze image: {str(e)}")
            
            else:
                analysis['format'] = 'SVG'
                analysis['dimensions'] = ('vector', 'vector')
        
        except Exception as e:
            analysis['issues'].append(f"File access error: {str(e)}")
        
        return analysis
    
    def validate_metadata_tags(self, file_path: Path) -> Dict[str, Any]:
        """Validate metadata tags in HTML files"""
        validation = {
            'file': str(file_path),
            'missing_tags': [],
            'invalid_tags': [],
            'recommendations': [],
            'seo_score': 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip non-HTML files
            if file_path.suffix not in ['.html', '.htm']:
                return validation
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Check basic meta tags
            found_tags = set()
            
            # Title tag
            title = soup.find('title')
            if title and title.get_text(strip=True):
                found_tags.add('title')
                title_text = title.get_text()
                if len(title_text) < 30:
                    validation['recommendations'].append("Title is short - consider 30-60 characters")
                elif len(title_text) > 60:
                    validation['recommendations'].append("Title is long - consider keeping under 60 characters")
            else:
                validation['missing_tags'].append('title')
            
            # Meta description
            description = soup.find('meta', attrs={'name': 'description'})
            if description and description.get('content'):
                found_tags.add('description')
                desc_content = description['content']
                if len(desc_content) < 120:
                    validation['recommendations'].append("Meta description is short - consider 120-160 characters")
                elif len(desc_content) > 160:
                    validation['recommendations'].append("Meta description is long - consider keeping under 160 characters")
            else:
                validation['missing_tags'].append('description')
            
            # Meta keywords (less important now, but still worth checking)
            keywords = soup.find('meta', attrs={'name': 'keywords'})
            if keywords and keywords.get('content'):
                found_tags.add('keywords')
            
            # Meta author
            author = soup.find('meta', attrs={'name': 'author'})
            if author and author.get('content'):
                found_tags.add('author')
            
            # Viewport (mobile)
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            if viewport and viewport.get('content'):
                found_tags.add('viewport')
                viewport_content = viewport['content']
                if 'width=device-width' not in viewport_content:
                    validation['invalid_tags'].append('viewport: missing width=device-width')
            else:
                validation['missing_tags'].append('viewport')
            
            # Charset
            charset = soup.find('meta', attrs={'charset': True})
            if not charset:
                charset = soup.find('meta', attrs={'http-equiv': 'Content-Type'})
            if charset:
                found_tags.add('charset')
            else:
                validation['missing_tags'].append('charset')
            
            # Open Graph tags
            og_found = set()
            for tag in self.og_tags:
                og_meta = soup.find('meta', attrs={'property': tag})
                if og_meta and og_meta.get('content'):
                    og_found.add(tag)
            
            # Twitter Card tags
            twitter_found = set()
            for tag in self.twitter_tags:
                twitter_meta = soup.find('meta', attrs={'name': tag})
                if twitter_meta and twitter_meta.get('content'):
                    twitter_found.add(tag)
            
            # Calculate SEO score
            base_score = len(found_tags) / len(self.required_meta_tags) * 40
            og_score = len(og_found) / len(self.og_tags) * 30
            twitter_score = len(twitter_found) / len(self.twitter_tags) * 20
            
            # Additional SEO factors
            additional_score = 0
            
            # Check for canonical URL
            canonical = soup.find('link', attrs={'rel': 'canonical'})
            if canonical:
                additional_score += 2
            
            # Check for structured data
            json_ld = soup.find_all('script', attrs={'type': 'application/ld+json'})
            if json_ld:
                additional_score += 3
            
            # Check for proper heading structure
            h1_tags = soup.find_all('h1')
            if len(h1_tags) == 1:
                additional_score += 2
            elif len(h1_tags) > 1:
                validation['recommendations'].append("Multiple H1 tags found - use only one per page")
            
            # Check for alt text on images
            images = soup.find_all('img')
            images_with_alt = len([img for img in images if img.get('alt')])
            if images and images_with_alt == len(images):
                additional_score += 3
            elif images:
                validation['recommendations'].append(f"{len(images) - images_with_alt} images missing alt text")
            
            validation['seo_score'] = min(100, base_score + og_score + twitter_score + additional_score)
            
            # Check for missing Open Graph tags if any are present
            if og_found and len(og_found) < len(self.og_tags):
                missing_og = set(self.og_tags) - og_found
                validation['missing_tags'].extend([f"og:{tag.split(':')[1]}" for tag in missing_og])
            
            # Check for missing Twitter tags if any are present
            if twitter_found and len(twitter_found) < len(self.twitter_tags):
                missing_twitter = set(self.twitter_tags) - twitter_found
                validation['missing_tags'].extend([f"twitter:{tag.split(':')[1]}" for tag in missing_twitter])
        
        except Exception as e:
            validation['invalid_tags'].append(f"Parse error: {str(e)}")
        
        return validation
    
    def find_duplicate_images(self, image_files: List[Path]) -> List[Dict[str, Any]]:
        """Find duplicate images based on content hash"""
        duplicates = []
        hash_map = {}
        
        for image_file in image_files:
            try:
                # Calculate file hash
                hasher = hashlib.md5()
                with open(image_file, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hasher.update(chunk)
                
                file_hash = hasher.hexdigest()
                
                if file_hash in hash_map:
                    # Found duplicate
                    duplicates.append({
                        'original': str(hash_map[file_hash]),
                        'duplicate': str(image_file),
                        'hash': file_hash,
                        'size': image_file.stat().st_size
                    })
                else:
                    hash_map[file_hash] = image_file
            
            except Exception as e:
                continue  # Skip files that can't be read
        
        return duplicates
    
    def validate_favicon_and_icons(self, html_files: List[Path]) -> Dict[str, Any]:
        """Validate favicon and icon configuration"""
        validation = {
            'favicon_found': False,
            'apple_touch_icons': [],
            'manifest_found': False,
            'issues': [],
            'recommendations': []
        }
        
        for file_path in html_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if file_path.suffix not in ['.html', '.htm']:
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Check for favicon
                favicon_links = soup.find_all('link', rel=lambda x: x and 'icon' in x)
                if favicon_links:
                    validation['favicon_found'] = True
                    
                    for link in favicon_links:
                        href = link.get('href')
                        if href:
                            # Check if favicon file exists
                            if not self.validate_image_exists(href, []):
                                validation['issues'].append(f"Favicon not found: {href}")
                
                # Check for Apple Touch Icons
                apple_icons = soup.find_all('link', rel=lambda x: x and 'apple-touch-icon' in x)
                for icon in apple_icons:
                    sizes = icon.get('sizes', 'default')
                    href = icon.get('href')
                    validation['apple_touch_icons'].append({
                        'sizes': sizes,
                        'href': href
                    })
                    
                    if href and not self.validate_image_exists(href, []):
                        validation['issues'].append(f"Apple touch icon not found: {href}")
                
                # Check for web app manifest
                manifest = soup.find('link', rel='manifest')
                if manifest:
                    validation['manifest_found'] = True
                    manifest_href = manifest.get('href')
                    if manifest_href:
                        # Could check if manifest file exists
                        pass
                
                break  # Only need to check one main HTML file
            
            except Exception as e:
                continue
        
        # Add recommendations
        if not validation['favicon_found']:
            validation['issues'].append("No favicon found")
            validation['recommendations'].append("Add favicon for better branding")
        
        if not validation['apple_touch_icons']:
            validation['recommendations'].append("Add Apple Touch Icons for iOS devices")
        
        if not validation['manifest_found']:
            validation['recommendations'].append("Add web app manifest for PWA capabilities")
        
        return validation
    
    def run_metadata_validation(self) -> Dict[str, Any]:
        """Run comprehensive metadata and image validation"""
        print("🖼️ Starting Metadata & Image Validator")
        print("Batch 199 - Phase 1 QA Pass & Bug Review")
        print("=" * 60)
        
        # Discover files
        print("\n📁 Discovering files...")
        html_files = self.discover_html_files()
        image_files = self.discover_image_files()
        
        self.log_result("Discovery", "HTML Files", "PASS" if html_files else "WARN",
                       {"count": len(html_files)})
        self.log_result("Discovery", "Image Files", "PASS" if image_files else "WARN",
                       {"count": len(image_files)})
        
        # Extract referenced images
        print(f"\n🔍 Extracting image references...")
        referenced_images = self.extract_referenced_images(html_files)
        
        self.log_result("Discovery", "Referenced Images", "PASS",
                       {"count": len(referenced_images)})
        
        # Check for missing images
        print(f"\n📷 Checking for missing images...")
        missing_count = 0
        
        for img_path in referenced_images:
            if not self.validate_image_exists(img_path, image_files):
                self.missing_images.append(img_path)
                missing_count += 1
                self.log_result("Missing Images", f"Image not found - {img_path}", "FAIL",
                               {"error": f"Referenced image not found: {img_path}"})
        
        if missing_count == 0:
            self.log_result("Missing Images", "All referenced images found", "PASS")
        
        # Analyze image properties
        print(f"\n🔬 Analyzing image properties...")
        for image_file in image_files[:50]:  # Limit to first 50 for performance
            analysis = self.analyze_image_properties(image_file)
            
            if analysis['issues']:
                for issue in analysis['issues']:
                    if 'too large' in issue:
                        self.oversized_images.append({
                            'file': str(image_file),
                            'issue': issue,
                            'size': analysis['size_bytes']
                        })
                        self.log_result("Image Optimization", f"{image_file.name} - {issue}", "WARN",
                                       {"file": str(image_file), "error": issue})
            
            if analysis['optimizations']:
                for optimization in analysis['optimizations']:
                    self.unoptimized_images.append({
                        'file': str(image_file),
                        'optimization': optimization
                    })
                    self.log_result("Image Optimization", f"{image_file.name} - {optimization}", "INFO",
                                   {"file": str(image_file)})
        
        # Find duplicate images
        print(f"\n🔄 Checking for duplicate images...")
        duplicates = self.find_duplicate_images(image_files)
        self.duplicate_images = duplicates
        
        if duplicates:
            for duplicate in duplicates:
                self.log_result("Duplicate Images", f"Duplicate found", "WARN",
                               {"original": duplicate['original'], 
                                "duplicate": duplicate['duplicate'],
                                "size": duplicate['size']})
        else:
            self.log_result("Duplicate Images", "No duplicates found", "PASS")
        
        # Validate metadata tags
        print(f"\n🏷️ Validating metadata tags...")
        metadata_issues = 0
        
        for file_path in html_files:
            validation = self.validate_metadata_tags(file_path)
            
            if validation['missing_tags']:
                metadata_issues += len(validation['missing_tags'])
                for tag in validation['missing_tags']:
                    self.missing_metadata.append({
                        'file': str(file_path),
                        'tag': tag,
                        'type': 'missing'
                    })
                    self.log_result("Metadata", f"{file_path.name} - Missing {tag}", "FAIL",
                                   {"file": str(file_path), "error": f"Missing {tag} tag"})
            
            if validation['invalid_tags']:
                metadata_issues += len(validation['invalid_tags'])
                for tag in validation['invalid_tags']:
                    self.missing_metadata.append({
                        'file': str(file_path),
                        'tag': tag,
                        'type': 'invalid'
                    })
                    self.log_result("Metadata", f"{file_path.name} - Invalid {tag}", "FAIL",
                                   {"file": str(file_path), "error": f"Invalid {tag}"})
            
            # Report SEO score
            if validation['seo_score'] >= 80:
                self.log_result("SEO", f"{file_path.name} - Score: {validation['seo_score']:.0f}%", "PASS",
                               {"file": str(file_path), "score": validation['seo_score']})
            else:
                self.log_result("SEO", f"{file_path.name} - Score: {validation['seo_score']:.0f}%", "WARN",
                               {"file": str(file_path), "score": validation['seo_score']})
        
        # Validate favicons and icons
        print(f"\n🎯 Validating favicons and icons...")
        icon_validation = self.validate_favicon_and_icons(html_files)
        
        if icon_validation['issues']:
            for issue in icon_validation['issues']:
                self.log_result("Icons", f"Icon issue - {issue}", "FAIL",
                               {"error": issue})
        else:
            self.log_result("Icons", "Icon validation passed", "PASS")
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive metadata validation report"""
        print("\n📊 Generating Metadata Validation Report...")
        
        total_checks = len(self.results)
        passed_checks = len([r for r in self.results if r['status'] == 'PASS'])
        failed_checks = len([r for r in self.results if r['status'] == 'FAIL'])
        warning_checks = len([r for r in self.results if r['status'] in ['WARN', 'INFO']])
        
        success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        report = {
            'batch_id': 'BATCH_199',
            'test_name': 'Metadata & Image Validator',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_checks': total_checks,
                'passed': passed_checks,
                'failed': failed_checks,
                'warnings': warning_checks,
                'success_rate': round(success_rate, 2)
            },
            'missing_images': {
                'count': len(self.missing_images),
                'details': self.missing_images
            },
            'missing_metadata': {
                'count': len(self.missing_metadata),
                'details': self.missing_metadata
            },
            'image_optimization': {
                'oversized': len(self.oversized_images),
                'unoptimized': len(self.unoptimized_images),
                'duplicates': len(self.duplicate_images),
                'details': {
                    'oversized': self.oversized_images,
                    'unoptimized': self.unoptimized_images,
                    'duplicates': self.duplicate_images
                }
            },
            'detailed_results': self.results,
            'recommendations': []
        }
        
        # Add recommendations
        if len(self.missing_images) == 0 and len(self.missing_metadata) == 0:
            report['recommendations'].append("✅ All images and metadata are properly configured")
        
        if self.missing_images:
            report['recommendations'].append(f"🖼️ Fix {len(self.missing_images)} missing image references")
        
        if self.missing_metadata:
            report['recommendations'].append(f"🏷️ Add {len(self.missing_metadata)} missing metadata tags")
        
        if self.oversized_images:
            report['recommendations'].append(f"📦 Optimize {len(self.oversized_images)} oversized images")
        
        if self.duplicate_images:
            report['recommendations'].append(f"🔄 Remove {len(self.duplicate_images)} duplicate images")
        
        if self.unoptimized_images:
            report['recommendations'].append(f"⚡ Consider optimizing {len(self.unoptimized_images)} images for better performance")
        
        # Save report
        report_file = f"QA_METADATA_VALIDATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Metadata Validation Report saved to: {report_file}")
        return report

def main():
    """Main metadata validator runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Metadata & Image Validator')
    parser.add_argument('--build-dir', default='dist',
                       help='Build directory to analyze')
    parser.add_argument('--base-url', default='https://morningstar.swg.ms11.com',
                       help='Base URL for the site')
    
    args = parser.parse_args()
    
    validator = MetadataValidator(build_dir=args.build_dir, base_url=args.base_url)
    
    try:
        report = validator.run_metadata_validation()
        
        print("\n" + "=" * 60)
        print("🎯 Metadata Validation Complete!")
        print(f"📊 Success Rate: {report['summary']['success_rate']}%")
        print(f"📋 Checks: {report['summary']['passed']}/{report['summary']['total_checks']} passed")
        print(f"🖼️ Missing Images: {report['missing_images']['count']}")
        print(f"🏷️ Missing Metadata: {report['missing_metadata']['count']}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        
        # Exit with appropriate code
        sys.exit(0 if failed_checks == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Metadata validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Metadata validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
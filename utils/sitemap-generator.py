#!/usr/bin/env python3
"""
SEO Metadata and Sitemap Generator for SWGDB
Automatically generates sitemap.xml and injects meta tags for optimal search visibility
"""

import os
import json
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from xml.dom import minidom
import hashlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SEOMetadataManager:
    """Manages SEO metadata and sitemap generation for SWGDB"""
    
    def __init__(self, base_url: str = "https://swgdb.com", output_dir: str = "website"):
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # SEO configuration
        self.default_meta = {
            "site_name": "SWGDB - Star Wars Galaxies Database",
            "description": "The ultimate Star Wars Galaxies database with heroic guides, character builds, loot tables, and community tools.",
            "keywords": ["Star Wars Galaxies", "SWG", "heroics", "builds", "loot", "database", "guides"],
            "author": "SWGDB Community",
            "og_type": "website",
            "og_image": f"{self.base_url}/static/images/swgdb-social-banner.jpg",
            "twitter_card": "summary_large_image",
            "twitter_creator": "@swgdb",
        }
        
        # Content discovery paths
        self.content_paths = [
            ("dashboard/templates", "html"),
            ("data", "json,yaml,yml"),
            ("docs", "md"),
            ("api", "py")
        ]
        
        # URL patterns and priorities
        self.url_patterns = {
            '/': {'priority': '1.0', 'changefreq': 'daily'},
            '/heroics': {'priority': '0.9', 'changefreq': 'weekly'},
            '/builds': {'priority': '0.9', 'changefreq': 'weekly'},
            '/loot': {'priority': '0.8', 'changefreq': 'weekly'},
            '/guides': {'priority': '0.8', 'changefreq': 'weekly'},
            '/tools': {'priority': '0.7', 'changefreq': 'monthly'},
            '/players': {'priority': '0.6', 'changefreq': 'weekly'},
            '/api': {'priority': '0.5', 'changefreq': 'monthly'},
        }

    def discover_content(self) -> List[Dict[str, Any]]:
        """Discover all content files and generate page metadata"""
        pages = []
        
        # Discover HTML templates
        templates_dir = Path("dashboard/templates")
        if templates_dir.exists():
            for template_file in templates_dir.rglob("*.html"):
                if not template_file.name.startswith('_'):  # Skip partials
                    page = self._analyze_template(template_file)
                    if page:
                        pages.append(page)
        
        # Discover data-driven pages
        data_dir = Path("data")
        if data_dir.exists():
            pages.extend(self._discover_data_pages(data_dir))
        
        # Add API endpoints
        pages.extend(self._discover_api_endpoints())
        
        # Add static pages
        pages.extend(self._get_static_pages())
        
        return pages

    def _analyze_template(self, template_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze HTML template to extract metadata"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from template
            title = self._extract_html_title(content)
            if not title:
                title = self._generate_title_from_filename(template_path.stem)
            
            # Generate URL from template path
            url_path = self._generate_url_from_template(template_path)
            
            # Determine page type and metadata
            page_type = self._determine_page_type(template_path, content)
            description = self._generate_description(page_type, title, content)
            keywords = self._generate_keywords(page_type, content)
            
            return {
                'url': url_path,
                'title': title,
                'description': description,
                'keywords': keywords,
                'page_type': page_type,
                'template': str(template_path),
                'last_modified': datetime.fromtimestamp(template_path.stat().st_mtime),
                'priority': self._get_priority(url_path),
                'changefreq': self._get_changefreq(url_path)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing template {template_path}: {e}")
            return None

    def _discover_data_pages(self, data_dir: Path) -> List[Dict[str, Any]]:
        """Discover pages generated from data files"""
        pages = []
        
        # Heroic pages
        heroics_dir = data_dir / "heroics"
        if heroics_dir.exists():
            for heroic_file in heroics_dir.glob("*.json"):
                try:
                    with open(heroic_file, 'r', encoding='utf-8') as f:
                        heroic_data = json.load(f)
                    
                    heroic_name = heroic_data.get('name', heroic_file.stem)
                    pages.append({
                        'url': f'/heroics/{heroic_file.stem}',
                        'title': f"{heroic_name} - Heroic Guide - SWGDB",
                        'description': f"Complete guide for {heroic_name} heroic instance including loot tables, strategies, and tips.",
                        'keywords': ['heroic', heroic_name.lower(), 'guide', 'loot', 'strategy'],
                        'page_type': 'heroic_guide',
                        'data_file': str(heroic_file),
                        'last_modified': datetime.fromtimestamp(heroic_file.stat().st_mtime),
                        'priority': '0.9',
                        'changefreq': 'weekly'
                    })
                except Exception as e:
                    logger.error(f"Error processing heroic file {heroic_file}: {e}")
        
        # Build pages
        builds_dir = data_dir / "builds"
        if builds_dir.exists():
            for build_file in builds_dir.glob("*.json"):
                try:
                    with open(build_file, 'r', encoding='utf-8') as f:
                        build_data = json.load(f)
                    
                    build_name = build_data.get('name', build_file.stem)
                    profession = build_data.get('profession', 'Unknown')
                    pages.append({
                        'url': f'/builds/{build_file.stem}',
                        'title': f"{build_name} - {profession} Build - SWGDB",
                        'description': f"{profession} character build: {build_name}. Skills, equipment recommendations, and gameplay tips.",
                        'keywords': ['character build', profession.lower(), build_name.lower(), 'skills', 'template'],
                        'page_type': 'character_build',
                        'data_file': str(build_file),
                        'last_modified': datetime.fromtimestamp(build_file.stat().st_mtime),
                        'priority': '0.8',
                        'changefreq': 'monthly'
                    })
                except Exception as e:
                    logger.error(f"Error processing build file {build_file}: {e}")
        
        # Quest pages
        quests_dir = data_dir / "quests"
        if quests_dir.exists():
            for quest_file in quests_dir.rglob("*.json"):
                try:
                    with open(quest_file, 'r', encoding='utf-8') as f:
                        quest_data = json.load(f)
                    
                    quest_name = quest_data.get('name', quest_file.stem)
                    planet = quest_data.get('planet', 'Unknown')
                    pages.append({
                        'url': f'/quests/{planet}/{quest_file.stem}',
                        'title': f"{quest_name} - {planet.title()} Quest - SWGDB",
                        'description': f"Quest guide for {quest_name} on {planet}. Steps, rewards, and completion tips.",
                        'keywords': ['quest', quest_name.lower(), planet.lower(), 'guide', 'walkthrough'],
                        'page_type': 'quest_guide',
                        'data_file': str(quest_file),
                        'last_modified': datetime.fromtimestamp(quest_file.stat().st_mtime),
                        'priority': '0.7',
                        'changefreq': 'monthly'
                    })
                except Exception as e:
                    logger.error(f"Error processing quest file {quest_file}: {e}")
        
        return pages

    def _discover_api_endpoints(self) -> List[Dict[str, Any]]:
        """Discover API endpoints for documentation"""
        pages = []
        
        api_endpoints = [
            {'path': '/api', 'name': 'API Documentation', 'description': 'SWGDB REST API documentation and endpoints'},
            {'path': '/api/builds', 'name': 'Builds API', 'description': 'Character builds API endpoint with search and filtering'},
            {'path': '/api/heroics', 'name': 'Heroics API', 'description': 'Heroic instances API with loot and guide data'},
            {'path': '/api/loot', 'name': 'Loot API', 'description': 'Item and loot database API with advanced search'},
            {'path': '/api/players', 'name': 'Players API', 'description': 'Player profiles and statistics API'},
        ]
        
        for endpoint in api_endpoints:
            pages.append({
                'url': endpoint['path'],
                'title': f"{endpoint['name']} - SWGDB API",
                'description': endpoint['description'],
                'keywords': ['api', 'documentation', 'rest', 'json', 'swgdb'],
                'page_type': 'api_documentation',
                'last_modified': datetime.now(),
                'priority': '0.5',
                'changefreq': 'monthly'
            })
        
        return pages

    def _get_static_pages(self) -> List[Dict[str, Any]]:
        """Define static pages with their metadata"""
        return [
            {
                'url': '/',
                'title': 'SWGDB - Star Wars Galaxies Database & Community Platform',
                'description': 'The ultimate Star Wars Galaxies database with heroic guides, character builds, loot tables, and community tools.',
                'keywords': ['star wars galaxies', 'swg', 'database', 'heroics', 'builds', 'loot', 'guides'],
                'page_type': 'homepage',
                'last_modified': datetime.now(),
                'priority': '1.0',
                'changefreq': 'daily'
            },
            {
                'url': '/about',
                'title': 'About SWGDB - Star Wars Galaxies Database',
                'description': 'Learn about SWGDB, the community-driven Star Wars Galaxies database and resource platform.',
                'keywords': ['about', 'swgdb', 'community', 'open source', 'star wars galaxies'],
                'page_type': 'about',
                'last_modified': datetime.now(),
                'priority': '0.6',
                'changefreq': 'monthly'
            },
            {
                'url': '/feedback',
                'title': 'Submit Feedback - SWGDB',
                'description': 'Report bugs, suggest features, or share feedback to help improve SWGDB for the community.',
                'keywords': ['feedback', 'bug report', 'suggestions', 'contact', 'support'],
                'page_type': 'feedback',
                'last_modified': datetime.now(),
                'priority': '0.4',
                'changefreq': 'monthly'
            }
        ]

    def generate_sitemap(self, pages: List[Dict[str, Any]]) -> str:
        """Generate XML sitemap from discovered pages"""
        
        # Create root element
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        urlset.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        urlset.set('xsi:schemaLocation', 'http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd')
        
        # Add URLs
        for page in pages:
            url_elem = ET.SubElement(urlset, 'url')
            
            # Location (required)
            loc = ET.SubElement(url_elem, 'loc')
            loc.text = urljoin(self.base_url, page['url'])
            
            # Last modification date
            if 'last_modified' in page and page['last_modified']:
                lastmod = ET.SubElement(url_elem, 'lastmod')
                if isinstance(page['last_modified'], datetime):
                    lastmod.text = page['last_modified'].strftime('%Y-%m-%d')
                else:
                    lastmod.text = str(page['last_modified'])[:10]
            
            # Change frequency
            if 'changefreq' in page:
                changefreq = ET.SubElement(url_elem, 'changefreq')
                changefreq.text = page['changefreq']
            
            # Priority
            if 'priority' in page:
                priority = ET.SubElement(url_elem, 'priority')
                priority.text = str(page['priority'])
        
        # Pretty print XML
        rough_string = ET.tostring(urlset, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        
        return reparsed.toprettyxml(indent="  ", encoding='UTF-8').decode('utf-8')

    def generate_meta_tags(self, page: Dict[str, Any]) -> str:
        """Generate HTML meta tags for a specific page"""
        
        meta_tags = []
        
        # Basic meta tags
        meta_tags.append(f'<meta charset="utf-8">')
        meta_tags.append(f'<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        
        # Title and description
        if 'title' in page:
            meta_tags.append(f'<title>{self._escape_html(page["title"])}</title>')
            meta_tags.append(f'<meta name="title" content="{self._escape_html(page["title"])}">')
        
        if 'description' in page:
            meta_tags.append(f'<meta name="description" content="{self._escape_html(page["description"])}">')
        
        # Keywords
        if 'keywords' in page and page['keywords']:
            if isinstance(page['keywords'], list):
                keywords_str = ', '.join(page['keywords'])
            else:
                keywords_str = str(page['keywords'])
            meta_tags.append(f'<meta name="keywords" content="{self._escape_html(keywords_str)}">')
        
        # Author
        meta_tags.append(f'<meta name="author" content="{self.default_meta["author"]}">')
        
        # Canonical URL
        canonical_url = urljoin(self.base_url, page['url'])
        meta_tags.append(f'<link rel="canonical" href="{canonical_url}">')
        
        # Open Graph tags
        meta_tags.append(f'<meta property="og:type" content="{self.default_meta["og_type"]}">')
        meta_tags.append(f'<meta property="og:url" content="{canonical_url}">')
        meta_tags.append(f'<meta property="og:site_name" content="{self.default_meta["site_name"]}">')
        
        if 'title' in page:
            meta_tags.append(f'<meta property="og:title" content="{self._escape_html(page["title"])}">')
        
        if 'description' in page:
            meta_tags.append(f'<meta property="og:description" content="{self._escape_html(page["description"])}">')
        
        # Open Graph image
        og_image = page.get('og_image', self.default_meta['og_image'])
        meta_tags.append(f'<meta property="og:image" content="{og_image}">')
        meta_tags.append(f'<meta property="og:image:alt" content="SWGDB - Star Wars Galaxies Database">')
        
        # Twitter Card tags
        meta_tags.append(f'<meta name="twitter:card" content="{self.default_meta["twitter_card"]}">')
        meta_tags.append(f'<meta name="twitter:creator" content="{self.default_meta["twitter_creator"]}">')
        
        if 'title' in page:
            meta_tags.append(f'<meta name="twitter:title" content="{self._escape_html(page["title"])}">')
        
        if 'description' in page:
            meta_tags.append(f'<meta name="twitter:description" content="{self._escape_html(page["description"])}">')
        
        meta_tags.append(f'<meta name="twitter:image" content="{og_image}">')
        
        # Additional meta tags for specific page types
        if page.get('page_type') == 'heroic_guide':
            meta_tags.append('<meta name="robots" content="index, follow">')
            meta_tags.append('<meta name="googlebot" content="index, follow">')
        elif page.get('page_type') == 'api_documentation':
            meta_tags.append('<meta name="robots" content="index, follow, noarchive">')
        
        return '\n'.join(meta_tags)

    def generate_robots_txt(self) -> str:
        """Generate robots.txt content"""
        
        robots_content = [
            "User-agent: *",
            "Allow: /",
            "",
            "# Sitemap location",
            f"Sitemap: {self.base_url}/sitemap.xml",
            "",
            "# Crawl delay for polite crawling",
            "Crawl-delay: 1",
            "",
            "# Disallow private/admin areas",
            "Disallow: /admin",
            "Disallow: /api/private",
            "Disallow: *.json$",
            "Disallow: *.log$",
            "",
            "# Allow important API documentation",
            "Allow: /api/",
            "Allow: /api/docs",
            "",
            "# Google-specific optimizations",
            "User-agent: Googlebot",
            "Allow: /",
            "Crawl-delay: 0.5",
        ]
        
        return '\n'.join(robots_content)

    def _extract_html_title(self, content: str) -> Optional[str]:
        """Extract title from HTML content"""
        import re
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        
        # Try h1 tags
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
        if h1_match:
            return h1_match.group(1).strip()
        
        return None

    def _generate_title_from_filename(self, filename: str) -> str:
        """Generate title from filename"""
        # Convert filename to title case
        title = filename.replace('_', ' ').replace('-', ' ').title()
        return f"{title} - SWGDB"

    def _generate_url_from_template(self, template_path: Path) -> str:
        """Generate URL from template path"""
        # Remove dashboard/templates prefix and .html suffix
        relative_path = template_path.relative_to(Path("dashboard/templates"))
        url_path = '/' + str(relative_path.with_suffix(''))
        
        # Clean up common patterns
        url_path = url_path.replace('/index', '/')
        if url_path.endswith('/'):
            url_path = url_path.rstrip('/') or '/'
        
        return url_path

    def _determine_page_type(self, template_path: Path, content: str) -> str:
        """Determine page type from template and content"""
        filename = template_path.name.lower()
        
        if 'heroic' in filename:
            return 'heroic_guide'
        elif 'build' in filename:
            return 'character_build'
        elif 'quest' in filename:
            return 'quest_guide'
        elif 'player' in filename:
            return 'player_profile'
        elif 'api' in filename:
            return 'api_documentation'
        elif 'admin' in filename:
            return 'admin_interface'
        elif filename == 'index.html':
            return 'homepage'
        else:
            return 'general'

    def _generate_description(self, page_type: str, title: str, content: str) -> str:
        """Generate description based on page type"""
        descriptions = {
            'heroic_guide': f"Complete heroic instance guide with loot tables, strategies, and tips for Star Wars Galaxies players.",
            'character_build': f"Star Wars Galaxies character build guide with skills, equipment, and gameplay strategies.",
            'quest_guide': f"Detailed quest walkthrough for Star Wars Galaxies with steps, rewards, and completion tips.",
            'player_profile': f"Star Wars Galaxies player profile with character progression and achievements.",
            'api_documentation': f"SWGDB API documentation with endpoints, examples, and integration guides.",
            'homepage': "The ultimate Star Wars Galaxies database with heroic guides, character builds, loot tables, and community tools.",
            'general': f"Star Wars Galaxies resource and information on SWGDB community database."
        }
        
        return descriptions.get(page_type, descriptions['general'])

    def _generate_keywords(self, page_type: str, content: str) -> List[str]:
        """Generate keywords based on page type and content"""
        base_keywords = ['star wars galaxies', 'swg', 'swgdb']
        
        type_keywords = {
            'heroic_guide': ['heroic', 'instance', 'loot', 'guide', 'strategy'],
            'character_build': ['character', 'build', 'template', 'skills', 'profession'],
            'quest_guide': ['quest', 'mission', 'walkthrough', 'guide', 'npc'],
            'player_profile': ['player', 'character', 'profile', 'stats', 'progression'],
            'api_documentation': ['api', 'documentation', 'rest', 'json', 'endpoints'],
        }
        
        keywords = base_keywords + type_keywords.get(page_type, [])
        
        # Add content-specific keywords (basic extraction)
        content_lower = content.lower()
        if 'jedi' in content_lower:
            keywords.append('jedi')
        if 'bounty' in content_lower:
            keywords.append('bounty hunter')
        if 'pilot' in content_lower:
            keywords.append('pilot')
        
        return list(set(keywords))  # Remove duplicates

    def _get_priority(self, url: str) -> str:
        """Get priority for URL based on patterns"""
        for pattern, config in self.url_patterns.items():
            if url.startswith(pattern):
                return config['priority']
        return '0.5'  # Default priority

    def _get_changefreq(self, url: str) -> str:
        """Get change frequency for URL based on patterns"""
        for pattern, config in self.url_patterns.items():
            if url.startswith(pattern):
                return config['changefreq']
        return 'monthly'  # Default frequency

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))

    def generate_all(self) -> Dict[str, str]:
        """Generate all SEO files and return their content"""
        logger.info("Discovering content...")
        pages = self.discover_content()
        logger.info(f"Found {len(pages)} pages")
        
        logger.info("Generating sitemap...")
        sitemap_content = self.generate_sitemap(pages)
        
        logger.info("Generating robots.txt...")
        robots_content = self.generate_robots_txt()
        
        # Save files
        sitemap_path = self.output_dir / 'sitemap.xml'
        robots_path = self.output_dir / 'robots.txt'
        
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(robots_content)
        
        logger.info(f"Generated sitemap: {sitemap_path}")
        logger.info(f"Generated robots.txt: {robots_path}")
        
        # Generate meta tags for each page
        meta_tags = {}
        for page in pages:
            meta_tags[page['url']] = self.generate_meta_tags(page)
        
        return {
            'sitemap': sitemap_content,
            'robots': robots_content,
            'meta_tags': meta_tags,
            'pages': pages
        }

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate SEO metadata and sitemap for SWGDB')
    parser.add_argument('--base-url', default='https://swgdb.com', help='Base URL for the site')
    parser.add_argument('--output-dir', default='website', help='Output directory for generated files')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Generate SEO files
    seo_manager = SEOMetadataManager(base_url=args.base_url, output_dir=args.output_dir)
    results = seo_manager.generate_all()
    
    print(f"\n✅ SEO Generation Complete!")
    print(f"📊 Generated metadata for {len(results['pages'])} pages")
    print(f"🗺️ Sitemap: {len(results['pages'])} URLs")
    print(f"🤖 Robots.txt: Search engine optimized")
    print(f"📱 Meta tags: Generated for all pages")
    
    print(f"\n🌟 Next steps:")
    print(f"1. Upload sitemap.xml to your web server root")
    print(f"2. Submit sitemap to Google Search Console")
    print(f"3. Test with Google's Rich Results Test")
    print(f"4. Monitor Core Web Vitals and SEO performance")

if __name__ == '__main__':
    main()
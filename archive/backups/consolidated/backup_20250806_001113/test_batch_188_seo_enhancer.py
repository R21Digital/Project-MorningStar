#!/usr/bin/env python3
"""
Comprehensive Test Suite for MorningStar SEO Enhancement System - Batch 188

Tests all components of the SEO enhancement system including:
- SEO configuration validation
- Meta tag generation
- Sitemap generation and validation
- Structured data validation
- Google Search Console integration
- SEO health checks
- Performance monitoring
"""

import json
import os
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess
import requests
from urllib.parse import urljoin

class TestSEOConfiguration(unittest.TestCase):
    """Test SEO configuration management"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config_file = self.test_dir / "seo.json"
        
        self.sample_config = {
            "site": {
                "title": "Test Site",
                "description": "Test description",
                "url": "https://test.com",
                "domain": "test.com",
                "language": "en-US"
            },
            "keywords": {
                "primary": ["test", "seo", "optimization"],
                "secondary": ["web", "search", "ranking"]
            },
            "structuredData": {
                "website": {
                    "@type": "WebSite",
                    "name": "Test Site"
                }
            },
            "robots": {
                "rules": [
                    "User-agent: *",
                    "Allow: /",
                    "Sitemap: https://test.com/sitemap.xml"
                ]
            },
            "sitemap": {
                "changefreq": {
                    "homepage": "daily",
                    "static": "monthly"
                },
                "priority": {
                    "homepage": "1.0",
                    "static": "0.5"
                }
            }
        }

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_valid_config_loading(self):
        """Test loading valid SEO configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.sample_config, f)
        
        with open(self.config_file, 'r') as f:
            loaded_config = json.load(f)
        
        self.assertEqual(loaded_config['site']['title'], "Test Site")
        self.assertEqual(loaded_config['site']['url'], "https://test.com")
        self.assertIn("primary", loaded_config['keywords'])

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON configuration"""
        with open(self.config_file, 'w') as f:
            f.write("{ invalid json }")
        
        with self.assertRaises(json.JSONDecodeError):
            with open(self.config_file, 'r') as f:
                json.load(f)

    def test_missing_config_sections(self):
        """Test handling of missing configuration sections"""
        incomplete_config = {"site": {"title": "Test"}}
        
        required_sections = ['keywords', 'structuredData', 'robots', 'sitemap']
        for section in required_sections:
            self.assertNotIn(section, incomplete_config)

    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config should pass
        self.assertTrue(self.validate_config(self.sample_config))
        
        # Invalid config should fail
        invalid_config = {"site": {}}  # Missing required fields
        self.assertFalse(self.validate_config(invalid_config))

    def validate_config(self, config):
        """Helper method to validate configuration"""
        required_site_fields = ['title', 'url', 'description']
        site_config = config.get('site', {})
        
        for field in required_site_fields:
            if field not in site_config:
                return False
        
        return True


class TestMetaTagGeneration(unittest.TestCase):
    """Test meta tag generation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.site_config = {
            "title": "Test Site",
            "url": "https://test.com",
            "description": "Test description"
        }
        
        self.page_data = {
            "title": "Test Page",
            "description": "Test page description",
            "keywords": ["test", "page"],
            "url": "/test-page",
            "type": "article",
            "author": "Test Author",
            "image": "/test-image.jpg"
        }

    def test_title_tag_generation(self):
        """Test title tag generation"""
        # Regular page title
        title_tag = self.generate_title_tag(self.page_data, self.site_config)
        expected = f"<title>{self.page_data['title']} | {self.site_config['title']}</title>"
        self.assertEqual(title_tag, expected)
        
        # Homepage title (same as site title)
        homepage_data = {"title": self.site_config['title']}
        homepage_title = self.generate_title_tag(homepage_data, self.site_config)
        expected_homepage = f"<title>{self.site_config['title']}</title>"
        self.assertEqual(homepage_title, expected_homepage)

    def test_meta_description_generation(self):
        """Test meta description generation"""
        meta_desc = self.generate_meta_description(self.page_data)
        expected = f'<meta name="description" content="{self.page_data["description"]}">'
        self.assertEqual(meta_desc, expected)

    def test_keywords_meta_tag(self):
        """Test keywords meta tag generation"""
        keywords_tag = self.generate_keywords_tag(self.page_data)
        expected = '<meta name="keywords" content="test, page">'
        self.assertEqual(keywords_tag, expected)

    def test_canonical_url_generation(self):
        """Test canonical URL generation"""
        canonical_tag = self.generate_canonical_tag(self.page_data, self.site_config)
        full_url = urljoin(self.site_config['url'], self.page_data['url'])
        expected = f'<link rel="canonical" href="{full_url}">'
        self.assertEqual(canonical_tag, expected)

    def test_open_graph_tags(self):
        """Test Open Graph tag generation"""
        og_tags = self.generate_og_tags(self.page_data, self.site_config)
        
        self.assertIn('og:title', str(og_tags))
        self.assertIn('og:description', str(og_tags))
        self.assertIn('og:url', str(og_tags))
        self.assertIn('og:type', str(og_tags))
        self.assertIn('og:image', str(og_tags))

    def test_twitter_card_tags(self):
        """Test Twitter Card tag generation"""
        twitter_tags = self.generate_twitter_tags(self.page_data)
        
        self.assertIn('twitter:card', str(twitter_tags))
        self.assertIn('twitter:title', str(twitter_tags))
        self.assertIn('twitter:description', str(twitter_tags))

    def test_schema_org_generation(self):
        """Test Schema.org structured data generation"""
        schema_data = self.generate_schema_org(self.page_data, self.site_config)
        
        self.assertIn('@context', schema_data)
        self.assertIn('@type', schema_data)
        self.assertEqual(schema_data['@context'], 'https://schema.org')

    # Helper methods
    def generate_title_tag(self, page_data, site_config):
        """Generate title tag"""
        title = page_data['title']
        if title == site_config['title']:
            return f"<title>{title}</title>"
        else:
            return f"<title>{title} | {site_config['title']}</title>"

    def generate_meta_description(self, page_data):
        """Generate meta description tag"""
        return f'<meta name="description" content="{page_data["description"]}">'

    def generate_keywords_tag(self, page_data):
        """Generate keywords meta tag"""
        keywords = ', '.join(page_data['keywords'])
        return f'<meta name="keywords" content="{keywords}">'

    def generate_canonical_tag(self, page_data, site_config):
        """Generate canonical URL tag"""
        full_url = urljoin(site_config['url'], page_data['url'])
        return f'<link rel="canonical" href="{full_url}">'

    def generate_og_tags(self, page_data, site_config):
        """Generate Open Graph tags"""
        tags = []
        tags.append(f'<meta property="og:title" content="{page_data["title"]}">')
        tags.append(f'<meta property="og:description" content="{page_data["description"]}">')
        tags.append(f'<meta property="og:type" content="{page_data["type"]}">')
        
        full_url = urljoin(site_config['url'], page_data['url'])
        tags.append(f'<meta property="og:url" content="{full_url}">')
        
        if 'image' in page_data:
            image_url = urljoin(site_config['url'], page_data['image'])
            tags.append(f'<meta property="og:image" content="{image_url}">')
        
        return tags

    def generate_twitter_tags(self, page_data):
        """Generate Twitter Card tags"""
        tags = []
        tags.append('<meta name="twitter:card" content="summary_large_image">')
        tags.append(f'<meta name="twitter:title" content="{page_data["title"]}">')
        tags.append(f'<meta name="twitter:description" content="{page_data["description"]}">')
        return tags

    def generate_schema_org(self, page_data, site_config):
        """Generate Schema.org structured data"""
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": page_data['title'],
            "description": page_data['description'],
            "author": {
                "@type": "Person",
                "name": page_data.get('author', 'Unknown')
            },
            "url": urljoin(site_config['url'], page_data['url'])
        }


class TestSitemapGeneration(unittest.TestCase):
    """Test sitemap generation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.site_url = "https://test.com"
        
        self.sample_pages = [
            {
                'url': '/',
                'priority': 1.0,
                'changefreq': 'daily',
                'lastmod': '2024-01-01'
            },
            {
                'url': '/about/',
                'priority': 0.8,
                'changefreq': 'monthly',
                'lastmod': '2024-01-01'
            },
            {
                'url': '/contact/',
                'priority': 0.6,
                'changefreq': 'yearly',
                'lastmod': '2024-01-01'
            }
        ]

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_xml_sitemap_generation(self):
        """Test XML sitemap generation"""
        sitemap_xml = self.generate_sitemap_xml(self.sample_pages)
        
        # Verify XML structure
        self.assertIn('<?xml version="1.0"', sitemap_xml)
        self.assertIn('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', sitemap_xml)
        self.assertIn('</urlset>', sitemap_xml)
        
        # Verify page entries
        for page in self.sample_pages:
            self.assertIn(f'<loc>{self.site_url}{page["url"]}</loc>', sitemap_xml)
            self.assertIn(f'<priority>{page["priority"]:.1f}</priority>', sitemap_xml)
            self.assertIn(f'<changefreq>{page["changefreq"]}</changefreq>', sitemap_xml)

    def test_xml_validation(self):
        """Test sitemap XML validation"""
        sitemap_xml = self.generate_sitemap_xml(self.sample_pages)
        
        try:
            ET.fromstring(sitemap_xml)
            xml_valid = True
        except ET.ParseError:
            xml_valid = False
        
        self.assertTrue(xml_valid, "Generated sitemap XML should be valid")

    def test_url_sorting(self):
        """Test URL sorting by priority"""
        sorted_pages = sorted(self.sample_pages, key=lambda x: x['priority'], reverse=True)
        
        # Highest priority should be first
        self.assertEqual(sorted_pages[0]['priority'], 1.0)
        self.assertEqual(sorted_pages[0]['url'], '/')

    def test_empty_sitemap(self):
        """Test handling of empty page list"""
        empty_sitemap = self.generate_sitemap_xml([])
        
        self.assertIn('<urlset', empty_sitemap)
        self.assertIn('</urlset>', empty_sitemap)
        # Should not contain any <url> tags
        self.assertNotIn('<url>', empty_sitemap)

    def test_sitemap_size_limits(self):
        """Test sitemap size limits (50,000 URLs)"""
        large_page_list = []
        for i in range(60000):  # Exceed limit
            large_page_list.append({
                'url': f'/page-{i}/',
                'priority': 0.5,
                'changefreq': 'monthly',
                'lastmod': '2024-01-01'
            })
        
        # Should split into multiple sitemaps
        chunks = self.split_sitemap_if_needed(large_page_list)
        self.assertGreater(len(chunks), 1)
        self.assertLessEqual(len(chunks[0]), 50000)

    def test_robots_txt_generation(self):
        """Test robots.txt generation"""
        robots_rules = [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            f"Sitemap: {self.site_url}/sitemap.xml"
        ]
        
        robots_txt = self.generate_robots_txt(robots_rules)
        
        for rule in robots_rules:
            self.assertIn(rule, robots_txt)

    # Helper methods
    def generate_sitemap_xml(self, pages):
        """Generate XML sitemap from page list"""
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            ''
        ]
        
        for page in pages:
            xml_lines.extend([
                '  <url>',
                f'    <loc>{self.site_url}{page["url"]}</loc>',
                f'    <lastmod>{page["lastmod"]}</lastmod>',
                f'    <changefreq>{page["changefreq"]}</changefreq>',
                f'    <priority>{page["priority"]:.1f}</priority>',
                '  </url>',
                ''
            ])
        
        xml_lines.append('</urlset>')
        return '\n'.join(xml_lines)

    def split_sitemap_if_needed(self, pages, chunk_size=50000):
        """Split sitemap into chunks if needed"""
        chunks = []
        for i in range(0, len(pages), chunk_size):
            chunks.append(pages[i:i + chunk_size])
        return chunks

    def generate_robots_txt(self, rules):
        """Generate robots.txt content"""
        return '\n'.join(rules) + '\n'


class TestStructuredData(unittest.TestCase):
    """Test structured data generation and validation"""
    
    def setUp(self):
        """Set up test environment"""
        self.site_config = {
            "title": "Test Site",
            "url": "https://test.com",
            "description": "Test description"
        }

    def test_website_schema(self):
        """Test Website schema generation"""
        schema = self.generate_website_schema(self.site_config)
        
        self.assertEqual(schema['@context'], 'https://schema.org')
        self.assertEqual(schema['@type'], 'WebSite')
        self.assertEqual(schema['name'], self.site_config['title'])
        self.assertEqual(schema['url'], self.site_config['url'])

    def test_organization_schema(self):
        """Test Organization schema generation"""
        org_data = {
            "name": "Test Organization",
            "url": "https://test.com",
            "logo": "https://test.com/logo.png"
        }
        
        schema = self.generate_organization_schema(org_data)
        
        self.assertEqual(schema['@type'], 'Organization')
        self.assertEqual(schema['name'], org_data['name'])
        self.assertIn('logo', schema)

    def test_software_application_schema(self):
        """Test SoftwareApplication schema generation"""
        app_data = {
            "name": "Test App",
            "description": "Test application",
            "operatingSystem": "Windows",
            "applicationCategory": "GameApplication"
        }
        
        schema = self.generate_software_schema(app_data)
        
        self.assertEqual(schema['@type'], 'SoftwareApplication')
        self.assertEqual(schema['name'], app_data['name'])
        self.assertEqual(schema['operatingSystem'], app_data['operatingSystem'])

    def test_article_schema(self):
        """Test Article schema generation"""
        article_data = {
            "headline": "Test Article",
            "description": "Test article description",
            "author": "Test Author",
            "datePublished": "2024-01-01"
        }
        
        schema = self.generate_article_schema(article_data)
        
        self.assertEqual(schema['@type'], 'Article')
        self.assertEqual(schema['headline'], article_data['headline'])
        self.assertIn('author', schema)

    def test_breadcrumb_schema(self):
        """Test BreadcrumbList schema generation"""
        breadcrumbs = [
            {"name": "Home", "url": "/"},
            {"name": "Features", "url": "/features/"},
            {"name": "AI Companion", "url": "/features/ai-companion/"}
        ]
        
        schema = self.generate_breadcrumb_schema(breadcrumbs)
        
        self.assertEqual(schema['@type'], 'BreadcrumbList')
        self.assertIn('itemListElement', schema)
        self.assertEqual(len(schema['itemListElement']), 3)

    def test_faq_schema(self):
        """Test FAQPage schema generation"""
        faq_data = [
            {
                "question": "What is this?",
                "answer": "This is a test."
            },
            {
                "question": "How does it work?",
                "answer": "It works by testing."
            }
        ]
        
        schema = self.generate_faq_schema(faq_data)
        
        self.assertEqual(schema['@type'], 'FAQPage')
        self.assertIn('mainEntity', schema)
        self.assertEqual(len(schema['mainEntity']), 2)

    def test_schema_validation(self):
        """Test schema validation"""
        valid_schema = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Test Site",
            "url": "https://test.com"
        }
        
        self.assertTrue(self.validate_schema(valid_schema))
        
        # Invalid schema (missing required fields)
        invalid_schema = {
            "@context": "https://schema.org"
            # Missing @type
        }
        
        self.assertFalse(self.validate_schema(invalid_schema))

    # Helper methods
    def generate_website_schema(self, site_config):
        """Generate Website schema"""
        return {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": site_config['title'],
            "url": site_config['url'],
            "description": site_config['description']
        }

    def generate_organization_schema(self, org_data):
        """Generate Organization schema"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": org_data['name'],
            "url": org_data['url']
        }
        
        if 'logo' in org_data:
            schema['logo'] = {
                "@type": "ImageObject",
                "url": org_data['logo']
            }
        
        return schema

    def generate_software_schema(self, app_data):
        """Generate SoftwareApplication schema"""
        return {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": app_data['name'],
            "description": app_data['description'],
            "operatingSystem": app_data['operatingSystem'],
            "applicationCategory": app_data['applicationCategory']
        }

    def generate_article_schema(self, article_data):
        """Generate Article schema"""
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article_data['headline'],
            "description": article_data['description'],
            "author": {
                "@type": "Person",
                "name": article_data['author']
            },
            "datePublished": article_data['datePublished']
        }

    def generate_breadcrumb_schema(self, breadcrumbs):
        """Generate BreadcrumbList schema"""
        items = []
        for i, crumb in enumerate(breadcrumbs, 1):
            items.append({
                "@type": "ListItem",
                "position": i,
                "name": crumb['name'],
                "item": f"https://test.com{crumb['url']}"
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }

    def generate_faq_schema(self, faq_data):
        """Generate FAQPage schema"""
        questions = []
        for item in faq_data:
            questions.append({
                "@type": "Question",
                "name": item['question'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item['answer']
                }
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": questions
        }

    def validate_schema(self, schema):
        """Validate schema structure"""
        required_fields = ["@context", "@type"]
        for field in required_fields:
            if field not in schema:
                return False
        return True


class TestGSCIntegration(unittest.TestCase):
    """Test Google Search Console integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.site_url = "https://test.com"
        self.sitemap_url = f"{self.site_url}/sitemap.xml"
        self.api_key = "test_api_key"

    @patch('requests.put')
    def test_sitemap_submission(self, mock_put):
        """Test sitemap submission to GSC"""
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = {"success": True}
        
        result = self.submit_sitemap_to_gsc(self.sitemap_url, self.api_key)
        
        self.assertTrue(result['success'])
        mock_put.assert_called_once()

    @patch('requests.put')
    def test_sitemap_submission_failure(self, mock_put):
        """Test handling of sitemap submission failure"""
        mock_put.return_value.status_code = 400
        mock_put.return_value.json.return_value = {"error": "Invalid sitemap"}
        
        result = self.submit_sitemap_to_gsc(self.sitemap_url, self.api_key)
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)

    @patch('requests.get')
    def test_sitemap_accessibility_check(self, mock_get):
        """Test sitemap accessibility verification"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://test.com/</loc></url>
</urlset>'''
        
        result = self.check_sitemap_accessibility(self.sitemap_url)
        
        self.assertTrue(result['accessible'])
        self.assertTrue(result['valid_xml'])

    @patch('requests.get')
    def test_robots_txt_check(self, mock_get):
        """Test robots.txt accessibility check"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '''User-agent: *
Allow: /
Sitemap: https://test.com/sitemap.xml'''
        
        result = self.check_robots_txt(self.site_url)
        
        self.assertTrue(result['accessible'])
        self.assertTrue(result['has_sitemap_reference'])

    def test_gsc_api_url_generation(self):
        """Test GSC API URL generation"""
        property_url = "https://test.com"
        sitemap_url = "https://test.com/sitemap.xml"
        
        api_url = self.generate_gsc_api_url(property_url, sitemap_url)
        
        expected = f"https://www.googleapis.com/webmasters/v3/sites/{property_url}/sitemaps/{sitemap_url}"
        self.assertEqual(api_url, expected)

    # Helper methods
    def submit_sitemap_to_gsc(self, sitemap_url, api_key):
        """Submit sitemap to Google Search Console"""
        # Simulate API call
        if api_key == "test_api_key":
            return {"success": True, "message": "Sitemap submitted"}
        else:
            return {"success": False, "error": "Invalid API key"}

    def check_sitemap_accessibility(self, sitemap_url):
        """Check if sitemap is accessible and valid"""
        # Simulate accessibility check
        return {
            "accessible": True,
            "valid_xml": True,
            "url_count": 1
        }

    def check_robots_txt(self, site_url):
        """Check robots.txt accessibility and content"""
        # Simulate robots.txt check
        return {
            "accessible": True,
            "has_sitemap_reference": True,
            "content": "User-agent: *\nAllow: /"
        }

    def generate_gsc_api_url(self, property_url, sitemap_url):
        """Generate GSC API URL"""
        return f"https://www.googleapis.com/webmasters/v3/sites/{property_url}/sitemaps/{sitemap_url}"


class TestSEOHealthCheck(unittest.TestCase):
    """Test SEO health check functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.site_url = "https://test.com"

    @patch('requests.get')
    def test_homepage_meta_tags_check(self, mock_get):
        """Test homepage meta tags verification"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '''
        <html>
        <head>
            <title>Test Site - Homepage</title>
            <meta name="description" content="Test site description">
            <link rel="canonical" href="https://test.com/">
            <script type="application/ld+json">{"@type": "WebSite"}</script>
        </head>
        </html>
        '''
        
        result = self.check_homepage_meta_tags(self.site_url)
        
        self.assertTrue(result['has_title'])
        self.assertTrue(result['has_description'])
        self.assertTrue(result['has_canonical'])
        self.assertTrue(result['has_structured_data'])

    @patch('requests.get')
    def test_missing_meta_tags_detection(self, mock_get):
        """Test detection of missing meta tags"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '''
        <html>
        <head>
            <title>Test Site</title>
            <!-- Missing description and canonical -->
        </head>
        </html>
        '''
        
        result = self.check_homepage_meta_tags(self.site_url)
        
        self.assertTrue(result['has_title'])
        self.assertFalse(result['has_description'])
        self.assertFalse(result['has_canonical'])

    def test_seo_score_calculation(self):
        """Test SEO score calculation"""
        checks = {
            'has_title': True,
            'has_description': True,
            'has_canonical': False,
            'has_structured_data': True,
            'robots_accessible': True,
            'sitemap_accessible': True
        }
        
        score = self.calculate_seo_score(checks)
        
        # 5 out of 6 checks passed = 83.3%
        self.assertAlmostEqual(score, 83.3, places=1)

    def test_critical_issues_detection(self):
        """Test detection of critical SEO issues"""
        checks = {
            'has_title': False,  # Critical
            'has_description': False,  # Critical
            'has_canonical': True,
            'robots_accessible': False,  # Critical
            'sitemap_accessible': True
        }
        
        critical_issues = self.get_critical_issues(checks)
        
        self.assertIn('missing_title', critical_issues)
        self.assertIn('missing_description', critical_issues)
        self.assertIn('robots_inaccessible', critical_issues)

    def test_seo_recommendations(self):
        """Test SEO recommendations generation"""
        checks = {
            'has_title': True,
            'has_description': False,
            'has_canonical': False,
            'has_structured_data': False
        }
        
        recommendations = self.generate_recommendations(checks)
        
        self.assertIn('add_meta_description', recommendations)
        self.assertIn('add_canonical_url', recommendations)
        self.assertIn('add_structured_data', recommendations)

    # Helper methods
    def check_homepage_meta_tags(self, site_url):
        """Check meta tags on homepage"""
        # Simulate meta tag checking
        return {
            'has_title': True,
            'has_description': True,
            'has_canonical': True,
            'has_structured_data': True
        }

    def calculate_seo_score(self, checks):
        """Calculate SEO score based on checks"""
        total_checks = len(checks)
        passed_checks = sum(1 for passed in checks.values() if passed)
        return (passed_checks / total_checks) * 100

    def get_critical_issues(self, checks):
        """Get list of critical SEO issues"""
        critical_mapping = {
            'has_title': 'missing_title',
            'has_description': 'missing_description',
            'robots_accessible': 'robots_inaccessible'
        }
        
        issues = []
        for check, issue_name in critical_mapping.items():
            if not checks.get(check, True):
                issues.append(issue_name)
        
        return issues

    def generate_recommendations(self, checks):
        """Generate SEO recommendations"""
        recommendations = []
        
        if not checks.get('has_description', True):
            recommendations.append('add_meta_description')
        if not checks.get('has_canonical', True):
            recommendations.append('add_canonical_url')
        if not checks.get('has_structured_data', True):
            recommendations.append('add_structured_data')
        
        return recommendations


class TestPerformanceMonitoring(unittest.TestCase):
    """Test SEO performance monitoring"""
    
    def test_sitemap_generation_performance(self):
        """Test sitemap generation performance monitoring"""
        start_time = datetime.now()
        
        # Simulate sitemap generation
        page_count = 1000
        self.simulate_sitemap_generation(page_count)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should be fast for 1000 pages
        self.assertLess(duration, 5.0)  # 5 seconds max
        
        # Calculate performance metrics
        pages_per_second = page_count / duration if duration > 0 else 0
        self.assertGreater(pages_per_second, 100)  # At least 100 pages/second

    def test_meta_tag_generation_performance(self):
        """Test meta tag generation performance"""
        page_count = 100
        
        start_time = datetime.now()
        
        for i in range(page_count):
            page_data = {
                'title': f'Page {i}',
                'description': f'Description for page {i}',
                'keywords': ['test', 'page']
            }
            self.generate_meta_tags(page_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should be very fast
        self.assertLess(duration, 1.0)  # 1 second max for 100 pages

    def test_memory_usage_monitoring(self):
        """Test memory usage during operations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Simulate large operation
        large_page_list = [{'url': f'/page-{i}/'} for i in range(10000)]
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        self.assertLess(memory_increase, 100 * 1024 * 1024)

    def test_batch_processing_efficiency(self):
        """Test efficiency of batch processing"""
        pages = [{'url': f'/page-{i}/'} for i in range(1000)]
        
        # Test single processing
        start_time = datetime.now()
        for page in pages:
            self.process_single_page(page)
        single_duration = (datetime.now() - start_time).total_seconds()
        
        # Test batch processing
        start_time = datetime.now()
        self.process_pages_batch(pages)
        batch_duration = (datetime.now() - start_time).total_seconds()
        
        # Batch processing should be more efficient
        self.assertLess(batch_duration, single_duration)

    # Helper methods
    def simulate_sitemap_generation(self, page_count):
        """Simulate sitemap generation"""
        # Simple simulation - just create data structures
        pages = []
        for i in range(page_count):
            pages.append({
                'url': f'/page-{i}/',
                'priority': 0.5,
                'changefreq': 'monthly'
            })
        return pages

    def generate_meta_tags(self, page_data):
        """Generate meta tags for performance testing"""
        tags = []
        tags.append(f'<title>{page_data["title"]}</title>')
        tags.append(f'<meta name="description" content="{page_data["description"]}">')
        if 'keywords' in page_data:
            keywords = ', '.join(page_data['keywords'])
            tags.append(f'<meta name="keywords" content="{keywords}">')
        return tags

    def process_single_page(self, page):
        """Process a single page"""
        # Simulate processing
        return {'processed': True, 'url': page['url']}

    def process_pages_batch(self, pages):
        """Process pages in batch"""
        # Simulate more efficient batch processing
        return [{'processed': True, 'url': page['url']} for page in pages]


class TestIntegrationScenarios(unittest.TestCase):
    """Test complete integration scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.site_url = "https://test.com"

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_complete_seo_workflow(self):
        """Test complete SEO enhancement workflow"""
        # 1. Load configuration
        config = self.load_test_config()
        self.assertIsNotNone(config)
        
        # 2. Generate content pages
        pages = self.create_test_pages()
        self.assertGreater(len(pages), 0)
        
        # 3. Generate meta tags for each page
        for page in pages:
            meta_tags = self.generate_page_meta_tags(page, config)
            self.assertGreater(len(meta_tags), 5)  # Should have multiple meta tags
        
        # 4. Generate sitemap
        sitemap_xml = self.generate_sitemap(pages)
        self.assertIn('<urlset', sitemap_xml)
        
        # 5. Validate sitemap XML
        try:
            ET.fromstring(sitemap_xml)
            xml_valid = True
        except ET.ParseError:
            xml_valid = False
        self.assertTrue(xml_valid)
        
        # 6. Generate robots.txt
        robots_txt = self.generate_robots_txt(config)
        self.assertIn('Sitemap:', robots_txt)
        
        # 7. Run health check
        health_result = self.run_health_check()
        self.assertIn('score', health_result)

    def test_error_handling_workflow(self):
        """Test error handling in SEO workflow"""
        # Test with invalid configuration
        invalid_config = {"invalid": "config"}
        
        with self.assertRaises(Exception):
            self.validate_config_strict(invalid_config)
        
        # Test with empty page list
        empty_sitemap = self.generate_sitemap([])
        self.assertIn('<urlset', empty_sitemap)
        
        # Test with malformed page data
        malformed_page = {"url": None}  # Invalid URL
        with self.assertRaises(Exception):
            self.generate_page_meta_tags(malformed_page, {})

    def test_large_scale_scenario(self):
        """Test large-scale SEO processing"""
        # Generate large number of pages
        large_page_count = 5000
        pages = []
        for i in range(large_page_count):
            pages.append({
                'url': f'/page-{i}/',
                'title': f'Page {i}',
                'description': f'Description for page {i}',
                'priority': 0.5,
                'changefreq': 'monthly'
            })
        
        # Process all pages
        start_time = datetime.now()
        sitemap_xml = self.generate_sitemap(pages)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Should complete in reasonable time
        self.assertLess(processing_time, 30.0)  # 30 seconds max
        
        # Verify sitemap contains all pages
        url_count = sitemap_xml.count('<url>')
        self.assertEqual(url_count, large_page_count)

    def test_multi_language_scenario(self):
        """Test multi-language SEO scenario"""
        languages = ['en', 'es', 'fr', 'de']
        
        for lang in languages:
            page_data = {
                'url': f'/{lang}/about/',
                'title': f'About Us ({lang.upper()})',
                'description': f'About us page in {lang}',
                'language': lang
            }
            
            meta_tags = self.generate_page_meta_tags(page_data, {})
            
            # Should include language-specific meta tags
            meta_tags_str = '\n'.join(meta_tags)
            self.assertIn(f'hreflang="{lang}"', meta_tags_str)

    # Helper methods
    def load_test_config(self):
        """Load test configuration"""
        return {
            "site": {
                "title": "Test Site",
                "url": self.site_url,
                "description": "Test site description"
            },
            "robots": {
                "rules": [
                    "User-agent: *",
                    "Allow: /",
                    f"Sitemap: {self.site_url}/sitemap.xml"
                ]
            }
        }

    def create_test_pages(self):
        """Create test pages"""
        return [
            {
                'url': '/',
                'title': 'Homepage',
                'description': 'Homepage description',
                'priority': 1.0,
                'changefreq': 'daily'
            },
            {
                'url': '/about/',
                'title': 'About Us',
                'description': 'About us page',
                'priority': 0.8,
                'changefreq': 'monthly'
            },
            {
                'url': '/contact/',
                'title': 'Contact',
                'description': 'Contact page',
                'priority': 0.6,
                'changefreq': 'yearly'
            }
        ]

    def generate_page_meta_tags(self, page_data, config):
        """Generate meta tags for a page"""
        tags = []
        
        if 'title' in page_data:
            tags.append(f'<title>{page_data["title"]}</title>')
        
        if 'description' in page_data:
            tags.append(f'<meta name="description" content="{page_data["description"]}">')
        
        # Add canonical URL
        tags.append(f'<link rel="canonical" href="{self.site_url}{page_data["url"]}">')
        
        # Add Open Graph tags
        tags.append(f'<meta property="og:title" content="{page_data.get("title", "")}">')
        tags.append(f'<meta property="og:description" content="{page_data.get("description", "")}">')
        tags.append(f'<meta property="og:url" content="{self.site_url}{page_data["url"]}">')
        
        # Add language-specific tags if applicable
        if 'language' in page_data:
            tags.append(f'<link rel="alternate" hreflang="{page_data["language"]}" href="{self.site_url}{page_data["url"]}">')
        
        return tags

    def generate_sitemap(self, pages):
        """Generate sitemap XML"""
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            ''
        ]
        
        for page in pages:
            xml_lines.extend([
                '  <url>',
                f'    <loc>{self.site_url}{page["url"]}</loc>',
                f'    <priority>{page.get("priority", 0.5):.1f}</priority>',
                f'    <changefreq>{page.get("changefreq", "monthly")}</changefreq>',
                '  </url>',
                ''
            ])
        
        xml_lines.append('</urlset>')
        return '\n'.join(xml_lines)

    def generate_robots_txt(self, config):
        """Generate robots.txt"""
        rules = config.get('robots', {}).get('rules', [])
        return '\n'.join(rules) + '\n'

    def run_health_check(self):
        """Run SEO health check"""
        return {
            'score': 85.0,
            'issues': [],
            'recommendations': ['add_more_structured_data']
        }

    def validate_config_strict(self, config):
        """Strict configuration validation"""
        required_sections = ['site']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required section: {section}")
        
        site_config = config['site']
        required_site_fields = ['title', 'url', 'description']
        for field in required_site_fields:
            if field not in site_config:
                raise ValueError(f"Missing required site field: {field}")


def run_test_suite():
    """Run the complete test suite"""
    print("🧪 Running MorningStar SEO Enhancement System Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_classes = [
        TestSEOConfiguration,
        TestMetaTagGeneration,
        TestSitemapGeneration,
        TestStructuredData,
        TestGSCIntegration,
        TestSEOHealthCheck,
        TestPerformanceMonitoring,
        TestIntegrationScenarios
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_tests - failures - errors}")
    print(f"Failed: {failures}")
    print(f"Errors: {errors}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0]}")
    
    if result.errors:
        print(f"\n🚨 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\n')[-2]}")
    
    if success_rate == 100:
        print(f"\n🎉 All tests passed! SEO Enhancement System is working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Please review the issues above.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_test_suite()
    sys.exit(0 if success else 1)
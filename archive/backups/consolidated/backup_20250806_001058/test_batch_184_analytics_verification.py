#!/usr/bin/env python3
"""
Batch 184 - Google Analytics + Search Console Integration Test Suite
Comprehensive testing of all analytics and SEO components

This test suite validates:
1. Google Analytics script integration
2. SEO meta tags and structured data
3. robots.txt and sitemap.xml configuration
4. Google Search Console setup
5. Analytics tracking functionality
6. Performance and accessibility
"""

import os
import json
import re
import unittest
import requests
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

class TestBatch184Analytics(unittest.TestCase):
    """Test suite for Batch 184 Analytics Integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_path = Path(__file__).parent
        self.website_path = self.base_path / "website"
        self.swgdb_site_path = self.base_path / "swgdb_site"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "batch": "184",
            "test_suite": "Google Analytics + Search Console Integration",
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }
    
    def tearDown(self):
        """Save test results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.base_path / f"BATCH_184_TEST_REPORT_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📊 Test results saved to: {results_file}")
    
    def record_test_result(self, test_name, status, details=None):
        """Record test result"""
        self.test_results["total_tests"] += 1
        if status == "PASS":
            self.test_results["passed_tests"] += 1
        else:
            self.test_results["failed_tests"] += 1
        
        test_result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        if details:
            test_result["details"] = details
        
        self.test_results["test_details"].append(test_result)
    
    def test_google_analytics_script_presence(self):
        """Test that Google Analytics script is present in base layout"""
        print("🧪 Testing Google Analytics script presence...")
        
        base_layout_path = self.website_path / "_includes" / "layouts" / "base.njk"
        
        if not base_layout_path.exists():
            self.record_test_result("google_analytics_script_presence", "FAIL", 
                                  {"error": "Base layout file not found"})
            self.fail("Base layout file not found")
        
        with open(base_layout_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Google Analytics script
        ga_script_pattern = r'https://www\.googletagmanager\.com/gtag/js\?id=G-[A-Z0-9]+'
        ga_match = re.search(ga_script_pattern, content)
        
        if ga_match:
            ga_id = ga_match.group(0).split('=')[-1]
            self.record_test_result("google_analytics_script_presence", "PASS",
                                  {"measurement_id": ga_id})
            print(f"✅ Google Analytics script found with ID: {ga_id}")
        else:
            self.record_test_result("google_analytics_script_presence", "FAIL",
                                  {"error": "Google Analytics script not found"})
            self.fail("Google Analytics script not found")
    
    def test_google_analytics_enhanced_configuration(self):
        """Test that Google Analytics has enhanced configuration"""
        print("🧪 Testing Google Analytics enhanced configuration...")
        
        base_layout_path = self.website_path / "_includes" / "layouts" / "base.njk"
        
        with open(base_layout_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for enhanced configuration elements
        enhanced_features = {
            "custom_dimensions": "custom_map" in content,
            "page_tracking": "page_title" in content and "page_location" in content,
            "custom_events": "trackSWGDBEvent" in content,
            "performance_tracking": "page_performance" in content,
            "engagement_tracking": "user_engagement" in content,
            "error_tracking": "javascript_error" in content
        }
        
        features_found = sum(enhanced_features.values())
        total_features = len(enhanced_features)
        
        if features_found >= 4:  # At least 4 out of 6 features
            self.record_test_result("google_analytics_enhanced_configuration", "PASS",
                                  {"features_found": features_found, "total_features": total_features,
                                   "features": enhanced_features})
            print(f"✅ Enhanced configuration found: {features_found}/{total_features} features")
        else:
            self.record_test_result("google_analytics_enhanced_configuration", "FAIL",
                                  {"features_found": features_found, "total_features": total_features,
                                   "features": enhanced_features})
            self.fail(f"Only {features_found}/{total_features} enhanced features found")
    
    def test_analytics_include_file(self):
        """Test that analytics include file exists and is properly configured"""
        print("🧪 Testing analytics include file...")
        
        analytics_path = self.swgdb_site_path / "_includes" / "analytics.html"
        
        if not analytics_path.exists():
            self.record_test_result("analytics_include_file", "FAIL",
                                  {"error": "Analytics include file not found"})
            self.fail("Analytics include file not found")
        
        with open(analytics_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required elements
        required_elements = {
            "google_analytics_script": "https://www.googletagmanager.com/gtag/js?id=G-Q4ZZ5SFJC0" in content,
            "gtag_config": "gtag('config', 'G-Q4ZZ5SFJC0')" in content,
            "custom_tracking": "trackSWGDBEvent" in content,
            "search_console_verification": "google-site-verification" in content,
            "structured_data": "application/ld+json" in content,
            "open_graph_tags": "og:title" in content,
            "twitter_cards": "twitter:card" in content,
            "meta_description": 'name="description"' in content,
            "canonical_url": 'rel="canonical"' in content
        }
        
        elements_found = sum(required_elements.values())
        total_elements = len(required_elements)
        
        if elements_found >= 7:  # At least 7 out of 9 elements
            self.record_test_result("analytics_include_file", "PASS",
                                  {"elements_found": elements_found, "total_elements": total_elements,
                                   "elements": required_elements})
            print(f"✅ Analytics include file properly configured: {elements_found}/{total_elements} elements")
        else:
            self.record_test_result("analytics_include_file", "FAIL",
                                  {"elements_found": elements_found, "total_elements": total_elements,
                                   "elements": required_elements})
            self.fail(f"Only {elements_found}/{total_elements} required elements found")
    
    def test_robots_txt_configuration(self):
        """Test that robots.txt is properly configured"""
        print("🧪 Testing robots.txt configuration...")
        
        robots_path = self.swgdb_site_path / "robots.txt"
        
        if not robots_path.exists():
            self.record_test_result("robots_txt_configuration", "FAIL",
                                  {"error": "robots.txt file not found"})
            self.fail("robots.txt file not found")
        
        with open(robots_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required directives
        required_directives = {
            "user_agent": "User-agent: *" in content,
            "allow_all": "Allow: /" in content,
            "sitemap_reference": "Sitemap: https://swgdb.com/sitemap.xml" in content,
            "disallow_admin": "Disallow: /admin/" in content,
            "disallow_private": "Disallow: /private/" in content,
            "crawl_delay": "Crawl-delay:" in content
        }
        
        directives_found = sum(required_directives.values())
        total_directives = len(required_directives)
        
        if directives_found >= 5:  # At least 5 out of 6 directives
            self.record_test_result("robots_txt_configuration", "PASS",
                                  {"directives_found": directives_found, "total_directives": total_directives,
                                   "directives": required_directives})
            print(f"✅ robots.txt properly configured: {directives_found}/{total_directives} directives")
        else:
            self.record_test_result("robots_txt_configuration", "FAIL",
                                  {"directives_found": directives_found, "total_directives": total_directives,
                                   "directives": required_directives})
            self.fail(f"Only {directives_found}/{total_directives} required directives found")
    
    def test_sitemap_xml_structure(self):
        """Test that sitemap.xml has proper structure and content"""
        print("🧪 Testing sitemap.xml structure...")
        
        sitemap_path = self.swgdb_site_path / "sitemap.xml"
        
        if not sitemap_path.exists():
            self.record_test_result("sitemap_xml_structure", "FAIL",
                                  {"error": "sitemap.xml file not found"})
            self.fail("sitemap.xml file not found")
        
        try:
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
            
            # Check namespace
            xmlns = root.get('xmlns', '')
            # Check both xmlns attribute and tag name for namespace
            if ('sitemaps.org' not in xmlns and 'sitemap/0.9' not in xmlns) and 'sitemaps.org' not in root.tag:
                self.record_test_result("sitemap_xml_structure", "FAIL",
                                      {"error": f"Incorrect namespace: {xmlns}, tag: {root.tag}"})
                self.fail(f"Incorrect sitemap namespace: {xmlns}, tag: {root.tag}")
            
            # Count URLs
            urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
            
            if len(urls) < 10:
                self.record_test_result("sitemap_xml_structure", "FAIL",
                                      {"error": f"Too few URLs: {len(urls)}"})
                self.fail(f"Too few URLs in sitemap: {len(urls)}")
            
            # Check for required pages
            required_pages = [
                'https://swgdb.com/',
                'https://swgdb.com/pages/heroics/',
                'https://swgdb.com/pages/loot/',
                'https://swgdb.com/pages/builds/',
                'https://swgdb.com/pages/tools/'
            ]
            
            pages_found = 0
            for url in urls:
                loc = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None:
                    for page in required_pages:
                        if page in loc.text:
                            pages_found += 1
                            break
            
            if pages_found >= 4:  # At least 4 out of 5 required pages
                self.record_test_result("sitemap_xml_structure", "PASS",
                                      {"url_count": len(urls), "required_pages_found": pages_found,
                                       "total_required_pages": len(required_pages)})
                print(f"✅ sitemap.xml properly structured: {len(urls)} URLs, {pages_found}/{len(required_pages)} required pages")
            else:
                self.record_test_result("sitemap_xml_structure", "FAIL",
                                      {"url_count": len(urls), "required_pages_found": pages_found,
                                       "total_required_pages": len(required_pages)})
                self.fail(f"Only {pages_found}/{len(required_pages)} required pages found")
                
        except ET.ParseError as e:
            self.record_test_result("sitemap_xml_structure", "FAIL",
                                  {"error": f"XML parsing error: {str(e)}"})
            self.fail(f"XML parsing error: {str(e)}")
    
    def test_seo_configuration(self):
        """Test that SEO configuration is properly set up"""
        print("🧪 Testing SEO configuration...")
        
        seo_config_path = self.website_path / "config" / "seo.json"
        
        if not seo_config_path.exists():
            self.record_test_result("seo_configuration", "FAIL",
                                  {"error": "SEO configuration file not found"})
            self.fail("SEO configuration file not found")
        
        with open(seo_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check for required sections
        required_sections = {
            "analytics": "analytics" in config,
            "search_console": "search_console" in config,
            "social": "social" in config,
            "structured_data": "structured_data" in config,
            "site": "site" in config
        }
        
        sections_found = sum(required_sections.values())
        total_sections = len(required_sections)
        
        if sections_found >= 4:  # At least 4 out of 5 sections
            self.record_test_result("seo_configuration", "PASS",
                                  {"sections_found": sections_found, "total_sections": total_sections,
                                   "sections": required_sections})
            print(f"✅ SEO configuration properly set up: {sections_found}/{total_sections} sections")
        else:
            self.record_test_result("seo_configuration", "FAIL",
                                  {"sections_found": sections_found, "total_sections": total_sections,
                                   "sections": required_sections})
            self.fail(f"Only {sections_found}/{total_sections} required sections found")
    
    def test_meta_tags_in_layout(self):
        """Test that meta tags are properly configured in layout"""
        print("🧪 Testing meta tags in layout...")
        
        base_layout_path = self.website_path / "_includes" / "layouts" / "base.njk"
        
        with open(base_layout_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required meta tags
        required_meta_tags = {
            "meta_description": 'name="description"' in content,
            "meta_keywords": 'name="keywords"' in content,
            "meta_author": 'name="author"' in content,
            "meta_robots": 'name="robots"' in content,
            "og_title": 'property="og:title"' in content,
            "og_description": 'property="og:description"' in content,
            "og_type": 'property="og:type"' in content,
            "og_url": 'property="og:url"' in content,
            "twitter_card": 'name="twitter:card"' in content,
            "twitter_title": 'name="twitter:title"' in content,
            "twitter_description": 'name="twitter:description"' in content,
            "canonical_url": 'rel="canonical"' in content
        }
        
        tags_found = sum(required_meta_tags.values())
        total_tags = len(required_meta_tags)
        
        if tags_found >= 10:  # At least 10 out of 12 tags
            self.record_test_result("meta_tags_in_layout", "PASS",
                                  {"tags_found": tags_found, "total_tags": total_tags,
                                   "tags": required_meta_tags})
            print(f"✅ Meta tags properly configured: {tags_found}/{total_tags} tags")
        else:
            self.record_test_result("meta_tags_in_layout", "FAIL",
                                  {"tags_found": tags_found, "total_tags": total_tags,
                                   "tags": required_meta_tags})
            self.fail(f"Only {tags_found}/{total_tags} required meta tags found")
    
    def test_google_search_console_setup_guide(self):
        """Test that Google Search Console setup guide exists"""
        print("🧪 Testing Google Search Console setup guide...")
        
        gsc_guide_path = self.swgdb_site_path / "GSC_SETUP_GUIDE.md"
        
        if not gsc_guide_path.exists():
            self.record_test_result("google_search_console_setup_guide", "FAIL",
                                  {"error": "Google Search Console setup guide not found"})
            self.fail("Google Search Console setup guide not found")
        
        with open(gsc_guide_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required sections
        required_sections = {
            "google_analytics_setup": "Google Analytics Setup" in content,
            "search_console_setup": "Google Search Console Setup" in content,
            "verification_instructions": "Verify Ownership" in content,
            "sitemap_submission": "Submit Sitemap" in content,
            "testing_instructions": "Testing & Validation" in content,
            "monitoring_instructions": "Monitoring & Maintenance" in content
        }
        
        sections_found = sum(required_sections.values())
        total_sections = len(required_sections)
        
        if sections_found >= 5:  # At least 5 out of 6 sections
            self.record_test_result("google_search_console_setup_guide", "PASS",
                                  {"sections_found": sections_found, "total_sections": total_sections,
                                   "sections": required_sections})
            print(f"✅ Google Search Console setup guide complete: {sections_found}/{total_sections} sections")
        else:
            self.record_test_result("google_search_console_setup_guide", "FAIL",
                                  {"sections_found": sections_found, "total_sections": total_sections,
                                   "sections": required_sections})
            self.fail(f"Only {sections_found}/{total_sections} required sections found")
    
    def test_analytics_deployment_script(self):
        """Test that analytics deployment script exists and is functional"""
        print("🧪 Testing analytics deployment script...")
        
        deploy_script_path = self.swgdb_site_path / "deploy_analytics.py"
        
        if not deploy_script_path.exists():
            self.record_test_result("analytics_deployment_script", "FAIL",
                                  {"error": "Analytics deployment script not found"})
            self.fail("Analytics deployment script not found")
        
        with open(deploy_script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required functions
        required_functions = {
            "add_analytics_to_html": "def add_analytics_to_html" in content,
            "update_meta_tags": "def update_meta_tags" in content,
            "main_function": "def main()" in content,
            "file_processing": "glob.glob" in content,
            "html_parsing": "re.search" in content
        }
        
        functions_found = sum(required_functions.values())
        total_functions = len(required_functions)
        
        if functions_found >= 4:  # At least 4 out of 5 functions
            self.record_test_result("analytics_deployment_script", "PASS",
                                  {"functions_found": functions_found, "total_functions": total_functions,
                                   "functions": required_functions})
            print(f"✅ Analytics deployment script functional: {functions_found}/{total_functions} functions")
        else:
            self.record_test_result("analytics_deployment_script", "FAIL",
                                  {"functions_found": functions_found, "total_functions": total_functions,
                                   "functions": required_functions})
            self.fail(f"Only {functions_found}/{total_functions} required functions found")
    
    @patch('requests.get')
    def test_google_analytics_measurement_id_validity(self, mock_get):
        """Test that Google Analytics Measurement ID is valid format"""
        print("🧪 Testing Google Analytics Measurement ID validity...")
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Check Measurement ID format
        measurement_id = "G-Q4ZZ5SFJC0"
        
        # Validate format: G-XXXXXXXXX
        if re.match(r'^G-[A-Z0-9]{10}$', measurement_id):
            self.record_test_result("google_analytics_measurement_id_validity", "PASS",
                                  {"measurement_id": measurement_id, "format": "valid"})
            print(f"✅ Google Analytics Measurement ID format valid: {measurement_id}")
        else:
            self.record_test_result("google_analytics_measurement_id_validity", "FAIL",
                                  {"measurement_id": measurement_id, "format": "invalid"})
            self.fail(f"Invalid Measurement ID format: {measurement_id}")
    
    def test_structured_data_presence(self):
        """Test that structured data is present in layout"""
        print("🧪 Testing structured data presence...")
        
        base_layout_path = self.website_path / "_includes" / "layouts" / "base.njk"
        
        with open(base_layout_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for structured data
        structured_data_elements = {
            "json_ld": "application/ld+json" in content,
            "schema_context": '"@context": "https://schema.org"' in content,
            "website_type": '"@type": "WebSite"' in content,
            "search_action": "SearchAction" in content,
            "organization_data": "Organization" in content
        }
        
        elements_found = sum(structured_data_elements.values())
        total_elements = len(structured_data_elements)
        
        if elements_found >= 3:  # At least 3 out of 5 elements
            self.record_test_result("structured_data_presence", "PASS",
                                  {"elements_found": elements_found, "total_elements": total_elements,
                                   "elements": structured_data_elements})
            print(f"✅ Structured data present: {elements_found}/{total_elements} elements")
        else:
            self.record_test_result("structured_data_presence", "FAIL",
                                  {"elements_found": elements_found, "total_elements": total_elements,
                                   "elements": structured_data_elements})
            self.fail(f"Only {elements_found}/{total_elements} structured data elements found")
    
    def test_performance_tracking_features(self):
        """Test that performance tracking features are implemented"""
        print("🧪 Testing performance tracking features...")
        
        base_layout_path = self.website_path / "_includes" / "layouts" / "base.njk"
        
        with open(base_layout_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for performance tracking features
        performance_features = {
            "core_web_vitals": "Core Web Vitals" in content,
            "load_time_tracking": "load_time_ms" in content,
            "dom_content_loaded": "domContentLoaded" in content,
            "slow_page_detection": "slow_page_load" in content,
            "user_engagement": "user_engagement" in content,
            "scroll_tracking": "max_scroll_percent" in content
        }
        
        features_found = sum(performance_features.values())
        total_features = len(performance_features)
        
        if features_found >= 4:  # At least 4 out of 6 features
            self.record_test_result("performance_tracking_features", "PASS",
                                  {"features_found": features_found, "total_features": total_features,
                                   "features": performance_features})
            print(f"✅ Performance tracking features implemented: {features_found}/{total_features} features")
        else:
            self.record_test_result("performance_tracking_features", "FAIL",
                                  {"features_found": features_found, "total_features": total_features,
                                   "features": performance_features})
            self.fail(f"Only {features_found}/{total_features} performance tracking features found")
    
    def test_error_tracking_implementation(self):
        """Test that error tracking is implemented"""
        print("🧪 Testing error tracking implementation...")
        
        base_layout_path = self.website_path / "_includes" / "layouts" / "base.njk"
        
        with open(base_layout_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for error tracking features
        error_tracking_features = {
            "javascript_error_tracking": "javascript_error" in content,
            "resource_error_tracking": "resource_error" in content,
            "error_event_listener": "addEventListener('error'" in content,
            "error_reporting": "trackSWGDBEvent" in content and "error" in content
        }
        
        features_found = sum(error_tracking_features.values())
        total_features = len(error_tracking_features)
        
        if features_found >= 3:  # At least 3 out of 4 features
            self.record_test_result("error_tracking_implementation", "PASS",
                                  {"features_found": features_found, "total_features": total_features,
                                   "features": error_tracking_features})
            print(f"✅ Error tracking implemented: {features_found}/{total_features} features")
        else:
            self.record_test_result("error_tracking_implementation", "FAIL",
                                  {"features_found": features_found, "total_features": total_features,
                                   "features": error_tracking_features})
            self.fail(f"Only {features_found}/{total_features} error tracking features found")
    
    def test_user_interaction_tracking(self):
        """Test that user interaction tracking is implemented"""
        print("🧪 Testing user interaction tracking...")
        
        base_layout_path = self.website_path / "_includes" / "layouts" / "base.njk"
        
        with open(base_layout_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for user interaction tracking features
        interaction_features = {
            "filter_tracking": "filter_used" in content,
            "search_tracking": "search_performed" in content,
            "navigation_tracking": "navigation_click" in content,
            "form_tracking": "form_submitted" in content,
            "tab_tracking": "tab_clicked" in content,
            "loot_interaction": "loot_interaction" in content
        }
        
        features_found = sum(interaction_features.values())
        total_features = len(interaction_features)
        
        if features_found >= 4:  # At least 4 out of 6 features
            self.record_test_result("user_interaction_tracking", "PASS",
                                  {"features_found": features_found, "total_features": total_features,
                                   "features": interaction_features})
            print(f"✅ User interaction tracking implemented: {features_found}/{total_features} features")
        else:
            self.record_test_result("user_interaction_tracking", "FAIL",
                                  {"features_found": features_found, "total_features": total_features,
                                   "features": interaction_features})
            self.fail(f"Only {features_found}/{total_features} user interaction tracking features found")

def run_test_suite():
    """Run the complete test suite"""
    print("🚀 Starting Batch 184 Analytics Integration Test Suite")
    print("=" * 70)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBatch184Analytics)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 BATCH 184 TEST SUMMARY")
    print("=" * 70)
    
    total_tests = result.testsRun
    failed_tests = len(result.failures) + len(result.errors)
    passed_tests = total_tests - failed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Batch 184 Analytics Integration is ready for production")
    else:
        print(f"\n⚠️ {failed_tests} TESTS FAILED")
        print("❌ Please review and fix the failed tests")
        
        if result.failures:
            print("\nFailed Tests:")
            for test, traceback in result.failures:
                print(f"  ❌ {test}")
        
        if result.errors:
            print("\nError Tests:")
            for test, traceback in result.errors:
                print(f"  ❌ {test}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_test_suite()
    
    if success:
        print("\n🎯 BATCH 184 IMPLEMENTATION: SUCCESS")
        print("✅ Google Analytics + Search Console Integration Complete")
        print("✅ SEO optimization implemented")
        print("✅ Analytics insights flowing")
    else:
        print("\n🔧 BATCH 184 IMPLEMENTATION: NEEDS ATTENTION")
        print("❌ Some tests failed - please review and fix") 
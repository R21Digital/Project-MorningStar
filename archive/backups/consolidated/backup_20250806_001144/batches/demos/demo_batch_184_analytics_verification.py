#!/usr/bin/env python3
"""
Batch 184 - Google Analytics + Search Console Integration Verification
Objective: Install and verify basic SEO/analytics setup for SWGDB

This script verifies that all required components are in place:
1. Google Tag Manager script in layout
2. robots.txt and sitemap.xml setup
3. Meta description tags
4. Domain verification with Google Search Console
"""

import os
import json
import re
import requests
from pathlib import Path
from datetime import datetime

class AnalyticsVerification:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.website_path = self.base_path / "website"
        self.swgdb_site_path = self.base_path / "swgdb_site"
        self.verification_results = {
            "timestamp": datetime.now().isoformat(),
            "batch": "184",
            "title": "Google Analytics + Search Console Integration",
            "status": "PENDING",
            "components": {},
            "recommendations": []
        }
    
    def verify_google_analytics_script(self):
        """Verify Google Analytics script is properly configured"""
        print("🔍 Verifying Google Analytics script...")
        
        # Check website base layout
        base_layout_path = self.website_path / "_includes" / "layouts" / "base.njk"
        if base_layout_path.exists():
            with open(base_layout_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Google Analytics script
            ga_script_pattern = r'https://www\.googletagmanager\.com/gtag/js\?id=G-[A-Z0-9]+'
            ga_match = re.search(ga_script_pattern, content)
            
            if ga_match:
                ga_id = ga_match.group(0).split('=')[-1]
                self.verification_results["components"]["google_analytics"] = {
                    "status": "PASS",
                    "measurement_id": ga_id,
                    "script_present": True,
                    "enhanced_tracking": "G-Q4ZZ5SFJC0" in content
                }
                print(f"✅ Google Analytics script found with ID: {ga_id}")
            else:
                self.verification_results["components"]["google_analytics"] = {
                    "status": "FAIL",
                    "error": "Google Analytics script not found"
                }
                print("❌ Google Analytics script not found")
        else:
            self.verification_results["components"]["google_analytics"] = {
                "status": "FAIL",
                "error": "Base layout file not found"
            }
            print("❌ Base layout file not found")
    
    def verify_analytics_include_file(self):
        """Verify analytics include file exists and is properly configured"""
        print("🔍 Verifying analytics include file...")
        
        analytics_path = self.swgdb_site_path / "_includes" / "analytics.html"
        if analytics_path.exists():
            with open(analytics_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required components
            required_elements = {
                "google_analytics_script": "https://www.googletagmanager.com/gtag/js?id=G-Q4ZZ5SFJC0" in content,
                "gtag_config": "gtag('config', 'G-Q4ZZ5SFJC0'" in content,
                "custom_tracking": "trackSWGDBEvent" in content,
                "search_console_verification": "google-site-verification" in content,
                "structured_data": "application/ld+json" in content,
                "open_graph_tags": "og:title" in content,
                "twitter_cards": "twitter:card" in content
            }
            
            all_present = all(required_elements.values())
            
            self.verification_results["components"]["analytics_include"] = {
                "status": "PASS" if all_present else "FAIL",
                "elements": required_elements,
                "file_path": str(analytics_path)
            }
            
            if all_present:
                print("✅ Analytics include file properly configured")
            else:
                missing = [k for k, v in required_elements.items() if not v]
                print(f"❌ Missing elements in analytics include: {missing}")
        else:
            self.verification_results["components"]["analytics_include"] = {
                "status": "FAIL",
                "error": "Analytics include file not found"
            }
            print("❌ Analytics include file not found")
    
    def verify_robots_txt(self):
        """Verify robots.txt is properly configured"""
        print("🔍 Verifying robots.txt...")
        
        robots_path = self.swgdb_site_path / "robots.txt"
        if robots_path.exists():
            with open(robots_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_elements = {
                "user_agent": "User-agent: *" in content,
                "allow_all": "Allow: /" in content,
                "sitemap_reference": "Sitemap: https://swgdb.com/sitemap.xml" in content,
                "disallow_admin": "Disallow: /admin/" in content,
                "disallow_private": "Disallow: /private/" in content
            }
            
            all_present = all(required_elements.values())
            
            self.verification_results["components"]["robots_txt"] = {
                "status": "PASS" if all_present else "FAIL",
                "elements": required_elements,
                "file_path": str(robots_path)
            }
            
            if all_present:
                print("✅ robots.txt properly configured")
            else:
                missing = [k for k, v in required_elements.items() if not v]
                print(f"❌ Missing elements in robots.txt: {missing}")
        else:
            self.verification_results["components"]["robots_txt"] = {
                "status": "FAIL",
                "error": "robots.txt file not found"
            }
            print("❌ robots.txt file not found")
    
    def verify_sitemap_xml(self):
        """Verify sitemap.xml is properly configured"""
        print("🔍 Verifying sitemap.xml...")
        
        sitemap_path = self.swgdb_site_path / "sitemap.xml"
        if sitemap_path.exists():
            with open(sitemap_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required XML structure
            required_elements = {
                "xml_declaration": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" in content,
                "urlset_namespace": "xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"" in content,
                "homepage_url": "https://swgdb.com/" in content,
                "heroics_url": "https://swgdb.com/pages/heroics/" in content,
                "loot_url": "https://swgdb.com/pages/loot/" in content,
                "builds_url": "https://swgdb.com/pages/builds/" in content,
                "tools_url": "https://swgdb.com/pages/tools/" in content
            }
            
            # Count URLs
            url_count = len(re.findall(r'<url>', content))
            
            all_present = all(required_elements.values())
            
            self.verification_results["components"]["sitemap_xml"] = {
                "status": "PASS" if all_present else "FAIL",
                "elements": required_elements,
                "url_count": url_count,
                "file_path": str(sitemap_path)
            }
            
            if all_present:
                print(f"✅ sitemap.xml properly configured with {url_count} URLs")
            else:
                missing = [k for k, v in required_elements.items() if not v]
                print(f"❌ Missing elements in sitemap.xml: {missing}")
        else:
            self.verification_results["components"]["sitemap_xml"] = {
                "status": "FAIL",
                "error": "sitemap.xml file not found"
            }
            print("❌ sitemap.xml file not found")
    
    def verify_seo_config(self):
        """Verify SEO configuration is properly set up"""
        print("🔍 Verifying SEO configuration...")
        
        seo_config_path = self.website_path / "config" / "seo.json"
        if seo_config_path.exists():
            with open(seo_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            required_sections = {
                "analytics": "analytics" in config,
                "search_console": "search_console" in config,
                "social": "social" in config,
                "structured_data": "structured_data" in config
            }
            
            analytics_config = config.get("analytics", {})
            analytics_elements = {
                "google_analytics_id": analytics_config.get("googleAnalyticsId") == "G-Q4ZZ5SFJC0",
                "tracking_enabled": analytics_config.get("trackingEnabled", False),
                "enable_cookie_consent": analytics_config.get("enableCookieConsent", False)
            }
            
            search_console_config = config.get("search_console", {})
            search_console_elements = {
                "google_site_verification": "googleSiteVerification" in search_console_config
            }
            
            all_sections_present = all(required_sections.values())
            all_analytics_present = all(analytics_elements.values())
            all_search_console_present = all(search_console_elements.values())
            
            self.verification_results["components"]["seo_config"] = {
                "status": "PASS" if all_sections_present and all_analytics_present else "FAIL",
                "sections": required_sections,
                "analytics_config": analytics_elements,
                "search_console_config": search_console_elements,
                "file_path": str(seo_config_path)
            }
            
            if all_sections_present and all_analytics_present:
                print("✅ SEO configuration properly set up")
            else:
                issues = []
                if not all_sections_present:
                    issues.append("missing sections")
                if not all_analytics_present:
                    issues.append("analytics configuration issues")
                print(f"❌ SEO configuration issues: {', '.join(issues)}")
        else:
            self.verification_results["components"]["seo_config"] = {
                "status": "FAIL",
                "error": "SEO configuration file not found"
            }
            print("❌ SEO configuration file not found")
    
    def verify_meta_tags_in_layout(self):
        """Verify meta description tags are properly configured in layout"""
        print("🔍 Verifying meta description tags...")
        
        base_layout_path = self.website_path / "_includes" / "layouts" / "base.njk"
        if base_layout_path.exists():
            with open(base_layout_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
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
            
            all_present = all(required_meta_tags.values())
            
            self.verification_results["components"]["meta_tags"] = {
                "status": "PASS" if all_present else "FAIL",
                "tags": required_meta_tags
            }
            
            if all_present:
                print("✅ Meta description tags properly configured")
            else:
                missing = [k for k, v in required_meta_tags.items() if not v]
                print(f"❌ Missing meta tags: {missing}")
        else:
            self.verification_results["components"]["meta_tags"] = {
                "status": "FAIL",
                "error": "Base layout file not found"
            }
            print("❌ Base layout file not found")
    
    def verify_google_search_console_setup(self):
        """Verify Google Search Console setup guide exists"""
        print("🔍 Verifying Google Search Console setup...")
        
        gsc_guide_path = self.swgdb_site_path / "GSC_SETUP_GUIDE.md"
        if gsc_guide_path.exists():
            with open(gsc_guide_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_sections = {
                "google_analytics_setup": "Google Analytics Setup" in content,
                "search_console_setup": "Google Search Console Setup" in content,
                "verification_instructions": "Verify Ownership" in content,
                "sitemap_submission": "Submit Sitemap" in content,
                "testing_instructions": "Testing & Validation" in content
            }
            
            all_present = all(required_sections.values())
            
            self.verification_results["components"]["search_console_setup"] = {
                "status": "PASS" if all_present else "FAIL",
                "sections": required_sections,
                "guide_path": str(gsc_guide_path)
            }
            
            if all_present:
                print("✅ Google Search Console setup guide exists")
            else:
                missing = [k for k, v in required_sections.items() if not v]
                print(f"❌ Missing sections in setup guide: {missing}")
        else:
            self.verification_results["components"]["search_console_setup"] = {
                "status": "FAIL",
                "error": "Google Search Console setup guide not found"
            }
            print("❌ Google Search Console setup guide not found")
    
    def verify_deployment_script(self):
        """Verify analytics deployment script exists"""
        print("🔍 Verifying analytics deployment script...")
        
        deploy_script_path = self.swgdb_site_path / "deploy_analytics.py"
        if deploy_script_path.exists():
            with open(deploy_script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_functions = {
                "add_analytics_to_html": "def add_analytics_to_html" in content,
                "update_meta_tags": "def update_meta_tags" in content,
                "main_function": "def main()" in content
            }
            
            all_present = all(required_functions.values())
            
            self.verification_results["components"]["deployment_script"] = {
                "status": "PASS" if all_present else "FAIL",
                "functions": required_functions,
                "script_path": str(deploy_script_path)
            }
            
            if all_present:
                print("✅ Analytics deployment script exists")
            else:
                missing = [k for k, v in required_functions.items() if not v]
                print(f"❌ Missing functions in deployment script: {missing}")
        else:
            self.verification_results["components"]["deployment_script"] = {
                "status": "FAIL",
                "error": "Analytics deployment script not found"
            }
            print("❌ Analytics deployment script not found")
    
    def generate_recommendations(self):
        """Generate recommendations based on verification results"""
        print("🔍 Generating recommendations...")
        
        recommendations = []
        
        # Check overall status
        all_components = self.verification_results["components"]
        failed_components = [name for name, data in all_components.items() if data.get("status") == "FAIL"]
        
        if failed_components:
            recommendations.append(f"Fix failed components: {', '.join(failed_components)}")
        
        # Specific recommendations
        if "google_analytics" in all_components and all_components["google_analytics"]["status"] == "PASS":
            recommendations.append("✅ Google Analytics is properly configured")
        else:
            recommendations.append("❌ Configure Google Analytics with Measurement ID G-Q4ZZ5SFJC0")
        
        if "search_console_setup" in all_components and all_components["search_console_setup"]["status"] == "PASS":
            recommendations.append("✅ Google Search Console setup guide is available")
        else:
            recommendations.append("❌ Create Google Search Console setup guide")
        
        if "robots_txt" in all_components and all_components["robots_txt"]["status"] == "PASS":
            recommendations.append("✅ robots.txt is properly configured")
        else:
            recommendations.append("❌ Configure robots.txt with proper directives")
        
        if "sitemap_xml" in all_components and all_components["sitemap_xml"]["status"] == "PASS":
            recommendations.append("✅ sitemap.xml is properly configured")
        else:
            recommendations.append("❌ Configure sitemap.xml with all pages")
        
        # Additional recommendations
        recommendations.extend([
            "🔍 Verify domain ownership in Google Search Console",
            "📊 Submit sitemap.xml to Google Search Console",
            "📈 Monitor Google Analytics for data flow",
            "🔍 Test page loading and tracking in real-time",
            "📱 Verify mobile-friendliness and Core Web Vitals"
        ])
        
        self.verification_results["recommendations"] = recommendations
    
    def determine_overall_status(self):
        """Determine overall verification status"""
        all_components = self.verification_results["components"]
        
        if not all_components:
            self.verification_results["status"] = "FAIL"
            return
        
        failed_components = [name for name, data in all_components.items() if data.get("status") == "FAIL"]
        
        if failed_components:
            self.verification_results["status"] = "PARTIAL"
            if len(failed_components) == len(all_components):
                self.verification_results["status"] = "FAIL"
        else:
            self.verification_results["status"] = "PASS"
    
    def save_results(self):
        """Save verification results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.base_path / f"BATCH_184_VERIFICATION_REPORT_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, indent=2)
        
        print(f"\n📊 Verification results saved to: {results_file}")
        return results_file
    
    def run_verification(self):
        """Run complete verification process"""
        print("🚀 Starting Batch 184 Analytics Verification")
        print("=" * 60)
        
        # Run all verification checks
        self.verify_google_analytics_script()
        self.verify_analytics_include_file()
        self.verify_robots_txt()
        self.verify_sitemap_xml()
        self.verify_seo_config()
        self.verify_meta_tags_in_layout()
        self.verify_google_search_console_setup()
        self.verify_deployment_script()
        
        # Generate recommendations and determine status
        self.generate_recommendations()
        self.determine_overall_status()
        
        # Save results
        results_file = self.save_results()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        
        status = self.verification_results["status"]
        status_emoji = {"PASS": "✅", "PARTIAL": "⚠️", "FAIL": "❌"}
        
        print(f"Overall Status: {status_emoji.get(status, '❓')} {status}")
        
        for component, data in self.verification_results["components"].items():
            comp_status = data.get("status", "UNKNOWN")
            comp_emoji = {"PASS": "✅", "FAIL": "❌", "UNKNOWN": "❓"}
            print(f"  {comp_emoji.get(comp_status, '❓')} {component}: {comp_status}")
        
        print(f"\n📋 Recommendations:")
        for rec in self.verification_results["recommendations"]:
            print(f"  {rec}")
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        return self.verification_results

def main():
    """Main function"""
    verifier = AnalyticsVerification()
    results = verifier.run_verification()
    
    if results["status"] == "PASS":
        print("\n🎉 Batch 184 verification completed successfully!")
        print("Google Analytics + Search Console Integration is ready.")
    elif results["status"] == "PARTIAL":
        print("\n⚠️ Batch 184 verification completed with issues.")
        print("Some components need attention before full deployment.")
    else:
        print("\n❌ Batch 184 verification failed.")
        print("Please address all issues before deployment.")

if __name__ == "__main__":
    main() 
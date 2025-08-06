#!/usr/bin/env python3
"""
Batch 196 - Contributor Badges + Credits Page Test
Goal: Acknowledge contributors, modders, guide writers, and community helpers.

Test Coverage:
- Tiered badges: Guide Author, Modder, Bug Hunter, Tester
- Link Discord handle or nickname
- Pull from mod/guide metadata
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

class ContributorBadgesTester:
    def __init__(self):
        self.test_results = {
            "batch": "196",
            "feature": "Contributor Badges + Credits Page",
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
        # Define test paths
        self.base_path = Path(__file__).parent
        self.credits_page_path = self.base_path / "src" / "pages" / "credits" / "index.11ty.js"
        self.contributors_data_path = self.base_path / "src" / "data" / "contributors.json"
        self.badge_component_path = self.base_path / "src" / "components" / "Badge.svelte"
        
        # Required features for Batch 196
        self.required_features = {
            "tiered_badges": {
                "keywords": ["guide-author", "modder", "bug-hunter", "tester"],
                "sections": ["Guide Authors", "Modders", "Bug Hunters", "Testers"]
            },
            "discord_integration": {
                "keywords": ["discord", "handle", "nickname", "@"],
                "sections": ["Discord Integration", "Community"]
            },
            "metadata_pulling": {
                "keywords": ["metadata", "auto_pull", "mod", "guide"],
                "sections": ["Metadata Integration", "Auto Pull"]
            }
        }

    def log_test(self, test_name, status, message, details=None):
        """Log a test result"""
        test_result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {}
        }
        
        self.test_results["tests"].append(test_result)
        self.test_results["summary"]["total_tests"] += 1
        
        if status == "PASS":
            self.test_results["summary"]["passed"] += 1
        elif status == "FAIL":
            self.test_results["summary"]["failed"] += 1
        elif status == "WARNING":
            self.test_results["summary"]["warnings"] += 1
            
        print(f"[{status}] {test_name}: {message}")

    def test_file_existence(self):
        """Test that required files exist"""
        print("\n=== Testing File Existence ===")
        
        # Test credits page file
        if self.credits_page_path.exists():
            self.log_test("Credits Page File Exists", "PASS", 
                         f"Found {self.credits_page_path}")
        else:
            self.log_test("Credits Page File Exists", "FAIL", 
                         f"Missing {self.credits_page_path}")
            
        # Test contributors data file
        if self.contributors_data_path.exists():
            self.log_test("Contributors Data File Exists", "PASS", 
                         f"Found {self.contributors_data_path}")
        else:
            self.log_test("Contributors Data File Exists", "FAIL", 
                         f"Missing {self.contributors_data_path}")
            
        # Test badge component file
        if self.badge_component_path.exists():
            self.log_test("Badge Component File Exists", "PASS", 
                         f"Found {self.badge_component_path}")
        else:
            self.log_test("Badge Component File Exists", "FAIL", 
                         f"Missing {self.badge_component_path}")

    def test_credits_page_structure(self):
        """Test the structure and content of the credits page"""
        print("\n=== Testing Credits Page Structure ===")
        
        if not self.credits_page_path.exists():
            self.log_test("Credits Page Structure", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.credits_page_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for required sections in navigation
            nav_sections = [
                "Guide Authors",
                "Modders", 
                "Bug Hunters",
                "Testers",
                "Community Helpers",
                "Special Thanks"
            ]
            
            for section in nav_sections:
                if section.lower() in content.lower():
                    self.log_test(f"Navigation Section: {section}", "PASS", 
                                 f"Found {section} in navigation")
                else:
                    self.log_test(f"Navigation Section: {section}", "WARNING", 
                                 f"Missing {section} in navigation")
                    
            # Test for badge tier information
            if "Badge Tiers" in content:
                self.log_test("Badge Tiers Section", "PASS", 
                             "Badge tiers section found")
            else:
                self.log_test("Badge Tiers Section", "FAIL", 
                             "Badge tiers section missing")
                
            # Test for community stats
            if "Community Stats" in content:
                self.log_test("Community Stats Section", "PASS", 
                             "Community stats section found")
            else:
                self.log_test("Community Stats Section", "WARNING", 
                             "Community stats section missing")
                
        except Exception as e:
            self.log_test("Credits Page Structure", "FAIL", f"Error reading file: {e}")

    def test_contributors_data_content(self):
        """Test the content of contributors data file"""
        print("\n=== Testing Contributors Data Content ===")
        
        if not self.contributors_data_path.exists():
            self.log_test("Contributors Data Content", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.contributors_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Test for required structure
            if "contributors" in data:
                self.log_test("Contributors Array", "PASS", 
                             f"Found contributors array with {len(data['contributors'])} contributors")
            else:
                self.log_test("Contributors Array", "FAIL", 
                             "Missing contributors array")
                
            # Test for metadata
            if "metadata" in data:
                self.log_test("Metadata Section", "PASS", 
                             "Metadata section found")
            else:
                self.log_test("Metadata Section", "WARNING", 
                             "Metadata section missing")
                
            # Test individual contributors
            if "contributors" in data:
                contributors = data["contributors"]
                for i, contributor in enumerate(contributors[:5]):  # Test first 5
                    # Test required fields
                    if "name" in contributor:
                        self.log_test(f"Contributor {i+1} Name", "PASS", 
                                     f"Name: {contributor['name']}")
                    else:
                        self.log_test(f"Contributor {i+1} Name", "FAIL", 
                                     "Missing name field")
                        
                    if "badges" in contributor:
                        self.log_test(f"Contributor {i+1} Badges", "PASS", 
                                     f"Badges: {contributor['badges']}")
                    else:
                        self.log_test(f"Contributor {i+1} Badges", "FAIL", 
                                     "Missing badges field")
                        
                    if "discord" in contributor:
                        self.log_test(f"Contributor {i+1} Discord", "PASS", 
                                     f"Discord: {contributor['discord']}")
                    else:
                        self.log_test(f"Contributor {i+1} Discord", "WARNING", 
                                     "Missing discord field")
                        
        except Exception as e:
            self.log_test("Contributors Data Content", "FAIL", f"Error reading file: {e}")

    def test_tiered_badges(self):
        """Test tiered badges implementation"""
        print("\n=== Testing Tiered Badges ===")
        
        if not self.contributors_data_path.exists():
            self.log_test("Tiered Badges", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.contributors_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Required badge types
            required_badges = ["guide-author", "modder", "bug-hunter", "tester"]
            
            if "contributors" in data:
                contributors = data["contributors"]
                badge_counts = {}
                
                for contributor in contributors:
                    if "badges" in contributor:
                        for badge in contributor["badges"]:
                            badge_counts[badge] = badge_counts.get(badge, 0) + 1
                
                for badge in required_badges:
                    if badge in badge_counts:
                        self.log_test(f"Badge Type: {badge}", "PASS", 
                                     f"Found {badge_counts[badge]} contributors with {badge} badge")
                    else:
                        self.log_test(f"Badge Type: {badge}", "FAIL", 
                                     f"No contributors with {badge} badge")
                        
            # Test badge metadata
            if "metadata" in data and "badge_counts" in data["metadata"]:
                self.log_test("Badge Counts Metadata", "PASS", 
                             "Badge counts metadata found")
            else:
                self.log_test("Badge Counts Metadata", "WARNING", 
                             "Badge counts metadata missing")
                
        except Exception as e:
            self.log_test("Tiered Badges", "FAIL", f"Error testing badges: {e}")

    def test_discord_integration(self):
        """Test Discord integration features"""
        print("\n=== Testing Discord Integration ===")
        
        if not self.contributors_data_path.exists():
            self.log_test("Discord Integration", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.contributors_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if "contributors" in data:
                contributors = data["contributors"]
                discord_users = 0
                
                for contributor in contributors:
                    if "discord" in contributor and contributor["discord"]:
                        discord_users += 1
                        
                if discord_users > 0:
                    self.log_test("Discord Handles", "PASS", 
                                 f"Found {discord_users} contributors with Discord handles")
                else:
                    self.log_test("Discord Handles", "FAIL", 
                                 "No contributors with Discord handles")
                    
            # Test Discord link in page
            if self.credits_page_path.exists():
                with open(self.credits_page_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if "discord.gg" in content or "discord" in content.lower():
                    self.log_test("Discord Link in Page", "PASS", 
                                 "Discord link found in credits page")
                else:
                    self.log_test("Discord Link in Page", "WARNING", 
                                 "Discord link missing in credits page")
                    
        except Exception as e:
            self.log_test("Discord Integration", "FAIL", f"Error testing Discord: {e}")

    def test_badge_component(self):
        """Test the Badge Svelte component"""
        print("\n=== Testing Badge Component ===")
        
        if not self.badge_component_path.exists():
            self.log_test("Badge Component", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.badge_component_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for required badge types
            badge_types = ["guide-author", "modder", "bug-hunter", "tester", "community-helper"]
            
            for badge_type in badge_types:
                if badge_type in content:
                    self.log_test(f"Badge Type: {badge_type}", "PASS", 
                                 f"Found {badge_type} in component")
                else:
                    self.log_test(f"Badge Type: {badge_type}", "WARNING", 
                                 f"Missing {badge_type} in component")
                    
            # Test for size variations
            sizes = ["small", "medium", "large"]
            for size in sizes:
                if size in content:
                    self.log_test(f"Badge Size: {size}", "PASS", 
                                 f"Found {size} size in component")
                else:
                    self.log_test(f"Badge Size: {size}", "WARNING", 
                                 f"Missing {size} size in component")
                    
            # Test for animations
            if "animated" in content:
                self.log_test("Animation Support", "PASS", 
                             "Animation support found in component")
            else:
                self.log_test("Animation Support", "WARNING", 
                             "Animation support missing in component")
                
            # Test for accessibility
            if "role=" in content and "tabindex" in content:
                self.log_test("Accessibility Features", "PASS", 
                             "Accessibility features found in component")
            else:
                self.log_test("Accessibility Features", "WARNING", 
                             "Accessibility features missing in component")
                
        except Exception as e:
            self.log_test("Badge Component", "FAIL", f"Error testing component: {e}")

    def test_metadata_pulling(self):
        """Test metadata pulling functionality"""
        print("\n=== Testing Metadata Pulling ===")
        
        if not self.contributors_data_path.exists():
            self.log_test("Metadata Pulling", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.contributors_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Test for metadata section
            if "metadata" in data:
                metadata = data["metadata"]
                
                # Test for auto_pull_metadata flag
                if "auto_pull_metadata" in metadata:
                    self.log_test("Auto Pull Metadata Flag", "PASS", 
                                 "Auto pull metadata flag found")
                else:
                    self.log_test("Auto Pull Metadata Flag", "WARNING", 
                                 "Auto pull metadata flag missing")
                    
                # Test for discord_integration flag
                if "discord_integration" in metadata:
                    self.log_test("Discord Integration Flag", "PASS", 
                                 "Discord integration flag found")
                else:
                    self.log_test("Discord Integration Flag", "WARNING", 
                                 "Discord integration flag missing")
                    
                # Test for badge counts
                if "badge_counts" in metadata:
                    self.log_test("Badge Counts Metadata", "PASS", 
                                 "Badge counts metadata found")
                else:
                    self.log_test("Badge Counts Metadata", "WARNING", 
                                 "Badge counts metadata missing")
                    
            else:
                self.log_test("Metadata Section", "FAIL", 
                             "Metadata section missing")
                
        except Exception as e:
            self.log_test("Metadata Pulling", "FAIL", f"Error testing metadata: {e}")

    def test_page_functionality(self):
        """Test that the page can be rendered properly"""
        print("\n=== Testing Page Functionality ===")
        
        if not self.credits_page_path.exists():
            self.log_test("Page Functionality", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.credits_page_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for required JavaScript functionality
            js_elements = [
                "fs.readFileSync",
                "JSON.parse",
                "eleventyComputed"
            ]
            
            for element in js_elements:
                if element in content:
                    self.log_test(f"JS Functionality: {element}", "PASS", 
                                 f"Found JS element: {element}")
                else:
                    self.log_test(f"JS Functionality: {element}", "WARNING", 
                                 f"Missing JS element: {element}")
                    
            # Test for error handling
            if "try {" in content and "catch (error)" in content:
                self.log_test("Error Handling", "PASS", "Error handling implemented")
            else:
                self.log_test("Error Handling", "WARNING", "Error handling missing")
                
            # Test for responsive design
            if "@media (max-width:" in content:
                self.log_test("Responsive Design", "PASS", "Responsive design implemented")
            else:
                self.log_test("Responsive Design", "WARNING", "Responsive design missing")
                
        except Exception as e:
            self.log_test("Page Functionality", "FAIL", f"Error testing functionality: {e}")

    def test_contributor_links(self):
        """Test contributor links and references"""
        print("\n=== Testing Contributor Links ===")
        
        if not self.contributors_data_path.exists():
            self.log_test("Contributor Links", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.contributors_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if "contributors" in data:
                contributors = data["contributors"]
                contributors_with_links = 0
                
                for contributor in contributors:
                    if "links" in contributor and contributor["links"]:
                        contributors_with_links += 1
                        
                if contributors_with_links > 0:
                    self.log_test("Contributor Links", "PASS", 
                                 f"Found {contributors_with_links} contributors with links")
                else:
                    self.log_test("Contributor Links", "WARNING", 
                                 "No contributors with links")
                    
            # Test for guide/mod references
            guide_mod_references = 0
            for contributor in contributors:
                if "contributions" in contributor:
                    contributions = contributor["contributions"].lower()
                    if "guide" in contributions or "mod" in contributions:
                        guide_mod_references += 1
                        
            if guide_mod_references > 0:
                self.log_test("Guide/Mod References", "PASS", 
                             f"Found {guide_mod_references} contributors with guide/mod references")
            else:
                self.log_test("Guide/Mod References", "WARNING", 
                             "No guide/mod references found")
                
        except Exception as e:
            self.log_test("Contributor Links", "FAIL", f"Error testing links: {e}")

    def run_all_tests(self):
        """Run all tests for Batch 196"""
        print("=" * 60)
        print("BATCH 196 - CONTRIBUTOR BADGES + CREDITS PAGE TEST")
        print("=" * 60)
        print(f"Testing: {self.test_results['feature']}")
        print(f"Timestamp: {self.test_results['timestamp']}")
        print("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_file_existence,
            self.test_credits_page_structure,
            self.test_contributors_data_content,
            self.test_tiered_badges,
            self.test_discord_integration,
            self.test_badge_component,
            self.test_metadata_pulling,
            self.test_page_functionality,
            self.test_contributor_links
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(test_method.__name__, "FAIL", f"Test method error: {e}")
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        summary = self.test_results["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Warnings: {summary['warnings']}")
        
        if summary['failed'] == 0 and summary['total_tests'] > 0:
            print("\n✅ BATCH 196 IMPLEMENTATION: SUCCESS")
            print("All required features for Contributor Badges + Credits Page are implemented.")
        elif summary['failed'] > 0:
            print("\n❌ BATCH 196 IMPLEMENTATION: FAILED")
            print("Some required features are missing or incomplete.")
        else:
            print("\n⚠️ BATCH 196 IMPLEMENTATION: PARTIAL")
            print("Implementation has warnings but no critical failures.")
            
        # Save test results
        self.save_test_results()

    def save_test_results(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"BATCH_196_TEST_REPORT_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"\nTest results saved to: {filename}")
        except Exception as e:
            print(f"\nError saving test results: {e}")

def main():
    """Main test execution"""
    tester = ContributorBadgesTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 
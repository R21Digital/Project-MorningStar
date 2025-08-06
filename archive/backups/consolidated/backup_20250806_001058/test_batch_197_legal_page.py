#!/usr/bin/env python3
"""
Batch 197 - Legal + Compliance Notices Page Test
Goal: Cover fair use, disclaimers, and mod compliance rules.

Test Coverage:
- DMCA disclaimer
- SWG Restoration rules summary  
- Mod compliance guidelines
- Terms of Use
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path

class LegalPageTester:
    def __init__(self):
        self.test_results = {
            "batch": "197",
            "feature": "Legal + Compliance Notices Page",
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
        self.legal_page_path = self.base_path / "src" / "pages" / "legal" / "index.11ty.js"
        self.legal_data_path = self.base_path / "src" / "data" / "legal" / "notices.md"
        
        # Required features for Batch 197
        self.required_features = {
            "dmca_disclaimer": {
                "keywords": ["DMCA", "copyright", "takedown", "infringement"],
                "sections": ["DMCA Disclaimer", "Digital Millennium Copyright Act"]
            },
            "swg_restoration_rules": {
                "keywords": ["SWG Restoration", "fair use", "community guidelines", "attribution"],
                "sections": ["SWG Restoration Rules Summary", "Fair Use of Star Wars Galaxies Content"]
            },
            "mod_compliance_guidelines": {
                "keywords": ["mod compliance", "mod development", "mod submission", "mod review"],
                "sections": ["Mod Compliance Guidelines", "Mod Development Standards"]
            },
            "terms_of_use": {
                "keywords": ["terms of use", "acceptance", "license", "restrictions"],
                "sections": ["Terms of Use", "Acceptance of Terms"]
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
        
        # Test legal page file
        if self.legal_page_path.exists():
            self.log_test("Legal Page File Exists", "PASS", 
                         f"Found {self.legal_page_path}")
        else:
            self.log_test("Legal Page File Exists", "FAIL", 
                         f"Missing {self.legal_page_path}")
            
        # Test legal data file
        if self.legal_data_path.exists():
            self.log_test("Legal Data File Exists", "PASS", 
                         f"Found {self.legal_data_path}")
        else:
            self.log_test("Legal Data File Exists", "FAIL", 
                         f"Missing {self.legal_data_path}")

    def test_legal_page_structure(self):
        """Test the structure and content of the legal page"""
        print("\n=== Testing Legal Page Structure ===")
        
        if not self.legal_page_path.exists():
            self.log_test("Legal Page Structure", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.legal_page_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for required sections in navigation
            nav_sections = [
                "DMCA Disclaimer",
                "SWG Restoration Rules", 
                "Mod Compliance Guidelines",
                "Terms of Use",
                "Fair Use Policy",
                "General Disclaimers"
            ]
            
            for section in nav_sections:
                if section.lower() in content.lower():
                    self.log_test(f"Navigation Section: {section}", "PASS", 
                                 f"Found {section} in navigation")
                else:
                    self.log_test(f"Navigation Section: {section}", "WARNING", 
                                 f"Missing {section} in navigation")
                    
            # Test for legal contact information
            if "legal@morningstar.swg.ms11.com" in content:
                self.log_test("Legal Contact Email", "PASS", 
                             "Legal contact email found")
            else:
                self.log_test("Legal Contact Email", "FAIL", 
                             "Legal contact email missing")
                
            # Test for compliance status indicators
            if "Compliance Status" in content and "✅ Compliant" in content:
                self.log_test("Compliance Status Indicators", "PASS", 
                             "Compliance status indicators found")
            else:
                self.log_test("Compliance Status Indicators", "WARNING", 
                             "Compliance status indicators missing")
                
        except Exception as e:
            self.log_test("Legal Page Structure", "FAIL", f"Error reading file: {e}")

    def test_legal_notices_content(self):
        """Test the content of legal notices markdown file"""
        print("\n=== Testing Legal Notices Content ===")
        
        if not self.legal_data_path.exists():
            self.log_test("Legal Notices Content", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.legal_data_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test each required feature
            for feature_name, feature_requirements in self.required_features.items():
                print(f"\n--- Testing {feature_name.replace('_', ' ').title()} ---")
                
                # Check for required sections
                sections_found = 0
                for section in feature_requirements["sections"]:
                    if section in content:
                        self.log_test(f"{feature_name} Section: {section}", "PASS", 
                                     f"Found section: {section}")
                        sections_found += 1
                    else:
                        self.log_test(f"{feature_name} Section: {section}", "FAIL", 
                                     f"Missing section: {section}")
                
                # Check for required keywords
                keywords_found = 0
                for keyword in feature_requirements["keywords"]:
                    if keyword.lower() in content.lower():
                        self.log_test(f"{feature_name} Keyword: {keyword}", "PASS", 
                                     f"Found keyword: {keyword}")
                        keywords_found += 1
                    else:
                        self.log_test(f"{feature_name} Keyword: {keyword}", "WARNING", 
                                     f"Missing keyword: {keyword}")
                
                # Overall feature assessment
                if sections_found >= len(feature_requirements["sections"]) * 0.8:
                    self.log_test(f"{feature_name} Overall", "PASS", 
                                 f"Feature adequately covered ({sections_found}/{len(feature_requirements['sections'])} sections)")
                else:
                    self.log_test(f"{feature_name} Overall", "FAIL", 
                                 f"Feature inadequately covered ({sections_found}/{len(feature_requirements['sections'])} sections)")
                    
        except Exception as e:
            self.log_test("Legal Notices Content", "FAIL", f"Error reading file: {e}")

    def test_dmca_compliance(self):
        """Test DMCA disclaimer compliance"""
        print("\n=== Testing DMCA Compliance ===")
        
        if not self.legal_data_path.exists():
            self.log_test("DMCA Compliance", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.legal_data_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Required DMCA elements
            dmca_elements = [
                "Digital Millennium Copyright Act",
                "copyright infringement", 
                "takedown procedure",
                "counter-notification",
                "designated copyright agent"
            ]
            
            elements_found = 0
            for element in dmca_elements:
                if element.lower() in content.lower():
                    self.log_test(f"DMCA Element: {element}", "PASS", 
                                 f"Found DMCA element: {element}")
                    elements_found += 1
                else:
                    self.log_test(f"DMCA Element: {element}", "FAIL", 
                                 f"Missing DMCA element: {element}")
                    
            # DMCA contact information
            if "legal@morningstar.swg.ms11.com" in content:
                self.log_test("DMCA Contact Email", "PASS", "DMCA contact email found")
            else:
                self.log_test("DMCA Contact Email", "FAIL", "DMCA contact email missing")
                
            # Response time specification
            if "48-72 hours" in content or "response time" in content.lower():
                self.log_test("DMCA Response Time", "PASS", "DMCA response time specified")
            else:
                self.log_test("DMCA Response Time", "WARNING", "DMCA response time not specified")
                
        except Exception as e:
            self.log_test("DMCA Compliance", "FAIL", f"Error testing DMCA: {e}")

    def test_swg_restoration_rules(self):
        """Test SWG restoration rules coverage"""
        print("\n=== Testing SWG Restoration Rules ===")
        
        if not self.legal_data_path.exists():
            self.log_test("SWG Restoration Rules", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.legal_data_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Required SWG restoration elements
            swg_elements = [
                "fair use",
                "educational purpose", 
                "non-commercial",
                "transformative",
                "community guidelines",
                "attribution",
                "Disney/Lucasfilm"
            ]
            
            elements_found = 0
            for element in swg_elements:
                if element.lower() in content.lower():
                    self.log_test(f"SWG Element: {element}", "PASS", 
                                 f"Found SWG element: {element}")
                    elements_found += 1
                else:
                    self.log_test(f"SWG Element: {element}", "WARNING", 
                                 f"Missing SWG element: {element}")
                    
            # Fair use factors
            fair_use_factors = [
                "purpose and character",
                "nature of copyrighted work", 
                "amount and substantiality",
                "effect on market"
            ]
            
            factors_found = 0
            for factor in fair_use_factors:
                if factor.lower() in content.lower():
                    self.log_test(f"Fair Use Factor: {factor}", "PASS", 
                                 f"Found fair use factor: {factor}")
                    factors_found += 1
                else:
                    self.log_test(f"Fair Use Factor: {factor}", "WARNING", 
                                 f"Missing fair use factor: {factor}")
                    
        except Exception as e:
            self.log_test("SWG Restoration Rules", "FAIL", f"Error testing SWG rules: {e}")

    def test_mod_compliance_guidelines(self):
        """Test mod compliance guidelines coverage"""
        print("\n=== Testing Mod Compliance Guidelines ===")
        
        if not self.legal_data_path.exists():
            self.log_test("Mod Compliance Guidelines", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.legal_data_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Required mod compliance elements
            mod_elements = [
                "mod development standards",
                "acceptable mod content",
                "prohibited mod content", 
                "mod submission guidelines",
                "mod review process",
                "safety testing",
                "malicious code"
            ]
            
            elements_found = 0
            for element in mod_elements:
                if element.lower() in content.lower():
                    self.log_test(f"Mod Element: {element}", "PASS", 
                                 f"Found mod element: {element}")
                    elements_found += 1
                else:
                    self.log_test(f"Mod Element: {element}", "WARNING", 
                                 f"Missing mod element: {element}")
                    
            # Mod categories
            mod_categories = [
                "game mechanics",
                "quality of life",
                "community tools", 
                "documentation",
                "commercial use",
                "copyright infringement"
            ]
            
            categories_found = 0
            for category in mod_categories:
                if category.lower() in content.lower():
                    self.log_test(f"Mod Category: {category}", "PASS", 
                                 f"Found mod category: {category}")
                    categories_found += 1
                else:
                    self.log_test(f"Mod Category: {category}", "WARNING", 
                                 f"Missing mod category: {category}")
                    
        except Exception as e:
            self.log_test("Mod Compliance Guidelines", "FAIL", f"Error testing mod guidelines: {e}")

    def test_terms_of_use(self):
        """Test Terms of Use coverage"""
        print("\n=== Testing Terms of Use ===")
        
        if not self.legal_data_path.exists():
            self.log_test("Terms of Use", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.legal_data_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Required Terms of Use elements
            terms_elements = [
                "acceptance of terms",
                "use license",
                "restrictions",
                "disclaimer",
                "limitations",
                "accuracy of materials",
                "links"
            ]
            
            elements_found = 0
            for element in terms_elements:
                if element.lower() in content.lower():
                    self.log_test(f"Terms Element: {element}", "PASS", 
                                 f"Found terms element: {element}")
                    elements_found += 1
                else:
                    self.log_test(f"Terms Element: {element}", "WARNING", 
                                 f"Missing terms element: {element}")
                    
            # Specific restrictions
            restrictions = [
                "modify or copy",
                "commercial purposes",
                "reverse engineer",
                "remove copyright",
                "transfer materials"
            ]
            
            restrictions_found = 0
            for restriction in restrictions:
                if restriction.lower() in content.lower():
                    self.log_test(f"Restriction: {restriction}", "PASS", 
                                 f"Found restriction: {restriction}")
                    restrictions_found += 1
                else:
                    self.log_test(f"Restriction: {restriction}", "WARNING", 
                                 f"Missing restriction: {restriction}")
                    
        except Exception as e:
            self.log_test("Terms of Use", "FAIL", f"Error testing terms of use: {e}")

    def test_page_functionality(self):
        """Test that the page can be rendered properly"""
        print("\n=== Testing Page Functionality ===")
        
        if not self.legal_page_path.exists():
            self.log_test("Page Functionality", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.legal_page_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for required JavaScript functionality
            js_elements = [
                "marked.parse",
                "fs.readFileSync",
                "path.join",
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

    def test_accessibility(self):
        """Test accessibility features"""
        print("\n=== Testing Accessibility ===")
        
        if not self.legal_page_path.exists():
            self.log_test("Accessibility", "FAIL", "Cannot test - file missing")
            return
            
        try:
            with open(self.legal_page_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Test for semantic HTML
            semantic_elements = [
                "<header>",
                "<main>",
                "<nav>",
                "<aside>",
                "<footer>"
            ]
            
            for element in semantic_elements:
                if element in content:
                    self.log_test(f"Semantic HTML: {element}", "PASS", 
                                 f"Found semantic element: {element}")
                else:
                    self.log_test(f"Semantic HTML: {element}", "WARNING", 
                                 f"Missing semantic element: {element}")
                    
            # Test for ARIA labels
            if "aria-label" in content or "role=" in content:
                self.log_test("ARIA Labels", "PASS", "ARIA labels found")
            else:
                self.log_test("ARIA Labels", "WARNING", "ARIA labels missing")
                
            # Test for proper heading structure
            if "<h1>" in content and "<h2>" in content and "<h3>" in content:
                self.log_test("Heading Structure", "PASS", "Proper heading structure found")
            else:
                self.log_test("Heading Structure", "WARNING", "Heading structure may be incomplete")
                
        except Exception as e:
            self.log_test("Accessibility", "FAIL", f"Error testing accessibility: {e}")

    def run_all_tests(self):
        """Run all tests for Batch 197"""
        print("=" * 60)
        print("BATCH 197 - LEGAL + COMPLIANCE NOTICES PAGE TEST")
        print("=" * 60)
        print(f"Testing: {self.test_results['feature']}")
        print(f"Timestamp: {self.test_results['timestamp']}")
        print("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_file_existence,
            self.test_legal_page_structure,
            self.test_legal_notices_content,
            self.test_dmca_compliance,
            self.test_swg_restoration_rules,
            self.test_mod_compliance_guidelines,
            self.test_terms_of_use,
            self.test_page_functionality,
            self.test_accessibility
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
            print("\n✅ BATCH 197 IMPLEMENTATION: SUCCESS")
            print("All required features for Legal + Compliance Notices Page are implemented.")
        elif summary['failed'] > 0:
            print("\n❌ BATCH 197 IMPLEMENTATION: FAILED")
            print("Some required features are missing or incomplete.")
        else:
            print("\n⚠️ BATCH 197 IMPLEMENTATION: PARTIAL")
            print("Implementation has warnings but no critical failures.")
            
        # Save test results
        self.save_test_results()

    def save_test_results(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"BATCH_197_TEST_REPORT_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"\nTest results saved to: {filename}")
        except Exception as e:
            print(f"\nError saving test results: {e}")

def main():
    """Main test execution"""
    tester = LegalPageTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 
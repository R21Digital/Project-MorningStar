#!/usr/bin/env python3
"""
Batch 185 - Bug Report Collector Verification
Verifies the implementation of the public bug report collector
"""

import json
import os
import requests
import sys
from datetime import datetime
from typing import Dict, List, Any

class Batch185Verifier:
    def __init__(self):
        self.results = {
            "batch": "185",
            "title": "Public Bug Report Collector",
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "overall_status": "PENDING"
        }
        
        # Configuration
        self.base_url = "http://localhost:5001"  # API base URL
        self.data_file = "data/bug_reports.json"
        self.api_key = "demo-key"  # Default API key for testing
        
    def verify_bug_reports_data_file(self) -> Dict[str, Any]:
        """Verify the bug reports data file exists and has correct structure"""
        print("🔍 Verifying bug reports data file...")
        
        try:
            if not os.path.exists(self.data_file):
                return {
                    "status": "FAIL",
                    "error": f"Data file not found: {self.data_file}"
                }
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check required structure
            required_keys = ['bug_reports', 'metadata', 'schema']
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                return {
                    "status": "FAIL",
                    "error": f"Missing required keys: {missing_keys}"
                }
            
            # Check schema structure
            schema = data.get('schema', {}).get('bug_report', {})
            required_schema_fields = ['id', 'title', 'description', 'priority', 'category']
            missing_schema_fields = [field for field in required_schema_fields if field not in schema]
            
            if missing_schema_fields:
                return {
                    "status": "FAIL",
                    "error": f"Missing schema fields: {missing_schema_fields}"
                }
            
            return {
                "status": "PASS",
                "details": {
                    "file_exists": True,
                    "structure_valid": True,
                    "schema_valid": True,
                    "report_count": len(data.get('bug_reports', []))
                }
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": f"Error reading data file: {str(e)}"
            }
    
    def verify_bug_report_page(self) -> Dict[str, Any]:
        """Verify the bug report page exists and has required elements"""
        print("🔍 Verifying bug report page...")
        
        page_file = "swgdb_site/pages/report-bug.html"
        
        try:
            if not os.path.exists(page_file):
                return {
                    "status": "FAIL",
                    "error": f"Bug report page not found: {page_file}"
                }
            
            with open(page_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required form elements
            required_elements = {
                "form_exists": '<form id="bug-report-form"' in content,
                "title_field": 'name="title"' in content,
                "description_field": 'name="description"' in content,
                "priority_field": 'name="priority"' in content,
                "category_field": 'name="category"' in content,
                "screenshot_field": 'name="screenshot"' in content,
                "submit_button": 'Submit Bug Report' in content,
                "reset_button": 'Reset Form' in content
            }
            
            missing_elements = [key for key, value in required_elements.items() if not value]
            
            if missing_elements:
                return {
                    "status": "FAIL",
                    "error": f"Missing form elements: {missing_elements}"
                }
            
            # Check for JavaScript functions
            required_functions = [
                'submitBugReport',
                'handleFileChange',
                'resetForm',
                'showSuccessMessage',
                'showErrorMessage'
            ]
            
            missing_functions = [func for func in required_functions if func not in content]
            
            if missing_functions:
                return {
                    "status": "FAIL",
                    "error": f"Missing JavaScript functions: {missing_functions}"
                }
            
            return {
                "status": "PASS",
                "details": {
                    "page_exists": True,
                    "form_elements": required_elements,
                    "javascript_functions": {func: func in content for func in required_functions}
                }
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": f"Error reading page file: {str(e)}"
            }
    
    def verify_bug_report_api(self) -> Dict[str, Any]:
        """Verify the bug report API endpoints"""
        print("🔍 Verifying bug report API...")
        
        api_file = "api/bug_report_api.py"
        
        try:
            if not os.path.exists(api_file):
                return {
                    "status": "FAIL",
                    "error": f"API file not found: {api_file}"
                }
            
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required API endpoints
            required_endpoints = [
                '/api/bug-report',
                '/api/bug-reports',
                '/api/bug-report/<bug_id>',
                '/api/bug-report/stats',
                '/api/health'
            ]
            
            missing_endpoints = [endpoint for endpoint in required_endpoints if endpoint not in content]
            
            if missing_endpoints:
                return {
                    "status": "FAIL",
                    "error": f"Missing API endpoints: {missing_endpoints}"
                }
            
            # Check for required functions
            required_functions = [
                'load_bug_reports',
                'save_bug_reports',
                'validate_bug_report',
                'submit_bug_report',
                'get_bug_reports'
            ]
            
            missing_functions = [func for func in required_functions if func not in content]
            
            if missing_functions:
                return {
                    "status": "FAIL",
                    "error": f"Missing API functions: {missing_functions}"
                }
            
            return {
                "status": "PASS",
                "details": {
                    "api_file_exists": True,
                    "endpoints": {endpoint: endpoint in content for endpoint in required_endpoints},
                    "functions": {func: func in content for func in required_functions}
                }
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": f"Error reading API file: {str(e)}"
            }
    
    def verify_bug_report_component(self) -> Dict[str, Any]:
        """Verify the React component exists"""
        print("🔍 Verifying bug report component...")
        
        component_file = "website/components/BugReportForm.tsx"
        
        try:
            if not os.path.exists(component_file):
                return {
                    "status": "FAIL",
                    "error": f"Component file not found: {component_file}"
                }
            
            with open(component_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required TypeScript interfaces
            required_interfaces = [
                'BugReport',
                'BugReportFormProps'
            ]
            
            missing_interfaces = [interface for interface in required_interfaces if interface not in content]
            
            if missing_interfaces:
                return {
                    "status": "FAIL",
                    "error": f"Missing TypeScript interfaces: {missing_interfaces}"
                }
            
            # Check for required form fields
            required_fields = [
                'title',
                'description',
                'priority',
                'category',
                'screenshot'
            ]
            
            missing_fields = [field for field in required_fields if field not in content]
            
            if missing_fields:
                return {
                    "status": "FAIL",
                    "error": f"Missing form fields: {missing_fields}"
                }
            
            return {
                "status": "PASS",
                "details": {
                    "component_exists": True,
                    "interfaces": {interface: interface in content for interface in required_interfaces},
                    "form_fields": {field: field in content for field in required_fields}
                }
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": f"Error reading component file: {str(e)}"
            }
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test the API endpoints if server is running"""
        print("🔍 Testing API endpoints...")
        
        try:
            # Test health endpoint
            health_response = requests.get(f"{self.base_url}/api/health", timeout=5)
            
            if health_response.status_code != 200:
                return {
                    "status": "SKIP",
                    "message": "API server not running or health check failed"
                }
            
            # Test bug report submission
            test_bug_report = {
                "title": "Test Bug Report",
                "description": "This is a test bug report for verification",
                "priority": "Medium",
                "category": "Website",
                "user_agent": "Test User Agent",
                "page_url": "http://localhost/report-bug"
            }
            
            submit_response = requests.post(
                f"{self.base_url}/api/bug-report",
                json=test_bug_report,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if submit_response.status_code != 201:
                return {
                    "status": "FAIL",
                    "error": f"Bug report submission failed: {submit_response.status_code}"
                }
            
            # Test getting bug reports
            reports_response = requests.get(
                f"{self.base_url}/api/bug-reports",
                headers={'X-API-Key': self.api_key},
                timeout=10
            )
            
            if reports_response.status_code != 200:
                return {
                    "status": "FAIL",
                    "error": f"Getting bug reports failed: {reports_response.status_code}"
                }
            
            # Test stats endpoint
            stats_response = requests.get(
                f"{self.base_url}/api/bug-report/stats",
                headers={'X-API-Key': self.api_key},
                timeout=10
            )
            
            if stats_response.status_code != 200:
                return {
                    "status": "FAIL",
                    "error": f"Stats endpoint failed: {stats_response.status_code}"
                }
            
            return {
                "status": "PASS",
                "details": {
                    "health_check": health_response.status_code == 200,
                    "submit_bug_report": submit_response.status_code == 201,
                    "get_bug_reports": reports_response.status_code == 200,
                    "get_stats": stats_response.status_code == 200
                }
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "status": "SKIP",
                "message": "API server not running (connection refused)"
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "error": f"API testing error: {str(e)}"
            }
    
    def run_verification(self) -> Dict[str, Any]:
        """Run all verification checks"""
        print("🚀 Starting Batch 185 verification...")
        print("=" * 50)
        
        # Run all verification checks
        self.results["components"] = {
            "bug_reports_data_file": self.verify_bug_reports_data_file(),
            "bug_report_page": self.verify_bug_report_page(),
            "bug_report_api": self.verify_bug_report_api(),
            "bug_report_component": self.verify_bug_report_component(),
            "api_endpoints": self.test_api_endpoints()
        }
        
        # Determine overall status
        failed_components = [
            name for name, result in self.results["components"].items()
            if result["status"] == "FAIL"
        ]
        
        if failed_components:
            self.results["overall_status"] = "FAIL"
            self.results["failed_components"] = failed_components
        else:
            self.results["overall_status"] = "PASS"
        
        return self.results
    
    def print_results(self):
        """Print verification results"""
        print("\n" + "=" * 50)
        print(f"📊 BATCH 185 VERIFICATION RESULTS")
        print("=" * 50)
        
        print(f"Overall Status: {'✅ PASS' if self.results['overall_status'] == 'PASS' else '❌ FAIL'}")
        print(f"Timestamp: {self.results['timestamp']}")
        print()
        
        for component_name, result in self.results["components"].items():
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {component_name.replace('_', ' ').title()}: {result['status']}")
            
            if result["status"] == "FAIL":
                print(f"   Error: {result['error']}")
            elif result["status"] == "SKIP":
                print(f"   Message: {result['message']}")
            elif "details" in result:
                print(f"   Details: {len(result['details'])} checks passed")
        
        print("\n" + "=" * 50)
        
        if self.results["overall_status"] == "PASS":
            print("🎉 All components verified successfully!")
        else:
            print("⚠️  Some components need attention.")
        
        return self.results["overall_status"] == "PASS"

def main():
    """Main verification function"""
    verifier = Batch185Verifier()
    results = verifier.run_verification()
    success = verifier.print_results()
    
    # Save results to file
    output_file = f"BATCH_185_VERIFICATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Results saved to: {output_file}")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 
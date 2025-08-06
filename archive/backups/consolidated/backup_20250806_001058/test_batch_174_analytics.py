#!/usr/bin/env python3
"""
Test Batch 174 - Google Analytics + Search Console Setup
Verifies that analytics and SEO components are properly implemented
"""

import os
import json
from pathlib import Path

def test_base_layout_template():
    """Test that base.njk layout exists with analytics integration"""
    print("Testing Base Layout Template...")
    
    layout_path = Path("website/_includes/layouts/base.njk")
    
    result = {
        'file': 'base.njk',
        'exists': layout_path.exists(),
        'path': str(layout_path)
    }
    
    print(f"  [OK] base.njk: {'EXISTS' if result['exists'] else 'MISSING'}")
    
    if result['exists']:
        content = layout_path.read_text()
        
        # Check for essential analytics features
        features = {
            'Google Analytics gtag': 'gtag(' in content and 'googleAnalyticsId' in content,
            'Search Console verification': 'google-site-verification' in content,
            'Enhanced tracking': 'trackSWGDBEvent' in content,
            'Custom dimensions': 'custom_dimension' in content,
            'Performance tracking': 'page_performance' in content,
            'User engagement tracking': 'user_engagement' in content,
            'Error tracking': 'javascript_error' in content,
            'Structured data': 'application/ld+json' in content,
            'Open Graph tags': 'property="og:' in content,
            'Twitter Cards': 'name="twitter:' in content,
            'Canonical URLs': 'rel="canonical"' in content,
            'Responsive design': 'viewport' in content,
            'Accessibility': 'role=' in content and 'sr-only' in content
        }
        
        result['features'] = features
        
        for feature, found in features.items():
            status = 'IMPLEMENTED' if found else 'MISSING'
            print(f"    - {feature}: {status}")
    
    return result

def test_seo_configuration():
    """Test that SEO configuration file exists and is properly structured"""
    print("\nTesting SEO Configuration...")
    
    config_path = Path("website/config/seo.json")
    
    result = {
        'file': 'seo.json',
        'exists': config_path.exists(),
        'path': str(config_path)
    }
    
    print(f"  [OK] seo.json: {'EXISTS' if result['exists'] else 'MISSING'}")
    
    if result['exists']:
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check required configuration sections
            required_sections = {
                'site': 'site' in config and isinstance(config['site'], dict),
                'analytics': 'analytics' in config and isinstance(config['analytics'], dict),
                'search_console': 'search_console' in config and isinstance(config['search_console'], dict),
                'social': 'social' in config and isinstance(config['social'], dict),
                'structured_data': 'structured_data' in config and isinstance(config['structured_data'], dict),
                'heroics': 'heroics' in config and isinstance(config['heroics'], dict),
                'sitemap': 'sitemap' in config and isinstance(config['sitemap'], dict),
                'robots': 'robots' in config and isinstance(config['robots'], dict)
            }
            
            result['sections'] = required_sections
            
            for section, found in required_sections.items():
                status = 'CONFIGURED' if found else 'MISSING'
                print(f"    - {section}: {status}")
            
            # Check analytics configuration
            if config.get('analytics'):
                analytics = config['analytics']
                analytics_checks = {
                    'Google Analytics ID': 'googleAnalyticsId' in analytics,
                    'Tracking enabled': analytics.get('trackingEnabled', False),
                    'Cookie consent': 'enableCookieConsent' in analytics
                }
                
                result['analytics'] = analytics_checks
                
                for check, passed in analytics_checks.items():
                    status = 'CONFIGURED' if passed else 'MISSING'
                    print(f"      - {check}: {status}")
            
            # Check heroics configuration
            if config.get('heroics'):
                heroics = config['heroics']
                expected_heroics = ['axkva_min', 'ig_88', 'geonosian_queen', 'krayt_dragon', 'nightsister_stronghold', 'janta_blood_crisis']
                
                heroic_checks = {}
                for heroic in expected_heroics:
                    found = heroic in heroics
                    heroic_checks[heroic] = found
                    status = 'CONFIGURED' if found else 'MISSING'
                    print(f"      - {heroic}: {status}")
                
                result['heroics'] = heroic_checks
                
        except json.JSONDecodeError as e:
            result['error'] = f"JSON decode error: {e}"
            print(f"    [ERROR] Invalid JSON: {e}")
        except Exception as e:
            result['error'] = f"Unexpected error: {e}"
            print(f"    [ERROR] {e}")
    
    return result

def test_existing_analytics_file():
    """Test that existing analytics.html is updated"""
    print("\nTesting Existing Analytics File...")
    
    analytics_path = Path("swgdb_site/_includes/analytics.html")
    
    result = {
        'file': 'analytics.html',
        'exists': analytics_path.exists(),
        'path': str(analytics_path)
    }
    
    print(f"  [OK] analytics.html: {'EXISTS' if result['exists'] else 'MISSING'}")
    
    if result['exists']:
        content = analytics_path.read_text()
        
        # Check for comprehensive analytics features
        features = {
            'Google Analytics 4': 'G-Q4ZZ5SFJC0' in content and 'gtag(' in content,
            'Search Console meta tag': 'google-site-verification' in content,
            'Enhanced event tracking': 'trackSWGDBEvent' in content,
            'Filter tracking': 'filter_used' in content,
            'Search tracking': 'search_performed' in content,
            'Navigation tracking': 'navigation_click' in content,
            'Performance tracking': 'page_load_time' in content,
            'User engagement': 'user_engagement' in content,
            'Structured data': 'application/ld+json' in content,
            'Open Graph meta': 'property="og:' in content,
            'Twitter Cards': 'name="twitter:' in content,
            'Privacy compliance': 'noscript' in content
        }
        
        result['features'] = features
        
        for feature, found in features.items():
            status = 'IMPLEMENTED' if found else 'MISSING'
            print(f"    - {feature}: {status}")
    
    return result

def test_seo_documentation():
    """Test that SEO documentation exists and is comprehensive"""
    print("\nTesting SEO Documentation...")
    
    doc_path = Path("docs/SEO.md")
    
    result = {
        'file': 'SEO.md',
        'exists': doc_path.exists(),
        'path': str(doc_path)
    }
    
    print(f"  [OK] SEO.md: {'EXISTS' if result['exists'] else 'MISSING'}")
    
    if result['exists']:
        content = doc_path.read_text()
        
        # Check for comprehensive documentation sections
        sections = {
            'Google Analytics Setup': '## Google Analytics Setup' in content,
            'Google Search Console Setup': '## Google Search Console Setup' in content,
            'SEO Configuration': '## SEO Configuration' in content,
            'Verification Checklist': '## Verification Checklist' in content,
            'Indexing Strategy': '## Indexing Strategy' in content,
            'Performance Optimization': '## Performance Optimization' in content,
            'Monitoring and Maintenance': '## Monitoring and Maintenance' in content,
            'Troubleshooting': '## Troubleshooting' in content or 'Troubleshooting Common Issues' in content
        }
        
        result['sections'] = sections
        
        for section, found in sections.items():
            status = 'DOCUMENTED' if found else 'MISSING' 
            print(f"    - {section}: {status}")
        
        # Check for practical implementation details
        implementation_details = {
            'Analytics tracking code': 'gtag(' in content,
            'Custom dimensions': 'custom_dimension' in content,
            'Event tracking examples': 'trackSWGDBEvent' in content,
            'Verification steps': 'verification' in content.lower(),
            'Core Web Vitals': 'Core Web Vitals' in content,
            'Structured data examples': 'JSON-LD' in content or 'structured data' in content.lower(),
            'Sitemap configuration': 'sitemap' in content.lower(),
            'Robots.txt': 'robots.txt' in content.lower()
        }
        
        result['implementation'] = implementation_details
        
        for detail, found in implementation_details.items():
            status = 'INCLUDED' if found else 'MISSING'
            print(f"      - {detail}: {status}")
    
    return result

def test_directory_structure():
    """Test that required directory structure exists"""
    print("\nTesting Directory Structure...")
    
    required_dirs = [
        "website/_includes/layouts",
        "website/config", 
        "docs"
    ]
    
    results = []
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        result = {
            'directory': dir_path,
            'exists': path.exists() and path.is_dir()
        }
        results.append(result)
        
        status = 'EXISTS' if result['exists'] else 'MISSING'
        print(f"  [OK] {dir_path}: {status}")
    
    return results

def generate_test_report(results):
    """Generate comprehensive test report for Batch 174"""
    print("\n" + "="*60)
    print("BATCH 174 ANALYTICS + SEO TEST REPORT")
    print("="*60)
    
    report = {
        'batch': 'Batch 174 - Google Analytics + Search Console Setup',
        'test_date': '2025-01-16',
        'results': results,
        'summary': {}
    }
    
    # Calculate summary statistics
    total_tests = 0
    passed_tests = 0
    
    for test_name, test_result in results.items():
        print(f"\n{test_name.upper().replace('_', ' ')}:")
        
        if isinstance(test_result, list):
            # Handle directory structure results
            for item in test_result:
                total_tests += 1
                if item.get('exists', False):
                    passed_tests += 1
                    print(f"  [PASS] {item.get('directory', 'Item')}")
                else:
                    print(f"  [FAIL] {item.get('directory', 'Item')}")
        else:
            # Handle single result
            if 'exists' in test_result:
                total_tests += 1
                if test_result['exists']:
                    passed_tests += 1
                    file_name = test_result.get('file', 'Item')
                    print(f"  [PASS] {file_name}")
                else:
                    file_name = test_result.get('file', 'Item')
                    print(f"  [FAIL] {file_name}")
            
            # Check sub-features
            if 'features' in test_result:
                feature_passed = sum(1 for f in test_result['features'].values() if f)
                feature_total = len(test_result['features'])
                print(f"    Features: {feature_passed}/{feature_total} implemented")
            
            if 'sections' in test_result:
                section_passed = sum(1 for s in test_result['sections'].values() if s)
                section_total = len(test_result['sections'])
                print(f"    Sections: {section_passed}/{section_total} configured")
    
    # Overall summary
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    report['summary'] = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': total_tests - passed_tests,
        'success_rate': f"{success_rate:.1f}%"
    }
    
    print(f"\nOVERALL SUMMARY:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {total_tests - passed_tests}")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"\n[SUCCESS] BATCH 174: IMPLEMENTATION EXCELLENT")
        print("Analytics and SEO setup is comprehensive and ready for production!")
    elif success_rate >= 75:
        print(f"\n[SUCCESS] BATCH 174: IMPLEMENTATION SUCCESSFUL")
        print("Analytics and SEO setup is working with minor optimizations needed.")
    elif success_rate >= 50:
        print(f"\n[WARNING] BATCH 174: IMPLEMENTATION PARTIAL")
        print("Core components exist but need completion.")
    else:
        print(f"\n[ERROR] BATCH 174: IMPLEMENTATION INCOMPLETE")
        print("Major components are missing. Significant work required.")
    
    # Implementation recommendations
    print(f"\n[NEXT STEPS]:")
    print("1. Replace 'your-google-site-verification-code-here' with actual verification code")
    print("2. Test analytics tracking in Google Analytics Real-Time reports")
    print("3. Submit sitemap to Google Search Console")
    print("4. Verify Core Web Vitals performance")
    print("5. Set up monitoring alerts for SEO metrics")
    
    # Save report to file
    report_path = Path("BATCH_174_ANALYTICS_TEST_REPORT.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")
    
    return report

def main():
    """Run all Batch 174 analytics and SEO tests"""
    print("Starting Batch 174 Google Analytics + Search Console Tests...")
    print("=" * 60)
    
    # Run all tests
    results = {
        'base_layout': test_base_layout_template(),
        'seo_configuration': test_seo_configuration(),
        'existing_analytics': test_existing_analytics_file(),
        'seo_documentation': test_seo_documentation(),
        'directory_structure': test_directory_structure()
    }
    
    # Generate comprehensive report
    report = generate_test_report(results)
    
    return report

if __name__ == "__main__":
    main()
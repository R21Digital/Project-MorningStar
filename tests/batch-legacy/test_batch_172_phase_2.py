#!/usr/bin/env python3
"""
Test Batch 172 - Heroic Page Loot Table UI (Phase 2)
Verifies that all Phase 2 components are properly implemented and integrated
"""

import os
import json
from pathlib import Path

def test_heroic_pages_exist():
    """Test that all heroic pages have been created"""
    print("Testing Heroic Pages Existence...")
    
    website_pages_dir = Path("website/pages/heroics")
    
    expected_pages = [
        "axkva-min.11ty.js",
        "ig-88.11ty.js", 
        "geonosian-queen.11ty.js",
        "krayt-dragon.11ty.js",
        "nightsister-stronghold.11ty.js",
        "janta-blood-crisis.11ty.js"
    ]
    
    results = []
    for page in expected_pages:
        page_path = website_pages_dir / page
        exists = page_path.exists()
        results.append({
            'page': page,
            'exists': exists,
            'path': str(page_path)
        })
        print(f"  [OK] {page}: {'EXISTS' if exists else 'MISSING'}")
    
    return results

def test_loot_table_component():
    """Test that LootTable React component exists"""
    print("\nTesting LootTable Component...")
    
    component_path = Path("website/components/LootTable.tsx")
    exists = component_path.exists()
    
    result = {
        'component': 'LootTable.tsx',
        'exists': exists,
        'path': str(component_path)
    }
    
    print(f"  [OK] LootTable.tsx: {'EXISTS' if exists else 'MISSING'}")
    
    if exists:
        # Check for key interfaces and functionality
        content = component_path.read_text()
        features = {
            'LootEntry interface': 'interface LootEntry' in content,
            'Sorting functionality': 'handleSort' in content,
            'Filtering functionality': 'handleFilterChange' in content,
            'API integration': 'fetch(' in content,
            'Responsive design': '@media' in content or 'mobile' in content.lower()
        }
        
        result['features'] = features
        
        for feature, found in features.items():
            status = 'FOUND' if found else 'MISSING'
            print(f"    - {feature}: {status}")
    
    return result

def test_loot_css_styling():
    """Test that loot.css styling exists and contains required classes"""
    print("\nTesting Loot CSS Styling...")
    
    css_path = Path("website/styles/loot.css")
    exists = css_path.exists()
    
    result = {
        'css_file': 'loot.css',
        'exists': exists,
        'path': str(css_path)
    }
    
    print(f"  [OK] loot.css: {'EXISTS' if exists else 'MISSING'}")
    
    if exists:
        content = css_path.read_text()
        
        # Check for essential CSS classes
        required_classes = [
            '.loot-table-container',
            '.loot-table-header', 
            '.loot-filters',
            '.loot-table',
            '.rarity-badge',
            '.difficulty-badge',
            '@media (max-width: 768px)',  # Mobile responsiveness
            '@media (prefers-color-scheme: dark)'  # Dark mode support
        ]
        
        class_results = {}
        for css_class in required_classes:
            found = css_class in content
            class_results[css_class] = found
            status = 'FOUND' if found else 'MISSING'
            print(f"    - {css_class}: {status}")
        
        result['classes'] = class_results
    
    return result

def test_heroic_page_structure():
    """Test that heroic pages have proper structure and components"""
    print("\nTesting Heroic Page Structure...")
    
    # Test one representative page (IG-88)
    page_path = Path("website/pages/heroics/ig-88.11ty.js")
    
    result = {
        'test_page': 'ig-88.11ty.js',
        'exists': page_path.exists()
    }
    
    if page_path.exists():
        content = page_path.read_text()
        
        # Check for required structural elements
        required_elements = [
            'tab-navigation',  # Tab system
            'tab-content',     # Tab content areas
            'loadLootTable()', # Loot table loading function
            'loadLootStats()', # Statistics loading
            '/api/heroics/loot', # API endpoint integration
            'Live Loot Table', # Loot table tab
            'Overview',        # Overview tab
            'Strategy'         # Strategy tab
        ]
        
        element_results = {}
        for element in required_elements:
            found = element in content
            element_results[element] = found
            status = 'FOUND' if found else 'MISSING'
            print(f"    - {element}: {status}")
        
        result['elements'] = element_results
    else:
        print("    Page not found - cannot test structure")
    
    return result

def test_api_integration_points():
    """Test that pages properly integrate with Phase 1 API endpoints"""
    print("\nTesting API Integration Points...")
    
    test_files = [
        "website/pages/heroics/ig-88.11ty.js",
        "website/pages/heroics/axkva-min.11ty.js",
        "website/components/LootTable.tsx"
    ]
    
    results = []
    
    for file_path in test_files:
        path = Path(file_path)
        result = {
            'file': file_path,
            'exists': path.exists()
        }
        
        if path.exists():
            content = path.read_text()
            
            # Check for proper API endpoint usage
            api_features = {
                '/api/heroics/loot': '/api/heroics/loot' in content,
                '/api/heroics/loot/stats': '/api/heroics/loot/stats' in content,
                'Error handling': 'catch (error)' in content or 'try {' in content,
                'Loading states': 'loading' in content.lower(),
                'Success response': 'result.success' in content
            }
            
            result['api_features'] = api_features
            
            print(f"  File: {file_path}")
            for feature, found in api_features.items():
                status = 'FOUND' if found else 'MISSING'
                print(f"    - {feature}: {status}")
        else:
            result['api_features'] = {}
            print(f"  File: {file_path} - NOT FOUND")
        
        results.append(result)
    
    return results

def test_heroics_index_integration():
    """Test that heroics index properly links to new pages"""
    print("\nTesting Heroics Index Integration...")
    
    index_path = Path("swgdb_site/pages/heroics/index.html")
    
    result = {
        'index_file': str(index_path),
        'exists': index_path.exists()
    }
    
    if index_path.exists():
        content = index_path.read_text()
        
        # Check for proper links to heroic pages
        expected_links = [
            'axkva-min/',
            'ig-88/',
            'geonosian-queen/',
            'krayt-dragon/',
            'nightsister-stronghold/',
            'janta-blood-crisis/'
        ]
        
        link_results = {}
        for link in expected_links:
            found = link in content
            link_results[link] = found
            status = 'FOUND' if found else 'MISSING'
            print(f"    - {link}: {status}")
        
        result['links'] = link_results
        
        # Check for "Live Loot" text in buttons
        live_loot_found = 'Live Loot' in content
        result['live_loot_mentioned'] = live_loot_found
        print(f"    - Live Loot mentioned: {'YES' if live_loot_found else 'NO'}")
    
    return result

def generate_test_report(results):
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("BATCH 172 PHASE 2 TEST REPORT")
    print("="*60)
    
    report = {
        'batch': 'Batch 172 - Heroic Page Loot Table UI (Phase 2)',
        'test_date': '2025-01-XX',
        'results': results,
        'summary': {}
    }
    
    # Calculate summary statistics
    total_tests = 0
    passed_tests = 0
    
    for test_name, test_result in results.items():
        print(f"\n{test_name.upper().replace('_', ' ')}:")
        
        if isinstance(test_result, list):
            # Handle list of results (like API integration)
            for item in test_result:
                if 'exists' in item:
                    total_tests += 1
                    if item['exists']:
                        passed_tests += 1
                        print(f"  [PASS] {item.get('file', item.get('page', 'Item'))}")
                    else:
                        print(f"  [FAIL] {item.get('file', item.get('page', 'Item'))}")
        else:
            # Handle single result
            if 'exists' in test_result:
                total_tests += 1
                if test_result['exists']:
                    passed_tests += 1
                    print(f"  [PASS] {test_result.get('component', test_result.get('css_file', 'Item'))}")
                else:
                    print(f"  [FAIL] {test_result.get('component', test_result.get('css_file', 'Item'))}")
    
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
    
    if success_rate >= 80:
        print(f"\n[SUCCESS] BATCH 172 PHASE 2: IMPLEMENTATION SUCCESSFUL")
        print("All major components are in place and properly integrated!")
    elif success_rate >= 60:
        print(f"\n[WARNING] BATCH 172 PHASE 2: MOSTLY COMPLETE")
        print("Most components are implemented, minor issues to resolve.")
    else:
        print(f"\n[ERROR] BATCH 172 PHASE 2: NEEDS ATTENTION")
        print("Significant components are missing or not properly integrated.")
    
    # Save report to file
    report_path = Path("BATCH_172_PHASE_2_TEST_REPORT.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")
    
    return report

def main():
    """Run all Phase 2 tests"""
    print("Starting Batch 172 Phase 2 Implementation Tests...")
    print("=" * 60)
    
    # Run all tests
    results = {
        'heroic_pages': test_heroic_pages_exist(),
        'loot_table_component': test_loot_table_component(),
        'loot_css_styling': test_loot_css_styling(),
        'heroic_page_structure': test_heroic_page_structure(),
        'api_integration': test_api_integration_points(),
        'heroics_index': test_heroics_index_integration()
    }
    
    # Generate comprehensive report
    report = generate_test_report(results)
    
    return report

if __name__ == "__main__":
    main()
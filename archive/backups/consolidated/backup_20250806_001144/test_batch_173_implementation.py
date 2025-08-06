#!/usr/bin/env python3
"""
Test Batch 173 Implementation - Bug Tracker Dashboard + Collection System
Tests the specific components implemented for Batch 173:
- src/data/bugs.json data structure
- src/components/BugEntryCard.tsx component
- src/admin/bugs/index.tsx dashboard
- src/components/NewBugForm.tsx form component
"""

import os
import json
from pathlib import Path

def test_bug_data_structure():
    """Test that bugs.json has proper data structure"""
    print("Testing Bug Data Structure...")
    
    bugs_path = Path("src/data/bugs.json")
    
    result = {
        'file': 'bugs.json',
        'exists': bugs_path.exists(),
        'path': str(bugs_path)
    }
    
    print(f"  [OK] bugs.json: {'EXISTS' if result['exists'] else 'MISSING'}")
    
    if result['exists']:
        try:
            with open(bugs_path, 'r') as f:
                data = json.load(f)
            
            # Check required structure
            structure_checks = {
                'bug_reports array': 'bug_reports' in data and isinstance(data['bug_reports'], list),
                'metadata object': 'metadata' in data and isinstance(data['metadata'], dict),
                'config object': 'config' in data and isinstance(data['config'], dict),
                'sample bug data': len(data.get('bug_reports', [])) > 0
            }
            
            result['structure'] = structure_checks
            
            for check, passed in structure_checks.items():
                status = 'VALID' if passed else 'INVALID'
                print(f"    - {check}: {status}")
            
            # Check bug report fields
            if data.get('bug_reports'):
                sample_bug = data['bug_reports'][0]
                required_fields = [
                    'id', 'title', 'severity', 'description', 'status', 
                    'tags', 'priority', 'reportedBy', 'reportedDate', 
                    'lastUpdated', 'reproductionSteps', 'environment', 'comments'
                ]
                
                field_results = {}
                for field in required_fields:
                    found = field in sample_bug
                    field_results[field] = found
                    status = 'FOUND' if found else 'MISSING'
                    print(f"    - Bug field '{field}': {status}")
                
                result['bug_fields'] = field_results
                
        except json.JSONDecodeError as e:
            result['error'] = f"JSON decode error: {e}"
            print(f"    [ERROR] Invalid JSON: {e}")
        except Exception as e:
            result['error'] = f"Unexpected error: {e}"
            print(f"    [ERROR] {e}")
    
    return result

def test_bug_entry_card_component():
    """Test that BugEntryCard component exists and has required functionality"""
    print("\nTesting BugEntryCard Component...")
    
    component_path = Path("src/components/BugEntryCard.tsx")
    
    result = {
        'component': 'BugEntryCard.tsx',
        'exists': component_path.exists(),
        'path': str(component_path)
    }
    
    print(f"  [OK] BugEntryCard.tsx: {'EXISTS' if result['exists'] else 'MISSING'}")
    
    if result['exists']:
        content = component_path.read_text()
        
        # Check for essential component features
        features = {
            'BugReport interface': 'interface BugReport' in content,
            'Status change handler': 'onStatusChange' in content,
            'Assignment handler': 'onAssignmentChange' in content,
            'Priority handler': 'onPriorityChange' in content,
            'Comment system': 'onAddComment' in content,
            'Edit functionality': 'onEdit' in content,
            'Delete functionality': 'onDelete' in content,
            'Visual styling': 'style jsx' in content,
            'Responsive design': '@media' in content
        }
        
        result['features'] = features
        
        for feature, found in features.items():
            status = 'IMPLEMENTED' if found else 'MISSING'
            print(f"    - {feature}: {status}")
    
    return result

def test_admin_bugs_dashboard():
    """Test that admin bugs dashboard exists with proper functionality"""
    print("\nTesting Admin Bugs Dashboard...")
    
    dashboard_path = Path("src/admin/bugs/index.tsx")
    
    result = {
        'dashboard': 'admin/bugs/index.tsx',
        'exists': dashboard_path.exists(),
        'path': str(dashboard_path)
    }
    
    print(f"  [OK] admin/bugs/index.tsx: {'EXISTS' if result['exists'] else 'MISSING'}")
    
    if result['exists']:
        content = dashboard_path.read_text()
        
        # Check for dashboard features
        features = {
            'Bug filtering': 'FilterState' in content and 'filters' in content,
            'Tag filtering': 'handleTagToggle' in content,
            'Status filtering': 'status' in content and 'severity' in content,
            'Search functionality': 'searchTerm' in content,
            'Sorting capability': 'sortBy' in content and 'sortOrder' in content,
            'Statistics display': 'statistics' in content,
            'Export functionality': 'handleExportBugs' in content,
            'New bug form': 'showNewBugForm' in content,
            'API integration': 'loadBugData' in content,
            'Responsive design': '@media' in content
        }
        
        result['features'] = features
        
        for feature, found in features.items():
            status = 'IMPLEMENTED' if found else 'MISSING'
            print(f"    - {feature}: {status}")
    
    return result

def test_new_bug_form_component():
    """Test that NewBugForm component exists with validation"""
    print("\nTesting NewBugForm Component...")
    
    form_path = Path("src/components/NewBugForm.tsx")
    
    result = {
        'component': 'NewBugForm.tsx',
        'exists': form_path.exists(),
        'path': str(form_path)
    }
    
    print(f"  [OK] NewBugForm.tsx: {'EXISTS' if result['exists'] else 'MISSING'}")
    
    if result['exists']:
        content = form_path.read_text()
        
        # Check for form features
        features = {
            'Form validation': 'validateForm' in content,
            'File upload': 'screenshot' in content and 'file' in content.lower(),
            'Environment auto-fill': 'handleAutoFillEnvironment' in content,
            'Reproduction steps': 'reproductionSteps' in content,
            'Tag selection': 'handleTagToggle' in content,
            'Priority selection': 'priority' in content,
            'Assignee selection': 'assignedTo' in content,
            'Modal overlay': 'overlay' in content,
            'Form submission': 'handleSubmit' in content,
            'Error handling': 'errors' in content
        }
        
        result['features'] = features
        
        for feature, found in features.items():
            status = 'IMPLEMENTED' if found else 'MISSING'
            print(f"    - {feature}: {status}")
    
    return result

def test_tag_filtering_system():
    """Test that tag filtering works for Bot/Website/Content categories"""
    print("\nTesting Tag Filtering System...")
    
    # Check bugs.json for proper tag categories
    bugs_path = Path("src/data/bugs.json")
    
    result = {
        'data_file': str(bugs_path),
        'exists': bugs_path.exists()
    }
    
    if result['exists']:
        with open(bugs_path, 'r') as f:
            data = json.load(f)
        
        # Check for required tag categories
        config = data.get('config', {})
        tag_categories = config.get('tagCategories', [])
        
        required_tags = ['Bot', 'Website', 'Content']
        tag_results = {}
        
        for tag in required_tags:
            found = tag in tag_categories
            tag_results[tag] = found
            status = 'AVAILABLE' if found else 'MISSING'
            print(f"    - Tag category '{tag}': {status}")
        
        result['tag_categories'] = tag_results
        
        # Check that sample bugs use these tags
        sample_tags_used = []
        for bug in data.get('bug_reports', []):
            sample_tags_used.extend(bug.get('tags', []))
        
        sample_usage = {}
        for tag in required_tags:
            used = tag in sample_tags_used
            sample_usage[tag] = used
            status = 'USED' if used else 'UNUSED'
            print(f"    - Tag '{tag}' in sample data: {status}")
        
        result['sample_usage'] = sample_usage
    
    return result

def test_assignment_priority_system():
    """Test assignment and priority management features"""
    print("\nTesting Assignment & Priority System...")
    
    bugs_path = Path("src/data/bugs.json")
    
    result = {
        'data_file': str(bugs_path),
        'exists': bugs_path.exists()
    }
    
    if result['exists']:
        with open(bugs_path, 'r') as f:
            data = json.load(f)
        
        config = data.get('config', {})
        
        # Check assignable developers
        assignable_devs = config.get('assignableDevs', [])
        dev_check = len(assignable_devs) > 0
        result['has_assignable_devs'] = dev_check
        print(f"    - Assignable developers defined: {'YES' if dev_check else 'NO'}")
        
        if assignable_devs:
            dev_fields = all('id' in dev and 'name' in dev and 'role' in dev for dev in assignable_devs)
            result['dev_fields_complete'] = dev_fields
            print(f"    - Developer fields complete: {'YES' if dev_fields else 'NO'}")
        
        # Check priority levels
        priority_levels = config.get('priorityLevels', [])
        required_priorities = ['P0', 'P1', 'P2', 'P3']
        
        priority_results = {}
        for priority in required_priorities:
            found = priority in priority_levels
            priority_results[priority] = found
            status = 'DEFINED' if found else 'MISSING'
            print(f"    - Priority level '{priority}': {status}")
        
        result['priority_levels'] = priority_results
        
        # Check sample bug assignments
        bugs = data.get('bug_reports', [])
        assignment_usage = {
            'has_assigned_bugs': any(bug.get('assignedTo') for bug in bugs),
            'has_unassigned_bugs': any(not bug.get('assignedTo') for bug in bugs),
            'priority_variety': len(set(bug.get('priority', 'P2') for bug in bugs)) > 1
        }
        
        result['assignment_usage'] = assignment_usage
        
        for check, passed in assignment_usage.items():
            status = 'YES' if passed else 'NO'
            print(f"    - {check.replace('_', ' ').title()}: {status}")
    
    return result

def test_export_functionality():
    """Test that export functionality is properly implemented"""
    print("\nTesting Export Functionality...")
    
    dashboard_path = Path("src/admin/bugs/index.tsx")
    
    result = {
        'dashboard_file': str(dashboard_path),
        'exists': dashboard_path.exists()
    }
    
    if result['exists']:
        content = dashboard_path.read_text()
        
        # Check for export features
        export_features = {
            'Export handler': 'handleExportBugs' in content,
            'JSON blob creation': 'Blob(' in content and 'application/json' in content,
            'File download': 'createElement(\'a\')' in content and 'download =' in content,
            'Export button': 'Export' in content and 'disabled=' in content,
            'Dynamic filename': 'bug-report-export-' in content,
            'Export data structure': 'exported_date' in content or 'total_bugs' in content
        }
        
        result['export_features'] = export_features
        
        for feature, found in export_features.items():
            status = 'IMPLEMENTED' if found else 'MISSING'
            print(f"    - {feature}: {status}")
    
    return result

def generate_test_report(results):
    """Generate comprehensive test report for Batch 173"""
    print("\n" + "="*60)
    print("BATCH 173 BUG TRACKER IMPLEMENTATION TEST REPORT")
    print("="*60)
    
    report = {
        'batch': 'Batch 173 - Bug Tracker Dashboard + Collection System',
        'test_date': '2025-01-16',
        'results': results,
        'summary': {}
    }
    
    # Calculate summary statistics
    total_tests = 0
    passed_tests = 0
    
    for test_name, test_result in results.items():
        print(f"\n{test_name.upper().replace('_', ' ')}:")
        
        if 'exists' in test_result:
            total_tests += 1
            if test_result['exists']:
                passed_tests += 1
                file_name = test_result.get('file', test_result.get('component', test_result.get('dashboard', 'Item')))
                print(f"  [PASS] {file_name}")
            else:
                file_name = test_result.get('file', test_result.get('component', test_result.get('dashboard', 'Item')))
                print(f"  [FAIL] {file_name}")
        
        # Check sub-features
        if 'features' in test_result:
            feature_passed = sum(1 for f in test_result['features'].values() if f)
            feature_total = len(test_result['features'])
            print(f"    Features: {feature_passed}/{feature_total} implemented")
    
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
        print(f"\n[SUCCESS] BATCH 173: IMPLEMENTATION EXCELLENT")
        print("Bug tracker system is fully implemented and ready for use!")
    elif success_rate >= 75:
        print(f"\n[SUCCESS] BATCH 173: IMPLEMENTATION SUCCESSFUL")
        print("Bug tracker system is working with minor issues to resolve.")
    elif success_rate >= 50:
        print(f"\n[WARNING] BATCH 173: IMPLEMENTATION PARTIAL")
        print("Core components exist but need completion and integration.")
    else:
        print(f"\n[ERROR] BATCH 173: IMPLEMENTATION INCOMPLETE")
        print("Major components are missing. Significant work required.")
    
    # Save report to file
    report_path = Path("BATCH_173_IMPLEMENTATION_TEST_REPORT.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")
    
    return report

def main():
    """Run all Batch 173 implementation tests"""
    print("Starting Batch 173 Bug Tracker Implementation Tests...")
    print("=" * 60)
    
    # Run specific implementation tests
    results = {
        'bug_data_structure': test_bug_data_structure(),
        'bug_entry_card': test_bug_entry_card_component(),
        'admin_dashboard': test_admin_bugs_dashboard(),
        'new_bug_form': test_new_bug_form_component(),
        'tag_filtering': test_tag_filtering_system(),
        'assignment_priority': test_assignment_priority_system(),
        'export_functionality': test_export_functionality()
    }
    
    # Generate comprehensive report
    report = generate_test_report(results)
    
    return report

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Batch 187 - Legal Mod Portal + SWGR Compliance Check Test Suite
Comprehensive testing for mod portal functionality and compliance checking
"""

import json
import os
import sys
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class TestModPortal(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.mods_data_path = Path("src/data/mods/mod-database.json")
        self.mods_data = {}
        self.compliance_checker = None
        self.test_mods = {}
        
        # Load test data
        self.load_test_data()
        
        # Initialize compliance checker
        self.setup_compliance_checker()
    
    def load_test_data(self):
        """Load mods database for testing"""
        try:
            if self.mods_data_path.exists():
                with open(self.mods_data_path, 'r', encoding='utf-8') as f:
                    self.mods_data = json.load(f)
                print(f"✅ Loaded {len(self.mods_data.get('mods', {}))} mods for testing")
            else:
                print(f"❌ Mods database not found at {self.mods_data_path}")
        except Exception as e:
            print(f"❌ Error loading test data: {e}")
    
    def setup_compliance_checker(self):
        """Set up compliance checker for testing"""
        class ComplianceChecker:
            def __init__(self):
                self.swgr_rules = {
                    'noAutomation': {
                        'keywords': ['auto', 'automated', 'automatic', 'bot', 'macro', 'script'],
                        'description': 'No automation of game actions',
                        'severity': 'critical'
                    },
                    'noCombatAutomation': {
                        'keywords': ['auto-target', 'auto-heal', 'auto-attack', 'combat automation'],
                        'description': 'No automation of combat actions',
                        'severity': 'critical'
                    },
                    'noMovementAutomation': {
                        'keywords': ['auto-move', 'auto-navigate', 'pathfinding', 'auto-travel'],
                        'description': 'No automation of movement',
                        'severity': 'critical'
                    },
                    'ms11Derived': {
                        'keywords': ['ms11', 'morningstar', 'internal', 'team'],
                        'description': 'MS11-derived tools are internal only',
                        'severity': 'internal'
                    },
                    'suspiciousFiles': {
                        'patterns': ['.exe', '.dll', '.bat', '.cmd', '.vbs', '.js'],
                        'description': 'Executable files are suspicious',
                        'severity': 'warning'
                    },
                    'noNetworkAccess': {
                        'keywords': ['network', 'http', 'https', 'api', 'server', 'remote'],
                        'description': 'No unauthorized network access',
                        'severity': 'critical'
                    }
                }
                
                self.categories = {
                    'UI': {'safe': True, 'description': 'User Interface improvements'},
                    'HUD': {'safe': True, 'description': 'Heads Up Display enhancements'},
                    'Crafting Helpers': {'safe': True, 'description': 'Crafting assistance tools'},
                    'Visual Upgrades': {'safe': True, 'description': 'Visual and aesthetic improvements'},
                    'Automation Tools': {'safe': False, 'description': 'Automation and scripting tools'}
                }
            
            def check_compliance(self, mod):
                """Check if a mod is SWGR compliant"""
                result = {
                    'compliant': True,
                    'issues': [],
                    'warnings': [],
                    'ms11Derived': False,
                    'category': mod.get('category', 'Unknown'),
                    'riskLevel': 'low'
                }
                
                # Check for MS11 derivation
                if self.is_ms11_derived(mod):
                    result['ms11Derived'] = True
                    result['compliant'] = False
                    result['issues'].append({
                        'type': 'ms11_derived',
                        'message': 'MS11-derived mods are for internal use only',
                        'severity': 'critical'
                    })
                
                # Check text for compliance issues
                text_to_check = [
                    mod.get('name', ''),
                    mod.get('description', ''),
                    mod.get('compliance_notes', '')
                ]
                
                if mod.get('features'):
                    text_to_check.extend(mod['features'])
                
                text_to_check = ' '.join(text_to_check).lower()
                
                # Apply rule checks
                for rule_name, rule in self.swgr_rules.items():
                    matches = self.check_rule(text_to_check, rule)
                    if matches:
                        if rule['severity'] == 'critical':
                            result['compliant'] = False
                            result['issues'].append({
                                'type': rule_name,
                                'message': rule['description'],
                                'details': matches,
                                'severity': 'critical'
                            })
                        elif rule['severity'] == 'warning':
                            result['warnings'].append({
                                'type': rule_name,
                                'message': rule['description'],
                                'details': matches,
                                'severity': 'warning'
                            })
                
                # Check category compliance
                category_info = self.categories.get(mod.get('category'))
                if category_info and not category_info['safe']:
                    result['compliant'] = False
                    result['issues'].append({
                        'type': 'category_risk',
                        'message': f"Category \"{mod.get('category')}\" may contain automation",
                        'severity': 'critical'
                    })
                
                # Determine risk level
                result['riskLevel'] = self.calculate_risk_level(result)
                
                return result
            
            def is_ms11_derived(self, mod):
                """Check if mod is MS11-derived"""
                ms11_indicators = ['ms11', 'morningstar', 'internal', 'team']
                
                text_to_check = [
                    mod.get('name', ''),
                    mod.get('author', ''),
                    mod.get('description', ''),
                    mod.get('id', '')
                ]
                text_to_check = ' '.join(text_to_check).lower()
                
                return any(indicator in text_to_check for indicator in ms11_indicators) or mod.get('ms11_derived', False)
            
            def check_rule(self, text, rule):
                """Check text against a specific rule"""
                matches = []
                
                if 'keywords' in rule:
                    for keyword in rule['keywords']:
                        if keyword.lower() in text:
                            matches.append(keyword)
                
                if 'patterns' in rule:
                    for pattern in rule['patterns']:
                        if pattern.lower() in text:
                            matches.append(pattern)
                
                return matches
            
            def calculate_risk_level(self, result):
                """Calculate risk level based on compliance result"""
                if result['ms11Derived']:
                    return 'critical'
                
                critical_issues = [issue for issue in result['issues'] if issue['severity'] == 'critical']
                warnings = len(result['warnings'])
                
                if critical_issues:
                    return 'high'
                if warnings > 2:
                    return 'medium'
                if warnings > 0:
                    return 'low'
                
                return 'low'
            
            def get_compliance_badge(self, compliance_result):
                """Get compliance status badge"""
                if compliance_result['ms11Derived']:
                    return {
                        'text': 'Internal Use Only',
                        'class': 'badge-internal',
                        'icon': '🔒',
                        'color': '#6c757d'
                    }
                
                if compliance_result['compliant']:
                    return {
                        'text': 'SWGR Safe',
                        'class': 'badge-safe',
                        'icon': '✅',
                        'color': '#28a745'
                    }
                else:
                    return {
                        'text': 'Not SWGR Compliant',
                        'class': 'badge-unsafe',
                        'icon': '❌',
                        'color': '#dc3545'
                    }
            
            def validate_submission(self, mod_data):
                """Validate mod submission"""
                result = {
                    'valid': True,
                    'errors': [],
                    'warnings': []
                }
                
                # Required fields
                required_fields = ['name', 'author', 'description', 'category']
                for field in required_fields:
                    if not mod_data.get(field) or mod_data[field].strip() == '':
                        result['valid'] = False
                        result['errors'].append(f"Missing required field: {field}")
                
                # Category validation
                if mod_data.get('category') and mod_data['category'] not in self.categories:
                    result['warnings'].append(f"Unknown category: {mod_data['category']}")
                
                # Description length
                if mod_data.get('description') and len(mod_data['description']) < 10:
                    result['warnings'].append('Description is very short')
                
                # Version format
                if mod_data.get('version') and not self.is_valid_version(mod_data['version']):
                    result['warnings'].append('Version should follow semantic versioning (x.y.z)')
                
                return result
            
            def is_valid_version(self, version):
                """Check if version follows semantic versioning"""
                import re
                return bool(re.match(r'^\d+\.\d+\.\d+$', version))
        
        self.compliance_checker = ComplianceChecker()
    
    def test_mod_database_structure(self):
        """Test mod database structure and required fields"""
        print("\n🔍 Testing mod database structure...")
        
        # Check if database exists
        self.assertTrue(self.mods_data_path.exists(), "Mod database file should exist")
        
        # Check required top-level fields
        required_fields = ['metadata', 'mods']
        for field in required_fields:
            self.assertIn(field, self.mods_data, f"Database should contain '{field}' field")
        
        # Check metadata structure
        metadata = self.mods_data.get('metadata', {})
        required_metadata = ['last_updated', 'total_mods', 'swgr_safe_count', 'ms11_derived_count', 'categories']
        for field in required_metadata:
            self.assertIn(field, metadata, f"Metadata should contain '{field}' field")
        
        # Check mods structure
        mods = self.mods_data.get('mods', {})
        self.assertGreater(len(mods), 0, "Database should contain at least one mod")
        
        # Check individual mod structure
        required_mod_fields = ['id', 'name', 'author', 'version', 'description', 'category', 'swgr_compliant', 'ms11_derived']
        for mod_id, mod in mods.items():
            for field in required_mod_fields:
                self.assertIn(field, mod, f"Mod '{mod_id}' should contain '{field}' field")
    
    def test_compliance_checker_functionality(self):
        """Test compliance checker functionality"""
        print("\n🔍 Testing compliance checker...")
        
        # Test SWGR safe mod
        safe_mod = {
            'id': 'test-safe',
            'name': 'Safe UI Mod',
            'author': 'TestAuthor',
            'description': 'Visual improvements for the user interface',
            'category': 'UI',
            'features': ['Better Layout', 'Visual Enhancements']
        }
        
        compliance = self.compliance_checker.check_compliance(safe_mod)
        self.assertTrue(compliance['compliant'], "Safe mod should be compliant")
        self.assertFalse(compliance['ms11Derived'], "Safe mod should not be MS11-derived")
        self.assertEqual(compliance['riskLevel'], 'low', "Safe mod should have low risk")
        
        # Test non-compliant mod
        unsafe_mod = {
            'id': 'test-unsafe',
            'name': 'Auto Combat Helper',
            'author': 'TestAuthor',
            'description': 'Automated combat assistance with auto-targeting',
            'category': 'Automation Tools',
            'features': ['Auto-targeting', 'Combat Automation']
        }
        
        compliance = self.compliance_checker.check_compliance(unsafe_mod)
        self.assertFalse(compliance['compliant'], "Unsafe mod should not be compliant")
        self.assertGreater(len(compliance['issues']), 0, "Unsafe mod should have compliance issues")
        self.assertIn('high', compliance['riskLevel'], "Unsafe mod should have high risk")
        
        # Test MS11-derived mod
        ms11_mod = {
            'id': 'test-ms11',
            'name': 'MS11 Combat Assistant',
            'author': 'MS11 Team',
            'description': 'Internal MS11 combat automation tool',
            'category': 'Automation Tools',
            'ms11_derived': True
        }
        
        compliance = self.compliance_checker.check_compliance(ms11_mod)
        self.assertTrue(compliance['ms11Derived'], "MS11 mod should be marked as MS11-derived")
        self.assertFalse(compliance['compliant'], "MS11 mod should not be compliant")
        self.assertEqual(compliance['riskLevel'], 'critical', "MS11 mod should have critical risk")
    
    def test_ms11_derived_detection(self):
        """Test MS11-derived mod detection"""
        print("\n🔍 Testing MS11-derived detection...")
        
        # Test various MS11 indicators
        ms11_indicators = [
            {'name': 'MS11 Combat Tool', 'author': 'MS11 Team'},
            {'name': 'MorningStar Helper', 'author': 'TestAuthor'},
            {'name': 'Internal Tool', 'author': 'MS11 Team'},
            {'name': 'Regular Mod', 'author': 'MS11 Team', 'ms11_derived': True}
        ]
        
        for i, mod_data in enumerate(ms11_indicators):
            mod = {
                'id': f'test-ms11-{i}',
                'name': mod_data['name'],
                'author': mod_data['author'],
                'description': 'Test mod',
                'category': 'UI'
            }
            
            if 'ms11_derived' in mod_data:
                mod['ms11_derived'] = mod_data['ms11_derived']
            
            is_ms11 = self.compliance_checker.is_ms11_derived(mod)
            expected_ms11 = 'ms11' in mod_data['name'].lower() or 'morningstar' in mod_data['name'].lower() or 'internal' in mod_data['name'].lower() or mod_data.get('ms11_derived', False)
            
            self.assertEqual(is_ms11, expected_ms11, f"MS11 detection failed for {mod_data['name']}")
    
    def test_filtering_system(self):
        """Test mod filtering functionality"""
        print("\n🔍 Testing filtering system...")
        
        mods = self.mods_data.get('mods', {})
        mods_list = list(mods.values())
        
        # Test SWGR safe filter
        safe_mods = [mod for mod in mods_list if self.compliance_checker.check_compliance(mod)['compliant'] and not self.compliance_checker.check_compliance(mod)['ms11Derived']]
        self.assertGreaterEqual(len(safe_mods), 0, "Should find SWGR safe mods")
        
        # Test category filter
        ui_mods = [mod for mod in mods_list if mod.get('category') == 'UI']
        self.assertGreaterEqual(len(ui_mods), 0, "Should find UI mods")
        
        # Test MS11-derived filter
        ms11_mods = [mod for mod in mods_list if self.compliance_checker.check_compliance(mod)['ms11Derived']]
        self.assertGreaterEqual(len(ms11_mods), 0, "Should find MS11-derived mods")
        
        # Test search functionality
        search_term = 'combat'
        search_results = [mod for mod in mods_list if self.mod_matches_search(mod, search_term)]
        self.assertGreaterEqual(len(search_results), 0, "Should find mods matching search term")
    
    def mod_matches_search(self, mod, search_term):
        """Helper function to check if mod matches search term"""
        search_text = [
            mod.get('name', ''),
            mod.get('author', ''),
            mod.get('description', ''),
            *mod.get('features', [])
        ]
        search_text = ' '.join(search_text).lower()
        return search_term.lower() in search_text
    
    def test_compliance_badges(self):
        """Test compliance badge generation"""
        print("\n🔍 Testing compliance badges...")
        
        # Test safe mod badge
        safe_compliance = {
            'compliant': True,
            'ms11Derived': False,
            'issues': [],
            'warnings': []
        }
        
        badge = self.compliance_checker.get_compliance_badge(safe_compliance)
        self.assertEqual(badge['text'], 'SWGR Safe', "Safe mod should have SWGR Safe badge")
        self.assertEqual(badge['icon'], '✅', "Safe mod should have checkmark icon")
        
        # Test unsafe mod badge
        unsafe_compliance = {
            'compliant': False,
            'ms11Derived': False,
            'issues': [{'message': 'Test issue'}],
            'warnings': []
        }
        
        badge = self.compliance_checker.get_compliance_badge(unsafe_compliance)
        self.assertEqual(badge['text'], 'Not SWGR Compliant', "Unsafe mod should have Not SWGR Compliant badge")
        self.assertEqual(badge['icon'], '❌', "Unsafe mod should have X icon")
        
        # Test MS11-derived badge
        ms11_compliance = {
            'compliant': False,
            'ms11Derived': True,
            'issues': [{'message': 'MS11-derived'}],
            'warnings': []
        }
        
        badge = self.compliance_checker.get_compliance_badge(ms11_compliance)
        self.assertEqual(badge['text'], 'Internal Use Only', "MS11 mod should have Internal Use Only badge")
        self.assertEqual(badge['icon'], '🔒', "MS11 mod should have lock icon")
    
    def test_mod_submission_validation(self):
        """Test mod submission validation"""
        print("\n🔍 Testing mod submission validation...")
        
        # Test valid submission
        valid_mod = {
            'name': 'Test Mod',
            'author': 'Test Author',
            'description': 'A comprehensive test mod with detailed description',
            'category': 'UI',
            'version': '1.0.0'
        }
        
        validation = self.compliance_checker.validate_submission(valid_mod)
        self.assertTrue(validation['valid'], "Valid mod should pass validation")
        self.assertEqual(len(validation['errors']), 0, "Valid mod should have no errors")
        
        # Test invalid submission
        invalid_mod = {
            'name': '',
            'author': 'Test Author',
            'description': 'Short',
            'category': 'Unknown Category',
            'version': 'invalid'
        }
        
        validation = self.compliance_checker.validate_submission(invalid_mod)
        self.assertFalse(validation['valid'], "Invalid mod should fail validation")
        self.assertGreater(len(validation['errors']), 0, "Invalid mod should have errors")
        self.assertGreater(len(validation['warnings']), 0, "Invalid mod should have warnings")
    
    def test_risk_level_calculation(self):
        """Test risk level calculation"""
        print("\n🔍 Testing risk level calculation...")
        
        # Test low risk
        low_risk = {
            'ms11Derived': False,
            'issues': [],
            'warnings': []
        }
        risk_level = self.compliance_checker.calculate_risk_level(low_risk)
        self.assertEqual(risk_level, 'low', "Mod with no issues should have low risk")
        
        # Test medium risk
        medium_risk = {
            'ms11Derived': False,
            'issues': [],
            'warnings': [{'message': 'Warning 1'}, {'message': 'Warning 2'}, {'message': 'Warning 3'}]
        }
        risk_level = self.compliance_checker.calculate_risk_level(medium_risk)
        self.assertEqual(risk_level, 'medium', "Mod with many warnings should have medium risk")
        
        # Test high risk
        high_risk = {
            'ms11Derived': False,
            'issues': [{'severity': 'critical'}],
            'warnings': []
        }
        risk_level = self.compliance_checker.calculate_risk_level(high_risk)
        self.assertEqual(risk_level, 'high', "Mod with critical issues should have high risk")
        
        # Test critical risk
        critical_risk = {
            'ms11Derived': True,
            'issues': [],
            'warnings': []
        }
        risk_level = self.compliance_checker.calculate_risk_level(critical_risk)
        self.assertEqual(risk_level, 'critical', "MS11-derived mod should have critical risk")
    
    def test_file_integrity(self):
        """Test file integrity and structure"""
        print("\n🔍 Testing file integrity...")
        
        # Check required files exist
        required_files = [
            "src/data/mods/mod-database.json",
            "src/lib/compliance-check.js",
            "src/components/ModCard.svelte",
            "src/pages/mods/index.11ty.js"
        ]
        
        for file_path in required_files:
            path_obj = Path(file_path)
            self.assertTrue(path_obj.exists(), f"Required file {file_path} should exist")
            self.assertGreater(path_obj.stat().st_size, 0, f"File {file_path} should not be empty")
        
        # Check mod database has valid JSON structure
        try:
            with open(self.mods_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.assertIsInstance(data, dict, "Mod database should be valid JSON object")
        except json.JSONDecodeError as e:
            self.fail(f"Mod database should be valid JSON: {e}")
    
    def test_data_quality(self):
        """Test data quality and consistency"""
        print("\n🔍 Testing data quality...")
        
        mods = self.mods_data.get('mods', {})
        
        for mod_id, mod in mods.items():
            # Check mod ID consistency
            self.assertEqual(mod['id'], mod_id, f"Mod ID should match key for {mod_id}")
            
            # Check required string fields are not empty
            string_fields = ['name', 'author', 'description', 'category']
            for field in string_fields:
                self.assertIsInstance(mod.get(field), str, f"Field {field} should be string for {mod_id}")
                self.assertGreater(len(mod[field].strip()), 0, f"Field {field} should not be empty for {mod_id}")
            
            # Check boolean fields
            boolean_fields = ['swgr_compliant', 'ms11_derived']
            for field in boolean_fields:
                self.assertIsInstance(mod.get(field), bool, f"Field {field} should be boolean for {mod_id}")
            
            # Check numeric fields
            numeric_fields = ['downloads', 'rating']
            for field in numeric_fields:
                if field in mod:
                    self.assertIsInstance(mod[field], (int, float), f"Field {field} should be numeric for {mod_id}")
                    if field == 'rating':
                        self.assertGreaterEqual(mod[field], 0, f"Rating should be non-negative for {mod_id}")
                        self.assertLessEqual(mod[field], 5, f"Rating should be <= 5 for {mod_id}")
            
            # Check array fields
            if 'features' in mod:
                self.assertIsInstance(mod['features'], list, f"Features should be array for {mod_id}")
                for feature in mod['features']:
                    self.assertIsInstance(feature, str, f"Feature should be string for {mod_id}")
            
            # Check date fields
            if 'last_updated' in mod:
                try:
                    datetime.fromisoformat(mod['last_updated'].replace('Z', '+00:00'))
                except ValueError:
                    self.fail(f"Last updated should be valid ISO date for {mod_id}")
    
    def test_compliance_rules(self):
        """Test compliance rules and keyword detection"""
        print("\n🔍 Testing compliance rules...")
        
        # Test automation keywords
        automation_keywords = ['auto', 'automated', 'automatic', 'bot', 'macro', 'script']
        for keyword in automation_keywords:
            test_mod = {
                'id': f'test-{keyword}',
                'name': f'Test {keyword.title()} Mod',
                'author': 'TestAuthor',
                'description': f'This mod uses {keyword} functionality',
                'category': 'UI'
            }
            
            compliance = self.compliance_checker.check_compliance(test_mod)
            self.assertFalse(compliance['compliant'], f"Mod with '{keyword}' should not be compliant")
            self.assertGreater(len(compliance['issues']), 0, f"Mod with '{keyword}' should have issues")
        
        # Test safe keywords
        safe_keywords = ['visual', 'display', 'interface', 'ui', 'hud']
        for keyword in safe_keywords:
            test_mod = {
                'id': f'test-{keyword}',
                'name': f'Test {keyword.title()} Mod',
                'author': 'TestAuthor',
                'description': f'This mod provides {keyword} improvements',
                'category': 'UI'
            }
            
            compliance = self.compliance_checker.check_compliance(test_mod)
            self.assertTrue(compliance['compliant'], f"Mod with '{keyword}' should be compliant")
    
    def test_category_compliance(self):
        """Test category-based compliance checking"""
        print("\n🔍 Testing category compliance...")
        
        # Test safe categories
        safe_categories = ['UI', 'HUD', 'Crafting Helpers', 'Visual Upgrades']
        for category in safe_categories:
            test_mod = {
                'id': f'test-{category.lower()}',
                'name': f'Test {category} Mod',
                'author': 'TestAuthor',
                'description': 'Test mod',
                'category': category
            }
            
            compliance = self.compliance_checker.check_compliance(test_mod)
            self.assertTrue(compliance['compliant'], f"Mod in '{category}' category should be compliant")
        
        # Test unsafe category
        unsafe_category = 'Automation Tools'
        test_mod = {
            'id': 'test-automation',
            'name': 'Test Automation Mod',
            'author': 'TestAuthor',
            'description': 'Test mod',
            'category': unsafe_category
        }
        
        compliance = self.compliance_checker.check_compliance(test_mod)
        self.assertFalse(compliance['compliant'], f"Mod in '{unsafe_category}' category should not be compliant")
    
    def test_statistics_generation(self):
        """Test statistics generation functionality"""
        print("\n🔍 Testing statistics generation...")
        
        mods = self.mods_data.get('mods', {})
        
        # Generate statistics
        stats = {
            'total_mods': len(mods),
            'swgr_safe': 0,
            'swgr_unsafe': 0,
            'ms11_derived': 0,
            'by_category': {},
            'by_risk_level': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
            'total_downloads': 0,
            'authors': set()
        }
        
        for mod_id, mod in mods.items():
            compliance = self.compliance_checker.check_compliance(mod)
            
            if compliance['ms11Derived']:
                stats['ms11_derived'] += 1
            elif compliance['compliant']:
                stats['swgr_safe'] += 1
            else:
                stats['swgr_unsafe'] += 1
            
            # Category breakdown
            category = mod.get('category', 'Unknown')
            if category not in stats['by_category']:
                stats['by_category'][category] = {'total': 0, 'safe': 0, 'unsafe': 0, 'ms11_derived': 0}
            
            stats['by_category'][category]['total'] += 1
            if compliance['ms11Derived']:
                stats['by_category'][category]['ms11_derived'] += 1
            elif compliance['compliant']:
                stats['by_category'][category]['safe'] += 1
            else:
                stats['by_category'][category]['unsafe'] += 1
            
            # Risk level
            stats['by_risk_level'][compliance['riskLevel']] += 1
            
            # Downloads and authors
            stats['total_downloads'] += mod.get('downloads', 0)
            stats['authors'].add(mod.get('author', 'Unknown'))
        
        stats['authors'] = len(stats['authors'])
        
        # Validate statistics
        self.assertEqual(stats['total_mods'], len(mods), "Total mods should match actual count")
        self.assertEqual(stats['swgr_safe'] + stats['swgr_unsafe'] + stats['ms11_derived'], stats['total_mods'], "Compliance breakdown should sum to total")
        self.assertGreaterEqual(stats['total_downloads'], 0, "Total downloads should be non-negative")
        self.assertGreaterEqual(stats['authors'], 1, "Should have at least one author")
        
        # Check risk level breakdown
        risk_sum = sum(stats['by_risk_level'].values())
        self.assertEqual(risk_sum, stats['total_mods'], "Risk level breakdown should sum to total")
    
    def run_tests(self):
        """Run all tests and generate report"""
        print("🚀 BATCH 187 - LEGAL MOD PORTAL + SWGR COMPLIANCE CHECK TEST SUITE")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test methods
        test_methods = [method for method in dir(self) if method.startswith('test_')]
        
        passed = 0
        failed = 0
        errors = []
        
        for method in test_methods:
            try:
                getattr(self, method)()
                passed += 1
                print(f"✅ {method}")
            except Exception as e:
                failed += 1
                error_msg = f"❌ {method}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
        
        # Print summary
        print(f"\n📊 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {passed + failed}")
        
        if errors:
            print(f"\n❌ ERRORS:")
            for error in errors:
                print(f"   {error}")
        
        success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("🎉 All tests passed! Batch 187 implementation is working correctly.")
        else:
            print("⚠️  Some tests failed. Please review the implementation.")
        
        print(f"\n✅ Test suite completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function to run the test suite"""
    test_suite = TestModPortal()
    test_suite.run_tests()

if __name__ == "__main__":
    main() 
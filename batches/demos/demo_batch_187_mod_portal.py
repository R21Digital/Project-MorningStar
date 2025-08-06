#!/usr/bin/env python3
"""
Batch 187 - Legal Mod Portal + SWGR Compliance Check Demo
Demonstrates the mod portal system with compliance checking and MS11-derived mod handling
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ModPortalDemo:
    def __init__(self):
        self.mods_data_path = Path("src/data/mods/mod-database.json")
        self.mods_data = {}
        self.compliance_checker = None
        self.stats = {}
        
    def load_mods_data(self):
        """Load mods database from JSON file"""
        try:
            if self.mods_data_path.exists():
                with open(self.mods_data_path, 'r', encoding='utf-8') as f:
                    self.mods_data = json.load(f)
                print(f"✅ Loaded {len(self.mods_data.get('mods', {}))} mods from database")
                return True
            else:
                print(f"❌ Mods database not found at {self.mods_data_path}")
                return False
        except Exception as e:
            print(f"❌ Error loading mods data: {e}")
            return False
    
    def simulate_compliance_checker(self):
        """Simulate the JavaScript compliance checker functionality"""
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
                    'ms11Derived': {
                        'keywords': ['ms11', 'morningstar', 'internal', 'team'],
                        'description': 'MS11-derived tools are internal only',
                        'severity': 'internal'
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
        
        self.compliance_checker = ComplianceChecker()
        print("✅ Compliance checker initialized")
    
    def generate_demo_statistics(self):
        """Generate comprehensive statistics about the mod database"""
        mods = self.mods_data.get('mods', {})
        metadata = self.mods_data.get('metadata', {})
        
        # Basic stats
        self.stats = {
            'total_mods': len(mods),
            'swgr_safe': 0,
            'swgr_unsafe': 0,
            'ms11_derived': 0,
            'by_category': {},
            'by_risk_level': {
                'low': 0,
                'medium': 0,
                'high': 0,
                'critical': 0
            },
            'total_downloads': 0,
            'average_rating': 0,
            'authors': set(),
            'compliance_issues': []
        }
        
        ratings = []
        
        for mod_id, mod in mods.items():
            # Compliance check
            compliance = self.compliance_checker.check_compliance(mod)
            
            if compliance['ms11Derived']:
                self.stats['ms11_derived'] += 1
            elif compliance['compliant']:
                self.stats['swgr_safe'] += 1
            else:
                self.stats['swgr_unsafe'] += 1
            
            # Category breakdown
            category = mod.get('category', 'Unknown')
            if category not in self.stats['by_category']:
                self.stats['by_category'][category] = {
                    'total': 0,
                    'safe': 0,
                    'unsafe': 0,
                    'ms11_derived': 0
                }
            
            self.stats['by_category'][category]['total'] += 1
            if compliance['ms11Derived']:
                self.stats['by_category'][category]['ms11_derived'] += 1
            elif compliance['compliant']:
                self.stats['by_category'][category]['safe'] += 1
            else:
                self.stats['by_category'][category]['unsafe'] += 1
            
            # Risk level
            self.stats['by_risk_level'][compliance['riskLevel']] += 1
            
            # Downloads and ratings
            self.stats['total_downloads'] += mod.get('downloads', 0)
            if mod.get('rating', 0) > 0:
                ratings.append(mod['rating'])
            
            # Authors
            self.stats['authors'].add(mod.get('author', 'Unknown'))
            
            # Collect compliance issues
            self.stats['compliance_issues'].extend(compliance['issues'])
        
        # Calculate averages
        if ratings:
            self.stats['average_rating'] = sum(ratings) / len(ratings)
        
        self.stats['authors'] = len(self.stats['authors'])
        
        print("✅ Generated comprehensive statistics")
    
    def demo_compliance_checking(self):
        """Demonstrate compliance checking functionality"""
        print("\n🔍 COMPLIANCE CHECKING DEMO")
        print("=" * 50)
        
        mods = self.mods_data.get('mods', {})
        
        for mod_id, mod in mods.items():
            print(f"\n📦 Checking: {mod['name']} (by {mod['author']})")
            print(f"   Category: {mod.get('category', 'Unknown')}")
            print(f"   Description: {mod['description'][:100]}...")
            
            compliance = self.compliance_checker.check_compliance(mod)
            badge = self.compliance_checker.get_compliance_badge(compliance)
            
            print(f"   Status: {badge['icon']} {badge['text']}")
            print(f"   Risk Level: {compliance['riskLevel'].upper()}")
            
            if compliance['issues']:
                print("   Issues:")
                for issue in compliance['issues']:
                    print(f"     ❌ {issue['message']}")
            
            if compliance['warnings']:
                print("   Warnings:")
                for warning in compliance['warnings']:
                    print(f"     ⚠️  {warning['message']}")
    
    def demo_filtering_system(self):
        """Demonstrate the filtering system"""
        print("\n🔍 FILTERING SYSTEM DEMO")
        print("=" * 50)
        
        mods = self.mods_data.get('mods', {})
        mods_list = list(mods.values())
        
        # Demo different filter combinations
        filter_scenarios = [
            {
                'name': 'SWGR Safe Mods Only',
                'filters': {'status': 'swgr_safe', 'category': 'all', 'search': ''}
            },
            {
                'name': 'UI Category Only',
                'filters': {'status': 'all', 'category': 'UI', 'search': ''}
            },
            {
                'name': 'MS11-Derived Mods',
                'filters': {'status': 'internal', 'category': 'all', 'search': ''}
            },
            {
                'name': 'Search for "Combat"',
                'filters': {'status': 'all', 'category': 'all', 'search': 'combat'}
            },
            {
                'name': 'Automation Tools (High Risk)',
                'filters': {'status': 'all', 'category': 'Automation Tools', 'search': ''}
            }
        ]
        
        for scenario in filter_scenarios:
            print(f"\n🎯 {scenario['name']}")
            filtered_mods = self.apply_filters(mods_list, scenario['filters'])
            
            print(f"   Found {len(filtered_mods)} mods:")
            for mod in filtered_mods:
                compliance = self.compliance_checker.check_compliance(mod)
                badge = self.compliance_checker.get_compliance_badge(compliance)
                print(f"     • {mod['name']} - {badge['icon']} {badge['text']}")
    
    def apply_filters(self, mods, filters):
        """Apply filters to mod list"""
        filtered = mods
        
        # Status filter
        if filters['status'] != 'all':
            if filters['status'] == 'swgr_safe':
                filtered = [mod for mod in filtered if self.compliance_checker.check_compliance(mod)['compliant'] and not self.compliance_checker.check_compliance(mod)['ms11Derived']]
            elif filters['status'] == 'swgr_unsafe':
                filtered = [mod for mod in filtered if not self.compliance_checker.check_compliance(mod)['compliant'] and not self.compliance_checker.check_compliance(mod)['ms11Derived']]
            elif filters['status'] == 'internal':
                filtered = [mod for mod in filtered if self.compliance_checker.check_compliance(mod)['ms11Derived']]
        
        # Category filter
        if filters['category'] != 'all':
            filtered = [mod for mod in filtered if mod.get('category') == filters['category']]
        
        # Search filter
        if filters['search']:
            search_term = filters['search'].lower()
            filtered = [mod for mod in filtered if self.mod_matches_search(mod, search_term)]
        
        return filtered
    
    def mod_matches_search(self, mod, search_term):
        """Check if mod matches search term"""
        search_text = [
            mod.get('name', ''),
            mod.get('author', ''),
            mod.get('description', ''),
            *mod.get('features', [])
        ]
        search_text = ' '.join(search_text).lower()
        return search_term in search_text
    
    def demo_ms11_derived_handling(self):
        """Demonstrate MS11-derived mod handling"""
        print("\n🔒 MS11-DERIVED MOD HANDLING DEMO")
        print("=" * 50)
        
        mods = self.mods_data.get('mods', {})
        ms11_mods = []
        
        for mod_id, mod in mods.items():
            if self.compliance_checker.is_ms11_derived(mod):
                ms11_mods.append(mod)
        
        print(f"Found {len(ms11_mods)} MS11-derived mods:")
        
        for mod in ms11_mods:
            print(f"\n🔒 {mod['name']}")
            print(f"   Author: {mod['author']}")
            print(f"   Description: {mod['description']}")
            print(f"   Internal Only: {mod.get('internal_only', False)}")
            print(f"   Download URL: {'None (Internal Only)' if mod.get('internal_only') else mod.get('download_url', 'Not available')}")
            
            compliance = self.compliance_checker.check_compliance(mod)
            print(f"   Compliance Issues: {len(compliance['issues'])}")
            for issue in compliance['issues']:
                print(f"     • {issue['message']}")
    
    def demo_mod_submission_workflow(self):
        """Demonstrate mod submission workflow"""
        print("\n📝 MOD SUBMISSION WORKFLOW DEMO")
        print("=" * 50)
        
        # Simulate a new mod submission
        new_mod = {
            'name': 'Demo Combat Helper',
            'author': 'DemoAuthor',
            'description': 'A combat helper with auto-targeting and damage prediction',
            'category': 'Automation Tools',
            'features': ['Auto-targeting', 'Damage Prediction', 'Combat Automation'],
            'version': '1.0.0'
        }
        
        print("📦 New Mod Submission:")
        print(f"   Name: {new_mod['name']}")
        print(f"   Author: {new_mod['author']}")
        print(f"   Category: {new_mod['category']}")
        print(f"   Description: {new_mod['description']}")
        print(f"   Features: {', '.join(new_mod['features'])}")
        
        # Check compliance
        compliance = self.compliance_checker.check_compliance(new_mod)
        badge = self.compliance_checker.get_compliance_badge(compliance)
        
        print(f"\n🔍 Compliance Check Result:")
        print(f"   Status: {badge['icon']} {badge['text']}")
        print(f"   Risk Level: {compliance['riskLevel'].upper()}")
        
        if compliance['issues']:
            print("   Issues Found:")
            for issue in compliance['issues']:
                print(f"     ❌ {issue['message']}")
                if 'details' in issue:
                    print(f"        Keywords: {', '.join(issue['details'])}")
        
        # Simulate submission decision
        if compliance['compliant']:
            print("\n✅ Mod would be accepted for review")
        else:
            print("\n❌ Mod would be rejected due to compliance issues")
            print("   Recommendation: Remove automation features to make it SWGR compliant")
    
    def print_statistics_report(self):
        """Print comprehensive statistics report"""
        print("\n📊 COMPREHENSIVE STATISTICS REPORT")
        print("=" * 50)
        
        print(f"📦 Total Mods: {self.stats['total_mods']}")
        print(f"✅ SWGR Safe: {self.stats['swgr_safe']}")
        print(f"❌ Not SWGR Compliant: {self.stats['swgr_unsafe']}")
        print(f"🔒 MS11-Derived (Internal): {self.stats['ms11_derived']}")
        print(f"👥 Unique Authors: {self.stats['authors']}")
        print(f"📥 Total Downloads: {self.stats['total_downloads']:,}")
        print(f"⭐ Average Rating: {self.stats['average_rating']:.1f}")
        
        print(f"\n📊 Risk Level Breakdown:")
        for level, count in self.stats['by_risk_level'].items():
            percentage = (count / self.stats['total_mods']) * 100 if self.stats['total_mods'] > 0 else 0
            print(f"   {level.upper()}: {count} ({percentage:.1f}%)")
        
        print(f"\n📂 Category Breakdown:")
        for category, stats in self.stats['by_category'].items():
            print(f"   {category}:")
            print(f"     Total: {stats['total']}")
            print(f"     Safe: {stats['safe']}")
            print(f"     Unsafe: {stats['unsafe']}")
            print(f"     Internal: {stats['ms11_derived']}")
        
        print(f"\n⚠️  Compliance Issues Found:")
        issue_types = {}
        for issue in self.stats['compliance_issues']:
            issue_type = issue['type']
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        for issue_type, count in issue_types.items():
            print(f"   {issue_type}: {count} occurrences")
    
    def demo_file_structure(self):
        """Demonstrate the file structure created for Batch 187"""
        print("\n📁 BATCH 187 FILE STRUCTURE")
        print("=" * 50)
        
        files_to_check = [
            "src/data/mods/mod-database.json",
            "src/lib/compliance-check.js",
            "src/components/ModCard.svelte",
            "src/pages/mods/index.11ty.js"
        ]
        
        for file_path in files_to_check:
            path_obj = Path(file_path)
            if path_obj.exists():
                size = path_obj.stat().st_size
                print(f"✅ {file_path} ({size:,} bytes)")
            else:
                print(f"❌ {file_path} (not found)")
        
        print(f"\n📊 Mod Database Structure:")
        if self.mods_data:
            metadata = self.mods_data.get('metadata', {})
            mods = self.mods_data.get('mods', {})
            
            print(f"   Metadata Fields: {list(metadata.keys())}")
            print(f"   Total Mods: {len(mods)}")
            
            if mods:
                sample_mod = list(mods.values())[0]
                print(f"   Sample Mod Fields: {list(sample_mod.keys())}")
    
    def run_demo(self):
        """Run the complete demo"""
        print("🚀 BATCH 187 - LEGAL MOD PORTAL + SWGR COMPLIANCE CHECK DEMO")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load data
        if not self.load_mods_data():
            print("❌ Failed to load mods data. Exiting.")
            return
        
        # Initialize compliance checker
        self.simulate_compliance_checker()
        
        # Generate statistics
        self.generate_demo_statistics()
        
        # Run demos
        self.demo_compliance_checking()
        self.demo_filtering_system()
        self.demo_ms11_derived_handling()
        self.demo_mod_submission_workflow()
        
        # Print final report
        self.print_statistics_report()
        self.demo_file_structure()
        
        print(f"\n✅ Demo completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎉 Batch 187 implementation successfully demonstrated!")

def main():
    """Main function to run the demo"""
    demo = ModPortalDemo()
    demo.run_demo()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Batch 193 - Heroic Guide Pages Test Suite
Tests the heroic guide system with map markers, loot links, and boss phases.
"""

import os
import sys
import json
import yaml
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class HeroicGuidesTester:
    """Test suite for heroic guide pages system"""
    
    def __init__(self):
        self.test_results = []
        self.base_path = "."
        
    def log_test(self, test_name: str, status: str, details: Dict[str, Any] = None):
        """Log test results"""
        result = {
            'test_name': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def test_page_generator_structure(self) -> bool:
        """Test the dynamic page generator structure"""
        print("\n🏗️ Testing Page Generator Structure...")
        
        try:
            page_path = "src/pages/heroics/[name]/index.11ty.js"
            if not os.path.exists(page_path):
                self.log_test("Page Generator File", "FAIL",
                            {"error": f"File not found: {page_path}"})
                return False
            
            with open(page_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required 11ty features
            required_features = [
                'pagination',
                'eleventyComputed',
                'permalink',
                'module.exports',
                'render(data)'
            ]
            
            for feature in required_features:
                if feature in content:
                    self.log_test(f"Page Feature - {feature}", "PASS")
                else:
                    self.log_test(f"Page Feature - {feature}", "FAIL",
                                {"error": f"Missing required feature: {feature}"})
            
            # Check for heroic-specific functionality
            heroic_features = [
                'heroicsData',
                'mapData',
                'lootTables',
                'boss-encounters',
                'tab-content'
            ]
            
            for feature in heroic_features:
                if feature in content:
                    self.log_test(f"Heroic Feature - {feature}", "PASS")
                else:
                    self.log_test(f"Heroic Feature - {feature}", "FAIL",
                                {"error": f"Missing heroic feature: {feature}"})
            
            return True
            
        except Exception as e:
            self.log_test("Page Generator Structure", "FAIL", {"error": str(e)})
            return False
    
    def test_heroic_data_structure(self) -> bool:
        """Test heroic data files structure"""
        print("\n📊 Testing Heroic Data Structure...")
        
        try:
            # Test heroics index
            index_path = "data/heroics/heroics_index.yml"
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = yaml.safe_load(f)
                
                if 'heroics' in index_data and index_data['heroics']:
                    self.log_test("Heroics Index", "PASS",
                                {"heroics_count": len(index_data['heroics'])})
                    
                    # Test individual heroic files
                    for heroic_id in index_data['heroics'].keys():
                        heroic_path = f"data/heroics/{heroic_id}.yml"
                        if os.path.exists(heroic_path):
                            with open(heroic_path, 'r', encoding='utf-8') as f:
                                heroic_data = yaml.safe_load(f)
                            
                            # Check for enhanced structure
                            required_sections = [
                                'heroic_id',
                                'name',
                                'planet',
                                'encounters',
                                'difficulty_tiers'
                            ]
                            
                            missing_sections = [section for section in required_sections
                                              if section not in heroic_data]
                            
                            if missing_sections:
                                self.log_test(f"Heroic Data - {heroic_id}", "FAIL",
                                            {"missing_sections": missing_sections})
                            else:
                                self.log_test(f"Heroic Data - {heroic_id}", "PASS",
                                            {"encounters": len(heroic_data.get('encounters', []))})
                        else:
                            self.log_test(f"Heroic File - {heroic_id}", "FAIL",
                                        {"error": f"File not found: {heroic_path}"})
                else:
                    self.log_test("Heroics Index", "FAIL",
                                {"error": "No heroics data found in index"})
            else:
                self.log_test("Heroics Index", "FAIL",
                            {"error": f"Index file not found: {index_path}"})
            
            return True
            
        except Exception as e:
            self.log_test("Heroic Data Structure", "FAIL", {"error": str(e)})
            return False
    
    def test_map_data_structure(self) -> bool:
        """Test map data files structure"""
        print("\n🗺️ Testing Map Data Structure...")
        
        try:
            map_dir = "src/data/maps"
            if not os.path.exists(map_dir):
                self.log_test("Map Data Directory", "FAIL",
                            {"error": f"Directory not found: {map_dir}"})
                return False
            
            map_files = [f for f in os.listdir(map_dir) if f.endswith('.json')]
            
            if not map_files:
                self.log_test("Map Data Files", "FAIL",
                            {"error": "No map data files found"})
                return False
            
            self.log_test("Map Data Files", "PASS",
                        {"files_found": len(map_files)})
            
            # Test individual map files
            for map_file in map_files:
                map_path = os.path.join(map_dir, map_file)
                try:
                    with open(map_path, 'r', encoding='utf-8') as f:
                        map_data = json.load(f)
                    
                    # Check required map structure
                    required_fields = [
                        'mapId',
                        'name',
                        'planet',
                        'coordinates',
                        'zones',
                        'markers'
                    ]
                    
                    missing_fields = [field for field in required_fields
                                    if field not in map_data]
                    
                    if missing_fields:
                        self.log_test(f"Map Structure - {map_file}", "FAIL",
                                    {"missing_fields": missing_fields})
                    else:
                        self.log_test(f"Map Structure - {map_file}", "PASS",
                                    {"zones": len(map_data.get('zones', [])),
                                     "markers": len(map_data.get('markers', []))})
                        
                        # Test zone structure
                        for zone in map_data.get('zones', []):
                            if not all(key in zone for key in ['id', 'name', 'type', 'coordinates']):
                                self.log_test(f"Zone Structure - {zone.get('id', 'unknown')}", "FAIL",
                                            {"error": "Missing required zone fields"})
                            else:
                                self.log_test(f"Zone Structure - {zone['id']}", "PASS")
                
                except json.JSONDecodeError as e:
                    self.log_test(f"Map JSON - {map_file}", "FAIL",
                                {"error": f"Invalid JSON: {str(e)}"})
                except Exception as e:
                    self.log_test(f"Map Processing - {map_file}", "FAIL",
                                {"error": str(e)})
            
            return True
            
        except Exception as e:
            self.log_test("Map Data Structure", "FAIL", {"error": str(e)})
            return False
    
    def test_map_viewer_component(self) -> bool:
        """Test MapViewer Svelte component"""
        print("\n🔍 Testing MapViewer Component...")
        
        try:
            component_path = "src/components/MapViewer.svelte"
            if not os.path.exists(component_path):
                self.log_test("MapViewer Component", "FAIL",
                            {"error": f"Component not found: {component_path}"})
                return False
            
            with open(component_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Svelte component structure
            svelte_features = [
                '<script>',
                'export let',
                'onMount',
                '</script>',
                '<style>',
                '</style>'
            ]
            
            for feature in svelte_features:
                if feature in content:
                    self.log_test(f"Svelte Feature - {feature}", "PASS")
                else:
                    self.log_test(f"Svelte Feature - {feature}", "FAIL",
                                {"error": f"Missing Svelte feature: {feature}"})
            
            # Check for map-specific functionality
            map_features = [
                'canvas',
                'renderMap',
                'worldToScreen',
                'screenToWorld',
                'renderZones',
                'renderMarkers',
                'handleMouseMove',
                'tooltip'
            ]
            
            for feature in map_features:
                if feature in content:
                    self.log_test(f"Map Feature - {feature}", "PASS")
                else:
                    self.log_test(f"Map Feature - {feature}", "FAIL",
                                {"error": f"Missing map feature: {feature}"})
            
            return True
            
        except Exception as e:
            self.log_test("MapViewer Component", "FAIL", {"error": str(e)})
            return False
    
    def test_loot_table_integration(self) -> bool:
        """Test loot table integration and structure"""
        print("\n💎 Testing Loot Table Integration...")
        
        try:
            # Check for enhanced loot tables
            loot_dir = "data/loot_tables"
            if not os.path.exists(loot_dir):
                self.log_test("Loot Tables Directory", "FAIL",
                            {"error": f"Directory not found: {loot_dir}"})
                return False
            
            # Look for heroic-specific loot tables
            heroic_loot_files = [f for f in os.listdir(loot_dir) 
                               if f.endswith('.json') and not f.startswith('Acklay')]
            
            if not heroic_loot_files:
                self.log_test("Heroic Loot Tables", "WARN",
                            {"note": "No heroic-specific loot tables found"})
            else:
                self.log_test("Heroic Loot Tables", "PASS",
                            {"files_found": len(heroic_loot_files)})
                
                # Test loot table structure
                for loot_file in heroic_loot_files:
                    loot_path = os.path.join(loot_dir, loot_file)
                    try:
                        with open(loot_path, 'r', encoding='utf-8') as f:
                            loot_data = json.load(f)
                        
                        # Check enhanced loot table structure
                        required_fields = [
                            'heroic_id',
                            'name',
                            'drops',
                            'drop_sources'
                        ]
                        
                        missing_fields = [field for field in required_fields
                                        if field not in loot_data]
                        
                        if missing_fields:
                            self.log_test(f"Loot Structure - {loot_file}", "FAIL",
                                        {"missing_fields": missing_fields})
                        else:
                            self.log_test(f"Loot Structure - {loot_file}", "PASS",
                                        {"items": len(loot_data.get('drops', {})),
                                         "sources": len(loot_data.get('drop_sources', {}))})
                    
                    except json.JSONDecodeError as e:
                        self.log_test(f"Loot JSON - {loot_file}", "FAIL",
                                    {"error": f"Invalid JSON: {str(e)}"})
                    except Exception as e:
                        self.log_test(f"Loot Processing - {loot_file}", "FAIL",
                                    {"error": str(e)})
            
            return True
            
        except Exception as e:
            self.log_test("Loot Table Integration", "FAIL", {"error": str(e)})
            return False
    
    def test_boss_phases_functionality(self) -> bool:
        """Test boss phase toggle functionality"""
        print("\n⚔️ Testing Boss Phases Functionality...")
        
        try:
            # Check page generator for boss phase support
            page_path = "src/pages/heroics/[name]/index.11ty.js"
            with open(page_path, 'r', encoding='utf-8') as f:
                page_content = f.read()
            
            phase_features = [
                'boss-phase-nav',
                'phase-buttons',
                'data-boss-id',
                'data-phase',
                'boss-encounter',
                'phaseButtons.forEach'
            ]
            
            for feature in phase_features:
                if feature in page_content:
                    self.log_test(f"Phase Feature - {feature}", "PASS")
                else:
                    self.log_test(f"Phase Feature - {feature}", "FAIL",
                                {"error": f"Missing phase feature: {feature}"})
            
            # Check heroic data for phase information
            heroic_path = "data/heroics/axkva_min.yml"
            if os.path.exists(heroic_path):
                with open(heroic_path, 'r', encoding='utf-8') as f:
                    heroic_data = yaml.safe_load(f)
                
                encounters = heroic_data.get('encounters', [])
                if encounters:
                    phases_found = set()
                    for encounter in encounters:
                        if 'phase' in encounter:
                            phases_found.add(encounter['phase'])
                    
                    if phases_found:
                        self.log_test("Boss Phases Data", "PASS",
                                    {"phases_found": sorted(list(phases_found))})
                    else:
                        self.log_test("Boss Phases Data", "FAIL",
                                    {"error": "No phase data found in encounters"})
                else:
                    self.log_test("Boss Encounters Data", "FAIL",
                                {"error": "No encounters found in heroic data"})
            else:
                self.log_test("Heroic Data File", "FAIL",
                            {"error": f"File not found: {heroic_path}"})
            
            return True
            
        except Exception as e:
            self.log_test("Boss Phases Functionality", "FAIL", {"error": str(e)})
            return False
    
    def test_markdown_yaml_structure(self) -> bool:
        """Test Markdown + YAML based structure"""
        print("\n📝 Testing Markdown + YAML Structure...")
        
        try:
            # Check heroic data files for YAML structure
            heroic_path = "data/heroics/axkva_min.yml"
            if os.path.exists(heroic_path):
                with open(heroic_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for YAML structure
                if content.strip().startswith('#') or 'metadata:' in content:
                    self.log_test("YAML Structure", "PASS")
                else:
                    self.log_test("YAML Structure", "FAIL",
                                {"error": "File doesn't appear to be valid YAML"})
                
                # Check for embedded markdown/HTML in tactics
                if 'general_tactics:' in content and ('|' in content or '<' in content):
                    self.log_test("Markdown/HTML Content", "PASS")
                else:
                    self.log_test("Markdown/HTML Content", "FAIL",
                                {"error": "No markdown/HTML content found in tactics"})
                
                # Parse as YAML to verify structure
                try:
                    yaml_data = yaml.safe_load(content)
                    
                    # Check for required sections
                    required_sections = [
                        'heroic_id',
                        'name',
                        'encounters',
                        'general_tactics'
                    ]
                    
                    missing_sections = [section for section in required_sections
                                      if section not in yaml_data]
                    
                    if missing_sections:
                        self.log_test("YAML Structure Validation", "FAIL",
                                    {"missing_sections": missing_sections})
                    else:
                        self.log_test("YAML Structure Validation", "PASS",
                                    {"sections_found": len(yaml_data.keys())})
                
                except yaml.YAMLError as e:
                    self.log_test("YAML Parsing", "FAIL",
                                {"error": f"YAML parsing error: {str(e)}"})
            else:
                self.log_test("YAML File Existence", "FAIL",
                            {"error": f"File not found: {heroic_path}"})
            
            return True
            
        except Exception as e:
            self.log_test("Markdown + YAML Structure", "FAIL", {"error": str(e)})
            return False
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print("\n📊 Generating Test Report...")
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warning_tests = len([t for t in self.test_results if t['status'] in ['WARN', 'INFO']])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'batch_id': 'BATCH_193',
            'test_name': 'Heroic Guide Pages with Map Markers + Loot Links',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'warnings': warning_tests,
                'success_rate': round(success_rate, 2)
            },
            'test_results': self.test_results,
            'overall_status': 'PASS' if failed_tests == 0 else 'FAIL',
            'features_tested': [
                'Dynamic page generation with 11ty',
                'Interactive map viewer with Svelte',
                'Enhanced loot table integration',
                'Boss phase toggle functionality',
                'Markdown + YAML content structure',
                'Map markers and navigation',
                'Heroic data organization'
            ],
            'recommendations': []
        }
        
        # Add recommendations based on results
        if failed_tests > 0:
            report['recommendations'].append("Address failed test cases to ensure full heroic guide functionality")
        
        if warning_tests > 0:
            report['recommendations'].append("Review warning items for potential improvements")
        
        if success_rate >= 95:
            report['recommendations'].append("Heroic guide system appears to be fully functional")
        elif success_rate >= 80:
            report['recommendations'].append("Heroic guide system is mostly functional with minor issues")
        else:
            report['recommendations'].append("Heroic guide system requires significant fixes")
        
        # Save report
        report_file = f"BATCH_193_TEST_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Test Report saved to: {report_file}")
        return report
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all heroic guide system tests"""
        print("🚀 Starting Heroic Guide Pages Test Suite...")
        print("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_page_generator_structure,
            self.test_heroic_data_structure,
            self.test_map_data_structure,
            self.test_map_viewer_component,
            self.test_loot_table_integration,
            self.test_boss_phases_functionality,
            self.test_markdown_yaml_structure
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(f"Test Method {test_method.__name__}", "FAIL",
                            {"error": str(e)})
        
        # Generate final report
        report = self.generate_test_report()
        
        print("\n" + "=" * 60)
        print(f"🎯 Test Suite Complete!")
        print(f"📊 Overall Status: {'✅ PASS' if report['overall_status'] == 'PASS' else '❌ FAIL'}")
        print(f"📈 Success Rate: {report['summary']['success_rate']}%")
        print(f"📋 Tests: {report['summary']['passed']}/{report['summary']['total_tests']} passed")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        return report

def main():
    """Main test runner"""
    tester = HeroicGuidesTester()
    
    try:
        # Run all tests
        report = tester.run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if report['overall_status'] == 'PASS' else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
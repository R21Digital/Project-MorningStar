#!/usr/bin/env python3
"""
Batch 155 - Build Analyzer Assistant (AskMrRoboto Alpha)
Demo Script

Purpose: Demonstrates Phase 1 of the build evaluator based on gear, stats, and role.
Features: Stat optimization recommendations, armor suggestions, and tape advice.
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.build_analyzer import BuildAnalyzer, analyze_character_build, format_build_report


class BuildAnalyzerDemo:
    """Demo class for the Build Analyzer Assistant"""
    
    def __init__(self):
        self.analyzer = BuildAnalyzer()
        self.sample_characters = self._create_sample_characters()
    
    def _create_sample_characters(self) -> Dict[str, Dict]:
        """Create sample character data for demonstration"""
        return {
            "rifleman_dps": {
                "name": "SniperX",
                "profession": "rifleman",
                "role": "dps",
                "stats": {
                    "damage": 180,
                    "accuracy": 150,
                    "critical": 80,
                    "constitution": 120,
                    "stamina": 100
                }
            },
            "medic_healer": {
                "name": "HealMaster",
                "profession": "medic",
                "role": "healer",
                "stats": {
                    "healing": 200,
                    "constitution": 180,
                    "stamina": 150,
                    "accuracy": 100,
                    "critical": 40
                }
            },
            "brawler_tank": {
                "name": "TankBuster",
                "profession": "brawler",
                "role": "tank",
                "stats": {
                    "constitution": 250,
                    "stamina": 200,
                    "defense": 150,
                    "damage": 80,
                    "accuracy": 60
                }
            },
            "pistoleer_dps": {
                "name": "QuickDraw",
                "profession": "pistoleer",
                "role": "dps",
                "stats": {
                    "damage": 160,
                    "accuracy": 120,
                    "critical": 120,
                    "constitution": 100,
                    "stamina": 80
                }
            },
            "under_optimized_rifleman": {
                "name": "NewbieRifleman",
                "profession": "rifleman",
                "role": "dps",
                "stats": {
                    "damage": 80,
                    "accuracy": 60,
                    "critical": 30,
                    "constitution": 80,
                    "stamina": 60
                }
            }
        }
    
    def run_demo(self):
        """Run the complete demo"""
        print("=" * 80)
        print("BATCH 155 - BUILD ANALYZER ASSISTANT (ASKMRROBOTO ALPHA)")
        print("=" * 80)
        print("Phase 1: Stat optimization, armor suggestions, and tape advice")
        print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test data loading
        self._test_data_loading()
        
        # Analyze sample characters
        self._analyze_sample_characters()
        
        # Test individual components
        self._test_individual_components()
        
        # Performance test
        self._performance_test()
        
        print("=" * 80)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 80)
    
    def _test_data_loading(self):
        """Test that data files are loaded correctly"""
        print("TESTING DATA LOADING:")
        print("-" * 20)
        
        if self.analyzer.breakpoints_data:
            print("✅ Breakpoints data loaded successfully")
            roles = list(self.analyzer.breakpoints_data.get('roles', {}).keys())
            print(f"   Available roles: {', '.join(roles)}")
        else:
            print("❌ Breakpoints data failed to load")
        
        if self.analyzer.meta_armor_data:
            print("✅ Meta armor data loaded successfully")
            armor_roles = list(self.analyzer.meta_armor_data.get('armor_recommendations', {}).keys())
            print(f"   Available armor roles: {', '.join(armor_roles)}")
        else:
            print("❌ Meta armor data failed to load")
        
        print()
    
    def _analyze_sample_characters(self):
        """Analyze all sample characters"""
        print("ANALYZING SAMPLE CHARACTERS:")
        print("-" * 30)
        
        for char_name, char_data in self.sample_characters.items():
            print(f"\nAnalyzing {char_data['name']} ({char_data['profession']}/{char_data['role']}):")
            print("-" * 50)
            
            try:
                analysis = self.analyzer.analyze_character(char_data)
                
                # Display key results
                print(f"Overall Score: {analysis.overall_score:.1f}/100")
                print(f"Primary Role: {analysis.primary_role}")
                print(f"Secondary Role: {analysis.secondary_role}")
                
                # Show stat status
                optimal_count = sum(1 for stat in analysis.stat_analysis.values() if stat.status == "optimal")
                total_stats = len(analysis.stat_analysis)
                print(f"Optimal Stats: {optimal_count}/{total_stats}")
                
                # Show top armor recommendation
                if analysis.armor_recommendations:
                    top_armor = analysis.armor_recommendations[0]
                    print(f"Top Armor: {top_armor.name} ({top_armor.priority} priority)")
                
                # Show priority improvements
                if analysis.priority_improvements:
                    print("Top Priority:")
                    print(f"  → {analysis.priority_improvements[0]}")
                
            except Exception as e:
                print(f"❌ Error analyzing {char_data['name']}: {e}")
        
        print()
    
    def _test_individual_components(self):
        """Test individual components of the analyzer"""
        print("TESTING INDIVIDUAL COMPONENTS:")
        print("-" * 32)
        
        # Test with a well-optimized character
        test_char = self.sample_characters["rifleman_dps"]
        
        # Test stat analysis
        print("Testing Stat Analysis:")
        analysis = self.analyzer.analyze_character(test_char)
        for stat_name, stat_analysis in analysis.stat_analysis.items():
            status_icon = "✅" if stat_analysis.status == "optimal" else "⚠️" if stat_analysis.status == "below_optimal" else "❌"
            print(f"  {status_icon} {stat_name}: {stat_analysis.current_value}/{stat_analysis.optimal_target}")
        
        # Test armor recommendations
        print("\nTesting Armor Recommendations:")
        for i, armor in enumerate(analysis.armor_recommendations[:2], 1):
            print(f"  {i}. {armor.name} - {armor.reason}")
        
        # Test tape recommendations
        print("\nTesting Tape Recommendations:")
        print(f"  Primary: {', '.join(analysis.tape_recommendations.primary_tapes)}")
        print(f"  Secondary: {', '.join(analysis.tape_recommendations.secondary_tapes)}")
        print(f"  Avoid: {', '.join(analysis.tape_recommendations.avoid_tapes)}")
        
        print()
    
    def _performance_test(self):
        """Test performance with multiple analyses"""
        print("PERFORMANCE TEST:")
        print("-" * 16)
        
        import time
        
        start_time = time.time()
        
        # Run multiple analyses
        for i in range(10):
            for char_data in self.sample_characters.values():
                analysis = self.analyzer.analyze_character(char_data)
        
        end_time = time.time()
        total_time = end_time - start_time
        total_analyses = 10 * len(self.sample_characters)
        
        print(f"Completed {total_analyses} analyses in {total_time:.3f} seconds")
        print(f"Average time per analysis: {(total_time/total_analyses)*1000:.2f}ms")
        
        print()
    
    def generate_detailed_report(self, character_name: str = None):
        """Generate a detailed report for a specific character"""
        if character_name is None:
            # Use the first character
            char_data = list(self.sample_characters.values())[0]
        else:
            char_data = self.sample_characters.get(character_name)
            if not char_data:
                print(f"Character '{character_name}' not found")
                return
        
        print("=" * 80)
        print(f"DETAILED BUILD ANALYSIS REPORT")
        print("=" * 80)
        
        analysis = self.analyzer.analyze_character(char_data)
        report = self.analyzer.format_analysis_report(analysis)
        print(report)
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("TESTING EDGE CASES:")
        print("-" * 20)
        
        # Test with missing data
        print("Testing with missing stats:")
        incomplete_char = {
            "name": "IncompleteChar",
            "profession": "rifleman",
            "role": "dps",
            "stats": {
                "damage": 100
                # Missing other stats
            }
        }
        
        try:
            analysis = self.analyzer.analyze_character(incomplete_char)
            print(f"✅ Analysis completed with score: {analysis.overall_score:.1f}")
        except Exception as e:
            print(f"❌ Error with incomplete data: {e}")
        
        # Test with invalid role
        print("\nTesting with invalid role:")
        invalid_role_char = {
            "name": "InvalidRole",
            "profession": "rifleman",
            "role": "invalid_role",
            "stats": {
                "damage": 100,
                "accuracy": 80,
                "critical": 50
            }
        }
        
        try:
            analysis = self.analyzer.analyze_character(invalid_role_char)
            print(f"✅ Analysis completed with score: {analysis.overall_score:.1f}")
        except Exception as e:
            print(f"❌ Error with invalid role: {e}")
        
        print()


def main():
    """Main demo function"""
    demo = BuildAnalyzerDemo()
    
    # Run the main demo
    demo.run_demo()
    
    # Generate a detailed report
    demo.generate_detailed_report("rifleman_dps")
    
    # Test edge cases
    demo.test_edge_cases()
    
    print("\n" + "=" * 80)
    print("BATCH 155 DEMO COMPLETED")
    print("Features demonstrated:")
    print("✅ Stat optimization recommendations")
    print("✅ Armor suggestions based on role and profession")
    print("✅ Tape advice for optimal performance")
    print("✅ Overall build scoring system")
    print("✅ Priority improvement suggestions")
    print("✅ Detailed analysis reports")
    print("=" * 80)


if __name__ == "__main__":
    main() 
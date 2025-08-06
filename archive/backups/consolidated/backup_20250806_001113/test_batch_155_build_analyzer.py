#!/usr/bin/env python3
"""
Batch 155 - Build Analyzer Assistant (AskMrRoboto Alpha)
Test Suite

Comprehensive testing for the build analyzer functionality including:
- Data loading and validation
- Stat analysis and scoring
- Armor recommendations
- Tape recommendations
- Edge cases and error handling
"""

import json
import sys
import os
import unittest
from datetime import datetime
from typing import Dict, List
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.build_analyzer import (
    BuildAnalyzer, 
    BuildAnalysis, 
    StatAnalysis, 
    ArmorRecommendation, 
    TapeRecommendation,
    analyze_character_build,
    format_build_report
)


class TestBuildAnalyzer(unittest.TestCase):
    """Test suite for the Build Analyzer Assistant"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = BuildAnalyzer()
        
        # Sample character data for testing
        self.sample_rifleman = {
            "name": "TestRifleman",
            "profession": "rifleman",
            "role": "dps",
            "stats": {
                "damage": 180,
                "accuracy": 150,
                "critical": 80,
                "constitution": 120,
                "stamina": 100
            }
        }
        
        self.sample_medic = {
            "name": "TestMedic",
            "profession": "medic",
            "role": "healer",
            "stats": {
                "healing": 200,
                "constitution": 180,
                "stamina": 150,
                "accuracy": 100,
                "critical": 40
            }
        }
        
        self.sample_brawler = {
            "name": "TestBrawler",
            "profession": "brawler",
            "role": "tank",
            "stats": {
                "constitution": 250,
                "stamina": 200,
                "defense": 150,
                "damage": 80,
                "accuracy": 60
            }
        }
    
    def test_data_loading(self):
        """Test that data files are loaded correctly"""
        print("Testing data loading...")
        
        # Test breakpoints data
        self.assertIsNotNone(self.analyzer.breakpoints_data)
        self.assertIn('roles', self.analyzer.breakpoints_data)
        self.assertIn('professions', self.analyzer.breakpoints_data)
        
        # Test meta armor data
        self.assertIsNotNone(self.analyzer.meta_armor_data)
        self.assertIn('armor_recommendations', self.analyzer.meta_armor_data)
        self.assertIn('tape_recommendations', self.analyzer.meta_armor_data)
        
        print("✅ Data loading tests passed")
    
    def test_rifleman_analysis(self):
        """Test analysis of a rifleman character"""
        print("Testing rifleman analysis...")
        
        analysis = self.analyzer.analyze_character(self.sample_rifleman)
        
        # Basic structure tests
        self.assertIsInstance(analysis, BuildAnalysis)
        self.assertEqual(analysis.character_name, "TestRifleman")
        self.assertEqual(analysis.profession, "rifleman")
        self.assertEqual(analysis.primary_role, "dps")
        self.assertEqual(analysis.secondary_role, "support")
        
        # Score should be reasonable
        self.assertGreaterEqual(analysis.overall_score, 0)
        self.assertLessEqual(analysis.overall_score, 100)
        
        # Should have stat analysis
        self.assertIsInstance(analysis.stat_analysis, dict)
        self.assertGreater(len(analysis.stat_analysis), 0)
        
        # Should have armor recommendations
        self.assertIsInstance(analysis.armor_recommendations, list)
        self.assertGreater(len(analysis.armor_recommendations), 0)
        
        # Should have tape recommendations
        self.assertIsInstance(analysis.tape_recommendations, TapeRecommendation)
        
        print("✅ Rifleman analysis tests passed")
    
    def test_medic_analysis(self):
        """Test analysis of a medic character"""
        print("Testing medic analysis...")
        
        analysis = self.analyzer.analyze_character(self.sample_medic)
        
        # Basic structure tests
        self.assertEqual(analysis.character_name, "TestMedic")
        self.assertEqual(analysis.profession, "medic")
        self.assertEqual(analysis.primary_role, "healer")
        self.assertEqual(analysis.secondary_role, "support")
        
        # Should have healing stat analysis
        self.assertIn('healing', analysis.stat_analysis)
        
        # Should have armor recommendations for healer
        self.assertGreater(len(analysis.armor_recommendations), 0)
        
        print("✅ Medic analysis tests passed")
    
    def test_brawler_analysis(self):
        """Test analysis of a brawler character"""
        print("Testing brawler analysis...")
        
        analysis = self.analyzer.analyze_character(self.sample_brawler)
        
        # Basic structure tests
        self.assertEqual(analysis.character_name, "TestBrawler")
        self.assertEqual(analysis.profession, "brawler")
        self.assertEqual(analysis.primary_role, "tank")
        self.assertEqual(analysis.secondary_role, "dps")
        
        # Should have defense stat analysis
        self.assertIn('defense', analysis.stat_analysis)
        
        # Should have armor recommendations for tank
        self.assertGreater(len(analysis.armor_recommendations), 0)
        
        print("✅ Brawler analysis tests passed")
    
    def test_stat_analysis_components(self):
        """Test individual stat analysis components"""
        print("Testing stat analysis components...")
        
        analysis = self.analyzer.analyze_character(self.sample_rifleman)
        
        for stat_name, stat_analysis in analysis.stat_analysis.items():
            # Test StatAnalysis structure
            self.assertIsInstance(stat_analysis, StatAnalysis)
            self.assertIsInstance(stat_analysis.current_value, int)
            self.assertIsInstance(stat_analysis.minimum_target, int)
            self.assertIsInstance(stat_analysis.optimal_target, int)
            self.assertIsInstance(stat_analysis.maximum_target, int)
            self.assertIsInstance(stat_analysis.priority, str)
            self.assertIsInstance(stat_analysis.status, str)
            self.assertIsInstance(stat_analysis.recommendation, str)
            
            # Test value ranges
            self.assertGreaterEqual(stat_analysis.current_value, 0)
            self.assertGreaterEqual(stat_analysis.minimum_target, 0)
            self.assertGreaterEqual(stat_analysis.optimal_target, stat_analysis.minimum_target)
            self.assertGreaterEqual(stat_analysis.maximum_target, stat_analysis.optimal_target)
            
            # Test status values
            self.assertIn(stat_analysis.status, ["optimal", "below_minimum", "below_optimal", "above_optimal"])
            
            # Test priority values
            self.assertIn(stat_analysis.priority, ["low", "medium", "high", "very_high"])
        
        print("✅ Stat analysis component tests passed")
    
    def test_armor_recommendations(self):
        """Test armor recommendation generation"""
        print("Testing armor recommendations...")
        
        analysis = self.analyzer.analyze_character(self.sample_rifleman)
        
        for armor_rec in analysis.armor_recommendations:
            # Test ArmorRecommendation structure
            self.assertIsInstance(armor_rec, ArmorRecommendation)
            self.assertIsInstance(armor_rec.name, str)
            self.assertIsInstance(armor_rec.reason, str)
            self.assertIsInstance(armor_rec.priority, str)
            self.assertIsInstance(armor_rec.stats, dict)
            self.assertIsInstance(armor_rec.cost, str)
            self.assertIsInstance(armor_rec.enhancement_suggestions, list)
            
            # Test priority values
            self.assertIn(armor_rec.priority, ["low", "medium", "high", "very_high"])
            
            # Test cost values
            self.assertIn(armor_rec.cost, ["low", "medium", "high"])
            
            # Should have enhancement suggestions
            self.assertGreater(len(armor_rec.enhancement_suggestions), 0)
        
        print("✅ Armor recommendation tests passed")
    
    def test_tape_recommendations(self):
        """Test tape recommendation generation"""
        print("Testing tape recommendations...")
        
        analysis = self.analyzer.analyze_character(self.sample_rifleman)
        
        # Test TapeRecommendation structure
        self.assertIsInstance(analysis.tape_recommendations, TapeRecommendation)
        self.assertIsInstance(analysis.tape_recommendations.primary_tapes, list)
        self.assertIsInstance(analysis.tape_recommendations.secondary_tapes, list)
        self.assertIsInstance(analysis.tape_recommendations.avoid_tapes, list)
        self.assertIsInstance(analysis.tape_recommendations.reasoning, str)
        
        # Should have recommendations
        self.assertGreater(len(analysis.tape_recommendations.primary_tapes), 0)
        self.assertGreater(len(analysis.tape_recommendations.secondary_tapes), 0)
        
        print("✅ Tape recommendation tests passed")
    
    def test_score_calculation(self):
        """Test overall score calculation"""
        print("Testing score calculation...")
        
        # Test with well-optimized character
        analysis = self.analyzer.analyze_character(self.sample_rifleman)
        self.assertGreaterEqual(analysis.overall_score, 0)
        self.assertLessEqual(analysis.overall_score, 100)
        
        # Test with under-optimized character
        under_optimized = {
            "name": "UnderOptimized",
            "profession": "rifleman",
            "role": "dps",
            "stats": {
                "damage": 50,
                "accuracy": 30,
                "critical": 20,
                "constitution": 60,
                "stamina": 40
            }
        }
        
        analysis2 = self.analyzer.analyze_character(under_optimized)
        self.assertLess(analysis2.overall_score, analysis.overall_score)
        
        print("✅ Score calculation tests passed")
    
    def test_priority_improvements(self):
        """Test priority improvement generation"""
        print("Testing priority improvements...")
        
        analysis = self.analyzer.analyze_character(self.sample_rifleman)
        
        # Should have priority improvements list
        self.assertIsInstance(analysis.priority_improvements, list)
        
        # Should not have more than 5 priority improvements
        self.assertLessEqual(len(analysis.priority_improvements), 5)
        
        # Each improvement should be a string
        for improvement in analysis.priority_improvements:
            self.assertIsInstance(improvement, str)
            self.assertGreater(len(improvement), 0)
        
        print("✅ Priority improvements tests passed")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("Testing edge cases...")
        
        # Test with missing stats
        incomplete_char = {
            "name": "Incomplete",
            "profession": "rifleman",
            "role": "dps",
            "stats": {
                "damage": 100
                # Missing other stats
            }
        }
        
        try:
            analysis = self.analyzer.analyze_character(incomplete_char)
            self.assertIsInstance(analysis, BuildAnalysis)
            print("✅ Incomplete character test passed")
        except Exception as e:
            self.fail(f"Incomplete character should not raise exception: {e}")
        
        # Test with invalid role
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
            self.assertIsInstance(analysis, BuildAnalysis)
            print("✅ Invalid role test passed")
        except Exception as e:
            self.fail(f"Invalid role should not raise exception: {e}")
        
        # Test with empty stats
        empty_stats_char = {
            "name": "EmptyStats",
            "profession": "rifleman",
            "role": "dps",
            "stats": {}
        }
        
        try:
            analysis = self.analyzer.analyze_character(empty_stats_char)
            self.assertIsInstance(analysis, BuildAnalysis)
            self.assertEqual(analysis.overall_score, 0.0)
            print("✅ Empty stats test passed")
        except Exception as e:
            self.fail(f"Empty stats should not raise exception: {e}")
        
        print("✅ Edge case tests passed")
    
    def test_report_formatting(self):
        """Test report formatting functionality"""
        print("Testing report formatting...")
        
        analysis = self.analyzer.analyze_character(self.sample_rifleman)
        report = self.analyzer.format_analysis_report(analysis)
        
        # Should return a string
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 0)
        
        # Should contain key sections
        self.assertIn("BUILD ANALYSIS REPORT", report)
        self.assertIn("STAT ANALYSIS", report)
        self.assertIn("ARMOR RECOMMENDATIONS", report)
        self.assertIn("TAPE RECOMMENDATIONS", report)
        self.assertIn("PRIORITY IMPROVEMENTS", report)
        self.assertIn("SUMMARY", report)
        
        # Should contain character name
        self.assertIn("TestRifleman", report)
        
        print("✅ Report formatting tests passed")
    
    def test_convenience_functions(self):
        """Test convenience functions"""
        print("Testing convenience functions...")
        
        # Test analyze_character_build
        analysis = analyze_character_build(self.sample_rifleman)
        self.assertIsInstance(analysis, BuildAnalysis)
        
        # Test format_build_report
        report = format_build_report(self.sample_rifleman)
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 0)
        
        print("✅ Convenience function tests passed")
    
    def test_performance(self):
        """Test performance with multiple analyses"""
        print("Testing performance...")
        
        import time
        
        start_time = time.time()
        
        # Run multiple analyses
        for i in range(10):
            analysis = self.analyzer.analyze_character(self.sample_rifleman)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 10 analyses in reasonable time (less than 5 seconds)
        self.assertLess(total_time, 5.0)
        
        avg_time = total_time / 10
        print(f"Average analysis time: {avg_time*1000:.2f}ms")
        
        print("✅ Performance tests passed")
    
    def test_data_validation(self):
        """Test data validation and error handling"""
        print("Testing data validation...")
        
        # Test with missing data files
        with patch.object(self.analyzer, 'breakpoints_data', None):
            with self.assertRaises(ValueError):
                self.analyzer.analyze_character(self.sample_rifleman)
        
        with patch.object(self.analyzer, 'meta_armor_data', None):
            with self.assertRaises(ValueError):
                self.analyzer.analyze_character(self.sample_rifleman)
        
        print("✅ Data validation tests passed")


class TestBuildAnalyzerIntegration(unittest.TestCase):
    """Integration tests for the Build Analyzer"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.analyzer = BuildAnalyzer()
    
    def test_full_workflow(self):
        """Test the complete workflow from character data to report"""
        print("Testing full workflow...")
        
        # Sample character data
        character_data = {
            "name": "IntegrationTest",
            "profession": "rifleman",
            "role": "dps",
            "stats": {
                "damage": 200,
                "accuracy": 180,
                "critical": 100,
                "constitution": 150,
                "stamina": 120
            }
        }
        
        # Step 1: Analyze character
        analysis = self.analyzer.analyze_character(character_data)
        self.assertIsInstance(analysis, BuildAnalysis)
        
        # Step 2: Generate report
        report = self.analyzer.format_analysis_report(analysis)
        self.assertIsInstance(report, str)
        
        # Step 3: Verify report contains expected information
        self.assertIn("IntegrationTest", report)
        self.assertIn("rifleman", report)
        self.assertIn("dps", report)
        
        print("✅ Full workflow test passed")
    
    def test_multiple_professions(self):
        """Test analysis across multiple professions"""
        print("Testing multiple professions...")
        
        professions = ["rifleman", "pistoleer", "medic", "brawler"]
        roles = ["dps", "dps", "healer", "tank"]
        
        for profession, role in zip(professions, roles):
            character_data = {
                "name": f"Test{profession.title()}",
                "profession": profession,
                "role": role,
                "stats": {
                    "damage": 150,
                    "accuracy": 120,
                    "critical": 80,
                    "constitution": 100,
                    "stamina": 80
                }
            }
            
            # Add role-specific stats
            if role == "healer":
                character_data["stats"]["healing"] = 180
            elif role == "tank":
                character_data["stats"]["defense"] = 120
            
            analysis = self.analyzer.analyze_character(character_data)
            self.assertEqual(analysis.profession, profession)
            self.assertEqual(analysis.primary_role, role)
        
        print("✅ Multiple professions test passed")


def run_performance_benchmark():
    """Run performance benchmark"""
    print("\n" + "=" * 60)
    print("PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    analyzer = BuildAnalyzer()
    
    # Create test characters
    test_characters = []
    for i in range(20):
        test_characters.append({
            "name": f"BenchmarkChar{i}",
            "profession": "rifleman",
            "role": "dps",
            "stats": {
                "damage": 150 + i,
                "accuracy": 120 + i,
                "critical": 80 + i,
                "constitution": 100 + i,
                "stamina": 80 + i
            }
        })
    
    import time
    
    # Warm up
    for char in test_characters[:5]:
        analyzer.analyze_character(char)
    
    # Benchmark
    start_time = time.time()
    
    for char in test_characters:
        analysis = analyzer.analyze_character(char)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"Analyzed {len(test_characters)} characters in {total_time:.3f} seconds")
    print(f"Average time per analysis: {(total_time/len(test_characters))*1000:.2f}ms")
    print(f"Throughput: {len(test_characters)/total_time:.1f} analyses/second")


def main():
    """Main test runner"""
    print("=" * 80)
    print("BATCH 155 - BUILD ANALYZER ASSISTANT TEST SUITE")
    print("=" * 80)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance benchmark
    run_performance_benchmark()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main() 
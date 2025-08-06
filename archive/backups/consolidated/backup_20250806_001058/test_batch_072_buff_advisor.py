#!/usr/bin/env python3
"""
Test suite for Batch 072 - Buff Advisor + Stat-Based Build Recommender

This test suite validates all components of the buff advisor system:
- Character stat analysis
- Buff food and entertainer dance recommendations  
- Armor and weapon setup recommendations
- Build integration with Batch 070
"""

import unittest
import json
import tempfile
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
import sys
sys.path.insert(0, str(project_root))

from modules.buff_advisor import (
    BuffAdvisor, create_buff_advisor,
    CharacterStatAnalyzer, create_stat_analyzer,
    BuffRecommender, create_buff_recommender,
    TemplateRecommender, create_template_recommender,
    BuildIntegration, create_build_integration
)


class TestCharacterStatAnalyzer(unittest.TestCase):
    """Test the CharacterStatAnalyzer component."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = create_stat_analyzer()
        self.sample_stats = {
            "strength": 95,
            "agility": 110,
            "constitution": 105,
            "stamina": 88,
            "mind": 120,
            "focus": 115,
            "willpower": 92
        }

    def test_parse_stats_log(self):
        """Test parsing stats from log content."""
        log_content = """
        Character: TestPlayer
        Strength: 95
        Agility: 110
        Constitution: 105
        Stamina: 88
        Mind: 120
        Focus: 115
        Willpower: 92
        """
        
        stats = self.analyzer.parse_stats_log(log_content)
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats["strength"], 95)
        self.assertEqual(stats["agility"], 110)
        self.assertEqual(stats["constitution"], 105)
        self.assertEqual(stats["stamina"], 88)
        self.assertEqual(stats["mind"], 120)
        self.assertEqual(stats["focus"], 115)
        self.assertEqual(stats["willpower"], 92)

    def test_parse_stats_log_invalid(self):
        """Test parsing invalid stats log."""
        log_content = "Invalid log content"
        stats = self.analyzer.parse_stats_log(log_content)
        
        self.assertIsInstance(stats, dict)
        # Should return dict with 0 values for all stats when parsing fails
        self.assertEqual(len(stats), 7)  # All 7 stats with 0 values
        for stat_name in ["strength", "agility", "constitution", "stamina", "mind", "focus", "willpower"]:
            self.assertEqual(stats[stat_name], 0)

    def test_analyze_stat_distribution(self):
        """Test stat distribution analysis."""
        analysis = self.analyzer.analyze_stat_distribution(self.sample_stats)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn("total_stats", analysis)
        self.assertIn("average_stat", analysis)
        self.assertIn("weakest_stats", analysis)
        self.assertIn("strongest_stats", analysis)
        self.assertIn("optimization_opportunities", analysis)
        
        self.assertEqual(analysis["total_stats"], 725)
        self.assertAlmostEqual(analysis["average_stat"], 103.57, places=1)

    def test_get_optimization_priorities_pve_damage(self):
        """Test getting optimization priorities for PvE damage."""
        priorities = self.analyzer.get_optimization_priorities(self.sample_stats, "pve_damage")
        
        self.assertIsInstance(priorities, list)
        self.assertGreater(len(priorities), 0)
        
        # Should prioritize strength, agility, constitution for PvE damage
        priority_stats = [p["stat"] for p in priorities]
        self.assertIn("strength", priority_stats)
        self.assertIn("agility", priority_stats)
        self.assertIn("constitution", priority_stats)

    def test_get_optimization_priorities_healing(self):
        """Test getting optimization priorities for healing."""
        priorities = self.analyzer.get_optimization_priorities(self.sample_stats, "healing")
        
        self.assertIsInstance(priorities, list)
        self.assertGreater(len(priorities), 0)
        
        # Should prioritize mind, focus, constitution for healing
        priority_stats = [p["stat"] for p in priorities]
        self.assertIn("mind", priority_stats)
        self.assertIn("focus", priority_stats)
        self.assertIn("constitution", priority_stats)

    def test_categorize_stat_level(self):
        """Test stat level categorization."""
        self.assertEqual(self.analyzer._categorize_stat_level(50), "low")
        self.assertEqual(self.analyzer._categorize_stat_level(100), "medium")
        self.assertEqual(self.analyzer._categorize_stat_level(150), "high")
        self.assertEqual(self.analyzer._categorize_stat_level(200), "excellent")


class TestBuffRecommender(unittest.TestCase):
    """Test the BuffRecommender component."""

    def setUp(self):
        """Set up test fixtures."""
        self.recommender = create_buff_recommender()
        self.sample_stats = {
            "strength": 95,
            "agility": 110,
            "constitution": 105,
            "stamina": 88,
            "mind": 120,
            "focus": 115,
            "willpower": 92
        }

    def test_recommend_buff_food(self):
        """Test buff food recommendations."""
        recommendations = self.recommender.recommend_buff_food(
            self.sample_stats, "pve_damage", "medium"
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        for rec in recommendations:
            self.assertIn("type", rec)
            self.assertEqual(rec["type"], "buff_food")
            self.assertIn("stat_target", rec)
            self.assertIn("items", rec)
            self.assertIn("stat_bonus", rec)
            self.assertIn("duration", rec)
            self.assertIn("cost", rec)

    def test_recommend_entertainer_dances(self):
        """Test entertainer dance recommendations."""
        recommendations = self.recommender.recommend_entertainer_dances(
            self.sample_stats, "pve_damage", "medium"
        )
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        for rec in recommendations:
            self.assertIn("type", rec)
            self.assertEqual(rec["type"], "entertainer_dance")
            self.assertIn("dance_name", rec)
            self.assertIn("stat_target", rec)
            self.assertIn("stat_bonus", rec)
            self.assertIn("duration", rec)
            self.assertIn("entertainer_level", rec)

    def test_get_combined_recommendations(self):
        """Test combined buff recommendations."""
        combined = self.recommender.get_combined_recommendations(
            self.sample_stats, "pve_damage", "medium"
        )
        
        self.assertIsInstance(combined, dict)
        self.assertIn("timestamp", combined)
        self.assertIn("optimization_type", combined)
        self.assertIn("budget", combined)
        self.assertIn("buff_food", combined)
        self.assertIn("entertainer_dances", combined)
        self.assertIn("total_expected_improvements", combined)
        self.assertIn("recommendation_count", combined)

    def test_budget_filtering(self):
        """Test that budget filtering works correctly."""
        # Test low budget
        low_budget_recs = self.recommender.recommend_buff_food(
            self.sample_stats, "pve_damage", "low"
        )
        
        # Test high budget
        high_budget_recs = self.recommender.recommend_buff_food(
            self.sample_stats, "pve_damage", "high"
        )
        
        # High budget should allow more expensive items
        self.assertGreaterEqual(len(high_budget_recs), len(low_budget_recs))


class TestTemplateRecommender(unittest.TestCase):
    """Test the TemplateRecommender component."""

    def setUp(self):
        """Set up test fixtures."""
        self.recommender = create_template_recommender()
        self.sample_stats = {
            "strength": 95,
            "agility": 110,
            "constitution": 105,
            "stamina": 88,
            "mind": 120,
            "focus": 115,
            "willpower": 92
        }
        self.sample_build_data = {
            "professions": ["rifleman", "medic"],
            "weapons": ["rifle", "carbine"],
            "combat_style": "hybrid"
        }

    def test_recommend_armor_setup(self):
        """Test armor setup recommendations."""
        recommendation = self.recommender.recommend_armor_setup(
            self.sample_stats, self.sample_build_data, "balanced", "medium"
        )
        
        self.assertIsInstance(recommendation, dict)
        self.assertIn("template_name", recommendation)
        self.assertIn("template_type", recommendation)
        self.assertIn("combat_style", recommendation)
        self.assertIn("cost", recommendation)
        self.assertIn("slots", recommendation)
        self.assertIn("set_bonus", recommendation)
        self.assertIn("total_stat_bonuses", recommendation)

    def test_recommend_weapon_setup(self):
        """Test weapon setup recommendations."""
        recommendation = self.recommender.recommend_weapon_setup(
            self.sample_stats, self.sample_build_data
        )
        
        self.assertIsInstance(recommendation, dict)
        self.assertIn("weapon_name", recommendation)
        self.assertIn("weapon_type", recommendation)
        self.assertIn("range", recommendation)
        self.assertIn("damage_type", recommendation)
        self.assertIn("weapon_bonus", recommendation)

    def test_get_complete_template_recommendation(self):
        """Test complete template recommendations."""
        complete = self.recommender.get_complete_template_recommendation(
            self.sample_stats, self.sample_build_data, "balanced", "medium"
        )
        
        self.assertIsInstance(complete, dict)
        self.assertIn("timestamp", complete)
        self.assertIn("optimization_type", complete)
        self.assertIn("budget", complete)
        self.assertIn("armor_setup", complete)
        self.assertIn("weapon_setup", complete)
        self.assertIn("total_expected_improvements", complete)
        self.assertIn("build_data", complete)

    def test_armor_template_selection(self):
        """Test armor template selection based on build data."""
        # Test rifleman build
        rifleman_build = {"professions": ["rifleman"]}
        rifleman_rec = self.recommender.recommend_armor_setup(
            self.sample_stats, rifleman_build, "pve_damage", "medium"
        )
        self.assertIn("rifleman", rifleman_rec["template_type"])
        
        # Test medic build
        medic_build = {"professions": ["medic"]}
        medic_rec = self.recommender.recommend_armor_setup(
            self.sample_stats, medic_build, "healing", "medium"
        )
        self.assertIn("medic", medic_rec["template_type"])


class TestBuildIntegration(unittest.TestCase):
    """Test the BuildIntegration component."""

    def setUp(self):
        """Set up test fixtures."""
        self.integration = create_build_integration()
        self.sample_stats = {
            "strength": 95,
            "agility": 110,
            "constitution": 105,
            "stamina": 88,
            "mind": 120,
            "focus": 115,
            "willpower": 92
        }

    def test_get_build_data(self):
        """Test getting build data."""
        build_data = self.integration.get_build_data("TestPlayer")
        
        # Should return a dict (may be empty if build awareness not available)
        self.assertIsInstance(build_data, dict)

    def test_analyze_with_build_context(self):
        """Test build-aware analysis."""
        analysis = self.integration.analyze_with_build_context(
            self.sample_stats, "TestPlayer", "balanced"
        )
        
        self.assertIsInstance(analysis, dict)
        self.assertIn("timestamp", analysis)
        self.assertIn("character_name", analysis)
        self.assertIn("stats", analysis)
        self.assertIn("build_data", analysis)
        self.assertIn("optimization_type", analysis)
        self.assertIn("build_aware_recommendations", analysis)

    def test_validate_build_compatibility(self):
        """Test build compatibility validation."""
        sample_build_data = {
            "professions": ["rifleman"],
            "weapons": ["rifle"],
            "combat_style": "ranged"
        }
        
        validation = self.integration.validate_build_compatibility(
            self.sample_stats, sample_build_data, "balanced"
        )
        
        self.assertIsInstance(validation, dict)
        self.assertIn("compatible", validation)
        self.assertIn("issues", validation)
        self.assertIn("warnings", validation)
        self.assertIn("suggestions", validation)

    def test_profession_compatibility_validation(self):
        """Test profession compatibility validation."""
        stats = {"agility": 80, "mind": 90}  # Low stats
        professions = ["rifleman", "medic"]
        
        validation = self.integration._validate_profession_compatibility(stats, professions)
        
        self.assertIsInstance(validation, dict)
        self.assertIn("issues", validation)
        self.assertIn("warnings", validation)
        self.assertIn("suggestions", validation)
        
        # Should have warnings for low agility (rifleman) and low mind (medic)
        warnings = validation["warnings"]
        self.assertGreater(len(warnings), 0)


class TestBuffAdvisor(unittest.TestCase):
    """Test the main BuffAdvisor component."""

    def setUp(self):
        """Set up test fixtures."""
        self.advisor = create_buff_advisor()
        self.sample_stats = {
            "strength": 95,
            "agility": 110,
            "constitution": 105,
            "stamina": 88,
            "mind": 120,
            "focus": 115,
            "willpower": 92
        }

    def test_analyze_character_and_recommend(self):
        """Test comprehensive character analysis and recommendations."""
        results = self.advisor.analyze_character_and_recommend(
            self.sample_stats, "TestPlayer", "pve_damage", "medium", True
        )
        
        self.assertIsInstance(results, dict)
        self.assertIn("timestamp", results)
        self.assertIn("character_name", results)
        self.assertIn("optimization_type", results)
        self.assertIn("budget", results)
        self.assertIn("stats", results)
        self.assertIn("stat_analysis", results)
        self.assertIn("optimization_priorities", results)
        self.assertIn("buff_recommendations", results)
        self.assertIn("template_recommendations", results)
        self.assertIn("build_analysis", results)
        self.assertIn("summary", results)

    def test_analyze_from_stats_log(self):
        """Test analysis from stats log content."""
        stats_log = """
        Character: TestPlayer
        Strength: 95
        Agility: 110
        Constitution: 105
        Stamina: 88
        Mind: 120
        Focus: 115
        Willpower: 92
        """
        
        results = self.advisor.analyze_from_stats_log(
            stats_log, "TestPlayer", "pve_damage", "medium"
        )
        
        self.assertIsInstance(results, dict)
        self.assertNotIn("error", results)
        self.assertIn("stats", results)

    def test_get_buff_recommendations(self):
        """Test getting buff recommendations."""
        recommendations = self.advisor.get_buff_recommendations(
            self.sample_stats, "pve_damage", "medium"
        )
        
        self.assertIsInstance(recommendations, dict)
        self.assertIn("timestamp", recommendations)
        self.assertIn("optimization_type", recommendations)
        self.assertIn("budget", recommendations)
        self.assertIn("buff_food", recommendations)
        self.assertIn("entertainer_dances", recommendations)

    def test_get_template_recommendations(self):
        """Test getting template recommendations."""
        recommendations = self.advisor.get_template_recommendations(
            self.sample_stats, "TestPlayer", "balanced", "medium"
        )
        
        self.assertIsInstance(recommendations, dict)
        self.assertIn("timestamp", recommendations)
        self.assertIn("optimization_type", recommendations)
        self.assertIn("budget", recommendations)
        self.assertIn("armor_setup", recommendations)
        self.assertIn("weapon_setup", recommendations)

    def test_get_build_compatibility_report(self):
        """Test getting build compatibility report."""
        report = self.advisor.get_build_compatibility_report(
            self.sample_stats, "TestPlayer", "balanced"
        )
        
        self.assertIsInstance(report, dict)
        # May have error if no build data available
        if "error" not in report:
            self.assertIn("timestamp", report)
            self.assertIn("character_name", report)
            self.assertIn("build_data", report)
            self.assertIn("validation", report)
            self.assertIn("analysis", report)

    def test_export_recommendations_report(self):
        """Test exporting recommendations report."""
        results = self.advisor.analyze_character_and_recommend(
            self.sample_stats, "TestPlayer", "pve_damage", "medium", False
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            filepath = self.advisor.export_recommendations_report(results, temp_file)
            
            self.assertEqual(filepath, temp_file)
            self.assertTrue(os.path.exists(filepath))
            
            # Verify the exported file contains valid JSON
            with open(filepath, 'r') as f:
                exported_data = json.load(f)
            
            self.assertIsInstance(exported_data, dict)
            self.assertIn("timestamp", exported_data)
            self.assertIn("character_name", exported_data)
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_get_recommendation_history(self):
        """Test getting recommendation history."""
        # Add some recommendations to history
        self.advisor.analyze_character_and_recommend(
            self.sample_stats, "TestPlayer", "pve_damage", "medium", False
        )
        
        history = self.advisor.get_recommendation_history("TestPlayer")
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
        
        # Check that the history contains the expected data
        latest = history[-1]
        self.assertIn("character_name", latest)
        self.assertEqual(latest["character_name"], "TestPlayer")

    def test_get_cached_character_stats(self):
        """Test getting cached character stats."""
        # Analyze a character to populate cache
        self.advisor.analyze_character_and_recommend(
            self.sample_stats, "TestPlayer", "pve_damage", "medium", False
        )
        
        cached_stats = self.advisor.get_cached_character_stats("TestPlayer")
        self.assertIsInstance(cached_stats, dict)
        self.assertIn("stats", cached_stats)
        self.assertIn("last_analyzed", cached_stats)
        self.assertIn("optimization_type", cached_stats)

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test with empty stats - should handle gracefully with 0 values
        results = self.advisor.analyze_character_and_recommend({})
        self.assertNotIn("error", results)
        self.assertIn("stats", results)
        
        # Test with invalid stats log - should handle gracefully with 0 values
        results = self.advisor.analyze_from_stats_log("Invalid log content")
        self.assertNotIn("error", results)
        self.assertIn("stats", results)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete buff advisor system."""

    def setUp(self):
        """Set up test fixtures."""
        self.advisor = create_buff_advisor()

    def test_complete_workflow(self):
        """Test the complete buff advisor workflow."""
        # Sample character stats
        stats = {
            "strength": 85,  # Low strength
            "agility": 125,  # Good agility
            "constitution": 95,  # Low constitution
            "stamina": 90,  # Low stamina
            "mind": 130,  # Good mind
            "focus": 110,  # Good focus
            "willpower": 88  # Low willpower
        }
        
        # Run comprehensive analysis
        results = self.advisor.analyze_character_and_recommend(
            stats, "IntegrationTest", "pve_damage", "medium", True
        )
        
        # Verify results structure
        self.assertIsInstance(results, dict)
        self.assertNotIn("error", results)
        
        # Verify stat analysis
        stat_analysis = results["stat_analysis"]
        self.assertIn("total_stats", stat_analysis)
        self.assertIn("weakest_stats", stat_analysis)
        self.assertIn("strongest_stats", stat_analysis)
        
        # Verify optimization priorities
        priorities = results["optimization_priorities"]
        self.assertIsInstance(priorities, list)
        self.assertGreater(len(priorities), 0)
        
        # Verify buff recommendations
        buff_recs = results["buff_recommendations"]
        self.assertIn("buff_food", buff_recs)
        self.assertIn("entertainer_dances", buff_recs)
        
        # Verify template recommendations
        template_recs = results["template_recommendations"]
        self.assertIn("armor_setup", template_recs)
        self.assertIn("weapon_setup", template_recs)
        
        # Verify summary
        summary = results["summary"]
        self.assertIn("total_stats", summary)
        self.assertIn("top_priorities", summary)
        self.assertIn("key_recommendations", summary)

    def test_different_optimization_types(self):
        """Test different optimization types."""
        stats = {
            "strength": 95,
            "agility": 110,
            "constitution": 105,
            "stamina": 88,
            "mind": 120,
            "focus": 115,
            "willpower": 92
        }
        
        optimization_types = ["pve_damage", "healing", "buff_stack", "balanced"]
        
        for opt_type in optimization_types:
            results = self.advisor.analyze_character_and_recommend(
                stats, f"Test_{opt_type}", opt_type, "medium", False
            )
            
            self.assertNotIn("error", results)
            self.assertEqual(results["optimization_type"], opt_type)
            
            # Verify that priorities are different for different optimization types
            priorities = results["optimization_priorities"]
            self.assertGreater(len(priorities), 0)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 
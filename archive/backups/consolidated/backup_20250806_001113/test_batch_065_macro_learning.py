"""Test suite for Batch 065 - Macro/Alias Learning + Shortcut Helper.

This module provides comprehensive testing for all components of the macro
learning system including macro parsing, alias analysis, recommendations,
shortcuts, and Discord alerts.
"""

import unittest
import json
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

# Import the modules to test
from modules.macro_learning.macro_parser import MacroParser, Macro, Alias, MacroAnalysis
from modules.macro_learning.alias_analyzer import AliasAnalyzer, AliasPattern, AliasAnalysis
from modules.macro_learning.macro_recommender import MacroRecommender, MacroRecommendation, FallbackMap, RecommendationReport
from modules.macro_learning.shortcut_helper import ShortcutHelper, Shortcut, ShortcutCategory, ShortcutAnalysis
from modules.macro_learning.discord_macro_alerts import DiscordMacroAlerts, MacroAlert, AlertSummary


class TestMacroParser(unittest.TestCase):
    """Test cases for MacroParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.parser = MacroParser(swg_directory=self.temp_dir)
        
        # Create test macro files
        self._create_test_macro_files()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def _create_test_macro_files(self):
        """Create test macro files for testing."""
        # Create macro directory
        macro_dir = os.path.join(self.temp_dir, "macros")
        os.makedirs(macro_dir, exist_ok=True)
        
        # Create test macro file
        macro_content = """heal: /heal {target}
/say Healing {target}

buff: /buff {target}
/say Buffing {target}

travel: /travel {destination}
/say Traveling to {destination}"""
        
        with open(os.path.join(macro_dir, "test_macros.txt"), 'w') as f:
            f.write(macro_content)
        
        # Create test alias file
        alias_content = """heal /heal {target}
buff /buff {target}
travel /travel {destination}
loot /loot
status /status"""
        
        with open(os.path.join(self.temp_dir, "alias.txt"), 'w') as f:
            f.write(alias_content)
    
    def test_initialization(self):
        """Test MacroParser initialization."""
        self.assertEqual(self.parser.swg_directory, self.temp_dir)
        self.assertIsInstance(self.parser.macros, dict)
        self.assertIsInstance(self.parser.aliases, dict)
    
    def test_scan_macro_directories(self):
        """Test scanning macro directories."""
        found_dirs = self.parser.scan_macro_directories()
        self.assertIn("macros", found_dirs)
        self.assertIn("test_macros.txt", found_dirs["macros"])
    
    def test_parse_macro_file(self):
        """Test parsing macro file."""
        macro_file = os.path.join(self.temp_dir, "macros", "test_macros.txt")
        macros = self.parser.parse_macro_file(macro_file)
        
        self.assertEqual(len(macros), 3)
        self.assertIn("heal", [m.name for m in macros])
        self.assertIn("buff", [m.name for m in macros])
        self.assertIn("travel", [m.name for m in macros])
    
    def test_parse_alias_file(self):
        """Test parsing alias file."""
        alias_file = os.path.join(self.temp_dir, "alias.txt")
        aliases = self.parser.parse_alias_file(alias_file)
        
        self.assertEqual(len(aliases), 5)
        self.assertIn("heal", [a.name for a in aliases])
        self.assertIn("buff", [a.name for a in aliases])
        self.assertIn("travel", [a.name for a in aliases])
    
    def test_load_all_macros(self):
        """Test loading all macros."""
        macros = self.parser.load_all_macros()
        self.assertGreater(len(macros), 0)
        self.assertIn("heal", macros)
        self.assertIn("buff", macros)
    
    def test_load_all_aliases(self):
        """Test loading all aliases."""
        aliases = self.parser.load_all_aliases()
        self.assertGreater(len(aliases), 0)
        self.assertIn("heal", aliases)
        self.assertIn("buff", aliases)
    
    def test_get_missing_critical_items(self):
        """Test finding missing critical items."""
        # Load macros and aliases first
        self.parser.load_all_macros()
        self.parser.load_all_aliases()
        
        missing_macros, missing_aliases = self.parser.get_missing_critical_items()
        
        # Should find some missing critical items
        self.assertIsInstance(missing_macros, list)
        self.assertIsInstance(missing_aliases, list)
    
    def test_analyze_macros(self):
        """Test macro analysis."""
        # Load macros and aliases first
        self.parser.load_all_macros()
        self.parser.load_all_aliases()
        
        analysis = self.parser.analyze_macros()
        
        self.assertIsInstance(analysis, MacroAnalysis)
        self.assertGreater(analysis.total_macros, 0)
        self.assertGreater(analysis.total_aliases, 0)
    
    def test_save_analysis_report(self):
        """Test saving analysis report."""
        # Load and analyze macros
        self.parser.load_all_macros()
        self.parser.load_all_aliases()
        analysis = self.parser.analyze_macros()
        
        # Save report
        report_path = self.parser.save_analysis_report(analysis)
        
        self.assertTrue(os.path.exists(report_path))
        self.assertTrue(report_path.endswith('.json'))


class TestAliasAnalyzer(unittest.TestCase):
    """Test cases for AliasAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = AliasAnalyzer()
        
        # Sample aliases for testing
        self.test_aliases = {
            "heal": {"command": "/heal {target}", "category": "combat"},
            "buff": {"command": "/buff {target}", "category": "combat"},
            "travel": {"command": "/travel {destination}", "category": "travel"},
            "craft": {"command": "/craft {item}", "category": "crafting"},
            "loot": {"command": "/loot", "category": "utility"},
            "say": {"command": "/say {message}", "category": "social"}
        }
    
    def test_initialization(self):
        """Test AliasAnalyzer initialization."""
        self.assertIsInstance(self.analyzer.aliases, dict)
        self.assertIsInstance(self.analyzer.patterns, dict)
        self.assertIsInstance(self.analyzer.category_stats, dict)
    
    def test_load_aliases(self):
        """Test loading aliases."""
        self.analyzer.load_aliases(self.test_aliases)
        self.assertEqual(len(self.analyzer.aliases), 6)
        self.assertIn("heal", self.analyzer.aliases)
        self.assertIn("buff", self.analyzer.aliases)
    
    def test_analyze_patterns(self):
        """Test pattern analysis."""
        self.analyzer.load_aliases(self.test_aliases)
        patterns = self.analyzer.analyze_patterns()
        
        self.assertGreater(len(patterns), 0)
        self.assertIsInstance(patterns, dict)
    
    def test_categorize_command(self):
        """Test command categorization."""
        combat_cmd = "/heal {target}"
        travel_cmd = "/travel {destination}"
        social_cmd = "/say {message}"
        
        self.assertEqual(self.analyzer._categorize_command(combat_cmd), "combat")
        self.assertEqual(self.analyzer._categorize_command(travel_cmd), "travel")
        self.assertEqual(self.analyzer._categorize_command(social_cmd), "social")
    
    def test_extract_pattern(self):
        """Test pattern extraction."""
        command = "/heal {target} with {item}"
        pattern = self.analyzer._extract_pattern(command)
        
        self.assertIn("{param}", pattern)
        self.assertNotIn("target", pattern)
    
    def test_calculate_complexity(self):
        """Test complexity calculation."""
        simple_pattern = "/heal"
        complex_pattern = "/heal {target} with {item} and {skill}"
        
        simple_score = self.analyzer._calculate_complexity(simple_pattern)
        complex_score = self.analyzer._calculate_complexity(complex_pattern)
        
        self.assertLess(simple_score, complex_score)
        self.assertGreaterEqual(simple_score, 0.0)
        self.assertLessEqual(complex_score, 1.0)
    
    def test_find_dependency_chains(self):
        """Test dependency chain finding."""
        self.analyzer.load_aliases(self.test_aliases)
        chains = self.analyzer.find_dependency_chains()
        
        self.assertIsInstance(chains, list)
    
    def test_generate_optimization_suggestions(self):
        """Test optimization suggestion generation."""
        self.analyzer.load_aliases(self.test_aliases)
        self.analyzer.analyze_patterns()
        
        suggestions = self.analyzer.generate_optimization_suggestions()
        
        self.assertIsInstance(suggestions, list)
    
    def test_get_comprehensive_analysis(self):
        """Test comprehensive analysis."""
        self.analyzer.load_aliases(self.test_aliases)
        analysis = self.analyzer.get_comprehensive_analysis()
        
        self.assertIsInstance(analysis, AliasAnalysis)
        self.assertEqual(analysis.total_aliases, 6)
        self.assertGreater(analysis.unique_patterns, 0)
    
    def test_save_analysis_report(self):
        """Test saving analysis report."""
        self.analyzer.load_aliases(self.test_aliases)
        analysis = self.analyzer.get_comprehensive_analysis()
        
        report_path = self.analyzer.save_analysis_report(analysis)
        
        self.assertTrue(os.path.exists(report_path))
        self.assertTrue(report_path.endswith('.json'))


class TestMacroRecommender(unittest.TestCase):
    """Test cases for MacroRecommender class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.recommender = MacroRecommender(data_directory=self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test MacroRecommender initialization."""
        self.assertEqual(self.recommender.data_directory, self.temp_dir)
        self.assertIsInstance(self.recommender.best_practice_macros, dict)
        self.assertIsInstance(self.recommender.fallback_maps, dict)
    
    def test_find_missing_macros(self):
        """Test finding missing macros."""
        existing_macros = {"heal": {}, "buff": {}}
        missing = self.recommender.find_missing_macros(existing_macros)
        
        self.assertIsInstance(missing, list)
        self.assertIn("travel", missing)  # Should be missing
        self.assertNotIn("heal", missing)  # Should not be missing
    
    def test_create_fallback_map(self):
        """Test creating fallback map."""
        available_macros = {"cure": {"category": "combat"}, "enhance": {"category": "combat"}}
        fallback = self.recommender.create_fallback_map("heal", available_macros)
        
        self.assertIsInstance(fallback, FallbackMap)
        self.assertEqual(fallback.original_macro, "heal")
        self.assertIn(fallback.fallback_macro, ["cure", "enhance"])
    
    def test_generate_recommendations(self):
        """Test generating recommendations."""
        missing_macros = ["heal", "buff", "travel"]
        existing_macros = {"cure": {}, "enhance": {}}
        
        recommendations = self.recommender.generate_recommendations(missing_macros, existing_macros)
        
        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), 3)
        
        for rec in recommendations:
            self.assertIsInstance(rec, MacroRecommendation)
            self.assertIn(rec.macro_name, missing_macros)
    
    def test_create_macro_file(self):
        """Test creating macro file."""
        macro_name = "test_macro"
        content = "/test {param}\n/say Testing"
        
        file_path = self.recommender.create_macro_file(macro_name, content)
        
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(file_path.endswith('.txt'))
        
        # Check file content
        with open(file_path, 'r') as f:
            file_content = f.read()
            self.assertIn(macro_name.upper(), file_content)
            self.assertIn(content, file_content)
    
    def test_generate_comprehensive_report(self):
        """Test generating comprehensive report."""
        missing_macros = ["heal", "buff"]
        missing_aliases = ["/heal", "/buff"]
        existing_macros = {"cure": {}}
        existing_aliases = {"/cure": {}}
        
        report = self.recommender.generate_comprehensive_report(
            missing_macros, missing_aliases, existing_macros, existing_aliases
        )
        
        self.assertIsInstance(report, RecommendationReport)
        self.assertEqual(report.total_recommendations, 2)
        self.assertEqual(len(report.missing_macros), 2)
        self.assertEqual(len(report.missing_aliases), 2)
    
    def test_save_recommendation_report(self):
        """Test saving recommendation report."""
        report = RecommendationReport(
            total_recommendations=2,
            critical_recommendations=1,
            missing_macros=["heal"],
            missing_aliases=["/heal"],
            fallback_maps=[],
            recommendations=[],
            priority_order=["heal"]
        )
        
        report_path = self.recommender.save_recommendation_report(report)
        
        self.assertTrue(os.path.exists(report_path))
        self.assertTrue(report_path.endswith('.json'))


class TestShortcutHelper(unittest.TestCase):
    """Test cases for ShortcutHelper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.shortcuts_file = os.path.join(self.temp_dir, "shortcuts.json")
        self.helper = ShortcutHelper(shortcuts_file=self.shortcuts_file, create_defaults=False)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test ShortcutHelper initialization."""
        self.assertEqual(self.helper.shortcuts_file, self.shortcuts_file)
        self.assertIsInstance(self.helper.shortcuts, dict)
        self.assertIsInstance(self.helper.categories, dict)
        self.assertIsInstance(self.helper.favorites, set)
    
    def test_add_shortcut(self):
        """Test adding shortcut."""
        success = self.helper.add_shortcut(
            "test_shortcut", "/test {param}", "utility", "F1", "Test shortcut"
        )
        
        self.assertTrue(success)
        self.assertIn("test_shortcut", self.helper.shortcuts)
        # Check if shortcut is in the utility category
        utility_shortcuts = [s.name for s in self.helper.categories["utility"]]
        self.assertIn("test_shortcut", utility_shortcuts)
    
    def test_remove_shortcut(self):
        """Test removing shortcut."""
        # Add shortcut first
        self.helper.add_shortcut("test_shortcut", "/test", "utility")
        
        # Remove it
        success = self.helper.remove_shortcut("test_shortcut")
        
        self.assertTrue(success)
        self.assertNotIn("test_shortcut", self.helper.shortcuts)
    
    def test_update_shortcut_usage(self):
        """Test updating shortcut usage."""
        self.helper.add_shortcut("test_shortcut", "/test", "utility")
        
        initial_usage = self.helper.shortcuts["test_shortcut"].usage_count
        self.helper.update_shortcut_usage("test_shortcut")
        
        updated_usage = self.helper.shortcuts["test_shortcut"].usage_count
        self.assertEqual(updated_usage, initial_usage + 1)
    
    def test_toggle_favorite(self):
        """Test toggling favorite status."""
        self.helper.add_shortcut("test_shortcut", "/test", "utility")
        
        # Toggle to favorite
        is_favorite = self.helper.toggle_favorite("test_shortcut")
        self.assertTrue(is_favorite)
        self.assertIn("test_shortcut", self.helper.favorites)
        
        # Toggle back
        is_favorite = self.helper.toggle_favorite("test_shortcut")
        self.assertFalse(is_favorite)
        self.assertNotIn("test_shortcut", self.helper.favorites)
    
    def test_get_shortcuts_by_category(self):
        """Test getting shortcuts by category."""
        self.helper.add_shortcut("combat_shortcut", "/attack", "combat")
        self.helper.add_shortcut("utility_shortcut", "/status", "utility")
        
        combat_shortcuts = self.helper.get_shortcuts_by_category("combat")
        utility_shortcuts = self.helper.get_shortcuts_by_category("utility")
        
        self.assertEqual(len(combat_shortcuts), 1)
        self.assertEqual(len(utility_shortcuts), 1)
        self.assertEqual(combat_shortcuts[0].name, "combat_shortcut")
    
    def test_search_shortcuts(self):
        """Test searching shortcuts."""
        self.helper.add_shortcut("heal_shortcut", "/heal {target}", "combat", description="Heal target")
        self.helper.add_shortcut("buff_shortcut", "/buff {target}", "combat", description="Buff target")
        
        results = self.helper.search_shortcuts("heal")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "heal_shortcut")
    
    def test_get_shortcut_suggestions(self):
        """Test getting shortcut suggestions."""
        self.helper.add_shortcut("heal_shortcut", "/heal", "combat")
        self.helper.add_shortcut("buff_shortcut", "/buff", "combat")
        
        suggestions = self.helper.get_shortcut_suggestions("combat")
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
    
    def test_generate_shortcut_report(self):
        """Test generating shortcut report."""
        self.helper.add_shortcut("heal_shortcut", "/heal", "combat")
        self.helper.add_shortcut("buff_shortcut", "/buff", "combat")
        self.helper.add_shortcut("status_shortcut", "/status", "utility")
        
        report = self.helper.generate_shortcut_report()
        
        self.assertIsInstance(report, ShortcutAnalysis)
        self.assertEqual(report.total_shortcuts, 3)
        self.assertIn("combat", report.categories)
        self.assertIn("utility", report.categories)


class TestDiscordMacroAlerts(unittest.TestCase):
    """Test cases for DiscordMacroAlerts class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.alerts = DiscordMacroAlerts()
    
    def test_initialization(self):
        """Test DiscordMacroAlerts initialization."""
        self.assertIsInstance(self.alerts.alerts, list)
        self.assertIsInstance(self.alerts.alert_history, list)
        self.assertIsInstance(self.alerts.alert_categories, dict)
    
    def test_create_missing_macros_alert(self):
        """Test creating missing macros alert."""
        missing_macros = ["heal", "buff"]
        missing_aliases = ["/heal", "/buff"]
        recommendations = ["Create heal macro", "Create buff macro"]
        
        alert = self.alerts.create_missing_macros_alert(
            missing_macros, missing_aliases, recommendations
        )
        
        self.assertIsInstance(alert, MacroAlert)
        self.assertEqual(len(alert.missing_items), 4)
        self.assertEqual(len(alert.recommendations), 2)
    
    def test_create_recommendation_alert(self):
        """Test creating recommendation alert."""
        recommendations = ["Use heal macro", "Use buff macro", "Use travel macro"]
        
        alert = self.alerts.create_recommendation_alert(recommendations, "combat")
        
        self.assertIsInstance(alert, MacroAlert)
        self.assertEqual(alert.alert_type, "recommendation")
        self.assertEqual(len(alert.recommendations), 3)
    
    def test_create_fallback_map_alert(self):
        """Test creating fallback map alert."""
        fallback_maps = [
            {"original_macro": "heal", "fallback_macro": "cure", "confidence": 0.8},
            {"original_macro": "buff", "fallback_macro": "enhance", "confidence": 0.6}
        ]
        
        alert = self.alerts.create_fallback_map_alert(fallback_maps)
        
        self.assertIsInstance(alert, MacroAlert)
        self.assertEqual(alert.alert_type, "info")
    
    @patch('modules.macro_learning.discord_macro_alerts.DiscordMacroAlerts._send_via_webhook')
    def test_send_macro_alert(self, mock_send):
        """Test sending macro alert."""
        mock_send.return_value = True
        
        alert = MacroAlert(
            alert_type="info",
            title="Test Alert",
            message="Test message",
            priority="low",
            missing_items=[],
            recommendations=[],
            timestamp=datetime.now()
        )
        
        # Mock webhook URL
        self.alerts.webhook_url = "https://discord.com/api/webhooks/test"
        
        # Call the async method synchronously
        import asyncio
        success = asyncio.run(self.alerts.send_macro_alert(alert))
        
        self.assertTrue(success)
        self.assertIn(alert, self.alerts.alerts)
        self.assertIn(alert, self.alerts.alert_history)
    
    def test_get_alert_summary(self):
        """Test getting alert summary."""
        # Add some test alerts
        test_alert = MacroAlert(
            alert_type="critical",
            title="Test Critical",
            message="Test",
            priority="high",
            missing_items=["heal"],
            recommendations=[],
            timestamp=datetime.now()
        )
        self.alerts.alert_history.append(test_alert)
        
        summary = self.alerts.get_alert_summary()
        
        self.assertIsInstance(summary, AlertSummary)
        self.assertEqual(summary.total_alerts, 1)
        self.assertEqual(summary.critical_alerts, 1)
    
    def test_save_alert_history(self):
        """Test saving alert history."""
        # Add test alert
        test_alert = MacroAlert(
            alert_type="info",
            title="Test Alert",
            message="Test",
            priority="low",
            missing_items=[],
            recommendations=[],
            timestamp=datetime.now()
        )
        self.alerts.alert_history.append(test_alert)
        
        history_path = self.alerts.save_alert_history()
        
        self.assertTrue(os.path.exists(history_path))
        self.assertTrue(history_path.endswith('.json'))


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete macro learning system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize all components
        self.parser = MacroParser(swg_directory=self.temp_dir)
        self.analyzer = AliasAnalyzer()
        self.recommender = MacroRecommender(data_directory=self.temp_dir)
        self.helper = ShortcutHelper(shortcuts_file=os.path.join(self.temp_dir, "shortcuts.json"), create_defaults=False)
        self.alerts = DiscordMacroAlerts()
        
        # Create test data
        self._create_test_data()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def _create_test_data(self):
        """Create test data for integration testing."""
        # Create macro files
        macro_dir = os.path.join(self.temp_dir, "macros")
        os.makedirs(macro_dir, exist_ok=True)
        
        macro_content = """heal: /heal {target}
/say Healing {target}

buff: /buff {target}
/say Buffing {target}"""
        
        with open(os.path.join(macro_dir, "test_macros.txt"), 'w') as f:
            f.write(macro_content)
        
        # Create alias file
        alias_content = """heal /heal {target}
buff /buff {target}
loot /loot"""
        
        with open(os.path.join(self.temp_dir, "alias.txt"), 'w') as f:
            f.write(alias_content)
    
    def test_complete_workflow(self):
        """Test complete macro learning workflow."""
        # 1. Parse macros and aliases
        macros = self.parser.load_all_macros()
        aliases = self.parser.load_all_aliases()
        
        self.assertGreater(len(macros), 0)
        self.assertGreater(len(aliases), 0)
        
        # 2. Analyze aliases
        self.analyzer.load_aliases({name: {"command": alias.command, "category": alias.category} 
                                   for name, alias in aliases.items()})
        alias_analysis = self.analyzer.get_comprehensive_analysis()
        
        self.assertIsInstance(alias_analysis, AliasAnalysis)
        
        # 3. Find missing macros
        missing_macros, missing_aliases = self.parser.get_missing_critical_items()
        
        self.assertIsInstance(missing_macros, list)
        self.assertIsInstance(missing_aliases, list)
        
        # 4. Generate recommendations
        recommendations = self.recommender.generate_recommendations(missing_macros, macros)
        
        self.assertIsInstance(recommendations, list)
        
        # 5. Create shortcuts
        for rec in recommendations[:3]:  # Add first 3 recommendations as shortcuts
            self.helper.add_shortcut(
                rec.macro_name, rec.suggested_content, rec.category
            )
        
        # 6. Generate reports
        macro_analysis = self.parser.analyze_macros()
        shortcut_report = self.helper.generate_shortcut_report()
        
        self.assertIsInstance(macro_analysis, MacroAnalysis)
        self.assertIsInstance(shortcut_report, ShortcutAnalysis)
        
        # 7. Test Discord alerts (mocked)
        if missing_macros or missing_aliases:
            alert = self.alerts.create_missing_macros_alert(
                missing_macros, missing_aliases, [r.reason for r in recommendations]
            )
            self.assertIsInstance(alert, MacroAlert)
    
    def test_fallback_map_creation(self):
        """Test fallback map creation workflow."""
        # Load macros
        macros = self.parser.load_all_macros()
        
        # Find missing macros
        missing_macros, _ = self.parser.get_missing_critical_items()
        
        # Create fallback maps
        fallback_maps = []
        for missing_macro in missing_macros[:3]:  # Test first 3
            fallback = self.recommender.create_fallback_map(missing_macro, macros)
            if fallback:
                fallback_maps.append(fallback)
        
        self.assertIsInstance(fallback_maps, list)
        
        # Test that fallback maps are valid
        for fallback in fallback_maps:
            self.assertIsInstance(fallback, FallbackMap)
            self.assertIn(fallback.original_macro, missing_macros)
            self.assertIn(fallback.fallback_macro, macros.keys())
    
    def test_shortcut_management(self):
        """Test shortcut management workflow."""
        # Add shortcuts for different categories
        categories = ["combat", "travel", "crafting", "utility"]
        
        for i, category in enumerate(categories):
            shortcut_name = f"test_{category}_shortcut"
            self.helper.add_shortcut(shortcut_name, f"/test_{category}", category)
        
        # Test category organization
        for category in categories:
            shortcuts = self.helper.get_shortcuts_by_category(category)
            self.assertEqual(len(shortcuts), 1)
            self.assertEqual(shortcuts[0].category, category)
        
        # Test favorites
        self.helper.toggle_favorite("test_combat_shortcut")
        favorites = self.helper.get_favorite_shortcuts()
        self.assertEqual(len(favorites), 1)
        self.assertEqual(favorites[0].name, "test_combat_shortcut")
        
        # Test usage tracking
        self.helper.update_shortcut_usage("test_combat_shortcut")
        self.assertEqual(self.helper.shortcuts["test_combat_shortcut"].usage_count, 1)
        
        # Test search
        results = self.helper.search_shortcuts("combat")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "test_combat_shortcut")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 
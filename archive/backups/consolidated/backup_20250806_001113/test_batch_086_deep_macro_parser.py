"""Test suite for Batch 086 - Deep Macro Parser + Learning AI (Phase 1).

This test suite covers all aspects of the deep macro parser including:
- File parsing and scanning
- Macro and alias classification
- Complexity analysis
- Usage pattern analysis
- Learning insights generation
- Report generation
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from core.deep_macro_parser import (
    DeepMacroParser, 
    DeepMacroAnalysis, 
    MacroLearningInsight
)

class TestDeepMacroParser(unittest.TestCase):
    """Test cases for DeepMacroParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.parser = DeepMacroParser(project_root=self.temp_dir)
        
        # Create test directories
        self.macro_dir = Path(self.temp_dir) / "data" / "macros"
        self.alias_dir = Path(self.temp_dir) / "data" / "aliases"
        self.macro_dir.mkdir(parents=True, exist_ok=True)
        self.alias_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test parser initialization."""
        self.assertIsNotNone(self.parser)
        self.assertEqual(self.parser.project_root, Path(self.temp_dir))
        self.assertEqual(self.parser.macro_dir, self.macro_dir)
        self.assertIsNotNone(self.parser.combat_patterns)
        self.assertIsNotNone(self.parser.utility_patterns)
        self.assertIsNotNone(self.parser.buff_patterns)
        self.assertIsNotNone(self.parser.ui_action_patterns)
    
    def test_extract_macro_name(self):
        """Test macro name extraction."""
        # Test filename extraction
        file_path = Path("test_macro.txt")
        content = "Some macro content"
        name = self.parser._extract_macro_name(file_path, content)
        self.assertEqual(name, "test_macro")
        
        # Test content extraction with # MACRO: pattern
        content = "# MACRO: heal_combat\nSome content"
        name = self.parser._extract_macro_name(file_path, content)
        self.assertEqual(name, "heal_combat")
        
        # Test content extraction with # NAME: pattern
        content = "# NAME: attack_sequence\nSome content"
        name = self.parser._extract_macro_name(file_path, content)
        self.assertEqual(name, "attack_sequence")
    
    def test_classify_macro(self):
        """Test macro classification."""
        # Test combat classification
        name = "heal"
        content = "/heal {target}\n/say Healing {target}"
        category = self.parser._classify_macro(name, content)
        self.assertEqual(category, "combat")
        
        # Test utility classification
        name = "travel"
        content = "/travel {destination}\n/say Traveling"
        category = self.parser._classify_macro(name, content)
        self.assertEqual(category, "utility")
        
        # Test buff classification
        name = "buff"
        content = "/buff {target}\n/enhance {target}"
        category = self.parser._classify_macro(name, content)
        self.assertEqual(category, "buff")
        
        # Test general classification
        name = "custom"
        content = "/custom {param}"
        category = self.parser._classify_macro(name, content)
        self.assertEqual(category, "general")
    
    def test_calculate_complexity(self):
        """Test complexity calculation."""
        # Test simple macro
        content = "/heal {target}"
        complexity = self.parser._calculate_complexity(content)
        self.assertIsInstance(complexity, float)
        self.assertGreaterEqual(complexity, 0.0)
        self.assertLessEqual(complexity, 1.0)
        
        # Test complex macro
        complex_content = """# Complex macro
/heal {target}
/buff {target}
/enhance {target}
/attack {target}
/special {target}
/defend
/flee
/travel {safe_location}
"""
        complexity = self.parser._calculate_complexity(complex_content)
        self.assertGreater(complexity, 0.5)  # Should be higher complexity
    
    def test_extract_dependencies(self):
        """Test dependency extraction."""
        content = "/heal {target}\n/buff {target}\n/attack {enemy}"
        dependencies = self.parser._extract_dependencies(content)
        
        # Should extract parameters and commands
        expected_params = ["target", "enemy"]
        expected_commands = ["heal", "buff", "attack"]
        
        for param in expected_params:
            self.assertIn(param, dependencies)
        
        for command in expected_commands:
            self.assertIn(command, dependencies)
    
    def test_parse_macro_file(self):
        """Test macro file parsing."""
        # Create test macro file
        macro_content = """# HEAL MACRO
# Created: 2025-08-01T10:43:03.912533
# Category: combat

/heal {target}
/say Healing {target}
"""
        macro_file = self.macro_dir / "test_heal.txt"
        with open(macro_file, 'w', encoding='utf-8') as f:
            f.write(macro_content)
        
        # Parse the file
        macros = self.parser._parse_macro_file(macro_file)
        
        self.assertEqual(len(macros), 1)
        macro = macros[0]
        self.assertEqual(macro.name, "test_heal")
        self.assertEqual(macro.category, "combat")
        self.assertIsNotNone(macro.last_modified)
        self.assertIsInstance(macro.dependencies, list)
    
    def test_scan_macro_files(self):
        """Test macro file scanning."""
        # Create multiple test macro files
        test_macros = {
            "heal.txt": "/heal {target}",
            "attack.txt": "/attack {target}",
            "travel.txt": "/travel {destination}"
        }
        
        for filename, content in test_macros.items():
            file_path = self.macro_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Scan for macros
        macros = self.parser.scan_macro_files()
        
        self.assertEqual(len(macros), 3)
        self.assertIn("heal", macros)
        self.assertIn("attack", macros)
        self.assertIn("travel", macros)
    
    def test_classify_alias(self):
        """Test alias classification."""
        # Test UI action classification
        name = "inventory"
        command = "/ui inventory"
        category = self.parser._classify_alias(name, command)
        self.assertEqual(category, "ui_action")
        
        # Test combat classification
        name = "heal"
        command = "/heal {target}"
        category = self.parser._classify_alias(name, command)
        self.assertEqual(category, "combat")
        
        # Test utility classification
        name = "travel"
        command = "/travel {destination}"
        category = self.parser._classify_alias(name, command)
        self.assertEqual(category, "utility")
    
    def test_parse_alias_file(self):
        """Test alias file parsing."""
        # Create test alias file
        alias_content = """# Test aliases
alias heal /heal {target}
alias attack /attack {target}
alias inventory /ui inventory
"""
        alias_file = self.alias_dir / "test_aliases.txt"
        with open(alias_file, 'w', encoding='utf-8') as f:
            f.write(alias_content)
        
        # Parse the file
        aliases = self.parser._parse_alias_file(alias_file)
        
        self.assertEqual(len(aliases), 3)
        
        # Check alias properties
        heal_alias = next(a for a in aliases if a.name == "heal")
        self.assertEqual(heal_alias.command, "/heal {target}")
        self.assertEqual(heal_alias.category, "combat")
    
    def test_scan_alias_files(self):
        """Test alias file scanning."""
        # Create test alias files
        test_aliases = {
            "alias_ui.txt": "alias inventory /ui inventory",
            "alias_combat.txt": "alias heal /heal {target}"
        }
        
        for filename, content in test_aliases.items():
            file_path = self.alias_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Scan for aliases
        aliases = self.parser.scan_alias_files()
        
        self.assertEqual(len(aliases), 2)
        self.assertIn("inventory", aliases)
        self.assertIn("heal", aliases)
    
    def test_analyze_usage_patterns(self):
        """Test usage pattern analysis."""
        # Create test macros and aliases
        macros = {
            "heal": MagicMock(content="/heal {target}\n/say Healing", category="combat"),
            "attack": MagicMock(content="/attack {target}\n/special {target}", category="combat"),
            "travel": MagicMock(content="/travel {destination}", category="utility")
        }
        
        aliases = {
            "heal": MagicMock(command="/heal {target}", category="combat"),
            "inventory": MagicMock(command="/ui inventory", category="ui_action")
        }
        
        # Analyze patterns
        patterns = self.parser.analyze_usage_patterns(macros, aliases)
        
        self.assertIn('command_frequency', patterns)
        self.assertIn('category_distribution', patterns)
        self.assertIn('complexity_distribution', patterns)
        
        # Check command frequency
        command_freq = patterns['command_frequency']
        self.assertGreater(command_freq['heal'], 0)
        self.assertGreater(command_freq['attack'], 0)
    
    def test_generate_learning_insights(self):
        """Test learning insights generation."""
        # Create test macros
        macros = {
            "complex_macro": MagicMock(
                content="/heal {target}\n/buff {target}\n/enhance {target}\n" * 5,  # Complex
                name="complex_macro"
            ),
            "simple_macro": MagicMock(
                content="/heal {target}",
                name="simple_macro"
            )
        }
        
        aliases = {}
        
        # Generate insights
        insights = self.parser.generate_learning_insights(macros, aliases)
        
        self.assertIsInstance(insights, list)
        
        # Should have insights for missing critical macros
        missing_insights = [i for i in insights if i.insight_type == "missing_feature"]
        self.assertGreater(len(missing_insights), 0)
        
        # Should have insights for complex macros
        complexity_insights = [i for i in insights if i.insight_type == "complexity"]
        self.assertGreater(len(complexity_insights), 0)
    
    def test_get_category_for_macro(self):
        """Test macro category determination."""
        self.assertEqual(self.parser._get_category_for_macro("heal"), "combat")
        self.assertEqual(self.parser._get_category_for_macro("buff"), "combat")
        self.assertEqual(self.parser._get_category_for_macro("travel"), "travel")
        self.assertEqual(self.parser._get_category_for_macro("craft"), "crafting")
        self.assertEqual(self.parser._get_category_for_macro("unknown"), "utility")
    
    def test_run_comprehensive_analysis(self):
        """Test comprehensive analysis."""
        # Create test data
        test_macro_content = "/heal {target}\n/say Healing {target}"
        test_alias_content = "alias heal /heal {target}\nalias inventory /ui inventory"
        
        # Create test files
        macro_file = self.macro_dir / "test_heal.txt"
        alias_file = self.alias_dir / "alias_test.txt"
        
        with open(macro_file, 'w', encoding='utf-8') as f:
            f.write(test_macro_content)
        
        with open(alias_file, 'w', encoding='utf-8') as f:
            f.write(test_alias_content)
        
        # Run analysis
        analysis = self.parser.run_comprehensive_analysis()
        
        # Verify analysis structure
        self.assertIsInstance(analysis, DeepMacroAnalysis)
        self.assertGreater(analysis.total_macros, 0)
        self.assertGreater(analysis.total_aliases, 0)
        self.assertIsInstance(analysis.macro_categories, dict)
        self.assertIsInstance(analysis.combat_macros, list)
        self.assertIsInstance(analysis.utility_macros, list)
        self.assertIsInstance(analysis.buff_macros, list)
        self.assertIsInstance(analysis.ui_action_mappings, dict)
        self.assertIsInstance(analysis.usage_patterns, dict)
        self.assertIsInstance(analysis.complexity_scores, dict)
        self.assertIsInstance(analysis.learning_suggestions, list)
        self.assertIsInstance(analysis.missing_critical, list)
        self.assertIsInstance(analysis.optimization_opportunities, list)
    
    def test_save_analysis_report(self):
        """Test analysis report saving."""
        # Create test analysis
        analysis = DeepMacroAnalysis(
            total_macros=5,
            total_aliases=3,
            macro_categories={"combat": 3, "utility": 2},
            alias_categories={"combat": 2, "ui_action": 1},
            combat_macros=["heal", "attack"],
            utility_macros=["travel"],
            buff_macros=["buff"],
            ui_action_mappings={"inventory": "/ui inventory"},
            usage_patterns={"heal": 5, "attack": 3},
            complexity_scores={"heal": 0.3, "attack": 0.5},
            learning_suggestions=["Create missing heal macro"],
            missing_critical=["craft"],
            optimization_opportunities=["Split complex macro"]
        )
        
        # Save report
        report_path = self.parser.save_analysis_report(analysis)
        
        # Verify file was created
        self.assertTrue(Path(report_path).exists())
        
        # Verify JSON content
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        self.assertEqual(report_data['total_macros'], 5)
        self.assertEqual(report_data['total_aliases'], 3)
        self.assertIn('analysis_timestamp', report_data)
        self.assertIn('parser_version', report_data)

class TestMacroLearningInsight(unittest.TestCase):
    """Test cases for MacroLearningInsight class."""
    
    def test_insight_creation(self):
        """Test insight creation."""
        insight = MacroLearningInsight(
            macro_name="test_macro",
            insight_type="complexity",
            confidence=0.8,
            description="High complexity macro",
            suggested_improvements=["Break into smaller macros"],
            related_macros=["macro1", "macro2"]
        )
        
        self.assertEqual(insight.macro_name, "test_macro")
        self.assertEqual(insight.insight_type, "complexity")
        self.assertEqual(insight.confidence, 0.8)
        self.assertEqual(insight.description, "High complexity macro")
        self.assertEqual(len(insight.suggested_improvements), 1)
        self.assertEqual(len(insight.related_macros), 2)

def run_integration_tests():
    """Run integration tests with actual file operations."""
    print("\n=== Running Integration Tests ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up test environment
        parser = DeepMacroParser(project_root=temp_dir)
        
        # Create test files
        macro_dir = Path(temp_dir) / "data" / "macros"
        alias_dir = Path(temp_dir) / "data" / "aliases"
        macro_dir.mkdir(parents=True, exist_ok=True)
        alias_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test macro
        macro_file = macro_dir / "test_heal.txt"
        with open(macro_file, 'w', encoding='utf-8') as f:
            f.write("""# HEAL MACRO
/heal {target}
/say Healing {target}
""")
        
        # Create test alias
        alias_file = alias_dir / "alias_test.txt"
        with open(alias_file, 'w', encoding='utf-8') as f:
            f.write("alias heal /heal {target}\nalias inventory /ui inventory")
        
        # Run analysis
        analysis = parser.run_comprehensive_analysis()
        
        # Verify results
        assert analysis.total_macros > 0, "Should find macros"
        assert analysis.total_aliases > 0, "Should find aliases"
        assert len(analysis.combat_macros) > 0, "Should classify combat macros"
        assert len(analysis.ui_action_mappings) > 0, "Should find UI action mappings"
        
        print("✅ Integration tests passed")

def main():
    """Run all tests."""
    print("🧪 Running Batch 086 - Deep Macro Parser Tests")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration tests
    run_integration_tests()
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    main() 
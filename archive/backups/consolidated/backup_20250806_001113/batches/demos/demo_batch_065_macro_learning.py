"""Demo script for Batch 065 - Macro/Alias Learning + Shortcut Helper.

This script demonstrates all features of the macro learning system including:
- Macro and alias parsing
- Pattern analysis and optimization
- Recommendation generation
- Shortcut management
- Discord alerts
"""

import os
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Import the modules to demo
from modules.macro_learning.macro_parser import MacroParser
from modules.macro_learning.alias_analyzer import AliasAnalyzer
from modules.macro_learning.macro_recommender import MacroRecommender
from modules.macro_learning.shortcut_helper import ShortcutHelper
from modules.macro_learning.discord_macro_alerts import DiscordMacroAlerts


def create_demo_environment():
    """Create a demo environment with sample macros and aliases."""
    print("🔧 Creating demo environment...")
    
    # Create temporary directory structure
    temp_dir = tempfile.mkdtemp()
    
    # Create macro directories
    macro_dir = os.path.join(temp_dir, "macros")
    os.makedirs(macro_dir, exist_ok=True)
    
    # Create sample macro file
    macro_content = """# Combat Macros
heal: /heal {target}
/say Healing {target}

buff: /buff {target}
/say Buffing {target}

attack: /attack {target}
/say Attacking {target}

defend: /defend
/say Defending

flee: /flee
/say Fleeing

# Travel Macros
travel: /travel {destination}
/say Traveling to {destination}

follow: /follow {target}
/say Following {target}

# Crafting Macros
craft: /craft {item}
/say Crafting {item}

harvest: /harvest {resource}
/say Harvesting {resource}

# Utility Macros
loot: /loot
/say Looting

status: /status
/say Checking status

# Social Macros
say: /say {message}
tell: /tell {player} {message}"""
    
    with open(os.path.join(macro_dir, "demo_macros.txt"), 'w') as f:
        f.write(macro_content)
    
    # Create sample alias file
    alias_content = """# Combat Aliases
heal /heal {target}
buff /buff {target}
attack /attack {target}
defend /defend
flee /flee

# Travel Aliases
travel /travel {destination}
follow /follow {target}

# Crafting Aliases
craft /craft {item}
harvest /harvest {resource}

# Utility Aliases
loot /loot
status /status

# Social Aliases
say /say {message}
tell /tell {player} {message}"""
    
    with open(os.path.join(temp_dir, "alias.txt"), 'w') as f:
        f.write(alias_content)
    
    print(f"✅ Demo environment created at: {temp_dir}")
    return temp_dir


def demo_macro_parser(temp_dir):
    """Demonstrate macro parser functionality."""
    print("\n📁 MACRO PARSER DEMO")
    print("=" * 50)
    
    # Initialize parser
    parser = MacroParser(swg_directory=temp_dir)
    
    # Scan macro directories
    print("🔍 Scanning macro directories...")
    found_dirs = parser.scan_macro_directories()
    print(f"Found directories: {list(found_dirs.keys())}")
    
    # Load all macros
    print("📖 Loading macros...")
    macros = parser.load_all_macros()
    print(f"Loaded {len(macros)} macros:")
    for name, macro in list(macros.items())[:5]:
        print(f"  • {name} ({macro.category})")
    
    # Load all aliases
    print("📖 Loading aliases...")
    aliases = parser.load_all_aliases()
    print(f"Loaded {len(aliases)} aliases:")
    for name, alias in list(aliases.items())[:5]:
        print(f"  • {name} -> {alias.command}")
    
    # Analyze macros
    print("📊 Analyzing macros...")
    analysis = parser.analyze_macros()
    print(f"Analysis results:")
    print(f"  • Total macros: {analysis.total_macros}")
    print(f"  • Total aliases: {analysis.total_aliases}")
    print(f"  • Critical macros: {len(analysis.critical_macros)}")
    print(f"  • Critical aliases: {len(analysis.critical_aliases)}")
    print(f"  • Missing macros: {len(analysis.missing_macros)}")
    print(f"  • Missing aliases: {len(analysis.missing_aliases)}")
    
    # Show category distribution
    print(f"  • Macro categories: {analysis.macro_categories}")
    print(f"  • Alias categories: {analysis.alias_categories}")
    
    # Save analysis report
    report_path = parser.save_analysis_report(analysis)
    print(f"📄 Analysis report saved to: {report_path}")
    
    return parser, analysis


def demo_alias_analyzer(parser):
    """Demonstrate alias analyzer functionality."""
    print("\n🔍 ALIAS ANALYZER DEMO")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = AliasAnalyzer()
    
    # Load aliases from parser
    aliases_data = {name: {"command": alias.command, "category": alias.category} 
                   for name, alias in parser.aliases.items()}
    analyzer.load_aliases(aliases_data)
    
    # Analyze patterns
    print("🔍 Analyzing alias patterns...")
    patterns = analyzer.analyze_patterns()
    print(f"Found {len(patterns)} unique patterns:")
    
    for pattern_name, pattern_data in list(patterns.items())[:5]:
        print(f"  • {pattern_name} (freq: {pattern_data.frequency}, complexity: {pattern_data.complexity_score:.2f})")
    
    # Get comprehensive analysis
    print("📊 Generating comprehensive analysis...")
    analysis = analyzer.get_comprehensive_analysis()
    print(f"Analysis results:")
    print(f"  • Total aliases: {analysis.total_aliases}")
    print(f"  • Unique patterns: {analysis.unique_patterns}")
    print(f"  • Most common patterns: {analysis.most_common_patterns[:3]}")
    print(f"  • Category distribution: {analysis.category_distribution}")
    print(f"  • Complexity distribution: {analysis.complexity_distribution}")
    
    # Find dependency chains
    print("🔗 Finding dependency chains...")
    chains = analyzer.find_dependency_chains()
    print(f"Found {len(chains)} dependency chains")
    
    # Generate optimization suggestions
    print("💡 Generating optimization suggestions...")
    suggestions = analyzer.generate_optimization_suggestions()
    print("Suggestions:")
    for suggestion in suggestions[:3]:
        print(f"  • {suggestion}")
    
    # Save analysis report
    report_path = analyzer.save_analysis_report(analysis)
    print(f"📄 Alias analysis report saved to: {report_path}")
    
    return analyzer, analysis


def demo_macro_recommender(parser, analysis):
    """Demonstrate macro recommender functionality."""
    print("\n💡 MACRO RECOMMENDER DEMO")
    print("=" * 50)
    
    # Initialize recommender
    recommender = MacroRecommender()
    
    # Find missing macros
    print("🔍 Finding missing macros...")
    missing_macros = recommender.find_missing_macros(parser.macros)
    print(f"Missing critical macros: {missing_macros}")
    
    # Generate recommendations
    print("💡 Generating recommendations...")
    recommendations = recommender.generate_recommendations(missing_macros, parser.macros)
    print(f"Generated {len(recommendations)} recommendations:")
    
    for rec in recommendations[:5]:
        print(f"  • {rec.macro_name} ({rec.category}) - {rec.reason}")
        print(f"    Priority: {rec.priority}, Critical: {rec.is_critical}")
        print(f"    Suggested content: {rec.suggested_content[:50]}...")
    
    # Create fallback maps
    print("🔄 Creating fallback maps...")
    fallback_maps = []
    for missing_macro in missing_macros[:3]:
        fallback = recommender.create_fallback_map(missing_macro, parser.macros)
        if fallback:
            fallback_maps.append(fallback)
            print(f"  • {fallback.original_macro} → {fallback.fallback_macro} (confidence: {fallback.confidence:.1%})")
    
    # Generate comprehensive report
    print("📊 Generating comprehensive report...")
    report = recommender.generate_comprehensive_report(
        missing_macros, analysis.missing_aliases, parser.macros, parser.aliases
    )
    print(f"Report summary:")
    print(f"  • Total recommendations: {report.total_recommendations}")
    print(f"  • Critical recommendations: {report.critical_recommendations}")
    print(f"  • Missing macros: {len(report.missing_macros)}")
    print(f"  • Missing aliases: {len(report.missing_aliases)}")
    print(f"  • Fallback maps: {len(report.fallback_maps)}")
    print(f"  • Priority order: {report.priority_order[:5]}")
    
    # Save recommendation report
    report_path = recommender.save_recommendation_report(report)
    print(f"📄 Recommendation report saved to: {report_path}")
    
    # Create sample macro file
    if recommendations:
        sample_rec = recommendations[0]
        macro_file = recommender.create_macro_file(
            sample_rec.macro_name, sample_rec.suggested_content
        )
        print(f"📝 Created sample macro file: {macro_file}")
    
    return recommender, report


def demo_shortcut_helper():
    """Demonstrate shortcut helper functionality."""
    print("\n⚡ SHORTCUT HELPER DEMO")
    print("=" * 50)
    
    # Initialize shortcut helper
    helper = ShortcutHelper()
    
    # Add some shortcuts
    print("➕ Adding shortcuts...")
    shortcuts_to_add = [
        ("heal", "/heal {target}", "combat", "F1", "Heal target"),
        ("buff", "/buff {target}", "combat", "F2", "Buff target"),
        ("attack", "/attack {target}", "combat", "F3", "Attack target"),
        ("travel", "/travel {destination}", "travel", "F6", "Travel to destination"),
        ("craft", "/craft {item}", "crafting", "F8", "Craft item"),
        ("loot", "/loot", "utility", "F9", "Loot items"),
        ("status", "/status", "utility", "F10", "Check status"),
        ("say", "/say {message}", "social", "F11", "Say message")
    ]
    
    for name, command, category, hotkey, description in shortcuts_to_add:
        success = helper.add_shortcut(name, command, category, hotkey, description)
        if success:
            print(f"  ✅ Added: {name} ({category})")
    
    # Test category organization
    print("\n📂 Category organization:")
    for category in ["combat", "travel", "crafting", "utility", "social"]:
        shortcuts = helper.get_shortcuts_by_category(category)
        print(f"  • {category}: {len(shortcuts)} shortcuts")
    
    # Test favorites
    print("\n⭐ Managing favorites:")
    helper.toggle_favorite("heal")
    helper.toggle_favorite("buff")
    helper.toggle_favorite("travel")
    
    favorites = helper.get_favorite_shortcuts()
    print(f"  • Favorites: {[s.name for s in favorites]}")
    
    # Test usage tracking
    print("\n📊 Usage tracking:")
    helper.update_shortcut_usage("heal")
    helper.update_shortcut_usage("heal")
    helper.update_shortcut_usage("buff")
    
    most_used = helper.get_most_used_shortcuts(5)
    print(f"  • Most used: {most_used}")
    
    # Test search
    print("\n🔍 Search functionality:")
    results = helper.search_shortcuts("heal")
    print(f"  • Search 'heal': {len(results)} results")
    
    # Test suggestions
    print("\n💡 Context suggestions:")
    suggestions = helper.get_shortcut_suggestions("combat")
    print(f"  • Combat suggestions: {suggestions[:5]}")
    
    # Generate report
    print("\n📊 Generating shortcut report...")
    report = helper.generate_shortcut_report()
    print(f"Report summary:")
    print(f"  • Total shortcuts: {report.total_shortcuts}")
    print(f"  • Categories: {list(report.categories.keys())}")
    print(f"  • Most used shortcuts: {report.most_used_shortcuts[:3]}")
    print(f"  • Unused shortcuts: {len(report.unused_shortcuts)}")
    print(f"  • Favorite shortcuts: {report.favorite_shortcuts}")
    print(f"  • Suggestions: {report.suggestions[:3]}")
    
    # Export shortcuts
    export_path = helper.export_shortcuts()
    print(f"📄 Shortcuts exported to: {export_path}")
    
    return helper, report


def demo_discord_alerts(parser, analysis, recommender, report):
    """Demonstrate Discord alerts functionality."""
    print("\n📢 DISCORD ALERTS DEMO")
    print("=" * 50)
    
    # Initialize Discord alerts
    alerts = DiscordMacroAlerts()
    
    # Create missing macros alert
    print("🚨 Creating missing macros alert...")
    missing_alert = alerts.create_missing_macros_alert(
        analysis.missing_macros,
        analysis.missing_aliases,
        [rec.reason for rec in report.recommendations[:3]]
    )
    print(f"Alert created: {missing_alert.title}")
    print(f"  • Type: {missing_alert.alert_type}")
    print(f"  • Priority: {missing_alert.priority}")
    print(f"  • Missing items: {len(missing_alert.missing_items)}")
    print(f"  • Recommendations: {len(missing_alert.recommendations)}")
    
    # Create recommendation alert
    print("\n💡 Creating recommendation alert...")
    recommendations = [rec.reason for rec in report.recommendations[:5]]
    rec_alert = alerts.create_recommendation_alert(recommendations, "combat")
    print(f"Recommendation alert created: {rec_alert.title}")
    print(f"  • Type: {rec_alert.alert_type}")
    print(f"  • Recommendations: {len(rec_alert.recommendations)}")
    
    # Create fallback map alert
    print("\n🔄 Creating fallback map alert...")
    fallback_data = []
    for fallback in report.fallback_maps[:3]:
        fallback_data.append({
            "original_macro": fallback.original_macro,
            "fallback_macro": fallback.fallback_macro,
            "confidence": fallback.confidence
        })
    
    fallback_alert = alerts.create_fallback_map_alert(fallback_data)
    print(f"Fallback alert created: {fallback_alert.title}")
    print(f"  • Type: {fallback_alert.alert_type}")
    print(f"  • Fallback maps: {len(fallback_data)}")
    
    # Get alert summary
    print("\n📊 Alert summary:")
    summary = alerts.get_alert_summary()
    print(f"  • Total alerts: {summary.total_alerts}")
    print(f"  • Critical alerts: {summary.critical_alerts}")
    print(f"  • Warning alerts: {summary.warning_alerts}")
    print(f"  • Info alerts: {summary.info_alerts}")
    print(f"  • Alerts by category: {summary.alerts_by_category}")
    
    # Save alert history
    history_path = alerts.save_alert_history()
    print(f"📄 Alert history saved to: {history_path}")
    
    # Test Discord connection (mocked)
    print("\n🔧 Testing Discord connection...")
    connection_test = alerts.test_discord_connection()
    print(f"Connection test result: {connection_test}")
    
    return alerts, summary


def demo_integration_workflow():
    """Demonstrate complete integration workflow."""
    print("\n🔄 INTEGRATION WORKFLOW DEMO")
    print("=" * 50)
    
    # Create demo environment
    temp_dir = create_demo_environment()
    
    try:
        # 1. Parse and analyze macros/aliases
        print("Step 1: Parsing and analyzing macros/aliases...")
        parser, macro_analysis = demo_macro_parser(temp_dir)
        
        # 2. Analyze alias patterns
        print("\nStep 2: Analyzing alias patterns...")
        analyzer, alias_analysis = demo_alias_analyzer(parser)
        
        # 3. Generate recommendations
        print("\nStep 3: Generating recommendations...")
        recommender, recommendation_report = demo_macro_recommender(parser, macro_analysis)
        
        # 4. Manage shortcuts
        print("\nStep 4: Managing shortcuts...")
        helper, shortcut_report = demo_shortcut_helper()
        
        # 5. Send Discord alerts
        print("\nStep 5: Sending Discord alerts...")
        alerts, alert_summary = demo_discord_alerts(parser, macro_analysis, recommender, recommendation_report)
        
        # 6. Generate comprehensive summary
        print("\n📋 COMPREHENSIVE SUMMARY")
        print("=" * 50)
        print(f"✅ Macro parsing: {macro_analysis.total_macros} macros, {macro_analysis.total_aliases} aliases")
        print(f"✅ Alias analysis: {alias_analysis.unique_patterns} patterns, {len(alias_analysis.optimization_suggestions)} suggestions")
        print(f"✅ Recommendations: {recommendation_report.total_recommendations} recommendations, {len(recommendation_report.fallback_maps)} fallbacks")
        print(f"✅ Shortcuts: {shortcut_report.total_shortcuts} shortcuts, {len(shortcut_report.favorite_shortcuts)} favorites")
        print(f"✅ Discord alerts: {alert_summary.total_alerts} alerts sent")
        
        print("\n🎉 Integration workflow completed successfully!")
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up demo environment: {temp_dir}")


def main():
    """Main demo function."""
    print("🚀 BATCH 065 - MACRO/ALIAS LEARNING + SHORTCUT HELPER DEMO")
    print("=" * 70)
    print("This demo showcases all features of the macro learning system:")
    print("• Parse /alias and macro folders")
    print("• Build fallback map if macro is missing")
    print("• Store best practice macros in data/macros/")
    print("• Recommend missing macros and alert via Discord")
    print("• Shortcut management and organization")
    print("=" * 70)
    
    # Run individual demos
    demo_integration_workflow()
    
    print("\n🎯 Demo completed! Check the generated files for detailed results.")
    print("📁 Generated files:")
    print("  • Macro analysis reports in logs/")
    print("  • Alias analysis reports in logs/")
    print("  • Recommendation reports in logs/")
    print("  • Shortcut exports in data/")
    print("  • Alert history in logs/")


if __name__ == "__main__":
    main() 
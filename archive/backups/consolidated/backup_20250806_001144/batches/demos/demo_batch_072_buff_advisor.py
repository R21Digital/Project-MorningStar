#!/usr/bin/env python3
"""
Demo script for Batch 072 - Buff Advisor + Stat-Based Build Recommender

This script demonstrates the comprehensive buff advisor system that:
- Analyzes character stats (via parsed /stats logs or user input)
- Recommends buff food and entertainer dances
- Suggests armor setups tied to build awareness
- Integrates with stat optimizer and build-aware behavior systems
"""

import json
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.buff_advisor import BuffAdvisor, create_buff_advisor
from android_ms11.utils.logging_utils import log_event


def demo_stat_analysis():
    """Demonstrate character stat analysis functionality."""
    print("\n" + "="*60)
    print("DEMO: Character Stat Analysis")
    print("="*60)
    
    # Sample stats from a /stats log
    sample_stats_log = """
    Character: TestPlayer
    Strength: 95
    Agility: 110
    Constitution: 105
    Stamina: 88
    Mind: 120
    Focus: 115
    Willpower: 92
    """
    
    # Sample direct stats input
    sample_stats = {
        "strength": 95,
        "agility": 110,
        "constitution": 105,
        "stamina": 88,
        "mind": 120,
        "focus": 115,
        "willpower": 92
    }
    
    advisor = create_buff_advisor()
    
    print("1. Parsing stats from /stats log:")
    parsed_stats = advisor.stat_analyzer.parse_stats_log(sample_stats_log)
    print(f"   Parsed stats: {parsed_stats}")
    
    print("\n2. Analyzing stat distribution:")
    analysis = advisor.stat_analyzer.analyze_stat_distribution(sample_stats)
    print(f"   Total stats: {analysis['total_stats']}")
    print(f"   Average stat: {analysis['average_stat']:.1f}")
    print(f"   Weakest stats: {analysis['weakest_stats']}")
    print(f"   Strongest stats: {analysis['strongest_stats']}")
    
    print("\n3. Getting optimization priorities:")
    priorities = advisor.stat_analyzer.get_optimization_priorities(sample_stats, "pve_damage")
    print("   PvE Damage priorities:")
    for i, priority in enumerate(priorities[:3], 1):
        print(f"   {i}. {priority['stat']}: {priority['current_value']} (score: {priority['priority_score']:.1f})")


def demo_buff_recommendations():
    """Demonstrate buff food and entertainer dance recommendations."""
    print("\n" + "="*60)
    print("DEMO: Buff Recommendations")
    print("="*60)
    
    sample_stats = {
        "strength": 95,
        "agility": 110,
        "constitution": 105,
        "stamina": 88,
        "mind": 120,
        "focus": 115,
        "willpower": 92
    }
    
    advisor = create_buff_advisor()
    
    print("1. Buff food recommendations for PvE damage:")
    buff_recs = advisor.get_buff_recommendations(sample_stats, "pve_damage", "medium")
    
    if "buff_food" in buff_recs:
        print("   Recommended buff foods:")
        for i, food in enumerate(buff_recs["buff_food"][:3], 1):
            print(f"   {i}. {food['stat_target'].title()} food: {', '.join(food['items'])}")
            print(f"      Bonus: +{food['expected_improvement']} {food['stat_target']}")
    
    print("\n2. Entertainer dance recommendations:")
    if "entertainer_dances" in buff_recs:
        print("   Recommended dances:")
        for i, dance in enumerate(buff_recs["entertainer_dances"][:3], 1):
            print(f"   {i}. {dance['dance_name']} ({dance['entertainer_level']} level)")
            print(f"      Bonus: +{dance['expected_improvement']} {dance['stat_target']}")
    
    print("\n3. Combined recommendations summary:")
    print(f"   Total recommendations: {buff_recs.get('recommendation_count', 0)}")
    print(f"   Expected improvements: {buff_recs.get('total_expected_improvements', {})}")


def demo_template_recommendations():
    """Demonstrate armor and weapon setup recommendations."""
    print("\n" + "="*60)
    print("DEMO: Template Recommendations")
    print("="*60)
    
    sample_stats = {
        "strength": 95,
        "agility": 110,
        "constitution": 105,
        "stamina": 88,
        "mind": 120,
        "focus": 115,
        "willpower": 92
    }
    
    # Sample build data (simulating Batch 070 integration)
    sample_build_data = {
        "professions": ["rifleman", "medic"],
        "weapons": ["rifle", "carbine"],
        "combat_style": "hybrid",
        "min_distance": 5
    }
    
    advisor = create_buff_advisor()
    
    print("1. Armor setup recommendations:")
    template_recs = advisor.get_template_recommendations(sample_stats, "TestPlayer", "balanced", "medium")
    
    if "armor_setup" in template_recs:
        armor = template_recs["armor_setup"]
        print(f"   Recommended armor: {armor.get('template_name', 'Unknown')}")
        print(f"   Combat style: {armor.get('combat_style', 'Unknown')}")
        print(f"   Cost: {armor.get('cost', 'Unknown')}")
        print(f"   Total stat bonuses: {armor.get('total_stat_bonuses', {})}")
    
    print("\n2. Weapon setup recommendations:")
    if "weapon_setup" in template_recs:
        weapon = template_recs["weapon_setup"]
        print(f"   Recommended weapon: {weapon.get('weapon_name', 'Unknown')}")
        print(f"   Range: {weapon.get('range', 'Unknown')}")
        print(f"   Damage type: {weapon.get('damage_type', 'Unknown')}")
        print(f"   Weapon bonuses: {weapon.get('weapon_bonus', {})}")
    
    print("\n3. Complete template recommendation:")
    print(f"   Total expected improvements: {template_recs.get('total_expected_improvements', {})}")


def demo_build_integration():
    """Demonstrate build integration with Batch 070."""
    print("\n" + "="*60)
    print("DEMO: Build Integration")
    print("="*60)
    
    sample_stats = {
        "strength": 95,
        "agility": 110,
        "constitution": 105,
        "stamina": 88,
        "mind": 120,
        "focus": 115,
        "willpower": 92
    }
    
    advisor = create_buff_advisor()
    
    print("1. Build compatibility report:")
    compatibility_report = advisor.get_build_compatibility_report(sample_stats, "TestPlayer", "balanced")
    
    if "validation" in compatibility_report:
        validation = compatibility_report["validation"]
        print(f"   Compatible: {validation.get('compatible', False)}")
        print(f"   Issues: {len(validation.get('issues', []))}")
        print(f"   Warnings: {len(validation.get('warnings', []))}")
        print(f"   Suggestions: {len(validation.get('suggestions', []))}")
    
    if "analysis" in compatibility_report:
        analysis = compatibility_report["analysis"]
        build_recs = analysis.get("build_aware_recommendations", {})
        print(f"   Compatibility score: {build_recs.get('compatibility_score', 0.0):.2f}")
        print(f"   Missing stats: {build_recs.get('missing_stats', [])}")
        print(f"   Optimal stats: {build_recs.get('optimal_stats', [])}")


def demo_comprehensive_analysis():
    """Demonstrate comprehensive character analysis and recommendations."""
    print("\n" + "="*60)
    print("DEMO: Comprehensive Analysis")
    print("="*60)
    
    # Sample stats log content
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
    
    advisor = create_buff_advisor()
    
    print("1. Comprehensive character analysis:")
    results = advisor.analyze_character_and_recommend(
        stats_log, "TestPlayer", "pve_damage", "medium", True
    )
    
    if "error" not in results:
        print("   Analysis completed successfully!")
        
        summary = results.get("summary", {})
        print(f"   Total stats: {summary.get('total_stats', 0)}")
        print(f"   Average stat: {summary.get('average_stat', 0):.1f}")
        print(f"   Top priorities: {summary.get('top_priorities', [])}")
        print(f"   Buff recommendations: {summary.get('buff_recommendations_count', 0)}")
        
        template_recs = summary.get("template_recommendations", {})
        print(f"   Armor setup: {template_recs.get('armor_setup', 'Unknown')}")
        print(f"   Weapon setup: {template_recs.get('weapon_setup', 'Unknown')}")
        
        print("\n   Key recommendations:")
        for rec in summary.get("key_recommendations", [])[:3]:
            print(f"   - {rec}")
    
    print("\n2. Exporting recommendations report:")
    if "error" not in results:
        filepath = advisor.export_recommendations_report(results)
        if filepath:
            print(f"   Report exported to: {filepath}")
        else:
            print("   Export failed")


def demo_error_handling():
    """Demonstrate error handling and edge cases."""
    print("\n" + "="*60)
    print("DEMO: Error Handling")
    print("="*60)
    
    advisor = create_buff_advisor()
    
    print("1. Invalid stats input:")
    result = advisor.analyze_character_and_recommend({})
    print(f"   Result: {result.get('error', 'No error')}")
    
    print("\n2. Invalid stats log:")
    result = advisor.analyze_from_stats_log("Invalid log content")
    print(f"   Result: {result.get('error', 'No error')}")
    
    print("\n3. Build compatibility with no build data:")
    result = advisor.get_build_compatibility_report({"strength": 100})
    print(f"   Result: {result.get('error', 'No error')}")


def main():
    """Run the complete demo."""
    print("Batch 072 - Buff Advisor + Stat-Based Build Recommender")
    print("="*60)
    print("This demo showcases the comprehensive buff advisor system that")
    print("integrates character stat analysis, buff recommendations, template")
    print("recommendations, and build awareness from Batch 070.")
    print("="*60)
    
    try:
        # Run all demo sections
        demo_stat_analysis()
        demo_buff_recommendations()
        demo_template_recommendations()
        demo_build_integration()
        demo_comprehensive_analysis()
        demo_error_handling()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("The Buff Advisor system provides:")
        print("✓ Character stat analysis from /stats logs")
        print("✓ Buff food and entertainer dance recommendations")
        print("✓ Armor and weapon setup suggestions")
        print("✓ Build-aware compatibility analysis")
        print("✓ Integration with stat optimizer and build awareness")
        print("✓ Comprehensive reporting and export capabilities")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        log_event(f"[DEMO] Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 
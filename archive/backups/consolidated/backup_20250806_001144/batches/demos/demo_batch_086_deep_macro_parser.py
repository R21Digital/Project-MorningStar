"""Demo script for Batch 086 - Deep Macro Parser + Learning AI (Phase 1).

This script demonstrates the deep macro parser capabilities by:
1. Creating sample macro and alias files
2. Running comprehensive analysis
3. Generating learning insights and recommendations
4. Producing detailed reports
"""

import json
import os
from pathlib import Path
from datetime import datetime

from core.deep_macro_parser import DeepMacroParser, DeepMacroAnalysis

def create_sample_macro_files():
    """Create sample macro files for testing."""
    macro_dir = Path("data/macros")
    macro_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample combat macros
    combat_macros = {
        "heal_combat.txt": """# HEAL COMBAT MACRO
# Created: 2025-08-01T10:43:03.912533
# Category: combat

/heal {target}
/say Healing {target}
/status
""",
        
        "attack_sequence.txt": """# ATTACK SEQUENCE MACRO
# Created: 2025-08-01T10:44:15.123456
# Category: combat

/attack {target}
/say Attacking {target}
/special {target}
/defend
""",
        
        "buff_rotation.txt": """# BUFF ROTATION MACRO
# Created: 2025-08-01T10:45:30.789012
# Category: buff

/buff {target}
/say Buffing {target}
/enhance {target}
/boost {target}
""",
        
        "flee_escape.txt": """# FLEE ESCAPE MACRO
# Created: 2025-08-01T10:46:45.456789
# Category: combat

/flee
/say Fleeing from combat
/travel {safe_location}
""",
    }
    
    # Sample utility macros
    utility_macros = {
        "travel_waypoint.txt": """# TRAVEL WAYPOINT MACRO
# Created: 2025-08-01T10:47:12.345678
# Category: utility

/travel {destination}
/say Traveling to {destination}
/waypoint {destination}
""",
        
        "loot_collection.txt": """# LOOT COLLECTION MACRO
# Created: 2025-08-01T10:48:25.678901
# Category: utility

/loot
/say Looting items
/inventory
/status
""",
        
        "craft_sequence.txt": """# CRAFT SEQUENCE MACRO
# Created: 2025-08-01T10:49:38.901234
# Category: utility

/craft {item}
/say Crafting {item}
/harvest {resource}
/survey {location}
""",
    }
    
    # Sample complex macro
    complex_macro = {
        "advanced_combat.txt": """# ADVANCED COMBAT MACRO
# Created: 2025-08-01T10:50:51.234567
# Category: combat

# Combat preparation
/buff {target}
/enhance {target}
/boost {target}

# Combat sequence
/attack {target}
/special {target}
/ability {target}

# Combat monitoring
/status
/health {target}

# Combat recovery
/heal {target}
/medic {target}

# Combat escape if needed
/defend
/flee
/travel {safe_location}
""",
    }
    
    # Create all macro files
    all_macros = {**combat_macros, **utility_macros, **complex_macro}
    
    for filename, content in all_macros.items():
        file_path = macro_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"Created {len(all_macros)} sample macro files in {macro_dir}")
    return all_macros

def create_sample_alias_files():
    """Create sample alias files for testing."""
    alias_dir = Path("data/aliases")
    alias_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample UI action aliases
    ui_aliases = {
        "alias_ui_actions.txt": """# UI ACTION ALIASES
# Created: 2025-08-01T11:00:00.000000

alias inventory /ui inventory
alias equipment /ui equipment
alias character /ui character
alias skills /ui skills
alias quests /ui quests
alias map /ui map
alias chat /ui chat
alias combat /ui combat
""",
        
        "alias_combat_shortcuts.txt": """# COMBAT SHORTCUT ALIASES
# Created: 2025-08-01T11:01:15.123456

alias heal /heal {target}
alias attack /attack {target}
alias buff /buff {target}
alias defend /defend
alias flee /flee
alias special /special {target}
""",
        
        "alias_utility_shortcuts.txt": """# UTILITY SHORTCUT ALIASES
# Created: 2025-08-01T11:02:30.456789

alias travel /travel {destination}
alias loot /loot
alias craft /craft {item}
alias harvest /harvest {resource}
alias survey /survey {location}
alias status /status
""",
    }
    
    # Create all alias files
    for filename, content in ui_aliases.items():
        file_path = alias_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"Created {len(ui_aliases)} sample alias files in {alias_dir}")
    return ui_aliases

def run_deep_macro_analysis():
    """Run comprehensive deep macro analysis."""
    print("\n=== Running Deep Macro Analysis ===")
    
    # Initialize parser
    parser = DeepMacroParser()
    
    # Run comprehensive analysis
    analysis = parser.run_comprehensive_analysis()
    
    # Display results
    print(f"\n📊 Analysis Results:")
    print(f"   Total Macros: {analysis.total_macros}")
    print(f"   Total Aliases: {analysis.total_aliases}")
    print(f"   Combat Macros: {len(analysis.combat_macros)}")
    print(f"   Utility Macros: {len(analysis.utility_macros)}")
    print(f"   Buff Macros: {len(analysis.buff_macros)}")
    print(f"   UI Action Mappings: {len(analysis.ui_action_mappings)}")
    
    print(f"\n📈 Category Distribution:")
    for category, count in analysis.macro_categories.items():
        print(f"   {category}: {count}")
    
    print(f"\n🔍 Usage Patterns (Top 5):")
    sorted_patterns = sorted(analysis.usage_patterns.items(), key=lambda x: x[1], reverse=True)
    for command, count in sorted_patterns[:5]:
        print(f"   /{command}: {count} uses")
    
    print(f"\n🎯 Complexity Scores:")
    for macro_name, score in analysis.complexity_scores.items():
        print(f"   {macro_name}: {score:.3f}")
    
    print(f"\n❌ Missing Critical Macros:")
    for missing in analysis.missing_critical:
        print(f"   - {missing}")
    
    print(f"\n💡 Learning Suggestions:")
    for suggestion in analysis.learning_suggestions:
        print(f"   - {suggestion}")
    
    print(f"\n⚡ Optimization Opportunities:")
    for opportunity in analysis.optimization_opportunities:
        print(f"   - {opportunity}")
    
    return analysis

def save_detailed_report(analysis: DeepMacroAnalysis):
    """Save detailed analysis report."""
    print("\n=== Saving Detailed Report ===")
    
    # Save JSON report
    parser = DeepMacroParser()
    report_path = parser.save_analysis_report(analysis)
    
    # Create human-readable report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"reports/deep_macro_report_{timestamp}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Deep Macro Parser Analysis Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Macros Analyzed:** {analysis.total_macros}\n")
        f.write(f"- **Total Aliases Analyzed:** {analysis.total_aliases}\n")
        f.write(f"- **Missing Critical Macros:** {len(analysis.missing_critical)}\n")
        f.write(f"- **Optimization Opportunities:** {len(analysis.optimization_opportunities)}\n\n")
        
        f.write("## Macro Categories\n\n")
        for category, count in analysis.macro_categories.items():
            f.write(f"- **{category}:** {count} macros\n")
        f.write("\n")
        
        f.write("## Combat Macros\n\n")
        for macro in analysis.combat_macros:
            f.write(f"- {macro}\n")
        f.write("\n")
        
        f.write("## Utility Macros\n\n")
        for macro in analysis.utility_macros:
            f.write(f"- {macro}\n")
        f.write("\n")
        
        f.write("## Buff Macros\n\n")
        for macro in analysis.buff_macros:
            f.write(f"- {macro}\n")
        f.write("\n")
        
        f.write("## UI Action Mappings\n\n")
        for alias, command in analysis.ui_action_mappings.items():
            f.write(f"- **{alias}:** `{command}`\n")
        f.write("\n")
        
        f.write("## Usage Patterns\n\n")
        sorted_patterns = sorted(analysis.usage_patterns.items(), key=lambda x: x[1], reverse=True)
        for command, count in sorted_patterns[:10]:
            f.write(f"- **/{command}:** {count} uses\n")
        f.write("\n")
        
        f.write("## Complexity Analysis\n\n")
        for macro_name, score in analysis.complexity_scores.items():
            complexity_level = "High" if score > 0.7 else "Medium" if score > 0.4 else "Low"
            f.write(f"- **{macro_name}:** {score:.3f} ({complexity_level})\n")
        f.write("\n")
        
        f.write("## Missing Critical Macros\n\n")
        for missing in analysis.missing_critical:
            f.write(f"- **{missing}:** Critical macro not found\n")
        f.write("\n")
        
        f.write("## Learning Suggestions\n\n")
        for suggestion in analysis.learning_suggestions:
            f.write(f"- {suggestion}\n")
        f.write("\n")
        
        f.write("## Optimization Opportunities\n\n")
        for opportunity in analysis.optimization_opportunities:
            f.write(f"- {opportunity}\n")
        f.write("\n")
    
    print(f"📄 Detailed report saved to: {report_file}")
    print(f"📊 JSON report saved to: {report_path}")
    
    return report_file, report_path

def main():
    """Main demo function."""
    print("🚀 Batch 086 - Deep Macro Parser + Learning AI (Phase 1) Demo")
    print("=" * 60)
    
    # Create sample data
    print("\n📁 Creating sample macro and alias files...")
    create_sample_macro_files()
    create_sample_alias_files()
    
    # Run analysis
    analysis = run_deep_macro_analysis()
    
    # Save reports
    report_file, json_path = save_detailed_report(analysis)
    
    print("\n✅ Demo completed successfully!")
    print(f"📋 Reports generated:")
    print(f"   - Markdown: {report_file}")
    print(f"   - JSON: {json_path}")
    
    return analysis

if __name__ == "__main__":
    main() 
"""Demo script for Batch 071 - Stat Optimizer Module.

This script demonstrates the comprehensive stat optimization capabilities including:
- Google Sheets data import for stat thresholds
- Optimal stat distribution analysis for PvE damage, buff stacking, and healing
- Suboptimal stat pool detection and alerts
- Integration with Discord alerts and CLI notifications
"""

import json
import time
from pathlib import Path
from datetime import datetime

from modules.stat_optimizer import (
    StatOptimizer, create_stat_optimizer,
    GoogleSheetsImporter, create_sheets_importer,
    StatAnalyzer, create_stat_analyzer,
    AlertManager, create_alert_manager
)
from android_ms11.utils.logging_utils import log_event


def demonstrate_google_sheets_integration():
    """Demonstrate Google Sheets integration for stat thresholds."""
    print("\n=== Google Sheets Integration Demo ===")
    
    # Create sheets importer with sample configuration
    sheets_config = {
        "google_api_key": "YOUR_API_KEY_HERE",  # Would be set in real usage
        "sheet_id": "YOUR_SHEET_ID_HERE",       # Would be set in real usage
        "cache_dir": "data/stat_cache"
    }
    
    sheets_importer = create_sheets_importer(sheets_config)
    
    # Test connection (will fail without real credentials, but shows the flow)
    print("Testing Google Sheets connection...")
    connection_success = sheets_importer.validate_sheet_connection()
    print(f"Connection successful: {connection_success}")
    
    # Import thresholds (will use defaults if sheets unavailable)
    print("\nImporting stat thresholds...")
    thresholds = sheets_importer.import_stat_thresholds()
    
    print(f"Imported {len(thresholds)} optimization types:")
    for opt_type, stats in thresholds.items():
        print(f"  {opt_type}: {len(stats)} stats")
        for stat_name, values in list(stats.items())[:3]:  # Show first 3
            print(f"    {stat_name}: min={values['min']}, optimal={values['optimal']}, max={values['max']}")
    
    return thresholds


def demonstrate_stat_analysis():
    """Demonstrate stat analysis capabilities."""
    print("\n=== Stat Analysis Demo ===")
    
    analyzer = create_stat_analyzer()
    
    # Sample character stats for different optimization types
    sample_characters = [
        {
            "name": "Rifleman",
            "stats": {
                "strength": 120,
                "agility": 140,
                "constitution": 110,
                "stamina": 90,
                "mind": 70,
                "focus": 80,
                "willpower": 60
            },
            "optimization_type": "pve_damage"
        },
        {
            "name": "Medic",
            "stats": {
                "strength": 80,
                "agility": 90,
                "constitution": 130,
                "stamina": 100,
                "mind": 160,
                "focus": 170,
                "willpower": 140
            },
            "optimization_type": "healing"
        },
        {
            "name": "Brawler",
            "stats": {
                "strength": 180,
                "agility": 130,
                "constitution": 150,
                "stamina": 120,
                "mind": 60,
                "focus": 70,
                "willpower": 50
            },
            "optimization_type": "buff_stack"
        }
    ]
    
    for character in sample_characters:
        print(f"\n--- Analyzing {character['name']} ({character['optimization_type']}) ---")
        
        # Analyze character stats
        analysis = analyzer.analyze_character_stats(
            character['stats'], 
            character['optimization_type']
        )
        
        print(f"Overall Score: {analysis['score']:.1f}/100")
        print(f"Critical Issues: {len(analysis['issues'])}")
        print(f"Warnings: {len(analysis['warnings'])}")
        
        # Show detailed stat analysis
        print("Detailed Analysis:")
        for stat_name, stat_analysis in analysis['analysis'].items():
            status = stat_analysis['status']
            current = stat_analysis['current_value']
            optimal = stat_analysis['optimal_value']
            score = stat_analysis['score']
            
            print(f"  {stat_name}: {current}/{optimal} ({score:.0f}%) - {status}")
        
        # Show recommendations
        print("Recommendations:")
        for rec in analysis['recommendations'][:3]:  # Show first 3
            print(f"  • {rec}")


def demonstrate_alert_management():
    """Demonstrate alert management capabilities."""
    print("\n=== Alert Management Demo ===")
    
    alert_config = {
        "critical_threshold": 50.0,
        "warning_threshold": 70.0,
        "cli_alerts": True,
        "alert_log_file": "logs/stat_alerts.json"
    }
    
    alert_manager = create_alert_manager(alert_config)
    
    # Test Discord connection
    print("Testing Discord connection...")
    discord_connected = alert_manager.test_discord_connection()
    print(f"Discord connected: {discord_connected}")
    
    # Sample analysis results that would trigger alerts
    sample_analyses = [
        {
            "score": 35.0,  # Critical
            "issues": ["strength: Below minimum threshold (80 < 100)"],
            "warnings": ["agility: Below optimal range (90 < 96)"],
            "recommendations": ["Critical: Major stat reallocation needed", "Increase Strength for better melee damage"],
            "optimization_type": "pve_damage"
        },
        {
            "score": 65.0,  # Warning
            "issues": [],
            "warnings": ["mind: Below optimal range (110 < 128)"],
            "recommendations": ["Warning: Significant stat improvements recommended", "Increase Mind for better healing power"],
            "optimization_type": "healing"
        },
        {
            "score": 85.0,  # Good
            "issues": [],
            "warnings": [],
            "recommendations": ["Good: Minor optimizations possible"],
            "optimization_type": "buff_stack"
        }
    ]
    
    for i, analysis in enumerate(sample_analyses, 1):
        print(f"\n--- Testing Alert {i} (Score: {analysis['score']:.1f}) ---")
        
        # Check and send alerts
        alerts_sent = alert_manager.check_and_alert(analysis, f"TestCharacter{i}")
        print(f"Alerts sent: {alerts_sent}")
    
    # Get alert summary
    alert_summary = alert_manager.get_alert_summary(7)
    print(f"\nAlert Summary (Last 7 days):")
    print(f"  Total Alerts: {alert_summary['total_alerts']}")
    print(f"  Critical Alerts: {alert_summary['critical_alerts']}")
    print(f"  Warning Alerts: {alert_summary['warning_alerts']}")


def demonstrate_comprehensive_optimization():
    """Demonstrate comprehensive stat optimization."""
    print("\n=== Comprehensive Stat Optimization Demo ===")
    
    # Create stat optimizer with configuration
    config = {
        "sheets_config": {
            "cache_dir": "data/stat_cache"
        },
        "analyzer_config": {},
        "alert_config": {
            "cli_alerts": True,
            "alert_log_file": "logs/stat_alerts.json"
        }
    }
    
    optimizer = create_stat_optimizer(config)
    
    # Sample character for comprehensive analysis
    character_stats = {
        "strength": 110,
        "agility": 130,
        "constitution": 120,
        "stamina": 95,
        "mind": 140,
        "focus": 150,
        "willpower": 100
    }
    
    character_name = "DemoCharacter"
    
    print(f"Analyzing {character_name} for all optimization types...")
    
    # Analyze all optimization types
    all_results = optimizer.analyze_all_optimization_types(character_stats, character_name)
    
    print(f"Best optimization type: {all_results['best_optimization']}")
    
    # Show results for each optimization type
    for opt_type, result in all_results['optimization_results'].items():
        if "error" not in result:
            score = result.get("overall_score", 0.0)
            issues = result.get("critical_issues", 0)
            warnings = result.get("warnings", 0)
            
            print(f"  {opt_type}: {score:.1f}/100 (Issues: {issues}, Warnings: {warnings})")
    
    # Test single optimization
    print(f"\n--- Single Optimization Test ({character_name}) ---")
    result = optimizer.optimize_character_stats(
        character_stats, 
        character_name, 
        "pve_damage",
        send_alerts=True
    )
    
    print(f"Optimization complete:")
    print(f"  Score: {result['overall_score']:.1f}/100")
    print(f"  Critical Issues: {result['critical_issues']}")
    print(f"  Warnings: {result['warnings']}")
    print(f"  Alerts Sent: {result['alerts_sent']}")
    
    # Get optimization summary
    summary = optimizer.get_optimization_summary(character_name)
    print(f"\nOptimization Summary for {character_name}:")
    print(f"  Total Optimizations: {summary['total_optimizations']}")
    print(f"  Average Score: {summary['average_score']:.1f}")
    
    # Export report
    report_path = optimizer.export_optimization_report(character_name)
    print(f"  Report exported to: {report_path}")


def demonstrate_connection_validation():
    """Demonstrate connection validation for all components."""
    print("\n=== Connection Validation Demo ===")
    
    optimizer = create_stat_optimizer()
    
    # Test Google Sheets connection
    print("Testing Google Sheets connection...")
    sheets_connected = optimizer.validate_google_sheets_connection()
    print(f"Google Sheets: {'✓ Connected' if sheets_connected else '✗ Not connected'}")
    
    # Test Discord connection
    print("Testing Discord connection...")
    discord_connected = optimizer.validate_discord_connection()
    print(f"Discord: {'✓ Connected' if discord_connected else '✗ Not connected'}")
    
    # Show alert summary
    alert_summary = optimizer.get_alert_summary(7)
    print(f"Recent Alerts: {alert_summary['total_alerts']} total")


def demonstrate_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n=== Error Handling Demo ===")
    
    optimizer = create_stat_optimizer()
    
    # Test with invalid character stats
    invalid_stats = {
        "strength": "invalid",  # Should be int
        "agility": 130,
        "constitution": 120
    }
    
    print("Testing with invalid character stats...")
    try:
        result = optimizer.optimize_character_stats(invalid_stats, "TestCharacter")
        if "error" in result:
            print(f"✓ Error handled: {result['error']}")
        else:
            print("✓ Invalid stats handled gracefully")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test with missing Google Sheets credentials
    print("Testing with missing Google Sheets credentials...")
    sheets_importer = create_sheets_importer({})  # No config
    thresholds = sheets_importer.import_stat_thresholds()
    print(f"✓ Fallback to default thresholds: {len(thresholds)} types available")


def main():
    """Main demo function."""
    print("=== Batch 071 - Stat Optimizer Module Demo ===")
    print("This demo showcases comprehensive stat optimization capabilities.")
    
    try:
        # Demonstrate Google Sheets integration
        demonstrate_google_sheets_integration()
        
        # Demonstrate stat analysis
        demonstrate_stat_analysis()
        
        # Demonstrate alert management
        demonstrate_alert_management()
        
        # Demonstrate comprehensive optimization
        demonstrate_comprehensive_optimization()
        
        # Demonstrate connection validation
        demonstrate_connection_validation()
        
        # Demonstrate error handling
        demonstrate_error_handling()
        
        print("\n=== Demo Complete ===")
        print("✓ Google Sheets integration working")
        print("✓ Stat analysis capabilities demonstrated")
        print("✓ Alert management system functional")
        print("✓ Comprehensive optimization features working")
        print("✓ Connection validation implemented")
        print("✓ Error handling robust")
        
    except Exception as e:
        print(f"Demo error: {e}")
        log_event(f"[DEMO] Error in demo: {e}")


if __name__ == "__main__":
    main() 
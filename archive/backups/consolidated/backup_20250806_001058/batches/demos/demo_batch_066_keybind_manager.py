#!/usr/bin/env python3
"""
MS11 Batch 066 - Player Keybind Manager + Validation Reporter Demo

This demo showcases the enhanced keybind manager functionality including:
- SWG configuration file parsing (options.cfg, inputmap.cfg)
- Required keybind validation for combat, healing, navigation, inventory
- Editable override system via CLI/JSON
- Discord integration for critical keybind alerts
- Comprehensive reporting with recommendations
"""

import json
import os
import tempfile
import asyncio
from pathlib import Path

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from modules.keybind_manager import (
    KeybindParser,
    KeybindValidator,
    KeybindOverrideManager,
    DiscordKeybindAlerts,
    KeybindReporter
)


def create_test_config_files(temp_dir: str) -> None:
    """Create test SWG configuration files for demo."""
    # Create options.cfg
    options_cfg = os.path.join(temp_dir, "options.cfg")
    with open(options_cfg, 'w') as f:
        f.write("# SWG Options Configuration\n")
        f.write("Keybind attack F1\n")
        f.write("Keybind use Enter\n")
        f.write("Keybind inventory I\n")
        f.write("Keybind map M\n")
        f.write("Keybind chat Enter\n")
        f.write("Keybind target Tab\n")
        f.write("Keybind heal H\n")
        f.write("Keybind follow F\n")
        f.write("Keybind stop Escape\n")
        f.write("Keybind loot L\n")
        f.write("Keybind custom_action X\n")
    
    # Create inputmap.cfg
    inputmap_cfg = os.path.join(temp_dir, "inputmap.cfg")
    with open(inputmap_cfg, 'w') as f:
        f.write("# SWG Input Map Configuration\n")
        f.write("input camera_zoom MouseWheel\n")
        f.write("input camera_rotate MouseButton2\n")
        f.write("input chat_say Enter\n")
        f.write("input group_chat G\n")


def demo_basic_parsing():
    """Demo basic keybind parsing functionality."""
    print("=" * 60)
    print("DEMO: Basic Keybind Parsing")
    print("=" * 60)
    
    # Create temporary directory with test files
    temp_dir = tempfile.mkdtemp()
    create_test_config_files(temp_dir)
    
    # Initialize parser
    parser = KeybindParser(swg_directory=temp_dir)
    
    # Parse config files
    parse_result = parser.parse_config_files()
    
    print(f"SWG Directory: {parse_result.swg_directory}")
    print(f"Config files found: {len(parse_result.config_files_found)}")
    for file in parse_result.config_files_found:
        print(f"  - {file}")
    
    print(f"\nTotal keybinds detected: {parse_result.total_keybinds}")
    print(f"Parse errors: {len(parse_result.parse_errors)}")
    
    if parse_result.parse_errors:
        for error in parse_result.parse_errors:
            print(f"  Error: {error}")
    
    # Show detected keybinds
    print(f"\nDetected Keybinds:")
    for name, keybind in parse_result.keybinds.items():
        print(f"  {name}: {keybind.key} ({keybind.category.value})")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


def demo_validation():
    """Demo keybind validation functionality."""
    print("\n" + "=" * 60)
    print("DEMO: Keybind Validation")
    print("=" * 60)
    
    # Create temporary directory with test files
    temp_dir = tempfile.mkdtemp()
    create_test_config_files(temp_dir)
    
    # Initialize parser and validator
    parser = KeybindParser(swg_directory=temp_dir)
    validator = KeybindValidator()
    
    # Parse and validate
    parse_result = parser.parse_config_files()
    validation_result = validator.validate_keybinds(
        parse_result.keybinds, 
        parse_result.required_keybinds
    )
    
    print(f"Validation Results:")
    print(f"  Total Keybinds: {validation_result.total_keybinds}")
    print(f"  ✅ Valid: {validation_result.valid_keybinds}")
    print(f"  ❌ Missing: {validation_result.missing_keybinds}")
    print(f"  ⚠️  Conflicting: {validation_result.conflicting_keybinds}")
    print(f"  ❓ Unknown: {validation_result.unknown_keybinds}")
    
    print(f"\nCritical Issues: {len(validation_result.critical_issues)}")
    for issue in validation_result.critical_issues:
        print(f"  • {issue}")
    
    print(f"\nRecommendations: {len(validation_result.recommendations)}")
    for rec in validation_result.recommendations:
        print(f"  • {rec}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


def demo_override_system():
    """Demo manual override system."""
    print("\n" + "=" * 60)
    print("DEMO: Manual Override System")
    print("=" * 60)
    
    # Create temporary override file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        overrides = {
            "attack": {
                "key": "F1",
                "category": "combat",
                "description": "Attack/Combat action",
                "required": True
            },
            "use": {
                "key": "Enter",
                "category": "utility",
                "description": "Use/Interact with objects",
                "required": True
            },
            "custom_action": {
                "key": "X",
                "category": "utility",
                "description": "Custom action",
                "required": False
            }
        }
        json.dump(overrides, f, indent=2)
        override_file = f.name
    
    print(f"Created override file: {override_file}")
    
    # Initialize override manager
    override_manager = KeybindOverrideManager(override_file=override_file)
    
    # Load overrides
    override_manager.load_from_file(override_file)
    
    print(f"\nLoaded overrides: {len(override_manager.list_overrides())}")
    for override in override_manager.list_overrides():
        print(f"  {override.name}: {override.key} ({override.category})")
    
    # Add new override
    success = override_manager.add_override(
        name="new_action",
        key="Y",
        category="utility",
        description="New action",
        required=False
    )
    print(f"\nAdded new override: {success}")
    
    # Show updated overrides
    print(f"\nUpdated overrides: {len(override_manager.list_overrides())}")
    for override in override_manager.list_overrides():
        print(f"  {override.name}: {override.key} ({override.category})")
    
    # Cleanup
    os.unlink(override_file)


def demo_discord_alerts():
    """Demo Discord alert functionality."""
    print("\n" + "=" * 60)
    print("DEMO: Discord Alert System")
    print("=" * 60)
    
    # Create test validation result with critical issues
    from modules.keybind_manager.keybind_validator import KeybindValidationResult
    
    validation_result = KeybindValidationResult(
        valid_keybinds=3,
        missing_keybinds=2,
        conflicting_keybinds=1,
        unknown_keybinds=0,
        total_keybinds=6,
        validation_errors=["Missing required keybind: attack", "Key conflict: F1 bound to attack, use"],
        recommendations=["Add keybind for 'attack': F1", "Resolve conflict for key 'F1' used by: attack, use"],
        critical_issues=["Missing required keybind: attack", "Key conflict: F1 bound to attack, use"]
    )
    
    # Initialize Discord alerts (without webhook for demo)
    alerts = DiscordKeybindAlerts()
    
    # Create alerts
    critical_alert = alerts.create_critical_alert(validation_result)
    warning_alert = alerts.create_warning_alert(validation_result)
    
    print(f"Critical Alert:")
    print(f"  Title: {critical_alert.title}")
    print(f"  Message: {critical_alert.message}")
    print(f"  Severity: {critical_alert.severity}")
    print(f"  Affected Keybinds: {critical_alert.keybinds_affected}")
    
    print(f"\nWarning Alert:")
    print(f"  Title: {warning_alert.title}")
    print(f"  Message: {warning_alert.message}")
    print(f"  Severity: {warning_alert.severity}")
    
    print(f"\nShould send alert: {alerts.should_send_alert(validation_result)}")
    print(f"Alert severity: {alerts.get_alert_severity(validation_result)}")
    
    # Simulate sending alert (without actual webhook)
    print(f"\nSimulating Discord alert send...")
    success = asyncio.run(alerts.send_keybind_alert(critical_alert))
    print(f"Alert sent: {success}")


def demo_reporting():
    """Demo comprehensive reporting functionality."""
    print("\n" + "=" * 60)
    print("DEMO: Comprehensive Reporting")
    print("=" * 60)
    
    # Create temporary directory with test files
    temp_dir = tempfile.mkdtemp()
    create_test_config_files(temp_dir)
    
    # Initialize all components
    parser = KeybindParser(swg_directory=temp_dir)
    validator = KeybindValidator()
    reporter = KeybindReporter()
    
    # Parse and validate
    parse_result = parser.parse_config_files()
    validation_result = validator.validate_keybinds(
        parse_result.keybinds, 
        parse_result.required_keybinds
    )
    
    # Generate report
    report = reporter.generate_report(
        parse_result.keybinds,
        validation_result,
        parse_result.swg_directory,
        parse_result.config_files_found
    )
    
    # Print report
    reporter.print_report(report, detailed=True)
    
    # Print category report
    reporter.print_category_report(parse_result.keybinds)
    
    # Generate fix script
    fix_script = reporter.generate_fix_script(report)
    print(f"\n🔧 FIX SCRIPT:")
    print("=" * 40)
    print(fix_script)
    
    # Save report to file
    report_file = os.path.join(temp_dir, "keybind_report.json")
    success = reporter.save_report(report, report_file)
    print(f"\nReport saved to {report_file}: {success}")
    
    # Save fix script to file
    script_file = os.path.join(temp_dir, "fix_keybinds.txt")
    success = reporter.save_fix_script(report, script_file)
    print(f"Fix script saved to {script_file}: {success}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


def demo_integration():
    """Demo full integration of all components."""
    print("\n" + "=" * 60)
    print("DEMO: Full Integration")
    print("=" * 60)
    
    # Create temporary directory with test files
    temp_dir = tempfile.mkdtemp()
    create_test_config_files(temp_dir)
    
    # Initialize all components
    parser = KeybindParser(swg_directory=temp_dir)
    validator = KeybindValidator()
    override_manager = KeybindOverrideManager(override_file=os.path.join(temp_dir, "overrides.json"))
    alerts = DiscordKeybindAlerts()
    reporter = KeybindReporter()
    
    # Parse config files
    parse_result = parser.parse_config_files()
    print(f"Parsed {parse_result.total_keybinds} keybinds from {len(parse_result.config_files_found)} files")
    
    # Apply manual overrides
    override_manager.add_override("missing_action", "Z", "utility", "Missing action", False)
    updated_keybinds = override_manager.apply_overrides_to_keybinds(parse_result.keybinds)
    print(f"Applied overrides, total keybinds: {len(updated_keybinds)}")
    
    # Validate keybinds
    validation_result = validator.validate_keybinds(updated_keybinds, parse_result.required_keybinds)
    print(f"Validation complete: {validation_result.valid_keybinds} valid, {validation_result.missing_keybinds} missing")
    
    # Check for critical issues and send alerts
    if alerts.should_send_alert(validation_result):
        severity = alerts.get_alert_severity(validation_result)
        if severity == "critical":
            alert = alerts.create_critical_alert(validation_result)
        else:
            alert = alerts.create_warning_alert(validation_result)
        
        print(f"Creating {severity} alert for {len(alert.keybinds_affected)} affected keybinds")
        success = asyncio.run(alerts.send_keybind_alert(alert))
        print(f"Alert sent: {success}")
    else:
        print("No alerts needed")
    
    # Generate comprehensive report
    report = reporter.generate_report(
        updated_keybinds,
        validation_result,
        parse_result.swg_directory,
        parse_result.config_files_found
    )
    
    print(f"\nFinal Report Summary:")
    print(f"  Total Keybinds: {report.summary['total_keybinds']}")
    print(f"  Valid: {report.summary['valid_keybinds']}")
    print(f"  Missing: {report.summary['missing_keybinds']}")
    print(f"  Conflicting: {report.summary['conflicting_keybinds']}")
    print(f"  Critical Issues: {len(report.critical_issues)}")
    print(f"  Recommendations: {len(report.recommendations)}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


def main():
    """Run all demos."""
    print("MS11 Batch 066 - Player Keybind Manager + Validation Reporter")
    print("=" * 80)
    
    try:
        # Run all demos
        demo_basic_parsing()
        demo_validation()
        demo_override_system()
        demo_discord_alerts()
        demo_reporting()
        demo_integration()
        
        print("\n" + "=" * 80)
        print("✅ All demos completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
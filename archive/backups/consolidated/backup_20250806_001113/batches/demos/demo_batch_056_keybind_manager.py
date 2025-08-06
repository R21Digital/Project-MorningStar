#!/usr/bin/env python3
"""
MS11 Batch 056 - Keybind Manager Demo

This demo showcases the keybind manager functionality including:
- SWG configuration file parsing
- Keybind detection and validation
- Manual override system
- Report generation
"""

import json
import os
import tempfile
from pathlib import Path

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from core.keybind_manager import (
    get_keybind_manager,
    validate_keybinds,
    save_keybind_report,
    KeybindStatus,
    KeybindCategory
)


def demo_basic_validation():
    """Demo basic keybind validation."""
    print("=" * 60)
    print("DEMO: Basic Keybind Validation")
    print("=" * 60)
    
    # Create keybind manager
    manager = get_keybind_manager()
    print(f"SWG Directory: {manager.swg_directory}")
    
    # Parse config files
    config_files = manager.parse_config_files()
    print(f"Config files found: {len(config_files)}")
    for file in config_files:
        print(f"  - {file}")
    
    # Validate keybinds
    report = manager.validate_keybinds()
    
    print(f"\nValidation Results:")
    print(f"  Total Keybinds: {report.total_keybinds}")
    print(f"  Valid: {report.valid_keybinds}")
    print(f"  Missing: {report.missing_keybinds}")
    print(f"  Conflicting: {report.conflicting_keybinds}")
    print(f"  Unknown: {report.unknown_keybinds}")
    
    # Show keybinds by category
    categories = {}
    for keybind in report.keybinds:
        category = keybind.category.value
        if category not in categories:
            categories[category] = []
        categories[category].append(keybind)
    
    print(f"\nKeybinds by Category:")
    for category, keybinds in categories.items():
        print(f"\n{category.upper()}:")
        for keybind in keybinds:
            status_icon = {
                KeybindStatus.VALID: "✓",
                KeybindStatus.MISSING: "✗",
                KeybindStatus.CONFLICT: "⚠",
                KeybindStatus.UNKNOWN: "?"
            }.get(keybind.status, "?")
            
            required_marker = " (REQUIRED)" if keybind.required else ""
            print(f"  {status_icon} {keybind.name}{required_marker}: {keybind.key or 'NOT SET'}")
            if keybind.suggestion:
                print(f"    Suggestion: {keybind.suggestion}")


def demo_manual_overrides():
    """Demo manual override functionality."""
    print("\n" + "=" * 60)
    print("DEMO: Manual Override System")
    print("=" * 60)
    
    # Create temporary override file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        overrides = {
            "attack": "F1",
            "use": "Enter",
            "inventory": "I",
            "map": "M",
            "chat": "Enter",
            "target": "Tab"
        }
        json.dump(overrides, f, indent=2)
        override_file = f.name
    
    print(f"Created override file: {override_file}")
    
    # Load overrides
    manager = get_keybind_manager()
    manager.load_manual_overrides(override_file)
    print("✓ Loaded manual overrides")
    
    # Validate with overrides
    report = manager.validate_keybinds()
    
    print(f"\nValidation with Overrides:")
    print(f"  Valid Keybinds: {report.valid_keybinds}")
    print(f"  Missing Keybinds: {report.missing_keybinds}")
    
    # Show overridden keybinds
    print(f"\nOverridden Keybinds:")
    for keybind in report.keybinds:
        if keybind.status == KeybindStatus.VALID and keybind.key:
            print(f"  ✓ {keybind.name}: {keybind.key}")
    
    # Cleanup
    os.unlink(override_file)
    print(f"\nCleaned up temporary file")


def demo_report_generation():
    """Demo report generation and saving."""
    print("\n" + "=" * 60)
    print("DEMO: Report Generation")
    print("=" * 60)
    
    # Generate report
    report = validate_keybinds()
    
    # Save report to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        report_file = f.name
    
    save_keybind_report(report_file)
    print(f"✓ Saved report to: {report_file}")
    
    # Load and display saved report
    with open(report_file, 'r') as f:
        saved_data = json.load(f)
    
    print(f"\nSaved Report Data:")
    print(f"  Total Keybinds: {saved_data['total_keybinds']}")
    print(f"  Valid Keybinds: {saved_data['valid_keybinds']}")
    print(f"  Missing Keybinds: {saved_data['missing_keybinds']}")
    print(f"  SWG Directory: {saved_data['swg_directory']}")
    print(f"  Config Files: {len(saved_data['config_files_found'])}")
    
    # Show suggestions
    if saved_data['suggestions']:
        print(f"\nSuggestions:")
        for i, suggestion in enumerate(saved_data['suggestions'], 1):
            print(f"  {i}. {suggestion}")
    
    # Cleanup
    os.unlink(report_file)
    print(f"\nCleaned up temporary file")


def demo_category_filtering():
    """Demo category-based filtering."""
    print("\n" + "=" * 60)
    print("DEMO: Category Filtering")
    print("=" * 60)
    
    report = validate_keybinds()
    
    # Group by category
    categories = {}
    for keybind in report.keybinds:
        category = keybind.category.value
        if category not in categories:
            categories[category] = []
        categories[category].append(keybind)
    
    # Show each category
    for category in KeybindCategory:
        category_keybinds = categories.get(category.value, [])
        if category_keybinds:
            print(f"\n{category.value.upper()} ({len(category_keybinds)} keybinds):")
            for keybind in category_keybinds:
                status_icon = {
                    KeybindStatus.VALID: "✓",
                    KeybindStatus.MISSING: "✗",
                    KeybindStatus.CONFLICT: "⚠",
                    KeybindStatus.UNKNOWN: "?"
                }.get(keybind.status, "?")
                
                required_marker = " (REQUIRED)" if keybind.required else ""
                print(f"  {status_icon} {keybind.name}{required_marker}: {keybind.key or 'NOT SET'}")


def demo_swg_directory_detection():
    """Demo SWG directory detection."""
    print("\n" + "=" * 60)
    print("DEMO: SWG Directory Detection")
    print("=" * 60)
    
    # Test with different directories
    test_directories = [
        None,  # Auto-detect
        "C:\\Program Files (x86)\\Sony\\Star Wars Galaxies",
        "D:\\Star Wars Galaxies",
        os.getcwd()  # Current directory
    ]
    
    for directory in test_directories:
        try:
            manager = get_keybind_manager(directory)
            print(f"Directory: {directory or 'Auto-detected'}")
            print(f"  Resolved to: {manager.swg_directory}")
            
            # Check if config files exist
            config_files = manager.parse_config_files()
            print(f"  Config files found: {len(config_files)}")
            
        except Exception as e:
            print(f"Directory: {directory}")
            print(f"  Error: {e}")
        
        print()


def demo_validation_scenarios():
    """Demo different validation scenarios."""
    print("\n" + "=" * 60)
    print("DEMO: Validation Scenarios")
    print("=" * 60)
    
    # Scenario 1: All keybinds valid
    print("Scenario 1: All Required Keybinds Valid")
    manager = get_keybind_manager()
    
    # Simulate all keybinds being set
    for name, keybind in manager.required_keybinds.items():
        keybind.key = f"Key_{name}"
        keybind.status = KeybindStatus.VALID
        manager.keybinds[name] = keybind
    
    report = manager.validate_keybinds()
    print(f"  Valid: {report.valid_keybinds}")
    print(f"  Missing: {report.missing_keybinds}")
    print(f"  Status: {'✅ All good!' if report.missing_keybinds == 0 else '❌ Issues found'}")
    
    # Scenario 2: Missing required keybinds
    print("\nScenario 2: Missing Required Keybinds")
    manager = get_keybind_manager()
    manager.keybinds.clear()  # Clear all keybinds
    
    report = manager.validate_keybinds()
    print(f"  Valid: {report.valid_keybinds}")
    print(f"  Missing: {report.missing_keybinds}")
    print(f"  Status: {'✅ All good!' if report.missing_keybinds == 0 else '❌ Issues found'}")
    
    # Show missing keybinds
    missing_keybinds = [k for k in report.keybinds if k.status == KeybindStatus.MISSING]
    if missing_keybinds:
        print(f"  Missing keybinds:")
        for keybind in missing_keybinds[:3]:  # Show first 3
            print(f"    - {keybind.name}: {keybind.suggestion}")
        if len(missing_keybinds) > 3:
            print(f"    ... and {len(missing_keybinds) - 3} more")


def main():
    """Run all demos."""
    print("MS11 Batch 056 - Keybind Manager Demo")
    print("=" * 60)
    
    try:
        demo_basic_validation()
        demo_manual_overrides()
        demo_report_generation()
        demo_category_filtering()
        demo_swg_directory_detection()
        demo_validation_scenarios()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("The keybind manager provides:")
        print("✅ SWG configuration file parsing")
        print("✅ Automatic keybind detection")
        print("✅ Validation with detailed reporting")
        print("✅ Manual override system")
        print("✅ Category-based filtering")
        print("✅ Report generation and saving")
        print("✅ Smart suggestions for missing keybinds")
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
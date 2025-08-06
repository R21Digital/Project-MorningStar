#!/usr/bin/env python3
"""
MS11 Batch 056 - Keybind Manager CLI

Command-line interface for the keybind manager system.
Provides validation, reporting, and manual override functionality.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.keybind_manager import (
    get_keybind_manager,
    validate_keybinds,
    save_keybind_report,
    KeybindStatus,
    KeybindCategory
)


def print_report(report, detailed: bool = False) -> None:
    """Print a formatted keybind report.
    
    Args:
        report: KeybindReport object
        detailed: Whether to show detailed information
    """
    print("\n" + "="*60)
    print("KEYBIND VALIDATION REPORT")
    print("="*60)
    
    # Summary statistics
    print(f"SWG Directory: {report.swg_directory}")
    print(f"Config Files Found: {len(report.config_files_found)}")
    if report.config_files_found:
        for file in report.config_files_found:
            print(f"  - {file}")
    
    print(f"\nSummary:")
    print(f"  Total Keybinds: {report.total_keybinds}")
    print(f"  Valid: {report.valid_keybinds} ✓")
    print(f"  Missing: {report.missing_keybinds} ✗")
    print(f"  Conflicting: {report.conflicting_keybinds} ⚠")
    print(f"  Unknown: {report.unknown_keybinds} ?")
    
    # Overall status
    if report.missing_keybinds == 0 and report.conflicting_keybinds == 0:
        print(f"\n✅ All required keybinds are properly configured!")
    elif report.missing_keybinds > 0:
        print(f"\n❌ {report.missing_keybinds} required keybinds are missing.")
    elif report.conflicting_keybinds > 0:
        print(f"\n⚠️  {report.conflicting_keybinds} keybinds have conflicts.")
    
    # Detailed breakdown by category
    if detailed:
        print(f"\nDetailed Breakdown:")
        categories = {}
        for keybind in report.keybinds:
            category = keybind.category.value
            if category not in categories:
                categories[category] = []
            categories[category].append(keybind)
        
        for category, keybinds in categories.items():
            print(f"\n{category.upper()}:")
            for keybind in keybinds:
                status_icon = {
                    KeybindStatus.VALID: "✓",
                    KeybindStatus.MISSING: "✗",
                    KeybindStatus.CONFLICT: "⚠",
                    KeybindStatus.UNKNOWN: "?"
                }.get(keybind.status, "?")
                
                print(f"  {status_icon} {keybind.name}: {keybind.key or 'NOT SET'}")
                print(f"    Description: {keybind.description}")
                if keybind.suggestion:
                    print(f"    Suggestion: {keybind.suggestion}")
    
    # Suggestions
    if report.suggestions:
        print(f"\nSuggestions:")
        for i, suggestion in enumerate(report.suggestions, 1):
            print(f"  {i}. {suggestion}")


def print_keybind_list(report, category: Optional[str] = None) -> None:
    """Print a list of keybinds, optionally filtered by category.
    
    Args:
        report: KeybindReport object
        category: Optional category filter
    """
    print(f"\nKeybind List" + (f" - {category.upper()}" if category else ""))
    print("-" * 40)
    
    for keybind in report.keybinds:
        if category and keybind.category.value != category:
            continue
            
        status_icon = {
            KeybindStatus.VALID: "✓",
            KeybindStatus.MISSING: "✗",
            KeybindStatus.CONFLICT: "⚠",
            KeybindStatus.UNKNOWN: "?"
        }.get(keybind.status, "?")
        
        required_marker = " (REQUIRED)" if keybind.required else ""
        print(f"{status_icon} {keybind.name}{required_marker}")
        print(f"  Key: {keybind.key or 'NOT SET'}")
        print(f"  Category: {keybind.category.value}")
        print(f"  Description: {keybind.description}")
        if keybind.suggestion:
            print(f"  Suggestion: {keybind.suggestion}")
        print()


def print_categories() -> None:
    """Print available keybind categories."""
    print("\nAvailable Categories:")
    for category in KeybindCategory:
        print(f"  - {category.value}")


def create_manual_override_template(filepath: str) -> None:
    """Create a manual override template file.
    
    Args:
        filepath: Path to create the template
    """
    template = {
        "manual_keybinds": {
            "attack": "F1",
            "use": "Enter",
            "inventory": "I",
            "map": "M",
            "chat": "Enter",
            "target": "Tab",
            "follow": "F",
            "stop": "Escape",
            "heal": "H",
            "loot": "L"
        },
        "description": "Manual keybind overrides. Edit these values to match your SWG keybinds.",
        "instructions": [
            "1. Edit the keybind values to match your SWG configuration",
            "2. Save the file",
            "3. Use --load-overrides to apply these settings"
        ]
    }
    
    with open(filepath, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"✓ Created manual override template: {filepath}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="MS11 Keybind Manager - Validate and manage SWG keybinds",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/keybind_manager.py --validate
  python cli/keybind_manager.py --validate --detailed
  python cli/keybind_manager.py --list
  python cli/keybind_manager.py --list --category combat
  python cli/keybind_manager.py --save-report keybinds.json
  python cli/keybind_manager.py --create-template overrides.json
  python cli/keybind_manager.py --load-overrides overrides.json
        """
    )
    
    parser.add_argument(
        '--swg-directory',
        help='Path to SWG installation directory'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate keybinds and show report'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed validation report'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all keybinds'
    )
    
    parser.add_argument(
        '--category',
        choices=[cat.value for cat in KeybindCategory],
        help='Filter keybinds by category'
    )
    
    parser.add_argument(
        '--categories',
        action='store_true',
        help='Show available categories'
    )
    
    parser.add_argument(
        '--save-report',
        metavar='FILE',
        help='Save validation report to JSON file'
    )
    
    parser.add_argument(
        '--create-template',
        metavar='FILE',
        help='Create manual override template file'
    )
    
    parser.add_argument(
        '--load-overrides',
        metavar='FILE',
        help='Load manual keybind overrides from file'
    )
    
    args = parser.parse_args()
    
    # Handle special commands first
    if args.categories:
        print_categories()
        return
    
    if args.create_template:
        create_manual_override_template(args.create_template)
        return
    
    # Get keybind manager
    try:
        manager = get_keybind_manager(args.swg_directory)
    except Exception as e:
        print(f"Error initializing keybind manager: {e}")
        return 1
    
    # Load overrides if specified
    if args.load_overrides:
        try:
            manager.load_manual_overrides(args.load_overrides)
            print(f"✓ Loaded overrides from {args.load_overrides}")
        except Exception as e:
            print(f"Error loading overrides: {e}")
            return 1
    
    # Get validation report
    try:
        report = manager.validate_keybinds()
    except Exception as e:
        print(f"Error validating keybinds: {e}")
        return 1
    
    # Handle commands
    if args.validate:
        print_report(report, args.detailed)
    
    if args.list:
        print_keybind_list(report, args.category)
    
    if args.save_report:
        try:
            manager.save_report(args.save_report)
            print(f"✓ Saved report to {args.save_report}")
        except Exception as e:
            print(f"Error saving report: {e}")
            return 1
    
    # If no specific command, show basic report
    if not any([args.validate, args.list, args.save_report, args.create_template, args.load_overrides]):
        print_report(report)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
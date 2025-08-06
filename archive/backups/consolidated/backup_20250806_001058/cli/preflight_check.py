#!/usr/bin/env python3
"""
CLI Interface for Batch 029 - Game State Requirements & Player Guidelines Enforcement

This module provides a command-line interface for the preflight check system,
allowing users to validate game state requirements and get resolution help.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import preflight check modules
try:
    from core.validation.preflight_check import (
        get_preflight_validator, run_preflight_check, generate_cli_report,
        save_preflight_report, is_system_ready, PreflightValidator,
        ValidationCheck, ValidationStatus, CheckType, PreflightReport
    )
    PREFLIGHT_CHECK_AVAILABLE = True
except ImportError as e:
    print(f"Error: Could not import preflight check modules: {e}")
    PREFLIGHT_CHECK_AVAILABLE = False


def display_system_status():
    """Display system readiness status."""
    if not PREFLIGHT_CHECK_AVAILABLE:
        print("Error: Preflight check not available")
        return
    
    print("=== System Status ===")
    
    # Check if system is ready
    ready = is_system_ready()
    status_icon = "✓" if ready else "✗"
    print(f"{status_icon} System Ready: {'Yes' if ready else 'No'}")
    
    if not ready:
        print("Run 'validate' command to see detailed issues")
    print()


def run_validation():
    """Run complete preflight validation."""
    if not PREFLIGHT_CHECK_AVAILABLE:
        print("Error: Preflight check not available")
        return
    
    print("=== Running Preflight Validation ===")
    print("Checking game state requirements...")
    print()
    
    # Run validation
    report = run_preflight_check()
    
    # Display results
    status_icon = {
        ValidationStatus.PASS: "✓",
        ValidationStatus.FAIL: "✗",
        ValidationStatus.WARNING: "⚠"
    }.get(report.overall_status, "?")
    
    print(f"{status_icon} Overall Status: {report.overall_status.value.upper()}")
    print(f"Checks: {report.passed_checks}/{report.total_checks} passed")
    print()
    
    # Show check results
    for check in report.checks:
        check_icon = {
            ValidationStatus.PASS: "✓",
            ValidationStatus.FAIL: "✗",
            ValidationStatus.WARNING: "⚠",
            ValidationStatus.SKIP: "○"
        }.get(check.status, "?")
        
        print(f"{check_icon} {check.name}: {check.message}")
        if check.fix_suggestion:
            print(f"   💡 {check.fix_suggestion}")
    
    print()
    
    # Show critical failures
    if report.critical_failures:
        print("CRITICAL FAILURES:")
        for failure in report.critical_failures:
            print(f"  ✗ {failure}")
        print()
    
    # Show recommendations
    if report.recommendations:
        print("RECOMMENDATIONS:")
        for rec in report.recommendations:
            print(f"  💡 {rec}")
        print()


def show_resolution_help():
    """Show resolution help and tips."""
    print("=== Resolution Help ===")
    print()
    print("To ensure optimal bot operation, please verify:")
    print()
    print("1. Window Mode")
    print("   ✓ Set game to windowed mode")
    print("   ✓ Not fullscreen or borderless windowed")
    print()
    print("2. Resolution")
    print("   ✓ Use 1920x1080 (recommended)")
    print("   ✓ Or 1600x900 (minimum)")
    print("   ✓ Avoid resolutions below 1024x768")
    print()
    print("3. UI Elements")
    print("   ✓ Minimap must be visible")
    print("   ✓ Quest journal must be accessible")
    print("   ✓ Chat window should be visible")
    print("   ✓ Inventory should be accessible")
    print()
    print("4. UI Scale")
    print("   ✓ Set UI scale to 1.0 (recommended)")
    print("   ✓ Acceptable range: 0.8 to 1.2")
    print("   ✓ Avoid extreme scaling")
    print()
    print("5. Performance")
    print("   ✓ Maintain 30+ FPS")
    print("   ✓ Keep memory usage under 90%")
    print("   ✓ Close unnecessary applications")
    print()
    print("6. Game State")
    print("   ✓ Game must be fully loaded")
    print("   ✓ Character must be logged in")
    print("   ✓ Not in loading screens or cutscenes")
    print()


def show_supported_resolutions():
    """Show list of supported resolutions."""
    if not PREFLIGHT_CHECK_AVAILABLE:
        print("Error: Preflight check not available")
        return
    
    validator = get_preflight_validator()
    
    print("=== Supported Resolutions ===")
    print()
    print("The following resolutions are supported:")
    print()
    
    for i, resolution in enumerate(validator.supported_resolutions, 1):
        width, height = resolution
        recommended = " (Recommended)" if resolution == (1920, 1080) else ""
        print(f"{i}. {width}x{height}{recommended}")
    
    print()
    print("Note: Higher resolutions provide better OCR accuracy")
    print("but may impact performance on slower systems.")


def show_required_ui_elements():
    """Show list of required UI elements."""
    if not PREFLIGHT_CHECK_AVAILABLE:
        print("Error: Preflight check not available")
        return
    
    validator = get_preflight_validator()
    
    print("=== Required UI Elements ===")
    print()
    
    for element_name, element_info in validator.required_ui_elements.items():
        required_marker = "✓" if element_info["required"] else "○"
        print(f"{required_marker} {element_name}")
        print(f"   Description: {element_info['description']}")
        print(f"   Keywords: {', '.join(element_info['keywords'])}")
        print(f"   Scan regions: {len(element_info['regions'])}")
        print()


def save_validation_report():
    """Save validation report to file."""
    if not PREFLIGHT_CHECK_AVAILABLE:
        print("Error: Preflight check not available")
        return
    
    print("=== Saving Validation Report ===")
    
    try:
        save_preflight_report("data/preflight_report.json")
        print("✅ Report saved to data/preflight_report.json")
        
        # Check file size
        report_path = Path("data/preflight_report.json")
        if report_path.exists():
            print(f"   File size: {report_path.stat().st_size} bytes")
            
            # Show sample data
            import json
            with open(report_path, 'r') as f:
                data = json.load(f)
            
            print(f"   Overall status: {data.get('overall_status', 'unknown')}")
            print(f"   Total checks: {data.get('summary', {}).get('total_checks', 0)}")
            print(f"   Critical failures: {len(data.get('critical_failures', []))}")
            
    except Exception as e:
        print(f"❌ Failed to save report: {e}")


def show_validation_types():
    """Show available validation check types."""
    print("=== Validation Check Types ===")
    print()
    
    check_types = [
        CheckType.WINDOW_MODE,
        CheckType.RESOLUTION,
        CheckType.UI_VISIBILITY,
        CheckType.UI_SCALE,
        CheckType.GAME_STATE,
        CheckType.PERFORMANCE
    ]
    
    for check_type in check_types:
        print(f"• {check_type.value.replace('_', ' ').title()}")
    
    print()
    print("Validation Status Types:")
    print("-" * 30)
    
    status_types = [
        ValidationStatus.PASS,
        ValidationStatus.FAIL,
        ValidationStatus.WARNING,
        ValidationStatus.SKIP
    ]
    
    for status in status_types:
        icon = {
            ValidationStatus.PASS: "✓",
            ValidationStatus.FAIL: "✗",
            ValidationStatus.WARNING: "⚠",
            ValidationStatus.SKIP: "○"
        }.get(status, "?")
        print(f"• {icon} {status.value.title()}")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="MS11 Preflight Check & Game State Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                    # Show system readiness
  %(prog)s validate                  # Run complete validation
  %(prog)s help                      # Show resolution help
  %(prog)s resolutions               # Show supported resolutions
  %(prog)s ui-elements               # Show required UI elements
  %(prog)s save                      # Save validation report
  %(prog)s types                     # Show validation types
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show system readiness status')
    
    # Validate command
    subparsers.add_parser('validate', help='Run complete preflight validation')
    
    # Help command
    subparsers.add_parser('help', help='Show resolution help and tips')
    
    # Resolutions command
    subparsers.add_parser('resolutions', help='Show supported resolutions')
    
    # UI elements command
    subparsers.add_parser('ui-elements', help='Show required UI elements')
    
    # Save command
    subparsers.add_parser('save', help='Save validation report to file')
    
    # Types command
    subparsers.add_parser('types', help='Show validation check types')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == 'status':
        display_system_status()
    elif args.command == 'validate':
        run_validation()
    elif args.command == 'help':
        show_resolution_help()
    elif args.command == 'resolutions':
        show_supported_resolutions()
    elif args.command == 'ui-elements':
        show_required_ui_elements()
    elif args.command == 'save':
        save_validation_report()
    elif args.command == 'types':
        show_validation_types()


if __name__ == "__main__":
    main() 
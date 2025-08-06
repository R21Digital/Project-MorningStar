#!/usr/bin/env python3
"""
CLI Interface for Batch 028 - User Keybinding Scanner & Validation Assistant

This module provides a command-line interface for the keybinding scanner system,
allowing users to scan, validate, and configure SWG keybindings.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import keybinding scanner modules
try:
    from core.keybinding_scanner import (
        get_keybinding_scanner, scan_keybindings, validate_keybindings,
        generate_report, setup_mode, KeybindingScanner, KeyBinding,
        BindingType, BindingStatus, KeybindingValidation
    )
    KEYBINDING_SCANNER_AVAILABLE = True
except ImportError as e:
    print(f"Error: Could not import keybinding scanner modules: {e}")
    KEYBINDING_SCANNER_AVAILABLE = False


def display_scanner_status():
    """Display keybinding scanner status and configuration."""
    if not KEYBINDING_SCANNER_AVAILABLE:
        print("Error: Keybinding scanner not available")
        return
    
    scanner = get_keybinding_scanner()
    
    print("=== Keybinding Scanner Status ===")
    print(f"SWG Path: {scanner.swg_path or 'Not found'}")
    print(f"User.cfg Path: {scanner.user_cfg_path or 'Not found'}")
    print(f"Inputmap.xml Path: {scanner.inputmap_path or 'Not found'}")
    print(f"OCR Available: {'Yes' if hasattr(scanner, 'OCR_AVAILABLE') and scanner.OCR_AVAILABLE else 'No'}")
    print()


def display_essential_bindings():
    """Display essential keybindings for bot operation."""
    if not KEYBINDING_SCANNER_AVAILABLE:
        print("Error: Keybinding scanner not available")
        return
    
    scanner = get_keybinding_scanner()
    
    print("=== Essential Keybindings ===")
    print("The following keybindings are required for bot operation:")
    print()
    
    for binding_name, binding_info in scanner.essential_bindings.items():
        required_marker = "✓" if binding_info["required"] else "○"
        print(f"{required_marker} {binding_name}")
        print(f"   Description: {binding_info['description']}")
        print(f"   Type: {binding_info['type'].value}")
        print(f"   Alternatives: {', '.join(binding_info['alternatives'])}")
        print()


def scan_and_display_bindings():
    """Scan and display all detected keybindings."""
    if not KEYBINDING_SCANNER_AVAILABLE:
        print("Error: Keybinding scanner not available")
        return
    
    scanner = get_keybinding_scanner()
    
    print("=== Scanning Keybindings ===")
    
    # Scan from all sources
    bindings = scanner.scan_all_sources()
    
    if bindings:
        print(f"Found {len(bindings)} keybindings:")
        print()
        
        for binding_name, binding in bindings.items():
            status_icon = "✓" if binding.status == BindingStatus.VALID else "⚠"
            print(f"{status_icon} {binding_name}: {binding.key}")
            if binding.modifier:
                print(f"   Modifier: {binding.modifier}")
            if binding.description:
                print(f"   Description: {binding.description}")
            print()
    else:
        print("No keybindings found in configuration files")
        print("This is normal if SWG is not installed or configuration files are not accessible")
        print()


def validate_and_report():
    """Validate keybindings and display comprehensive report."""
    if not KEYBINDING_SCANNER_AVAILABLE:
        print("Error: Keybinding scanner not available")
        return
    
    scanner = get_keybinding_scanner()
    
    print("=== Keybinding Validation Report ===")
    
    # Generate comprehensive report
    report = scanner.generate_binding_report()
    print(report)
    
    # Additional validation details
    validation = scanner.validate_essential_bindings()
    
    if validation.missing_bindings > 0:
        print(f"\n⚠️  WARNING: {validation.missing_bindings} essential bindings are missing!")
        print("The bot may not function properly without these bindings.")
        print("Consider running setup mode to configure missing bindings.")
    else:
        print(f"\n✅ All essential bindings are properly configured!")
    
    if validation.conflicting_bindings > 0:
        print(f"\n⚠️  WARNING: {validation.conflicting_bindings} key conflicts detected!")
        print("Some keys are bound to multiple actions, which may cause issues.")
    
    print()


def run_setup_mode():
    """Run interactive setup mode for keybinding configuration."""
    if not KEYBINDING_SCANNER_AVAILABLE:
        print("Error: Keybinding scanner not available")
        return
    
    print("=== Interactive Setup Mode ===")
    print("This mode will help you configure essential keybindings.")
    print("You will be prompted to press keys for each essential binding.")
    print("Type 'skip' to skip a binding, or 'quit' to exit.\n")
    
    try:
        setup_bindings = setup_mode()
        
        if setup_bindings:
            print(f"\n✅ Setup completed! Configured {len(setup_bindings)} bindings:")
            for binding_name, key in setup_bindings.items():
                print(f"   {binding_name} -> {key}")
            
            # Save configuration
            scanner = get_keybinding_scanner()
            scanner.save_binding_config()
            print("\nConfiguration saved to data/keybindings.json")
        else:
            print("\nSetup was cancelled or no bindings were configured.")
            
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
    except Exception as e:
        print(f"\nError during setup: {e}")


def test_ocr_fallback():
    """Test OCR fallback for keybinding detection."""
    if not KEYBINDING_SCANNER_AVAILABLE:
        print("Error: Keybinding scanner not available")
        return
    
    scanner = get_keybinding_scanner()
    
    print("=== OCR Fallback Test ===")
    print("Attempting to detect keybindings via OCR...")
    print("(This works best when SWG keybinding screen is visible)")
    print()
    
    try:
        ocr_bindings = scanner.scan_keybinding_screen_ocr()
        
        if ocr_bindings:
            print(f"Found {len(ocr_bindings)} keybindings via OCR:")
            for binding_name, binding in ocr_bindings.items():
                print(f"   {binding_name}: {binding.key}")
        else:
            print("No keybindings detected via OCR")
            print("This is normal if:")
            print("- SWG is not running")
            print("- Keybinding screen is not visible")
            print("- OCR is not available")
            
    except Exception as e:
        print(f"OCR test failed: {e}")


def analyze_config_files():
    """Analyze SWG configuration files if they exist."""
    if not KEYBINDING_SCANNER_AVAILABLE:
        print("Error: Keybinding scanner not available")
        return
    
    scanner = get_keybinding_scanner()
    
    print("=== Configuration File Analysis ===")
    
    # Analyze user.cfg
    if scanner.user_cfg_path and scanner.user_cfg_path.exists():
        print(f"User.cfg found: {scanner.user_cfg_path}")
        try:
            with open(scanner.user_cfg_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                keybinding_lines = [line for line in lines if 'KeyBinding' in line]
                print(f"   KeyBinding entries: {len(keybinding_lines)}")
                
                if keybinding_lines:
                    print("   Sample entries:")
                    for line in keybinding_lines[:3]:
                        print(f"     {line.strip()}")
        except Exception as e:
            print(f"   Error reading user.cfg: {e}")
    else:
        print("User.cfg not found")
    
    # Analyze inputmap.xml
    if scanner.inputmap_path and scanner.inputmap_path.exists():
        print(f"\nInputmap.xml found: {scanner.inputmap_path}")
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(scanner.inputmap_path)
            root = tree.getroot()
            binding_elements = root.findall(".//binding")
            print(f"   Binding elements: {len(binding_elements)}")
            
            if binding_elements:
                print("   Sample entries:")
                for elem in binding_elements[:3]:
                    action = elem.get("action", "unknown")
                    key = elem.get("key", "unknown")
                    print(f"     Action: {action}, Key: {key}")
        except Exception as e:
            print(f"   Error reading inputmap.xml: {e}")
    else:
        print("Inputmap.xml not found")
    
    print()


def save_configuration():
    """Save current keybinding configuration to file."""
    if not KEYBINDING_SCANNER_AVAILABLE:
        print("Error: Keybinding scanner not available")
        return
    
    scanner = get_keybinding_scanner()
    
    print("=== Saving Configuration ===")
    
    try:
        scanner.save_binding_config()
        print("✅ Configuration saved to data/keybindings.json")
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="SWG Keybinding Scanner & Validation Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                    # Show scanner status
  %(prog)s essential                 # Show essential bindings
  %(prog)s scan                      # Scan and display bindings
  %(prog)s validate                  # Validate and report
  %(prog)s setup                     # Run interactive setup
  %(prog)s ocr                       # Test OCR fallback
  %(prog)s analyze                   # Analyze config files
  %(prog)s save                      # Save configuration
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show scanner status and configuration')
    
    # Essential command
    subparsers.add_parser('essential', help='Show essential keybindings')
    
    # Scan command
    subparsers.add_parser('scan', help='Scan and display keybindings')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate keybindings and generate report')
    
    # Setup command
    subparsers.add_parser('setup', help='Run interactive setup mode')
    
    # OCR command
    subparsers.add_parser('ocr', help='Test OCR fallback for keybinding detection')
    
    # Analyze command
    subparsers.add_parser('analyze', help='Analyze SWG configuration files')
    
    # Save command
    subparsers.add_parser('save', help='Save current configuration to file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == 'status':
        display_scanner_status()
    elif args.command == 'essential':
        display_essential_bindings()
    elif args.command == 'scan':
        scan_and_display_bindings()
    elif args.command == 'validate':
        validate_and_report()
    elif args.command == 'setup':
        run_setup_mode()
    elif args.command == 'ocr':
        test_ocr_fallback()
    elif args.command == 'analyze':
        analyze_config_files()
    elif args.command == 'save':
        save_configuration()


if __name__ == "__main__":
    main() 
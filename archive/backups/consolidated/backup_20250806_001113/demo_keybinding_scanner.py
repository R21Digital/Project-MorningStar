#!/usr/bin/env python3
"""
Demonstration script for Batch 028 - User Keybinding Scanner & Validation Assistant

This script demonstrates the keybinding scanner functionality including:
- Scanning SWG configuration files (user.cfg, inputmap.xml)
- Validating essential keybindings for bot operation
- OCR fallback for keybinding screen detection
- Interactive setup mode for binding assistance
- Comprehensive reporting and validation
"""

import time
from pathlib import Path

# Import the keybinding scanner modules
try:
    from core.keybinding_scanner import (
        get_keybinding_scanner, scan_keybindings, validate_keybindings,
        generate_report, setup_mode, KeybindingScanner, KeyBinding,
        BindingType, BindingStatus, KeybindingValidation
    )
    KEYBINDING_SCANNER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import keybinding scanner modules: {e}")
    KEYBINDING_SCANNER_AVAILABLE = False


def demonstrate_keybinding_scanner():
    """Demonstrate the keybinding scanner functionality."""
    if not KEYBINDING_SCANNER_AVAILABLE:
        print("Keybinding scanner modules not available. Skipping demonstration.")
        return
    
    print("=== Keybinding Scanner Demonstration ===\n")
    
    # Get the keybinding scanner instance
    scanner = get_keybinding_scanner()
    
    print("1. Keybinding Scanner Initialization")
    print("-" * 40)
    
    # Show scanner status
    print(f"SWG Path: {scanner.swg_path or 'Not found'}")
    print(f"User.cfg Path: {scanner.user_cfg_path or 'Not found'}")
    print(f"Inputmap.xml Path: {scanner.inputmap_path or 'Not found'}")
    print(f"OCR Available: {scanner.OCR_AVAILABLE if hasattr(scanner, 'OCR_AVAILABLE') else 'Unknown'}")
    print()
    
    # Show essential bindings
    print("2. Essential Keybindings")
    print("-" * 40)
    
    for binding_name, binding_info in scanner.essential_bindings.items():
        required_marker = "✓" if binding_info["required"] else "○"
        print(f"{required_marker} {binding_name}: {binding_info['description']}")
        print(f"   Type: {binding_info['type'].value}")
        print(f"   Alternatives: {', '.join(binding_info['alternatives'])}")
        print()
    
    # Scan keybindings
    print("3. Keybinding Scanning")
    print("-" * 40)
    
    # Scan from configuration files
    user_cfg_bindings = scanner.scan_user_cfg()
    print(f"User.cfg bindings found: {len(user_cfg_bindings)}")
    
    inputmap_bindings = scanner.scan_inputmap_xml()
    print(f"Inputmap.xml bindings found: {len(inputmap_bindings)}")
    
    # Scan all sources
    all_bindings = scanner.scan_all_sources()
    print(f"Total bindings found: {len(all_bindings)}")
    
    # Show detected bindings
    if all_bindings:
        print("\nDetected bindings:")
        for binding_name, binding in all_bindings.items():
            status_icon = "✓" if binding.status == BindingStatus.VALID else "⚠"
            print(f"  {status_icon} {binding_name}: {binding.key}")
            if binding.modifier:
                print(f"    Modifier: {binding.modifier}")
            if binding.description:
                print(f"    Description: {binding.description}")
    else:
        print("No bindings found in configuration files")
    
    print()
    
    # Validate keybindings
    print("4. Keybinding Validation")
    print("-" * 40)
    
    validation = scanner.validate_essential_bindings()
    
    print(f"Total bindings: {validation.total_bindings}")
    print(f"Valid bindings: {validation.valid_bindings}")
    print(f"Missing bindings: {validation.missing_bindings}")
    print(f"Conflicting bindings: {validation.conflicting_bindings}")
    print()
    
    if validation.warnings:
        print("Warnings:")
        for warning in validation.warnings:
            print(f"  ⚠ {warning}")
        print()
    
    if validation.recommendations:
        print("Recommendations:")
        for rec in validation.recommendations:
            print(f"  💡 {rec}")
        print()
    
    # Test OCR fallback
    print("5. OCR Fallback Testing")
    print("-" * 40)
    
    try:
        ocr_bindings = scanner.scan_keybinding_screen_ocr()
        print(f"OCR bindings found: {len(ocr_bindings)}")
        
        if ocr_bindings:
            print("OCR-detected bindings:")
            for binding_name, binding in ocr_bindings.items():
                print(f"  {binding_name}: {binding.key}")
        else:
            print("No bindings detected via OCR (normal if not on keybinding screen)")
        
    except Exception as e:
        print(f"OCR testing failed: {e}")
    
    print()
    
    # Generate comprehensive report
    print("6. Comprehensive Report")
    print("-" * 40)
    
    report = scanner.generate_binding_report()
    print(report)
    
    print("\n7. Configuration File Analysis")
    print("-" * 40)
    
    # Analyze configuration files if they exist
    if scanner.user_cfg_path and scanner.user_cfg_path.exists():
        print(f"User.cfg file found: {scanner.user_cfg_path}")
        try:
            with open(scanner.user_cfg_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                keybinding_lines = [line for line in lines if 'KeyBinding' in line]
                print(f"KeyBinding lines found: {len(keybinding_lines)}")
                
                if keybinding_lines:
                    print("Sample KeyBinding entries:")
                    for line in keybinding_lines[:5]:  # Show first 5
                        print(f"  {line.strip()}")
        except Exception as e:
            print(f"Error reading user.cfg: {e}")
    else:
        print("User.cfg file not found")
    
    if scanner.inputmap_path and scanner.inputmap_path.exists():
        print(f"\nInputmap.xml file found: {scanner.inputmap_path}")
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(scanner.inputmap_path)
            root = tree.getroot()
            binding_elements = root.findall(".//binding")
            print(f"Binding elements found: {len(binding_elements)}")
            
            if binding_elements:
                print("Sample binding entries:")
                for elem in binding_elements[:5]:  # Show first 5
                    action = elem.get("action", "unknown")
                    key = elem.get("key", "unknown")
                    print(f"  Action: {action}, Key: {key}")
        except Exception as e:
            print(f"Error reading inputmap.xml: {e}")
    else:
        print("Inputmap.xml file not found")
    
    print("\n8. Advanced Features")
    print("-" * 40)
    
    # Test binding classification
    test_actions = ["attack", "mount", "use", "interact", "forward", "inventory", "chat"]
    print("Binding classification test:")
    for action in test_actions:
        binding_type = scanner._classify_binding(action)
        print(f"  {action} -> {binding_type.value}")
    
    # Test SWG path detection
    print(f"\nSWG installation detection:")
    print(f"  Detected path: {scanner.swg_path or 'Not found'}")
    
    # Test configuration file detection
    print(f"\nConfiguration file detection:")
    print(f"  User.cfg: {'Found' if scanner.user_cfg_path else 'Not found'}")
    print(f"  Inputmap.xml: {'Found' if scanner.inputmap_path else 'Not found'}")
    
    print("\n=== Demonstration Complete ===")


def demonstrate_setup_mode():
    """Demonstrate the interactive setup mode."""
    print("\n=== Setup Mode Demonstration ===\n")
    
    if not KEYBINDING_SCANNER_AVAILABLE:
        print("Keybinding scanner not available for setup mode.")
        return
    
    print("This would normally run an interactive setup mode.")
    print("For demonstration purposes, we'll show what it would do:")
    
    scanner = get_keybinding_scanner()
    
    print("\nEssential bindings that would be configured:")
    for binding_name, binding_info in scanner.essential_bindings.items():
        if binding_info["required"]:
            print(f"  {binding_name}: {binding_info['description']}")
    
    print("\nIn real setup mode, you would:")
    print("1. Be prompted to press each key")
    print("2. Have your keypresses captured")
    print("3. See confirmation of each binding")
    print("4. Get a summary of all configured bindings")
    
    # Simulate setup mode (without actual key capture)
    print("\nSimulated setup mode:")
    setup_bindings = {
        "attack": "f1",
        "mount": "m",
        "use": "u",
        "interact": "i",
        "forward": "w",
        "backward": "s",
        "left": "a",
        "right": "d"
    }
    
    for binding_name, key in setup_bindings.items():
        print(f"  ✓ {binding_name} -> {key}")
    
    print("\nSetup mode would save these bindings for bot use.")


def demonstrate_integration():
    """Demonstrate integration with existing systems."""
    print("\n=== Integration with Existing Systems ===\n")
    
    # Check if OCR system is available
    try:
        from core.ocr import get_ocr_engine
        ocr_engine = get_ocr_engine()
        print("✓ OCR engine integration available")
        print(f"  OCR available: {ocr_engine.available}")
    except ImportError:
        print("✗ OCR engine integration not available")
    
    # Check if screenshot system is available
    try:
        from core.screenshot import capture_screen
        print("✓ Screenshot system integration available")
    except ImportError:
        print("✗ Screenshot system integration not available")
    
    # Show keybinding scanner integration
    scanner = get_keybinding_scanner()
    print(f"✓ Keybinding scanner available")
    print(f"  Essential bindings: {len(scanner.essential_bindings)}")
    print(f"  SWG path found: {'Yes' if scanner.swg_path else 'No'}")
    
    # Test file access capabilities
    print(f"\nFile access capabilities:")
    print(f"  User.cfg accessible: {'Yes' if scanner.user_cfg_path and scanner.user_cfg_path.exists() else 'No'}")
    print(f"  Inputmap.xml accessible: {'Yes' if scanner.inputmap_path and scanner.inputmap_path.exists() else 'No'}")
    
    # Test validation capabilities
    validation = scanner.validate_essential_bindings()
    print(f"\nValidation capabilities:")
    print(f"  Total bindings: {validation.total_bindings}")
    print(f"  Missing essential: {len(validation.essential_missing)}")
    print(f"  Conflicts detected: {validation.conflicting_bindings}")


def demonstrate_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n=== Error Handling Demonstration ===\n")
    
    if not KEYBINDING_SCANNER_AVAILABLE:
        print("Keybinding scanner not available for error handling test.")
        return
    
    # Test with non-existent paths
    print("Testing with non-existent SWG path:")
    test_scanner = KeybindingScanner("C:/NonExistent/SWG")
    
    print(f"  SWG Path: {test_scanner.swg_path}")
    print(f"  User.cfg Path: {test_scanner.user_cfg_path}")
    print(f"  Inputmap Path: {test_scanner.inputmap_path}")
    
    # Test scanning with missing files
    print("\nTesting scanning with missing files:")
    user_cfg_bindings = test_scanner.scan_user_cfg()
    inputmap_bindings = test_scanner.scan_inputmap_xml()
    
    print(f"  User.cfg bindings: {len(user_cfg_bindings)}")
    print(f"  Inputmap bindings: {len(inputmap_bindings)}")
    
    # Test validation with no bindings
    print("\nTesting validation with no bindings:")
    validation = test_scanner.validate_essential_bindings()
    
    print(f"  Total bindings: {validation.total_bindings}")
    print(f"  Missing essential: {len(validation.essential_missing)}")
    print(f"  Warnings: {len(validation.warnings)}")
    
    if validation.warnings:
        print("  Sample warnings:")
        for warning in validation.warnings[:3]:
            print(f"    - {warning}")


if __name__ == "__main__":
    print("Batch 028 - User Keybinding Scanner & Validation Assistant")
    print("=" * 65)
    
    # Run demonstrations
    demonstrate_keybinding_scanner()
    demonstrate_setup_mode()
    demonstrate_integration()
    demonstrate_error_handling()
    
    print("\nDemonstration completed successfully!") 
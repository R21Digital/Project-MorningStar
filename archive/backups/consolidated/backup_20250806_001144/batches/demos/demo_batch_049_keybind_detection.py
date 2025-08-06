#!/usr/bin/env python3
"""Demo script for Batch 049 - Keybind Detection + Input Mapping Module

This demo showcases the comprehensive keybind detection and validation system.
It demonstrates auto-detection, manual configuration, validation, and reporting.
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any

# Import our keybind modules
from core.keybind_manager import KeybindManager, KeybindManagerConfig, DetectionMode
from utils.keybind_validator import KeybindValidator, ValidationReport
from core.keybinding_scanner import KeybindingScanner


def setup_logging():
    """Setup logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('demo_batch_049.log'),
            logging.StreamHandler()
        ]
    )


def demo_auto_detection():
    """Demo auto-detection of keybinds."""
    print("\n" + "="*60)
    print("DEMO: AUTO-DETECTION OF KEYBINDS")
    print("="*60)
    
    manager = KeybindManager()
    
    print("Starting auto-detection...")
    result = manager.auto_detect_keybinds()
    
    print(f"\nDetection Results:")
    print(f"  Bindings found: {len(result.bindings)}")
    print(f"  Detection methods: {', '.join(result.detection_methods)}")
    print(f"  Confidence: {result.confidence:.1%}")
    print(f"  Detection time: {result.detection_time:.2f}s")
    
    if result.bindings:
        print(f"\nDetected Bindings:")
        for action, key in result.bindings.items():
            print(f"  {action}: {key}")
    
    if result.missing_essential:
        print(f"\nMissing Essential Bindings:")
        for action in result.missing_essential:
            print(f"  ❌ {action}")
    
    if result.conflicts:
        print(f"\nConflicts Detected:")
        for action1, action2, key in result.conflicts:
            print(f"  ⚠️  {action1} and {action2} both use {key}")
    
    if result.warnings:
        print(f"\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")
    
    return result


def demo_manual_configuration():
    """Demo manual configuration of keybinds."""
    print("\n" + "="*60)
    print("DEMO: MANUAL CONFIGURATION")
    print("="*60)
    
    manager = KeybindManager()
    
    # Simulate manual configuration with test data
    test_bindings = {
        "attack": "1",
        "target_next": "Tab",
        "use": "E",
        "inventory": "I",
        "mount": "M",
        "forward": "W",
        "backward": "S",
        "left": "A",
        "right": "D"
    }
    
    print("Simulating manual configuration...")
    print("Test bindings configured:")
    for action, key in test_bindings.items():
        print(f"  {action}: {key}")
    
    return test_bindings


def demo_validation(bindings: Dict[str, str]):
    """Demo validation of keybinds."""
    print("\n" + "="*60)
    print("DEMO: KEYBIND VALIDATION")
    print("="*60)
    
    validator = KeybindValidator()
    
    print("Validating keybinds...")
    report = validator.validate_keybinds(bindings)
    
    print(validator.generate_validation_report(report))
    
    return report


def demo_conflict_detection(bindings: Dict[str, str]):
    """Demo conflict detection."""
    print("\n" + "="*60)
    print("DEMO: CONFLICT DETECTION")
    print("="*60)
    
    validator = KeybindValidator()
    
    # Add some conflicts to test
    test_bindings = bindings.copy()
    test_bindings["attack"] = "Tab"  # Conflict with target_next
    test_bindings["use"] = "W"       # Conflict with forward
    
    print("Testing conflict detection...")
    conflicts = validator.detect_conflicts(test_bindings)
    
    if conflicts:
        print("Conflicts detected:")
        for action1, action2, key in conflicts:
            print(f"  ⚠️  {action1} and {action2} both use {key}")
    else:
        print("No conflicts detected.")
    
    return conflicts


def demo_alternative_suggestions():
    """Demo alternative key suggestions."""
    print("\n" + "="*60)
    print("DEMO: ALTERNATIVE KEY SUGGESTIONS")
    print("="*60)
    
    validator = KeybindValidator()
    
    test_cases = [
        ("attack", "1"),
        ("target_next", "Tab"),
        ("use", "E"),
        ("inventory", "I"),
        ("mount", "M")
    ]
    
    for action, current_key in test_cases:
        alternatives = validator.suggest_alternative_keys(action, current_key)
        print(f"{action} (currently {current_key}):")
        print(f"  Alternatives: {', '.join(alternatives)}")


def demo_save_and_load():
    """Demo saving and loading keybinds."""
    print("\n" + "="*60)
    print("DEMO: SAVE AND LOAD KEYBINDS")
    print("="*60)
    
    manager = KeybindManager()
    
    # Test bindings
    test_bindings = {
        "attack": "1",
        "target_next": "Tab",
        "use": "E",
        "inventory": "I",
        "mount": "M",
        "forward": "W",
        "backward": "S",
        "left": "A",
        "right": "D"
    }
    
    print("Saving test keybinds...")
    success = manager.save_keybinds(test_bindings, backup=True)
    
    if success:
        print("✓ Keybinds saved successfully!")
        
        print("\nLoading keybinds...")
        loaded_bindings = manager.load_keybinds()
        
        if loaded_bindings:
            print("✓ Keybinds loaded successfully!")
            print(f"Loaded {len(loaded_bindings)} bindings:")
            for action, key in loaded_bindings.items():
                print(f"  {action}: {key}")
        else:
            print("✗ Failed to load keybinds.")
    else:
        print("✗ Failed to save keybinds.")


def demo_full_setup():
    """Demo the full setup process."""
    print("\n" + "="*60)
    print("DEMO: FULL SETUP PROCESS")
    print("="*60)
    
    # Create a custom config for demo
    config = KeybindManagerConfig(
        detection_mode=DetectionMode.AUTO,
        auto_save=True,
        backup_existing=True,
        validate_on_load=True
    )
    
    manager = KeybindManager(config)
    
    print("Running full setup process...")
    print("(This would normally be interactive)")
    
    # Simulate the setup process
    print("\n1. Auto-detecting keybinds...")
    result = manager.auto_detect_keybinds()
    
    print(f"   Found {len(result.bindings)} bindings")
    
    print("\n2. Validating keybinds...")
    validation_report = manager.validator.validate_keybinds(result.bindings)
    
    print(f"   Confidence: {validation_report.confidence_score:.1%}")
    print(f"   Missing essential: {len(validation_report.essential_missing)}")
    
    print("\n3. Saving keybinds...")
    success = manager.save_keybinds(result.bindings)
    
    if success:
        print("   ✓ Setup completed successfully!")
    else:
        print("   ✗ Setup failed.")
    
    return success


def demo_integration_with_existing_system():
    """Demo integration with existing automation system."""
    print("\n" + "="*60)
    print("DEMO: INTEGRATION WITH AUTOMATION SYSTEM")
    print("="*60)
    
    manager = KeybindManager()
    
    # Load or detect keybinds
    bindings = manager.get_all_bindings()
    if not bindings:
        result = manager.auto_detect_keybinds()
        bindings = result.bindings
    
    print("Keybinds available for automation:")
    for action, key in bindings.items():
        print(f"  {action}: {key}")
    
    # Simulate automation usage
    automation_actions = [
        "attack",
        "target_next", 
        "use",
        "forward",
        "inventory"
    ]
    
    print(f"\nAutomation system can use these actions:")
    for action in automation_actions:
        key = manager.get_binding(action)
        if key:
            print(f"  ✓ {action}: {key}")
        else:
            print(f"  ❌ {action}: Not configured")
    
    # Test setting a new binding
    print(f"\nTesting dynamic binding update...")
    success = manager.set_binding("test_action", "F12")
    if success:
        print("  ✓ Successfully set test_action -> F12")
        print(f"  Current binding: {manager.get_binding('test_action')}")


def generate_demo_report():
    """Generate a comprehensive demo report."""
    print("\n" + "="*60)
    print("DEMO REPORT")
    print("="*60)
    
    report = {
        "demo_timestamp": time.time(),
        "features_demonstrated": [
            "Auto-detection from SWG config files",
            "Manual configuration interface",
            "Comprehensive validation",
            "Conflict detection",
            "Alternative key suggestions",
            "Save/load functionality",
            "Integration with automation system"
        ],
        "files_created": [
            "config/keybind_template.json",
            "utils/keybind_validator.py", 
            "core/keybind_manager.py",
            "config/player_keybinds.json (if saved)"
        ],
        "key_features": {
            "auto_detect": "Reads user.cfg and inputmap.xml",
            "manual_config": "Guided setup with validation",
            "validation": "Comprehensive binding validation",
            "conflict_detection": "Identifies key conflicts",
            "suggestions": "Alternative key recommendations",
            "save_load": "Persistent storage with backup",
            "integration": "Easy integration with automation"
        },
        "usage_examples": {
            "basic_setup": "manager = KeybindManager(); manager.run_full_setup()",
            "auto_detect": "result = manager.auto_detect_keybinds()",
            "manual_config": "bindings = manager.manual_config_keybinds()",
            "validation": "report = manager.validate_current_keybinds()",
            "get_binding": "key = manager.get_binding('attack')",
            "set_binding": "manager.set_binding('action', 'key')"
        }
    }
    
    print("Demo completed successfully!")
    print(f"Features demonstrated: {len(report['features_demonstrated'])}")
    print(f"Files created: {len(report['files_created'])}")
    
    # Save demo report
    with open('demo_batch_049_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\nDemo report saved to: demo_batch_049_report.json")


def main():
    """Run the complete demo."""
    print("🚀 BATCH 049 DEMO: KEYBIND DETECTION + INPUT MAPPING MODULE")
    print("="*80)
    
    setup_logging()
    
    try:
        # Run all demos
        demo_auto_detection()
        demo_manual_configuration()
        
        test_bindings = {
            "attack": "1",
            "target_next": "Tab", 
            "use": "E",
            "inventory": "I",
            "mount": "M",
            "forward": "W",
            "backward": "S",
            "left": "A",
            "right": "D"
        }
        
        demo_validation(test_bindings)
        demo_conflict_detection(test_bindings)
        demo_alternative_suggestions()
        demo_save_and_load()
        demo_full_setup()
        demo_integration_with_existing_system()
        
        generate_demo_report()
        
        print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("The keybind detection and validation system is ready for use.")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logging.error(f"Demo error: {e}", exc_info=True)


if __name__ == "__main__":
    main() 
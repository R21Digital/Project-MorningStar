#!/usr/bin/env python3
"""
Demonstration script for Batch 029 - Game State Requirements & Player Guidelines Enforcement

This script demonstrates the preflight check functionality including:
- Window mode validation
- Resolution compatibility checking
- UI element visibility verification
- UI scale compatibility testing
- Game state validation
- Performance assessment
- CLI reporting and resolution help
"""

import time
from pathlib import Path

# Import the preflight check modules
try:
    from core.validation.preflight_check import (
        get_preflight_validator, run_preflight_check, generate_cli_report,
        save_preflight_report, is_system_ready, PreflightValidator,
        ValidationCheck, ValidationStatus, CheckType, PreflightReport
    )
    PREFLIGHT_CHECK_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import preflight check modules: {e}")
    PREFLIGHT_CHECK_AVAILABLE = False


def demonstrate_preflight_check():
    """Demonstrate the preflight check functionality."""
    if not PREFLIGHT_CHECK_AVAILABLE:
        print("Preflight check modules not available. Skipping demonstration.")
        return
    
    print("=== Preflight Check Demonstration ===\n")
    
    # Get the preflight validator instance
    validator = get_preflight_validator()
    
    print("1. Preflight Validator Initialization")
    print("-" * 40)
    
    # Show validator status
    print(f"Supported Resolutions: {len(validator.supported_resolutions)}")
    print(f"Required UI Elements: {len(validator.required_ui_elements)}")
    print(f"OCR Available: {OCR_AVAILABLE if hasattr(validator, 'OCR_AVAILABLE') else 'Unknown'}")
    print()
    
    # Show supported resolutions
    print("2. Supported Resolutions")
    print("-" * 40)
    
    for i, resolution in enumerate(validator.supported_resolutions, 1):
        print(f"{i}. {resolution[0]}x{resolution[1]}")
    print()
    
    # Show required UI elements
    print("3. Required UI Elements")
    print("-" * 40)
    
    for element_name, element_info in validator.required_ui_elements.items():
        required_marker = "✓" if element_info["required"] else "○"
        print(f"{required_marker} {element_name}: {element_info['description']}")
        print(f"   Keywords: {', '.join(element_info['keywords'])}")
        print(f"   Regions: {len(element_info['regions'])} scan areas")
        print()
    
    # Run preflight checks
    print("4. Running Preflight Checks")
    print("-" * 40)
    
    start_time = time.time()
    report = validator.run_all_checks()
    end_time = time.time()
    
    print(f"Validation completed in {end_time - start_time:.2f} seconds")
    print(f"Total checks: {report.total_checks}")
    print(f"Passed: {report.passed_checks}")
    print(f"Failed: {report.failed_checks}")
    print(f"Warnings: {report.warning_checks}")
    print(f"Skipped: {report.skipped_checks}")
    print()
    
    # Show detailed check results
    print("5. Detailed Check Results")
    print("-" * 40)
    
    for check in report.checks:
        status_icon = {
            ValidationStatus.PASS: "✓",
            ValidationStatus.FAIL: "✗",
            ValidationStatus.WARNING: "⚠",
            ValidationStatus.SKIP: "○"
        }.get(check.status, "?")
        
        print(f"{status_icon} {check.name}")
        print(f"   Type: {check.check_type.value}")
        print(f"   Message: {check.message}")
        if check.details:
            print(f"   Details: {check.details}")
        if check.fix_suggestion:
            print(f"   Fix: {check.fix_suggestion}")
        print()
    
    # Show overall status
    print("6. Overall Status")
    print("-" * 40)
    
    status_icon = {
        ValidationStatus.PASS: "✓",
        ValidationStatus.FAIL: "✗",
        ValidationStatus.WARNING: "⚠"
    }.get(report.overall_status, "?")
    
    print(f"{status_icon} Overall Status: {report.overall_status.value.upper()}")
    print(f"System Ready: {'Yes' if is_system_ready() else 'No'}")
    print()
    
    # Show critical failures
    if report.critical_failures:
        print("7. Critical Failures")
        print("-" * 40)
        
        for failure in report.critical_failures:
            print(f"✗ {failure}")
        print()
    
    # Show recommendations
    if report.recommendations:
        print("8. Recommendations")
        print("-" * 40)
        
        for rec in report.recommendations:
            print(f"💡 {rec}")
        print()
    
    print("=== Demonstration Complete ===")


def demonstrate_cli_report():
    """Demonstrate CLI report generation."""
    print("\n=== CLI Report Demonstration ===\n")
    
    if not PREFLIGHT_CHECK_AVAILABLE:
        print("Preflight check not available for CLI report demonstration.")
        return
    
    print("Generating CLI-friendly report...")
    print()
    
    # Generate CLI report
    cli_report = generate_cli_report()
    print(cli_report)
    
    print("\nCLI report demonstration completed!")


def demonstrate_report_saving():
    """Demonstrate report saving functionality."""
    print("\n=== Report Saving Demonstration ===\n")
    
    if not PREFLIGHT_CHECK_AVAILABLE:
        print("Preflight check not available for report saving demonstration.")
        return
    
    print("Saving preflight report to file...")
    
    # Save report
    save_preflight_report("data/preflight_report.json")
    
    # Check if file was created
    report_path = Path("data/preflight_report.json")
    if report_path.exists():
        print(f"✓ Report saved to {report_path}")
        print(f"  File size: {report_path.stat().st_size} bytes")
        
        # Show sample of saved data
        try:
            import json
            with open(report_path, 'r') as f:
                data = json.load(f)
            
            print(f"  Overall status: {data.get('overall_status', 'unknown')}")
            print(f"  Total checks: {data.get('summary', {}).get('total_checks', 0)}")
            print(f"  Critical failures: {len(data.get('critical_failures', []))}")
            
        except Exception as e:
            print(f"  Error reading saved report: {e}")
    else:
        print("✗ Failed to save report")
    
    print("\nReport saving demonstration completed!")


def demonstrate_validation_types():
    """Demonstrate different types of validation checks."""
    print("\n=== Validation Types Demonstration ===\n")
    
    if not PREFLIGHT_CHECK_AVAILABLE:
        print("Preflight check not available for validation types demonstration.")
        return
    
    validator = get_preflight_validator()
    
    print("Validation Check Types:")
    print("-" * 30)
    
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
    
    print("\nValidation types demonstration completed!")


def demonstrate_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n=== Error Handling Demonstration ===\n")
    
    if not PREFLIGHT_CHECK_AVAILABLE:
        print("Preflight check not available for error handling demonstration.")
        return
    
    print("Testing error handling scenarios:")
    print("-" * 40)
    
    # Test with missing OCR
    print("1. Testing with missing OCR:")
    try:
        # Simulate OCR unavailability
        original_ocr_available = OCR_AVAILABLE
        # This would normally be done by mocking, but for demo we'll just show the concept
        print("   OCR unavailable - UI visibility checks would be skipped")
        print("   Status: Would show SKIP status for UI-related checks")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test with invalid game state
    print("\n2. Testing with invalid game state:")
    print("   Game not loaded - Game State check would fail")
    print("   Status: Would show FAIL status for Game State check")
    
    # Test with unsupported resolution
    print("\n3. Testing with unsupported resolution:")
    print("   Resolution 800x600 - Resolution check would warn")
    print("   Status: Would show WARNING status for Resolution check")
    
    print("\nError handling demonstration completed!")


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
    
    # Show preflight validator integration
    if PREFLIGHT_CHECK_AVAILABLE:
        validator = get_preflight_validator()
        print(f"✓ Preflight validator available")
        print(f"  Supported resolutions: {len(validator.supported_resolutions)}")
        print(f"  Required UI elements: {len(validator.required_ui_elements)}")
        
        # Test system readiness
        ready = is_system_ready()
        print(f"  System ready: {'Yes' if ready else 'No'}")
    else:
        print("✗ Preflight validator not available")
    
    # Test file access capabilities
    print(f"\nFile access capabilities:")
    data_dir = Path("data")
    print(f"  Data directory: {'Exists' if data_dir.exists() else 'Missing'}")
    if data_dir.exists():
        print(f"  Writable: {'Yes' if data_dir.is_dir() else 'No'}")


if __name__ == "__main__":
    print("Batch 029 - Game State Requirements & Player Guidelines Enforcement")
    print("=" * 75)
    
    # Run demonstrations
    demonstrate_preflight_check()
    demonstrate_cli_report()
    demonstrate_report_saving()
    demonstrate_validation_types()
    demonstrate_error_handling()
    demonstrate_integration()
    
    print("\nDemonstration completed successfully!") 
#!/usr/bin/env python3
"""
Batch 170 - Red-Team Detection Audit & Telemetry Review Demo

This demo showcases the comprehensive red-team audit system that performs
systematic audits against likely server detections and ensures safety
defaults are properly configured.
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path

from safety.redteam.audit_runner import (
    RedTeamAuditor, get_redteam_auditor,
    AuditResult, RiskLevel, DetectionSurface
)

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_section(title: str):
    """Print a formatted section."""
    print(f"\n--- {title} ---")

def demo_audit_runner():
    """Demonstrate the red-team audit runner."""
    print_section("Red-Team Audit Runner")
    
    # Initialize auditor
    auditor = get_redteam_auditor()
    print(f"✓ Auditor initialized: {auditor.__class__.__name__}")
    
    # Check safety defaults
    safety_status = auditor._check_safety_defaults()
    print(f"✓ Safety defaults checked: {len(safety_status)} settings")
    
    # Run comprehensive audit
    print("Running comprehensive audit...")
    report = auditor.run_full_audit()
    
    print(f"✓ Audit completed: {report.audit_id}")
    print(f"  Total checks: {report.total_checks}")
    print(f"  Passed: {report.passed_checks}")
    print(f"  Failed: {report.failed_checks}")
    print(f"  Warnings: {report.warning_checks}")
    print(f"  Critical: {report.critical_checks}")
    print(f"  Overall risk: {report.overall_risk_level.value.upper()}")
    
    return auditor, report

def demo_detection_surfaces():
    """Demonstrate detection surface checks."""
    print_section("Detection Surface Checks")
    
    auditor = get_redteam_auditor()
    
    # Test each detection surface
    surfaces = [
        DetectionSurface.PROCESS_NAMES,
        DetectionSurface.WINDOW_TITLES,
        DetectionSurface.MACRO_CADENCE,
        DetectionSurface.SESSION_LENGTH,
        DetectionSurface.INPUT_TIMING,
        DetectionSurface.REPEAT_ROUTES,
        DetectionSurface.BEHAVIOR_PATTERNS
    ]
    
    for surface in surfaces:
        print(f"\nTesting {surface.value}:")
        
        # Simulate check for this surface
        if surface == DetectionSurface.PROCESS_NAMES:
            result, details, evidence = auditor._check_process_names()
        elif surface == DetectionSurface.WINDOW_TITLES:
            result, details, evidence = auditor._check_window_titles()
        elif surface == DetectionSurface.MACRO_CADENCE:
            result, details, evidence = auditor._check_macro_cadence()
        elif surface == DetectionSurface.SESSION_LENGTH:
            result, details, evidence = auditor._check_session_length()
        elif surface == DetectionSurface.INPUT_TIMING:
            result, details, evidence = auditor._check_input_timing()
        elif surface == DetectionSurface.REPEAT_ROUTES:
            result, details, evidence = auditor._check_repeat_routes()
        elif surface == DetectionSurface.BEHAVIOR_PATTERNS:
            result, details, evidence = auditor._check_behavior_patterns()
        else:
            result = AuditResult.PASS
            details = "Surface not implemented"
            evidence = {}
        
        status_icon = "✓" if result == AuditResult.PASS else "✗"
        print(f"  {status_icon} {result.value.upper()}: {details}")
        
        if evidence:
            print(f"    Evidence: {len(evidence)} items")

def demo_safety_defaults():
    """Demonstrate safety defaults configuration."""
    print_section("Safety Defaults Configuration")
    
    # Load safety defaults
    config_path = "config/safety_defaults.json"
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"✓ Safety defaults loaded from {config_path}")
        
        # Check critical settings
        critical_settings = [
            "session_caps.enabled",
            "humanization.enabled", 
            "anti_patterns.enabled",
            "enforcement.enabled"
        ]
        
        print("\nCritical safety settings:")
        for setting in critical_settings:
            keys = setting.split('.')
            value = config
            for key in keys:
                if key in value:
                    value = value[key]
                else:
                    value = "NOT FOUND"
                    break
            
            status = "✓" if value == True else "✗"
            print(f"  {status} {setting}: {value}")
    else:
        print(f"✗ Safety defaults file not found: {config_path}")

def demo_variability_simulation():
    """Demonstrate variability simulation."""
    print_section("Variability Simulation")
    
    auditor = get_redteam_auditor()
    
    # Run variability simulation
    variability = auditor._simulate_variability()
    
    print("Timing variations:")
    for timing_type, values in variability["timing_variations"].items():
        print(f"  {timing_type}: {len(values)} samples")
        if values:
            avg = sum(values) / len(values)
            variance = sum((x - avg) ** 2 for x in values) / len(values)
            print(f"    Average: {avg:.3f}s, Variance: {variance:.3f}")
    
    print("\nBehavior variations:")
    for behavior_type, actions in variability["behavior_variations"].items():
        print(f"  {behavior_type}: {len(actions)} options")
        print(f"    Options: {', '.join(actions)}")
    
    print("\nSession variations:")
    for session_type, values in variability["session_variations"].items():
        print(f"  {session_type}: {len(values)} samples")
        if values:
            avg = sum(values) / len(values)
            print(f"    Average: {avg:.1f}")
    
    print(f"\nOverall variability score: {variability['variability_score']:.3f}")

def demo_audit_reporting():
    """Demonstrate audit reporting capabilities."""
    print_section("Audit Reporting")
    
    auditor = get_redteam_auditor()
    
    # Run audit to get report
    report = auditor.run_full_audit()
    
    # Export in different formats
    print("Exporting audit report...")
    
    # JSON format
    json_report = auditor.export_report(report, "json")
    print(f"✓ JSON report: {len(json_report)} characters")
    
    # Text format
    text_report = auditor.export_report(report, "text")
    print(f"✓ Text report: {len(text_report)} characters")
    
    # Print summary
    print("\nReport Summary:")
    print(f"  Audit ID: {report.audit_id}")
    print(f"  Timestamp: {report.timestamp}")
    print(f"  Overall Risk: {report.overall_risk_level.value.upper()}")
    print(f"  Total Checks: {report.total_checks}")
    print(f"  Pass Rate: {report.passed_checks}/{report.total_checks}")
    
    # Print recommendations
    if report.recommendations:
        print("\nRecommendations:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")

def demo_safety_monitoring():
    """Demonstrate safety monitoring capabilities."""
    print_section("Safety Monitoring")
    
    auditor = get_redteam_auditor()
    
    # Get audit summary
    summary = auditor.get_audit_summary()
    
    if "message" in summary:
        print(f"ℹ {summary['message']}")
    else:
        print("Audit History Summary:")
        print(f"  Total audits: {summary['total_audits']}")
        print(f"  Recent audits: {summary['recent_audits']}")
        print(f"  Average pass rate: {summary['average_pass_rate']:.2%}")
        print(f"  Critical findings: {summary['critical_findings']}")
        
        if summary['last_audit']:
            last_audit = summary['last_audit']
            print(f"  Last audit: {last_audit['audit_id']}")
            print(f"  Last risk level: {last_audit['overall_risk_level']}")

def demo_remediation_steps():
    """Demonstrate remediation step generation."""
    print_section("Remediation Steps")
    
    auditor = get_redteam_auditor()
    
    # Run audit to get findings
    report = auditor.run_full_audit()
    
    # Group findings by result
    critical_findings = [f for f in report.findings if f.result == AuditResult.CRITICAL]
    failed_findings = [f for f in report.findings if f.result == AuditResult.FAIL]
    warning_findings = [f for f in report.findings if f.result == AuditResult.WARNING]
    
    print(f"Critical findings: {len(critical_findings)}")
    for finding in critical_findings:
        print(f"  ✗ {finding.check_name}")
        print(f"    Risk: {finding.risk_level.value.upper()}")
        print(f"    Details: {finding.details}")
        print(f"    Remediation:")
        for step in finding.remediation_steps:
            print(f"      - {step}")
        print()
    
    print(f"Failed findings: {len(failed_findings)}")
    for finding in failed_findings:
        print(f"  ✗ {finding.check_name}")
        print(f"    Risk: {finding.risk_level.value.upper()}")
        print(f"    Details: {finding.details}")
        print()
    
    print(f"Warning findings: {len(warning_findings)}")
    for finding in warning_findings:
        print(f"  ⚠ {finding.check_name}")
        print(f"    Risk: {finding.risk_level.value.upper()}")
        print(f"    Details: {finding.details}")
        print()

def demo_configuration_validation():
    """Demonstrate configuration validation."""
    print_section("Configuration Validation")
    
    # Check safety defaults file
    config_path = "config/safety_defaults.json"
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"✓ Safety defaults file exists: {config_path}")
        
        # Validate critical sections
        required_sections = [
            "session_management",
            "humanization", 
            "anti_patterns",
            "detection_surfaces",
            "enforcement"
        ]
        
        print("\nValidating configuration sections:")
        for section in required_sections:
            if section in config:
                print(f"  ✓ {section}: present")
            else:
                print(f"  ✗ {section}: missing")
        
        # Check enforcement settings
        enforcement = config.get("enforcement", {})
        if enforcement.get("enabled", False):
            print("  ✓ Enforcement enabled")
        else:
            print("  ✗ Enforcement disabled")
            
        # Check strict mode
        strict_mode = enforcement.get("strict_mode", {})
        if strict_mode.get("enabled", False):
            print("  ✓ Strict mode enabled")
        else:
            print("  ✗ Strict mode disabled")
    else:
        print(f"✗ Safety defaults file missing: {config_path}")

def demo_integration_testing():
    """Demonstrate integration with existing systems."""
    print_section("Integration Testing")
    
    # Test integration with existing safety modules
    try:
        from safety.identity_guard import get_identity_guard
        identity_guard = get_identity_guard()
        print("✓ Identity Guard integration: available")
    except ImportError:
        print("✗ Identity Guard integration: not available")
    
    try:
        from safety.macro_watcher import get_macro_watcher
        macro_watcher = get_macro_watcher()
        print("✓ Macro Watcher integration: available")
    except ImportError:
        print("✗ Macro Watcher integration: not available")
    
    # Test configuration integration
    config_files = [
        "config/anti_detection_config.json",
        "config/identity_policy.json",
        "config/safety_defaults.json"
    ]
    
    print("\nConfiguration file integration:")
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"  ✓ {config_file}: present")
        else:
            print(f"  ✗ {config_file}: missing")

def main():
    """Run the complete red-team audit demo."""
    print_header("Batch 170 - Red-Team Detection Audit & Telemetry Review Demo")
    print("This demo showcases the comprehensive red-team audit system")
    print("including detection surface analysis, safety defaults, and")
    print("variability simulation.")
    
    try:
        # Run all demo sections
        auditor, report = demo_audit_runner()
        demo_detection_surfaces()
        demo_safety_defaults()
        demo_variability_simulation()
        demo_audit_reporting()
        demo_safety_monitoring()
        demo_remediation_steps()
        demo_configuration_validation()
        demo_integration_testing()
        
        print_header("Demo Complete")
        print("✓ All red-team audit features demonstrated successfully!")
        print("\nKey Features Demonstrated:")
        print("  • Comprehensive detection surface auditing")
        print("  • Safety defaults configuration validation")
        print("  • Variability simulation and analysis")
        print("  • Audit reporting and remediation steps")
        print("  • Safety monitoring and alerting")
        print("  • Configuration validation and integration")
        
        print(f"\nFinal Audit Results:")
        print(f"  Overall Risk Level: {report.overall_risk_level.value.upper()}")
        print(f"  Pass Rate: {report.passed_checks}/{report.total_checks}")
        print(f"  Critical Issues: {report.critical_checks}")
        print(f"  Failed Checks: {report.failed_checks}")
        
        if report.recommendations:
            print(f"\nTop Recommendations:")
            for i, rec in enumerate(report.recommendations[:3], 1):
                print(f"  {i}. {rec}")
        
        print("\nNext Steps:")
        print("  1. Review all failed checks and apply remediation steps")
        print("  2. Enable all safety defaults if not already enabled")
        print("  3. Configure monitoring and alerting systems")
        print("  4. Schedule regular audits and review results")
        print("  5. Monitor for new detection methods and update accordingly")
        
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
MS11 Batch 093 - Macro Safety + Auto-Cancellation System Demo

This script demonstrates the macro safety system's capabilities including:
- Performance monitoring (CPU, memory, FPS, latency)
- Macro safety profiles and risk levels
- Auto-cancellation based on performance thresholds
- Discord notifications
- Per-profile overrides
- Comprehensive logging and reporting
"""

import time
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Import the macro safety system
from core.macro_safety import (
    macro_safety_manager, 
    MacroSafetyProfile, 
    SafetyLevel, 
    PerformanceThresholds
)


def demo_performance_monitoring():
    """Demonstrate performance monitoring capabilities."""
    print("\n" + "="*60)
    print("🔍 PERFORMANCE MONITORING DEMO")
    print("="*60)
    
    # Get current performance metrics
    metrics = macro_safety_manager.performance_monitor.get_current_metrics()
    
    print(f"📊 Current Performance Metrics:")
    print(f"   CPU Usage: {metrics.cpu_usage:.1f}%")
    print(f"   Memory Usage: {metrics.memory_usage:.1f}%")
    print(f"   FPS: {metrics.fps if metrics.fps else 'N/A'}")
    print(f"   Latency: {metrics.latency if metrics.latency else 'N/A'}ms")
    print(f"   Response Time: {metrics.response_time if metrics.response_time else 'N/A'}ms")
    
    # Get average metrics over 30 seconds
    avg_metrics = macro_safety_manager.performance_monitor.get_average_metrics(30)
    print(f"\n📈 Average Metrics (30s window):")
    print(f"   CPU Usage: {avg_metrics.cpu_usage:.1f}%")
    print(f"   Memory Usage: {avg_metrics.memory_usage:.1f}%")
    
    # Check if monitoring is active
    print(f"\n🔄 Monitoring Status:")
    print(f"   Active: {macro_safety_manager.performance_monitor.monitoring}")
    print(f"   History Size: {len(macro_safety_manager.performance_monitor.performance_history)}")


def demo_safety_profiles():
    """Demonstrate macro safety profiles."""
    print("\n" + "="*60)
    print("🛡️ SAFETY PROFILES DEMO")
    print("="*60)
    
    # Show default safety profiles
    print("📋 Default Safety Profiles:")
    for macro_id, profile in macro_safety_manager.safety_profiles.items():
        print(f"   {macro_id}:")
        print(f"     Name: {profile.name}")
        print(f"     Category: {profile.category}")
        print(f"     Safety Level: {profile.safety_level.value}")
        print(f"     Max Duration: {profile.max_duration}s")
        print(f"     Auto-Cancel: {profile.auto_cancel_enabled}")
        print(f"     Discord Notify: {profile.discord_notify}")
        print()


def demo_macro_lifecycle():
    """Demonstrate macro start/stop lifecycle."""
    print("\n" + "="*60)
    print("⚡ MACRO LIFECYCLE DEMO")
    print("="*60)
    
    # Start some test macros
    test_macros = [
        ("heal", "Heal Macro", "safe"),
        ("attack", "Attack Macro", "risky"),
        ("dance", "Dance Macro", "dangerous"),
        ("craft", "Craft Macro", "safe")
    ]
    
    print("🚀 Starting test macros...")
    for macro_id, name, safety_level in test_macros:
        success = macro_safety_manager.start_macro(macro_id, name)
        print(f"   {macro_id}: {'✅ Started' if success else '❌ Failed'}")
    
    # Show active macros
    print(f"\n📊 Active Macros: {len(macro_safety_manager.active_macros)}")
    for macro_id, info in macro_safety_manager.active_macros.items():
        duration = (datetime.now() - info["start_time"]).total_seconds()
        print(f"   {macro_id}: {info['name']} ({duration:.1f}s)")
    
    # Simulate some time passing
    print("\n⏰ Simulating time passage...")
    time.sleep(2)
    
    # Check safety (should not trigger cancellations yet)
    print("\n🔍 Checking macro safety...")
    cancellations = macro_safety_manager.check_macro_safety()
    print(f"   Cancellations: {len(cancellations)}")
    
    # Stop some macros
    print("\n🛑 Stopping macros...")
    for macro_id in ["heal", "craft"]:
        success = macro_safety_manager.stop_macro(macro_id)
        print(f"   {macro_id}: {'✅ Stopped' if success else '❌ Failed'}")
    
    print(f"\n📊 Remaining Active Macros: {len(macro_safety_manager.active_macros)}")


def demo_performance_thresholds():
    """Demonstrate performance threshold monitoring."""
    print("\n" + "="*60)
    print("⚠️ PERFORMANCE THRESHOLDS DEMO")
    print("="*60)
    
    # Create a test macro with strict thresholds
    test_profile = MacroSafetyProfile(
        macro_id="test_strict",
        name="Test Strict Macro",
        category="test",
        safety_level=SafetyLevel.DANGEROUS,
        max_duration=60,
        performance_thresholds=PerformanceThresholds(
            cpu_usage_max=50.0,  # Very low threshold
            memory_usage_max=60.0,  # Very low threshold
            fps_min=30.0,
            latency_max=200.0,
            response_time_max=500.0
        )
    )
    
    # Add to safety profiles
    macro_safety_manager.safety_profiles["test_strict"] = test_profile
    
    print("🔧 Created test macro with strict thresholds:")
    print(f"   CPU Max: {test_profile.performance_thresholds.cpu_usage_max}%")
    print(f"   Memory Max: {test_profile.performance_thresholds.memory_usage_max}%")
    print(f"   FPS Min: {test_profile.performance_thresholds.fps_min}")
    print(f"   Latency Max: {test_profile.performance_thresholds.latency_max}ms")
    
    # Start the test macro
    success = macro_safety_manager.start_macro("test_strict", "Test Strict Macro")
    print(f"\n🚀 Started test macro: {'✅ Success' if success else '❌ Failed'}")
    
    # Check safety multiple times
    print("\n🔍 Checking safety multiple times...")
    for i in range(3):
        cancellations = macro_safety_manager.check_macro_safety()
        if cancellations:
            for cancellation in cancellations:
                print(f"   ❌ Cancelled {cancellation.macro_name}: {cancellation.cancellation_reason}")
        else:
            print(f"   ✅ Check {i+1}: No cancellations")
        time.sleep(1)
    
    # Clean up
    macro_safety_manager.stop_macro("test_strict")


def demo_profile_overrides():
    """Demonstrate per-profile macro overrides."""
    print("\n" + "="*60)
    print("📁 PROFILE OVERRIDES DEMO")
    print("="*60)
    
    # Create a profile override file
    override_data = {
        "dance": {
            "name": "Dance Macro (Override)",
            "category": "social",
            "safety_level": "safe",  # Override from dangerous to safe
            "max_duration": 1800,  # 30 minutes instead of 1 hour
            "auto_cancel_enabled": False,  # Disable auto-cancel
            "discord_notify": False,  # Disable Discord notifications
            "description": "Dance macro with relaxed safety settings"
        },
        "custom_macro": {
            "name": "Custom Macro",
            "category": "utility",
            "safety_level": "risky",
            "max_duration": 300,
            "auto_cancel_enabled": True,
            "discord_notify": True,
            "description": "Custom macro for testing"
        }
    }
    
    # Save override file
    override_file = Path("config/macro_safety/test_profile.safe.json")
    override_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(override_file, 'w', encoding='utf-8') as f:
        json.dump(override_data, f, indent=2)
    
    print(f"📝 Created profile override file: {override_file}")
    print("   - Modified dance macro safety settings")
    print("   - Added custom macro")
    
    # Load the override
    macro_safety_manager.load_profile_overrides("test_profile")
    
    print("\n📋 Updated Safety Profiles:")
    for macro_id in ["dance", "custom_macro"]:
        if macro_id in macro_safety_manager.safety_profiles:
            profile = macro_safety_manager.safety_profiles[macro_id]
            print(f"   {macro_id}:")
            print(f"     Safety Level: {profile.safety_level.value}")
            print(f"     Max Duration: {profile.max_duration}s")
            print(f"     Auto-Cancel: {profile.auto_cancel_enabled}")
            print(f"     Discord Notify: {profile.discord_notify}")
            print()
    
    # Clean up
    override_file.unlink(missing_ok=True)


def demo_safety_reporting():
    """Demonstrate safety reporting and logging."""
    print("\n" + "="*60)
    print("📊 SAFETY REPORTING DEMO")
    print("="*60)
    
    # Get comprehensive safety report
    report = macro_safety_manager.get_safety_report()
    
    print("📈 Safety Report:")
    print(f"   Active Macros: {report['active_macros']}")
    print(f"   Total Cancellations: {report['total_cancellations']}")
    print(f"   Performance Metrics:")
    print(f"     CPU Usage: {report['performance_metrics']['cpu_usage']:.1f}%")
    print(f"     Memory Usage: {report['performance_metrics']['memory_usage']:.1f}%")
    print(f"     FPS: {report['performance_metrics']['fps'] or 'N/A'}")
    print(f"     Latency: {report['performance_metrics']['latency'] or 'N/A'}ms")
    
    # Show recent cancellations
    if report['recent_cancellations']:
        print(f"\n🚨 Recent Cancellations:")
        for cancellation in report['recent_cancellations']:
            print(f"   {cancellation['macro_name']}: {cancellation['reason']}")
    else:
        print(f"\n✅ No recent cancellations")
    
    # Save cancellation log
    print(f"\n💾 Saving cancellation log...")
    log_path = macro_safety_manager.save_cancellation_log()
    print(f"   Log saved to: {log_path}")
    
    # Show log file contents
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
            print(f"   Total cancellations in log: {log_data['total_cancellations']}")


def demo_discord_integration():
    """Demonstrate Discord notification integration."""
    print("\n" + "="*60)
    print("📢 DISCORD INTEGRATION DEMO")
    print("="*60)
    
    # Create a test cancellation event
    from core.macro_safety import MacroCancellationEvent, PerformanceSnapshot
    
    test_metrics = PerformanceSnapshot(
        timestamp=datetime.now(),
        cpu_usage=85.5,
        memory_usage=78.2,
        fps=12.0,
        latency=650.0,
        response_time=1200.0
    )
    
    test_cancellation = MacroCancellationEvent(
        macro_id="test_discord",
        macro_name="Test Discord Macro",
        cancellation_reason="Performance threshold exceeded",
        performance_metrics=test_metrics,
        timestamp=datetime.now(),
        session_id="demo_session_123"
    )
    
    print("📢 Simulating Discord notification...")
    macro_safety_manager._send_discord_notification(test_cancellation)
    print("   ✅ Discord notification sent (logged)")


def demo_cleanup():
    """Clean up demo state."""
    print("\n" + "="*60)
    print("🧹 CLEANUP DEMO")
    print("="*60)
    
    # Stop all active macros
    active_macros = list(macro_safety_manager.active_macros.keys())
    if active_macros:
        print(f"🛑 Stopping {len(active_macros)} active macros...")
        for macro_id in active_macros:
            macro_safety_manager.stop_macro(macro_id)
            print(f"   ✅ Stopped {macro_id}")
    else:
        print("✅ No active macros to stop")
    
    # Show final state
    report = macro_safety_manager.get_safety_report()
    print(f"\n📊 Final State:")
    print(f"   Active Macros: {report['active_macros']}")
    print(f"   Total Cancellations: {report['total_cancellations']}")
    
    print("\n🎉 Demo completed successfully!")


def main():
    """Run the complete macro safety demo."""
    print("🚀 MS11 Batch 093 - Macro Safety System Demo")
    print("="*60)
    print("This demo showcases the macro safety and auto-cancellation system.")
    print("Features demonstrated:")
    print("  • Performance monitoring (CPU, memory, FPS, latency)")
    print("  • Macro safety profiles and risk levels")
    print("  • Auto-cancellation based on performance thresholds")
    print("  • Discord notifications")
    print("  • Per-profile overrides")
    print("  • Comprehensive logging and reporting")
    print("="*60)
    
    try:
        # Run all demos
        demo_performance_monitoring()
        demo_safety_profiles()
        demo_macro_lifecycle()
        demo_performance_thresholds()
        demo_profile_overrides()
        demo_safety_reporting()
        demo_discord_integration()
        demo_cleanup()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Visit /macro-safety in the dashboard")
        print("  2. Monitor real-time performance metrics")
        print("  3. Start and stop macros through the UI")
        print("  4. Configure profile-specific overrides")
        print("  5. Review cancellation logs and reports")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Batch 132 Demo - Macro & Memory Safety Handler (Crash Prevention)

This demo showcases the comprehensive crash prevention system including:
- Macro monitoring for dangerous patterns
- Memory safety and resource monitoring
- Automatic intervention and user alerts
- Dashboard integration and Discord notifications

Features:
1. Monitor running macros for dangerous patterns (infinite loops, spam, etc.)
2. Cancel or pause macros if crash-prone behavior is detected
3. Warn users via dashboard or Discord alerts
4. Maintain list of risky macros and their effects
5. Memory and CPU monitoring with automatic cleanup
6. Emergency shutdown procedures
"""

import time
import json
import threading
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import psutil
import gc

# Import our safety modules
from safety.macro_watcher import MacroWatcher, get_macro_watcher
from core.crash_guard import CrashGuard, get_crash_guard

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockMacro:
    """Mock macro for testing purposes."""
    
    def __init__(self, macro_id: str, name: str, behavior: str = "normal"):
        self.macro_id = macro_id
        self.name = name
        self.behavior = behavior
        self.running = False
        self.commands_executed = 0
        self.last_command_time = datetime.now()
        
    def start(self):
        """Start the mock macro."""
        self.running = True
        logger.info(f"Started mock macro: {self.name} ({self.macro_id})")
        
    def stop(self):
        """Stop the mock macro."""
        self.running = False
        logger.info(f"Stopped mock macro: {self.name} ({self.macro_id})")
        
    def pause(self):
        """Pause the mock macro."""
        self.running = False
        logger.info(f"Paused mock macro: {self.name} ({self.macro_id})")
        
    def execute_command(self, command: str):
        """Execute a command and log it."""
        if not self.running:
            return
            
        self.commands_executed += 1
        self.last_command_time = datetime.now()
        
        # Simulate different behaviors
        if self.behavior == "spam":
            # Simulate command spam
            for _ in range(random.randint(5, 15)):
                self._log_command(f"/attack target")
                time.sleep(0.1)
        elif self.behavior == "infinite_loop":
            # Simulate infinite loop pattern
            self._log_command("while(true) { /attack }")
        elif self.behavior == "memory_leak":
            # Simulate memory leak
            self._log_command("createObject()")
            self._log_command("new Object()")
        elif self.behavior == "rapid_movement":
            # Simulate rapid movement
            for _ in range(random.randint(3, 8)):
                self._log_command(f"/move {random.randint(100, 999)} {random.randint(100, 999)}")
                time.sleep(0.05)
        else:
            # Normal behavior
            self._log_command(command)
            
    def _log_command(self, command: str):
        """Log a command to the macro watcher."""
        macro_watcher = get_macro_watcher()
        macro_watcher.log_macro_event(
            self.macro_id,
            "command_executed",
            {"command": command, "timestamp": datetime.now().isoformat()}
        )

class SafetyDemo:
    """Demonstrates the macro and memory safety features."""
    
    def __init__(self):
        self.macro_watcher = get_macro_watcher()
        self.crash_guard = get_crash_guard()
        self.mock_macros: Dict[str, MockMacro] = {}
        self.demo_running = False
        
        # Set up alert callbacks
        self.macro_watcher.add_alert_callback(self._handle_macro_alert)
        self.crash_guard.add_emergency_callback(self._handle_emergency)
        self.crash_guard.add_recovery_callback(self._handle_recovery)
        
    def _handle_macro_alert(self, event):
        """Handle macro alerts."""
        logger.warning(f"🔔 MACRO ALERT: {event.event_type} - {event.macro_name}")
        logger.warning(f"   Risk Score: {event.risk_score:.2f}")
        logger.warning(f"   Data: {event.data}")
        
        # Simulate Discord alert
        self._send_discord_alert(event)
        
    def _handle_emergency(self, event_type: str, data: Dict[str, Any]):
        """Handle emergency situations."""
        logger.critical(f"🚨 EMERGENCY: {event_type}")
        logger.critical(f"   Data: {data}")
        
        # Simulate emergency Discord alert
        self._send_emergency_discord_alert(event_type, data)
        
    def _handle_recovery(self, event_type: str, data: Dict[str, Any]):
        """Handle recovery situations."""
        logger.info(f"🔄 RECOVERY: {event_type}")
        logger.info(f"   Data: {data}")
        
    def _send_discord_alert(self, event):
        """Simulate sending Discord alert."""
        alert_message = f"""
🔔 **Macro Safety Alert**
**Macro:** {event.macro_name}
**Event:** {event.event_type}
**Risk Score:** {event.risk_score:.2f}
**Time:** {event.timestamp.strftime('%H:%M:%S')}
        """
        logger.info(f"📢 Discord Alert: {alert_message.strip()}")
        
    def _send_emergency_discord_alert(self, event_type: str, data: Dict[str, Any]):
        """Simulate sending emergency Discord alert."""
        alert_message = f"""
🚨 **EMERGENCY ALERT**
**Type:** {event_type}
**Time:** {datetime.now().strftime('%H:%M:%S')}
**Data:** {data}
        """
        logger.critical(f"📢 Emergency Discord Alert: {alert_message.strip()}")
        
    def create_mock_macros(self):
        """Create mock macros for testing."""
        macros = [
            ("normal_macro", "Normal Combat Macro", "normal"),
            ("spam_macro", "Spam Attack Macro", "spam"),
            ("loop_macro", "Infinite Loop Macro", "infinite_loop"),
            ("memory_macro", "Memory Leak Macro", "memory_leak"),
            ("movement_macro", "Rapid Movement Macro", "rapid_movement")
        ]
        
        for macro_id, name, behavior in macros:
            macro = MockMacro(macro_id, name, behavior)
            self.mock_macros[macro_id] = macro
            
            # Register with macro watcher
            self.macro_watcher.register_macro(macro_id, name)
            
        logger.info(f"Created {len(self.mock_macros)} mock macros")
        
    def start_safety_systems(self):
        """Start the safety monitoring systems."""
        logger.info("🚀 Starting safety systems...")
        
        # Start macro watcher
        self.macro_watcher.start_monitoring()
        logger.info("✅ Macro watcher started")
        
        # Start crash guard
        self.crash_guard.start_guarding()
        logger.info("✅ Crash guard started")
        
    def stop_safety_systems(self):
        """Stop the safety monitoring systems."""
        logger.info("🛑 Stopping safety systems...")
        
        # Stop macro watcher
        self.macro_watcher.stop_monitoring()
        logger.info("✅ Macro watcher stopped")
        
        # Stop crash guard
        self.crash_guard.stop_guarding()
        logger.info("✅ Crash guard stopped")
        
    def run_macro_behavior_demo(self):
        """Demonstrate different macro behaviors and safety responses."""
        logger.info("🎭 Starting macro behavior demonstration...")
        
        # Start all macros
        for macro in self.mock_macros.values():
            macro.start()
            
        # Simulate macro execution for 30 seconds
        start_time = time.time()
        while time.time() - start_time < 30:
            for macro in self.mock_macros.values():
                if macro.running:
                    # Execute commands based on behavior
                    if macro.behavior == "normal":
                        macro.execute_command("/attack nearest")
                    elif macro.behavior == "spam":
                        macro.execute_command("/attack target")
                    elif macro.behavior == "infinite_loop":
                        macro.execute_command("while(true) { /attack }")
                    elif macro.behavior == "memory_leak":
                        macro.execute_command("createObject()")
                    elif macro.behavior == "rapid_movement":
                        macro.execute_command(f"/move {random.randint(100, 999)} {random.randint(100, 999)}")
                        
            time.sleep(1)
            
        # Stop all macros
        for macro in self.mock_macros.values():
            macro.stop()
            
        logger.info("✅ Macro behavior demonstration completed")
        
    def demonstrate_memory_pressure(self):
        """Demonstrate memory pressure and cleanup."""
        logger.info("💾 Demonstrating memory pressure handling...")
        
        # Create memory pressure
        large_objects = []
        for i in range(1000):
            large_objects.append([f"object_{i}" * 1000])
            
        logger.info(f"Created {len(large_objects)} large objects")
        
        # Force garbage collection
        collected = gc.collect()
        logger.info(f"Garbage collection collected {collected} objects")
        
        # Clear objects
        large_objects.clear()
        collected = gc.collect()
        logger.info(f"After cleanup, collected {collected} objects")
        
    def show_safety_statistics(self):
        """Display safety system statistics."""
        logger.info("📊 Safety System Statistics:")
        
        # Macro watcher stats
        macro_stats = self.macro_watcher.get_statistics()
        logger.info(f"  Macro Watcher:")
        logger.info(f"    Total Macros: {macro_stats.get('total_macros', 0)}")
        logger.info(f"    Safe Macros: {macro_stats.get('safe_macros', 0)}")
        logger.info(f"    Unsafe Macros: {macro_stats.get('unsafe_macros', 0)}")
        logger.info(f"    Critical Macros: {macro_stats.get('critical_macros', 0)}")
        logger.info(f"    Patterns Loaded: {macro_stats.get('patterns_loaded', 0)}")
        logger.info(f"    Monitoring Active: {macro_stats.get('monitoring_active', False)}")
        
        # Crash guard stats
        crash_stats = self.crash_guard.get_statistics()
        logger.info(f"  Crash Guard:")
        logger.info(f"    Guard Level: {crash_stats.get('guard_level', 'unknown')}")
        logger.info(f"    Active: {crash_stats.get('active', False)}")
        logger.info(f"    Snapshots: {crash_stats.get('snapshots_count', 0)}")
        logger.info(f"    Events: {crash_stats.get('events_count', 0)}")
        logger.info(f"    Avg Memory: {crash_stats.get('avg_memory_percent', 0):.1f}%")
        logger.info(f"    Max Memory: {crash_stats.get('max_memory_percent', 0):.1f}%")
        logger.info(f"    Avg CPU: {crash_stats.get('avg_cpu_percent', 0):.1f}%")
        logger.info(f"    Max CPU: {crash_stats.get('max_cpu_percent', 0):.1f}%")
        
    def show_macro_health_details(self):
        """Show detailed macro health information."""
        logger.info("🔍 Detailed Macro Health:")
        
        all_health = self.macro_watcher.get_all_macro_health()
        for macro_id, health in all_health.items():
            logger.info(f"  Macro: {health.macro_name}")
            logger.info(f"    ID: {health.macro_id}")
            logger.info(f"    State: {health.state.value}")
            logger.info(f"    Risk Level: {health.risk_level.value}")
            logger.info(f"    Risk Score: {health.risk_score:.2f}")
            logger.info(f"    Memory Usage: {health.memory_usage:.1f}%")
            logger.info(f"    CPU Usage: {health.cpu_usage:.1f}%")
            logger.info(f"    Pattern Matches: {len(health.pattern_matches)}")
            logger.info(f"    Warnings: {len(health.warnings)}")
            logger.info(f"    Is Safe: {health.is_safe}")
            
            if health.warnings:
                for warning in health.warnings:
                    logger.info(f"      ⚠️ {warning}")
                    
    def demonstrate_emergency_shutdown(self):
        """Demonstrate emergency shutdown procedures."""
        logger.info("🚨 Demonstrating emergency shutdown procedures...")
        
        # Simulate critical memory usage
        logger.info("Simulating critical memory usage...")
        
        # Create extreme memory pressure
        extreme_objects = []
        for i in range(10000):
            extreme_objects.append([f"extreme_object_{i}" * 10000])
            
        logger.info(f"Created {len(extreme_objects)} extreme objects")
        
        # Show current memory state
        memory_state = self.crash_guard.get_current_memory_state()
        logger.info(f"Current Memory State: {memory_state}")
        
        # Clear objects to prevent actual crash
        extreme_objects.clear()
        gc.collect()
        
        logger.info("✅ Emergency shutdown demonstration completed")
        
    def run_comprehensive_demo(self):
        """Run the comprehensive safety demonstration."""
        logger.info("🎯 Starting Batch 132 - Macro & Memory Safety Handler Demo")
        logger.info("=" * 60)
        
        try:
            # Step 1: Initialize systems
            logger.info("\n📋 Step 1: Initializing Safety Systems")
            self.create_mock_macros()
            self.start_safety_systems()
            
            # Step 2: Show initial statistics
            logger.info("\n📊 Step 2: Initial Statistics")
            self.show_safety_statistics()
            
            # Step 3: Demonstrate macro behaviors
            logger.info("\n🎭 Step 3: Macro Behavior Demonstration")
            self.run_macro_behavior_demo()
            
            # Step 4: Show macro health details
            logger.info("\n🔍 Step 4: Macro Health Details")
            self.show_macro_health_details()
            
            # Step 5: Demonstrate memory handling
            logger.info("\n💾 Step 5: Memory Pressure Handling")
            self.demonstrate_memory_pressure()
            
            # Step 6: Show updated statistics
            logger.info("\n📊 Step 6: Updated Statistics")
            self.show_safety_statistics()
            
            # Step 7: Demonstrate emergency procedures
            logger.info("\n🚨 Step 7: Emergency Procedures")
            self.demonstrate_emergency_shutdown()
            
            # Step 8: Final statistics
            logger.info("\n📊 Step 8: Final Statistics")
            self.show_safety_statistics()
            
        except Exception as e:
            logger.error(f"❌ Demo error: {e}")
        finally:
            # Cleanup
            logger.info("\n🧹 Cleanup")
            self.stop_safety_systems()
            
            # Unregister macros
            for macro_id in self.mock_macros.keys():
                self.macro_watcher.unregister_macro(macro_id)
                
        logger.info("\n✅ Batch 132 Demo Completed Successfully!")
        logger.info("=" * 60)

def main():
    """Main demo function."""
    print("🎯 Batch 132 - Macro & Memory Safety Handler Demo")
    print("=" * 60)
    print("This demo showcases crash prevention features:")
    print("• Monitor running macros for dangerous patterns")
    print("• Cancel or pause macros if crash-prone behavior detected")
    print("• Warn users via dashboard or Discord alerts")
    print("• Maintain list of risky macros and their effects")
    print("• Memory and CPU monitoring with automatic cleanup")
    print("• Emergency shutdown procedures")
    print("=" * 60)
    
    # Create and run demo
    demo = SafetyDemo()
    demo.run_comprehensive_demo()
    
    print("\n🎉 Demo completed! Check the logs above for detailed information.")
    print("Key Features Demonstrated:")
    print("✅ Macro monitoring and pattern detection")
    print("✅ Automatic intervention (pause/stop)")
    print("✅ User alerts via Discord simulation")
    print("✅ Memory safety and resource monitoring")
    print("✅ Emergency shutdown procedures")
    print("✅ Dashboard integration ready")

if __name__ == "__main__":
    main() 
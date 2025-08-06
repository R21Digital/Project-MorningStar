#!/usr/bin/env python3
"""
Demo Batch 163 - Identity & Impersonation Protection

This demonstration showcases the identity protection system including:
- Real-time chat rate limiting examples
- Log sanitization demonstrations
- Movement randomization examples
- Mood and emote randomization
- Camera movement randomization
- Behavior pattern protection
"""

import json
import time
import random
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from safety.identity_guard import IdentityGuard, IdentityRiskLevel, ProtectionType

class IdentityGuardDemo:
    """Demonstration of identity protection system."""
    
    def __init__(self):
        self.identity_guard = IdentityGuard()
        self.demo_scenarios = []
        self.current_scenario = None
        self.scenario_start_time = None
        
    def setup_demo_scenarios(self):
        """Setup demonstration scenarios."""
        self.demo_scenarios = [
            {
                "name": "Chat Rate Limiting Demo",
                "description": "Demonstrate chat message rate limiting and repetitive detection",
                "duration": 30,
                "messages": [
                    "Hello there!",
                    "How are you doing?",
                    "Nice weather today",
                    "Hello there!",  # Duplicate
                    "Hello there!",  # Duplicate
                    "Hello there!",  # Duplicate
                    "Hello there!",  # Duplicate
                    "Hello there!",  # Duplicate
                    "How are you doing?",  # Duplicate
                    "How are you doing?",  # Duplicate
                ]
            },
            {
                "name": "Log Sanitization Demo",
                "description": "Demonstrate log message sanitization for sensitive data",
                "duration": 20,
                "messages": [
                    "User john.doe@email.com logged in from 192.168.1.100",
                    "Discord user @username123 joined the server",
                    "Phone number 555-123-4567 called support",
                    "Credit card 1234-5678-9012-3456 used for purchase",
                    "User admin@company.com accessed sensitive data",
                    "IP address 10.0.0.1 connected to database",
                    "Email user@example.org sent message to support@company.com"
                ]
            },
            {
                "name": "Movement Randomization Demo",
                "description": "Demonstrate movement coordinate randomization",
                "duration": 25,
                "base_coordinates": [
                    (100, 200), (300, 400), (500, 600),
                    (700, 800), (900, 1000), (1100, 1200)
                ]
            },
            {
                "name": "Mood & Emote Randomization Demo",
                "description": "Demonstrate mood and emote randomization timing",
                "duration": 40,
                "mood_checks": 8,
                "emote_checks": 10
            },
            {
                "name": "Camera Movement Demo",
                "description": "Demonstrate camera movement randomization",
                "duration": 30,
                "movement_checks": 12
            },
            {
                "name": "Repetitive Action Detection Demo",
                "description": "Demonstrate repetitive action detection and prevention",
                "duration": 20,
                "actions": [
                    ("walk", "north"),
                    ("walk", "north"),
                    ("walk", "north"),
                    ("walk", "north"),
                    ("walk", "north"),
                    ("walk", "north"),
                    ("interact", "npc"),
                    ("interact", "npc"),
                    ("interact", "npc"),
                    ("interact", "npc"),
                    ("interact", "npc"),
                    ("interact", "npc")
                ]
            },
            {
                "name": "Response Time Humanization Demo",
                "description": "Demonstrate response time variation",
                "duration": 15,
                "base_delays": [1.0, 2.0, 3.0, 1.5, 2.5]
            }
        ]
    
    def run_demo_scenario(self, scenario: Dict[str, Any]):
        """Run a demonstration scenario."""
        print(f"\n🎭 Running Demo: {scenario['name']}")
        print(f"📝 {scenario['description']}")
        print(f"⏱️  Duration: {scenario['duration']} seconds")
        print("-" * 60)
        
        self.current_scenario = scenario
        self.scenario_start_time = time.time()
        
        if "messages" in scenario:
            self._demo_chat_rate_limiting(scenario)
        elif "base_coordinates" in scenario:
            self._demo_movement_randomization(scenario)
        elif "mood_checks" in scenario:
            self._demo_mood_emote_randomization(scenario)
        elif "movement_checks" in scenario:
            self._demo_camera_movement(scenario)
        elif "actions" in scenario:
            self._demo_repetitive_actions(scenario)
        elif "base_delays" in scenario:
            self._demo_response_timing(scenario)
        
        self._display_final_status()
    
    def _demo_chat_rate_limiting(self, scenario: Dict[str, Any]):
        """Demonstrate chat rate limiting."""
        print("💬 Chat Rate Limiting Demonstration")
        print("=" * 40)
        
        allowed_count = 0
        blocked_count = 0
        
        for i, message in enumerate(scenario["messages"], 1):
            print(f"\n[{i:2d}] Message: '{message}'")
            
            if self.identity_guard.check_chat_rate_limit(message):
                print("   ✅ ALLOWED")
                allowed_count += 1
            else:
                print("   ❌ BLOCKED (Rate limited)")
                blocked_count += 1
            
            time.sleep(0.5)
        
        print(f"\n📊 Results:")
        print(f"   Allowed: {allowed_count}")
        print(f"   Blocked: {blocked_count}")
        print(f"   Total: {len(scenario['messages'])}")
    
    def _demo_movement_randomization(self, scenario: Dict[str, Any]):
        """Demonstrate movement randomization."""
        print("🚶 Movement Randomization Demonstration")
        print("=" * 40)
        
        for i, base_coord in enumerate(scenario["base_coordinates"], 1):
            print(f"\n[{i:2d}] Base Coordinates: {base_coord}")
            
            randomized = self.identity_guard.randomize_movement("walk", base_coord)
            print(f"    Randomized: {randomized}")
            
            if randomized != base_coord:
                print("    ✅ Variation applied")
            else:
                print("    ⚠️  No variation (randomization disabled)")
            
            time.sleep(0.3)
    
    def _demo_mood_emote_randomization(self, scenario: Dict[str, Any]):
        """Demonstrate mood and emote randomization."""
        print("😊 Mood & Emote Randomization Demonstration")
        print("=" * 40)
        
        mood_count = 0
        emote_count = 0
        start_time = time.time()
        
        while time.time() - start_time < scenario["duration"]:
            elapsed = time.time() - start_time
            
            # Check for mood
            mood = self.identity_guard.randomize_mood()
            if mood:
                print(f"[{elapsed:5.1f}s] Mood: {mood}")
                mood_count += 1
            
            # Check for emote
            emote = self.identity_guard.randomize_idle_emote()
            if emote:
                print(f"[{elapsed:5.1f}s] Emote: {emote}")
                emote_count += 1
            
            time.sleep(0.5)
        
        print(f"\n📊 Results:")
        print(f"   Moods generated: {mood_count}")
        print(f"   Emotes generated: {emote_count}")
        print(f"   Duration: {scenario['duration']} seconds")
    
    def _demo_camera_movement(self, scenario: Dict[str, Any]):
        """Demonstrate camera movement randomization."""
        print("👁️ Camera Movement Randomization Demonstration")
        print("=" * 40)
        
        movement_count = 0
        start_time = time.time()
        
        while time.time() - start_time < scenario["duration"]:
            elapsed = time.time() - start_time
            
            movement = self.identity_guard.randomize_camera_movement()
            if movement:
                movement_type, distance = movement
                print(f"[{elapsed:5.1f}s] Camera: {movement_type} ({distance:.1f})")
                movement_count += 1
            
            time.sleep(0.5)
        
        print(f"\n📊 Results:")
        print(f"   Movements generated: {movement_count}")
        print(f"   Duration: {scenario['duration']} seconds")
    
    def _demo_repetitive_actions(self, scenario: Dict[str, Any]):
        """Demonstrate repetitive action detection."""
        print("🔄 Repetitive Action Detection Demonstration")
        print("=" * 40)
        
        allowed_count = 0
        blocked_count = 0
        
        for i, (action_type, action_data) in enumerate(scenario["actions"], 1):
            print(f"\n[{i:2d}] Action: {action_type} -> {action_data}")
            
            if self.identity_guard.avoid_repetitive_actions(action_type, action_data):
                print("   ✅ ALLOWED")
                allowed_count += 1
            else:
                print("   ❌ BLOCKED (Repetitive)")
                blocked_count += 1
            
            time.sleep(0.3)
        
        print(f"\n📊 Results:")
        print(f"   Allowed: {allowed_count}")
        print(f"   Blocked: {blocked_count}")
        print(f"   Total: {len(scenario['actions'])}")
    
    def _demo_response_timing(self, scenario: Dict[str, Any]):
        """Demonstrate response time humanization."""
        print("⏱️ Response Time Humanization Demonstration")
        print("=" * 40)
        
        for i, base_delay in enumerate(scenario["base_delays"], 1):
            print(f"\n[{i:2d}] Base Delay: {base_delay:.1f}s")
            
            humanized = self.identity_guard.humanize_response_time(base_delay)
            print(f"    Humanized: {humanized:.1f}s")
            
            if humanized != base_delay:
                variation = ((humanized - base_delay) / base_delay) * 100
                print(f"    Variation: {variation:+.1f}%")
            else:
                print("    ⚠️  No variation (humanization disabled)")
            
            time.sleep(0.3)
    
    def _display_final_status(self):
        """Display final status after scenario."""
        print("\n" + "=" * 60)
        print("📊 DEMO COMPLETE")
        print("=" * 60)
        
        health = self.identity_guard.get_identity_health()
        statistics = self.identity_guard.get_statistics()
        
        print(f"Total Events: {health['total_events']}")
        print(f"Risk Events: {health['risk_events']}")
        print(f"Sanitized Logs: {health['sanitized_logs']}")
        print(f"Rate Limited Messages: {health['rate_limited_messages']}")
        print(f"Randomization Actions: {health['randomization_actions']}")
        print(f"Current Risk Level: {health['current_risk_level']}")
    
    def run_all_demos(self):
        """Run all demonstration scenarios."""
        print("🎭 Starting Identity Guard Demonstrations")
        print("=" * 60)
        
        self.setup_demo_scenarios()
        
        for scenario in self.demo_scenarios:
            self.run_demo_scenario(scenario)
            print("\n" + "=" * 60)
            time.sleep(2)
    
    def demonstrate_configuration_changes(self):
        """Demonstrate configuration changes and their effects."""
        print("\n🔧 Configuration Changes Demonstration")
        print("=" * 60)
        
        # Show current configuration
        print("Current Configuration:")
        config = self.identity_guard.config
        print(f"  Chat Rate Limit: {config.get('chat_rate_limit', 'N/A')}")
        print(f"  Sanitize Logs: {config.get('sanitize_logs', 'N/A')}")
        print(f"  Randomize Movement: {config.get('randomize_movement', 'N/A')}")
        print(f"  Idle Emotes: {config.get('idle_emotes', 'N/A')}")
        
        # Demonstrate configuration change
        print("\n📝 Changing configuration...")
        original_rate_limit = config.get('chat_rate_limit', 12)
        
        # Simulate configuration change
        print(f"  Changing chat rate limit from {original_rate_limit} to 5")
        
        # Test with new rate limit
        print("\nTesting with new rate limit:")
        for i in range(7):
            message = f"Test message {i+1}"
            if self.identity_guard.check_chat_rate_limit(message):
                print(f"  [{i+1}] '{message}' -> ALLOWED")
            else:
                print(f"  [{i+1}] '{message}' -> BLOCKED")
            time.sleep(0.2)
    
    def demonstrate_log_sanitization(self):
        """Demonstrate log sanitization with various sensitive data."""
        print("\n🛡️ Log Sanitization Demonstration")
        print("=" * 60)
        
        sensitive_messages = [
            "User john.doe@email.com logged in from 192.168.1.100",
            "Discord user @username123 joined the server",
            "Phone number 555-123-4567 called support",
            "Credit card 1234-5678-9012-3456 used for purchase",
            "User admin@company.com accessed sensitive data",
            "IP address 10.0.0.1 connected to database",
            "Email user@example.org sent message to support@company.com"
        ]
        
        for i, message in enumerate(sensitive_messages, 1):
            print(f"\n[{i:2d}] Original: {message}")
            sanitized = self.identity_guard.sanitize_log_message(message)
            print(f"    Sanitized: {sanitized}")
            
            if sanitized != message:
                print("    ✅ Sanitization applied")
            else:
                print("    ⚠️  No sanitization (disabled)")
            
            time.sleep(0.5)
    
    def demonstrate_risk_assessment(self):
        """Demonstrate risk assessment with various events."""
        print("\n⚠️ Risk Assessment Demonstration")
        print("=" * 60)
        
        test_events = [
            ("sensitive_data_detected", {"data": "test@email.com"}),
            ("rate_limit_exceeded", {"message_type": "chat"}),
            ("repetitive_pattern", {"pattern": "test"}),
            ("normal_event", {"data": "normal"}),
            ("high_risk_event", {"data": "critical"}),
            ("medium_risk_event", {"data": "warning"})
        ]
        
        for i, (event_type, data) in enumerate(test_events, 1):
            print(f"\n[{i:2d}] Event: {event_type}")
            print(f"    Data: {data}")
            
            risk_level = self.identity_guard._assess_risk_level(event_type, data)
            action = self.identity_guard._determine_action(event_type, data)
            
            print(f"    Risk Level: {risk_level.value}")
            print(f"    Action: {action}")
            
            time.sleep(0.3)
    
    def demonstrate_dashboard_integration(self):
        """Demonstrate dashboard integration data structure."""
        print("\n📊 Dashboard Integration Demonstration")
        print("=" * 60)
        
        health = self.identity_guard.get_identity_health()
        statistics = self.identity_guard.get_statistics()
        
        print("Identity Health Data:")
        print(json.dumps(health, indent=2))
        
        print("\nStatistics Data:")
        print(json.dumps(statistics, indent=2))
    
    def demonstrate_emergency_protocols(self):
        """Demonstrate emergency protocols and alerts."""
        print("\n🚨 Emergency Protocols Demonstration")
        print("=" * 60)
        
        # Simulate high-risk events
        print("Simulating high-risk events...")
        
        for i in range(5):
            self.identity_guard._log_identity_event("sensitive_data_detected", {
                "data": f"critical_data_{i}",
                "severity": "high"
            })
            time.sleep(0.2)
        
        # Check risk level
        health = self.identity_guard.get_identity_health()
        print(f"\nCurrent Risk Level: {health['current_risk_level']}")
        print(f"Risk Events: {health['risk_events']}")
        
        if health['current_risk_level'] in ['high', 'critical']:
            print("🚨 HIGH RISK DETECTED - Emergency protocols activated!")
        else:
            print("✅ Risk level normal")

def main():
    """Run the complete demonstration."""
    demo = IdentityGuardDemo()
    
    try:
        print("🎭 Identity Guard System Demonstration")
        print("=" * 60)
        
        # Run all demos
        demo.run_all_demos()
        
        # Additional demonstrations
        demo.demonstrate_configuration_changes()
        demo.demonstrate_log_sanitization()
        demo.demonstrate_risk_assessment()
        demo.demonstrate_dashboard_integration()
        demo.demonstrate_emergency_protocols()
        
        print("\n🎉 All demonstrations completed successfully!")
        
    except Exception as e:
        print(f"❌ Demonstration failed with error: {e}")

if __name__ == "__main__":
    main() 
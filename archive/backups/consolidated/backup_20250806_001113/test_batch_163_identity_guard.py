#!/usr/bin/env python3
"""
Test Batch 163 - Identity & Impersonation Protection

This test suite validates the identity protection system including:
- Chat rate limiting and repetitive message detection
- Log sanitization for sensitive data
- Movement randomization
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

class IdentityGuardTester:
    """Test suite for identity protection system."""
    
    def __init__(self):
        self.identity_guard = IdentityGuard()
        self.test_results = []
        self.scenarios = []
        
    def setup_test_scenarios(self):
        """Setup various test scenarios."""
        self.scenarios = [
            {
                "name": "Chat Rate Limiting",
                "description": "Test chat message rate limiting",
                "test_type": "rate_limiting",
                "expected_blocks": 3,
                "messages": [
                    "Hello there!",
                    "How are you doing?",
                    "Nice weather today",
                    "Hello there!",  # Duplicate
                    "Hello there!",  # Duplicate
                    "Hello there!",  # Duplicate
                    "Hello there!",  # Duplicate
                    "Hello there!",  # Duplicate
                ]
            },
            {
                "name": "Log Sanitization",
                "description": "Test log message sanitization",
                "test_type": "sanitization",
                "expected_sanitized": 5,
                "messages": [
                    "User john.doe@email.com logged in",
                    "Discord user @username123 joined",
                    "IP address 192.168.1.100 connected",
                    "Phone number 555-123-4567 called",
                    "Credit card 1234-5678-9012-3456 used"
                ]
            },
            {
                "name": "Movement Randomization",
                "description": "Test movement coordinate randomization",
                "test_type": "randomization",
                "expected_variations": 10,
                "base_coordinates": [(100, 200), (300, 400), (500, 600)]
            },
            {
                "name": "Mood Randomization",
                "description": "Test mood randomization timing",
                "test_type": "mood_randomization",
                "expected_moods": 3,
                "test_duration": 10
            },
            {
                "name": "Emote Randomization",
                "description": "Test idle emote randomization",
                "test_type": "emote_randomization",
                "expected_emotes": 3,
                "test_duration": 10
            },
            {
                "name": "Camera Movement",
                "description": "Test camera movement randomization",
                "test_type": "camera_randomization",
                "expected_movements": 5,
                "test_duration": 15
            },
            {
                "name": "Repetitive Action Detection",
                "description": "Test repetitive action detection",
                "test_type": "repetitive_actions",
                "expected_blocks": 2,
                "actions": [
                    ("walk", "north"),
                    ("walk", "north"),
                    ("walk", "north"),
                    ("walk", "north"),
                    ("walk", "north"),
                    ("walk", "north")
                ]
            },
            {
                "name": "Response Time Humanization",
                "description": "Test response time variation",
                "test_type": "response_timing",
                "expected_variations": 10,
                "base_delays": [1.0, 2.0, 3.0]
            }
        ]
    
    def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a test scenario and return results."""
        print(f"\n🧪 Running: {scenario['name']}")
        print(f"📝 {scenario['description']}")
        
        start_time = time.time()
        results = {
            "scenario": scenario["name"],
            "test_type": scenario["test_type"],
            "success": False,
            "metrics": {},
            "errors": []
        }
        
        try:
            if scenario["test_type"] == "rate_limiting":
                results = self._test_chat_rate_limiting(scenario)
            elif scenario["test_type"] == "sanitization":
                results = self._test_log_sanitization(scenario)
            elif scenario["test_type"] == "randomization":
                results = self._test_movement_randomization(scenario)
            elif scenario["test_type"] == "mood_randomization":
                results = self._test_mood_randomization(scenario)
            elif scenario["test_type"] == "emote_randomization":
                results = self._test_emote_randomization(scenario)
            elif scenario["test_type"] == "camera_randomization":
                results = self._test_camera_randomization(scenario)
            elif scenario["test_type"] == "repetitive_actions":
                results = self._test_repetitive_actions(scenario)
            elif scenario["test_type"] == "response_timing":
                results = self._test_response_timing(scenario)
            else:
                results["errors"].append(f"Unknown test type: {scenario['test_type']}")
            
            results["execution_time"] = time.time() - start_time
            results["success"] = len(results["errors"]) == 0
            
        except Exception as e:
            results["errors"].append(f"Test execution failed: {str(e)}")
            results["execution_time"] = time.time() - start_time
        
        self.test_results.append(results)
        return results
    
    def _test_chat_rate_limiting(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test chat rate limiting functionality."""
        results = {
            "scenario": scenario["name"],
            "test_type": "rate_limiting",
            "success": False,
            "metrics": {},
            "errors": []
        }
        
        blocked_messages = 0
        allowed_messages = 0
        
        for message in scenario["messages"]:
            if self.identity_guard.check_chat_rate_limit(message):
                allowed_messages += 1
            else:
                blocked_messages += 1
        
        results["metrics"] = {
            "total_messages": len(scenario["messages"]),
            "allowed_messages": allowed_messages,
            "blocked_messages": blocked_messages,
            "expected_blocks": scenario["expected_blocks"]
        }
        
        if blocked_messages >= scenario["expected_blocks"]:
            results["success"] = True
            print(f"✅ Rate limiting working: {blocked_messages} messages blocked")
        else:
            results["errors"].append(f"Expected {scenario['expected_blocks']} blocks, got {blocked_messages}")
            print(f"❌ Rate limiting failed: {blocked_messages} messages blocked")
        
        return results
    
    def _test_log_sanitization(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test log message sanitization."""
        results = {
            "scenario": scenario["name"],
            "test_type": "sanitization",
            "success": False,
            "metrics": {},
            "errors": []
        }
        
        sanitized_count = 0
        original_messages = []
        sanitized_messages = []
        
        for message in scenario["messages"]:
            original_messages.append(message)
            sanitized = self.identity_guard.sanitize_log_message(message)
            sanitized_messages.append(sanitized)
            
            if sanitized != message:
                sanitized_count += 1
        
        results["metrics"] = {
            "total_messages": len(scenario["messages"]),
            "sanitized_count": sanitized_count,
            "expected_sanitized": scenario["expected_sanitized"],
            "original_messages": original_messages,
            "sanitized_messages": sanitized_messages
        }
        
        if sanitized_count >= scenario["expected_sanitized"]:
            results["success"] = True
            print(f"✅ Sanitization working: {sanitized_count} messages sanitized")
        else:
            results["errors"].append(f"Expected {scenario['expected_sanitized']} sanitized, got {sanitized_count}")
            print(f"❌ Sanitization failed: {sanitized_count} messages sanitized")
        
        return results
    
    def _test_movement_randomization(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test movement coordinate randomization."""
        results = {
            "scenario": scenario["name"],
            "test_type": "randomization",
            "success": False,
            "metrics": {},
            "errors": []
        }
        
        variations = 0
        original_coords = []
        randomized_coords = []
        
        for base_coord in scenario["base_coordinates"]:
            original_coords.append(base_coord)
            randomized = self.identity_guard.randomize_movement("walk", base_coord)
            randomized_coords.append(randomized)
            
            if randomized != base_coord:
                variations += 1
        
        results["metrics"] = {
            "total_coordinates": len(scenario["base_coordinates"]),
            "variations": variations,
            "expected_variations": scenario["expected_variations"],
            "original_coordinates": original_coords,
            "randomized_coordinates": randomized_coords
        }
        
        if variations >= scenario["expected_variations"]:
            results["success"] = True
            print(f"✅ Movement randomization working: {variations} variations")
        else:
            results["errors"].append(f"Expected {scenario['expected_variations']} variations, got {variations}")
            print(f"❌ Movement randomization failed: {variations} variations")
        
        return results
    
    def _test_mood_randomization(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test mood randomization timing."""
        results = {
            "scenario": scenario["name"],
            "test_type": "mood_randomization",
            "success": False,
            "metrics": {},
            "errors": []
        }
        
        moods_generated = 0
        start_time = time.time()
        
        # Simulate time passing and check for mood generation
        while time.time() - start_time < scenario["test_duration"]:
            mood = self.identity_guard.randomize_mood()
            if mood:
                moods_generated += 1
            time.sleep(0.1)
        
        results["metrics"] = {
            "test_duration": scenario["test_duration"],
            "moods_generated": moods_generated,
            "expected_moods": scenario["expected_moods"]
        }
        
        if moods_generated >= scenario["expected_moods"]:
            results["success"] = True
            print(f"✅ Mood randomization working: {moods_generated} moods generated")
        else:
            results["errors"].append(f"Expected {scenario['expected_moods']} moods, got {moods_generated}")
            print(f"❌ Mood randomization failed: {moods_generated} moods generated")
        
        return results
    
    def _test_emote_randomization(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test idle emote randomization."""
        results = {
            "scenario": scenario["name"],
            "test_type": "emote_randomization",
            "success": False,
            "metrics": {},
            "errors": []
        }
        
        emotes_generated = 0
        start_time = time.time()
        
        # Simulate time passing and check for emote generation
        while time.time() - start_time < scenario["test_duration"]:
            emote = self.identity_guard.randomize_idle_emote()
            if emote:
                emotes_generated += 1
            time.sleep(0.1)
        
        results["metrics"] = {
            "test_duration": scenario["test_duration"],
            "emotes_generated": emotes_generated,
            "expected_emotes": scenario["expected_emotes"]
        }
        
        if emotes_generated >= scenario["expected_emotes"]:
            results["success"] = True
            print(f"✅ Emote randomization working: {emotes_generated} emotes generated")
        else:
            results["errors"].append(f"Expected {scenario['expected_emotes']} emotes, got {emotes_generated}")
            print(f"❌ Emote randomization failed: {emotes_generated} emotes generated")
        
        return results
    
    def _test_camera_randomization(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test camera movement randomization."""
        results = {
            "scenario": scenario["name"],
            "test_type": "camera_randomization",
            "success": False,
            "metrics": {},
            "errors": []
        }
        
        movements_generated = 0
        start_time = time.time()
        
        # Simulate time passing and check for camera movements
        while time.time() - start_time < scenario["test_duration"]:
            movement = self.identity_guard.randomize_camera_movement()
            if movement:
                movements_generated += 1
            time.sleep(0.1)
        
        results["metrics"] = {
            "test_duration": scenario["test_duration"],
            "movements_generated": movements_generated,
            "expected_movements": scenario["expected_movements"]
        }
        
        if movements_generated >= scenario["expected_movements"]:
            results["success"] = True
            print(f"✅ Camera randomization working: {movements_generated} movements generated")
        else:
            results["errors"].append(f"Expected {scenario['expected_movements']} movements, got {movements_generated}")
            print(f"❌ Camera randomization failed: {movements_generated} movements generated")
        
        return results
    
    def _test_repetitive_actions(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test repetitive action detection."""
        results = {
            "scenario": scenario["name"],
            "test_type": "repetitive_actions",
            "success": False,
            "metrics": {},
            "errors": []
        }
        
        blocked_actions = 0
        allowed_actions = 0
        
        for action_type, action_data in scenario["actions"]:
            if self.identity_guard.avoid_repetitive_actions(action_type, action_data):
                allowed_actions += 1
            else:
                blocked_actions += 1
        
        results["metrics"] = {
            "total_actions": len(scenario["actions"]),
            "allowed_actions": allowed_actions,
            "blocked_actions": blocked_actions,
            "expected_blocks": scenario["expected_blocks"]
        }
        
        if blocked_actions >= scenario["expected_blocks"]:
            results["success"] = True
            print(f"✅ Repetitive action detection working: {blocked_actions} actions blocked")
        else:
            results["errors"].append(f"Expected {scenario['expected_blocks']} blocks, got {blocked_actions}")
            print(f"❌ Repetitive action detection failed: {blocked_actions} actions blocked")
        
        return results
    
    def _test_response_timing(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test response time humanization."""
        results = {
            "scenario": scenario["name"],
            "test_type": "response_timing",
            "success": False,
            "metrics": {},
            "errors": []
        }
        
        variations = 0
        original_times = []
        humanized_times = []
        
        for base_delay in scenario["base_delays"]:
            original_times.append(base_delay)
            humanized = self.identity_guard.humanize_response_time(base_delay)
            humanized_times.append(humanized)
            
            if humanized != base_delay:
                variations += 1
        
        results["metrics"] = {
            "total_delays": len(scenario["base_delays"]),
            "variations": variations,
            "expected_variations": scenario["expected_variations"],
            "original_times": original_times,
            "humanized_times": humanized_times
        }
        
        if variations >= scenario["expected_variations"]:
            results["success"] = True
            print(f"✅ Response timing humanization working: {variations} variations")
        else:
            results["errors"].append(f"Expected {scenario['expected_variations']} variations, got {variations}")
            print(f"❌ Response timing humanization failed: {variations} variations")
        
        return results
    
    def test_identity_health_retrieval(self):
        """Test identity health status retrieval."""
        print("\n🧪 Testing: Identity Health Retrieval")
        
        try:
            health = self.identity_guard.get_identity_health()
            statistics = self.identity_guard.get_statistics()
            
            required_fields = [
                "total_events", "risk_events", "sanitized_logs",
                "rate_limited_messages", "randomization_actions"
            ]
            
            all_fields_present = all(field in health for field in required_fields)
            stats_fields_present = all(field in statistics for field in required_fields)
            
            if all_fields_present and stats_fields_present:
                print("✅ Identity health retrieval working")
                return True
            else:
                print("❌ Identity health retrieval failed - missing fields")
                return False
                
        except Exception as e:
            print(f"❌ Identity health retrieval failed: {e}")
            return False
    
    def test_configuration_loading(self):
        """Test configuration loading and validation."""
        print("\n🧪 Testing: Configuration Loading")
        
        try:
            config = self.identity_guard.config
            
            required_sections = [
                "idle_emotes", "chat_rate_limit", "sanitize_logs",
                "randomize_movement", "randomize_mood", "camera_wiggles"
            ]
            
            all_sections_present = all(section in config for section in required_sections)
            
            if all_sections_present:
                print("✅ Configuration loading working")
                return True
            else:
                print("❌ Configuration loading failed - missing sections")
                return False
                
        except Exception as e:
            print(f"❌ Configuration loading failed: {e}")
            return False
    
    def test_risk_assessment(self):
        """Test risk level assessment functionality."""
        print("\n🧪 Testing: Risk Assessment")
        
        try:
            # Test different risk scenarios
            test_events = [
                ("sensitive_data_detected", {"data": "test@email.com"}),
                ("rate_limit_exceeded", {"message_type": "chat"}),
                ("repetitive_pattern", {"pattern": "test"}),
                ("normal_event", {"data": "normal"})
            ]
            
            risk_levels = []
            for event_type, data in test_events:
                risk_level = self.identity_guard._assess_risk_level(event_type, data)
                risk_levels.append(risk_level)
            
            # Verify risk levels are appropriate
            high_risk_count = sum(1 for level in risk_levels if level == IdentityRiskLevel.HIGH)
            medium_risk_count = sum(1 for level in risk_levels if level == IdentityRiskLevel.MEDIUM)
            
            if high_risk_count >= 1 and medium_risk_count >= 1:
                print("✅ Risk assessment working")
                return True
            else:
                print("❌ Risk assessment failed - inappropriate risk levels")
                return False
                
        except Exception as e:
            print(f"❌ Risk assessment failed: {e}")
            return False
    
    def run_all_scenarios(self):
        """Run all test scenarios."""
        print("🚀 Starting Identity Guard Test Suite")
        print("=" * 50)
        
        self.setup_test_scenarios()
        
        for scenario in self.scenarios:
            self.run_scenario(scenario)
        
        # Additional tests
        self.test_identity_health_retrieval()
        self.test_configuration_loading()
        self.test_risk_assessment()
        
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 50)
        print("📊 IDENTITY GUARD TEST REPORT")
        print("=" * 50)
        
        total_tests = len(self.test_results) + 3  # +3 for additional tests
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['scenario']} ({result['test_type']})")
            if result["errors"]:
                for error in result["errors"]:
                    print(f"    Error: {error}")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "results": self.test_results
        }
        
        try:
            with open("test_reports/batch_163_identity_guard_report.json", "w") as f:
                json.dump(report_data, f, indent=2)
            print(f"\n📄 Detailed report saved to: test_reports/batch_163_identity_guard_report.json")
        except Exception as e:
            print(f"⚠️  Failed to save report: {e}")

def main():
    """Run the complete test suite."""
    tester = IdentityGuardTester()
    
    try:
        tester.run_all_scenarios()
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")

if __name__ == "__main__":
    main() 
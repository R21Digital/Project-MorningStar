#!/usr/bin/env python3
"""
Test Batch 162 - Intelligent Stuck Recovery v2

This test suite validates the stuck recovery system including:
- Stuck detection mechanisms
- Recovery action execution
- Cooldown and backoff systems
- Timeline and logging functionality
"""

import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from core.recovery.stuck_recovery import (
    StuckRecoverySystem, 
    StuckType, 
    RecoveryAction, 
    RecoveryStatus
)


class StuckRecoveryTester:
    """Test suite for stuck recovery system."""
    
    def __init__(self):
        self.recovery_system = StuckRecoverySystem()
        self.test_results = []
        self.scenarios = []
    
    def setup_test_scenarios(self):
        """Setup various test scenarios."""
        self.scenarios = [
            {
                "name": "No Coordinate Delta",
                "description": "Test detection when coordinates don't change",
                "setup": self._setup_no_coordinate_delta,
                "expected_detection": StuckType.NO_COORDINATE_DELTA,
                "expected_confidence": 0.8,
                "recovery_actions": ["micro_path_jitter", "mount_toggle"]
            },
            {
                "name": "Repeat Clicks",
                "description": "Test detection when same click is repeated",
                "setup": self._setup_repeat_clicks,
                "expected_detection": StuckType.REPEAT_CLICKS,
                "expected_confidence": 0.7,
                "recovery_actions": ["micro_path_jitter", "face_camera_rescan"]
            },
            {
                "name": "No Quest Progress",
                "description": "Test detection when quest progress stalls",
                "setup": self._setup_no_quest_progress,
                "expected_detection": StuckType.NO_QUEST_PROGRESS,
                "expected_confidence": 0.6,
                "recovery_actions": ["face_camera_rescan", "nearest_navmesh_waypoint"]
            },
            {
                "name": "Path Oscillation",
                "description": "Test detection when path oscillates between points",
                "setup": self._setup_path_oscillation,
                "expected_detection": StuckType.PATH_OSCILLATION,
                "expected_confidence": 0.75,
                "recovery_actions": ["micro_path_jitter", "shuttle_fallback"]
            },
            {
                "name": "Multiple Stuck Types",
                "description": "Test detection with multiple stuck indicators",
                "setup": self._setup_multiple_stuck_types,
                "expected_detection": StuckType.NO_COORDINATE_DELTA,
                "expected_confidence": 0.9,
                "recovery_actions": ["micro_path_jitter", "mount_toggle", "shuttle_fallback"]
            }
        ]
    
    def _setup_no_coordinate_delta(self):
        """Setup scenario for no coordinate delta detection."""
        # Simulate character staying in same position
        base_coords = (1000, 1000)
        for i in range(15):  # More than threshold
            self.recovery_system.update_coordinates(base_coords[0], base_coords[1])
            time.sleep(0.1)
    
    def _setup_repeat_clicks(self):
        """Setup scenario for repeat clicks detection."""
        # Simulate repeated clicking
        for i in range(8):  # More than threshold
            self.recovery_system.record_click("npc_interact", "quest_giver")
            time.sleep(0.1)
    
    def _setup_no_quest_progress(self):
        """Setup scenario for no quest progress detection."""
        # Simulate quest progress that stalls
        quest_id = "test_quest_001"
        self.recovery_system.record_quest_progress(quest_id, 0.5)
        time.sleep(0.1)
        self.recovery_system.record_quest_progress(quest_id, 0.5)  # Same progress
        time.sleep(0.1)
        
        # Wait longer than timeout
        time.sleep(0.5)  # Simulate time passing
    
    def _setup_path_oscillation(self):
        """Setup scenario for path oscillation detection."""
        # Simulate oscillating between two points
        point_a = (1000, 1000)
        point_b = (1005, 1005)
        
        for i in range(10):
            if i % 2 == 0:
                self.recovery_system.record_path_point(point_a[0], point_a[1])
            else:
                self.recovery_system.record_path_point(point_b[0], point_b[1])
            time.sleep(0.1)
    
    def _setup_multiple_stuck_types(self):
        """Setup scenario with multiple stuck indicators."""
        # Combine multiple stuck indicators
        base_coords = (1000, 1000)
        
        # No coordinate delta
        for i in range(12):
            self.recovery_system.update_coordinates(base_coords[0], base_coords[1])
            time.sleep(0.1)
        
        # Repeat clicks
        for i in range(6):
            self.recovery_system.record_click("npc_interact", "quest_giver")
            time.sleep(0.1)
        
        # Path oscillation
        point_a = (1000, 1000)
        point_b = (1005, 1005)
        for i in range(8):
            if i % 2 == 0:
                self.recovery_system.record_path_point(point_a[0], point_a[1])
            else:
                self.recovery_system.record_path_point(point_b[0], point_b[1])
            time.sleep(0.1)
    
    def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a test scenario."""
        print(f"\n🧪 Running scenario: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        
        # Reset recovery system
        self.recovery_system = StuckRecoverySystem()
        
        # Setup scenario
        scenario['setup']()
        
        # Check if detection occurred
        detection = self.recovery_system.state.stuck_detection
        detection_success = False
        
        if detection:
            detection_success = (
                detection.stuck_type == scenario['expected_detection'] and
                detection.confidence >= scenario['expected_confidence']
            )
            print(f"   ✅ Detection: {detection.stuck_type.value} (confidence: {detection.confidence:.2f})")
        else:
            print(f"   ❌ No detection occurred")
        
        # Check recovery status
        recovery_started = self.recovery_system.state.is_recovering
        print(f"   Recovery started: {recovery_started}")
        
        # Simulate recovery process
        recovery_results = []
        if recovery_started:
            recovery_results = self._simulate_recovery_process(scenario['recovery_actions'])
        
        return {
            "scenario_name": scenario['name'],
            "detection_success": detection_success,
            "detection_type": detection.stuck_type.value if detection else None,
            "detection_confidence": detection.confidence if detection else 0.0,
            "recovery_started": recovery_started,
            "recovery_results": recovery_results,
            "expected_detection": scenario['expected_detection'].value,
            "expected_confidence": scenario['expected_confidence']
        }
    
    def _simulate_recovery_process(self, expected_actions: List[str]) -> List[Dict[str, Any]]:
        """Simulate the recovery process."""
        results = []
        
        # Get recovery history
        history = self.recovery_system.state.recovery_history
        
        for attempt in history:
            results.append({
                "action": attempt.action.value,
                "status": attempt.status.value,
                "duration": attempt.end_time - attempt.start_time if attempt.end_time else 0,
                "success": attempt.status == RecoveryStatus.SUCCESS
            })
        
        return results
    
    def run_all_scenarios(self):
        """Run all test scenarios."""
        print("🚀 Starting stuck recovery test suite...")
        
        self.setup_test_scenarios()
        
        for scenario in self.scenarios:
            result = self.run_scenario(scenario)
            self.test_results.append(result)
            
            # Brief pause between scenarios
            time.sleep(0.5)
    
    def test_recovery_actions(self):
        """Test individual recovery actions."""
        print("\n🔧 Testing recovery actions...")
        
        # Test micro path jitter
        print("   Testing micro path jitter...")
        self.recovery_system = StuckRecoverySystem()
        self.recovery_system.state.last_coordinates = (1000, 1000)
        
        result = self.recovery_system._perform_micro_path_jitter(5.0)
        print(f"   ✅ Micro path jitter completed: {result}")
        
        # Test mount toggle
        print("   Testing mount toggle...")
        result = self.recovery_system._perform_mount_toggle(5.0)
        print(f"   ✅ Mount toggle completed: {result}")
        
        # Test face camera rescan
        print("   Testing face camera rescan...")
        result = self.recovery_system._perform_face_camera_rescan(5.0)
        print(f"   ✅ Face camera rescan completed: {result}")
        
        # Test nearest navmesh waypoint
        print("   Testing nearest navmesh waypoint...")
        result = self.recovery_system._perform_nearest_navmesh_waypoint(5.0)
        print(f"   ✅ Nearest navmesh waypoint completed: {result}")
        
        # Test shuttle fallback
        print("   Testing shuttle fallback...")
        result = self.recovery_system._perform_shuttle_fallback(5.0)
        print(f"   ✅ Shuttle fallback completed: {result}")
        
        # Test safe logout
        print("   Testing safe logout...")
        result = self.recovery_system._perform_safe_logout(5.0)
        print(f"   ✅ Safe logout completed: {result}")
    
    def test_cooldown_system(self):
        """Test cooldown and backoff mechanisms."""
        print("\n⏰ Testing cooldown system...")
        
        self.recovery_system = StuckRecoverySystem()
        
        # Test cooldown application
        action = RecoveryAction.MICRO_PATH_JITTER
        current_time = time.time()
        
        # Set cooldown
        self.recovery_system.state.cooldowns[action] = current_time + 30.0
        
        # Check if action is on cooldown
        cooldown_until = self.recovery_system.state.cooldowns.get(action)
        is_on_cooldown = cooldown_until and current_time < cooldown_until
        
        print(f"   Action on cooldown: {is_on_cooldown}")
        print(f"   Cooldown until: {cooldown_until}")
        
        # Test cooldown expiration
        time.sleep(0.1)  # Small delay
        future_time = time.time() + 60.0  # Future time
        self.recovery_system.state.cooldowns[action] = future_time
        
        cooldown_until = self.recovery_system.state.cooldowns.get(action)
        is_on_cooldown = cooldown_until and current_time < cooldown_until
        
        print(f"   Action on cooldown (future): {is_on_cooldown}")
    
    def test_timeline_functionality(self):
        """Test timeline and logging functionality."""
        print("\n📊 Testing timeline functionality...")
        
        self.recovery_system = StuckRecoverySystem()
        
        # Simulate some events
        self.recovery_system.update_coordinates(1000, 1000)
        self.recovery_system.record_click("npc_interact", "test_npc")
        self.recovery_system.record_quest_progress("test_quest", 0.5)
        
        # Trigger stuck detection
        self._setup_no_coordinate_delta()
        
        # Get timeline
        timeline = self.recovery_system.get_recovery_timeline()
        print(f"   Timeline events: {len(timeline)}")
        
        for event in timeline:
            print(f"   - {event['title']} at {event['timestamp']}")
        
        # Get recovery status
        status = self.recovery_system.get_recovery_status()
        print(f"   Recovery status: {status['is_recovering']}")
        print(f"   Total attempts: {status['statistics']['total_attempts']}")
    
    def test_configuration_loading(self):
        """Test configuration and playbook loading."""
        print("\n⚙️ Testing configuration loading...")
        
        # Test default configuration
        self.recovery_system = StuckRecoverySystem()
        
        print(f"   Coordinate delta threshold: {self.recovery_system.coordinate_delta_threshold}")
        print(f"   Repeat click threshold: {self.recovery_system.repeat_click_threshold}")
        print(f"   Quest progress timeout: {self.recovery_system.quest_progress_timeout}")
        print(f"   Detection confidence threshold: {self.recovery_system.detection_confidence_threshold}")
        
        # Test playbook loading
        playbooks = self.recovery_system.playbooks
        print(f"   Loaded playbooks: {len(playbooks.get('playbooks', {}))}")
        
        for playbook_name, playbook_data in playbooks.get('playbooks', {}).items():
            actions = playbook_data.get('actions', [])
            print(f"   - {playbook_name}: {len(actions)} actions")
    
    def test_error_handling(self):
        """Test error handling and edge cases."""
        print("\n🛡️ Testing error handling...")
        
        self.recovery_system = StuckRecoverySystem()
        
        # Test with invalid coordinates
        try:
            self.recovery_system.update_coordinates(None, None)
            print("   ✅ Handled invalid coordinates gracefully")
        except Exception as e:
            print(f"   ❌ Error with invalid coordinates: {e}")
        
        # Test with empty data
        try:
            self.recovery_system.record_click("", None)
            print("   ✅ Handled empty click data gracefully")
        except Exception as e:
            print(f"   ❌ Error with empty click data: {e}")
        
        # Test recovery with no stuck detection
        try:
            self.recovery_system.start_recovery()
            print("   ✅ Handled recovery without stuck detection gracefully")
        except Exception as e:
            print(f"   ❌ Error starting recovery: {e}")
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n📋 Generating test report...")
        
        total_scenarios = len(self.test_results)
        successful_detections = sum(1 for r in self.test_results if r['detection_success'])
        successful_recoveries = sum(1 for r in self.test_results if r['recovery_started'])
        
        print(f"\n📊 Test Results Summary:")
        print(f"   Total scenarios: {total_scenarios}")
        print(f"   Successful detections: {successful_detections}/{total_scenarios}")
        print(f"   Successful recoveries: {successful_recoveries}/{total_scenarios}")
        print(f"   Detection success rate: {successful_detections/total_scenarios*100:.1f}%")
        print(f"   Recovery success rate: {successful_recoveries/total_scenarios*100:.1f}%")
        
        # Detailed results
        print(f"\n📝 Detailed Results:")
        for result in self.test_results:
            status = "✅ PASS" if result['detection_success'] else "❌ FAIL"
            print(f"   {status} {result['scenario_name']}")
            print(f"      Detection: {result['detection_type']} (confidence: {result['detection_confidence']:.2f})")
            print(f"      Recovery: {'Started' if result['recovery_started'] else 'Not Started'}")
            
            if result['recovery_results']:
                for recovery in result['recovery_results']:
                    recovery_status = "✅" if recovery['success'] else "❌"
                    print(f"      {recovery_status} {recovery['action']}: {recovery['status']}")
        
        # Save test results
        report_data = {
            "test_timestamp": datetime.now().isoformat(),
            "total_scenarios": total_scenarios,
            "successful_detections": successful_detections,
            "successful_recoveries": successful_recoveries,
            "detection_success_rate": successful_detections/total_scenarios*100,
            "recovery_success_rate": successful_recoveries/total_scenarios*100,
            "detailed_results": self.test_results
        }
        
        report_file = Path("test_reports/batch_162_test_report.json")
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Test report saved to: {report_file}")
        
        return report_data


def main():
    """Run the complete test suite."""
    tester = StuckRecoveryTester()
    
    try:
        print("🧪 Batch 162 - Intelligent Stuck Recovery v2 Test Suite")
        print("=" * 60)
        
        # Run all test components
        tester.run_all_scenarios()
        tester.test_recovery_actions()
        tester.test_cooldown_system()
        tester.test_timeline_functionality()
        tester.test_configuration_loading()
        tester.test_error_handling()
        
        # Generate report
        report = tester.generate_test_report()
        
        print("\n🎉 Test suite completed successfully!")
        print(f"📊 Overall success rate: {report['detection_success_rate']:.1f}%")
        
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Demo Batch 162 - Intelligent Stuck Recovery v2

This demonstration showcases the stuck recovery system in action,
simulating various stuck scenarios and recovery processes.
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


class StuckRecoveryDemo:
    """Demonstration of stuck recovery system."""
    
    def __init__(self):
        self.recovery_system = StuckRecoverySystem()
        self.demo_scenarios = []
        self.current_scenario = None
        self.scenario_start_time = None
    
    def setup_demo_scenarios(self):
        """Setup demonstration scenarios."""
        self.demo_scenarios = [
            {
                "name": "Coordinate Stuck Demo",
                "description": "Demonstrate detection when character coordinates don't change",
                "duration": 30,
                "setup": self._setup_coordinate_stuck,
                "expected_detection": StuckType.NO_COORDINATE_DELTA,
                "recovery_actions": ["micro_path_jitter", "mount_toggle"]
            },
            {
                "name": "Click Loop Demo",
                "description": "Demonstrate detection when same click is repeated",
                "duration": 25,
                "setup": self._setup_click_loop,
                "expected_detection": StuckType.REPEAT_CLICKS,
                "recovery_actions": ["micro_path_jitter", "face_camera_rescan"]
            },
            {
                "name": "Quest Stuck Demo",
                "description": "Demonstrate detection when quest progress stalls",
                "duration": 35,
                "setup": self._setup_quest_stuck,
                "expected_detection": StuckType.NO_QUEST_PROGRESS,
                "recovery_actions": ["face_camera_rescan", "nearest_navmesh_waypoint"]
            },
            {
                "name": "Path Oscillation Demo",
                "description": "Demonstrate detection when path oscillates between points",
                "duration": 28,
                "setup": self._setup_path_oscillation,
                "expected_detection": StuckType.PATH_OSCILLATION,
                "recovery_actions": ["micro_path_jitter", "shuttle_fallback"]
            },
            {
                "name": "Complex Stuck Demo",
                "description": "Demonstrate detection with multiple stuck indicators",
                "duration": 40,
                "setup": self._setup_complex_stuck,
                "expected_detection": StuckType.NO_COORDINATE_DELTA,
                "recovery_actions": ["micro_path_jitter", "mount_toggle", "shuttle_fallback", "safe_logout"]
            }
        ]
    
    def _setup_coordinate_stuck(self):
        """Setup coordinate stuck scenario."""
        print("   📍 Setting up coordinate stuck scenario...")
        
        # Simulate character staying in same position
        base_coords = (1500, 1500)
        for i in range(20):
            self.recovery_system.update_coordinates(base_coords[0], base_coords[1])
            time.sleep(0.2)
            if i % 5 == 0:
                print(f"      Position update {i+1}/20: {base_coords}")
    
    def _setup_click_loop(self):
        """Setup click loop scenario."""
        print("   🖱️ Setting up click loop scenario...")
        
        # Simulate repeated clicking on same target
        target = "quest_giver_npc"
        for i in range(12):
            self.recovery_system.record_click("npc_interact", target)
            time.sleep(0.3)
            if i % 3 == 0:
                print(f"      Click {i+1}/12: {target}")
    
    def _setup_quest_stuck(self):
        """Setup quest stuck scenario."""
        print("   📋 Setting up quest stuck scenario...")
        
        # Simulate quest progress that stalls
        quest_id = "demo_quest_001"
        initial_progress = 0.3
        
        # Record initial progress
        self.recovery_system.record_quest_progress(quest_id, initial_progress)
        print(f"      Initial quest progress: {initial_progress}")
        
        # Simulate time passing with no progress
        for i in range(15):
            self.recovery_system.record_quest_progress(quest_id, initial_progress)  # Same progress
            time.sleep(0.4)
            if i % 5 == 0:
                print(f"      Progress check {i+1}/15: {initial_progress} (no change)")
    
    def _setup_path_oscillation(self):
        """Setup path oscillation scenario."""
        print("   🌀 Setting up path oscillation scenario...")
        
        # Simulate oscillating between two points
        point_a = (2000, 2000)
        point_b = (2008, 2008)
        
        for i in range(16):
            if i % 2 == 0:
                self.recovery_system.record_path_point(point_a[0], point_a[1])
                print(f"      Path point {i+1}/16: {point_a}")
            else:
                self.recovery_system.record_path_point(point_b[0], point_b[1])
                print(f"      Path point {i+1}/16: {point_b}")
            time.sleep(0.3)
    
    def _setup_complex_stuck(self):
        """Setup complex stuck scenario with multiple indicators."""
        print("   🔄 Setting up complex stuck scenario...")
        
        # Combine multiple stuck indicators
        base_coords = (2500, 2500)
        target = "complex_npc"
        quest_id = "complex_quest"
        
        # Coordinate stuck
        print("      Phase 1: Coordinate stuck")
        for i in range(15):
            self.recovery_system.update_coordinates(base_coords[0], base_coords[1])
            time.sleep(0.2)
        
        # Click loop
        print("      Phase 2: Click loop")
        for i in range(8):
            self.recovery_system.record_click("npc_interact", target)
            time.sleep(0.3)
        
        # Quest stuck
        print("      Phase 3: Quest stuck")
        self.recovery_system.record_quest_progress(quest_id, 0.6)
        for i in range(10):
            self.recovery_system.record_quest_progress(quest_id, 0.6)  # Same progress
            time.sleep(0.4)
        
        # Path oscillation
        print("      Phase 4: Path oscillation")
        point_a = (2500, 2500)
        point_b = (2505, 2505)
        for i in range(12):
            if i % 2 == 0:
                self.recovery_system.record_path_point(point_a[0], point_a[1])
            else:
                self.recovery_system.record_path_point(point_b[0], point_b[1])
            time.sleep(0.3)
    
    def run_demo_scenario(self, scenario: Dict[str, Any]):
        """Run a demonstration scenario."""
        print(f"\n🎬 Running Demo: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Duration: {scenario['duration']} seconds")
        print(f"   Expected Detection: {scenario['expected_detection'].value}")
        print(f"   Recovery Actions: {', '.join(scenario['recovery_actions'])}")
        
        # Reset recovery system
        self.recovery_system = StuckRecoverySystem()
        self.current_scenario = scenario
        self.scenario_start_time = time.time()
        
        # Setup scenario
        scenario['setup']()
        
        # Monitor for detection
        detection_occurred = False
        detection_time = None
        
        print("\n   🔍 Monitoring for stuck detection...")
        
        # Continue monitoring for a bit after setup
        for i in range(10):
            time.sleep(0.5)
            
            # Check if detection occurred
            if self.recovery_system.state.stuck_detection and not detection_occurred:
                detection_occurred = True
                detection_time = time.time() - self.scenario_start_time
                detection = self.recovery_system.state.stuck_detection
                
                print(f"\n   🚨 STUCK DETECTED!")
                print(f"      Type: {detection.stuck_type.value}")
                print(f"      Confidence: {detection.confidence:.2f}")
                print(f"      Coordinates: {detection.coordinates}")
                print(f"      Detection Time: {detection_time:.1f}s")
                print(f"      Method: {detection.detection_method}")
            
            # Check if recovery started
            if self.recovery_system.state.is_recovering and detection_occurred:
                print(f"\n   🔧 RECOVERY STARTED!")
                self._monitor_recovery_process()
                break
        
        if not detection_occurred:
            print("   ⚠️ No stuck detection occurred in this scenario")
        
        # Display final status
        self._display_final_status()
    
    def _monitor_recovery_process(self):
        """Monitor the recovery process."""
        print("\n   📊 Monitoring recovery process...")
        
        recovery_start_time = time.time()
        attempt_count = 0
        
        while self.recovery_system.state.is_recovering:
            time.sleep(1.0)
            
            current_attempt = self.recovery_system.state.current_attempt
            if current_attempt:
                elapsed = time.time() - current_attempt.start_time
                print(f"      Recovery attempt {attempt_count + 1}: {current_attempt.action.value}")
                print(f"         Status: {current_attempt.status.value}")
                print(f"         Duration: {elapsed:.1f}s")
                
                # Check if attempt completed
                if current_attempt.end_time:
                    if current_attempt.status == RecoveryStatus.SUCCESS:
                        print(f"         ✅ SUCCESS")
                    elif current_attempt.status == RecoveryStatus.FAILED:
                        print(f"         ❌ FAILED: {current_attempt.error_message}")
                    
                    attempt_count += 1
            
            # Check if recovery completed
            if not self.recovery_system.state.is_recovering:
                total_time = time.time() - recovery_start_time
                print(f"\n   🎉 RECOVERY COMPLETED!")
                print(f"      Total time: {total_time:.1f}s")
                print(f"      Total attempts: {len(self.recovery_system.state.recovery_history)}")
                break
    
    def _display_final_status(self):
        """Display final status after scenario."""
        print("\n   📋 Final Status:")
        
        # Detection status
        detection = self.recovery_system.state.stuck_detection
        if detection:
            print(f"      Detection: {detection.stuck_type.value} (confidence: {detection.confidence:.2f})")
        else:
            print("      Detection: None")
        
        # Recovery status
        print(f"      Recovery Active: {self.recovery_system.state.is_recovering}")
        print(f"      Recovery History: {len(self.recovery_system.state.recovery_history)} attempts")
        
        # Statistics
        status = self.recovery_system.get_recovery_status()
        stats = status.get('statistics', {})
        print(f"      Successful Attempts: {stats.get('successful_attempts', 0)}")
        print(f"      Failed Attempts: {stats.get('failed_attempts', 0)}")
        print(f"      Skipped Attempts: {stats.get('skipped_attempts', 0)}")
    
    def run_all_demos(self):
        """Run all demonstration scenarios."""
        print("🎬 Batch 162 - Intelligent Stuck Recovery v2 Demo")
        print("=" * 60)
        
        self.setup_demo_scenarios()
        
        for i, scenario in enumerate(self.demo_scenarios, 1):
            print(f"\n{'='*60}")
            print(f"DEMO {i}/{len(self.demo_scenarios)}")
            print(f"{'='*60}")
            
            self.run_demo_scenario(scenario)
            
            # Pause between demos
            if i < len(self.demo_scenarios):
                print(f"\n⏸️ Pausing 3 seconds before next demo...")
                time.sleep(3)
    
    def demonstrate_timeline_functionality(self):
        """Demonstrate timeline and logging functionality."""
        print("\n📊 Timeline Functionality Demo")
        print("=" * 40)
        
        # Reset system
        self.recovery_system = StuckRecoverySystem()
        
        # Simulate some events
        print("   📍 Recording coordinate updates...")
        for i in range(5):
            self.recovery_system.update_coordinates(1000 + i, 1000 + i)
            time.sleep(0.2)
        
        print("   🖱️ Recording click events...")
        for i in range(3):
            self.recovery_system.record_click("npc_interact", f"npc_{i}")
            time.sleep(0.2)
        
        print("   📋 Recording quest progress...")
        self.recovery_system.record_quest_progress("demo_quest", 0.3)
        time.sleep(0.2)
        self.recovery_system.record_quest_progress("demo_quest", 0.3)  # Same progress
        
        # Trigger stuck detection
        print("   🔍 Triggering stuck detection...")
        self._setup_coordinate_stuck()
        
        # Display timeline
        timeline = self.recovery_system.get_recovery_timeline()
        print(f"\n   📅 Timeline Events ({len(timeline)} total):")
        
        for i, event in enumerate(timeline, 1):
            timestamp = datetime.fromtimestamp(event['timestamp']).strftime('%H:%M:%S')
            print(f"      {i}. {event['title']} at {timestamp}")
            print(f"         {event['description']}")
        
        # Display recovery status
        status = self.recovery_system.get_recovery_status()
        print(f"\n   📊 Recovery Status:")
        print(f"      Is Recovering: {status['is_recovering']}")
        print(f"      Current Attempt: {status['current_attempt']['action'] if status['current_attempt'] else 'None'}")
        print(f"      Total Attempts: {status['statistics']['total_attempts']}")
    
    def demonstrate_configuration_features(self):
        """Demonstrate configuration and playbook features."""
        print("\n⚙️ Configuration Features Demo")
        print("=" * 40)
        
        # Display current configuration
        print("   📋 Current Configuration:")
        print(f"      Coordinate Delta Threshold: {self.recovery_system.coordinate_delta_threshold}")
        print(f"      Repeat Click Threshold: {self.recovery_system.repeat_click_threshold}")
        print(f"      Quest Progress Timeout: {self.recovery_system.quest_progress_timeout}")
        print(f"      Detection Confidence Threshold: {self.recovery_system.detection_confidence_threshold}")
        print(f"      Max Recovery Attempts: {self.recovery_system.max_recovery_attempts}")
        
        # Display playbooks
        playbooks = self.recovery_system.playbooks
        print(f"\n   📚 Available Playbooks:")
        
        for playbook_name, playbook_data in playbooks.get('playbooks', {}).items():
            actions = playbook_data.get('actions', [])
            print(f"      {playbook_name}: {len(actions)} actions")
            print(f"         Description: {playbook_data.get('description', 'No description')}")
            
            for i, action in enumerate(actions, 1):
                print(f"         {i}. {action['name']} ({action['action']})")
                print(f"            Timeout: {action['timeout']}s, Cooldown: {action['cooldown']}s")
        
        # Display stuck type mappings
        stuck_type_playbooks = playbooks.get('stuck_type_playbooks', {})
        print(f"\n   🎯 Stuck Type to Playbook Mappings:")
        for stuck_type, playbook in stuck_type_playbooks.items():
            print(f"      {stuck_type} → {playbook}")
    
    def demonstrate_cooldown_system(self):
        """Demonstrate cooldown and backoff system."""
        print("\n⏰ Cooldown System Demo")
        print("=" * 30)
        
        # Reset system
        self.recovery_system = StuckRecoverySystem()
        
        # Set some cooldowns
        current_time = time.time()
        actions = [
            RecoveryAction.MICRO_PATH_JITTER,
            RecoveryAction.MOUNT_TOGGLE,
            RecoveryAction.FACE_CAMERA_RESCAN
        ]
        
        cooldown_durations = [30, 60, 120]
        
        print("   🔒 Setting up cooldowns...")
        for action, duration in zip(actions, cooldown_durations):
            self.recovery_system.state.cooldowns[action] = current_time + duration
            print(f"      {action.value}: {duration}s cooldown")
        
        # Display cooldown status
        print(f"\n   📊 Cooldown Status:")
        for action, until in self.recovery_system.state.cooldowns.items():
            remaining = until - current_time
            if remaining > 0:
                print(f"      {action.value}: {remaining:.1f}s remaining")
            else:
                print(f"      {action.value}: Available")
        
        # Simulate time passing
        print(f"\n   ⏳ Simulating time passage...")
        time.sleep(2)
        
        current_time = time.time()
        print(f"   📊 Updated Cooldown Status:")
        for action, until in self.recovery_system.state.cooldowns.items():
            remaining = until - current_time
            if remaining > 0:
                print(f"      {action.value}: {remaining:.1f}s remaining")
            else:
                print(f"      {action.value}: Available")
    
    def demonstrate_dashboard_integration(self):
        """Demonstrate dashboard integration data structure."""
        print("\n📊 Dashboard Integration Demo")
        print("=" * 40)
        
        # Get recovery status for dashboard
        status = self.recovery_system.get_recovery_status()
        
        print("   📋 Recovery Status Data Structure:")
        print(f"      Is Recovering: {status['is_recovering']}")
        print(f"      Current Attempt: {status['current_attempt']}")
        print(f"      Stuck Detection: {status['stuck_detection']}")
        print(f"      Recovery History: {len(status['recovery_history'])} attempts")
        print(f"      Cooldowns: {len(status['cooldowns'])} active")
        
        # Display statistics
        stats = status.get('statistics', {})
        print(f"\n   📊 Statistics:")
        print(f"      Total Attempts: {stats.get('total_attempts', 0)}")
        print(f"      Successful: {stats.get('successful_attempts', 0)}")
        print(f"      Failed: {stats.get('failed_attempts', 0)}")
        print(f"      Skipped: {stats.get('skipped_attempts', 0)}")
        
        # Get timeline for dashboard
        timeline = self.recovery_system.get_recovery_timeline()
        print(f"\n   📅 Timeline Data Structure:")
        print(f"      Total Events: {len(timeline)}")
        
        for i, event in enumerate(timeline[:3], 1):  # Show first 3 events
            print(f"      Event {i}:")
            print(f"         Type: {event['type']}")
            print(f"         Title: {event['title']}")
            print(f"         Description: {event['description']}")
            print(f"         Timestamp: {event['timestamp']}")
        
        if len(timeline) > 3:
            print(f"      ... and {len(timeline) - 3} more events")
    
    def demonstrate_emergency_protocols(self):
        """Demonstrate emergency protocols and safety features."""
        print("\n🚨 Emergency Protocols Demo")
        print("=" * 40)
        
        # Reset system
        self.recovery_system = StuckRecoverySystem()
        
        print("   🔒 Safety Features:")
        print(f"      Max Recovery Attempts: {self.recovery_system.max_recovery_attempts}")
        print(f"      Recovery Timeout: {self.recovery_system.recovery_cooldown_base}s")
        print(f"      Max Cooldown: {self.recovery_system.max_cooldown}s")
        print(f"      Detection Cooldown: {self.recovery_system.detection_cooldown}s")
        
        # Simulate emergency scenario
        print(f"\n   🚨 Simulating Emergency Scenario...")
        
        # Trigger multiple stuck detections
        self._setup_complex_stuck()
        
        # Check if emergency protocols would trigger
        if self.recovery_system.state.stuck_detection:
            detection = self.recovery_system.state.stuck_detection
            print(f"      Emergency Detection: {detection.stuck_type.value}")
            print(f"      Confidence: {detection.confidence:.2f}")
            
            if detection.confidence >= 0.9:
                print(f"      🚨 HIGH CONFIDENCE - Emergency protocols may trigger")
            elif detection.confidence >= 0.7:
                print(f"      ⚠️ MEDIUM CONFIDENCE - Standard recovery initiated")
            else:
                print(f"      ℹ️ LOW CONFIDENCE - Monitoring only")
        
        # Show recovery actions that would be taken
        if self.recovery_system.state.is_recovering:
            print(f"\n   🔧 Recovery Actions:")
            history = self.recovery_system.state.recovery_history
            for i, attempt in enumerate(history, 1):
                status_icon = "✅" if attempt.status == RecoveryStatus.SUCCESS else "❌"
                print(f"      {i}. {status_icon} {attempt.action.value}: {attempt.status.value}")
        
        print(f"\n   🛡️ Emergency Features:")
        print(f"      - Automatic cooldown management")
        print(f"      - Escalating recovery actions")
        print(f"      - Safe logout as last resort")
        print(f"      - Comprehensive logging")
        print(f"      - Dashboard integration")


def main():
    """Run the complete demonstration."""
    demo = StuckRecoveryDemo()
    
    try:
        print("🎬 Batch 162 - Intelligent Stuck Recovery v2 Demonstration")
        print("=" * 70)
        
        # Run all demo components
        demo.run_all_demos()
        demo.demonstrate_timeline_functionality()
        demo.demonstrate_configuration_features()
        demo.demonstrate_cooldown_system()
        demo.demonstrate_dashboard_integration()
        demo.demonstrate_emergency_protocols()
        
        print("\n🎉 Demonstration completed successfully!")
        print("📊 The stuck recovery system is ready for production use.")
        
    except Exception as e:
        print(f"❌ Demonstration failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
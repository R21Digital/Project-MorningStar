#!/usr/bin/env python3
"""
Demo Batch 168 - T-Unit (BH) PvP Phase 2

This demo showcases the T-Unit BH PvP Phase 2 functionality including:
- Target acquisition from mission terminal → triangulation heuristics
- Range & LoS management; burst windows; escape path on counter-gank
- Strict safety checks: disable in high-risk policy, cooldowns between hunts
- Logs integrate with Seasonal BH Leaderboard (Batch 144)
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta

# Import the T-Unit BH PvP mode
from modes.tunit_bh_pvp import (
    TUnitBHPvP, PvPTarget, HuntSession, PvPTargetType, 
    HuntStatus, SafetyLevel
)


def create_sample_terminal_text() -> str:
    """Create sample BH terminal text for PvP targets."""
    return """
    BOUNTY HUNTER TERMINAL - MOS EISLEY (PvP TARGETS)
    
    Available PvP Missions:
    OvertPlayer 100,200 1500m 1000c
    TEFTarget 300,400 2000m 1500c
    EnemyPlayer 500,600 2500m 2000c
    GCWTarget 700,800 3000m 2500c
    HostilePlayer 900,1000 3500m 3000c
    """


def create_sample_targets() -> List[PvPTarget]:
    """Create sample PvP targets for demonstration."""
    return [
        PvPTarget(
            name="OvertPlayer",
            target_type=PvPTargetType.OVERT,
            location={
                "planet": "tatooine",
                "city": "mos_eisley",
                "coordinates": [100, 200],
                "zone": "cantina",
                "confidence": 0.8,
                "last_update": datetime.now().isoformat(),
                "triangulation": {
                    "base_location": [100, 200],
                    "confidence": 0.8,
                    "signal_strength": 0.85,
                    "predicted_path": [[100, 200], [120, 220], [140, 240]]
                }
            },
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        ),
        PvPTarget(
            name="TEFTarget",
            target_type=PvPTargetType.TEF_FLAGGED,
            location={
                "planet": "dantooine",
                "city": "imperial_outpost",
                "coordinates": [300, 400],
                "zone": "outskirts",
                "confidence": 0.7,
                "last_update": datetime.now().isoformat(),
                "triangulation": {
                    "base_location": [300, 400],
                    "confidence": 0.7,
                    "signal_strength": 0.75,
                    "predicted_path": [[300, 400], [320, 420], [340, 440]]
                }
            },
            difficulty="hard",
            reward_credits=1500,
            risk_level=SafetyLevel.DANGER,
            last_seen=datetime.now()
        ),
        PvPTarget(
            name="GCWTarget",
            target_type=PvPTargetType.GCW_TARGET,
            location={
                "planet": "naboo",
                "city": "theed",
                "coordinates": [700, 800],
                "zone": "palace_grounds",
                "confidence": 0.75,
                "last_update": datetime.now().isoformat(),
                "triangulation": {
                    "base_location": [700, 800],
                    "confidence": 0.75,
                    "signal_strength": 0.8,
                    "predicted_path": [[700, 800], [720, 820], [740, 840]]
                }
            },
            difficulty="hard",
            reward_credits=2500,
            risk_level=SafetyLevel.DANGER,
            last_seen=datetime.now()
        )
    ]


def demo_target_acquisition(tunit: TUnitBHPvP) -> None:
    """Demonstrate target acquisition from mission terminal."""
    print("\n" + "="*60)
    print("🎯 DEMO: Target Acquisition from Mission Terminal")
    print("="*60)
    
    # Create sample terminal text
    terminal_text = create_sample_terminal_text()
    print(f"Terminal Text:\n{terminal_text}")
    
    # Acquire targets
    targets = tunit.acquire_targets_from_terminal(terminal_text)
    
    print(f"\nAcquired Targets: {len(targets)}")
    for i, target in enumerate(targets, 1):
        print(f"\n{i}. {target.name}")
        print(f"   Type: {target.target_type.value}")
        print(f"   Location: {target.location.get('coordinates', 'Unknown')}")
        print(f"   Difficulty: {target.difficulty}")
        print(f"   Reward: {target.reward_credits} credits")
        print(f"   Risk Level: {target.risk_level.value}")
        print(f"   Confidence: {target.location.get('confidence', 0):.2f}")
        
        if target.triangulation_data:
            print(f"   Triangulation Data:")
            print(f"     Signal Strength: {target.triangulation_data.get('signal_strength', 0):.2f}")
            print(f"     Predicted Path: {len(target.triangulation_data.get('predicted_path', []))} points")


def demo_safety_assessment(tunit: TUnitBHPvP) -> None:
    """Demonstrate safety assessment functionality."""
    print("\n" + "="*60)
    print("🛡️ DEMO: Safety Assessment")
    print("="*60)
    
    # Test different safety scenarios
    scenarios = [
        ("Safe Zone", {"players": [], "zone_risk": 0.2, "recent_activity": False}),
        ("Caution Zone", {"players": [{"hostile": False}] * 6, "zone_risk": 0.5, "recent_activity": False}),
        ("Danger Zone", {"players": [{"hostile": True}] * 8, "zone_risk": 0.8, "recent_activity": True}),
        ("Critical Zone", {"players": [{"hostile": True}] * 12, "zone_risk": 0.9, "recent_activity": True})
    ]
    
    for scenario_name, scenario_data in scenarios:
        print(f"\n--- {scenario_name} ---")
        
        # Simulate the assessment manually
        risk_score = 0.0
        if len(scenario_data["players"]) > 10:
            risk_score += 0.3
        elif len(scenario_data["players"]) > 5:
            risk_score += 0.2
        
        if scenario_data["zone_risk"] > 0.7:
            risk_score += 0.4
        elif scenario_data["zone_risk"] > 0.4:
            risk_score += 0.2
        
        if scenario_data["recent_activity"]:
            risk_score += 0.2
        
        # Determine safety level based on risk score
        if risk_score >= 0.8:
            safety_level = SafetyLevel.CRITICAL
        elif risk_score >= 0.6:
            safety_level = SafetyLevel.DANGER
        elif risk_score >= 0.4:
            safety_level = SafetyLevel.CAUTION
        else:
            safety_level = SafetyLevel.SAFE
        
        print(f"Calculated Risk Score: {risk_score:.2f}")
        print(f"Safety Level: {safety_level.value}")
        print(f"Mode Enabled: {tunit.is_enabled()}")


def demo_hunt_cycle(tunit: TUnitBHPvP) -> None:
    """Demonstrate a complete hunt cycle."""
    print("\n" + "="*60)
    print("🎯 DEMO: Complete Hunt Cycle")
    print("="*60)
    
    # Create sample target
    target = PvPTarget(
        name="DemoTarget",
        target_type=PvPTargetType.OVERT,
        location={
            "planet": "tatooine",
            "city": "mos_eisley",
            "coordinates": [100, 200],
            "zone": "cantina",
            "confidence": 0.8,
            "last_update": datetime.now().isoformat(),
            "triangulation": {
                "base_location": [100, 200],
                "confidence": 0.8,
                "signal_strength": 0.85,
                "predicted_path": [[100, 200], [120, 220], [140, 240]]
            }
        },
        difficulty="medium",
        reward_credits=1000,
        risk_level=SafetyLevel.CAUTION,
        last_seen=datetime.now()
    )
    
    print(f"Target: {target.name}")
    print(f"Type: {target.target_type.value}")
    print(f"Location: {target.location.get('coordinates', 'Unknown')}")
    print(f"Reward: {target.reward_credits} credits")
    print(f"Risk Level: {target.risk_level.value}")
    
    # Step 1: Start Hunt
    print(f"\n--- Step 1: Starting Hunt ---")
    hunt_success = tunit.start_hunt(target)
    print(f"Hunt Started: {hunt_success}")
    
    if hunt_success:
        print(f"Active Hunt: {tunit.active_hunt is not None}")
        print(f"Hunt Status: {tunit.active_hunt.status.value}")
        print(f"Escape Path Length: {len(tunit.active_hunt.escape_path)}")
        
        # Step 2: Range and LoS Management
        print(f"\n--- Step 2: Range and LoS Management ---")
        range_data = tunit.manage_range_and_los()
        print(f"Status: {range_data['status']}")
        print(f"Action: {range_data['action']}")
        print(f"Current Distance: {range_data['current_distance']:.1f}")
        print(f"Optimal Range: {range_data['optimal_range']:.1f}")
        print(f"Line of Sight: {range_data['line_of_sight']}")
        
        # Step 3: Burst Window Management
        print(f"\n--- Step 3: Burst Window Management ---")
        burst_data = tunit.manage_burst_windows()
        print(f"Status: {burst_data['status']}")
        print(f"Available Bursts: {burst_data['available_bursts']}")
        print(f"Can Create Burst: {burst_data['can_create_burst']}")
        print(f"Total Bursts: {burst_data['total_bursts']}")
        
        # Step 4: Counter-Gank Detection
        print(f"\n--- Step 4: Counter-Gank Detection ---")
        counter_gank_data = tunit.handle_counter_gank()
        print(f"Status: {counter_gank_data['status']}")
        print(f"Counter-Gank Detected: {counter_gank_data['counter_gank_detected']}")
        
        if counter_gank_data.get('escape_success') is not None:
            print(f"Escape Success: {counter_gank_data['escape_success']}")
        
        # Step 5: Complete Hunt
        print(f"\n--- Step 5: Completing Hunt ---")
        completion_success = tunit.complete_hunt(success=True)
        print(f"Hunt Completed: {completion_success}")
        print(f"Active Hunt: {tunit.active_hunt is None}")
        print(f"Hunt History Length: {len(tunit.hunt_history)}")
        print(f"Cooldown Until: {tunit.cooldown_until}")


def demo_triangulation_heuristics(tunit: TUnitBHPvP) -> None:
    """Demonstrate triangulation heuristics."""
    print("\n" + "="*60)
    print("📍 DEMO: Triangulation Heuristics")
    print("="*60)
    
    # Sample target data
    target_data = {
        "name": "OvertPlayer",
        "coordinates": [100, 200],
        "distance": 1500,
        "reward_credits": 1000
    }
    
    print(f"Original Target Data:")
    print(f"  Name: {target_data['name']}")
    print(f"  Coordinates: {target_data['coordinates']}")
    print(f"  Distance: {target_data['distance']}m")
    print(f"  Reward: {target_data['reward_credits']}c")
    
    # Apply triangulation heuristics
    triangulated_location = tunit._apply_triangulation_heuristics(target_data)
    
    if triangulated_location:
        print(f"\nTriangulated Location:")
        print(f"  Planet: {triangulated_location.get('planet', 'Unknown')}")
        print(f"  Coordinates: {triangulated_location.get('coordinates', 'Unknown')}")
        print(f"  Confidence: {triangulated_location.get('confidence', 0):.2f}")
        print(f"  Last Update: {triangulated_location.get('last_update', 'Unknown')}")
        
        triangulation_data = triangulated_location.get('triangulation', {})
        print(f"\nTriangulation Details:")
        print(f"  Base Location: {triangulation_data.get('base_location', 'Unknown')}")
        print(f"  Confidence: {triangulation_data.get('confidence', 0):.2f}")
        print(f"  Signal Strength: {triangulation_data.get('signal_strength', 0):.2f}")
        print(f"  Predicted Path Points: {len(triangulation_data.get('predicted_path', []))}")
    else:
        print(f"\nTriangulation failed - confidence below threshold")


def demo_escape_planning(tunit: TUnitBHPvP) -> None:
    """Demonstrate escape path planning."""
    print("\n" + "="*60)
    print("🏃 DEMO: Escape Path Planning")
    print("="*60)
    
    # Create sample target for hunt
    target = PvPTarget(
        name="EscapeDemoTarget",
        target_type=PvPTargetType.OVERT,
        location={
            "planet": "tatooine",
            "city": "mos_eisley",
            "coordinates": [100, 200],
            "zone": "cantina"
        },
        difficulty="medium",
        reward_credits=1000,
        risk_level=SafetyLevel.CAUTION,
        last_seen=datetime.now()
    )
    
    # Start hunt to trigger escape planning
    hunt_success = tunit.start_hunt(target)
    
    if hunt_success and tunit.active_hunt:
        print(f"Hunt started for: {target.name}")
        print(f"Escape Path Planned: {len(tunit.active_hunt.escape_path)} waypoints")
        
        for i, waypoint in enumerate(tunit.active_hunt.escape_path, 1):
            print(f"\nWaypoint {i}:")
            print(f"  Location: {waypoint['location']}")
            print(f"  Type: {waypoint['type']}")
            print(f"  Distance: {waypoint['distance']}m")
            print(f"  Risk Level: {waypoint['risk_level']}")
        
        # Complete hunt
        tunit.complete_hunt(success=True)


def demo_leaderboard_integration(tunit: TUnitBHPvP) -> None:
    """Demonstrate leaderboard integration."""
    print("\n" + "="*60)
    print("🏆 DEMO: Leaderboard Integration (Batch 144)")
    print("="*60)
    
    # Create sample targets for multiple hunts
    targets = [
        PvPTarget(
            name="LeaderboardTarget1",
            target_type=PvPTargetType.OVERT,
            location={"coordinates": [100, 200]},
            difficulty="medium",
            reward_credits=1000,
            risk_level=SafetyLevel.CAUTION,
            last_seen=datetime.now()
        ),
        PvPTarget(
            name="LeaderboardTarget2",
            target_type=PvPTargetType.TEF_FLAGGED,
            location={"coordinates": [300, 400]},
            difficulty="hard",
            reward_credits=1500,
            risk_level=SafetyLevel.DANGER,
            last_seen=datetime.now()
        ),
        PvPTarget(
            name="LeaderboardTarget3",
            target_type=PvPTargetType.GCW_TARGET,
            location={"coordinates": [500, 600]},
            difficulty="hard",
            reward_credits=2500,
            risk_level=SafetyLevel.DANGER,
            last_seen=datetime.now()
        )
    ]
    
    print(f"Simulating {len(targets)} hunts for leaderboard integration...")
    
    for i, target in enumerate(targets, 1):
        print(f"\n--- Hunt {i}: {target.name} ---")
        
        # Start hunt
        hunt_success = tunit.start_hunt(target)
        if hunt_success:
            print(f"  Hunt started successfully")
            print(f"  Target Type: {target.target_type.value}")
            print(f"  Reward: {target.reward_credits} credits")
            print(f"  Risk Level: {target.risk_level.value}")
            
            # Simulate hunt duration
            time.sleep(0.1)  # Simulate hunt time
            
            # Complete hunt with random success
            import random
            success = random.choice([True, True, True, False])  # 75% success rate
            completion_success = tunit.complete_hunt(success=success)
            
            print(f"  Hunt completed: {completion_success}")
            print(f"  Success: {success}")
            print(f"  Duration: {(datetime.now() - tunit.hunt_history[-1].start_time).seconds}s")
        else:
            print(f"  Hunt failed to start")
    
    print(f"\nTotal Hunts in History: {len(tunit.hunt_history)}")
    print(f"Successful Hunts: {sum(1 for hunt in tunit.hunt_history if hunt.status == HuntStatus.COMPLETED)}")
    print(f"Failed Hunts: {sum(1 for hunt in tunit.hunt_history if hunt.status == HuntStatus.FAILED)}")
    
    # Check if leaderboard data was created
    leaderboard_file = Path("data/bh/leaderboard_data.json")
    if leaderboard_file.exists():
        print(f"\nLeaderboard data file created: {leaderboard_file}")
        with leaderboard_file.open("r") as f:
            leaderboard_data = json.load(f)
        print(f"Total hunts logged: {len(leaderboard_data.get('hunts', []))}")
    else:
        print(f"\nLeaderboard data file not found (expected for demo)")


def demo_configuration_options(tunit: TUnitBHPvP) -> None:
    """Demonstrate configuration options."""
    print("\n" + "="*60)
    print("⚙️ DEMO: Configuration Options")
    print("="*60)
    
    print(f"Current Configuration:")
    print(f"  Enabled: {tunit.config.get('enabled', False)}")
    print(f"  Opt-in Required: {tunit.config.get('opt_in_required', True)}")
    
    safety_settings = tunit.config.get('safety_settings', {})
    print(f"\nSafety Settings:")
    print(f"  Max Risk Level: {safety_settings.get('max_risk_level', 'unknown')}")
    print(f"  Cooldown Between Hunts: {safety_settings.get('cooldown_between_hunts', 0)}s")
    print(f"  Max Hunt Duration: {safety_settings.get('max_hunt_duration', 0)}s")
    print(f"  Emergency Escape Threshold: {safety_settings.get('emergency_escape_threshold', 0)}")
    print(f"  Disable in High Risk: {safety_settings.get('disable_in_high_risk', False)}")
    
    target_acquisition = tunit.config.get('target_acquisition', {})
    print(f"\nTarget Acquisition:")
    print(f"  Mission Terminal Enabled: {target_acquisition.get('mission_terminal_enabled', False)}")
    print(f"  Triangulation Heuristics: {target_acquisition.get('triangulation_heuristics', False)}")
    print(f"  Max Tracking Distance: {target_acquisition.get('max_tracking_distance', 0)}m")
    print(f"  Min Target Confidence: {target_acquisition.get('min_target_confidence', 0)}")
    
    combat_settings = tunit.config.get('combat_settings', {})
    print(f"\nCombat Settings:")
    print(f"  Range Management: {combat_settings.get('range_management', False)}")
    print(f"  Line of Sight Check: {combat_settings.get('line_of_sight_check', False)}")
    print(f"  Burst Window Duration: {combat_settings.get('burst_window_duration', 0)}s")
    print(f"  Burst Window Cooldown: {combat_settings.get('burst_window_cooldown', 0)}s")
    print(f"  Escape Path Planning: {combat_settings.get('escape_path_planning', False)}")
    print(f"  Counter-Gank Response: {combat_settings.get('counter_gank_response', False)}")
    
    logging_settings = tunit.config.get('logging_settings', {})
    print(f"\nLogging Settings:")
    print(f"  Integrate with Leaderboard: {logging_settings.get('integrate_with_leaderboard', False)}")
    print(f"  Log Hunt Details: {logging_settings.get('log_hunt_details', False)}")
    print(f"  Log Safety Checks: {logging_settings.get('log_safety_checks', False)}")
    print(f"  Log Triangulation Data: {logging_settings.get('log_triangulation_data', False)}")
    print(f"  Leaderboard Batch 144: {logging_settings.get('leaderboard_batch_144', False)}")
    
    discord_alerts = tunit.config.get('discord_alerts', {})
    print(f"\nDiscord Alerts:")
    print(f"  Enabled: {discord_alerts.get('enabled', False)}")
    print(f"  Alert Types: {discord_alerts.get('alert_types', [])}")
    print(f"  Include Risk Level: {discord_alerts.get('include_risk_level', False)}")
    print(f"  Include Rewards: {discord_alerts.get('include_rewards', False)}")


def demo_target_signals(tunit: TUnitBHPvP) -> None:
    """Demonstrate target signals configuration."""
    print("\n" + "="*60)
    print("📡 DEMO: Target Signals Configuration")
    print("="*60)
    
    signal_patterns = tunit.target_signals.get('signal_patterns', {})
    print(f"Signal Patterns:")
    
    for target_type, pattern in signal_patterns.items():
        print(f"\n{target_type.upper()}:")
        print(f"  Confidence Threshold: {pattern.get('confidence_threshold', 0):.2f}")
        print(f"  Refresh Rate: {pattern.get('refresh_rate', 0)}s")
        print(f"  Location Accuracy: {pattern.get('location_accuracy', 0):.2f}")
        print(f"  Detection Range: {pattern.get('detection_range', 0)}m")
        print(f"  Signal Strength Multiplier: {pattern.get('signal_strength_multiplier', 0):.2f}")
        print(f"  Priority Level: {pattern.get('priority_level', 'unknown')}")
        
        risk_assessment = pattern.get('risk_assessment', {})
        print(f"  Risk Assessment:")
        print(f"    Base Risk: {risk_assessment.get('base_risk', 0):.2f}")
        print(f"    Distance Factor: {risk_assessment.get('distance_factor', 0):.2f}")
        print(f"    Reward Factor: {risk_assessment.get('reward_factor', 0):.2f}")
        print(f"    Zone Factor: {risk_assessment.get('zone_factor', 0):.2f}")
    
    triangulation_heuristics = tunit.target_signals.get('triangulation_heuristics', {})
    print(f"\nTriangulation Heuristics:")
    print(f"  Max Distance: {triangulation_heuristics.get('max_distance', 0)}m")
    print(f"  Min Confidence: {triangulation_heuristics.get('min_confidence', 0):.2f}")
    print(f"  Location Update Interval: {triangulation_heuristics.get('location_update_interval', 0)}s")
    print(f"  Path Prediction: {triangulation_heuristics.get('path_prediction', False)}")
    print(f"  Zone Analysis: {triangulation_heuristics.get('zone_analysis', False)}")


def main() -> None:
    """Main demo function."""
    print("🎯 T-Unit (BH) PvP Phase 2 - Demo")
    print("="*60)
    print("Mature Bounty Hunter mode for PvP targets (opt-in, off by default)")
    print("="*60)
    
    # Initialize T-Unit BH PvP
    print("\nInitializing T-Unit BH PvP...")
    tunit = TUnitBHPvP()
    
    # Enable mode for demo
    tunit.config["enabled"] = True
    tunit.safety_level = SafetyLevel.SAFE
    
    # Check if mode is enabled
    print(f"Mode Enabled: {tunit.is_enabled()}")
    print(f"Safety Level: {tunit.safety_level.value}")
    
    # Run demos
    demo_target_acquisition(tunit)
    demo_safety_assessment(tunit)
    demo_triangulation_heuristics(tunit)
    demo_escape_planning(tunit)
    demo_hunt_cycle(tunit)
    demo_leaderboard_integration(tunit)
    demo_configuration_options(tunit)
    demo_target_signals(tunit)
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("✅ Target acquisition from mission terminal → triangulation heuristics")
    print("✅ Range & LoS management; burst windows; escape path on counter-gank")
    print("✅ Strict safety checks: disable in high-risk policy, cooldowns between hunts")
    print("✅ Logs integrate with Seasonal BH Leaderboard (Batch 144)")
    print("\nSafety Features:")
    print("✅ Opt-in required (disabled by default)")
    print("✅ Automatic risk assessment and safety level management")
    print("✅ Cooldown periods between hunts")
    print("✅ Escape path planning for emergency situations")
    print("✅ Counter-gank detection and response")
    print("✅ Discord alerts for hunt events")
    print("✅ Comprehensive logging and leaderboard integration")


if __name__ == "__main__":
    main() 
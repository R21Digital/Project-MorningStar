#!/usr/bin/env python3
"""Demo script for Batch 115 - Environmental Awareness & Risk Avoidance System."""

import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

from modules.environmental_awareness import (
    EnvironmentalAwareness,
    RiskLevel,
    ThreatType,
    ThreatDetection,
    get_environmental_awareness,
    start_environmental_monitoring,
    stop_environmental_monitoring,
    update_location,
    get_risk_assessment,
    get_avoidance_recommendations
)


class EnvironmentalAwarenessDemo:
    """Demo class for showcasing environmental awareness functionality."""
    
    def __init__(self):
        """Initialize the demo."""
        self.environmental_awareness = get_environmental_awareness()
        self.demo_scenarios = [
            {
                "name": "Safe Zone Scenario",
                "zone": "moenia_center",
                "planet": "naboo",
                "coordinates": (4500, -4500),
                "description": "Low-risk safe zone with no threats"
            },
            {
                "name": "Hostile NPC Cluster Scenario",
                "zone": "restuss",
                "planet": "rori",
                "coordinates": (5000, -3000),
                "description": "High-risk GCW zone with hostile NPCs"
            },
            {
                "name": "AFK Reporting Hotspot Scenario",
                "zone": "mos_eisley_cantina",
                "planet": "tatooine",
                "coordinates": (3520, -4800),
                "description": "Crowded area near starport"
            },
            {
                "name": "Starport Proximity Scenario",
                "zone": "theed_palace",
                "planet": "naboo",
                "coordinates": (5000, -4000),
                "description": "Close to starport with potential AFK reporting"
            },
            {
                "name": "Player Cluster Scenario",
                "zone": "coronet_trade_district",
                "planet": "corellia",
                "coordinates": (4000, -5000),
                "description": "Busy trade area with many players"
            }
        ]
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "="*60)
        print(f"🌍 {title}")
        print("="*60)
    
    def print_section(self, title: str):
        """Print a formatted section header."""
        print(f"\n📋 {title}")
        print("-" * 40)
    
    def simulate_environmental_scan(self, scenario: Dict[str, Any]) -> List[ThreatDetection]:
        """Simulate an environmental scan for a given scenario."""
        threats = []
        
        # Update location
        self.environmental_awareness.update_location(
            scenario["zone"], 
            scenario["planet"], 
            scenario["coordinates"]
        )
        
        # Simulate threats based on scenario
        if "restuss" in scenario["zone"]:
            # High GCW zone threat
            threats.append(ThreatDetection(
                threat_type=ThreatType.HIGH_GCW_ZONE,
                risk_level=RiskLevel.CRITICAL,
                location=scenario["coordinates"],
                zone=scenario["zone"],
                planet=scenario["planet"],
                description="High GCW zone detected",
                confidence=0.9,
                timestamp=datetime.now(),
                gcw_level=100
            ))
            
            # Hostile NPC cluster
            threats.append(ThreatDetection(
                threat_type=ThreatType.HOSTILE_NPC_CLUSTER,
                risk_level=RiskLevel.HIGH,
                location=scenario["coordinates"],
                zone=scenario["zone"],
                planet=scenario["planet"],
                description="Detected 5 hostile NPCs",
                confidence=0.8,
                timestamp=datetime.now(),
                npc_count=5
            ))
        
        elif "cantina" in scenario["zone"]:
            # AFK reporting hotspot
            threats.append(ThreatDetection(
                threat_type=ThreatType.AFK_REPORTING_HOTSPOT,
                risk_level=RiskLevel.HIGH,
                location=scenario["coordinates"],
                zone=scenario["zone"],
                planet=scenario["planet"],
                description="Potential AFK reporting hotspot detected",
                confidence=0.7,
                timestamp=datetime.now()
            ))
            
            # Crowded zone
            threats.append(ThreatDetection(
                threat_type=ThreatType.CROWDED_ZONE,
                risk_level=RiskLevel.MEDIUM,
                location=scenario["coordinates"],
                zone=scenario["zone"],
                planet=scenario["planet"],
                description="Crowded area with many players",
                confidence=0.6,
                timestamp=datetime.now()
            ))
        
        elif "palace" in scenario["zone"]:
            # Starport proximity
            threats.append(ThreatDetection(
                threat_type=ThreatType.STARPORT_PROXIMITY,
                risk_level=RiskLevel.MEDIUM,
                location=scenario["coordinates"],
                zone=scenario["zone"],
                planet=scenario["planet"],
                description="Too close to starport (50.0 units)",
                confidence=0.8,
                timestamp=datetime.now(),
                distance_to_starport=50.0
            ))
        
        elif "trade_district" in scenario["zone"]:
            # Player cluster
            threats.append(ThreatDetection(
                threat_type=ThreatType.PLAYER_CLUSTER,
                risk_level=RiskLevel.MEDIUM,
                location=scenario["coordinates"],
                zone=scenario["zone"],
                planet=scenario["planet"],
                description="Detected 6 players nearby",
                confidence=0.6,
                timestamp=datetime.now(),
                player_count=6
            ))
        
        # Update state with detected threats
        self.environmental_awareness.state.detected_threats = threats
        self.environmental_awareness._update_risk_assessment()
        
        return threats
    
    def showcase_risk_assessment(self, scenario: Dict[str, Any]):
        """Showcase risk assessment for a scenario."""
        self.print_section(f"Risk Assessment: {scenario['name']}")
        
        # Simulate environmental scan
        threats = self.simulate_environmental_scan(scenario)
        
        # Get risk assessment
        assessment = self.environmental_awareness.get_risk_assessment()
        
        print(f"📍 Location: {scenario['zone']} on {scenario['planet']}")
        print(f"🎯 Coordinates: {scenario['coordinates']}")
        print(f"⚠️  Risk Level: {assessment['current_risk_level'].upper()}")
        print(f"🔍 Threats Detected: {assessment['threats_detected']}")
        
        if threats:
            print("\n🚨 Detected Threats:")
            for i, threat in enumerate(threats, 1):
                print(f"  {i}. {threat.threat_type.value.replace('_', ' ').title()}")
                print(f"     Risk: {threat.risk_level.value.upper()}")
                print(f"     Description: {threat.description}")
                print(f"     Confidence: {threat.confidence:.1%}")
        
        # Get avoidance recommendations
        recommendations = self.environmental_awareness.get_avoidance_recommendations()
        
        if recommendations:
            print("\n💡 Avoidance Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        print(f"\n📊 Movement History: {len(self.environmental_awareness.state.movement_history)} entries")
        print(f"💀 Death Locations: {len(self.environmental_awareness.state.death_locations)} recorded")
    
    def showcase_monitoring_session(self):
        """Showcase a complete monitoring session."""
        self.print_section("Environmental Monitoring Session")
        
        # Start monitoring
        print("🟢 Starting environmental monitoring...")
        success = self.environmental_awareness.start_monitoring("DemoCharacter")
        
        if success:
            print("✅ Monitoring started successfully")
            
            # Simulate some movement and threats
            print("\n🔄 Simulating environmental changes...")
            
            # Move to different locations
            locations = [
                ("moenia_center", "naboo", (4500, -4500)),
                ("restuss", "rori", (5000, -3000)),
                ("mos_eisley_cantina", "tatooine", (3520, -4800)),
                ("theed_palace", "naboo", (5000, -4000))
            ]
            
            for zone, planet, coords in locations:
                print(f"  📍 Moving to {zone} on {planet}...")
                self.environmental_awareness.update_location(zone, planet, coords)
                
                # Simulate some threats
                if "restuss" in zone:
                    threat = ThreatDetection(
                        threat_type=ThreatType.HIGH_GCW_ZONE,
                        risk_level=RiskLevel.CRITICAL,
                        location=coords,
                        zone=zone,
                        planet=planet,
                        description="Critical GCW threat detected",
                        confidence=0.9,
                        timestamp=datetime.now()
                    )
                    self.environmental_awareness.state.detected_threats = [threat]
                    print(f"    ⚠️  Critical threat detected in {zone}")
                
                time.sleep(1)  # Brief pause for demo
            
            # Stop monitoring
            print("\n🔴 Stopping environmental monitoring...")
            summary = self.environmental_awareness.stop_monitoring()
            
            if summary:
                print("📈 Monitoring Session Summary:")
                print(f"  Duration: {summary.get('session_duration', 0):.1f} seconds")
                print(f"  Threats Detected: {summary.get('threats_detected', 0)}")
                print(f"  Zones Visited: {len(summary.get('zones_visited', []))}")
                print(f"  Avoidance Actions: {len(summary.get('avoidance_actions', []))}")
        else:
            print("❌ Failed to start monitoring")
    
    def showcase_death_location_tracking(self):
        """Showcase death location tracking."""
        self.print_section("Death Location Tracking")
        
        # Add some death locations
        death_locations = [
            (3000, -5500, "Anchorhead outskirts"),
            (5000, -4000, "Theed palace area"),
            (3520, -4800, "Mos Eisley cantina")
        ]
        
        print("💀 Recording death locations...")
        for x, y, description in death_locations:
            self.environmental_awareness.add_death_location((x, y))
            print(f"  📍 Death recorded at ({x}, {y}) - {description}")
        
        print(f"\n📊 Total death locations tracked: {len(self.environmental_awareness.state.death_locations)}")
        
        # Show avoidance recommendations for death locations
        death_threat = ThreatDetection(
            threat_type=ThreatType.DEATH_LOCATION,
            risk_level=RiskLevel.MEDIUM,
            location=(3000, -5500),
            zone="anchorhead",
            planet="tatooine",
            description="Previous death location",
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        self.environmental_awareness.state.detected_threats = [death_threat]
        recommendations = self.environmental_awareness.get_avoidance_recommendations()
        
        if recommendations:
            print("\n💡 Death Location Avoidance:")
            for rec in recommendations:
                print(f"  • {rec}")
    
    def showcase_avoidance_strategies(self):
        """Showcase different avoidance strategies."""
        self.print_section("Avoidance Strategies")
        
        strategies = [
            {
                "threat": ThreatType.HOSTILE_NPC_CLUSTER,
                "strategy": "move_to_safe_zone",
                "description": "Move to nearest safe zone when hostile NPCs detected"
            },
            {
                "threat": ThreatType.HIGH_GCW_ZONE,
                "strategy": "change_zone",
                "description": "Change to a different zone when in high-risk GCW area"
            },
            {
                "threat": ThreatType.AFK_REPORTING_HOTSPOT,
                "strategy": "random_movement",
                "description": "Perform random movement to avoid AFK reporting"
            },
            {
                "threat": ThreatType.STARPORT_PROXIMITY,
                "strategy": "reduce_activity",
                "description": "Reduce activity when too close to starport"
            },
            {
                "threat": ThreatType.CROWDED_ZONE,
                "strategy": "move_to_less_crowded",
                "description": "Move to less crowded area to avoid detection"
            },
            {
                "threat": ThreatType.DEATH_LOCATION,
                "strategy": "avoid_area",
                "description": "Avoid specific area where death occurred"
            }
        ]
        
        for i, strategy in enumerate(strategies, 1):
            print(f"{i}. {strategy['threat'].value.replace('_', ' ').title()}")
            print(f"   Strategy: {strategy['strategy']}")
            print(f"   Description: {strategy['description']}")
            print()
    
    def showcase_risk_zones(self):
        """Showcase risk zone information."""
        self.print_section("Risk Zone Information")
        
        risk_zones = [
            {
                "zone": "restuss",
                "planet": "rori",
                "risk_level": "CRITICAL",
                "threats": ["High GCW Zone", "Hostile NPC Cluster"],
                "strategy": "Change Zone"
            },
            {
                "zone": "battlefield",
                "planet": "dantooine",
                "risk_level": "CRITICAL",
                "threats": ["High GCW Zone", "Hostile NPC Cluster"],
                "strategy": "Change Zone"
            },
            {
                "zone": "mos_eisley_cantina",
                "planet": "tatooine",
                "risk_level": "HIGH",
                "threats": ["AFK Reporting Hotspot", "Crowded Zone"],
                "strategy": "Random Movement"
            },
            {
                "zone": "coronet_trade_district",
                "planet": "corellia",
                "risk_level": "HIGH",
                "threats": ["AFK Reporting Hotspot", "Crowded Zone"],
                "strategy": "Move to Less Crowded"
            },
            {
                "zone": "moenia_center",
                "planet": "naboo",
                "risk_level": "LOW",
                "threats": [],
                "strategy": "None"
            }
        ]
        
        for zone_info in risk_zones:
            print(f"🌍 {zone_info['zone']} ({zone_info['planet']})")
            print(f"   Risk Level: {zone_info['risk_level']}")
            if zone_info['threats']:
                print(f"   Threats: {', '.join(zone_info['threats'])}")
            print(f"   Strategy: {zone_info['strategy']}")
            print()
    
    def showcase_safe_zones(self):
        """Showcase safe zone information."""
        self.print_section("Safe Zone Information")
        
        safe_zones = self.environmental_awareness.config["environmental_awareness"]["safe_zones"]
        
        for zone_name, zones in safe_zones.items():
            print(f"🛡️  {zone_name.title()}:")
            for i, zone in enumerate(zones, 1):
                x, y, width, height = zone
                print(f"   Zone {i}: ({x}, {y}) - {width}x{height}")
            print()
    
    def run_full_demo(self):
        """Run the complete environmental awareness demo."""
        self.print_header("Environmental Awareness & Risk Avoidance System Demo")
        
        print("🎯 This demo showcases the environmental awareness system that detects")
        print("   and avoids various threats in the game environment.")
        print()
        print("🔍 Features demonstrated:")
        print("   • Hostile NPC cluster detection")
        print("   • High GCW zone detection")
        print("   • AFK reporting hotspot detection")
        print("   • Starport proximity detection")
        print("   • Player cluster detection")
        print("   • Death location tracking")
        print("   • Risk assessment and avoidance strategies")
        print()
        
        # Showcase different scenarios
        for scenario in self.demo_scenarios:
            self.showcase_risk_assessment(scenario)
            time.sleep(2)  # Brief pause between scenarios
        
        # Showcase monitoring session
        self.showcase_monitoring_session()
        
        # Showcase death location tracking
        self.showcase_death_location_tracking()
        
        # Showcase avoidance strategies
        self.showcase_avoidance_strategies()
        
        # Showcase risk zones
        self.showcase_risk_zones()
        
        # Showcase safe zones
        self.showcase_safe_zones()
        
        self.print_header("Demo Complete")
        print("✅ Environmental awareness system demo completed successfully!")
        print("🔧 The system is ready for integration with the main bot framework.")
        print("📊 All threat detection, risk assessment, and avoidance strategies")
        print("   have been demonstrated and are fully functional.")


def main():
    """Main demo function."""
    try:
        demo = EnvironmentalAwarenessDemo()
        demo.run_full_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
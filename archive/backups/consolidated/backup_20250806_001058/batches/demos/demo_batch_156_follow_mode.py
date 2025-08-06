#!/usr/bin/env python3
"""
Demo script for Batch 156 - Multi-Char Follow Mode (Quester + Support)

This script demonstrates the follow mode functionality that allows a second MS11 bot
instance to follow a main character, providing healing, buffing, and support.

Usage:
    python demo_batch_156_follow_mode.py
"""

import time
import random
import json
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class FollowDemoConfig:
    """Configuration for the follow mode demo."""
    leader_name: str = "QuestLeader"
    follow_distance: int = 5
    heal_threshold: int = 80
    buff_interval: int = 60  # 1 minute for demo
    emergency_heal_threshold: int = 50
    demo_duration: int = 300  # 5 minutes
    cycle_interval: float = 2.0  # 2 seconds between cycles


class FollowModeDemo:
    """Demo class for follow mode functionality."""
    
    def __init__(self, config: FollowDemoConfig):
        self.config = config
        self.start_time = time.time()
        self.cycles_completed = 0
        self.total_heals = 0
        self.total_buffs = 0
        self.total_assists = 0
        self.leader_health = 100
        self.last_buff_time = 0
        
    def run_demo(self):
        """Run the follow mode demo."""
        print("=" * 60)
        print("🎯 BATCH 156 - MULTI-CHAR FOLLOW MODE DEMO")
        print("=" * 60)
        print(f"📋 Configuration:")
        print(f"   Leader: {self.config.leader_name}")
        print(f"   Follow Distance: {self.config.follow_distance}")
        print(f"   Heal Threshold: {self.config.heal_threshold}%")
        print(f"   Buff Interval: {self.config.buff_interval}s")
        print(f"   Emergency Heal Threshold: {self.config.emergency_heal_threshold}%")
        print(f"   Demo Duration: {self.config.demo_duration}s")
        print("=" * 60)
        
        print(f"\n🚀 Starting follow mode for {self.config.leader_name}...")
        
        # Simulate pre-buff routine
        print("\n🪄 Applying pre-buffs...")
        self._simulate_pre_buffs()
        
        print(f"\n📡 Follow mode active. Following {self.config.leader_name}")
        print("Press Ctrl+C to stop the demo\n")
        
        try:
            while time.time() - self.start_time < self.config.demo_duration:
                self._run_follow_cycle()
                time.sleep(self.config.cycle_interval)
                
        except KeyboardInterrupt:
            print("\n⏹️ Demo interrupted by user")
        
        self._print_summary()
    
    def _run_follow_cycle(self):
        """Run a single follow cycle."""
        self.cycles_completed += 1
        
        # Simulate leader health changes
        self._update_leader_health()
        
        print(f"\n[Cycle {self.cycles_completed}] Leader health: {self.leader_health}%")
        
        # Check party status
        self._check_party_status()
        
        # Prioritize healing if needed
        if self.leader_health <= self.config.emergency_heal_threshold:
            self._emergency_heal()
            self.total_heals += 1
        elif self.leader_health <= self.config.heal_threshold:
            self._heal_leader()
            self.total_heals += 1
        
        # Apply buffs on interval
        if self._should_apply_buffs():
            self._apply_buffs()
            self.total_buffs += 1
        
        # Follow leader
        self._follow_leader()
        
        # Assist if not healing
        if self.leader_health > self.config.heal_threshold:
            self._assist_leader()
            self.total_assists += 1
    
    def _update_leader_health(self):
        """Simulate leader health changes."""
        # Simulate health changes based on combat/activity
        if random.random() < 0.3:  # 30% chance of health change
            change = random.randint(-15, 5)
            self.leader_health = max(0, min(100, self.leader_health + change))
    
    def _check_party_status(self):
        """Simulate party status checking."""
        if random.random() < 0.1:  # 10% chance to check party
            print("🎉 Checking party status...")
    
    def _emergency_heal(self):
        """Simulate emergency healing."""
        print(f"🚨 EMERGENCY HEALING {self.config.leader_name}!")
        time.sleep(1.0)  # Simulate cast time
        print(f"✅ Emergency heal successful on {self.config.leader_name}")
    
    def _heal_leader(self):
        """Simulate healing the leader."""
        print(f"💚 Healing {self.config.leader_name}...")
        time.sleep(0.5)  # Simulate cast time
        print(f"✅ Successfully healed {self.config.leader_name}")
    
    def _should_apply_buffs(self) -> bool:
        """Check if it's time to apply buffs."""
        current_time = time.time()
        return (current_time - self.last_buff_time) >= self.config.buff_interval
    
    def _apply_buffs(self):
        """Simulate applying buffs."""
        print(f"✨ Applying buffs to {self.config.leader_name}...")
        buffs = ["Enhance Health", "Enhance Stamina", "Enhance Action"]
        
        for buff in buffs:
            print(f"🪄 Casting {buff}...")
            time.sleep(0.3)  # Simulate cast time
            print(f"✅ Applied {buff} to {self.config.leader_name}")
        
        self.last_buff_time = time.time()
    
    def _follow_leader(self):
        """Simulate following the leader."""
        print(f"📡 Following {self.config.leader_name} at distance {self.config.follow_distance}...")
        time.sleep(0.2)  # Simulate movement
        print(f"✅ Successfully following {self.config.leader_name}")
    
    def _assist_leader(self):
        """Simulate assisting the leader."""
        print(f"⚔️ Assisting {self.config.leader_name}...")
        time.sleep(0.3)  # Simulate assist action
        print(f"✅ Assisted {self.config.leader_name}")
    
    def _simulate_pre_buffs(self):
        """Simulate pre-buff routine."""
        pre_buffs = ["Enhance Health", "Enhance Stamina", "Enhance Mind"]
        
        for buff in pre_buffs:
            print(f"🪄 Casting {buff}...")
            time.sleep(0.5)
            print(f"✅ Applied {buff}")
        
        print("✅ Pre-buff complete.")
    
    def _print_summary(self):
        """Print demo summary."""
        elapsed_time = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 FOLLOW MODE DEMO SUMMARY")
        print("=" * 60)
        print(f"⏱️  Demo Duration: {elapsed_time:.1f} seconds")
        print(f"🔄 Cycles Completed: {self.cycles_completed}")
        print(f"💚 Total Heals Cast: {self.total_heals}")
        print(f"✨ Total Buffs Applied: {self.total_buffs}")
        print(f"⚔️  Total Assists Given: {self.total_assists}")
        print(f"📈 Average Cycles/Minute: {self.cycles_completed / (elapsed_time / 60):.1f}")
        print("=" * 60)


def create_sample_config() -> Dict[str, Any]:
    """Create a sample configuration for follow mode."""
    return {
        "follow_leader_name": "QuestLeader",
        "follow_distance": 5,
        "heal_threshold": 80,
        "buff_interval": 300,
        "support_priority": "heal",
        "auto_join_party": True,
        "emergency_heal_threshold": 50
    }


def test_follow_mode_integration():
    """Test the follow mode integration with different scenarios."""
    print("\n🧪 Testing Follow Mode Integration")
    print("-" * 40)
    
    # Test different leader names
    test_leaders = ["QuestLeader", "CombatMaster", "SupportBot"]
    
    for leader in test_leaders:
        print(f"\n📋 Testing with leader: {leader}")
        config = FollowDemoConfig(
            leader_name=leader,
            demo_duration=30,  # 30 seconds for testing
            cycle_interval=1.0
        )
        
        demo = FollowModeDemo(config)
        demo.run_demo()


def test_follow_mode_edge_cases():
    """Test edge cases for follow mode."""
    print("\n🔍 Testing Follow Mode Edge Cases")
    print("-" * 40)
    
    # Test with very low heal threshold
    print("\n📋 Testing with low heal threshold (30%)")
    config = FollowDemoConfig(
        heal_threshold=30,
        emergency_heal_threshold=20,
        demo_duration=20,
        cycle_interval=1.0
    )
    
    demo = FollowModeDemo(config)
    demo.run_demo()
    
    # Test with frequent buffing
    print("\n📋 Testing with frequent buffing (10s interval)")
    config = FollowDemoConfig(
        buff_interval=10,
        demo_duration=30,
        cycle_interval=1.0
    )
    
    demo = FollowModeDemo(config)
    demo.run_demo()


def main():
    """Main demo function."""
    print("🎯 BATCH 156 - MULTI-CHAR FOLLOW MODE DEMO")
    print("=" * 60)
    print("This demo shows how a second MS11 bot instance can follow")
    print("a main character, providing healing, buffing, and support.")
    print("=" * 60)
    
    # Create sample configuration
    sample_config = create_sample_config()
    print(f"\n📄 Sample Configuration:")
    print(json.dumps(sample_config, indent=2))
    
    # Run main demo
    config = FollowDemoConfig()
    demo = FollowModeDemo(config)
    demo.run_demo()
    
    # Run integration tests
    test_follow_mode_integration()
    
    # Run edge case tests
    test_follow_mode_edge_cases()
    
    print("\n✅ Follow Mode Demo Complete!")
    print("\n💡 Usage Examples:")
    print("  python src/main.py --mode follow --follow-character QuestLeader")
    print("  python src/main.py --mode follow --follow-character CombatMaster --max_loops 100")
    print("  python src/main.py --mode follow --follow-character SupportBot --loop")


if __name__ == "__main__":
    main() 
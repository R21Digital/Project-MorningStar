#!/usr/bin/env python3
"""MS11 Batch 081 - Anti-Detection Defense Layer v2 Demo"""

import time
import random
from datetime import datetime, timedelta
from typing import Dict, Any

from core.anti_detection import DefenseManager


class AntiDetectionDemo:
    """Demo class for anti-detection defense layer v2."""
    
    def __init__(self):
        """Initialize the demo."""
        self.defense_manager = DefenseManager()
        self.demo_characters = ["DemoMarksman", "DemoMedic", "DemoEngineer"]
        self.demo_duration = 60  # Demo duration in seconds
        
        print("🛡️  MS11 Batch 081 - Anti-Detection Defense Layer v2 Demo")
        print("=" * 60)
    
    def run_full_demo(self):
        """Run the complete anti-detection demo."""
        print("\n🚀 Starting Anti-Detection Defense Layer v2 Demo...")
        
        # Setup demo characters
        self._setup_demo_characters()
        
        # Run individual demos
        self._demo_timing_randomization()
        self._demo_emote_system()
        self._demo_anti_ping_logic()
        self._demo_session_tracking()
        self._demo_defense_manager()
        self._demo_integration()
        
        # Generate demo report
        report = self.generate_demo_report()
        self._print_demo_report(report)
        
        print("\n✅ Anti-Detection Defense Layer v2 Demo completed!")
    
    def _setup_demo_characters(self):
        """Setup demo character profiles."""
        print("\n👥 Setting up demo character profiles...")
        
        for character in self.demo_characters:
            self.defense_manager.add_character_profile(
                character_name=character,
                max_daily_hours=8.0,
                max_consecutive_hours=4.0,
                mandatory_break_hours=1.0,
                rotation_priority=random.randint(1, 5)
            )
        
        print(f"✅ Added {len(self.demo_characters)} character profiles")
    
    def _demo_timing_randomization(self):
        """Demo timing randomization features."""
        print("\n⏰ Demo: Timing Randomization")
        print("-" * 40)
        
        timing_randomizer = self.defense_manager.timing_randomizer
        
        # Demo idle timing
        print("📊 Idle Timing Examples:")
        for i in range(5):
            idle_timing = timing_randomizer.get_randomized_idle_timing()
            print(f"  {i+1}. Idle timing: {idle_timing:.2f}s")
        
        # Demo action timing
        print("\n📊 Action Timing Examples:")
        for i in range(5):
            action_timing = timing_randomizer.get_randomized_action_timing()
            print(f"  {i+1}. Action timing: {action_timing:.2f}s")
        
        # Demo login window
        login_time, logout_time = timing_randomizer.get_login_window()
        print(f"\n🕐 Login Window: {login_time.strftime('%H:%M')} - {logout_time.strftime('%H:%M')}")
        
        # Demo session duration
        session_duration = timing_randomizer.get_session_duration()
        print(f"⏱️  Session Duration: {session_duration:.1f} hours")
        
        # Demo break logic
        print(f"\n☕ Break Logic:")
        for hours in [1.0, 2.0, 3.0, 4.0, 5.0]:
            should_break = timing_randomizer.should_take_break(hours)
            print(f"  {hours}h session: {'Take break' if should_break else 'Continue'}")
    
    def _demo_emote_system(self):
        """Demo emote system features."""
        print("\n😊 Demo: Emote System")
        print("-" * 40)
        
        emote_system = self.defense_manager.emote_system
        
        # Demo different contexts
        contexts = [
            ("Idle", EmoteContext(idle_time_seconds=180.0)),
            ("Social", EmoteContext(player_nearby=True, social_event=True)),
            ("Mixed", EmoteContext(player_nearby=True, idle_time_seconds=120.0))
        ]
        
        for context_name, context in contexts:
            print(f"\n📋 Context: {context_name}")
            emote = emote_system.get_random_emote(context)
            if emote:
                print(f"  Selected emote: {emote.command} - {emote.description}")
                print(f"  Probability: {emote.probability:.2f}")
                print(f"  Context tags: {emote.context}")
        
        # Demo emote execution
        print(f"\n🎭 Emote Execution Examples:")
        for i in range(3):
            idle_context = EmoteContext(idle_time_seconds=200.0)
            emote = emote_system.trigger_contextual_emote(idle_context)
            if emote:
                print(f"  {i+1}. Executed: {emote.command}")
        
        # Demo emote statistics
        stats = emote_system.get_emote_statistics()
        print(f"\n📊 Emote Statistics:")
        print(f"  Total emotes: {stats['total_emotes']}")
        if stats['emote_breakdown']:
            most_used = stats['most_used_emote']
            print(f"  Most used: {most_used}")
    
    def _demo_anti_ping_logic(self):
        """Demo anti-ping logic features."""
        print("\n💬 Demo: Anti-Ping Logic")
        print("-" * 40)
        
        anti_ping = self.defense_manager.anti_ping_logic
        
        # Demo tell detection
        test_messages = [
            "Player1 tells you: Hey, are you there?",
            "Player2 whispers: Can you help me?",
            "Player3 says to you: What are you doing?",
            "Player4 tells you: Are you a bot?",
            "Regular chat message that should be ignored"
        ]
        
        print("🔍 Tell Detection Examples:")
        for i, message in enumerate(test_messages, 1):
            tell_message = anti_ping.detect_tell_message(message)
            if tell_message:
                print(f"  {i}. Detected tell from: {tell_message.sender}")
                print(f"     Message: {tell_message.message[:50]}...")
                
                # Demo response processing
                response_details = anti_ping.process_tell_message(tell_message)
                if response_details:
                    print(f"     Response: {response_details['response']}")
                    print(f"     Delay: {response_details['delay_seconds']:.1f}s")
            else:
                print(f"  {i}. No tell detected (ignored)")
        
        # Demo ignore list
        print(f"\n🚫 Ignore List Management:")
        anti_ping.add_to_ignore_list("SpamPlayer")
        anti_ping.add_to_ignore_list("BotHunter")
        print(f"  Added 2 players to ignore list")
        print(f"  Total ignored: {len(anti_ping.ignore_list)}")
        
        # Demo statistics
        stats = anti_ping.get_tell_statistics()
        print(f"\n📊 Tell Statistics:")
        print(f"  Total tells: {stats['total_tells']}")
        print(f"  Responses sent: {stats['responses_sent']}")
        print(f"  Response rate: {stats['response_rate']:.1f}%")
    
    def _demo_session_tracking(self):
        """Demo session tracking features."""
        print("\n📊 Demo: Session Tracking")
        print("-" * 40)
        
        session_tracker = self.defense_manager.session_tracker
        
        # Demo character availability
        available = session_tracker.get_available_characters()
        print(f"✅ Available characters: {available}")
        
        # Demo character rotation
        rotation = session_tracker.get_character_rotation()
        print(f"🔄 Character rotation: {rotation}")
        
        # Demo session limits
        print(f"\n⏰ Session Limits:")
        for character in self.demo_characters[:2]:
            daily_stats = session_tracker.get_character_daily_stats(character)
            print(f"  {character}: {daily_stats['total_hours']:.1f}h today, {daily_stats['sessions_count']} sessions")
        
        # Demo break logic
        print(f"\n☕ Break Logic:")
        for character in self.demo_characters[:2]:
            should_break = session_tracker.should_take_break(character)
            break_duration = session_tracker.get_break_duration()
            print(f"  {character}: {'Take break' if should_break else 'Continue'} ({break_duration}h break)")
        
        # Demo statistics
        stats = session_tracker.get_session_statistics()
        print(f"\n📊 Session Statistics:")
        print(f"  Total sessions: {stats['total_sessions']}")
        print(f"  Total hours: {stats['total_hours']:.1f}")
        print(f"  Characters used: {stats['characters_used']}")
    
    def _demo_defense_manager(self):
        """Demo defense manager integration."""
        print("\n🛡️ Demo: Defense Manager Integration")
        print("-" * 40)
        
        # Start defense for a character
        character = self.demo_characters[0]
        print(f"🚀 Starting defense for: {character}")
        
        if self.defense_manager.start_defense(character):
            print(f"✅ Defense started successfully")
            
            # Demo various features
            print(f"\n📊 Defense Features:")
            
            # Timing
            idle_timing = self.defense_manager.get_randomized_timing("idle")
            action_timing = self.defense_manager.get_randomized_timing("action")
            print(f"  Idle timing: {idle_timing:.2f}s")
            print(f"  Action timing: {action_timing:.2f}s")
            
            # Emotes
            emote = self.defense_manager.trigger_emote("idle")
            if emote:
                print(f"  Triggered emote: {emote}")
            
            # Tell processing
            test_tell = "Player1 tells you: Are you available?"
            response = self.defense_manager.process_tell_message(test_tell)
            if response:
                print(f"  Tell response: {response['response']}")
            
            # Session info
            session_info = self.defense_manager.get_current_session_info()
            if session_info:
                print(f"  Current session: {session_info['duration_hours']:.2f}h")
            
            # Stop defense
            session_data = self.defense_manager.stop_defense("Demo completed")
            if session_data:
                print(f"✅ Defense stopped, session duration: {session_data.duration_hours:.2f}h")
        else:
            print(f"❌ Failed to start defense for {character}")
    
    def _demo_integration(self):
        """Demo integration with existing systems."""
        print("\n🔗 Demo: System Integration")
        print("-" * 40)
        
        # Demo with multiple characters
        print("🔄 Multi-character session demo:")
        
        for character in self.demo_characters:
            print(f"\n👤 Character: {character}")
            
            # Start session
            if self.defense_manager.start_defense(character):
                print(f"  ✅ Session started")
                
                # Simulate some activity
                for i in range(3):
                    timing = self.defense_manager.get_randomized_timing("action")
                    emote = self.defense_manager.trigger_emote("social")
                    print(f"  Activity {i+1}: {timing:.2f}s delay, emote: {emote or 'none'}")
                    time.sleep(0.1)  # Quick demo
                
                # End session
                session_data = self.defense_manager.stop_defense(f"Demo session {i+1}")
                if session_data:
                    print(f"  ✅ Session ended: {session_data.duration_hours:.2f}h")
            else:
                print(f"  ❌ Failed to start session")
    
    def generate_demo_report(self) -> Dict[str, Any]:
        """Generate comprehensive demo report."""
        return {
            "demo_info": {
                "batch": "081",
                "name": "Anti-Detection Defense Layer v2",
                "version": "2.0.0",
                "demo_duration": self.demo_duration,
                "characters_used": self.demo_characters
            },
            "defense_statistics": self.defense_manager.get_defense_statistics(),
            "character_stats": {
                character: self.defense_manager.get_character_daily_stats(character)
                for character in self.demo_characters
            },
            "available_characters": self.defense_manager.get_available_characters(),
            "character_rotation": self.defense_manager.get_character_rotation(),
            "demo_timestamp": datetime.now().isoformat()
        }
    
    def _print_demo_report(self, report: Dict[str, Any]):
        """Print the demo report."""
        print("\n📋 Demo Report")
        print("=" * 60)
        
        # Demo info
        demo_info = report["demo_info"]
        print(f"Batch: {demo_info['batch']}")
        print(f"Name: {demo_info['name']}")
        print(f"Version: {demo_info['version']}")
        print(f"Characters: {', '.join(demo_info['characters_used'])}")
        
        # Defense statistics
        defense_stats = report["defense_statistics"]
        print(f"\n🛡️ Defense Statistics:")
        print(f"  Active: {defense_stats['defense_state']['is_active']}")
        print(f"  Current character: {defense_stats['defense_state']['current_character']}")
        
        # Component statistics
        timing_stats = defense_stats["timing_randomizer"]
        emote_stats = defense_stats["emote_system"]
        tell_stats = defense_stats["anti_ping_logic"]
        session_stats = defense_stats["session_tracker"]
        
        print(f"\n⏰ Timing Randomizer:")
        print(f"  Total timings: {timing_stats['total_timings']}")
        print(f"  Average timing: {timing_stats['average_timing']:.2f}s")
        
        print(f"\n😊 Emote System:")
        print(f"  Total emotes: {emote_stats['total_emotes']}")
        if emote_stats['most_used_emote']:
            print(f"  Most used: {emote_stats['most_used_emote']}")
        
        print(f"\n💬 Anti-Ping Logic:")
        print(f"  Total tells: {tell_stats['total_tells']}")
        print(f"  Response rate: {tell_stats['response_rate']:.1f}%")
        
        print(f"\n📊 Session Tracker:")
        print(f"  Total sessions: {session_stats['total_sessions']}")
        print(f"  Total hours: {session_stats['total_hours']:.1f}")
        print(f"  Characters used: {session_stats['characters_used']}")
        
        # Character statistics
        print(f"\n👥 Character Statistics:")
        for character, stats in report["character_stats"].items():
            print(f"  {character}: {stats['total_hours']:.1f}h, {stats['sessions_count']} sessions")
        
        print(f"\n🔄 Available characters: {', '.join(report['available_characters'])}")
        print(f"🔄 Character rotation: {', '.join(report['character_rotation'])}")


def main():
    """Main demo function."""
    demo = AntiDetectionDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main() 
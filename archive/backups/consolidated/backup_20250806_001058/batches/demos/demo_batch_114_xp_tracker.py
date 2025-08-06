"""Demo Batch 114 - Experimental XP Tracker (Deep Skill Mapping)

This demo showcases the enhanced XP tracking capabilities including:
- Log XP gains with timestamps, quest name (if known), and zone
- Visualize XP gain rates per hour
- Detect which skills are progressing fastest
- Recommend optimal skill paths and detect leveling slowdowns
- Store XP gain summaries in session logs and charts
"""

import json
import time
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from modules.experimental_xp_tracker import ExperimentalXPTracker


class XPTrackerDemo:
    """Demo class for showcasing XP tracker features."""
    
    def __init__(self):
        """Initialize the demo with a temporary config."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "xp_tracker_config.json"
        self.xp_tracker = ExperimentalXPTracker(str(self.config_path))
        
        # Demo data for realistic XP tracking
        self.demo_quests = [
            "Healing the Sick",
            "Hunting the Beast",
            "Crafting Supplies",
            "Exploration Mission",
            "Social Gathering",
            "Combat Training",
            "Medical Emergency",
            "Artisan Workshop",
            "Scout Reconnaissance",
            "Entertainment Performance"
        ]
        
        self.demo_zones = [
            "dantooine", "naboo", "corellia", "tatooine", "lok",
            "rori", "talus", "yavin4", "endor", "coruscant"
        ]
        
        self.demo_professions = {
            "marksman": ["combat_marksman_novice", "combat_marksman_marksman", "combat_marksman_rifleman"],
            "medic": ["science_medic_novice", "science_medic_doctor", "science_medic_combat_medic"],
            "artisan": ["crafting_artisan_novice", "crafting_artisan_engineering", "crafting_artisan_armorsmith"],
            "scout": ["outdoors_scout_novice", "outdoors_scout_ranger", "outdoors_scout_creature_handler"],
            "brawler": ["combat_brawler_novice", "combat_brawler_unarmed", "combat_brawler_teras_kasi"],
            "entertainer": ["social_entertainer_novice", "social_entertainer_musician", "social_entertainer_dancer"]
        }
        
        self.demo_sources = ["quest", "combat", "crafting", "exploration", "social"]
    
    def simulate_xp_session(self, duration_minutes: int = 30) -> None:
        """Simulate an XP tracking session with realistic data."""
        print(f"\n🎮 Starting XP Tracking Session Demo ({duration_minutes} minutes)")
        print("=" * 60)
        
        # Start session
        session_id = self.xp_tracker.start_session()
        print(f"📊 Session ID: {session_id}")
        print(f"⏰ Start Time: {self.xp_tracker.session_start_time}")
        
        # Simulate XP gains over time
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        event_count = 0
        while datetime.now() < end_time:
            # Generate realistic XP event
            event = self._generate_demo_xp_event()
            
            # Record the event
            xp_event = self.xp_tracker.record_xp_gain(**event)
            
            event_count += 1
            print(f"📈 Event {event_count}: {event['amount']} XP for {event['skill']} ({event['profession']}) "
                  f"from {event['source']} in {event.get('zone', 'unknown zone')}")
            
            # Add some realistic delays
            time.sleep(0.1)  # 100ms between events for demo
        
        print(f"\n✅ Session completed with {event_count} XP events")
        print(f"⏰ End Time: {datetime.now()}")
        print(f"⏱️  Duration: {duration_minutes} minutes")
    
    def _generate_demo_xp_event(self) -> Dict[str, Any]:
        """Generate a realistic XP event for demo purposes."""
        import random
        
        # Select random profession and skill
        profession = random.choice(list(self.demo_professions.keys()))
        skill = random.choice(self.demo_professions[profession])
        
        # Generate realistic XP amount based on source
        source = random.choice(self.demo_sources)
        if source == "quest":
            xp_amount = random.randint(200, 500)
            quest_name = random.choice(self.demo_quests)
        elif source == "combat":
            xp_amount = random.randint(50, 150)
            quest_name = None
        elif source == "crafting":
            xp_amount = random.randint(25, 100)
            quest_name = None
        elif source == "exploration":
            xp_amount = random.randint(10, 50)
            quest_name = None
        else:  # social
            xp_amount = random.randint(5, 25)
            quest_name = None
        
        # Select zone (with some profession-specific preferences)
        zone = random.choice(self.demo_zones)
        
        # Generate level progression (occasionally)
        level_before = random.randint(1, 10) if random.random() < 0.1 else None
        level_after = level_before + 1 if level_before else None
        
        return {
            "amount": xp_amount,
            "profession": profession,
            "skill": skill,
            "source": source,
            "quest_name": quest_name,
            "zone": zone,
            "level_before": level_before,
            "level_after": level_after
        }
    
    def showcase_analytics(self) -> None:
        """Showcase the analytics capabilities."""
        print(f"\n📊 XP Analytics Dashboard")
        print("=" * 60)
        
        # Generate comprehensive summary
        summary = self.xp_tracker.generate_xp_summary()
        
        print(f"💰 Total XP Gained: {summary['total_xp']:,}")
        print(f"⚡ XP per Hour: {summary['xp_per_hour']:.1f}")
        print(f"⏱️  Session Duration: {summary['session_duration_hours']:.2f} hours")
        
        # XP by source breakdown
        print(f"\n📈 XP by Source:")
        for source, xp in summary['xp_by_source'].items():
            percentage = (xp / summary['total_xp']) * 100
            print(f"  {source.title()}: {xp:,} XP ({percentage:.1f}%)")
        
        # XP by profession breakdown
        print(f"\n🎯 XP by Profession:")
        for profession, xp in summary['xp_by_profession'].items():
            percentage = (xp / summary['total_xp']) * 100
            print(f"  {profession.title()}: {xp:,} XP ({percentage:.1f}%)")
        
        # XP by zone breakdown
        print(f"\n🌍 XP by Zone:")
        for zone, xp in summary['xp_by_zone'].items():
            percentage = (xp / summary['total_xp']) * 100
            print(f"  {zone.title()}: {xp:,} XP ({percentage:.1f}%)")
        
        # Top gaining skills
        print(f"\n🏆 Top Gaining Skills:")
        for skill, xp in summary['top_gaining_skills'].items():
            print(f"  {skill}: {xp:,} XP")
        
        # Fastest progressing skills
        print(f"\n🚀 Fastest Progressing Skills:")
        for skill in summary['fastest_progressing_skills']:
            print(f"  {skill}")
    
    def showcase_skill_analysis(self) -> None:
        """Showcase skill analysis capabilities."""
        print(f"\n🎯 Skill Analysis")
        print("=" * 60)
        
        # Get fastest and slowest progressing skills
        fastest_skills = self.xp_tracker.get_fastest_progressing_skills(limit=3)
        slowest_skills = self.xp_tracker.get_slowest_progressing_skills(limit=3)
        
        print(f"🚀 Fastest Progressing Skills:")
        for i, skill in enumerate(fastest_skills, 1):
            print(f"  {i}. {skill.skill_name} ({skill.profession}) - {skill.progress_rate:.1f} XP/hour")
        
        print(f"\n🐌 Slowest Progressing Skills:")
        for i, skill in enumerate(slowest_skills, 1):
            print(f"  {i}. {skill.skill_name} ({skill.profession}) - {skill.progress_rate:.1f} XP/hour")
        
        # Detect slowdowns
        slowdowns = self.xp_tracker.detect_leveling_slowdowns()
        if slowdowns:
            print(f"\n⚠️  Leveling Slowdowns Detected:")
            for slowdown in slowdowns[:3]:  # Show top 3
                print(f"  {slowdown['skill']} ({slowdown['profession']}): "
                      f"{slowdown['slowdown_percentage']:.1f}% slower than average")
        else:
            print(f"\n✅ No significant slowdowns detected")
    
    def showcase_optimal_paths(self) -> None:
        """Showcase optimal skill path recommendations."""
        print(f"\n🗺️  Optimal Skill Paths")
        print("=" * 60)
        
        recommendations = self.xp_tracker.recommend_optimal_skill_paths()
        
        for profession, skills in recommendations.items():
            print(f"\n{profession.title()} Profession:")
            for i, skill in enumerate(skills, 1):
                print(f"  {i}. {skill}")
    
    def showcase_profession_analytics(self) -> None:
        """Showcase profession-specific analytics."""
        print(f"\n🎓 Profession Analytics")
        print("=" * 60)
        
        for profession in self.demo_professions.keys():
            analytics = self.xp_tracker.get_profession_analytics(profession)
            if analytics:
                print(f"\n{profession.title()}:")
                print(f"  Total XP: {analytics.total_xp:,}")
                print(f"  Skills Count: {analytics.skills_count}")
                print(f"  Average Level: {analytics.average_level:.1f}")
                print(f"  XP per Hour: {analytics.xp_per_hour:.1f}")
                print(f"  Fastest Skill: {analytics.fastest_skill}")
                print(f"  Slowest Skill: {analytics.slowest_skill}")
                print(f"  Quest Completion Rate: {analytics.quest_completion_rate:.1%}")
                print(f"  Optimal Zones: {', '.join(analytics.optimal_zones)}")
    
    def showcase_zone_recommendations(self) -> None:
        """Showcase zone recommendations."""
        print(f"\n🌍 Zone Recommendations")
        print("=" * 60)
        
        for profession in self.demo_professions.keys():
            recommendations = self.xp_tracker.get_zone_recommendations(profession)
            if recommendations:
                print(f"\n{profession.title()} - Best Zones:")
                for i, rec in enumerate(recommendations[:3], 1):  # Top 3 zones
                    print(f"  {i}. {rec['zone'].title()}: {rec['avg_xp']:.1f} XP/event "
                          f"({rec['total_xp']:,} total from {rec['events']} events)")
    
    def create_visualization(self) -> str:
        """Create and save XP visualization."""
        print(f"\n📊 Creating XP Visualization...")
        
        # Create visualization
        viz_path = self.xp_tracker.create_xp_visualization()
        
        if viz_path:
            print(f"✅ Visualization saved to: {viz_path}")
            return viz_path
        else:
            print("❌ No XP events to visualize")
            return None
    
    def export_session_data(self) -> str:
        """Export session data to JSON."""
        print(f"\n💾 Exporting Session Data...")
        
        # Export data
        export_path = self.xp_tracker.export_xp_data()
        
        print(f"✅ Session data exported to: {export_path}")
        
        # Show export summary
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        session_summary = export_data['session_summary']
        print(f"\n📋 Export Summary:")
        print(f"  Session ID: {session_summary['session_id']}")
        print(f"  Total XP: {session_summary['total_xp']:,}")
        print(f"  XP per Hour: {session_summary['xp_per_hour']:.1f}")
        print(f"  Events Recorded: {len(export_data['xp_events'])}")
        print(f"  Skills Tracked: {len(export_data['skill_progress'])}")
        print(f"  Zones Visited: {len(export_data['zone_efficiency'])}")
        
        return export_path
    
    def run_full_demo(self) -> None:
        """Run the complete XP tracker demo."""
        print("🎮 Batch 114 - Experimental XP Tracker Demo")
        print("=" * 60)
        print("This demo showcases deep skill mapping and XP analytics")
        print("Features: logging, visualization, skill detection, and session summaries")
        
        try:
            # Simulate XP session
            self.simulate_xp_session(duration_minutes=2)  # 2 minutes for demo
            
            # Showcase all features
            self.showcase_analytics()
            self.showcase_skill_analysis()
            self.showcase_optimal_paths()
            self.showcase_profession_analytics()
            self.showcase_zone_recommendations()
            
            # Create visualization
            viz_path = self.create_visualization()
            
            # Export data
            export_path = self.export_session_data()
            
            print(f"\n🎉 Demo completed successfully!")
            print(f"📊 Visualization: {viz_path}")
            print(f"💾 Export: {export_path}")
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main demo function."""
    demo = XPTrackerDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main() 
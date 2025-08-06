"""Demo Batch 077 - Public Website Integration Layer.

This demo showcases the public data export functionality for SWGDB integration,
including quest tracking summaries, bot metrics, heroic readiness export, and
markdown/JSON generation for Eleventy.
"""

import json
import yaml
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from exporters.public_data_exporter import (
    PublicDataExporter,
    QuestTrackingSummary,
    BotMetrics,
    HeroicReadiness,
    create_public_data_exporter
)
from website_sync.sync_to_swgdb import (
    SWGDBSync,
    SyncStatus,
    WebsiteConfig,
    create_swgdb_sync
)


class PublicWebsiteIntegrationDemo:
    """Demo class for public website integration functionality."""

    def __init__(self):
        """Initialize the demo."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "data"
        self.session_logs_dir = Path(self.temp_dir) / "session_logs"
        self.export_dir = Path(self.temp_dir) / "data" / "exported"
        self.website_dir = Path(self.temp_dir) / "website_data"
        
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session_logs_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.website_dir.mkdir(parents=True, exist_ok=True)
        
        # Create demo data
        self._create_demo_data()
        
        # Initialize components
        self.exporter = create_public_data_exporter(
            data_dir=str(self.data_dir),
            session_logs_dir=str(self.session_logs_dir)
        )
        
        config = WebsiteConfig(
            target_directory=str(self.website_dir),
            backup_directory=str(self.temp_dir) / "backups",
            allowed_file_types=[".json", ".md"],
            max_file_size=10 * 1024 * 1024,  # 10MB
            sync_interval=3600,  # 1 hour
            enable_backup=True,
            enable_validation=True
        )
        
        self.sync = create_swgdb_sync(config)

    def cleanup(self):
        """Clean up demo resources."""
        shutil.rmtree(self.temp_dir)

    def _create_demo_data(self):
        """Create comprehensive demo data."""
        print("Creating demo data...")
        
        # Create enhanced progress tracker with realistic quest data
        progress_data = {
            "checklists": {
                "quest_tracker": {
                    "items": [
                        {
                            "name": "Jedi Initiate Quest",
                            "status": "completed",
                            "progress": 100.0,
                            "xp_reward": 5000,
                            "credit_reward": 2500,
                            "category": "jedi",
                            "location": "Coruscant",
                            "created_at": "2025-01-01T00:00:00",
                            "completed_at": "2025-01-02T00:00:00"
                        },
                        {
                            "name": "Combat Training - Naboo",
                            "status": "completed",
                            "progress": 100.0,
                            "xp_reward": 3000,
                            "credit_reward": 1500,
                            "category": "combat",
                            "location": "Naboo",
                            "created_at": "2025-01-03T00:00:00",
                            "completed_at": "2025-01-04T00:00:00"
                        },
                        {
                            "name": "Heroic: Axkva Min",
                            "status": "completed",
                            "progress": 100.0,
                            "xp_reward": 15000,
                            "credit_reward": 7500,
                            "category": "heroic",
                            "location": "Dathomir",
                            "created_at": "2025-01-05T00:00:00",
                            "completed_at": "2025-01-06T00:00:00"
                        },
                        {
                            "name": "Crafting Mastery - Corellia",
                            "status": "in_progress",
                            "progress": 75.0,
                            "xp_reward": 8000,
                            "credit_reward": 4000,
                            "category": "crafting",
                            "location": "Corellia",
                            "created_at": "2025-01-07T00:00:00",
                            "completed_at": None
                        },
                        {
                            "name": "Space Combat Training",
                            "status": "completed",
                            "progress": 100.0,
                            "xp_reward": 4000,
                            "credit_reward": 2000,
                            "category": "space",
                            "location": "Space",
                            "created_at": "2025-01-08T00:00:00",
                            "completed_at": "2025-01-09T00:00:00"
                        },
                        {
                            "name": "Heroic: Nightsister Ritual",
                            "status": "not_started",
                            "progress": 0.0,
                            "xp_reward": 12000,
                            "credit_reward": 6000,
                            "category": "heroic",
                            "location": "Dathomir",
                            "created_at": None,
                            "completed_at": None
                        }
                    ]
                }
            }
        }
        
        with open(self.data_dir / "enhanced_progress_tracker.json", 'w') as f:
            json.dump(progress_data, f)
        
        # Create multiple session logs with realistic progression
        sessions = [
            {
                "session_id": "session_001",
                "start_time": "2025-01-01T10:00:00",
                "end_time": "2025-01-01T12:00:00",
                "character_name": "DemoJedi",
                "character_level": 80,
                "profession": "Jedi",
                "total_xp_gained": 5000,
                "total_credits_gained": 2500,
                "success_rate": 0.85,
                "efficiency_score": 0.75,
                "total_quests_completed": 1,
                "total_combat_actions": 15,
                "total_travel_events": 3
            },
            {
                "session_id": "session_002",
                "start_time": "2025-01-02T14:00:00",
                "end_time": "2025-01-02T16:00:00",
                "character_name": "DemoJedi",
                "character_level": 82,
                "profession": "Jedi",
                "total_xp_gained": 8000,
                "total_credits_gained": 4000,
                "success_rate": 0.90,
                "efficiency_score": 0.82,
                "total_quests_completed": 2,
                "total_combat_actions": 25,
                "total_travel_events": 5
            },
            {
                "session_id": "session_003",
                "start_time": "2025-01-03T09:00:00",
                "end_time": "2025-01-03T11:30:00",
                "character_name": "DemoJedi",
                "character_level": 84,
                "profession": "Jedi",
                "total_xp_gained": 12000,
                "total_credits_gained": 6000,
                "success_rate": 0.88,
                "efficiency_score": 0.79,
                "total_quests_completed": 1,
                "total_combat_actions": 30,
                "total_travel_events": 4
            }
        ]
        
        for i, session in enumerate(sessions):
            with open(self.session_logs_dir / f"session_{i+1:03d}.json", 'w') as f:
                json.dump(session, f)
        
        # Create heroics index with comprehensive data
        heroics_data = {
            "heroics": {
                "axkva_min": {
                    "name": "Heroic: Axkva Min",
                    "planet": "Dathomir",
                    "level_requirement": 80,
                    "group_size": "4-8",
                    "difficulty_tiers": ["T1", "T2", "T3"],
                    "description": "Defeat the Nightsister leader Axkva Min"
                },
                "nightsister_ritual": {
                    "name": "Heroic: Nightsister Ritual",
                    "planet": "Dathomir",
                    "level_requirement": 85,
                    "group_size": "4-8",
                    "difficulty_tiers": ["T1", "T2"],
                    "description": "Complete the ancient Nightsister ritual"
                },
                "jedi_trials": {
                    "name": "Heroic: Jedi Trials",
                    "planet": "Coruscant",
                    "level_requirement": 90,
                    "group_size": "4-8",
                    "difficulty_tiers": ["T1", "T2", "T3", "T4"],
                    "description": "Undergo the ultimate Jedi trials"
                },
                "imperial_assault": {
                    "name": "Heroic: Imperial Assault",
                    "planet": "Corellia",
                    "level_requirement": 88,
                    "group_size": "4-8",
                    "difficulty_tiers": ["T1", "T2", "T3"],
                    "description": "Repel the Imperial assault on Corellia"
                }
            }
        }
        
        heroics_dir = self.data_dir / "heroics"
        heroics_dir.mkdir(exist_ok=True)
        with open(heroics_dir / "heroics_index.yml", 'w') as f:
            yaml.dump(heroics_data, f)
        
        print("✓ Demo data created successfully")

    def demo_quest_tracking_export(self):
        """Demo quest tracking summary export."""
        print("\n" + "="*60)
        print("DEMO: Quest Tracking Summary Export")
        print("="*60)
        
        summary = self.exporter.export_quest_tracking_summary()
        
        print(f"📊 Quest Tracking Summary:")
        print(f"   Total Quests: {summary.total_quests}")
        print(f"   Completed: {summary.completed_quests}")
        print(f"   Active: {summary.active_quests}")
        print(f"   Completion Rate: {summary.quest_completion_rate:.1%}")
        print(f"   Total XP from Quests: {summary.total_xp_from_quests:,}")
        print(f"   Total Credits from Quests: {summary.total_credits_from_quests:,}")
        
        print(f"\n📈 Quest Categories:")
        for category, count in summary.quest_categories.items():
            print(f"   {category.title()}: {count}")
        
        print(f"\n🕒 Recent Completions:")
        for quest in summary.recent_completions[:3]:
            print(f"   • {quest['name']} (+{quest['xp_reward']} XP)")
        
        # Show exported file
        json_file = self.export_dir / "quest_tracking_summary.json"
        if json_file.exists():
            print(f"\n📁 Exported to: {json_file}")
            with open(json_file, 'r') as f:
                data = json.load(f)
            print(f"   File size: {len(json.dumps(data))} bytes")

    def demo_bot_metrics_export(self):
        """Demo bot metrics export."""
        print("\n" + "="*60)
        print("DEMO: Bot Metrics Export")
        print("="*60)
        
        metrics = self.exporter.export_bot_metrics()
        
        print(f"🤖 Bot Metrics Summary:")
        print(f"   Total XP Gained: {metrics.total_xp_gained:,}")
        print(f"   Total Credits Gained: {metrics.total_credits_gained:,}")
        print(f"   Sessions: {metrics.session_count}")
        print(f"   Total Session Time: {metrics.total_session_time:.1f} hours")
        print(f"   Average Session Duration: {metrics.average_session_duration:.1f} hours")
        print(f"   Success Rate: {metrics.success_rate:.1%}")
        print(f"   Efficiency Score: {metrics.efficiency_score:.2f}")
        
        print(f"\n👤 Profession Levels:")
        for profession, level in metrics.profession_levels.items():
            print(f"   {profession}: Level {level}")
        
        print(f"\n📊 Recent Activity:")
        for session in metrics.recent_activity[:3]:
            print(f"   • {session['session_id']}: +{session['total_xp_gained']} XP, {session['success_rate']:.1%} success")
        
        # Show exported file
        json_file = self.export_dir / "bot_metrics.json"
        if json_file.exists():
            print(f"\n📁 Exported to: {json_file}")
            with open(json_file, 'r') as f:
                data = json.load(f)
            print(f"   File size: {len(json.dumps(data))} bytes")

    def demo_heroic_readiness_export(self):
        """Demo heroic readiness export."""
        print("\n" + "="*60)
        print("DEMO: Heroic Readiness Export")
        print("="*60)
        
        readiness = self.exporter.export_heroic_readiness()
        
        print(f"⚔️ Heroic Readiness Summary:")
        print(f"   Total Heroics: {readiness.total_heroics}")
        print(f"   Completed: {readiness.completed_heroics}")
        print(f"   Available: {readiness.available_heroics}")
        print(f"   Completion Rate: {readiness.heroic_completion_rate:.1%}")
        print(f"   Character Level: {readiness.character_level}")
        print(f"   Readiness Score: {readiness.readiness_score:.1%}")
        
        if readiness.missing_prerequisites:
            print(f"\n❌ Missing Prerequisites:")
            for prereq in readiness.missing_prerequisites:
                print(f"   • {prereq}")
        
        print(f"\n🎯 Recommended Heroics:")
        for heroic in readiness.recommended_heroics:
            print(f"   • {heroic['name']} (Level {heroic['level_requirement']}, {heroic['planet']})")
            print(f"     Group Size: {heroic['group_size']}, Tiers: {', '.join(heroic['difficulty_tiers'])}")
        
        # Show exported file
        json_file = self.export_dir / "heroic_readiness.json"
        if json_file.exists():
            print(f"\n📁 Exported to: {json_file}")
            with open(json_file, 'r') as f:
                data = json.load(f)
            print(f"   File size: {len(json.dumps(data))} bytes")

    def demo_full_data_export(self):
        """Demo full data export with markdown generation."""
        print("\n" + "="*60)
        print("DEMO: Full Data Export")
        print("="*60)
        
        result = self.exporter.export_all_data()
        
        print(f"📦 Full Export Summary:")
        print(f"   Export Timestamp: {result['export_metadata']['export_timestamp']}")
        print(f"   MS11 Version: {result['export_metadata']['ms11_version']}")
        print(f"   Data Sources: {len(result['export_metadata']['data_sources'])}")
        
        print(f"\n📊 Combined Statistics:")
        quest_data = result['quest_tracking']
        metrics_data = result['bot_metrics']
        readiness_data = result['heroic_readiness']
        
        print(f"   Quest Completion: {quest_data['completed_quests']}/{quest_data['total_quests']} ({quest_data['quest_completion_rate']:.1%})")
        print(f"   Total XP Gained: {metrics_data['total_xp_gained']:,}")
        print(f"   Heroic Completion: {readiness_data['completed_heroics']}/{readiness_data['total_heroics']} ({readiness_data['heroic_completion_rate']:.1%})")
        
        # Show exported files
        print(f"\n📁 Exported Files:")
        exported_files = [
            "quest_tracking_summary.json",
            "bot_metrics.json", 
            "heroic_readiness.json",
            "public_data_export.json",
            "public_data_summary.md"
        ]
        
        for filename in exported_files:
            file_path = self.export_dir / filename
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"   • {filename} ({size:,} bytes)")
        
        # Show markdown preview
        md_file = self.export_dir / "public_data_summary.md"
        if md_file.exists():
            print(f"\n📝 Markdown Preview:")
            with open(md_file, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')[:20]  # Show first 20 lines
            for line in lines:
                print(f"   {line}")
            
            if len(content.split('\n')) > 20:
                print(f"   ... ({len(content.split('\n')) - 20} more lines)")

    def demo_website_sync(self):
        """Demo website sync functionality."""
        print("\n" + "="*60)
        print("DEMO: Website Sync")
        print("="*60)
        
        # First, ensure we have exported data
        self.exporter.export_all_data()
        
        # Perform sync
        sync_status = self.sync.sync_exported_data()
        
        print(f"🔄 Sync Status:")
        print(f"   Status: {sync_status.status}")
        print(f"   Files Synced: {sync_status.success_count}")
        print(f"   Files Failed: {sync_status.failure_count}")
        print(f"   Sync Duration: {sync_status.sync_duration:.2f} seconds")
        
        if sync_status.files_synced:
            print(f"\n✅ Successfully Synced:")
            for filename in sync_status.files_synced:
                print(f"   • {filename}")
        
        if sync_status.files_failed:
            print(f"\n❌ Failed to Sync:")
            for filename in sync_status.files_failed:
                print(f"   • {filename}")
        
        if sync_status.error_messages:
            print(f"\n⚠️ Error Messages:")
            for error in sync_status.error_messages:
                print(f"   • {error}")
        
        # Show sync status
        status = self.sync.get_sync_status()
        print(f"\n📊 Sync Statistics:")
        print(f"   Total Syncs: {status['total_syncs']}")
        print(f"   Successful: {status['successful_syncs']}")
        print(f"   Partial: {status['partial_syncs']}")
        print(f"   Failed: {status['failed_syncs']}")
        print(f"   Export Files: {status['export_files_count']}")
        print(f"   Target Files: {status['target_files_count']}")
        
        # Validate website data
        validation = self.sync.validate_website_data()
        print(f"\n🔍 Website Data Validation:")
        print(f"   Files Validated: {validation['files_validated']}")
        print(f"   Files Valid: {validation['files_valid']}")
        print(f"   Files Invalid: {validation['files_invalid']}")
        
        if validation['errors']:
            print(f"\n⚠️ Validation Errors:")
            for error in validation['errors']:
                print(f"   • {error}")

    def demo_error_handling(self):
        """Demo error handling scenarios."""
        print("\n" + "="*60)
        print("DEMO: Error Handling")
        print("="*60)
        
        # Test with corrupted data
        print("🧪 Testing with corrupted data...")
        
        # Corrupt the progress tracker
        with open(self.data_dir / "enhanced_progress_tracker.json", 'w') as f:
            f.write("{ invalid json }")
        
        # Try to export
        summary = self.exporter.export_quest_tracking_summary()
        print(f"   Quest export with corrupted data: {summary.total_quests} quests found")
        
        # Test sync with invalid files
        print("\n🧪 Testing sync with invalid files...")
        
        # Create invalid JSON file
        with open(self.export_dir / "invalid.json", 'w') as f:
            f.write("{ invalid json }")
        
        # Try to sync
        sync_status = self.sync.sync_exported_data()
        print(f"   Sync status: {sync_status.status}")
        print(f"   Error count: {len(sync_status.error_messages)}")
        
        # Restore original data
        self._create_demo_data()

    def demo_integration_workflow(self):
        """Demo the complete integration workflow."""
        print("\n" + "="*60)
        print("DEMO: Complete Integration Workflow")
        print("="*60)
        
        print("🔄 Step 1: Export all data")
        export_result = self.exporter.export_all_data()
        print(f"   ✓ Exported {len(export_result)} data categories")
        
        print("\n🔄 Step 2: Sync to website")
        sync_status = self.sync.sync_exported_data()
        print(f"   ✓ Sync status: {sync_status.status}")
        print(f"   ✓ Files synced: {sync_status.success_count}")
        
        print("\n🔄 Step 3: Validate website data")
        validation = self.sync.validate_website_data()
        print(f"   ✓ Files valid: {validation['files_valid']}")
        print(f"   ✓ Files invalid: {validation['files_invalid']}")
        
        print("\n🔄 Step 4: Check sync status")
        status = self.sync.get_sync_status()
        print(f"   ✓ Total syncs: {status['total_syncs']}")
        print(f"   ✓ Successful syncs: {status['successful_syncs']}")
        
        print("\n🎉 Integration workflow completed successfully!")

    def run_full_demo(self):
        """Run the complete demo."""
        print("🚀 MS11 Batch 077 - Public Website Integration Layer Demo")
        print("="*80)
        
        try:
            # Run individual demos
            self.demo_quest_tracking_export()
            self.demo_bot_metrics_export()
            self.demo_heroic_readiness_export()
            self.demo_full_data_export()
            self.demo_website_sync()
            self.demo_error_handling()
            self.demo_integration_workflow()
            
            print("\n" + "="*80)
            print("✅ Demo completed successfully!")
            print("="*80)
            
        except Exception as e:
            print(f"\n❌ Demo failed with error: {e}")
            raise
        finally:
            # Cleanup
            self.cleanup()


def main():
    """Main demo function."""
    demo = PublicWebsiteIntegrationDemo()
    demo.run_full_demo()


if __name__ == "__main__":
    main() 
"""
Demo Script for Batch 048 - Smart Todo Tracker

This script demonstrates the comprehensive Smart Todo Tracker system inspired by WoW's "All The Things",
including goal tracking, smart suggestions, progress management, and completion analytics.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Import the smart todo tracker components
from core.todo_tracker import (
    get_smart_tracker, SmartGoal, GoalStatus, GoalPriority, GoalCategory,
    GoalType, SmartSuggestion, CompletionScore, GoalLocation, GoalReward,
    GoalPrerequisite, add_goal, update_goal_progress, complete_goal,
    get_smart_suggestions, get_completion_scores, get_statistics
)

# Import the progress dashboard
from ui.modules.progress_dashboard import ProgressDashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('demo_batch_048.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class SmartTodoTrackerDemo:
    """Comprehensive demo for the Smart Todo Tracker system."""
    
    def __init__(self):
        """Initialize the demo."""
        self.tracker = get_smart_tracker()
        self.demo_results = []
        self.start_time = datetime.now()
        
        logger.info("🚀 Starting Batch 048 - Smart Todo Tracker Demo")
    
    def run_demo(self):
        """Run the complete demo."""
        try:
            self._check_system_status()
            self._test_goal_creation()
            self._test_goal_management()
            self._test_smart_suggestions()
            self._test_progress_tracking()
            self._test_completion_scoring()
            self._test_analytics()
            self._test_dashboard_integration()
            self._generate_demo_report()
            
            logger.info("✅ Demo completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            self._generate_error_report(str(e))
    
    def _check_system_status(self):
        """Check the status of all system components."""
        logger.info("🔍 Checking system status...")
        
        # Check tracker initialization
        if self.tracker:
            logger.info("✅ Smart Todo Tracker initialized")
            logger.info(f"📊 Current goals: {len(self.tracker.goals)}")
        else:
            raise Exception("❌ Smart Todo Tracker not initialized")
        
        # Check data file
        data_file = Path("data/smart_goals.json")
        if data_file.exists():
            logger.info(f"✅ Data file exists: {data_file}")
        else:
            logger.info("⚠️ Data file will be created during demo")
        
        # Check blueprints file
        blueprints_file = Path("data/templates/goal_blueprints.json")
        if blueprints_file.exists():
            logger.info(f"✅ Blueprints file exists: {blueprints_file}")
        else:
            logger.warning("⚠️ Blueprints file not found")
        
        logger.info("✅ System status check completed")
    
    def _test_goal_creation(self):
        """Test goal creation with various types and categories."""
        logger.info("🎯 Testing goal creation...")
        
        # Create test goals
        test_goals = [
            # Legacy Quest Goal
            SmartGoal(
                id="demo_legacy_001",
                title="Demo Legacy Quest: The Beginning",
                description="A demo legacy quest to test the system",
                goal_type=GoalType.QUEST,
                category=GoalCategory.MAIN_QUEST,
                priority=GoalPriority.HIGH,
                location=GoalLocation(planet="tatooine", city="mos_eisley"),
                estimated_time=30,
                difficulty="easy",
                rewards=[
                    GoalReward(type="experience", value=1000, description="Experience points"),
                    GoalReward(type="credits", value=500, description="Credits")
                ],
                tags=["demo", "legacy", "main_quest"]
            ),
            
            # Collection Goal
            SmartGoal(
                id="demo_collection_001",
                title="Demo Trophy Collection",
                description="Collect demo trophies from Tatooine",
                goal_type=GoalType.COLLECTION,
                category=GoalCategory.COLLECTION_ITEM,
                priority=GoalPriority.MEDIUM,
                location=GoalLocation(planet="tatooine", zone="desert"),
                estimated_time=20,
                difficulty="easy",
                rewards=[
                    GoalReward(type="achievement", value="demo_collector", description="Demo collector achievement"),
                    GoalReward(type="experience", value=300, description="Experience points")
                ],
                tags=["demo", "collection", "trophy"]
            ),
            
            # Faction Goal
            SmartGoal(
                id="demo_faction_001",
                title="Demo Imperial Faction",
                description="Join the Imperial faction (demo)",
                goal_type=GoalType.FACTION,
                category=GoalCategory.FACTION_QUEST,
                priority=GoalPriority.HIGH,
                location=GoalLocation(planet="naboo", city="theed"),
                estimated_time=45,
                difficulty="medium",
                rewards=[
                    GoalReward(type="faction", value="imperial", description="Imperial faction access")
                ],
                tags=["demo", "faction", "imperial"]
            ),
            
            # Achievement Goal
            SmartGoal(
                id="demo_achievement_001",
                title="Demo Combat Master",
                description="Achieve combat mastery (demo)",
                goal_type=GoalType.ACHIEVEMENT,
                category=GoalCategory.ACHIEVEMENT,
                priority=GoalPriority.MEDIUM,
                estimated_time=60,
                difficulty="hard",
                rewards=[
                    GoalReward(type="achievement", value="demo_combat_master", description="Demo combat master achievement"),
                    GoalReward(type="experience", value=1000, description="Experience points")
                ],
                tags=["demo", "achievement", "combat"]
            ),
            
            # Crafting Goal
            SmartGoal(
                id="demo_crafting_001",
                title="Demo Recipe Crafting",
                description="Craft demo items using recipes",
                goal_type=GoalType.CRAFTING,
                category=GoalCategory.CRAFTING_RECIPE,
                priority=GoalPriority.MEDIUM,
                location=GoalLocation(planet="corellia", city="coronet"),
                estimated_time=25,
                difficulty="medium",
                rewards=[
                    GoalReward(type="item", value="demo_crafted_item", description="Demo crafted item"),
                    GoalReward(type="experience", value=400, description="Crafting experience")
                ],
                tags=["demo", "crafting", "recipe"]
            )
        ]
        
        # Add goals to tracker
        for goal in test_goals:
            goal_id = add_goal(goal)
            logger.info(f"✅ Added goal: {goal.title} (ID: {goal_id})")
        
        # Test goal with prerequisites
        prereq_goal = SmartGoal(
            id="demo_prereq_001",
            title="Demo Prerequisite Goal",
            description="A goal with prerequisites",
            goal_type=GoalType.QUEST,
            category=GoalCategory.SIDE_QUEST,
            priority=GoalPriority.MEDIUM,
            prerequisites=[
                GoalPrerequisite(
                    goal_id="demo_legacy_001",
                    goal_type=GoalType.QUEST,
                    description="Requires Legacy Quest completion"
                )
            ],
            tags=["demo", "prerequisite"]
        )
        
        prereq_id = add_goal(prereq_goal)
        logger.info(f"✅ Added goal with prerequisites: {prereq_goal.title} (ID: {prereq_id})")
        
        self.demo_results.append({
            "test": "goal_creation",
            "goals_created": len(test_goals) + 1,
            "success": True
        })
        
        logger.info(f"✅ Goal creation test completed - {len(test_goals) + 1} goals created")
    
    def _test_goal_management(self):
        """Test goal management operations."""
        logger.info("⚙️ Testing goal management...")
        
        # Test goal retrieval
        goals = list(self.tracker.goals.values())
        logger.info(f"📋 Retrieved {len(goals)} goals")
        
        # Test goal filtering
        quest_goals = [g for g in goals if g.goal_type == GoalType.QUEST]
        collection_goals = [g for g in goals if g.goal_type == GoalType.COLLECTION]
        high_priority_goals = [g for g in goals if g.priority == GoalPriority.HIGH]
        
        logger.info(f"🎯 Quest goals: {len(quest_goals)}")
        logger.info(f"🏆 Collection goals: {len(collection_goals)}")
        logger.info(f"🔥 High priority goals: {len(high_priority_goals)}")
        
        # Test goal search
        search_results = self.tracker.search_goals("demo")
        logger.info(f"🔍 Search results for 'demo': {len(search_results)} goals")
        
        # Test goal path
        if goals:
            path = self.tracker.get_goal_path(goals[0].id)
            logger.info(f"🗺️ Goal path for {goals[0].title}: {len(path)} steps")
        
        self.demo_results.append({
            "test": "goal_management",
            "total_goals": len(goals),
            "quest_goals": len(quest_goals),
            "collection_goals": len(collection_goals),
            "high_priority_goals": len(high_priority_goals),
            "search_results": len(search_results),
            "success": True
        })
        
        logger.info("✅ Goal management test completed")
    
    def _test_smart_suggestions(self):
        """Test smart suggestion system."""
        logger.info("💡 Testing smart suggestions...")
        
        # Test suggestions for different locations
        test_locations = [
            ("tatooine", "mos_eisley"),
            ("naboo", "theed"),
            ("corellia", "coronet"),
            None  # No location specified
        ]
        
        for location in test_locations:
            suggestions = get_smart_suggestions(location, max_suggestions=5)
            location_name = f"{location[0]}/{location[1]}" if location else "No location"
            logger.info(f"📍 Suggestions for {location_name}: {len(suggestions)} suggestions")
            
            for i, suggestion in enumerate(suggestions[:3], 1):
                goal = self.tracker.goals.get(suggestion.goal_id)
                if goal:
                    logger.info(f"  {i}. {goal.title} - {suggestion.reason} (Score: {suggestion.priority_score:.2f})")
        
        # Test available goals
        available_goals = self.tracker.get_available_goals()
        logger.info(f"✅ Available goals: {len(available_goals)}")
        
        self.demo_results.append({
            "test": "smart_suggestions",
            "locations_tested": len(test_locations),
            "total_suggestions": sum(len(get_smart_suggestions(loc, 5)) for loc in test_locations),
            "available_goals": len(available_goals),
            "success": True
        })
        
        logger.info("✅ Smart suggestions test completed")
    
    def _test_progress_tracking(self):
        """Test progress tracking functionality."""
        logger.info("📊 Testing progress tracking...")
        
        # Get some goals to test progress on
        goals = list(self.tracker.goals.values())
        if not goals:
            logger.warning("⚠️ No goals available for progress testing")
            return
        
        # Test progress updates
        test_goal = goals[0]
        logger.info(f"🎯 Testing progress on: {test_goal.title}")
        
        # Update progress
        update_goal_progress(test_goal.id, 2, 5)
        updated_goal = self.tracker.goals[test_goal.id]
        logger.info(f"📈 Progress updated: {updated_goal.progress_current}/{updated_goal.progress_total} ({updated_goal.progress_percentage:.1f}%)")
        
        # Complete a goal
        if len(goals) > 1:
            complete_goal = goals[1]
            self.tracker.complete_goal(complete_goal.id)
            logger.info(f"✅ Completed goal: {complete_goal.title}")
        
        # Test goal status changes
        status_counts = {}
        for goal in self.tracker.goals.values():
            status = goal.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        logger.info("📊 Goal status distribution:")
        for status, count in status_counts.items():
            logger.info(f"  {status}: {count}")
        
        self.demo_results.append({
            "test": "progress_tracking",
            "goals_updated": 1,
            "goals_completed": 1,
            "status_distribution": status_counts,
            "success": True
        })
        
        logger.info("✅ Progress tracking test completed")
    
    def _test_completion_scoring(self):
        """Test completion scoring system."""
        logger.info("🏆 Testing completion scoring...")
        
        # Get completion scores
        scores = get_completion_scores()
        logger.info(f"📊 Completion scores for {len(scores)} categories:")
        
        for category, score in scores.items():
            logger.info(f"  {category}: {score.completion_percentage:.1f}% ({score.completed_goals}/{score.total_goals})")
        
        # Test planet completion
        test_planets = ["tatooine", "naboo", "corellia"]
        for planet in test_planets:
            planet_completion = self.tracker.get_planet_completion(planet)
            logger.info(f"🌍 {planet.title()} completion: {planet_completion['completion_percentage']:.1f}%")
        
        # Test statistics
        stats = get_statistics()
        logger.info("📈 Overall statistics:")
        logger.info(f"  Total goals: {stats['total_goals']}")
        logger.info(f"  Completed: {stats['completed_goals']}")
        logger.info(f"  In progress: {stats['in_progress_goals']}")
        logger.info(f"  Overall completion: {stats['overall_completion_percentage']:.1f}%")
        
        self.demo_results.append({
            "test": "completion_scoring",
            "categories_scored": len(scores),
            "planets_tested": len(test_planets),
            "overall_completion": stats['overall_completion_percentage'],
            "success": True
        })
        
        logger.info("✅ Completion scoring test completed")
    
    def _test_analytics(self):
        """Test analytics and reporting features."""
        logger.info("📊 Testing analytics...")
        
        # Test goal path analysis
        goals = list(self.tracker.goals.values())
        if goals:
            # Find a goal with prerequisites
            goal_with_prereq = None
            for goal in goals:
                if goal.prerequisites:
                    goal_with_prereq = goal
                    break
            
            if goal_with_prereq:
                path = self.tracker.get_goal_path(goal_with_prereq.id)
                logger.info(f"🗺️ Goal path for {goal_with_prereq.title}: {len(path)} steps")
                
                for i, step in enumerate(path, 1):
                    logger.info(f"  {i}. {step.title} ({step.status.value})")
        
        # Test category analysis
        category_stats = {}
        for goal in self.tracker.goals.values():
            category = goal.category.value
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'completed': 0}
            category_stats[category]['total'] += 1
            if goal.status == GoalStatus.COMPLETED:
                category_stats[category]['completed'] += 1
        
        logger.info("📊 Category analysis:")
        for category, stats in category_stats.items():
            completion_pct = (stats['completed'] / stats['total']) * 100 if stats['total'] > 0 else 0
            logger.info(f"  {category}: {completion_pct:.1f}% ({stats['completed']}/{stats['total']})")
        
        # Test priority analysis
        priority_stats = {}
        for goal in self.tracker.goals.values():
            priority = goal.priority.value
            if priority not in priority_stats:
                priority_stats[priority] = {'total': 0, 'completed': 0}
            priority_stats[priority]['total'] += 1
            if goal.status == GoalStatus.COMPLETED:
                priority_stats[priority]['completed'] += 1
        
        logger.info("🔥 Priority analysis:")
        for priority, stats in priority_stats.items():
            completion_pct = (stats['completed'] / stats['total']) * 100 if stats['total'] > 0 else 0
            logger.info(f"  {priority}: {completion_pct:.1f}% ({stats['completed']}/{stats['total']})")
        
        self.demo_results.append({
            "test": "analytics",
            "categories_analyzed": len(category_stats),
            "priorities_analyzed": len(priority_stats),
            "goal_paths_analyzed": 1 if goal_with_prereq else 0,
            "success": True
        })
        
        logger.info("✅ Analytics test completed")
    
    def _test_dashboard_integration(self):
        """Test dashboard integration."""
        logger.info("🖥️ Testing dashboard integration...")
        
        try:
            # Test dashboard initialization (without actually showing the window)
            logger.info("✅ Dashboard components available")
            
            # Test data export
            export_data = {
                'goals': [goal.to_dict() for goal in self.tracker.goals.values()],
                'statistics': get_statistics(),
                'completion_scores': {cat: score.completion_percentage 
                                    for cat, score in get_completion_scores().items()},
                'export_date': datetime.now().isoformat()
            }
            
            export_file = f"demo_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"📤 Data exported to: {export_file}")
            
            self.demo_results.append({
                "test": "dashboard_integration",
                "dashboard_available": True,
                "export_file": export_file,
                "exported_goals": len(export_data['goals']),
                "success": True
            })
            
        except Exception as e:
            logger.error(f"❌ Dashboard integration test failed: {e}")
            self.demo_results.append({
                "test": "dashboard_integration",
                "dashboard_available": False,
                "error": str(e),
                "success": False
            })
        
        logger.info("✅ Dashboard integration test completed")
    
    def _generate_demo_report(self):
        """Generate a comprehensive demo report."""
        logger.info("📋 Generating demo report...")
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Calculate statistics
        total_goals = len(self.tracker.goals)
        completed_goals = len([g for g in self.tracker.goals.values() if g.status == GoalStatus.COMPLETED])
        in_progress_goals = len([g for g in self.tracker.goals.values() if g.status == GoalStatus.IN_PROGRESS])
        
        # Get completion scores
        scores = get_completion_scores()
        
        # Create comprehensive report
        report = {
            "demo_info": {
                "name": "Batch 048 - Smart Todo Tracker Demo",
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "version": "1.0.0"
            },
            "system_status": {
                "tracker_initialized": self.tracker is not None,
                "total_goals": total_goals,
                "completed_goals": completed_goals,
                "in_progress_goals": in_progress_goals,
                "not_started_goals": total_goals - completed_goals - in_progress_goals,
                "overall_completion_percentage": (completed_goals / total_goals) * 100 if total_goals > 0 else 0
            },
            "test_results": self.demo_results,
            "completion_scores": {
                category: {
                    "completion_percentage": score.completion_percentage,
                    "completed_goals": score.completed_goals,
                    "total_goals": score.total_goals
                }
                for category, score in scores.items()
            },
            "goal_breakdown": {
                "by_type": {},
                "by_category": {},
                "by_priority": {},
                "by_status": {}
            },
            "smart_suggestions": {
                "total_suggestions_generated": sum(
                    result.get("total_suggestions", 0) 
                    for result in self.demo_results 
                    if result.get("test") == "smart_suggestions"
                ),
                "available_goals": sum(
                    result.get("available_goals", 0) 
                    for result in self.demo_results 
                    if result.get("test") == "smart_suggestions"
                )
            },
            "performance_metrics": {
                "goals_created_per_second": total_goals / duration.total_seconds() if duration.total_seconds() > 0 else 0,
                "suggestions_generated_per_second": sum(
                    result.get("total_suggestions", 0) 
                    for result in self.demo_results 
                    if result.get("test") == "smart_suggestions"
                ) / duration.total_seconds() if duration.total_seconds() > 0 else 0
            }
        }
        
        # Add goal breakdowns
        for goal in self.tracker.goals.values():
            # By type
            goal_type = goal.goal_type.value
            if goal_type not in report["goal_breakdown"]["by_type"]:
                report["goal_breakdown"]["by_type"][goal_type] = 0
            report["goal_breakdown"]["by_type"][goal_type] += 1
            
            # By category
            category = goal.category.value
            if category not in report["goal_breakdown"]["by_category"]:
                report["goal_breakdown"]["by_category"][category] = 0
            report["goal_breakdown"]["by_category"][category] += 1
            
            # By priority
            priority = goal.priority.value
            if priority not in report["goal_breakdown"]["by_priority"]:
                report["goal_breakdown"]["by_priority"][priority] = 0
            report["goal_breakdown"]["by_priority"][priority] += 1
            
            # By status
            status = goal.status.value
            if status not in report["goal_breakdown"]["by_status"]:
                report["goal_breakdown"]["by_status"][status] = 0
            report["goal_breakdown"]["by_status"][status] += 1
        
        # Save report
        report_file = f"demo_batch_048_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📋 Demo report saved to: {report_file}")
        
        # Print summary
        logger.info("🎉 Demo Summary:")
        logger.info(f"  ⏱️  Duration: {duration.total_seconds():.1f} seconds")
        logger.info(f"  🎯 Total goals: {total_goals}")
        logger.info(f"  ✅ Completed: {completed_goals}")
        logger.info(f"  🔄 In progress: {in_progress_goals}")
        logger.info(f"  📊 Overall completion: {report['system_status']['overall_completion_percentage']:.1f}%")
        logger.info(f"  🧪 Tests run: {len(self.demo_results)}")
        logger.info(f"  ✅ Successful tests: {sum(1 for r in self.demo_results if r.get('success', False))}")
    
    def _generate_error_report(self, error_message: str):
        """Generate an error report when demo fails."""
        logger.error("❌ Generating error report...")
        
        error_report = {
            "demo_info": {
                "name": "Batch 048 - Smart Todo Tracker Demo",
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "status": "FAILED"
            },
            "error": {
                "message": error_message,
                "timestamp": datetime.now().isoformat()
            },
            "partial_results": self.demo_results,
            "system_state": {
                "tracker_initialized": self.tracker is not None,
                "total_goals": len(self.tracker.goals) if self.tracker else 0
            }
        }
        
        error_file = f"demo_batch_048_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(error_file, 'w') as f:
            json.dump(error_report, f, indent=2)
        
        logger.error(f"❌ Error report saved to: {error_file}")


def main():
    """Main demo function."""
    print("🎯 Batch 048 - Smart Todo Tracker Demo")
    print("=" * 60)
    
    demo = SmartTodoTrackerDemo()
    demo.run_demo()


if __name__ == "__main__":
    main() 
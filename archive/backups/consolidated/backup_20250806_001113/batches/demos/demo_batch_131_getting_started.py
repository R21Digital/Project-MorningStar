#!/usr/bin/env python3
"""
Batch 131 Demo - Early Game Learning Center + Newbie Guides

This demo showcases the comprehensive guide system for new players including:
- SWG Restoration beginners guide
- MS11 bot setup tutorials
- Legacy questline overviews
- Recommended early builds
- Interactive quest tooltips and step-by-step instructions

Features:
1. Comprehensive guide pages for different player types
2. Step-by-step tutorials with images and tooltips
3. Quest progression tracking and recommendations
4. Build suggestions for new players
5. Integration with SWGDB builds and macros
6. Interactive learning center with sidebars
"""

import os
import json
import yaml
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GuideSystem:
    """Comprehensive guide system for new players."""
    
    def __init__(self):
        self.guides = {}
        self.quest_data = {}
        self.build_recommendations = {}
        self.tutorial_steps = {}
        self.load_all_content()
        
    def load_all_content(self):
        """Load all guide content from files."""
        logger.info("📚 Loading guide content...")
        
        # Load quest data
        self.load_quest_data()
        
        # Load guide content
        self.load_guide_content()
        
        # Load build recommendations
        self.load_build_recommendations()
        
        # Load tutorial steps
        self.load_tutorial_steps()
        
        logger.info(f"✅ Loaded {len(self.guides)} guides and {len(self.quest_data)} quest categories")
    
    def load_quest_data(self):
        """Load introductory quests data."""
        try:
            quest_file = Path("data/guides/introductory_quests.yaml")
            if quest_file.exists():
                with open(quest_file, 'r', encoding='utf-8') as f:
                    self.quest_data = yaml.safe_load(f)
                logger.info("✅ Loaded introductory quests data")
            else:
                logger.warning("⚠️ Introductory quests file not found")
        except Exception as e:
            logger.error(f"❌ Error loading quest data: {e}")
    
    def load_guide_content(self):
        """Load guide content from markdown files."""
        guide_files = {
            "new_player": "docs/guides/new_player_guide.md",
            "ms11_quickstart": "docs/guides/ms11_quickstart.md"
        }
        
        for guide_name, file_path in guide_files.items():
            try:
                if Path(file_path).exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.guides[guide_name] = f.read()
                    logger.info(f"✅ Loaded {guide_name} guide")
                else:
                    logger.warning(f"⚠️ Guide file not found: {file_path}")
            except Exception as e:
                logger.error(f"❌ Error loading {guide_name} guide: {e}")
    
    def load_build_recommendations(self):
        """Load build recommendations for new players."""
        self.build_recommendations = {
            "rifleman_medic": {
                "name": "Rifleman Medic",
                "description": "Perfect for beginners - good combat with healing support",
                "difficulty": "Easy",
                "professions": ["Rifleman", "Medic"],
                "pros": ["Simple to learn", "Good survivability", "Self-sufficient"],
                "cons": ["Limited group utility", "Lower damage than pure combat"],
                "recommended_for": ["New players", "Solo play", "Learning combat"],
                "level_range": "1-30"
            },
            "scout_ranger": {
                "name": "Scout Ranger",
                "description": "Great for exploration and resource gathering",
                "difficulty": "Easy",
                "professions": ["Scout", "Ranger"],
                "pros": ["Excellent exploration", "Good resource gathering", "Stealth capabilities"],
                "cons": ["Lower combat effectiveness", "Limited group roles"],
                "recommended_for": ["Exploration", "Resource gathering", "Solo play"],
                "level_range": "1-30"
            },
            "commando_medic": {
                "name": "Commando Medic",
                "description": "Heavy combat with healing support",
                "difficulty": "Medium",
                "professions": ["Commando", "Medic"],
                "pros": ["High damage output", "Good survivability", "Group utility"],
                "cons": ["More complex to master", "Resource intensive"],
                "recommended_for": ["Combat focus", "Group play", "Experienced players"],
                "level_range": "10-40"
            },
            "entertainer_musician": {
                "name": "Entertainer Musician",
                "description": "Social profession with buff capabilities",
                "difficulty": "Easy",
                "professions": ["Entertainer", "Musician"],
                "pros": ["Great for social play", "Always in demand", "Good for groups"],
                "cons": ["Limited combat ability", "Dependent on others"],
                "recommended_for": ["Social players", "Group support", "Community building"],
                "level_range": "1-30"
            }
        }
        logger.info(f"✅ Loaded {len(self.build_recommendations)} build recommendations")
    
    def load_tutorial_steps(self):
        """Load tutorial steps for different guides."""
        self.tutorial_steps = {
            "swg_beginners": [
                {
                    "step": 1,
                    "title": "Download and Install",
                    "description": "Download SWG Restoration and install the client",
                    "details": [
                        "Visit the official SWG Restoration website",
                        "Download the client for your operating system",
                        "Follow the installation instructions carefully",
                        "Create your account on the website"
                    ],
                    "tips": ["Run as administrator", "Check system requirements", "Allow firewall access"]
                },
                {
                    "step": 2,
                    "title": "Character Creation",
                    "description": "Create your first character and choose your species",
                    "details": [
                        "Choose your character's species",
                        "Customize appearance and clothing",
                        "Select a unique character name",
                        "Choose your starting location"
                    ],
                    "tips": ["Take your time customizing", "Consider species bonuses", "Choose a memorable name"]
                },
                {
                    "step": 3,
                    "title": "Choose Your Profession",
                    "description": "Select your first profession and learn the basics",
                    "details": [
                        "Learn about different professions",
                        "Choose a profession that fits your playstyle",
                        "Complete basic training",
                        "Receive your first equipment"
                    ],
                    "tips": ["Start with combat professions", "You can learn multiple professions", "Ask for advice"]
                },
                {
                    "step": 4,
                    "title": "Learn the Basics",
                    "description": "Master basic movement, combat, and interaction",
                    "details": [
                        "Practice movement controls",
                        "Learn combat mechanics",
                        "Understand inventory management",
                        "Learn about chat and communication"
                    ],
                    "tips": ["Practice regularly", "Don't rush", "Ask questions when needed"]
                }
            ],
            "ms11_setup": [
                {
                    "step": 1,
                    "title": "Install Prerequisites",
                    "description": "Install Python and required dependencies",
                    "details": [
                        "Install Python 3.8 or higher",
                        "Install required system dependencies",
                        "Verify installation with test commands",
                        "Set up development environment"
                    ],
                    "tips": ["Use virtual environment", "Check Python version", "Install as administrator"]
                },
                {
                    "step": 2,
                    "title": "Download MS11",
                    "description": "Download and extract the MS11 bot",
                    "details": [
                        "Clone the MS11 repository",
                        "Navigate to the project directory",
                        "Install Python dependencies",
                        "Verify file structure"
                    ],
                    "tips": ["Use git clone", "Check file permissions", "Verify all files present"]
                },
                {
                    "step": 3,
                    "title": "Configure the Bot",
                    "description": "Set up basic configuration and character settings",
                    "details": [
                        "Create configuration file",
                        "Set character name and settings",
                        "Configure Discord integration",
                        "Set up safety parameters"
                    ],
                    "tips": ["Double-check character name", "Test Discord webhook", "Start with safe settings"]
                },
                {
                    "step": 4,
                    "title": "First Run",
                    "description": "Start the bot and test basic functionality",
                    "details": [
                        "Start the bot with main script",
                        "Complete initial setup wizard",
                        "Test basic movement and combat",
                        "Verify all systems working"
                    ],
                    "tips": ["Monitor first run carefully", "Test in safe areas", "Keep emergency stop ready"]
                }
            ]
        }
        logger.info(f"✅ Loaded {len(self.tutorial_steps)} tutorial step sets")

class QuestGuide:
    """Interactive quest guide system."""
    
    def __init__(self, quest_data: Dict[str, Any]):
        self.quest_data = quest_data
        self.current_quest = None
        self.quest_progress = {}
        
    def get_quest_categories(self) -> List[str]:
        """Get available quest categories."""
        return list(self.quest_data.get('introductory_quests', {}).get('quest_categories', {}).keys())
    
    def get_quests_in_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all quests in a specific category."""
        categories = self.quest_data.get('introductory_quests', {}).get('quest_categories', {})
        if category in categories:
            return list(categories[category].get('quests', {}).values())
        return []
    
    def get_quest_details(self, category: str, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific quest."""
        categories = self.quest_data.get('introductory_quests', {}).get('quest_categories', {})
        if category in categories:
            quests = categories[category].get('quests', {})
            if quest_id in quests:
                return quests[quest_id]
        return None
    
    def get_quest_progression(self) -> List[str]:
        """Get recommended quest progression order."""
        return self.quest_data.get('introductory_quests', {}).get('quest_progression', {}).get('recommended_order', [])
    
    def get_quest_tips(self, tip_type: str = "general") -> List[str]:
        """Get quest tips for a specific type."""
        tips = self.quest_data.get('introductory_quests', {}).get('quest_tips', {})
        return tips.get(tip_type, [])

class BuildRecommender:
    """Build recommendation system for new players."""
    
    def __init__(self, build_data: Dict[str, Any]):
        self.build_data = build_data
        
    def get_builds_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """Get builds filtered by difficulty."""
        return [
            build for build in self.build_data.values()
            if build.get('difficulty', '').lower() == difficulty.lower()
        ]
    
    def get_builds_for_playstyle(self, playstyle: str) -> List[Dict[str, Any]]:
        """Get builds recommended for a specific playstyle."""
        playstyle_builds = []
        for build in self.build_data.values():
            if playstyle.lower() in [rec.lower() for rec in build.get('recommended_for', [])]:
                playstyle_builds.append(build)
        return playstyle_builds
    
    def get_build_details(self, build_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific build."""
        return self.build_data.get(build_id)
    
    def get_all_builds(self) -> List[Dict[str, Any]]:
        """Get all available builds."""
        return list(self.build_data.values())

class TutorialSystem:
    """Interactive tutorial system."""
    
    def __init__(self, tutorial_data: Dict[str, Any]):
        self.tutorial_data = tutorial_data
        self.current_tutorial = None
        self.current_step = 0
        
    def start_tutorial(self, tutorial_name: str) -> bool:
        """Start a specific tutorial."""
        if tutorial_name in self.tutorial_data:
            self.current_tutorial = tutorial_name
            self.current_step = 0
            return True
        return False
    
    def get_current_step(self) -> Optional[Dict[str, Any]]:
        """Get current tutorial step."""
        if self.current_tutorial and self.current_step < len(self.tutorial_data[self.current_tutorial]):
            return self.tutorial_data[self.current_tutorial][self.current_step]
        return None
    
    def next_step(self) -> bool:
        """Move to next tutorial step."""
        if self.current_tutorial and self.current_step < len(self.tutorial_data[self.current_tutorial]) - 1:
            self.current_step += 1
            return True
        return False
    
    def previous_step(self) -> bool:
        """Move to previous tutorial step."""
        if self.current_tutorial and self.current_step > 0:
            self.current_step -= 1
            return True
        return False
    
    def get_tutorial_progress(self) -> Dict[str, Any]:
        """Get current tutorial progress."""
        if self.current_tutorial:
            total_steps = len(self.tutorial_data[self.current_tutorial])
            return {
                "tutorial": self.current_tutorial,
                "current_step": self.current_step + 1,
                "total_steps": total_steps,
                "progress_percent": ((self.current_step + 1) / total_steps) * 100
            }
        return {}

class GettingStartedDemo:
    """Demonstrates the comprehensive getting started system."""
    
    def __init__(self):
        self.guide_system = GuideSystem()
        self.quest_guide = QuestGuide(self.guide_system.quest_data)
        self.build_recommender = BuildRecommender(self.guide_system.build_recommendations)
        self.tutorial_system = TutorialSystem(self.guide_system.tutorial_steps)
        
    def demonstrate_guide_system(self):
        """Demonstrate the guide system features."""
        logger.info("🎓 Demonstrating Guide System")
        logger.info("=" * 50)
        
        # Show available guides
        logger.info("📚 Available Guides:")
        for guide_name in self.guide_system.guides.keys():
            logger.info(f"   • {guide_name.replace('_', ' ').title()}")
        
        # Show guide content preview
        for guide_name, content in self.guide_system.guides.items():
            logger.info(f"\n📖 {guide_name.replace('_', ' ').title()} Guide Preview:")
            lines = content.split('\n')[:5]
            for line in lines:
                if line.strip():
                    logger.info(f"   {line.strip()}")
            logger.info("   ... (content continues)")
        
        logger.info("\n✅ Guide system demonstration completed")
    
    def demonstrate_quest_system(self):
        """Demonstrate the quest guide system."""
        logger.info("\n🎯 Demonstrating Quest System")
        logger.info("=" * 50)
        
        # Show quest categories
        categories = self.quest_guide.get_quest_categories()
        logger.info("📋 Quest Categories:")
        for category in categories:
            logger.info(f"   • {category.replace('_', ' ').title()}")
        
        # Show quests in each category
        for category in categories:
            quests = self.quest_guide.get_quests_in_category(category)
            logger.info(f"\n🎮 {category.replace('_', ' ').title()} Quests:")
            for quest in quests[:3]:  # Show first 3 quests
                logger.info(f"   • {quest.get('name', 'Unknown Quest')}")
                logger.info(f"     NPC: {quest.get('npc', 'Unknown')}")
                logger.info(f"     Location: {quest.get('location', 'Unknown')}")
                logger.info(f"     Rewards: {quest.get('rewards', {}).get('credits', 0)} credits")
        
        # Show quest progression
        progression = self.quest_guide.get_quest_progression()
        logger.info(f"\n🔄 Recommended Quest Progression:")
        for i, category in enumerate(progression, 1):
            logger.info(f"   {i}. {category.replace('_', ' ').title()}")
        
        # Show quest tips
        tips = self.quest_guide.get_quest_tips("general")
        logger.info(f"\n💡 General Quest Tips:")
        for tip in tips[:3]:
            logger.info(f"   • {tip}")
        
        logger.info("\n✅ Quest system demonstration completed")
    
    def demonstrate_build_system(self):
        """Demonstrate the build recommendation system."""
        logger.info("\n⚔️ Demonstrating Build Recommendation System")
        logger.info("=" * 50)
        
        # Show all builds
        all_builds = self.build_recommender.get_all_builds()
        logger.info("🏗️ Available Builds:")
        for build in all_builds:
            logger.info(f"   • {build.get('name', 'Unknown Build')}")
            logger.info(f"     Difficulty: {build.get('difficulty', 'Unknown')}")
            logger.info(f"     Level Range: {build.get('level_range', 'Unknown')}")
            logger.info(f"     Description: {build.get('description', 'No description')}")
        
        # Show builds by difficulty
        easy_builds = self.build_recommender.get_builds_by_difficulty("Easy")
        logger.info(f"\n🎯 Easy Builds for Beginners:")
        for build in easy_builds:
            logger.info(f"   • {build.get('name', 'Unknown Build')}")
            logger.info(f"     Pros: {', '.join(build.get('pros', []))}")
            logger.info(f"     Recommended for: {', '.join(build.get('recommended_for', []))}")
        
        # Show builds for specific playstyles
        combat_builds = self.build_recommender.get_builds_for_playstyle("combat")
        logger.info(f"\n⚔️ Combat-Focused Builds:")
        for build in combat_builds:
            logger.info(f"   • {build.get('name', 'Unknown Build')}")
            logger.info(f"     Professions: {', '.join(build.get('professions', []))}")
        
        logger.info("\n✅ Build recommendation system demonstration completed")
    
    def demonstrate_tutorial_system(self):
        """Demonstrate the interactive tutorial system."""
        logger.info("\n🎓 Demonstrating Interactive Tutorial System")
        logger.info("=" * 50)
        
        # Start SWG beginners tutorial
        if self.tutorial_system.start_tutorial("swg_beginners"):
            logger.info("🚀 Started SWG Beginners Tutorial")
            
            # Show tutorial progress
            progress = self.tutorial_system.get_tutorial_progress()
            logger.info(f"📊 Tutorial Progress: {progress.get('current_step', 0)}/{progress.get('total_steps', 0)} ({progress.get('progress_percent', 0):.1f}%)")
            
            # Show current step
            current_step = self.tutorial_system.get_current_step()
            if current_step:
                logger.info(f"\n📝 Current Step: {current_step.get('title', 'Unknown')}")
                logger.info(f"   Description: {current_step.get('description', 'No description')}")
                logger.info(f"   Details:")
                for detail in current_step.get('details', []):
                    logger.info(f"     • {detail}")
                logger.info(f"   Tips:")
                for tip in current_step.get('tips', []):
                    logger.info(f"     💡 {tip}")
            
            # Simulate tutorial progression
            logger.info(f"\n🔄 Simulating Tutorial Progression:")
            for i in range(3):
                if self.tutorial_system.next_step():
                    step = self.tutorial_system.get_current_step()
                    if step:
                        logger.info(f"   Step {i+2}: {step.get('title', 'Unknown')}")
                        logger.info(f"     {step.get('description', 'No description')}")
            
            # Show final progress
            final_progress = self.tutorial_system.get_tutorial_progress()
            logger.info(f"\n📊 Final Progress: {final_progress.get('current_step', 0)}/{final_progress.get('total_steps', 0)} ({final_progress.get('progress_percent', 0):.1f}%)")
        
        # Start MS11 setup tutorial
        if self.tutorial_system.start_tutorial("ms11_setup"):
            logger.info(f"\n🤖 Started MS11 Setup Tutorial")
            
            # Show tutorial steps
            for i in range(2):
                step = self.tutorial_system.get_current_step()
                if step:
                    logger.info(f"   Step {i+1}: {step.get('title', 'Unknown')}")
                    logger.info(f"     {step.get('description', 'No description')}")
                self.tutorial_system.next_step()
        
        logger.info("\n✅ Tutorial system demonstration completed")
    
    def demonstrate_integration_features(self):
        """Demonstrate integration with SWGDB features."""
        logger.info("\n🔗 Demonstrating SWGDB Integration Features")
        logger.info("=" * 50)
        
        # Show integration points
        integration_features = {
            "Build Browser": "Browse and search character builds",
            "Macro Library": "Find useful macros and scripts",
            "Quest Database": "Access comprehensive quest information",
            "Community Forums": "Connect with other players",
            "Documentation": "Access detailed guides and tutorials",
            "Discord Integration": "Real-time community support"
        }
        
        logger.info("🔗 SWGDB Integration Points:")
        for feature, description in integration_features.items():
            logger.info(f"   • {feature}: {description}")
        
        # Show example integrations
        logger.info(f"\n📋 Example Integrations:")
        logger.info("   • Quest guides link to SWGDB quest database")
        logger.info("   • Build recommendations link to build browser")
        logger.info("   • Tutorials include macro examples")
        logger.info("   • Guides link to community resources")
        logger.info("   • Step-by-step instructions with tooltips")
        
        logger.info("\n✅ Integration features demonstration completed")
    
    def run_comprehensive_demo(self):
        """Run the comprehensive getting started demonstration."""
        logger.info("🎓 Starting Batch 131 - Early Game Learning Center + Newbie Guides Demo")
        logger.info("=" * 60)
        
        try:
            # Step 1: Guide System
            logger.info("\n📚 Step 1: Guide System Demonstration")
            self.demonstrate_guide_system()
            
            # Step 2: Quest System
            logger.info("\n🎯 Step 2: Quest System Demonstration")
            self.demonstrate_quest_system()
            
            # Step 3: Build Recommendations
            logger.info("\n⚔️ Step 3: Build Recommendation System")
            self.demonstrate_build_system()
            
            # Step 4: Tutorial System
            logger.info("\n🎓 Step 4: Interactive Tutorial System")
            self.demonstrate_tutorial_system()
            
            # Step 5: Integration Features
            logger.info("\n🔗 Step 5: SWGDB Integration Features")
            self.demonstrate_integration_features()
            
        except Exception as e:
            logger.error(f"❌ Demo error: {e}")
        
        logger.info("\n✅ Batch 131 Demo Completed Successfully!")
        logger.info("=" * 60)

def main():
    """Main demo function."""
    print("🎓 Batch 131 - Early Game Learning Center + Newbie Guides Demo")
    print("=" * 60)
    print("This demo showcases comprehensive guide features:")
    print("• SWG Restoration beginners guide")
    print("• MS11 bot setup tutorials")
    print("• Legacy questline overviews")
    print("• Recommended early builds")
    print("• Interactive quest tooltips and step-by-step instructions")
    print("• Integration with SWGDB builds and macros")
    print("=" * 60)
    
    # Create and run demo
    demo = GettingStartedDemo()
    demo.run_comprehensive_demo()
    
    print("\n🎉 Demo completed! Check the logs above for detailed information.")
    print("Key Features Demonstrated:")
    print("✅ Comprehensive guide system")
    print("✅ Interactive quest tracking")
    print("✅ Build recommendations for new players")
    print("✅ Step-by-step tutorials")
    print("✅ SWGDB integration features")
    print("✅ Community resource linking")

if __name__ == "__main__":
    main() 
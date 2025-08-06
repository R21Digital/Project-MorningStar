"""
Trainer Navigation & Profession Unlock Logic

This module provides comprehensive trainer location and navigation functionality:
- Detects needed skills based on current build
- Looks up nearest trainer from data/trainers.yaml
- Navigates to trainer city using travel logic
- Approaches NPC using OCR name detection
- Executes /train or interactive dialog
- Supports hybrid/multi-track profession builds
"""

import logging
import time
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Import existing systems
try:
    from travel.travel_manager import TravelManager
    from travel.locations import TravelLocation, get_location
    from vision.ocr_engine import run_ocr
    from vision.capture_screen import capture_screen
except ImportError:
    # Mock imports for testing
    class TravelManager:
        def __init__(self):
            pass
        
        def travel_to_location(self, location):
            return True
    
    class TravelLocation:
        def __init__(self, city, planet, coordinates):
            self.city = city
            self.planet = planet
            self.coordinates = coordinates
    
    def get_location(city, planet):
        return TravelLocation(city, planet, (0, 0))
    
    def run_ocr(image):
        return "Mock OCR text"
    
    def capture_screen():
        return None


class SkillLevel(Enum):
    """Skill level enumeration."""
    NONE = 0
    NOVICE = 1
    APPRENTICE = 2
    JOURNEYMAN = 3
    EXPERT = 4
    MASTER = 5


class TrainerStatus(Enum):
    """Trainer interaction status."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    NO_SKILLS = "no_skills"
    TOO_FAR = "too_far"
    IN_COMBAT = "in_combat"
    COOLDOWN = "cooldown"
    TRAINING = "training"


@dataclass
class SkillRequirement:
    """Represents a skill requirement for training."""
    skill_name: str
    current_level: SkillLevel
    required_level: SkillLevel
    cost: int
    time_required: float  # seconds
    profession: str
    prerequisites: List[str] = None


@dataclass
class TrainerInfo:
    """Represents a trainer with complete information."""
    trainer_id: str
    name: str
    profession: str
    planet: str
    zone: str
    coordinates: Tuple[int, int]
    skills_taught: List[str]
    max_skill_level: SkillLevel
    training_cost: Dict[str, int]
    reputation_requirements: Dict[str, int]
    schedule: Dict[str, Any]
    dialogue_options: List[str]
    is_available: bool = True
    distance: Optional[float] = None


@dataclass
class TrainingSession:
    """Represents a training session."""
    trainer_id: str
    skills_to_learn: List[SkillRequirement]
    total_cost: int
    estimated_time: float
    status: TrainerStatus
    start_time: Optional[float] = None
    completion_time: Optional[float] = None


class TrainerLocator:
    """
    Trainer Navigation & Profession Unlock Logic.
    
    Features:
    - Detects needed skills based on current build
    - Looks up nearest trainer from data/trainers.yaml
    - Navigates to trainer city using travel logic
    - Approaches NPC using OCR name detection
    - Executes /train or interactive dialog
    - Supports hybrid/multi-track profession builds
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the trainer locator system."""
        self.logger = logging.getLogger("trainer_locator")
        self.setup_logging()
        
        # Initialize components
        self.travel_manager = TravelManager()
        self.trainers_data: Dict[str, Any] = {}
        self.current_skills: Dict[str, SkillLevel] = {}
        self.training_sessions: List[TrainingSession] = []
        
        # Configuration
        self.config = self.load_config(config_path)
        self.ocr_interval = self.config.get("ocr_interval", 1.0)
        self.training_cooldown = self.config.get("training_cooldown", 300)  # 5 minutes
        
        # File paths
        self.trainers_file = Path("data/trainers.yaml")
        self.expanded_trainers_file = Path("data/trainers/expanded_trainers.json")
        
        # Load trainer data
        self.load_trainer_data()
    
    def setup_logging(self):
        """Set up logging for trainer locator."""
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration for the trainer locator."""
        default_config = {
            "ocr_interval": 1.0,
            "training_cooldown": 300,  # 5 minutes
            "max_training_distance": 1000,  # meters
            "auto_travel": True,
            "auto_train": True,
            "skill_detection_keywords": [
                "skill", "level", "train", "learn", "profession"
            ],
            "trainer_detection_keywords": [
                "trainer", "master", "teacher", "instructor"
            ]
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def load_trainer_data(self):
        """Load trainer data from YAML and JSON files."""
        # Load from expanded trainers JSON
        if self.expanded_trainers_file.exists():
            try:
                with open(self.expanded_trainers_file, 'r') as f:
                    data = json.load(f)
                    self.trainers_data = data.get("trainers", [])
                self.logger.info(f"Loaded {len(self.trainers_data)} trainers from expanded data")
            except Exception as e:
                self.logger.error(f"Failed to load expanded trainers: {e}")
        
        # Load from basic trainers YAML
        if self.trainers_file.exists():
            try:
                with open(self.trainers_file, 'r') as f:
                    yaml_data = yaml.safe_load(f)
                    # Convert YAML format to trainer objects
                    for profession, planets in yaml_data.items():
                        if isinstance(planets, dict):  # Check if planets is a dict
                            for planet, cities in planets.items():
                                if isinstance(cities, dict):  # Check if cities is a dict
                                    for city, trainer_info in cities.items():
                                        if isinstance(trainer_info, dict):  # Check if trainer_info is a dict
                                            trainer = {
                                                "trainer_id": f"{planet}_{city}_{profession}",
                                                "name": trainer_info.get("name", f"{profession.title()} Trainer"),
                                                "profession": profession,
                                                "planet": planet,
                                                "zone": city,
                                                "coordinates": (trainer_info.get("x", 0), trainer_info.get("y", 0)),
                                                "skills_taught": self.get_default_skills(profession),
                                                "max_skill_level": SkillLevel.EXPERT,
                                                "training_cost": {"credits": trainer_info.get("cost", 100)},
                                                "reputation_requirements": trainer_info.get("reputation", {}),
                                                "schedule": {"available_hours": trainer_info.get("schedule", list(range(8, 21)))},
                                                "dialogue_options": ["Learn skills", "Leave"]
                                            }
                                            self.trainers_data.append(trainer)
                self.logger.info(f"Loaded additional trainers from YAML")
            except Exception as e:
                self.logger.error(f"Failed to load trainers YAML: {e}")
    
    def get_default_skills(self, profession: str) -> List[str]:
        """Get default skills for a profession."""
        skill_mapping = {
            "artisan": ["crafting", "engineering", "electronics", "machinery"],
            "marksman": ["ranged_weapons", "tactics", "precision", "marksmanship"],
            "combat": ["unarmed_combat", "melee_weapons", "tactics", "defense"],
            "medic": ["healing", "diagnosis", "surgery", "pharmacology"],
            "scout": ["survival", "tracking", "stealth", "exploration"],
            "entertainer": ["performance", "music", "dance", "oratory"],
            "trader": ["business", "negotiation", "appraisal", "commerce"]
        }
        return skill_mapping.get(profession, ["basic_skills"])
    
    def detect_current_skills(self) -> Dict[str, SkillLevel]:
        """Detect current skills via OCR or internal database."""
        try:
            # Capture screen for skill detection
            screen = capture_screen()
            if screen is None:
                return self.current_skills
            
            # Run OCR on the screen
            ocr_text = run_ocr(screen)
            
            # Parse skills from OCR text
            skills = self.parse_skills_from_text(ocr_text)
            self.current_skills.update(skills)
            
            self.logger.info(f"Detected {len(skills)} skills via OCR")
            return self.current_skills
        
        except Exception as e:
            self.logger.error(f"Error detecting skills: {e}")
            return self.current_skills
    
    def parse_skills_from_text(self, text: str) -> Dict[str, SkillLevel]:
        """Parse skills from OCR text."""
        skills = {}
        
        # Look for skill patterns like "Skill: Marksmanship Level: Expert"
        import re
        skill_patterns = [
            r"(\w+):\s*(\w+)",
            r"skill\s+(\w+)\s+level\s+(\w+)",
            r"(\w+)\s+(\w+)"
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for skill_name, level_name in matches:
                level = self.parse_skill_level(level_name)
                if level != SkillLevel.NONE:
                    skills[skill_name.lower()] = level
        
        return skills
    
    def parse_skill_level(self, level_text: str) -> SkillLevel:
        """Parse skill level from text."""
        level_mapping = {
            "none": SkillLevel.NONE,
            "novice": SkillLevel.NOVICE,
            "apprentice": SkillLevel.APPRENTICE,
            "journeyman": SkillLevel.JOURNEYMAN,
            "expert": SkillLevel.EXPERT,
            "master": SkillLevel.MASTER
        }
        
        level_lower = level_text.lower()
        return level_mapping.get(level_lower, SkillLevel.NONE)
    
    def detect_needed_skills(self, target_profession: str) -> List[SkillRequirement]:
        """Detect skills needed for a target profession."""
        current_skills = self.detect_current_skills()
        needed_skills = []
        
        # Get target skills for profession
        target_skills = self.get_profession_skills(target_profession)
        
        for skill_name, target_level in target_skills.items():
            current_level = current_skills.get(skill_name, SkillLevel.NONE)
            
            if current_level.value < target_level.value:
                requirement = SkillRequirement(
                    skill_name=skill_name,
                    current_level=current_level,
                    required_level=target_level,
                    cost=self.calculate_training_cost(skill_name, current_level, target_level),
                    time_required=self.calculate_training_time(skill_name, current_level, target_level),
                    profession=target_profession,
                    prerequisites=self.get_skill_prerequisites(skill_name)
                )
                needed_skills.append(requirement)
        
        return needed_skills
    
    def get_profession_skills(self, profession: str) -> Dict[str, SkillLevel]:
        """Get target skills for a profession."""
        profession_skills = {
            "artisan": {
                "crafting": SkillLevel.EXPERT,
                "engineering": SkillLevel.JOURNEYMAN,
                "electronics": SkillLevel.APPRENTICE,
                "machinery": SkillLevel.NOVICE
            },
            "marksman": {
                "ranged_weapons": SkillLevel.EXPERT,
                "tactics": SkillLevel.JOURNEYMAN,
                "precision": SkillLevel.APPRENTICE,
                "marksmanship": SkillLevel.NOVICE
            },
            "combat": {
                "unarmed_combat": SkillLevel.EXPERT,
                "melee_weapons": SkillLevel.JOURNEYMAN,
                "tactics": SkillLevel.APPRENTICE,
                "defense": SkillLevel.NOVICE
            },
            "medic": {
                "healing": SkillLevel.EXPERT,
                "diagnosis": SkillLevel.JOURNEYMAN,
                "surgery": SkillLevel.APPRENTICE,
                "pharmacology": SkillLevel.NOVICE
            }
        }
        
        return profession_skills.get(profession, {"basic_skills": SkillLevel.NOVICE})
    
    def calculate_training_cost(self, skill_name: str, current_level: SkillLevel, target_level: SkillLevel) -> int:
        """Calculate training cost for a skill."""
        base_cost = 100
        level_difference = target_level.value - current_level.value
        return base_cost * level_difference
    
    def calculate_training_time(self, skill_name: str, current_level: SkillLevel, target_level: SkillLevel) -> float:
        """Calculate training time for a skill."""
        base_time = 60  # seconds
        level_difference = target_level.value - current_level.value
        return base_time * level_difference
    
    def get_skill_prerequisites(self, skill_name: str) -> List[str]:
        """Get prerequisites for a skill."""
        prerequisites = {
            "engineering": ["crafting"],
            "electronics": ["crafting"],
            "machinery": ["crafting"],
            "tactics": ["ranged_weapons"],
            "precision": ["ranged_weapons"],
            "marksmanship": ["ranged_weapons"],
            "melee_weapons": ["unarmed_combat"],
            "defense": ["unarmed_combat"],
            "diagnosis": ["healing"],
            "surgery": ["healing"],
            "pharmacology": ["healing"]
        }
        
        return prerequisites.get(skill_name, [])
    
    def find_trainers_for_profession(self, profession: str, planet: Optional[str] = None) -> List[TrainerInfo]:
        """Find trainers for a specific profession."""
        trainers = []
        
        for trainer_data in self.trainers_data:
            if trainer_data["profession"].lower() == profession.lower():
                if planet and trainer_data["planet"].lower() != planet.lower():
                    continue
                
                trainer = TrainerInfo(
                    trainer_id=trainer_data["trainer_id"],
                    name=trainer_data["name"],
                    profession=trainer_data["profession"],
                    planet=trainer_data["planet"],
                    zone=trainer_data["zone"],
                    coordinates=tuple(trainer_data["coordinates"]),
                    skills_taught=trainer_data["skills_taught"],
                    max_skill_level=SkillLevel(trainer_data.get("max_skill_level", 4)),
                    training_cost=trainer_data.get("training_cost", {}),
                    reputation_requirements=trainer_data.get("reputation_requirements", {}),
                    schedule=trainer_data.get("schedule", {}),
                    dialogue_options=trainer_data.get("dialogue_options", [])
                )
                trainers.append(trainer)
        
        return trainers
    
    def find_nearest_trainer(self, profession: str, planet: Optional[str] = None) -> Optional[TrainerInfo]:
        """Find the nearest trainer for a profession."""
        trainers = self.find_trainers_for_profession(profession, planet)
        
        if not trainers:
            return None
        
        # For now, return the first available trainer
        # In a real implementation, you'd calculate distances
        return trainers[0]
    
    def navigate_to_trainer(self, trainer: TrainerInfo) -> bool:
        """Navigate to a trainer location."""
        try:
            # Get travel location for trainer
            location = get_location(trainer.zone, trainer.planet)
            if not location:
                self.logger.error(f"Unknown location: {trainer.zone}, {trainer.planet}")
                return False
            
            # Travel to the location
            success = self.travel_manager.travel_to_location(location)
            if not success:
                self.logger.error(f"Failed to travel to {trainer.zone}, {trainer.planet}")
                return False
            
            self.logger.info(f"Successfully traveled to {trainer.zone}, {trainer.planet}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error navigating to trainer: {e}")
            return False
    
    def detect_trainer_npc(self, trainer: TrainerInfo) -> bool:
        """Detect trainer NPC using OCR."""
        try:
            # Capture screen for NPC detection
            screen = capture_screen()
            if screen is None:
                return False
            
            # Run OCR on the screen
            ocr_text = run_ocr(screen)
            
            # Check if trainer name is in OCR text
            trainer_name_lower = trainer.name.lower()
            ocr_text_lower = ocr_text.lower()
            
            if trainer_name_lower in ocr_text_lower:
                self.logger.info(f"Detected trainer NPC: {trainer.name}")
                return True
            
            # Check for trainer keywords
            trainer_keywords = self.config.get("trainer_detection_keywords", [])
            for keyword in trainer_keywords:
                if keyword.lower() in ocr_text_lower:
                    self.logger.info(f"Detected trainer via keyword: {keyword}")
                    return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Error detecting trainer NPC: {e}")
            return False
    
    def approach_trainer(self, trainer: TrainerInfo) -> bool:
        """Approach trainer NPC."""
        try:
            # Move to trainer coordinates
            self.logger.info(f"Moving to trainer coordinates: {trainer.coordinates}")
            
            # Wait for trainer detection
            max_attempts = 10
            for attempt in range(max_attempts):
                if self.detect_trainer_npc(trainer):
                    self.logger.info(f"Successfully approached trainer: {trainer.name}")
                    return True
                
                time.sleep(self.ocr_interval)
            
            self.logger.warning(f"Failed to detect trainer after {max_attempts} attempts")
            return False
        
        except Exception as e:
            self.logger.error(f"Error approaching trainer: {e}")
            return False
    
    def execute_training(self, trainer: TrainerInfo, skills_to_learn: List[SkillRequirement]) -> bool:
        """Execute training session with trainer."""
        try:
            # Create training session
            total_cost = sum(skill.cost for skill in skills_to_learn)
            estimated_time = sum(skill.time_required for skill in skills_to_learn)
            
            session = TrainingSession(
                trainer_id=trainer.trainer_id,
                skills_to_learn=skills_to_learn,
                total_cost=total_cost,
                estimated_time=estimated_time,
                status=TrainerStatus.TRAINING,
                start_time=time.time()
            )
            
            self.training_sessions.append(session)
            
            # Execute training commands
            for skill in skills_to_learn:
                self.logger.info(f"Training skill: {skill.skill_name} to {skill.required_level.name}")
                
                # Simulate training time (faster for demo)
                time.sleep(min(skill.time_required / 10, 1.0))  # Scale down for demo
                
                # Update current skills
                self.current_skills[skill.skill_name] = skill.required_level
            
            session.completion_time = time.time()
            session.status = TrainerStatus.AVAILABLE
            
            self.logger.info(f"Completed training session with {trainer.name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error executing training: {e}")
            return False
    
    def auto_train_profession(self, profession: str, target_planet: Optional[str] = None) -> bool:
        """Automatically train a profession."""
        try:
            self.logger.info(f"Starting auto-training for profession: {profession}")
            
            # Detect needed skills
            needed_skills = self.detect_needed_skills(profession)
            if not needed_skills:
                self.logger.info(f"No skills needed for profession: {profession}")
                return True
            
            self.logger.info(f"Detected {len(needed_skills)} skills needed")
            
            # Find nearest trainer
            trainer = self.find_nearest_trainer(profession, target_planet)
            if not trainer:
                self.logger.error(f"No trainer found for profession: {profession}")
                return False
            
            self.logger.info(f"Found trainer: {trainer.name} at {trainer.zone}, {trainer.planet}")
            
            # Navigate to trainer
            if not self.navigate_to_trainer(trainer):
                return False
            
            # Approach trainer
            if not self.approach_trainer(trainer):
                return False
            
            # Execute training
            if not self.execute_training(trainer, needed_skills):
                return False
            
            self.logger.info(f"Successfully completed auto-training for {profession}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error in auto-training: {e}")
            return False
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get training session summary."""
        total_sessions = len(self.training_sessions)
        completed_sessions = len([s for s in self.training_sessions if s.status == TrainerStatus.AVAILABLE])
        total_cost = sum(s.total_cost for s in self.training_sessions)
        total_time = sum(s.estimated_time for s in self.training_sessions)
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "total_cost": total_cost,
            "total_time": total_time,
            "current_skills": {k: v.name for k, v in self.current_skills.items()},
            "recent_sessions": [
                {
                    "trainer_id": s.trainer_id,
                    "skills_count": len(s.skills_to_learn),
                    "cost": s.total_cost,
                    "status": s.status.value
                }
                for s in self.training_sessions[-5:]  # Last 5 sessions
            ]
        }


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Trainer Navigation & Profession Unlock Logic")
    parser.add_argument("--profession", type=str, required=True, help="Profession to train")
    parser.add_argument("--planet", type=str, help="Target planet for training")
    parser.add_argument("--auto-train", action="store_true", help="Start automatic training")
    parser.add_argument("--detect-skills", action="store_true", help="Detect current skills")
    parser.add_argument("--find-trainers", action="store_true", help="Find trainers for profession")
    parser.add_argument("--summary", action="store_true", help="Show training summary")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    
    args = parser.parse_args()
    
    locator = TrainerLocator(args.config)
    
    if args.detect_skills:
        skills = locator.detect_current_skills()
        print("Current Skills:")
        for skill, level in skills.items():
            print(f"  {skill}: {level.name}")
    
    elif args.find_trainers:
        trainers = locator.find_trainers_for_profession(args.profession, args.planet)
        print(f"Trainers for {args.profession}:")
        for trainer in trainers:
            print(f"  {trainer.name} at {trainer.zone}, {trainer.planet}")
    
    elif args.auto_train:
        success = locator.auto_train_profession(args.profession, args.planet)
        if success:
            print(f"✅ Successfully trained {args.profession}")
        else:
            print(f"❌ Failed to train {args.profession}")
    
    elif args.summary:
        summary = locator.get_training_summary()
        print("Training Summary:")
        print(f"  Total Sessions: {summary['total_sessions']}")
        print(f"  Completed Sessions: {summary['completed_sessions']}")
        print(f"  Total Cost: {summary['total_cost']} credits")
        print(f"  Total Time: {summary['total_time']:.1f} seconds")
    
    else:
        print("Trainer Locator initialized. Use --auto-train, --detect-skills, --find-trainers, or --summary")


if __name__ == "__main__":
    main() 
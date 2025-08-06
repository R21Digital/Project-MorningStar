"""Profession Trainer for Batch 063 - Smart Crafting Integration.

This module provides:
- Profession training coordination
- Support for Artisan, Chef, and Structures professions
- Training location detection and travel
- Skill progression tracking
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from core.ocr import OCREngine
from core.screenshot import capture_screen
from core.state_tracker import update_state, get_state
from core.travel_manager import TravelManager


@dataclass
class TrainingLocation:
    """Represents a training location."""
    name: str
    profession: str
    planet: str
    city: str
    coords: Tuple[int, int]
    trainer_name: str
    available_skills: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "profession": self.profession,
            "planet": self.planet,
            "city": self.city,
            "coords": self.coords,
            "trainer_name": self.trainer_name,
            "available_skills": self.available_skills
        }


@dataclass
class TrainingSession:
    """Represents a training session."""
    profession: str
    location: TrainingLocation
    skills_to_learn: List[str]
    start_time: float
    is_active: bool = True
    skills_learned: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "profession": self.profession,
            "location": self.location.to_dict(),
            "skills_to_learn": self.skills_to_learn,
            "start_time": self.start_time,
            "is_active": self.is_active,
            "skills_learned": self.skills_learned
        }


class ProfessionTrainer:
    """Handles profession training for crafting professions."""
    
    def __init__(self):
        """Initialize the profession trainer."""
        self.ocr_engine = OCREngine()
        self.travel_manager = TravelManager()
        self.logger = logging.getLogger(__name__)
        
        # Known training locations
        self.training_locations = self._load_training_locations()
        
        # Profession skill trees
        self.skill_trees = {
            "artisan": {
                "novice": ["crafting_artisan_novice"],
                "apprentice": ["crafting_artisan_apprentice"],
                "journeyman": ["crafting_artisan_journeyman"],
                "expert": ["crafting_artisan_expert"],
                "master": ["crafting_artisan_master"]
            },
            "chef": {
                "novice": ["crafting_chef_novice"],
                "apprentice": ["crafting_chef_apprentice"],
                "journeyman": ["crafting_chef_journeyman"],
                "expert": ["crafting_chef_expert"],
                "master": ["crafting_chef_master"]
            },
            "structures": {
                "novice": ["crafting_structures_novice"],
                "apprentice": ["crafting_structures_apprentice"],
                "journeyman": ["crafting_structures_journeyman"],
                "expert": ["crafting_structures_expert"],
                "master": ["crafting_structures_master"]
            }
        }
        
        # Active training session
        self.active_session: Optional[TrainingSession] = None
    
    def _load_training_locations(self) -> Dict[str, List[TrainingLocation]]:
        """Load known training locations."""
        locations = {
            "artisan": [
                TrainingLocation(
                    name="Artisan Trainer - Corellia",
                    profession="artisan",
                    planet="Corellia",
                    city="Coronet",
                    coords=(100, 200),
                    trainer_name="Master Artisan",
                    available_skills=["crafting_artisan_novice", "crafting_artisan_apprentice"]
                ),
                TrainingLocation(
                    name="Artisan Trainer - Naboo",
                    profession="artisan",
                    planet="Naboo",
                    city="Theed",
                    coords=(150, 250),
                    trainer_name="Expert Artisan",
                    available_skills=["crafting_artisan_journeyman", "crafting_artisan_expert"]
                )
            ],
            "chef": [
                TrainingLocation(
                    name="Chef Trainer - Corellia",
                    profession="chef",
                    planet="Corellia",
                    city="Coronet",
                    coords=(120, 180),
                    trainer_name="Master Chef",
                    available_skills=["crafting_chef_novice", "crafting_chef_apprentice"]
                ),
                TrainingLocation(
                    name="Chef Trainer - Naboo",
                    profession="chef",
                    planet="Naboo",
                    city="Theed",
                    coords=(160, 220),
                    trainer_name="Expert Chef",
                    available_skills=["crafting_chef_journeyman", "crafting_chef_expert"]
                )
            ],
            "structures": [
                TrainingLocation(
                    name="Architect Trainer - Corellia",
                    profession="structures",
                    planet="Corellia",
                    city="Coronet",
                    coords=(140, 160),
                    trainer_name="Master Architect",
                    available_skills=["crafting_structures_novice", "crafting_structures_apprentice"]
                ),
                TrainingLocation(
                    name="Architect Trainer - Naboo",
                    profession="structures",
                    planet="Naboo",
                    city="Theed",
                    coords=(180, 240),
                    trainer_name="Expert Architect",
                    available_skills=["crafting_structures_journeyman", "crafting_structures_expert"]
                )
            ]
        }
        
        return locations
    
    def get_available_skills(self, profession: str) -> List[str]:
        """Get available skills for a profession.
        
        Parameters
        ----------
        profession : str
            Profession to get skills for
            
        Returns
        -------
        List[str]
            List of available skills
        """
        return self.skill_trees.get(profession, {}).get("novice", [])
    
    def get_current_skills(self) -> Dict[str, List[str]]:
        """Get currently learned skills.
        
        Returns
        -------
        Dict[str, List[str]]
            Dictionary of profession to learned skills
        """
        # This would integrate with the skills system
        # For now, return placeholder data
        return {
            "artisan": ["crafting_artisan_novice"],
            "chef": [],
            "structures": []
        }
    
    def get_missing_skills(self, profession: str) -> List[str]:
        """Get missing skills for a profession.
        
        Parameters
        ----------
        profession : str
            Profession to check
            
        Returns
        -------
        List[str]
            List of missing skills
        """
        current_skills = self.get_current_skills().get(profession, [])
        available_skills = self.get_available_skills(profession)
        
        missing = []
        for skill in available_skills:
            if skill not in current_skills:
                missing.append(skill)
        
        return missing
    
    def find_training_location(self, profession: str, skill: str) -> Optional[TrainingLocation]:
        """Find training location for a specific skill.
        
        Parameters
        ----------
        profession : str
            Profession to train
        skill : str
            Skill to learn
            
        Returns
        -------
        Optional[TrainingLocation]
            Training location if found
        """
        locations = self.training_locations.get(profession, [])
        
        for location in locations:
            if skill in location.available_skills:
                return location
        
        return None
    
    def start_training_session(self, profession: str, skills: List[str] = None) -> bool:
        """Start a training session for a profession.
        
        Parameters
        ----------
        profession : str
            Profession to train
        skills : List[str], optional
            Specific skills to learn
            
        Returns
        -------
        bool
            True if session started successfully
        """
        if skills is None:
            skills = self.get_missing_skills(profession)
        
        if not skills:
            self.logger.info(f"No missing skills for {profession}")
            return False
        
        # Find training location for first skill
        location = self.find_training_location(profession, skills[0])
        if not location:
            self.logger.error(f"No training location found for {profession} skill {skills[0]}")
            return False
        
        # Travel to training location
        if not self._travel_to_training_location(location):
            self.logger.error(f"Failed to travel to training location: {location.name}")
            return False
        
        # Start training session
        self.active_session = TrainingSession(
            profession=profession,
            location=location,
            skills_to_learn=skills,
            start_time=time.time()
        )
        
        self.logger.info(f"Started training session for {profession} at {location.name}")
        update_state("active_training_session", self.active_session.to_dict())
        
        return True
    
    def _travel_to_training_location(self, location: TrainingLocation) -> bool:
        """Travel to a training location.
        
        Parameters
        ----------
        location : TrainingLocation
            Location to travel to
            
        Returns
        -------
        bool
            True if travel successful
        """
        try:
            # Use travel manager to travel to location
            success = self.travel_manager.travel_to_location(
                planet=location.planet,
                city=location.city,
                coords=location.coords
            )
            
            if success:
                self.logger.info(f"Traveled to {location.name}")
                return True
            else:
                self.logger.warning(f"Failed to travel to {location.name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Travel error: {e}")
            return False
    
    def run_training_loop(self) -> Dict[str, Any]:
        """Run the training loop.
        
        Returns
        -------
        Dict[str, Any]
            Results of training session
        """
        if not self.active_session:
            self.logger.error("No active training session")
            return {"success": False, "error": "No active session"}
        
        results = {
            "profession": self.active_session.profession,
            "location": self.active_session.location.name,
            "skills_learned": 0,
            "skills_completed": [],
            "errors": []
        }
        
        try:
            # Interact with trainer
            if not self._interact_with_trainer(self.active_session.location):
                results["errors"].append("Failed to interact with trainer")
                return results
            
            # Learn skills
            for skill in self.active_session.skills_to_learn:
                if self._learn_skill(skill):
                    results["skills_learned"] += 1
                    results["skills_completed"].append(skill)
                    self.active_session.skills_learned += 1
                    self.logger.info(f"Learned skill: {skill}")
                else:
                    results["errors"].append(f"Failed to learn skill: {skill}")
            
        except Exception as e:
            self.logger.error(f"Training loop error: {e}")
            results["errors"].append(str(e))
        
        return results
    
    def _interact_with_trainer(self, location: TrainingLocation) -> bool:
        """Interact with the trainer.
        
        Parameters
        ----------
        location : TrainingLocation
            Training location with trainer
            
        Returns
        -------
        bool
            True if interaction successful
        """
        # Simulate trainer interaction
        self.logger.info(f"Interacting with trainer: {location.trainer_name}")
        
        # Simulate UI interaction
        time.sleep(1.0)
        
        return True
    
    def _learn_skill(self, skill: str) -> bool:
        """Learn a specific skill.
        
        Parameters
        ----------
        skill : str
            Skill to learn
            
        Returns
        -------
        bool
            True if skill learned successfully
        """
        # Simulate skill learning
        self.logger.info(f"Learning skill: {skill}")
        
        # Simulate learning process
        time.sleep(2.0)
        
        # Simulate success (95% success rate for testing)
        import random
        success = random.random() > 0.05
        
        return success
    
    def stop_training_session(self) -> Dict[str, Any]:
        """Stop the active training session.
        
        Returns
        -------
        Dict[str, Any]
            Session summary
        """
        if not self.active_session:
            return {"success": False, "error": "No active session"}
        
        session_duration = time.time() - self.active_session.start_time
        summary = {
            "profession": self.active_session.profession,
            "location": self.active_session.location.name,
            "duration_seconds": session_duration,
            "skills_learned": self.active_session.skills_learned,
            "success": True
        }
        
        self.active_session.is_active = False
        self.active_session = None
        
        self.logger.info(f"Stopped training session: {summary['skills_learned']} skills learned")
        update_state("active_training_session", None)
        
        return summary
    
    def get_training_status(self) -> Dict[str, Any]:
        """Get current training status.
        
        Returns
        -------
        Dict[str, Any]
            Current training status
        """
        current_skills = self.get_current_skills()
        
        status = {
            "active_session": self.active_session.to_dict() if self.active_session else None,
            "current_skills": current_skills,
            "available_locations": {
                profession: [loc.to_dict() for loc in locations]
                for profession, locations in self.training_locations.items()
            }
        }
        
        # Add missing skills for each profession
        status["missing_skills"] = {}
        for profession in ["artisan", "chef", "structures"]:
            status["missing_skills"][profession] = self.get_missing_skills(profession)
        
        return status
    
    def detect_trainer_npc(self) -> Optional[str]:
        """Detect trainer NPC using OCR.
        
        Returns
        -------
        Optional[str]
            Trainer name if detected
        """
        screen = capture_screen()
        text_results = self.ocr_engine.scan_text(screen)
        
        trainer_keywords = ["trainer", "master", "expert", "teacher", "instructor"]
        
        for result in text_results:
            text = result.text.lower()
            for keyword in trainer_keywords:
                if keyword in text:
                    self.logger.info(f"Detected trainer: {result.text}")
                    return result.text
        
        return None
    
    def get_profession_progress(self, profession: str) -> Dict[str, Any]:
        """Get progress for a specific profession.
        
        Parameters
        ----------
        profession : str
            Profession to get progress for
            
        Returns
        -------
        Dict[str, Any]
            Profession progress
        """
        current_skills = self.get_current_skills().get(profession, [])
        all_skills = []
        
        # Get all skills for profession
        for level_skills in self.skill_trees.get(profession, {}).values():
            all_skills.extend(level_skills)
        
        learned_count = len(current_skills)
        total_count = len(all_skills)
        progress_percentage = (learned_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "profession": profession,
            "learned_skills": current_skills,
            "total_skills": all_skills,
            "learned_count": learned_count,
            "total_count": total_count,
            "progress_percentage": progress_percentage
        } 
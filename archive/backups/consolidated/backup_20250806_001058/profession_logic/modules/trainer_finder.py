"""
Trainer Finder Module for MS11

This module provides logic to:
- Load trainer NPCs from data/trainers.json
- Match available skill tree vs current skills (stub logic OK)
- Route to the nearest trainer if skills are available to learn
"""

import json
import logging
import math
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from core.database import get_database, find_trainers_for_profession
from core.navigation.navigation_engine import NavigationEngine, Coordinate, navigate_to_coordinates


class TrainerStatus(Enum):
    """Trainer interaction status."""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    NO_SKILLS = "no_skills"
    TOO_FAR = "too_far"
    IN_COMBAT = "in_combat"
    COOLDOWN = "cooldown"


class SkillLevel(Enum):
    """Skill level enumeration."""
    NONE = 0
    NOVICE = 1
    APPRENTICE = 2
    JOURNEYMAN = 3
    EXPERT = 4
    MASTER = 5


@dataclass
class SkillRequirement:
    """Represents a skill requirement for training."""
    skill_name: str
    current_level: SkillLevel
    required_level: SkillLevel
    cost: int
    time_required: float  # seconds


@dataclass
class TrainerLocation:
    """Represents a trainer location with metadata."""
    trainer_id: str
    name: str
    profession: str
    planet: str
    city: str
    coordinates: Tuple[int, int]
    skills_taught: List[str]
    max_skill_level: SkillLevel
    training_cost: Dict[str, int]
    reputation_requirements: Dict[str, int]
    schedule: Dict[str, Any]
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


class TrainerFinder:
    """
    Trainer finder and routing system.
    
    Features:
    - Load trainer data from database
    - Match current skills vs available training
    - Find nearest available trainer
    - Route to trainer location
    - Handle training session management
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize trainer finder.
        
        Args:
            data_dir: Path to data directory
        """
        self.logger = logging.getLogger("trainer_finder")
        self.data_dir = Path(data_dir)
        self.database = get_database()
        self.navigation_engine = NavigationEngine()
        
        # Current character state (stub data)
        self.current_skills: Dict[str, SkillLevel] = {}
        self.current_location: Optional[Coordinate] = None
        self.current_planet: str = "tatooine"
        self.current_city: str = "mos_eisley"
        
        # Training session tracking
        self.active_session: Optional[TrainingSession] = None
        self.recent_trainers: List[str] = []
        self.cooldown_trainers: Dict[str, float] = {}
        
        self._setup_logging()
        self._load_character_state()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _load_character_state(self):
        """Load current character state (stub implementation)."""
        # In a real implementation, this would read from game state or config
        self.current_skills = {
            "rifleman": SkillLevel.NOVICE,
            "medic": SkillLevel.NONE,
            "artisan": SkillLevel.NONE,
            "marksman": SkillLevel.NONE,
        }
        
        # Set current location (stub)
        self.current_location = Coordinate(
            x=3432, y=-4795, 
            zone="mos_eisley", 
            planet="tatooine"
        )
        
        self.logger.info(f"Loaded character state: {self.current_skills}")
    
    def find_available_trainers(self, profession: str, 
                              planet: Optional[str] = None) -> List[TrainerLocation]:
        """Find available trainers for a profession.
        
        Args:
            profession: Profession to find trainers for
            planet: Optional planet filter
            
        Returns:
            List of available trainer locations
        """
        try:
            # Get trainers from database
            trainers = find_trainers_for_profession(profession, planet)
            
            available_trainers = []
            for trainer in trainers:
                # Check if trainer is available (not in cooldown)
                if trainer.trainer_id in self.cooldown_trainers:
                    continue
                
                # Create trainer location
                trainer_loc = TrainerLocation(
                    trainer_id=trainer.trainer_id,
                    name=trainer.name,
                    profession=trainer.profession,
                    planet=trainer.planet,
                    city=trainer.zone,
                    coordinates=(trainer.coordinates[0], trainer.coordinates[1]),
                    skills_taught=trainer.skills_taught,
                    max_skill_level=SkillLevel(trainer.max_skill_level),
                    training_cost=trainer.training_cost,
                    reputation_requirements=trainer.reputation_requirement,
                    schedule=trainer.schedule,
                    is_available=trainer.metadata.get("is_available", True) if trainer.metadata else True
                )
                
                # Calculate distance if we have current location
                if self.current_location:
                    trainer_coord = Coordinate(
                        x=trainer_loc.coordinates[0],
                        y=trainer_loc.coordinates[1],
                        zone=trainer_loc.city,
                        planet=trainer_loc.planet
                    )
                    trainer_loc.distance = self.current_location.distance_to(trainer_coord)
                
                available_trainers.append(trainer_loc)
            
            # Sort by distance (nearest first)
            available_trainers.sort(key=lambda t: t.distance or float('inf'))
            
            self.logger.info(f"Found {len(available_trainers)} available trainers for {profession}")
            return available_trainers
            
        except Exception as e:
            self.logger.error(f"Error finding trainers for {profession}: {e}")
            return []
    
    def check_skill_requirements(self, trainer: TrainerLocation) -> List[SkillRequirement]:
        """Check what skills can be learned from a trainer.
        
        Args:
            trainer: Trainer location to check
            
        Returns:
            List of skills that can be learned
        """
        available_skills = []
        
        for skill_name in trainer.skills_taught:
            current_level = self.current_skills.get(skill_name, SkillLevel.NONE)
            
            # Check if we can learn this skill
            if current_level.value < trainer.max_skill_level.value:
                # Calculate next level
                next_level = SkillLevel(current_level.value + 1)
                
                # Get training cost (stub logic)
                cost = trainer.training_cost.get(skill_name, 100)
                
                # Calculate time required (stub logic)
                time_required = 30.0  # 30 seconds per skill level
                
                skill_req = SkillRequirement(
                    skill_name=skill_name,
                    current_level=current_level,
                    required_level=next_level,
                    cost=cost,
                    time_required=time_required
                )
                
                available_skills.append(skill_req)
        
        self.logger.info(f"Found {len(available_skills)} available skills at {trainer.name}")
        return available_skills
    
    def find_nearest_trainer_with_skills(self, profession: str, 
                                       planet: Optional[str] = None) -> Optional[Tuple[TrainerLocation, List[SkillRequirement]]]:
        """Find the nearest trainer that has skills to learn.
        
        Args:
            profession: Profession to find trainers for
            planet: Optional planet filter
            
        Returns:
            Tuple of (trainer_location, available_skills) or None
        """
        available_trainers = self.find_available_trainers(profession, planet)
        
        for trainer in available_trainers:
            if not trainer.is_available:
                continue
                
            available_skills = self.check_skill_requirements(trainer)
            
            if available_skills:
                self.logger.info(f"Found trainer {trainer.name} with {len(available_skills)} skills to learn")
                return (trainer, available_skills)
        
        self.logger.warning(f"No trainers found with available skills for {profession}")
        return None
    
    def route_to_trainer(self, trainer: TrainerLocation) -> bool:
        """Route to a trainer location.
        
        Args:
            trainer: Trainer location to route to
            
        Returns:
            True if routing was successful
        """
        try:
            # Check if we need to travel to a different planet
            if trainer.planet.lower() != self.current_planet.lower():
                self.logger.info(f"Need to travel from {self.current_planet} to {trainer.planet}")
                # TODO: Implement interplanetary travel
                return False
            
            # Navigate to trainer coordinates
            success = navigate_to_coordinates(
                target_x=trainer.coordinates[0],
                target_y=trainer.coordinates[1],
                current_x=self.current_location.x if self.current_location else None,
                current_y=self.current_location.y if self.current_location else None,
                zone=trainer.city,
                planet=trainer.planet
            )
            
            if success:
                self.logger.info(f"Successfully routed to trainer {trainer.name}")
                return True
            else:
                self.logger.error(f"Failed to route to trainer {trainer.name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error routing to trainer {trainer.name}: {e}")
            return False
    
    def start_training_session(self, trainer: TrainerLocation, 
                             skills_to_learn: List[SkillRequirement]) -> TrainingSession:
        """Start a training session with a trainer.
        
        Args:
            trainer: Trainer to train with
            skills_to_learn: Skills to learn
            
        Returns:
            Training session object
        """
        import time
        
        total_cost = sum(skill.cost for skill in skills_to_learn)
        estimated_time = sum(skill.time_required for skill in skills_to_learn)
        
        session = TrainingSession(
            trainer_id=trainer.trainer_id,
            skills_to_learn=skills_to_learn,
            total_cost=total_cost,
            estimated_time=estimated_time,
            status=TrainerStatus.AVAILABLE,
            start_time=time.time()
        )
        
        self.active_session = session
        self.logger.info(f"Started training session with {trainer.name} for {len(skills_to_learn)} skills")
        
        return session
    
    def complete_training_session(self) -> bool:
        """Complete the current training session.
        
        Returns:
            True if session was completed successfully
        """
        if not self.active_session:
            self.logger.warning("No active training session to complete")
            return False
        
        import time
        
        # Update character skills (stub implementation)
        for skill_req in self.active_session.skills_to_learn:
            self.current_skills[skill_req.skill_name] = skill_req.required_level
        
        # Mark trainer as on cooldown
        cooldown_duration = 300.0  # 5 minutes
        self.cooldown_trainers[self.active_session.trainer_id] = time.time() + cooldown_duration
        
        # Update session
        self.active_session.completion_time = time.time()
        self.active_session.status = TrainerStatus.COOLDOWN
        
        self.logger.info(f"Completed training session: {len(self.active_session.skills_to_learn)} skills learned")
        
        # Clear active session
        self.active_session = None
        
        return True
    
    def auto_train_profession(self, profession: str, 
                            max_trainers: int = 3) -> bool:
        """Automatically find and train with available trainers.
        
        Args:
            profession: Profession to train
            max_trainers: Maximum number of trainers to visit
            
        Returns:
            True if training was successful
        """
        trainers_visited = 0
        
        while trainers_visited < max_trainers:
            # Find nearest trainer with available skills
            result = self.find_nearest_trainer_with_skills(profession)
            
            if not result:
                self.logger.info(f"No more trainers available for {profession}")
                break
            
            trainer, available_skills = result
            
            # Route to trainer
            if not self.route_to_trainer(trainer):
                self.logger.error(f"Failed to route to trainer {trainer.name}")
                continue
            
            # Start training session
            session = self.start_training_session(trainer, available_skills)
            
            # Complete training session (stub - in real implementation this would wait for training to complete)
            if self.complete_training_session():
                trainers_visited += 1
                self.logger.info(f"Successfully trained with {trainer.name}")
            else:
                self.logger.error(f"Failed to complete training with {trainer.name}")
        
        return trainers_visited > 0
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get a summary of training status.
        
        Returns:
            Dictionary with training summary
        """
        return {
            "current_skills": {skill: level.name for skill, level in self.current_skills.items()},
            "current_location": str(self.current_location) if self.current_location else None,
            "active_session": self.active_session.trainer_id if self.active_session else None,
            "recent_trainers": self.recent_trainers,
            "cooldown_trainers": len(self.cooldown_trainers)
        }


# Global convenience functions
def get_trainer_finder() -> TrainerFinder:
    """Get the global trainer finder instance."""
    return TrainerFinder()


def find_nearest_trainer(profession: str, planet: Optional[str] = None) -> Optional[Tuple[TrainerLocation, List[SkillRequirement]]]:
    """Find the nearest trainer with available skills."""
    finder = get_trainer_finder()
    return finder.find_nearest_trainer_with_skills(profession, planet)


def route_to_trainer(trainer: TrainerLocation) -> bool:
    """Route to a trainer location."""
    finder = get_trainer_finder()
    return finder.route_to_trainer(trainer)


def auto_train_profession(profession: str, max_trainers: int = 3) -> bool:
    """Automatically train a profession."""
    finder = get_trainer_finder()
    return finder.auto_train_profession(profession, max_trainers)


def get_training_summary() -> Dict[str, Any]:
    """Get training summary."""
    finder = get_trainer_finder()
    return finder.get_training_summary()

"""
Build Manager

This module provides functionality to manage build selection, progression logic,
and integration with the combat system.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .spec_detector import SpecDetector, BuildMatch, DetectionResult
from core.combat.combat_engine import CombatEngine, CombatProfile
from core.database import get_database


class ProgressionPhase(Enum):
    """Progression phase enumeration."""
    EARLY_GAME = "early_game"
    MID_GAME = "mid_game"
    LATE_GAME = "late_game"
    COMPLETE = "complete"


@dataclass
class BuildInfo:
    """Represents build information."""
    name: str
    description: str
    build_type: str
    primary_profession: str
    secondary_profession: Optional[str]
    combat_profile: str
    training_priorities: List[str]
    leveling_plan: Dict[str, Any]


@dataclass
class TrainingPlan:
    """Represents a training plan for a build."""
    build_name: str
    current_phase: ProgressionPhase
    next_skills: List[str]
    completed_skills: List[str]
    missing_skills: List[str]
    completion_ratio: float
    estimated_time_to_complete: float  # hours
    recommended_activities: List[str]


class BuildManager:
    """Manages build selection, progression, and combat profile integration."""
    
    def __init__(self, data_dir: str = "data", profiles_dir: str = "profiles/combat"):
        self.logger = logging.getLogger("build_manager")
        self.data_dir = Path(data_dir)
        self.profiles_dir = Path(profiles_dir)
        self.spec_detector = SpecDetector()
        self.combat_engine = CombatEngine()
        self.database = get_database()
        self.current_build: Optional[BuildInfo] = None
        self.current_training_plan: Optional[TrainingPlan] = None
        self.session_start_time = time.time()
        self.build_detection_log: List[Dict[str, Any]] = []
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def detect_and_select_build(self, force_refresh: bool = False) -> Optional[BuildInfo]:
        """Detect current build and select appropriate combat profile."""
        try:
            # Detect current specification
            detection_result = self.spec_detector.detect_current_spec(force_refresh)
            
            # Log detection result
            self._log_build_detection(detection_result)
            
            if not detection_result.detected_build:
                self.logger.warning("No build detected, using default")
                default_build = self._get_default_build()
                if default_build:
                    self.current_build = self._create_build_info(default_build)
                    return self.current_build
                return None
            
            # Create build info from detection
            build_match = detection_result.detected_build
            build_data = self.spec_detector.get_build_info(build_match.build_name)
            
            if not build_data:
                self.logger.error(f"Build data not found for {build_match.build_name}")
                return None
            
            self.current_build = self._create_build_info(build_match.build_name, build_data)
            
            # Load corresponding combat profile
            self._load_combat_profile()
            
            # Create training plan
            self.current_training_plan = self._create_training_plan(detection_result)
            
            self.logger.info(f"Selected build: {self.current_build.name} (confidence: {build_match.confidence:.2f})")
            return self.current_build
            
        except Exception as e:
            self.logger.error(f"Build detection and selection failed: {e}")
            return None
    
    def _create_build_info(self, build_name: str, build_data: Optional[Dict[str, Any]] = None) -> BuildInfo:
        """Create BuildInfo from build data."""
        if not build_data:
            build_data = self.spec_detector.get_build_info(build_name) or {}
        
        return BuildInfo(
            name=build_name,
            description=build_data.get("description", ""),
            build_type=build_data.get("build_type", "pure_combat"),
            primary_profession=build_data.get("primary_profession", ""),
            secondary_profession=build_data.get("secondary_profession"),
            combat_profile=build_data.get("combat_profile", "default"),
            training_priorities=build_data.get("training_priorities", []),
            leveling_plan=build_data.get("leveling_plan", {})
        )
    
    def _get_default_build(self) -> Optional[str]:
        """Get default build for new character."""
        return self.spec_detector.get_default_build("new_character")
    
    def _load_combat_profile(self):
        """Load the appropriate combat profile for the current build."""
        if not self.current_build:
            return
        
        try:
            profile_name = self.current_build.combat_profile
            success = self.combat_engine.load_combat_profile(profile_name)
            
            if success:
                self.logger.info(f"Loaded combat profile: {profile_name}")
            else:
                self.logger.warning(f"Failed to load combat profile: {profile_name}, using default")
                self.combat_engine.load_combat_profile("default_rifleman")
                
        except Exception as e:
            self.logger.error(f"Error loading combat profile: {e}")
    
    def _create_training_plan(self, detection_result: DetectionResult) -> TrainingPlan:
        """Create a training plan based on current skills and build."""
        if not self.current_build:
            return TrainingPlan(
                build_name="unknown",
                current_phase=ProgressionPhase.EARLY_GAME,
                next_skills=[],
                completed_skills=[],
                missing_skills=[],
                completion_ratio=0.0,
                estimated_time_to_complete=0.0,
                recommended_activities=[]
            )
        
        # Determine current phase
        current_phase = self._determine_progression_phase(detection_result.current_skills)
        
        # Get next skills to train
        next_skills = self._get_next_skills(detection_result.current_skills)
        
        # Calculate completion
        completion_info = self.spec_detector.validate_build_completion(
            self.current_build.name, 
            detection_result.current_skills
        )
        
        # Estimate time to complete
        estimated_time = self._estimate_completion_time(next_skills)
        
        # Get recommended activities
        recommended_activities = self._get_recommended_activities(current_phase)
        
        return TrainingPlan(
            build_name=self.current_build.name,
            current_phase=current_phase,
            next_skills=next_skills,
            completed_skills=detection_result.current_skills,
            missing_skills=completion_info.get("missing_skills", []),
            completion_ratio=completion_info.get("completion_ratio", 0.0),
            estimated_time_to_complete=estimated_time,
            recommended_activities=recommended_activities
        )
    
    def _determine_progression_phase(self, current_skills: List[str]) -> ProgressionPhase:
        """Determine the current progression phase based on skills."""
        if not self.current_build:
            return ProgressionPhase.EARLY_GAME
        
        leveling_plan = self.current_build.leveling_plan
        
        # Check early game skills
        early_skills = leveling_plan.get("early_game", {}).get("skills", [])
        early_completed = all(skill in current_skills for skill in early_skills)
        
        if not early_completed:
            return ProgressionPhase.EARLY_GAME
        
        # Check mid game skills
        mid_skills = leveling_plan.get("mid_game", {}).get("skills", [])
        mid_completed = all(skill in current_skills for skill in mid_skills)
        
        if not mid_completed:
            return ProgressionPhase.MID_GAME
        
        # Check late game skills
        late_skills = leveling_plan.get("late_game", {}).get("skills", [])
        late_completed = all(skill in current_skills for skill in late_skills)
        
        if not late_completed:
            return ProgressionPhase.LATE_GAME
        
        return ProgressionPhase.COMPLETE
    
    def _get_next_skills(self, current_skills: List[str]) -> List[str]:
        """Get the next skills to train based on training priorities."""
        if not self.current_build:
            return []
        
        training_priorities = self.current_build.training_priorities
        next_skills = []
        
        for skill in training_priorities:
            if skill not in current_skills:
                next_skills.append(skill)
                if len(next_skills) >= 3:  # Limit to next 3 skills
                    break
        
        return next_skills
    
    def _estimate_completion_time(self, next_skills: List[str]) -> float:
        """Estimate time to complete the next skills (in hours)."""
        # Rough estimation: 1-2 hours per skill depending on complexity
        base_time_per_skill = 1.5  # hours
        total_time = len(next_skills) * base_time_per_skill
        
        # Adjust based on skill complexity
        for skill in next_skills:
            if "Master" in skill:
                total_time += 0.5  # Master skills take longer
            elif "Novice" in skill:
                total_time -= 0.2  # Novice skills are faster
        
        return max(0.5, total_time)  # Minimum 30 minutes
    
    def _get_recommended_activities(self, phase: ProgressionPhase) -> List[str]:
        """Get recommended activities for the current phase."""
        if not self.current_build:
            return ["questing", "combat"]
        
        leveling_plan = self.current_build.leveling_plan
        phase_data = leveling_plan.get(phase.value, {})
        combat_style = phase_data.get("combat_style", "basic_combat")
        
        recommendations = {
            ProgressionPhase.EARLY_GAME: ["questing", "basic_combat", "skill_training"],
            ProgressionPhase.MID_GAME: ["questing", "combat", "skill_training", "group_activities"],
            ProgressionPhase.LATE_GAME: ["elite_combat", "group_activities", "skill_training", "endgame_content"],
            ProgressionPhase.COMPLETE: ["endgame_content", "group_activities", "elite_combat"]
        }
        
        return recommendations.get(phase, ["questing", "combat"])
    
    def _log_build_detection(self, detection_result: DetectionResult):
        """Log build detection results."""
        log_entry = {
            "timestamp": time.time(),
            "detected_build": detection_result.detected_build.build_name if detection_result.detected_build else None,
            "confidence": detection_result.confidence_score,
            "current_skills": detection_result.current_skills,
            "detection_method": detection_result.detection_method.value,
            "error_message": detection_result.error_message
        }
        
        self.build_detection_log.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.build_detection_log) > 100:
            self.build_detection_log = self.build_detection_log[-100:]
    
    def follow_skill_progression(self) -> bool:
        """Follow the skill progression logic for the current build."""
        if not self.current_training_plan:
            self.logger.warning("No training plan available")
            return False
        
        try:
            next_skills = self.current_training_plan.next_skills
            if not next_skills:
                self.logger.info("No more skills to train")
                return True
            
            # Find trainers for next skills
            for skill in next_skills:
                self.logger.info(f"Attempting to train: {skill}")
                # This would integrate with the trainer system
                # For now, just log the intention
                
            return True
            
        except Exception as e:
            self.logger.error(f"Skill progression failed: {e}")
            return False
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary including build detection."""
        session_duration = time.time() - self.session_start_time
        
        return {
            "session_duration": session_duration,
            "current_build": self.current_build.name if self.current_build else None,
            "build_type": self.current_build.build_type if self.current_build else None,
            "current_phase": self.current_training_plan.current_phase.value if self.current_training_plan else None,
            "completion_ratio": self.current_training_plan.completion_ratio if self.current_training_plan else 0.0,
            "next_skills": self.current_training_plan.next_skills if self.current_training_plan else [],
            "detection_log": self.build_detection_log,
            "combat_profile": self.current_build.combat_profile if self.current_build else None,
            "recommended_activities": self.current_training_plan.recommended_activities if self.current_training_plan else []
        }
    
    def get_build_progress(self) -> Dict[str, Any]:
        """Get detailed build progress information."""
        if not self.current_build or not self.current_training_plan:
            return {"error": "No build or training plan available"}
        
        return {
            "build_name": self.current_build.name,
            "build_type": self.current_build.build_type,
            "primary_profession": self.current_build.primary_profession,
            "secondary_profession": self.current_build.secondary_profession,
            "current_phase": self.current_training_plan.current_phase.value,
            "completion_ratio": self.current_training_plan.completion_ratio,
            "completed_skills": self.current_training_plan.completed_skills,
            "next_skills": self.current_training_plan.next_skills,
            "missing_skills": self.current_training_plan.missing_skills,
            "estimated_time_to_complete": self.current_training_plan.estimated_time_to_complete,
            "recommended_activities": self.current_training_plan.recommended_activities
        }
    
    def force_build_selection(self, build_name: str) -> bool:
        """Force selection of a specific build."""
        try:
            build_data = self.spec_detector.get_build_info(build_name)
            if not build_data:
                self.logger.error(f"Build not found: {build_name}")
                return False
            
            self.current_build = self._create_build_info(build_name, build_data)
            self._load_combat_profile()
            
            # Create training plan with empty skills (assumes starting fresh)
            detection_result = DetectionResult(
                detected_build=None,
                current_skills=[],
                available_skills=[],
                detection_timestamp=time.time(),
                detection_method=self.spec_detector.DetectionMethod.OCR,
                confidence_score=1.0
            )
            
            self.current_training_plan = self._create_training_plan(detection_result)
            
            self.logger.info(f"Force selected build: {build_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Force build selection failed: {e}")
            return False
    
    def get_available_builds(self) -> List[Dict[str, Any]]:
        """Get list of available builds with descriptions."""
        builds = []
        
        for build_name in self.spec_detector.get_available_builds():
            build_data = self.spec_detector.get_build_info(build_name)
            if build_data:
                builds.append({
                    "name": build_name,
                    "description": build_data.get("description", ""),
                    "build_type": build_data.get("build_type", ""),
                    "primary_profession": build_data.get("primary_profession", ""),
                    "secondary_profession": build_data.get("secondary_profession"),
                    "combat_profile": build_data.get("combat_profile", "")
                })
        
        return builds


# Global convenience functions
def get_build_manager() -> BuildManager:
    """Get a global build manager instance."""
    return BuildManager()


def auto_detect_and_select_build() -> Optional[BuildInfo]:
    """Automatically detect and select the appropriate build."""
    manager = get_build_manager()
    return manager.detect_and_select_build()


def get_current_build_progress() -> Dict[str, Any]:
    """Get current build progress information."""
    manager = get_build_manager()
    return manager.get_build_progress()


def follow_current_build_progression() -> bool:
    """Follow the skill progression for the current build."""
    manager = get_build_manager()
    return manager.follow_skill_progression() 
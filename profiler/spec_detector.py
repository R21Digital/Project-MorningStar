"""
Spec Detector

This module provides functionality to detect character specifications (profession builds)
by reading UI elements and matching against known build templates.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import difflib
import re

import cv2
import numpy as np

from core.screenshot import capture_screen
from core.ocr import extract_text_from_screen
from core.dialogue_handler import DialogueHandler


class DetectionMethod(Enum):
    """Detection method enumeration."""
    OCR = "ocr"
    TEMPLATE = "template"
    MEMORY = "memory"
    UI_READ = "ui_read"


class BuildType(Enum):
    """Build type enumeration."""
    PURE_COMBAT = "pure_combat"
    PURE_HEALER = "pure_healer"
    HYBRID = "hybrid"
    MELEE_COMBAT = "melee_combat"
    AGILE_COMBAT = "agile_combat"
    COMBAT_HEALER = "combat_healer"


@dataclass
class BuildMatch:
    """Represents a build match result."""
    build_name: str
    confidence: float
    matched_skills: List[str]
    missing_skills: List[str]
    build_type: BuildType
    primary_profession: str
    secondary_profession: Optional[str] = None
    detection_method: DetectionMethod = DetectionMethod.OCR


@dataclass
class DetectionResult:
    """Represents a detection result."""
    detected_build: Optional[BuildMatch]
    current_skills: List[str]
    available_skills: List[str]
    detection_timestamp: float
    detection_method: DetectionMethod
    confidence_score: float
    error_message: Optional[str] = None


class SpecDetector:
    """Detects character specifications and matches against known builds."""
    
    def __init__(self, data_dir: str = "data", builds_file: str = "data/profiler/builds.json"):
        self.logger = logging.getLogger("spec_detector")
        self.data_dir = Path(data_dir)
        self.builds_file = Path(builds_file)
        self.builds_data: Dict[str, Any] = {}
        self.detection_config: Dict[str, Any] = {}
        self.ocr_handler = DialogueHandler()
        self.last_detection: Optional[DetectionResult] = None
        self.detection_cache: Dict[str, DetectionResult] = {}
        self.cache_timeout = 30.0  # seconds
        self.confidence_thresholds = {
            "exact_match": 0.95,
            "partial_match": 0.80,
            "fuzzy_match": 0.60
        }
        self._setup_logging()
        self._load_builds_data()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _load_builds_data(self):
        """Load builds data from JSON file."""
        try:
            if not self.builds_file.exists():
                self.logger.warning(f"Builds file not found: {self.builds_file}")
                return
            
            with open(self.builds_file, 'r', encoding='utf-8') as f:
                self.builds_data = json.load(f)
            
            self.detection_config = self.builds_data.get("build_detection", {})
            self.confidence_thresholds.update(
                self.detection_config.get("confidence_thresholds", {})
            )
            
            self.logger.info(f"Loaded {len(self.builds_data.get('builds', {}))} builds")
            
        except Exception as e:
            self.logger.error(f"Failed to load builds data: {e}")
    
    def detect_current_spec(self, force_refresh: bool = False) -> DetectionResult:
        """Detect the current character specification."""
        try:
            # Check cache first
            if not force_refresh and self.last_detection:
                time_since_last = time.time() - self.last_detection.detection_timestamp
                if time_since_last < self.cache_timeout:
                    self.logger.debug("Using cached detection result")
                    return self.last_detection
            
            # Perform detection
            current_skills = self._read_current_skills()
            available_skills = self._get_available_skills()
            
            if not current_skills:
                return DetectionResult(
                    detected_build=None,
                    current_skills=[],
                    available_skills=available_skills,
                    detection_timestamp=time.time(),
                    detection_method=DetectionMethod.OCR,
                    confidence_score=0.0,
                    error_message="No skills detected"
                )
            
            # Match against known builds
            best_match = self._match_build(current_skills)
            
            result = DetectionResult(
                detected_build=best_match,
                current_skills=current_skills,
                available_skills=available_skills,
                detection_timestamp=time.time(),
                detection_method=DetectionMethod.OCR,
                confidence_score=best_match.confidence if best_match else 0.0
            )
            
            self.last_detection = result
            return result
            
        except Exception as e:
            self.logger.error(f"Detection failed: {e}")
            return DetectionResult(
                detected_build=None,
                current_skills=[],
                available_skills=[],
                detection_timestamp=time.time(),
                detection_method=DetectionMethod.OCR,
                confidence_score=0.0,
                error_message=str(e)
            )
    
    def _read_current_skills(self) -> List[str]:
        """Read current skills from UI using OCR."""
        try:
            # Capture screen for skill detection
            screen = capture_screen()
            if screen is None:
                self.logger.warning("Failed to capture screen for skill detection")
                return []
            
            # Extract text from screen
            text_data = extract_text_from_screen(screen)
            if not text_data:
                self.logger.warning("No text extracted from screen")
                return []
            
            # Parse skills from extracted text
            skills = self._parse_skills_from_text(text_data)
            
            self.logger.info(f"Detected {len(skills)} skills: {skills}")
            return skills
            
        except Exception as e:
            self.logger.error(f"Failed to read current skills: {e}")
            return []
    
    def _parse_skills_from_text(self, text_data: List[Dict[str, Any]]) -> List[str]:
        """Parse skills from OCR text data."""
        skills = []
        profession_patterns = self.detection_config.get("ocr_patterns", {}).get("profession_titles", [])
        skill_indicators = self.detection_config.get("ocr_patterns", {}).get("skill_indicators", [])
        
        for text_item in text_data:
            text = text_item.get("text", "").strip()
            if not text:
                continue
            
            # Check for profession titles
            for profession in profession_patterns:
                if profession.lower() in text.lower():
                    skills.append(profession)
            
            # Check for skill indicators
            for indicator in skill_indicators:
                if indicator.lower() in text.lower():
                    # Extract full skill name
                    skill_name = self._extract_skill_name(text, indicator)
                    if skill_name:
                        skills.append(skill_name)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        
        return unique_skills
    
    def _extract_skill_name(self, text: str, indicator: str) -> Optional[str]:
        """Extract full skill name from text containing indicator."""
        # Simple pattern matching for skill names
        patterns = [
            rf"{indicator}\s+(\w+(?:\s+\w+)*)",  # "Novice Marksman"
            rf"(\w+(?:\s+\w+)*)\s+{indicator}",  # "Marksman Novice"
            rf"{indicator}",  # Just the indicator itself
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.groups() else indicator
        
        return None
    
    def _get_available_skills(self) -> List[str]:
        """Get list of available skills from all builds."""
        available_skills = set()
        
        for build_name, build_data in self.builds_data.get("builds", {}).items():
            skill_trees = build_data.get("skill_trees", {})
            for profession, tree_data in skill_trees.items():
                required_skills = tree_data.get("required_skills", [])
                optional_skills = tree_data.get("optional_skills", [])
                available_skills.update(required_skills)
                available_skills.update(optional_skills)
        
        return sorted(list(available_skills))
    
    def _match_build(self, current_skills: List[str]) -> Optional[BuildMatch]:
        """Match current skills against known builds."""
        best_match = None
        best_confidence = 0.0
        
        for build_name, build_data in self.builds_data.get("builds", {}).items():
            match_result = self._calculate_build_match(build_name, build_data, current_skills)
            
            if match_result and match_result.confidence > best_confidence:
                best_match = match_result
                best_confidence = match_result.confidence
        
        return best_match
    
    def _calculate_build_match(self, build_name: str, build_data: Dict[str, Any], current_skills: List[str]) -> Optional[BuildMatch]:
        """Calculate match between current skills and a specific build."""
        try:
            # Get all skills for this build
            build_skills = set()
            skill_trees = build_data.get("skill_trees", {})
            
            for profession, tree_data in skill_trees.items():
                required_skills = tree_data.get("required_skills", [])
                optional_skills = tree_data.get("optional_skills", [])
                build_skills.update(required_skills)
                build_skills.update(optional_skills)
            
            # Calculate matches
            matched_skills = [skill for skill in current_skills if skill in build_skills]
            missing_skills = [skill for skill in build_skills if skill not in current_skills]
            
            if not matched_skills:
                return None
            
            # Calculate confidence based on match ratio
            total_build_skills = len(build_skills)
            match_ratio = len(matched_skills) / total_build_skills
            
            # Adjust confidence based on required vs optional skills
            required_skills = set()
            for tree_data in skill_trees.values():
                required_skills.update(tree_data.get("required_skills", []))
            
            required_matches = len([skill for skill in matched_skills if skill in required_skills])
            required_ratio = required_matches / len(required_skills) if required_skills else 1.0
            
            # Final confidence calculation
            confidence = (match_ratio * 0.6) + (required_ratio * 0.4)
            
            # Apply fuzzy matching for similar skill names
            fuzzy_matches = self._find_fuzzy_matches(current_skills, build_skills)
            if fuzzy_matches:
                confidence += 0.1  # Bonus for fuzzy matches
            
            confidence = min(confidence, 1.0)  # Cap at 1.0
            
            # Only return if confidence meets minimum threshold
            if confidence < self.confidence_thresholds["fuzzy_match"]:
                return None
            
            return BuildMatch(
                build_name=build_name,
                confidence=confidence,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                build_type=BuildType(build_data.get("build_type", "pure_combat")),
                primary_profession=build_data.get("primary_profession", ""),
                secondary_profession=build_data.get("secondary_profession")
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating build match for {build_name}: {e}")
            return None
    
    def _find_fuzzy_matches(self, current_skills: List[str], build_skills: set) -> List[str]:
        """Find fuzzy matches between current skills and build skills."""
        fuzzy_matches = []
        
        for current_skill in current_skills:
            for build_skill in build_skills:
                # Use difflib for fuzzy string matching
                similarity = difflib.SequenceMatcher(None, current_skill.lower(), build_skill.lower()).ratio()
                if similarity > 0.8:  # 80% similarity threshold
                    fuzzy_matches.append(build_skill)
        
        return fuzzy_matches
    
    def get_build_info(self, build_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific build."""
        return self.builds_data.get("builds", {}).get(build_name)
    
    def get_available_builds(self) -> List[str]:
        """Get list of available build names."""
        return list(self.builds_data.get("builds", {}).keys())
    
    def get_default_build(self, player_type: str = "new_character") -> Optional[str]:
        """Get default build for a player type."""
        default_builds = self.builds_data.get("default_builds", {})
        return default_builds.get(player_type)
    
    def validate_build_completion(self, build_name: str, current_skills: List[str]) -> Dict[str, Any]:
        """Validate how complete a build is based on current skills."""
        build_data = self.get_build_info(build_name)
        if not build_data:
            return {"valid": False, "error": "Build not found"}
        
        skill_trees = build_data.get("skill_trees", {})
        total_required = 0
        total_optional = 0
        completed_required = 0
        completed_optional = 0
        
        for profession, tree_data in skill_trees.items():
            required_skills = tree_data.get("required_skills", [])
            optional_skills = tree_data.get("optional_skills", [])
            
            total_required += len(required_skills)
            total_optional += len(optional_skills)
            
            for skill in required_skills:
                if skill in current_skills:
                    completed_required += 1
            
            for skill in optional_skills:
                if skill in current_skills:
                    completed_optional += 1
        
        completion_ratio = completed_required / total_required if total_required > 0 else 0.0
        
        return {
            "valid": True,
            "build_name": build_name,
            "total_required": total_required,
            "total_optional": total_optional,
            "completed_required": completed_required,
            "completed_optional": completed_optional,
            "completion_ratio": completion_ratio,
            "is_complete": completion_ratio >= 1.0
        }
    
    def get_detection_summary(self) -> Dict[str, Any]:
        """Get summary of detection capabilities and results."""
        return {
            "total_builds": len(self.builds_data.get("builds", {})),
            "available_builds": self.get_available_builds(),
            "last_detection": self.last_detection.detection_timestamp if self.last_detection else None,
            "confidence_thresholds": self.confidence_thresholds,
            "detection_config": self.detection_config
        }


# Global convenience functions
def get_spec_detector() -> SpecDetector:
    """Get a global spec detector instance."""
    return SpecDetector()


def detect_current_build() -> Optional[BuildMatch]:
    """Detect the current character build."""
    detector = get_spec_detector()
    result = detector.detect_current_spec()
    return result.detected_build


def get_build_completion(build_name: str) -> Dict[str, Any]:
    """Get completion status for a specific build."""
    detector = get_spec_detector()
    result = detector.detect_current_spec()
    return detector.validate_build_completion(build_name, result.current_skills) 
"""Build Analyzer for comparing skill data to build information.

This module analyzes combat performance against build data from SkillCalc,
providing insights on skill point ROI, build efficiency, and optimization
recommendations.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

from core.skill_calculator_parser import SkillCalculatorParser
from core.build_aware_behavior import BuildAwareBehavior
from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)

@dataclass
class SkillPointROI:
    """Data class for skill point return on investment analysis."""
    skill_name: str
    skill_line: str
    skill_points_invested: int
    damage_dealt: int
    usage_count: int
    roi_score: float
    efficiency_rating: str
    recommendation: str

@dataclass
class BuildAnalysis:
    """Data class for comprehensive build analysis."""
    build_name: str
    total_skill_points: int
    skills_analyzed: int
    average_roi: float
    most_efficient_skills: List[SkillPointROI]
    least_efficient_skills: List[SkillPointROI]
    unused_skills: List[str]
    build_efficiency_score: float
    optimization_recommendations: List[str]

@dataclass
class SkillLineAnalysis:
    """Data class for skill line performance analysis."""
    skill_line: str
    total_skill_points: int
    skills_used: int
    total_damage: int
    average_dps: float
    uptime_percentage: float
    efficiency_score: float
    unused_skills: List[str]

class BuildAnalyzer:
    """Analyzes combat performance against build data for optimization insights."""
    
    def __init__(self):
        """Initialize the build analyzer."""
        self.skill_parser = SkillCalculatorParser()
        self.build_aware_behavior = BuildAwareBehavior()
        self.current_build = None
        self.build_data = {}
        
        # Skill point costs (approximate values)
        self.skill_point_costs = {
            "novice": 4,
            "apprentice": 8,
            "journeyman": 16,
            "expert": 32,
            "master": 64
        }
        
        # Skill line definitions
        self.skill_lines = {
            "combat": ["rifleman", "pistoleer", "carbineer", "brawler", "marksman"],
            "support": ["medic", "entertainer", "scout"],
            "crafting": ["artisan", "chef", "structures"],
            "social": ["entertainer", "politician"]
        }
        
        log_event("[BUILD_ANALYZER] Initialized build analyzer")
    
    def load_build_from_link(self, skill_calculator_url: str) -> Dict[str, Any]:
        """Load and parse a build from a skill calculator link.
        
        Parameters
        ----------
        skill_calculator_url : str
            URL from swgr.org/skill-calculator/
            
        Returns
        -------
        dict
            Parsed build information
        """
        try:
            log_event(f"[BUILD_ANALYZER] Loading build from skill calculator link")
            
            # Parse the skill calculator link
            build_data = self.skill_parser.parse_skill_calculator_link(skill_calculator_url)
            
            # Store the current build
            self.current_build = build_data
            self.build_data = build_data
            
            # Load into build-aware behavior
            self.build_aware_behavior.load_build_from_link(skill_calculator_url)
            
            log_event(f"[BUILD_ANALYZER] Successfully loaded build: {build_data.get('build_summary', 'Unknown')}")
            return build_data
            
        except Exception as e:
            log_event(f"[BUILD_ANALYZER] Error loading build from link: {e}")
            raise
    
    def load_build_from_file(self, filepath: str) -> Dict[str, Any]:
        """Load build data from a JSON file.
        
        Parameters
        ----------
        filepath : str
            Path to build JSON file
            
        Returns
        -------
        dict
            Loaded build data
        """
        try:
            with open(filepath, 'r') as f:
                build_data = json.load(f)
            
            self.current_build = build_data
            self.build_data = build_data
            
            log_event(f"[BUILD_ANALYZER] Loaded build from file: {filepath}")
            return build_data
            
        except Exception as e:
            log_event(f"[BUILD_ANALYZER] Error loading build from file: {e}")
            raise
    
    def analyze_skill_point_roi(self, combat_data: Dict[str, Any]) -> List[SkillPointROI]:
        """Analyze skill point return on investment for each skill.
        
        Parameters
        ----------
        combat_data : dict
            Combat performance data including skill usage
            
        Returns
        -------
        List[SkillPointROI]
            ROI analysis for each skill
        """
        if not self.current_build:
            log_event("[BUILD_ANALYZER] No build loaded for ROI analysis")
            return []
        
        roi_analysis = []
        skills_used = combat_data.get("skill_usage", {})
        abilities_granted = self.current_build.get("abilities_granted", [])
        
        for skill_name, usage_data in skills_used.items():
            # Estimate skill points invested based on skill name and level
            skill_points = self._estimate_skill_points(skill_name)
            
            # Get combat performance data
            damage_dealt = usage_data.get("total_damage", 0)
            usage_count = usage_data.get("usage_count", 0)
            
            # Calculate ROI score (damage per skill point)
            roi_score = 0.0
            if skill_points > 0:
                roi_score = damage_dealt / skill_points
            
            # Determine efficiency rating
            efficiency_rating = self._calculate_efficiency_rating(roi_score, usage_count)
            
            # Generate recommendation
            recommendation = self._generate_skill_recommendation(
                skill_name, roi_score, usage_count, skill_points, abilities_granted
            )
            
            # Determine skill line
            skill_line = self._determine_skill_line(skill_name)
            
            roi_analysis.append(SkillPointROI(
                skill_name=skill_name,
                skill_line=skill_line,
                skill_points_invested=skill_points,
                damage_dealt=damage_dealt,
                usage_count=usage_count,
                roi_score=roi_score,
                efficiency_rating=efficiency_rating,
                recommendation=recommendation
            ))
        
        # Sort by ROI score (highest first)
        roi_analysis.sort(key=lambda x: x.roi_score, reverse=True)
        
        log_event(f"[BUILD_ANALYZER] Analyzed ROI for {len(roi_analysis)} skills")
        return roi_analysis
    
    def analyze_build_efficiency(self, combat_data: Dict[str, Any]) -> BuildAnalysis:
        """Analyze overall build efficiency and provide recommendations.
        
        Parameters
        ----------
        combat_data : dict
            Combat performance data
            
        Returns
        -------
        BuildAnalysis
            Comprehensive build analysis
        """
        if not self.current_build:
            log_event("[BUILD_ANALYZER] No build loaded for efficiency analysis")
            return None
        
        # Analyze skill point ROI
        roi_analysis = self.analyze_skill_point_roi(combat_data)
        
        # Calculate total skill points
        total_skill_points = sum(roi.skill_points_invested for roi in roi_analysis)
        
        # Calculate average ROI
        average_roi = 0.0
        if roi_analysis:
            average_roi = sum(roi.roi_score for roi in roi_analysis) / len(roi_analysis)
        
        # Identify most and least efficient skills
        most_efficient_skills = roi_analysis[:5] if len(roi_analysis) >= 5 else roi_analysis
        least_efficient_skills = roi_analysis[-5:] if len(roi_analysis) >= 5 else roi_analysis
        
        # Find unused skills from build
        used_skills = {roi.skill_name for roi in roi_analysis}
        abilities_granted = self.current_build.get("abilities_granted", [])
        unused_skills = [skill for skill in abilities_granted if skill not in used_skills]
        
        # Calculate build efficiency score
        build_efficiency_score = self._calculate_build_efficiency_score(
            roi_analysis, total_skill_points, combat_data
        )
        
        # Generate optimization recommendations
        optimization_recommendations = self._generate_optimization_recommendations(
            roi_analysis, unused_skills, build_efficiency_score
        )
        
        build_analysis = BuildAnalysis(
            build_name=self.current_build.get("build_summary", "Unknown Build"),
            total_skill_points=total_skill_points,
            skills_analyzed=len(roi_analysis),
            average_roi=average_roi,
            most_efficient_skills=most_efficient_skills,
            least_efficient_skills=least_efficient_skills,
            unused_skills=unused_skills,
            build_efficiency_score=build_efficiency_score,
            optimization_recommendations=optimization_recommendations
        )
        
        log_event(f"[BUILD_ANALYZER] Build efficiency analysis complete - "
                 f"Score: {build_efficiency_score:.2f}, Average ROI: {average_roi:.2f}")
        
        return build_analysis
    
    def analyze_skill_line_performance(self, combat_data: Dict[str, Any]) -> List[SkillLineAnalysis]:
        """Analyze performance by skill line.
        
        Parameters
        ----------
        combat_data : dict
            Combat performance data
            
        Returns
        -------
        List[SkillLineAnalysis]
            Skill line performance analysis
        """
        skill_line_analysis = []
        skill_line_data = combat_data.get("skill_line_analysis", {})
        
        for skill_line, line_data in skill_line_data.items():
            # Calculate total skill points for this line
            total_skill_points = self._calculate_skill_line_points(skill_line)
            
            # Get performance metrics
            skills_used = len(line_data.get("skills_in_line", []))
            total_damage = sum(
                combat_data.get("skill_usage", {}).get(skill, {}).get("total_damage", 0)
                for skill in line_data.get("skills_in_line", [])
            )
            
            # Calculate average DPS
            session_duration = combat_data.get("session_duration", 1)
            average_dps = total_damage / session_duration if session_duration > 0 else 0
            
            # Get uptime percentage
            uptime_percentage = line_data.get("uptime_percentage", 0)
            
            # Calculate efficiency score
            efficiency_score = self._calculate_skill_line_efficiency(
                total_damage, total_skill_points, uptime_percentage
            )
            
            # Find unused skills in this line
            used_skills_in_line = set(line_data.get("skills_in_line", []))
            all_skills_in_line = self._get_all_skills_in_line(skill_line)
            unused_skills = list(all_skills_in_line - used_skills_in_line)
            
            analysis = SkillLineAnalysis(
                skill_line=skill_line,
                total_skill_points=total_skill_points,
                skills_used=skills_used,
                total_damage=total_damage,
                average_dps=average_dps,
                uptime_percentage=uptime_percentage,
                efficiency_score=efficiency_score,
                unused_skills=unused_skills
            )
            
            skill_line_analysis.append(analysis)
        
        # Sort by efficiency score
        skill_line_analysis.sort(key=lambda x: x.efficiency_score, reverse=True)
        
        log_event(f"[BUILD_ANALYZER] Analyzed {len(skill_line_analysis)} skill lines")
        return skill_line_analysis
    
    def _estimate_skill_points(self, skill_name: str) -> int:
        """Estimate skill points invested in a skill based on its name.
        
        Parameters
        ----------
        skill_name : str
            Name of the skill
            
        Returns
        -------
        int
            Estimated skill points invested
        """
        skill_name_lower = skill_name.lower()
        
        # Check for skill level indicators
        if "master" in skill_name_lower:
            return self.skill_point_costs["master"]
        elif "expert" in skill_name_lower:
            return self.skill_point_costs["expert"]
        elif "journeyman" in skill_name_lower:
            return self.skill_point_costs["journeyman"]
        elif "apprentice" in skill_name_lower:
            return self.skill_point_costs["apprentice"]
        elif "novice" in skill_name_lower:
            return self.skill_point_costs["novice"]
        else:
            # Default to apprentice level
            return self.skill_point_costs["apprentice"]
    
    def _calculate_efficiency_rating(self, roi_score: float, usage_count: int) -> str:
        """Calculate efficiency rating based on ROI and usage.
        
        Parameters
        ----------
        roi_score : float
            Return on investment score
        usage_count : int
            Number of times skill was used
            
        Returns
        -------
        str
            Efficiency rating
        """
        if roi_score > 1000 and usage_count > 10:
            return "Excellent"
        elif roi_score > 500 and usage_count > 5:
            return "Good"
        elif roi_score > 100 and usage_count > 2:
            return "Average"
        elif usage_count == 0:
            return "Unused"
        else:
            return "Poor"
    
    def _generate_skill_recommendation(self, skill_name: str, roi_score: float, 
                                     usage_count: int, skill_points: int, 
                                     abilities_granted: List[str]) -> str:
        """Generate recommendation for a skill.
        
        Parameters
        ----------
        skill_name : str
            Name of the skill
        roi_score : float
            ROI score
        usage_count : int
            Usage count
        skill_points : int
            Skill points invested
        abilities_granted : List[str]
            List of abilities granted by the build
            
        Returns
        -------
        str
            Recommendation text
        """
        if skill_name not in abilities_granted:
            return "Skill not in current build - consider adding"
        
        if usage_count == 0:
            return "Skill unused - consider removing or using more"
        
        if roi_score < 100:
            return "Low ROI - consider replacing with more efficient skill"
        elif roi_score > 1000:
            return "Excellent ROI - consider investing more points"
        else:
            return "Good performance - maintain current investment"
    
    def _determine_skill_line(self, skill_name: str) -> str:
        """Determine which skill line a skill belongs to.
        
        Parameters
        ----------
        skill_name : str
            Name of the skill
            
        Returns
        -------
        str
            Skill line name
        """
        skill_name_lower = skill_name.lower()
        
        for line_name, professions in self.skill_lines.items():
            for profession in professions:
                if profession in skill_name_lower:
                    return line_name
        
        return "unknown"
    
    def _calculate_build_efficiency_score(self, roi_analysis: List[SkillPointROI], 
                                        total_skill_points: int, 
                                        combat_data: Dict[str, Any]) -> float:
        """Calculate overall build efficiency score.
        
        Parameters
        ----------
        roi_analysis : List[SkillPointROI]
            ROI analysis for all skills
        total_skill_points : int
            Total skill points invested
        combat_data : dict
            Combat performance data
            
        Returns
        -------
        float
            Build efficiency score (0-100)
        """
        if not roi_analysis or total_skill_points == 0:
            return 0.0
        
        # Calculate weighted average ROI
        total_damage = sum(roi.damage_dealt for roi in roi_analysis)
        weighted_roi = total_damage / total_skill_points if total_skill_points > 0 else 0
        
        # Calculate skill utilization rate
        used_skills = len(roi_analysis)
        total_skills = len(self.current_build.get("abilities_granted", []))
        utilization_rate = (used_skills / total_skills * 100) if total_skills > 0 else 0
        
        # Calculate efficiency score (0-100)
        efficiency_score = min(100.0, (weighted_roi / 1000) * 50 + utilization_rate * 0.5)
        
        return efficiency_score
    
    def _generate_optimization_recommendations(self, roi_analysis: List[SkillPointROI], 
                                            unused_skills: List[str], 
                                            build_efficiency_score: float) -> List[str]:
        """Generate optimization recommendations.
        
        Parameters
        ----------
        roi_analysis : List[SkillPointROI]
            ROI analysis for all skills
        unused_skills : List[str]
            List of unused skills
        build_efficiency_score : float
            Overall build efficiency score
            
        Returns
        -------
        List[str]
            List of optimization recommendations
        """
        recommendations = []
        
        # Analyze unused skills
        if unused_skills:
            recommendations.append(f"Consider using {len(unused_skills)} unused skills: {', '.join(unused_skills[:3])}")
        
        # Analyze low ROI skills
        low_roi_skills = [roi for roi in roi_analysis if roi.roi_score < 100 and roi.usage_count > 0]
        if low_roi_skills:
            recommendations.append(f"Replace {len(low_roi_skills)} low-ROI skills with more efficient alternatives")
        
        # Analyze high ROI skills
        high_roi_skills = [roi for roi in roi_analysis if roi.roi_score > 1000]
        if high_roi_skills:
            recommendations.append(f"Consider investing more points in {len(high_roi_skills)} high-performing skills")
        
        # Overall efficiency recommendations
        if build_efficiency_score < 50:
            recommendations.append("Overall build efficiency is low - consider major restructuring")
        elif build_efficiency_score < 75:
            recommendations.append("Build efficiency is moderate - minor optimizations recommended")
        else:
            recommendations.append("Build efficiency is good - maintain current strategy")
        
        return recommendations
    
    def _calculate_skill_line_points(self, skill_line: str) -> int:
        """Calculate total skill points for a skill line.
        
        Parameters
        ----------
        skill_line : str
            Name of the skill line
            
        Returns
        -------
        int
            Total skill points invested in the line
        """
        # This is a simplified calculation - in practice, you'd need to parse the actual build
        professions = self.skill_lines.get(skill_line, [])
        return len(professions) * 32  # Assume 32 points per profession
    
    def _calculate_skill_line_efficiency(self, total_damage: int, skill_points: int, 
                                       uptime_percentage: float) -> float:
        """Calculate efficiency score for a skill line.
        
        Parameters
        ----------
        total_damage : int
            Total damage dealt by skills in the line
        skill_points : int
            Skill points invested in the line
        uptime_percentage : float
            Uptime percentage for the line
            
        Returns
        -------
        float
            Efficiency score
        """
        if skill_points == 0:
            return 0.0
        
        damage_per_point = total_damage / skill_points
        efficiency = damage_per_point * (uptime_percentage / 100)
        
        return efficiency
    
    def _get_all_skills_in_line(self, skill_line: str) -> set:
        """Get all possible skills in a skill line.
        
        Parameters
        ----------
        skill_line : str
            Name of the skill line
            
        Returns
        -------
        set
            Set of all skills in the line
        """
        # This would need to be populated with actual skill data
        # For now, return a basic set based on the skill line
        if skill_line == "combat":
            return {"rifle_shot", "pistol_shot", "melee_attack", "sniper_shot"}
        elif skill_line == "support":
            return {"heal", "cure_poison", "buff", "debuff"}
        else:
            return set() 
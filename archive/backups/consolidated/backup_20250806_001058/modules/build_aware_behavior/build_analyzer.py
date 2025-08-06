"""
Build Analyzer - Build Analysis and Combat Preference Detection

This module provides comprehensive build analysis including:
- Combat preference analysis
- Skill tree optimization assessment
- Build synergy analysis
- Combat behavior recommendations
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from .skillcalc_parser import BuildInfo, ProfessionType, WeaponClass, CombatRange

logger = logging.getLogger(__name__)


class CombatStyle(Enum):
    """Combat style preferences."""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"
    SPECIALIZED = "specialized"


class BuildOptimization(Enum):
    """Build optimization levels."""
    OPTIMAL = "optimal"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"


@dataclass
class CombatPreference:
    """Combat preference analysis."""
    primary_range: CombatRange
    secondary_range: Optional[CombatRange] = None
    combat_style: CombatStyle = CombatStyle.BALANCED
    preferred_weapons: List[str] = None
    avoidance_skills: List[str] = None
    defensive_skills: List[str] = None
    offensive_skills: List[str] = None
    
    def __post_init__(self):
        if self.preferred_weapons is None:
            self.preferred_weapons = []
        if self.avoidance_skills is None:
            self.avoidance_skills = []
        if self.defensive_skills is None:
            self.defensive_skills = []
        if self.offensive_skills is None:
            self.offensive_skills = []


@dataclass
class BuildAnalysis:
    """Comprehensive build analysis results."""
    build_info: BuildInfo
    combat_preference: CombatPreference
    optimization_level: BuildOptimization
    synergy_score: float
    recommendations: List[str]
    warnings: List[str]
    behavior_adjustments: Dict[str, Any]
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
        if self.warnings is None:
            self.warnings = []
        if self.behavior_adjustments is None:
            self.behavior_adjustments = {}


class BuildAnalyzer:
    """Comprehensive build analysis system."""
    
    def __init__(self):
        """Initialize the build analyzer."""
        # Combat style detection patterns
        self.aggressive_patterns = [
            "berserker", "frenzy", "rage", "aggressive", "offensive"
        ]
        
        self.defensive_patterns = [
            "defensive", "block", "dodge", "evasion", "shield"
        ]
        
        # Weapon preference patterns
        self.weapon_preferences = {
            CombatRange.MELEE: ["sword", "polearm", "axe", "knife", "unarmed"],
            CombatRange.RANGED: ["rifle", "pistol", "carbine", "bow"],
            CombatRange.HEAVY: ["heavy_weapon", "rocket", "grenade"],
            CombatRange.MIXED: ["mixed", "versatile"]
        }
        
        # Skill categorization
        self.offensive_skills = [
            "damage", "attack", "strike", "shot", "blast", "burst"
        ]
        
        self.defensive_skills = [
            "block", "dodge", "evasion", "shield", "armor", "resist"
        ]
        
        self.avoidance_skills = [
            "stealth", "concealment", "camouflage", "invisibility"
        ]
        
        logger.info("BuildAnalyzer initialized")
    
    def analyze_build(self, build_info: BuildInfo) -> BuildAnalysis:
        """Analyze a build and provide comprehensive insights.
        
        Parameters
        ----------
        build_info : BuildInfo
            Build information to analyze
            
        Returns
        -------
        BuildAnalysis
            Comprehensive build analysis
        """
        analysis = BuildAnalysis(
            build_info=build_info,
            combat_preference=CombatPreference(primary_range=CombatRange.MIXED),
            optimization_level=BuildOptimization.AVERAGE,
            synergy_score=0.0,
            recommendations=[],
            warnings=[],
            behavior_adjustments={}
        )
        
        try:
            # Analyze combat preferences
            analysis.combat_preference = self._analyze_combat_preferences(build_info)
            
            # Assess build optimization
            analysis.optimization_level = self._assess_optimization(build_info)
            
            # Calculate synergy score
            analysis.synergy_score = self._calculate_synergy_score(build_info)
            
            # Generate recommendations
            analysis.recommendations = self._generate_recommendations(build_info, analysis)
            
            # Generate warnings
            analysis.warnings = self._generate_warnings(build_info, analysis)
            
            # Determine behavior adjustments
            analysis.behavior_adjustments = self._determine_behavior_adjustments(build_info, analysis)
            
        except Exception as e:
            analysis.warnings.append(f"Error during build analysis: {str(e)}")
            logger.error(f"Error analyzing build: {e}")
        
        return analysis
    
    def _analyze_combat_preferences(self, build_info: BuildInfo) -> CombatPreference:
        """Analyze combat preferences from build data.
        
        Parameters
        ----------
        build_info : BuildInfo
            Build information to analyze
            
        Returns
        -------
        CombatPreference
            Combat preference analysis
        """
        preference = CombatPreference(
            primary_range=build_info.combat_range or CombatRange.MIXED
        )
        
        # Analyze skill trees for combat style
        offensive_points = 0
        defensive_points = 0
        avoidance_points = 0
        
        for tree_name, skill_tree in build_info.skill_trees.items():
            tree_lower = tree_name.lower()
            
            # Count offensive skills
            for skill in self.offensive_skills:
                if skill in tree_lower:
                    offensive_points += skill_tree.current_points
                    break
            
            # Count defensive skills
            for skill in self.defensive_skills:
                if skill in tree_lower:
                    defensive_points += skill_tree.current_points
                    break
            
            # Count avoidance skills
            for skill in self.avoidance_skills:
                if skill in tree_lower:
                    avoidance_points += skill_tree.current_points
                    break
        
        # Determine combat style
        total_combat_points = offensive_points + defensive_points + avoidance_points
        if total_combat_points > 0:
            offensive_ratio = offensive_points / total_combat_points
            defensive_ratio = defensive_points / total_combat_points
            
            if offensive_ratio > 0.6:
                preference.combat_style = CombatStyle.AGGRESSIVE
            elif defensive_ratio > 0.6:
                preference.combat_style = CombatStyle.DEFENSIVE
            elif abs(offensive_ratio - defensive_ratio) < 0.2:
                preference.combat_style = CombatStyle.BALANCED
            else:
                preference.combat_style = CombatStyle.SPECIALIZED
        
        # Determine preferred weapons
        if build_info.weapon_class:
            weapon_class = build_info.weapon_class.value
            preference.preferred_weapons = self.weapon_preferences.get(
                build_info.combat_range, []
            )
        
        # Categorize skills
        self._categorize_skills(build_info, preference)
        
        return preference
    
    def _categorize_skills(self, build_info: BuildInfo, preference: CombatPreference) -> None:
        """Categorize skills into offensive, defensive, and avoidance.
        
        Parameters
        ----------
        build_info : BuildInfo
            Build information
        preference : CombatPreference
            Combat preference to update
        """
        for tree_name, skill_tree in build_info.skill_trees.items():
            tree_lower = tree_name.lower()
            
            # Check for offensive skills
            for skill in self.offensive_skills:
                if skill in tree_lower:
                    preference.offensive_skills.append(tree_name)
                    break
            
            # Check for defensive skills
            for skill in self.defensive_skills:
                if skill in tree_lower:
                    preference.defensive_skills.append(tree_name)
                    break
            
            # Check for avoidance skills
            for skill in self.avoidance_skills:
                if skill in tree_lower:
                    preference.avoidance_skills.append(tree_name)
                    break
    
    def _assess_optimization(self, build_info: BuildInfo) -> BuildOptimization:
        """Assess build optimization level.
        
        Parameters
        ----------
        build_info : BuildInfo
            Build information to assess
            
        Returns
        -------
        BuildOptimization
            Optimization level assessment
        """
        completion = build_info.completion_percentage
        
        if completion >= 95:
            return BuildOptimization.OPTIMAL
        elif completion >= 80:
            return BuildOptimization.GOOD
        elif completion >= 60:
            return BuildOptimization.AVERAGE
        else:
            return BuildOptimization.POOR
    
    def _calculate_synergy_score(self, build_info: BuildInfo) -> float:
        """Calculate build synergy score.
        
        Parameters
        ----------
        build_info : BuildInfo
            Build information to analyze
            
        Returns
        -------
        float
            Synergy score (0.0 to 1.0)
        """
        if not build_info.profession or not build_info.weapon_class:
            return 0.5
        
        synergy_score = 0.0
        
        # Check profession-weapon synergy
        profession_weapon_synergy = self._check_profession_weapon_synergy(
            build_info.profession, build_info.weapon_class
        )
        synergy_score += profession_weapon_synergy * 0.4
        
        # Check skill tree distribution
        skill_distribution_score = self._check_skill_distribution(build_info)
        synergy_score += skill_distribution_score * 0.3
        
        # Check combat range consistency
        range_consistency_score = self._check_range_consistency(build_info)
        synergy_score += range_consistency_score * 0.3
        
        return min(1.0, max(0.0, synergy_score))
    
    def _check_profession_weapon_synergy(self, profession: ProfessionType, weapon_class: WeaponClass) -> float:
        """Check synergy between profession and weapon class.
        
        Parameters
        ----------
        profession : ProfessionType
            Detected profession
        weapon_class : WeaponClass
            Detected weapon class
            
        Returns
        -------
        float
            Synergy score (0.0 to 1.0)
        """
        # Define optimal profession-weapon combinations
        optimal_combinations = {
            ProfessionType.COMMANDO: [WeaponClass.HEAVY_WEAPONS],
            ProfessionType.RIFLEMAN: [WeaponClass.RANGED],
            ProfessionType.PISTOLEER: [WeaponClass.RANGED],
            ProfessionType.CARBINEER: [WeaponClass.RANGED],
            ProfessionType.SWORDSMAN: [WeaponClass.MELEE],
            ProfessionType.TERAS_KASI: [WeaponClass.UNARMED],
            ProfessionType.BOWMAN: [WeaponClass.RANGED],
            ProfessionType.SMUGGLER: [WeaponClass.LIGHT_WEAPONS, WeaponClass.RANGED],
            ProfessionType.BOUNTY_HUNTER: [WeaponClass.RANGED, WeaponClass.MELEE],
            ProfessionType.SPY: [WeaponClass.LIGHT_WEAPONS, WeaponClass.RANGED]
        }
        
        optimal_weapons = optimal_combinations.get(profession, [])
        
        if weapon_class in optimal_weapons:
            return 1.0
        elif optimal_weapons:
            return 0.5  # Suboptimal but workable
        else:
            return 0.3  # Poor synergy
    
    def _check_skill_distribution(self, build_info: BuildInfo) -> float:
        """Check skill tree distribution for balance.
        
        Parameters
        ----------
        build_info : BuildInfo
            Build information to analyze
            
        Returns
        -------
        float
            Distribution score (0.0 to 1.0)
        """
        if not build_info.skill_trees:
            return 0.5
        
        # Calculate point distribution
        total_points = sum(tree.current_points for tree in build_info.skill_trees.values())
        if total_points == 0:
            return 0.5
        
        # Check for over-specialization (too many points in few trees)
        point_counts = [tree.current_points for tree in build_info.skill_trees.values()]
        point_counts.sort(reverse=True)
        
        # If top 2 trees have more than 80% of points, it's over-specialized
        if len(point_counts) >= 2 and (point_counts[0] + point_counts[1]) / total_points > 0.8:
            return 0.3
        
        # If points are well distributed, it's good
        if len(point_counts) >= 3 and point_counts[2] > 0:
            return 0.8
        
        return 0.5
    
    def _check_range_consistency(self, build_info: BuildInfo) -> float:
        """Check combat range consistency.
        
        Parameters
        ----------
        build_info : BuildInfo
            Build information to analyze
            
        Returns
        -------
        float
            Consistency score (0.0 to 1.0)
        """
        if not build_info.combat_range:
            return 0.5
        
        # Check if skill trees align with combat range
        range_keywords = {
            CombatRange.MELEE: ["melee", "close", "sword", "unarmed"],
            CombatRange.RANGED: ["ranged", "distance", "rifle", "pistol"],
            CombatRange.HEAVY: ["heavy", "explosive", "rocket"],
            CombatRange.MIXED: ["mixed", "versatile"]
        }
        
        expected_keywords = range_keywords.get(build_info.combat_range, [])
        consistency_score = 0.0
        
        for tree_name, skill_tree in build_info.skill_trees.items():
            tree_lower = tree_name.lower()
            for keyword in expected_keywords:
                if keyword in tree_lower:
                    consistency_score += skill_tree.current_points
                    break
        
        total_points = sum(tree.current_points for tree in build_info.skill_trees.values())
        if total_points > 0:
            return min(1.0, consistency_score / total_points)
        
        return 0.5
    
    def _generate_recommendations(self, build_info: BuildInfo, analysis: BuildAnalysis) -> List[str]:
        """Generate build recommendations.
        
        Parameters
        ----------
        build_info : BuildInfo
            Build information
        analysis : BuildAnalysis
            Build analysis results
            
        Returns
        -------
        list
            List of recommendations
        """
        recommendations = []
        
        # Completion recommendations
        if build_info.completion_percentage < 100:
            recommendations.append(
                f"Complete your build - currently {build_info.completion_percentage:.1f}% complete"
            )
        
        # Profession-specific recommendations
        if build_info.profession:
            prof_recs = self._get_profession_recommendations(build_info.profession, build_info)
            recommendations.extend(prof_recs)
        
        # Synergy recommendations
        if analysis.synergy_score < 0.7:
            recommendations.append("Consider improving profession-weapon synergy")
        
        # Combat style recommendations
        if analysis.combat_preference.combat_style == CombatStyle.SPECIALIZED:
            recommendations.append("Consider balancing offensive and defensive skills")
        
        return recommendations
    
    def _generate_warnings(self, build_info: BuildInfo, analysis: BuildAnalysis) -> List[str]:
        """Generate build warnings.
        
        Parameters
        ----------
        build_info : BuildInfo
            Build information
        analysis : BuildAnalysis
            Build analysis results
            
        Returns
        -------
        list
            List of warnings
        """
        warnings = []
        
        # Check for empty skill trees
        empty_trees = [
            tree_name for tree_name, skill_tree in build_info.skill_trees.items()
            if skill_tree.current_points == 0
        ]
        
        if empty_trees:
            warnings.append(f"Empty skill trees: {', '.join(empty_trees)}")
        
        # Check for low synergy
        if analysis.synergy_score < 0.5:
            warnings.append("Low build synergy detected")
        
        # Check for over-specialization
        if analysis.combat_preference.combat_style == CombatStyle.SPECIALIZED:
            warnings.append("Build may be over-specialized")
        
        return warnings
    
    def _determine_behavior_adjustments(self, build_info: BuildInfo, analysis: BuildAnalysis) -> Dict[str, Any]:
        """Determine MS11 behavior adjustments based on build.
        
        Parameters
        ----------
        build_info : BuildInfo
            Build information
        analysis : BuildAnalysis
            Build analysis results
            
        Returns
        -------
        dict
            Behavior adjustment recommendations
        """
        adjustments = {
            "combat_range": build_info.combat_range.value if build_info.combat_range else "mixed",
            "combat_style": analysis.combat_preference.combat_style.value,
            "weapon_preferences": analysis.combat_preference.preferred_weapons,
            "cooldown_timings": {},
            "ability_priorities": {},
            "target_selection": {},
            "movement_behavior": {}
        }
        
        # Adjust cooldown timings based on combat style
        if analysis.combat_preference.combat_style == CombatStyle.AGGRESSIVE:
            adjustments["cooldown_timings"] = {
                "offensive_abilities": "reduced",
                "defensive_abilities": "normal",
                "utility_abilities": "increased"
            }
        elif analysis.combat_preference.combat_style == CombatStyle.DEFENSIVE:
            adjustments["cooldown_timings"] = {
                "offensive_abilities": "normal",
                "defensive_abilities": "reduced",
                "utility_abilities": "normal"
            }
        
        # Adjust ability priorities based on combat range
        if build_info.combat_range == CombatRange.MELEE:
            adjustments["ability_priorities"] = {
                "primary": "melee_attacks",
                "secondary": "defensive_abilities",
                "tertiary": "utility_abilities"
            }
        elif build_info.combat_range == CombatRange.RANGED:
            adjustments["ability_priorities"] = {
                "primary": "ranged_attacks",
                "secondary": "positioning_abilities",
                "tertiary": "defensive_abilities"
            }
        
        # Adjust target selection based on profession
        if build_info.profession:
            adjustments["target_selection"] = self._get_target_selection_adjustments(build_info.profession)
        
        # Adjust movement behavior based on combat range
        adjustments["movement_behavior"] = self._get_movement_adjustments(build_info.combat_range)
        
        return adjustments
    
    def _get_profession_recommendations(self, profession: ProfessionType, build_info: BuildInfo) -> List[str]:
        """Get profession-specific recommendations.
        
        Parameters
        ----------
        profession : ProfessionType
            Detected profession
        build_info : BuildInfo
            Build information
            
        Returns
        -------
        list
            List of recommendations
        """
        recommendations = []
        
        if profession == ProfessionType.COMMANDO:
            if build_info.combat_range != CombatRange.HEAVY:
                recommendations.append("Consider heavy weapons specialization for Commando")
            recommendations.append("Focus on area damage abilities")
        
        elif profession == ProfessionType.RIFLEMAN:
            if build_info.combat_range != CombatRange.RANGED:
                recommendations.append("Focus on ranged combat skills for Rifleman")
            recommendations.append("Prioritize single-target damage abilities")
        
        elif profession == ProfessionType.SWORDSMAN:
            if build_info.combat_range != CombatRange.MELEE:
                recommendations.append("Focus on melee combat skills for Swordsman")
            recommendations.append("Consider defensive stance abilities")
        
        elif profession == ProfessionType.SMUGGLER:
            recommendations.append("Utilize stealth and deception abilities")
            recommendations.append("Focus on mobility and escape abilities")
        
        return recommendations
    
    def _get_target_selection_adjustments(self, profession: ProfessionType) -> Dict[str, str]:
        """Get target selection adjustments based on profession.
        
        Parameters
        ----------
        profession : ProfessionType
            Detected profession
            
        Returns
        -------
        dict
            Target selection adjustments
        """
        adjustments = {
            "priority": "closest",
            "secondary": "weakest",
            "avoidance": "strongest"
        }
        
        if profession in [ProfessionType.COMMANDO, ProfessionType.RIFLEMAN]:
            adjustments["priority"] = "highest_damage"
            adjustments["secondary"] = "closest"
        
        elif profession in [ProfessionType.SWORDSMAN, ProfessionType.TERAS_KASI]:
            adjustments["priority"] = "closest"
            adjustments["secondary"] = "highest_threat"
        
        elif profession in [ProfessionType.SMUGGLER, ProfessionType.SPY]:
            adjustments["priority"] = "weakest"
            adjustments["secondary"] = "isolated"
        
        return adjustments
    
    def _get_movement_adjustments(self, combat_range: Optional[CombatRange]) -> Dict[str, str]:
        """Get movement behavior adjustments based on combat range.
        
        Parameters
        ----------
        combat_range : CombatRange, optional
            Detected combat range
            
        Returns
        -------
        dict
            Movement behavior adjustments
        """
        adjustments = {
            "engagement": "standard",
            "retreat": "standard",
            "positioning": "standard"
        }
        
        if combat_range == CombatRange.MELEE:
            adjustments["engagement"] = "aggressive"
            adjustments["positioning"] = "close_range"
        
        elif combat_range == CombatRange.RANGED:
            adjustments["engagement"] = "cautious"
            adjustments["positioning"] = "maintain_distance"
            adjustments["retreat"] = "quick"
        
        elif combat_range == CombatRange.HEAVY:
            adjustments["engagement"] = "calculated"
            adjustments["positioning"] = "optimal_range"
        
        return adjustments 
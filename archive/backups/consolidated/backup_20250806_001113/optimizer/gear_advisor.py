#!/usr/bin/env python3
"""
Gear Advisor for Batch 124 - Gear/Armor Optimizer (AskMrRoboto Logic)

This module provides gear optimization recommendations based on:
- Scanned stats from Batch 122 (Stat Scanner + Attribute Parser)
- Selected build from Batch 123 (Build Metadata + Community Templates)
- Cross-referencing with armor sets and known resists
- Recommending gear improvements and enhancements
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ocr.stat_extractor import CharacterProfile, StatType, get_stat_extractor
from core.build_loader import BuildMetadata, get_build_loader
from utils.logging_utils import log_event


class OptimizationType(Enum):
    """Types of gear optimization."""
    COMBAT = "combat"
    DPS = "dps"
    TANK = "tank"
    SUPPORT = "support"
    BALANCED = "balanced"


class GearSlot(Enum):
    """Gear slots for armor pieces."""
    HEAD = "head"
    CHEST = "chest"
    LEGS = "legs"
    FEET = "feet"
    HANDS = "hands"


@dataclass
class GearRecommendation:
    """Individual gear recommendation."""
    slot: GearSlot
    current_item: Optional[str]
    recommended_item: str
    improvement_score: float
    stat_gains: Dict[str, int]
    resist_gains: Dict[str, int]
    enhancement_slots: int
    recommended_enhancements: List[str]
    cost: str
    priority: str  # "high", "medium", "low"
    reasoning: str


@dataclass
class OptimizationResult:
    """Complete gear optimization result."""
    character_name: str
    build_id: str
    optimization_type: OptimizationType
    current_stats: Dict[str, int]
    target_stats: Dict[str, int]
    recommendations: List[GearRecommendation]
    overall_improvement: float
    total_cost: str
    implementation_priority: List[str]
    notes: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class GearAdvisor:
    """
    Gear optimization advisor that recommends armor sets and enhancements.
    
    Features:
    - Analyzes scanned stats from Batch 122
    - Considers selected build from Batch 123
    - Cross-references armor sets and resists
    - Recommends optimal gear improvements
    - Provides enhancement suggestions
    - Calculates improvement scores and costs
    """
    
    def __init__(self, armor_sets_file: str = "data/armor_sets.json"):
        """Initialize the gear advisor.
        
        Args:
            armor_sets_file: Path to the armor sets database
        """
        self.armor_sets_file = Path(armor_sets_file)
        self.armor_sets: Dict[str, Any] = {}
        self.enhancements: Dict[str, Any] = {}
        self.resist_types: Dict[str, str] = {}
        self.stat_extractor = get_stat_extractor()
        self.build_loader = get_build_loader()
        self.logger = logging.getLogger(__name__)
        
        self._load_armor_data()
    
    def _load_armor_data(self) -> None:
        """Load armor sets and enhancement data."""
        if not self.armor_sets_file.exists():
            self.logger.warning(f"Armor sets file not found: {self.armor_sets_file}")
            return
        
        try:
            with open(self.armor_sets_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.armor_sets = data.get('armor_sets', {})
            self.enhancements = data.get('enhancements', {})
            self.resist_types = data.get('resist_types', {})
            
            self.logger.info(f"Loaded {len(self.armor_sets)} armor sets and {len(self.enhancements)} enhancements")
            
        except Exception as e:
            self.logger.error(f"Error loading armor data: {e}")
    
    def analyze_gear_optimization(self, 
                                character_profile: CharacterProfile,
                                build_id: str,
                                optimization_type: OptimizationType = OptimizationType.BALANCED,
                                budget: str = "medium") -> OptimizationResult:
        """Analyze gear optimization for a character.
        
        Args:
            character_profile: Character stats from Batch 122
            build_id: Selected build ID from Batch 123
            optimization_type: Type of optimization to perform
            budget: Budget constraint for recommendations
            
        Returns:
            OptimizationResult with recommendations
        """
        try:
            # Get build data
            build_data = self.build_loader.get_build(build_id)
            if not build_data:
                raise ValueError(f"Build {build_id} not found")
            
            # Extract current stats
            current_stats = self._extract_current_stats(character_profile)
            
            # Determine target stats based on build and optimization type
            target_stats = self._calculate_target_stats(build_data, optimization_type)
            
            # Generate gear recommendations
            recommendations = self._generate_gear_recommendations(
                current_stats, target_stats, build_data, optimization_type, budget
            )
            
            # Calculate overall improvement
            overall_improvement = self._calculate_overall_improvement(recommendations)
            
            # Determine implementation priority
            implementation_priority = self._determine_implementation_priority(recommendations)
            
            # Calculate total cost
            total_cost = self._calculate_total_cost(recommendations)
            
            # Generate notes
            notes = self._generate_optimization_notes(
                character_profile, build_data, optimization_type, recommendations
            )
            
            return OptimizationResult(
                character_name=character_profile.character_name,
                build_id=build_id,
                optimization_type=optimization_type,
                current_stats=current_stats,
                target_stats=target_stats,
                recommendations=recommendations,
                overall_improvement=overall_improvement,
                total_cost=total_cost,
                implementation_priority=implementation_priority,
                notes=notes
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing gear optimization: {e}")
            raise
    
    def _extract_current_stats(self, character_profile: CharacterProfile) -> Dict[str, int]:
        """Extract current character stats from profile."""
        stats = {}
        
        # Extract base stats
        for stat_type, stat in character_profile.stats.items():
            if stat_type in [StatType.HEALTH, StatType.ACTION, StatType.MIND, StatType.LUCK]:
                stats[stat_type.value] = stat.current_value
        
        # Extract resists
        for stat_type, stat in character_profile.stats.items():
            if stat_type.value.startswith('resist_'):
                resist_type = stat_type.value.replace('resist_', '')
                stats[f"resist_{resist_type}"] = stat.current_value
        
        # Extract tapes
        for stat_type, stat in character_profile.stats.items():
            if stat_type.value.startswith('tape_'):
                tape_type = stat_type.value.replace('tape_', '')
                stats[f"tape_{tape_type}"] = stat.current_value
        
        return stats
    
    def _calculate_target_stats(self, build_data: BuildMetadata, 
                              optimization_type: OptimizationType) -> Dict[str, int]:
        """Calculate target stats based on build and optimization type."""
        target_stats = {}
        
        # Base stats based on build category
        if build_data.category.value == "combat":
            if optimization_type == OptimizationType.DPS:
                target_stats.update({
                    "agility": 100,
                    "stamina": 80,
                    "strength": 60,
                    "constitution": 70
                })
            elif optimization_type == OptimizationType.TANK:
                target_stats.update({
                    "constitution": 100,
                    "stamina": 90,
                    "strength": 80,
                    "agility": 40
                })
            else:  # BALANCED
                target_stats.update({
                    "constitution": 80,
                    "stamina": 70,
                    "agility": 70,
                    "strength": 60
                })
        elif build_data.category.value == "support":
            target_stats.update({
                "mind": 100,
                "focus": 90,
                "constitution": 70,
                "stamina": 60
            })
        
        # Resists based on build specialization
        if build_data.specialization.value == "pvp":
            target_stats.update({
                "resist_energy": 40,
                "resist_kinetic": 40,
                "resist_blast": 30,
                "resist_heat": 25
            })
        else:  # PvE
            target_stats.update({
                "resist_energy": 25,
                "resist_kinetic": 25,
                "resist_blast": 20,
                "resist_heat": 15
            })
        
        return target_stats
    
    def _generate_gear_recommendations(self, 
                                     current_stats: Dict[str, int],
                                     target_stats: Dict[str, int],
                                     build_data: BuildMetadata,
                                     optimization_type: OptimizationType,
                                     budget: str) -> List[GearRecommendation]:
        """Generate gear recommendations."""
        recommendations = []
        
        # Find optimal armor set for the build
        optimal_armor_set = self._find_optimal_armor_set(build_data, optimization_type, budget)
        
        if not optimal_armor_set:
            return recommendations
        
        armor_set_data = self.armor_sets[optimal_armor_set]
        
        # Generate recommendations for each slot
        for slot_name, slot_data in armor_set_data['slots'].items():
            slot = GearSlot(slot_name)
            
            # Calculate stat gains
            stat_gains = slot_data['base_stats'].copy()
            resist_gains = slot_data['resists'].copy()
            
            # Calculate improvement score
            improvement_score = self._calculate_slot_improvement_score(
                slot_name, stat_gains, resist_gains, current_stats, target_stats
            )
            
            # Determine priority
            priority = self._determine_slot_priority(slot_name, improvement_score)
            
            # Generate reasoning
            reasoning = self._generate_slot_reasoning(
                slot_name, stat_gains, resist_gains, build_data, optimization_type
            )
            
            # Recommend enhancements
            recommended_enhancements = self._recommend_enhancements(
                slot_data, build_data, optimization_type, budget
            )
            
            recommendation = GearRecommendation(
                slot=slot,
                current_item=None,  # Would be determined from actual gear scan
                recommended_item=slot_data['name'],
                improvement_score=improvement_score,
                stat_gains=stat_gains,
                resist_gains=resist_gains,
                enhancement_slots=slot_data['enhancement_slots'],
                recommended_enhancements=recommended_enhancements,
                cost=armor_set_data['cost'],
                priority=priority,
                reasoning=reasoning
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _find_optimal_armor_set(self, build_data: BuildMetadata,
                               optimization_type: OptimizationType,
                               budget: str) -> Optional[str]:
        """Find the optimal armor set for the build."""
        best_set = None
        best_score = 0
        
        for set_id, set_data in self.armor_sets.items():
            # Check if set matches build requirements
            if not self._armor_set_matches_build(set_data, build_data):
                continue
            
            # Check budget constraint
            if not self._is_within_budget(set_data['cost'], budget):
                continue
            
            # Calculate compatibility score
            score = self._calculate_armor_set_score(set_data, build_data, optimization_type)
            
            if score > best_score:
                best_score = score
                best_set = set_id
        
        return best_set
    
    def _armor_set_matches_build(self, armor_set: Dict[str, Any], 
                                build_data: BuildMetadata) -> bool:
        """Check if armor set matches build requirements."""
        # Check profession compatibility
        if build_data.category.value == "combat" and armor_set['profession'] != "combat":
            return False
        
        if build_data.category.value == "support" and armor_set['profession'] != "support":
            return False
        
        # Check combat style compatibility
        if build_data.combat.get('style') and armor_set['combat_style'] != build_data.combat['style']:
            return False
        
        return True
    
    def _calculate_armor_set_score(self, armor_set: Dict[str, Any],
                                 build_data: BuildMetadata,
                                 optimization_type: OptimizationType) -> float:
        """Calculate compatibility score for armor set."""
        score = 0
        
        # Base score for profession match
        if armor_set['profession'] == build_data.category.value:
            score += 50
        
        # Combat style bonus
        if armor_set['combat_style'] == build_data.combat.get('style', ''):
            score += 30
        
        # Specialization bonus
        if armor_set['specialization'] == build_data.specialization.value:
            score += 20
        
        # Optimization type bonus
        if optimization_type == OptimizationType.TANK and armor_set['type'] == 'heavy':
            score += 25
        elif optimization_type == OptimizationType.DPS and armor_set['type'] == 'medium':
            score += 25
        elif optimization_type == OptimizationType.SUPPORT and armor_set['type'] == 'light':
            score += 25
        
        return score
    
    def _calculate_slot_improvement_score(self, slot_name: str,
                                        stat_gains: Dict[str, int],
                                        resist_gains: Dict[str, int],
                                        current_stats: Dict[str, int],
                                        target_stats: Dict[str, int]) -> float:
        """Calculate improvement score for a gear slot."""
        score = 0
        
        # Stat improvement score
        for stat, gain in stat_gains.items():
            if stat in target_stats:
                current = current_stats.get(stat, 0)
                target = target_stats[stat]
                if current < target:
                    improvement = min(gain, target - current)
                    score += improvement * 2  # Stat improvements weighted higher
        
        # Resist improvement score
        for resist, gain in resist_gains.items():
            resist_key = f"resist_{resist}"
            if resist_key in target_stats:
                current = current_stats.get(resist_key, 0)
                target = target_stats[resist_key]
                if current < target:
                    improvement = min(gain, target - current)
                    score += improvement
        
        return score
    
    def _determine_slot_priority(self, slot_name: str, improvement_score: float) -> str:
        """Determine priority for a gear slot."""
        if improvement_score > 50:
            return "high"
        elif improvement_score > 20:
            return "medium"
        else:
            return "low"
    
    def _generate_slot_reasoning(self, slot_name: str,
                                stat_gains: Dict[str, int],
                                resist_gains: Dict[str, int],
                                build_data: BuildMetadata,
                                optimization_type: OptimizationType) -> str:
        """Generate reasoning for gear slot recommendation."""
        reasoning_parts = []
        
        # Add stat gains reasoning
        if stat_gains:
            stat_list = [f"+{gain} {stat}" for stat, gain in stat_gains.items()]
            reasoning_parts.append(f"Provides {', '.join(stat_list)}")
        
        # Add resist gains reasoning
        if resist_gains:
            resist_list = [f"+{gain}% {resist}" for resist, gain in resist_gains.items()]
            reasoning_parts.append(f"Adds {', '.join(resist_list)} resistance")
        
        # Add build-specific reasoning
        if build_data.category.value == "combat":
            if slot_name in ["chest", "head"]:
                reasoning_parts.append("Critical for combat survivability")
        elif build_data.category.value == "support":
            if slot_name in ["chest", "head"]:
                reasoning_parts.append("Essential for support effectiveness")
        
        return ". ".join(reasoning_parts)
    
    def _recommend_enhancements(self, slot_data: Dict[str, Any],
                              build_data: BuildMetadata,
                              optimization_type: OptimizationType,
                              budget: str) -> List[str]:
        """Recommend enhancements for a gear slot."""
        recommendations = []
        available_enhancements = slot_data['available_enhancements']
        
        # Filter by budget
        affordable_enhancements = [
            enh for enh in available_enhancements
            if self._is_within_budget(self.enhancements.get(enh, {}).get('cost', 'high'), budget)
        ]
        
        # Prioritize based on build and optimization type
        if build_data.category.value == "combat":
            if optimization_type == OptimizationType.DPS:
                priority_order = ["damage", "critical", "accuracy", "defense"]
            elif optimization_type == OptimizationType.TANK:
                priority_order = ["defense", "health", "constitution", "armor"]
            else:  # BALANCED
                priority_order = ["accuracy", "defense", "health", "damage"]
        else:  # Support
            priority_order = ["mind", "focus", "healing", "defense"]
        
        # Select enhancements based on priority
        for enhancement in priority_order:
            if enhancement in affordable_enhancements and len(recommendations) < slot_data['enhancement_slots']:
                recommendations.append(enhancement)
        
        return recommendations
    
    def _calculate_overall_improvement(self, recommendations: List[GearRecommendation]) -> float:
        """Calculate overall improvement score."""
        if not recommendations:
            return 0
        
        total_score = sum(rec.improvement_score for rec in recommendations)
        return total_score / len(recommendations)
    
    def _determine_implementation_priority(self, recommendations: List[GearRecommendation]) -> List[str]:
        """Determine implementation priority order."""
        # Sort by priority and improvement score
        sorted_recs = sorted(
            recommendations,
            key=lambda x: (x.priority == "high", x.improvement_score),
            reverse=True
        )
        
        return [f"{rec.slot.value}: {rec.recommended_item}" for rec in sorted_recs]
    
    def _calculate_total_cost(self, recommendations: List[GearRecommendation]) -> str:
        """Calculate total cost of recommendations."""
        costs = {"low": 0, "medium": 0, "high": 0}
        
        for rec in recommendations:
            if rec.cost in costs:
                costs[rec.cost] += 1
        
        if costs["high"] > 0:
            return "high"
        elif costs["medium"] > 0:
            return "medium"
        else:
            return "low"
    
    def _generate_optimization_notes(self, character_profile: CharacterProfile,
                                   build_data: BuildMetadata,
                                   optimization_type: OptimizationType,
                                   recommendations: List[GearRecommendation]) -> List[str]:
        """Generate optimization notes."""
        notes = []
        
        # Build-specific notes
        notes.append(f"Optimizing for {build_data.name} build ({build_data.category.value})")
        notes.append(f"Focus: {optimization_type.value} optimization")
        
        # Gear recommendations summary
        high_priority = [r for r in recommendations if r.priority == "high"]
        if high_priority:
            notes.append(f"Priority upgrades: {len(high_priority)} high-impact items")
        
        # Enhancement opportunities
        total_enhancement_slots = sum(r.enhancement_slots for r in recommendations)
        if total_enhancement_slots > 0:
            notes.append(f"Enhancement opportunities: {total_enhancement_slots} slots available")
        
        # Cost considerations
        total_cost = self._calculate_total_cost(recommendations)
        notes.append(f"Implementation cost: {total_cost}")
        
        return notes
    
    def _is_within_budget(self, item_cost: str, budget: str) -> bool:
        """Check if item cost is within budget."""
        cost_levels = {"low": 1, "medium": 2, "high": 3}
        item_level = cost_levels.get(item_cost, 3)
        budget_level = cost_levels.get(budget, 2)
        return item_level <= budget_level
    
    def save_optimization_result(self, result: OptimizationResult, 
                               output_path: str = None) -> bool:
        """Save optimization result to file."""
        try:
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"data/gear_optimization_{result.character_name}_{timestamp}.json"
            
            # Convert to serializable format
            result_dict = {
                "character_name": result.character_name,
                "build_id": result.build_id,
                "optimization_type": result.optimization_type.value,
                "current_stats": result.current_stats,
                "target_stats": result.target_stats,
                "recommendations": [
                    {
                        "slot": rec.slot.value,
                        "current_item": rec.current_item,
                        "recommended_item": rec.recommended_item,
                        "improvement_score": rec.improvement_score,
                        "stat_gains": rec.stat_gains,
                        "resist_gains": rec.resist_gains,
                        "enhancement_slots": rec.enhancement_slots,
                        "recommended_enhancements": rec.recommended_enhancements,
                        "cost": rec.cost,
                        "priority": rec.priority,
                        "reasoning": rec.reasoning
                    }
                    for rec in result.recommendations
                ],
                "overall_improvement": result.overall_improvement,
                "total_cost": result.total_cost,
                "implementation_priority": result.implementation_priority,
                "notes": result.notes,
                "timestamp": result.timestamp.isoformat()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2)
            
            self.logger.info(f"Optimization result saved to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving optimization result: {e}")
            return False


# Global instance
gear_advisor = GearAdvisor()


def get_gear_advisor() -> GearAdvisor:
    """Get the global gear advisor instance."""
    return gear_advisor


def analyze_character_gear(character_name: str,
                          build_id: str,
                          optimization_type: OptimizationType = OptimizationType.BALANCED,
                          budget: str = "medium") -> Optional[OptimizationResult]:
    """Convenience function to analyze character gear."""
    try:
        advisor = get_gear_advisor()
        extractor = get_stat_extractor()
        
        # Get character profile (or create one if not exists)
        profile = extractor.load_character_profile(character_name)
        if not profile:
            # Create a default profile for testing
            profile = extractor.create_character_profile(character_name, "Rifleman", 50)
        
        return advisor.analyze_gear_optimization(profile, build_id, optimization_type, budget)
        
    except Exception as e:
        logging.error(f"Error analyzing character gear: {e}")
        return None


def save_gear_optimization_result(result: OptimizationResult) -> bool:
    """Convenience function to save optimization result."""
    advisor = get_gear_advisor()
    return advisor.save_optimization_result(result) 
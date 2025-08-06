#!/usr/bin/env python3
"""
Build Optimizer v2 (GCW + Attributes-Aware)
Full "AskMrRoboto"-style advice using GCW calculator & Attributes logic

This module provides comprehensive build optimization including:
- Input: scanned stats (Batch 122), selected role, GCW role
- Output: prioritized armor resists, tapes, foods, ent buffs, suggested reallocations
- Explain tradeoffs; link to items/builds pages
- Persist last three optimizations per character
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


class OptimizationRole(Enum):
    """Optimization roles for different playstyles."""
    DPS = "dps"
    TANK = "tank"
    SUPPORT = "support"
    HYBRID = "hybrid"
    PVP = "pvp"


class GCWRole(Enum):
    """GCW-specific roles."""
    INFANTRY = "infantry"
    SPECIALIST = "specialist"
    COMMANDO = "commando"
    SNIPER = "sniper"
    MEDIC = "medic"
    ENGINEER = "engineer"


class OptimizationPriority(Enum):
    """Priority levels for optimization recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class AttributeBreakpoint:
    """Attribute breakpoint for optimization."""
    attribute: str
    current_value: int
    target_value: int
    breakpoint_value: int
    improvement_potential: float
    priority: OptimizationPriority
    reasoning: str


@dataclass
class GCWOptimization:
    """GCW-specific optimization data."""
    role: GCWRole
    current_rank: int
    target_rank: int
    required_attributes: Dict[str, int]
    recommended_gear: List[str]
    strategy_notes: List[str]


@dataclass
class ArmorRecommendation:
    """Armor piece recommendation."""
    slot: str
    current_item: Optional[str]
    recommended_item: str
    resist_gains: Dict[str, int]
    stat_gains: Dict[str, int]
    cost: str
    priority: OptimizationPriority
    reasoning: str


@dataclass
class EnhancementRecommendation:
    """Enhancement recommendation."""
    type: str  # "tape", "food", "ent_buff", "reallocation"
    name: str
    effect: Dict[str, int]
    duration: Optional[str]
    cost: str
    priority: OptimizationPriority
    reasoning: str


@dataclass
class OptimizationResult:
    """Complete build optimization result."""
    character_name: str
    selected_role: OptimizationRole
    gcw_role: Optional[GCWRole]
    current_stats: Dict[str, int]
    target_stats: Dict[str, int]
    attribute_breakpoints: List[AttributeBreakpoint]
    armor_recommendations: List[ArmorRecommendation]
    enhancement_recommendations: List[EnhancementRecommendation]
    gcw_optimization: Optional[GCWOptimization]
    overall_improvement: float
    total_cost: str
    implementation_priority: List[str]
    tradeoffs: List[str]
    links: Dict[str, str]  # Links to items/builds pages
    timestamp: datetime = field(default_factory=datetime.now)


class BuildOptimizerV2:
    """
    Advanced build optimizer with GCW and attributes awareness.
    
    Features:
    - Analyzes scanned stats from Batch 122
    - Considers selected role and GCW role
    - Provides prioritized armor resists, tapes, foods, ent buffs
    - Suggests attribute reallocations based on breakpoints
    - Explains tradeoffs and links to relevant pages
    - Persists last three optimizations per character
    """
    
    def __init__(self, 
                 attributes_file: str = "data/meta/attributes_breakpoints.json",
                 gcw_file: str = "data/meta/gcw_weighting.json"):
        """Initialize the build optimizer.
        
        Args:
            attributes_file: Path to attributes breakpoints data
            gcw_file: Path to GCW weighting data
        """
        self.attributes_file = Path(attributes_file)
        self.gcw_file = Path(gcw_file)
        self.attributes_data: Dict[str, Any] = {}
        self.gcw_data: Dict[str, Any] = {}
        self.stat_extractor = get_stat_extractor()
        self.build_loader = get_build_loader()
        self.logger = logging.getLogger(__name__)
        
        self._load_optimization_data()
    
    def _load_optimization_data(self) -> None:
        """Load attributes and GCW optimization data."""
        try:
            if self.attributes_file.exists():
                with open(self.attributes_file, 'r') as f:
                    self.attributes_data = json.load(f)
                self.logger.info(f"Loaded attributes data from {self.attributes_file}")
            else:
                self.logger.warning(f"Attributes file not found: {self.attributes_file}")
                self.attributes_data = self._create_default_attributes_data()
                
            if self.gcw_file.exists():
                with open(self.gcw_file, 'r') as f:
                    self.gcw_data = json.load(f)
                self.logger.info(f"Loaded GCW data from {self.gcw_file}")
            else:
                self.logger.warning(f"GCW file not found: {self.gcw_file}")
                self.gcw_data = self._create_default_gcw_data()
                
        except Exception as e:
            self.logger.error(f"Error loading optimization data: {e}")
            self.attributes_data = self._create_default_attributes_data()
            self.gcw_data = self._create_default_gcw_data()
    
    def _create_default_attributes_data(self) -> Dict[str, Any]:
        """Create default attributes breakpoints data."""
        return {
            "breakpoints": {
                "strength": {
                    "melee_damage": [100, 200, 300, 400, 500],
                    "health": [50, 100, 150, 200, 250],
                    "carry_weight": [25, 50, 75, 100, 125]
                },
                "precision": {
                    "ranged_damage": [100, 200, 300, 400, 500],
                    "critical_chance": [50, 100, 150, 200, 250],
                    "accuracy": [25, 50, 75, 100, 125]
                },
                "agility": {
                    "dodge": [50, 100, 150, 200, 250],
                    "speed": [25, 50, 75, 100, 125],
                    "stamina": [100, 200, 300, 400, 500]
                },
                "constitution": {
                    "health": [200, 400, 600, 800, 1000],
                    "stamina": [100, 200, 300, 400, 500],
                    "resistance": [25, 50, 75, 100, 125]
                },
                "focus": {
                    "force_power": [100, 200, 300, 400, 500],
                    "mental_resistance": [50, 100, 150, 200, 250],
                    "healing_power": [25, 50, 75, 100, 125]
                },
                "willpower": {
                    "mental_resistance": [100, 200, 300, 400, 500],
                    "force_power": [50, 100, 150, 200, 250],
                    "healing_power": [25, 50, 75, 100, 125]
                }
            },
            "role_priorities": {
                "dps": ["precision", "strength", "agility"],
                "tank": ["constitution", "willpower", "strength"],
                "support": ["focus", "willpower", "constitution"],
                "hybrid": ["precision", "constitution", "agility"],
                "pvp": ["precision", "agility", "constitution"]
            }
        }
    
    def _create_default_gcw_data(self) -> Dict[str, Any]:
        """Create default GCW weighting data."""
        return {
            "roles": {
                "infantry": {
                    "primary_attributes": ["strength", "constitution"],
                    "secondary_attributes": ["agility", "precision"],
                    "gear_priorities": ["armor", "weapons", "enhancements"],
                    "strategy": "Close combat with heavy armor"
                },
                "specialist": {
                    "primary_attributes": ["precision", "agility"],
                    "secondary_attributes": ["strength", "constitution"],
                    "gear_priorities": ["weapons", "enhancements", "armor"],
                    "strategy": "Ranged combat with mobility"
                },
                "commando": {
                    "primary_attributes": ["strength", "precision"],
                    "secondary_attributes": ["agility", "constitution"],
                    "gear_priorities": ["weapons", "armor", "enhancements"],
                    "strategy": "Heavy weapons and explosives"
                },
                "sniper": {
                    "primary_attributes": ["precision", "focus"],
                    "secondary_attributes": ["agility", "willpower"],
                    "gear_priorities": ["weapons", "enhancements", "armor"],
                    "strategy": "Long-range precision strikes"
                },
                "medic": {
                    "primary_attributes": ["focus", "willpower"],
                    "secondary_attributes": ["constitution", "agility"],
                    "gear_priorities": ["enhancements", "armor", "weapons"],
                    "strategy": "Healing and support"
                },
                "engineer": {
                    "primary_attributes": ["focus", "precision"],
                    "secondary_attributes": ["willpower", "agility"],
                    "gear_priorities": ["enhancements", "weapons", "armor"],
                    "strategy": "Technical support and gadgets"
                }
            },
            "rank_requirements": {
                1: {"min_attributes": 100, "gear_tier": "basic"},
                2: {"min_attributes": 200, "gear_tier": "standard"},
                3: {"min_attributes": 300, "gear_tier": "advanced"},
                4: {"min_attributes": 400, "gear_tier": "elite"},
                5: {"min_attributes": 500, "gear_tier": "master"}
            }
        }
    
    def optimize_build(self,
                      character_profile: CharacterProfile,
                      selected_role: OptimizationRole,
                      gcw_role: Optional[GCWRole] = None,
                      budget: str = "medium") -> OptimizationResult:
        """Perform comprehensive build optimization.
        
        Args:
            character_profile: Scanned character stats
            selected_role: Primary optimization role
            gcw_role: Optional GCW-specific role
            budget: Budget constraint ("low", "medium", "high")
            
        Returns:
            Complete optimization result
        """
        self.logger.info(f"Starting build optimization for {character_profile.name}")
        
        # Extract current stats
        current_stats = self._extract_current_stats(character_profile)
        
        # Calculate target stats based on role
        target_stats = self._calculate_target_stats(selected_role, gcw_role)
        
        # Analyze attribute breakpoints
        attribute_breakpoints = self._analyze_attribute_breakpoints(
            current_stats, target_stats, selected_role
        )
        
        # Generate armor recommendations
        armor_recommendations = self._generate_armor_recommendations(
            current_stats, target_stats, selected_role, gcw_role, budget
        )
        
        # Generate enhancement recommendations
        enhancement_recommendations = self._generate_enhancement_recommendations(
            current_stats, target_stats, selected_role, gcw_role, budget
        )
        
        # Generate GCW optimization if applicable
        gcw_optimization = None
        if gcw_role:
            gcw_optimization = self._generate_gcw_optimization(
                current_stats, gcw_role
            )
        
        # Calculate overall improvement
        overall_improvement = self._calculate_overall_improvement(
            attribute_breakpoints, armor_recommendations, enhancement_recommendations
        )
        
        # Generate implementation priority
        implementation_priority = self._determine_implementation_priority(
            attribute_breakpoints, armor_recommendations, enhancement_recommendations
        )
        
        # Calculate total cost
        total_cost = self._calculate_total_cost(
            armor_recommendations, enhancement_recommendations
        )
        
        # Generate tradeoffs
        tradeoffs = self._generate_tradeoffs(
            selected_role, gcw_role, attribute_breakpoints, 
            armor_recommendations, enhancement_recommendations
        )
        
        # Generate links
        links = self._generate_links(selected_role, gcw_role)
        
        result = OptimizationResult(
            character_name=character_profile.name,
            selected_role=selected_role,
            gcw_role=gcw_role,
            current_stats=current_stats,
            target_stats=target_stats,
            attribute_breakpoints=attribute_breakpoints,
            armor_recommendations=armor_recommendations,
            enhancement_recommendations=enhancement_recommendations,
            gcw_optimization=gcw_optimization,
            overall_improvement=overall_improvement,
            total_cost=total_cost,
            implementation_priority=implementation_priority,
            tradeoffs=tradeoffs,
            links=links
        )
        
        # Persist optimization result
        self._save_optimization_result(result)
        
        self.logger.info(f"Build optimization completed for {character_profile.name}")
        return result
    
    def _extract_current_stats(self, character_profile: CharacterProfile) -> Dict[str, int]:
        """Extract current character stats."""
        stats = {}
        
        # Extract basic attributes
        for stat_type in StatType:
            value = character_profile.get_stat(stat_type)
            if value is not None:
                stats[stat_type.value] = value
        
        # Extract derived stats
        stats.update({
            "health": character_profile.get_health() or 0,
            "stamina": character_profile.get_stamina() or 0,
            "force_power": character_profile.get_force_power() or 0,
            "mental_resistance": character_profile.get_mental_resistance() or 0
        })
        
        return stats
    
    def _calculate_target_stats(self, 
                              selected_role: OptimizationRole,
                              gcw_role: Optional[GCWRole]) -> Dict[str, int]:
        """Calculate target stats based on role."""
        target_stats = {}
        
        # Get role priorities
        role_priorities = self.attributes_data.get("role_priorities", {})
        priorities = role_priorities.get(selected_role.value, ["precision", "strength", "agility"])
        
        # Set base targets
        base_targets = {
            "strength": 300,
            "precision": 300,
            "agility": 250,
            "constitution": 250,
            "focus": 200,
            "willpower": 200
        }
        
        # Adjust based on role priorities
        for i, priority in enumerate(priorities):
            if priority in base_targets:
                # Higher priority attributes get higher targets
                multiplier = 1.5 - (i * 0.1)
                base_targets[priority] = int(base_targets[priority] * multiplier)
        
        # Adjust for GCW role if specified
        if gcw_role and gcw_role.value in self.gcw_data.get("roles", {}):
            gcw_role_data = self.gcw_data["roles"][gcw_role.value]
            primary_attrs = gcw_role_data.get("primary_attributes", [])
            secondary_attrs = gcw_role_data.get("secondary_attributes", [])
            
            for attr in primary_attrs:
                if attr in base_targets:
                    base_targets[attr] = int(base_targets[attr] * 1.3)
            
            for attr in secondary_attrs:
                if attr in base_targets:
                    base_targets[attr] = int(base_targets[attr] * 1.1)
        
        target_stats.update(base_targets)
        return target_stats
    
    def _analyze_attribute_breakpoints(self,
                                     current_stats: Dict[str, int],
                                     target_stats: Dict[str, int],
                                     selected_role: OptimizationRole) -> List[AttributeBreakpoint]:
        """Analyze attribute breakpoints for optimization."""
        breakpoints = []
        breakpoints_data = self.attributes_data.get("breakpoints", {})
        
        for attribute, current_value in current_stats.items():
            if attribute not in breakpoints_data:
                continue
                
            target_value = target_stats.get(attribute, current_value)
            attribute_breakpoints = breakpoints_data[attribute]
            
            # Find the next breakpoint
            next_breakpoint = None
            for breakpoint_value in attribute_breakpoints.values():
                for value in breakpoint_value:
                    if value > current_value:
                        next_breakpoint = value
                        break
                if next_breakpoint:
                    break
            
            if next_breakpoint:
                improvement_potential = (next_breakpoint - current_value) / next_breakpoint
                priority = self._determine_attribute_priority(
                    attribute, improvement_potential, selected_role
                )
                
                reasoning = self._generate_attribute_reasoning(
                    attribute, current_value, next_breakpoint, selected_role
                )
                
                breakpoint = AttributeBreakpoint(
                    attribute=attribute,
                    current_value=current_value,
                    target_value=target_value,
                    breakpoint_value=next_breakpoint,
                    improvement_potential=improvement_potential,
                    priority=priority,
                    reasoning=reasoning
                )
                breakpoints.append(breakpoint)
        
        # Sort by priority and improvement potential
        breakpoints.sort(key=lambda x: (x.priority.value, x.improvement_potential), reverse=True)
        return breakpoints
    
    def _determine_attribute_priority(self,
                                    attribute: str,
                                    improvement_potential: float,
                                    selected_role: OptimizationRole) -> OptimizationPriority:
        """Determine priority for attribute improvement."""
        role_priorities = self.attributes_data.get("role_priorities", {})
        priorities = role_priorities.get(selected_role.value, [])
        
        if attribute in priorities[:2]:  # Top 2 priorities
            if improvement_potential > 0.3:
                return OptimizationPriority.CRITICAL
            else:
                return OptimizationPriority.HIGH
        elif attribute in priorities[2:4]:  # Secondary priorities
            if improvement_potential > 0.4:
                return OptimizationPriority.HIGH
            else:
                return OptimizationPriority.MEDIUM
        else:
            if improvement_potential > 0.5:
                return OptimizationPriority.MEDIUM
            else:
                return OptimizationPriority.LOW
    
    def _generate_attribute_reasoning(self,
                                    attribute: str,
                                    current_value: int,
                                    breakpoint_value: int,
                                    selected_role: OptimizationRole) -> str:
        """Generate reasoning for attribute improvement."""
        role_name = selected_role.value.upper()
        
        if attribute == "strength":
            return f"STR {current_value} → {breakpoint_value} for {role_name} melee damage and health"
        elif attribute == "precision":
            return f"PRE {current_value} → {breakpoint_value} for {role_name} ranged damage and crits"
        elif attribute == "agility":
            return f"AGI {current_value} → {breakpoint_value} for {role_name} dodge and mobility"
        elif attribute == "constitution":
            return f"CON {current_value} → {breakpoint_value} for {role_name} health and stamina"
        elif attribute == "focus":
            return f"FOC {current_value} → {breakpoint_value} for {role_name} force power"
        elif attribute == "willpower":
            return f"WIL {current_value} → {breakpoint_value} for {role_name} mental resistance"
        else:
            return f"{attribute.title()} {current_value} → {breakpoint_value} for {role_name} optimization"
    
    def _generate_armor_recommendations(self,
                                      current_stats: Dict[str, int],
                                      target_stats: Dict[str, int],
                                      selected_role: OptimizationRole,
                                      gcw_role: Optional[GCWRole],
                                      budget: str) -> List[ArmorRecommendation]:
        """Generate armor recommendations."""
        recommendations = []
        
        # Define armor slots and their priorities
        armor_slots = {
            "chest": {"priority": 1, "resist_focus": ["kinetic", "energy"]},
            "legs": {"priority": 2, "resist_focus": ["kinetic", "blast"]},
            "head": {"priority": 3, "resist_focus": ["energy", "stun"]},
            "feet": {"priority": 4, "resist_focus": ["kinetic", "acid"]},
            "hands": {"priority": 5, "resist_focus": ["energy", "cold"]}
        }
        
        for slot, slot_data in armor_slots.items():
            # Generate recommendation for each slot
            recommendation = self._generate_slot_recommendation(
                slot, slot_data, current_stats, target_stats, 
                selected_role, gcw_role, budget
            )
            if recommendation:
                recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_slot_recommendation(self,
                                    slot: str,
                                    slot_data: Dict[str, Any],
                                    current_stats: Dict[str, int],
                                    target_stats: Dict[str, int],
                                    selected_role: OptimizationRole,
                                    gcw_role: Optional[GCWRole],
                                    budget: str) -> Optional[ArmorRecommendation]:
        """Generate recommendation for a specific armor slot."""
        # This is a simplified implementation
        # In a full implementation, this would cross-reference with actual armor database
        
        resist_gains = {
            "kinetic": 25,
            "energy": 20,
            "blast": 15,
            "stun": 10,
            "acid": 10,
            "cold": 10
        }
        
        stat_gains = {
            "constitution": 15,
            "agility": 10
        }
        
        # Adjust based on role
        if selected_role == OptimizationRole.TANK:
            resist_gains = {k: v * 1.5 for k, v in resist_gains.items()}
            stat_gains["constitution"] = 25
        elif selected_role == OptimizationRole.DPS:
            stat_gains["precision"] = 20
            stat_gains["strength"] = 15
        
        # Adjust based on GCW role
        if gcw_role:
            gcw_role_data = self.gcw_data.get("roles", {}).get(gcw_role.value, {})
            if "armor" in gcw_role_data.get("gear_priorities", []):
                resist_gains = {k: v * 1.2 for k, v in resist_gains.items()}
        
        # Determine cost based on budget
        cost_map = {"low": "5k-15k", "medium": "15k-50k", "high": "50k-150k"}
        cost = cost_map.get(budget, "15k-50k")
        
        # Determine priority
        priority = OptimizationPriority.HIGH if slot_data["priority"] <= 2 else OptimizationPriority.MEDIUM
        
        reasoning = f"Optimize {slot} for {selected_role.value.upper()} role"
        if gcw_role:
            reasoning += f" with {gcw_role.value} specialization"
        
        return ArmorRecommendation(
            slot=slot,
            current_item=None,  # Would be extracted from character profile
            recommended_item=f"Enhanced {slot.title()} Armor",
            resist_gains=resist_gains,
            stat_gains=stat_gains,
            cost=cost,
            priority=priority,
            reasoning=reasoning
        )
    
    def _generate_enhancement_recommendations(self,
                                            current_stats: Dict[str, int],
                                            target_stats: Dict[str, int],
                                            selected_role: OptimizationRole,
                                            gcw_role: Optional[GCWRole],
                                            budget: str) -> List[EnhancementRecommendation]:
        """Generate enhancement recommendations."""
        recommendations = []
        
        # Generate tape recommendations
        tape_recommendations = self._generate_tape_recommendations(
            current_stats, target_stats, selected_role, gcw_role, budget
        )
        recommendations.extend(tape_recommendations)
        
        # Generate food recommendations
        food_recommendations = self._generate_food_recommendations(
            current_stats, target_stats, selected_role, gcw_role, budget
        )
        recommendations.extend(food_recommendations)
        
        # Generate ent buff recommendations
        ent_buff_recommendations = self._generate_ent_buff_recommendations(
            current_stats, target_stats, selected_role, gcw_role, budget
        )
        recommendations.extend(ent_buff_recommendations)
        
        return recommendations
    
    def _generate_tape_recommendations(self,
                                     current_stats: Dict[str, int],
                                     target_stats: Dict[str, int],
                                     selected_role: OptimizationRole,
                                     gcw_role: Optional[GCWRole],
                                     budget: str) -> List[EnhancementRecommendation]:
        """Generate tape recommendations."""
        recommendations = []
        
        # Identify attributes that need improvement
        for attribute, current_value in current_stats.items():
            target_value = target_stats.get(attribute, current_value)
            if target_value > current_value:
                improvement = target_value - current_value
                
                if improvement >= 20:  # Significant improvement needed
                    priority = OptimizationPriority.HIGH
                elif improvement >= 10:
                    priority = OptimizationPriority.MEDIUM
                else:
                    priority = OptimizationPriority.LOW
                
                effect = {attribute: improvement}
                cost = "1k-5k" if budget == "low" else "5k-15k" if budget == "medium" else "15k-50k"
                
                reasoning = f"Boost {attribute.title()} from {current_value} to {target_value}"
                
                recommendation = EnhancementRecommendation(
                    type="tape",
                    name=f"{attribute.title()} Enhancement Tape",
                    effect=effect,
                    duration="Permanent",
                    cost=cost,
                    priority=priority,
                    reasoning=reasoning
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_food_recommendations(self,
                                     current_stats: Dict[str, int],
                                     target_stats: Dict[str, int],
                                     selected_role: OptimizationRole,
                                     gcw_role: Optional[GCWRole],
                                     budget: str) -> List[EnhancementRecommendation]:
        """Generate food recommendations."""
        recommendations = []
        
        # Role-specific food recommendations
        role_foods = {
            OptimizationRole.DPS: {"precision": 15, "strength": 10},
            OptimizationRole.TANK: {"constitution": 20, "willpower": 10},
            OptimizationRole.SUPPORT: {"focus": 15, "willpower": 15},
            OptimizationRole.HYBRID: {"precision": 10, "constitution": 10, "agility": 10},
            OptimizationRole.PVP: {"precision": 15, "agility": 15}
        }
        
        food_effects = role_foods.get(selected_role, {"constitution": 10})
        
        for attribute, bonus in food_effects.items():
            priority = OptimizationPriority.MEDIUM
            cost = "500-2k" if budget == "low" else "2k-8k" if budget == "medium" else "8k-25k"
            
            reasoning = f"Temporary {attribute.title()} boost for {selected_role.value.upper()} role"
            
            recommendation = EnhancementRecommendation(
                type="food",
                name=f"{attribute.title()} Boosting Food",
                effect={attribute: bonus},
                duration="2 hours",
                cost=cost,
                priority=priority,
                reasoning=reasoning
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_ent_buff_recommendations(self,
                                         current_stats: Dict[str, int],
                                         target_stats: Dict[str, int],
                                         selected_role: OptimizationRole,
                                         gcw_role: Optional[GCWRole],
                                         budget: str) -> List[EnhancementRecommendation]:
        """Generate ent buff recommendations."""
        recommendations = []
        
        # Role-specific ent buffs
        role_ent_buffs = {
            OptimizationRole.DPS: {"precision": 25, "strength": 20},
            OptimizationRole.TANK: {"constitution": 30, "willpower": 20},
            OptimizationRole.SUPPORT: {"focus": 25, "willpower": 25},
            OptimizationRole.HYBRID: {"precision": 15, "constitution": 15, "agility": 15},
            OptimizationRole.PVP: {"precision": 25, "agility": 25}
        }
        
        ent_buff_effects = role_ent_buffs.get(selected_role, {"constitution": 20})
        
        for attribute, bonus in ent_buff_effects.items():
            priority = OptimizationPriority.HIGH
            cost = "Free"  # Ent buffs are typically free
            
            reasoning = f"Ent buff for {attribute.title()} boost in {selected_role.value.upper()} role"
            
            recommendation = EnhancementRecommendation(
                type="ent_buff",
                name=f"{attribute.title()} Ent Buff",
                effect={attribute: bonus},
                duration="4 hours",
                cost=cost,
                priority=priority,
                reasoning=reasoning
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_gcw_optimization(self,
                                  current_stats: Dict[str, int],
                                  gcw_role: GCWRole) -> Optional[GCWOptimization]:
        """Generate GCW-specific optimization."""
        if gcw_role.value not in self.gcw_data.get("roles", {}):
            return None
        
        gcw_role_data = self.gcw_data["roles"][gcw_role.value]
        primary_attrs = gcw_role_data.get("primary_attributes", [])
        secondary_attrs = gcw_role_data.get("secondary_attributes", [])
        
        # Calculate required attributes for GCW role
        required_attributes = {}
        for attr in primary_attrs:
            required_attributes[attr] = 400  # High requirement for primary
        for attr in secondary_attrs:
            required_attributes[attr] = 300  # Medium requirement for secondary
        
        # Determine current and target GCW rank
        current_rank = 1  # Would be extracted from character profile
        target_rank = min(current_rank + 1, 5)  # Aim for next rank
        
        # Generate recommended gear
        gear_priorities = gcw_role_data.get("gear_priorities", [])
        recommended_gear = []
        for gear_type in gear_priorities:
            if gear_type == "armor":
                recommended_gear.extend(["Enhanced Combat Armor", "Resistance Plating"])
            elif gear_type == "weapons":
                recommended_gear.extend(["High-Precision Rifle", "Combat Knife"])
            elif gear_type == "enhancements":
                recommended_gear.extend(["Combat Stimulants", "Tactical Gear"])
        
        # Generate strategy notes
        strategy = gcw_role_data.get("strategy", "General combat optimization")
        strategy_notes = [
            f"Focus on {', '.join(primary_attrs)} for primary role",
            f"Maintain {', '.join(secondary_attrs)} for secondary capabilities",
            f"Strategy: {strategy}",
            f"Target GCW Rank: {target_rank}"
        ]
        
        return GCWOptimization(
            role=gcw_role,
            current_rank=current_rank,
            target_rank=target_rank,
            required_attributes=required_attributes,
            recommended_gear=recommended_gear,
            strategy_notes=strategy_notes
        )
    
    def _calculate_overall_improvement(self,
                                     attribute_breakpoints: List[AttributeBreakpoint],
                                     armor_recommendations: List[ArmorRecommendation],
                                     enhancement_recommendations: List[EnhancementRecommendation]) -> float:
        """Calculate overall improvement score."""
        total_improvement = 0.0
        total_weight = 0.0
        
        # Weight attribute improvements
        for breakpoint in attribute_breakpoints:
            weight = 1.0 if breakpoint.priority == OptimizationPriority.CRITICAL else 0.7
            total_improvement += breakpoint.improvement_potential * weight
            total_weight += weight
        
        # Weight armor improvements
        for armor in armor_recommendations:
            weight = 1.0 if armor.priority == OptimizationPriority.HIGH else 0.7
            improvement = sum(armor.resist_gains.values()) / 100.0  # Normalize
            total_improvement += improvement * weight
            total_weight += weight
        
        # Weight enhancement improvements
        for enhancement in enhancement_recommendations:
            weight = 1.0 if enhancement.priority == OptimizationPriority.HIGH else 0.7
            improvement = sum(enhancement.effect.values()) / 100.0  # Normalize
            total_improvement += improvement * weight
            total_weight += weight
        
        return total_improvement / total_weight if total_weight > 0 else 0.0
    
    def _determine_implementation_priority(self,
                                        attribute_breakpoints: List[AttributeBreakpoint],
                                        armor_recommendations: List[ArmorRecommendation],
                                        enhancement_recommendations: List[EnhancementRecommendation]) -> List[str]:
        """Determine implementation priority order."""
        priority_items = []
        
        # Critical items first
        for breakpoint in attribute_breakpoints:
            if breakpoint.priority == OptimizationPriority.CRITICAL:
                priority_items.append(f"Improve {breakpoint.attribute.title()} to {breakpoint.breakpoint_value}")
        
        for armor in armor_recommendations:
            if armor.priority == OptimizationPriority.CRITICAL:
                priority_items.append(f"Upgrade {armor.slot} armor")
        
        for enhancement in enhancement_recommendations:
            if enhancement.priority == OptimizationPriority.CRITICAL:
                priority_items.append(f"Apply {enhancement.name}")
        
        # High priority items
        for breakpoint in attribute_breakpoints:
            if breakpoint.priority == OptimizationPriority.HIGH:
                priority_items.append(f"Boost {breakpoint.attribute.title()} attributes")
        
        for armor in armor_recommendations:
            if armor.priority == OptimizationPriority.HIGH:
                priority_items.append(f"Enhance {armor.slot} protection")
        
        for enhancement in enhancement_recommendations:
            if enhancement.priority == OptimizationPriority.HIGH:
                priority_items.append(f"Use {enhancement.name}")
        
        return priority_items
    
    def _calculate_total_cost(self,
                            armor_recommendations: List[ArmorRecommendation],
                            enhancement_recommendations: List[EnhancementRecommendation]) -> str:
        """Calculate total cost of recommendations."""
        total_cost = 0
        
        for armor in armor_recommendations:
            cost_str = armor.cost
            if "-" in cost_str:
                avg_cost = sum(int(x.replace("k", "000")) for x in cost_str.split("-"))
                total_cost += avg_cost // 2
            else:
                total_cost += int(cost_str.replace("k", "000"))
        
        for enhancement in enhancement_recommendations:
            if enhancement.cost != "Free":
                cost_str = enhancement.cost
                if "-" in cost_str:
                    avg_cost = sum(int(x.replace("k", "000")) for x in cost_str.split("-"))
                    total_cost += avg_cost // 2
                else:
                    total_cost += int(cost_str.replace("k", "000"))
        
        if total_cost < 10000:
            return f"{total_cost//1000}k credits"
        elif total_cost < 100000:
            return f"{total_cost//1000}k credits"
        else:
            return f"{total_cost//1000}k credits"
    
    def _generate_tradeoffs(self,
                           selected_role: OptimizationRole,
                           gcw_role: Optional[GCWRole],
                           attribute_breakpoints: List[AttributeBreakpoint],
                           armor_recommendations: List[ArmorRecommendation],
                           enhancement_recommendations: List[EnhancementRecommendation]) -> List[str]:
        """Generate tradeoff explanations."""
        tradeoffs = []
        
        # Role-specific tradeoffs
        if selected_role == OptimizationRole.DPS:
            tradeoffs.append("High damage output but reduced survivability")
            tradeoffs.append("Focus on precision over constitution")
        elif selected_role == OptimizationRole.TANK:
            tradeoffs.append("High survivability but reduced damage output")
            tradeoffs.append("Focus on constitution over precision")
        elif selected_role == OptimizationRole.SUPPORT:
            tradeoffs.append("Balanced approach with healing capabilities")
            tradeoffs.append("Focus on focus and willpower")
        
        # GCW-specific tradeoffs
        if gcw_role:
            tradeoffs.append(f"Specialized for {gcw_role.value} role in GCW")
            tradeoffs.append("May be less effective in PvE scenarios")
        
        # Cost tradeoffs
        total_cost = self._calculate_total_cost(armor_recommendations, enhancement_recommendations)
        if "100k" in total_cost or "150k" in total_cost:
            tradeoffs.append("High cost investment required")
        elif "50k" in total_cost:
            tradeoffs.append("Moderate cost investment")
        else:
            tradeoffs.append("Low cost optimization")
        
        return tradeoffs
    
    def _generate_links(self,
                       selected_role: OptimizationRole,
                       gcw_role: Optional[GCWRole]) -> Dict[str, str]:
        """Generate links to relevant pages."""
        links = {
            "builds": "/builds",
            "items": "/items",
            "armor": "/armor",
            "enhancements": "/enhancements"
        }
        
        # Role-specific links
        if selected_role == OptimizationRole.DPS:
            links["weapons"] = "/weapons/dps"
        elif selected_role == OptimizationRole.TANK:
            links["armor"] = "/armor/tank"
        elif selected_role == OptimizationRole.SUPPORT:
            links["healing"] = "/healing"
        
        # GCW-specific links
        if gcw_role:
            links["gcw"] = f"/gcw/{gcw_role.value}"
            links["faction"] = "/faction"
        
        return links
    
    def _save_optimization_result(self, result: OptimizationResult) -> None:
        """Save optimization result to persistent storage."""
        try:
            # Create optimization history directory
            history_dir = Path("data/optimization_history")
            history_dir.mkdir(exist_ok=True)
            
            # Save to character-specific file
            character_file = history_dir / f"{result.character_name}_optimizations.json"
            
            # Load existing history
            history = []
            if character_file.exists():
                with open(character_file, 'r') as f:
                    history = json.load(f)
            
            # Add new result
            result_dict = {
                "timestamp": result.timestamp.isoformat(),
                "selected_role": result.selected_role.value,
                "gcw_role": result.gcw_role.value if result.gcw_role else None,
                "overall_improvement": result.overall_improvement,
                "total_cost": result.total_cost,
                "implementation_priority": result.implementation_priority
            }
            
            history.append(result_dict)
            
            # Keep only last 3 optimizations
            if len(history) > 3:
                history = history[-3:]
            
            # Save updated history
            with open(character_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            self.logger.info(f"Saved optimization result for {result.character_name}")
            
        except Exception as e:
            self.logger.error(f"Error saving optimization result: {e}")


def get_build_optimizer_v2() -> BuildOptimizerV2:
    """Get a singleton instance of BuildOptimizerV2."""
    if not hasattr(get_build_optimizer_v2, '_instance'):
        get_build_optimizer_v2._instance = BuildOptimizerV2()
    return get_build_optimizer_v2._instance


def optimize_character_build(character_name: str,
                           selected_role: OptimizationRole,
                           gcw_role: Optional[GCWRole] = None,
                           budget: str = "medium") -> Optional[OptimizationResult]:
    """Convenience function to optimize a character's build."""
    try:
        # Get character profile (this would integrate with Batch 122 stat scanner)
        stat_extractor = get_stat_extractor()
        character_profile = stat_extractor.get_character_profile(character_name)
        
        if not character_profile:
            logging.error(f"Could not get character profile for {character_name}")
            return None
        
        # Perform optimization
        optimizer = get_build_optimizer_v2()
        result = optimizer.optimize_build(
            character_profile=character_profile,
            selected_role=selected_role,
            gcw_role=gcw_role,
            budget=budget
        )
        
        return result
        
    except Exception as e:
        logging.error(f"Error optimizing build for {character_name}: {e}")
        return None


def save_optimization_result(result: OptimizationResult) -> bool:
    """Save optimization result to file."""
    try:
        optimizer = get_build_optimizer_v2()
        optimizer._save_optimization_result(result)
        return True
    except Exception as e:
        logging.error(f"Error saving optimization result: {e}")
        return False 
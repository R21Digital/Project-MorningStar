#!/usr/bin/env python3
"""Profile Generator Module for Batch 042.

This module provides functionality to generate planetary quest profiles for 100% completion
mode based on imported quest data from the wiki.
"""

import json
import logging
import yaml
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from .fallback_detector import FallbackDetector


class ProfileGenerator:
    """Generates planetary quest profiles for 100% completion mode."""
    
    def __init__(self):
        """Initialize the profile generator."""
        self.logger = logging.getLogger(__name__)
        self.detector = FallbackDetector()
        
        # Data directories
        self.data_dir = Path("data")
        self.quests_dir = self.data_dir / "quests"
        self.profiles_dir = self.data_dir / "quest_profiles"
        self.profiles_dir.mkdir(exist_ok=True)
        
        # Profile templates
        self.profile_templates = {
            'legacy': self._get_legacy_template(),
            'theme_park': self._get_theme_park_template(),
            'faction': self._get_faction_template(),
            'crafting': self._get_crafting_template(),
            'exploration': self._get_exploration_template(),
            'social': self._get_social_template(),
            'combat': self._get_combat_template(),
            'delivery': self._get_delivery_template(),
            'collection': self._get_collection_template()
        }

    def generate_planetary_profiles(self, planet: str = None) -> Dict[str, Any]:
        """Generate planetary quest profiles for 100% completion mode."""
        self.logger.info(f"Generating planetary quest profiles for {planet or 'all planets'}")
        
        if planet:
            planets = [planet]
        else:
            # Get all planets from quest database
            stats = self.detector.get_database_stats()
            planets = list(stats['quests_by_planet'].keys())
        
        generated_profiles = {}
        
        for target_planet in planets:
            try:
                profile = self._generate_planet_profile(target_planet)
                if profile:
                    generated_profiles[target_planet] = profile
                    self._save_planet_profile(target_planet, profile)
            except Exception as e:
                self.logger.error(f"Error generating profile for {target_planet}: {e}")
        
        self.logger.info(f"Generated {len(generated_profiles)} planetary profiles")
        return generated_profiles

    def _generate_planet_profile(self, planet: str) -> Optional[Dict[str, Any]]:
        """Generate a quest profile for a specific planet."""
        # Get all quests for the planet
        planet_quests = self.detector.get_quests_by_planet(planet)
        
        if not planet_quests:
            self.logger.warning(f"No quests found for planet: {planet}")
            return None
        
        # Organize quests by type
        quests_by_type = defaultdict(list)
        for quest in planet_quests:
            quest_type = quest['database_info'].get('quest_type', 'unknown')
            quests_by_type[quest_type].append(quest)
        
        # Generate profile sections
        profile = {
            'planet': planet,
            'generated_date': datetime.now().isoformat(),
            'total_quests': len(planet_quests),
            'quests_by_type': dict(quests_by_type),
            'completion_goals': self._generate_completion_goals(planet_quests),
            'quest_chains': self._identify_quest_chains(planet_quests),
            'recommended_order': self._generate_recommended_order(planet_quests),
            'prerequisites_map': self._build_prerequisites_map(planet_quests),
            'rewards_summary': self._generate_rewards_summary(planet_quests),
            'difficulty_progression': self._generate_difficulty_progression(planet_quests),
            'completion_estimates': self._generate_completion_estimates(planet_quests)
        }
        
        return profile

    def _generate_completion_goals(self, planet_quests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate completion goals for the planet."""
        goals = {
            'total_quests': len(planet_quests),
            'quests_by_type': {},
            'quests_by_difficulty': {},
            'estimated_completion_time': 0,
            'required_levels': set(),
            'unlock_requirements': []
        }
        
        for quest in planet_quests:
            quest_info = quest['database_info']
            quest_type = quest_info.get('quest_type', 'unknown')
            difficulty = quest_info.get('difficulty', 'medium')
            level_req = quest_info.get('level_requirement', 0)
            
            # Count by type
            goals['quests_by_type'][quest_type] = goals['quests_by_type'].get(quest_type, 0) + 1
            
            # Count by difficulty
            goals['quests_by_difficulty'][difficulty] = goals['quests_by_difficulty'].get(difficulty, 0) + 1
            
            # Track level requirements
            if level_req > 0:
                goals['required_levels'].add(level_req)
            
            # Estimate completion time (rough estimates)
            time_estimate = self._estimate_quest_time(quest_info)
            goals['estimated_completion_time'] += time_estimate
        
        # Convert set to list for JSON serialization
        goals['required_levels'] = sorted(list(goals['required_levels']))
        
        return goals

    def _identify_quest_chains(self, planet_quests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify quest chains and dependencies."""
        quest_chains = []
        
        # Group quests by potential chains
        chain_groups = defaultdict(list)
        
        for quest in planet_quests:
            quest_info = quest['database_info']
            quest_name = quest_info.get('name', '').lower()
            
            # Identify chain keywords
            chain_keywords = ['part', 'chapter', 'episode', 'mission', 'quest']
            for keyword in chain_keywords:
                if keyword in quest_name:
                    # Extract chain identifier
                    parts = quest_name.split(keyword)
                    if len(parts) > 1:
                        chain_id = parts[0].strip()
                        chain_groups[chain_id].append(quest)
                        break
        
        # Create chain profiles
        for chain_id, chain_quests in chain_groups.items():
            if len(chain_quests) > 1:  # Only consider actual chains
                chain_profile = {
                    'chain_id': chain_id,
                    'quests': [q['quest_id'] for q in chain_quests],
                    'total_quests': len(chain_quests),
                    'estimated_time': sum(self._estimate_quest_time(q['database_info']) for q in chain_quests),
                    'prerequisites': self._get_chain_prerequisites(chain_quests)
                }
                quest_chains.append(chain_profile)
        
        return quest_chains

    def _generate_recommended_order(self, planet_quests: List[Dict[str, Any]]) -> List[str]:
        """Generate recommended quest completion order."""
        # Sort quests by level requirement and difficulty
        sorted_quests = sorted(planet_quests, key=lambda q: (
            q['database_info'].get('level_requirement', 0),
            self._difficulty_to_numeric(q['database_info'].get('difficulty', 'medium'))
        ))
        
        return [q['quest_id'] for q in sorted_quests]

    def _build_prerequisites_map(self, planet_quests: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Build a map of quest prerequisites."""
        prerequisites_map = {}
        
        for quest in planet_quests:
            quest_id = quest['quest_id']
            detailed_data = quest.get('detailed_data', {})
            
            if detailed_data and 'prerequisites' in detailed_data:
                prerequisites_map[quest_id] = detailed_data['prerequisites']
            else:
                prerequisites_map[quest_id] = []
        
        return prerequisites_map

    def _generate_rewards_summary(self, planet_quests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of quest rewards."""
        rewards_summary = {
            'total_experience': 0,
            'total_credits': 0,
            'total_reputation': {},
            'items': [],
            'unlocks': []
        }
        
        for quest in planet_quests:
            detailed_data = quest.get('detailed_data', {})
            if detailed_data and 'rewards' in detailed_data:
                rewards = detailed_data['rewards']
                
                # Sum experience
                if 'experience' in rewards:
                    rewards_summary['total_experience'] += rewards['experience']
                
                # Sum credits
                if 'credits' in rewards:
                    rewards_summary['total_credits'] += rewards['credits']
                
                # Sum reputation
                if 'reputation' in rewards:
                    for faction, amount in rewards['reputation'].items():
                        rewards_summary['total_reputation'][faction] = rewards_summary['total_reputation'].get(faction, 0) + amount
                
                # Collect items
                if 'items' in rewards:
                    rewards_summary['items'].extend(rewards['items'])
                
                # Collect unlocks
                if 'unlocks' in rewards:
                    rewards_summary['unlocks'].extend(rewards['unlocks'])
        
        return rewards_summary

    def _generate_difficulty_progression(self, planet_quests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate difficulty progression for the planet."""
        progression = []
        
        # Group quests by difficulty
        difficulty_groups = defaultdict(list)
        for quest in planet_quests:
            difficulty = quest['database_info'].get('difficulty', 'medium')
            difficulty_groups[difficulty].append(quest)
        
        # Create progression stages
        difficulty_order = ['easy', 'medium', 'hard', 'expert']
        
        for difficulty in difficulty_order:
            if difficulty in difficulty_groups:
                stage = {
                    'difficulty': difficulty,
                    'quests': [q['quest_id'] for q in difficulty_groups[difficulty]],
                    'count': len(difficulty_groups[difficulty]),
                    'estimated_time': sum(self._estimate_quest_time(q['database_info']) for q in difficulty_groups[difficulty])
                }
                progression.append(stage)
        
        return progression

    def _generate_completion_estimates(self, planet_quests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate completion time and effort estimates."""
        total_time = 0
        total_quests = len(planet_quests)
        
        for quest in planet_quests:
            total_time += self._estimate_quest_time(quest['database_info'])
        
        return {
            'total_quests': total_quests,
            'estimated_time_minutes': total_time,
            'estimated_time_hours': total_time / 60,
            'average_time_per_quest': total_time / total_quests if total_quests > 0 else 0,
            'completion_percentage_milestones': [
                {'percentage': 25, 'quests': total_quests // 4},
                {'percentage': 50, 'quests': total_quests // 2},
                {'percentage': 75, 'quests': (total_quests * 3) // 4},
                {'percentage': 100, 'quests': total_quests}
            ]
        }

    def _estimate_quest_time(self, quest_info: Dict[str, Any]) -> int:
        """Estimate completion time for a quest in minutes."""
        quest_type = quest_info.get('quest_type', 'unknown')
        difficulty = quest_info.get('difficulty', 'medium')
        
        # Base time estimates by type
        base_times = {
            'legacy': 30,
            'theme_park': 20,
            'faction': 25,
            'crafting': 15,
            'exploration': 20,
            'social': 10,
            'combat': 15,
            'delivery': 10,
            'collection': 20,
            'unknown': 15
        }
        
        base_time = base_times.get(quest_type, 15)
        
        # Adjust by difficulty
        difficulty_multipliers = {
            'easy': 0.8,
            'medium': 1.0,
            'hard': 1.5,
            'expert': 2.0
        }
        
        multiplier = difficulty_multipliers.get(difficulty, 1.0)
        
        return int(base_time * multiplier)

    def _difficulty_to_numeric(self, difficulty: str) -> int:
        """Convert difficulty to numeric value for sorting."""
        difficulty_map = {
            'easy': 1,
            'medium': 2,
            'hard': 3,
            'expert': 4
        }
        return difficulty_map.get(difficulty, 2)

    def _get_chain_prerequisites(self, chain_quests: List[Dict[str, Any]]) -> List[str]:
        """Get prerequisites for a quest chain."""
        prerequisites = set()
        
        for quest in chain_quests:
            detailed_data = quest.get('detailed_data', {})
            if detailed_data and 'prerequisites' in detailed_data:
                prerequisites.update(detailed_data['prerequisites'])
        
        return list(prerequisites)

    def _save_planet_profile(self, planet: str, profile: Dict[str, Any]):
        """Save a planet profile to file."""
        try:
            profile_file = self.profiles_dir / f"{planet}_quest_profile.yaml"
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                yaml.dump(profile, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"Saved planet profile: {profile_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving planet profile for {planet}: {e}")

    def _get_legacy_template(self) -> Dict[str, Any]:
        """Get template for legacy quest profiles."""
        return {
            'quest_type': 'legacy',
            'completion_style': 'story_driven',
            'recommended_approach': 'sequential',
            'time_estimate_multiplier': 1.5
        }

    def _get_theme_park_template(self) -> Dict[str, Any]:
        """Get template for theme park quest profiles."""
        return {
            'quest_type': 'theme_park',
            'completion_style': 'entertainment_focused',
            'recommended_approach': 'casual',
            'time_estimate_multiplier': 1.0
        }

    def _get_faction_template(self) -> Dict[str, Any]:
        """Get template for faction quest profiles."""
        return {
            'quest_type': 'faction',
            'completion_style': 'reputation_building',
            'recommended_approach': 'faction_aligned',
            'time_estimate_multiplier': 1.2
        }

    def _get_crafting_template(self) -> Dict[str, Any]:
        """Get template for crafting quest profiles."""
        return {
            'quest_type': 'crafting',
            'completion_style': 'skill_based',
            'recommended_approach': 'profession_focused',
            'time_estimate_multiplier': 0.8
        }

    def _get_exploration_template(self) -> Dict[str, Any]:
        """Get template for exploration quest profiles."""
        return {
            'quest_type': 'exploration',
            'completion_style': 'discovery_focused',
            'recommended_approach': 'wander_and_explore',
            'time_estimate_multiplier': 1.3
        }

    def _get_social_template(self) -> Dict[str, Any]:
        """Get template for social quest profiles."""
        return {
            'quest_type': 'social',
            'completion_style': 'interaction_based',
            'recommended_approach': 'community_focused',
            'time_estimate_multiplier': 0.7
        }

    def _get_combat_template(self) -> Dict[str, Any]:
        """Get template for combat quest profiles."""
        return {
            'quest_type': 'combat',
            'completion_style': 'action_oriented',
            'recommended_approach': 'combat_ready',
            'time_estimate_multiplier': 1.1
        }

    def _get_delivery_template(self) -> Dict[str, Any]:
        """Get template for delivery quest profiles."""
        return {
            'quest_type': 'delivery',
            'completion_style': 'logistics_focused',
            'recommended_approach': 'efficient_routing',
            'time_estimate_multiplier': 0.9
        }

    def _get_collection_template(self) -> Dict[str, Any]:
        """Get template for collection quest profiles."""
        return {
            'quest_type': 'collection',
            'completion_style': 'gathering_focused',
            'recommended_approach': 'systematic_search',
            'time_estimate_multiplier': 1.0
        }


def generate_planetary_profiles(planet: str = None) -> Dict[str, Any]:
    """Generate planetary quest profiles for 100% completion mode."""
    generator = ProfileGenerator()
    return generator.generate_planetary_profiles(planet) 
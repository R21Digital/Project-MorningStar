"""SWGR Skill Calculator Integration for Batch 041.

This module provides functionality to parse SWGR skill calculator URLs
and extract skill tree data for automatic combat profile generation.
"""

import re
import json
import logging
import urllib.parse
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

import requests


@dataclass
class SkillTree:
    """Represents a parsed skill tree from SWGR skill calculator."""
    professions: Dict[str, Dict[str, Any]]
    total_points: int
    character_level: int
    build_hash: str
    url: str
    
    def get_profession_names(self) -> List[str]:
        """Get list of profession names in the skill tree."""
        return list(self.professions.keys())
    
    def get_profession_points(self, profession: str) -> int:
        """Get total points invested in a specific profession."""
        if profession not in self.professions:
            return 0
        return self.professions[profession].get('points', 0)
    
    def get_profession_skills(self, profession: str) -> Dict[str, Any]:
        """Get skills for a specific profession."""
        if profession not in self.professions:
            return {}
        return self.professions[profession].get('skills', {})


class SkillCalculator:
    """Main class for parsing SWGR skill calculator URLs and extracting skill data."""
    
    def __init__(self):
        """Initialize the skill calculator."""
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://swgr.org/skill-calculator/"
        
        # SWGR profession mappings
        self.professions = {
            "brawler": "Brawler",
            "marksman": "Marksman", 
            "scout": "Scout",
            "artisan": "Artisan",
            "entertainer": "Entertainer",
            "medic": "Medic",
            "officer": "Officer",
            "smuggler": "Smuggler",
            "spy": "Spy",
            "trader": "Trader",
            "bounty_hunter": "Bounty Hunter",
            "commando": "Commando",
            "force_sensitive": "Force Sensitive",
            "jedi": "Jedi",
            "sith": "Sith"
        }
    
    def parse_swgr_url(self, url: str) -> Optional[SkillTree]:
        """Parse SWGR skill calculator URL and extract skill tree data.
        
        Parameters
        ----------
        url : str
            SWGR skill calculator URL
            
        Returns
        -------
        SkillTree or None
            Parsed skill tree data if successful, None otherwise
        """
        try:
            self.logger.info(f"Parsing SWGR skill calculator URL: {url}")
            
            # Extract build hash from URL
            build_hash = self._extract_build_hash(url)
            if not build_hash:
                self.logger.error("Could not extract build hash from URL")
                return None
            
            # Fetch skill tree data
            skill_data = self._fetch_skill_data(build_hash)
            if not skill_data:
                self.logger.error("Could not fetch skill data")
                return None
            
            # Parse skill tree
            skill_tree = self._parse_skill_tree(skill_data, build_hash, url)
            if not skill_tree:
                self.logger.error("Could not parse skill tree")
                return None
            
            self.logger.info(f"Successfully parsed skill tree with {len(skill_tree.professions)} professions")
            return skill_tree
            
        except Exception as e:
            self.logger.error(f"Error parsing SWGR URL: {e}")
            return None
    
    def _extract_build_hash(self, url: str) -> Optional[str]:
        """Extract build hash from SWGR skill calculator URL.
        
        Parameters
        ----------
        url : str
            SWGR skill calculator URL
            
        Returns
        -------
        str or None
            Build hash if found, None otherwise
        """
        try:
            # Parse URL
            parsed_url = urllib.parse.urlparse(url)
            
            # Check if it's a valid SWGR skill calculator URL
            if not parsed_url.netloc.endswith('swgr.org'):
                self.logger.error("Invalid SWGR domain")
                return None
            
            if '/skill-calculator/' not in parsed_url.path:
                self.logger.error("Not a skill calculator URL")
                return None
            
            # Extract hash from path or query parameters
            path_parts = parsed_url.path.split('/')
            for part in path_parts:
                if len(part) > 20:  # Likely a build hash
                    return part
            
            # Check query parameters
            query_params = urllib.parse.parse_qs(parsed_url.query)
            if 'build' in query_params:
                return query_params['build'][0]
            
            # Check fragment
            if parsed_url.fragment:
                return parsed_url.fragment
            
            self.logger.error("Could not find build hash in URL")
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting build hash: {e}")
            return None
    
    def _fetch_skill_data(self, build_hash: str) -> Optional[Dict[str, Any]]:
        """Fetch skill data from SWGR API using build hash.
        
        Parameters
        ----------
        build_hash : str
            Build hash to fetch data for
            
        Returns
        -------
        dict or None
            Skill data if successful, None otherwise
        """
        try:
            # Construct API URL
            api_url = f"{self.base_url}api/build/{build_hash}"
            
            # Fetch data
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            self.logger.info(f"Successfully fetched skill data for build {build_hash}")
            return data
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching skill data: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing skill data JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching skill data: {e}")
            return None
    
    def _parse_skill_tree(self, skill_data: Dict[str, Any], build_hash: str, url: str) -> Optional[SkillTree]:
        """Parse skill data into SkillTree object.
        
        Parameters
        ----------
        skill_data : dict
            Raw skill data from SWGR API
        build_hash : str
            Build hash
        url : str
            Original URL
            
        Returns
        -------
        SkillTree or None
            Parsed skill tree if successful, None otherwise
        """
        try:
            # Extract professions and skills
            professions = {}
            total_points = 0
            character_level = skill_data.get('level', 80)
            
            # Parse profession data
            for profession_key, profession_data in skill_data.get('professions', {}).items():
                profession_name = self.professions.get(profession_key, profession_key.title())
                
                # Extract skills for this profession
                skills = {}
                profession_points = 0
                
                for skill_key, skill_info in profession_data.get('skills', {}).items():
                    if isinstance(skill_info, dict):
                        skill_level = skill_info.get('level', 0)
                        skill_points = skill_info.get('points', 0)
                    else:
                        skill_level = skill_info
                        skill_points = skill_level
                    
                    if skill_level > 0:
                        skills[skill_key] = {
                            'level': skill_level,
                            'points': skill_points
                        }
                        profession_points += skill_points
                
                professions[profession_name] = {
                    'points': profession_points,
                    'skills': skills,
                    'key': profession_key
                }
                total_points += profession_points
            
            # Create SkillTree object
            skill_tree = SkillTree(
                professions=professions,
                total_points=total_points,
                character_level=character_level,
                build_hash=build_hash,
                url=url
            )
            
            self.logger.info(f"Parsed skill tree: {len(professions)} professions, {total_points} total points")
            return skill_tree
            
        except Exception as e:
            self.logger.error(f"Error parsing skill tree: {e}")
            return None
    
    def generate_combat_profile(self, skill_tree: SkillTree) -> Dict[str, Any]:
        """Generate combat profile from skill tree data.
        
        Parameters
        ----------
        skill_tree : SkillTree
            Parsed skill tree data
            
        Returns
        -------
        dict
            Generated combat profile
        """
        try:
            self.logger.info("Generating combat profile from skill tree")
            
            # Analyze professions and determine role
            from .profession_analyzer import analyze_professions, determine_role
            
            profession_analysis = analyze_professions(skill_tree.professions)
            role = determine_role(profession_analysis)
            
            # Generate combat configuration
            from .combat_generator import generate_combat_config
            
            combat_config = generate_combat_config(skill_tree, profession_analysis, role)
            
            # Create comprehensive profile
            profile = {
                'character_level': skill_tree.character_level,
                'total_points': skill_tree.total_points,
                'build_hash': skill_tree.build_hash,
                'url': skill_tree.url,
                'professions': skill_tree.professions,
                'profession_analysis': profession_analysis,
                'role': role,
                'combat_config': combat_config,
                'generated_at': self._get_timestamp()
            }
            
            self.logger.info(f"Generated combat profile for {role} role")
            return profile
            
        except Exception as e:
            self.logger.error(f"Error generating combat profile: {e}")
            return {}
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().isoformat()


def parse_swgr_url(url: str) -> Optional[SkillTree]:
    """Parse SWGR skill calculator URL.
    
    Parameters
    ----------
    url : str
        SWGR skill calculator URL
        
    Returns
    -------
    SkillTree or None
        Parsed skill tree data if successful, None otherwise
    """
    calculator = SkillCalculator()
    return calculator.parse_swgr_url(url)


def generate_combat_profile(skill_tree: SkillTree) -> Dict[str, Any]:
    """Generate combat profile from skill tree data.
    
    Parameters
    ----------
    skill_tree : SkillTree
        Parsed skill tree data
        
    Returns
    -------
    dict
        Generated combat profile
    """
    calculator = SkillCalculator()
    return calculator.generate_combat_profile(skill_tree) 
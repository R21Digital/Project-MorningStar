"""
SkillCalc Parser - SWG Skill Calculator Link Parser

This module provides comprehensive parsing of SWG skill calculator links including:
- Link validation and extraction
- Build data parsing and interpretation
- Profession and skill tree analysis
- Weapon class and combat preference detection
"""

import re
import json
import logging
import urllib.parse
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import requests

logger = logging.getLogger(__name__)


class ProfessionType(Enum):
    """SWG profession types."""
    COMMANDO = "commando"
    RIFLEMAN = "rifleman"
    PISTOLEER = "pistoleer"
    CARBINEER = "carbineer"
    SWORDSMAN = "swordsman"
    TERAS_KASI = "teras_kasi"
    BOWMAN = "bowman"
    SMUGGLER = "smuggler"
    BOUNTY_HUNTER = "bounty_hunter"
    SPY = "spy"
    MEDIC = "medic"
    COMBAT_MEDIC = "combat_medic"
    DOCTOR = "doctor"
    ARCHITECT = "architect"
    ARMORSMITH = "armorsmith"
    WEAPONSMITH = "weaponsmith"
    TAILOR = "tailor"
    CHEF = "chef"
    DANCER = "dancer"
    MUSICIAN = "musician"
    ENTERTAINER = "entertainer"
    IMAGE_DESIGNER = "image_designer"
    MERCHANT = "merchant"
    SCOUT = "scout"
    RANGER = "ranger"
    CREATURE_HANDLER = "creature_handler"
    BIO_ENGINEER = "bio_engineer"
    ARTISAN = "artisan"


class WeaponClass(Enum):
    """Weapon class types."""
    RANGED = "ranged"
    MELEE = "melee"
    HEAVY_WEAPONS = "heavy_weapons"
    LIGHT_WEAPONS = "light_weapons"
    UNARMED = "unarmed"
    SPECIAL = "special"


class CombatRange(Enum):
    """Combat range preferences."""
    MELEE = "melee"
    RANGED = "ranged"
    MIXED = "mixed"
    HEAVY = "heavy"


@dataclass
class SkillTree:
    """Represents a skill tree with its points and max points."""
    name: str
    current_points: int
    max_points: int
    skills: Dict[str, int] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = {}
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        return (self.current_points / self.max_points) * 100 if self.max_points > 0 else 0


@dataclass
class BuildInfo:
    """Comprehensive build information."""
    build_id: str
    profession: Optional[ProfessionType] = None
    weapon_class: Optional[WeaponClass] = None
    combat_range: Optional[CombatRange] = None
    skill_trees: Dict[str, SkillTree] = None
    total_points: int = 0
    max_points: int = 0
    build_url: str = ""
    is_valid: bool = False
    parse_errors: List[str] = None
    
    def __post_init__(self):
        if self.skill_trees is None:
            self.skill_trees = {}
        if self.parse_errors is None:
            self.parse_errors = []
    
    @property
    def completion_percentage(self) -> float:
        """Calculate overall build completion percentage."""
        return (self.total_points / self.max_points) * 100 if self.max_points > 0 else 0


class SkillCalcParser:
    """SWG Skill Calculator link parser and build analyzer."""
    
    def __init__(self):
        """Initialize the SkillCalc parser."""
        self.base_url = "https://swgr.org/skill-calculator/"
        self.valid_domains = ["swgr.org", "www.swgr.org"]
        
        # Profession detection patterns
        self.profession_patterns = {
            ProfessionType.COMMANDO: [r"commando", r"heavy_weapons"],
            ProfessionType.RIFLEMAN: [r"rifleman", r"rifle"],
            ProfessionType.PISTOLEER: [r"pistoleer", r"pistol"],
            ProfessionType.CARBINEER: [r"carbineer", r"carbine"],
            ProfessionType.SWORDSMAN: [r"swordsman", r"sword"],
            ProfessionType.TERAS_KASI: [r"teras_kasi", r"unarmed"],
            ProfessionType.BOWMAN: [r"bowman", r"bow"],
            ProfessionType.SMUGGLER: [r"smuggler"],
            ProfessionType.BOUNTY_HUNTER: [r"bounty_hunter"],
            ProfessionType.SPY: [r"spy"],
            ProfessionType.MEDIC: [r"medic"],
            ProfessionType.COMBAT_MEDIC: [r"combat_medic"],
            ProfessionType.DOCTOR: [r"doctor"],
            ProfessionType.ARCHITECT: [r"architect"],
            ProfessionType.ARMORSMITH: [r"armorsmith"],
            ProfessionType.WEAPONSMITH: [r"weaponsmith"],
            ProfessionType.TAILOR: [r"tailor"],
            ProfessionType.CHEF: [r"chef"],
            ProfessionType.DANCER: [r"dancer"],
            ProfessionType.MUSICIAN: [r"musician"],
            ProfessionType.ENTERTAINER: [r"entertainer"],
            ProfessionType.IMAGE_DESIGNER: [r"image_designer"],
            ProfessionType.MERCHANT: [r"merchant"],
            ProfessionType.SCOUT: [r"scout"],
            ProfessionType.RANGER: [r"ranger"],
            ProfessionType.CREATURE_HANDLER: [r"creature_handler"],
            ProfessionType.BIO_ENGINEER: [r"bio_engineer"],
            ProfessionType.ARTISAN: [r"artisan"]
        }
        
        # Weapon class detection patterns
        self.weapon_patterns = {
            WeaponClass.RANGED: [r"rifle", r"pistol", r"carbine", r"bow"],
            WeaponClass.MELEE: [r"sword", r"polearm", r"axe"],
            WeaponClass.HEAVY_WEAPONS: [r"heavy_weapon", r"rocket", r"grenade"],
            WeaponClass.LIGHT_WEAPONS: [r"light_weapon", r"knife"],
            WeaponClass.UNARMED: [r"unarmed", r"teras_kasi"],
            WeaponClass.SPECIAL: [r"special", r"exotic"]
        }
        
        logger.info("SkillCalcParser initialized")
    
    def parse_skillcalc_link(self, url: str) -> BuildInfo:
        """Parse a SkillCalc link and extract build information.
        
        Parameters
        ----------
        url : str
            SkillCalc URL to parse
            
        Returns
        -------
        BuildInfo
            Parsed build information
        """
        build_info = BuildInfo(build_id="", build_url=url)
        
        try:
            # Validate URL
            if not self._validate_url(url):
                build_info.parse_errors.append("Invalid SkillCalc URL")
                return build_info
            
            # Extract build ID
            build_id = self._extract_build_id(url)
            if not build_id:
                build_info.parse_errors.append("Could not extract build ID from URL")
                return build_info
            
            build_info.build_id = build_id
            
            # Fetch build data
            build_data = self._fetch_build_data(build_id)
            if not build_data:
                build_info.parse_errors.append("Could not fetch build data")
                return build_info
            
            # Parse build data
            self._parse_build_data(build_data, build_info)
            
            # Detect profession and weapon class
            self._detect_profession_and_weapon(build_info)
            
            # Determine combat range preference
            self._determine_combat_range(build_info)
            
            build_info.is_valid = len(build_info.parse_errors) == 0
            
        except Exception as e:
            build_info.parse_errors.append(f"Error parsing build: {str(e)}")
            logger.error(f"Error parsing SkillCalc link: {e}")
        
        return build_info
    
    def _validate_url(self, url: str) -> bool:
        """Validate if the URL is a valid SkillCalc link.
        
        Parameters
        ----------
        url : str
            URL to validate
            
        Returns
        -------
        bool
            True if valid SkillCalc URL
        """
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Check domain
            if parsed.netloc not in self.valid_domains:
                return False
            
            # Check path
            if not parsed.path.startswith("/skill-calculator/"):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _extract_build_id(self, url: str) -> Optional[str]:
        """Extract build ID from SkillCalc URL.
        
        Parameters
        ----------
        url : str
            SkillCalc URL
            
        Returns
        -------
        str, optional
            Build ID if found
        """
        try:
            # Extract build ID from URL path
            path_match = re.search(r"/skill-calculator/([^/?]+)", url)
            if path_match:
                return path_match.group(1)
            
            # Extract from query parameters
            parsed = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed.query)
            
            if "build" in query_params:
                return query_params["build"][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting build ID: {e}")
            return None
    
    def _fetch_build_data(self, build_id: str) -> Optional[Dict[str, Any]]:
        """Fetch build data from SkillCalc API.
        
        Parameters
        ----------
        build_id : str
            Build ID to fetch
            
        Returns
        -------
        dict, optional
            Build data if successful
        """
        try:
            # Construct API URL
            api_url = f"{self.base_url}api/build/{build_id}"
            
            # Fetch data
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error fetching build data: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing build data JSON: {e}")
            return None
    
    def _parse_build_data(self, build_data: Dict[str, Any], build_info: BuildInfo) -> None:
        """Parse build data and populate BuildInfo.
        
        Parameters
        ----------
        build_data : dict
            Raw build data from API
        build_info : BuildInfo
            BuildInfo object to populate
        """
        try:
            # Extract basic information
            build_info.total_points = build_data.get("total_points", 0)
            build_info.max_points = build_data.get("max_points", 250)
            
            # Parse skill trees
            skill_trees_data = build_data.get("skill_trees", {})
            for tree_name, tree_data in skill_trees_data.items():
                skill_tree = SkillTree(
                    name=tree_name,
                    current_points=tree_data.get("current_points", 0),
                    max_points=tree_data.get("max_points", 0),
                    skills=tree_data.get("skills", {})
                )
                build_info.skill_trees[tree_name] = skill_tree
            
        except Exception as e:
            build_info.parse_errors.append(f"Error parsing build data: {str(e)}")
            logger.error(f"Error parsing build data: {e}")
    
    def _detect_profession_and_weapon(self, build_info: BuildInfo) -> None:
        """Detect profession and weapon class from skill trees.
        
        Parameters
        ----------
        build_info : BuildInfo
            BuildInfo object to analyze
        """
        try:
            # Analyze skill trees for profession patterns
            profession_scores = {}
            weapon_scores = {}
            
            for tree_name, skill_tree in build_info.skill_trees.items():
                tree_lower = tree_name.lower()
                
                # Check profession patterns
                for profession, patterns in self.profession_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, tree_lower):
                            profession_scores[profession] = profession_scores.get(profession, 0) + skill_tree.current_points
                
                # Check weapon patterns
                for weapon_class, patterns in self.weapon_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, tree_lower):
                            weapon_scores[weapon_class] = weapon_scores.get(weapon_class, 0) + skill_tree.current_points
            
            # Determine primary profession
            if profession_scores:
                primary_profession = max(profession_scores.items(), key=lambda x: x[1])
                if primary_profession[1] > 0:
                    build_info.profession = primary_profession[0]
            
            # Determine primary weapon class
            if weapon_scores:
                primary_weapon = max(weapon_scores.items(), key=lambda x: x[1])
                if primary_weapon[1] > 0:
                    build_info.weapon_class = primary_weapon[0]
            
        except Exception as e:
            build_info.parse_errors.append(f"Error detecting profession/weapon: {str(e)}")
            logger.error(f"Error detecting profession and weapon: {e}")
    
    def _determine_combat_range(self, build_info: BuildInfo) -> None:
        """Determine combat range preference based on weapon class and skills.
        
        Parameters
        ----------
        build_info : BuildInfo
            BuildInfo object to analyze
        """
        try:
            if not build_info.weapon_class:
                build_info.combat_range = CombatRange.MIXED
                return
            
            # Map weapon classes to combat ranges
            weapon_to_range = {
                WeaponClass.RANGED: CombatRange.RANGED,
                WeaponClass.MELEE: CombatRange.MELEE,
                WeaponClass.HEAVY_WEAPONS: CombatRange.HEAVY,
                WeaponClass.LIGHT_WEAPONS: CombatRange.MELEE,
                WeaponClass.UNARMED: CombatRange.MELEE,
                WeaponClass.SPECIAL: CombatRange.MIXED
            }
            
            build_info.combat_range = weapon_to_range.get(build_info.weapon_class, CombatRange.MIXED)
            
        except Exception as e:
            build_info.parse_errors.append(f"Error determining combat range: {str(e)}")
            logger.error(f"Error determining combat range: {e}")
    
    def get_build_summary(self, build_info: BuildInfo) -> Dict[str, Any]:
        """Generate a summary of the parsed build.
        
        Parameters
        ----------
        build_info : BuildInfo
            BuildInfo object to summarize
            
        Returns
        -------
        dict
            Build summary
        """
        summary = {
            "build_id": build_info.build_id,
            "is_valid": build_info.is_valid,
            "profession": build_info.profession.value if build_info.profession else "Unknown",
            "weapon_class": build_info.weapon_class.value if build_info.weapon_class else "Unknown",
            "combat_range": build_info.combat_range.value if build_info.combat_range else "Unknown",
            "total_points": build_info.total_points,
            "max_points": build_info.max_points,
            "completion_percentage": build_info.completion_percentage,
            "skill_trees": {},
            "parse_errors": build_info.parse_errors
        }
        
        # Add skill tree summaries
        for tree_name, skill_tree in build_info.skill_trees.items():
            summary["skill_trees"][tree_name] = {
                "current_points": skill_tree.current_points,
                "max_points": skill_tree.max_points,
                "completion_percentage": skill_tree.completion_percentage,
                "skills": skill_tree.skills
            }
        
        return summary
    
    def validate_build_completeness(self, build_info: BuildInfo) -> Dict[str, Any]:
        """Validate build completeness and provide recommendations.
        
        Parameters
        ----------
        build_info : BuildInfo
            BuildInfo object to validate
            
        Returns
        -------
        dict
            Validation results and recommendations
        """
        validation = {
            "is_complete": False,
            "completion_percentage": build_info.completion_percentage,
            "missing_points": build_info.max_points - build_info.total_points,
            "recommendations": [],
            "warnings": []
        }
        
        # Check if build is complete
        if build_info.completion_percentage >= 100:
            validation["is_complete"] = True
        else:
            validation["recommendations"].append(
                f"Build is {build_info.completion_percentage:.1f}% complete. "
                f"Missing {validation['missing_points']} skill points."
            )
        
        # Check for empty skill trees
        empty_trees = []
        for tree_name, skill_tree in build_info.skill_trees.items():
            if skill_tree.current_points == 0:
                empty_trees.append(tree_name)
        
        if empty_trees:
            validation["warnings"].append(f"Empty skill trees: {', '.join(empty_trees)}")
        
        # Check for profession-specific recommendations
        if build_info.profession:
            validation["recommendations"].extend(
                self._get_profession_recommendations(build_info.profession, build_info)
            )
        
        return validation
    
    def _get_profession_recommendations(self, profession: ProfessionType, build_info: BuildInfo) -> List[str]:
        """Get profession-specific recommendations.
        
        Parameters
        ----------
        profession : ProfessionType
            Detected profession
        build_info : BuildInfo
            BuildInfo object
            
        Returns
        -------
        list
            List of recommendations
        """
        recommendations = []
        
        if profession == ProfessionType.COMMANDO:
            if build_info.combat_range != CombatRange.HEAVY:
                recommendations.append("Consider heavy weapons specialization for Commando")
        
        elif profession == ProfessionType.RIFLEMAN:
            if build_info.combat_range != CombatRange.RANGED:
                recommendations.append("Focus on ranged combat skills for Rifleman")
        
        elif profession == ProfessionType.SWORDSMAN:
            if build_info.combat_range != CombatRange.MELEE:
                recommendations.append("Focus on melee combat skills for Swordsman")
        
        return recommendations 
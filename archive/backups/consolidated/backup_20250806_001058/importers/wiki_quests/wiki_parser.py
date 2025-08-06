#!/usr/bin/env python3
"""Wiki Parser Module for Batch 042.

This module provides functionality to parse markdown/YAML content from SWGR wiki pages
and extract structured quest data including NPCs, objectives, prerequisites, and rewards.
"""

import re
import logging
import yaml
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class QuestType(Enum):
    """Types of quests available in SWGR."""
    LEGACY = "legacy"
    THEME_PARK = "theme_park"
    FACTION = "faction"
    CRAFTING = "crafting"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    COMBAT = "combat"
    DELIVERY = "delivery"
    COLLECTION = "collection"
    UNKNOWN = "unknown"


class QuestDifficulty(Enum):
    """Quest difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


@dataclass
class QuestData:
    """Represents extracted quest data from wiki pages."""
    quest_id: str
    name: str
    description: str = ""
    quest_type: QuestType = QuestType.UNKNOWN
    difficulty: QuestDifficulty = QuestDifficulty.MEDIUM
    level_requirement: int = 0
    planet: str = ""
    zone: str = ""
    coordinates: Tuple[int, int] = (0, 0)
    npc: str = ""
    rewards: Dict[str, Any] = None
    prerequisites: List[str] = None
    objectives: List[Dict[str, Any]] = None
    dialogue: List[str] = None
    steps: List[Dict[str, Any]] = None
    completion_conditions: List[Dict[str, Any]] = None
    failure_conditions: List[Dict[str, Any]] = None
    hints: List[str] = None
    metadata: Dict[str, Any] = None
    source_url: str = ""
    last_updated: str = ""

    def __post_init__(self):
        if self.rewards is None:
            self.rewards = {}
        if self.prerequisites is None:
            self.prerequisites = []
        if self.objectives is None:
            self.objectives = []
        if self.dialogue is None:
            self.dialogue = []
        if self.steps is None:
            self.steps = []
        if self.completion_conditions is None:
            self.completion_conditions = []
        if self.failure_conditions is None:
            self.failure_conditions = []
        if self.hints is None:
            self.hints = []
        if self.metadata is None:
            self.metadata = {}


class WikiParser:
    """Parser for SWGR wiki pages to extract quest data."""
    
    def __init__(self):
        """Initialize the wiki parser."""
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MS11-Wiki-Parser/1.0 (Educational Bot)'
        })
        
        # Wiki-specific patterns
        self.wiki_patterns = {
            'quest_id': r'quest[_-]?id[:\s]*([^\n\r]+)',
            'quest_name': r'name[:\s]*([^\n\r]+)',
            'description': r'description[:\s]*([^\n\r]+)',
            'planet': r'planet[:\s]*([^\n\r]+)',
            'npc': r'npc[:\s]*([^\n\r]+)',
            'coordinates': r'coordinates[:\s]*\[?(\d+)[,\s]+(\d+)\]?',
            'level_req': r'level[_\s]*requirement[:\s]*(\d+)',
            'difficulty': r'difficulty[:\s]*(easy|medium|hard|expert)',
            'rewards': r'rewards?[:\s]*([^\n\r]+)',
            'prerequisites': r'prerequisites?[:\s]*([^\n\r]+)',
            'objectives': r'objectives?[:\s]*([^\n\r]+)',
            'hints': r'hints?[:\s]*([^\n\r]+)'
        }
        
        # Quest type indicators
        self.quest_type_indicators = {
            QuestType.LEGACY: ['legacy', 'story', 'main', 'epic'],
            QuestType.THEME_PARK: ['theme park', 'theme_park', 'entertainer', 'musician'],
            QuestType.FACTION: ['faction', 'imperial', 'rebel', 'neutral'],
            QuestType.CRAFTING: ['craft', 'crafting', 'artisan', 'architect'],
            QuestType.EXPLORATION: ['explore', 'exploration', 'survey', 'scout'],
            QuestType.SOCIAL: ['social', 'entertainer', 'dancer', 'musician'],
            QuestType.COMBAT: ['combat', 'battle', 'fight', 'kill'],
            QuestType.DELIVERY: ['delivery', 'deliver', 'transport', 'courier'],
            QuestType.COLLECTION: ['collection', 'collect', 'gather', 'find']
        }

    def parse_wiki_page(self, url: str) -> Optional[QuestData]:
        """Parse a wiki page and extract quest data."""
        try:
            self.logger.info(f"Parsing wiki page: {url}")
            
            # Fetch the page content
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract quest data
            quest_data = self._extract_quest_data(soup, url)
            
            if quest_data:
                self.logger.info(f"Successfully parsed quest: {quest_data.name}")
                return quest_data
            else:
                self.logger.warning(f"No quest data found on page: {url}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error parsing wiki page {url}: {e}")
            return None

    def _extract_quest_data(self, soup: BeautifulSoup, url: str) -> Optional[QuestData]:
        """Extract quest data from parsed HTML content."""
        try:
            # Get page text content
            page_text = soup.get_text()
            
            # Extract basic quest information
            quest_id = self._extract_quest_id(url, page_text)
            name = self._extract_quest_name(soup, page_text)
            description = self._extract_description(soup, page_text)
            planet = self._extract_planet(soup, page_text)
            npc = self._extract_npc(soup, page_text)
            coordinates = self._extract_coordinates(soup, page_text)
            level_req = self._extract_level_requirement(page_text)
            difficulty = self._extract_difficulty(page_text)
            quest_type = self._determine_quest_type(page_text)
            
            # Extract complex data
            rewards = self._extract_rewards(soup, page_text)
            prerequisites = self._extract_prerequisites(soup, page_text)
            objectives = self._extract_objectives(soup, page_text)
            hints = self._extract_hints(soup, page_text)
            
            # Create quest data object
            quest_data = QuestData(
                quest_id=quest_id,
                name=name,
                description=description,
                quest_type=quest_type,
                difficulty=difficulty,
                level_requirement=level_req,
                planet=planet,
                npc=npc,
                coordinates=coordinates,
                rewards=rewards,
                prerequisites=prerequisites,
                objectives=objectives,
                hints=hints,
                source_url=url,
                last_updated=self._extract_last_updated(soup)
            )
            
            return quest_data
            
        except Exception as e:
            self.logger.error(f"Error extracting quest data: {e}")
            return None

    def _extract_quest_id(self, url: str, page_text: str) -> str:
        """Extract quest ID from URL or page content."""
        # Try to extract from URL first
        url_path = urlparse(url).path
        if '/quest/' in url_path:
            quest_part = url_path.split('/quest/')[-1]
            return quest_part.replace('/', '_').replace('-', '_')
        
        # Try to extract from page content
        match = re.search(self.wiki_patterns['quest_id'], page_text, re.IGNORECASE)
        if match:
            return match.group(1).strip().replace(' ', '_').lower()
        
        # Generate from name if available
        name_match = re.search(self.wiki_patterns['quest_name'], page_text, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip()
            return name.replace(' ', '_').lower()
        
        return "unknown_quest"

    def _extract_quest_name(self, soup: BeautifulSoup, page_text: str) -> str:
        """Extract quest name from page content."""
        # Try to get from page title first
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            if 'quest' in title.lower() or 'mission' in title.lower():
                return title
        
        # Try to extract from content
        match = re.search(self.wiki_patterns['quest_name'], page_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Try to find in headings
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            heading_text = heading.get_text().strip()
            if heading_text and len(heading_text) < 100:
                return heading_text
        
        return "Unknown Quest"

    def _extract_description(self, soup: BeautifulSoup, page_text: str) -> str:
        """Extract quest description from page content."""
        # Try to extract from content
        match = re.search(self.wiki_patterns['description'], page_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Try to find in paragraphs
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if text and len(text) > 20 and len(text) < 500:
                return text
        
        return ""

    def _extract_planet(self, soup: BeautifulSoup, page_text: str) -> str:
        """Extract planet information from page content."""
        # Try to extract from content
        match = re.search(self.wiki_patterns['planet'], page_text, re.IGNORECASE)
        if match:
            return match.group(1).strip().lower()
        
        # Try to find in navigation or breadcrumbs
        nav_links = soup.find_all('a', href=True)
        for link in nav_links:
            href = link.get('href', '')
            if any(planet in href.lower() for planet in ['tatooine', 'naboo', 'corellia', 'dantooine']):
                return link.get_text().strip().lower()
        
        return ""

    def _extract_npc(self, soup: BeautifulSoup, page_text: str) -> str:
        """Extract NPC information from page content."""
        # Try to extract from content
        match = re.search(self.wiki_patterns['npc'], page_text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Try to find NPC mentions in text
        npc_patterns = [
            r'quest giver[:\s]*([^\n\r]+)',
            r'npc[:\s]*([^\n\r]+)',
            r'contact[:\s]*([^\n\r]+)'
        ]
        
        for pattern in npc_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""

    def _extract_coordinates(self, soup: BeautifulSoup, page_text: str) -> Tuple[int, int]:
        """Extract coordinates from page content."""
        # Try to extract from content
        match = re.search(self.wiki_patterns['coordinates'], page_text, re.IGNORECASE)
        if match:
            try:
                x = int(match.group(1))
                y = int(match.group(2))
                return (x, y)
            except ValueError:
                pass
        
        return (0, 0)

    def _extract_level_requirement(self, page_text: str) -> int:
        """Extract level requirement from page content."""
        match = re.search(self.wiki_patterns['level_req'], page_text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        
        return 0

    def _extract_difficulty(self, page_text: str) -> QuestDifficulty:
        """Extract difficulty level from page content."""
        match = re.search(self.wiki_patterns['difficulty'], page_text, re.IGNORECASE)
        if match:
            difficulty = match.group(1).lower()
            try:
                return QuestDifficulty(difficulty)
            except ValueError:
                pass
        
        return QuestDifficulty.MEDIUM

    def _determine_quest_type(self, page_text: str) -> QuestType:
        """Determine quest type based on content analysis."""
        page_text_lower = page_text.lower()
        
        for quest_type, indicators in self.quest_type_indicators.items():
            for indicator in indicators:
                if indicator in page_text_lower:
                    return quest_type
        
        return QuestType.UNKNOWN

    def _extract_rewards(self, soup: BeautifulSoup, page_text: str) -> Dict[str, Any]:
        """Extract rewards from page content."""
        rewards = {}
        
        # Try to extract from content
        match = re.search(self.wiki_patterns['rewards'], page_text, re.IGNORECASE)
        if match:
            rewards_text = match.group(1).strip()
            
            # Parse common reward patterns
            if 'experience' in rewards_text.lower():
                exp_match = re.search(r'(\d+)\s*exp', rewards_text, re.IGNORECASE)
                if exp_match:
                    rewards['experience'] = int(exp_match.group(1))
            
            if 'credits' in rewards_text.lower():
                cred_match = re.search(r'(\d+)\s*credits?', rewards_text, re.IGNORECASE)
                if cred_match:
                    rewards['credits'] = int(cred_match.group(1))
        
        return rewards

    def _extract_prerequisites(self, soup: BeautifulSoup, page_text: str) -> List[str]:
        """Extract prerequisites from page content."""
        prerequisites = []
        
        # Try to extract from content
        match = re.search(self.wiki_patterns['prerequisites'], page_text, re.IGNORECASE)
        if match:
            prereq_text = match.group(1).strip()
            # Split by common delimiters
            prereqs = re.split(r'[,;]', prereq_text)
            prerequisites = [p.strip() for p in prereqs if p.strip()]
        
        return prerequisites

    def _extract_objectives(self, soup: BeautifulSoup, page_text: str) -> List[Dict[str, Any]]:
        """Extract objectives from page content."""
        objectives = []
        
        # Try to extract from content
        match = re.search(self.wiki_patterns['objectives'], page_text, re.IGNORECASE)
        if match:
            obj_text = match.group(1).strip()
            # Split objectives
            obj_list = re.split(r'[,;]', obj_text)
            for obj in obj_list:
                obj = obj.strip()
                if obj:
                    objectives.append({
                        'description': obj,
                        'type': 'unknown',
                        'completed': False
                    })
        
        return objectives

    def _extract_hints(self, soup: BeautifulSoup, page_text: str) -> List[str]:
        """Extract hints from page content."""
        hints = []
        
        # Try to extract from content
        match = re.search(self.wiki_patterns['hints'], page_text, re.IGNORECASE)
        if match:
            hints_text = match.group(1).strip()
            # Split hints
            hints_list = re.split(r'[,;]', hints_text)
            hints = [h.strip() for h in hints_list if h.strip()]
        
        return hints

    def _extract_last_updated(self, soup: BeautifulSoup) -> str:
        """Extract last updated timestamp from page."""
        # Look for common timestamp patterns
        timestamp_patterns = [
            r'last updated[:\s]*([^\n\r]+)',
            r'updated[:\s]*([^\n\r]+)',
            r'date[:\s]*([^\n\r]+)'
        ]
        
        page_text = soup.get_text()
        for pattern in timestamp_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""


def parse_wiki_page(url: str) -> Optional[QuestData]:
    """Parse a wiki page and extract quest data."""
    parser = WikiParser()
    return parser.parse_wiki_page(url)


def extract_quest_data(soup: BeautifulSoup, url: str) -> Optional[QuestData]:
    """Extract quest data from parsed HTML content."""
    parser = WikiParser()
    return parser._extract_quest_data(soup, url) 
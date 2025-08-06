"""
Wiki Quest Scraper + Profile Generator

This module provides functionality to automatically extract quest data from public SWG wikis
and generate YAML profiles for the MS11 quest system.
"""

import json
import logging
import re
import time
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse
import yaml

# Custom YAML representer for tuples
def tuple_representer(dumper, data):
    return dumper.represent_list(list(data))

yaml.add_representer(tuple, tuple_representer)

import requests
from bs4 import BeautifulSoup


class QuestType(Enum):
    """Types of quests available in SWG."""
    COMBAT = "combat"
    DELIVERY = "delivery"
    COLLECTION = "collection"
    FACTION = "faction"
    CRAFTING = "crafting"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    UNKNOWN = "unknown"


class QuestDifficulty(Enum):
    """Quest difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


@dataclass
class QuestData:
    """Represents extracted quest data."""
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


class WikiQuestScraper:
    """Scrapes quest data from SWG wikis and generates YAML profiles."""
    
    def __init__(self):
        """Initialize the quest scraper."""
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MS11-Quest-Scraper/1.0 (Educational Bot)'
        })
        
        # Wiki sources
        self.wiki_sources = {
            'swgr': 'https://swgr.org/wiki/',
            'fandom': 'https://swg.fandom.com/wiki/'
        }
        
        # Quest data storage
        self.quests: Dict[str, QuestData] = {}
        self.internal_index: Dict[str, Any] = {
            'planets': {},
            'quest_types': {},
            'last_updated': ''
        }
        
        # Create output directories
        self.output_dir = Path("data/quests")
        self.output_dir.mkdir(exist_ok=True)
        
        # Create planet subdirectories
        self.planets = [
            "tatooine", "naboo", "corellia", "dantooine", "lok", 
            "rori", "talus", "yavin4", "endor", "dathomir"
        ]
        for planet in self.planets:
            (self.output_dir / planet).mkdir(exist_ok=True)
    
    def scrape_swgr_wiki(self, category_url: str = None) -> List[QuestData]:
        """Scrape quest data from SWGR wiki.
        
        Parameters
        ----------
        category_url : str, optional
            URL to quest category page
            
        Returns
        -------
        List[QuestData]
            List of extracted quest data
        """
        if category_url is None:
            category_url = "https://swgr.org/wiki/Category:Quests"
        
        self.logger.info(f"Scraping SWGR wiki: {category_url}")
        
        try:
            response = self.session.get(category_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            quest_links = self._extract_quest_links(soup)
            
            quests = []
            for link in quest_links[:10]:  # Limit for testing
                try:
                    quest_data = self._scrape_quest_page(link)
                    if quest_data:
                        quests.append(quest_data)
                        self.logger.info(f"Scraped quest: {quest_data.name}")
                except Exception as e:
                    self.logger.error(f"Failed to scrape quest {link}: {e}")
                
                time.sleep(1)  # Be respectful to the server
            
            return quests
            
        except Exception as e:
            self.logger.error(f"Failed to scrape SWGR wiki: {e}")
            return []
    
    def scrape_fandom_wiki(self, category_url: str = None) -> List[QuestData]:
        """Scrape quest data from SWG Fandom wiki.
        
        Parameters
        ----------
        category_url : str, optional
            URL to quest category page
            
        Returns
        -------
        List[QuestData]
            List of extracted quest data
        """
        if category_url is None:
            category_url = "https://swg.fandom.com/wiki/Category:Quests"
        
        self.logger.info(f"Scraping Fandom wiki: {category_url}")
        
        try:
            response = self.session.get(category_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            quest_links = self._extract_quest_links(soup)
            
            quests = []
            for link in quest_links[:10]:  # Limit for testing
                try:
                    quest_data = self._scrape_quest_page(link)
                    if quest_data:
                        quests.append(quest_data)
                        self.logger.info(f"Scraped quest: {quest_data.name}")
                except Exception as e:
                    self.logger.error(f"Failed to scrape quest {link}: {e}")
                
                time.sleep(1)  # Be respectful to the server
            
            return quests
            
        except Exception as e:
            self.logger.error(f"Failed to scrape Fandom wiki: {e}")
            return []
    
    def _extract_quest_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract quest page links from category page.
        
        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML content
            
        Returns
        -------
        List[str]
            List of quest page URLs
        """
        links = []
        
        # Look for links in category pages
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'Quest' in link.text or 'quest' in href.lower():
                if href.startswith('/'):
                    href = urljoin(soup.base_url, href)
                links.append(href)
        
        return list(set(links))  # Remove duplicates
    
    def _scrape_quest_page(self, url: str) -> Optional[QuestData]:
        """Scrape individual quest page.
        
        Parameters
        ----------
        url : str
            Quest page URL
            
        Returns
        -------
        Optional[QuestData]
            Extracted quest data, or None if failed
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract quest information
            quest_id = self._extract_quest_id(url)
            name = self._extract_quest_name(soup)
            description = self._extract_quest_description(soup)
            quest_type = self._extract_quest_type(soup)
            planet = self._extract_planet(soup)
            npc = self._extract_npc(soup)
            coordinates = self._extract_coordinates(soup)
            rewards = self._extract_rewards(soup)
            dialogue = self._extract_dialogue(soup)
            prerequisites = self._extract_prerequisites(soup)
            
            if not name:
                return None
            
            quest_data = QuestData(
                quest_id=quest_id,
                name=name,
                description=description,
                quest_type=quest_type,
                planet=planet,
                npc=npc,
                coordinates=coordinates,
                rewards=rewards,
                dialogue=dialogue,
                prerequisites=prerequisites,
                source_url=url,
                last_updated=time.strftime("%Y-%m-%d")
            )
            
            return quest_data
            
        except Exception as e:
            self.logger.error(f"Failed to scrape quest page {url}: {e}")
            return None
    
    def _extract_quest_id(self, url: str) -> str:
        """Extract quest ID from URL.
        
        Parameters
        ----------
        url : str
            Quest page URL
            
        Returns
        -------
        str
            Quest ID
        """
        # Extract from URL path
        path = urlparse(url).path
        parts = path.split('/')
        
        if len(parts) > 1:
            quest_name = parts[-1]
            # Clean up the quest name
            quest_id = re.sub(r'[^a-zA-Z0-9_]', '_', quest_name.lower())
            return quest_id
        
        return f"quest_{hash(url) % 10000}"
    
    def _extract_quest_name(self, soup: BeautifulSoup) -> str:
        """Extract quest name from page.
        
        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML content
            
        Returns
        -------
        str
            Quest name
        """
        # Try to find the main title
        title = soup.find('h1')
        if title:
            return title.get_text().strip()
        
        # Try to find title in page metadata
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text()
            # Remove wiki name from title
            if ' - ' in title_text:
                return title_text.split(' - ')[0].strip()
            return title_text.strip()
        
        return ""
    
    def _extract_quest_description(self, soup: BeautifulSoup) -> str:
        """Extract quest description from page.
        
        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML content
            
        Returns
        -------
        str
            Quest description
        """
        # Look for description in infobox or first paragraph
        infobox = soup.find('table', class_='infobox')
        if infobox:
            desc_row = infobox.find('td', string=re.compile(r'description|summary', re.I))
            if desc_row and desc_row.find_next_sibling('td'):
                return desc_row.find_next_sibling('td').get_text().strip()
        
        # Look for first paragraph
        content = soup.find('div', id='content')
        if content:
            first_p = content.find('p')
            if first_p:
                return first_p.get_text().strip()
        
        return ""
    
    def _extract_quest_type(self, soup: BeautifulSoup) -> QuestType:
        """Extract quest type from page.
        
        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML content
            
        Returns
        -------
        QuestType
            Quest type
        """
        text = soup.get_text().lower()
        
        if any(word in text for word in ['combat', 'kill', 'attack', 'fight']):
            return QuestType.COMBAT
        elif any(word in text for word in ['delivery', 'deliver', 'transport']):
            return QuestType.DELIVERY
        elif any(word in text for word in ['collect', 'gather', 'find']):
            return QuestType.COLLECTION
        elif any(word in text for word in ['faction', 'imperial', 'rebel']):
            return QuestType.FACTION
        elif any(word in text for word in ['craft', 'build', 'create']):
            return QuestType.CRAFTING
        elif any(word in text for word in ['explore', 'discover', 'search']):
            return QuestType.EXPLORATION
        elif any(word in text for word in ['social', 'talk', 'conversation']):
            return QuestType.SOCIAL
        
        return QuestType.UNKNOWN
    
    def _extract_planet(self, soup: BeautifulSoup) -> str:
        """Extract planet from page.
        
        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML content
            
        Returns
        -------
        str
            Planet name
        """
        text = soup.get_text().lower()
        
        planets = {
            'tatooine': ['tatooine', 'mos eisley', 'anchorhead'],
            'naboo': ['naboo', 'theed', 'kaadara'],
            'corellia': ['corellia', 'coronet', 'tyrena'],
            'dantooine': ['dantooine', 'khoonda'],
            'lok': ['lok', 'nyms stronghold'],
            'rori': ['rori', 'narmle'],
            'talus': ['talus', 'dearic'],
            'yavin4': ['yavin4', 'yavin 4'],
            'endor': ['endor'],
            'dathomir': ['dathomir']
        }
        
        for planet, keywords in planets.items():
            if any(keyword in text for keyword in keywords):
                return planet
        
        return ""
    
    def _extract_npc(self, soup: BeautifulSoup) -> str:
        """Extract NPC from page.
        
        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML content
            
        Returns
        -------
        str
            NPC name
        """
        # Look for NPC mentions in text
        text = soup.get_text()
        
        # Common NPC patterns
        npc_patterns = [
            r'Quest Giver:\s*([^\n]+)',
            r'NPC:\s*([^\n]+)',
            r'Start NPC:\s*([^\n]+)',
            r'([A-Z][a-z]+ [A-Z][a-z]+)\s*\(NPC\)',
        ]
        
        for pattern in npc_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_coordinates(self, soup: BeautifulSoup) -> Tuple[int, int]:
        """Extract coordinates from page.
        
        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML content
            
        Returns
        -------
        Tuple[int, int]
            Coordinates (x, y)
        """
        text = soup.get_text()
        
        # Look for coordinate patterns
        coord_patterns = [
            r'coordinates?:\s*([-\d]+),\s*([-\d]+)',
            r'location:\s*([-\d]+),\s*([-\d]+)',
            r'\(([-\d]+),\s*([-\d]+)\)',
        ]
        
        for pattern in coord_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    x = int(match.group(1))
                    y = int(match.group(2))
                    return (x, y)
                except ValueError:
                    continue
        
        return (0, 0)
    
    def _extract_rewards(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract rewards from page.
        
        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML content
            
        Returns
        -------
        Dict[str, Any]
            Rewards dictionary
        """
        rewards = {}
        text = soup.get_text().lower()
        
        # Extract credits
        credit_match = re.search(r'(\d+)\s*credits?', text)
        if credit_match:
            rewards['credits'] = int(credit_match.group(1))
        
        # Extract experience
        exp_match = re.search(r'(\d+)\s*experience', text)
        if exp_match:
            rewards['experience'] = int(exp_match.group(1))
        
        # Extract items
        items = []
        item_patterns = [
            r'reward.*?([a-zA-Z\s]+)',
            r'item.*?([a-zA-Z\s]+)',
            r'items?:\s*([a-zA-Z\s,]+)',
        ]
        
        for pattern in item_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Split by comma and clean up
                item_list = [item.strip() for item in match.split(',') if len(item.strip()) > 3]
                items.extend(item_list)
        
        if items:
            rewards['items'] = list(set(items))
        
        return rewards
    
    def _extract_dialogue(self, soup: BeautifulSoup) -> List[str]:
        """Extract dialogue from page.
        
        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML content
            
        Returns
        -------
        List[str]
            List of dialogue lines
        """
        dialogue = []
        text = soup.get_text()
        
        # Look for dialogue patterns
        dialogue_patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'Dialogue:\s*([^\n]+)',
        ]
        
        for pattern in dialogue_patterns:
            matches = re.findall(pattern, text)
            dialogue.extend([line.strip() for line in matches if len(line.strip()) > 10])
        
        return dialogue[:5]  # Limit to 5 dialogue lines
    
    def _extract_prerequisites(self, soup: BeautifulSoup) -> List[str]:
        """Extract prerequisites from page.
        
        Parameters
        ----------
        soup : BeautifulSoup
            Parsed HTML content
            
        Returns
        -------
        List[str]
            List of prerequisites
        """
        prerequisites = []
        text = soup.get_text().lower()
        
        # Look for prerequisite patterns
        prereq_patterns = [
            r'prerequisite.*?([a-zA-Z\s]+)',
            r'requirement.*?([a-zA-Z\s]+)',
            r'level\s*(\d+)',
        ]
        
        for pattern in prereq_patterns:
            matches = re.findall(pattern, text)
            prerequisites.extend([prereq.strip() for prereq in matches if len(prereq.strip()) > 3])
        
        return list(set(prerequisites))
    
    def generate_yaml_profile(self, quest_data: QuestData) -> str:
        """Generate YAML profile for quest data.
        
        Parameters
        ----------
        quest_data : QuestData
            Quest data to convert
            
        Returns
        -------
        str
            YAML string representation
        """
        if quest_data is None:
            raise ValueError("Quest data cannot be None")
            
        # Convert to dictionary
        quest_dict = asdict(quest_data)
        
        # Convert enums to strings
        quest_dict['quest_type'] = quest_dict['quest_type'].value
        quest_dict['difficulty'] = quest_dict['difficulty'].value
        
        # Convert tuple coordinates to list
        if isinstance(quest_dict.get('coordinates'), tuple):
            quest_dict['coordinates'] = list(quest_dict['coordinates'])
        
        # Add default structure
        if not quest_dict.get('steps'):
            quest_dict['steps'] = [
                {
                    'step_id': 'start_quest',
                    'type': 'dialogue',
                    'npc_id': quest_dict.get('npc', 'quest_giver'),
                    'coordinates': quest_dict.get('coordinates', [0, 0]),
                    'description': 'Start the quest'
                }
            ]
        
        if not quest_dict.get('completion_conditions'):
            quest_dict['completion_conditions'] = [
                {
                    'type': 'dialogue',
                    'npc_id': quest_dict.get('npc', 'quest_giver'),
                    'description': 'Complete the quest'
                }
            ]
        
        if not quest_dict.get('metadata'):
            quest_dict['metadata'] = {
                'created_date': time.strftime("%Y-%m-%d"),
                'last_updated': time.strftime("%Y-%m-%d"),
                'version': '1.0',
                'author': 'MS11_Quest_Scraper',
                'source_url': quest_dict.get('source_url', ''),
                'tags': [quest_dict.get('planet', ''), quest_dict.get('quest_type', '')]
            }
        
        # Generate YAML without anchors
        yaml_content = yaml.dump(quest_dict, default_flow_style=False, sort_keys=False, default_style=None)
        
        return yaml_content
    
    def save_quest_profile(self, quest_data: QuestData) -> bool:
        """Save quest profile to YAML file.
        
        Parameters
        ----------
        quest_data : QuestData
            Quest data to save
            
        Returns
        -------
        bool
            True if saved successfully
        """
        if quest_data is None:
            self.logger.error("Cannot save None quest data")
            return False
            
        try:
            # Generate YAML content
            yaml_content = self.generate_yaml_profile(quest_data)
            
            # Determine file path
            planet = quest_data.planet or 'unknown'
            filename = f"{quest_data.quest_id}.yaml"
            file_path = self.output_dir / planet / filename
            
            # Save file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            self.logger.info(f"Saved quest profile: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save quest profile: {e}")
            return False
    
    def update_internal_index(self, quest_data: QuestData):
        """Update internal index with quest data.
        
        Parameters
        ----------
        quest_data : QuestData
            Quest data to index
        """
        planet = quest_data.planet or 'unknown'
        quest_type = quest_data.quest_type.value
        
        # Initialize planet entry
        if planet not in self.internal_index['planets']:
            self.internal_index['planets'][planet] = {
                'quests': {},
                'quest_types': {}
            }
        
        # Add quest to planet
        self.internal_index['planets'][planet]['quests'][quest_data.quest_id] = {
            'name': quest_data.name,
            'type': quest_type,
            'difficulty': quest_data.difficulty.value,
            'level_requirement': quest_data.level_requirement,
            'coordinates': quest_data.coordinates,
            'npc': quest_data.npc,
            'file_path': f"{planet}/{quest_data.quest_id}.yaml"
        }
        
        # Add quest type to planet
        if quest_type not in self.internal_index['planets'][planet]['quest_types']:
            self.internal_index['planets'][planet]['quest_types'][quest_type] = []
        
        self.internal_index['planets'][planet]['quest_types'][quest_type].append(quest_data.quest_id)
        
        # Update global quest types
        if quest_type not in self.internal_index['quest_types']:
            self.internal_index['quest_types'][quest_type] = []
        
        self.internal_index['quest_types'][quest_type].append(quest_data.quest_id)
    
    def save_internal_index(self):
        """Save internal index to YAML file."""
        try:
            self.internal_index['last_updated'] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            index_path = Path("data/internal_index.yaml")
            with open(index_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.internal_index, f, default_flow_style=False, sort_keys=False)
            
            self.logger.info(f"Saved internal index: {index_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save internal index: {e}")
    
    def scrape_all_wikis(self) -> List[QuestData]:
        """Scrape quest data from all available wikis.
        
        Returns
        -------
        List[QuestData]
            List of all extracted quest data
        """
        all_quests = []
        
        # Scrape SWGR wiki
        swgr_quests = self.scrape_swgr_wiki()
        all_quests.extend(swgr_quests)
        
        # Scrape Fandom wiki
        fandom_quests = self.scrape_fandom_wiki()
        all_quests.extend(fandom_quests)
        
        # Process and save quests
        for quest_data in all_quests:
            if self.save_quest_profile(quest_data):
                self.update_internal_index(quest_data)
        
        # Save internal index
        self.save_internal_index()
        
        self.logger.info(f"Scraped {len(all_quests)} quests total")
        return all_quests


# Global instance
_quest_scraper: Optional[WikiQuestScraper] = None


def get_quest_scraper() -> WikiQuestScraper:
    """Get the global quest scraper instance."""
    global _quest_scraper
    if _quest_scraper is None:
        _quest_scraper = WikiQuestScraper()
    return _quest_scraper


def scrape_quests_from_wikis() -> List[QuestData]:
    """Scrape quests from all available wikis."""
    scraper = get_quest_scraper()
    return scraper.scrape_all_wikis()


def generate_quest_profile(quest_data: QuestData) -> str:
    """Generate YAML profile for quest data."""
    scraper = get_quest_scraper()
    return scraper.generate_yaml_profile(quest_data)


def save_quest_profile(quest_data: QuestData) -> bool:
    """Save quest profile to YAML file."""
    scraper = get_quest_scraper()
    return scraper.save_quest_profile(quest_data) 
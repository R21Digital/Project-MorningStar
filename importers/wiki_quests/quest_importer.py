#!/usr/bin/env python3
"""Quest Importer Module for Batch 042.

This module provides functionality to import quest data from wiki pages and store
NPCs, objectives, prerequisites, and rewards into data/quests/ directory.
"""

import json
import logging
import yaml
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from .wiki_parser import WikiParser, QuestData, QuestType, QuestDifficulty


class QuestImporter:
    """Imports quest data from wiki pages and stores in local database."""
    
    def __init__(self):
        """Initialize the quest importer."""
        self.logger = logging.getLogger(__name__)
        self.parser = WikiParser()
        
        # Data directories
        self.data_dir = Path("data")
        self.quests_dir = self.data_dir / "quests"
        self.quests_dir.mkdir(exist_ok=True)
        
        # Database files
        self.quest_db_file = self.data_dir / "quest_database.json"
        self.quest_index_file = self.data_dir / "quest_index.yaml"
        
        # Load existing database
        self.quest_database = self._load_quest_database()
        self.quest_index = self._load_quest_index()
        
        # Import statistics
        self.stats = {
            'total_imported': 0,
            'total_updated': 0,
            'total_failed': 0,
            'last_import': None
        }

    def import_quests_from_wiki(self, wiki_urls: List[str], category_urls: List[str] = None) -> Dict[str, Any]:
        """Import quests from wiki pages and category pages."""
        self.logger.info(f"Starting quest import from {len(wiki_urls)} URLs")
        
        imported_quests = []
        failed_urls = []
        
        # Import from direct URLs
        for url in wiki_urls:
            try:
                quest_data = self.parser.parse_wiki_page(url)
                if quest_data:
                    success = self._save_quest_data(quest_data)
                    if success:
                        imported_quests.append(quest_data)
                        self.stats['total_imported'] += 1
                    else:
                        failed_urls.append(url)
                        self.stats['total_failed'] += 1
                else:
                    failed_urls.append(url)
                    self.stats['total_failed'] += 1
            except Exception as e:
                self.logger.error(f"Error importing quest from {url}: {e}")
                failed_urls.append(url)
                self.stats['total_failed'] += 1
        
        # Import from category pages
        if category_urls:
            for category_url in category_urls:
                try:
                    category_quests = self._import_from_category(category_url)
                    imported_quests.extend(category_quests)
                except Exception as e:
                    self.logger.error(f"Error importing from category {category_url}: {e}")
        
        # Update statistics
        self.stats['last_import'] = datetime.now().isoformat()
        
        # Save updated database
        self._save_quest_database()
        self._save_quest_index()
        
        self.logger.info(f"Import completed: {len(imported_quests)} imported, {len(failed_urls)} failed")
        
        return {
            'imported_quests': len(imported_quests),
            'failed_urls': len(failed_urls),
            'total_quests': len(self.quest_database),
            'stats': self.stats
        }

    def _import_from_category(self, category_url: str) -> List[QuestData]:
        """Import quests from a category page."""
        self.logger.info(f"Importing quests from category: {category_url}")
        
        try:
            response = self.parser.session.get(category_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            quest_links = self._extract_quest_links(soup, category_url)
            
            imported_quests = []
            for link in quest_links:
                try:
                    quest_data = self.parser.parse_wiki_page(link)
                    if quest_data:
                        success = self._save_quest_data(quest_data)
                        if success:
                            imported_quests.append(quest_data)
                            self.stats['total_imported'] += 1
                        else:
                            self.stats['total_failed'] += 1
                    else:
                        self.stats['total_failed'] += 1
                except Exception as e:
                    self.logger.error(f"Error importing quest from {link}: {e}")
                    self.stats['total_failed'] += 1
            
            return imported_quests
            
        except Exception as e:
            self.logger.error(f"Error importing from category {category_url}: {e}")
            return []

    def _extract_quest_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract quest links from a category page."""
        quest_links = []
        
        # Look for links that might be quest pages
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text().strip().lower()
            
            # Check if link looks like a quest
            if any(keyword in href.lower() or keyword in text for keyword in [
                'quest', 'mission', 'task', 'objective', 'legacy', 'theme_park'
            ]):
                full_url = urljoin(base_url, href)
                quest_links.append(full_url)
        
        return quest_links

    def _save_quest_data(self, quest_data: QuestData) -> bool:
        """Save quest data to the appropriate location."""
        try:
            # Create quest file path
            quest_file = self._get_quest_file_path(quest_data)
            quest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert quest data to YAML format
            quest_yaml = self._convert_to_yaml(quest_data)
            
            # Save quest file
            with open(quest_file, 'w', encoding='utf-8') as f:
                f.write(quest_yaml)
            
            # Update database
            self._update_quest_database(quest_data)
            
            # Update index
            self._update_quest_index(quest_data)
            
            self.logger.info(f"Saved quest: {quest_data.name} to {quest_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving quest data: {e}")
            return False

    def _get_quest_file_path(self, quest_data: QuestData) -> Path:
        """Get the file path for a quest based on its data."""
        # Determine planet directory
        planet = quest_data.planet.lower() if quest_data.planet else "unknown"
        planet_dir = self.quests_dir / planet
        
        # Create filename
        quest_id = quest_data.quest_id.replace(' ', '_').lower()
        filename = f"{quest_id}.yaml"
        
        return planet_dir / filename

    def _convert_to_yaml(self, quest_data: QuestData) -> str:
        """Convert quest data to YAML format."""
        # Convert enum values to strings
        quest_dict = {
            'quest_id': quest_data.quest_id,
            'name': quest_data.name,
            'description': quest_data.description,
            'quest_type': quest_data.quest_type.value,
            'difficulty': quest_data.difficulty.value,
            'level_requirement': quest_data.level_requirement,
            'planet': quest_data.planet,
            'zone': quest_data.zone,
            'coordinates': list(quest_data.coordinates),
            'npc': quest_data.npc,
            'rewards': quest_data.rewards,
            'prerequisites': quest_data.prerequisites,
            'objectives': quest_data.objectives,
            'dialogue': quest_data.dialogue,
            'steps': quest_data.steps,
            'completion_conditions': quest_data.completion_conditions,
            'failure_conditions': quest_data.failure_conditions,
            'hints': quest_data.hints,
            'metadata': {
                **quest_data.metadata,
                'source_url': quest_data.source_url,
                'last_updated': quest_data.last_updated,
                'imported_date': datetime.now().isoformat(),
                'imported_by': 'wiki_quest_importer'
            }
        }
        
        # Add YAML header
        yaml_content = f"""# Quest Data imported from SWGR Wiki
# Quest ID: {quest_data.quest_id}
# Imported: {datetime.now().isoformat()}
# Source: {quest_data.source_url}

"""
        
        # Convert to YAML
        yaml_content += yaml.dump(quest_dict, default_flow_style=False, allow_unicode=True)
        
        return yaml_content

    def _update_quest_database(self, quest_data: QuestData):
        """Update the quest database with new quest data."""
        quest_entry = {
            'quest_id': quest_data.quest_id,
            'name': quest_data.name,
            'planet': quest_data.planet,
            'quest_type': quest_data.quest_type.value,
            'difficulty': quest_data.difficulty.value,
            'level_requirement': quest_data.level_requirement,
            'source_url': quest_data.source_url,
            'imported_date': datetime.now().isoformat(),
            'file_path': str(self._get_quest_file_path(quest_data))
        }
        
        self.quest_database[quest_data.quest_id] = quest_entry

    def _update_quest_index(self, quest_data: QuestData):
        """Update the quest index with new quest data."""
        # Add to planet index
        planet = quest_data.planet.lower() if quest_data.planet else "unknown"
        if planet not in self.quest_index:
            self.quest_index[planet] = []
        
        quest_entry = {
            'quest_id': quest_data.quest_id,
            'name': quest_data.name,
            'quest_type': quest_data.quest_type.value,
            'difficulty': quest_data.difficulty.value,
            'level_requirement': quest_data.level_requirement,
            'file_path': str(self._get_quest_file_path(quest_data))
        }
        
        # Check if quest already exists
        existing_quests = [q for q in self.quest_index[planet] if q['quest_id'] == quest_data.quest_id]
        if existing_quests:
            # Update existing entry
            for quest in existing_quests:
                quest.update(quest_entry)
        else:
            # Add new entry
            self.quest_index[planet].append(quest_entry)

    def _load_quest_database(self) -> Dict[str, Any]:
        """Load the quest database from file."""
        if self.quest_db_file.exists():
            try:
                with open(self.quest_db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading quest database: {e}")
        
        return {}

    def _save_quest_database(self):
        """Save the quest database to file."""
        try:
            with open(self.quest_db_file, 'w', encoding='utf-8') as f:
                json.dump(self.quest_database, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving quest database: {e}")

    def _load_quest_index(self) -> Dict[str, Any]:
        """Load the quest index from file."""
        if self.quest_index_file.exists():
            try:
                with open(self.quest_index_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                self.logger.error(f"Error loading quest index: {e}")
        
        return {}

    def _save_quest_index(self):
        """Save the quest index to file."""
        try:
            with open(self.quest_index_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.quest_index, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            self.logger.error(f"Error saving quest index: {e}")

    def update_quest_database(self, force_update: bool = False) -> Dict[str, Any]:
        """Update the quest database by re-importing all quests."""
        self.logger.info("Starting quest database update")
        
        # Get all quest URLs from database
        quest_urls = []
        for quest_id, quest_data in self.quest_database.items():
            if 'source_url' in quest_data:
                quest_urls.append(quest_data['source_url'])
        
        if not quest_urls:
            self.logger.warning("No quest URLs found in database for update")
            return {'updated': 0, 'failed': 0}
        
        # Re-import quests
        result = self.import_quests_from_wiki(quest_urls)
        result['updated'] = result['imported_quests']
        result['imported_quests'] = 0  # Reset for update operation
        
        self.logger.info(f"Database update completed: {result['updated']} updated")
        return result

    def get_import_stats(self) -> Dict[str, Any]:
        """Get import statistics."""
        return {
            'stats': self.stats,
            'total_quests': len(self.quest_database),
            'quests_by_planet': {planet: len(quests) for planet, quests in self.quest_index.items()},
            'quests_by_type': self._get_quests_by_type()
        }

    def _get_quests_by_type(self) -> Dict[str, int]:
        """Get count of quests by type."""
        type_counts = {}
        for quest_data in self.quest_database.values():
            quest_type = quest_data.get('quest_type', 'unknown')
            type_counts[quest_type] = type_counts.get(quest_type, 0) + 1
        return type_counts


def import_quests_from_wiki(wiki_urls: List[str], category_urls: List[str] = None) -> Dict[str, Any]:
    """Import quests from wiki pages."""
    importer = QuestImporter()
    return importer.import_quests_from_wiki(wiki_urls, category_urls)


def update_quest_database(force_update: bool = False) -> Dict[str, Any]:
    """Update the quest database."""
    importer = QuestImporter()
    return importer.update_quest_database(force_update) 
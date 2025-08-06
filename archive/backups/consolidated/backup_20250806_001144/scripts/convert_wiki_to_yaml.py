#!/usr/bin/env python3
"""
Wiki to YAML/JSON Converter
Automates conversion from scraped SWGR.org and Fandom data to structured YAML/JSON files.
"""

import json
import yaml
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WikiQuest:
    """Represents a quest from wiki data."""
    title: str
    description: str
    level_requirement: int
    planet: str
    zone: str
    coordinates: List[int]
    rewards: Dict[str, Any]
    steps: List[Dict[str, Any]]
    prerequisites: List[str]
    quest_chain: Optional[str] = None


@dataclass
class WikiTrainer:
    """Represents a trainer from wiki data."""
    name: str
    profession: str
    planet: str
    zone: str
    coordinates: List[int]
    level_requirement: int
    skills_taught: List[str]
    training_cost: Dict[str, Any]


@dataclass
class WikiCollection:
    """Represents a collection from wiki data."""
    name: str
    description: str
    planet: str
    zones: List[str]
    items: List[Dict[str, Any]]
    completion_rewards: Dict[str, Any]


class WikiConverter:
    """
    Converts scraped wiki data to structured YAML/JSON format.
    
    Supports various input formats:
    - HTML scraped from SWGR.org
    - JSON from Fandom API
    - Plain text with regex patterns
    """
    
    def __init__(self, output_dir: str = "data"):
        """
        Initialize the converter.
        
        Args:
            output_dir: Directory to save converted files
        """
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger("wiki_converter")
        self._setup_logging()
        
        # Create output directories
        (self.output_dir / "quests").mkdir(exist_ok=True)
        (self.output_dir / "trainers").mkdir(exist_ok=True)
        (self.output_dir / "collections").mkdir(exist_ok=True)
        (self.output_dir / "dialogue").mkdir(exist_ok=True)
    
    def _setup_logging(self):
        """Set up logging for the converter."""
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def parse_html_quest(self, html_content: str) -> Optional[WikiQuest]:
        """
        Parse quest data from HTML content.
        
        Args:
            html_content: HTML content from SWGR.org
            
        Returns:
            WikiQuest object or None if parsing failed
        """
        try:
            # Extract quest information using regex patterns
            title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content)
            description_match = re.search(r'<div class="description">(.*?)</div>', html_content)
            level_match = re.search(r'Level Requirement:\s*(\d+)', html_content)
            planet_match = re.search(r'Planet:\s*([A-Za-z]+)', html_content)
            
            if not all([title_match, level_match, planet_match]):
                self.logger.warning("Missing required quest fields in HTML")
                return None
            
            title = title_match.group(1).strip()
            description = description_match.group(1).strip() if description_match else ""
            level_requirement = int(level_match.group(1))
            planet = planet_match.group(1).lower()
            
            # Extract coordinates (default if not found)
            coords_match = re.search(r'Coordinates:\s*\[(\d+),\s*(\d+)\]', html_content)
            coordinates = [int(coords_match.group(1)), int(coords_match.group(2))] if coords_match else [0, 0]
            
            # Extract rewards
            rewards = self._extract_rewards_from_html(html_content)
            
            # Extract steps
            steps = self._extract_steps_from_html(html_content)
            
            # Extract prerequisites
            prerequisites = self._extract_prerequisites_from_html(html_content)
            
            return WikiQuest(
                title=title,
                description=description,
                level_requirement=level_requirement,
                planet=planet,
                zone="unknown",  # Default zone
                coordinates=coordinates,
                rewards=rewards,
                steps=steps,
                prerequisites=prerequisites
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML quest: {e}")
            return None
    
    def parse_json_quest(self, json_data: Dict[str, Any]) -> Optional[WikiQuest]:
        """
        Parse quest data from JSON content.
        
        Args:
            json_data: JSON data from Fandom API
            
        Returns:
            WikiQuest object or None if parsing failed
        """
        try:
            # Handle different JSON structures
            if 'quest' in json_data:
                quest_data = json_data['quest']
            elif 'data' in json_data:
                quest_data = json_data['data']
            else:
                quest_data = json_data
            
            title = quest_data.get('title', 'Unknown Quest')
            description = quest_data.get('description', '')
            level_requirement = quest_data.get('level_requirement', 1)
            planet = quest_data.get('planet', 'unknown').lower()
            zone = quest_data.get('zone', 'unknown')
            
            # Extract coordinates
            coords = quest_data.get('coordinates', [0, 0])
            coordinates = coords if isinstance(coords, list) else [0, 0]
            
            # Extract rewards
            rewards = quest_data.get('rewards', {})
            
            # Extract steps
            steps = quest_data.get('steps', [])
            
            # Extract prerequisites
            prerequisites = quest_data.get('prerequisites', [])
            
            return WikiQuest(
                title=title,
                description=description,
                level_requirement=level_requirement,
                planet=planet,
                zone=zone,
                coordinates=coordinates,
                rewards=rewards,
                steps=steps,
                prerequisites=prerequisites,
                quest_chain=quest_data.get('quest_chain')
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON quest: {e}")
            return None
    
    def parse_html_trainer(self, html_content: str) -> Optional[WikiTrainer]:
        """
        Parse trainer data from HTML content.
        
        Args:
            html_content: HTML content from SWGR.org
            
        Returns:
            WikiTrainer object or None if parsing failed
        """
        try:
            # Extract trainer information
            name_match = re.search(r'<h2[^>]*>(.*?)</h2>', html_content)
            profession_match = re.search(r'Profession:\s*([A-Za-z]+)', html_content)
            planet_match = re.search(r'Planet:\s*([A-Za-z]+)', html_content)
            level_match = re.search(r'Level Requirement:\s*(\d+)', html_content)
            
            if not all([name_match, profession_match, planet_match, level_match]):
                self.logger.warning("Missing required trainer fields in HTML")
                return None
            
            name = name_match.group(1).strip()
            profession = profession_match.group(1).lower()
            planet = planet_match.group(1).lower()
            level_requirement = int(level_match.group(1))
            
            # Extract coordinates
            coords_match = re.search(r'Coordinates:\s*\[(\d+),\s*(\d+)\]', html_content)
            coordinates = [int(coords_match.group(1)), int(coords_match.group(2))] if coords_match else [0, 0]
            
            # Extract skills taught
            skills_match = re.search(r'Skills Taught:\s*(.*?)(?:\n|$)', html_content)
            skills_taught = [s.strip() for s in skills_match.group(1).split(',')] if skills_match else []
            
            # Extract training cost
            training_cost = self._extract_training_cost_from_html(html_content)
            
            return WikiTrainer(
                name=name,
                profession=profession,
                planet=planet,
                zone="unknown",  # Default zone
                coordinates=coordinates,
                level_requirement=level_requirement,
                skills_taught=skills_taught,
                training_cost=training_cost
            )
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML trainer: {e}")
            return None
    
    def _extract_rewards_from_html(self, html_content: str) -> Dict[str, Any]:
        """Extract rewards from HTML content."""
        rewards = {}
        
        # Extract experience
        exp_match = re.search(r'Experience:\s*(\d+)', html_content)
        if exp_match:
            rewards['experience'] = int(exp_match.group(1))
        
        # Extract credits
        credits_match = re.search(r'Credits:\s*(\d+)', html_content)
        if credits_match:
            rewards['credits'] = int(credits_match.group(1))
        
        # Extract items
        items_match = re.search(r'Items:\s*(.*?)(?:\n|$)', html_content)
        if items_match:
            items_text = items_match.group(1)
            rewards['items'] = [item.strip() for item in items_text.split(',')]
        
        return rewards
    
    def _extract_steps_from_html(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract quest steps from HTML content."""
        steps = []
        
        # Look for step patterns
        step_pattern = r'<div class="step">(.*?)</div>'
        step_matches = re.findall(step_pattern, html_content, re.DOTALL)
        
        for i, step_content in enumerate(step_matches):
            step = {
                'step_id': f'step_{i+1}',
                'type': 'unknown',
                'description': step_content.strip()
            }
            steps.append(step)
        
        return steps
    
    def _extract_prerequisites_from_html(self, html_content: str) -> List[str]:
        """Extract prerequisites from HTML content."""
        prereq_match = re.search(r'Prerequisites:\s*(.*?)(?:\n|$)', html_content)
        if prereq_match:
            prereq_text = prereq_match.group(1)
            return [prereq.strip() for prereq in prereq_text.split(',')]
        return []
    
    def _extract_training_cost_from_html(self, html_content: str) -> Dict[str, Any]:
        """Extract training cost from HTML content."""
        cost = {}
        
        credits_match = re.search(r'Training Cost:\s*(\d+)\s*credits', html_content)
        if credits_match:
            cost['credits'] = int(credits_match.group(1))
        
        reputation_match = re.search(r'Reputation:\s*(\d+)', html_content)
        if reputation_match:
            cost['reputation'] = int(reputation_match.group(1))
        
        return cost
    
    def convert_quest_to_yaml(self, quest: WikiQuest) -> str:
        """
        Convert WikiQuest to YAML format.
        
        Args:
            quest: WikiQuest object
            
        Returns:
            YAML string representation
        """
        quest_data = {
            'quest_id': self._generate_quest_id(quest.title),
            'name': quest.title,
            'description': quest.description,
            'quest_type': 'unknown',
            'difficulty': 'medium',
            'level_requirement': quest.level_requirement,
            'planet': quest.planet,
            'zone': quest.zone,
            'coordinates': quest.coordinates,
            'quest_chain': quest.quest_chain,
            'prerequisites': quest.prerequisites,
            'rewards': quest.rewards,
            'steps': quest.steps,
            'completion_conditions': [],
            'failure_conditions': [],
            'hints': [],
            'metadata': {
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'version': '1.0',
                'author': 'Wiki_Converter',
                'source': 'SWGR.org'
            }
        }
        
        return yaml.dump(quest_data, default_flow_style=False, sort_keys=False)
    
    def convert_trainer_to_json(self, trainer: WikiTrainer) -> str:
        """
        Convert WikiTrainer to JSON format.
        
        Args:
            trainer: WikiTrainer object
            
        Returns:
            JSON string representation
        """
        trainer_data = {
            'trainer_id': self._generate_trainer_id(trainer.name),
            'name': trainer.name,
            'profession': trainer.profession,
            'planet': trainer.planet,
            'zone': trainer.zone,
            'coordinates': trainer.coordinates,
            'level_requirement': trainer.level_requirement,
            'reputation_requirement': {},
            'skills_taught': trainer.skills_taught,
            'max_skill_level': 4,
            'training_cost': trainer.training_cost,
            'schedule': {
                'available_hours': [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                'rest_days': []
            },
            'dialogue_options': [
                f"Learn {trainer.profession} skills",
                "Ask about advanced techniques",
                "Leave"
            ],
            'metadata': {
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'version': '1.0'
            }
        }
        
        return json.dumps(trainer_data, indent=2)
    
    def _generate_quest_id(self, title: str) -> str:
        """Generate a quest ID from title."""
        return re.sub(r'[^a-zA-Z0-9]', '_', title.lower()).strip('_')
    
    def _generate_trainer_id(self, name: str) -> str:
        """Generate a trainer ID from name."""
        return re.sub(r'[^a-zA-Z0-9]', '_', name.lower()).strip('_')
    
    def save_quest(self, quest: WikiQuest, filename: Optional[str] = None) -> str:
        """
        Save quest to YAML file.
        
        Args:
            quest: WikiQuest object
            filename: Optional filename, auto-generated if not provided
            
        Returns:
            Path to saved file
        """
        if filename is None:
            quest_id = self._generate_quest_id(quest.title)
            filename = f"{quest_id}.yaml"
        
        filepath = self.output_dir / "quests" / filename
        yaml_content = self.convert_quest_to_yaml(quest)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        self.logger.info(f"Saved quest to {filepath}")
        return str(filepath)
    
    def save_trainer(self, trainer: WikiTrainer, filename: Optional[str] = None) -> str:
        """
        Save trainer to JSON file.
        
        Args:
            trainer: WikiTrainer object
            filename: Optional filename, auto-generated if not provided
            
        Returns:
            Path to saved file
        """
        if filename is None:
            trainer_id = self._generate_trainer_id(trainer.name)
            filename = f"{trainer_id}.json"
        
        filepath = self.output_dir / "trainers" / filename
        json_content = self.convert_trainer_to_json(trainer)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_content)
        
        self.logger.info(f"Saved trainer to {filepath}")
        return str(filepath)
    
    def batch_convert_html(self, html_files: List[str]) -> Dict[str, int]:
        """
        Batch convert HTML files to YAML/JSON.
        
        Args:
            html_files: List of HTML file paths
            
        Returns:
            Dictionary with conversion statistics
        """
        stats = {'quests_converted': 0, 'trainers_converted': 0, 'errors': 0}
        
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Try to parse as quest
                quest = self.parse_html_quest(html_content)
                if quest:
                    self.save_quest(quest)
                    stats['quests_converted'] += 1
                    continue
                
                # Try to parse as trainer
                trainer = self.parse_html_trainer(html_content)
                if trainer:
                    self.save_trainer(trainer)
                    stats['trainers_converted'] += 1
                    continue
                
                self.logger.warning(f"Could not parse {html_file} as quest or trainer")
                stats['errors'] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing {html_file}: {e}")
                stats['errors'] += 1
        
        return stats
    
    def batch_convert_json(self, json_files: List[str]) -> Dict[str, int]:
        """
        Batch convert JSON files to YAML/JSON.
        
        Args:
            json_files: List of JSON file paths
            
        Returns:
            Dictionary with conversion statistics
        """
        stats = {'quests_converted': 0, 'trainers_converted': 0, 'errors': 0}
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # Try to parse as quest
                quest = self.parse_json_quest(json_data)
                if quest:
                    self.save_quest(quest)
                    stats['quests_converted'] += 1
                    continue
                
                self.logger.warning(f"Could not parse {json_file} as quest")
                stats['errors'] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing {json_file}: {e}")
                stats['errors'] += 1
        
        return stats


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert wiki data to YAML/JSON format')
    parser.add_argument('input_files', nargs='+', help='Input HTML or JSON files')
    parser.add_argument('--output-dir', default='data', help='Output directory')
    parser.add_argument('--format', choices=['html', 'json'], help='Input format')
    
    args = parser.parse_args()
    
    converter = WikiConverter(args.output_dir)
    
    if args.format == 'html' or any(f.endswith('.html') for f in args.input_files):
        stats = converter.batch_convert_html(args.input_files)
    elif args.format == 'json' or any(f.endswith('.json') for f in args.input_files):
        stats = converter.batch_convert_json(args.input_files)
    else:
        print("Could not determine input format. Please specify --format")
        return
    
    print(f"Conversion complete!")
    print(f"Quests converted: {stats['quests_converted']}")
    print(f"Trainers converted: {stats['trainers_converted']}")
    print(f"Errors: {stats['errors']}")


if __name__ == "__main__":
    main() 
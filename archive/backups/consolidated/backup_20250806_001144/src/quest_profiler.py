"""
Quest Knowledge Builder & Smart Profile Learning System

This module provides a hybrid system to create and grow quest profiles using:
- Live gameplay monitoring via OCR
- Wiki scraping from external sources
- GPT logic for unclear text inference
- Auto-generation of structured quest YAML files
"""

import time
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re

# Simple logging setup to avoid import issues
class SimpleLogger:
    def __init__(self, name):
        self.name = name
    
    def info(self, message):
        print(f"[INFO] {self.name}: {message}")
    
    def warning(self, message):
        print(f"[WARNING] {self.name}: {message}")
    
    def error(self, message):
        print(f"[ERROR] {self.name}: {message}")
    
    def debug(self, message):
        print(f"[DEBUG] {self.name}: {message}")
    
    def setLevel(self, level):
        pass
    
    def addHandler(self, handler):
        pass

# Import existing systems
# Mock OCR functions for testing (avoiding import issues)
def run_ocr(image):
    return "Mock OCR text"

def capture_screen():
    return None

# Mock LegacyQuestManager for testing
class LegacyQuestManager:
    def __init__(self):
        pass
    
    def list_all_quests(self):
        return []


@dataclass
class QuestMetadata:
    """Metadata for a discovered quest."""
    quest_id: str
    name: str
    giver: str
    location: str
    planet: str
    coordinates: Tuple[int, int]
    reward: str
    quest_type: str
    difficulty: str
    level_requirement: int
    discovered_time: datetime
    source: str  # "ocr", "wiki", "gpt"


@dataclass
class QuestObjective:
    """Individual objective within a quest."""
    objective_id: str
    description: str
    objective_type: str  # "collect", "kill", "talk", "explore", "craft"
    target: str
    coordinates: Optional[Tuple[int, int]]
    count: int
    completed: bool = False


@dataclass
class QuestStep:
    """Individual step within a quest."""
    step_id: str
    step_type: str  # "dialogue", "movement", "combat", "collection", "exploration"
    description: str
    npc_id: Optional[str]
    coordinates: Optional[Tuple[int, int]]
    requirements: Dict[str, Any]
    completed: bool = False


class QuestProfiler:
    """
    Quest Knowledge Builder & Smart Profile Learning System.
    
    Features:
    - OCR-based quest monitoring
    - Wiki scraping integration
    - GPT inference for unclear text
    - Auto-generation of quest YAML files
    - Quest database management
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the quest profiler system."""
        self.logger = SimpleLogger("quest_profiler")
        self.setup_logging()
        
        # Initialize components
        self.legacy_manager = LegacyQuestManager()
        self.quest_database: Dict[str, QuestMetadata] = {}
        self.active_quests: Dict[str, Dict[str, Any]] = {}
        self.discovered_quests: List[QuestMetadata] = []
        
        # Configuration
        self.config = self.load_config(config_path)
        self.ocr_interval = self.config.get("ocr_interval", 2.0)
        self.quest_detection_keywords = self.config.get("quest_detection_keywords", [
            "quest", "mission", "task", "objective", "assignment"
        ])
        
        # File paths
        self.quests_dir = Path("data/quests")
        self.quests_dir.mkdir(exist_ok=True)
        
        # Load existing quest data
        self.load_existing_quests()
    
    def setup_logging(self):
        """Set up logging for quest profiler."""
        # Simple logging setup - no handlers needed
        pass
    
    def load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration for the quest profiler."""
        default_config = {
            "ocr_interval": 2.0,
            "quest_detection_keywords": [
                "quest", "mission", "task", "objective", "assignment"
            ],
            "wiki_sources": [
                "https://swgr.org/wiki/",
                "https://swg.fandom.com/wiki/"
            ],
            "gpt_enabled": True,
            "auto_save_interval": 300,  # 5 minutes
            "quest_types": [
                "legacy", "theme_park", "kashyyyk", "heroic", "daily", "weekly"
            ]
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def load_existing_quests(self):
        """Load existing quest data from various sources."""
        # Load from legacy quest manager
        legacy_quests = self.legacy_manager.list_all_quests()
        for quest in legacy_quests:
            quest_id = quest.get("id", f"legacy_{quest.get('title', '').lower().replace(' ', '_')}")
            metadata = QuestMetadata(
                quest_id=quest_id,
                name=quest.get("title", "Unknown Quest"),
                giver=quest.get("npc", "Unknown"),
                location=quest.get("location", "Unknown"),
                planet=quest.get("planet", "Unknown"),
                coordinates=(0, 0),
                reward=quest.get("reward", "Unknown"),
                quest_type="legacy",
                difficulty=quest.get("difficulty", "medium"),
                level_requirement=quest.get("level", 1),
                discovered_time=datetime.now(),
                source="legacy"
            )
            self.quest_database[quest_id] = metadata
        
        # Load from YAML quest files
        for yaml_file in self.quests_dir.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    quest_data = yaml.safe_load(f)
                    quest_id = quest_data.get("quest_id", yaml_file.stem)
                    metadata = QuestMetadata(
                        quest_id=quest_id,
                        name=quest_data.get("name", "Unknown Quest"),
                        giver=quest_data.get("giver", "Unknown"),
                        location=quest_data.get("zone", "Unknown"),
                        planet=quest_data.get("planet", "Unknown"),
                        coordinates=tuple(quest_data.get("coordinates", [0, 0])),
                        reward=str(quest_data.get("rewards", {})),
                        quest_type=quest_data.get("quest_type", "unknown"),
                        difficulty=quest_data.get("difficulty", "medium"),
                        level_requirement=quest_data.get("level_requirement", 1),
                        discovered_time=datetime.now(),
                        source="yaml"
                    )
                    self.quest_database[quest_id] = metadata
            except Exception as e:
                self.logger.warning(f"Failed to load quest from {yaml_file}: {e}")
        
        self.logger.info(f"Loaded {len(self.quest_database)} existing quests")
    
    def start_monitoring(self):
        """Start continuous quest monitoring via OCR."""
        self.logger.info("Starting quest monitoring...")
        
        try:
            while True:
                self.monitor_quest_acquisition()
                time.sleep(self.ocr_interval)
        except KeyboardInterrupt:
            self.logger.info("Quest monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error in quest monitoring: {e}")
    
    def monitor_quest_acquisition(self):
        """Monitor for new quest acquisition via OCR."""
        try:
            # Capture screen for OCR
            screen = capture_screen()
            if screen is None:
                return
            
            # Run OCR on the screen
            ocr_text = run_ocr(screen)
            
            # Check for quest-related keywords
            if self.detect_quest_keywords(ocr_text):
                self.logger.info("Quest-related text detected via OCR")
                
                # Extract quest information
                quest_info = self.extract_quest_info(ocr_text)
                if quest_info:
                    self.process_discovered_quest(quest_info)
        
        except Exception as e:
            self.logger.error(f"Error in quest acquisition monitoring: {e}")
    
    def detect_quest_keywords(self, text: str) -> bool:
        """Detect if OCR text contains quest-related keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.quest_detection_keywords)
    
    def extract_quest_info(self, ocr_text: str) -> Optional[Dict[str, Any]]:
        """Extract quest information from OCR text."""
        quest_info = {}
        
        # Extract quest name (look for patterns like "Quest: [Name]" or "Mission: [Name]")
        name_patterns = [
            r"quest:\s*([^\n]+)",
            r"mission:\s*([^\n]+)",
            r"task:\s*([^\n]+)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                quest_info["name"] = match.group(1).strip()
                break
        
        # Extract NPC/Quest Giver
        npc_patterns = [
            r"from\s+([^\n]+)",
            r"giver:\s*([^\n]+)",
            r"npc:\s*([^\n]+)",
            r"From:\s*([^\n]+)"
        ]
        
        for pattern in npc_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                quest_info["giver"] = match.group(1).strip()
                break
        
        # Extract location/planet
        location_patterns = [
            r"location:\s*([^\n]+)",
            r"planet:\s*([^\n]+)",
            r"at\s+([^\n]+)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                quest_info["location"] = match.group(1).strip()
                break
        
        # Extract rewards
        reward_patterns = [
            r"reward:\s*([^\n]+)",
            r"rewards:\s*([^\n]+)",
            r"you\s+receive\s+([^\n]+)"
        ]
        
        for pattern in reward_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                quest_info["reward"] = match.group(1).strip()
                break
        
        return quest_info if quest_info else None
    
    def process_discovered_quest(self, quest_info: Dict[str, Any]):
        """Process a newly discovered quest."""
        # Generate quest ID
        quest_name = quest_info.get("name", "Unknown Quest")
        quest_id = f"discovered_{quest_name.lower().replace(' ', '_').replace('-', '_')}"
        
        # Check if quest already exists
        if quest_id in self.quest_database:
            self.logger.info(f"Quest already exists: {quest_name}")
            return
        
        # Create quest metadata
        metadata = QuestMetadata(
            quest_id=quest_id,
            name=quest_name,
            giver=quest_info.get("giver", "Unknown"),
            location=quest_info.get("location", "Unknown"),
            planet=self.extract_planet_from_location(quest_info.get("location", "")),
            coordinates=(0, 0),  # Will be updated during quest execution
            reward=quest_info.get("reward", "Unknown"),
            quest_type="discovered",
            difficulty="medium",
            level_requirement=1,
            discovered_time=datetime.now(),
            source="ocr"
        )
        
        # Add to discovered quests
        self.discovered_quests.append(metadata)
        self.quest_database[quest_id] = metadata
        
        self.logger.info(f"Discovered new quest: {quest_name} from {metadata.giver}")
        
        # Auto-generate quest YAML
        self.generate_quest_yaml(metadata)
    
    def extract_planet_from_location(self, location: str) -> str:
        """Extract planet name from location string."""
        planets = ["tatooine", "naboo", "corellia", "dantooine", "endor", "lok", "rori", "talus", "yavin4", "dathomir", "kashyyyk", "mustafar"]
        
        location_lower = location.lower()
        for planet in planets:
            if planet in location_lower:
                return planet
        
        return "unknown"
    
    def generate_quest_yaml(self, metadata: QuestMetadata):
        """Auto-generate a draft YAML quest file."""
        quest_data = {
            "quest_id": metadata.quest_id,
            "name": metadata.name,
            "description": f"Auto-generated quest discovered via OCR",
            "quest_type": metadata.quest_type,
            "difficulty": metadata.difficulty,
            "level_requirement": metadata.level_requirement,
            "planet": metadata.planet,
            "zone": metadata.location,
            "coordinates": list(metadata.coordinates),
            "giver": metadata.giver,
            "rewards": {
                "experience": 100,
                "credits": 500,
                "items": []
            },
            "steps": [
                {
                    "step_id": "talk_to_giver",
                    "type": "dialogue",
                    "npc_id": metadata.giver,
                    "coordinates": list(metadata.coordinates),
                    "description": f"Talk to {metadata.giver} to start the quest"
                }
            ],
            "metadata": {
                "created_date": metadata.discovered_time.strftime("%Y-%m-%d"),
                "last_updated": metadata.discovered_time.strftime("%Y-%m-%d"),
                "version": "1.0",
                "author": "MS11_Quest_Profiler",
                "source": metadata.source
            },
            "state": {
                "status": "available",
                "current_step": None,
                "steps_completed": 0,
                "total_steps": 1
            }
        }
        
        # Save to YAML file
        planet_dir = self.quests_dir / metadata.planet
        planet_dir.mkdir(exist_ok=True)
        
        yaml_file = planet_dir / f"{metadata.quest_id}.yaml"
        try:
            with open(yaml_file, 'w') as f:
                yaml.dump(quest_data, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Generated quest YAML: {yaml_file}")
        except Exception as e:
            self.logger.error(f"Failed to generate quest YAML: {e}")
    
    def scrape_wiki_quests(self, source_url: str) -> List[Dict[str, Any]]:
        """Scrape quest data from wiki sources."""
        # This would integrate with the existing wiki importers
        # For now, return empty list as placeholder
        self.logger.info(f"Scraping quests from: {source_url}")
        return []
    
    def infer_with_gpt(self, unclear_text: str) -> str:
        """Use GPT to infer unclear OCR text."""
        # This would integrate with GPT API
        # For now, return the original text as placeholder
        self.logger.info(f"GPT inference for unclear text: {unclear_text[:50]}...")
        return unclear_text
    
    def get_quest_statistics(self) -> Dict[str, Any]:
        """Get statistics about discovered and existing quests."""
        total_quests = len(self.quest_database)
        discovered_count = len(self.discovered_quests)
        legacy_count = len([q for q in self.quest_database.values() if q.source == "legacy"])
        yaml_count = len([q for q in self.quest_database.values() if q.source == "yaml"])
        ocr_count = len([q for q in self.quest_database.values() if q.source == "ocr"])
        
        return {
            "total_quests": total_quests,
            "discovered_quests": discovered_count,
            "legacy_quests": legacy_count,
            "yaml_quests": yaml_count,
            "ocr_discovered": ocr_count,
            "quests_by_planet": self.get_quests_by_planet(),
            "quests_by_type": self.get_quests_by_type()
        }
    
    def get_quests_by_planet(self) -> Dict[str, int]:
        """Get count of quests by planet."""
        planet_counts = {}
        for quest in self.quest_database.values():
            planet = quest.planet
            planet_counts[planet] = planet_counts.get(planet, 0) + 1
        return planet_counts
    
    def get_quests_by_type(self) -> Dict[str, int]:
        """Get count of quests by type."""
        type_counts = {}
        for quest in self.quest_database.values():
            quest_type = quest.quest_type
            type_counts[quest_type] = type_counts.get(quest_type, 0) + 1
        return type_counts
    
    def save_quest_database(self):
        """Save the quest database to disk."""
        try:
            db_file = Path("data/quest_database.json")
            db_file.parent.mkdir(exist_ok=True)
            
            # Convert dataclasses to dictionaries
            db_data = {
                quest_id: asdict(metadata) for quest_id, metadata in self.quest_database.items()
            }
            
            with open(db_file, 'w') as f:
                json.dump(db_data, f, indent=2, default=str)
            
            self.logger.info(f"Saved quest database to {db_file}")
        except Exception as e:
            self.logger.error(f"Failed to save quest database: {e}")


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quest Knowledge Builder & Smart Profile Learning")
    parser.add_argument("--monitor", action="store_true", help="Start continuous quest monitoring")
    parser.add_argument("--stats", action="store_true", help="Show quest statistics")
    parser.add_argument("--learn-live", action="store_true", help="Start live quest learning mode")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    
    args = parser.parse_args()
    
    profiler = QuestProfiler(args.config)
    
    if args.monitor:
        profiler.start_monitoring()
    elif args.stats:
        stats = profiler.get_quest_statistics()
        print("Quest Statistics:")
        print(f"Total Quests: {stats['total_quests']}")
        print(f"Discovered Quests: {stats['discovered_quests']}")
        print(f"Legacy Quests: {stats['legacy_quests']}")
        print(f"YAML Quests: {stats['yaml_quests']}")
        print(f"OCR Discovered: {stats['ocr_discovered']}")
        print("\nQuests by Planet:")
        for planet, count in stats['quests_by_planet'].items():
            print(f"  {planet}: {count}")
        print("\nQuests by Type:")
        for quest_type, count in stats['quests_by_type'].items():
            print(f"  {quest_type}: {count}")
    elif args.learn_live:
        print("Starting live quest learning mode...")
        profiler.start_monitoring()
    else:
        print("Quest Profiler initialized. Use --monitor, --stats, or --learn-live")


if __name__ == "__main__":
    main() 
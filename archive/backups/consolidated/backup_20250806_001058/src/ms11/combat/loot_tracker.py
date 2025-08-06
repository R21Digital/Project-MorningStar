#!/usr/bin/env python3
"""
Batch 183 - Heroics Loot Table Integration with MS11
Objective: Track rare item drops and populate heroics_loot.json for SWGDB integration
"""

import os
import json
import re
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

from utils.license_hooks import requires_license
from profession_logic.utils.logger import logger

class LootRarity(Enum):
    """Loot rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class LootDrop:
    """Data structure for a loot drop"""
    item_name: str
    rarity: str
    heroic_name: str
    boss_name: str
    character_name: str
    timestamp: str
    location: str
    instance_id: Optional[str] = None
    drop_rate: Optional[float] = None

@dataclass
class HeroicLootData:
    """Data structure for heroic loot information"""
    heroic_name: str
    location: str
    bosses: Dict[str, List[LootDrop]]
    total_drops: int
    last_drop: Optional[str]

class LootTracker:
    """Main loot tracking class for MS11"""
    
    def __init__(self, config_path: str = "src/data/loot_targets.json", 
                 loot_file: str = "src/data/loot_logs/heroics_loot.json"):
        self.config_path = Path(config_path)
        self.loot_file = Path(loot_file)
        self.config = {}
        self.loot_data = {}
        self.current_heroic = None
        self.current_boss = None
        self.current_character = None
        self.current_location = None
        
        # Load configuration and data
        self._load_config()
        self._load_loot_data()
        
        # Loot message patterns
        self.loot_patterns = [
            r"You loot (.+?) from (.+?)\.",
            r"You receive (.+?) from (.+?)\.",
            r"You found (.+?) in (.+?)\.",
            r"(.+?) was added to your inventory from (.+?)\."
        ]
        
        logger.info("[LOOT] Loot tracker initialized")
    
    def _load_config(self) -> None:
        """Load loot tracking configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                logger.info(f"[LOOT] Configuration loaded from {self.config_path}")
            else:
                logger.warning(f"[LOOT] Configuration file not found: {self.config_path}")
                self.config = {}
        except Exception as e:
            logger.error(f"[LOOT] Error loading configuration: {e}")
            self.config = {}
    
    def _load_loot_data(self) -> None:
        """Load existing loot data"""
        try:
            if self.loot_file.exists():
                with open(self.loot_file, 'r') as f:
                    self.loot_data = json.load(f)
                logger.info(f"[LOOT] Loot data loaded from {self.loot_file}")
            else:
                logger.warning(f"[LOOT] Loot data file not found: {self.loot_file}")
                self._initialize_loot_data()
        except Exception as e:
            logger.error(f"[LOOT] Error loading loot data: {e}")
            self._initialize_loot_data()
    
    def _initialize_loot_data(self) -> None:
        """Initialize empty loot data structure"""
        self.loot_data = {
            "metadata": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "total_drops": 0,
                "data_source": "MS11 Loot Tracker"
            },
            "heroics": {
                "axkva-min": {
                    "name": "Axkva Min",
                    "location": "Dathomir",
                    "bosses": {
                        "axkva-min": {
                            "name": "Axkva Min",
                            "drops": []
                        }
                    },
                    "total_drops": 0,
                    "last_drop": None
                },
                "ig-88": {
                    "name": "IG-88",
                    "location": "Bespin",
                    "bosses": {
                        "ig-88": {
                            "name": "IG-88",
                            "drops": []
                        }
                    },
                    "total_drops": 0,
                    "last_drop": None
                },
                "tusken-army": {
                    "name": "Tusken Army",
                    "location": "Tatooine",
                    "bosses": {
                        "tusken-chieftain": {
                            "name": "Tusken Chieftain",
                            "drops": []
                        }
                    },
                    "total_drops": 0,
                    "last_drop": None
                }
            },
            "characters": {},
            "statistics": {
                "total_drops": 0,
                "unique_items": 0,
                "rarest_drops": [],
                "most_active_heroic": None,
                "most_active_character": None
            }
        }
    
    def _save_loot_data(self) -> None:
        """Save loot data to file"""
        try:
            # Update metadata
            self.loot_data["metadata"]["last_updated"] = datetime.now().isoformat()
            self.loot_data["metadata"]["total_drops"] = self.loot_data["statistics"]["total_drops"]
            
            # Ensure directory exists
            self.loot_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.loot_file, 'w') as f:
                json.dump(self.loot_data, f, indent=2)
            
            logger.info(f"[LOOT] Loot data saved to {self.loot_file}")
        except Exception as e:
            logger.error(f"[LOOT] Error saving loot data: {e}")
    
    def set_current_context(self, heroic: str = None, boss: str = None, 
                          character: str = None, location: str = None) -> None:
        """Set current context for loot tracking"""
        if heroic:
            self.current_heroic = heroic
        if boss:
            self.current_boss = boss
        if character:
            self.current_character = character
        if location:
            self.current_location = location
        
        logger.info(f"[LOOT] Context set: Heroic={self.current_heroic}, Boss={self.current_boss}, Character={self.current_character}")
    
    def parse_loot_message(self, message: str) -> Optional[LootDrop]:
        """Parse loot message and extract item information"""
        if not self.config.get("tracking_enabled", True):
            return None
        
        # Try different patterns
        for pattern in self.loot_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                item_name = match.group(1).strip()
                source = match.group(2).strip() if len(match.groups()) > 1 else "Unknown"
                
                # Check if item should be tracked
                if self._should_track_item(item_name):
                    return self._create_loot_drop(item_name, source)
        
        return None
    
    def _should_track_item(self, item_name: str) -> bool:
        """Check if item should be tracked based on configuration"""
        # Check excluded items
        excluded_items = self.config.get("excluded_items", [])
        if item_name in excluded_items:
            return False
        
        # Check specific items
        specific_items = self.config.get("specific_items", [])
        if item_name in specific_items:
            return True
        
        # Check rarity levels (placeholder - would need item database)
        rarity_levels = self.config.get("rarity_levels", {})
        if rarity_levels.get("rare", True) or rarity_levels.get("epic", True):
            # Assume items with certain keywords are rare
            rare_keywords = ["Rare", "Epic", "Legendary", "Crystal", "Artifact", "Robe", "Rifle", "Armor"]
            if any(keyword.lower() in item_name.lower() for keyword in rare_keywords):
                return True
        
        return False
    
    def _create_loot_drop(self, item_name: str, source: str) -> LootDrop:
        """Create a loot drop record"""
        # Determine rarity (placeholder logic)
        rarity = self._determine_rarity(item_name)
        
        # Determine heroic and boss from context or source
        heroic_name = self.current_heroic or self._extract_heroic_from_source(source)
        boss_name = self.current_boss or self._extract_boss_from_source(source)
        
        return LootDrop(
            item_name=item_name,
            rarity=rarity,
            heroic_name=heroic_name,
            boss_name=boss_name,
            character_name=self.current_character or "Unknown",
            timestamp=datetime.now().isoformat(),
            location=self.current_location or "Unknown"
        )
    
    def _determine_rarity(self, item_name: str) -> str:
        """Determine item rarity (placeholder implementation)"""
        item_lower = item_name.lower()
        
        if any(word in item_lower for word in ["legendary", "artifact"]):
            return LootRarity.LEGENDARY.value
        elif any(word in item_lower for word in ["epic", "crystal"]):
            return LootRarity.EPIC.value
        elif any(word in item_lower for word in ["rare", "robe", "rifle", "armor"]):
            return LootRarity.RARE.value
        elif any(word in item_lower for word in ["uncommon"]):
            return LootRarity.UNCOMMON.value
        else:
            return LootRarity.COMMON.value
    
    def _extract_heroic_from_source(self, source: str) -> str:
        """Extract heroic name from source"""
        source_lower = source.lower()
        
        if "axkva" in source_lower or "nightsister" in source_lower:
            return "axkva-min"
        elif "ig-88" in source_lower or "bounty" in source_lower:
            return "ig-88"
        elif "tusken" in source_lower or "chieftain" in source_lower:
            return "tusken-army"
        else:
            return "unknown"
    
    def _extract_boss_from_source(self, source: str) -> str:
        """Extract boss name from source"""
        source_lower = source.lower()
        
        if "axkva" in source_lower:
            return "axkva-min"
        elif "ig-88" in source_lower:
            return "ig-88"
        elif "chieftain" in source_lower:
            return "tusken-chieftain"
        else:
            return "unknown"
    
    def record_loot_drop(self, loot_drop: LootDrop) -> None:
        """Record a loot drop in the data structure"""
        try:
            heroic_key = loot_drop.heroic_name.replace(" ", "-").lower()
            boss_key = loot_drop.boss_name.replace(" ", "-").lower()
            
            # Initialize heroic if not exists
            if heroic_key not in self.loot_data["heroics"]:
                self.loot_data["heroics"][heroic_key] = {
                    "name": loot_drop.heroic_name,
                    "location": loot_drop.location,
                    "bosses": {},
                    "total_drops": 0,
                    "last_drop": None
                }
            
            # Initialize boss if not exists
            if boss_key not in self.loot_data["heroics"][heroic_key]["bosses"]:
                self.loot_data["heroics"][heroic_key]["bosses"][boss_key] = {
                    "name": loot_drop.boss_name,
                    "drops": []
                }
            
            # Add drop to boss
            drop_data = asdict(loot_drop)
            self.loot_data["heroics"][heroic_key]["bosses"][boss_key]["drops"].append(drop_data)
            
            # Update heroic statistics
            self.loot_data["heroics"][heroic_key]["total_drops"] += 1
            self.loot_data["heroics"][heroic_key]["last_drop"] = loot_drop.timestamp
            
            # Update character statistics
            if loot_drop.character_name not in self.loot_data["characters"]:
                self.loot_data["characters"][loot_drop.character_name] = {
                    "drops": [],
                    "total_drops": 0,
                    "last_drop": None
                }
            
            self.loot_data["characters"][loot_drop.character_name]["drops"].append(drop_data)
            self.loot_data["characters"][loot_drop.character_name]["total_drops"] += 1
            self.loot_data["characters"][loot_drop.character_name]["last_drop"] = loot_drop.timestamp
            
            # Update global statistics
            self.loot_data["statistics"]["total_drops"] += 1
            
            # Update unique items count
            all_items = set()
            for heroic in self.loot_data["heroics"].values():
                for boss in heroic["bosses"].values():
                    for drop in boss["drops"]:
                        all_items.add(drop["item_name"])
            
            self.loot_data["statistics"]["unique_items"] = len(all_items)
            
            # Update most active heroic
            most_active = max(self.loot_data["heroics"].keys(), 
                            key=lambda k: self.loot_data["heroics"][k]["total_drops"])
            self.loot_data["statistics"]["most_active_heroic"] = most_active
            
            # Update most active character
            if self.loot_data["characters"]:
                most_active_char = max(self.loot_data["characters"].keys(),
                                     key=lambda k: self.loot_data["characters"][k]["total_drops"])
                self.loot_data["statistics"]["most_active_character"] = most_active_char
            
            # Save data
            self._save_loot_data()
            
            logger.info(f"[LOOT] Recorded drop: {loot_drop.item_name} from {loot_drop.boss_name}")
            print(f"🎁 Loot tracked: {loot_drop.item_name} ({loot_drop.rarity}) from {loot_drop.boss_name}")
            
        except Exception as e:
            logger.error(f"[LOOT] Error recording loot drop: {e}")
    
    def process_loot_message(self, message: str) -> bool:
        """Process a loot message and record if applicable"""
        loot_drop = self.parse_loot_message(message)
        if loot_drop:
            self.record_loot_drop(loot_drop)
            return True
        return False
    
    def get_loot_statistics(self) -> Dict[str, Any]:
        """Get loot tracking statistics"""
        return {
            "total_drops": self.loot_data["statistics"]["total_drops"],
            "unique_items": self.loot_data["statistics"]["unique_items"],
            "most_active_heroic": self.loot_data["statistics"]["most_active_heroic"],
            "most_active_character": self.loot_data["statistics"]["most_active_character"],
            "heroics_count": len(self.loot_data["heroics"]),
            "characters_count": len(self.loot_data["characters"])
        }
    
    def get_heroic_drops(self, heroic_name: str) -> List[Dict[str, Any]]:
        """Get all drops for a specific heroic"""
        heroic_key = heroic_name.replace(" ", "-").lower()
        if heroic_key in self.loot_data["heroics"]:
            drops = []
            for boss in self.loot_data["heroics"][heroic_key]["bosses"].values():
                drops.extend(boss["drops"])
            return drops
        return []
    
    def get_character_drops(self, character_name: str) -> List[Dict[str, Any]]:
        """Get all drops for a specific character"""
        if character_name in self.loot_data["characters"]:
            return self.loot_data["characters"][character_name]["drops"]
        return []

# Global instance
loot_tracker = LootTracker()

@requires_license
def process_loot_message(message: str) -> bool:
    """Process a loot message"""
    return loot_tracker.process_loot_message(message)

@requires_license
def set_loot_context(heroic: str = None, boss: str = None, 
                    character: str = None, location: str = None) -> None:
    """Set current loot tracking context"""
    loot_tracker.set_current_context(heroic, boss, character, location)

@requires_license
def get_loot_statistics() -> Dict[str, Any]:
    """Get loot tracking statistics"""
    return loot_tracker.get_loot_statistics()

@requires_license
def get_heroic_drops(heroic_name: str) -> List[Dict[str, Any]]:
    """Get drops for a specific heroic"""
    return loot_tracker.get_heroic_drops(heroic_name)

@requires_license
def get_character_drops(character_name: str) -> List[Dict[str, Any]]:
    """Get drops for a specific character"""
    return loot_tracker.get_character_drops(character_name) 
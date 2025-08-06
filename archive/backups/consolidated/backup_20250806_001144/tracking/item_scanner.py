#!/usr/bin/env python3
"""
Item Scanner + Loot Memory Logger for MS11

This module scans loot obtained in-game and remembers drops by creature/instance/vendor.
It uses OCR and macro-based detection to capture loot information and build comprehensive loot tables.
"""

import time
import json
import logging
import threading
import random
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import re
import cv2
import numpy as np
from PIL import Image
import pytesseract

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LootSource(Enum):
    """Types of loot sources."""
    CREATURE = "creature"
    INSTANCE = "instance"
    VENDOR = "vendor"
    CONTAINER = "container"
    QUEST = "quest"
    CRAFTING = "crafting"

class ItemRarity(Enum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class LootItem:
    """Represents a looted item."""
    item_id: str
    item_name: str
    quantity: int
    rarity: ItemRarity
    source_type: LootSource
    source_name: str
    location: str
    coordinates: Optional[Tuple[float, float]]
    timestamp: datetime
    session_id: str
    character_name: str
    combat_log_match: Optional[str] = None
    ocr_confidence: Optional[float] = None
    macro_detected: bool = False

@dataclass
class LootTable:
    """Represents a loot table for a specific source."""
    source_name: str
    source_type: LootSource
    total_kills: int
    total_loot: int
    last_updated: datetime
    items: Dict[str, Dict[str, Any]]  # item_id -> item_data
    drop_rates: Dict[str, float]  # item_id -> drop_rate
    rarity_distribution: Dict[str, int]  # rarity -> count

@dataclass
class LootSession:
    """Represents a loot scanning session."""
    session_id: str
    character_name: str
    start_time: datetime
    end_time: Optional[datetime]
    total_items: int
    total_value: float
    sources_encountered: Set[str]
    items_looted: List[LootItem]

class ItemScanner:
    """Scans and tracks loot obtained in-game."""
    
    def __init__(self, data_dir: str = "data/loot_tables"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.active_sessions: Dict[str, LootSession] = {}
        self.loot_tables: Dict[str, LootTable] = {}
        self.recent_loot: List[LootItem] = []
        self.combat_log_cache: List[str] = []
        
        # OCR settings
        self.ocr_enabled = True
        self.ocr_confidence_threshold = 0.7
        self.ocr_regions = {
            "loot_window": (100, 200, 400, 600),  # x, y, width, height
            "chat_log": (50, 500, 300, 200),
            "inventory": (600, 100, 200, 400)
        }
        
        # Macro detection patterns
        self.loot_patterns = [
            r"looted\s+(\d+)\s+(.+)",
            r"received\s+(.+)",
            r"found\s+(.+)",
            r"obtained\s+(.+)",
            r"(\d+)\s+(.+)",
            r"(.+)\s+\((\d+)\)"
        ]
        
        # Item rarity patterns
        self.rarity_patterns = {
            ItemRarity.COMMON: [r"common", r"basic", r"standard"],
            ItemRarity.UNCOMMON: [r"uncommon", r"enhanced", r"improved"],
            ItemRarity.RARE: [r"rare", r"exceptional", r"superior"],
            ItemRarity.EPIC: [r"epic", r"masterwork", r"exquisite"],
            ItemRarity.LEGENDARY: [r"legendary", r"artifact", r"mythic"]
        }
        
        # Load existing loot tables
        self._load_loot_tables()
        
        # Start monitoring thread
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        logger.info("ItemScanner initialized with OCR and macro detection")
    
    def _load_loot_tables(self) -> None:
        """Load existing loot tables from disk."""
        try:
            for table_file in self.data_dir.glob("*.json"):
                try:
                    with open(table_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    source_name = table_file.stem
                    loot_table = LootTable(
                        source_name=source_name,
                        source_type=LootSource(data.get('source_type', 'creature')),
                        total_kills=data.get('total_kills', 0),
                        total_loot=data.get('total_loot', 0),
                        last_updated=datetime.fromisoformat(data.get('last_updated', datetime.now().isoformat())),
                        items=data.get('items', {}),
                        drop_rates=data.get('drop_rates', {}),
                        rarity_distribution=data.get('rarity_distribution', {})
                    )
                    
                    self.loot_tables[source_name] = loot_table
                    
                except Exception as e:
                    logger.error(f"Error loading loot table {table_file}: {e}")
            
            logger.info(f"Loaded {len(self.loot_tables)} loot tables")
            
        except Exception as e:
            logger.error(f"Error loading loot tables: {e}")
    
    def _save_loot_table(self, source_name: str) -> None:
        """Save a loot table to disk."""
        try:
            if source_name in self.loot_tables:
                table = self.loot_tables[source_name]
                table_file = self.data_dir / f"{source_name}.json"
                
                data = {
                    'source_type': table.source_type.value,
                    'total_kills': table.total_kills,
                    'total_loot': table.total_loot,
                    'last_updated': table.last_updated.isoformat(),
                    'items': table.items,
                    'drop_rates': table.drop_rates,
                    'rarity_distribution': table.rarity_distribution
                }
                
                with open(table_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            logger.error(f"Error saving loot table {source_name}: {e}")
    
    def start_monitoring(self) -> None:
        """Start the loot monitoring thread."""
        if self.monitoring:
            logger.warning("Loot monitoring already active")
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Loot monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop the loot monitoring thread."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Loot monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop for loot detection."""
        while self.monitoring:
            try:
                # Check for new loot via OCR
                if self.ocr_enabled:
                    self._scan_ocr_regions()
                
                # Check for new combat log entries
                self._check_combat_log()
                
                # Clean up old data
                self._cleanup_old_data()
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _scan_ocr_regions(self) -> None:
        """Scan OCR regions for loot information."""
        try:
            # This would integrate with screen capture
            # For demo purposes, we'll simulate OCR detection
            
            # Simulate OCR detection of loot
            if random.random() < 0.1:  # 10% chance of finding loot
                self._simulate_ocr_loot_detection()
                
        except Exception as e:
            logger.error(f"Error in OCR scanning: {e}")
    
    def _simulate_ocr_loot_detection(self) -> None:
        """Simulate OCR loot detection for demo purposes."""
        sample_items = [
            ("Krayt Dragon Pearl", ItemRarity.LEGENDARY, 1),
            ("Composite Armor", ItemRarity.RARE, 1),
            ("Power Crystal", ItemRarity.EPIC, 2),
            ("Credits", ItemRarity.COMMON, 5000),
            ("Rancor Hide", ItemRarity.UNCOMMON, 3)
        ]
        
        item_name, rarity, quantity = random.choice(sample_items)
        source_name = random.choice(["Krayt Dragon", "Rancor", "Acklay", "Giant Spider"])
        
        self._process_loot_detection(
            item_name=item_name,
            quantity=quantity,
            rarity=rarity,
            source_name=source_name,
            detection_method="ocr",
            confidence=random.uniform(0.7, 0.95)
        )
    
    def _check_combat_log(self) -> None:
        """Check combat log for loot information."""
        try:
            # This would read from actual combat log
            # For demo purposes, we'll simulate log entries
            
            if random.random() < 0.05:  # 5% chance of log entry
                self._simulate_combat_log_entry()
                
        except Exception as e:
            logger.error(f"Error checking combat log: {e}")
    
    def _simulate_combat_log_entry(self) -> None:
        """Simulate combat log entries for demo purposes."""
        log_entries = [
            "You looted 1 Krayt Dragon Pearl from Krayt Dragon",
            "You received 2 Power Crystal from Rancor",
            "You found 1 Composite Armor from Acklay",
            "You obtained 5000 Credits from Giant Spider",
            "You looted 3 Rancor Hide from Rancor"
        ]
        
        log_entry = random.choice(log_entries)
        self._process_combat_log_entry(log_entry)
    
    def _process_combat_log_entry(self, log_entry: str) -> None:
        """Process a combat log entry for loot information."""
        try:
            # Add to cache
            self.combat_log_cache.append(log_entry)
            
            # Keep only recent entries
            if len(self.combat_log_cache) > 100:
                self.combat_log_cache = self.combat_log_cache[-100:]
            
            # Parse loot information
            for pattern in self.loot_patterns:
                match = re.search(pattern, log_entry, re.IGNORECASE)
                if match:
                    if len(match.groups()) == 2:
                        quantity = int(match.group(1))
                        item_name = match.group(2).strip()
                    else:
                        quantity = 1
                        item_name = match.group(1).strip()
                    
                    # Extract source from log entry
                    source_match = re.search(r"from\s+(.+)", log_entry, re.IGNORECASE)
                    source_name = source_match.group(1).strip() if source_match else "Unknown"
                    
                    # Determine rarity
                    rarity = self._determine_item_rarity(item_name)
                    
                    self._process_loot_detection(
                        item_name=item_name,
                        quantity=quantity,
                        rarity=rarity,
                        source_name=source_name,
                        detection_method="combat_log",
                        confidence=1.0
                    )
                    break
                    
        except Exception as e:
            logger.error(f"Error processing combat log entry: {e}")
    
    def _determine_item_rarity(self, item_name: str) -> ItemRarity:
        """Determine item rarity based on name patterns."""
        item_name_lower = item_name.lower()
        
        for rarity, patterns in self.rarity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, item_name_lower):
                    return rarity
        
        # Default to common if no pattern matches
        return ItemRarity.COMMON
    
    def _process_loot_detection(self, item_name: str, quantity: int, rarity: ItemRarity,
                               source_name: str, detection_method: str, confidence: float) -> None:
        """Process detected loot and update loot tables."""
        try:
            # Generate item ID
            item_id = self._generate_item_id(item_name)
            
            # Create loot item
            loot_item = LootItem(
                item_id=item_id,
                item_name=item_name,
                quantity=quantity,
                rarity=rarity,
                source_type=LootSource.CREATURE,
                source_name=source_name,
                location="Unknown",
                coordinates=None,
                timestamp=datetime.now(),
                session_id=self._get_active_session_id(),
                character_name=self._get_current_character(),
                combat_log_match=None,
                ocr_confidence=confidence if detection_method == "ocr" else None,
                macro_detected=detection_method == "macro"
            )
            
            # Add to recent loot
            self.recent_loot.append(loot_item)
            
            # Keep only recent items
            if len(self.recent_loot) > 100:
                self.recent_loot = self.recent_loot[-100:]
            
            # Update loot table
            self._update_loot_table(loot_item)
            
            # Update active session
            self._update_active_session(loot_item)
            
            logger.info(f"Loot detected: {quantity}x {item_name} from {source_name}")
            
        except Exception as e:
            logger.error(f"Error processing loot detection: {e}")
    
    def _generate_item_id(self, item_name: str) -> str:
        """Generate a unique item ID."""
        # Simple hash-based ID generation
        import hashlib
        return hashlib.md5(item_name.encode()).hexdigest()[:8]
    
    def _get_active_session_id(self) -> str:
        """Get the current active session ID."""
        # For demo purposes, return a default session
        return "default_session"
    
    def _get_current_character(self) -> str:
        """Get the current character name."""
        # For demo purposes, return a default character
        return "DefaultCharacter"
    
    def _update_loot_table(self, loot_item: LootItem) -> None:
        """Update loot table for the source."""
        source_name = loot_item.source_name
        
        if source_name not in self.loot_tables:
            # Create new loot table
            self.loot_tables[source_name] = LootTable(
                source_name=source_name,
                source_type=loot_item.source_type,
                total_kills=0,
                total_loot=0,
                last_updated=datetime.now(),
                items={},
                drop_rates={},
                rarity_distribution={}
            )
        
        table = self.loot_tables[source_name]
        
        # Update item data
        if loot_item.item_id not in table.items:
            table.items[loot_item.item_id] = {
                'name': loot_item.item_name,
                'rarity': loot_item.rarity.value,
                'total_drops': 0,
                'total_quantity': 0,
                'first_seen': loot_item.timestamp.isoformat(),
                'last_seen': loot_item.timestamp.isoformat()
            }
        
        item_data = table.items[loot_item.item_id]
        item_data['total_drops'] += 1
        item_data['total_quantity'] += loot_item.quantity
        item_data['last_seen'] = loot_item.timestamp.isoformat()
        
        # Update rarity distribution
        rarity_key = loot_item.rarity.value
        table.rarity_distribution[rarity_key] = table.rarity_distribution.get(rarity_key, 0) + 1
        
        # Update total loot count
        table.total_loot += 1
        table.last_updated = datetime.now()
        
        # Calculate drop rates
        self._calculate_drop_rates(table)
        
        # Save to disk
        self._save_loot_table(source_name)
    
    def _calculate_drop_rates(self, table: LootTable) -> None:
        """Calculate drop rates for items in a loot table."""
        if table.total_loot == 0:
            return
        
        for item_id, item_data in table.items.items():
            drop_rate = (item_data['total_drops'] / table.total_loot) * 100
            table.drop_rates[item_id] = round(drop_rate, 2)
    
    def _update_active_session(self, loot_item: LootItem) -> None:
        """Update the active loot session."""
        session_id = loot_item.session_id
        
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = LootSession(
                session_id=session_id,
                character_name=loot_item.character_name,
                start_time=datetime.now(),
                end_time=None,
                total_items=0,
                total_value=0.0,
                sources_encountered=set(),
                items_looted=[]
            )
        
        session = self.active_sessions[session_id]
        session.items_looted.append(loot_item)
        session.total_items += 1
        session.sources_encountered.add(loot_item.source_name)
        
        # Calculate value (simplified)
        value_multipliers = {
            ItemRarity.COMMON: 1,
            ItemRarity.UNCOMMON: 5,
            ItemRarity.RARE: 25,
            ItemRarity.EPIC: 100,
            ItemRarity.LEGENDARY: 500
        }
        
        session.total_value += loot_item.quantity * value_multipliers.get(loot_item.rarity, 1)
    
    def _cleanup_old_data(self) -> None:
        """Clean up old loot data."""
        try:
            # Remove old recent loot (older than 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.recent_loot = [
                item for item in self.recent_loot
                if item.timestamp > cutoff_time
            ]
            
            # Close old sessions (older than 2 hours)
            session_cutoff = datetime.now() - timedelta(hours=2)
            for session_id, session in list(self.active_sessions.items()):
                if session.start_time < session_cutoff and session.end_time is None:
                    session.end_time = datetime.now()
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def get_recent_loot(self, limit: int = 20) -> List[LootItem]:
        """Get recent loot items."""
        return self.recent_loot[-limit:] if self.recent_loot else []
    
    def get_loot_table(self, source_name: str) -> Optional[LootTable]:
        """Get loot table for a specific source."""
        return self.loot_tables.get(source_name)
    
    def get_all_loot_tables(self) -> Dict[str, LootTable]:
        """Get all loot tables."""
        return self.loot_tables.copy()
    
    def get_active_sessions(self) -> Dict[str, LootSession]:
        """Get active loot sessions."""
        return self.active_sessions.copy()
    
    def get_loot_statistics(self) -> Dict[str, Any]:
        """Get comprehensive loot statistics."""
        try:
            total_items = sum(len(table.items) for table in self.loot_tables.values())
            total_sources = len(self.loot_tables)
            total_sessions = len(self.active_sessions)
            
            # Calculate total value
            total_value = sum(session.total_value for session in self.active_sessions.values())
            
            # Get rarity distribution
            rarity_dist = {}
            for table in self.loot_tables.values():
                for rarity, count in table.rarity_distribution.items():
                    rarity_dist[rarity] = rarity_dist.get(rarity, 0) + count
            
            return {
                "total_items": total_items,
                "total_sources": total_sources,
                "total_sessions": total_sessions,
                "total_value": total_value,
                "recent_loot_count": len(self.recent_loot),
                "rarity_distribution": rarity_dist,
                "monitoring_active": self.monitoring
            }
            
        except Exception as e:
            logger.error(f"Error getting loot statistics: {e}")
            return {}
    
    def search_loot(self, query: str, source_name: Optional[str] = None) -> List[LootItem]:
        """Search for loot items by name or source."""
        results = []
        query_lower = query.lower()
        
        for item in self.recent_loot:
            if (query_lower in item.item_name.lower() or 
                query_lower in item.source_name.lower()):
                if source_name is None or item.source_name.lower() == source_name.lower():
                    results.append(item)
        
        return results
    
    def get_source_statistics(self, source_name: str) -> Dict[str, Any]:
        """Get statistics for a specific source."""
        table = self.get_loot_table(source_name)
        if not table:
            return {}
        
        return {
            "source_name": table.source_name,
            "source_type": table.source_type.value,
            "total_kills": table.total_kills,
            "total_loot": table.total_loot,
            "unique_items": len(table.items),
            "last_updated": table.last_updated.isoformat(),
            "drop_rates": table.drop_rates,
            "rarity_distribution": table.rarity_distribution
        }

# Global instance
item_scanner = ItemScanner()

def get_item_scanner() -> ItemScanner:
    """Get the global item scanner instance."""
    return item_scanner 
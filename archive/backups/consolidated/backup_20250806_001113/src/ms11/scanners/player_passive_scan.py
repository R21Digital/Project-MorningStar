#!/usr/bin/env python3
"""
Batch 178 - Passive Player Scanner (Walk-by Scan)

Passive player scanner that collects lightweight metadata from nearby players
during travel or idle moments for SWGDB population.

Features:
- Lightweight scanning during travel/idle moments
- Parse: Name, race, faction (if shown), guild tag, title
- Store lightweight scan per player
- Avoid duplication via name + timestamp tracking
- Include opt-out logic for privacy
- Foundation for Players Seen stats page

Expected Output:
- New lightweight player registry dataset updated by bot
- Foundation for Players Seen stats page in future
"""

import os
import json
import time
import re
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageGrab

from utils.license_hooks import requires_license

# Setup logger
logger = logging.getLogger(__name__)


@dataclass
class PassivePlayerScan:
    """Lightweight player scan data structure."""
    name: str
    race: Optional[str] = None
    faction: Optional[str] = None
    guild: Optional[str] = None
    title: Optional[str] = None
    timestamp: str = None
    scan_id: str = None
    location: Optional[str] = None
    confidence: float = 0.0
    source: str = "passive_scan"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.scan_id is None:
            self.scan_id = f"passive_scan_{int(time.time())}_{hash(self.name)}"


@dataclass
class PlayerRegistryEntry:
    """Player registry entry for SWGDB population."""
    name: str
    first_seen: str = None
    last_seen: str = None
    total_scans: int = 1
    guild: Optional[str] = None
    title: Optional[str] = None
    race: Optional[str] = None
    faction: Optional[str] = None
    locations_seen: List[str] = None
    scan_frequency: float = 0.0  # scans per day
    
    def __post_init__(self):
        if self.first_seen is None:
            self.first_seen = datetime.now().isoformat()
        self.last_seen = datetime.now().isoformat()
        if self.locations_seen is None:
            self.locations_seen = []


class PassivePlayerScanner:
    """Passive player scanner for lightweight metadata collection."""
    
    def __init__(self, config_path: str = "config/passive_scanner_config.json"):
        """Initialize the passive player scanner.
        
        Parameters
        ----------
        config_path : str
            Path to scanner configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # Data storage
        self.registry_file = "data/player_registry.json"
        self.scans_file = "data/passive_scans.json"
        self.data_dir = Path("data")
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Player tracking
        self.player_registry: Dict[str, PlayerRegistryEntry] = {}
        self.scan_history: List[PassivePlayerScan] = []
        self.recent_scans: Set[str] = set()
        self.opt_out_players: Set[str] = set()
        
        # Scanner settings
        self.scan_interval = self.config.get("scan_interval", 60)  # seconds
        self.idle_scan_interval = self.config.get("idle_scan_interval", 300)  # 5 minutes
        self.travel_scan_interval = self.config.get("travel_scan_interval", 30)  # 30 seconds
        self.ocr_confidence_threshold = self.config.get("ocr_confidence_threshold", 50.0)
        self.last_scan_time = 0
        self.is_running = False
        self.scan_thread = None
        self.current_mode = "idle"  # idle, travel, combat
        
        # Screen regions for passive scanning
        self.scan_regions = self.config.get("scan_regions", {
            "nearby_area": (100, 100, 500, 400),
            "chat_window": (50, 400, 600, 500),
            "target_info": (700, 100, 900, 200),
            "group_window": (800, 200, 1000, 400)
        })
        
        # Text patterns for lightweight extraction
        self.name_patterns = self.config.get("name_patterns", [
            r'^[A-Z][a-z]+[A-Z][a-z]+$',  # CamelCase names
            r'^[A-Z][a-z]+_[A-Z][a-z]+$',  # Underscore names
            r'^[A-Z][a-z]+[0-9]+$',  # Names with numbers
        ])
        
        self.guild_patterns = self.config.get("guild_patterns", [
            r'\[([^\]]+)\]',  # [Guild Name]
            r'<([^>]+)>',  # <Guild Name>
        ])
        
        self.title_patterns = self.config.get("title_patterns", [
            r'([A-Z][a-z]+ [A-Z][a-z]+)',  # Title format
            r'([A-Z][a-z]+ of [A-Z][a-z]+)',  # "of" titles
        ])
        
        # Race patterns (lightweight)
        self.race_patterns = self.config.get("race_patterns", {
            "human": ["human", "humanoid"],
            "wookiee": ["wookiee", "wookie"],
            "twilek": ["twilek", "twi'lek"],
            "zabrak": ["zabrak"],
            "ithorian": ["ithorian", "hammerhead"],
            "rodian": ["rodian"],
            "mon calamari": ["mon calamari", "moncal"],
            "sullustan": ["sullustan"],
            "togruta": ["togruta"],
            "kel dor": ["kel dor", "kel-dor"],
            "chiss": ["chiss"],
            "trandoshan": ["trandoshan"],
            "geonosian": ["geonosian"],
            "gotal": ["gotal"],
            "quarren": ["quarren"],
            "aqualish": ["aqualish"],
            "gran": ["gran"],
            "duros": ["duros"],
            "neimoidian": ["neimoidian"],
            "weequay": ["weequay"]
        })
        
        # Faction patterns (lightweight)
        self.faction_patterns = self.config.get("faction_patterns", {
            "rebel": ["rebel", "alliance", "resistance"],
            "imperial": ["imperial", "empire"],
            "neutral": ["neutral", "independent"],
            "jedi": ["jedi", "force user"],
            "sith": ["sith", "dark side"],
            "mandalorian": ["mandalorian", "mando"],
            "hutt": ["hutt", "hutt cartel"],
            "black sun": ["black sun", "blacksun"],
            "corsec": ["corsec", "corporate sector"],
            "smuggler": ["smuggler", "criminal"]
        })
        
        # Privacy settings
        self.privacy_enabled = self.config.get("privacy_enabled", True)
        self.opt_out_keywords = self.config.get("opt_out_keywords", [
            "private", "no scan", "opt out", "do not track"
        ])
        
        # Load existing data
        self._load_existing_data()
        
        logger.info("[PASSIVE-SCANNER] Passive player scanner initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load scanner configuration."""
        if not os.path.exists(self.config_path):
            logger.warning(f"[PASSIVE-SCANNER] Config file not found: {self.config_path}")
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"[PASSIVE-SCANNER] Loaded config from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] Failed to load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "scan_interval": 60,
            "idle_scan_interval": 300,
            "travel_scan_interval": 30,
            "ocr_confidence_threshold": 50.0,
            "privacy_enabled": True,
            "opt_out_keywords": ["private", "no scan", "opt out", "do not track"],
            "scan_regions": {
                "nearby_area": (100, 100, 500, 400),
                "chat_window": (50, 400, 600, 500),
                "target_info": (700, 100, 900, 200),
                "group_window": (800, 200, 1000, 400)
            },
            "name_patterns": [
                r'^[A-Z][a-z]+[A-Z][a-z]+$',
                r'^[A-Z][a-z]+_[A-Z][a-z]+$',
                r'^[A-Z][a-z]+[0-9]+$'
            ],
            "guild_patterns": [
                r'\[([^\]]+)\]',
                r'<([^>]+)>'
            ],
            "title_patterns": [
                r'([A-Z][a-z]+ [A-Z][a-z]+)',
                r'([A-Z][a-z]+ of [A-Z][a-z]+)'
            ],
            "race_patterns": {
                "human": ["human", "humanoid"],
                "wookiee": ["wookiee", "wookie"],
                "twilek": ["twilek", "twi'lek"],
                "zabrak": ["zabrak"],
                "ithorian": ["ithorian", "hammerhead"],
                "rodian": ["rodian"],
                "mon calamari": ["mon calamari", "moncal"],
                "sullustan": ["sullustan"],
                "togruta": ["togruta"],
                "kel dor": ["kel dor", "kel-dor"],
                "chiss": ["chiss"],
                "trandoshan": ["trandoshan"],
                "geonosian": ["geonosian"],
                "gotal": ["gotal"],
                "quarren": ["quarren"],
                "aqualish": ["aqualish"],
                "gran": ["gran"],
                "duros": ["duros"],
                "neimoidian": ["neimoidian"],
                "weequay": ["weequay"]
            },
            "faction_patterns": {
                "rebel": ["rebel", "alliance", "resistance"],
                "imperial": ["imperial", "empire"],
                "neutral": ["neutral", "independent"],
                "jedi": ["jedi", "force user"],
                "sith": ["sith", "dark side"],
                "mandalorian": ["mandalorian", "mando"],
                "hutt": ["hutt", "hutt cartel"],
                "black sun": ["black sun", "blacksun"],
                "corsec": ["corsec", "corporate sector"],
                "smuggler": ["smuggler", "criminal"]
            }
        }
    
    def _load_existing_data(self) -> None:
        """Load existing scan data."""
        try:
            # Load player registry
            if os.path.exists(self.registry_file):
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "players" in data:
                    for player_name, player_data in data["players"].items():
                        self.player_registry[player_name] = PlayerRegistryEntry(**player_data)
                
                if "opt_out_players" in data:
                    self.opt_out_players = set(data["opt_out_players"])
                
                logger.info(f"[PASSIVE-SCANNER] Loaded {len(self.player_registry)} players from registry")
                logger.info(f"[PASSIVE-SCANNER] Loaded {len(self.opt_out_players)} opt-out players")
            
            # Load scan history
            if os.path.exists(self.scans_file):
                with open(self.scans_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if "scans" in data:
                    for scan_data in data["scans"]:
                        self.scan_history.append(PassivePlayerScan(**scan_data))
                
                logger.info(f"[PASSIVE-SCANNER] Loaded {len(self.scan_history)} scans")
                
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] Error loading existing data: {e}")
    
    def _save_data(self) -> None:
        """Save scan data to files."""
        try:
            # Save player registry
            registry_data = {
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "total_players": len(self.player_registry),
                    "total_scans": len(self.scan_history),
                    "scanner_version": "1.0"
                },
                "players": {
                    name: asdict(profile) for name, profile in self.player_registry.items()
                },
                "opt_out_players": list(self.opt_out_players)
            }
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            
            # Save scan history
            scan_data = {
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "total_scans": len(self.scan_history),
                    "scanner_version": "1.0"
                },
                "scans": [
                    asdict(scan) for scan in self.scan_history[-1000:]  # Keep last 1000
                ]
            }
            
            with open(self.scans_file, 'w', encoding='utf-8') as f:
                json.dump(scan_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[PASSIVE-SCANNER] Saved {len(self.player_registry)} players, {len(self.scan_history)} scans")
            
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] Error saving data: {e}")
    
    def start_scanning(self) -> None:
        """Start automatic passive scanning."""
        if self.is_running:
            logger.warning("[PASSIVE-SCANNER] Scanning already running")
            return
        
        self.is_running = True
        self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.scan_thread.start()
        logger.info("[PASSIVE-SCANNER] Automatic passive scanning started")
    
    def stop_scanning(self) -> None:
        """Stop automatic passive scanning."""
        self.is_running = False
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
        self._save_data()
        logger.info("[PASSIVE-SCANNER] Automatic passive scanning stopped")
    
    def set_mode(self, mode: str) -> None:
        """Set scanner mode (idle, travel, combat)."""
        if mode in ["idle", "travel", "combat"]:
            self.current_mode = mode
            logger.info(f"[PASSIVE-SCANNER] Mode set to: {mode}")
        else:
            logger.warning(f"[PASSIVE-SCANNER] Invalid mode: {mode}")
    
    def _get_scan_interval(self) -> int:
        """Get scan interval based on current mode."""
        if self.current_mode == "travel":
            return self.travel_scan_interval
        elif self.current_mode == "combat":
            return self.scan_interval * 2  # Slower during combat
        else:
            return self.idle_scan_interval
    
    def _scan_loop(self) -> None:
        """Background scanning loop."""
        while self.is_running:
            try:
                current_time = time.time()
                scan_interval = self._get_scan_interval()
                
                if current_time - self.last_scan_time >= scan_interval:
                    self._perform_passive_scan()
                    self.last_scan_time = current_time
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"[PASSIVE-SCANNER] Error in scan loop: {e}")
                time.sleep(10)  # Brief pause on error
    
    def _perform_passive_scan(self) -> None:
        """Perform a single passive scan."""
        try:
            # Capture screen regions
            for region_name, coords in self.scan_regions.items():
                scans = self._scan_region_passive(region_name, coords)
                
                # Process scans
                for scan in scans:
                    self._process_passive_scan(scan)
            
            # Auto-save periodically
            if len(self.scan_history) % 20 == 0:  # Save every 20 scans
                self._save_data()
                
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] Error in passive scan: {e}")
    
    def _scan_region_passive(self, region_name: str, coords: Tuple[int, int, int, int]) -> List[PassivePlayerScan]:
        """Scan a specific screen region for players (passive mode)."""
        scans = []
        
        try:
            # Capture screen region
            screenshot = ImageGrab.grab(bbox=coords)
            screenshot_np = np.array(screenshot)
            
            # Convert to grayscale for OCR
            gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)
            
            # Perform OCR with lower confidence threshold for passive scanning
            text_data = self._extract_text_with_confidence(gray)
            
            if text_data["confidence"] >= self.ocr_confidence_threshold:
                # Parse text for lightweight player information
                players = self._parse_player_text_passive(text_data["text"])
                
                for player_data in players:
                    # Check for opt-out keywords
                    if self._check_opt_out(player_data["name"], text_data["text"]):
                        continue
                    
                    scan = PassivePlayerScan(
                        name=player_data["name"],
                        guild=player_data.get("guild"),
                        title=player_data.get("title"),
                        race=player_data.get("race"),
                        faction=player_data.get("faction"),
                        confidence=text_data["confidence"],
                        source=region_name
                    )
                    scans.append(scan)
            
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] Error scanning region {region_name}: {e}")
        
        return scans
    
    def _extract_text_with_confidence(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text from image with confidence score."""
        try:
            # Configure OCR for passive scanning (faster, less accurate)
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789[]<>(){}:;.,!?-_ '
            
            # Perform OCR
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # Get confidence data
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "text": text.strip(),
                "confidence": avg_confidence,
                "word_count": len(text.split())
            }
            
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] OCR error: {e}")
            return {"text": "", "confidence": 0, "word_count": 0}
    
    def _parse_player_text_passive(self, text: str) -> List[Dict[str, Any]]:
        """Parse text for lightweight player information."""
        players = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            player_data = self._extract_player_info_passive(line)
            if player_data:
                players.append(player_data)
        
        return players
    
    def _extract_player_info_passive(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract lightweight player information from text line."""
        try:
            player_data = {"name": None}
            
            # Extract name using patterns
            for pattern in self.name_patterns:
                match = re.search(pattern, text)
                if match:
                    player_data["name"] = match.group(0)
                    break
            
            if not player_data["name"]:
                # Try to extract any capitalized word as name
                words = text.split()
                for word in words:
                    if re.match(r'^[A-Z][a-z]+[A-Za-z0-9]*$', word):
                        player_data["name"] = word
                        break
            
            if not player_data["name"]:
                return None
            
            # Extract guild (lightweight)
            for pattern in self.guild_patterns:
                match = re.search(pattern, text)
                if match:
                    player_data["guild"] = match.group(1)
                    break
            
            # Extract title (lightweight)
            for pattern in self.title_patterns:
                match = re.search(pattern, text)
                if match:
                    title = match.group(1)
                    # Avoid capturing guild names as titles
                    if title != player_data.get("guild"):
                        player_data["title"] = title
                        break
            
            # Extract race/species (lightweight)
            text_lower = text.lower()
            for race, patterns in self.race_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        player_data["race"] = race
                        break
                if player_data.get("race"):
                    break
            
            # Extract faction (lightweight)
            for faction, patterns in self.faction_patterns.items():
                for pattern in patterns:
                    if pattern in text_lower:
                        player_data["faction"] = faction
                        break
                if player_data.get("faction"):
                    break
            
            return player_data
            
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] Error extracting player info: {e}")
            return None
    
    def _check_opt_out(self, player_name: str, text: str) -> bool:
        """Check if player has opted out of scanning."""
        if not self.privacy_enabled:
            return False
        
        # Check if player is in opt-out list
        if player_name in self.opt_out_players:
            return True
        
        # Check for opt-out keywords in text
        text_lower = text.lower()
        for keyword in self.opt_out_keywords:
            if keyword in text_lower:
                self.opt_out_players.add(player_name)
                logger.info(f"[PASSIVE-SCANNER] Player {player_name} opted out")
                return True
        
        return False
    
    def _process_passive_scan(self, scan: PassivePlayerScan) -> None:
        """Process a new passive player scan."""
        try:
            # Check if this is a recent scan to avoid duplicates
            scan_key = f"{scan.name}_{scan.timestamp}"
            if scan_key in self.recent_scans:
                return
            
            # Add to recent scans
            self.recent_scans.add(scan_key)
            
            # Add to scan history
            self.scan_history.append(scan)
            
            # Update player registry
            if scan.name in self.player_registry:
                entry = self.player_registry[scan.name]
                entry.total_scans += 1
                entry.last_seen = scan.timestamp
                
                # Update information if new data is available
                if scan.guild and not entry.guild:
                    entry.guild = scan.guild
                if scan.title and not entry.title:
                    entry.title = scan.title
                if scan.race and not entry.race:
                    entry.race = scan.race
                if scan.faction and not entry.faction:
                    entry.faction = scan.faction
                
                # Add location if new
                if scan.location and scan.location not in entry.locations_seen:
                    entry.locations_seen.append(scan.location)
                
                # Calculate scan frequency
                first_seen = datetime.fromisoformat(entry.first_seen)
                last_seen = datetime.fromisoformat(entry.last_seen)
                days_active = (last_seen - first_seen).days + 1
                entry.scan_frequency = entry.total_scans / days_active
                
            else:
                # Create new player registry entry
                entry = PlayerRegistryEntry(
                    name=scan.name,
                    guild=scan.guild,
                    title=scan.title,
                    race=scan.race,
                    faction=scan.faction,
                    first_seen=scan.timestamp,
                    last_seen=scan.timestamp,
                    total_scans=1,
                    locations_seen=[scan.location] if scan.location else [],
                    scan_frequency=1.0
                )
                self.player_registry[scan.name] = entry
            
            logger.debug(f"[PASSIVE-SCANNER] Scanned player: {scan.name} ({scan.guild or 'No Guild'})")
            
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] Error processing scan: {e}")
    
    def manual_passive_scan(self) -> List[PassivePlayerScan]:
        """Perform a manual passive scan."""
        scans = []
        
        try:
            for region_name, coords in self.scan_regions.items():
                region_scans = self._scan_region_passive(region_name, coords)
                scans.extend(region_scans)
                
                for scan in region_scans:
                    self._process_passive_scan(scan)
            
            logger.info(f"[PASSIVE-SCANNER] Manual scan found {len(scans)} players")
            return scans
            
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] Error in manual scan: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get passive scanner statistics."""
        try:
            total_scans = len(self.scan_history)
            unique_players = len(self.player_registry)
            
            # Calculate recent activity (last 24 hours)
            now = datetime.now()
            recent_scans = [
                s for s in self.scan_history 
                if (now - datetime.fromisoformat(s.timestamp)).total_seconds() < 86400
            ]
            
            # Guild statistics
            guild_counts = {}
            for entry in self.player_registry.values():
                if entry.guild:
                    guild_counts[entry.guild] = guild_counts.get(entry.guild, 0) + 1
            
            # Faction statistics
            faction_counts = {}
            for entry in self.player_registry.values():
                if entry.faction:
                    faction_counts[entry.faction] = faction_counts.get(entry.faction, 0) + 1
            
            # Race statistics
            race_counts = {}
            for entry in self.player_registry.values():
                if entry.race:
                    race_counts[entry.race] = race_counts.get(entry.race, 0) + 1
            
            return {
                "total_scans": total_scans,
                "unique_players": unique_players,
                "recent_scans_24h": len(recent_scans),
                "guild_distribution": guild_counts,
                "faction_distribution": faction_counts,
                "race_distribution": race_counts,
                "opt_out_players": len(self.opt_out_players),
                "scanner_running": self.is_running,
                "current_mode": self.current_mode,
                "last_scan_time": self.last_scan_time
            }
            
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] Error getting statistics: {e}")
            return {}
    
    def export_for_swgdb(self) -> Dict[str, Any]:
        """Export data for SWGDB population."""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "scanner_version": "1.0",
                "players": [],
                "scans": []
            }
            
            # Export player registry
            for entry in self.player_registry.values():
                player_export = {
                    "name": entry.name,
                    "guild": entry.guild,
                    "title": entry.title,
                    "race": entry.race,
                    "faction": entry.faction,
                    "first_seen": entry.first_seen,
                    "last_seen": entry.last_seen,
                    "total_scans": entry.total_scans,
                    "scan_frequency": entry.scan_frequency,
                    "locations_seen": entry.locations_seen
                }
                export_data["players"].append(player_export)
            
            # Export recent scans
            recent_scans = self.scan_history[-100:]  # Last 100 scans
            for scan in recent_scans:
                scan_export = {
                    "name": scan.name,
                    "guild": scan.guild,
                    "title": scan.title,
                    "race": scan.race,
                    "faction": scan.faction,
                    "timestamp": scan.timestamp,
                    "location": scan.location,
                    "confidence": scan.confidence,
                    "source": scan.source
                }
                export_data["scans"].append(scan_export)
            
            return export_data
            
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] Error exporting for SWGDB: {e}")
            return {}
    
    def add_opt_out_player(self, player_name: str) -> None:
        """Add player to opt-out list."""
        self.opt_out_players.add(player_name)
        logger.info(f"[PASSIVE-SCANNER] Added {player_name} to opt-out list")
    
    def remove_opt_out_player(self, player_name: str) -> None:
        """Remove player from opt-out list."""
        if player_name in self.opt_out_players:
            self.opt_out_players.remove(player_name)
            logger.info(f"[PASSIVE-SCANNER] Removed {player_name} from opt-out list")
    
    def update_location(self, location: str) -> None:
        """Update current location for scan tracking."""
        try:
            # Update location for new scans
            for scan in self.scan_history[-10:]:  # Update recent scans
                scan.location = location
            
            logger.info(f"[PASSIVE-SCANNER] Location updated: {location}")
            
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] Error updating location: {e}")
    
    def cleanup(self) -> None:
        """Cleanup scanner resources."""
        try:
            self.stop_scanning()
            self._save_data()
            logger.info("[PASSIVE-SCANNER] Cleanup completed")
            
        except Exception as e:
            logger.error(f"[PASSIVE-SCANNER] Error during cleanup: {e}")


# Global scanner instance
passive_scanner = PassivePlayerScanner()


@requires_license
def start_passive_scanning() -> None:
    """Start automatic passive player scanning."""
    passive_scanner.start_scanning()


@requires_license
def stop_passive_scanning() -> None:
    """Stop automatic passive player scanning."""
    passive_scanner.stop_scanning()


@requires_license
def manual_passive_scan() -> List[PassivePlayerScan]:
    """Perform a manual passive player scan."""
    return passive_scanner.manual_passive_scan()


@requires_license
def get_passive_scan_statistics() -> Dict[str, Any]:
    """Get passive scanning statistics."""
    return passive_scanner.get_statistics()


@requires_license
def export_passive_data_for_swgdb() -> Dict[str, Any]:
    """Export passive scan data for SWGDB population."""
    return passive_scanner.export_for_swgdb()


@requires_license
def set_passive_scanner_mode(mode: str) -> None:
    """Set passive scanner mode (idle, travel, combat)."""
    passive_scanner.set_mode(mode)


@requires_license
def update_passive_scan_location(location: str) -> None:
    """Update current location for passive scanning."""
    passive_scanner.update_location(location)


@requires_license
def add_opt_out_player(player_name: str) -> None:
    """Add player to opt-out list."""
    passive_scanner.add_opt_out_player(player_name)


@requires_license
def remove_opt_out_player(player_name: str) -> None:
    """Remove player from opt-out list."""
    passive_scanner.remove_opt_out_player(player_name)


if __name__ == "__main__":
    # Test the passive scanner
    print("🎮 Passive Player Scanner - Batch 178")
    print("=" * 50)
    
    # Start scanning
    start_passive_scanning()
    
    try:
        # Set to travel mode
        set_passive_scanner_mode("travel")
        
        # Run for a few seconds
        time.sleep(10)
        
        # Get statistics
        stats = get_passive_scan_statistics()
        print(f"Passive Scanner Statistics: {stats}")
        
        # Manual scan
        scans = manual_passive_scan()
        print(f"Manual scan found {len(scans)} players")
        
    finally:
        # Stop scanning
        stop_passive_scanning()
        print("Passive scanner stopped") 
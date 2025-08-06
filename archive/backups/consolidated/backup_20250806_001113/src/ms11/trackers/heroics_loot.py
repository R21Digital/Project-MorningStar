#!/usr/bin/env python3
"""
MS11 Heroics Loot Tracker - Phase 1
Parses bot session logs to extract loot received from Heroic instances.
"""

import json
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

class HeroicsLootTracker:
    """Tracks and processes loot from Heroic instances."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        self.loot_logs_dir = Path(self.config.get('loot_logs_dir', 'src/data/loot_logs'))
        self.loot_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Heroic instance patterns for log parsing
        self.heroic_patterns = {
            'axkva_min': [
                r'Axkva Min.*?defeated',
                r'You have received.*?from Axkva Min',
                r'Loot:.*?Axkva Min'
            ],
            'ig_88': [
                r'IG-88.*?destroyed',
                r'You have received.*?from IG-88',
                r'Loot:.*?IG-88'
            ],
            'geonosian_queen': [
                r'Geonosian Queen.*?defeated', 
                r'You have received.*?from.*?Queen',
                r'Loot:.*?Queen'
            ],
            'nightsister_stronghold': [
                r'Sister.*?defeated',
                r'You have received.*?from.*?Sister',
                r'Loot:.*?Stronghold'
            ],
            'krayt_dragon': [
                r'Ancient Krayt.*?defeated',
                r'You have received.*?from.*?Krayt',
                r'Loot:.*?Krayt'
            ]
        }
        
        # Loot item patterns
        self.loot_patterns = {
            'item_received': r'You have received\s+(.+?)(?:\s+\[|$)',
            'item_name': r'(?:received|found|obtained)\s+(.+?)(?:\s+\[|$)',
            'quantity': r'(\d+)x?\s+(.+)',
            'rarity': r'\[(Common|Uncommon|Rare|Epic|Legendary)\]',
            'stats': r'(\d+)-(\d+)\s+(damage|armor|force)',
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'loot_logs_dir': 'src/data/loot_logs',
            'session_logs_dir': 'data/session_logs',
            'max_log_age_days': 30,
            'backup_logs': True,
            'validate_items': True,
            'heroic_timeout_minutes': 120
        }
    
    def parse_session_logs(self, session_logs_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """Parse session logs to extract heroic loot data."""
        logs_dir = Path(session_logs_dir or self.config['session_logs_dir'])
        if not logs_dir.exists():
            self.logger.warning(f"Session logs directory not found: {logs_dir}")
            return []
        
        loot_entries = []
        
        # Process log files
        for log_file in logs_dir.glob('*.log'):
            try:
                entries = self._parse_log_file(log_file)
                loot_entries.extend(entries)
                self.logger.info(f"Parsed {len(entries)} loot entries from {log_file.name}")
            except Exception as e:
                self.logger.error(f"Error parsing log file {log_file}: {e}")
        
        return loot_entries
    
    def _parse_log_file(self, log_file: Path) -> List[Dict[str, Any]]:
        """Parse individual log file for heroic loot."""
        entries = []
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Split into potential sessions
        session_blocks = self._split_into_sessions(content)
        
        for session_block in session_blocks:
            session_entries = self._parse_session_block(session_block, log_file.name)
            entries.extend(session_entries)
        
        return entries
    
    def _split_into_sessions(self, content: str) -> List[str]:
        """Split log content into session blocks."""
        # Look for session start markers
        session_markers = [
            r'\[Session Start\]',
            r'Loading character:',
            r'Entering game world',
            r'MS11 Bot Started'
        ]
        
        blocks = []
        current_block = []
        
        for line in content.split('\n'):
            # Check if this line starts a new session
            is_session_start = any(re.search(marker, line, re.IGNORECASE) for marker in session_markers)
            
            if is_session_start and current_block:
                blocks.append('\n'.join(current_block))
                current_block = []
            
            current_block.append(line)
        
        # Add final block
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return blocks
    
    def _parse_session_block(self, session_block: str, log_filename: str) -> List[Dict[str, Any]]:
        """Parse a session block for heroic loot."""
        entries = []
        lines = session_block.split('\n')
        
        # Extract session metadata
        session_metadata = self._extract_session_metadata(session_block)
        
        # Look for heroic activity
        for i, line in enumerate(lines):
            heroic_type = self._detect_heroic_type(line)
            if heroic_type:
                # Parse surrounding lines for loot
                context_lines = lines[max(0, i-10):min(len(lines), i+20)]
                loot_items = self._extract_loot_from_context(context_lines, heroic_type)
                
                for item in loot_items:
                    timestamp = self._extract_timestamp(line)
                    if not timestamp:
                        # Use current time as fallback but make it recent for testing
                        timestamp = datetime.now(timezone.utc).isoformat()
                    
                    entry = {
                        'timestamp': timestamp,
                        'player_name': session_metadata.get('player_name', 'Unknown'),
                        'heroic_instance': heroic_type,
                        'boss_name': self._extract_boss_name(line, heroic_type),
                        'item_name': item['name'],
                        'item_type': item.get('type', 'unknown'),
                        'rarity': item.get('rarity', 'common'),
                        'quantity': item.get('quantity', 1),
                        'stats': item.get('stats', {}),
                        'source_log': log_filename,
                        'completion_status': 'completed',
                        'difficulty': session_metadata.get('difficulty', 'normal'),
                        'group_size': session_metadata.get('group_size', 1),
                        'session_id': session_metadata.get('session_id'),
                        'raw_log_line': line.strip()
                    }
                    entries.append(entry)
        
        return entries
    
    def _detect_heroic_type(self, line: str) -> Optional[str]:
        """Detect which heroic instance this line refers to."""
        for heroic_type, patterns in self.heroic_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return heroic_type
        return None
    
    def _extract_loot_from_context(self, context_lines: List[str], heroic_type: str) -> List[Dict[str, Any]]:
        """Extract loot items from context lines around heroic activity."""
        items = []
        
        for line in context_lines:
            # Look for loot received patterns
            if 'You have received' in line:
                match = re.search(self.loot_patterns['item_received'], line, re.IGNORECASE)
                if match:
                    received_text = match.group(1).strip()
                    
                    # Parse quantity and item name
                    quantity = 1
                    item_name = received_text
                    
                    # Check for quantity pattern (e.g., "2x Item Name" or "5x Item")
                    quantity_match = re.match(r'(\d+)x?\s+(.+)', received_text)
                    if quantity_match:
                        quantity = int(quantity_match.group(1))
                        item_name = quantity_match.group(2).strip()
                    
                    if self._is_valid_item_name(item_name):
                        item = {
                            'name': item_name,
                            'type': self._classify_item_type(item_name),
                            'rarity': self._extract_rarity(line),
                            'quantity': quantity,
                            'stats': self._extract_stats(line)
                        }
                        items.append(item)
        
        return items
    
    def _extract_session_metadata(self, session_block: str) -> Dict[str, Any]:
        """Extract metadata from session block."""
        metadata = {}
        
        # Player name
        player_match = re.search(r'Player:\s*([^\n\r]+)', session_block, re.IGNORECASE)
        if player_match:
            metadata['player_name'] = player_match.group(1).strip()
        
        # Session ID
        session_match = re.search(r'Session ID:\s*([^\n\r]+)', session_block, re.IGNORECASE)
        if session_match:
            metadata['session_id'] = session_match.group(1).strip()
        
        # Group size
        group_match = re.search(r'Group size:\s*(\d+)', session_block, re.IGNORECASE)
        if group_match:
            metadata['group_size'] = int(group_match.group(1))
        
        # Difficulty
        if re.search(r'heroic|hard|nightmare', session_block, re.IGNORECASE):
            metadata['difficulty'] = 'heroic'
        else:
            metadata['difficulty'] = 'normal'
        
        return metadata
    
    def _extract_timestamp(self, line: str) -> Optional[str]:
        """Extract timestamp from log line."""
        # Common timestamp patterns
        patterns = [
            r'\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]',
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
            r'(\d{2}:\d{2}:\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(1)
                try:
                    # Try to parse and convert to ISO format
                    if 'T' in timestamp_str:
                        return timestamp_str
                    elif '-' in timestamp_str and ' ' in timestamp_str:
                        # Format: "2025-01-27 10:30:05"
                        dt = datetime.fromisoformat(timestamp_str)
                        return dt.replace(tzinfo=timezone.utc).isoformat()
                    elif '-' in timestamp_str:
                        dt = datetime.fromisoformat(timestamp_str.replace(' ', 'T'))
                        return dt.replace(tzinfo=timezone.utc).isoformat()
                    else:
                        # Time only, use today's date
                        today = datetime.now().date()
                        dt = datetime.combine(today, datetime.strptime(timestamp_str, '%H:%M:%S').time())
                        return dt.replace(tzinfo=timezone.utc).isoformat()
                except ValueError:
                    continue
        
        return None
    
    def _extract_boss_name(self, line: str, heroic_type: str) -> str:
        """Extract boss name from log line."""
        boss_patterns = {
            'axkva_min': r'(Axkva Min)',
            'ig_88': r'(IG-88)',
            'geonosian_queen': r'(Geonosian Queen|Queen)',
            'nightsister_stronghold': r'(Sister [A-Za-z]+|Nightsister [A-Za-z]+)',
            'krayt_dragon': r'(Ancient Krayt Dragon|Krayt Dragon)'
        }
        
        if heroic_type in boss_patterns:
            match = re.search(boss_patterns[heroic_type], line, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return heroic_type.replace('_', ' ').title()
    
    def _is_valid_item_name(self, item_name: str) -> bool:
        """Validate if this is a real item name."""
        if not item_name or len(item_name) < 3:
            return False
        
        # Filter out common false positives
        false_positives = [
            'experience', 'credits', 'xp', 'health', 'action', 'mind',
            'you', 'the', 'and', 'or', 'but', 'from', 'to'
        ]
        
        return item_name.lower() not in false_positives
    
    def _classify_item_type(self, item_name: str) -> str:
        """Classify item type based on name."""
        item_name_lower = item_name.lower()
        
        type_keywords = {
            'weapon': ['sword', 'saber', 'rifle', 'pistol', 'carbine', 'blade', 'staff'],
            'armor': ['armor', 'helmet', 'boots', 'gloves', 'chest', 'leggings'],
            'accessory': ['ring', 'necklace', 'earring', 'bracelet', 'pendant'],
            'material': ['crystal', 'ore', 'hide', 'bone', 'essence', 'fragment'],
            'consumable': ['stim', 'food', 'drink', 'medicine', 'buff'],
            'currency': ['credit', 'token', 'badge', 'coin'],
            'cosmetic': ['decoration', 'painting', 'statue', 'furniture']
        }
        
        for item_type, keywords in type_keywords.items():
            if any(keyword in item_name_lower for keyword in keywords):
                return item_type
        
        return 'misc'
    
    def _extract_rarity(self, line: str) -> str:
        """Extract item rarity from line."""
        match = re.search(self.loot_patterns['rarity'], line, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        return 'common'
    
    def _extract_quantity(self, line: str) -> int:
        """Extract item quantity from line."""
        match = re.search(self.loot_patterns['quantity'], line)
        if match:
            return int(match.group(1))
        return 1
    
    def _extract_stats(self, line: str) -> Dict[str, Any]:
        """Extract item stats from line."""
        stats = {}
        match = re.search(self.loot_patterns['stats'], line)
        if match:
            min_val, max_val, stat_type = match.groups()
            stats[stat_type] = f"{min_val}-{max_val}"
        return stats
    
    def store_loot_data(self, loot_entries: List[Dict[str, Any]]) -> str:
        """Store loot data to persistent storage."""
        if not loot_entries:
            self.logger.warning("No loot entries to store")
            return ""
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"heroic_loot_logs_{timestamp}.json"
        filepath = self.loot_logs_dir / filename
        
        # Prepare data with metadata
        data = {
            'metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'version': '1.0',
                'total_entries': len(loot_entries),
                'heroic_instances': list(set(entry['heroic_instance'] for entry in loot_entries)),
                'date_range': {
                    'start': min(entry['timestamp'] for entry in loot_entries),
                    'end': max(entry['timestamp'] for entry in loot_entries)
                }
            },
            'loot_entries': loot_entries
        }
        
        # Write to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Stored {len(loot_entries)} loot entries to {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error storing loot data: {e}")
            raise
    
    def get_recent_loot_data(self, heroic_type: Optional[str] = None, 
                           hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent loot data from storage."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        all_entries = []
        
        # Load all loot log files
        for log_file in self.loot_logs_dir.glob('heroic_loot_logs_*.json'):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_entries.extend(data.get('loot_entries', []))
            except Exception as e:
                self.logger.error(f"Error loading loot file {log_file}: {e}")
        
        # Filter by time and heroic type
        filtered_entries = []
        for entry in all_entries:
            try:
                entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                # Make cutoff_time offset-aware if entry_time is offset-aware
                if entry_time.tzinfo is not None and cutoff_time.tzinfo is None:
                    cutoff_time = cutoff_time.replace(tzinfo=timezone.utc)
                elif entry_time.tzinfo is None and cutoff_time.tzinfo is not None:
                    entry_time = entry_time.replace(tzinfo=timezone.utc)
                
                if entry_time >= cutoff_time:
                    if not heroic_type or entry['heroic_instance'] == heroic_type:
                        filtered_entries.append(entry)
            except (ValueError, KeyError):
                continue
        
        return filtered_entries
    
    def get_loot_statistics(self, heroic_type: Optional[str] = None) -> Dict[str, Any]:
        """Get loot statistics for analysis."""
        entries = self.get_recent_loot_data(heroic_type, hours=24*7)  # Last week
        
        if not entries:
            return {'total_entries': 0}
        
        # Calculate statistics
        stats = {
            'total_entries': len(entries),
            'unique_items': len(set(entry['item_name'] for entry in entries)),
            'heroic_breakdown': {},
            'rarity_distribution': {},
            'type_distribution': {},
            'most_common_items': {},
            'date_range': {
                'start': min(entry['timestamp'] for entry in entries),
                'end': max(entry['timestamp'] for entry in entries)
            }
        }
        
        # Count by heroic
        for entry in entries:
            heroic = entry['heroic_instance']
            stats['heroic_breakdown'][heroic] = stats['heroic_breakdown'].get(heroic, 0) + 1
        
        # Count by rarity
        for entry in entries:
            rarity = entry.get('rarity', 'common')
            stats['rarity_distribution'][rarity] = stats['rarity_distribution'].get(rarity, 0) + 1
        
        # Count by type
        for entry in entries:
            item_type = entry.get('item_type', 'misc')
            stats['type_distribution'][item_type] = stats['type_distribution'].get(item_type, 0) + 1
        
        # Most common items
        item_counts = {}
        for entry in entries:
            item_name = entry['item_name']
            item_counts[item_name] = item_counts.get(item_name, 0) + 1
        
        stats['most_common_items'] = dict(sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return stats

def main():
    """Demo the heroics loot tracker."""
    logging.basicConfig(level=logging.INFO)
    
    tracker = HeroicsLootTracker()
    
    # Parse session logs
    print("Parsing session logs for heroic loot...")
    loot_entries = tracker.parse_session_logs()
    
    if loot_entries:
        print(f"Found {len(loot_entries)} loot entries")
        
        # Store the data
        filepath = tracker.store_loot_data(loot_entries)
        print(f"Stored loot data to: {filepath}")
        
        # Show statistics
        stats = tracker.get_loot_statistics()
        print(f"Statistics: {json.dumps(stats, indent=2)}")
    else:
        print("No loot entries found in session logs")

if __name__ == "__main__":
    main()
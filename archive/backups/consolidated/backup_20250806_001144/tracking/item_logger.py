#!/usr/bin/env python3
"""
Item Discovery Tracker + Vendor Log Recorder for SWG

This module provides comprehensive tracking of vendors and items discovered by the bot,
including item names, costs, sellers, timestamps, and searchable archives.

Author: SWG Bot Development Team
"""

import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from collections import defaultdict, Counter
import statistics
import re

# Item Categories
class ItemCategory(Enum):
    ARMOR = "armor"
    WEAPONS = "weapons"
    BUFFS = "buffs"
    CONSUMABLES = "consumables"
    UTILITIES = "utilities"
    ENHANCEMENTS = "enhancements"
    CRAFTING_MATERIALS = "crafting_materials"
    DECORATIONS = "decorations"
    CLOTHING = "clothing"
    FOOD = "food"
    MEDICAL = "medical"
    UNKNOWN = "unknown"

# Vendor Types
class VendorType(Enum):
    ARMORSMITH = "armorsmith"
    WEAPONSMITH = "weaponsmith"
    TAILOR = "tailor"
    ARCHITECT = "architect"
    DOCTOR = "doctor"
    ENTERTAINER = "entertainer"
    MERCHANT = "merchant"
    BAZAAR = "bazaar"
    UNKNOWN = "unknown"

@dataclass
class DiscoveredItem:
    """Represents an item discovered at a vendor."""
    item_name: str
    item_id: str
    category: ItemCategory
    cost: int
    vendor_id: str
    vendor_name: str
    vendor_type: VendorType
    planet: str
    location: str
    coordinates: Tuple[float, float]
    timestamp: datetime
    quality: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    resists: Optional[Dict[str, Any]] = None
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['coordinates'] = list(self.coordinates)
        return data

@dataclass
class VendorProfile:
    """Represents a vendor profile with discovered items."""
    vendor_id: str
    vendor_name: str
    vendor_type: VendorType
    planet: str
    location: str
    coordinates: Tuple[float, float]
    first_discovered: datetime
    last_visited: datetime
    total_visits: int
    items_discovered: int
    average_item_cost: float
    most_expensive_item: Optional[str] = None
    most_expensive_cost: int = 0
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['first_discovered'] = self.first_discovered.isoformat()
        data['last_visited'] = self.last_visited.isoformat()
        data['coordinates'] = list(self.coordinates)
        return data

@dataclass
class DiscoverySession:
    """Represents a discovery session with multiple vendors."""
    session_id: str
    character_name: str
    start_time: datetime
    end_time: datetime
    planets_visited: List[str]
    vendors_discovered: int
    items_discovered: int
    total_value_discovered: int
    most_valuable_item: Optional[str] = None
    most_valuable_cost: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        return data

class ItemLogger:
    """
    Comprehensive item discovery and vendor tracking system.
    
    Features:
    - Track all vendors visited by the bot
    - Log all items discovered with details
    - Build searchable archive of discoveries
    - Generate vendor profiles and statistics
    - Track discovery sessions and trends
    - Provide Discord alerts for rare items
    """
    
    def __init__(self, 
                 data_dir: str = "data/vendor_history",
                 items_file: str = "discovered_items.json",
                 vendors_file: str = "vendor_profiles.json",
                 sessions_file: str = "discovery_sessions.json",
                 alerts_file: str = "item_alerts.json"):
        """
        Initialize the Item Logger.
        
        Args:
            data_dir: Directory for storing vendor history data
            items_file: File for discovered items
            vendors_file: File for vendor profiles
            sessions_file: File for discovery sessions
            alerts_file: File for item alerts
        """
        self.data_dir = Path(data_dir)
        self.items_file = self.data_dir / items_file
        self.vendors_file = self.data_dir / vendors_file
        self.sessions_file = self.data_dir / sessions_file
        self.alerts_file = self.data_dir / alerts_file
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data storage
        self.discovered_items: Dict[str, DiscoveredItem] = {}
        self.vendor_profiles: Dict[str, VendorProfile] = {}
        self.discovery_sessions: Dict[str, DiscoverySession] = {}
        self.item_alerts: Dict[str, Dict[str, Any]] = {}
        
        # Search indexes
        self.item_name_index: Dict[str, Set[str]] = defaultdict(set)
        self.vendor_type_index: Dict[str, Set[str]] = defaultdict(set)
        self.planet_index: Dict[str, Set[str]] = defaultdict(set)
        self.category_index: Dict[str, Set[str]] = defaultdict(set)
        
        # Load existing data
        self.load_data()
        self.build_search_indexes()
    
    def load_data(self) -> None:
        """Load all data from files."""
        try:
            # Load discovered items
            if self.items_file.exists():
                with open(self.items_file, 'r') as f:
                    items_data = json.load(f)
                    for item_id, item_data in items_data.items():
                        self.discovered_items[item_id] = self._deserialize_item(item_data)
            
            # Load vendor profiles
            if self.vendors_file.exists():
                with open(self.vendors_file, 'r') as f:
                    vendors_data = json.load(f)
                    for vendor_id, vendor_data in vendors_data.items():
                        self.vendor_profiles[vendor_id] = self._deserialize_vendor(vendor_data)
            
            # Load discovery sessions
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r') as f:
                    sessions_data = json.load(f)
                    for session_id, session_data in sessions_data.items():
                        self.discovery_sessions[session_id] = self._deserialize_session(session_data)
            
            # Load item alerts
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r') as f:
                    self.item_alerts = json.load(f)
                    
        except Exception as e:
            print(f"Error loading item logger data: {e}")
    
    def save_data(self) -> None:
        """Save all data to files."""
        try:
            # Save discovered items
            items_data = {
                item_id: item.to_dict() 
                for item_id, item in self.discovered_items.items()
            }
            with open(self.items_file, 'w') as f:
                json.dump(items_data, f, indent=2, default=str)
            
            # Save vendor profiles
            vendors_data = {
                vendor_id: vendor.to_dict() 
                for vendor_id, vendor in self.vendor_profiles.items()
            }
            with open(self.vendors_file, 'w') as f:
                json.dump(vendors_data, f, indent=2, default=str)
            
            # Save discovery sessions
            sessions_data = {
                session_id: session.to_dict() 
                for session_id, session in self.discovery_sessions.items()
            }
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions_data, f, indent=2, default=str)
            
            # Save item alerts
            with open(self.alerts_file, 'w') as f:
                json.dump(self.item_alerts, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error saving item logger data: {e}")
    
    def log_item_discovery(self, item_data: Dict[str, Any]) -> DiscoveredItem:
        """
        Log an item discovery at a vendor.
        
        Args:
            item_data: Item discovery information
            
        Returns:
            Created item record
        """
        # Generate unique item ID
        item_id = f"{item_data['item_name'].lower().replace(' ', '_')}_{int(time.time())}"
        
        # Handle coordinates
        coords = item_data.get('coordinates', (0.0, 0.0))
        if isinstance(coords, list):
            coords = tuple(coords)
        
        # Create discovered item
        item = DiscoveredItem(
            item_name=item_data['item_name'],
            item_id=item_id,
            category=ItemCategory(item_data.get('category', 'unknown')),
            cost=item_data.get('cost', 0),
            vendor_id=item_data['vendor_id'],
            vendor_name=item_data['vendor_name'],
            vendor_type=VendorType(item_data.get('vendor_type', 'unknown')),
            planet=item_data['planet'],
            location=item_data['location'],
            coordinates=coords,
            timestamp=datetime.fromisoformat(item_data.get('timestamp', datetime.now().isoformat())),
            quality=item_data.get('quality'),
            stats=item_data.get('stats'),
            resists=item_data.get('resists'),
            notes=item_data.get('notes', '')
        )
        
        # Add to discovered items
        self.discovered_items[item_id] = item
        
        # Update vendor profile
        self._update_vendor_profile(item)
        
        # Check for alerts
        self._check_item_alerts(item)
        
        # Update search indexes
        self._update_search_indexes(item)
        
        self.save_data()
        return item
    
    def log_vendor_visit(self, vendor_data: Dict[str, Any]) -> VendorProfile:
        """
        Log a vendor visit.
        
        Args:
            vendor_data: Vendor visit information
            
        Returns:
            Updated vendor profile
        """
        vendor_id = vendor_data['vendor_id']
        
        # Handle coordinates
        coords = vendor_data.get('coordinates', (0.0, 0.0))
        if isinstance(coords, list):
            coords = tuple(coords)
        
        if vendor_id not in self.vendor_profiles:
            # Create new vendor profile
            profile = VendorProfile(
                vendor_id=vendor_id,
                vendor_name=vendor_data['vendor_name'],
                vendor_type=VendorType(vendor_data.get('vendor_type', 'unknown')),
                planet=vendor_data['planet'],
                location=vendor_data['location'],
                coordinates=coords,
                first_discovered=datetime.fromisoformat(vendor_data.get('timestamp', datetime.now().isoformat())),
                last_visited=datetime.fromisoformat(vendor_data.get('timestamp', datetime.now().isoformat())),
                total_visits=1,
                items_discovered=0,
                average_item_cost=0.0,
                notes=vendor_data.get('notes', '')
            )
            self.vendor_profiles[vendor_id] = profile
        else:
            # Update existing profile
            profile = self.vendor_profiles[vendor_id]
            profile.last_visited = datetime.fromisoformat(vendor_data.get('timestamp', datetime.now().isoformat()))
            profile.total_visits += 1
            profile.notes = vendor_data.get('notes', profile.notes)
        
        self.save_data()
        return profile
    
    def search_items(self, 
                    item_name: Optional[str] = None,
                    vendor_type: Optional[str] = None,
                    planet: Optional[str] = None,
                    category: Optional[str] = None,
                    min_cost: Optional[int] = None,
                    max_cost: Optional[int] = None,
                    vendor_name: Optional[str] = None) -> List[DiscoveredItem]:
        """
        Search discovered items with various filters.
        
        Args:
            item_name: Item name filter (partial match)
            vendor_type: Vendor type filter
            planet: Planet filter
            category: Item category filter
            min_cost: Minimum cost filter
            max_cost: Maximum cost filter
            vendor_name: Vendor name filter (partial match)
            
        Returns:
            List of matching items
        """
        matching_items = []
        
        for item in self.discovered_items.values():
            # Item name filter
            if item_name and item_name.lower() not in item.item_name.lower():
                continue
            
            # Vendor type filter
            if vendor_type and item.vendor_type.value != vendor_type.lower():
                continue
            
            # Planet filter
            if planet and item.planet.lower() != planet.lower():
                continue
            
            # Category filter
            if category and item.category.value != category.lower():
                continue
            
            # Cost filters
            if min_cost is not None and item.cost < min_cost:
                continue
            if max_cost is not None and item.cost > max_cost:
                continue
            
            # Vendor name filter
            if vendor_name and vendor_name.lower() not in item.vendor_name.lower():
                continue
            
            matching_items.append(item)
        
        # Sort by timestamp (newest first)
        matching_items.sort(key=lambda x: x.timestamp, reverse=True)
        
        return matching_items
    
    def get_vendor_statistics(self, vendor_type: Optional[str] = None, 
                             planet: Optional[str] = None) -> Dict[str, Any]:
        """
        Get vendor statistics.
        
        Args:
            vendor_type: Optional vendor type filter
            planet: Optional planet filter
            
        Returns:
            Vendor statistics
        """
        stats = {
            'total_vendors': 0,
            'total_items': 0,
            'total_value': 0,
            'average_items_per_vendor': 0.0,
            'average_item_cost': 0.0,
            'vendor_types': Counter(),
            'planets': Counter(),
            'most_expensive_item': None,
            'most_expensive_cost': 0,
            'recent_discoveries': []
        }
        
        for vendor in self.vendor_profiles.values():
            if vendor_type and vendor.vendor_type.value != vendor_type.lower():
                continue
            if planet and vendor.planet.lower() != planet.lower():
                continue
            
            stats['total_vendors'] += 1
            stats['vendor_types'][vendor.vendor_type.value] += 1
            stats['planets'][vendor.planet] += 1
        
        # Calculate item statistics
        for item in self.discovered_items.values():
            if vendor_type and item.vendor_type.value != vendor_type.lower():
                continue
            if planet and item.planet.lower() != planet.lower():
                continue
            
            stats['total_items'] += 1
            stats['total_value'] += item.cost
            
            if item.cost > stats['most_expensive_cost']:
                stats['most_expensive_cost'] = item.cost
                stats['most_expensive_item'] = item.item_name
        
        # Calculate averages
        if stats['total_vendors'] > 0:
            stats['average_items_per_vendor'] = stats['total_items'] / stats['total_vendors']
        if stats['total_items'] > 0:
            stats['average_item_cost'] = stats['total_value'] / stats['total_items']
        
        # Get recent discoveries (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_items = [item for item in self.discovered_items.values() 
                       if item.timestamp > recent_cutoff]
        stats['recent_discoveries'] = recent_items[:10]  # Top 10 recent
        
        return stats
    
    def get_discovery_session(self, character_name: str, 
                             start_time: Optional[datetime] = None) -> DiscoverySession:
        """
        Get or create a discovery session for a character.
        
        Args:
            character_name: Name of the character
            start_time: Optional start time (defaults to now)
            
        Returns:
            Discovery session
        """
        session_id = f"{character_name}_{int(time.time())}"
        
        session = DiscoverySession(
            session_id=session_id,
            character_name=character_name,
            start_time=start_time or datetime.now(),
            end_time=datetime.now(),
            planets_visited=[],
            vendors_discovered=0,
            items_discovered=0,
            total_value_discovered=0
        )
        
        self.discovery_sessions[session_id] = session
        return session
    
    def update_discovery_session(self, session_id: str, 
                               items_discovered: List[DiscoveredItem]) -> DiscoverySession:
        """
        Update a discovery session with new discoveries.
        
        Args:
            session_id: Session ID
            items_discovered: List of newly discovered items
            
        Returns:
            Updated session
        """
        if session_id not in self.discovery_sessions:
            return None
        
        session = self.discovery_sessions[session_id]
        session.end_time = datetime.now()
        
        # Update session statistics
        planets_visited = set(session.planets_visited)
        vendors_discovered = set()
        
        for item in items_discovered:
            session.items_discovered += 1
            session.total_value_discovered += item.cost
            planets_visited.add(item.planet)
            vendors_discovered.add(item.vendor_id)
            
            if item.cost > session.most_valuable_cost:
                session.most_valuable_cost = item.cost
                session.most_valuable_item = item.item_name
        
        session.planets_visited = list(planets_visited)
        session.vendors_discovered = len(vendors_discovered)
        
        self.save_data()
        return session
    
    def add_item_alert(self, item_name: str, alert_type: str, 
                      conditions: Dict[str, Any], discord_webhook: Optional[str] = None) -> None:
        """
        Add an item alert for rare or valuable items.
        
        Args:
            item_name: Item name to alert on
            alert_type: Type of alert (rare, valuable, specific)
            conditions: Alert conditions
            discord_webhook: Optional Discord webhook URL
        """
        alert_id = f"{item_name.lower().replace(' ', '_')}_{alert_type}"
        
        self.item_alerts[alert_id] = {
            'item_name': item_name,
            'alert_type': alert_type,
            'conditions': conditions,
            'discord_webhook': discord_webhook,
            'created_at': datetime.now().isoformat(),
            'triggered_count': 0
        }
        
        self.save_data()
    
    def get_my_discovered_items(self, character_name: str, 
                               limit: int = 50) -> List[DiscoveredItem]:
        """
        Get items discovered by a specific character.
        
        Args:
            character_name: Name of the character
            limit: Maximum number of items to return
            
        Returns:
            List of discovered items
        """
        # This would typically filter by character, but for now return recent items
        recent_items = sorted(self.discovered_items.values(), 
                            key=lambda x: x.timestamp, reverse=True)
        return recent_items[:limit]
    
    def export_vendor_data(self, planet: Optional[str] = None, 
                          vendor_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Export vendor data for a specific planet or vendor type.
        
        Args:
            planet: Optional planet filter
            vendor_type: Optional vendor type filter
            
        Returns:
            Exported vendor data
        """
        export_data = {
            'vendors': [],
            'items': [],
            'statistics': {}
        }
        
        # Filter vendors
        for vendor in self.vendor_profiles.values():
            if planet and vendor.planet.lower() != planet.lower():
                continue
            if vendor_type and vendor.vendor_type.value != vendor_type.lower():
                continue
            
            export_data['vendors'].append(vendor.to_dict())
        
        # Filter items
        for item in self.discovered_items.values():
            if planet and item.planet.lower() != planet.lower():
                continue
            if vendor_type and item.vendor_type.value != vendor_type.lower():
                continue
            
            export_data['items'].append(item.to_dict())
        
        # Add statistics
        export_data['statistics'] = self.get_vendor_statistics(vendor_type, planet)
        
        return export_data
    
    def _update_vendor_profile(self, item: DiscoveredItem) -> None:
        """Update vendor profile with new item discovery."""
        vendor_id = item.vendor_id
        
        if vendor_id not in self.vendor_profiles:
            # Create new vendor profile
            profile = VendorProfile(
                vendor_id=vendor_id,
                vendor_name=item.vendor_name,
                vendor_type=item.vendor_type,
                planet=item.planet,
                location=item.location,
                coordinates=item.coordinates,
                first_discovered=item.timestamp,
                last_visited=item.timestamp,
                total_visits=1,
                items_discovered=1,
                average_item_cost=item.cost,
                most_expensive_item=item.item_name,
                most_expensive_cost=item.cost
            )
            self.vendor_profiles[vendor_id] = profile
        else:
            # Update existing profile
            profile = self.vendor_profiles[vendor_id]
            profile.last_visited = item.timestamp
            profile.items_discovered += 1
            
            # Update average cost
            total_cost = profile.average_item_cost * (profile.items_discovered - 1) + item.cost
            profile.average_item_cost = total_cost / profile.items_discovered
            
            # Update most expensive item
            if item.cost > profile.most_expensive_cost:
                profile.most_expensive_cost = item.cost
                profile.most_expensive_item = item.item_name
    
    def _check_item_alerts(self, item: DiscoveredItem) -> None:
        """Check if item triggers any alerts."""
        for alert_id, alert in self.item_alerts.items():
            if alert['item_name'].lower() in item.item_name.lower():
                # Check conditions
                triggered = True
                conditions = alert['conditions']
                
                if 'min_cost' in conditions and item.cost < conditions['min_cost']:
                    triggered = False
                if 'max_cost' in conditions and item.cost > conditions['max_cost']:
                    triggered = False
                if 'vendor_type' in conditions and item.vendor_type.value != conditions['vendor_type']:
                    triggered = False
                
                if triggered:
                    alert['triggered_count'] += 1
                    self._send_discord_alert(item, alert)
    
    def _send_discord_alert(self, item: DiscoveredItem, alert: Dict[str, Any]) -> None:
        """Send Discord alert for item discovery."""
        if not alert.get('discord_webhook'):
            return
        
        # This would integrate with Discord webhook
        message = f"🔍 **Item Discovery Alert!**\n"
        message += f"**Item:** {item.item_name}\n"
        message += f"**Cost:** {item.cost:,} credits\n"
        message += f"**Vendor:** {item.vendor_name} ({item.vendor_type.value})\n"
        message += f"**Location:** {item.location}, {item.planet}\n"
        message += f"**Discovered:** {item.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        
        print(f"Discord Alert: {message}")
        # TODO: Implement actual Discord webhook integration
    
    def _update_search_indexes(self, item: DiscoveredItem) -> None:
        """Update search indexes for the item."""
        # Item name index
        words = re.findall(r'\w+', item.item_name.lower())
        for word in words:
            self.item_name_index[word].add(item.item_id)
        
        # Vendor type index
        self.vendor_type_index[item.vendor_type.value].add(item.item_id)
        
        # Planet index
        self.planet_index[item.planet.lower()].add(item.item_id)
        
        # Category index
        self.category_index[item.category.value].add(item.item_id)
    
    def build_search_indexes(self) -> None:
        """Build search indexes from existing data."""
        for item in self.discovered_items.values():
            self._update_search_indexes(item)
    
    def _deserialize_item(self, data: Dict[str, Any]) -> DiscoveredItem:
        """Deserialize item from dictionary."""
        try:
            timestamp = datetime.fromisoformat(data['timestamp'])
        except (ValueError, TypeError):
            timestamp = datetime.now()
        
        # Handle coordinates
        coords = data.get('coordinates', [0.0, 0.0])
        if isinstance(coords, list):
            coords = tuple(coords)
        
        # Handle category string conversion
        category_str = data['category']
        if category_str.startswith('ItemCategory.'):
            category_str = category_str.replace('ItemCategory.', '').lower()
        
        # Handle vendor type string conversion
        vendor_type_str = data['vendor_type']
        if vendor_type_str.startswith('VendorType.'):
            vendor_type_str = vendor_type_str.replace('VendorType.', '').lower()
        
        return DiscoveredItem(
            item_name=data['item_name'],
            item_id=data['item_id'],
            category=ItemCategory(category_str),
            cost=data['cost'],
            vendor_id=data['vendor_id'],
            vendor_name=data['vendor_name'],
            vendor_type=VendorType(vendor_type_str),
            planet=data['planet'],
            location=data['location'],
            coordinates=coords,
            timestamp=timestamp,
            quality=data.get('quality'),
            stats=data.get('stats'),
            resists=data.get('resists'),
            notes=data.get('notes', '')
        )
    
    def _deserialize_vendor(self, data: Dict[str, Any]) -> VendorProfile:
        """Deserialize vendor from dictionary."""
        try:
            first_discovered = datetime.fromisoformat(data['first_discovered'])
        except (ValueError, TypeError):
            first_discovered = datetime.now()
        
        try:
            last_visited = datetime.fromisoformat(data['last_visited'])
        except (ValueError, TypeError):
            last_visited = datetime.now()
        
        # Handle coordinates
        coords = data.get('coordinates', [0.0, 0.0])
        if isinstance(coords, list):
            coords = tuple(coords)
        
        # Handle vendor type string conversion
        vendor_type_str = data['vendor_type']
        if vendor_type_str.startswith('VendorType.'):
            vendor_type_str = vendor_type_str.replace('VendorType.', '').lower()
        
        return VendorProfile(
            vendor_id=data['vendor_id'],
            vendor_name=data['vendor_name'],
            vendor_type=VendorType(vendor_type_str),
            planet=data['planet'],
            location=data['location'],
            coordinates=coords,
            first_discovered=first_discovered,
            last_visited=last_visited,
            total_visits=data['total_visits'],
            items_discovered=data['items_discovered'],
            average_item_cost=data['average_item_cost'],
            most_expensive_item=data.get('most_expensive_item'),
            most_expensive_cost=data.get('most_expensive_cost', 0),
            notes=data.get('notes', '')
        )
    
    def _deserialize_session(self, data: Dict[str, Any]) -> DiscoverySession:
        """Deserialize session from dictionary."""
        try:
            start_time = datetime.fromisoformat(data['start_time'])
        except (ValueError, TypeError):
            start_time = datetime.now()
        
        try:
            end_time = datetime.fromisoformat(data['end_time'])
        except (ValueError, TypeError):
            end_time = datetime.now()
        
        return DiscoverySession(
            session_id=data['session_id'],
            character_name=data['character_name'],
            start_time=start_time,
            end_time=end_time,
            planets_visited=data['planets_visited'],
            vendors_discovered=data['vendors_discovered'],
            items_discovered=data['items_discovered'],
            total_value_discovered=data['total_value_discovered'],
            most_valuable_item=data.get('most_valuable_item'),
            most_valuable_cost=data.get('most_valuable_cost', 0)
        ) 
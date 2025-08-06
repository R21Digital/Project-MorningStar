"""Material Tracker integration for SWGTracker.com data."""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import aiohttp
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class MaterialData:
    """Represents material data from SWGTracker."""
    name: str
    rarity: str
    location: str
    price: Optional[float]
    last_seen: str
    quantity: Optional[int]
    source: str = "swgtracker"
    timestamp: str = ""


@dataclass
class MaterialTrackerConfig:
    """Configuration for Material Tracker."""
    api_url: str = "https://swgtracker.com/api/materials"
    cache_duration: int = 3600  # 1 hour
    max_retries: int = 3
    timeout: int = 30


class MaterialTracker:
    """Handles SWGTracker.com material data synchronization."""
    
    def __init__(self, config: Optional[MaterialTrackerConfig] = None):
        """Initialize the Material Tracker.
        
        Parameters
        ----------
        config : MaterialTrackerConfig, optional
            Configuration for the tracker
        """
        self.config = config or MaterialTrackerConfig()
        self.cache_dir = Path("data/live_feeds/materials")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.materials: Dict[str, MaterialData] = {}
        self.last_sync: Optional[datetime] = None
        
    async def sync_materials(self) -> bool:
        """Sync material data from SWGTracker.com.
        
        Returns
        -------
        bool
            True if sync was successful, False otherwise
        """
        try:
            logger.info("Starting material data sync from SWGTracker.com")
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
                async with session.get(self.config.api_url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch materials: {response.status}")
                        return False
                    
                    data = await response.json()
                    await self._process_material_data(data)
                    
            self.last_sync = datetime.now()
            await self._save_to_cache()
            logger.info(f"Material sync completed: {len(self.materials)} materials")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing materials: {e}")
            return False
    
    async def _process_material_data(self, data: List[Dict[str, Any]]) -> None:
        """Process raw material data from API.
        
        Parameters
        ----------
        data : List[Dict[str, Any]]
            Raw material data from SWGTracker API
        """
        self.materials.clear()
        
        for item in data:
            try:
                material = MaterialData(
                    name=item.get("name", ""),
                    rarity=item.get("rarity", "common"),
                    location=item.get("location", ""),
                    price=item.get("price"),
                    last_seen=item.get("last_seen", ""),
                    quantity=item.get("quantity"),
                    timestamp=datetime.now().isoformat()
                )
                
                if material.name:
                    self.materials[material.name.lower()] = material
                    
            except Exception as e:
                logger.warning(f"Error processing material {item.get('name', 'unknown')}: {e}")
    
    async def _save_to_cache(self) -> None:
        """Save material data to local cache."""
        cache_file = self.cache_dir / "materials_cache.json"
        
        cache_data = {
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "materials": [asdict(material) for material in self.materials.values()]
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def load_from_cache(self) -> bool:
        """Load material data from local cache.
        
        Returns
        -------
        bool
            True if cache was loaded successfully
        """
        cache_file = self.cache_dir / "materials_cache.json"
        
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            self.materials.clear()
            for material_data in data.get("materials", []):
                material = MaterialData(**material_data)
                self.materials[material.name.lower()] = material
            
            last_sync_str = data.get("last_sync")
            if last_sync_str:
                self.last_sync = datetime.fromisoformat(last_sync_str)
            
            logger.info(f"Loaded {len(self.materials)} materials from cache")
            return True
            
        except Exception as e:
            logger.error(f"Error loading material cache: {e}")
            return False
    
    def get_rare_materials(self, min_rarity: str = "rare") -> List[MaterialData]:
        """Get materials filtered by rarity.
        
        Parameters
        ----------
        min_rarity : str
            Minimum rarity level to include
            
        Returns
        -------
        List[MaterialData]
            List of materials meeting rarity criteria
        """
        rarity_levels = ["common", "uncommon", "rare", "very_rare", "legendary"]
        
        try:
            min_level = rarity_levels.index(min_rarity.lower())
            return [
                material for material in self.materials.values()
                if material.rarity.lower() in rarity_levels[min_level:]
            ]
        except ValueError:
            logger.warning(f"Invalid rarity level: {min_rarity}")
            return []
    
    def get_materials_by_location(self, location: str) -> List[MaterialData]:
        """Get materials found in a specific location.
        
        Parameters
        ----------
        location : str
            Location to filter by
            
        Returns
        -------
        List[MaterialData]
            List of materials found in the location
        """
        return [
            material for material in self.materials.values()
            if location.lower() in material.location.lower()
        ]
    
    def get_price_data(self) -> Dict[str, float]:
        """Get price data for materials with known prices.
        
        Returns
        -------
        Dict[str, float]
            Dictionary mapping material names to prices
        """
        return {
            material.name: material.price
            for material in self.materials.values()
            if material.price is not None
        }
    
    def is_cache_stale(self) -> bool:
        """Check if the cache is stale and needs refreshing.
        
        Returns
        -------
        bool
            True if cache is stale
        """
        if not self.last_sync:
            return True
        
        age = datetime.now() - self.last_sync
        return age.total_seconds() > self.config.cache_duration
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status.
        
        Returns
        -------
        Dict[str, Any]
            Status information including last sync time and material count
        """
        return {
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "material_count": len(self.materials),
            "cache_stale": self.is_cache_stale(),
            "cache_dir": str(self.cache_dir)
        } 
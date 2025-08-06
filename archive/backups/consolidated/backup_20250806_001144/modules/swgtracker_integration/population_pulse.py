"""Population Pulse integration for SWGTracker.com data."""

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
class PopulationData:
    """Represents population data from SWGTracker."""
    planet: str
    city: str
    population: int
    change_24h: int
    change_7d: int
    activity_level: str
    peak_hours: List[str]
    source: str = "swgtracker"
    timestamp: str = ""


@dataclass
class PopulationPulseConfig:
    """Configuration for Population Pulse Tracker."""
    api_url: str = "https://swgtracker.com/api/population-pulse"
    cache_duration: int = 1800  # 30 minutes
    max_retries: int = 3
    timeout: int = 30


class PopulationPulseTracker:
    """Handles SWGTracker.com population pulse data synchronization."""
    
    def __init__(self, config: Optional[PopulationPulseConfig] = None):
        """Initialize the Population Pulse Tracker.
        
        Parameters
        ----------
        config : PopulationPulseConfig, optional
            Configuration for the tracker
        """
        self.config = config or PopulationPulseConfig()
        self.cache_dir = Path("data/live_feeds/population")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.population_data: Dict[str, PopulationData] = {}
        self.last_sync: Optional[datetime] = None
        
    async def sync_population_data(self) -> bool:
        """Sync population data from SWGTracker.com.
        
        Returns
        -------
        bool
            True if sync was successful, False otherwise
        """
        try:
            logger.info("Starting population pulse data sync from SWGTracker.com")
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
                async with session.get(self.config.api_url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch population data: {response.status}")
                        return False
                    
                    data = await response.json()
                    await self._process_population_data(data)
                    
            self.last_sync = datetime.now()
            await self._save_to_cache()
            logger.info(f"Population sync completed: {len(self.population_data)} locations")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing population data: {e}")
            return False
    
    async def _process_population_data(self, data: List[Dict[str, Any]]) -> None:
        """Process raw population data from API.
        
        Parameters
        ----------
        data : List[Dict[str, Any]]
            Raw population data from SWGTracker API
        """
        self.population_data.clear()
        
        for item in data:
            try:
                population = PopulationData(
                    planet=item.get("planet", ""),
                    city=item.get("city", ""),
                    population=item.get("population", 0),
                    change_24h=item.get("change_24h", 0),
                    change_7d=item.get("change_7d", 0),
                    activity_level=item.get("activity_level", "low"),
                    peak_hours=item.get("peak_hours", []),
                    timestamp=datetime.now().isoformat()
                )
                
                key = f"{population.planet}_{population.city}".lower()
                if population.city:
                    self.population_data[key] = population
                    
            except Exception as e:
                logger.warning(f"Error processing population data for {item.get('city', 'unknown')}: {e}")
    
    async def _save_to_cache(self) -> None:
        """Save population data to local cache."""
        cache_file = self.cache_dir / "population_cache.json"
        
        cache_data = {
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "population_data": [asdict(data) for data in self.population_data.values()]
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def load_from_cache(self) -> bool:
        """Load population data from local cache.
        
        Returns
        -------
        bool
            True if cache was loaded successfully
        """
        cache_file = self.cache_dir / "population_cache.json"
        
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            self.population_data.clear()
            for pop_data in data.get("population_data", []):
                population = PopulationData(**pop_data)
                key = f"{population.planet}_{population.city}".lower()
                self.population_data[key] = population
            
            last_sync_str = data.get("last_sync")
            if last_sync_str:
                self.last_sync = datetime.fromisoformat(last_sync_str)
            
            logger.info(f"Loaded {len(self.population_data)} population records from cache")
            return True
            
        except Exception as e:
            logger.error(f"Error loading population cache: {e}")
            return False
    
    def get_popular_locations(self, min_population: int = 50) -> List[PopulationData]:
        """Get locations with population above threshold.
        
        Parameters
        ----------
        min_population : int
            Minimum population threshold
            
        Returns
        -------
        List[PopulationData]
            List of popular locations
        """
        return [
            data for data in self.population_data.values()
            if data.population >= min_population
        ]
    
    def get_growing_locations(self, min_growth: int = 10) -> List[PopulationData]:
        """Get locations with positive population growth.
        
        Parameters
        ----------
        min_growth : int
            Minimum growth threshold
            
        Returns
        -------
        List[PopulationData]
            List of growing locations
        """
        return [
            data for data in self.population_data.values()
            if data.change_24h >= min_growth
        ]
    
    def get_active_locations(self, activity_level: str = "high") -> List[PopulationData]:
        """Get locations with specific activity level.
        
        Parameters
        ----------
        activity_level : str
            Activity level to filter by
            
        Returns
        -------
        List[PopulationData]
            List of active locations
        """
        return [
            data for data in self.population_data.values()
            if data.activity_level.lower() == activity_level.lower()
        ]
    
    def get_locations_by_planet(self, planet: str) -> List[PopulationData]:
        """Get all locations on a specific planet.
        
        Parameters
        ----------
        planet : str
            Planet to filter by
            
        Returns
        -------
        List[PopulationData]
            List of locations on the planet
        """
        return [
            data for data in self.population_data.values()
            if data.planet.lower() == planet.lower()
        ]
    
    def get_peak_hour_locations(self, hour: str) -> List[PopulationData]:
        """Get locations active during a specific hour.
        
        Parameters
        ----------
        hour : str
            Hour to search for (e.g., "18:00")
            
        Returns
        -------
        List[PopulationData]
            List of locations active during the hour
        """
        return [
            data for data in self.population_data.values()
            if hour in data.peak_hours
        ]
    
    def get_population_trends(self) -> Dict[str, Dict[str, int]]:
        """Get population trends by planet.
        
        Returns
        -------
        Dict[str, Dict[str, int]]
            Dictionary mapping planets to trend data
        """
        trends = {}
        
        for data in self.population_data.values():
            planet = data.planet
            if planet not in trends:
                trends[planet] = {
                    "total_population": 0,
                    "total_growth_24h": 0,
                    "location_count": 0
                }
            
            trends[planet]["total_population"] += data.population
            trends[planet]["total_growth_24h"] += data.change_24h
            trends[planet]["location_count"] += 1
        
        return trends
    
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
            Status information including last sync time and data count
        """
        return {
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "location_count": len(self.population_data),
            "cache_stale": self.is_cache_stale(),
            "cache_dir": str(self.cache_dir)
        } 
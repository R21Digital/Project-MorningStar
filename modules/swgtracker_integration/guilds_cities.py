"""Guilds & Cities integration for SWGTracker.com data."""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import aiohttp
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class GuildData:
    """Represents guild data from SWGTracker."""
    name: str
    faction: str
    member_count: int
    territory_count: int
    influence: float
    headquarters: str
    leader: str
    source: str = "swgtracker"
    timestamp: str = ""


@dataclass
class CityData:
    """Represents city data from SWGTracker."""
    name: str
    planet: str
    coordinates: Tuple[int, int]
    population: int
    mayor: str
    guild_controlled: bool
    controlling_guild: Optional[str]
    travel_hub: bool
    source: str = "swgtracker"
    timestamp: str = ""


@dataclass
class GuildsCitiesConfig:
    """Configuration for Guilds & Cities Tracker."""
    api_url: str = "https://swgtracker.com/api/guilds-cities"
    cache_duration: int = 7200  # 2 hours
    max_retries: int = 3
    timeout: int = 30


class GuildsCitiesTracker:
    """Handles SWGTracker.com guilds and cities data synchronization."""
    
    def __init__(self, config: Optional[GuildsCitiesConfig] = None):
        """Initialize the Guilds & Cities Tracker.
        
        Parameters
        ----------
        config : GuildsCitiesConfig, optional
            Configuration for the tracker
        """
        self.config = config or GuildsCitiesConfig()
        self.cache_dir = Path("data/live_feeds/guilds_cities")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.guilds: Dict[str, GuildData] = {}
        self.cities: Dict[str, CityData] = {}
        self.last_sync: Optional[datetime] = None
        
    async def sync_guilds_cities(self) -> bool:
        """Sync guilds and cities data from SWGTracker.com.
        
        Returns
        -------
        bool
            True if sync was successful, False otherwise
        """
        try:
            logger.info("Starting guilds and cities data sync from SWGTracker.com")
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
                async with session.get(self.config.api_url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch guilds/cities: {response.status}")
                        return False
                    
                    data = await response.json()
                    await self._process_guilds_cities_data(data)
                    
            self.last_sync = datetime.now()
            await self._save_to_cache()
            logger.info(f"Guilds/Cities sync completed: {len(self.guilds)} guilds, {len(self.cities)} cities")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing guilds/cities: {e}")
            return False
    
    async def _process_guilds_cities_data(self, data: Dict[str, Any]) -> None:
        """Process raw guilds and cities data from API.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Raw guilds and cities data from SWGTracker API
        """
        self.guilds.clear()
        self.cities.clear()
        
        # Process guilds
        for guild_data in data.get("guilds", []):
            try:
                guild = GuildData(
                    name=guild_data.get("name", ""),
                    faction=guild_data.get("faction", "neutral"),
                    member_count=guild_data.get("member_count", 0),
                    territory_count=guild_data.get("territory_count", 0),
                    influence=guild_data.get("influence", 0.0),
                    headquarters=guild_data.get("headquarters", ""),
                    leader=guild_data.get("leader", ""),
                    timestamp=datetime.now().isoformat()
                )
                
                if guild.name:
                    self.guilds[guild.name.lower()] = guild
                    
            except Exception as e:
                logger.warning(f"Error processing guild {guild_data.get('name', 'unknown')}: {e}")
        
        # Process cities
        for city_data in data.get("cities", []):
            try:
                coords = city_data.get("coordinates", [0, 0])
                city = CityData(
                    name=city_data.get("name", ""),
                    planet=city_data.get("planet", ""),
                    coordinates=(coords[0], coords[1]) if len(coords) >= 2 else (0, 0),
                    population=city_data.get("population", 0),
                    mayor=city_data.get("mayor", ""),
                    guild_controlled=city_data.get("guild_controlled", False),
                    controlling_guild=city_data.get("controlling_guild"),
                    travel_hub=city_data.get("travel_hub", False),
                    timestamp=datetime.now().isoformat()
                )
                
                if city.name:
                    self.cities[city.name.lower()] = city
                    
            except Exception as e:
                logger.warning(f"Error processing city {city_data.get('name', 'unknown')}: {e}")
    
    async def _save_to_cache(self) -> None:
        """Save guilds and cities data to local cache."""
        cache_file = self.cache_dir / "guilds_cities_cache.json"
        
        cache_data = {
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "guilds": [asdict(guild) for guild in self.guilds.values()],
            "cities": [asdict(city) for city in self.cities.values()]
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def load_from_cache(self) -> bool:
        """Load guilds and cities data from local cache.
        
        Returns
        -------
        bool
            True if cache was loaded successfully
        """
        cache_file = self.cache_dir / "guilds_cities_cache.json"
        
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            self.guilds.clear()
            self.cities.clear()
            
            # Load guilds
            for guild_data in data.get("guilds", []):
                guild = GuildData(**guild_data)
                self.guilds[guild.name.lower()] = guild
            
            # Load cities
            for city_data in data.get("cities", []):
                city = CityData(**city_data)
                self.cities[city.name.lower()] = city
            
            last_sync_str = data.get("last_sync")
            if last_sync_str:
                self.last_sync = datetime.fromisoformat(last_sync_str)
            
            logger.info(f"Loaded {len(self.guilds)} guilds and {len(self.cities)} cities from cache")
            return True
            
        except Exception as e:
            logger.error(f"Error loading guilds/cities cache: {e}")
            return False
    
    def get_travel_hubs(self) -> List[CityData]:
        """Get cities that are travel hubs.
        
        Returns
        -------
        List[CityData]
            List of travel hub cities
        """
        return [city for city in self.cities.values() if city.travel_hub]
    
    def get_guild_territories(self, guild_name: str) -> List[CityData]:
        """Get cities controlled by a specific guild.
        
        Parameters
        ----------
        guild_name : str
            Name of the guild to search for
            
        Returns
        -------
        List[CityData]
            List of cities controlled by the guild
        """
        return [
            city for city in self.cities.values()
            if city.controlling_guild and city.controlling_guild.lower() == guild_name.lower()
        ]
    
    def get_popular_cities(self, min_population: int = 100) -> List[CityData]:
        """Get cities with population above threshold.
        
        Parameters
        ----------
        min_population : int
            Minimum population threshold
            
        Returns
        -------
        List[CityData]
            List of popular cities
        """
        return [
            city for city in self.cities.values()
            if city.population >= min_population
        ]
    
    def get_faction_guilds(self, faction: str) -> List[GuildData]:
        """Get guilds belonging to a specific faction.
        
        Parameters
        ----------
        faction : str
            Faction to filter by
            
        Returns
        -------
        List[GuildData]
            List of guilds in the faction
        """
        return [
            guild for guild in self.guilds.values()
            if guild.faction.lower() == faction.lower()
        ]
    
    def get_large_guilds(self, min_members: int = 50) -> List[GuildData]:
        """Get guilds with member count above threshold.
        
        Parameters
        ----------
        min_members : int
            Minimum member count threshold
            
        Returns
        -------
        List[GuildData]
            List of large guilds
        """
        return [
            guild for guild in self.guilds.values()
            if guild.member_count >= min_members
        ]
    
    def get_territory_heatmap_data(self) -> Dict[str, int]:
        """Get territory control data for heatmap visualization.
        
        Returns
        -------
        Dict[str, int]
            Dictionary mapping guild names to territory counts
        """
        return {
            guild.name: guild.territory_count
            for guild in self.guilds.values()
            if guild.territory_count > 0
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
            Status information including last sync time and counts
        """
        return {
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "guild_count": len(self.guilds),
            "city_count": len(self.cities),
            "cache_stale": self.is_cache_stale(),
            "cache_dir": str(self.cache_dir)
        } 
"""Data Sync Manager for coordinating all SWGTracker.com integrations."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .material_tracker import MaterialTracker, MaterialTrackerConfig
from .guilds_cities import GuildsCitiesTracker, GuildsCitiesConfig
from .population_pulse import PopulationPulseTracker, PopulationPulseConfig

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of a data sync operation."""
    success: bool
    tracker_name: str
    data_count: int
    error_message: Optional[str] = None
    duration_seconds: float = 0.0


@dataclass
class DataSyncManagerConfig:
    """Configuration for the Data Sync Manager."""
    enable_materials: bool = True
    enable_guilds_cities: bool = True
    enable_population: bool = True
    sync_interval: int = 3600  # 1 hour
    parallel_sync: bool = True
    retry_failed: bool = True
    max_retries: int = 3


class DataSyncManager:
    """Coordinates synchronization of all SWGTracker.com data feeds."""
    
    def __init__(self, config: Optional[DataSyncManagerConfig] = None):
        """Initialize the Data Sync Manager.
        
        Parameters
        ----------
        config : DataSyncManagerConfig, optional
            Configuration for the sync manager
        """
        self.config = config or DataSyncManagerConfig()
        self.cache_dir = Path("data/live_feeds")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize trackers
        self.material_tracker = MaterialTracker() if self.config.enable_materials else None
        self.guilds_cities_tracker = GuildsCitiesTracker() if self.config.enable_guilds_cities else None
        self.population_tracker = PopulationPulseTracker() if self.config.enable_population else None
        
        self.sync_history: List[SyncResult] = []
        self.last_full_sync: Optional[datetime] = None
        
    async def sync_all_data(self) -> List[SyncResult]:
        """Sync all enabled data feeds.
        
        Returns
        -------
        List[SyncResult]
            Results of all sync operations
        """
        logger.info("Starting full SWGTracker.com data sync")
        
        sync_tasks = []
        
        if self.material_tracker:
            sync_tasks.append(self._sync_materials())
        
        if self.guilds_cities_tracker:
            sync_tasks.append(self._sync_guilds_cities())
        
        if self.population_tracker:
            sync_tasks.append(self._sync_population())
        
        if not sync_tasks:
            logger.warning("No data trackers enabled")
            return []
        
        if self.config.parallel_sync:
            results = await asyncio.gather(*sync_tasks, return_exceptions=True)
        else:
            results = []
            for task in sync_tasks:
                try:
                    result = await task
                    results.append(result)
                except Exception as e:
                    results.append(SyncResult(
                        success=False,
                        tracker_name="unknown",
                        data_count=0,
                        error_message=str(e)
                    ))
        
        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(SyncResult(
                    success=False,
                    tracker_name="unknown",
                    data_count=0,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        self.sync_history.extend(processed_results)
        self.last_full_sync = datetime.now()
        
        # Save sync history
        await self._save_sync_history()
        
        success_count = sum(1 for r in processed_results if r.success)
        logger.info(f"Sync completed: {success_count}/{len(processed_results)} successful")
        
        return processed_results
    
    async def _sync_materials(self) -> SyncResult:
        """Sync material data."""
        start_time = datetime.now()
        
        try:
            success = await self.material_tracker.sync_materials()
            duration = (datetime.now() - start_time).total_seconds()
            
            return SyncResult(
                success=success,
                tracker_name="materials",
                data_count=len(self.material_tracker.materials),
                duration_seconds=duration
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return SyncResult(
                success=False,
                tracker_name="materials",
                data_count=0,
                error_message=str(e),
                duration_seconds=duration
            )
    
    async def _sync_guilds_cities(self) -> SyncResult:
        """Sync guilds and cities data."""
        start_time = datetime.now()
        
        try:
            success = await self.guilds_cities_tracker.sync_guilds_cities()
            duration = (datetime.now() - start_time).total_seconds()
            
            total_count = len(self.guilds_cities_tracker.guilds) + len(self.guilds_cities_tracker.cities)
            
            return SyncResult(
                success=success,
                tracker_name="guilds_cities",
                data_count=total_count,
                duration_seconds=duration
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return SyncResult(
                success=False,
                tracker_name="guilds_cities",
                data_count=0,
                error_message=str(e),
                duration_seconds=duration
            )
    
    async def _sync_population(self) -> SyncResult:
        """Sync population data."""
        start_time = datetime.now()
        
        try:
            success = await self.population_tracker.sync_population_data()
            duration = (datetime.now() - start_time).total_seconds()
            
            return SyncResult(
                success=success,
                tracker_name="population",
                data_count=len(self.population_tracker.population_data),
                duration_seconds=duration
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return SyncResult(
                success=False,
                tracker_name="population",
                data_count=0,
                error_message=str(e),
                duration_seconds=duration
            )
    
    async def _save_sync_history(self) -> None:
        """Save sync history to cache."""
        history_file = self.cache_dir / "sync_history.json"
        
        history_data = {
            "last_full_sync": self.last_full_sync.isoformat() if self.last_full_sync else None,
            "sync_results": [
                {
                    "success": result.success,
                    "tracker_name": result.tracker_name,
                    "data_count": result.data_count,
                    "error_message": result.error_message,
                    "duration_seconds": result.duration_seconds,
                    "timestamp": datetime.now().isoformat()
                }
                for result in self.sync_history[-100:]  # Keep last 100 results
            ]
        }
        
        import json
        with open(history_file, 'w') as f:
            json.dump(history_data, f, indent=2)
    
    def load_all_caches(self) -> Dict[str, bool]:
        """Load all data from local caches.
        
        Returns
        -------
        Dict[str, bool]
            Dictionary mapping tracker names to load success status
        """
        results = {}
        
        if self.material_tracker:
            results["materials"] = self.material_tracker.load_from_cache()
        
        if self.guilds_cities_tracker:
            results["guilds_cities"] = self.guilds_cities_tracker.load_from_cache()
        
        if self.population_tracker:
            results["population"] = self.population_tracker.load_from_cache()
        
        return results
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get comprehensive sync status for all trackers.
        
        Returns
        -------
        Dict[str, Any]
            Status information for all trackers
        """
        status = {
            "last_full_sync": self.last_full_sync.isoformat() if self.last_full_sync else None,
            "enabled_trackers": [],
            "tracker_status": {}
        }
        
        if self.material_tracker:
            status["enabled_trackers"].append("materials")
            status["tracker_status"]["materials"] = self.material_tracker.get_sync_status()
        
        if self.guilds_cities_tracker:
            status["enabled_trackers"].append("guilds_cities")
            status["tracker_status"]["guilds_cities"] = self.guilds_cities_tracker.get_sync_status()
        
        if self.population_tracker:
            status["enabled_trackers"].append("population")
            status["tracker_status"]["population"] = self.population_tracker.get_sync_status()
        
        return status
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of all available data.
        
        Returns
        -------
        Dict[str, Any]
            Summary of all data sources
        """
        summary = {
            "materials": {},
            "guilds_cities": {},
            "population": {}
        }
        
        if self.material_tracker:
            summary["materials"] = {
                "total_materials": len(self.material_tracker.materials),
                "rare_materials": len(self.material_tracker.get_rare_materials()),
                "price_data_available": len(self.material_tracker.get_price_data())
            }
        
        if self.guilds_cities_tracker:
            summary["guilds_cities"] = {
                "total_guilds": len(self.guilds_cities_tracker.guilds),
                "total_cities": len(self.guilds_cities_tracker.cities),
                "travel_hubs": len(self.guilds_cities_tracker.get_travel_hubs()),
                "popular_cities": len(self.guilds_cities_tracker.get_popular_cities())
            }
        
        if self.population_tracker:
            summary["population"] = {
                "total_locations": len(self.population_tracker.population_data),
                "popular_locations": len(self.population_tracker.get_popular_locations()),
                "growing_locations": len(self.population_tracker.get_growing_locations())
            }
        
        return summary
    
    def is_any_cache_stale(self) -> bool:
        """Check if any cache is stale and needs refreshing.
        
        Returns
        -------
        bool
            True if any cache is stale
        """
        if self.material_tracker and self.material_tracker.is_cache_stale():
            return True
        
        if self.guilds_cities_tracker and self.guilds_cities_tracker.is_cache_stale():
            return True
        
        if self.population_tracker and self.population_tracker.is_cache_stale():
            return True
        
        return False 
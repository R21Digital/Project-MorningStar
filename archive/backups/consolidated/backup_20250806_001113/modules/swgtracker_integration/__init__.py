"""SWGTracker.com Data Integration Layer.

This module provides integration with SWGTracker.com feeds for:
- Material Tracker data
- Guilds & Cities data  
- Population Pulse data

Features:
- Sync data from SWGTracker.com APIs
- Store data in local cache (data/live_feeds/)
- Provide dashboard panels for:
  - Rare materials
  - Popular travel hubs
  - Guild territory heatmaps
"""

from .material_tracker import MaterialTracker
from .guilds_cities import GuildsCitiesTracker
from .population_pulse import PopulationPulseTracker
from .data_sync_manager import DataSyncManager
from .dashboard_panels import DashboardPanels

__all__ = [
    "MaterialTracker",
    "GuildsCitiesTracker", 
    "PopulationPulseTracker",
    "DataSyncManager",
    "DashboardPanels"
] 
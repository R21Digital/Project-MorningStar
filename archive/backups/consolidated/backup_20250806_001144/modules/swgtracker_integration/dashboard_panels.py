"""Dashboard panels for SWGTracker.com data visualization."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from .material_tracker import MaterialTracker
from .guilds_cities import GuildsCitiesTracker
from .population_pulse import PopulationPulseTracker

logger = logging.getLogger(__name__)


@dataclass
class DashboardPanel:
    """Represents a dashboard panel."""
    title: str
    panel_type: str
    data: Dict[str, Any]
    last_updated: str
    refresh_interval: int = 300  # 5 minutes


@dataclass
class DashboardConfig:
    """Configuration for dashboard panels."""
    enable_rare_materials: bool = True
    enable_travel_hubs: bool = True
    enable_guild_heatmap: bool = True
    auto_refresh: bool = True
    refresh_interval: int = 300  # 5 minutes


class DashboardPanels:
    """Provides dashboard panels for SWGTracker.com data visualization."""
    
    def __init__(self, 
                 material_tracker: Optional[MaterialTracker] = None,
                 guilds_cities_tracker: Optional[GuildsCitiesTracker] = None,
                 population_tracker: Optional[PopulationPulseTracker] = None,
                 config: Optional[DashboardConfig] = None):
        """Initialize the Dashboard Panels.
        
        Parameters
        ----------
        material_tracker : MaterialTracker, optional
            Material tracker instance
        guilds_cities_tracker : GuildsCitiesTracker, optional
            Guilds and cities tracker instance
        population_tracker : PopulationPulseTracker, optional
            Population tracker instance
        config : DashboardConfig, optional
            Configuration for dashboard panels
        """
        self.config = config or DashboardConfig()
        self.material_tracker = material_tracker
        self.guilds_cities_tracker = guilds_cities_tracker
        self.population_tracker = population_tracker
        
        self.cache_dir = Path("data/live_feeds/dashboard")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.panels: Dict[str, DashboardPanel] = {}
        
    def generate_rare_materials_panel(self) -> Optional[DashboardPanel]:
        """Generate dashboard panel for rare materials.
        
        Returns
        -------
        DashboardPanel, optional
            Rare materials panel data
        """
        if not self.material_tracker or not self.config.enable_rare_materials:
            return None
        
        try:
            rare_materials = self.material_tracker.get_rare_materials("rare")
            
            # Group by rarity
            rarity_groups = {}
            for material in rare_materials:
                rarity = material.rarity
                if rarity not in rarity_groups:
                    rarity_groups[rarity] = []
                rarity_groups[rarity].append({
                    "name": material.name,
                    "location": material.location,
                    "price": material.price,
                    "last_seen": material.last_seen
                })
            
            # Get price statistics
            prices = [m.price for m in rare_materials if m.price is not None]
            price_stats = {
                "average_price": sum(prices) / len(prices) if prices else 0,
                "max_price": max(prices) if prices else 0,
                "min_price": min(prices) if prices else 0,
                "total_materials": len(rare_materials)
            }
            
            panel_data = {
                "rarity_groups": rarity_groups,
                "price_statistics": price_stats,
                "total_rare_materials": len(rare_materials),
                "last_updated": datetime.now().isoformat()
            }
            
            return DashboardPanel(
                title="Rare Materials",
                panel_type="rare_materials",
                data=panel_data,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error generating rare materials panel: {e}")
            return None
    
    def generate_travel_hubs_panel(self) -> Optional[DashboardPanel]:
        """Generate dashboard panel for travel hubs.
        
        Returns
        -------
        DashboardPanel, optional
            Travel hubs panel data
        """
        if not self.guilds_cities_tracker or not self.config.enable_travel_hubs:
            return None
        
        try:
            travel_hubs = self.guilds_cities_tracker.get_travel_hubs()
            popular_cities = self.guilds_cities_tracker.get_popular_cities(100)
            
            # Group by planet
            planet_groups = {}
            for city in travel_hubs:
                planet = city.planet
                if planet not in planet_groups:
                    planet_groups[planet] = []
                planet_groups[planet].append({
                    "name": city.name,
                    "coordinates": city.coordinates,
                    "population": city.population,
                    "mayor": city.mayor,
                    "guild_controlled": city.guild_controlled,
                    "controlling_guild": city.controlling_guild
                })
            
            # Get statistics
            total_population = sum(city.population for city in travel_hubs)
            guild_controlled_count = sum(1 for city in travel_hubs if city.guild_controlled)
            
            panel_data = {
                "planet_groups": planet_groups,
                "statistics": {
                    "total_travel_hubs": len(travel_hubs),
                    "total_population": total_population,
                    "guild_controlled": guild_controlled_count,
                    "average_population": total_population / len(travel_hubs) if travel_hubs else 0
                },
                "popular_cities": [
                    {
                        "name": city.name,
                        "planet": city.planet,
                        "population": city.population,
                        "coordinates": city.coordinates
                    }
                    for city in popular_cities[:10]  # Top 10
                ],
                "last_updated": datetime.now().isoformat()
            }
            
            return DashboardPanel(
                title="Travel Hubs",
                panel_type="travel_hubs",
                data=panel_data,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error generating travel hubs panel: {e}")
            return None
    
    def generate_guild_heatmap_panel(self) -> Optional[DashboardPanel]:
        """Generate dashboard panel for guild territory heatmap.
        
        Returns
        -------
        DashboardPanel, optional
            Guild heatmap panel data
        """
        if not self.guilds_cities_tracker or not self.config.enable_guild_heatmap:
            return None
        
        try:
            heatmap_data = self.guilds_cities_tracker.get_territory_heatmap_data()
            large_guilds = self.guilds_cities_tracker.get_large_guilds(50)
            
            # Get faction breakdown
            faction_guilds = {}
            for guild in self.guilds_cities_tracker.guilds.values():
                faction = guild.faction
                if faction not in faction_guilds:
                    faction_guilds[faction] = {
                        "guild_count": 0,
                        "total_territories": 0,
                        "total_members": 0
                    }
                faction_guilds[faction]["guild_count"] += 1
                faction_guilds[faction]["total_territories"] += guild.territory_count
                faction_guilds[faction]["total_members"] += guild.member_count
            
            # Top guilds by territory
            top_guilds = sorted(
                self.guilds_cities_tracker.guilds.values(),
                key=lambda g: g.territory_count,
                reverse=True
            )[:10]
            
            panel_data = {
                "heatmap_data": heatmap_data,
                "faction_breakdown": faction_guilds,
                "top_guilds": [
                    {
                        "name": guild.name,
                        "faction": guild.faction,
                        "territory_count": guild.territory_count,
                        "member_count": guild.member_count,
                        "influence": guild.influence,
                        "headquarters": guild.headquarters
                    }
                    for guild in top_guilds
                ],
                "statistics": {
                    "total_guilds": len(self.guilds_cities_tracker.guilds),
                    "total_territories": sum(heatmap_data.values()),
                    "large_guilds": len(large_guilds),
                    "average_territories": sum(heatmap_data.values()) / len(heatmap_data) if heatmap_data else 0
                },
                "last_updated": datetime.now().isoformat()
            }
            
            return DashboardPanel(
                title="Guild Territory Heatmap",
                panel_type="guild_heatmap",
                data=panel_data,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error generating guild heatmap panel: {e}")
            return None
    
    def generate_population_trends_panel(self) -> Optional[DashboardPanel]:
        """Generate dashboard panel for population trends.
        
        Returns
        -------
        DashboardPanel, optional
            Population trends panel data
        """
        if not self.population_tracker:
            return None
        
        try:
            trends = self.population_tracker.get_population_trends()
            growing_locations = self.population_tracker.get_growing_locations()
            active_locations = self.population_tracker.get_active_locations("high")
            
            # Top growing locations
            top_growing = sorted(
                growing_locations,
                key=lambda loc: loc.change_24h,
                reverse=True
            )[:10]
            
            panel_data = {
                "planet_trends": trends,
                "top_growing": [
                    {
                        "planet": loc.planet,
                        "city": loc.city,
                        "population": loc.population,
                        "change_24h": loc.change_24h,
                        "activity_level": loc.activity_level
                    }
                    for loc in top_growing
                ],
                "active_locations": [
                    {
                        "planet": loc.planet,
                        "city": loc.city,
                        "population": loc.population,
                        "activity_level": loc.activity_level
                    }
                    for loc in active_locations[:10]
                ],
                "statistics": {
                    "total_locations": len(self.population_tracker.population_data),
                    "growing_locations": len(growing_locations),
                    "active_locations": len(active_locations),
                    "total_population": sum(loc.population for loc in self.population_tracker.population_data.values())
                },
                "last_updated": datetime.now().isoformat()
            }
            
            return DashboardPanel(
                title="Population Trends",
                panel_type="population_trends",
                data=panel_data,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error generating population trends panel: {e}")
            return None
    
    def generate_all_panels(self) -> Dict[str, DashboardPanel]:
        """Generate all available dashboard panels.
        
        Returns
        -------
        Dict[str, DashboardPanel]
            Dictionary of all generated panels
        """
        panels = {}
        
        # Generate each panel type
        rare_materials = self.generate_rare_materials_panel()
        if rare_materials:
            panels["rare_materials"] = rare_materials
        
        travel_hubs = self.generate_travel_hubs_panel()
        if travel_hubs:
            panels["travel_hubs"] = travel_hubs
        
        guild_heatmap = self.generate_guild_heatmap_panel()
        if guild_heatmap:
            panels["guild_heatmap"] = guild_heatmap
        
        population_trends = self.generate_population_trends_panel()
        if population_trends:
            panels["population_trends"] = population_trends
        
        self.panels = panels
        return panels
    
    def save_panels_to_cache(self) -> None:
        """Save all panels to local cache."""
        if not self.panels:
            return
        
        cache_file = self.cache_dir / "dashboard_panels.json"
        
        cache_data = {
            "last_updated": datetime.now().isoformat(),
            "panels": {
                name: {
                    "title": panel.title,
                    "panel_type": panel.panel_type,
                    "data": panel.data,
                    "last_updated": panel.last_updated,
                    "refresh_interval": panel.refresh_interval
                }
                for name, panel in self.panels.items()
            }
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def load_panels_from_cache(self) -> bool:
        """Load panels from local cache.
        
        Returns
        -------
        bool
            True if cache was loaded successfully
        """
        cache_file = self.cache_dir / "dashboard_panels.json"
        
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            self.panels.clear()
            for name, panel_data in data.get("panels", {}).items():
                panel = DashboardPanel(
                    title=panel_data["title"],
                    panel_type=panel_data["panel_type"],
                    data=panel_data["data"],
                    last_updated=panel_data["last_updated"],
                    refresh_interval=panel_data.get("refresh_interval", 300)
                )
                self.panels[name] = panel
            
            logger.info(f"Loaded {len(self.panels)} dashboard panels from cache")
            return True
            
        except Exception as e:
            logger.error(f"Error loading dashboard panels cache: {e}")
            return False
    
    def get_panel_summary(self) -> Dict[str, Any]:
        """Get summary of all available panels.
        
        Returns
        -------
        Dict[str, Any]
            Summary of all panels
        """
        summary = {
            "total_panels": len(self.panels),
            "available_panels": list(self.panels.keys()),
            "panel_types": {
                "rare_materials": "Rare Materials",
                "travel_hubs": "Travel Hubs", 
                "guild_heatmap": "Guild Territory Heatmap",
                "population_trends": "Population Trends"
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return summary
    
    def export_panel_data(self, panel_name: str, format: str = "json") -> Optional[str]:
        """Export panel data in specified format.
        
        Parameters
        ----------
        panel_name : str
            Name of the panel to export
        format : str
            Export format (json, csv, etc.)
            
        Returns
        -------
        str, optional
            Exported data as string
        """
        if panel_name not in self.panels:
            return None
        
        panel = self.panels[panel_name]
        
        if format.lower() == "json":
            return json.dumps(panel.data, indent=2)
        else:
            logger.warning(f"Unsupported export format: {format}")
            return None 
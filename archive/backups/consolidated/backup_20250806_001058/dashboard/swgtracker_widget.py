#!/usr/bin/env python3
"""
MS11 Batch 057 - SWGTracker Dashboard Widget

Dashboard widget for displaying SWGTracker.com data including:
- Top populated cities
- Rare materials currently active
- Guild-controlled territories
- Server pulse information
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.swgtracker_integration import (
    get_swgtracker_integration,
    get_top_cities,
    get_active_resources,
    get_guild_territories,
    get_rare_materials,
    ResourceData,
    CityData,
    PulseData
)


class SWGTrackerWidget:
    """Dashboard widget for SWGTracker data visualization."""
    
    def __init__(self):
        """Initialize the SWGTracker widget."""
        self.integration = get_swgtracker_integration()
        self.last_refresh = None
        self.cache_duration = 300  # 5 minutes
    
    def _should_refresh(self) -> bool:
        """Check if data should be refreshed."""
        if not self.last_refresh:
            return True
        
        elapsed = time.time() - self.last_refresh
        return elapsed > self.cache_duration
    
    def _refresh_data(self) -> None:
        """Refresh all data."""
        try:
            self.integration.refresh_all_data()
            self.last_refresh = time.time()
        except Exception as e:
            print(f"Warning: Failed to refresh SWGTracker data: {e}")
    
    def get_top_cities_widget(self, limit: int = 10) -> Dict[str, Any]:
        """Generate top cities widget data.
        
        Args:
            limit: Maximum number of cities to display
            
        Returns:
            Widget data dictionary
        """
        if self._should_refresh():
            self._refresh_data()
        
        try:
            cities = get_top_cities(limit)
            
            widget_data = {
                'title': f'Top {len(cities)} Cities by Population',
                'type': 'cities',
                'timestamp': datetime.now().isoformat(),
                'data': []
            }
            
            for i, city in enumerate(cities, 1):
                widget_data['data'].append({
                    'rank': i,
                    'name': city.name,
                    'planet': city.planet,
                    'mayor': city.mayor,
                    'population': city.population,
                    'status': city.status,
                    'formatted_population': f"{city.population:,}"
                })
            
            return widget_data
            
        except Exception as e:
            return {
                'title': 'Top Cities',
                'type': 'cities',
                'error': f'Failed to load cities: {e}',
                'timestamp': datetime.now().isoformat(),
                'data': []
            }
    
    def get_rare_materials_widget(self, min_rating: int = 800, limit: int = 15) -> Dict[str, Any]:
        """Generate rare materials widget data.
        
        Args:
            min_rating: Minimum rating to consider "rare"
            limit: Maximum number of materials to display
            
        Returns:
            Widget data dictionary
        """
        if self._should_refresh():
            self._refresh_data()
        
        try:
            materials = get_rare_materials(min_rating)
            
            widget_data = {
                'title': f'Rare Materials (Rating ≥ {min_rating})',
                'type': 'materials',
                'timestamp': datetime.now().isoformat(),
                'min_rating': min_rating,
                'total_count': len(materials),
                'data': []
            }
            
            for i, material in enumerate(materials[:limit], 1):
                widget_data['data'].append({
                    'rank': i,
                    'name': material.name,
                    'type': material.type,
                    'rating': material.rating,
                    'planet': material.planet,
                    'status': material.status,
                    'date': material.date,
                    'oq': material.oq,
                    'sr': material.sr,
                    'quality_color': self._get_quality_color(material.rating)
                })
            
            return widget_data
            
        except Exception as e:
            return {
                'title': 'Rare Materials',
                'type': 'materials',
                'error': f'Failed to load materials: {e}',
                'timestamp': datetime.now().isoformat(),
                'data': []
            }
    
    def get_guild_territories_widget(self, limit: int = 10) -> Dict[str, Any]:
        """Generate guild territories widget data.
        
        Args:
            limit: Maximum number of guilds to display
            
        Returns:
            Widget data dictionary
        """
        if self._should_refresh():
            self._refresh_data()
        
        try:
            territories = get_guild_territories()
            
            # Sort by number of cities controlled
            sorted_territories = sorted(
                territories.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )
            
            widget_data = {
                'title': 'Guild Territories',
                'type': 'territories',
                'timestamp': datetime.now().isoformat(),
                'total_guilds': len(territories),
                'total_cities': sum(len(cities) for cities in territories.values()),
                'data': []
            }
            
            for i, (guild_name, cities) in enumerate(sorted_territories[:limit], 1):
                widget_data['data'].append({
                    'rank': i,
                    'guild_name': guild_name,
                    'city_count': len(cities),
                    'cities': cities[:5],  # Show first 5 cities
                    'has_more': len(cities) > 5
                })
            
            return widget_data
            
        except Exception as e:
            return {
                'title': 'Guild Territories',
                'type': 'territories',
                'error': f'Failed to load territories: {e}',
                'timestamp': datetime.now().isoformat(),
                'data': []
            }
    
    def get_server_pulse_widget(self) -> Dict[str, Any]:
        """Generate server pulse widget data.
        
        Returns:
            Widget data dictionary
        """
        if self._should_refresh():
            self._refresh_data()
        
        try:
            pulse = self.integration.fetch_pulse()
            
            if pulse:
                # Determine activity level
                if pulse.online_players > 1000:
                    activity_level = "High"
                    activity_color = "green"
                elif pulse.online_players > 500:
                    activity_level = "Medium"
                    activity_color = "yellow"
                else:
                    activity_level = "Low"
                    activity_color = "red"
                
                widget_data = {
                    'title': 'Server Pulse',
                    'type': 'pulse',
                    'timestamp': datetime.now().isoformat(),
                    'online_players': pulse.online_players,
                    'formatted_players': f"{pulse.online_players:,}",
                    'server_status': pulse.server_status,
                    'uptime': pulse.uptime,
                    'activity_level': activity_level,
                    'activity_color': activity_color,
                    'last_updated': pulse.timestamp
                }
            else:
                widget_data = {
                    'title': 'Server Pulse',
                    'type': 'pulse',
                    'timestamp': datetime.now().isoformat(),
                    'error': 'No pulse data available',
                    'online_players': 0,
                    'server_status': 'Unknown'
                }
            
            return widget_data
            
        except Exception as e:
            return {
                'title': 'Server Pulse',
                'type': 'pulse',
                'error': f'Failed to load pulse: {e}',
                'timestamp': datetime.now().isoformat(),
                'online_players': 0,
                'server_status': 'Error'
            }
    
    def get_resource_summary_widget(self) -> Dict[str, Any]:
        """Generate resource summary widget data.
        
        Returns:
            Widget data dictionary
        """
        if self._should_refresh():
            self._refresh_data()
        
        try:
            resources = self.integration.fetch_resources()
            active_resources = [r for r in resources if r.status.lower() == 'active']
            rare_resources = [r for r in active_resources if r.rating >= 800]
            very_rare_resources = [r for r in active_resources if r.rating >= 900]
            
            # Group by category
            categories = {}
            for resource in active_resources:
                category = resource.type.lower()
                if category not in categories:
                    categories[category] = []
                categories[category].append(resource)
            
            # Get top categories
            top_categories = sorted(
                categories.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )[:5]
            
            widget_data = {
                'title': 'Resource Summary',
                'type': 'summary',
                'timestamp': datetime.now().isoformat(),
                'total_resources': len(resources),
                'active_resources': len(active_resources),
                'rare_resources': len(rare_resources),
                'very_rare_resources': len(very_rare_resources),
                'top_categories': [
                    {
                        'category': category,
                        'count': len(resources_list)
                    }
                    for category, resources_list in top_categories
                ]
            }
            
            return widget_data
            
        except Exception as e:
            return {
                'title': 'Resource Summary',
                'type': 'summary',
                'error': f'Failed to load summary: {e}',
                'timestamp': datetime.now().isoformat(),
                'total_resources': 0,
                'active_resources': 0,
                'rare_resources': 0
            }
    
    def _get_quality_color(self, rating: int) -> str:
        """Get color for resource quality.
        
        Args:
            rating: Resource rating
            
        Returns:
            Color string
        """
        if rating >= 900:
            return "purple"
        elif rating >= 850:
            return "blue"
        elif rating >= 800:
            return "green"
        else:
            return "gray"
    
    def get_all_widgets(self) -> Dict[str, Any]:
        """Generate all widget data.
        
        Returns:
            Dictionary containing all widget data
        """
        return {
            'cities': self.get_top_cities_widget(),
            'materials': self.get_rare_materials_widget(),
            'territories': self.get_guild_territories_widget(),
            'pulse': self.get_server_pulse_widget(),
            'summary': self.get_resource_summary_widget(),
            'last_refresh': self.last_refresh,
            'cache_duration': self.cache_duration
        }
    
    def export_widget_data(self, filepath: str) -> None:
        """Export widget data to JSON file.
        
        Args:
            filepath: Path to save the data
        """
        try:
            data = self.get_all_widgets()
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✓ Exported widget data to {filepath}")
            
        except Exception as e:
            print(f"Error exporting widget data: {e}")


def create_html_widget(widget_data: Dict[str, Any], widget_type: str) -> str:
    """Create HTML for a specific widget type.
    
    Args:
        widget_data: Widget data dictionary
        widget_type: Type of widget to create
        
    Returns:
        HTML string
    """
    if 'error' in widget_data:
        return f"""
        <div class="widget widget-{widget_type}">
            <h3>{widget_data['title']}</h3>
            <div class="error">Error: {widget_data['error']}</div>
        </div>
        """
    
    if widget_type == 'cities':
        return _create_cities_html(widget_data)
    elif widget_type == 'materials':
        return _create_materials_html(widget_data)
    elif widget_type == 'territories':
        return _create_territories_html(widget_data)
    elif widget_type == 'pulse':
        return _create_pulse_html(widget_data)
    elif widget_type == 'summary':
        return _create_summary_html(widget_data)
    else:
        return f"<div>Unknown widget type: {widget_type}</div>"


def _create_cities_html(data: Dict[str, Any]) -> str:
    """Create HTML for cities widget."""
    html = f"""
    <div class="widget widget-cities">
        <h3>{data['title']}</h3>
        <div class="widget-content">
            <table class="cities-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>City</th>
                        <th>Planet</th>
                        <th>Mayor</th>
                        <th>Population</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for item in data['data']:
        html += f"""
                    <tr>
                        <td>{item['rank']}</td>
                        <td>{item['name']}</td>
                        <td>{item['planet']}</td>
                        <td>{item['mayor']}</td>
                        <td>{item['formatted_population']}</td>
                        <td>{item['status']}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    return html


def _create_materials_html(data: Dict[str, Any]) -> str:
    """Create HTML for materials widget."""
    html = f"""
    <div class="widget widget-materials">
        <h3>{data['title']} ({data['total_count']} total)</h3>
        <div class="widget-content">
            <table class="materials-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Rating</th>
                        <th>Planet</th>
                        <th>OQ</th>
                        <th>SR</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for item in data['data']:
        html += f"""
                    <tr class="quality-{item['quality_color']}">
                        <td>{item['rank']}</td>
                        <td>{item['name']}</td>
                        <td>{item['type']}</td>
                        <td>{item['rating']}</td>
                        <td>{item['planet']}</td>
                        <td>{item['oq'] or '-'}</td>
                        <td>{item['sr'] or '-'}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    return html


def _create_territories_html(data: Dict[str, Any]) -> str:
    """Create HTML for territories widget."""
    html = f"""
    <div class="widget widget-territories">
        <h3>{data['title']} ({data['total_guilds']} guilds, {data['total_cities']} cities)</h3>
        <div class="widget-content">
            <table class="territories-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Guild</th>
                        <th>Cities</th>
                        <th>City List</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for item in data['data']:
        cities_text = ', '.join(item['cities'])
        if item['has_more']:
            cities_text += f" (+{item['city_count'] - len(item['cities'])} more)"
        
        html += f"""
                    <tr>
                        <td>{item['rank']}</td>
                        <td>{item['guild_name']}</td>
                        <td>{item['city_count']}</td>
                        <td>{cities_text}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
    """
    
    return html


def _create_pulse_html(data: Dict[str, Any]) -> str:
    """Create HTML for pulse widget."""
    if 'error' in data:
        status_class = "error"
        status_text = "Error"
    else:
        status_class = f"status-{data['activity_color']}"
        status_text = data['activity_level']
    
    html = f"""
    <div class="widget widget-pulse">
        <h3>{data['title']}</h3>
        <div class="widget-content">
            <div class="pulse-info">
                <div class="pulse-item">
                    <span class="label">Online Players:</span>
                    <span class="value">{data['formatted_players']}</span>
                </div>
                <div class="pulse-item">
                    <span class="label">Server Status:</span>
                    <span class="value">{data['server_status']}</span>
                </div>
                <div class="pulse-item">
                    <span class="label">Activity Level:</span>
                    <span class="value {status_class}">{status_text}</span>
                </div>
                <div class="pulse-item">
                    <span class="label">Uptime:</span>
                    <span class="value">{data.get('uptime', 'Unknown')}</span>
                </div>
            </div>
        </div>
    </div>
    """
    
    return html


def _create_summary_html(data: Dict[str, Any]) -> str:
    """Create HTML for summary widget."""
    html = f"""
    <div class="widget widget-summary">
        <h3>{data['title']}</h3>
        <div class="widget-content">
            <div class="summary-stats">
                <div class="stat-item">
                    <span class="label">Total Resources:</span>
                    <span class="value">{data['total_resources']:,}</span>
                </div>
                <div class="stat-item">
                    <span class="label">Active Resources:</span>
                    <span class="value">{data['active_resources']:,}</span>
                </div>
                <div class="stat-item">
                    <span class="label">Rare (800+):</span>
                    <span class="value">{data['rare_resources']:,}</span>
                </div>
                <div class="stat-item">
                    <span class="label">Very Rare (900+):</span>
                    <span class="value">{data['very_rare_resources']:,}</span>
                </div>
            </div>
            <div class="top-categories">
                <h4>Top Categories:</h4>
                <ul>
    """
    
    for category in data['top_categories']:
        html += f"""
                    <li>{category['category']}: {category['count']} resources</li>
        """
    
    html += """
                </ul>
            </div>
        </div>
    </div>
    """
    
    return html


# Global convenience functions
def get_swgtracker_widget() -> SWGTrackerWidget:
    """Get or create the global SWGTracker widget instance.
    
    Returns:
        SWGTrackerWidget instance
    """
    global _swgtracker_widget
    if not hasattr(get_swgtracker_widget, '_swgtracker_widget'):
        get_swgtracker_widget._swgtracker_widget = SWGTrackerWidget()
    return get_swgtracker_widget._swgtracker_widget


def create_dashboard_html() -> str:
    """Create complete dashboard HTML.
    
    Returns:
        Complete HTML dashboard string
    """
    widget = get_swgtracker_widget()
    all_data = widget.get_all_widgets()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MS11 SWGTracker Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .dashboard { max-width: 1200px; margin: 0 auto; }
            .widget { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .widget h3 { margin-top: 0; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f8f9fa; font-weight: bold; }
            .error { color: red; font-weight: bold; }
            .quality-purple { background-color: #e6e6fa; }
            .quality-blue { background-color: #e6f3ff; }
            .quality-green { background-color: #e6ffe6; }
            .status-green { color: green; font-weight: bold; }
            .status-yellow { color: orange; font-weight: bold; }
            .status-red { color: red; font-weight: bold; }
            .pulse-info, .summary-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .pulse-item, .stat-item { display: flex; justify-content: space-between; padding: 10px; background: #f8f9fa; border-radius: 4px; }
            .label { font-weight: bold; }
            .top-categories { margin-top: 20px; }
            .top-categories ul { list-style: none; padding: 0; }
            .top-categories li { padding: 5px 0; border-bottom: 1px solid #eee; }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <h1>MS11 SWGTracker Dashboard</h1>
            <p>Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    """
    
    # Add each widget
    for widget_type, data in all_data.items():
        if widget_type not in ['last_refresh', 'cache_duration']:
            html += create_html_widget(data, widget_type)
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html


if __name__ == "__main__":
    # Demo the widget functionality
    widget = get_swgtracker_widget()
    
    print("MS11 SWGTracker Dashboard Widget Demo")
    print("=" * 50)
    
    # Generate all widgets
    all_data = widget.get_all_widgets()
    
    for widget_type, data in all_data.items():
        if widget_type not in ['last_refresh', 'cache_duration']:
            print(f"\n{data['title']}:")
            if 'error' in data:
                print(f"  Error: {data['error']}")
            else:
                print(f"  Data points: {len(data.get('data', []))}")
                print(f"  Timestamp: {data['timestamp']}")
    
    # Export data
    widget.export_widget_data("swgtracker_dashboard_data.json")
    
    # Create HTML dashboard
    html = create_dashboard_html()
    with open("swgtracker_dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\n✓ Generated dashboard files:")
    print(f"  - swgtracker_dashboard_data.json")
    print(f"  - swgtracker_dashboard.html") 
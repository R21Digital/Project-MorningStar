"""Google Sheets Importer for Stat Optimizer Module.

This module handles importing stat thresholds and reference data from Google Sheets
for use in stat optimization analysis.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import requests
from datetime import datetime

from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)

class GoogleSheetsImporter:
    """Handles importing data from Google Sheets for stat optimization."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Google Sheets importer.
        
        Parameters
        ----------
        config : dict, optional
            Configuration including API keys, sheet IDs, and cache settings
        """
        self.config = config or {}
        self.api_key = self.config.get("google_api_key")
        self.sheet_id = self.config.get("sheet_id")
        self.cache_dir = Path(self.config.get("cache_dir", "data/stat_cache"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Default stat thresholds if sheets unavailable
        self.default_thresholds = {
            "pve_damage": {
                "strength": {"min": 100, "optimal": 150, "max": 200},
                "agility": {"min": 80, "optimal": 120, "max": 160},
                "constitution": {"min": 90, "optimal": 130, "max": 180},
                "stamina": {"min": 70, "optimal": 100, "max": 140},
                "mind": {"min": 50, "optimal": 80, "max": 120},
                "focus": {"min": 60, "optimal": 90, "max": 130},
                "willpower": {"min": 40, "optimal": 70, "max": 110}
            },
            "buff_stack": {
                "strength": {"min": 120, "optimal": 170, "max": 220},
                "agility": {"min": 100, "optimal": 140, "max": 180},
                "constitution": {"min": 110, "optimal": 150, "max": 200},
                "stamina": {"min": 90, "optimal": 120, "max": 160},
                "mind": {"min": 70, "optimal": 100, "max": 140},
                "focus": {"min": 80, "optimal": 110, "max": 150},
                "willpower": {"min": 60, "optimal": 90, "max": 130}
            },
            "healing": {
                "strength": {"min": 60, "optimal": 90, "max": 130},
                "agility": {"min": 70, "optimal": 100, "max": 140},
                "constitution": {"min": 100, "optimal": 140, "max": 180},
                "stamina": {"min": 80, "optimal": 110, "max": 150},
                "mind": {"min": 120, "optimal": 160, "max": 200},
                "focus": {"min": 130, "optimal": 170, "max": 210},
                "willpower": {"min": 110, "optimal": 150, "max": 190}
            }
        }
        
        log_event("[SHEETS_IMPORTER] Initialized Google Sheets importer")
    
    def import_stat_thresholds(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Import stat thresholds from Google Sheets or use cached data.
        
        Parameters
        ----------
        force_refresh : bool, optional
            Force refresh from Google Sheets even if cache exists
            
        Returns
        -------
        dict
            Stat thresholds organized by optimization type
        """
        cache_file = self.cache_dir / "stat_thresholds.json"
        
        # Check if we should use cached data
        if not force_refresh and cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is still valid (less than 24 hours old)
                cache_time = datetime.fromisoformat(cached_data.get("cached_at", "2000-01-01"))
                if (datetime.now() - cache_time).total_seconds() < 86400:  # 24 hours
                    log_event("[SHEETS_IMPORTER] Using cached stat thresholds")
                    return cached_data.get("thresholds", self.default_thresholds)
                    
            except Exception as e:
                log_event(f"[SHEETS_IMPORTER] Error reading cache: {e}")
        
        # Try to import from Google Sheets
        if self.api_key and self.sheet_id:
            try:
                thresholds = self._fetch_from_sheets()
                if thresholds:
                    # Cache the data
                    cache_data = {
                        "thresholds": thresholds,
                        "cached_at": datetime.now().isoformat(),
                        "source": "google_sheets"
                    }
                    with open(cache_file, 'w') as f:
                        json.dump(cache_data, f, indent=2)
                    
                    log_event("[SHEETS_IMPORTER] Successfully imported from Google Sheets")
                    return thresholds
                    
            except Exception as e:
                log_event(f"[SHEETS_IMPORTER] Error fetching from sheets: {e}")
        
        # Fall back to default thresholds
        log_event("[SHEETS_IMPORTER] Using default stat thresholds")
        return self.default_thresholds
    
    def _fetch_from_sheets(self) -> Optional[Dict[str, Any]]:
        """Fetch data from Google Sheets API.
        
        Returns
        -------
        dict, optional
            Parsed stat thresholds from sheets
        """
        if not self.api_key or not self.sheet_id:
            return None
        
        try:
            # Google Sheets API endpoint
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}/values/StatThresholds!A1:Z1000"
            params = {"key": self.api_key}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            values = data.get("values", [])
            
            if not values:
                log_event("[SHEETS_IMPORTER] No data found in sheets")
                return None
            
            # Parse the sheet data
            thresholds = self._parse_sheet_data(values)
            
            log_event(f"[SHEETS_IMPORTER] Successfully parsed {len(thresholds)} threshold categories")
            return thresholds
            
        except Exception as e:
            log_event(f"[SHEETS_IMPORTER] Error fetching from sheets: {e}")
            return None
    
    def _parse_sheet_data(self, values: List[List[str]]) -> Dict[str, Any]:
        """Parse raw sheet data into structured thresholds.
        
        Parameters
        ----------
        values : list
            Raw sheet data as list of rows
            
        Returns
        -------
        dict
            Structured stat thresholds
        """
        thresholds = {}
        current_category = None
        
        for row in values:
            if not row:
                continue
                
            first_cell = row[0].strip().lower()
            
            # Check for category headers
            if first_cell in ["pve damage", "pve_damage", "damage"]:
                current_category = "pve_damage"
                thresholds[current_category] = {}
            elif first_cell in ["buff stack", "buff_stack", "buff"]:
                current_category = "buff_stack"
                thresholds[current_category] = {}
            elif first_cell in ["healing", "heal"]:
                current_category = "healing"
                thresholds[current_category] = {}
            elif first_cell in ["stat", "attribute", "attr"]:
                # Skip header row
                continue
            elif current_category and len(row) >= 4:
                # Parse stat row: Stat, Min, Optimal, Max
                try:
                    stat_name = row[0].strip().lower()
                    min_val = int(row[1])
                    optimal_val = int(row[2])
                    max_val = int(row[3])
                    
                    thresholds[current_category][stat_name] = {
                        "min": min_val,
                        "optimal": optimal_val,
                        "max": max_val
                    }
                except (ValueError, IndexError):
                    continue
        
        return thresholds
    
    def get_optimization_targets(self, optimization_type: str) -> Dict[str, Dict[str, int]]:
        """Get optimization targets for a specific type.
        
        Parameters
        ----------
        optimization_type : str
            Type of optimization (pve_damage, buff_stack, healing)
            
        Returns
        -------
        dict
            Optimization targets for the specified type
        """
        thresholds = self.import_stat_thresholds()
        return thresholds.get(optimization_type, {})
    
    def validate_sheet_connection(self) -> bool:
        """Test connection to Google Sheets.
        
        Returns
        -------
        bool
            True if connection successful, False otherwise
        """
        if not self.api_key or not self.sheet_id:
            log_event("[SHEETS_IMPORTER] No API key or sheet ID configured")
            return False
        
        try:
            url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}"
            params = {"key": self.api_key}
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            log_event("[SHEETS_IMPORTER] Google Sheets connection successful")
            return True
            
        except Exception as e:
            log_event(f"[SHEETS_IMPORTER] Connection test failed: {e}")
            return False


def create_sheets_importer(config: Dict[str, Any] = None) -> GoogleSheetsImporter:
    """Create a Google Sheets importer instance.
    
    Parameters
    ----------
    config : dict, optional
        Configuration for the importer
        
    Returns
    -------
    GoogleSheetsImporter
        Configured importer instance
    """
    return GoogleSheetsImporter(config) 
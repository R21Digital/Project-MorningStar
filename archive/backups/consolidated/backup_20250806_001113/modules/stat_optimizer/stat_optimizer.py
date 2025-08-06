"""Main Stat Optimizer Module for MS11.

This module provides the primary interface for stat optimization, integrating
Google Sheets data import, stat analysis, and alert management.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from android_ms11.utils.logging_utils import log_event

from .sheets_importer import GoogleSheetsImporter, create_sheets_importer
from .stat_analyzer import StatAnalyzer, create_stat_analyzer
from .alert_manager import AlertManager, create_alert_manager

logger = logging.getLogger(__name__)

class StatOptimizer:
    """Main stat optimizer that integrates all components."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the stat optimizer.
        
        Parameters
        ----------
        config : dict, optional
            Configuration for all optimizer components
        """
        self.config = config or {}
        
        # Initialize components
        self.sheets_importer = create_sheets_importer(self.config.get("sheets_config", {}))
        self.stat_analyzer = create_stat_analyzer(self.config.get("analyzer_config", {}))
        self.alert_manager = create_alert_manager(self.config.get("alert_config", {}))
        
        # Optimization history
        self.optimization_history = []
        
        # Character stat cache
        self.character_stats_cache = {}
        
        log_event("[STAT_OPTIMIZER] Stat optimizer initialized")
    
    def optimize_character_stats(self, character_stats: Dict[str, int], 
                               character_name: str = "Unknown",
                               optimization_type: str = "pve_damage",
                               force_refresh_thresholds: bool = False,
                               send_alerts: bool = True) -> Dict[str, Any]:
        """Perform comprehensive stat optimization analysis.
        
        Parameters
        ----------
        character_stats : dict
            Current character stats (strength, agility, etc.)
        character_name : str, optional
            Name of the character being analyzed
        optimization_type : str, optional
            Type of optimization (pve_damage, buff_stack, healing)
        force_refresh_thresholds : bool, optional
            Force refresh of thresholds from Google Sheets
        send_alerts : bool, optional
            Whether to send alerts for suboptimal stats
            
        Returns
        -------
        dict
            Comprehensive optimization results
        """
        try:
            log_event(f"[STAT_OPTIMIZER] Starting optimization for {character_name}")
            
            # Import thresholds from Google Sheets
            thresholds = self.sheets_importer.import_stat_thresholds(force_refresh_thresholds)
            optimization_targets = thresholds.get(optimization_type, {})
            
            # Analyze character stats
            analysis = self.stat_analyzer.analyze_character_stats(
                character_stats, optimization_type, optimization_targets
            )
            
            # Add metadata to analysis
            analysis["character_name"] = character_name
            analysis["thresholds_source"] = "google_sheets" if force_refresh_thresholds else "cached"
            
            # Send alerts if requested
            alerts_sent = False
            if send_alerts:
                alerts_sent = self.alert_manager.check_and_alert(analysis, character_name)
            
            # Create comprehensive results
            results = {
                "timestamp": datetime.now().isoformat(),
                "character_name": character_name,
                "optimization_type": optimization_type,
                "analysis": analysis,
                "alerts_sent": alerts_sent,
                "recommendations": analysis.get("recommendations", []),
                "overall_score": analysis.get("score", 0.0),
                "critical_issues": len(analysis.get("issues", [])),
                "warnings": len(analysis.get("warnings", []))
            }
            
            # Store in history
            self.optimization_history.append(results)
            
            # Cache character stats
            self.character_stats_cache[character_name] = {
                "stats": character_stats.copy(),
                "last_optimized": datetime.now().isoformat(),
                "optimization_type": optimization_type
            }
            
            log_event(f"[STAT_OPTIMIZER] Optimization complete for {character_name} - Score: {results['overall_score']:.1f}")
            return results
            
        except Exception as e:
            log_event(f"[STAT_OPTIMIZER] Error during optimization: {e}")
            return {
                "error": str(e),
                "character_name": character_name,
                "optimization_type": optimization_type,
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_all_optimization_types(self, character_stats: Dict[str, int], 
                                     character_name: str = "Unknown") -> Dict[str, Any]:
        """Analyze character stats for all optimization types.
        
        Parameters
        ----------
        character_stats : dict
            Current character stats
        character_name : str, optional
            Character name
            
        Returns
        -------
        dict
            Analysis results for all optimization types
        """
        optimization_types = ["pve_damage", "buff_stack", "healing"]
        results = {}
        
        for opt_type in optimization_types:
            try:
                result = self.optimize_character_stats(
                    character_stats, character_name, opt_type, send_alerts=False
                )
                results[opt_type] = result
            except Exception as e:
                log_event(f"[STAT_OPTIMIZER] Error analyzing {opt_type}: {e}")
                results[opt_type] = {"error": str(e)}
        
        return {
            "character_name": character_name,
            "timestamp": datetime.now().isoformat(),
            "optimization_results": results,
            "best_optimization": self._find_best_optimization(results)
        }
    
    def _find_best_optimization(self, results: Dict[str, Any]) -> str:
        """Find the optimization type with the best score.
        
        Parameters
        ----------
        results : dict
            Results for all optimization types
            
        Returns
        -------
        str
            Best optimization type
        """
        best_type = "pve_damage"
        best_score = 0.0
        
        for opt_type, result in results.items():
            if "error" in result:
                continue
            
            score = result.get("overall_score", 0.0)
            if score > best_score:
                best_score = score
                best_type = opt_type
        
        return best_type
    
    def get_optimization_summary(self, character_name: str = None) -> Dict[str, Any]:
        """Get summary of optimization history.
        
        Parameters
        ----------
        character_name : str, optional
            Filter by character name
            
        Returns
        -------
        dict
            Optimization summary
        """
        if character_name:
            history = [h for h in self.optimization_history 
                      if h.get("character_name") == character_name]
        else:
            history = self.optimization_history
        
        if not history:
            return {"total_optimizations": 0, "average_score": 0.0}
        
        total_optimizations = len(history)
        total_score = sum(h.get("overall_score", 0.0) for h in history)
        average_score = total_score / total_optimizations if total_optimizations > 0 else 0.0
        
        # Count by optimization type
        type_counts = {}
        for h in history:
            opt_type = h.get("optimization_type", "unknown")
            type_counts[opt_type] = type_counts.get(opt_type, 0) + 1
        
        return {
            "total_optimizations": total_optimizations,
            "average_score": average_score,
            "optimization_type_counts": type_counts,
            "character_name": character_name
        }
    
    def validate_google_sheets_connection(self) -> bool:
        """Test Google Sheets connection.
        
        Returns
        -------
        bool
            True if connection successful
        """
        return self.sheets_importer.validate_sheet_connection()
    
    def validate_discord_connection(self) -> bool:
        """Test Discord connection.
        
        Returns
        -------
        bool
            True if connection successful
        """
        return self.alert_manager.test_discord_connection()
    
    def get_alert_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of recent alerts.
        
        Parameters
        ----------
        days : int, optional
            Number of days to look back
            
        Returns
        -------
        dict
            Alert summary
        """
        return self.alert_manager.get_alert_summary(days)
    
    def export_optimization_report(self, character_name: str, 
                                 output_file: str = None) -> str:
        """Export detailed optimization report to file.
        
        Parameters
        ----------
        character_name : str
            Character name to export report for
        output_file : str, optional
            Output file path
            
        Returns
        -------
        str
            Path to exported report
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"reports/stat_optimization_{character_name}_{timestamp}.json"
        
        # Create reports directory
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get character data
        character_data = {
            "character_name": character_name,
            "export_timestamp": datetime.now().isoformat(),
            "optimization_history": [h for h in self.optimization_history 
                                   if h.get("character_name") == character_name],
            "cached_stats": self.character_stats_cache.get(character_name, {}),
            "summary": self.get_optimization_summary(character_name),
            "alert_summary": self.get_alert_summary(30)  # Last 30 days
        }
        
        # Export to file
        with open(output_path, 'w') as f:
            json.dump(character_data, f, indent=2)
        
        log_event(f"[STAT_OPTIMIZER] Report exported to {output_path}")
        return str(output_path)
    
    def get_character_stats_cache(self, character_name: str = None) -> Dict[str, Any]:
        """Get cached character stats.
        
        Parameters
        ----------
        character_name : str, optional
            Specific character name, or None for all
            
        Returns
        -------
        dict
            Cached character stats
        """
        if character_name:
            return self.character_stats_cache.get(character_name, {})
        else:
            return self.character_stats_cache.copy()
    
    def clear_cache(self, character_name: str = None):
        """Clear character stats cache.
        
        Parameters
        ----------
        character_name : str, optional
            Specific character to clear, or None for all
        """
        if character_name:
            self.character_stats_cache.pop(character_name, None)
            log_event(f"[STAT_OPTIMIZER] Cleared cache for {character_name}")
        else:
            self.character_stats_cache.clear()
            log_event("[STAT_OPTIMIZER] Cleared all character stats cache")


def create_stat_optimizer(config: Dict[str, Any] = None) -> StatOptimizer:
    """Create a stat optimizer instance.
    
    Parameters
    ----------
    config : dict, optional
        Configuration for the optimizer
        
    Returns
    -------
    StatOptimizer
        Configured optimizer instance
    """
    return StatOptimizer(config) 
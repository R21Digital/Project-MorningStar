"""Performance Analyzer for coordinating combat and build analysis.

This module coordinates the analysis of combat performance data and build information,
generating comprehensive reports and managing Discord alerts.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

from .combat_stats_tracker import CombatStatsTracker
from .build_analyzer import BuildAnalyzer
from .discord_notifier import DiscordNotifier
from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)

@dataclass
class AnalysisReport:
    """Data class for comprehensive analysis report."""
    session_id: str
    timestamp: datetime
    combat_performance: Dict[str, Any]
    build_analysis: Optional[Dict[str, Any]]
    skill_line_analysis: List[Dict[str, Any]]
    recommendations: List[str]
    discord_sent: bool
    report_file: str

class PerformanceAnalyzer:
    """Coordinates combat and build analysis with Discord integration."""
    
    def __init__(self, webhook_url: str = None, bot_token: str = None, channel_id: int = None):
        """Initialize the performance analyzer.
        
        Parameters
        ----------
        webhook_url : str, optional
            Discord webhook URL
        bot_token : str, optional
            Discord bot token
        channel_id : int, optional
            Discord channel ID
        """
        self.combat_tracker = CombatStatsTracker()
        self.build_analyzer = BuildAnalyzer()
        self.discord_notifier = DiscordNotifier(webhook_url, bot_token, channel_id)
        
        # Analysis settings
        self.auto_discord_alerts = True
        self.save_reports = True
        self.report_dir = Path("logs/performance_reports")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        log_event("[PERFORMANCE_ANALYZER] Initialized performance analyzer")
    
    def start_analysis_session(self, session_id: str = None) -> str:
        """Start a new analysis session.
        
        Parameters
        ----------
        session_id : str, optional
            Custom session ID
            
        Returns
        -------
        str
            Session ID
        """
        session_id = session_id or f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize combat tracker with new session
        self.combat_tracker = CombatStatsTracker(session_id)
        
        log_event(f"[PERFORMANCE_ANALYZER] Started analysis session: {session_id}")
        return session_id
    
    def load_build_for_analysis(self, skill_calculator_url: str = None, build_file: str = None) -> bool:
        """Load build data for analysis.
        
        Parameters
        ----------
        skill_calculator_url : str, optional
            SkillCalc URL to load build from
        build_file : str, optional
            Path to build JSON file
            
        Returns
        -------
        bool
            True if build loaded successfully
        """
        try:
            if skill_calculator_url:
                self.build_analyzer.load_build_from_link(skill_calculator_url)
                log_event(f"[PERFORMANCE_ANALYZER] Loaded build from URL: {skill_calculator_url}")
                return True
            elif build_file:
                self.build_analyzer.load_build_from_file(build_file)
                log_event(f"[PERFORMANCE_ANALYZER] Loaded build from file: {build_file}")
                return True
            else:
                log_event("[PERFORMANCE_ANALYZER] No build source provided")
                return False
                
        except Exception as e:
            log_event(f"[PERFORMANCE_ANALYZER] Error loading build: {e}")
            return False
    
    def record_combat_event(self, event_type: str, **kwargs) -> None:
        """Record a combat event for analysis.
        
        Parameters
        ----------
        event_type : str
            Type of combat event (skill_usage, enemy_kill, combat_start, combat_end)
        **kwargs
            Event-specific parameters
        """
        try:
            if event_type == "combat_start":
                enemy_type = kwargs.get("enemy_type", "unknown")
                enemy_level = kwargs.get("enemy_level", 1)
                self.combat_tracker.start_combat_session(enemy_type, enemy_level)
                
            elif event_type == "combat_end":
                result = kwargs.get("result", "victory")
                enemy_hp_remaining = kwargs.get("enemy_hp_remaining", 0)
                self.combat_tracker.end_combat_session(result, enemy_hp_remaining)
                
            elif event_type == "skill_usage":
                skill_name = kwargs.get("skill_name", "unknown")
                damage_dealt = kwargs.get("damage_dealt", 0)
                target = kwargs.get("target")
                cooldown = kwargs.get("cooldown", 0.0)
                skill_line = kwargs.get("skill_line", "unknown")
                self.combat_tracker.record_skill_usage(
                    skill_name, damage_dealt, target, cooldown, skill_line
                )
                
            elif event_type == "enemy_kill":
                enemy_type = kwargs.get("enemy_type", "unknown")
                damage_dealt = kwargs.get("damage_dealt", 0)
                self.combat_tracker.record_enemy_kill(enemy_type, damage_dealt)
                
            log_event(f"[PERFORMANCE_ANALYZER] Recorded {event_type} event")
            
        except Exception as e:
            log_event(f"[PERFORMANCE_ANALYZER] Error recording {event_type} event: {e}")
    
    def generate_comprehensive_report(self) -> AnalysisReport:
        """Generate a comprehensive analysis report.
        
        Returns
        -------
        AnalysisReport
            Complete analysis report
        """
        try:
            # Get combat performance data
            combat_performance = self.combat_tracker.end_session()
            
            # Analyze build efficiency if build is loaded
            build_analysis = None
            if self.build_analyzer.current_build:
                build_analysis = self.build_analyzer.analyze_build_efficiency(combat_performance)
                
                # Add skill line analysis
                skill_line_analysis = self.build_analyzer.analyze_skill_line_performance(combat_performance)
                build_analysis["skill_line_analysis"] = [asdict(analysis) for analysis in skill_line_analysis]
            else:
                skill_line_analysis = []
            
            # Generate recommendations
            recommendations = self._generate_recommendations(combat_performance, build_analysis)
            
            # Send Discord alert
            discord_sent = False
            if self.auto_discord_alerts:
                discord_sent = asyncio.run(
                    self.discord_notifier.send_combat_performance_alert(
                        combat_performance, build_analysis
                    )
                )
            
            # Save report
            report_file = ""
            if self.save_reports:
                report_file = self._save_analysis_report(combat_performance, build_analysis, recommendations)
            
            # Create analysis report
            report = AnalysisReport(
                session_id=combat_performance.get("session_id", "unknown"),
                timestamp=datetime.now(),
                combat_performance=combat_performance,
                build_analysis=build_analysis,
                skill_line_analysis=skill_line_analysis,
                recommendations=recommendations,
                discord_sent=discord_sent,
                report_file=report_file
            )
            
            log_event(f"[PERFORMANCE_ANALYZER] Generated comprehensive report for session: {report.session_id}")
            return report
            
        except Exception as e:
            log_event(f"[PERFORMANCE_ANALYZER] Error generating report: {e}")
            raise
    
    def analyze_session_performance(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance from existing session data.
        
        Parameters
        ----------
        session_data : dict
            Session data to analyze
            
        Returns
        -------
        dict
            Analysis results
        """
        try:
            analysis = {
                "combat_performance": session_data,
                "build_analysis": None,
                "skill_line_analysis": [],
                "recommendations": []
            }
            
            # Analyze build if available
            if self.build_analyzer.current_build:
                build_analysis = self.build_analyzer.analyze_build_efficiency(session_data)
                analysis["build_analysis"] = build_analysis
                
                skill_line_analysis = self.build_analyzer.analyze_skill_line_performance(session_data)
                analysis["skill_line_analysis"] = [asdict(analysis) for analysis in skill_line_analysis]
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(
                session_data, analysis["build_analysis"]
            )
            
            log_event("[PERFORMANCE_ANALYZER] Analyzed session performance")
            return analysis
            
        except Exception as e:
            log_event(f"[PERFORMANCE_ANALYZER] Error analyzing session: {e}")
            raise
    
    def send_discord_alert(self, analysis_data: Dict[str, Any]) -> bool:
        """Send Discord alert with analysis data.
        
        Parameters
        ----------
        analysis_data : dict
            Analysis data to send
            
        Returns
        -------
        bool
            True if sent successfully
        """
        try:
            combat_performance = analysis_data.get("combat_performance", {})
            build_analysis = analysis_data.get("build_analysis")
            
            success = asyncio.run(
                self.discord_notifier.send_combat_performance_alert(
                    combat_performance, build_analysis
                )
            )
            
            if success:
                log_event("[PERFORMANCE_ANALYZER] Discord alert sent successfully")
            else:
                log_event("[PERFORMANCE_ANALYZER] Failed to send Discord alert")
            
            return success
            
        except Exception as e:
            log_event(f"[PERFORMANCE_ANALYZER] Error sending Discord alert: {e}")
            return False
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary.
        
        Returns
        -------
        dict
            Performance summary data
        """
        try:
            performance_summary = self.combat_tracker.get_performance_summary()
            skill_analysis = self.combat_tracker.get_skill_analysis()
            
            summary = {
                "performance_summary": asdict(performance_summary),
                "skill_analysis": skill_analysis,
                "session_duration": self.combat_tracker.session_duration,
                "total_damage": self.combat_tracker.total_damage,
                "total_kills": self.combat_tracker.total_kills
            }
            
            return summary
            
        except Exception as e:
            log_event(f"[PERFORMANCE_ANALYZER] Error getting performance summary: {e}")
            return {}
    
    def _generate_recommendations(self, combat_data: Dict[str, Any], 
                                build_analysis: Optional[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on analysis.
        
        Parameters
        ----------
        combat_data : dict
            Combat performance data
        build_analysis : dict, optional
            Build analysis data
            
        Returns
        -------
        List[str]
            List of recommendations
        """
        recommendations = []
        
        # Combat performance recommendations
        performance_summary = combat_data.get("performance_summary", {})
        average_dps = performance_summary.get("average_dps", 0)
        efficiency_score = performance_summary.get("efficiency_score", 0)
        
        if average_dps < 100:
            recommendations.append("Low DPS detected - consider using higher damage skills")
        elif average_dps > 500:
            recommendations.append("Excellent DPS performance - maintain current strategy")
        
        if efficiency_score < 50:
            recommendations.append("Low efficiency - focus on skill rotation optimization")
        elif efficiency_score > 80:
            recommendations.append("High efficiency - excellent skill usage")
        
        # Build-specific recommendations
        if build_analysis:
            unused_skills = build_analysis.get("unused_skills", [])
            if unused_skills:
                recommendations.append(f"Consider using {len(unused_skills)} unused skills from your build")
            
            build_efficiency = build_analysis.get("build_efficiency_score", 0)
            if build_efficiency < 50:
                recommendations.append("Build efficiency is low - consider restructuring")
            elif build_efficiency > 75:
                recommendations.append("Build efficiency is good - minor optimizations only")
        
        # Skill usage recommendations
        skill_analysis = combat_data.get("skill_analysis", {})
        skill_usage = skill_analysis.get("skill_usage", {})
        
        if skill_usage:
            # Find skills with low usage
            low_usage_skills = [
                skill for skill, data in skill_usage.items()
                if data.get("usage_count", 0) < 3
            ]
            
            if low_usage_skills:
                recommendations.append(f"Consider using {len(low_usage_skills)} underutilized skills more frequently")
        
        return recommendations
    
    def _save_analysis_report(self, combat_data: Dict[str, Any], 
                            build_analysis: Optional[Dict[str, Any]], 
                            recommendations: List[str]) -> str:
        """Save analysis report to file.
        
        Parameters
        ----------
        combat_data : dict
            Combat performance data
        build_analysis : dict, optional
            Build analysis data
        recommendations : List[str]
            List of recommendations
            
        Returns
        -------
        str
            Path to saved report file
        """
        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "combat_performance": combat_data,
                "build_analysis": build_analysis,
                "recommendations": recommendations
            }
            
            filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.report_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            log_event(f"[PERFORMANCE_ANALYZER] Saved report to {filepath}")
            return str(filepath)
            
        except Exception as e:
            log_event(f"[PERFORMANCE_ANALYZER] Error saving report: {e}")
            return ""
    
    def test_discord_integration(self) -> bool:
        """Test Discord integration.
        
        Returns
        -------
        bool
            True if test successful
        """
        try:
            success = self.discord_notifier.test_connection()
            if success:
                log_event("[PERFORMANCE_ANALYZER] Discord integration test successful")
            else:
                log_event("[PERFORMANCE_ANALYZER] Discord integration test failed")
            return success
            
        except Exception as e:
            log_event(f"[PERFORMANCE_ANALYZER] Discord test error: {e}")
            return False
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """Get current analysis status.
        
        Returns
        -------
        dict
            Analysis status information
        """
        status = {
            "session_active": self.combat_tracker.current_session is not None,
            "session_duration": self.combat_tracker.session_duration,
            "total_damage": self.combat_tracker.total_damage,
            "total_kills": self.combat_tracker.total_kills,
            "build_loaded": self.build_analyzer.current_build is not None,
            "discord_configured": bool(self.discord_notifier.webhook_url or self.discord_notifier.bot_token),
            "auto_alerts_enabled": self.auto_discord_alerts,
            "save_reports_enabled": self.save_reports
        }
        
        if self.build_analyzer.current_build:
            status["build_name"] = self.build_analyzer.current_build.get("build_summary", "Unknown")
        
        return status 
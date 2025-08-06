"""Public Data Exporter for MS11.

This module provides functionality to export MS11 data to the SWGDB public site,
including quest tracking summaries, bot metrics, and heroic readiness data.
"""

import json
import yaml
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from android_ms11.utils.logging_utils import log_event


@dataclass
class QuestTrackingSummary:
    """Quest tracking summary for public export."""
    total_quests: int
    completed_quests: int
    active_quests: int
    quest_completion_rate: float
    total_xp_from_quests: int
    total_credits_from_quests: int
    recent_completions: List[Dict[str, Any]]
    quest_categories: Dict[str, int]
    last_updated: str


@dataclass
class BotMetrics:
    """Bot metrics for public export."""
    total_xp_gained: int
    total_credits_gained: int
    profession_levels: Dict[str, int]
    session_count: int
    total_session_time: float
    average_session_duration: float
    success_rate: float
    efficiency_score: float
    recent_activity: List[Dict[str, Any]]
    last_updated: str


@dataclass
class HeroicReadiness:
    """Heroic readiness data for public export."""
    total_heroics: int
    completed_heroics: int
    available_heroics: int
    heroic_completion_rate: float
    character_level: int
    readiness_score: float
    missing_prerequisites: List[str]
    recommended_heroics: List[Dict[str, Any]]
    last_updated: str


class PublicDataExporter:
    """Main public data exporter for SWGDB integration."""

    def __init__(self, data_dir: str = "data", session_logs_dir: str = "session_logs"):
        """Initialize the public data exporter.

        Parameters
        ----------
        data_dir : str
            Directory containing MS11 data files
        session_logs_dir : str
            Directory containing session logs
        """
        self.data_dir = Path(data_dir)
        self.session_logs_dir = Path(session_logs_dir)
        self.export_dir = Path("data/exported")
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        log_event("[PUBLIC_DATA_EXPORTER] Public data exporter initialized")

    def export_quest_tracking_summary(self) -> QuestTrackingSummary:
        """Export quest tracking summary data."""
        try:
            # Load quest tracking data
            progress_file = self.data_dir / "enhanced_progress_tracker.json"
            if not progress_file.exists():
                log_event("[PUBLIC_DATA_EXPORTER] Progress tracker file not found")
                return self._create_empty_quest_summary()
            
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
            
            # Extract quest data from checklists
            quests = []
            for checklist_name, checklist_data in progress_data.get("checklists", {}).items():
                if "quest" in checklist_name.lower() or "heroic" in checklist_name.lower():
                    for item in checklist_data.get("items", []):
                        quests.append({
                            "name": item.get("name", ""),
                            "status": item.get("status", "not_started"),
                            "progress": item.get("progress", 0.0),
                            "xp_reward": item.get("xp_reward", 0),
                            "credit_reward": item.get("credit_reward", 0),
                            "category": item.get("category", ""),
                            "location": item.get("location", ""),
                            "created_at": item.get("created_at", ""),
                            "completed_at": item.get("completed_at", "")
                        })
            
            # Calculate summary statistics
            total_quests = len(quests)
            completed_quests = len([q for q in quests if q["status"] == "completed"])
            active_quests = len([q for q in quests if q["status"] in ["in_progress", "started"]])
            quest_completion_rate = completed_quests / total_quests if total_quests > 0 else 0.0
            
            total_xp_from_quests = sum(q["xp_reward"] for q in quests if q["status"] == "completed")
            total_credits_from_quests = sum(q["credit_reward"] for q in quests if q["status"] == "completed")
            
            # Get recent completions (last 7 days)
            recent_completions = []
            cutoff_date = datetime.now() - timedelta(days=7)
            for quest in quests:
                if quest["status"] == "completed" and quest["completed_at"]:
                    try:
                        completed_date = datetime.fromisoformat(quest["completed_at"].replace("Z", "+00:00"))
                        if completed_date > cutoff_date:
                            recent_completions.append(quest)
                    except:
                        pass
            
            # Categorize quests
            quest_categories = {}
            for quest in quests:
                category = quest["category"] or "general"
                quest_categories[category] = quest_categories.get(category, 0) + 1
            
            summary = QuestTrackingSummary(
                total_quests=total_quests,
                completed_quests=completed_quests,
                active_quests=active_quests,
                quest_completion_rate=quest_completion_rate,
                total_xp_from_quests=total_xp_from_quests,
                total_credits_from_quests=total_credits_from_quests,
                recent_completions=recent_completions[:10],  # Limit to 10 most recent
                quest_categories=quest_categories,
                last_updated=datetime.now().isoformat()
            )
            
            # Export to JSON
            self._export_to_json("quest_tracking_summary.json", asdict(summary))
            
            log_event(f"[PUBLIC_DATA_EXPORTER] Exported quest tracking summary: {completed_quests}/{total_quests} completed")
            return summary
            
        except Exception as e:
            log_event(f"[PUBLIC_DATA_EXPORTER] Error exporting quest tracking summary: {e}")
            return self._create_empty_quest_summary()

    def export_bot_metrics(self) -> BotMetrics:
        """Export bot metrics data."""
        try:
            # Load session logs
            session_files = list(self.session_logs_dir.glob("*.json"))
            if not session_files:
                log_event("[PUBLIC_DATA_EXPORTER] No session log files found")
                return self._create_empty_bot_metrics()
            
            # Process session data
            total_xp_gained = 0
            total_credits_gained = 0
            session_count = 0
            total_session_time = 0.0
            success_rates = []
            efficiency_scores = []
            recent_activity = []
            profession_levels = {}
            
            for session_file in session_files:
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    # Extract metrics
                    total_xp_gained += session_data.get("total_xp_gained", 0)
                    total_credits_gained += session_data.get("total_credits_gained", 0)
                    session_count += 1
                    
                    # Calculate session duration
                    start_time = session_data.get("start_time")
                    end_time = session_data.get("end_time")
                    if start_time and end_time:
                        try:
                            start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                            duration = (end_dt - start_dt).total_seconds() / 3600  # hours
                            total_session_time += duration
                        except:
                            pass
                    
                    # Extract success and efficiency metrics
                    success_rate = session_data.get("success_rate", 0.0)
                    efficiency_score = session_data.get("efficiency_score", 0.0)
                    if success_rate is not None:
                        success_rates.append(success_rate)
                    if efficiency_score is not None:
                        efficiency_scores.append(efficiency_score)
                    
                    # Extract profession levels
                    profession = session_data.get("profession")
                    character_level = session_data.get("character_level")
                    if profession and character_level:
                        profession_levels[profession] = max(profession_levels.get(profession, 0), character_level)
                    
                    # Add to recent activity
                    recent_activity.append({
                        "session_id": session_data.get("session_id", ""),
                        "start_time": start_time,
                        "total_xp_gained": session_data.get("total_xp_gained", 0),
                        "total_credits_gained": session_data.get("total_credits_gained", 0),
                        "success_rate": success_rate,
                        "efficiency_score": efficiency_score
                    })
                    
                except Exception as e:
                    log_event(f"[PUBLIC_DATA_EXPORTER] Error processing session file {session_file}: {e}")
                    continue
            
            # Calculate averages
            average_session_duration = total_session_time / session_count if session_count > 0 else 0.0
            average_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0
            average_efficiency_score = sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 0.0
            
            # Sort recent activity by start time (most recent first)
            recent_activity.sort(key=lambda x: x.get("start_time", ""), reverse=True)
            
            metrics = BotMetrics(
                total_xp_gained=total_xp_gained,
                total_credits_gained=total_credits_gained,
                profession_levels=profession_levels,
                session_count=session_count,
                total_session_time=total_session_time,
                average_session_duration=average_session_duration,
                success_rate=average_success_rate,
                efficiency_score=average_efficiency_score,
                recent_activity=recent_activity[:20],  # Last 20 sessions
                last_updated=datetime.now().isoformat()
            )
            
            # Export to JSON
            self._export_to_json("bot_metrics.json", asdict(metrics))
            
            log_event(f"[PUBLIC_DATA_EXPORTER] Exported bot metrics: {session_count} sessions, {total_xp_gained} XP")
            return metrics
            
        except Exception as e:
            log_event(f"[PUBLIC_DATA_EXPORTER] Error exporting bot metrics: {e}")
            return self._create_empty_bot_metrics()

    def export_heroic_readiness(self) -> HeroicReadiness:
        """Export heroic readiness data."""
        try:
            # Load heroics data
            heroics_index_file = self.data_dir / "heroics" / "heroics_index.yml"
            if not heroics_index_file.exists():
                log_event("[PUBLIC_DATA_EXPORTER] Heroics index file not found")
                return self._create_empty_heroic_readiness()
            
            with open(heroics_index_file, 'r') as f:
                heroics_data = yaml.safe_load(f)
            
            # Load progress data for completion status
            progress_file = self.data_dir / "enhanced_progress_tracker.json"
            completed_heroics = set()
            if progress_file.exists():
                with open(progress_file, 'r') as f:
                    progress_data = json.load(f)
                
                # Find completed heroics
                for checklist_name, checklist_data in progress_data.get("checklists", {}).items():
                    if "heroic" in checklist_name.lower():
                        for item in checklist_data.get("items", []):
                            if item.get("status") == "completed":
                                completed_heroics.add(item.get("name", "").lower())
            
            # Process heroics data
            total_heroics = len(heroics_data.get("heroics", {}))
            completed_count = len(completed_heroics)
            heroic_completion_rate = completed_count / total_heroics if total_heroics > 0 else 0.0
            
            # Calculate readiness score based on character level
            # This is a simplified calculation - in practice, you'd check actual character level
            character_level = 80  # Placeholder - would come from character data
            readiness_score = min(1.0, character_level / 90.0)  # Normalize to 90 as max level
            
            # Find missing prerequisites
            missing_prerequisites = []
            if character_level < 80:
                missing_prerequisites.append(f"Character level {character_level}/80")
            
            # Generate recommended heroics
            recommended_heroics = []
            for heroic_id, heroic_info in heroics_data.get("heroics", {}).items():
                heroic_name = heroic_info.get("name", "")
                level_requirement = heroic_info.get("level_requirement", 0)
                
                if character_level >= level_requirement and heroic_name.lower() not in completed_heroics:
                    recommended_heroics.append({
                        "name": heroic_name,
                        "planet": heroic_info.get("planet", ""),
                        "level_requirement": level_requirement,
                        "group_size": heroic_info.get("group_size", ""),
                        "difficulty_tiers": heroic_info.get("difficulty_tiers", [])
                    })
            
            # Sort by level requirement
            recommended_heroics.sort(key=lambda x: x["level_requirement"])
            
            readiness = HeroicReadiness(
                total_heroics=total_heroics,
                completed_heroics=completed_count,
                available_heroics=len(recommended_heroics),
                heroic_completion_rate=heroic_completion_rate,
                character_level=character_level,
                readiness_score=readiness_score,
                missing_prerequisites=missing_prerequisites,
                recommended_heroics=recommended_heroics[:5],  # Top 5 recommendations
                last_updated=datetime.now().isoformat()
            )
            
            # Export to JSON
            self._export_to_json("heroic_readiness.json", asdict(readiness))
            
            log_event(f"[PUBLIC_DATA_EXPORTER] Exported heroic readiness: {completed_count}/{total_heroics} completed")
            return readiness
            
        except Exception as e:
            log_event(f"[PUBLIC_DATA_EXPORTER] Error exporting heroic readiness: {e}")
            return self._create_empty_heroic_readiness()

    def export_all_data(self) -> Dict[str, Any]:
        """Export all public data."""
        try:
            log_event("[PUBLIC_DATA_EXPORTER] Starting full data export")
            
            # Export all data types
            quest_summary = self.export_quest_tracking_summary()
            bot_metrics = self.export_bot_metrics()
            heroic_readiness = self.export_heroic_readiness()
            
            # Create combined export
            combined_data = {
                "export_metadata": {
                    "export_timestamp": datetime.now().isoformat(),
                    "ms11_version": "1.0.0",
                    "data_sources": [
                        "enhanced_progress_tracker.json",
                        "session_logs",
                        "heroics_index.yml"
                    ]
                },
                "quest_tracking": asdict(quest_summary),
                "bot_metrics": asdict(bot_metrics),
                "heroic_readiness": asdict(heroic_readiness)
            }
            
            # Export combined data
            self._export_to_json("public_data_export.json", combined_data)
            
            # Generate markdown summary
            self._generate_markdown_summary(combined_data)
            
            log_event("[PUBLIC_DATA_EXPORTER] Full data export completed successfully")
            return combined_data
            
        except Exception as e:
            log_event(f"[PUBLIC_DATA_EXPORTER] Error in full data export: {e}")
            return {"error": str(e)}

    def _export_to_json(self, filename: str, data: Dict[str, Any]) -> None:
        """Export data to JSON file."""
        try:
            export_path = self.export_dir / filename
            with open(export_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            log_event(f"[PUBLIC_DATA_EXPORTER] Exported {filename}")
        except Exception as e:
            log_event(f"[PUBLIC_DATA_EXPORTER] Error exporting {filename}: {e}")

    def _generate_markdown_summary(self, data: Dict[str, Any]) -> None:
        """Generate markdown summary for Eleventy."""
        try:
            md_content = f"""# MS11 Public Data Export

Generated: {data['export_metadata']['export_timestamp']}

## Quest Tracking Summary

- **Total Quests**: {data['quest_tracking']['total_quests']}
- **Completed**: {data['quest_tracking']['completed_quests']}
- **Completion Rate**: {data['quest_tracking']['quest_completion_rate']:.1%}
- **Total XP from Quests**: {data['quest_tracking']['total_xp_from_quests']:,}
- **Total Credits from Quests**: {data['quest_tracking']['total_credits_from_quests']:,}

## Bot Metrics

- **Total XP Gained**: {data['bot_metrics']['total_xp_gained']:,}
- **Total Credits Gained**: {data['bot_metrics']['total_credits_gained']:,}
- **Sessions**: {data['bot_metrics']['session_count']}
- **Success Rate**: {data['bot_metrics']['success_rate']:.1%}
- **Efficiency Score**: {data['bot_metrics']['efficiency_score']:.2f}

## Heroic Readiness

- **Total Heroics**: {data['heroic_readiness']['total_heroics']}
- **Completed**: {data['heroic_readiness']['completed_heroics']}
- **Completion Rate**: {data['heroic_readiness']['heroic_completion_rate']:.1%}
- **Character Level**: {data['heroic_readiness']['character_level']}
- **Readiness Score**: {data['heroic_readiness']['readiness_score']:.1%}

## Recent Activity

### Recent Quest Completions
"""
            
            for quest in data['quest_tracking']['recent_completions'][:5]:
                md_content += f"- {quest['name']} (+{quest['xp_reward']} XP)\n"
            
            md_content += "\n### Recent Sessions\n"
            for session in data['bot_metrics']['recent_activity'][:5]:
                md_content += f"- {session['session_id']}: +{session['total_xp_gained']} XP, {session['success_rate']:.1%} success\n"
            
            md_content += "\n### Recommended Heroics\n"
            for heroic in data['heroic_readiness']['recommended_heroics']:
                md_content += f"- {heroic['name']} (Level {heroic['level_requirement']}, {heroic['planet']})\n"
            
            # Write markdown file
            md_path = self.export_dir / "public_data_summary.md"
            with open(md_path, 'w') as f:
                f.write(md_content)
            
            log_event("[PUBLIC_DATA_EXPORTER] Generated markdown summary")
            
        except Exception as e:
            log_event(f"[PUBLIC_DATA_EXPORTER] Error generating markdown summary: {e}")

    def _create_empty_quest_summary(self) -> QuestTrackingSummary:
        """Create empty quest summary."""
        return QuestTrackingSummary(
            total_quests=0,
            completed_quests=0,
            active_quests=0,
            quest_completion_rate=0.0,
            total_xp_from_quests=0,
            total_credits_from_quests=0,
            recent_completions=[],
            quest_categories={},
            last_updated=datetime.now().isoformat()
        )

    def _create_empty_bot_metrics(self) -> BotMetrics:
        """Create empty bot metrics."""
        return BotMetrics(
            total_xp_gained=0,
            total_credits_gained=0,
            profession_levels={},
            session_count=0,
            total_session_time=0.0,
            average_session_duration=0.0,
            success_rate=0.0,
            efficiency_score=0.0,
            recent_activity=[],
            last_updated=datetime.now().isoformat()
        )

    def _create_empty_heroic_readiness(self) -> HeroicReadiness:
        """Create empty heroic readiness."""
        return HeroicReadiness(
            total_heroics=0,
            completed_heroics=0,
            available_heroics=0,
            heroic_completion_rate=0.0,
            character_level=0,
            readiness_score=0.0,
            missing_prerequisites=[],
            recommended_heroics=[],
            last_updated=datetime.now().isoformat()
        )


def create_public_data_exporter(data_dir: str = "data", session_logs_dir: str = "session_logs") -> PublicDataExporter:
    """Create and return a PublicDataExporter instance."""
    return PublicDataExporter(data_dir, session_logs_dir)


__all__ = [
    "PublicDataExporter",
    "create_public_data_exporter",
    "QuestTrackingSummary",
    "BotMetrics",
    "HeroicReadiness"
] 
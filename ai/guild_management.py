"""
MS11 Guild & Group Management System
Advanced guild operations, social coordination, and group dynamics management
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Tuple, Callable, Union, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
import threading
import uuid
import hashlib

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

try:
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.metrics import silhouette_score
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from core.structured_logging import StructuredLogger
from core.observability_integration import get_observability_manager, trace_gaming_operation

# Initialize logger
logger = StructuredLogger("guild_management")

class GuildRole(Enum):
    """Guild hierarchy roles"""
    GUILD_MASTER = "guild_master"
    OFFICER = "officer"
    VETERAN = "veteran"
    MEMBER = "member"
    RECRUIT = "recruit"
    GUEST = "guest"

class EventType(Enum):
    """Guild event types"""
    RAID = "raid"
    PVP = "pvp"
    CRAFTING = "crafting"
    SOCIAL = "social"
    TRAINING = "training"
    MEETING = "meeting"
    COMPETITION = "competition"
    EXPLORATION = "exploration"

class GuildActivityType(Enum):
    """Types of guild activities"""
    CHAT_MESSAGE = "chat_message"
    MEMBER_JOIN = "member_join"
    MEMBER_LEAVE = "member_leave"
    RANK_CHANGE = "rank_change"
    DONATION = "donation"
    WITHDRAWAL = "withdrawal"
    EVENT_CREATE = "event_create"
    EVENT_JOIN = "event_join"
    ACHIEVEMENT = "achievement"
    CONFLICT = "conflict"

class RelationshipType(Enum):
    """Inter-guild relationship types"""
    ALLIED = "allied"
    NEUTRAL = "neutral"
    RIVAL = "rival"
    ENEMY = "enemy"
    UNKNOWN = "unknown"

class CommunicationPriority(Enum):
    """Priority levels for guild communications"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

@dataclass
class GuildMember:
    """Guild member information"""
    member_id: str
    character_name: str
    guild_role: GuildRole
    join_date: datetime
    last_active: datetime
    contribution_score: float
    specializations: List[str]
    preferred_activities: List[EventType]
    availability_schedule: Dict[str, List[Tuple[int, int]]]  # day -> [(start_hour, end_hour)]
    reputation_score: float
    notes: str = ""
    is_online: bool = False
    current_activity: Optional[str] = None
    permissions: Dict[str, bool] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GuildEvent:
    """Guild event/activity"""
    event_id: str
    event_type: EventType
    title: str
    description: str
    organizer_id: str
    scheduled_time: datetime
    duration_hours: float
    location: Optional[str]
    requirements: Dict[str, Any]
    max_participants: Optional[int]
    participants: List[str]
    waitlist: List[str]
    status: str  # "scheduled", "active", "completed", "cancelled"
    recurring: bool = False
    recurrence_pattern: Optional[str] = None
    rewards: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GuildAlliance:
    """Guild alliance/relationship"""
    alliance_id: str
    guild_id: str
    other_guild_id: str
    relationship_type: RelationshipType
    established_date: datetime
    strength: float  # 0.0 to 1.0
    mutual: bool
    terms: Dict[str, Any]
    contact_person: Optional[str]
    notes: str = ""

@dataclass
class GuildActivity:
    """Guild activity log entry"""
    activity_id: str
    activity_type: GuildActivityType
    timestamp: datetime
    member_id: str
    details: Dict[str, Any]
    visibility: str  # "public", "members", "officers", "private"
    impact_score: float = 0.0

@dataclass
class CommunicationChannel:
    """Guild communication channel"""
    channel_id: str
    name: str
    channel_type: str  # "general", "officer", "raid", "pvp", "social"
    permissions: Dict[GuildRole, Dict[str, bool]]
    active: bool = True
    message_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    moderation_rules: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GuildResource:
    """Guild shared resources"""
    resource_id: str
    resource_type: str
    quantity: int
    reserved_quantity: int
    access_permissions: Dict[GuildRole, Dict[str, bool]]
    location: Optional[str]
    last_updated: datetime
    usage_history: List[Dict[str, Any]] = field(default_factory=list)

class GuildAnalytics:
    """Analytics engine for guild performance and insights"""
    
    def __init__(self):
        self.activity_metrics: Dict[str, Any] = {}
        self.member_metrics: Dict[str, Any] = {}
        self.trend_data: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
        
    def analyze_member_engagement(self, members: List[GuildMember], 
                                activities: List[GuildActivity]) -> Dict[str, Any]:
        """Analyze member engagement patterns"""
        try:
            analysis = {
                "total_members": len(members),
                "active_members": 0,
                "engagement_distribution": defaultdict(int),
                "activity_participation": defaultdict(int),
                "role_distribution": defaultdict(int)
            }
            
            # Analyze member activity
            recent_cutoff = datetime.utcnow() - timedelta(days=7)
            
            for member in members:
                # Role distribution
                analysis["role_distribution"][member.guild_role.value] += 1
                
                # Activity level
                if member.last_active > recent_cutoff:
                    analysis["active_members"] += 1
                    
                    # Categorize engagement level
                    days_since_active = (datetime.utcnow() - member.last_active).days
                    
                    if days_since_active <= 1:
                        analysis["engagement_distribution"]["daily"] += 1
                    elif days_since_active <= 3:
                        analysis["engagement_distribution"]["frequent"] += 1
                    elif days_since_active <= 7:
                        analysis["engagement_distribution"]["weekly"] += 1
                    else:
                        analysis["engagement_distribution"]["inactive"] += 1
            
            # Analyze activity participation
            for activity in activities[-100:]:  # Last 100 activities
                analysis["activity_participation"][activity.activity_type.value] += 1
            
            # Calculate engagement score
            if len(members) > 0:
                analysis["engagement_score"] = analysis["active_members"] / len(members)
            else:
                analysis["engagement_score"] = 0.0
                
            return analysis
            
        except Exception as e:
            logger.error("Member engagement analysis error", error=str(e))
            return {}
    
    def analyze_event_success(self, events: List[GuildEvent]) -> Dict[str, Any]:
        """Analyze event success patterns"""
        try:
            analysis = {
                "total_events": len(events),
                "completed_events": 0,
                "average_participation": 0.0,
                "event_type_success": defaultdict(list),
                "optimal_scheduling": defaultdict(int)
            }
            
            participation_rates = []
            
            for event in events:
                if event.status == "completed":
                    analysis["completed_events"] += 1
                    
                    # Calculate participation rate
                    if event.max_participants:
                        participation_rate = len(event.participants) / event.max_participants
                        participation_rates.append(participation_rate)
                        analysis["event_type_success"][event.event_type.value].append(participation_rate)
                    
                    # Analyze scheduling patterns
                    hour = event.scheduled_time.hour
                    day_of_week = event.scheduled_time.weekday()
                    
                    analysis["optimal_scheduling"][f"hour_{hour}"] += 1
                    analysis["optimal_scheduling"][f"day_{day_of_week}"] += 1
            
            if participation_rates:
                analysis["average_participation"] = sum(participation_rates) / len(participation_rates)
            
            # Calculate success rates by event type
            for event_type, rates in analysis["event_type_success"].items():
                if rates:
                    analysis["event_type_success"][event_type] = {
                        "average_rate": sum(rates) / len(rates),
                        "event_count": len(rates),
                        "max_rate": max(rates),
                        "min_rate": min(rates)
                    }
            
            return analysis
            
        except Exception as e:
            logger.error("Event success analysis error", error=str(e))
            return {}
    
    def identify_influential_members(self, members: List[GuildMember], 
                                   activities: List[GuildActivity]) -> List[Dict[str, Any]]:
        """Identify influential guild members"""
        try:
            influence_scores = {}
            
            for member in members:
                score = 0.0
                
                # Base score from role
                role_weights = {
                    GuildRole.GUILD_MASTER: 1.0,
                    GuildRole.OFFICER: 0.8,
                    GuildRole.VETERAN: 0.6,
                    GuildRole.MEMBER: 0.4,
                    GuildRole.RECRUIT: 0.2,
                    GuildRole.GUEST: 0.1
                }
                
                score += role_weights.get(member.guild_role, 0.2)
                
                # Activity influence
                member_activities = [a for a in activities if a.member_id == member.member_id]
                activity_influence = len(member_activities) * 0.1
                score += min(activity_influence, 0.5)  # Cap at 0.5
                
                # Contribution score
                score += member.contribution_score * 0.3
                
                # Reputation score
                score += member.reputation_score * 0.2
                
                influence_scores[member.member_id] = {
                    "member_id": member.member_id,
                    "character_name": member.character_name,
                    "influence_score": score,
                    "role": member.guild_role.value,
                    "activities_count": len(member_activities),
                    "contribution_score": member.contribution_score,
                    "reputation_score": member.reputation_score
                }
            
            # Sort by influence score
            influential_members = sorted(
                influence_scores.values(),
                key=lambda x: x["influence_score"],
                reverse=True
            )
            
            return influential_members[:10]  # Top 10 influential members
            
        except Exception as e:
            logger.error("Influential members analysis error", error=str(e))
            return []

class EventScheduler:
    """Advanced event scheduling and coordination"""
    
    def __init__(self):
        self.scheduled_events: Dict[str, GuildEvent] = {}
        self.recurring_events: List[str] = []
        self.scheduling_conflicts: List[Dict[str, Any]] = []
        
    def suggest_optimal_time(self, 
                           members: List[GuildMember],
                           duration_hours: float,
                           event_type: EventType,
                           days_ahead: int = 7) -> List[datetime]:
        """Suggest optimal times for events based on member availability"""
        
        try:
            suggestions = []
            now = datetime.utcnow()
            
            # Analyze member availability patterns
            availability_matrix = self._build_availability_matrix(members)
            
            # Check each potential time slot
            for days_offset in range(1, days_ahead + 1):
                check_date = now + timedelta(days=days_offset)
                day_of_week = check_date.strftime("%A").lower()
                
                # Check each hour of the day
                for hour in range(24):
                    potential_time = check_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    
                    # Calculate availability score for this time slot
                    availability_score = self._calculate_time_slot_score(
                        day_of_week, hour, duration_hours, availability_matrix
                    )
                    
                    if availability_score > 0.3:  # Minimum threshold
                        suggestions.append({
                            "datetime": potential_time,
                            "availability_score": availability_score,
                            "expected_participants": int(len(members) * availability_score),
                            "day_of_week": day_of_week,
                            "hour": hour
                        })
            
            # Sort by availability score
            suggestions.sort(key=lambda x: x["availability_score"], reverse=True)
            
            return [s["datetime"] for s in suggestions[:5]]  # Top 5 suggestions
            
        except Exception as e:
            logger.error("Optimal time suggestion error", error=str(e))
            return []
    
    def _build_availability_matrix(self, members: List[GuildMember]) -> Dict[str, Dict[int, float]]:
        """Build availability matrix from member schedules"""
        
        availability = defaultdict(lambda: defaultdict(float))
        
        for member in members:
            for day, time_slots in member.availability_schedule.items():
                for start_hour, end_hour in time_slots:
                    for hour in range(start_hour, end_hour):
                        availability[day][hour] += 1.0
        
        # Normalize by total members
        total_members = len(members)
        if total_members > 0:
            for day in availability:
                for hour in availability[day]:
                    availability[day][hour] /= total_members
        
        return availability
    
    def _calculate_time_slot_score(self, 
                                  day: str, 
                                  hour: int, 
                                  duration: float,
                                  availability_matrix: Dict[str, Dict[int, float]]) -> float:
        """Calculate availability score for a time slot"""
        
        try:
            scores = []
            
            # Check each hour of the event duration
            for hour_offset in range(int(duration) + 1):
                check_hour = (hour + hour_offset) % 24
                score = availability_matrix[day].get(check_hour, 0.0)
                scores.append(score)
            
            # Return average score across duration
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error("Time slot score calculation error", error=str(e))
            return 0.0
    
    def detect_scheduling_conflicts(self, new_event: GuildEvent, existing_events: List[GuildEvent]) -> List[Dict[str, Any]]:
        """Detect conflicts with existing events"""
        
        conflicts = []
        
        try:
            new_start = new_event.scheduled_time
            new_end = new_start + timedelta(hours=new_event.duration_hours)
            
            for existing in existing_events:
                existing_start = existing.scheduled_time
                existing_end = existing_start + timedelta(hours=existing.duration_hours)
                
                # Check for time overlap
                if (new_start < existing_end and new_end > existing_start):
                    # Calculate overlap details
                    overlap_start = max(new_start, existing_start)
                    overlap_end = min(new_end, existing_end)
                    overlap_hours = (overlap_end - overlap_start).total_seconds() / 3600
                    
                    # Check for participant overlap
                    participant_overlap = set(new_event.participants) & set(existing.participants)
                    
                    conflict_severity = "high" if participant_overlap else "medium"
                    
                    conflicts.append({
                        "conflicting_event_id": existing.event_id,
                        "conflicting_event_title": existing.title,
                        "overlap_hours": overlap_hours,
                        "participant_overlap": list(participant_overlap),
                        "conflict_severity": conflict_severity
                    })
            
        except Exception as e:
            logger.error("Conflict detection error", error=str(e))
        
        return conflicts

class SocialDynamicsAnalyzer:
    """Analyze guild social dynamics and relationships"""
    
    def __init__(self):
        self.interaction_graph = None
        if NETWORKX_AVAILABLE:
            self.interaction_graph = nx.Graph()
            
        self.relationship_scores: Dict[Tuple[str, str], float] = {}
        self.communication_patterns: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
    def analyze_member_interactions(self, activities: List[GuildActivity]) -> Dict[str, Any]:
        """Analyze interaction patterns between members"""
        
        try:
            interaction_counts = defaultdict(lambda: defaultdict(int))
            
            # Count interactions
            for activity in activities:
                if activity.activity_type == GuildActivityType.CHAT_MESSAGE:
                    sender = activity.member_id
                    
                    # Look for mentions or replies in details
                    if "mentions" in activity.details:
                        for mentioned in activity.details["mentions"]:
                            interaction_counts[sender][mentioned] += 1
                            
                            # Add to graph if available
                            if self.interaction_graph is not None:
                                if not self.interaction_graph.has_edge(sender, mentioned):
                                    self.interaction_graph.add_edge(sender, mentioned, weight=0)
                                
                                self.interaction_graph[sender][mentioned]["weight"] += 1
            
            # Calculate relationship strengths
            relationships = []
            for member1, interactions in interaction_counts.items():
                for member2, count in interactions.items():
                    if count > 3:  # Minimum interaction threshold
                        relationships.append({
                            "member1": member1,
                            "member2": member2,
                            "interaction_count": count,
                            "relationship_strength": min(count / 50.0, 1.0)  # Normalize to 0-1
                        })
            
            # Identify cliques/groups if networkx is available
            cliques = []
            if self.interaction_graph is not None and len(self.interaction_graph.nodes()) > 2:
                try:
                    # Find cliques of size 3 or larger
                    for clique in nx.find_cliques(self.interaction_graph):
                        if len(clique) >= 3:
                            cliques.append({
                                "members": list(clique),
                                "size": len(clique),
                                "cohesion": self._calculate_clique_cohesion(clique)
                            })
                except Exception as e:
                    logger.warning("Clique detection error", error=str(e))
            
            return {
                "total_interactions": sum(sum(interactions.values()) for interactions in interaction_counts.values()),
                "active_relationships": len(relationships),
                "strong_relationships": len([r for r in relationships if r["relationship_strength"] > 0.7]),
                "relationship_details": relationships,
                "social_cliques": cliques,
                "most_connected_members": self._find_most_connected_members(interaction_counts)
            }
            
        except Exception as e:
            logger.error("Member interaction analysis error", error=str(e))
            return {}
    
    def _calculate_clique_cohesion(self, clique: List[str]) -> float:
        """Calculate cohesion score for a clique"""
        
        if not self.interaction_graph or len(clique) < 2:
            return 0.0
        
        try:
            total_possible_edges = len(clique) * (len(clique) - 1) / 2
            actual_edges = 0
            total_weight = 0
            
            for i, member1 in enumerate(clique):
                for member2 in clique[i+1:]:
                    if self.interaction_graph.has_edge(member1, member2):
                        actual_edges += 1
                        total_weight += self.interaction_graph[member1][member2].get("weight", 1)
            
            if total_possible_edges == 0:
                return 0.0
            
            density = actual_edges / total_possible_edges
            avg_weight = total_weight / max(actual_edges, 1)
            
            return (density * 0.7) + (min(avg_weight / 10.0, 1.0) * 0.3)
            
        except Exception as e:
            logger.error("Clique cohesion calculation error", error=str(e))
            return 0.0
    
    def _find_most_connected_members(self, interaction_counts: Dict[str, Dict[str, int]]) -> List[Dict[str, Any]]:
        """Find members with highest social connectivity"""
        
        try:
            connectivity_scores = {}
            
            for member in interaction_counts:
                # Count total interactions (sent and received)
                sent_interactions = sum(interaction_counts[member].values())
                
                received_interactions = 0
                for other_member, interactions in interaction_counts.items():
                    if member in interactions:
                        received_interactions += interactions[member]
                
                total_interactions = sent_interactions + received_interactions
                unique_connections = len(interaction_counts[member])
                
                # Calculate connectivity score
                connectivity_score = (total_interactions * 0.7) + (unique_connections * 0.3)
                
                connectivity_scores[member] = {
                    "member_id": member,
                    "connectivity_score": connectivity_score,
                    "total_interactions": total_interactions,
                    "unique_connections": unique_connections
                }
            
            # Sort by connectivity score
            most_connected = sorted(
                connectivity_scores.values(),
                key=lambda x: x["connectivity_score"],
                reverse=True
            )
            
            return most_connected[:5]  # Top 5 most connected
            
        except Exception as e:
            logger.error("Most connected members analysis error", error=str(e))
            return []
    
    def detect_social_issues(self, members: List[GuildMember], activities: List[GuildActivity]) -> List[Dict[str, Any]]:
        """Detect potential social issues in the guild"""
        
        issues = []
        
        try:
            # Detect inactive members
            inactive_threshold = datetime.utcnow() - timedelta(days=14)
            inactive_members = [
                m for m in members 
                if m.last_active < inactive_threshold and m.guild_role != GuildRole.GUEST
            ]
            
            if inactive_members:
                issues.append({
                    "issue_type": "inactive_members",
                    "severity": "medium",
                    "description": f"{len(inactive_members)} members have been inactive for over 2 weeks",
                    "affected_members": [m.member_id for m in inactive_members],
                    "recommendation": "Consider reaching out to inactive members or reviewing retention policies"
                })
            
            # Detect potential conflicts
            conflict_activities = [
                a for a in activities 
                if a.activity_type == GuildActivityType.CONFLICT
            ]
            
            recent_conflicts = [
                a for a in conflict_activities 
                if a.timestamp > datetime.utcnow() - timedelta(days=7)
            ]
            
            if len(recent_conflicts) > 2:
                issues.append({
                    "issue_type": "frequent_conflicts",
                    "severity": "high",
                    "description": f"{len(recent_conflicts)} conflicts recorded in the past week",
                    "recommendation": "Review guild policies and consider mediation"
                })
            
            # Detect role imbalance
            role_counts = defaultdict(int)
            for member in members:
                role_counts[member.guild_role] += 1
            
            total_members = len(members)
            officer_ratio = (role_counts[GuildRole.OFFICER] + role_counts[GuildRole.GUILD_MASTER]) / max(total_members, 1)
            
            if officer_ratio > 0.3:
                issues.append({
                    "issue_type": "too_many_officers",
                    "severity": "medium",
                    "description": f"Officer ratio is {officer_ratio:.1%}, which may indicate role inflation",
                    "recommendation": "Review officer roles and responsibilities"
                })
            elif officer_ratio < 0.05 and total_members > 10:
                issues.append({
                    "issue_type": "too_few_officers",
                    "severity": "medium",
                    "description": f"Officer ratio is {officer_ratio:.1%}, which may indicate insufficient leadership",
                    "recommendation": "Consider promoting qualified members to officer roles"
                })
            
        except Exception as e:
            logger.error("Social issues detection error", error=str(e))
        
        return issues

class GuildManager:
    """Main guild management system"""
    
    def __init__(self,
                 guild_id: str,
                 guild_name: str,
                 max_members: int = 100):
        
        self.guild_id = guild_id
        self.guild_name = guild_name
        self.max_members = max_members
        
        # Core data
        self.members: Dict[str, GuildMember] = {}
        self.events: Dict[str, GuildEvent] = {}
        self.activities: deque = deque(maxlen=10000)
        self.alliances: Dict[str, GuildAlliance] = {}
        self.communication_channels: Dict[str, CommunicationChannel] = {}
        self.resources: Dict[str, GuildResource] = {}
        
        # Analysis components
        self.analytics = GuildAnalytics()
        self.event_scheduler = EventScheduler()
        self.social_analyzer = SocialDynamicsAnalyzer()
        
        # Guild settings
        self.guild_settings = {
            "auto_accept_applications": False,
            "min_level_requirement": 1,
            "activity_requirement_days": 30,
            "officer_promotion_threshold": 0.8,
            "resource_sharing_enabled": True,
            "event_auto_scheduling": True
        }
        
        # Background processing
        self.management_active = False
        self.management_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.member_callbacks: List[Callable[[str, GuildMember], None]] = []
        self.event_callbacks: List[Callable[[GuildEvent], None]] = []
        self.activity_callbacks: List[Callable[[GuildActivity], None]] = []
        
        # Observability
        self.observability_manager = get_observability_manager()
        
        # Initialize default channels
        self._initialize_default_channels()
        
        logger.info("Guild manager initialized", 
                   guild_id=guild_id, 
                   guild_name=guild_name)
    
    def _initialize_default_channels(self):
        """Initialize default communication channels"""
        
        default_channels = [
            {
                "channel_id": "general",
                "name": "General Chat",
                "channel_type": "general",
                "permissions": {
                    GuildRole.GUILD_MASTER: {"read": True, "write": True, "moderate": True},
                    GuildRole.OFFICER: {"read": True, "write": True, "moderate": True},
                    GuildRole.VETERAN: {"read": True, "write": True, "moderate": False},
                    GuildRole.MEMBER: {"read": True, "write": True, "moderate": False},
                    GuildRole.RECRUIT: {"read": True, "write": True, "moderate": False},
                    GuildRole.GUEST: {"read": True, "write": False, "moderate": False}
                }
            },
            {
                "channel_id": "officers",
                "name": "Officer Channel",
                "channel_type": "officer",
                "permissions": {
                    GuildRole.GUILD_MASTER: {"read": True, "write": True, "moderate": True},
                    GuildRole.OFFICER: {"read": True, "write": True, "moderate": False},
                    GuildRole.VETERAN: {"read": False, "write": False, "moderate": False},
                    GuildRole.MEMBER: {"read": False, "write": False, "moderate": False},
                    GuildRole.RECRUIT: {"read": False, "write": False, "moderate": False},
                    GuildRole.GUEST: {"read": False, "write": False, "moderate": False}
                }
            }
        ]
        
        for channel_data in default_channels:
            channel = CommunicationChannel(**channel_data)
            self.communication_channels[channel.channel_id] = channel
    
    @trace_gaming_operation("add_guild_member")
    def add_member(self, member: GuildMember) -> bool:
        """Add member to guild"""
        
        try:
            if len(self.members) >= self.max_members:
                logger.warning("Guild at maximum capacity", 
                             current=len(self.members),
                             max_members=self.max_members)
                return False
            
            # Check level requirement
            if member.character_name != "System":  # Skip for system entries
                min_level = self.guild_settings.get("min_level_requirement", 1)
                # Would need to get character level from somewhere
                # For now, assuming it's met
            
            self.members[member.member_id] = member
            
            # Record activity
            self._record_activity(GuildActivityType.MEMBER_JOIN, member.member_id, {
                "character_name": member.character_name,
                "role": member.guild_role.value
            })
            
            # Notify callbacks
            for callback in self.member_callbacks:
                try:
                    callback("added", member)
                except Exception as e:
                    logger.error("Member callback error", error=str(e))
            
            logger.info("Member added to guild",
                       guild_id=self.guild_id,
                       member_id=member.member_id,
                       character_name=member.character_name)
            
            return True
            
        except Exception as e:
            logger.error("Failed to add guild member", error=str(e))
            return False
    
    def remove_member(self, member_id: str, reason: str = "") -> bool:
        """Remove member from guild"""
        
        try:
            if member_id not in self.members:
                logger.warning("Member not found for removal", member_id=member_id)
                return False
            
            member = self.members[member_id]
            
            # Cancel any events organized by this member
            for event in self.events.values():
                if event.organizer_id == member_id:
                    event.status = "cancelled"
                
                # Remove from participants
                if member_id in event.participants:
                    event.participants.remove(member_id)
                if member_id in event.waitlist:
                    event.waitlist.remove(member_id)
            
            # Record activity
            self._record_activity(GuildActivityType.MEMBER_LEAVE, member_id, {
                "character_name": member.character_name,
                "reason": reason
            })
            
            # Remove member
            del self.members[member_id]
            
            # Notify callbacks
            for callback in self.member_callbacks:
                try:
                    callback("removed", member)
                except Exception as e:
                    logger.error("Member callback error", error=str(e))
            
            logger.info("Member removed from guild",
                       guild_id=self.guild_id,
                       member_id=member_id,
                       reason=reason)
            
            return True
            
        except Exception as e:
            logger.error("Failed to remove guild member", error=str(e))
            return False
    
    def change_member_role(self, member_id: str, new_role: GuildRole) -> bool:
        """Change member's guild role"""
        
        try:
            if member_id not in self.members:
                logger.warning("Member not found for role change", member_id=member_id)
                return False
            
            member = self.members[member_id]
            old_role = member.guild_role
            member.guild_role = new_role
            
            # Record activity
            self._record_activity(GuildActivityType.RANK_CHANGE, member_id, {
                "character_name": member.character_name,
                "old_role": old_role.value,
                "new_role": new_role.value
            })
            
            logger.info("Member role changed",
                       guild_id=self.guild_id,
                       member_id=member_id,
                       old_role=old_role.value,
                       new_role=new_role.value)
            
            return True
            
        except Exception as e:
            logger.error("Failed to change member role", error=str(e))
            return False
    
    @trace_gaming_operation("create_guild_event")
    def create_event(self, event: GuildEvent) -> bool:
        """Create guild event"""
        
        try:
            # Check for scheduling conflicts
            existing_events = list(self.events.values())
            conflicts = self.event_scheduler.detect_scheduling_conflicts(event, existing_events)
            
            if conflicts:
                high_conflicts = [c for c in conflicts if c["conflict_severity"] == "high"]
                if high_conflicts:
                    logger.warning("Event has high-severity conflicts",
                                 event_id=event.event_id,
                                 conflicts=len(high_conflicts))
                    # Could return False here to prevent scheduling
            
            self.events[event.event_id] = event
            
            # Record activity
            self._record_activity(GuildActivityType.EVENT_CREATE, event.organizer_id, {
                "event_id": event.event_id,
                "event_title": event.title,
                "event_type": event.event_type.value,
                "scheduled_time": event.scheduled_time.isoformat()
            })
            
            # Notify callbacks
            for callback in self.event_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error("Event callback error", error=str(e))
            
            logger.info("Guild event created",
                       guild_id=self.guild_id,
                       event_id=event.event_id,
                       title=event.title)
            
            return True
            
        except Exception as e:
            logger.error("Failed to create guild event", error=str(e))
            return False
    
    def join_event(self, event_id: str, member_id: str) -> bool:
        """Member joins guild event"""
        
        try:
            if event_id not in self.events:
                logger.warning("Event not found", event_id=event_id)
                return False
            
            if member_id not in self.members:
                logger.warning("Member not found", member_id=member_id)
                return False
            
            event = self.events[event_id]
            member = self.members[member_id]
            
            # Check if already joined
            if member_id in event.participants:
                logger.debug("Member already in event", member_id=member_id, event_id=event_id)
                return True
            
            # Check capacity
            if event.max_participants and len(event.participants) >= event.max_participants:
                # Add to waitlist
                if member_id not in event.waitlist:
                    event.waitlist.append(member_id)
                    logger.info("Member added to event waitlist", member_id=member_id, event_id=event_id)
                return True
            
            # Add to participants
            event.participants.append(member_id)
            
            # Record activity
            self._record_activity(GuildActivityType.EVENT_JOIN, member_id, {
                "event_id": event_id,
                "event_title": event.title,
                "character_name": member.character_name
            })
            
            logger.info("Member joined event",
                       guild_id=self.guild_id,
                       member_id=member_id,
                       event_id=event_id)
            
            return True
            
        except Exception as e:
            logger.error("Failed to join guild event", error=str(e))
            return False
    
    def _record_activity(self, activity_type: GuildActivityType, member_id: str, details: Dict[str, Any]):
        """Record guild activity"""
        
        try:
            activity = GuildActivity(
                activity_id=str(uuid.uuid4()),
                activity_type=activity_type,
                timestamp=datetime.utcnow(),
                member_id=member_id,
                details=details,
                visibility="members"  # Default visibility
            )
            
            self.activities.append(activity)
            
            # Notify callbacks
            for callback in self.activity_callbacks:
                try:
                    callback(activity)
                except Exception as e:
                    logger.error("Activity callback error", error=str(e))
                    
        except Exception as e:
            logger.error("Failed to record activity", error=str(e))
    
    @trace_gaming_operation("guild_analytics")
    async def generate_guild_report(self) -> Dict[str, Any]:
        """Generate comprehensive guild analytics report"""
        
        try:
            member_list = list(self.members.values())
            activity_list = list(self.activities)
            event_list = list(self.events.values())
            
            # Run analytics
            engagement_analysis = self.analytics.analyze_member_engagement(member_list, activity_list)
            event_analysis = self.analytics.analyze_event_success(event_list)
            influential_members = self.analytics.identify_influential_members(member_list, activity_list)
            
            social_analysis = self.social_analyzer.analyze_member_interactions(activity_list)
            social_issues = self.social_analyzer.detect_social_issues(member_list, activity_list)
            
            # Compile report
            report = {
                "guild_info": {
                    "guild_id": self.guild_id,
                    "guild_name": self.guild_name,
                    "total_members": len(self.members),
                    "max_members": self.max_members,
                    "member_capacity_used": len(self.members) / self.max_members,
                    "report_generated": datetime.utcnow().isoformat()
                },
                "member_engagement": engagement_analysis,
                "event_success": event_analysis,
                "influential_members": influential_members,
                "social_dynamics": social_analysis,
                "identified_issues": social_issues,
                "recent_activities": [
                    {
                        "type": a.activity_type.value,
                        "timestamp": a.timestamp.isoformat(),
                        "member_id": a.member_id,
                        "details": a.details
                    }
                    for a in list(self.activities)[-20:]  # Last 20 activities
                ],
                "upcoming_events": [
                    {
                        "event_id": e.event_id,
                        "title": e.title,
                        "type": e.event_type.value,
                        "scheduled_time": e.scheduled_time.isoformat(),
                        "participants": len(e.participants),
                        "max_participants": e.max_participants
                    }
                    for e in event_list
                    if e.scheduled_time > datetime.utcnow() and e.status == "scheduled"
                ]
            }
            
            return report
            
        except Exception as e:
            logger.error("Failed to generate guild report", error=str(e))
            return {"error": str(e)}
    
    def suggest_member_promotions(self) -> List[Dict[str, Any]]:
        """Suggest member promotions based on activity and contributions"""
        
        try:
            suggestions = []
            promotion_threshold = self.guild_settings.get("officer_promotion_threshold", 0.8)
            
            for member in self.members.values():
                # Skip if already high rank
                if member.guild_role in [GuildRole.GUILD_MASTER, GuildRole.OFFICER]:
                    continue
                
                # Calculate promotion score
                promotion_score = 0.0
                
                # Contribution score factor
                promotion_score += member.contribution_score * 0.4
                
                # Reputation score factor
                promotion_score += member.reputation_score * 0.3
                
                # Activity factor (days since join)
                days_member = (datetime.utcnow() - member.join_date).days
                activity_score = min(days_member / 90.0, 1.0)  # 90 days for full score
                promotion_score += activity_score * 0.3
                
                # Check if above threshold
                if promotion_score >= promotion_threshold:
                    suggested_role = None
                    
                    if member.guild_role == GuildRole.RECRUIT:
                        suggested_role = GuildRole.MEMBER
                    elif member.guild_role == GuildRole.MEMBER:
                        suggested_role = GuildRole.VETERAN
                    elif member.guild_role == GuildRole.VETERAN:
                        if promotion_score >= 0.9:  # Higher threshold for officer
                            suggested_role = GuildRole.OFFICER
                    
                    if suggested_role:
                        suggestions.append({
                            "member_id": member.member_id,
                            "character_name": member.character_name,
                            "current_role": member.guild_role.value,
                            "suggested_role": suggested_role.value,
                            "promotion_score": promotion_score,
                            "reasons": [
                                f"High contribution score ({member.contribution_score:.2f})",
                                f"Good reputation ({member.reputation_score:.2f})",
                                f"Active for {days_member} days"
                            ]
                        })
            
            # Sort by promotion score
            suggestions.sort(key=lambda x: x["promotion_score"], reverse=True)
            
            return suggestions
            
        except Exception as e:
            logger.error("Failed to suggest promotions", error=str(e))
            return []
    
    def start_guild_management(self):
        """Start background guild management"""
        
        if self.management_active:
            logger.warning("Guild management already active")
            return
        
        self.management_active = True
        self.management_thread = threading.Thread(
            target=self._management_loop,
            daemon=True
        )
        self.management_thread.start()
        
        logger.info("Guild management started", guild_id=self.guild_id)
    
    def stop_guild_management(self):
        """Stop background guild management"""
        
        if not self.management_active:
            return
        
        self.management_active = False
        if self.management_thread:
            self.management_thread.join(timeout=2.0)
        
        logger.info("Guild management stopped", guild_id=self.guild_id)
    
    def _management_loop(self):
        """Background guild management loop"""
        
        while self.management_active:
            try:
                # Periodic maintenance tasks
                self._cleanup_old_activities()
                self._check_inactive_members()
                self._process_event_reminders()
                
                time.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error("Guild management loop error", error=str(e))
                time.sleep(60)  # Shorter sleep on error
    
    def _cleanup_old_activities(self):
        """Clean up old activities"""
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            # Activities are in a deque with maxlen, so they auto-cleanup
            # But we can manually remove very old ones if needed
            while self.activities and self.activities[0].timestamp < cutoff_date:
                self.activities.popleft()
                
        except Exception as e:
            logger.error("Activity cleanup error", error=str(e))
    
    def _check_inactive_members(self):
        """Check for inactive members and flag for review"""
        
        try:
            activity_requirement_days = self.guild_settings.get("activity_requirement_days", 30)
            cutoff_date = datetime.utcnow() - timedelta(days=activity_requirement_days)
            
            inactive_count = 0
            
            for member in self.members.values():
                if member.last_active < cutoff_date and member.guild_role != GuildRole.GUEST:
                    inactive_count += 1
                    
                    # Could automatically demote or flag for officer review
                    if member.guild_role == GuildRole.RECRUIT:
                        # Auto-remove inactive recruits after extended period
                        extended_cutoff = datetime.utcnow() - timedelta(days=activity_requirement_days * 2)
                        if member.last_active < extended_cutoff:
                            self.remove_member(member.member_id, "Inactive recruit - auto-removed")
            
            if inactive_count > 0:
                logger.info("Inactive members detected", 
                           guild_id=self.guild_id,
                           count=inactive_count)
                
        except Exception as e:
            logger.error("Inactive member check error", error=str(e))
    
    def _process_event_reminders(self):
        """Process event reminders and notifications"""
        
        try:
            now = datetime.utcnow()
            reminder_window = timedelta(hours=24)  # 24 hour reminder
            
            for event in self.events.values():
                if event.status == "scheduled":
                    time_until_event = event.scheduled_time - now
                    
                    # Send reminders for events starting within 24 hours
                    if timedelta(0) <= time_until_event <= reminder_window:
                        # Would send notifications to participants
                        logger.debug("Event reminder triggered",
                                   guild_id=self.guild_id,
                                   event_id=event.event_id,
                                   event_title=event.title)
                    
                    # Mark past events as completed/missed
                    elif time_until_event < timedelta(0):
                        hours_past = abs(time_until_event.total_seconds()) / 3600
                        if hours_past > event.duration_hours + 1:  # 1 hour grace period
                            event.status = "completed"  # Or "missed" if no participants showed
                            
        except Exception as e:
            logger.error("Event reminder processing error", error=str(e))
    
    def add_member_callback(self, callback: Callable[[str, GuildMember], None]):
        """Add callback for member events"""
        self.member_callbacks.append(callback)
    
    def add_event_callback(self, callback: Callable[[GuildEvent], None]):
        """Add callback for event events"""
        self.event_callbacks.append(callback)
    
    def add_activity_callback(self, callback: Callable[[GuildActivity], None]):
        """Add callback for activity events"""
        self.activity_callbacks.append(callback)
    
    def get_guild_status(self) -> Dict[str, Any]:
        """Get current guild status"""
        
        try:
            return {
                "guild_id": self.guild_id,
                "guild_name": self.guild_name,
                "member_count": len(self.members),
                "max_members": self.max_members,
                "capacity_used": len(self.members) / self.max_members,
                "active_events": len([e for e in self.events.values() if e.status == "scheduled"]),
                "recent_activities": len([a for a in self.activities if a.timestamp > datetime.utcnow() - timedelta(days=7)]),
                "online_members": len([m for m in self.members.values() if m.is_online]),
                "management_active": self.management_active,
                "channels": len(self.communication_channels),
                "alliances": len(self.alliances)
            }
            
        except Exception as e:
            logger.error("Error getting guild status", error=str(e))
            return {"error": str(e)}

# Global guild manager instances
_guild_managers: Dict[str, GuildManager] = {}

def initialize_guild_manager(guild_id: str, guild_name: str, **kwargs) -> GuildManager:
    """Initialize guild manager for specific guild"""
    global _guild_managers
    
    manager = GuildManager(guild_id, guild_name, **kwargs)
    _guild_managers[guild_id] = manager
    return manager

def get_guild_manager(guild_id: str) -> Optional[GuildManager]:
    """Get guild manager for specific guild"""
    return _guild_managers.get(guild_id)
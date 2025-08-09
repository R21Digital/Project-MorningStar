"""
MS11 Behavioral Pattern Learning System
Advanced machine learning for user behavior analysis, adaptation, and optimization
"""

import asyncio
import numpy as np
import time
import json
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque, defaultdict
import threading
import pickle
import hashlib

try:
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.decomposition import PCA
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, silhouette_score
    import pandas as pd
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from core.structured_logging import StructuredLogger
from core.observability_integration import get_observability_manager, trace_gaming_operation

# Initialize logger
logger = StructuredLogger("behavioral_learning")

class BehaviorType(Enum):
    """Types of player behaviors to analyze"""
    COMBAT_PATTERN = "combat_pattern"
    QUEST_PREFERENCE = "quest_preference"
    MOVEMENT_STYLE = "movement_style"
    CRAFTING_BEHAVIOR = "crafting_behavior"
    SOCIAL_INTERACTION = "social_interaction"
    RESOURCE_MANAGEMENT = "resource_management"
    SKILL_PROGRESSION = "skill_progression"
    SESSION_TIMING = "session_timing"
    RISK_TOLERANCE = "risk_tolerance"
    EXPLORATION_STYLE = "exploration_style"

class LearningModelType(Enum):
    """Types of machine learning models"""
    CLUSTERING = "clustering"
    CLASSIFICATION = "classification"
    ANOMALY_DETECTION = "anomaly_detection"
    SEQUENCE_PREDICTION = "sequence_prediction"
    REINFORCEMENT = "reinforcement"
    NEURAL_NETWORK = "neural_network"

class AdaptationStrategy(Enum):
    """Strategies for behavior adaptation"""
    IMMEDIATE = "immediate"        # Apply changes immediately
    GRADUAL = "gradual"           # Apply changes gradually over time
    SCHEDULED = "scheduled"       # Apply changes at specific times
    CONDITIONAL = "conditional"   # Apply changes based on conditions
    USER_APPROVAL = "user_approval"  # Require user approval for changes

@dataclass
class BehaviorEvent:
    """Individual behavior event data"""
    timestamp: datetime
    behavior_type: BehaviorType
    action: str
    context: Dict[str, Any]
    outcome: Optional[str] = None
    success: bool = True
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BehaviorPattern:
    """Identified behavior pattern"""
    pattern_id: str
    behavior_type: BehaviorType
    description: str
    frequency: float
    confidence: float
    triggers: List[str]
    characteristics: Dict[str, Any]
    first_observed: datetime
    last_observed: datetime
    occurrence_count: int = 0

@dataclass
class BehaviorPrediction:
    """Predicted behavior"""
    predicted_action: str
    behavior_type: BehaviorType
    confidence: float
    expected_timestamp: datetime
    context_requirements: Dict[str, Any]
    alternative_actions: List[Tuple[str, float]]

@dataclass
class AdaptationRecommendation:
    """Behavior-based adaptation recommendation"""
    recommendation_id: str
    behavior_pattern: str
    suggested_change: str
    expected_benefit: str
    confidence: float
    strategy: AdaptationStrategy
    implementation_details: Dict[str, Any]
    created_at: datetime

class BehaviorSequenceDataset(Dataset):
    """PyTorch dataset for behavior sequences"""
    
    def __init__(self, sequences: List[List[BehaviorEvent]], sequence_length: int = 10):
        self.sequences = sequences
        self.sequence_length = sequence_length
        self.processed_sequences = self._process_sequences()
    
    def _process_sequences(self):
        """Convert behavior events to numerical sequences"""
        processed = []
        
        # Create action vocabulary
        all_actions = set()
        for seq in self.sequences:
            for event in seq:
                all_actions.add(event.action)
        
        self.action_vocab = {action: idx for idx, action in enumerate(all_actions)}
        self.vocab_size = len(self.action_vocab)
        
        # Process sequences
        for seq in self.sequences:
            if len(seq) >= self.sequence_length:
                for i in range(len(seq) - self.sequence_length + 1):
                    subseq = seq[i:i + self.sequence_length]
                    
                    # Convert to indices
                    indices = [self.action_vocab[event.action] for event in subseq]
                    
                    # Extract features (simplified)
                    features = []
                    for event in subseq:
                        # Time features
                        hour_of_day = event.timestamp.hour / 24.0
                        day_of_week = event.timestamp.weekday() / 7.0
                        
                        # Duration feature
                        duration_normalized = min(event.duration / 3600.0, 1.0)  # Max 1 hour
                        
                        # Success feature
                        success_feature = 1.0 if event.success else 0.0
                        
                        features.extend([hour_of_day, day_of_week, duration_normalized, success_feature])
                    
                    processed.append({
                        'sequence': torch.LongTensor(indices),
                        'features': torch.FloatTensor(features),
                        'target': indices[-1]  # Predict next action
                    })
        
        return processed
    
    def __len__(self):
        return len(self.processed_sequences)
    
    def __getitem__(self, idx):
        return self.processed_sequences[idx]

class BehaviorLSTM(nn.Module):
    """LSTM model for behavior sequence prediction"""
    
    def __init__(self, vocab_size: int, feature_dim: int, hidden_dim: int = 128, num_layers: int = 2):
        super(BehaviorLSTM, self).__init__()
        
        self.vocab_size = vocab_size
        self.feature_dim = feature_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # Embedding layer for actions
        self.action_embedding = nn.Embedding(vocab_size, 64)
        
        # LSTM for sequence modeling
        self.lstm = nn.LSTM(
            64 + feature_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            dropout=0.2
        )
        
        # Output layer
        self.output = nn.Linear(hidden_dim, vocab_size)
        
    def forward(self, action_sequence, features):
        batch_size, seq_len = action_sequence.size()
        
        # Embed actions
        action_embeds = self.action_embedding(action_sequence)
        
        # Reshape features to match sequence
        features = features.view(batch_size, seq_len, -1)
        
        # Combine embeddings and features
        combined = torch.cat([action_embeds, features], dim=-1)
        
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(combined)
        
        # Get last output for prediction
        output = self.output(lstm_out[:, -1, :])
        
        return output

class BehaviorAnalyzer:
    """Core behavior analysis engine"""
    
    def __init__(self, analysis_window_hours: int = 24, min_pattern_occurrences: int = 3):
        self.analysis_window_hours = analysis_window_hours
        self.min_pattern_occurrences = min_pattern_occurrences
        
        # Data storage
        self.behavior_events: deque = deque(maxlen=10000)
        self.identified_patterns: Dict[str, BehaviorPattern] = {}
        
        # ML models
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Analysis state
        self.last_analysis_time = None
        self.analysis_lock = threading.Lock()
        
    @trace_gaming_operation("behavior_analysis")
    def analyze_behavior_patterns(self, events: List[BehaviorEvent]) -> List[BehaviorPattern]:
        """Analyze events to identify behavior patterns"""
        
        if not SKLEARN_AVAILABLE:
            logger.warning("Scikit-learn not available, skipping pattern analysis")
            return []
        
        try:
            with self.analysis_lock:
                patterns = []
                
                # Group events by behavior type
                grouped_events = defaultdict(list)
                for event in events:
                    grouped_events[event.behavior_type].append(event)
                
                # Analyze each behavior type
                for behavior_type, type_events in grouped_events.items():
                    if len(type_events) >= self.min_pattern_occurrences:
                        behavior_patterns = self._analyze_behavior_type(behavior_type, type_events)
                        patterns.extend(behavior_patterns)
                
                return patterns
                
        except Exception as e:
            logger.error("Behavior pattern analysis error", error=str(e))
            return []
    
    def _analyze_behavior_type(self, behavior_type: BehaviorType, events: List[BehaviorEvent]) -> List[BehaviorPattern]:
        """Analyze patterns for specific behavior type"""
        patterns = []
        
        try:
            # Extract features from events
            features = self._extract_features(events)
            
            if len(features) < self.min_pattern_occurrences:
                return patterns
            
            # Perform clustering to identify patterns
            clustering_results = self._perform_clustering(features)
            
            # Convert clusters to behavior patterns
            for cluster_id, cluster_events in clustering_results.items():
                if len(cluster_events) >= self.min_pattern_occurrences:
                    pattern = self._create_behavior_pattern(behavior_type, cluster_events, cluster_id)
                    patterns.append(pattern)
            
        except Exception as e:
            logger.error("Behavior type analysis error", behavior_type=behavior_type.value, error=str(e))
        
        return patterns
    
    def _extract_features(self, events: List[BehaviorEvent]) -> np.ndarray:
        """Extract numerical features from behavior events"""
        features = []
        
        for event in events:
            feature_vector = []
            
            # Temporal features
            feature_vector.append(event.timestamp.hour)  # Hour of day
            feature_vector.append(event.timestamp.weekday())  # Day of week
            feature_vector.append(event.duration)  # Duration
            
            # Success rate feature
            feature_vector.append(1.0 if event.success else 0.0)
            
            # Context features (simplified - hash common context values)
            context_hash = hashlib.md5(str(sorted(event.context.items())).encode()).hexdigest()
            feature_vector.append(int(context_hash[:8], 16) % 1000)  # Reduced hash
            
            # Action frequency (approximate)
            action_frequency = sum(1 for e in events if e.action == event.action) / len(events)
            feature_vector.append(action_frequency)
            
            features.append(feature_vector)
        
        return np.array(features)
    
    def _perform_clustering(self, features: np.ndarray) -> Dict[int, List[BehaviorEvent]]:
        """Perform clustering to identify behavior patterns"""
        
        try:
            # Standardize features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Try different clustering methods
            clustering_methods = [
                ("kmeans", KMeans(n_clusters=min(5, len(features) // 2), random_state=42)),
                ("dbscan", DBSCAN(eps=0.5, min_samples=self.min_pattern_occurrences))
            ]
            
            best_clusters = None
            best_score = -1
            
            for method_name, clusterer in clustering_methods:
                try:
                    cluster_labels = clusterer.fit_predict(features_scaled)
                    
                    # Calculate silhouette score if we have multiple clusters
                    unique_labels = np.unique(cluster_labels)
                    if len(unique_labels) > 1 and -1 not in unique_labels:
                        score = silhouette_score(features_scaled, cluster_labels)
                        if score > best_score:
                            best_score = score
                            best_clusters = cluster_labels
                            
                except Exception as e:
                    logger.warning(f"Clustering method {method_name} failed", error=str(e))
                    continue
            
            if best_clusters is not None:
                # Group events by cluster
                clustered_events = defaultdict(list)
                for i, label in enumerate(best_clusters):
                    if label != -1:  # Ignore noise points in DBSCAN
                        clustered_events[label].append(self.behavior_events[i])
                
                return dict(clustered_events)
            
        except Exception as e:
            logger.error("Clustering error", error=str(e))
        
        return {}
    
    def _create_behavior_pattern(self, 
                               behavior_type: BehaviorType, 
                               events: List[BehaviorEvent], 
                               cluster_id: int) -> BehaviorPattern:
        """Create behavior pattern from clustered events"""
        
        # Calculate pattern characteristics
        actions = [e.action for e in events]
        most_common_action = max(set(actions), key=actions.count)
        
        # Calculate frequency (events per hour)
        time_span = (max(e.timestamp for e in events) - min(e.timestamp for e in events)).total_seconds() / 3600
        frequency = len(events) / max(time_span, 1.0)
        
        # Identify triggers (common context keys)
        all_contexts = [e.context for e in events]
        common_triggers = []
        
        if all_contexts:
            all_keys = set()
            for ctx in all_contexts:
                all_keys.update(ctx.keys())
            
            for key in all_keys:
                if sum(1 for ctx in all_contexts if key in ctx) / len(all_contexts) > 0.7:
                    common_triggers.append(key)
        
        # Calculate confidence based on consistency
        success_rate = sum(1 for e in events if e.success) / len(events)
        action_consistency = actions.count(most_common_action) / len(actions)
        confidence = (success_rate + action_consistency) / 2.0
        
        pattern_id = f"{behavior_type.value}_cluster_{cluster_id}_{int(time.time())}"
        
        return BehaviorPattern(
            pattern_id=pattern_id,
            behavior_type=behavior_type,
            description=f"Common {behavior_type.value} pattern: {most_common_action}",
            frequency=frequency,
            confidence=confidence,
            triggers=common_triggers,
            characteristics={
                "primary_action": most_common_action,
                "success_rate": success_rate,
                "avg_duration": sum(e.duration for e in events) / len(events),
                "time_of_day_preference": self._analyze_time_preference(events)
            },
            first_observed=min(e.timestamp for e in events),
            last_observed=max(e.timestamp for e in events),
            occurrence_count=len(events)
        )
    
    def _analyze_time_preference(self, events: List[BehaviorEvent]) -> Dict[str, float]:
        """Analyze time-of-day preferences"""
        hours = [e.timestamp.hour for e in events]
        
        # Group into time periods
        morning = sum(1 for h in hours if 6 <= h < 12) / len(hours)
        afternoon = sum(1 for h in hours if 12 <= h < 18) / len(hours)
        evening = sum(1 for h in hours if 18 <= h < 24) / len(hours)
        night = sum(1 for h in hours if 0 <= h < 6) / len(hours)
        
        return {
            "morning": morning,
            "afternoon": afternoon,
            "evening": evening,
            "night": night
        }

class BehaviorPredictor:
    """Behavior prediction engine using machine learning"""
    
    def __init__(self):
        self.sequence_model = None
        self.classification_models: Dict[BehaviorType, Any] = {}
        self.prediction_history: List[BehaviorPrediction] = []
        
    @trace_gaming_operation("behavior_prediction")
    def predict_next_behavior(self, 
                            recent_events: List[BehaviorEvent],
                            context: Dict[str, Any]) -> Optional[BehaviorPrediction]:
        """Predict next likely behavior based on recent events"""
        
        if not recent_events:
            return None
        
        try:
            # Use different prediction methods based on available data
            predictions = []
            
            # Sequence-based prediction
            if self.sequence_model and len(recent_events) >= 5:
                seq_prediction = self._predict_with_sequence_model(recent_events)
                if seq_prediction:
                    predictions.append(seq_prediction)
            
            # Pattern-based prediction
            pattern_prediction = self._predict_with_patterns(recent_events, context)
            if pattern_prediction:
                predictions.append(pattern_prediction)
            
            # Statistical prediction
            stats_prediction = self._predict_with_statistics(recent_events, context)
            if stats_prediction:
                predictions.append(stats_prediction)
            
            # Combine predictions
            if predictions:
                return self._combine_predictions(predictions)
            
        except Exception as e:
            logger.error("Behavior prediction error", error=str(e))
        
        return None
    
    def _predict_with_sequence_model(self, events: List[BehaviorEvent]) -> Optional[BehaviorPrediction]:
        """Predict using trained sequence model"""
        
        if not TORCH_AVAILABLE or not self.sequence_model:
            return None
        
        try:
            # Convert events to model input format
            # This is a simplified version - in practice would need proper preprocessing
            
            # For now, return None as this requires trained model
            return None
            
        except Exception as e:
            logger.error("Sequence model prediction error", error=str(e))
            return None
    
    def _predict_with_patterns(self, 
                              events: List[BehaviorEvent], 
                              context: Dict[str, Any]) -> Optional[BehaviorPrediction]:
        """Predict based on identified patterns"""
        
        try:
            # Analyze recent behavior type distribution
            recent_behavior_types = [e.behavior_type for e in events[-10:]]
            
            if not recent_behavior_types:
                return None
            
            # Find most common recent behavior type
            most_common_type = max(set(recent_behavior_types), key=recent_behavior_types.count)
            
            # Predict likely next action within that behavior type
            same_type_events = [e for e in events if e.behavior_type == most_common_type]
            
            if len(same_type_events) >= 2:
                recent_actions = [e.action for e in same_type_events[-5:]]
                
                # Simple frequency-based prediction
                action_counts = defaultdict(int)
                for action in recent_actions:
                    action_counts[action] += 1
                
                predicted_action = max(action_counts, key=action_counts.get)
                confidence = action_counts[predicted_action] / len(recent_actions)
                
                return BehaviorPrediction(
                    predicted_action=predicted_action,
                    behavior_type=most_common_type,
                    confidence=confidence,
                    expected_timestamp=datetime.utcnow() + timedelta(minutes=5),
                    context_requirements=context,
                    alternative_actions=[]
                )
            
        except Exception as e:
            logger.error("Pattern-based prediction error", error=str(e))
        
        return None
    
    def _predict_with_statistics(self, 
                               events: List[BehaviorEvent], 
                               context: Dict[str, Any]) -> Optional[BehaviorPrediction]:
        """Predict using statistical analysis"""
        
        try:
            current_time = datetime.utcnow()
            current_hour = current_time.hour
            current_weekday = current_time.weekday()
            
            # Find events from similar time periods
            similar_time_events = [
                e for e in events
                if abs(e.timestamp.hour - current_hour) <= 2
                and e.timestamp.weekday() == current_weekday
            ]
            
            if len(similar_time_events) >= 3:
                # Calculate action probabilities
                actions = [e.action for e in similar_time_events]
                action_probs = {}
                
                for action in set(actions):
                    action_probs[action] = actions.count(action) / len(actions)
                
                # Get most likely action
                predicted_action = max(action_probs, key=action_probs.get)
                confidence = action_probs[predicted_action]
                
                # Determine behavior type
                behavior_types = [e.behavior_type for e in similar_time_events if e.action == predicted_action]
                predicted_type = max(set(behavior_types), key=behavior_types.count) if behavior_types else BehaviorType.QUEST_PREFERENCE
                
                return BehaviorPrediction(
                    predicted_action=predicted_action,
                    behavior_type=predicted_type,
                    confidence=confidence,
                    expected_timestamp=current_time + timedelta(minutes=10),
                    context_requirements=context,
                    alternative_actions=[(action, prob) for action, prob in sorted(action_probs.items(), key=lambda x: x[1], reverse=True)[1:4]]
                )
            
        except Exception as e:
            logger.error("Statistical prediction error", error=str(e))
        
        return None
    
    def _combine_predictions(self, predictions: List[BehaviorPrediction]) -> BehaviorPrediction:
        """Combine multiple predictions into best estimate"""
        
        # Simple weighted average based on confidence
        total_confidence = sum(p.confidence for p in predictions)
        
        if total_confidence == 0:
            return predictions[0]
        
        # Weight predictions by confidence
        action_scores = defaultdict(float)
        
        for pred in predictions:
            weight = pred.confidence / total_confidence
            action_scores[pred.predicted_action] += weight
        
        # Get best action
        best_action = max(action_scores, key=action_scores.get)
        best_confidence = action_scores[best_action]
        
        # Use prediction with highest confidence for other details
        best_pred = max(predictions, key=lambda p: p.confidence)
        
        return BehaviorPrediction(
            predicted_action=best_action,
            behavior_type=best_pred.behavior_type,
            confidence=best_confidence,
            expected_timestamp=best_pred.expected_timestamp,
            context_requirements=best_pred.context_requirements,
            alternative_actions=[]
        )

class BehaviorAdaptationEngine:
    """Engine for generating and applying behavior-based adaptations"""
    
    def __init__(self):
        self.adaptation_history: List[AdaptationRecommendation] = []
        self.active_adaptations: Dict[str, Any] = {}
        self.adaptation_effectiveness: Dict[str, float] = {}
        
    @trace_gaming_operation("adaptation_generation")
    def generate_adaptations(self, 
                           patterns: List[BehaviorPattern],
                           current_performance: Dict[str, float]) -> List[AdaptationRecommendation]:
        """Generate adaptation recommendations based on behavior patterns"""
        
        recommendations = []
        
        try:
            for pattern in patterns:
                # Analyze pattern for optimization opportunities
                adaptations = self._analyze_pattern_for_adaptations(pattern, current_performance)
                recommendations.extend(adaptations)
            
            # Sort by expected benefit
            recommendations.sort(key=lambda x: x.confidence, reverse=True)
            
            return recommendations[:10]  # Limit to top 10 recommendations
            
        except Exception as e:
            logger.error("Adaptation generation error", error=str(e))
            return []
    
    def _analyze_pattern_for_adaptations(self, 
                                       pattern: BehaviorPattern, 
                                       performance: Dict[str, float]) -> List[AdaptationRecommendation]:
        """Analyze single pattern for adaptation opportunities"""
        
        adaptations = []
        
        try:
            # Combat pattern optimizations
            if pattern.behavior_type == BehaviorType.COMBAT_PATTERN:
                if pattern.characteristics.get("success_rate", 1.0) < 0.8:
                    adaptations.append(AdaptationRecommendation(
                        recommendation_id=f"combat_optimize_{pattern.pattern_id}",
                        behavior_pattern=pattern.pattern_id,
                        suggested_change="Adjust combat timing and skill rotation",
                        expected_benefit="Increase combat success rate by 15-20%",
                        confidence=0.85,
                        strategy=AdaptationStrategy.GRADUAL,
                        implementation_details={
                            "delay_between_actions": 0.2,
                            "skill_priority_adjustment": True,
                            "health_threshold_adjustment": 0.3
                        },
                        created_at=datetime.utcnow()
                    ))
            
            # Quest preference optimizations
            elif pattern.behavior_type == BehaviorType.QUEST_PREFERENCE:
                if pattern.frequency < 1.0:  # Less than 1 quest per hour
                    adaptations.append(AdaptationRecommendation(
                        recommendation_id=f"quest_efficiency_{pattern.pattern_id}",
                        behavior_pattern=pattern.pattern_id,
                        suggested_change="Optimize quest selection and routing",
                        expected_benefit="Increase quest completion rate by 25%",
                        confidence=0.78,
                        strategy=AdaptationStrategy.IMMEDIATE,
                        implementation_details={
                            "prefer_nearby_quests": True,
                            "batch_similar_quests": True,
                            "skip_low_reward_quests": True
                        },
                        created_at=datetime.utcnow()
                    ))
            
            # Movement style optimizations
            elif pattern.behavior_type == BehaviorType.MOVEMENT_STYLE:
                avg_duration = pattern.characteristics.get("avg_duration", 0)
                if avg_duration > 300:  # More than 5 minutes per movement
                    adaptations.append(AdaptationRecommendation(
                        recommendation_id=f"movement_optimize_{pattern.pattern_id}",
                        behavior_pattern=pattern.pattern_id,
                        suggested_change="Optimize pathfinding and movement efficiency",
                        expected_benefit="Reduce travel time by 30%",
                        confidence=0.82,
                        strategy=AdaptationStrategy.IMMEDIATE,
                        implementation_details={
                            "use_waypoints": True,
                            "avoid_obstacles": True,
                            "mount_usage": True
                        },
                        created_at=datetime.utcnow()
                    ))
            
            # Session timing optimizations
            elif pattern.behavior_type == BehaviorType.SESSION_TIMING:
                time_prefs = pattern.characteristics.get("time_of_day_preference", {})
                
                # Suggest break scheduling based on patterns
                if max(time_prefs.values()) > 0.4:  # Strong time preference
                    peak_time = max(time_prefs, key=time_prefs.get)
                    
                    adaptations.append(AdaptationRecommendation(
                        recommendation_id=f"session_optimize_{pattern.pattern_id}",
                        behavior_pattern=pattern.pattern_id,
                        suggested_change=f"Schedule intensive activities during {peak_time} hours",
                        expected_benefit="Improve efficiency by leveraging peak performance time",
                        confidence=0.75,
                        strategy=AdaptationStrategy.SCHEDULED,
                        implementation_details={
                            "preferred_time_window": peak_time,
                            "activity_scheduling": True,
                            "break_reminders": True
                        },
                        created_at=datetime.utcnow()
                    ))
            
            # Resource management optimizations
            elif pattern.behavior_type == BehaviorType.RESOURCE_MANAGEMENT:
                if pattern.confidence < 0.6:  # Inconsistent resource management
                    adaptations.append(AdaptationRecommendation(
                        recommendation_id=f"resource_optimize_{pattern.pattern_id}",
                        behavior_pattern=pattern.pattern_id,
                        suggested_change="Implement automated resource management",
                        expected_benefit="Reduce resource waste and improve efficiency",
                        confidence=0.80,
                        strategy=AdaptationStrategy.USER_APPROVAL,
                        implementation_details={
                            "auto_sell_threshold": 0.9,
                            "inventory_management": True,
                            "resource_alerts": True
                        },
                        created_at=datetime.utcnow()
                    ))
            
        except Exception as e:
            logger.error("Pattern adaptation analysis error", pattern_id=pattern.pattern_id, error=str(e))
        
        return adaptations
    
    def apply_adaptation(self, recommendation: AdaptationRecommendation) -> bool:
        """Apply an adaptation recommendation"""
        
        try:
            logger.info("Applying behavioral adaptation",
                       recommendation_id=recommendation.recommendation_id,
                       strategy=recommendation.strategy.value)
            
            # Store as active adaptation
            self.active_adaptations[recommendation.recommendation_id] = {
                "recommendation": recommendation,
                "applied_at": datetime.utcnow(),
                "status": "active"
            }
            
            # Apply based on strategy
            if recommendation.strategy == AdaptationStrategy.IMMEDIATE:
                return self._apply_immediate_adaptation(recommendation)
            elif recommendation.strategy == AdaptationStrategy.GRADUAL:
                return self._apply_gradual_adaptation(recommendation)
            elif recommendation.strategy == AdaptationStrategy.SCHEDULED:
                return self._apply_scheduled_adaptation(recommendation)
            elif recommendation.strategy == AdaptationStrategy.CONDITIONAL:
                return self._apply_conditional_adaptation(recommendation)
            elif recommendation.strategy == AdaptationStrategy.USER_APPROVAL:
                return self._request_user_approval(recommendation)
            
            return True
            
        except Exception as e:
            logger.error("Adaptation application error", 
                        recommendation_id=recommendation.recommendation_id, 
                        error=str(e))
            return False
    
    def _apply_immediate_adaptation(self, recommendation: AdaptationRecommendation) -> bool:
        """Apply adaptation immediately"""
        # Implementation would integrate with automation system
        logger.info("Applied immediate adaptation", recommendation_id=recommendation.recommendation_id)
        return True
    
    def _apply_gradual_adaptation(self, recommendation: AdaptationRecommendation) -> bool:
        """Apply adaptation gradually over time"""
        # Implementation would schedule gradual changes
        logger.info("Started gradual adaptation", recommendation_id=recommendation.recommendation_id)
        return True
    
    def _apply_scheduled_adaptation(self, recommendation: AdaptationRecommendation) -> bool:
        """Schedule adaptation for specific times"""
        # Implementation would integrate with scheduler
        logger.info("Scheduled adaptation", recommendation_id=recommendation.recommendation_id)
        return True
    
    def _apply_conditional_adaptation(self, recommendation: AdaptationRecommendation) -> bool:
        """Set up conditional adaptation triggers"""
        # Implementation would set up condition monitoring
        logger.info("Set up conditional adaptation", recommendation_id=recommendation.recommendation_id)
        return True
    
    def _request_user_approval(self, recommendation: AdaptationRecommendation) -> bool:
        """Request user approval for adaptation"""
        # Implementation would present to user interface
        logger.info("Requested user approval for adaptation", recommendation_id=recommendation.recommendation_id)
        return True

class BehaviorLearningManager:
    """Main behavioral learning manager"""
    
    def __init__(self,
                 data_retention_days: int = 30,
                 analysis_interval_hours: int = 6,
                 enable_predictions: bool = True,
                 enable_adaptations: bool = True):
        
        self.data_retention_days = data_retention_days
        self.analysis_interval_hours = analysis_interval_hours
        self.enable_predictions = enable_predictions
        self.enable_adaptations = enable_adaptations
        
        # Core components
        self.analyzer = BehaviorAnalyzer()
        self.predictor = BehaviorPredictor() if enable_predictions else None
        self.adaptation_engine = BehaviorAdaptationEngine() if enable_adaptations else None
        
        # Data management
        self.behavior_events: deque = deque(maxlen=50000)
        self.learned_patterns: Dict[str, BehaviorPattern] = {}
        self.active_predictions: List[BehaviorPrediction] = []
        
        # Background processing
        self.learning_active = False
        self.learning_thread: Optional[threading.Thread] = None
        
        # Callbacks
        self.pattern_callbacks: List[Callable[[BehaviorPattern], None]] = []
        self.prediction_callbacks: List[Callable[[BehaviorPrediction], None]] = []
        self.adaptation_callbacks: List[Callable[[AdaptationRecommendation], None]] = []
        
        # Performance tracking
        self.learning_stats = {
            "total_events_processed": 0,
            "patterns_identified": 0,
            "predictions_made": 0,
            "adaptations_applied": 0,
            "last_analysis_time": None
        }
        
        # Observability
        self.observability_manager = get_observability_manager()
    
    @trace_gaming_operation("record_behavior")
    def record_behavior_event(self, event: BehaviorEvent):
        """Record a new behavior event"""
        try:
            self.behavior_events.append(event)
            self.learning_stats["total_events_processed"] += 1
            
            # Trigger real-time analysis if needed
            if len(self.behavior_events) % 100 == 0:
                asyncio.create_task(self._trigger_analysis())
            
        except Exception as e:
            logger.error("Failed to record behavior event", error=str(e))
    
    @trace_gaming_operation("behavioral_learning")
    async def perform_learning_cycle(self) -> Dict[str, Any]:
        """Perform complete learning cycle"""
        
        start_time = time.time()
        results = {
            "patterns_found": 0,
            "predictions_made": 0,
            "adaptations_generated": 0,
            "processing_time": 0.0
        }
        
        try:
            # Get recent events for analysis
            recent_events = list(self.behavior_events)[-1000:]  # Last 1000 events
            
            if not recent_events:
                return results
            
            # Step 1: Analyze behavior patterns
            logger.info("Starting behavior pattern analysis", events_count=len(recent_events))
            
            new_patterns = self.analyzer.analyze_behavior_patterns(recent_events)
            
            for pattern in new_patterns:
                self.learned_patterns[pattern.pattern_id] = pattern
                
                # Notify callbacks
                for callback in self.pattern_callbacks:
                    try:
                        callback(pattern)
                    except Exception as e:
                        logger.error("Pattern callback error", error=str(e))
            
            results["patterns_found"] = len(new_patterns)
            self.learning_stats["patterns_identified"] += len(new_patterns)
            
            # Step 2: Generate predictions
            if self.predictor and recent_events:
                logger.info("Generating behavior predictions")
                
                prediction = await self._generate_prediction(recent_events[-10:])
                
                if prediction:
                    self.active_predictions.append(prediction)
                    results["predictions_made"] = 1
                    self.learning_stats["predictions_made"] += 1
                    
                    # Notify callbacks
                    for callback in self.prediction_callbacks:
                        try:
                            callback(prediction)
                        except Exception as e:
                            logger.error("Prediction callback error", error=str(e))
            
            # Step 3: Generate adaptations
            if self.adaptation_engine and new_patterns:
                logger.info("Generating behavioral adaptations")
                
                current_performance = await self._calculate_current_performance()
                adaptations = self.adaptation_engine.generate_adaptations(new_patterns, current_performance)
                
                results["adaptations_generated"] = len(adaptations)
                self.learning_stats["adaptations_applied"] += len(adaptations)
                
                # Apply high-confidence adaptations
                for adaptation in adaptations:
                    if adaptation.confidence > 0.8:
                        self.adaptation_engine.apply_adaptation(adaptation)
                        
                        # Notify callbacks
                        for callback in self.adaptation_callbacks:
                            try:
                                callback(adaptation)
                            except Exception as e:
                                logger.error("Adaptation callback error", error=str(e))
            
            # Update performance stats
            processing_time = time.time() - start_time
            results["processing_time"] = processing_time
            self.learning_stats["last_analysis_time"] = datetime.utcnow()
            
            logger.info("Learning cycle completed", **results)
            
            return results
            
        except Exception as e:
            logger.error("Learning cycle error", error=str(e))
            results["processing_time"] = time.time() - start_time
            return results
    
    async def _trigger_analysis(self):
        """Trigger background analysis"""
        try:
            if not self.learning_active:
                await self.perform_learning_cycle()
        except Exception as e:
            logger.error("Background analysis error", error=str(e))
    
    async def _generate_prediction(self, recent_events: List[BehaviorEvent]) -> Optional[BehaviorPrediction]:
        """Generate behavior prediction"""
        try:
            context = {
                "timestamp": datetime.utcnow().isoformat(),
                "session_duration": len(recent_events) * 60,  # Approximate
                "recent_success_rate": sum(1 for e in recent_events if e.success) / len(recent_events)
            }
            
            return self.predictor.predict_next_behavior(recent_events, context)
            
        except Exception as e:
            logger.error("Prediction generation error", error=str(e))
            return None
    
    async def _calculate_current_performance(self) -> Dict[str, float]:
        """Calculate current performance metrics"""
        try:
            recent_events = list(self.behavior_events)[-100:]
            
            if not recent_events:
                return {}
            
            performance = {
                "overall_success_rate": sum(1 for e in recent_events if e.success) / len(recent_events),
                "avg_event_duration": sum(e.duration for e in recent_events) / len(recent_events),
                "events_per_hour": len(recent_events) / max((
                    (recent_events[-1].timestamp - recent_events[0].timestamp).total_seconds() / 3600
                ), 1.0)
            }
            
            # Behavior-specific performance
            for behavior_type in BehaviorType:
                type_events = [e for e in recent_events if e.behavior_type == behavior_type]
                if type_events:
                    performance[f"{behavior_type.value}_success_rate"] = (
                        sum(1 for e in type_events if e.success) / len(type_events)
                    )
            
            return performance
            
        except Exception as e:
            logger.error("Performance calculation error", error=str(e))
            return {}
    
    def start_continuous_learning(self):
        """Start continuous background learning"""
        if self.learning_active:
            logger.warning("Learning already active")
            return
        
        self.learning_active = True
        self.learning_thread = threading.Thread(
            target=self._learning_loop,
            daemon=True
        )
        self.learning_thread.start()
        
        logger.info("Started continuous behavioral learning", 
                   interval_hours=self.analysis_interval_hours)
    
    def stop_continuous_learning(self):
        """Stop continuous background learning"""
        if not self.learning_active:
            return
        
        self.learning_active = False
        if self.learning_thread:
            self.learning_thread.join(timeout=2.0)
        
        logger.info("Stopped continuous behavioral learning")
    
    def _learning_loop(self):
        """Background learning loop"""
        while self.learning_active:
            try:
                # Run learning cycle
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                results = loop.run_until_complete(self.perform_learning_cycle())
                
                logger.debug("Background learning cycle completed", **results)
                
                loop.close()
                
                # Sleep until next cycle
                time.sleep(self.analysis_interval_hours * 3600)
                
            except Exception as e:
                logger.error("Learning loop error", error=str(e))
                time.sleep(300)  # Wait 5 minutes before retry
    
    def add_pattern_callback(self, callback: Callable[[BehaviorPattern], None]):
        """Add callback for new patterns"""
        self.pattern_callbacks.append(callback)
    
    def add_prediction_callback(self, callback: Callable[[BehaviorPrediction], None]):
        """Add callback for new predictions"""
        self.prediction_callbacks.append(callback)
    
    def add_adaptation_callback(self, callback: Callable[[AdaptationRecommendation], None]):
        """Add callback for new adaptations"""
        self.adaptation_callbacks.append(callback)
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning performance statistics"""
        stats = self.learning_stats.copy()
        stats["total_patterns"] = len(self.learned_patterns)
        stats["active_predictions"] = len(self.active_predictions)
        stats["events_in_buffer"] = len(self.behavior_events)
        
        return stats
    
    def save_learning_data(self, filepath: str):
        """Save learning data to file"""
        try:
            data = {
                "patterns": {k: asdict(v) for k, v in self.learned_patterns.items()},
                "events": [asdict(e) for e in list(self.behavior_events)[-1000:]],  # Last 1000 events
                "predictions": [asdict(p) for p in self.active_predictions],
                "stats": self.learning_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info("Saved learning data", filepath=filepath)
            
        except Exception as e:
            logger.error("Failed to save learning data", error=str(e))
    
    def load_learning_data(self, filepath: str):
        """Load learning data from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Restore patterns
            for pattern_id, pattern_data in data.get("patterns", {}).items():
                pattern_data["first_observed"] = datetime.fromisoformat(pattern_data["first_observed"])
                pattern_data["last_observed"] = datetime.fromisoformat(pattern_data["last_observed"])
                pattern_data["behavior_type"] = BehaviorType(pattern_data["behavior_type"])
                
                self.learned_patterns[pattern_id] = BehaviorPattern(**pattern_data)
            
            # Restore events
            for event_data in data.get("events", []):
                event_data["timestamp"] = datetime.fromisoformat(event_data["timestamp"])
                event_data["behavior_type"] = BehaviorType(event_data["behavior_type"])
                
                self.behavior_events.append(BehaviorEvent(**event_data))
            
            # Restore stats
            self.learning_stats.update(data.get("stats", {}))
            
            logger.info("Loaded learning data", 
                       patterns=len(self.learned_patterns),
                       events=len(self.behavior_events))
            
        except Exception as e:
            logger.error("Failed to load learning data", error=str(e))
    
    async def shutdown(self):
        """Shutdown behavioral learning manager"""
        try:
            # Stop continuous learning
            self.stop_continuous_learning()
            
            logger.info("Behavioral learning manager shutdown completed")
            
        except Exception as e:
            logger.error("Failed to shutdown behavioral learning manager", error=str(e))

# Global behavioral learning manager instance
_global_behavior_manager: Optional[BehaviorLearningManager] = None

def initialize_behavioral_learning(**kwargs) -> BehaviorLearningManager:
    """Initialize global behavioral learning manager"""
    global _global_behavior_manager
    
    _global_behavior_manager = BehaviorLearningManager(**kwargs)
    return _global_behavior_manager

def get_behavior_learning_manager() -> Optional[BehaviorLearningManager]:
    """Get global behavioral learning manager instance"""
    return _global_behavior_manager
"""
MS11 Predictive Analytics System
Advanced analytics for gaming performance, resource optimization, and strategic decision making
"""

import asyncio
import numpy as np
import time
import json
from typing import Dict, List, Any, Optional, Tuple, Callable, Union, NamedTuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque, defaultdict
import threading
import math
import statistics
from concurrent.futures import ThreadPoolExecutor

try:
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import mean_squared_error, accuracy_score, r2_score
    from sklearn.cluster import KMeans
    import pandas as pd
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import scipy.stats as stats
    from scipy.optimize import minimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from core.structured_logging import StructuredLogger
from core.observability_integration import get_observability_manager, trace_gaming_operation

# Initialize logger
logger = StructuredLogger("predictive_analytics")

class PredictionType(Enum):
    """Types of predictions supported"""
    EXPERIENCE_GAIN = "experience_gain"
    RESOURCE_CONSUMPTION = "resource_consumption"
    QUEST_COMPLETION_TIME = "quest_completion_time"
    COMBAT_OUTCOME = "combat_outcome"
    EQUIPMENT_DURABILITY = "equipment_durability"
    SKILL_PROGRESSION = "skill_progression"
    SESSION_DURATION = "session_duration"
    DEATH_RISK = "death_risk"
    MARKET_PRICES = "market_prices"
    SERVER_POPULATION = "server_population"

class AnalyticsModel(Enum):
    """Machine learning models for analytics"""
    LINEAR_REGRESSION = "linear_regression"
    POLYNOMIAL_REGRESSION = "polynomial_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    LOGISTIC_REGRESSION = "logistic_regression"
    TIME_SERIES = "time_series"
    ENSEMBLE = "ensemble"

class ConfidenceLevel(Enum):
    """Confidence levels for predictions"""
    LOW = "low"           # 0-60%
    MEDIUM = "medium"     # 61-80%
    HIGH = "high"         # 81-95%
    VERY_HIGH = "very_high"  # 95%+

@dataclass
class DataPoint:
    """Single data point for analytics"""
    timestamp: datetime
    prediction_type: PredictionType
    features: Dict[str, float]
    target_value: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PredictionResult:
    """Prediction result with confidence metrics"""
    prediction_type: PredictionType
    predicted_value: float
    confidence_score: float
    confidence_level: ConfidenceLevel
    prediction_interval: Tuple[float, float]
    model_used: AnalyticsModel
    features_used: List[str]
    timestamp: datetime
    valid_until: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Set confidence level based on score
        if self.confidence_score >= 0.95:
            self.confidence_level = ConfidenceLevel.VERY_HIGH
        elif self.confidence_score >= 0.81:
            self.confidence_level = ConfidenceLevel.HIGH
        elif self.confidence_score >= 0.61:
            self.confidence_level = ConfidenceLevel.MEDIUM
        else:
            self.confidence_level = ConfidenceLevel.LOW

@dataclass
class AnalyticsInsight:
    """Actionable insight from analytics"""
    insight_id: str
    title: str
    description: str
    category: str
    impact_level: str  # "low", "medium", "high", "critical"
    recommended_actions: List[str]
    supporting_data: Dict[str, Any]
    confidence: float
    generated_at: datetime
    expires_at: Optional[datetime] = None

@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_type: AnalyticsModel
    prediction_type: PredictionType
    accuracy: float
    mse: float
    r2_score: float
    last_trained: datetime
    training_samples: int
    cross_val_score: float
    feature_importance: Dict[str, float] = field(default_factory=dict)

class FeatureEngineering:
    """Feature engineering utilities"""
    
    @staticmethod
    def extract_temporal_features(timestamp: datetime) -> Dict[str, float]:
        """Extract temporal features from timestamp"""
        return {
            "hour_of_day": timestamp.hour / 24.0,
            "day_of_week": timestamp.weekday() / 7.0,
            "day_of_month": timestamp.day / 31.0,
            "month": timestamp.month / 12.0,
            "is_weekend": float(timestamp.weekday() >= 5),
            "is_peak_hours": float(18 <= timestamp.hour <= 22),
            "time_since_epoch": timestamp.timestamp() / (365.25 * 24 * 3600)  # Years since epoch
        }
    
    @staticmethod
    def extract_gaming_features(game_state: Dict[str, Any]) -> Dict[str, float]:
        """Extract gaming-specific features"""
        features = {}
        
        # Character features
        if "character" in game_state:
            char = game_state["character"]
            features.update({
                "character_level": float(char.get("level", 1)),
                "health_percentage": float(char.get("health", 100)) / 100.0,
                "mana_percentage": float(char.get("mana", 100)) / 100.0,
                "stamina_percentage": float(char.get("stamina", 100)) / 100.0,
                "experience_to_next_level": float(char.get("exp_to_next", 0))
            })
        
        # Combat features
        if "combat" in game_state:
            combat = game_state["combat"]
            features.update({
                "in_combat": float(combat.get("active", False)),
                "combat_duration": float(combat.get("duration", 0)),
                "enemies_nearby": float(combat.get("enemy_count", 0)),
                "damage_taken_rate": float(combat.get("damage_rate", 0)),
                "damage_dealt_rate": float(combat.get("dps", 0))
            })
        
        # Location features
        if "location" in game_state:
            loc = game_state["location"]
            features.update({
                "zone_danger_level": float(loc.get("danger", 1)),
                "distance_to_town": float(loc.get("town_distance", 0)),
                "player_density": float(loc.get("player_count", 0)),
                "resource_availability": float(loc.get("resources", 1))
            })
        
        # Equipment features
        if "equipment" in game_state:
            eq = game_state["equipment"]
            features.update({
                "avg_durability": sum(item.get("durability", 100) for item in eq.values()) / max(len(eq), 1) / 100.0,
                "equipment_value": float(sum(item.get("value", 0) for item in eq.values())),
                "weapon_damage": float(eq.get("weapon", {}).get("damage", 0)),
                "armor_rating": float(eq.get("armor", {}).get("protection", 0))
            })
        
        return features
    
    @staticmethod
    def create_lag_features(data: List[float], lags: List[int]) -> Dict[str, float]:
        """Create lagged features from time series data"""
        features = {}
        
        for lag in lags:
            if len(data) > lag:
                features[f"lag_{lag}"] = data[-lag - 1]
            else:
                features[f"lag_{lag}"] = 0.0
        
        return features
    
    @staticmethod
    def create_statistical_features(data: List[float], window: int = 10) -> Dict[str, float]:
        """Create statistical features from recent data"""
        if len(data) < 2:
            return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "trend": 0.0}
        
        recent_data = data[-window:]
        
        features = {
            "mean": statistics.mean(recent_data),
            "std": statistics.stdev(recent_data) if len(recent_data) > 1 else 0.0,
            "min": min(recent_data),
            "max": max(recent_data),
            "range": max(recent_data) - min(recent_data)
        }
        
        # Calculate trend (simple linear regression slope)
        if len(recent_data) >= 3:
            x = list(range(len(recent_data)))
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(recent_data)
            sum_xy = sum(x[i] * recent_data[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            if n * sum_x2 - sum_x ** 2 != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
                features["trend"] = slope
            else:
                features["trend"] = 0.0
        else:
            features["trend"] = 0.0
        
        return features

class PredictiveModel:
    """Individual predictive model wrapper"""
    
    def __init__(self, 
                 model_type: AnalyticsModel,
                 prediction_type: PredictionType,
                 feature_names: List[str]):
        
        self.model_type = model_type
        self.prediction_type = prediction_type
        self.feature_names = feature_names
        
        # Model components
        self.model = None
        self.scaler = StandardScaler()
        self.polynomial_features = None
        
        # Performance tracking
        self.performance = None
        self.is_trained = False
        
        # Training history
        self.training_history: List[Dict[str, Any]] = []
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the ML model based on type"""
        if not SKLEARN_AVAILABLE:
            logger.warning("Scikit-learn not available, model initialization failed")
            return
        
        try:
            if self.model_type == AnalyticsModel.LINEAR_REGRESSION:
                self.model = LinearRegression()
                
            elif self.model_type == AnalyticsModel.POLYNOMIAL_REGRESSION:
                self.model = LinearRegression()
                self.polynomial_features = PolynomialFeatures(degree=2, interaction_only=True)
                
            elif self.model_type == AnalyticsModel.RANDOM_FOREST:
                self.model = RandomForestRegressor(n_estimators=100, random_state=42)
                
            elif self.model_type == AnalyticsModel.GRADIENT_BOOSTING:
                self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
                
            elif self.model_type == AnalyticsModel.LOGISTIC_REGRESSION:
                self.model = LogisticRegression(random_state=42)
            
        except Exception as e:
            logger.error("Model initialization error", model_type=self.model_type.value, error=str(e))
    
    @trace_gaming_operation("model_training")
    def train(self, data_points: List[DataPoint]) -> bool:
        """Train the model on provided data"""
        
        if not self.model or not data_points:
            return False
        
        try:
            # Extract features and targets
            X = []
            y = []
            
            for point in data_points:
                if point.target_value is not None:
                    # Build feature vector in consistent order
                    feature_vector = [point.features.get(name, 0.0) for name in self.feature_names]
                    X.append(feature_vector)
                    y.append(point.target_value)
            
            if len(X) < 10:  # Need minimum samples for training
                logger.warning("Insufficient training data", samples=len(X))
                return False
            
            X = np.array(X)
            y = np.array(y)
            
            # Split data for validation
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Apply polynomial features if needed
            if self.polynomial_features:
                X_train_scaled = self.polynomial_features.fit_transform(X_train_scaled)
                X_test_scaled = self.polynomial_features.transform(X_test_scaled)
            
            # Train model
            start_time = time.time()
            self.model.fit(X_train_scaled, y_train)
            training_time = time.time() - start_time
            
            # Evaluate model
            train_pred = self.model.predict(X_train_scaled)
            test_pred = self.model.predict(X_test_scaled)
            
            train_score = r2_score(y_train, train_pred)
            test_score = r2_score(y_test, test_pred)
            mse = mean_squared_error(y_test, test_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
            cv_mean = cv_scores.mean()
            
            # Feature importance (if available)
            feature_importance = {}
            if hasattr(self.model, 'feature_importances_'):
                importance_scores = self.model.feature_importances_
                if self.polynomial_features:
                    # For polynomial features, map back to original features (simplified)
                    feature_importance = {name: importance_scores[i] if i < len(importance_scores) else 0.0 
                                        for i, name in enumerate(self.feature_names)}
                else:
                    feature_importance = {name: importance_scores[i] 
                                        for i, name in enumerate(self.feature_names)}
            
            # Store performance metrics
            self.performance = ModelPerformance(
                model_type=self.model_type,
                prediction_type=self.prediction_type,
                accuracy=test_score,
                mse=mse,
                r2_score=test_score,
                last_trained=datetime.utcnow(),
                training_samples=len(X),
                cross_val_score=cv_mean,
                feature_importance=feature_importance
            )
            
            self.is_trained = True
            
            # Record training history
            self.training_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "samples": len(X),
                "train_score": train_score,
                "test_score": test_score,
                "cv_score": cv_mean,
                "training_time": training_time
            })
            
            logger.info("Model training completed",
                       model_type=self.model_type.value,
                       prediction_type=self.prediction_type.value,
                       test_score=test_score,
                       samples=len(X))
            
            return True
            
        except Exception as e:
            logger.error("Model training error", 
                        model_type=self.model_type.value,
                        prediction_type=self.prediction_type.value,
                        error=str(e))
            return False
    
    @trace_gaming_operation("model_prediction")
    def predict(self, features: Dict[str, float], 
                confidence_interval: float = 0.95) -> Optional[PredictionResult]:
        """Make prediction with confidence intervals"""
        
        if not self.is_trained or not self.model:
            return None
        
        try:
            # Build feature vector
            feature_vector = [features.get(name, 0.0) for name in self.feature_names]
            X = np.array([feature_vector])
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Apply polynomial features if needed
            if self.polynomial_features:
                X_scaled = self.polynomial_features.transform(X_scaled)
            
            # Make prediction
            prediction = self.model.predict(X_scaled)[0]
            
            # Calculate confidence score based on model performance
            confidence_score = self.performance.r2_score if self.performance else 0.5
            
            # Calculate prediction interval (simplified)
            if self.performance:
                std_error = math.sqrt(self.performance.mse)
                margin = std_error * 1.96  # Approximate 95% confidence interval
                prediction_interval = (prediction - margin, prediction + margin)
            else:
                prediction_interval = (prediction * 0.8, prediction * 1.2)
            
            return PredictionResult(
                prediction_type=self.prediction_type,
                predicted_value=prediction,
                confidence_score=confidence_score,
                confidence_level=ConfidenceLevel.MEDIUM,  # Will be set in __post_init__
                prediction_interval=prediction_interval,
                model_used=self.model_type,
                features_used=self.feature_names.copy(),
                timestamp=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(hours=1),
                metadata={
                    "feature_importance": self.performance.feature_importance if self.performance else {},
                    "training_samples": self.performance.training_samples if self.performance else 0
                }
            )
            
        except Exception as e:
            logger.error("Prediction error",
                        model_type=self.model_type.value,
                        prediction_type=self.prediction_type.value,
                        error=str(e))
            return None

class InsightGenerator:
    """Generate actionable insights from analytics"""
    
    def __init__(self):
        self.insight_templates = self._load_insight_templates()
        self.generated_insights: Dict[str, AnalyticsInsight] = {}
    
    def _load_insight_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load insight generation templates"""
        return {
            "low_efficiency": {
                "title": "Low Efficiency Detected",
                "category": "performance",
                "template": "Your {activity} efficiency is {percentage}% below optimal. Consider {recommendations}."
            },
            "resource_waste": {
                "title": "Resource Management Issue",
                "category": "economy",
                "template": "You're wasting approximately {amount} {resource} per hour. This could be optimized."
            },
            "timing_optimization": {
                "title": "Optimal Timing Opportunity",
                "category": "strategy",
                "template": "Data shows {time_period} is {percentage}% more effective for {activity}."
            },
            "risk_warning": {
                "title": "Elevated Risk Detected",
                "category": "safety",
                "template": "Current conditions indicate {percentage}% higher risk of {risk_type}."
            },
            "skill_progression": {
                "title": "Skill Development Insight",
                "category": "progression",
                "template": "At current pace, you'll reach {skill} level {level} in {timeframe}."
            }
        }
    
    def generate_insights(self, 
                         predictions: List[PredictionResult],
                         historical_data: List[DataPoint],
                         current_state: Dict[str, Any]) -> List[AnalyticsInsight]:
        """Generate insights from predictions and data"""
        
        insights = []
        
        try:
            # Performance efficiency insights
            insights.extend(self._analyze_efficiency(predictions, historical_data))
            
            # Resource optimization insights
            insights.extend(self._analyze_resource_usage(predictions, historical_data))
            
            # Timing optimization insights
            insights.extend(self._analyze_timing_patterns(historical_data))
            
            # Risk assessment insights
            insights.extend(self._analyze_risk_factors(predictions, current_state))
            
            # Progression insights
            insights.extend(self._analyze_progression(predictions, historical_data))
            
            # Store generated insights
            for insight in insights:
                self.generated_insights[insight.insight_id] = insight
            
        except Exception as e:
            logger.error("Insight generation error", error=str(e))
        
        return insights
    
    def _analyze_efficiency(self, 
                           predictions: List[PredictionResult],
                           historical_data: List[DataPoint]) -> List[AnalyticsInsight]:
        """Analyze efficiency patterns"""
        insights = []
        
        try:
            # Look for experience gain efficiency
            exp_predictions = [p for p in predictions if p.prediction_type == PredictionType.EXPERIENCE_GAIN]
            
            if exp_predictions:
                current_exp_rate = exp_predictions[0].predicted_value
                
                # Calculate historical average
                exp_data = [dp for dp in historical_data if dp.prediction_type == PredictionType.EXPERIENCE_GAIN]
                if len(exp_data) > 10:
                    historical_avg = sum(dp.target_value for dp in exp_data if dp.target_value) / len([dp for dp in exp_data if dp.target_value])
                    
                    if current_exp_rate < historical_avg * 0.8:  # 20% below average
                        efficiency_drop = ((historical_avg - current_exp_rate) / historical_avg) * 100
                        
                        insights.append(AnalyticsInsight(
                            insight_id=f"low_exp_efficiency_{int(time.time())}",
                            title="Experience Gain Efficiency Below Average",
                            description=f"Current experience rate is {efficiency_drop:.1f}% below your historical average.",
                            category="performance",
                            impact_level="medium",
                            recommended_actions=[
                                "Switch to higher-level content",
                                "Optimize skill rotation",
                                "Check for better equipment",
                                "Consider grouping with other players"
                            ],
                            supporting_data={
                                "current_rate": current_exp_rate,
                                "historical_average": historical_avg,
                                "efficiency_drop": efficiency_drop
                            },
                            confidence=exp_predictions[0].confidence_score,
                            generated_at=datetime.utcnow(),
                            expires_at=datetime.utcnow() + timedelta(hours=2)
                        ))
            
        except Exception as e:
            logger.error("Efficiency analysis error", error=str(e))
        
        return insights
    
    def _analyze_resource_usage(self, 
                               predictions: List[PredictionResult],
                               historical_data: List[DataPoint]) -> List[AnalyticsInsight]:
        """Analyze resource consumption patterns"""
        insights = []
        
        try:
            resource_predictions = [p for p in predictions if p.prediction_type == PredictionType.RESOURCE_CONSUMPTION]
            
            for pred in resource_predictions:
                if pred.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]:
                    predicted_consumption = pred.predicted_value
                    
                    # Analyze if consumption is unusually high
                    resource_data = [dp for dp in historical_data[-100:] 
                                   if dp.prediction_type == PredictionType.RESOURCE_CONSUMPTION]
                    
                    if resource_data:
                        avg_consumption = sum(dp.target_value for dp in resource_data if dp.target_value) / len([dp for dp in resource_data if dp.target_value])
                        
                        if predicted_consumption > avg_consumption * 1.5:  # 50% above average
                            waste_amount = predicted_consumption - avg_consumption
                            
                            insights.append(AnalyticsInsight(
                                insight_id=f"high_resource_usage_{int(time.time())}",
                                title="Elevated Resource Consumption Detected",
                                description=f"Predicted resource usage is {((predicted_consumption/avg_consumption - 1) * 100):.1f}% above normal.",
                                category="economy",
                                impact_level="medium",
                                recommended_actions=[
                                    "Review current activities for efficiency",
                                    "Consider alternative approaches",
                                    "Check for equipment or skill optimizations",
                                    "Monitor resource prices for better timing"
                                ],
                                supporting_data={
                                    "predicted_consumption": predicted_consumption,
                                    "average_consumption": avg_consumption,
                                    "waste_estimate": waste_amount
                                },
                                confidence=pred.confidence_score,
                                generated_at=datetime.utcnow(),
                                expires_at=datetime.utcnow() + timedelta(hours=1)
                            ))
            
        except Exception as e:
            logger.error("Resource usage analysis error", error=str(e))
        
        return insights
    
    def _analyze_timing_patterns(self, historical_data: List[DataPoint]) -> List[AnalyticsInsight]:
        """Analyze timing patterns for optimization"""
        insights = []
        
        try:
            # Group data by hour of day
            hourly_performance = defaultdict(list)
            
            for dp in historical_data[-500:]:  # Last 500 data points
                if dp.target_value is not None:
                    hour = dp.timestamp.hour
                    hourly_performance[hour].append(dp.target_value)
            
            # Find best and worst performing hours
            if len(hourly_performance) >= 5:  # Need data from multiple hours
                avg_performance_by_hour = {
                    hour: sum(values) / len(values)
                    for hour, values in hourly_performance.items()
                    if len(values) >= 3
                }
                
                if avg_performance_by_hour:
                    best_hour = max(avg_performance_by_hour, key=avg_performance_by_hour.get)
                    worst_hour = min(avg_performance_by_hour, key=avg_performance_by_hour.get)
                    
                    best_performance = avg_performance_by_hour[best_hour]
                    worst_performance = avg_performance_by_hour[worst_hour]
                    
                    if best_performance > worst_performance * 1.3:  # 30% difference
                        improvement = ((best_performance / worst_performance - 1) * 100)
                        
                        insights.append(AnalyticsInsight(
                            insight_id=f"timing_optimization_{int(time.time())}",
                            title="Optimal Gaming Hours Identified",
                            description=f"Performance is {improvement:.1f}% better during {best_hour}:00 compared to {worst_hour}:00.",
                            category="strategy",
                            impact_level="medium",
                            recommended_actions=[
                                f"Schedule important activities around {best_hour}:00",
                                f"Avoid demanding tasks during {worst_hour}:00",
                                "Consider adjusting gaming schedule",
                                "Plan breaks during low-performance periods"
                            ],
                            supporting_data={
                                "best_hour": best_hour,
                                "worst_hour": worst_hour,
                                "performance_difference": improvement,
                                "hourly_averages": avg_performance_by_hour
                            },
                            confidence=0.8,
                            generated_at=datetime.utcnow(),
                            expires_at=datetime.utcnow() + timedelta(days=7)
                        ))
            
        except Exception as e:
            logger.error("Timing pattern analysis error", error=str(e))
        
        return insights
    
    def _analyze_risk_factors(self, 
                             predictions: List[PredictionResult],
                             current_state: Dict[str, Any]) -> List[AnalyticsInsight]:
        """Analyze risk factors"""
        insights = []
        
        try:
            # Check death risk predictions
            death_risk_pred = [p for p in predictions if p.prediction_type == PredictionType.DEATH_RISK]
            
            for pred in death_risk_pred:
                if pred.predicted_value > 0.3:  # High death risk
                    risk_level = "critical" if pred.predicted_value > 0.7 else "high"
                    
                    insights.append(AnalyticsInsight(
                        insight_id=f"death_risk_warning_{int(time.time())}",
                        title="Elevated Death Risk Detected",
                        description=f"Current conditions indicate {pred.predicted_value*100:.1f}% death risk.",
                        category="safety",
                        impact_level=risk_level,
                        recommended_actions=[
                            "Return to town for healing/repairs",
                            "Avoid high-level enemies",
                            "Use defensive skills/items",
                            "Consider switching to safer content"
                        ],
                        supporting_data={
                            "risk_probability": pred.predicted_value,
                            "risk_factors": pred.metadata.get("feature_importance", {}),
                            "current_health": current_state.get("character", {}).get("health", 100)
                        },
                        confidence=pred.confidence_score,
                        generated_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(minutes=30)
                    ))
            
            # Equipment durability warnings
            durability_pred = [p for p in predictions if p.prediction_type == PredictionType.EQUIPMENT_DURABILITY]
            
            for pred in durability_pred:
                if pred.predicted_value < 20:  # Low durability predicted
                    insights.append(AnalyticsInsight(
                        insight_id=f"durability_warning_{int(time.time())}",
                        title="Equipment Durability Warning",
                        description=f"Equipment durability will drop to {pred.predicted_value:.1f}% soon.",
                        category="maintenance",
                        impact_level="medium",
                        recommended_actions=[
                            "Visit repair vendor",
                            "Carry repair items",
                            "Avoid intensive activities",
                            "Switch to backup equipment"
                        ],
                        supporting_data={
                            "predicted_durability": pred.predicted_value,
                            "time_until_break": pred.valid_until.isoformat()
                        },
                        confidence=pred.confidence_score,
                        generated_at=datetime.utcnow(),
                        expires_at=pred.valid_until
                    ))
            
        except Exception as e:
            logger.error("Risk factor analysis error", error=str(e))
        
        return insights
    
    def _analyze_progression(self, 
                            predictions: List[PredictionResult],
                            historical_data: List[DataPoint]) -> List[AnalyticsInsight]:
        """Analyze skill and character progression"""
        insights = []
        
        try:
            skill_predictions = [p for p in predictions if p.prediction_type == PredictionType.SKILL_PROGRESSION]
            
            for pred in skill_predictions:
                if pred.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]:
                    # Calculate time to next milestone
                    current_progress = pred.predicted_value
                    next_milestone = math.ceil(current_progress / 10) * 10  # Next 10-point milestone
                    
                    if next_milestone > current_progress:
                        # Estimate time based on recent progression rate
                        recent_skill_data = [dp for dp in historical_data[-50:] 
                                           if dp.prediction_type == PredictionType.SKILL_PROGRESSION]
                        
                        if len(recent_skill_data) >= 5:
                            progression_rates = []
                            for i in range(1, len(recent_skill_data)):
                                if recent_skill_data[i].target_value and recent_skill_data[i-1].target_value:
                                    time_diff = (recent_skill_data[i].timestamp - recent_skill_data[i-1].timestamp).total_seconds() / 3600
                                    progress_diff = recent_skill_data[i].target_value - recent_skill_data[i-1].target_value
                                    if time_diff > 0 and progress_diff > 0:
                                        progression_rates.append(progress_diff / time_diff)
                            
                            if progression_rates:
                                avg_rate = sum(progression_rates) / len(progression_rates)
                                remaining_progress = next_milestone - current_progress
                                estimated_hours = remaining_progress / max(avg_rate, 0.001)
                                
                                if estimated_hours < 168:  # Less than a week
                                    timeframe = f"{estimated_hours:.1f} hours" if estimated_hours < 24 else f"{estimated_hours/24:.1f} days"
                                    
                                    insights.append(AnalyticsInsight(
                                        insight_id=f"skill_milestone_{int(time.time())}",
                                        title="Skill Milestone Approaching",
                                        description=f"You're approaching skill level {next_milestone}, estimated in {timeframe}.",
                                        category="progression",
                                        impact_level="low",
                                        recommended_actions=[
                                            "Continue current training approach",
                                            "Consider skill-specific optimizations",
                                            "Plan for next training phase",
                                            "Check for skill synergies"
                                        ],
                                        supporting_data={
                                            "current_level": current_progress,
                                            "next_milestone": next_milestone,
                                            "estimated_time_hours": estimated_hours,
                                            "progression_rate": avg_rate
                                        },
                                        confidence=pred.confidence_score,
                                        generated_at=datetime.utcnow(),
                                        expires_at=datetime.utcnow() + timedelta(days=1)
                                    ))
            
        except Exception as e:
            logger.error("Progression analysis error", error=str(e))
        
        return insights

class PredictiveAnalyticsManager:
    """Main predictive analytics manager"""
    
    def __init__(self,
                 data_retention_days: int = 30,
                 model_retrain_hours: int = 24,
                 prediction_cache_minutes: int = 15):
        
        self.data_retention_days = data_retention_days
        self.model_retrain_hours = model_retrain_hours
        self.prediction_cache_minutes = prediction_cache_minutes
        
        # Data storage
        self.data_points: deque = deque(maxlen=100000)
        self.predictions_cache: Dict[str, PredictionResult] = {}
        
        # Model management
        self.models: Dict[Tuple[PredictionType, AnalyticsModel], PredictiveModel] = {}
        self.feature_engineer = FeatureEngineering()
        self.insight_generator = InsightGenerator()
        
        # Background processing
        self.analytics_active = False
        self.analytics_thread: Optional[threading.Thread] = None
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Callbacks
        self.prediction_callbacks: List[Callable[[PredictionResult], None]] = []
        self.insight_callbacks: List[Callable[[AnalyticsInsight], None]] = []
        
        # Performance tracking
        self.analytics_stats = {
            "total_predictions": 0,
            "successful_predictions": 0,
            "models_trained": 0,
            "insights_generated": 0,
            "last_analysis_time": None
        }
        
        # Feature definitions
        self.feature_definitions = {
            PredictionType.EXPERIENCE_GAIN: [
                "character_level", "hour_of_day", "day_of_week", "in_combat",
                "zone_danger_level", "player_density", "session_duration",
                "lag_1", "lag_2", "trend", "mean"
            ],
            PredictionType.RESOURCE_CONSUMPTION: [
                "character_level", "activity_intensity", "equipment_durability",
                "zone_danger_level", "combat_duration", "lag_1", "mean", "std"
            ],
            PredictionType.QUEST_COMPLETION_TIME: [
                "character_level", "quest_difficulty", "distance_to_town",
                "player_density", "equipment_value", "hour_of_day", "trend"
            ],
            PredictionType.COMBAT_OUTCOME: [
                "character_level", "health_percentage", "enemy_count",
                "weapon_damage", "armor_rating", "combat_duration", "zone_danger_level"
            ],
            PredictionType.EQUIPMENT_DURABILITY: [
                "avg_durability", "combat_duration", "activity_intensity",
                "zone_danger_level", "lag_1", "lag_2", "trend"
            ]
        }
        
        # Initialize models
        self._initialize_models()
        
        # Observability
        self.observability_manager = get_observability_manager()
    
    def _initialize_models(self):
        """Initialize predictive models"""
        try:
            model_configs = [
                (PredictionType.EXPERIENCE_GAIN, AnalyticsModel.RANDOM_FOREST),
                (PredictionType.EXPERIENCE_GAIN, AnalyticsModel.GRADIENT_BOOSTING),
                (PredictionType.RESOURCE_CONSUMPTION, AnalyticsModel.LINEAR_REGRESSION),
                (PredictionType.QUEST_COMPLETION_TIME, AnalyticsModel.RANDOM_FOREST),
                (PredictionType.COMBAT_OUTCOME, AnalyticsModel.LOGISTIC_REGRESSION),
                (PredictionType.EQUIPMENT_DURABILITY, AnalyticsModel.LINEAR_REGRESSION)
            ]
            
            for pred_type, model_type in model_configs:
                features = self.feature_definitions.get(pred_type, [])
                if features:
                    model = PredictiveModel(model_type, pred_type, features)
                    self.models[(pred_type, model_type)] = model
            
            logger.info("Initialized predictive models", count=len(self.models))
            
        except Exception as e:
            logger.error("Model initialization error", error=str(e))
    
    @trace_gaming_operation("record_data_point")
    def record_data_point(self, data_point: DataPoint):
        """Record a new data point for analytics"""
        try:
            # Add temporal features
            temporal_features = self.feature_engineer.extract_temporal_features(data_point.timestamp)
            data_point.features.update(temporal_features)
            
            # Add to storage
            self.data_points.append(data_point)
            
            # Trigger model retraining if enough new data
            if len(self.data_points) % 100 == 0:
                asyncio.create_task(self._trigger_model_training())
            
        except Exception as e:
            logger.error("Failed to record data point", error=str(e))
    
    @trace_gaming_operation("predictive_analysis")
    async def generate_predictions(self, 
                                  current_state: Dict[str, Any],
                                  prediction_types: Optional[List[PredictionType]] = None) -> List[PredictionResult]:
        """Generate predictions for specified types"""
        
        if prediction_types is None:
            prediction_types = list(PredictionType)
        
        predictions = []
        
        try:
            # Extract current features
            current_features = {}
            
            # Temporal features
            current_features.update(self.feature_engineer.extract_temporal_features(datetime.utcnow()))
            
            # Gaming features
            current_features.update(self.feature_engineer.extract_gaming_features(current_state))
            
            # Historical features
            for pred_type in prediction_types:
                type_data = [dp for dp in list(self.data_points)[-100:] 
                           if dp.prediction_type == pred_type and dp.target_value is not None]
                
                if len(type_data) >= 5:
                    # Lag features
                    values = [dp.target_value for dp in type_data]
                    current_features.update(self.feature_engineer.create_lag_features(values, [1, 2, 5]))
                    
                    # Statistical features
                    current_features.update(self.feature_engineer.create_statistical_features(values))
            
            # Generate predictions for each type
            prediction_tasks = []
            
            for pred_type in prediction_types:
                # Check cache first
                cache_key = f"{pred_type.value}_{hash(str(sorted(current_features.items())))}"
                
                if cache_key in self.predictions_cache:
                    cached_pred = self.predictions_cache[cache_key]
                    if cached_pred.valid_until > datetime.utcnow():
                        predictions.append(cached_pred)
                        continue
                
                # Find best model for this prediction type
                available_models = [(pt, mt, model) for (pt, mt), model in self.models.items() 
                                  if pt == pred_type and model.is_trained]
                
                if available_models:
                    # Use the best performing model
                    best_model = max(available_models, 
                                   key=lambda x: x[2].performance.r2_score if x[2].performance else 0.0)[2]
                    
                    # Generate prediction
                    task = asyncio.get_event_loop().run_in_executor(
                        self.thread_pool,
                        self._generate_single_prediction,
                        best_model,
                        current_features,
                        cache_key
                    )
                    prediction_tasks.append(task)
            
            # Wait for all predictions
            for task in prediction_tasks:
                try:
                    prediction = await task
                    if prediction:
                        predictions.append(prediction)
                        self.analytics_stats["total_predictions"] += 1
                        
                        if prediction.confidence_score > 0.6:
                            self.analytics_stats["successful_predictions"] += 1
                        
                        # Notify callbacks
                        for callback in self.prediction_callbacks:
                            try:
                                callback(prediction)
                            except Exception as e:
                                logger.error("Prediction callback error", error=str(e))
                        
                except Exception as e:
                    logger.error("Prediction task error", error=str(e))
            
            return predictions
            
        except Exception as e:
            logger.error("Prediction generation error", error=str(e))
            return []
    
    def _generate_single_prediction(self, 
                                   model: PredictiveModel,
                                   features: Dict[str, float],
                                   cache_key: str) -> Optional[PredictionResult]:
        """Generate single prediction using model"""
        try:
            prediction = model.predict(features)
            
            if prediction:
                # Cache the prediction
                self.predictions_cache[cache_key] = prediction
                return prediction
                
        except Exception as e:
            logger.error("Single prediction error", error=str(e))
        
        return None
    
    @trace_gaming_operation("insight_generation")
    async def generate_insights(self, current_state: Dict[str, Any]) -> List[AnalyticsInsight]:
        """Generate actionable insights from current data"""
        
        try:
            # Get recent predictions
            recent_predictions = await self.generate_predictions(current_state)
            
            # Get historical data
            historical_data = list(self.data_points)[-1000:]
            
            # Generate insights
            insights = self.insight_generator.generate_insights(
                recent_predictions, historical_data, current_state
            )
            
            self.analytics_stats["insights_generated"] += len(insights)
            
            # Notify callbacks
            for insight in insights:
                for callback in self.insight_callbacks:
                    try:
                        callback(insight)
                    except Exception as e:
                        logger.error("Insight callback error", error=str(e))
            
            logger.info("Generated analytics insights", count=len(insights))
            
            return insights
            
        except Exception as e:
            logger.error("Insight generation error", error=str(e))
            return []
    
    async def _trigger_model_training(self):
        """Trigger background model training"""
        try:
            if not self.analytics_active:
                await self.retrain_models()
        except Exception as e:
            logger.error("Background model training error", error=str(e))
    
    @trace_gaming_operation("model_retraining")
    async def retrain_models(self) -> Dict[str, bool]:
        """Retrain all models with latest data"""
        
        training_results = {}
        
        try:
            # Group data by prediction type
            data_by_type = defaultdict(list)
            for dp in self.data_points:
                data_by_type[dp.prediction_type].append(dp)
            
            # Retrain models
            training_tasks = []
            
            for (pred_type, model_type), model in self.models.items():
                if pred_type in data_by_type and len(data_by_type[pred_type]) >= 20:
                    task = asyncio.get_event_loop().run_in_executor(
                        self.thread_pool,
                        self._train_single_model,
                        model,
                        data_by_type[pred_type]
                    )
                    training_tasks.append((pred_type, model_type, task))
            
            # Wait for training completion
            for pred_type, model_type, task in training_tasks:
                try:
                    success = await task
                    key = f"{pred_type.value}_{model_type.value}"
                    training_results[key] = success
                    
                    if success:
                        self.analytics_stats["models_trained"] += 1
                        
                except Exception as e:
                    logger.error("Model training task error", 
                                pred_type=pred_type.value, 
                                model_type=model_type.value,
                                error=str(e))
                    training_results[f"{pred_type.value}_{model_type.value}"] = False
            
            logger.info("Model retraining completed", results=training_results)
            
            return training_results
            
        except Exception as e:
            logger.error("Model retraining error", error=str(e))
            return training_results
    
    def _train_single_model(self, model: PredictiveModel, data_points: List[DataPoint]) -> bool:
        """Train single model"""
        try:
            return model.train(data_points)
        except Exception as e:
            logger.error("Single model training error", error=str(e))
            return False
    
    def start_continuous_analytics(self):
        """Start continuous background analytics"""
        if self.analytics_active:
            logger.warning("Analytics already active")
            return
        
        self.analytics_active = True
        self.analytics_thread = threading.Thread(
            target=self._analytics_loop,
            daemon=True
        )
        self.analytics_thread.start()
        
        logger.info("Started continuous predictive analytics")
    
    def stop_continuous_analytics(self):
        """Stop continuous background analytics"""
        if not self.analytics_active:
            return
        
        self.analytics_active = False
        if self.analytics_thread:
            self.analytics_thread.join(timeout=2.0)
        
        logger.info("Stopped continuous predictive analytics")
    
    def _analytics_loop(self):
        """Background analytics loop"""
        while self.analytics_active:
            try:
                # Run model retraining
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                results = loop.run_until_complete(self.retrain_models())
                
                logger.debug("Background model retraining completed", results=results)
                
                loop.close()
                
                # Sleep until next cycle
                time.sleep(self.model_retrain_hours * 3600)
                
            except Exception as e:
                logger.error("Analytics loop error", error=str(e))
                time.sleep(3600)  # Wait 1 hour before retry
    
    def add_prediction_callback(self, callback: Callable[[PredictionResult], None]):
        """Add callback for new predictions"""
        self.prediction_callbacks.append(callback)
    
    def add_insight_callback(self, callback: Callable[[AnalyticsInsight], None]):
        """Add callback for new insights"""
        self.insight_callbacks.append(callback)
    
    def get_model_performance(self) -> Dict[str, ModelPerformance]:
        """Get performance metrics for all models"""
        performance = {}
        
        for (pred_type, model_type), model in self.models.items():
            if model.performance:
                key = f"{pred_type.value}_{model_type.value}"
                performance[key] = model.performance
        
        return performance
    
    def get_analytics_stats(self) -> Dict[str, Any]:
        """Get analytics performance statistics"""
        stats = self.analytics_stats.copy()
        stats["total_data_points"] = len(self.data_points)
        stats["active_models"] = sum(1 for model in self.models.values() if model.is_trained)
        stats["cached_predictions"] = len(self.predictions_cache)
        
        return stats
    
    def export_analytics_data(self, filepath: str):
        """Export analytics data for analysis"""
        try:
            data = {
                "data_points": [asdict(dp) for dp in list(self.data_points)[-5000:]],  # Last 5000 points
                "model_performance": {
                    f"{pt.value}_{mt.value}": asdict(model.performance) if model.performance else None
                    for (pt, mt), model in self.models.items()
                },
                "analytics_stats": self.analytics_stats,
                "insights": [asdict(insight) for insight in self.insight_generator.generated_insights.values()],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info("Exported analytics data", filepath=filepath)
            
        except Exception as e:
            logger.error("Failed to export analytics data", error=str(e))
    
    async def shutdown(self):
        """Shutdown predictive analytics manager"""
        try:
            # Stop continuous analytics
            self.stop_continuous_analytics()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            logger.info("Predictive analytics manager shutdown completed")
            
        except Exception as e:
            logger.error("Failed to shutdown predictive analytics manager", error=str(e))

# Global predictive analytics manager instance
_global_analytics_manager: Optional[PredictiveAnalyticsManager] = None

def initialize_predictive_analytics(**kwargs) -> PredictiveAnalyticsManager:
    """Initialize global predictive analytics manager"""
    global _global_analytics_manager
    
    _global_analytics_manager = PredictiveAnalyticsManager(**kwargs)
    return _global_analytics_manager

def get_predictive_analytics_manager() -> Optional[PredictiveAnalyticsManager]:
    """Get global predictive analytics manager instance"""
    return _global_analytics_manager
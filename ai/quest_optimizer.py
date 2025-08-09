"""
MS11 AI-Powered Quest Optimization System
Machine learning models for optimal quest routing and strategy optimization
"""

import asyncio
import numpy as np
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import pickle
import hashlib
from collections import defaultdict, deque
import threading
import math

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    import pandas as pd
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

from core.structured_logging import StructuredLogger
from core.observability_integration import get_observability_manager, trace_gaming_operation
from core.caching_strategy import get_cache_manager

# Initialize logger
logger = StructuredLogger("quest_optimizer")

class OptimizationObjective(Enum):
    """Optimization objectives for quest planning"""
    EXPERIENCE_PER_HOUR = "experience_per_hour"
    CREDITS_PER_HOUR = "credits_per_hour"
    SKILL_POINTS_PER_HOUR = "skill_points_per_hour"
    COMPLETION_TIME = "completion_time"
    RESOURCE_EFFICIENCY = "resource_efficiency"
    RISK_MINIMIZATION = "risk_minimization"

class QuestDifficulty(Enum):
    """Quest difficulty levels"""
    TRIVIAL = "trivial"
    EASY = "easy"
    MODERATE = "moderate"
    CHALLENGING = "challenging"
    HEROIC = "heroic"

class CharacterRole(Enum):
    """Character role classifications"""
    COMBAT = "combat"
    CRAFTER = "crafter"
    TRADER = "trader"
    ENTERTAINER = "entertainer"
    HYBRID = "hybrid"

@dataclass
class QuestNode:
    """Individual quest with performance data"""
    quest_id: str
    name: str
    location: Tuple[float, float]  # x, y coordinates
    planet: str
    level_requirement: int
    skill_requirements: List[str]
    estimated_duration_minutes: float
    experience_reward: int
    credit_reward: int
    difficulty: QuestDifficulty
    prerequisites: List[str] = field(default_factory=list)
    follows_up: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Performance metrics (learned from data)
    success_rate: float = 1.0
    average_completion_time: float = 0.0
    resource_cost: float = 0.0
    risk_factor: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CharacterProfile:
    """Character profile for optimization"""
    character_id: str
    name: str
    level: int
    skills: Dict[str, int]  # skill_name -> skill_level
    location: Tuple[float, float]
    planet: str
    role: CharacterRole
    play_style: str  # aggressive, conservative, efficient
    available_time_minutes: int
    objectives: List[OptimizationObjective]
    
    # Learned preferences
    preferred_quest_types: List[str] = field(default_factory=list)
    avoided_quest_types: List[str] = field(default_factory=list)
    performance_history: Dict[str, float] = field(default_factory=dict)

@dataclass
class QuestRoute:
    """Optimized quest route"""
    route_id: str
    character_id: str
    quests: List[QuestNode]
    total_estimated_time: float
    total_experience: int
    total_credits: int
    efficiency_score: float
    risk_score: float
    travel_time: float
    created_at: datetime
    
    # Route metrics
    experience_per_hour: float = 0.0
    credits_per_hour: float = 0.0
    completion_probability: float = 1.0
    
    def __post_init__(self):
        if self.total_estimated_time > 0:
            self.experience_per_hour = (self.total_experience / self.total_estimated_time) * 60
            self.credits_per_hour = (self.total_credits / self.total_estimated_time) * 60

@dataclass
class QuestPerformanceData:
    """Historical quest performance data"""
    quest_id: str
    character_id: str
    completion_time: float
    success: bool
    experience_gained: int
    credits_gained: int
    resources_used: Dict[str, int]
    timestamp: datetime
    character_level_at_time: int
    server_population: int = 100  # Estimated server activity
    time_of_day: int = 12  # Hour of day (0-23)

class QuestGraph:
    """Quest dependency graph for pathfinding"""
    
    def __init__(self):
        self.graph = nx.DiGraph() if NETWORKX_AVAILABLE else None
        self.quest_nodes: Dict[str, QuestNode] = {}
        self.location_clusters: Dict[str, List[QuestNode]] = defaultdict(list)
        
    def add_quest(self, quest: QuestNode):
        """Add quest to graph"""
        self.quest_nodes[quest.quest_id] = quest
        
        if NETWORKX_AVAILABLE and self.graph:
            self.graph.add_node(quest.quest_id, **quest.to_dict())
            
            # Add prerequisite edges
            for prereq in quest.prerequisites:
                if prereq in self.quest_nodes:
                    self.graph.add_edge(prereq, quest.quest_id)
            
            # Add follow-up edges
            for followup in quest.follows_up:
                if followup in self.quest_nodes:
                    self.graph.add_edge(quest.quest_id, followup)
        
        # Group by location clusters
        location_key = f"{quest.planet}_{int(quest.location[0]/1000)}_{int(quest.location[1]/1000)}"
        self.location_clusters[location_key].append(quest)
    
    def get_available_quests(self, character: CharacterProfile, 
                           completed_quests: Set[str]) -> List[QuestNode]:
        """Get quests available for character"""
        available = []
        
        for quest in self.quest_nodes.values():
            # Skip completed quests
            if quest.quest_id in completed_quests:
                continue
            
            # Check level requirement
            if quest.level_requirement > character.level:
                continue
            
            # Check skill requirements
            skill_requirements_met = True
            for skill_req in quest.skill_requirements:
                if skill_req not in character.skills or character.skills[skill_req] == 0:
                    skill_requirements_met = False
                    break
            
            if not skill_requirements_met:
                continue
            
            # Check prerequisites
            prerequisites_met = all(prereq in completed_quests for prereq in quest.prerequisites)
            if not prerequisites_met:
                continue
            
            available.append(quest)
        
        return available
    
    def find_quest_chains(self, start_quest: str, max_length: int = 10) -> List[List[str]]:
        """Find quest chains starting from a quest"""
        if not NETWORKX_AVAILABLE or not self.graph:
            return []
        
        chains = []
        
        def dfs_chains(current_quest: str, current_chain: List[str], visited: Set[str]):
            if len(current_chain) >= max_length:
                return
            
            # Add current chain
            if len(current_chain) > 1:
                chains.append(current_chain.copy())
            
            # Explore successors
            for successor in self.graph.successors(current_quest):
                if successor not in visited:
                    visited.add(successor)
                    current_chain.append(successor)
                    dfs_chains(successor, current_chain, visited)
                    current_chain.pop()
                    visited.remove(successor)
        
        if start_quest in self.quest_nodes:
            dfs_chains(start_quest, [start_quest], {start_quest})
        
        return chains

class QuestPerformancePredictor:
    """ML model for predicting quest performance"""
    
    def __init__(self):
        self.completion_time_model = None
        self.success_rate_model = None
        self.experience_model = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.label_encoders = {}
        
        self.is_trained = False
        self.training_data = []
        
    def add_performance_data(self, data: QuestPerformanceData):
        """Add historical performance data"""
        self.training_data.append(data)
        
        # Retrain periodically
        if len(self.training_data) % 100 == 0:
            asyncio.create_task(self.retrain_models())
    
    def prepare_features(self, quest: QuestNode, character: CharacterProfile, 
                        context: Dict[str, Any] = None) -> np.ndarray:
        """Prepare features for ML model"""
        if not SKLEARN_AVAILABLE:
            return np.array([])
        
        context = context or {}
        
        features = [
            # Quest features
            quest.level_requirement,
            quest.estimated_duration_minutes,
            quest.experience_reward,
            quest.credit_reward,
            len(quest.skill_requirements),
            len(quest.prerequisites),
            quest.difficulty.value.__hash__() % 1000,  # Simple encoding
            
            # Character features
            character.level,
            len(character.skills),
            character.available_time_minutes,
            
            # Character-quest compatibility
            character.level - quest.level_requirement,  # Level advantage
            sum(character.skills.get(skill, 0) for skill in quest.skill_requirements),
            
            # Location features
            quest.location[0], quest.location[1],
            abs(quest.location[0] - character.location[0]),  # Distance
            abs(quest.location[1] - character.location[1]),
            
            # Context features
            context.get('server_population', 100),
            context.get('time_of_day', 12),
            context.get('character_fatigue', 0),
        ]
        
        return np.array(features).reshape(1, -1)
    
    async def retrain_models(self):
        """Retrain ML models with new data"""
        if not SKLEARN_AVAILABLE or len(self.training_data) < 50:
            return
        
        try:
            # Prepare training data
            features_list = []
            completion_times = []
            success_rates = []
            experience_values = []
            
            for data in self.training_data:
                # This is simplified - in reality you'd need to store quest and character data
                # For now, we'll create dummy features based on available data
                features = [
                    data.character_level_at_time,
                    data.completion_time,
                    data.experience_gained,
                    data.credits_gained,
                    data.server_population,
                    data.time_of_day,
                    1.0 if data.success else 0.0,
                ]
                
                features_list.append(features)
                completion_times.append(data.completion_time)
                success_rates.append(1.0 if data.success else 0.0)
                experience_values.append(data.experience_gained)
            
            X = np.array(features_list)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test = train_test_split(X_scaled, test_size=0.2, random_state=42)
            
            # Train completion time model
            y_time_train, y_time_test = train_test_split(completion_times, test_size=0.2, random_state=42)
            self.completion_time_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.completion_time_model.fit(X_train, y_time_train)
            
            # Train success rate model
            y_success_train, y_success_test = train_test_split(success_rates, test_size=0.2, random_state=42)
            self.success_rate_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.success_rate_model.fit(X_train, y_success_train)
            
            # Train experience model
            y_exp_train, y_exp_test = train_test_split(experience_values, test_size=0.2, random_state=42)
            self.experience_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
            self.experience_model.fit(X_train, y_exp_train)
            
            self.is_trained = True
            
            # Log model performance
            if len(y_time_test) > 0:
                time_score = self.completion_time_model.score(X_test, y_time_test)
                success_score = self.success_rate_model.score(X_test, y_success_test)
                exp_score = self.experience_model.score(X_test, y_exp_test)
                
                logger.info("Quest performance models retrained",
                           time_model_score=time_score,
                           success_model_score=success_score,
                           experience_model_score=exp_score,
                           training_samples=len(self.training_data))
            
        except Exception as e:
            logger.error("Failed to retrain quest performance models", error=str(e))
    
    def predict_quest_performance(self, quest: QuestNode, character: CharacterProfile,
                                context: Dict[str, Any] = None) -> Dict[str, float]:
        """Predict quest performance metrics"""
        if not self.is_trained or not SKLEARN_AVAILABLE:
            # Return default predictions
            return {
                "completion_time": quest.estimated_duration_minutes,
                "success_rate": 0.8,
                "experience_gain": quest.experience_reward,
                "efficiency_score": 0.5
            }
        
        try:
            features = self.prepare_features(quest, character, context)
            features_scaled = self.scaler.transform(features)
            
            predictions = {}
            
            if self.completion_time_model:
                predictions["completion_time"] = self.completion_time_model.predict(features_scaled)[0]
            
            if self.success_rate_model:
                predictions["success_rate"] = max(0.0, min(1.0, self.success_rate_model.predict(features_scaled)[0]))
            
            if self.experience_model:
                predictions["experience_gain"] = max(0, self.experience_model.predict(features_scaled)[0])
            
            # Calculate efficiency score
            predicted_time = predictions.get("completion_time", quest.estimated_duration_minutes)
            predicted_exp = predictions.get("experience_gain", quest.experience_reward)
            predictions["efficiency_score"] = predicted_exp / max(predicted_time, 1.0)
            
            return predictions
            
        except Exception as e:
            logger.error("Failed to predict quest performance", error=str(e))
            return {
                "completion_time": quest.estimated_duration_minutes,
                "success_rate": 0.8,
                "experience_gain": quest.experience_reward,
                "efficiency_score": 0.5
            }

class QuestRouteOptimizer:
    """Advanced quest route optimization using AI"""
    
    def __init__(self, quest_graph: QuestGraph, performance_predictor: QuestPerformancePredictor):
        self.quest_graph = quest_graph
        self.performance_predictor = performance_predictor
        
        # Optimization parameters
        self.max_route_time = 240  # 4 hours default
        self.max_travel_percentage = 0.3  # 30% travel time max
        self.population_size = 50  # Genetic algorithm population
        self.generations = 100
        
        # Caching
        self.route_cache = {}
        self.cache_manager = get_cache_manager()
        
        # Observability
        self.observability_manager = get_observability_manager()
    
    @trace_gaming_operation("optimize_quest_route")
    async def optimize_route(self, character: CharacterProfile,
                           completed_quests: Set[str],
                           objectives: List[OptimizationObjective],
                           context: Dict[str, Any] = None) -> QuestRoute:
        """Optimize quest route for character"""
        
        # Check cache first
        cache_key = self._generate_cache_key(character, completed_quests, objectives)
        if self.cache_manager:
            cached_route = await self.cache_manager.get(cache_key)
            if cached_route:
                logger.info("Returning cached quest route", character=character.name)
                return cached_route
        
        # Get available quests
        available_quests = self.quest_graph.get_available_quests(character, completed_quests)
        
        if not available_quests:
            logger.warning("No available quests found", character=character.name)
            return self._create_empty_route(character)
        
        # Generate route candidates using multiple strategies
        routes = []
        
        # Strategy 1: Greedy optimization
        greedy_route = await self._greedy_optimization(character, available_quests, objectives, context)
        if greedy_route:
            routes.append(greedy_route)
        
        # Strategy 2: Location-based clustering
        cluster_route = await self._cluster_based_optimization(character, available_quests, objectives, context)
        if cluster_route:
            routes.append(cluster_route)
        
        # Strategy 3: Chain-based optimization
        chain_route = await self._chain_based_optimization(character, available_quests, objectives, context)
        if chain_route:
            routes.append(chain_route)
        
        # Strategy 4: Genetic algorithm (if we have enough quests)
        if len(available_quests) > 10:
            ga_route = await self._genetic_algorithm_optimization(character, available_quests, objectives, context)
            if ga_route:
                routes.append(ga_route)
        
        # Select best route
        if not routes:
            return self._create_empty_route(character)
        
        best_route = max(routes, key=lambda r: self._calculate_route_score(r, objectives))
        
        # Cache the result
        if self.cache_manager:
            await self.cache_manager.set(cache_key, best_route, ttl=1800)  # 30 minutes
        
        logger.info("Quest route optimized",
                   character=character.name,
                   quest_count=len(best_route.quests),
                   total_time=best_route.total_estimated_time,
                   efficiency_score=best_route.efficiency_score)
        
        return best_route
    
    async def _greedy_optimization(self, character: CharacterProfile, 
                                 available_quests: List[QuestNode],
                                 objectives: List[OptimizationObjective],
                                 context: Dict[str, Any]) -> Optional[QuestRoute]:
        """Greedy optimization: select best quest at each step"""
        try:
            selected_quests = []
            remaining_time = character.available_time_minutes
            current_location = character.location
            
            remaining_quests = available_quests.copy()
            
            while remaining_quests and remaining_time > 0:
                best_quest = None
                best_score = -1
                
                for quest in remaining_quests:
                    # Predict performance
                    predictions = self.performance_predictor.predict_quest_performance(quest, character, context)
                    
                    # Calculate travel time
                    travel_time = self._calculate_travel_time(current_location, quest.location)
                    total_time = predictions["completion_time"] + travel_time
                    
                    if total_time > remaining_time:
                        continue
                    
                    # Calculate score based on objectives
                    score = self._calculate_quest_score(quest, predictions, objectives, travel_time)
                    
                    if score > best_score:
                        best_score = score
                        best_quest = quest
                
                if best_quest:
                    selected_quests.append(best_quest)
                    remaining_quests.remove(best_quest)
                    
                    # Update time and location
                    predictions = self.performance_predictor.predict_quest_performance(best_quest, character, context)
                    travel_time = self._calculate_travel_time(current_location, best_quest.location)
                    remaining_time -= (predictions["completion_time"] + travel_time)
                    current_location = best_quest.location
                else:
                    break
            
            if selected_quests:
                return self._create_route(character, selected_quests, "greedy")
            
        except Exception as e:
            logger.error("Greedy optimization failed", error=str(e))
        
        return None
    
    async def _cluster_based_optimization(self, character: CharacterProfile,
                                        available_quests: List[QuestNode],
                                        objectives: List[OptimizationObjective],
                                        context: Dict[str, Any]) -> Optional[QuestRoute]:
        """Location-based clustering optimization"""
        try:
            if not SKLEARN_AVAILABLE or len(available_quests) < 3:
                return None
            
            # Extract quest locations
            locations = np.array([quest.location for quest in available_quests])
            
            # Determine number of clusters
            n_clusters = min(5, len(available_quests) // 3)
            
            # Cluster quests by location
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(locations)
            
            # Group quests by cluster
            clusters = defaultdict(list)
            for i, quest in enumerate(available_quests):
                clusters[cluster_labels[i]].append(quest)
            
            # Find best cluster to start with (closest to character)
            best_cluster_order = []
            current_location = character.location
            remaining_clusters = set(clusters.keys())
            
            while remaining_clusters:
                closest_cluster = min(remaining_clusters, 
                                    key=lambda c: min(self._calculate_travel_time(current_location, quest.location) 
                                                    for quest in clusters[c]))
                best_cluster_order.append(closest_cluster)
                remaining_clusters.remove(closest_cluster)
                
                # Update location to center of selected cluster
                cluster_center = kmeans.cluster_centers_[closest_cluster]
                current_location = tuple(cluster_center)
            
            # Build route by processing clusters in order
            selected_quests = []
            remaining_time = character.available_time_minutes
            current_location = character.location
            
            for cluster_id in best_cluster_order:
                cluster_quests = clusters[cluster_id]
                
                # Optimize within cluster using greedy approach
                cluster_quests.sort(key=lambda q: self._calculate_travel_time(current_location, q.location))
                
                for quest in cluster_quests:
                    predictions = self.performance_predictor.predict_quest_performance(quest, character, context)
                    travel_time = self._calculate_travel_time(current_location, quest.location)
                    total_time = predictions["completion_time"] + travel_time
                    
                    if total_time <= remaining_time:
                        selected_quests.append(quest)
                        remaining_time -= total_time
                        current_location = quest.location
                    
                    if remaining_time <= 0:
                        break
                
                if remaining_time <= 0:
                    break
            
            if selected_quests:
                return self._create_route(character, selected_quests, "cluster")
                
        except Exception as e:
            logger.error("Cluster-based optimization failed", error=str(e))
        
        return None
    
    async def _chain_based_optimization(self, character: CharacterProfile,
                                      available_quests: List[QuestNode],
                                      objectives: List[OptimizationObjective],
                                      context: Dict[str, Any]) -> Optional[QuestRoute]:
        """Quest chain-based optimization"""
        try:
            # Find all quest chains starting from available quests
            all_chains = []
            for quest in available_quests:
                chains = self.quest_graph.find_quest_chains(quest.quest_id, max_length=8)
                all_chains.extend(chains)
            
            if not all_chains:
                return None
            
            # Evaluate each chain
            best_chain = None
            best_score = -1
            
            for chain_ids in all_chains:
                # Convert IDs to quest objects
                chain_quests = []
                for quest_id in chain_ids:
                    quest = self.quest_graph.quest_nodes.get(quest_id)
                    if quest and quest in available_quests:
                        chain_quests.append(quest)
                
                if not chain_quests:
                    continue
                
                # Check if chain fits within time constraint
                total_time = 0
                current_location = character.location
                
                valid_chain = True
                for quest in chain_quests:
                    predictions = self.performance_predictor.predict_quest_performance(quest, character, context)
                    travel_time = self._calculate_travel_time(current_location, quest.location)
                    total_time += predictions["completion_time"] + travel_time
                    current_location = quest.location
                    
                    if total_time > character.available_time_minutes:
                        valid_chain = False
                        break
                
                if not valid_chain:
                    continue
                
                # Calculate chain score
                route = self._create_route(character, chain_quests, "chain")
                score = self._calculate_route_score(route, objectives)
                
                if score > best_score:
                    best_score = score
                    best_chain = route
            
            return best_chain
            
        except Exception as e:
            logger.error("Chain-based optimization failed", error=str(e))
        
        return None
    
    async def _genetic_algorithm_optimization(self, character: CharacterProfile,
                                           available_quests: List[QuestNode],
                                           objectives: List[OptimizationObjective],
                                           context: Dict[str, Any]) -> Optional[QuestRoute]:
        """Genetic algorithm for complex route optimization"""
        try:
            if len(available_quests) < 10:
                return None
            
            # Initialize population
            population = []
            for _ in range(self.population_size):
                # Create random individual
                num_quests = min(np.random.randint(3, min(15, len(available_quests))), 
                               len(available_quests))
                individual = np.random.choice(available_quests, size=num_quests, replace=False)
                population.append(list(individual))
            
            # Evolution loop
            for generation in range(self.generations):
                # Evaluate fitness
                fitness_scores = []
                for individual in population:
                    route = self._create_route(character, individual, f"ga_gen_{generation}")
                    if self._is_route_valid(route, character):
                        score = self._calculate_route_score(route, objectives)
                    else:
                        score = -1  # Invalid route
                    fitness_scores.append(score)
                
                # Selection and reproduction
                new_population = []
                
                # Keep best individuals (elitism)
                elite_count = self.population_size // 10
                elite_indices = np.argsort(fitness_scores)[-elite_count:]
                for idx in elite_indices:
                    new_population.append(population[idx].copy())
                
                # Generate offspring
                while len(new_population) < self.population_size:
                    # Tournament selection
                    parent1 = self._tournament_selection(population, fitness_scores)
                    parent2 = self._tournament_selection(population, fitness_scores)
                    
                    # Crossover and mutation
                    offspring = self._crossover_and_mutate(parent1, parent2, available_quests)
                    new_population.append(offspring)
                
                population = new_population
            
            # Return best individual
            final_fitness = []
            for individual in population:
                route = self._create_route(character, individual, "ga_final")
                if self._is_route_valid(route, character):
                    score = self._calculate_route_score(route, objectives)
                else:
                    score = -1
                final_fitness.append(score)
            
            best_idx = np.argmax(final_fitness)
            if final_fitness[best_idx] > 0:
                return self._create_route(character, population[best_idx], "genetic")
            
        except Exception as e:
            logger.error("Genetic algorithm optimization failed", error=str(e))
        
        return None
    
    def _tournament_selection(self, population: List[List[QuestNode]], 
                            fitness_scores: List[float], tournament_size: int = 3) -> List[QuestNode]:
        """Tournament selection for genetic algorithm"""
        tournament_indices = np.random.choice(len(population), size=tournament_size, replace=False)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_idx].copy()
    
    def _crossover_and_mutate(self, parent1: List[QuestNode], parent2: List[QuestNode],
                            available_quests: List[QuestNode]) -> List[QuestNode]:
        """Crossover and mutation for genetic algorithm"""
        # Order crossover
        if len(parent1) > 1 and len(parent2) > 1:
            # Take random segment from parent1
            start = np.random.randint(0, len(parent1))
            end = np.random.randint(start, len(parent1))
            offspring = parent1[start:end+1]
            
            # Add remaining quests from parent2 in order
            for quest in parent2:
                if quest not in offspring and len(offspring) < 12:
                    offspring.append(quest)
        else:
            offspring = parent1.copy()
        
        # Mutation: randomly replace some quests
        mutation_rate = 0.1
        for i in range(len(offspring)):
            if np.random.random() < mutation_rate:
                new_quest = np.random.choice(available_quests)
                if new_quest not in offspring:
                    offspring[i] = new_quest
        
        return offspring
    
    def _calculate_travel_time(self, from_location: Tuple[float, float], 
                             to_location: Tuple[float, float]) -> float:
        """Calculate travel time between locations"""
        # Simple Euclidean distance with travel speed
        distance = math.sqrt((to_location[0] - from_location[0])**2 + 
                           (to_location[1] - from_location[1])**2)
        
        # Assume travel speed of 100 units per minute
        travel_speed = 100.0
        travel_time = distance / travel_speed
        
        return max(travel_time, 0.5)  # Minimum 30 seconds travel time
    
    def _calculate_quest_score(self, quest: QuestNode, predictions: Dict[str, float],
                             objectives: List[OptimizationObjective], travel_time: float) -> float:
        """Calculate quest score based on objectives"""
        score = 0.0
        total_time = predictions["completion_time"] + travel_time
        
        for objective in objectives:
            if objective == OptimizationObjective.EXPERIENCE_PER_HOUR:
                if total_time > 0:
                    score += (predictions["experience_gain"] / total_time) * 60 * 0.3
            
            elif objective == OptimizationObjective.CREDITS_PER_HOUR:
                if total_time > 0:
                    score += (quest.credit_reward / total_time) * 60 * 0.2
            
            elif objective == OptimizationObjective.COMPLETION_TIME:
                # Favor shorter quests
                score += (60 - min(predictions["completion_time"], 60)) * 0.1
            
            elif objective == OptimizationObjective.RESOURCE_EFFICIENCY:
                # Favor quests with low resource cost
                score += (1.0 - quest.resource_cost) * 0.2
            
            elif objective == OptimizationObjective.RISK_MINIMIZATION:
                score += predictions["success_rate"] * 0.3
        
        return score
    
    def _calculate_route_score(self, route: QuestRoute, objectives: List[OptimizationObjective]) -> float:
        """Calculate overall route score"""
        if not route.quests or route.total_estimated_time <= 0:
            return 0.0
        
        score = 0.0
        
        for objective in objectives:
            if objective == OptimizationObjective.EXPERIENCE_PER_HOUR:
                score += route.experience_per_hour * 0.4
            
            elif objective == OptimizationObjective.CREDITS_PER_HOUR:
                score += route.credits_per_hour * 0.001  # Scale credits appropriately
            
            elif objective == OptimizationObjective.COMPLETION_TIME:
                # Penalize longer routes
                score += max(0, 300 - route.total_estimated_time) * 0.1
            
            elif objective == OptimizationObjective.RESOURCE_EFFICIENCY:
                score += route.efficiency_score * 100
            
            elif objective == OptimizationObjective.RISK_MINIMIZATION:
                score += route.completion_probability * 50
        
        return score
    
    def _create_route(self, character: CharacterProfile, quests: List[QuestNode], 
                     method: str) -> QuestRoute:
        """Create quest route from selected quests"""
        if not quests:
            return self._create_empty_route(character)
        
        # Calculate route metrics
        total_time = 0.0
        total_experience = 0
        total_credits = 0
        travel_time = 0.0
        
        current_location = character.location
        completion_probability = 1.0
        
        for quest in quests:
            # Get predictions
            predictions = self.performance_predictor.predict_quest_performance(quest, character)
            
            # Add travel time
            quest_travel_time = self._calculate_travel_time(current_location, quest.location)
            travel_time += quest_travel_time
            total_time += quest_travel_time
            
            # Add quest time
            total_time += predictions["completion_time"]
            total_experience += predictions["experience_gain"]
            total_credits += quest.credit_reward
            
            # Update completion probability
            completion_probability *= predictions["success_rate"]
            
            current_location = quest.location
        
        # Calculate efficiency score
        efficiency_score = total_experience / max(total_time, 1.0) if total_time > 0 else 0.0
        
        # Calculate risk score (inverse of completion probability)
        risk_score = 1.0 - completion_probability
        
        route = QuestRoute(
            route_id=f"{character.character_id}_{method}_{datetime.now().isoformat()}",
            character_id=character.character_id,
            quests=quests,
            total_estimated_time=total_time,
            total_experience=total_experience,
            total_credits=total_credits,
            efficiency_score=efficiency_score,
            risk_score=risk_score,
            travel_time=travel_time,
            created_at=datetime.now(),
            completion_probability=completion_probability
        )
        
        return route
    
    def _create_empty_route(self, character: CharacterProfile) -> QuestRoute:
        """Create empty route when no quests available"""
        return QuestRoute(
            route_id=f"{character.character_id}_empty_{datetime.now().isoformat()}",
            character_id=character.character_id,
            quests=[],
            total_estimated_time=0.0,
            total_experience=0,
            total_credits=0,
            efficiency_score=0.0,
            risk_score=0.0,
            travel_time=0.0,
            created_at=datetime.now()
        )
    
    def _is_route_valid(self, route: QuestRoute, character: CharacterProfile) -> bool:
        """Check if route is valid for character"""
        if not route.quests:
            return False
        
        if route.total_estimated_time > character.available_time_minutes:
            return False
        
        # Check travel time percentage
        if route.travel_time / max(route.total_estimated_time, 1.0) > self.max_travel_percentage:
            return False
        
        return True
    
    def _generate_cache_key(self, character: CharacterProfile, completed_quests: Set[str],
                          objectives: List[OptimizationObjective]) -> str:
        """Generate cache key for route optimization"""
        key_data = {
            "character_id": character.character_id,
            "level": character.level,
            "location": character.location,
            "available_time": character.available_time_minutes,
            "completed_quests": sorted(list(completed_quests)),
            "objectives": [obj.value for obj in objectives]
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return f"quest_route_{hashlib.md5(key_string.encode()).hexdigest()}"

class AIQuestOptimizer:
    """Main AI-powered quest optimization system"""
    
    def __init__(self):
        self.quest_graph = QuestGraph()
        self.performance_predictor = QuestPerformancePredictor()
        self.route_optimizer = QuestRouteOptimizer(self.quest_graph, self.performance_predictor)
        
        # Learning components
        self.performance_history: List[QuestPerformanceData] = []
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        
        # Thread safety
        self._lock = threading.Lock()
    
    async def initialize(self, quest_data_file: Optional[str] = None):
        """Initialize quest optimizer"""
        try:
            # Load quest data if provided
            if quest_data_file:
                await self.load_quest_data(quest_data_file)
            
            # Start background learning tasks
            await self._start_background_tasks()
            
            logger.info("AI Quest Optimizer initialized")
            
        except Exception as e:
            logger.error("Failed to initialize AI Quest Optimizer", error=str(e))
            raise
    
    async def load_quest_data(self, data_file: str):
        """Load quest data from file"""
        try:
            with open(data_file, 'r') as f:
                quest_data = json.load(f)
            
            for quest_dict in quest_data.get('quests', []):
                quest = QuestNode(**quest_dict)
                self.quest_graph.add_quest(quest)
            
            logger.info("Quest data loaded", quest_count=len(self.quest_graph.quest_nodes))
            
        except Exception as e:
            logger.error("Failed to load quest data", file=data_file, error=str(e))
    
    async def _start_background_tasks(self):
        """Start background learning tasks"""
        try:
            # Model retraining task
            task = asyncio.create_task(self._model_retraining_loop())
            self.background_tasks.append(task)
            
            # Performance analysis task
            task = asyncio.create_task(self._performance_analysis_loop())
            self.background_tasks.append(task)
            
            logger.info("AI Quest Optimizer background tasks started")
            
        except Exception as e:
            logger.error("Failed to start background tasks", error=str(e))
    
    async def _model_retraining_loop(self):
        """Background model retraining loop"""
        try:
            while True:
                await asyncio.sleep(3600)  # Every hour
                
                # Retrain models with new data
                if len(self.performance_predictor.training_data) > 50:
                    await self.performance_predictor.retrain_models()
                
        except asyncio.CancelledError:
            logger.info("Model retraining loop cancelled")
        except Exception as e:
            logger.error("Model retraining loop error", error=str(e))
    
    async def _performance_analysis_loop(self):
        """Background performance analysis loop"""
        try:
            while True:
                await asyncio.sleep(1800)  # Every 30 minutes
                
                # Analyze performance trends and update quest metadata
                await self._analyze_performance_trends()
                
        except asyncio.CancelledError:
            logger.info("Performance analysis loop cancelled")
        except Exception as e:
            logger.error("Performance analysis loop error", error=str(e))
    
    async def _analyze_performance_trends(self):
        """Analyze performance trends and update quest data"""
        try:
            # Group performance data by quest
            quest_performance = defaultdict(list)
            
            for data in self.performance_predictor.training_data[-1000:]:  # Last 1000 entries
                quest_performance[data.quest_id].append(data)
            
            # Update quest metadata based on trends
            for quest_id, performances in quest_performance.items():
                if quest_id in self.quest_graph.quest_nodes and len(performances) >= 5:
                    quest = self.quest_graph.quest_nodes[quest_id]
                    
                    # Calculate updated metrics
                    success_rates = [1.0 if p.success else 0.0 for p in performances]
                    completion_times = [p.completion_time for p in performances if p.success]
                    
                    quest.success_rate = sum(success_rates) / len(success_rates)
                    if completion_times:
                        quest.average_completion_time = sum(completion_times) / len(completion_times)
            
            logger.debug("Performance trends analyzed", quests_updated=len(quest_performance))
            
        except Exception as e:
            logger.error("Failed to analyze performance trends", error=str(e))
    
    @trace_gaming_operation("optimize_quest_route")
    async def optimize_quest_route(self, character: CharacterProfile,
                                 completed_quests: Set[str],
                                 objectives: Optional[List[OptimizationObjective]] = None,
                                 context: Optional[Dict[str, Any]] = None) -> QuestRoute:
        """Optimize quest route for character"""
        
        objectives = objectives or [OptimizationObjective.EXPERIENCE_PER_HOUR]
        context = context or {}
        
        return await self.route_optimizer.optimize_route(character, completed_quests, objectives, context)
    
    def record_quest_performance(self, performance_data: QuestPerformanceData):
        """Record quest performance for learning"""
        with self._lock:
            self.performance_predictor.add_performance_data(performance_data)
            self.performance_history.append(performance_data)
            
            # Keep only recent data
            if len(self.performance_history) > 10000:
                self.performance_history = self.performance_history[-5000:]
        
        logger.debug("Quest performance recorded", 
                    quest_id=performance_data.quest_id,
                    character_id=performance_data.character_id,
                    success=performance_data.success)
    
    async def get_quest_recommendations(self, character: CharacterProfile,
                                     completed_quests: Set[str],
                                     limit: int = 10) -> List[Tuple[QuestNode, Dict[str, Any]]]:
        """Get quest recommendations with predicted performance"""
        
        available_quests = self.quest_graph.get_available_quests(character, completed_quests)
        recommendations = []
        
        for quest in available_quests[:limit * 2]:  # Get more to filter best
            predictions = self.performance_predictor.predict_quest_performance(quest, character)
            recommendations.append((quest, predictions))
        
        # Sort by efficiency score
        recommendations.sort(key=lambda x: x[1]["efficiency_score"], reverse=True)
        
        return recommendations[:limit]
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get AI learning statistics"""
        return {
            "quest_count": len(self.quest_graph.quest_nodes),
            "performance_records": len(self.performance_predictor.training_data),
            "model_trained": self.performance_predictor.is_trained,
            "recent_performance_count": len([p for p in self.performance_history 
                                           if p.timestamp > datetime.now() - timedelta(days=7)])
        }
    
    async def shutdown(self):
        """Shutdown quest optimizer"""
        try:
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            logger.info("AI Quest Optimizer shutdown completed")
            
        except Exception as e:
            logger.error("Failed to shutdown quest optimizer", error=str(e))

# Global quest optimizer instance
_global_quest_optimizer: Optional[AIQuestOptimizer] = None

def initialize_quest_optimizer(quest_data_file: Optional[str] = None) -> AIQuestOptimizer:
    """Initialize global quest optimizer"""
    global _global_quest_optimizer
    
    _global_quest_optimizer = AIQuestOptimizer()
    asyncio.create_task(_global_quest_optimizer.initialize(quest_data_file))
    
    return _global_quest_optimizer

def get_quest_optimizer() -> Optional[AIQuestOptimizer]:
    """Get global quest optimizer instance"""
    return _global_quest_optimizer
"""Hyperspace pathing simulation for advanced space navigation."""

import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from utils.logging_utils import log_event


class HyperspaceZone(Enum):
    """Hyperspace zones for navigation."""
    CORUSCANT_SECTOR = "coruscant_sector"
    CORELLIA_SECTOR = "corellia_sector"
    NABOO_SECTOR = "naboo_sector"
    TATOOINE_SECTOR = "tatooine_sector"
    HOTH_SECTOR = "hoth_sector"
    MUSTAFAR_SECTOR = "mustafar_sector"
    DEEP_SPACE = "deep_space"


class HyperspaceRouteType(Enum):
    """Types of hyperspace routes."""
    DIRECT = "direct"
    SAFE = "safe"
    FAST = "fast"
    STEALTH = "stealth"


@dataclass
class HyperspaceNode:
    """Represents a hyperspace navigation node."""
    name: str
    zone: HyperspaceZone
    coordinates: Tuple[float, float, float]
    security_level: float  # 0.0 (safe) to 1.0 (dangerous)
    traffic_density: float  # 0.0 (empty) to 1.0 (crowded)
    fuel_cost: float
    travel_time: float  # in minutes
    connections: List[str]  # connected node names


@dataclass
class HyperspaceRoute:
    """Represents a hyperspace route between nodes."""
    route_id: str
    start_node: str
    end_node: str
    route_type: HyperspaceRouteType
    distance: float
    travel_time: float  # in minutes
    fuel_cost: float
    risk_level: float  # 0.0 (safe) to 1.0 (dangerous)
    waypoints: List[str]
    restrictions: Dict[str, Any]


@dataclass
class NavigationRequest:
    """Request for hyperspace navigation."""
    start_location: str
    destination: str
    route_type: HyperspaceRouteType
    ship_class: str
    fuel_capacity: float
    max_risk_tolerance: float
    time_constraint: Optional[float] = None  # in minutes


@dataclass
class NavigationResult:
    """Result of hyperspace navigation calculation."""
    route: HyperspaceRoute
    total_distance: float
    total_time: float
    total_fuel_cost: float
    risk_assessment: Dict[str, float]
    waypoints: List[str]
    estimated_arrival: datetime
    warnings: List[str]


class HyperspacePathingSimulator:
    """Simulates hyperspace navigation and pathing."""
    
    def __init__(self, config_path: str = "config/space_config.json"):
        """Initialize the hyperspace pathing simulator.
        
        Parameters
        ----------
        config_path : str
            Path to space configuration file
        """
        self.config = self._load_config(config_path)
        self.nodes: Dict[str, HyperspaceNode] = {}
        self.routes: Dict[str, HyperspaceRoute] = {}
        self.zone_data: Dict[HyperspaceZone, Dict[str, Any]] = {}
        
        # Load hyperspace data
        self._load_hyperspace_data()
        self._build_route_network()
        
        # Navigation state
        self.current_location: Optional[str] = None
        self.active_route: Optional[NavigationResult] = None
        self.navigation_history: List[NavigationResult] = []
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load space configuration."""
        path = Path(config_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _load_hyperspace_data(self) -> None:
        """Load hyperspace navigation data."""
        # Load from data file if exists
        data_file = Path("data/space_quests/hyperspace_data.json")
        if data_file.exists():
            try:
                with data_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._parse_hyperspace_data(data)
            except Exception as e:
                log_event(f"[HYPESPACE] Error loading hyperspace data: {e}")
        
        # Initialize default nodes if no data loaded
        if not self.nodes:
            self._create_default_nodes()
    
    def _parse_hyperspace_data(self, data: Dict[str, Any]) -> None:
        """Parse hyperspace data from JSON."""
        # Parse nodes
        for node_data in data.get("nodes", []):
            node = HyperspaceNode(
                name=node_data["name"],
                zone=HyperspaceZone(node_data["zone"]),
                coordinates=tuple(node_data["coordinates"]),
                security_level=node_data["security_level"],
                traffic_density=node_data["traffic_density"],
                fuel_cost=node_data["fuel_cost"],
                travel_time=node_data["travel_time"],
                connections=node_data["connections"]
            )
            self.nodes[node.name] = node
        
        # Parse routes
        for route_data in data.get("routes", []):
            route = HyperspaceRoute(
                route_id=route_data["route_id"],
                start_node=route_data["start_node"],
                end_node=route_data["end_node"],
                route_type=HyperspaceRouteType(route_data["route_type"]),
                distance=route_data["distance"],
                travel_time=route_data["travel_time"],
                fuel_cost=route_data["fuel_cost"],
                risk_level=route_data["risk_level"],
                waypoints=route_data["waypoints"],
                restrictions=route_data.get("restrictions", {})
            )
            self.routes[route.route_id] = route
    
    def _create_default_nodes(self) -> None:
        """Create default hyperspace navigation nodes."""
        default_nodes = [
            {
                "name": "Corellia Starport",
                "zone": HyperspaceZone.CORELLIA_SECTOR,
                "coordinates": (100.0, 200.0, 50.0),
                "security_level": 0.2,
                "traffic_density": 0.8,
                "fuel_cost": 10.0,
                "travel_time": 15.0,
                "connections": ["Naboo Orbital", "Coruscant Central", "Tatooine Spaceport"]
            },
            {
                "name": "Naboo Orbital",
                "zone": HyperspaceZone.NABOO_SECTOR,
                "coordinates": (150.0, 250.0, 75.0),
                "security_level": 0.1,
                "traffic_density": 0.6,
                "fuel_cost": 8.0,
                "travel_time": 12.0,
                "connections": ["Corellia Starport", "Coruscant Central", "Deep Space Station"]
            },
            {
                "name": "Coruscant Central",
                "zone": HyperspaceZone.CORUSCANT_SECTOR,
                "coordinates": (200.0, 300.0, 100.0),
                "security_level": 0.3,
                "traffic_density": 0.9,
                "fuel_cost": 15.0,
                "travel_time": 20.0,
                "connections": ["Corellia Starport", "Naboo Orbital", "Tatooine Spaceport"]
            },
            {
                "name": "Tatooine Spaceport",
                "zone": HyperspaceZone.TATOOINE_SECTOR,
                "coordinates": (50.0, 100.0, 25.0),
                "security_level": 0.5,
                "traffic_density": 0.4,
                "fuel_cost": 5.0,
                "travel_time": 8.0,
                "connections": ["Corellia Starport", "Coruscant Central", "Hoth Station"]
            },
            {
                "name": "Hoth Station",
                "zone": HyperspaceZone.HOTH_SECTOR,
                "coordinates": (25.0, 50.0, 10.0),
                "security_level": 0.7,
                "traffic_density": 0.2,
                "fuel_cost": 3.0,
                "travel_time": 5.0,
                "connections": ["Tatooine Spaceport", "Deep Space Station"]
            },
            {
                "name": "Deep Space Station",
                "zone": HyperspaceZone.DEEP_SPACE,
                "coordinates": (300.0, 400.0, 150.0),
                "security_level": 0.8,
                "traffic_density": 0.1,
                "fuel_cost": 20.0,
                "travel_time": 30.0,
                "connections": ["Naboo Orbital", "Hoth Station", "Mustafar Outpost"]
            },
            {
                "name": "Mustafar Outpost",
                "zone": HyperspaceZone.MUSTAFAR_SECTOR,
                "coordinates": (400.0, 500.0, 200.0),
                "security_level": 0.9,
                "traffic_density": 0.05,
                "fuel_cost": 25.0,
                "travel_time": 45.0,
                "connections": ["Deep Space Station"]
            }
        ]
        
        for node_data in default_nodes:
            node = HyperspaceNode(**node_data)
            self.nodes[node.name] = node
    
    def _build_route_network(self) -> None:
        """Build the route network between nodes."""
        route_id = 0
        
        for node_name, node in self.nodes.items():
            for connected_node in node.connections:
                if connected_node in self.nodes:
                    # Calculate route properties
                    distance = self._calculate_distance(node, self.nodes[connected_node])
                    travel_time = self._calculate_travel_time(distance, node, self.nodes[connected_node])
                    fuel_cost = self._calculate_fuel_cost(distance, node, self.nodes[connected_node])
                    risk_level = self._calculate_risk_level(node, self.nodes[connected_node])
                    
                    # Create route
                    route = HyperspaceRoute(
                        route_id=f"route_{route_id}",
                        start_node=node_name,
                        end_node=connected_node,
                        route_type=self._determine_route_type(node, self.nodes[connected_node]),
                        distance=distance,
                        travel_time=travel_time,
                        fuel_cost=fuel_cost,
                        risk_level=risk_level,
                        waypoints=[node_name, connected_node],
                        restrictions={}
                    )
                    
                    self.routes[route.route_id] = route
                    route_id += 1
    
    def _calculate_distance(self, node1: HyperspaceNode, node2: HyperspaceNode) -> float:
        """Calculate distance between two nodes."""
        x1, y1, z1 = node1.coordinates
        x2, y2, z2 = node2.coordinates
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
    
    def _calculate_travel_time(self, distance: float, start: HyperspaceNode, end: HyperspaceNode) -> float:
        """Calculate travel time between nodes."""
        # Base time + zone modifiers
        base_time = distance * 0.5  # minutes per unit distance
        zone_modifier = self._get_zone_travel_modifier(start.zone, end.zone)
        return base_time * zone_modifier
    
    def _calculate_fuel_cost(self, distance: float, start: HyperspaceNode, end: HyperspaceNode) -> float:
        """Calculate fuel cost for route."""
        # Base fuel + zone modifiers
        base_fuel = distance * 0.1
        zone_modifier = self._get_zone_fuel_modifier(start.zone, end.zone)
        return base_fuel * zone_modifier
    
    def _calculate_risk_level(self, start: HyperspaceNode, end: HyperspaceNode) -> float:
        """Calculate risk level for route."""
        # Average security levels + zone risk
        avg_security = (start.security_level + end.security_level) / 2
        zone_risk = self._get_zone_risk_modifier(start.zone, end.zone)
        return min(1.0, avg_security + zone_risk)
    
    def _determine_route_type(self, start: HyperspaceNode, end: HyperspaceNode) -> HyperspaceRouteType:
        """Determine the best route type between nodes."""
        risk_level = self._calculate_risk_level(start, end)
        
        if risk_level < 0.3:
            return HyperspaceRouteType.SAFE
        elif risk_level < 0.6:
            return HyperspaceRouteType.DIRECT
        elif risk_level < 0.8:
            return HyperspaceRouteType.FAST
        else:
            return HyperspaceRouteType.STEALTH
    
    def _get_zone_travel_modifier(self, zone1: HyperspaceZone, zone2: HyperspaceZone) -> float:
        """Get travel time modifier for zone transition."""
        modifiers = {
            (HyperspaceZone.CORUSCANT_SECTOR, HyperspaceZone.CORELLIA_SECTOR): 1.2,
            (HyperspaceZone.CORELLIA_SECTOR, HyperspaceZone.NABOO_SECTOR): 1.1,
            (HyperspaceZone.DEEP_SPACE, HyperspaceZone.CORUSCANT_SECTOR): 2.0,
            (HyperspaceZone.MUSTAFAR_SECTOR, HyperspaceZone.DEEP_SPACE): 1.8,
        }
        return modifiers.get((zone1, zone2), 1.0)
    
    def _get_zone_fuel_modifier(self, zone1: HyperspaceZone, zone2: HyperspaceZone) -> float:
        """Get fuel cost modifier for zone transition."""
        modifiers = {
            (HyperspaceZone.DEEP_SPACE, HyperspaceZone.CORUSCANT_SECTOR): 1.5,
            (HyperspaceZone.MUSTAFAR_SECTOR, HyperspaceZone.DEEP_SPACE): 1.3,
        }
        return modifiers.get((zone1, zone2), 1.0)
    
    def _get_zone_risk_modifier(self, zone1: HyperspaceZone, zone2: HyperspaceZone) -> float:
        """Get risk modifier for zone transition."""
        modifiers = {
            (HyperspaceZone.DEEP_SPACE, HyperspaceZone.CORUSCANT_SECTOR): 0.3,
            (HyperspaceZone.MUSTAFAR_SECTOR, HyperspaceZone.DEEP_SPACE): 0.2,
        }
        return modifiers.get((zone1, zone2), 0.0)
    
    def calculate_route(self, request: NavigationRequest) -> Optional[NavigationResult]:
        """Calculate optimal hyperspace route.
        
        Parameters
        ----------
        request : NavigationRequest
            Navigation request with start, destination, and constraints
            
        Returns
        -------
        NavigationResult, optional
            Calculated route or None if no route found
        """
        if request.start_location not in self.nodes or request.destination not in self.nodes:
            log_event(f"[HYPESPACE] Invalid locations: {request.start_location} -> {request.destination}")
            return None
        
        # Find all possible routes
        possible_routes = self._find_all_routes(request.start_location, request.destination)
        
        if not possible_routes:
            log_event(f"[HYPESPACE] No routes found between {request.start_location} and {request.destination}")
            return None
        
        # Filter routes based on constraints
        valid_routes = self._filter_routes_by_constraints(possible_routes, request)
        
        if not valid_routes:
            log_event(f"[HYPESPACE] No valid routes found for constraints")
            return None
        
        # Select best route based on type preference
        best_route = self._select_best_route(valid_routes, request.route_type)
        
        if best_route:
            return self._create_navigation_result(best_route, request)
        
        return None
    
    def _find_all_routes(self, start: str, destination: str) -> List[List[HyperspaceRoute]]:
        """Find all possible routes between start and destination."""
        # Simple pathfinding - find direct connections first
        routes = []
        
        for route in self.routes.values():
            if route.start_node == start and route.end_node == destination:
                routes.append([route])
        
        # If no direct route, find multi-hop routes
        if not routes:
            routes = self._find_multi_hop_routes(start, destination)
        
        return routes
    
    def _find_multi_hop_routes(self, start: str, destination: str, max_hops: int = 3) -> List[List[HyperspaceRoute]]:
        """Find multi-hop routes between start and destination."""
        routes = []
        visited = set()
        
        def dfs(current: str, path: List[HyperspaceRoute], hops: int):
            if hops > max_hops:
                return
            
            if current == destination and path:
                routes.append(path[:])
                return
            
            visited.add(current)
            
            for route in self.routes.values():
                if route.start_node == current and route.end_node not in visited:
                    path.append(route)
                    dfs(route.end_node, path, hops + 1)
                    path.pop()
            
            visited.remove(current)
        
        dfs(start, [], 0)
        return routes
    
    def _filter_routes_by_constraints(self, routes: List[List[HyperspaceRoute]], request: NavigationRequest) -> List[List[HyperspaceRoute]]:
        """Filter routes based on navigation constraints."""
        valid_routes = []
        
        for route_chain in routes:
            total_fuel = sum(route.fuel_cost for route in route_chain)
            total_risk = max(route.risk_level for route in route_chain)
            total_time = sum(route.travel_time for route in route_chain)
            
            # Check constraints
            if total_fuel > request.fuel_capacity:
                continue
            
            if total_risk > request.max_risk_tolerance:
                continue
            
            if request.time_constraint and total_time > request.time_constraint:
                continue
            
            valid_routes.append(route_chain)
        
        return valid_routes
    
    def _select_best_route(self, routes: List[List[HyperspaceRoute]], route_type: HyperspaceRouteType) -> Optional[List[HyperspaceRoute]]:
        """Select the best route based on type preference."""
        if not routes:
            return None
        
        # Score routes based on type preference
        scored_routes = []
        for route_chain in routes:
            score = self._calculate_route_score(route_chain, route_type)
            scored_routes.append((score, route_chain))
        
        # Sort by score (higher is better)
        scored_routes.sort(key=lambda x: x[0], reverse=True)
        
        return scored_routes[0][1] if scored_routes else None
    
    def _calculate_route_score(self, route_chain: List[HyperspaceRoute], preferred_type: HyperspaceRouteType) -> float:
        """Calculate score for route based on preferred type."""
        score = 0.0
        
        for route in route_chain:
            # Base score
            score += 100.0
            
            # Type preference bonus
            if route.route_type == preferred_type:
                score += 50.0
            
            # Safety bonus
            if route.risk_level < 0.3:
                score += 25.0
            
            # Efficiency bonus
            if route.travel_time < 10.0:
                score += 15.0
        
        return score
    
    def _create_navigation_result(self, route_chain: List[HyperspaceRoute], request: NavigationRequest) -> NavigationResult:
        """Create navigation result from route chain."""
        total_distance = sum(route.distance for route in route_chain)
        total_time = sum(route.travel_time for route in route_chain)
        total_fuel = sum(route.fuel_cost for route in route_chain)
        
        # Create combined route
        combined_route = HyperspaceRoute(
            route_id=f"combined_{len(self.navigation_history)}",
            start_node=request.start_location,
            end_node=request.destination,
            route_type=request.route_type,
            distance=total_distance,
            travel_time=total_time,
            fuel_cost=total_fuel,
            risk_level=max(route.risk_level for route in route_chain),
            waypoints=[route.start_node for route in route_chain] + [route_chain[-1].end_node],
            restrictions={}
        )
        
        # Calculate risk assessment
        risk_assessment = {
            "combat_risk": max(route.risk_level for route in route_chain),
            "piracy_risk": sum(route.risk_level for route in route_chain) / len(route_chain),
            "navigation_risk": 0.1 if len(route_chain) > 1 else 0.05,
            "zone_transitions": len(set(route.start_node for route in route_chain))
        }
        
        # Generate warnings
        warnings = []
        if combined_route.risk_level > 0.7:
            warnings.append("High risk route - consider alternative path")
        if total_fuel > request.fuel_capacity * 0.8:
            warnings.append("High fuel consumption - ensure adequate reserves")
        if total_time > 60:
            warnings.append("Long travel time - consider faster route")
        
        # Calculate estimated arrival
        estimated_arrival = datetime.now() + timedelta(minutes=total_time)
        
        return NavigationResult(
            route=combined_route,
            total_distance=total_distance,
            total_time=total_time,
            total_fuel_cost=total_fuel,
            risk_assessment=risk_assessment,
            waypoints=combined_route.waypoints,
            estimated_arrival=estimated_arrival,
            warnings=warnings
        )
    
    def start_navigation(self, result: NavigationResult) -> bool:
        """Start navigation along calculated route.
        
        Parameters
        ----------
        result : NavigationResult
            Navigation result to execute
            
        Returns
        -------
        bool
            True if navigation started successfully
        """
        if self.active_route:
            log_event("[HYPESPACE] Navigation already in progress")
            return False
        
        self.active_route = result
        self.current_location = result.route.start_node
        self.navigation_history.append(result)
        
        log_event(f"[HYPESPACE] Started navigation: {result.route.start_node} -> {result.route.end_node}")
        log_event(f"[HYPESPACE] Estimated arrival: {result.estimated_arrival}")
        
        return True
    
    def update_navigation_progress(self, current_waypoint: str) -> Dict[str, Any]:
        """Update navigation progress.
        
        Parameters
        ----------
        current_waypoint : str
            Current waypoint in navigation
            
        Returns
        -------
        Dict[str, Any]
            Navigation progress information
        """
        if not self.active_route:
            return {"status": "no_active_navigation"}
        
        self.current_location = current_waypoint
        
        # Calculate progress
        total_waypoints = len(self.active_route.waypoints)
        current_index = self.active_route.waypoints.index(current_waypoint) if current_waypoint in self.active_route.waypoints else 0
        progress_percentage = (current_index / (total_waypoints - 1)) * 100 if total_waypoints > 1 else 100
        
        # Calculate remaining time
        elapsed_time = (datetime.now() - (self.active_route.estimated_arrival - timedelta(minutes=self.active_route.total_time))).total_seconds() / 60
        remaining_time = max(0, self.active_route.total_time - elapsed_time)
        
        return {
            "status": "navigating",
            "current_waypoint": current_waypoint,
            "progress_percentage": progress_percentage,
            "remaining_time": remaining_time,
            "next_waypoint": self.active_route.waypoints[current_index + 1] if current_index + 1 < len(self.active_route.waypoints) else None,
            "destination": self.active_route.route.end_node
        }
    
    def complete_navigation(self) -> bool:
        """Complete current navigation.
        
        Returns
        -------
        bool
            True if navigation completed successfully
        """
        if not self.active_route:
            return False
        
        log_event(f"[HYPESPACE] Navigation completed: {self.active_route.route.start_node} -> {self.active_route.route.end_node}")
        
        self.current_location = self.active_route.route.end_node
        self.active_route = None
        
        return True
    
    def get_navigation_status(self) -> Dict[str, Any]:
        """Get current navigation status.
        
        Returns
        -------
        Dict[str, Any]
            Current navigation status
        """
        if self.active_route:
            return {
                "status": "navigating",
                "route": self.active_route.route.route_id,
                "current_location": self.current_location,
                "destination": self.active_route.route.end_node,
                "estimated_arrival": self.active_route.estimated_arrival.isoformat(),
                "total_distance": self.active_route.total_distance,
                "total_time": self.active_route.total_time,
                "total_fuel_cost": self.active_route.total_fuel_cost
            }
        else:
            return {
                "status": "idle",
                "current_location": self.current_location
            }
    
    def get_available_destinations(self, from_location: str) -> List[Dict[str, Any]]:
        """Get available destinations from a location.
        
        Parameters
        ----------
        from_location : str
            Starting location
            
        Returns
        -------
        List[Dict[str, Any]]
            List of available destinations with route information
        """
        if from_location not in self.nodes:
            return []
        
        destinations = []
        
        for route in self.routes.values():
            if route.start_node == from_location:
                destination_node = self.nodes[route.end_node]
                destinations.append({
                    "name": route.end_node,
                    "zone": destination_node.zone.value,
                    "distance": route.distance,
                    "travel_time": route.travel_time,
                    "fuel_cost": route.fuel_cost,
                    "risk_level": route.risk_level,
                    "route_type": route.route_type.value
                })
        
        return destinations 
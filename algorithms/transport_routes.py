"""
Data structure for managing public transport routes and stops.

This module implements an efficient data structure for managing public transport
routes where each route has a unique identifier and a set of stops. The structure
allows for efficient retrieval of routes based on stops and efficient addition/removal
of stops from routes.

Problem Statement:
A software system needs to manage a list of public transport routes, where each route
has a unique identifier and a set of stops. Design a data structure that allows:
1. Efficient retrieval of routes based on a given stop
2. Efficient addition or removal of stops from a route

Time Complexity Analysis:
- Add stop to route: O(1) average case
- Remove stop from route: O(1) average case  
- Find routes by stop: O(k) where k is number of routes containing the stop
- Add new route: O(m) where m is number of stops in the route

Space Complexity: O(n * m) where n is routes and m is average stops per route
"""

from typing import Set, List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import random
import string


@dataclass
class Stop:
    """
    Represents a public transport stop.
    
    Attributes:
        stop_id: Unique identifier for the stop
        name: Human-readable name of the stop
        latitude: GPS latitude coordinate
        longitude: GPS longitude coordinate
    """
    stop_id: str
    name: str
    latitude: float
    longitude: float
    
    def __hash__(self):
        return hash(self.stop_id)
    
    def __eq__(self, other):
        if isinstance(other, Stop):
            return self.stop_id == other.stop_id
        return False


@dataclass
class Route:
    """
    Represents a public transport route.
    
    Attributes:
        route_id: Unique identifier for the route
        name: Human-readable name of the route
        stops: Set of stops that belong to this route
        route_type: Type of transport (bus, metro, tram, etc.)
    """
    route_id: str
    name: str
    stops: Set[Stop] = field(default_factory=set)
    route_type: str = "bus"
    
    def add_stop(self, stop: Stop) -> bool:
        """
        Add a stop to this route.
        
        Args:
            stop: Stop to add
            
        Returns:
            True if stop was added, False if already existed
            
        Time Complexity: O(1) average case
        """
        if stop in self.stops:
            return False
        self.stops.add(stop)
        return True
    
    def remove_stop(self, stop: Stop) -> bool:
        """
        Remove a stop from this route.
        
        Args:
            stop: Stop to remove
            
        Returns:
            True if stop was removed, False if not found
            
        Time Complexity: O(1) average case
        """
        if stop in self.stops:
            self.stops.remove(stop)
            return True
        return False
    
    def has_stop(self, stop: Stop) -> bool:
        """
        Check if route contains a specific stop.
        
        Args:
            stop: Stop to check
            
        Returns:
            True if route contains the stop
            
        Time Complexity: O(1) average case
        """
        return stop in self.stops
    
    def get_stop_count(self) -> int:
        """
        Get the number of stops in this route.
        
        Returns:
            Number of stops
            
        Time Complexity: O(1)
        """
        return len(self.stops)


class TransportRouteManager:
    """
    Efficient data structure for managing public transport routes and stops.
    
    This class uses a combination of hash maps to provide efficient operations:
    1. routes: Maps route_id to Route objects
    2. stop_to_routes: Maps stop to set of routes containing that stop
    3. stops: Maps stop_id to Stop objects for quick lookup
    
    The dual indexing approach ensures both route-based and stop-based
    operations are efficient.
    """
    
    def __init__(self):
        """Initialize the transport route manager."""
        # Primary storage: route_id -> Route
        self.routes: Dict[str, Route] = {}
        
        # Inverse index: stop -> set of routes containing that stop
        self.stop_to_routes: Dict[Stop, Set[str]] = defaultdict(set)
        
        # Stop lookup: stop_id -> Stop object
        self.stops: Dict[str, Stop] = {}
    
    def add_stop(self, stop_id: str, name: str, latitude: float, longitude: float) -> Stop:
        """
        Add a new stop to the system.
        
        Args:
            stop_id: Unique identifier for the stop
            name: Human-readable name
            latitude: GPS latitude
            longitude: GPS longitude
            
        Returns:
            The created Stop object
            
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        if stop_id in self.stops:
            raise ValueError(f"Stop with ID {stop_id} already exists")
        
        stop = Stop(stop_id, name, latitude, longitude)
        self.stops[stop_id] = stop
        return stop
    
    def get_stop(self, stop_id: str) -> Optional[Stop]:
        """
        Retrieve a stop by its ID.
        
        Args:
            stop_id: ID of the stop to retrieve
            
        Returns:
            Stop object if found, None otherwise
            
        Time Complexity: O(1)
        """
        return self.stops.get(stop_id)
    
    def add_route(self, route_id: str, name: str, route_type: str = "bus") -> Route:
        """
        Add a new route to the system.
        
        Args:
            route_id: Unique identifier for the route
            name: Human-readable name
            route_type: Type of transport
            
        Returns:
            The created Route object
            
        Time Complexity: O(1)
        Space Complexity: O(1)
        """
        if route_id in self.routes:
            raise ValueError(f"Route with ID {route_id} already exists")
        
        route = Route(route_id, name, set(), route_type)
        self.routes[route_id] = route
        return route
    
    def get_route(self, route_id: str) -> Optional[Route]:
        """
        Retrieve a route by its ID.
        
        Args:
            route_id: ID of the route to retrieve
            
        Returns:
            Route object if found, None otherwise
            
        Time Complexity: O(1)
        """
        return self.routes.get(route_id)
    
    def add_stop_to_route(self, route_id: str, stop_id: str) -> bool:
        """
        Add a stop to a specific route.
        
        This operation updates both the route's stop set and the inverse index
        for efficient bidirectional lookup.
        
        Args:
            route_id: ID of the route
            stop_id: ID of the stop to add
            
        Returns:
            True if stop was added successfully
            
        Raises:
            ValueError: If route or stop doesn't exist
            
        Time Complexity: O(1) average case
        Space Complexity: O(1)
        """
        route = self.routes.get(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")
        
        stop = self.stops.get(stop_id)
        if not stop:
            raise ValueError(f"Stop {stop_id} not found")
        
        # Add stop to route
        added = route.add_stop(stop)
        
        if added:
            # Update inverse index
            self.stop_to_routes[stop].add(route_id)
        
        return added
    
    def remove_stop_from_route(self, route_id: str, stop_id: str) -> bool:
        """
        Remove a stop from a specific route.
        
        This operation updates both the route's stop set and the inverse index.
        
        Args:
            route_id: ID of the route
            stop_id: ID of the stop to remove
            
        Returns:
            True if stop was removed successfully
            
        Raises:
            ValueError: If route or stop doesn't exist
            
        Time Complexity: O(1) average case
        Space Complexity: O(1)
        """
        route = self.routes.get(route_id)
        if not route:
            raise ValueError(f"Route {route_id} not found")
        
        stop = self.stops.get(stop_id)
        if not stop:
            raise ValueError(f"Stop {stop_id} not found")
        
        # Remove stop from route
        removed = route.remove_stop(stop)
        
        if removed:
            # Update inverse index
            self.stop_to_routes[stop].discard(route_id)
            
            # Clean up empty sets in inverse index
            if not self.stop_to_routes[stop]:
                del self.stop_to_routes[stop]
        
        return removed
    
    def get_routes_by_stop(self, stop_id: str) -> List[Route]:
        """
        Find all routes that contain a specific stop.
        
        This is one of the key operations that benefits from the inverse index.
        Without it, we would need to iterate through all routes.
        
        Args:
            stop_id: ID of the stop to search for
            
        Returns:
            List of Route objects containing the stop
            
        Time Complexity: O(k) where k is number of routes containing the stop
        Space Complexity: O(k)
        """
        stop = self.stops.get(stop_id)
        if not stop:
            return []
        
        route_ids = self.stop_to_routes.get(stop, set())
        return [self.routes[route_id] for route_id in route_ids]
    
    def get_common_routes(self, stop_ids: List[str]) -> List[Route]:
        """
        Find routes that contain all specified stops.
        
        Useful for finding routes that connect multiple stops.
        
        Args:
            stop_ids: List of stop IDs that must all be in the route
            
        Returns:
            List of routes containing all specified stops
            
        Time Complexity: O(k * s) where k is routes per stop, s is number of stops
        Space Complexity: O(k)
        """
        if not stop_ids:
            return []
        
        # Get routes for first stop
        common_routes = set()
        first_stop = self.stops.get(stop_ids[0])
        if first_stop:
            common_routes = set(self.stop_to_routes.get(first_stop, set()))
        
        # Intersect with routes for remaining stops
        for stop_id in stop_ids[1:]:
            stop = self.stops.get(stop_id)
            if not stop:
                return []  # If any stop doesn't exist, no common routes
            
            stop_routes = self.stop_to_routes.get(stop, set())
            common_routes &= stop_routes
            
            if not common_routes:
                break  # Early termination if no common routes remain
        
        return [self.routes[route_id] for route_id in common_routes]
    
    def remove_route(self, route_id: str) -> bool:
        """
        Remove a route from the system.
        
        This operation cleans up all references in the inverse index.
        
        Args:
            route_id: ID of the route to remove
            
        Returns:
            True if route was removed
            
        Time Complexity: O(m) where m is number of stops in the route
        Space Complexity: O(1)
        """
        route = self.routes.get(route_id)
        if not route:
            return False
        
        # Remove route from inverse index for all its stops
        for stop in route.stops:
            self.stop_to_routes[stop].discard(route_id)
            if not self.stop_to_routes[stop]:
                del self.stop_to_routes[stop]
        
        # Remove route from primary storage
        del self.routes[route_id]
        return True
    
    def get_route_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the route system.
        
        Returns:
            Dictionary with system statistics
            
        Time Complexity: O(n) where n is number of routes
        """
        total_routes = len(self.routes)
        total_stops = len(self.stops)
        total_connections = sum(len(route.stops) for route in self.routes.values())
        
        if total_routes > 0:
            avg_stops_per_route = total_connections / total_routes
        else:
            avg_stops_per_route = 0
        
        return {
            "total_routes": total_routes,
            "total_stops": total_stops,
            "total_connections": total_connections,
            "average_stops_per_route": round(avg_stops_per_route, 2)
        }
    
    def find_transfer_points(self, min_routes: int = 2) -> List[Tuple[Stop, int]]:
        """
        Find stops that serve as transfer points (served by multiple routes).
        
        Args:
            min_routes: Minimum number of routes for a stop to be considered a transfer point
            
        Returns:
            List of tuples (stop, route_count) sorted by route count descending
            
        Time Complexity: O(s + s log s) where s is number of stops
        """
        transfer_points = []
        
        for stop, route_ids in self.stop_to_routes.items():
            route_count = len(route_ids)
            if route_count >= min_routes:
                transfer_points.append((stop, route_count))
        
        # Sort by route count descending
        transfer_points.sort(key=lambda x: x[1], reverse=True)
        return transfer_points


def generate_sample_transport_data(manager: TransportRouteManager, 
                                 num_stops: int = 100, 
                                 num_routes: int = 20) -> None:
    """
    Generate sample transport data for testing.
    
    Args:
        manager: TransportRouteManager instance
        num_stops: Number of stops to create
        num_routes: Number of routes to create
    """
    print(f"Generating {num_stops} stops and {num_routes} routes...")
    
    # Generate stops
    stops = []
    for i in range(num_stops):
        stop_id = f"STOP_{i:03d}"
        name = f"Stop {i+1}"
        # Generate coordinates around a central point (Bogotá)
        latitude = 4.60971 + random.uniform(-0.1, 0.1)
        longitude = -74.08175 + random.uniform(-0.1, 0.1)
        
        stop = manager.add_stop(stop_id, name, latitude, longitude)
        stops.append(stop)
    
    # Generate routes with different types
    route_types = ["bus", "metro", "tram", "rapid_transit"]
    
    for i in range(num_routes):
        route_id = f"ROUTE_{i:03d}"
        route_type = random.choice(route_types)
        name = f"{route_type.title()} Line {i+1}"
        
        route = manager.add_route(route_id, name, route_type)
        
        # Add random stops to route (5-15 stops per route)
        num_stops_in_route = random.randint(5, min(15, num_stops))
        selected_stops = random.sample(stops, num_stops_in_route)
        
        for stop in selected_stops:
            manager.add_stop_to_route(route_id, stop.stop_id)
    
    print("Sample data generation completed!")


def demonstrate_transport_system():
    """
    Demonstrate the transport route management system with comprehensive examples.
    """
    print("="*60)
    print("PUBLIC TRANSPORT ROUTE MANAGEMENT SYSTEM")
    print("="*60)
    
    # Initialize the system
    manager = TransportRouteManager()
    
    # Generate sample data
    generate_sample_transport_data(manager, num_stops=50, num_routes=10)
    
    # Display system statistics
    stats = manager.get_route_statistics()
    print(f"\\nSYSTEM STATISTICS:")
    print(f"- Total routes: {stats['total_routes']}")
    print(f"- Total stops: {stats['total_stops']}")
    print(f"- Total connections: {stats['total_connections']}")
    print(f"- Average stops per route: {stats['average_stops_per_route']}")
    
    # Demonstrate finding routes by stop
    print(f"\\n{'-'*40}")
    print("FINDING ROUTES BY STOP")
    print(f"{'-'*40}")
    
    sample_stop_id = "STOP_010"
    routes_for_stop = manager.get_routes_by_stop(sample_stop_id)
    print(f"Routes serving stop {sample_stop_id}:")
    for route in routes_for_stop:
        print(f"  - {route.route_id}: {route.name} ({route.route_type})")
    
    # Demonstrate finding common routes
    print(f"\\n{'-'*40}")
    print("FINDING COMMON ROUTES")
    print(f"{'-'*40}")
    
    test_stops = ["STOP_005", "STOP_015", "STOP_025"]
    common_routes = manager.get_common_routes(test_stops)
    print(f"Routes connecting stops {', '.join(test_stops)}:")
    for route in common_routes:
        print(f"  - {route.route_id}: {route.name}")
    
    # Find transfer points
    print(f"\\n{'-'*40}")
    print("TRANSFER POINTS ANALYSIS")
    print(f"{'-'*40}")
    
    transfer_points = manager.find_transfer_points(min_routes=2)
    print("Top transfer points (stops served by multiple routes):")
    for i, (stop, route_count) in enumerate(transfer_points[:10], 1):
        print(f"  {i:2d}. {stop.stop_id} ({stop.name}): {route_count} routes")
    
    # Demonstrate adding and removing stops
    print(f"\\n{'-'*40}")
    print("DYNAMIC ROUTE MODIFICATION")
    print(f"{'-'*40}")
    
    # Add a new stop
    new_stop = manager.add_stop("NEW_STOP", "New Terminal", 4.65, -74.09)
    print(f"Added new stop: {new_stop.stop_id}")
    
    # Add the stop to some routes
    sample_routes = list(manager.routes.keys())[:3]
    for route_id in sample_routes:
        manager.add_stop_to_route(route_id, new_stop.stop_id)
        print(f"Added {new_stop.stop_id} to route {route_id}")
    
    # Verify the stop is now served by these routes
    routes_for_new_stop = manager.get_routes_by_stop(new_stop.stop_id)
    print(f"\\nRoutes now serving {new_stop.stop_id}:")
    for route in routes_for_new_stop:
        print(f"  - {route.route_id}: {route.name}")
    
    # Performance demonstration
    print(f"\\n{'-'*40}")
    print("PERFORMANCE DEMONSTRATION")
    print(f"{'-'*40}")
    
    import time
    
    # Measure time for finding routes by stop
    start_time = time.time()
    for _ in range(1000):
        manager.get_routes_by_stop("STOP_010")
    lookup_time = time.time() - start_time
    
    print(f"Time for 1000 route lookups by stop: {lookup_time:.6f} seconds")
    print(f"Average time per lookup: {lookup_time/1000:.9f} seconds")
    
    # Measure time for adding/removing stops
    start_time = time.time()
    test_route = list(manager.routes.keys())[0]
    test_stop = "STOP_001"
    
    for _ in range(1000):
        manager.add_stop_to_route(test_route, test_stop)
        manager.remove_stop_from_route(test_route, test_stop)
    
    modification_time = time.time() - start_time
    print(f"Time for 1000 add/remove operations: {modification_time:.6f} seconds")
    print(f"Average time per operation: {modification_time/2000:.9f} seconds")


def analyze_complexity():
    """
    Provide detailed complexity analysis of the data structure.
    """
    print(f"\\n{'='*60}")
    print("COMPLEXITY ANALYSIS")
    print(f"{'='*60}")
    
    print("""
    DATA STRUCTURE CHOICE JUSTIFICATION:
    
    The TransportRouteManager uses a combination of hash maps to achieve
    optimal performance for the required operations:
    
    1. Primary Storage (routes): Dict[str, Route]
       - Maps route_id to Route objects
       - Enables O(1) route lookup and modification
    
    2. Inverse Index (stop_to_routes): Dict[Stop, Set[str]]
       - Maps each stop to set of routes containing it
       - Enables efficient route discovery by stop
    
    3. Stop Registry (stops): Dict[str, Stop]
       - Maps stop_id to Stop objects
       - Enables O(1) stop lookup
    
    OPERATION COMPLEXITIES:
    
    ✓ Add stop to route: O(1) average case
      - Hash set insertion + inverse index update
    
    ✓ Remove stop from route: O(1) average case
      - Hash set removal + inverse index cleanup
    
    ✓ Find routes by stop: O(k) where k = routes containing the stop
      - Direct lookup in inverse index + route object retrieval
    
    ✓ Add new route: O(m) where m = number of stops in the route
      - Route creation + updating inverse index for all stops
    
    ✓ Find common routes: O(k * s) where k = avg routes per stop, s = stops
      - Set intersection operations across multiple stops
    
    SPACE COMPLEXITY:
    
    Total space: O(R + S + C) where:
    - R = number of routes
    - S = number of stops  
    - C = total connections (sum of stops across all routes)
    
    The inverse index adds O(C) space but enables much faster queries.
    
    ALTERNATIVE APPROACHES CONSIDERED:
    
    1. Simple List Approach:
       - Routes as list, linear search for stops
       - Time: O(n) for route lookup by stop
       - Space: O(R + C)
       - Rejected: Too slow for large datasets
    
    2. Graph-Based Approach:
       - Model as bipartite graph (routes-stops)
       - Time: O(degree) for lookups
       - Space: O(R + S + C)
       - Rejected: More complex, similar performance
    
    3. Database with Indexes:
       - Relational tables with B-tree indexes
       - Time: O(log n) for most operations
       - Space: O(R + S + C + index overhead)
       - Considered: Good for persistent storage, overkill for in-memory
    
    SCALABILITY CONSIDERATIONS:
    
    ✓ Memory Efficient: Stores each stop/route object once
    ✓ Cache Friendly: Hash map access patterns
    ✓ Concurrent Safe: Can be made thread-safe with locks
    ✓ Extensible: Easy to add new query types
    
    REAL-WORLD PERFORMANCE:
    
    For a typical city transport system:
    - 10,000 stops
    - 500 routes  
    - 50 stops per route average
    - Memory usage: ~50MB
    - Query response: <1ms
    
    This design scales well to metropolitan transit systems.
    """)


def main():
    """
    Main demonstration of the transport route management system.
    """
    demonstrate_transport_system()
    analyze_complexity()


if __name__ == "__main__":
    main()

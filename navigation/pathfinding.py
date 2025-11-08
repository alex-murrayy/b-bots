"""
Pathfinding algorithms for navigating the campus map
Implements Dijkstra's algorithm for shortest path finding
"""

from typing import List, Dict, Tuple, Optional
import heapq
from map import CampusMap


class Pathfinder:
    """Pathfinding system using Dijkstra's algorithm"""
    
    def __init__(self, campus_map: CampusMap):
        self.map = campus_map
    
    def find_shortest_path(self, start: str, end: str) -> Tuple[List[str], float]:
        """
        Find the shortest path between two locations using Dijkstra's algorithm.
        
        Returns:
            Tuple of (path as list of location names, total distance)
            Returns ([], float('inf')) if no path exists
        """
        if start not in self.map.locations or end not in self.map.locations:
            return [], float('inf')
        
        if start == end:
            return [start], 0.0
        
        # Dijkstra's algorithm
        distances: Dict[str, float] = {start: 0.0}
        previous: Dict[str, Optional[str]] = {start: None}
        visited: set = set()
        pq: List[Tuple[float, str]] = [(0.0, start)]  # priority queue
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == end:
                # Reconstruct path
                path = []
                node = end
                while node is not None:
                    path.append(node)
                    node = previous[node]
                path.reverse()
                return path, current_dist
            
            # Explore neighbors
            neighbors = self.map.get_neighbors(current)
            for neighbor, edge_dist in neighbors.items():
                if neighbor in visited:
                    continue
                
                new_dist = current_dist + edge_dist
                
                if neighbor not in distances or new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    heapq.heappush(pq, (new_dist, neighbor))
        
        # No path found
        return [], float('inf')
    
    def find_path_to_multiple(self, start: str, destinations: List[str], 
                              return_to_start: bool = False) -> Tuple[List[str], float]:
        """
        Find shortest path visiting multiple destinations (TSP approximation using nearest neighbor).
        
        Args:
            start: Starting location
            destinations: List of destinations to visit
            return_to_start: If True, return to starting location after visiting all destinations
        
        Returns:
            Tuple of (path as list of location names, total distance)
        """
        if not destinations:
            return [start], 0.0
        
        # Remove duplicates and start location from destinations
        destinations = list(set(destinations))
        if start in destinations:
            destinations.remove(start)
        
        if not destinations:
            if return_to_start:
                return [start, start], 0.0
            return [start], 0.0
        
        path = [start]
        total_distance = 0.0
        current = start
        remaining = set(destinations)
        
        # Greedy nearest neighbor approach
        while remaining:
            # Find nearest unvisited destination
            nearest = None
            nearest_dist = float('inf')
            nearest_path = []
            
            for dest in remaining:
                sub_path, dist = self.find_shortest_path(current, dest)
                if dist < nearest_dist:
                    nearest = dest
                    nearest_dist = dist
                    nearest_path = sub_path
            
            if nearest is None:
                break
            
            # Add path (skip first node as it's already in path)
            path.extend(nearest_path[1:])
            total_distance += nearest_dist
            current = nearest
            remaining.remove(nearest)
        
        # Return to start if requested
        if return_to_start and current != start:
            return_path, return_dist = self.find_shortest_path(current, start)
            path.extend(return_path[1:])
            total_distance += return_dist
        
        return path, total_distance
    
    def calculate_distance(self, path: List[str]) -> float:
        """Calculate total distance of a given path"""
        if len(path) < 2:
            return 0.0
        
        total = 0.0
        for i in range(len(path) - 1):
            dist = self.map.get_distance(path[i], path[i + 1])
            if dist is None:
                # Path not directly connected, find shortest path
                _, dist = self.find_shortest_path(path[i], path[i + 1])
            total += dist
        
        return total
    
    def get_path_instructions(self, path: List[str]) -> List[Dict[str, any]]:
        """
        Generate step-by-step instructions for following a path.
        Useful for RC car navigation.
        """
        if len(path) < 2:
            return []
        
        instructions = []
        for i in range(len(path) - 1):
            current = path[i]
            next_loc = path[i + 1]
            distance = self.map.get_distance(current, next_loc)
            
            if distance is None:
                # If not directly connected, we need intermediate steps
                # For simplicity, we'll use direct path info
                distance = 0
            
            instruction = {
                'from': current,
                'to': next_loc,
                'distance': distance,
                'step': i + 1,
                'action': f"Navigate from {current} to {next_loc}"
            }
            instructions.append(instruction)
        
        return instructions


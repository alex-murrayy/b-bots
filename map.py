"""
Campus Map Module for University at Buffalo
Represents the campus as a graph with buildings and paths between them.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Location:
    """Represents a location on campus"""
    name: str
    building_code: str
    coordinates: Tuple[float, float]  # (x, y) for visualization
    description: str = ""
    is_delivery_point: bool = True


class CampusMap:
    """Graph representation of UB campus with buildings and paths"""
    
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.graph: Dict[str, Dict[str, float]] = {}  # adjacency list with distances
        
        self._initialize_ub_campus()
    
    def _initialize_ub_campus(self):
        """Initialize University at Buffalo campus locations and connections"""
        
        # North Campus - Major Buildings
        locations_data = [
            # Academic Buildings
            ("Capen Hall", "CPN", (0, 0), "Main library and student center", True),
            ("Norton Hall", "NRN", (2, 0), "Engineering and sciences", True),
            ("Alumni Arena", "AA", (4, 2), "Athletics and events", True),
            ("Student Union", "SU", (1, 1), "Student activities center", True),
            ("Davis Hall", "DAV", (3, -1), "Engineering building", True),
            ("Baldy Hall", "BLD", (-1, 2), "Humanities building", True),
            ("Clemens Hall", "CLE", (-2, 0), "Social sciences", True),
            ("O'Brian Hall", "OBR", (0, 3), "Law school", True),
            ("Jacobs Management Center", "JMC", (2, 3), "Business school", True),
            ("Furnas Hall", "FUR", (4, 0), "Engineering labs", True),
            ("Knox Hall", "KNX", (-1, -1), "Natural sciences", True),
            ("Park Hall", "PRK", (-2, 2), "Arts and humanities", True),
            
            # Residence Halls
            ("Ellicott Complex", "ELL", (5, -2), "Residence hall complex", True),
            ("Greiner Hall", "GRN", (1, -3), "Residence hall", True),
            ("Governors Complex", "GOV", (-3, -2), "Residence hall complex", True),
            
            # Dining Locations
            ("C3 Dining Center", "C3", (5, -1), "Main dining facility", True),
            ("One World Café", "OWC", (1, 0), "Café and dining", True),
            ("The Cellar", "CEL", (0, 1), "Basement dining area", True),
            
            # Other Important Locations
            ("UB Commons", "UBC", (2, 1), "Shopping and services", True),
            ("Baird Point", "BPD", (-1, 3), "Outdoor gathering space", True),
            ("Center for the Arts", "CFA", (-2, 1), "Arts and performances", True),
        ]
        
        # Add all locations
        for name, code, coords, desc, is_delivery in locations_data:
            self.add_location(name, code, coords, desc, is_delivery)
        
        # Define paths between locations (undirected graph)
        # Format: (location1, location2, distance_in_meters)
        connections = [
            # Main academic area connections
            ("Capen Hall", "Norton Hall", 200),
            ("Capen Hall", "Student Union", 150),
            ("Capen Hall", "One World Café", 100),
            ("Capen Hall", "Baldy Hall", 180),
            ("Capen Hall", "Clemens Hall", 220),
            ("Capen Hall", "Knox Hall", 250),
            
            # Engineering area
            ("Norton Hall", "Davis Hall", 150),
            ("Norton Hall", "Furnas Hall", 200),
            ("Davis Hall", "Furnas Hall", 100),
            
            # Student life area
            ("Student Union", "One World Café", 50),
            ("Student Union", "The Cellar", 30),
            ("Student Union", "UB Commons", 80),
            ("Alumni Arena", "Student Union", 250),
            ("Alumni Arena", "Furnas Hall", 180),
            
            # Humanities area
            ("Baldy Hall", "Park Hall", 150),
            ("Baldy Hall", "O'Brian Hall", 200),
            ("Baldy Hall", "Baird Point", 100),
            ("Clemens Hall", "Park Hall", 180),
            ("Park Hall", "Center for the Arts", 120),
            
            # Professional schools
            ("O'Brian Hall", "Jacobs Management Center", 150),
            ("O'Brian Hall", "Baird Point", 80),
            
            # Residence halls
            ("Ellicott Complex", "C3 Dining Center", 50),
            ("Ellicott Complex", "Furnas Hall", 300),
            ("Greiner Hall", "Knox Hall", 200),
            ("Greiner Hall", "Clemens Hall", 250),
            ("Governors Complex", "Park Hall", 300),
            ("Governors Complex", "Center for the Arts", 250),
            
            # Dining connections
            ("C3 Dining Center", "Alumni Arena", 350),
            ("One World Café", "UB Commons", 100),
            ("The Cellar", "UB Commons", 80),
            
            # Cross-campus connections
            ("UB Commons", "Alumni Arena", 200),
            ("Baird Point", "Center for the Arts", 150),
            ("Jacobs Management Center", "Alumni Arena", 300),
        ]
        
        # Add all connections (bidirectional)
        for loc1, loc2, distance in connections:
            self.add_connection(loc1, loc2, distance)
    
    def add_location(self, name: str, code: str, coordinates: Tuple[float, float], 
                    description: str = "", is_delivery_point: bool = True):
        """Add a location to the campus map"""
        location = Location(name, code, coordinates, description, is_delivery_point)
        self.locations[name] = location
        if name not in self.graph:
            self.graph[name] = {}
    
    def add_connection(self, loc1: str, loc2: str, distance: float):
        """Add a bidirectional connection between two locations"""
        if loc1 not in self.locations or loc2 not in self.locations:
            raise ValueError(f"Location(s) not found: {loc1}, {loc2}")
        
        if loc1 not in self.graph:
            self.graph[loc1] = {}
        if loc2 not in self.graph:
            self.graph[loc2] = {}
        
        self.graph[loc1][loc2] = distance
        self.graph[loc2][loc1] = distance
    
    def get_location(self, name: str) -> Optional[Location]:
        """Get a location by name"""
        return self.locations.get(name)
    
    def get_neighbors(self, location: str) -> Dict[str, float]:
        """Get all neighbors of a location with distances"""
        return self.graph.get(location, {})
    
    def get_distance(self, loc1: str, loc2: str) -> Optional[float]:
        """Get direct distance between two locations"""
        if loc1 in self.graph and loc2 in self.graph[loc1]:
            return self.graph[loc1][loc2]
        return None
    
    def get_all_delivery_points(self) -> List[str]:
        """Get all locations that are delivery points"""
        return [name for name, loc in self.locations.items() if loc.is_delivery_point]
    
    def get_all_locations(self) -> List[str]:
        """Get all location names"""
        return list(self.locations.keys())
    
    def __str__(self) -> str:
        """String representation of the map"""
        return f"CampusMap with {len(self.locations)} locations and {sum(len(neighbors) for neighbors in self.graph.values()) // 2} paths"


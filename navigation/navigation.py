"""
Navigation Module for RC Car
Converts high-level pathfinding routes into actionable navigation commands
and handles real-world navigation challenges
"""

from typing import List, Dict, Tuple, Optional
from enum import Enum
import math
from map import CampusMap
from pathfinding import Pathfinder


class NavigationMode(Enum):
    """Navigation modes for the robot"""
    GPS_BASED = "gps"  # Use GPS coordinates
    LANDMARK_BASED = "landmark"  # Use visual landmarks
    ODOMETRY = "odometry"  # Use wheel encoders
    MANUAL = "manual"  # Manual control with instructions
    HYBRID = "hybrid"  # Combine multiple methods


class NavigationState(Enum):
    """Current navigation state"""
    IDLE = "idle"
    NAVIGATING = "navigating"
    ARRIVED = "arrived"
    LOST = "lost"
    BLOCKED = "blocked"


class NavigationController:
    """
    Navigation controller that converts pathfinding routes into
    actual navigation commands for the RC car
    """
    
    def __init__(self, campus_map: CampusMap, pathfinder: Pathfinder,
                 navigation_mode: NavigationMode = NavigationMode.MANUAL):
        self.map = campus_map
        self.pathfinder = pathfinder
        self.navigation_mode = navigation_mode
        self.current_route: List[str] = []
        self.current_waypoint_index = 0
        self.current_location: Optional[str] = None
        self.state = NavigationState.IDLE
        
        # For GPS-based navigation
        self.location_coordinates: Dict[str, Tuple[float, float]] = {}
        for name, loc in campus_map.locations.items():
            self.location_coordinates[name] = loc.coordinates
    
    def set_route(self, route: List[str], start_location: str):
        """Set a navigation route"""
        self.current_route = route
        self.current_waypoint_index = 0
        self.current_location = start_location
        self.state = NavigationState.NAVIGATING
    
    def get_next_waypoint(self) -> Optional[str]:
        """Get the next waypoint in the route"""
        if self.current_waypoint_index < len(self.current_route):
            return self.current_route[self.current_waypoint_index]
        return None
    
    def advance_to_next_waypoint(self):
        """Advance to the next waypoint"""
        if self.current_waypoint_index < len(self.current_route):
            self.current_waypoint_index += 1
            if self.current_waypoint_index < len(self.current_route):
                self.current_location = self.current_route[self.current_waypoint_index - 1]
            else:
                # Reached destination
                self.state = NavigationState.ARRIVED
                self.current_location = self.current_route[-1]
    
    def get_navigation_instructions(self, route: List[str]) -> List[Dict]:
        """
        Convert a route into detailed navigation instructions
        
        Returns list of instruction dictionaries with:
        - action: what to do (forward, turn_left, turn_right, stop)
        - distance: how far to travel (meters)
        - direction: heading direction (degrees, for GPS)
        - landmark: visual landmark to look for (for landmark-based)
        """
        instructions = []
        
        if not route or len(route) < 2:
            return instructions
        
        for i in range(len(route) - 1):
            current = route[i]
            next_loc = route[i + 1]
            
            # Get distance and calculate direction
            distance = self.map.get_distance(current, next_loc)
            if distance is None:
                # Not directly connected, find path
                sub_path, dist = self.pathfinder.find_shortest_path(current, next_loc)
                if sub_path:
                    distance = dist
                    # Add intermediate waypoints
                    for j in range(len(sub_path) - 1):
                        instructions.append({
                            'action': 'navigate_to',
                            'from': sub_path[j],
                            'to': sub_path[j + 1],
                            'distance': self.map.get_distance(sub_path[j], sub_path[j + 1]) or 0,
                            'waypoint': sub_path[j + 1]
                        })
                    continue
            
            # Calculate heading direction
            direction = self._calculate_heading(current, next_loc)
            
            instruction = {
                'action': 'navigate_to',
                'from': current,
                'to': next_loc,
                'distance': distance or 0,
                'direction': direction,
                'waypoint': next_loc,
                'step': i + 1
            }
            
            # Add mode-specific information
            if self.navigation_mode == NavigationMode.GPS_BASED:
                instruction['gps_target'] = self.location_coordinates.get(next_loc)
            elif self.navigation_mode == NavigationMode.LANDMARK_BASED:
                instruction['landmark'] = self._get_landmark_for_location(next_loc)
            
            instructions.append(instruction)
        
        return instructions
    
    def _calculate_heading(self, from_loc: str, to_loc: str) -> float:
        """Calculate heading angle from one location to another"""
        from_coords = self.location_coordinates.get(from_loc)
        to_coords = self.location_coordinates.get(to_loc)
        
        if not from_coords or not to_coords:
            return 0.0
        
        dx = to_coords[0] - from_coords[0]
        dy = to_coords[1] - from_coords[1]
        
        # Calculate angle in degrees (0 = North, 90 = East, etc.)
        heading = math.degrees(math.atan2(dy, dx))
        return heading
    
    def _get_landmark_for_location(self, location: str) -> str:
        """Get a landmark description for a location"""
        loc = self.map.get_location(location)
        if loc:
            return loc.description or location
        return location
    
    def get_motor_commands(self, instruction: Dict) -> List[Dict]:
        """
        Convert a navigation instruction into motor commands
        
        Returns list of motor command dictionaries:
        - command: motor command (forward, backward, turn_left, turn_right, stop)
        - duration: how long to execute (seconds)
        - speed: motor speed (0-255)
        """
        commands = []
        
        action = instruction.get('action')
        distance = instruction.get('distance', 0)
        
        if action == 'navigate_to':
            # Estimate travel time based on distance
            # Assuming average speed of 1 m/s for RC car
            speed = 200  # Default speed
            estimated_time = distance / 1.0  # seconds
            
            # For simple navigation, just go forward
            # In reality, you'd need to account for turns, obstacles, etc.
            if distance > 0:
                commands.append({
                    'command': 'forward',
                    'duration': estimated_time,
                    'speed': speed,
                    'distance': distance
                })
            
            # Add stop command
            commands.append({
                'command': 'stop',
                'duration': 0.5
            })
        
        return commands
    
    def update_location(self, location: str):
        """Update the robot's current location (from GPS, landmarks, etc.)"""
        self.current_location = location
        
        # Check if we've reached the current waypoint
        next_waypoint = self.get_next_waypoint()
        if next_waypoint and location == next_waypoint:
            self.advance_to_next_waypoint()
        
        # Update state based on progress
        if self.current_waypoint_index >= len(self.current_route):
            self.state = NavigationState.ARRIVED
        elif self.current_waypoint_index < len(self.current_route):
            self.state = NavigationState.NAVIGATING
    
    def get_current_status(self) -> Dict:
        """Get current navigation status"""
        return {
            'state': self.state.value,
            'current_location': self.current_location,
            'current_waypoint': self.get_next_waypoint(),
            'waypoint_index': self.current_waypoint_index,
            'total_waypoints': len(self.current_route),
            'progress': self.current_waypoint_index / len(self.current_route) if self.current_route else 0
        }
    
    def recalculate_route(self, current_location: str, destination: str):
        """Recalculate route from current location to destination"""
        path, distance = self.pathfinder.find_shortest_path(current_location, destination)
        if path:
            self.set_route(path, current_location)
            return path, distance
        return None, float('inf')


class RealWorldNavigation:
    """
    Enhanced navigation that accounts for real-world challenges:
    - Obstacles
    - GPS accuracy
    - Landmark recognition
    - Path corrections
    """
    
    def __init__(self, navigation_controller: NavigationController):
        self.controller = navigation_controller
        self.obstacles: List[Tuple[float, float]] = []
        self.gps_accuracy = 5.0  # meters
        self.landmark_confidence_threshold = 0.7
    
    def add_obstacle(self, position: Tuple[float, float]):
        """Add an obstacle to avoid"""
        self.obstacles.append(position)
    
    def check_for_obstacles(self, path: List[Tuple[float, float]]) -> bool:
        """Check if path is blocked by obstacles"""
        # Simple obstacle checking - in reality, you'd use sensors
        for waypoint in path:
            for obstacle in self.obstacles:
                distance = math.sqrt(
                    (waypoint[0] - obstacle[0])**2 + 
                    (waypoint[1] - obstacle[1])**2
                )
                if distance < 2.0:  # 2 meter buffer
                    return True
        return False
    
    def get_corrected_heading(self, current_gps: Tuple[float, float], 
                             target_gps: Tuple[float, float]) -> float:
        """Calculate heading with GPS correction"""
        dx = target_gps[0] - current_gps[0]
        dy = target_gps[1] - current_gps[1]
        heading = math.degrees(math.atan2(dy, dx))
        return heading
    
    def should_recalculate(self, current_gps: Tuple[float, float], 
                          expected_location: str) -> bool:
        """Check if we need to recalculate route based on GPS drift"""
        expected_gps = self.controller.location_coordinates.get(expected_location)
        if not expected_gps:
            return False
        
        distance_error = math.sqrt(
            (current_gps[0] - expected_gps[0])**2 + 
            (current_gps[1] - expected_gps[1])**2
        )
        
        # Recalculate if we're more than 2x GPS accuracy away
        return distance_error > (2 * self.gps_accuracy)


def create_navigation_plan(route: List[str], campus_map: CampusMap, 
                          pathfinder: Pathfinder) -> Dict:
    """
    Create a comprehensive navigation plan from a route
    
    Returns a dictionary with:
    - waypoints: list of waypoints
    - instructions: detailed navigation instructions
    - motor_commands: low-level motor commands
    - estimated_time: total estimated time
    - estimated_distance: total distance
    """
    controller = NavigationController(campus_map, pathfinder, NavigationMode.MANUAL)
    controller.set_route(route, route[0] if route else "")
    
    instructions = controller.get_navigation_instructions(route)
    
    motor_commands = []
    total_distance = 0
    total_time = 0
    
    for instruction in instructions:
        cmds = controller.get_motor_commands(instruction)
        motor_commands.extend(cmds)
        total_distance += instruction.get('distance', 0)
        total_time += sum(cmd.get('duration', 0) for cmd in cmds)
    
    return {
        'waypoints': route,
        'instructions': instructions,
        'motor_commands': motor_commands,
        'estimated_time': total_time,
        'estimated_distance': total_distance,
        'waypoint_count': len(route)
    }


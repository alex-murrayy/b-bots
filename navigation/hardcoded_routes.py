"""
Hardcoded Routes System
Simple, reliable routes for RC car delivery demonstrations
Perfect for demos where you know the exact paths
"""

from typing import List, Dict, Tuple
from enum import Enum


class RouteAction(Enum):
    """Actions the robot can take"""
    FORWARD = "forward"
    BACKWARD = "backward"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    STOP = "stop"
    CENTER = "center"
    WAIT = "wait"  # Pause for a specified time


class HardcodedRoute:
    """A hardcoded route with specific instructions"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.instructions: List[Dict] = []
    
    def add_instruction(self, action: RouteAction, duration: float = 1.0, 
                       speed: int = 200, angle: int = 30, **kwargs):
        """
        Add an instruction to the route
        
        Args:
            action: What to do (forward, backward, turn_left, etc.)
            duration: How long to perform action (seconds)
            speed: Motor speed (0-255) for forward/backward
            angle: Steering angle for turns (degrees)
        """
        instruction = {
            'action': action.value,
            'duration': duration,
            'speed': speed,
            'angle': angle,
            **kwargs
        }
        self.instructions.append(instruction)
        return self
    
    def forward(self, duration: float, speed: int = 200):
        """Move forward"""
        return self.add_instruction(RouteAction.FORWARD, duration, speed)
    
    def backward(self, duration: float, speed: int = 200):
        """Move backward"""
        return self.add_instruction(RouteAction.BACKWARD, duration, speed)
    
    def turn_left(self, duration: float = 0.5, angle: int = 30):
        """Turn left"""
        return self.add_instruction(RouteAction.TURN_LEFT, duration, angle=angle)
    
    def turn_right(self, duration: float = 0.5, angle: int = 30):
        """Turn right"""
        return self.add_instruction(RouteAction.TURN_RIGHT, duration, angle=angle)
    
    def stop(self, duration: float = 0.5):
        """Stop"""
        return self.add_instruction(RouteAction.STOP, duration)
    
    def center_steering(self):
        """Center steering"""
        return self.add_instruction(RouteAction.CENTER, 0.1)
    
    def wait(self, duration: float):
        """Wait/pause"""
        return self.add_instruction(RouteAction.WAIT, duration)
    
    def __len__(self):
        return len(self.instructions)
    
    def __str__(self):
        return f"Route '{self.name}': {len(self.instructions)} instructions"


class RouteLibrary:
    """Library of hardcoded routes"""
    
    def __init__(self):
        self.routes: Dict[str, HardcodedRoute] = {}
        self._initialize_routes()
    
    def _initialize_routes(self):
        """Initialize hardcoded routes"""
        
        # Route 1: Student Union → Capen Hall → Norton Hall
        route1 = HardcodedRoute(
            "Student Union to Norton Hall",
            "Quick delivery from Student Union to Norton Hall via Capen"
        )
        route1.forward(3.0, speed=200)  # Go forward 3 seconds
        route1.turn_left(0.3)  # Turn left
        route1.forward(2.0, speed=180)  # Continue forward
        route1.center_steering()  # Straighten out
        route1.forward(2.5, speed=200)  # Final approach
        route1.stop(1.0)  # Stop at destination
        self.routes["student_union_to_norton"] = route1
        
        # Route 2: C3 Dining → Ellicott Complex
        route2 = HardcodedRoute(
            "C3 Dining to Ellicott Complex",
            "Delivery from C3 dining to Ellicott residence hall"
        )
        route2.forward(2.0, speed=200)
        route2.turn_right(0.4)
        route2.forward(3.0, speed=180)
        route2.center_steering()
        route2.forward(1.5, speed=200)
        route2.stop(1.0)
        self.routes["c3_to_ellicott"] = route2
        
        # Route 3: One World Café → Greiner Hall
        route3 = HardcodedRoute(
            "One World Café to Greiner Hall",
            "Delivery from café to residence hall"
        )
        route3.forward(2.5, speed=200)
        route3.turn_left(0.5)
        route3.forward(4.0, speed=180)
        route3.turn_right(0.3)
        route3.forward(2.0, speed=200)
        route3.center_steering()
        route3.forward(1.0, speed=150)
        route3.stop(1.0)
        self.routes["cafe_to_greiner"] = route3
        
        # You can add more routes here
        # Route 4: Return to base
        route4 = HardcodedRoute(
            "Return to Student Union",
            "Return route to Student Union"
        )
        route4.forward(2.0, speed=200)
        route4.turn_right(0.4)
        route4.forward(3.0, speed=180)
        route4.center_steering()
        route4.forward(2.5, speed=200)
        route4.stop(1.0)
        self.routes["return_to_union"] = route4
    
    def get_route(self, route_name: str) -> HardcodedRoute:
        """Get a route by name"""
        return self.routes.get(route_name)
    
    def list_routes(self) -> List[str]:
        """List all available routes"""
        return list(self.routes.keys())
    
    def add_route(self, name: str, route: HardcodedRoute):
        """Add a custom route"""
        self.routes[name] = route


# Pre-defined route mappings for common deliveries
ROUTE_MAPPINGS = {
    # Format: (pickup_location, delivery_location): route_name
    ("Student Union", "Norton Hall"): "student_union_to_norton",
    ("C3 Dining Center", "Ellicott Complex"): "c3_to_ellicott",
    ("One World Café", "Greiner Hall"): "cafe_to_greiner",
    # Add reverse routes
    ("Norton Hall", "Student Union"): "return_to_union",
    ("Ellicott Complex", "Student Union"): "return_to_union",
    ("Greiner Hall", "Student Union"): "return_to_union",
}


def get_route_for_delivery(pickup: str, delivery: str) -> HardcodedRoute:
    """Get hardcoded route for a pickup/delivery pair"""
    route_name = ROUTE_MAPPINGS.get((pickup, delivery))
    if route_name:
        library = RouteLibrary()
        return library.get_route(route_name)
    return None


if __name__ == '__main__':
    # Test the route library
    print("=" * 60)
    print("Hardcoded Routes Library")
    print("=" * 60)
    print()
    
    library = RouteLibrary()
    
    print("Available Routes:")
    for name in library.list_routes():
        route = library.get_route(name)
        print(f"  • {name}")
        print(f"    {route.description}")
        print(f"    Instructions: {len(route)} steps")
        print()
    
    # Show detailed route
    print("=" * 60)
    print("Route Details: Student Union → Norton Hall")
    print("=" * 60)
    route = library.get_route("student_union_to_norton")
    for i, instruction in enumerate(route.instructions, 1):
        action = instruction['action']
        duration = instruction['duration']
        print(f"{i}. {action.upper()}")
        print(f"   Duration: {duration:.1f}s", end="")
        if 'speed' in instruction:
            print(f", Speed: {instruction['speed']}")
        elif 'angle' in instruction:
            print(f", Angle: {instruction['angle']}°")
        else:
            print()


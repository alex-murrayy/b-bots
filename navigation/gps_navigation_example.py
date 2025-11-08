#!/usr/bin/env python3
"""
GPS Navigation Example
Demonstrates how to use GPS-based navigation with the RC car
"""

import time
from map import CampusMap
from pathfinding import Pathfinder
from navigation import NavigationController, NavigationMode
from gps_integration import GPSModule, UB_BUILDINGS_GPS
from update_map_with_gps import create_gps_enabled_map
# Optional: Arduino controller (only needed for real hardware)
try:
    from controls.arduino_wasd_controller import ArduinoWASDController
    HAS_ARDUINO_CONTROLLER = True
except ImportError:
    HAS_ARDUINO_CONTROLLER = False
    ArduinoWASDController = None


class GPSNavigator:
    """
    Complete GPS navigation system for RC car
    Combines GPS, pathfinding, and motor control
    """
    
    def __init__(self, gps_port: str = None, arduino_port: str = '/dev/ttyACM0',
                 simulate: bool = False):
        """
        Initialize GPS navigator
        
        Args:
            gps_port: GPS module serial port (None = simulation)
            arduino_port: Arduino serial port
            simulate: Use simulation mode (no real hardware)
        """
        # Initialize components
        self.campus_map = create_gps_enabled_map()
        self.pathfinder = Pathfinder(self.campus_map)
        self.nav = NavigationController(self.campus_map, self.pathfinder, NavigationMode.GPS_BASED)
        
        # Initialize GPS
        self.gps = GPSModule(port=gps_port, simulate=simulate or (gps_port is None))
        
        # Initialize motor controller (optional, only if not simulating)
        self.motor_controller = None
        if not simulate and HAS_ARDUINO_CONTROLLER:
            try:
                self.motor_controller = ArduinoWASDController(port=arduino_port)
                self.motor_controller.connect()
            except:
                print("Warning: Could not connect to motor controller")
                print("Navigation will run in simulation mode")
                simulate = True
                self.gps = GPSModule(simulate=True)
        elif not simulate:
            print("Warning: Arduino controller not available")
            print("Navigation will run in simulation mode")
            simulate = True
            self.gps = GPSModule(simulate=True)
        
        # Navigation parameters
        self.arrival_threshold = 5.0  # meters - consider arrived when within this distance
        self.navigation_active = False
        self.current_route = []
    
    def plan_route(self, start: str, destinations: list) -> list:
        """
        Plan a route from start to destinations
        
        Args:
            start: Starting location name
            destinations: List of destination location names
        
        Returns:
            Route as list of location names
        """
        if not destinations:
            return [start]
        
        # Use pathfinder to plan route
        route = [start]
        current = start
        
        for destination in destinations:
            path, _ = self.pathfinder.find_shortest_path(current, destination)
            if path and len(path) > 1:
                route.extend(path[1:])  # Skip first (already in route)
            current = destination
        
        return route
    
    def navigate_to_location(self, target_location: str, start_location: str = None):
        """
        Navigate to a specific location
        
        Args:
            target_location: Destination location name
            start_location: Starting location (None = use current GPS)
        """
        if start_location is None:
            # Get current location from GPS
            current_gps = self.gps.get_location()
            if not current_gps:
                print("Error: No GPS fix. Cannot determine current location.")
                return False
            
            # Find nearest location to current GPS
            start_location = self._find_nearest_location(current_gps)
            if not start_location:
                print("Error: Could not determine starting location from GPS")
                return False
        
        # Plan route
        route = self.plan_route(start_location, [target_location])
        print(f"Route planned: {' → '.join(route)}")
        
        # Set navigation route
        self.nav.set_route(route, start_location)
        self.current_route = route
        self.navigation_active = True
        
        # Navigate
        return self._execute_navigation(route)
    
    def _find_nearest_location(self, gps_coords: tuple) -> str:
        """Find the nearest location to given GPS coordinates"""
        min_distance = float('inf')
        nearest = None
        
        for name, location_gps in UB_BUILDINGS_GPS.items():
            distance = self.gps.calculate_distance(gps_coords, location_gps)
            if distance < min_distance:
                min_distance = distance
                nearest = name
        
        # Only return if within reasonable distance (e.g., 100m)
        if min_distance < 100:
            return nearest
        return None
    
    def _execute_navigation(self, route: list) -> bool:
        """Execute navigation along a route"""
        print("\nStarting navigation...")
        
        for waypoint_index, waypoint in enumerate(route[1:], 1):  # Skip start
            print(f"\n--- Waypoint {waypoint_index}/{len(route)-1}: {waypoint} ---")
            
            target_gps = UB_BUILDINGS_GPS.get(waypoint)
            if not target_gps:
                print(f"Error: No GPS coordinates for {waypoint}")
                continue
            
            # Navigate to waypoint
            success = self._navigate_to_waypoint(target_gps, waypoint)
            if not success:
                print(f"Failed to reach {waypoint}")
                return False
            
            # Update navigation state
            self.nav.update_location(waypoint)
        
        print("\n✓ Navigation completed!")
        return True
    
    def _navigate_to_waypoint(self, target_gps: tuple, waypoint_name: str) -> bool:
        """Navigate to a specific waypoint using GPS"""
        max_iterations = 1000  # Safety limit
        iteration = 0
        
        while iteration < max_iterations:
            # Get current position
            current_gps = self.gps.get_location()
            if not current_gps:
                print("  Error: Lost GPS fix")
                return False
            
            # Calculate distance and heading
            distance = self.gps.calculate_distance(current_gps, target_gps)
            heading = self.gps.calculate_heading(current_gps, target_gps)
            
            print(f"  Distance: {distance:.2f}m, Heading: {heading:.2f}°")
            
            # Check if arrived
            if distance <= self.arrival_threshold:
                print(f"  ✓ Arrived at {waypoint_name}!")
                if self.motor_controller:
                    self.motor_controller.stop()
                return True
            
            # Calculate heading error (simplified - in reality, need current heading from compass)
            # For now, just move forward if close enough
            if distance < 50:  # Within 50m, move forward
                if self.motor_controller:
                    self.motor_controller.forward()
                print(f"  → Moving forward...")
            else:
                # Too far - might need to recalculate
                print(f"  → Adjusting course...")
            
            # In simulation, move toward target
            if self.gps.simulate:
                # Simulate movement (move 1% closer each iteration)
                lat_diff = target_gps[0] - current_gps[0]
                lon_diff = target_gps[1] - current_gps[1]
                new_lat = current_gps[0] + lat_diff * 0.01
                new_lon = current_gps[1] + lon_diff * 0.01
                self.gps.set_simulated_location(new_lat, new_lon)
            
            time.sleep(0.1)  # Update every 100ms
            iteration += 1
        
        print(f"  ✗ Timeout reaching {waypoint_name}")
        return False
    
    def stop_navigation(self):
        """Stop navigation"""
        self.navigation_active = False
        if self.motor_controller:
            self.motor_controller.stop()
    
    def get_status(self) -> dict:
        """Get navigation status"""
        nav_status = self.nav.get_current_status()
        gps_loc = self.gps.get_location()
        
        return {
            'navigation_active': self.navigation_active,
            'gps_location': gps_loc,
            'gps_has_fix': self.gps.has_fix(),
            'current_location': nav_status['current_location'],
            'current_waypoint': nav_status['current_waypoint'],
            'progress': nav_status['progress'],
            'state': nav_status['state']
        }


def main():
    """Example usage"""
    print("=" * 60)
    print("GPS Navigation Example")
    print("=" * 60)
    print()
    
    # Create navigator in simulation mode (for testing)
    navigator = GPSNavigator(simulate=True)
    
    # Example: Navigate from Student Union to Norton Hall
    print("Example: Navigate from Student Union to Norton Hall")
    print("-" * 60)
    
    success = navigator.navigate_to_location("Norton Hall", "Student Union")
    
    if success:
        print("\n✓ Navigation example completed successfully!")
    else:
        print("\n✗ Navigation example failed")
    
    # Show status
    status = navigator.get_status()
    print(f"\nFinal Status:")
    print(f"  GPS Location: {status['gps_location']}")
    print(f"  Current Location: {status['current_location']}")
    print(f"  State: {status['state']}")


if __name__ == '__main__':
    main()


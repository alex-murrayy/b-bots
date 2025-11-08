#!/usr/bin/env python3
"""
Route Executor
Executes hardcoded routes by sending commands to the RC car
"""

import time
from typing import Optional
from hardcoded_routes import HardcodedRoute, RouteAction, RouteLibrary

# Try to import Arduino controller
try:
    from controls.arduino_wasd_controller import ArduinoWASDController
    HAS_CONTROLLER = True
except ImportError:
    HAS_CONTROLLER = False
    ArduinoWASDController = None


class RouteExecutor:
    """Executes hardcoded routes on the RC car"""
    
    def __init__(self, arduino_port: str = '/dev/ttyACM0', simulate: bool = False):
        """
        Initialize route executor
        
        Args:
            arduino_port: Arduino serial port
            simulate: Simulation mode (don't send real commands)
        """
        self.simulate = simulate
        self.controller = None
        
        if not simulate and HAS_CONTROLLER:
            try:
                self.controller = ArduinoWASDController(port=arduino_port)
                self.controller.connect()
                print(f"Connected to Arduino on {arduino_port}")
            except Exception as e:
                print(f"Could not connect to Arduino: {e}")
                print("Running in simulation mode")
                self.simulate = True
        else:
            self.simulate = True
            if simulate:
                print("Running in simulation mode")
    
    def execute_route(self, route: HardcodedRoute, verbose: bool = True) -> bool:
        """
        Execute a hardcoded route
        
        Args:
            route: HardcodedRoute to execute
            verbose: Print progress information
        
        Returns:
            True if route completed successfully
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"Executing Route: {route.name}")
            print(f"{'='*60}")
            print(f"Description: {route.description}")
            print(f"Instructions: {len(route)} steps")
            print(f"{'='*60}\n")
        
        try:
            for i, instruction in enumerate(route.instructions, 1):
                action = instruction['action']
                duration = instruction.get('duration', 1.0)
                
                if verbose:
                    print(f"Step {i}/{len(route.instructions)}: {action.upper()}", end="")
                    if 'speed' in instruction:
                        print(f" (speed: {instruction['speed']}, duration: {duration:.1f}s)")
                    elif 'angle' in instruction:
                        print(f" (angle: {instruction['angle']}°, duration: {duration:.1f}s)")
                    else:
                        print(f" (duration: {duration:.1f}s)")
                
                # Execute instruction
                if action == RouteAction.FORWARD.value:
                    speed = instruction.get('speed', 200)
                    if not self.simulate and self.controller:
                        self.controller.forward()
                    if verbose:
                        print(f"  → Moving forward at speed {speed}")
                    time.sleep(duration)
                    if not self.simulate and self.controller:
                        self.controller.stop()
                
                elif action == RouteAction.BACKWARD.value:
                    speed = instruction.get('speed', 200)
                    if not self.simulate and self.controller:
                        self.controller.backward()
                    if verbose:
                        print(f"  → Moving backward at speed {speed}")
                    time.sleep(duration)
                    if not self.simulate and self.controller:
                        self.controller.stop()
                
                elif action == RouteAction.TURN_LEFT.value:
                    angle = instruction.get('angle', 30)
                    if not self.simulate and self.controller:
                        self.controller.left()
                    if verbose:
                        print(f"  → Turning left {angle}°")
                    time.sleep(duration)
                    if not self.simulate and self.controller:
                        self.controller.center()
                
                elif action == RouteAction.TURN_RIGHT.value:
                    angle = instruction.get('angle', 30)
                    if not self.simulate and self.controller:
                        self.controller.right()
                    if verbose:
                        print(f"  → Turning right {angle}°")
                    time.sleep(duration)
                    if not self.simulate and self.controller:
                        self.controller.center()
                
                elif action == RouteAction.STOP.value:
                    if not self.simulate and self.controller:
                        self.controller.stop()
                    if verbose:
                        print(f"  → Stopped")
                    time.sleep(duration)
                
                elif action == RouteAction.CENTER.value:
                    if not self.simulate and self.controller:
                        self.controller.center()
                    if verbose:
                        print(f"  → Centered steering")
                    time.sleep(duration)
                
                elif action == RouteAction.WAIT.value:
                    if verbose:
                        print(f"  → Waiting {duration:.1f}s")
                    time.sleep(duration)
                
                # Small pause between instructions
                time.sleep(0.1)
            
            if verbose:
                print(f"\n{'='*60}")
                print("✓ Route completed successfully!")
                print(f"{'='*60}\n")
            
            return True
        
        except KeyboardInterrupt:
            print("\n\nRoute execution interrupted!")
            if not self.simulate and self.controller:
                self.controller.stop()
            return False
        except Exception as e:
            print(f"\nError executing route: {e}")
            if not self.simulate and self.controller:
                self.controller.stop()
            return False
    
    def execute_route_by_name(self, route_name: str, verbose: bool = True) -> bool:
        """Execute a route by name"""
        library = RouteLibrary()
        route = library.get_route(route_name)
        if route:
            return self.execute_route(route, verbose)
        else:
            print(f"Route not found: {route_name}")
            return False
    
    def close(self):
        """Close connections"""
        if self.controller:
            self.controller.disconnect()


def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Execute hardcoded routes')
    parser.add_argument('--route', '-r', required=True,
                       help='Route name to execute')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0',
                       help='Arduino port')
    parser.add_argument('--simulate', '-s', action='store_true',
                       help='Simulation mode (no real commands)')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List available routes')
    
    args = parser.parse_args()
    
    if args.list:
        library = RouteLibrary()
        print("Available Routes:")
        for name in library.list_routes():
            route = library.get_route(name)
            print(f"  • {name}")
            print(f"    {route.description}")
        return
    
    executor = RouteExecutor(arduino_port=args.port, simulate=args.simulate)
    
    try:
        success = executor.execute_route_by_name(args.route, verbose=True)
        exit(0 if success else 1)
    finally:
        executor.close()


if __name__ == '__main__':
    main()


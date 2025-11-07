"""
Main script for UB Food Delivery RC Car System
Demonstrates the delivery system with example orders and routes
"""

from map import CampusMap
from pathfinding import Pathfinder
from delivery import DeliverySystem, OrderStatus
import json


def print_separator():
    """Print a visual separator"""
    print("\n" + "=" * 80 + "\n")


def print_location_info(campus_map: CampusMap):
    """Print information about all locations"""
    print("UB CAMPUS LOCATIONS")
    print_separator()
    
    locations = campus_map.get_all_locations()
    print(f"Total locations: {len(locations)}\n")
    
    for name in sorted(locations):
        loc = campus_map.get_location(name)
        print(f"  • {name} ({loc.building_code})")
        if loc.description:
            print(f"    {loc.description}")
        print(f"    Coordinates: {loc.coordinates}")
        print()
    
    print_separator()


def print_path(pathfinder: Pathfinder, start: str, end: str):
    """Print pathfinding result between two locations"""
    path, distance = pathfinder.find_shortest_path(start, end)
    
    print(f"PATH: {start} → {end}")
    print_separator()
    
    if not path:
        print("  No path found!")
        return
    
    print(f"  Total distance: {distance:.1f} meters")
    print(f"  Estimated time: {distance / 10.0:.1f} seconds (at 10 m/s)")
    print(f"\n  Route:")
    for i, location in enumerate(path):
        if i == 0:
            print(f"    {i+1}. {location} [START]")
        elif i == len(path) - 1:
            print(f"    {i+1}. {location} [END]")
        else:
            dist = pathfinder.map.get_distance(path[i-1], location)
            print(f"    {i+1}. {location} ({dist:.0f}m from previous)")
    print_separator()


def demo_basic_pathfinding(campus_map: CampusMap, pathfinder: Pathfinder):
    """Demonstrate basic pathfinding"""
    print("DEMONSTRATION: Basic Pathfinding")
    print_separator()
    
    # Example paths
    examples = [
        ("Capen Hall", "Ellicott Complex"),
        ("Student Union", "C3 Dining Center"),
        ("Norton Hall", "O'Brian Hall"),
        ("Greiner Hall", "Alumni Arena"),
    ]
    
    for start, end in examples:
        print_path(pathfinder, start, end)


def demo_delivery_system(campus_map: CampusMap, pathfinder: Pathfinder):
    """Demonstrate the delivery system"""
    print("DEMONSTRATION: Food Delivery System")
    print_separator()
    
    # Create delivery system
    delivery = DeliverySystem(campus_map, pathfinder)
    
    # Create some example orders
    print("Creating delivery orders...\n")
    
    order1 = delivery.create_order(
        customer_name="Alice",
        pickup_location="C3 Dining Center",
        delivery_location="Greiner Hall",
        items=["Pizza", "Soda"],
        priority=1
    )
    print(f"  Created {order1} for Alice")
    
    order2 = delivery.create_order(
        customer_name="Bob",
        pickup_location="One World Café",
        delivery_location="Norton Hall",
        items=["Burrito", "Coffee"],
        priority=2
    )
    print(f"  Created {order2} for Bob")
    
    order3 = delivery.create_order(
        customer_name="Charlie",
        pickup_location="The Cellar",
        delivery_location="Davis Hall",
        items=["Sandwich", "Chips"],
        priority=1
    )
    print(f"  Created {order3} for Charlie")
    
    print_separator()
    
    # Plan delivery route
    start_location = "Student Union"
    print(f"Planning delivery route starting from {start_location}...\n")
    
    route, distance, details = delivery.plan_delivery_route(start_location)
    
    print("DELIVERY ROUTE:")
    print(f"  Total distance: {distance:.1f} meters")
    print(f"  Estimated time: {details['estimated_time_minutes']:.1f} minutes")
    print(f"  Orders to deliver: {details['total_orders']}")
    print(f"\n  Route:")
    route_info = details.get('route_info', {})
    for i, location in enumerate(route):
        marker = ""
        if i == 0:
            marker = " [START]"
        elif i == len(route) - 1:
            marker = " [END]"
        
        location_info = f"    {i+1}. {location}{marker}"
        if location in route_info:
            location_info += f" → {', '.join(route_info[location])}"
        print(location_info)
    
    print_separator()
    
    # Get navigation instructions
    print("NAVIGATION INSTRUCTIONS:")
    instructions = delivery.get_route_instructions(route)
    for instruction in instructions:
        print(f"  Step {instruction['step']}: {instruction['action']}")
        print(f"    Distance: {instruction['distance']:.0f}m")
    
    print_separator()
    
    # Show statistics
    stats = delivery.get_statistics()
    print("DELIVERY STATISTICS:")
    print(f"  Total orders: {stats['total_orders']}")
    print(f"  Pending: {stats['pending']}")
    print(f"  In progress: {stats['in_progress']}")
    print(f"  Completed: {stats['completed']}")
    print_separator()


def interactive_mode(campus_map: CampusMap, pathfinder: Pathfinder):
    """Interactive mode for testing the system"""
    print("INTERACTIVE MODE")
    print_separator()
    print("Commands:")
    print("  'locations' - List all locations")
    print("  'path <start> <end>' - Find path between locations")
    print("  'order <customer> <pickup> <delivery> <items>' - Create order")
    print("  'route <start>' - Plan delivery route")
    print("  'stats' - Show statistics")
    print("  'quit' - Exit")
    print_separator()
    
    delivery = DeliverySystem(campus_map, pathfinder)
    
    while True:
        try:
            command = input("\n> ").strip().split()
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'locations':
                locations = campus_map.get_all_locations()
                for loc in sorted(locations):
                    print(f"  • {loc}")
            elif cmd == 'path' and len(command) >= 3:
                start = ' '.join(command[1:-1])
                end = command[-1]
                path, distance = pathfinder.find_shortest_path(start, end)
                if path:
                    print(f"Path: {' → '.join(path)}")
                    print(f"Distance: {distance:.1f}m")
                else:
                    print("No path found!")
            elif cmd == 'order' and len(command) >= 5:
                customer = command[1]
                pickup = ' '.join(command[2:-2])
                delivery = command[-2]
                items = command[-1].split(',')
                order_id = delivery.create_order(customer, pickup, delivery, items)
                print(f"Created order: {order_id}")
            elif cmd == 'route' and len(command) >= 2:
                start = ' '.join(command[1:])
                route, distance, details = delivery.plan_delivery_route(start)
                print(f"Route: {' → '.join(route)}")
                print(f"Distance: {distance:.1f}m")
                print(f"Orders: {details['total_orders']}")
            elif cmd == 'stats':
                stats = delivery.get_statistics()
                print(f"Orders: {stats['total_orders']} | "
                      f"Pending: {stats['pending']} | "
                      f"In Progress: {stats['in_progress']} | "
                      f"Completed: {stats['completed']}")
            else:
                print("Invalid command. Type 'quit' to exit.")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("UNIVERSITY AT BUFFALO - RC CAR FOOD DELIVERY SYSTEM")
    print("=" * 80 + "\n")
    
    # Initialize campus map and pathfinder
    print("Initializing campus map...")
    campus_map = CampusMap()
    pathfinder = Pathfinder(campus_map)
    print(f"✓ Loaded {len(campus_map.get_all_locations())} locations\n")
    
    # Run demonstrations
    print_location_info(campus_map)
    demo_basic_pathfinding(campus_map, pathfinder)
    demo_delivery_system(campus_map, pathfinder)
    
    # Optional: Run interactive mode
    print("\nWould you like to enter interactive mode? (y/n): ", end='')
    # For automated runs, skip interactive mode
    # response = input().strip().lower()
    # if response == 'y':
    #     interactive_mode(campus_map, pathfinder)
    
    print("\n" + "=" * 80)
    print("Demo completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()


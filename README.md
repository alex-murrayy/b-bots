# University at Buffalo - RC Car Food Delivery System

A pathfinding and delivery management system for an RC car to deliver food across the University at Buffalo campus.

## Summary

Food delivery system for an RC car at the University at Buffalo. It includes:

### Core Components

**Campus Map** (`map.py`)

- Graph representation of UB North Campus
- 21 locations: academic buildings, residence halls, dining facilities
- Connections between locations with distances in meters

**Pathfinding** (`pathfinding.py`)

- Dijkstra's algorithm for shortest paths
- Multi-stop route optimization
- Step-by-step navigation instructions

**Delivery System** (`delivery.py`)

- Order management (create, track, complete)
- Route optimization ensuring pickups before deliveries
- Priority-based scheduling
- Delivery statistics

**Main Demo** (`main.py`)

- Demonstrations of pathfinding and delivery
- Interactive mode (commented out)
- Example usage

### Features

- Ensures pickups happen before deliveries
- Greedy route optimization to minimize distance
- Step-by-step navigation instructions for RC car control
- Priority support for urgent orders
- Delivery statistics and tracking
- Graph representation of UB North Campus with major buildings, residence halls, and dining locations
- Dijkstra's algorithm for finding shortest paths between any two locations
- Greedy algorithm for optimizing multi-stop delivery routes
- Complete order management system with priority scheduling

## Project Structure

```
.
├── map.py           # Campus map representation with locations and connections
├── pathfinding.py   # Pathfinding algorithms (Dijkstra's)
├── delivery.py      # Delivery order management system
├── main.py          # Demo script and interactive mode
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Installation

1. Clone or download this repository
2. Ensure Python 3.7+ is installed
3. No external dependencies required (uses only Python standard library)

## Usage

Run the demo:

```bash
python main.py
```

The system is ready for integration with RC car hardware. We can extend it with:

- GPS tracking
- Obstacle avoidance
- Real-time route adjustments
- Hardware control interfaces

All code is documented and follows best practices. The system uses only Python standard library, so no external dependencies are required.

### Basic Pathfinding

```python
from map import CampusMap
from pathfinding import Pathfinder

# Initialize map and pathfinder
campus_map = CampusMap()
pathfinder = Pathfinder(campus_map)

# Find shortest path
path, distance = pathfinder.find_shortest_path("Capen Hall", "Ellicott Complex")
print(f"Path: {path}")
print(f"Distance: {distance:.1f} meters")
```

### Delivery System

```python
from delivery import DeliverySystem

# Create delivery system
delivery = DeliverySystem(campus_map, pathfinder)

# Create an order
order_id = delivery.create_order(
    customer_name="Alice",
    pickup_location="C3 Dining Center",
    delivery_location="Greiner Hall",
    items=["Pizza", "Soda"],
    priority=1
)

# Plan delivery route
route, distance, details = delivery.plan_delivery_route("Student Union")
print(f"Route: {route}")
print(f"Distance: {distance:.1f} meters")
```

## Campus Locations

The system includes major locations on UB North Campus:

### Academic Buildings

- Capen Hall, Norton Hall, Davis Hall, Furnas Hall
- Baldy Hall, Clemens Hall, Park Hall, Knox Hall
- O'Brian Hall (Law), Jacobs Management Center (Business)

### Residence Halls

- Ellicott Complex, Greiner Hall, Governors Complex

### Dining Locations

- C3 Dining Center, One World Café, The Cellar

### Other Locations

- Student Union, Alumni Arena, UB Commons, Center for the Arts, Baird Point

## Algorithm Details

### Pathfinding

- **Algorithm**: Dijkstra's algorithm
- **Complexity**: O(V log V + E) where V = vertices, E = edges
- **Guarantee**: Always finds the shortest path if one exists

### Route Optimization

- **Algorithm**: Greedy nearest-neighbor approach
- **Use Case**: Multi-stop delivery optimization
- **Note**: Provides good solutions but not guaranteed optimal (TSP is NP-hard)

## Extending the System

### Adding New Locations

```python
campus_map.add_location(
    name="New Building",
    code="NEW",
    coordinates=(x, y),
    description="Description here",
    is_delivery_point=True
)

campus_map.add_connection("Capen Hall", "New Building", 150)  # 150 meters
```

### Custom Pathfinding

You can extend the `Pathfinder` class to implement A\* algorithm for better performance with heuristics, or add obstacle avoidance for the RC car.

### RC Car Integration

The `get_path_instructions()` method provides step-by-step navigation instructions that can be sent to an RC car controller. You can extend this to:

- Convert to motor commands (forward, turn left, turn right)
- Add sensor feedback (GPS, IMU, camera)
- Implement obstacle avoidance
- Add real-time route adjustments

## Future Enhancements

- [ ] A\* pathfinding with heuristics for better performance
- [ ] Real-time GPS tracking and route updates
- [ ] Obstacle detection and avoidance
- [ ] Battery/power management
- [ ] Web dashboard for order management
- [ ] Integration with actual RC car hardware
- [ ] Machine learning for route optimization
- [ ] Multi-vehicle coordination

## License

This project is provided as-is for educational and development purposes.

## Contact

For questions or contributions, please open an issue or submit a pull request.

# b-bots

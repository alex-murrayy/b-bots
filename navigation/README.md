# Navigation and Pathfinding System

Navigation and pathfinding system for the RC car food delivery system at University at Buffalo.

## Overview

The navigation system provides:
- **Campus Map** - Graph representation of UB campus with locations and connections
- **Pathfinding** - Dijkstra's algorithm for shortest paths
- **Route Planning** - Multi-stop route optimization
- **GPS Integration** - GPS coordinate support for real navigation
- **Route Execution** - Execute planned routes on RC car

## Quick Start

### Find Shortest Path

```python
from navigation.map import CampusMap
from navigation.pathfinding import Pathfinder

# Initialize map and pathfinder
campus_map = CampusMap()
pathfinder = Pathfinder(campus_map)

# Find shortest path
path, distance = pathfinder.find_shortest_path("Capen Hall", "Norton Hall")
print(f"Path: {path}")
print(f"Distance: {distance:.1f} meters")
```

### Plan Delivery Route

```python
from navigation.map import CampusMap
from navigation.pathfinding import Pathfinder
from app.delivery import DeliverySystem

# Initialize system
campus_map = CampusMap()
pathfinder = Pathfinder(campus_map)
delivery_system = DeliverySystem(campus_map, pathfinder)

# Create order
order_id = delivery_system.create_order(
    customer_name="Alice",
    pickup_location="Student Union",
    delivery_location="Norton Hall",
    items=["Pizza", "Soda"],
    priority=0
)

# Plan route
route, distance, details = delivery_system.plan_delivery_route(
    start_location="Student Union",
    order_ids=[order_id]
)

print(f"Route: {route}")
print(f"Distance: {distance:.1f} meters")
```

## Components

### 1. Campus Map (`map.py`)

Graph representation of UB North Campus with:
- **21+ locations** (buildings, dorms, dining)
- **Connections** with distances in meters
- **GPS coordinates** (latitude/longitude)
- **Extensible structure**

**Locations Include:**
- Academic buildings (Capen Hall, Norton Hall, Davis Hall, etc.)
- Residence halls (Ellicott Complex, Greiner Hall, Governors Complex)
- Dining locations (C3 Dining Center, One World Café, Student Union)
- Other locations (Alumni Arena, UB Commons, Center for the Arts)

### 2. Pathfinding (`pathfinding.py`)

**Algorithm**: Dijkstra's algorithm
- **Complexity**: O(V log V + E)
- **Guarantee**: Always finds shortest path
- **Multi-stop support**: Visit multiple destinations

**Features:**
- Shortest path between two locations
- Multi-stop route optimization (TSP approximation)
- Step-by-step navigation instructions
- Distance calculations

### 3. Route Execution (`route_executor.py`)

Execute planned routes on RC car:
- **GPS-based navigation** - Use GPS coordinates
- **Landmark-based navigation** - Use visual landmarks
- **Simulation mode** - Test without hardware
- **Arrival detection** - Detect when destination reached

### 4. GPS Integration (`gps_integration.py`)

GPS module interface for real navigation:
- **Hardware support** - Connect GPS module
- **Simulation mode** - Test without hardware
- **Coordinate conversion** - Convert between formats
- **Distance calculations** - Calculate distances from GPS

## Map Accuracy

### Current Map Status

The current map is **approximate and simplified**. It uses:
- ✅ **Building names and locations**
- ✅ **Relative positions** (which buildings are near each other)
- ✅ **Approximate distances** between buildings
- ✅ **Graph structure** showing connectivity
- ✅ **GPS coordinates** for major buildings

### Limitations

- ❌ **Real GPS coordinates** (some locations have approximate coordinates)
- ❌ **Actual walkable paths** (sidewalks, roads)
- ❌ **Elevation data**
- ❌ **Obstacle information**
- ❌ **Traffic/pedestrian flow data**

## Navigation Methods

### 1. GPS-Based Navigation ⭐ Recommended

**How it works:**
- Robot has GPS receiver
- Gets real-time GPS coordinates
- Compares to target location coordinates
- Calculates heading and distance
- Navigates toward target

**Requirements:**
- GPS module (e.g., NEO-6M, NEO-M8N)
- Real GPS coordinates for each building
- Compass/IMU for heading
- GPS accuracy: ~3-5 meters (good enough for buildings)

**Implementation:**
```python
from navigation.gps_integration import GPSModule

# Initialize GPS
gps = GPSModule(port='/dev/ttyUSB0')

# Get current position
current_gps = gps.get_position()

# Get target position
target_gps = (42.9538, -78.8294)  # Capen Hall

# Calculate distance and heading
distance = calculate_distance(current_gps, target_gps)
heading = calculate_heading(current_gps, target_gps)

# Navigate toward target
robot.turn_to_heading(heading)
robot.move_forward(distance)
```

### 2. Landmark-Based Navigation

**How it works:**
- Robot uses camera/computer vision
- Recognizes landmarks (building signs, distinctive features)
- Navigates by following landmarks
- Good for known environments

**Requirements:**
- Camera module
- Computer vision library (OpenCV)
- Pre-trained landmark recognition
- Good lighting conditions

### 3. Odometry-Based Navigation

**How it works:**
- Robot tracks wheel rotations
- Estimates position based on movement
- Needs periodic corrections (landmarks or GPS)
- Drifts over time

**Requirements:**
- Wheel encoders
- IMU (Inertial Measurement Unit)
- Starting position
- Periodic correction points

### 4. Simulation Mode

**How it works:**
- Simulates GPS readings
- Simulates movement
- Good for testing without hardware
- No actual robot movement

**Usage:**
```python
from navigation.route_executor import RouteExecutor

# Create route executor in simulation mode
executor = RouteExecutor(simulate=True)

# Execute route
route = ["Student Union", "Capen Hall", "Norton Hall"]
executor.execute_route(route)
```

## Usage Examples

### Basic Pathfinding

```python
from navigation.map import CampusMap
from navigation.pathfinding import Pathfinder

campus_map = CampusMap()
pathfinder = Pathfinder(campus_map)

# Find shortest path
path, distance = pathfinder.find_shortest_path("Capen Hall", "Ellicott Complex")
print(f"Path: {path}")
print(f"Distance: {distance:.1f} meters")
```

### Multi-Stop Route

```python
# Find path visiting multiple destinations
path, distance = pathfinder.find_path_to_multiple(
    start="Student Union",
    destinations=["Capen Hall", "Norton Hall", "Davis Hall"],
    return_to_start=True
)
print(f"Route: {path}")
print(f"Total distance: {distance:.1f} meters")
```

### Navigation Instructions

```python
# Get step-by-step instructions
instructions = pathfinder.get_path_instructions(path)
for instruction in instructions:
    print(f"{instruction['action']}: {instruction['description']}")
```

### GPS Navigation

```python
from navigation.gps_integration import GPSModule
from navigation.route_executor import RouteExecutor

# Initialize GPS (simulation mode)
gps = GPSModule(simulate=True)

# Initialize route executor
executor = RouteExecutor(gps_module=gps, simulate=True)

# Execute route
route = ["Student Union", "Capen Hall", "Norton Hall"]
executor.execute_route(route)
```

## Testing

### Test Pathfinding

```bash
python3 navigation/test_navigation.py
```

This will test:
- ✅ GPS coordinate loading
- ✅ Distance calculations
- ✅ Heading calculations
- ✅ Navigation plan creation
- ✅ GPS navigation simulation
- ✅ Arrival detection

**All tests use simulation mode** - no hardware needed!

### Test GPS Integration

```python
from navigation.gps_integration import GPSModule

# Test in simulation mode
gps = GPSModule(simulate=True)
position = gps.get_position()
print(f"Current position: {position}")
```

## Adding New Locations

```python
from navigation.map import CampusMap

campus_map = CampusMap()

# Add new location
campus_map.add_location(
    name="New Building",
    code="NEW",
    coordinates=(42.9538, -78.8294),  # GPS coordinates
    description="Description here",
    is_delivery_point=True
)

# Add connection
campus_map.add_connection("Capen Hall", "New Building", 150)  # 150 meters
```

## Algorithm Details

### Pathfinding (Dijkstra's Algorithm)

- **Algorithm**: Dijkstra's algorithm
- **Complexity**: O(V log V + E) where V = vertices, E = edges
- **Guarantee**: Always finds the shortest path if one exists
- **Implementation**: Uses priority queue (heapq)

### Route Optimization

- **Algorithm**: Greedy nearest-neighbor approach
- **Use Case**: Multi-stop delivery optimization
- **Constraint**: Pickups must happen before deliveries
- **Note**: Provides good solutions but not guaranteed optimal (TSP is NP-hard)

## File Structure

```
navigation/
├── map.py                    # Campus map with locations
├── pathfinding.py            # Dijkstra's algorithm
├── route_executor.py         # Route execution
├── gps_integration.py        # GPS module interface
├── gps_navigation_example.py # GPS navigation example
├── test_navigation.py        # Test suite
├── update_map_with_gps.py    # Update map with GPS coordinates
└── README.md                 # This file
```

## Future Enhancements

- [ ] Real GPS tracking and navigation
- [ ] Obstacle detection and avoidance
- [ ] Real-time route adjustments
- [ ] A* pathfinding with heuristics
- [ ] Machine learning route optimization
- [ ] Multi-vehicle coordination
- [ ] Battery/power management
- [ ] Traffic/pedestrian flow data

## Troubleshooting

### GPS Not Working

1. Check GPS module connection
2. Verify GPS coordinates are correct
3. Test in simulation mode first
4. Check GPS signal strength

### Pathfinding Returns No Path

1. Verify locations exist in map
2. Check map connections
3. Ensure locations are connected in graph
4. Test with known locations first

### Route Execution Fails

1. Check GPS module is working
2. Verify route is valid
3. Test in simulation mode
4. Check RC car controls are working

## License

This code is provided as-is for educational and development purposes.


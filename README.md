# University at Buffalo - RC Car Food Delivery System

A complete food delivery system for an RC car that navigates the University at Buffalo campus, from order placement to autonomous delivery.

## Overview

This system provides end-to-end food delivery automation:

- **Web Interface** - Users place orders via browser
- **Order Management** - Route optimization and order tracking
- **Pathfinding** - Dijkstra's algorithm for shortest paths
- **RC Car Control** - Arduino-based motor control
- **Navigation** - GPS and landmark-based navigation support

## Project Structure

```
.
├── app/                    # Web application and API
│   ├── order_app.py       # Web interface (Flask)
│   ├── pi_server.py       # API server (runs on Raspberry Pi)
│   ├── delivery.py        # Order management system
│   └── README.md          # App documentation
│
├── controls/              # RC car control system
│   ├── arduinoControls.ino        # Arduino sketch
│   ├── interactive_control.py     # Interactive keyboard control
│   ├── arduino_wasd_controller.py # Low-level controller
│   ├── motor_monitor.py           # Performance monitoring
│   └── README.md                  # Controls documentation
│
├── navigation/            # Navigation and pathfinding
│   ├── map.py            # Campus map with locations
│   ├── pathfinding.py    # Dijkstra's algorithm
│   ├── route_executor.py # Route execution
│   ├── gps_integration.py # GPS support
│   └── README.md         # Navigation documentation
│
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd "Hacking 2025"

# Install dependencies
pip3 install -r requirements.txt

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the System

**Option A: Full System (Laptop + Raspberry Pi)**

```bash
# Terminal 1: Start Pi Server (on Raspberry Pi)
python3 app/pi_server.py --host 0.0.0.0 --port 5000

# Terminal 2: Start Order App (on laptop)
python3 app/order_app.py --host 0.0.0.0 --port 5001 --pi-url http://raspberrypi.local:5000

# Open browser: http://localhost:5001
```

**Option B: Local Testing (Simulation Mode)**

```bash
# Start Pi Server in simulation mode
python3 app/pi_server.py --simulate --host 127.0.0.1 --port 5000

# Start Order App
python3 app/order_app.py --host 127.0.0.1 --port 5001 --pi-url http://127.0.0.1:5000

# Open browser: http://localhost:5001
```

### 3. Control RC Car

```bash
# Interactive control
python3 controls/interactive_control.py

# With monitoring
python3 controls/interactive_control.py --monitor
```

## Core Components

### 1. Web Application (`app/`)

**Order App** - Web interface for placing orders

- User-friendly order form
- Order status tracking
- System health monitoring
- UB-branded design

**Pi Server** - API server running on Raspberry Pi

- Receives orders from web app
- Manages delivery queue
- Executes routes
- Integrates with RC car controls

**Delivery System** - Order management and routing

- Order creation and tracking
- Route optimization
- Priority scheduling
- Statistics and analytics

See `app/README.md` for detailed documentation.

### 2. Controls System (`controls/`)

**Arduino Sketch** - Motor control firmware

- WASD protocol (single character commands)
- Latched drive, momentary steering
- Serial communication (9600 baud)

**Python Controllers** - Software control layer

- Interactive keyboard control
- Remote control via SSH
- Performance monitoring
- Background service support

See `controls/README.md` for detailed documentation.

### 3. Navigation System (`navigation/`)

**Campus Map** - Graph representation of UB campus

- 21+ locations (buildings, dorms, dining)
- Connections with distances
- GPS coordinate support
- Extensible structure

**Pathfinding** - Shortest path algorithms

- Dijkstra's algorithm
- Multi-stop route optimization
- Step-by-step navigation instructions

**Route Execution** - Navigate planned routes

- GPS-based navigation
- Landmark-based navigation
- Simulation mode for testing

See `navigation/README.md` for detailed documentation.

## Features

### Order Management

- ✅ Web-based order placement
- ✅ Route optimization (multi-order)
- ✅ Priority scheduling
- ✅ Order status tracking
- ✅ Real-time updates

### Pathfinding

- ✅ Dijkstra's algorithm (optimal paths)
- ✅ Multi-stop optimization
- ✅ Pickup-before-delivery constraints
- ✅ Distance calculations
- ✅ Navigation instructions

### RC Car Control

- ✅ WASD keyboard control
- ✅ Remote control via SSH
- ✅ Performance monitoring
- ✅ Auto-stop safety features
- ✅ Background service support

### Navigation

- ✅ GPS coordinate support
- ✅ Landmark-based navigation
- ✅ Simulation mode
- ✅ Route planning
- ✅ Arrival detection

## Campus Locations

### Academic Buildings

- Capen Hall, Norton Hall, Davis Hall, Furnas Hall
- Baldy Hall, Clemens Hall, Park Hall, Knox Hall
- O'Brian Hall (Law), Jacobs Management Center (Business)

### Residence Halls

- Ellicott Complex, Greiner Hall, Governors Complex

### Dining Locations

- C3 Dining Center, One World Café, The Cellar, Student Union

### Other Locations

- Alumni Arena, UB Commons, Center for the Arts, Baird Point

## API Endpoints

### Order App (localhost:5001)

- `GET /` - Order form page
- `GET /orders` - Orders list
- `GET /status` - System status
- `POST /api/order` - Create order

### Pi Server (raspberrypi.local:5000)

- `GET /api/health` - Health check
- `GET /api/orders` - Get all orders
- `POST /api/orders` - Create order
- `POST /api/orders/<id>/execute` - Execute order
- `POST /api/orders/execute-all` - Execute all pending

## Usage Examples

### Place an Order

```bash
curl -X POST http://localhost:5001/api/order \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Alice",
    "pickup_location": "Student Union",
    "delivery_location": "Norton Hall",
    "items": ["Pizza", "Soda"],
    "priority": 0
  }'
```

### Control RC Car

```bash
# Interactive control
python3 controls/interactive_control.py

# Keyboard:
# W - Forward
# S - Backward
# A - Steer Left
# D - Steer Right
# Space - Stop
# Q - Quit
```

### Find Shortest Path

```python
from navigation.map import CampusMap
from navigation.pathfinding import Pathfinder

campus_map = CampusMap()
pathfinder = Pathfinder(campus_map)

path, distance = pathfinder.find_shortest_path("Capen Hall", "Norton Hall")
print(f"Path: {path}")
print(f"Distance: {distance:.1f} meters")
```

## Configuration

### Environment Variables

**Pi Server:**

- `ARDUINO_PORT` - Arduino serial port (default: `/dev/ttyACM0`)
- `SIMULATE` - Enable simulation mode (default: `false`)

**Order App:**

- `PI_SERVER_URL` - Pi server URL (default: `http://raspberrypi.local:5000`)

### Command Line Options

**Pi Server:**

```bash
python3 app/pi_server.py --help
  --host HOST          Host to bind to (default: 0.0.0.0)
  --port PORT          Port to bind to (default: 5000)
  --arduino-port PORT  Arduino port
  --simulate           Enable simulation mode
  --debug              Enable debug mode
```

**Order App:**

```bash
python3 app/order_app.py --help
  --host HOST     Host to bind to
  --port PORT     Port to bind to (default: 5001)
  --pi-url URL    Pi server URL
  --debug         Enable debug mode
```

## Algorithms

### Pathfinding

- **Algorithm**: Dijkstra's algorithm
- **Complexity**: O(V log V + E)
- **Guarantee**: Always finds shortest path

### Route Optimization

- **Algorithm**: Greedy nearest-neighbor
- **Constraint**: Pickups before deliveries
- **Note**: Good solutions, not guaranteed optimal (TSP is NP-hard)

## Troubleshooting

### Can't Connect to Pi Server

1. Check Pi server is running: `ssh pi@raspberrypi.local "ps aux | grep pi_server"`
2. Check network: `ping raspberrypi.local`
3. Verify firewall settings

### RC Car Not Responding

1. Check Arduino connection: `python3 controls/arduino_wasd_controller.py --list-ports`
2. Test serial communication
3. Verify Arduino sketch is uploaded

### Orders Not Executing

1. Check Pi server logs
2. Verify order status via API
3. Check route executor availability
4. Run in simulation mode for testing

## Development

### Running in Development Mode

```bash
# Pi Server
python3 app/pi_server.py --debug

# Order App
python3 app/order_app.py --debug
```

### Testing

```bash
# Test pathfinding
python3 navigation/test_navigation.py

# Test controls
python3 controls/interactive_control.py --monitor

# Test order system
curl http://localhost:5000/api/health
```

## Future Enhancements

- [ ] Real GPS tracking and navigation
- [ ] Obstacle detection and avoidance
- [ ] Persistent order storage (database)
- [ ] Real-time WebSocket updates
- [ ] User authentication
- [ ] Multi-vehicle coordination
- [ ] Battery management
- [ ] Machine learning route optimization

## Documentation

- **Main README** (`README.md`) - This file
- **App Documentation** (`app/README.md`) - Web app and API
- **Controls Documentation** (`controls/README.md`) - RC car control
- **Navigation Documentation** (`navigation/README.md`) - Pathfinding and navigation

## License

This project is provided as-is for educational and development purposes.

## Contact

For questions or contributions, please open an issue or submit a pull request.

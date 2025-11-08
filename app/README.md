# Order App - Food Delivery Ordering System

Web-based application for placing delivery orders that are sent to the Raspberry Pi for execution.

## Overview

The order system provides a complete web-based interface for:
- Placing delivery orders
- Tracking order status
- Managing deliveries
- Monitoring system health

## Architecture

```
User Browser → Order App (Laptop) → Pi Server (Raspberry Pi) → Delivery System → RC Car
```

### Components

1. **Order App** (`order_app.py`) - Web interface running on laptop/computer
2. **Pi Server** (`pi_server.py`) - API server running on Raspberry Pi
3. **Delivery System** (`delivery.py`) - Order management and routing
4. **Route Executor** - Executes delivery routes on RC car

## Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
# Or use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Setup Raspberry Pi Server

On your Raspberry Pi:

```bash
# Install dependencies
pip3 install flask flask-cors

# Copy files to Pi
scp app/pi_server.py pi@raspberrypi.local:~/
scp app/delivery.py pi@raspberrypi.local:~/app/
scp -r navigation/ pi@raspberrypi.local:~/

# Start Pi server
python3 pi_server.py --host 0.0.0.0 --port 5000
```

Or run in simulation mode (no Arduino):
```bash
python3 pi_server.py --simulate --host 127.0.0.1 --port 5000
```

### 3. Setup Order App (Laptop)

On your laptop/computer:

```bash
# Start order app
python3 app/order_app.py --host 0.0.0.0 --port 5001

# Or specify Pi server URL
python3 app/order_app.py --pi-url http://raspberrypi.local:5000
```

### 4. Access Web Interface

Open browser to: `http://localhost:5001`

## How the Order System Works

### Order Lifecycle

```
PENDING → IN_PROGRESS → COMPLETED
   ↓
CANCELLED (if cancelled)
```

### Order Flow

1. **User Places Order**
   - Fills out form in browser (localhost:5001)
   - Submits order

2. **Order App Validates**
   - Validates form data
   - Sends HTTP POST to Pi Server

3. **Pi Server Receives**
   - Creates order in DeliverySystem
   - Stores in memory: `delivery_system.orders[order_id]`
   - Status: PENDING

4. **Order Execution** (when triggered)
   - Status: PENDING → IN_PROGRESS
   - Route planned using pathfinding
   - Route executed (currently simulated)
   - Status: IN_PROGRESS → COMPLETED

### Order Storage

**Location**: Raspberry Pi memory (`delivery_system.orders` dictionary)

**Storage Details**:
- **Type**: Python dictionary `Dict[str, Order]`
- **Key**: Order ID (e.g., "ORD-0001")
- **Value**: Order object with all order details
- **Persistence**: ❌ **NOT persistent** - orders are lost when server restarts

**Order Data Structure**:
```python
@dataclass
class Order:
    order_id: str              # "ORD-0001"
    customer_name: str         # "Alice"
    pickup_location: str       # "Student Union"
    delivery_location: str     # "Norton Hall"
    items: List[str]           # ["Pizza", "Soda"]
    status: OrderStatus        # PENDING, IN_PROGRESS, COMPLETED, CANCELLED
    created_at: datetime       # When order was created
    completed_at: Optional[datetime]  # When order was completed
    priority: int              # 0=normal, 1=high, 2=urgent
```

### Communication Flow

```
User Browser (localhost:5001)
    ↓
JavaScript: POST /api/order
    ↓
Order App (Flask)
    ↓
HTTP POST to Pi Server
    ↓
Pi Server (raspberrypi.local:5000)
    ↓
DeliverySystem.create_order()
    ↓
Stored in: delivery_system.orders[order_id] = Order(...)
```

**Code Example**:
```python
# Order App sends request
response = requests.post(
    'http://raspberrypi.local:5000/api/orders',
    json=order_data,
    timeout=10
)

# Pi Server receives request
@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    order_id = delivery_system.create_order(...)
    # Order stored in: delivery_system.orders[order_id]
    return jsonify({'order_id': order_id})
```

### Route Planning

- Uses **Dijkstra's algorithm** for shortest paths
- Optimizes multi-order routes (greedy algorithm)
- Ensures pickups happen before deliveries
- Returns route path, distance, and details

**Example**:
```python
# Plan route for order
route, distance, details = delivery_system.plan_delivery_route(
    start_location="Student Union",
    order_ids=["ORD-0001"]
)

# Route: ["Student Union", "Capen Hall", "Norton Hall"]
# Distance: 350.0 meters
```

## Usage

### Starting the Pi Server

```bash
# On Raspberry Pi
python3 pi_server.py --host 0.0.0.0 --port 5000

# With Arduino
python3 pi_server.py --arduino-port /dev/ttyACM0

# Simulation mode (no Arduino needed)
python3 pi_server.py --simulate
```

### Starting the Order App

```bash
# On laptop
python3 app/order_app.py --port 5001

# With custom Pi server URL
python3 app/order_app.py --pi-url http://192.168.1.100:5000
```

### Placing Orders

1. Open browser to `http://localhost:5001`
2. Fill out the order form:
   - Customer name
   - Pickup location
   - Delivery location
   - Items (one per line)
   - Priority (optional)
3. Click "Place Order"
4. Order is sent to Pi server and added to queue

### Viewing Orders

- Visit `http://localhost:5001/orders` to see all orders
- Orders auto-refresh every 5 seconds
- View order status (pending, in_progress, completed)

### Executing Orders

Orders can be executed manually:

```bash
# Execute single order
curl -X POST http://raspberrypi.local:5000/api/orders/ORD-0001/execute

# Execute all pending
curl -X POST http://raspberrypi.local:5000/api/orders/execute-all
```

## API Endpoints

### Order App Endpoints

- `GET /` - Order form page
- `GET /orders` - Orders list page
- `GET /status` - Status page
- `POST /api/order` - Create order
- `GET /api/orders` - Get all orders
- `GET /api/order/<order_id>` - Get specific order

### Pi Server Endpoints

- `GET /api/health` - Health check
- `GET /api/orders` - Get all orders
- `GET /api/orders/<order_id>` - Get specific order
- `POST /api/orders` - Create order
- `POST /api/orders/<order_id>/execute` - Execute order
- `POST /api/orders/execute-all` - Execute all pending orders
- `POST /api/orders/<order_id>/cancel` - Cancel order
- `GET /api/statistics` - Get delivery statistics

## Example Usage

### Place Order via API

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

### Execute Order on Pi

```bash
curl -X POST http://raspberrypi.local:5000/api/orders/ORD-0001/execute
```

### Get All Orders

```bash
curl http://raspberrypi.local:5000/api/orders
```

### Check System Health

```bash
curl http://raspberrypi.local:5000/api/health
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
python3 pi_server.py --help
  --host HOST          Host to bind to (default: 0.0.0.0)
  --port PORT          Port to bind to (default: 5000)
  --arduino-port PORT  Arduino port (default: /dev/ttyACM0)
  --simulate           Enable simulation mode
  --debug              Enable debug mode
```

**Order App:**
```bash
python3 app/order_app.py --help
  --host HOST     Host to bind to (default: 0.0.0.0)
  --port PORT     Port to bind to (default: 5001)
  --pi-url URL    Pi server URL
  --debug         Enable debug mode
```

## Troubleshooting

### Can't Connect to Pi Server

1. Check Pi server is running:
   ```bash
   ssh pi@raspberrypi.local "ps aux | grep pi_server"
   ```

2. Check network connectivity:
   ```bash
   ping raspberrypi.local
   ```

3. Check firewall settings on Pi

4. Verify Pi server URL in order app

### Orders Not Executing

1. Check Pi server logs for errors
2. Verify Arduino connection (if not in simulation mode)
3. Check order status via API
4. Verify route executor is available

### Arduino Not Responding

1. Check serial port:
   ```bash
   python3 -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
   ```

2. Test Arduino connection:
   ```bash
   python3 controls/arduino_wasd_controller.py --list-ports
   ```

3. Run in simulation mode for testing:
   ```bash
   python3 pi_server.py --simulate
   ```

## Development

### Running in Development Mode

```bash
# Pi Server
python3 pi_server.py --debug

# Order App
python3 app/order_app.py --debug
```

### Testing

Test Pi server health:
```bash
curl http://raspberrypi.local:5000/api/health
```

Test order creation:
```bash
curl -X POST http://localhost:5001/api/order \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Test","pickup_location":"Student Union","delivery_location":"Norton Hall","items":["Test"]}'
```

## File Structure

```
app/
├── order_app.py              # Web interface (Flask)
├── pi_server.py              # API server (Flask)
├── delivery.py               # Order management system
├── simple_delivery_system.py # Simplified delivery system
├── templates/
│   ├── order_form.html      # Order placement form
│   ├── orders.html          # Orders list page
│   └── status.html          # System status page
├── start_order_app.sh       # Start script
├── start_pi_server.sh       # Start script
└── README.md                # This file
```

## Future Improvements

1. **Real Route Execution** - Integrate with route executor for actual RC car movement
2. **GPS Integration** - Use GPS for location tracking
3. **Real-time Updates** - WebSocket support for real-time order status
4. **Order History** - Persistent storage for orders (database)
5. **User Authentication** - Add user accounts and authentication
6. **Multiple Cars** - Support for multiple delivery vehicles
7. **Route Optimization** - Better multi-order route optimization
8. **Notifications** - SMS/Email notifications for order updates

## License

This code is provided as-is for educational and development purposes.

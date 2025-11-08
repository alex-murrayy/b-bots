#!/bin/bash
# Quick start script for Pi Server

echo "Starting UB Food Delivery Pi Server..."
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Flask not found. Installing dependencies..."
    pip3 install flask flask-cors
fi

# Get Arduino port from user or use default
ARDUINO_PORT="${ARDUINO_PORT:-/dev/ttyACM0}"
if [ -z "$ARDUINO_PORT" ]; then
    echo "Arduino port (default: $ARDUINO_PORT):"
    read -r input
    if [ -n "$input" ]; then
        ARDUINO_PORT="$input"
    fi
fi

# Check if simulate mode
SIMULATE=""
echo "Run in simulation mode? (y/n, default: n):"
read -r simulate
if [ "$simulate" = "y" ] || [ "$simulate" = "Y" ]; then
    SIMULATE="--simulate"
    echo "Running in simulation mode (no Arduino needed)"
else
    echo "Using Arduino port: $ARDUINO_PORT"
fi

echo "Starting Pi Server on http://0.0.0.0:5000"
echo ""

# Start the server
python3 app/pi_server.py --host 0.0.0.0 --port 5000 --arduino-port "$ARDUINO_PORT" $SIMULATE


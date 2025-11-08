#!/bin/bash
# Quick start script for Order App

echo "Starting UB Food Delivery Order App..."
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Flask not found. Installing dependencies..."
    pip3 install flask flask-cors requests
fi

# Get Pi server URL from user or use default
PI_URL="${PI_SERVER_URL:-http://raspberrypi.local:5000}"
if [ -z "$PI_SERVER_URL" ]; then
    echo "Pi Server URL (default: $PI_URL):"
    read -r input
    if [ -n "$input" ]; then
        PI_URL="$input"
    fi
fi

echo "Pi Server URL: $PI_URL"
echo "Starting Order App on http://localhost:5001"
echo ""

# Start the app
python3 app/order_app.py --pi-url "$PI_URL" --host 0.0.0.0 --port 5001

